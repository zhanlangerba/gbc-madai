# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""A module containing load method for PDF files."""

import logging
import re
from pathlib import Path
import tempfile
import base64
import requests
from tqdm import tqdm
import zipfile
import os

import pandas as pd
from io import BytesIO

from graphrag.config.models.input_config import InputConfig
from graphrag.index.utils.hashing import gen_sha512_hash
from graphrag.index.input.util import load_files, generate_image_descriptions, generate_image_descriptions_sync
from graphrag.logger.base import ProgressLogger
from graphrag.storage.pipeline_storage import PipelineStorage

log = logging.getLogger(__name__)


def to_b64(file_path):
    """将文件转换为base64编码：二进制数据（如 PDF 文件）不能直接传输。Base64 编码将二进制数据转换为 ASCII 字符串，使其可以安全地嵌入到 JSON 中。
    """
    try:
        with open(file_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        raise Exception(f'File: {file_path} - Info: {e}')


def do_parse(file_path, url=None, **kwargs):
    """调用MinerU远程Server服务解析PDF文件"""
    try:

        # 拼接 /predict 到 url 路径
        if url:
            if not url.endswith('/'):
                url = url + '/'
            url = url + 'predict'

        response = requests.post(url, json={
            'file': to_b64(file_path),
            'kwargs': kwargs
        })

        if response.status_code == 200:
            output = response.json()
            output['file_path'] = file_path
            return output
        else:
            raise Exception(response.text)
    except Exception as e:
        log.error(f'File: {file_path} - Info: {e}')
        return None


async def download_output_files(url:str, output_dir:str, local_dir:str, doc_id:str):
    """从远程服务器下载解析结果文件"""
    try:
        # 将字符串路径转换为Path对象
        local_dir_path = Path(local_dir) / doc_id
        
        # 拼接 /download_output_files 到 url 路径
        if url:
            if not url.endswith('/'):
                url = url + '/'
            url = url + 'download_output_files'

        
        # 确保output_dir是正确的格式，移除可能的尾部斜杠
        clean_output_dir = output_dir.rstrip('/')
        
        # 直接构建完整的路径
        full_path = f"{clean_output_dir}/{doc_id}"
        
        # 发送请求
        response = requests.get(url, params={'output_dir': full_path})
        
        if response.status_code == 200:
            # 保存ZIP文件到临时位置
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
                temp_file.write(response.content)
                zip_path = temp_file.name
            
            # 检查ZIP文件大小
            zip_size = os.path.getsize(zip_path)
            
            if zip_size > 0:
                # 确保目标目录存在
                local_dir_path.mkdir(parents=True, exist_ok=True)
                
                # 临时目录用于解压
                temp_extract_dir = local_dir_path / "_temp_extract"
                temp_extract_dir.mkdir(parents=True, exist_ok=True)
                
                # 先将所有内容解压到临时目录
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_extract_dir)
                
                # 查找解压后的auto目录
                auto_dir = None
                for root, dirs, files in os.walk(temp_extract_dir):
                    if os.path.basename(root) == "auto":
                        auto_dir = Path(root)
                        break
                
                if auto_dir and auto_dir.exists():
                    # 如果找到auto目录，将其内容复制到local_dir_path
                    # 先创建local_dir_path/auto
                    target_auto_dir = local_dir_path / "auto"
                    target_auto_dir.mkdir(parents=True, exist_ok=True)
                    
                    # 复制auto目录中的所有内容
                    import shutil
                    for item in auto_dir.iterdir():
                        if item.is_file():
                            shutil.copy2(item, target_auto_dir)
                        elif item.is_dir():
                            # 对于目录（如images），复制整个目录
                            shutil.copytree(item, target_auto_dir / item.name, dirs_exist_ok=True)
                else:
                    # 如果没有找到auto目录，将所有内容复制到local_dir_path
                    for item in temp_extract_dir.iterdir():
                        if item.is_file():
                            shutil.copy2(item, local_dir_path)
                        elif item.is_dir() and item.name != "_temp_extract":
                            shutil.copytree(item, local_dir_path / item.name, dirs_exist_ok=True)
                
                # 删除临时解压目录
                shutil.rmtree(temp_extract_dir, ignore_errors=True)
                
                # 删除临时ZIP文件
                os.unlink(zip_path)
                
                return True
            else:
                os.unlink(zip_path)
        
        # 如果下载失败，创建一个空目录
        local_dir_path.mkdir(parents=True, exist_ok=True)
        
        # 创建一个标记文件，表示下载失败
        with open(local_dir_path / "download_failed.txt", "w") as f:
            f.write(f"下载失败时间: {pd.Timestamp.now().isoformat()}\n")
            f.write(f"尝试的路径: {full_path}\n")
            f.write(f"错误信息: 状态码 {response.status_code}\n")
        return False
    except Exception as e:
        import traceback
        log.error(traceback.format_exc())
        
        # 确保目标目录存在，即使出错也创建
        local_dir_path = Path(local_dir) / doc_id
        local_dir_path.mkdir(parents=True, exist_ok=True)
        
        # 创建一个标记文件，表示下载出错
        with open(local_dir_path / "download_error.txt", "w") as f:
            f.write(f"下载错误时间: {pd.Timestamp.now().isoformat()}\n")
            f.write(f"错误信息: {str(e)}\n")
            f.write(traceback.format_exc())
        
        return False


