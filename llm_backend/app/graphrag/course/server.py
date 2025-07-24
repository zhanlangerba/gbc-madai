import os
import uuid
import shutil
import tempfile
import gc
import fitz
import torch
import base64
import filetype
import json
import litserve as ls
from pathlib import Path
from fastapi import HTTPException, Request
import zipfile
from fastapi.responses import FileResponse
import io

class MinerUAPI(ls.LitAPI):
    def __init__(self, output_dir='/home/07_minerU/tmp'):
        self.output_dir = Path(output_dir)

    def setup(self, device):
        if device.startswith('cuda'):
            os.environ['CUDA_VISIBLE_DEVICES'] = device.split(':')[-1]
            if torch.cuda.device_count() > 1:
                raise RuntimeError("Remove any CUDA actions before setting 'CUDA_VISIBLE_DEVICES'.")

        from magic_pdf.tools.cli import do_parse, convert_file_to_pdf
        from magic_pdf.model.doc_analyze_by_custom_model import ModelSingleton

        self.do_parse = do_parse
        self.convert_file_to_pdf = convert_file_to_pdf

        model_manager = ModelSingleton()
        model_manager.get_model(True, False)
        model_manager.get_model(False, False)
        print(f'Model initialization complete on {device}!')

    def decode_request(self, request):
        file = request['file']
        file = self.cvt2pdf(file)
        opts = request.get('kwargs', {})
        opts.setdefault('debug_able', False)
        opts.setdefault('parse_method', 'auto')
        return file, opts

    def predict(self, inputs):
        try:
            # 使用时间戳和UUID组合生成唯一目录名
            import time
            timestamp = int(time.time())
            pdf_name = f"{timestamp}_{str(uuid.uuid4())}"
            output_dir = self.output_dir.joinpath(pdf_name)
            
            # 确保目录不存在
            while output_dir.exists():
                pdf_name = f"{timestamp}_{str(uuid.uuid4())}"
                output_dir = self.output_dir.joinpath(pdf_name)
                
            self.do_parse(self.output_dir, pdf_name, inputs[0], [], **inputs[1])
            return output_dir
        except Exception as e:
            shutil.rmtree(output_dir, ignore_errors=True)
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            self.clean_memory()

    def encode_response(self, response):
        return {'output_dir': str(response)}

    def clean_memory(self):
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
        gc.collect()

    def cvt2pdf(self, file_base64):
        try:
            temp_dir = Path(tempfile.mkdtemp())
            temp_file = temp_dir.joinpath('tmpfile')
            file_bytes = base64.b64decode(file_base64)
            file_ext = filetype.guess_extension(file_bytes)

            if file_ext in ['pdf', 'jpg', 'png', 'doc', 'docx', 'ppt', 'pptx']:
                if file_ext == 'pdf':
                    return file_bytes
                elif file_ext in ['jpg', 'png']:
                    with fitz.open(stream=file_bytes, filetype=file_ext) as f:
                        return f.convert_to_pdf()
                else:
                    temp_file.write_bytes(file_bytes)
                    self.convert_file_to_pdf(temp_file, temp_dir)
                    return temp_file.with_suffix('.pdf').read_bytes()
            else:
                raise Exception('Unsupported file format')
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == '__main__':
    server = ls.LitServer(
        MinerUAPI(output_dir='/home/07_minerU/tmp'),
        accelerator='cuda',
        devices='auto',
        workers_per_device=1,
        timeout=False
    )
    
    # 获取FastAPI应用实例
    app = server.app
      

    @app.get("/download_output_files")
    async def download_output_files(output_dir: str):
        """
        下载指定输出目录中的所有文件
        
        参数:
        - output_dir: 输出目录路径
        
        返回:
        - 包含所有文件的ZIP压缩包
        """
        try:
            # 打印接收到的路径，用于调试
            print(f"接收到的output_dir: {output_dir}")
            
            # 确保路径格式正确
            output_dir = output_dir.rstrip('/')
            
            # 关键修复：处理路径中的auto子目录
            # 如果路径不存在但路径中包含/auto，尝试移除它
            dir_path = Path(output_dir)
            if not dir_path.exists() and '/auto' in output_dir:
                output_dir = output_dir.replace('/auto', '')
                dir_path = Path(output_dir)
                print(f"尝试移除/auto后的路径: {dir_path}")
            
            # 如果路径仍然不存在，尝试添加/auto
            if not dir_path.exists() and '/auto' not in output_dir:
                output_dir = f"{output_dir}/auto"
                dir_path = Path(output_dir)
                print(f"尝试添加/auto后的路径: {dir_path}")
            
            # 列出父目录内容，帮助调试
            parent_dir = str(Path(output_dir).parent)
            print(f"父目录: {parent_dir}")
            if os.path.exists(parent_dir):
                print(f"父目录内容: {os.listdir(parent_dir)}")
            else:
                print(f"父目录不存在: {parent_dir}")
            
            print(f"转换后的路径: {dir_path}, 存在: {dir_path.exists()}, 是目录: {dir_path.is_dir() if dir_path.exists() else False}")
            
            # 直接检查目录是否存在，如果不存在，尝试在父目录或其他可能的位置查找
            if not dir_path.exists() or not dir_path.is_dir():
                # 尝试在父目录中查找
                base_tmp_dir = parent_dir
                
                # 如果父目录不存在，尝试使用MinerUAPI的output_dir
                if not os.path.exists(base_tmp_dir):
                    base_tmp_dir = str(server.api.output_dir)
                    print(f"使用API的output_dir: {base_tmp_dir}")
                
                if os.path.exists(base_tmp_dir):
                    # 获取目录名的关键部分
                    basename = os.path.basename(output_dir)
                    # 移除可能的auto后缀
                    if basename == "auto" and output_dir != f"{base_tmp_dir}/auto":
                        basename = os.path.basename(os.path.dirname(output_dir))
                    
                    # 直接列出base_tmp_dir中的所有目录
                    tmp_contents = os.listdir(base_tmp_dir)
                    print(f"{base_tmp_dir}目录内容: {tmp_contents}")
                    
                    # 尝试精确匹配
                    if basename in tmp_contents:
                        dir_path = Path(os.path.join(base_tmp_dir, basename))
                        print(f"找到精确匹配的目录: {dir_path}")
                    else:
                        # 尝试部分匹配
                        parts = basename.split('_')
                        if len(parts) > 0:
                            # 尝试匹配时间戳部分
                            timestamp_part = parts[0]
                            matching_dirs = [d for d in tmp_contents if timestamp_part in d]
                            if matching_dirs:
                                dir_path = Path(os.path.join(base_tmp_dir, matching_dirs[0]))
                                print(f"找到匹配时间戳的目录: {dir_path}")
                            elif len(parts) > 1:
                                # 尝试匹配UUID部分
                                uuid_part = parts[1].split('/')[0]
                                matching_dirs = [d for d in tmp_contents if uuid_part in d]
                                if matching_dirs:
                                    dir_path = Path(os.path.join(base_tmp_dir, matching_dirs[0]))
                                    print(f"找到匹配UUID的目录: {dir_path}")
                                else:
                                    # 最后尝试：按修改时间排序，取最新的
                                    tmp_dirs = [os.path.join(base_tmp_dir, d) for d in tmp_contents if os.path.isdir(os.path.join(base_tmp_dir, d))]
                                    if tmp_dirs:
                                        tmp_dirs.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                                        dir_path = Path(tmp_dirs[0])
                                        print(f"使用最新的目录: {dir_path}")
                                    else:
                                        # 如果在当前目录找不到，尝试在MinerUAPI的output_dir中查找
                                        if base_tmp_dir != str(server.api.output_dir):
                                            print(f"在{base_tmp_dir}中找不到匹配的目录，尝试在{server.api.output_dir}中查找")
                                            return await download_output_files(f"{server.api.output_dir}/{basename}")
                                        else:
                                            raise HTTPException(status_code=404, detail=f"找不到匹配的目录: {output_dir}")
                        else:
                            # 如果无法解析目录名，尝试在MinerUAPI的output_dir中查找
                            if base_tmp_dir != str(server.api.output_dir):
                                print(f"无法解析目录名，尝试在{server.api.output_dir}中查找")
                                return await download_output_files(f"{server.api.output_dir}/{basename}")
                            else:
                                raise HTTPException(status_code=404, detail=f"无法解析目录名: {output_dir}")
                else:
                    # 如果基础目录不存在，尝试在MinerUAPI的output_dir中查找
                    if base_tmp_dir != str(server.api.output_dir):
                        print(f"基础目录{base_tmp_dir}不存在，尝试在{server.api.output_dir}中查找")
                        return await download_output_files(f"{server.api.output_dir}/{os.path.basename(output_dir)}")
                    else:
                        raise HTTPException(status_code=404, detail=f"基础目录不存在: {base_tmp_dir}")
            
            # 再次检查目录是否存在
            if not dir_path.exists() or not dir_path.is_dir():
                # 最后尝试：如果所有尝试都失败，检查是否可以直接使用MinerUAPI的output_dir
                if str(dir_path) != str(server.api.output_dir):
                    print(f"找不到有效的目录{dir_path}，尝试使用{server.api.output_dir}")
                    return await download_output_files(str(server.api.output_dir))
                else:
                    raise HTTPException(status_code=404, detail=f"找不到有效的目录: {output_dir}")
            
            # 创建临时文件用于存储ZIP
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
            temp_file.close()
            
            print(f"将打包目录: {dir_path}")
            
            # 创建ZIP文件
            with zipfile.ZipFile(temp_file.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 遍历目录中的所有文件和子目录
                file_count = 0
                dir_count = 0
                for root, dirs, files in os.walk(dir_path):
                    print(f"遍历目录: {root}, 包含文件数: {len(files)}, 子目录数: {len(dirs)}")
                    
                    # 添加空目录
                    for dir_name in dirs:
                        dir_path_full = os.path.join(root, dir_name)
                        # 计算目录在ZIP中的相对路径
                        dir_arcname = os.path.relpath(dir_path_full, dir_path) + '/'
                        # 创建目录条目
                        zipinfo = zipfile.ZipInfo(dir_arcname)
                        zipinfo.external_attr = 0o755 << 16  # 设置目录权限
                        zipf.writestr(zipinfo, '')
                        dir_count += 1
                        print(f"添加目录: {dir_arcname}")
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        # 计算文件在ZIP中的相对路径
                        arcname = os.path.relpath(file_path, dir_path)
                        # 添加文件到ZIP
                        zipf.write(file_path, arcname)
                        file_count += 1
            
            print(f"总共添加了 {file_count} 个文件和 {dir_count} 个目录到ZIP")
            
            # 返回ZIP文件供下载
            zip_size = os.path.getsize(temp_file.name)
            print(f"生成的ZIP文件大小: {zip_size} 字节")
            return FileResponse(
                path=temp_file.name,
                filename=f"{os.path.basename(output_dir)}.zip",
                media_type="application/zip",
                background=None  # 在响应发送后删除临时文件
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"下载文件失败，错误: {str(e)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"下载文件失败: {str(e)}")
    
    
    # 启动服务器
    server.run(ip='0.0.0.0', port=8000)