async def load_pdf(
    config: InputConfig,
    progress: ProgressLogger | None,
    storage: PipelineStorage,
) -> pd.DataFrame:
    """Load PDF inputs from a directory using remote parsing service."""
    
    # 通过 settings.yaml 文件配置 本地存放 MinerU解析结果文件的路径
    if hasattr(config, "local_output_dir") and config.local_output_dir:
        local_output_dir = Path(config.local_output_dir)
    else:
        # 这里如果没有配置，则使用下面的路径存储
        local_output_dir = Path("./pdf_outputs")

    # 如果目录不存在，则创建
    local_output_dir.mkdir(parents=True, exist_ok=True)
    
    async def load_file(path: str, group: dict | None) -> pd.DataFrame:
        if group is None:
            group = {}
        try:
            # 以二进制方式获取PDF内容
            buffer = BytesIO(await storage.get(path, as_bytes=True))
                
            # 将二进制内容保存到临时文件
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(buffer.getvalue())
                file_path = temp_file.name
                
            # 1. 调用MinerU远程Server服务解析PDF
            result = do_parse(file_path, url=config.mineru_api_url)
            
            if not result or 'output_dir' not in result:
                data = pd.DataFrame([{
                    "text": f"[解析失败] {path}",
                    "title": Path(path).name,
                    "id": path
                }])
                return data
        
            # 获取输出目录
            output_dir = result['output_dir']
            if not output_dir.endswith('/auto'):
                output_dir = f"{output_dir}/auto"
        
          
            # 从output_dir中提取唯一标识符作为ID
            id_match = re.search(r'\/([^\/]+)\/auto$', output_dir)
            doc_id = id_match.group(1) if id_match else path
                
            # 创建文档专属的本地目录
            doc_local_dir = local_output_dir / doc_id
            doc_local_dir.mkdir(parents=True, exist_ok=True)
                
            # 初始化元数据
            metadata = {
                "file_path": path,
                "output_dir": output_dir,
                "parse_time": pd.Timestamp.now().isoformat(),
                "doc_id": doc_id
            }
                
            try:
                # 2. 下载文件
                download_success = await download_output_files(config.mineru_api_url, config.mineru_output_dir, config.local_output_dir, doc_id)
                metadata["local_output_dir"] = str(doc_local_dir)
                    
                if download_success:
                    # 首先尝试从auto子目录读取文件
                    auto_dir = doc_local_dir / "auto"
                    md_file_path = None
                    content_list_path = None
                        
              
                    # 尝试从auto目录读取md文件
                    md_file_path = auto_dir / f"{doc_id}.md"
                    
                    # 尝试从auto目录读取content_list.json
                    content_list_path = auto_dir / f"{doc_id}_content_list.json"


                    # 现在尝试读取MD文件
                    if md_file_path and md_file_path.exists():
                        try:
                            with open(md_file_path, 'r', encoding='utf-8') as md_file:
                                text_content = md_file.read()
                        except Exception as e:
                            log.error(f"读取MD文件失败: {str(e)}")
                            text_content = f"[读取MD文件失败] {path}: {str(e)}"
                    else:
                        log.error(f"MD文件不存在: {md_file_path}")
                        text_content = f"[MD文件不存在] {path}"
                else:
                    text_content = f"[下载文件失败] {path}"
                    
                # 创建解析结果对象，用于提取结构化信息
                parse_content = {}
                    
                # 将MD文件内容添加到parse_content
                parse_content['markdown_text'] = text_content

                # 创建DataFrame行
                data = pd.DataFrame([{
                    "text": text_content,
                    "title": Path(path).name,  # 使用文件名作为标题
                    "id": doc_id  # 使用提取的ID
                }])
                    
                # 提取结构化信息 - 修改为检查auto目录并使用异步调用
                structured_info = await extract_tables_from_model_json(auto_dir if auto_dir.exists() else doc_local_dir, doc_id)
                    
       
                # 为表格生成描述
                if structured_info and structured_info.get("tables") and config.table_description_api_key and config.table_description_model:
                    structured_info = generate_descriptions_for_tables(auto_dir if auto_dir.exists() else doc_local_dir, structured_info, config)
                    
                # 从content_list.json提取图片信息 - 更新路径
                image_info = None
                if content_list_path and content_list_path.exists():
                    image_info = extract_images_from_content_list(auto_dir if auto_dir.exists() else doc_local_dir, doc_id)
                else:
                    log.error(f"content_list.json文件不存在: {content_list_path}")
                
        
                # # 为图片生成描述
                if image_info and image_info.get("images") and config.image_description_api_key and config.image_description_model:
                    image_info = generate_descriptions_for_images(auto_dir if auto_dir.exists() else doc_local_dir, image_info, config)
                    
                # 构建增强的Markdown文本，包含元数据
                enhanced_text = enhance_markdown_with_metadata(text_content, structured_info, image_info)
                    
                # 更新DataFrame中的文本
                data["text"] = [enhanced_text]
                    
                # 构建统一的内容元素列表
                content_elements = []
                    
                # 添加表格元素
                if structured_info and structured_info.get("tables"):
                    for table in structured_info["tables"]:
                        content_elements.append({
                            "type": "table",
                            "page": table.get("page", 0),
                            "element_idx": table.get("table_idx", 0),
                            "html": table.get("html", ""),
                            "description": table.get("description", "")
                        })
                    
                # 添加图片元素
                if image_info and image_info.get("images"):
                    for image in image_info["images"]:
                        content_elements.append({
                            "type": "image",
                            "page": image.get("page", 0),
                            "element_idx": image.get("image_idx", 0),
                            "path": image.get("path", ""),
                            "description": image.get("description", "")
                        })
                    
                # 按页码和元素索引排序
                content_elements.sort(key=lambda x: (x["page"], x["element_idx"]))
                    
                # 将内容元素添加到元数据
                metadata["content_elements"] = content_elements
                    
                # 添加内容类型统计
                content_types = {}
                if structured_info and structured_info.get("tables"):
                    content_types["table"] = len(structured_info["tables"])
                if image_info and image_info.get("images"):
                    content_types["image"] = len(image_info["images"])
                if not content_types:
                    content_types["default"] = "text"
                metadata["content_types"] = content_types
                    
                # 更新DataFrame的元数据
                data["metadata"] = [metadata]
                    
                # 添加分组信息
                for key, value in group.items():
                    data[key] = value
                    
                # 添加创建日期
                creation_date = await storage.get_creation_date(path)
                data["creation_date"] = creation_date
                
                # 导出数据到CSV文件，以便直观查看
                try:
                    import os
                    csv_dir = Path('./data/pdf_csv_exports')
                    csv_dir.mkdir(parents=True, exist_ok=True)
                    
                    # 创建CSV文件名，使用doc_id以避免文件名冲突
                    csv_filename = f"{doc_id}_pdf_data.csv"
                    csv_path = csv_dir / csv_filename
                    
                    # 将DataFrame导出为CSV
                    data.to_csv(csv_path, index=False, encoding='utf-8')
                    log.info(f"PDF数据已导出到: {csv_path}")
                    
                    # 如果有结构化信息，也导出到单独的CSV
                    if structured_info and structured_info.get("tables"):
                        tables_data = []
                        for table in structured_info.get("tables", []):
                            # 限制HTML长度，避免CSV过大
                            html_truncated = table.get("html", "")
                            if len(html_truncated) > 1000:
                                html_truncated = html_truncated[:1000] + "..."
                                
                            tables_data.append({
                                "table_idx": table.get("table_idx", ""),
                                "page": table.get("page", ""),
                                "caption": table.get("caption", ""),
                                "description": table.get("description", ""),
                                "html": html_truncated
                            })
                            
                        if tables_data:
                            tables_df = pd.DataFrame(tables_data)
                            tables_csv_path = csv_dir / f"{doc_id}_tables.csv"
                            tables_df.to_csv(tables_csv_path, index=False, encoding='utf-8')
                            log.info(f"表格数据已导出到: {tables_csv_path}")
                    
                    # 如果有图片信息，也导出到单独的CSV
                    if image_info and image_info.get("images"):
                        images_data = []
                        for img in image_info.get("images", []):
                            # 限制上下文长度
                            context_before = img.get("context_before", "")
                            if len(context_before) > 500:
                                context_before = context_before[:500] + "..."
                                
                            context_after = img.get("context_after", "")
                            if len(context_after) > 500:
                                context_after = context_after[:500] + "..."
                                
                            images_data.append({
                                "image_idx": img.get("image_idx", ""),
                                "page": img.get("page", ""),
                                "path": img.get("path", ""),
                                "caption": img.get("caption", ""),
                                "description": img.get("description", ""),
                                "context_before": context_before,
                                "context_after": context_after
                            })
                            
                        if images_data:
                            images_df = pd.DataFrame(images_data)
                            images_csv_path = csv_dir / f"{doc_id}_images.csv"
                            images_df.to_csv(images_csv_path, index=False, encoding='utf-8')
                            log.info(f"图片数据已导出到: {images_csv_path}")
                    
                    # 导出metadata到JSON文件
                    import json
                    metadata_path = csv_dir / f"{doc_id}_metadata.json"
                    
                    # 将metadata转换为可序列化的对象
                    metadata_serializable = {}
                    for k, v in metadata.items():
                        if isinstance(v, (str, int, float, bool, list, dict)) or v is None:
                            metadata_serializable[k] = v
                        else:
                            metadata_serializable[k] = str(v)
                    
                    with open(metadata_path, 'w', encoding='utf-8') as f:
                        json.dump(metadata_serializable, f, ensure_ascii=False, indent=2)
                    log.info(f"元数据已导出到: {metadata_path}")
                    
                except Exception as e:
                    log.error(f"导出CSV时出错: {str(e)}")
                    import traceback
                    log.error(traceback.format_exc())
                

                return data

            except Exception as e:
                log.error(f"处理PDF文件时出错: {path}, 错误: {str(e)}")
                # 创建一个包含错误信息的DataFrame
                data = pd.DataFrame([{
                    "text": f"[处理错误] {path}: {str(e)}",
                    "title": Path(path).name,  # 使用文件名作为标题
                    "id": path  # 使用文件路径作为ID
                }])
        
                # 添加分组信息
                for key, value in group.items():
                    data[key] = value
        
                # 添加创建日期
                try:
                    creation_date = await storage.get_creation_date(path)
                    data["creation_date"] = creation_date
                except:
                    data["creation_date"] = pd.Timestamp.now()
        
                return data

        except Exception as e:
            log.error(f"处理PDF文件时出错: {path}, 错误: {str(e)}")
            # 创建一个包含错误信息的DataFrame
            data = pd.DataFrame([{
                "text": f"[处理错误] {path}: {str(e)}",
                "title": Path(path).name,  # 使用文件名作为标题
                "id": path  # 使用文件路径作为ID
            }])
                
            # 添加分组信息
            for key, value in group.items():
                data[key] = value
                
            # 添加创建日期
            try:
                creation_date = await storage.get_creation_date(path)
                data["creation_date"] = creation_date
            except:
                data["creation_date"] = pd.Timestamp.now()

            return data

    # 使用现有的load_files函数来处理文件加载
    return await load_files(load_file, config, storage, progress)

async def extract_tables_from_model_json(doc_local_dir, doc_id):
    """从model.json中提取表格信息"""
    # 尝试多种可能的路径
    model_json_paths = [
        doc_local_dir / f"{doc_id}_model.json",  # 原始路径
        doc_local_dir / "model.json",            # 简化名称
    ]
    
    model_json_path = None
    for path in model_json_paths:
        if path.exists():
            model_json_path = path
            break
    
    if not model_json_path:
        log.info(f"model.json文件不存在，尝试了这些路径: {[str(p) for p in model_json_paths]}")
        return None
    
    structured_info = {
        "content_types": {},
        "tables": []
    }
    
    try:
        # 读取model.json文件
        with open(model_json_path, 'r', encoding='utf-8') as f:
            import json
            model_json = json.load(f)
        
        for page_idx, page in enumerate(model_json):
            page_info = page.get('page_info', {})
            layout_dets = page.get('layout_dets', [])
            
            for obj in layout_dets:
                category_id = obj.get('category_id')
                
                # 只处理表格 (category_id = 5)
                if category_id == 5:
                    poly = obj.get('poly', [])
                    
                    if len(poly) >= 8:  # 确保有足够的坐标点
                        # 计算边界框
                        x_coords = [poly[i] for i in range(0, len(poly), 2)]
                        y_coords = [poly[i+1] for i in range(0, len(poly), 2)]
                        bbox = [min(x_coords), min(y_coords), max(x_coords), max(y_coords)]
                        
                        # 获取HTML内容
                        html_content = obj.get('html', "")
                        
                        # 创建表格数据
                        table_data = {
                            "page": page_info.get('page_no', page_idx+1),
                            "table_idx": len(structured_info["tables"]),
                            "bbox": bbox,
                            "score": obj.get('score', 0),
                            "html": html_content
                        }
                        
                        # 查找相关的表格标题 (category_id = 6)
                        for caption_obj in layout_dets:
                            if caption_obj.get('category_id') == 6:
                                caption_poly = caption_obj.get('poly', [])
                                if len(caption_poly) >= 8:
                                    # 检查标题是否在表格附近
                                    caption_y_coords = [caption_poly[i+1] for i in range(0, len(caption_poly), 2)]
                                    caption_y_min = min(caption_y_coords)
                                    caption_y_max = max(caption_y_coords)
                                    
                                    # 如果标题在表格上方或下方附近
                                    if (abs(caption_y_min - bbox[1]) < 100 or abs(caption_y_max - bbox[3]) < 100):
                                        table_data["caption"] = caption_obj.get('text', "")
                        
                        # 如果没有找到标题，设置为空字符串
                        if "caption" not in table_data:
                            table_data["caption"] = ""
                        
                        # 添加脚注字段
                        table_data["footnote"] = ""
                        
                        structured_info["tables"].append(table_data)

        # 更新content_types
        if structured_info["tables"]:
            structured_info["content_types"] = {"table": len(structured_info["tables"])}
        else:
            structured_info["content_types"] = {"default": "text"}
        
        return structured_info
    
    except Exception as e:
        print(f"提取表格信息时出错: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return {"content_types": {"default": "text"}, "tables": []}

def extract_images_from_content_list(doc_local_dir, doc_id):
    """从content_list.json中提取图片信息，并包含前后文本作为上下文"""
    # 尝试多种可能的路径
    content_list_paths = [
        doc_local_dir / f"{doc_id}_content_list.json",  # 原始路径
        doc_local_dir / "content_list.json",            # 简化名称
    ]
    
    content_list_path = None
    for path in content_list_paths:
        if path.exists():
            content_list_path = path
            break
    
    if not content_list_path:
        print(f"content_list.json文件不存在，尝试了这些路径: {[str(p) for p in content_list_paths]}")
        return None
    
    structured_info = {
        "content_types": {},
        "images": []
    }
    
    try:
        # 读取content_list.json文件
        with open(content_list_path, 'r', encoding='utf-8') as f:
            import json
            content_list = json.load(f)
               
        # 遍历content_list查找图片
        for idx, item in enumerate(content_list):
            if item.get('type') == 'image':
                # 创建图片数据
                image_data = {
                    "page": item.get('page_idx', 0),
                    "image_idx": len(structured_info["images"]),
                    "path": item.get('img_path', ''),
                    "caption": '',
                    "context_before": '',
                    "context_after": ''
                }
                
                # 提取图片标题
                img_caption = item.get('img_caption', [])
                if img_caption and isinstance(img_caption, list):
                    image_data["caption"] = ' '.join(img_caption)
                elif img_caption and isinstance(img_caption, str):
                    image_data["caption"] = img_caption
                
                # 获取图片前一项的内容作为上下文
                if idx > 0:
                    prev_item = content_list[idx-1]
                    if prev_item.get('type') == 'text':
                        image_data["context_before"] = prev_item.get('text', '')
                
                # 获取图片后一项的内容作为上下文
                if idx < len(content_list) - 1:
                    next_item = content_list[idx+1]
                    if next_item.get('type') == 'text':
                        image_data["context_after"] = next_item.get('text', '')

                # 如果图片路径是相对路径，确保它是相对于doc_local_dir的
                if image_data["path"] and not image_data["path"].startswith('/'):
                    # 检查文件是否存在
                    img_path = doc_local_dir / image_data["path"]
                    # if img_path.exists():
                    #     print(f"图片文件存在: {img_path}")
                    # else:
                    #     print(f"警告: 图片文件不存在: {img_path}")
                
                structured_info["images"].append(image_data)
               
        
        # 更新content_types
        if structured_info["images"]:
            structured_info["content_types"] = {"image": len(structured_info["images"])}
        else:
            structured_info["content_types"] = {"default": "text"}
        
        return structured_info
    
    except Exception as e:
        print(f"提取图片信息时出错: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return {"content_types": {"default": "text"}, "images": []}

def generate_descriptions_for_images(doc_local_dir, image_info, config):
    """为图片生成描述"""
    if not image_info or not image_info.get("images"):
        return image_info
    
    try:
        # 收集所有需要处理的图片路径
        image_paths = []
        for image_data in image_info["images"]:
            if image_data.get("path"):
                img_path = doc_local_dir / image_data["path"]
                if img_path.exists():
                    image_paths.append(img_path)
        
        if not image_paths:
            return image_info
        
        # 获取图片所在目录
        image_dir = image_paths[0].parent
        
        # 生成临时输出文件路径
        output_file = doc_local_dir / "image_descriptions.json"
        
        # 调用图片描述生成函数
        try:
            # 导入函数
            from graphrag.index.input.util import generate_image_descriptions_sync
            
            # 生成描述，传递image_info参数
            descriptions = generate_image_descriptions_sync(
                config=config,
                image_dir=image_dir,
                output_file=output_file,
                max_retries=3,
                retry_delay=2,
                image_info=image_info  # 传递上下文信息
            )
            
            # 将描述添加到图片数据中
            for image_data in image_info["images"]:
                if image_data.get("path"):
                    img_path = str(doc_local_dir / image_data["path"])
                    # 尝试不同的路径格式匹配
                    if img_path in descriptions:
                        image_data["description"] = descriptions[img_path]
                    else:
                        # 尝试使用相对路径
                        rel_path = str(image_data["path"])
                        matching_keys = [k for k in descriptions.keys() if k.endswith(rel_path)]
                        if matching_keys:
                            image_data["description"] = descriptions[matching_keys[0]]
                        else:
                            # 尝试使用文件名匹配
                            img_name = Path(image_data["path"]).name
                            matching_keys = [k for k in descriptions.keys() if Path(k).name == img_name]
                            if matching_keys:
                                image_data["description"] = descriptions[matching_keys[0]]
                            else:
                                image_data["description"] = "无法生成图片描述"
                else:
                    image_data["description"] = "图片路径为空"
        
        except ImportError:
            log.error("无法导入generate_image_descriptions_sync函数，跳过描述生成")
            for image_data in image_info["images"]:
                image_data["description"] = "描述生成功能不可用"
        except Exception as e:
            log.error(f"生成图片描述时出错: {str(e)}")
            import traceback
            log.error(traceback.format_exc())
            for image_data in image_info["images"]:
                image_data["description"] = f"描述生成失败: {str(e)}"
        
        return image_info
    
    except Exception as e:
        log.error(f"处理图片描述时出错: {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        return image_info

def generate_descriptions_for_tables(doc_local_dir, structured_info, config):
    """为表格生成描述"""
    if not structured_info or not structured_info.get("tables"):
        return structured_info
    
    try:
        # 收集所有需要处理的表格HTML内容
        tables_data = []
        for table_data in structured_info["tables"]:
            if table_data.get("html"):
                tables_data.append({
                    "index": table_data.get("table_idx", 0),
                    "html": table_data.get("html", ""),
                    "caption": table_data.get("caption", "")
                })
        
        if not tables_data:
            return structured_info
        
        # 生成临时输出文件路径
        output_file = doc_local_dir / "table_descriptions.json"
        
        # 调用表格描述生成函数
        try:
            # 导入OpenAI API
            import os
            import json
            import time
            from openai import OpenAI
            
            # 获取API密钥和配置
            api_key = config.table_description_api_key
            base_url = config.base_url if hasattr(config, "base_url") else "https://api.deepseek.com"
            model = config.table_description_model
            
            # 设置模型和参数
            max_retries = 3
            retry_delay = 2
            max_tokens = 300
            temperature = 0.7
            
            # 初始化OpenAI客户端
            client = OpenAI(
                api_key=api_key,
                base_url=base_url,
            )
            
            # 为每个表格生成描述
            descriptions = {}
            for table_info in tables_data:
                table_idx = table_info["index"]
                html_content = table_info["html"]
                caption = table_info["caption"]
                
                # 构建提示词
                prompt_text = """你是一个助理，负责总结表格和文本。给出表格或文本的简明摘要。表格的格式为HTML"""
                
                # 构建用户消息
                user_message = f"请总结以下表格内容:\n\n{html_content}"
                if caption:
                    user_message = f"表格标题: {caption}\n\n{user_message}"
                
                # 构建消息列表
                messages = [
                    {"role": "system", "content": prompt_text},
                    {"role": "user", "content": user_message}
                ]
                
                # 发送请求并获取响应
                success = False
                for attempt in range(max_retries):
                    try:
                        response = client.chat.completions.create(
                            model=model,
                            messages=messages,
                            max_tokens=max_tokens,
                            temperature=temperature
                        )
                        
                        # 提取描述
                        description = response.choices[0].message.content
                        descriptions[table_idx] = description
                        success = True
                        break
                        
                    except Exception as e:
                        log.error(f"处理表格时出错 (尝试 {attempt+1}/{max_retries}): {str(e)}")
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay * (attempt + 1))
                
                if not success:
                    descriptions[table_idx] = f"[描述生成失败: 多次尝试后仍然失败]"
                
                # 每处理完一个表格后保存一次
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(descriptions, f, ensure_ascii=False, indent=2)
                
                # 添加延迟，避免API限制
                time.sleep(1)
            
            # 将描述添加到表格数据中
            for table_data in structured_info["tables"]:
                table_idx = table_data.get("table_idx", 0)
                if table_idx in descriptions:
                    table_data["description"] = descriptions[table_idx]
                else:
                    table_data["description"] = "未生成描述"
        
        except ImportError:
            log.error("导入OpenAI模块失败，无法生成表格描述")
            for table_data in structured_info["tables"]:
                table_data["description"] = "描述生成功能不可用"
        except Exception as e:
            log.error(f"生成表格描述时出错: {str(e)}")
            import traceback
            log.error(traceback.format_exc())
            for table_data in structured_info["tables"]:
                table_data["description"] = f"描述生成失败: {str(e)}"
        
        return structured_info
    
    except Exception as e:
        log.error(f"处理表格描述时出错: {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        return structured_info

def enhance_markdown_with_metadata(text, structured_info, image_info):
    """将元数据以注释形式插入到Markdown文本中"""
    import json
    import re
    
    # 如果没有结构化信息，直接返回原文本
    if (not structured_info or not structured_info.get("tables")) and (not image_info or not image_info.get("images")):
        return text
    
    # 创建一个表格模式的正则表达式
    table_pattern = re.compile(r'<table>.*?</table>', re.DOTALL)
    
    # 创建一个图片模式的正则表达式
    image_pattern = re.compile(r'!\[.*?\]\((.*?)\)', re.DOTALL)
    
    # 分割文本为行
    lines = text.split('\n')
    enhanced_lines = []
    
    # 处理表格
    if structured_info and structured_info.get("tables"):
        tables = structured_info["tables"]
        for i, line in enumerate(lines):
            enhanced_lines.append(line)
            
            # 检查这一行是否包含表格
            table_matches = table_pattern.findall(line)
            if table_matches:
                for table_html in table_matches:
                    # 查找匹配的表格元数据
                    for table in tables:
                        if table.get("html") and table_html in table.get("html"):
                            # 创建元数据注释
                            metadata = {
                                "type": "table",
                                "page": table.get("page", 0),
                                "element_idx": table.get("table_idx", 0),
                                "description": table.get("description", "")
                            }
                            
                            # 插入元数据注释
                            metadata_str = json.dumps(metadata, ensure_ascii=False, indent=4)
                            enhanced_lines.insert(enhanced_lines.index(line), f"<!-- METADATA\n{metadata_str}\n-->")
                            break
    
    # 处理图片
    if image_info and image_info.get("images"):
        images = image_info["images"]
        result = []
        
        for line in enhanced_lines:
            # 检查这一行是否包含图片
            image_matches = image_pattern.findall(line)
            if image_matches:
                for img_path in image_matches:
                    # 查找匹配的图片元数据
                    for image in images:
                        if image.get("path") and (img_path in image.get("path") or image.get("path") in img_path):
                            # 创建元数据注释
                            metadata = {
                                "type": "image",
                                "page": image.get("page", 0),
                                "element_idx": image.get("image_idx", 0),
                                "path": image.get("path", ""),
                                "description": image.get("description", "")
                            }
                            
                            # 插入元数据注释
                            metadata_str = json.dumps(metadata, ensure_ascii=False, indent=4)
                            result.append(f"<!-- METADATA\n{metadata_str}\n-->")
                            result.append(line)
                            break
                    else:
                        result.append(line)
            else:
                result.append(line)
        
        enhanced_lines = result
    
    # 重新组合文本
    return '\n'.join(enhanced_lines) 