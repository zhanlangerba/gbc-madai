# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""Shared column processing for structured input files."""

import logging
import re
from typing import Any, Dict, List, Tuple, Optional
import os
import base64
import json
import asyncio

import requests
from pathlib import Path
from PIL import Image
import io
import time

import pandas as pd

from graphrag.config.models.input_config import InputConfig
from graphrag.index.utils.hashing import gen_sha512_hash
from graphrag.logger.base import ProgressLogger
from graphrag.storage.pipeline_storage import PipelineStorage

log = logging.getLogger(__name__)


async def load_files(
    loader: Any,
    config: InputConfig,
    storage: PipelineStorage,
    progress: ProgressLogger | None,
) -> pd.DataFrame:
    """Load files from storage and apply a loader function."""
    files = list(
        storage.find(
            re.compile(config.file_pattern),
            progress=progress,
            file_filter=config.file_filter,
        )
    )

    if len(files) == 0:
        msg = f"No {config.file_type} files found in {config.base_dir}"
        raise ValueError(msg)

    files_loaded = []
    
    for file, group in files:
        try:
            files_loaded.append(await loader(file, group))
        except Exception as e:  # noqa: BLE001 (catching Exception is fine here)
            log.warning("Warning! Error loading file %s. Skipping...", file)
            log.warning("Error: %s", e)

    log.info(
        "Found %d %s files, loading %d", len(files), config.file_type, len(files_loaded)
    )
    result = pd.concat(files_loaded)
    total_files_log = (
        f"Total number of unfiltered {config.file_type} rows: {len(result)}"
    )
    log.info(total_files_log)
    return result


def process_data_columns(
    documents: pd.DataFrame, config: InputConfig, path: str
) -> pd.DataFrame:
    """Process configured data columns of a DataFrame.
    
    核心的关键点是：如果 config.text_column 为 None，并且 documents 中没有 text 列，那么会终止Workflow
    """

    # 检查 documents 中是否存在 id 列。如果不存在，使用 apply 方法对每一行应用 gen_sha512_hash 函数，生成一个 SHA-512 哈希值作为 id 列的值。
    if "id" not in documents.columns:
        documents["id"] = documents.apply(
            lambda x: gen_sha512_hash(x, x.keys()), axis=1
        )

    # 如果 config.text_column 不为 None 且 DataFrame 中没有 text 列，接下来会检查 config.text_column 指定的列是否存在。
    # 如果不存在，记录警告信息，且终止Workflow
    if config.text_column is not None and "text" not in documents.columns:
        if config.text_column not in documents.columns:
            log.warning(
                "text_column %s not found in csv file %s",
                config.text_column,
                path,
            )
        else:
            # 如果存在，则将 text_column 中的值提取到新的 text 列中。
            documents["text"] = documents.apply(lambda x: x[config.text_column], axis=1)

    if config.title_column is not None:
        # 检查 config.title_column 是否不为 None
        if config.title_column not in documents.columns:
            log.warning(
                "title_column %s not found in csv file %s",
                config.title_column,
                path,
            )
        else:
            documents["title"] = documents.apply(
                lambda x: x[config.title_column], axis=1
            )
    else:
        documents["title"] = documents.apply(lambda _: path, axis=1)
    return documents


async def generate_image_descriptions(
    image_dir: Path, 
    output_file: Path = None,
    api_key: str = None,
    model: str = "gpt-4o",
    max_retries: int = 3,
    retry_delay: int = 2,
    batch_size: int = 10,
    max_tokens: int = 300,
    temperature: float = 0.7
) -> Dict[str, str]:
    """
    使用视觉模型为目录中的图片生成描述，并保存为键值对
    
    参数:
    - image_dir: 图片目录路径
    - output_file: 输出文件路径，如果为None则不保存到文件
    - api_key: OpenAI API密钥，如果为None则从环境变量获取
    - model: 使用的模型名称，默认为gpt-4o
    - max_retries: 最大重试次数
    - retry_delay: 重试延迟（秒）
    - batch_size: 批处理大小，每次处理的图片数量
    - max_tokens: 生成描述的最大token数
    - temperature: 生成描述的随机性，0-1之间
    
    返回:
    - 图片路径到描述的字典
    """
    # 获取API密钥
    if api_key is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("未提供API密钥，请设置OPENAI_API_KEY环境变量或直接传入api_key参数")
    
    # 检查图片目录是否存在
    if not image_dir.exists() or not image_dir.is_dir():
        log.warning(f"图片目录不存在或不是目录: {image_dir}")
        return {}
    
    # 获取所有图片文件
    image_files = []
    for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
        image_files.extend(list(image_dir.glob(f"*{ext}")))
        image_files.extend(list(image_dir.glob(f"*{ext.upper()}")))
    
    if not image_files:
        log.warning(f"图片目录中没有找到图片: {image_dir}")
        return {}
    
    log.info(f"找到 {len(image_files)} 张图片，开始生成描述")
    
    # 定义异步函数处理单个图片
    async def process_image(session, image_path):
        # 读取图片并转换为base64
        try:
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # 构建请求
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的图像描述助手。请详细描述图片中的内容，包括主要对象、场景、颜色、布局等关键信息。描述应该客观、准确、全面。"
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "请详细描述这张图片的内容:"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            # 发送请求并获取响应
            for attempt in range(max_retries):
                try:
                    async with session.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers=headers,
                        json=payload
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            description = result["choices"][0]["message"]["content"]
                            log.info(f"成功生成图片描述: {image_path.name}")
                            return str(image_path), description
                        else:
                            error_text = await response.text()
                            log.error(f"API请求失败 (尝试 {attempt+1}/{max_retries}): {response.status} - {error_text}")
                            if attempt < max_retries - 1:
                                await asyncio.sleep(retry_delay * (attempt + 1))  # 指数退避
                            else:
                                return str(image_path), f"[描述生成失败: API错误 {response.status}]"
                except Exception as e:
                    log.error(f"处理图片时出错 (尝试 {attempt+1}/{max_retries}): {str(e)}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay * (attempt + 1))
                    else:
                        return str(image_path), f"[描述生成失败: {str(e)}]"
        except Exception as e:
            log.error(f"读取图片失败: {image_path} - {str(e)}")
            return str(image_path), f"[描述生成失败: 无法读取图片 - {str(e)}]"
    
    # # 批量处理图片
    # async def process_batch(batch):
    #     async with aiohttp.ClientSession() as session:
    #         tasks = [process_image(session, img_path) for img_path in batch]
    #         return await asyncio.gather(*tasks)
    
    # 分批处理所有图片
    descriptions = {}
    batches = [image_files[i:i+batch_size] for i in range(0, len(image_files), batch_size)]
    
    for i, batch in enumerate(batches):
        log.info(f"处理批次 {i+1}/{len(batches)}, 包含 {len(batch)} 张图片")
        loop = asyncio.get_event_loop()
        batch_results = loop.run_until_complete(process_batch(batch))
        
        # 更新描述字典
        for img_path, description in batch_results:
            descriptions[img_path] = description
        
        # 每批处理完后保存一次，防止中途失败
        if output_file is not None:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(descriptions, f, ensure_ascii=False, indent=2)
            log.info(f"已将当前描述保存到: {output_file}")
        
        # 批次之间添加延迟，避免API限制
        if i < len(batches) - 1:
            time.sleep(1)
    
    log.info(f"所有图片处理完成，共生成 {len(descriptions)} 个描述")
    
    # 最终保存
    if output_file is not None and descriptions:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(descriptions, f, ensure_ascii=False, indent=2)
        log.info(f"所有描述已保存到: {output_file}")
    
    return descriptions


def generate_image_descriptions_sync(
    config:InputConfig,
    image_dir: Path, 
    output_file: Path = None,
    api_key: str = None,
    model: str = "gpt-4o",
    max_retries: int = 3,
    retry_delay: int = 2,
    max_tokens: int = 300,
    temperature: float = 0.7,
    image_info: dict = None  # 添加参数接收图片信息
) -> Dict[str, str]:
    """
    使用视觉模型为目录中的图片生成描述的同步版本
    
    参数与异步版本相同，但一次只处理一张图片
    新增image_info参数用于传递图片的上下文信息
    """
    # 获取API密钥和配置
    api_key = config.image_description_api_key
    model = config.image_description_model
    base_url = config.image_description_base_url if hasattr(config, "image_description_base_url") else "https://api.openai.com/v1"
    
    log.info(f"使用模型: {model}, 基础URL: {base_url}")
    
    # 检查图片目录是否存在
    if not image_dir.exists() or not image_dir.is_dir():
        log.warning(f"图片目录不存在或不是目录: {image_dir}")
        return {}
    
    # 获取所有图片文件
    image_files = []
    for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
        image_files.extend(list(image_dir.glob(f"*{ext}")))
        image_files.extend(list(image_dir.glob(f"*{ext.upper()}")))
    
    if not image_files:
        log.warning(f"图片目录中没有找到图片: {image_dir}")
        return {}
    
    log.info(f"找到 {len(image_files)} 张图片，开始生成描述")
    
    descriptions = {}
    
    try:
        # 导入OpenAI API
        from openai import OpenAI
        
        # 初始化OpenAI客户端
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        
        # 创建图片路径到上下文的映射
        context_map = {}
        if image_info and image_info.get("images"):
            for img in image_info.get("images", []):
                if img.get("path"):
                    img_name = Path(img.get("path")).name
                    context_map[img_name] = {
                        "context_before": img.get("context_before", ""),
                        "context_after": img.get("context_after", ""),
                        "caption": img.get("caption", "")
                    }
        
        for i, image_path in enumerate(image_files):
            log.info(f"处理图片 {i+1}/{len(image_files)}: {image_path.name}")
            
            # 获取该图片的上下文信息
            img_name = image_path.name
            context_before = ""
            context_after = ""
            caption = ""
            
            if img_name in context_map:
                context_before = context_map[img_name].get("context_before", "")
                context_after = context_map[img_name].get("context_after", "")
                caption = context_map[img_name].get("caption", "")
            
            # 读取图片并转换为base64
            try:
                with open(image_path, "rb") as image_file:
                    image_data = base64.b64encode(image_file.read()).decode('utf-8')
                
                # 构建更完善的系统提示
                system_prompt = """你是一个专业的图像描述助手。请详细描述图片中的内容，包括主要对象、场景、颜色、布局等关键信息。描述应该客观、准确、全面。

我会提供图片的前后文本上下文，但请注意：
1. 上下文信息不一定与图片直接相关，要谨慎分析
2. 不要仅基于上下文猜测图片内容，优先描述你实际看到的内容
3. 如果上下文与图片内容看起来有相关性，可以在描述中提及这种关系
4. 如果上下文与图片内容明显不相关，请忽略上下文，专注于描述图片本身"""

                # 构建用户消息
                user_content = []
                user_content.append({"type": "text", "text": "请详细描述这张图片的内容:"})
                
                # 添加图片前后上下文
                context_text = ""
                if context_before:
                    context_text += f"图片前文: {context_before}\n\n"
                if context_after:
                    context_text += f"图片后文: {context_after}\n\n"
                if caption:
                    context_text += f"图片标题: {caption}\n\n"
                
                if context_text:
                    user_content.append({"type": "text", "text": context_text})
                
                # 添加图片
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}"
                    }
                })
                
                # 构建完整的消息列表
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
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
                        descriptions[str(image_path)] = description
                        log.info(f"成功生成图片描述: {image_path.name}")
                        success = True
                        break
                        
                    except Exception as e:
                        log.error(f"处理图片时出错 (尝试 {attempt+1}/{max_retries}): {str(e)}")
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay * (attempt + 1))
                
                if not success:
                    descriptions[str(image_path)] = f"[描述生成失败: 多次尝试后仍然失败]"
            
            except Exception as e:
                log.error(f"读取图片失败: {image_path} - {str(e)}")
                descriptions[str(image_path)] = f"[描述生成失败: 无法读取图片 - {str(e)}]"
            
            # 每处理完一张图片后保存一次，防止中途失败
            if output_file is not None:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(descriptions, f, ensure_ascii=False, indent=2)
            
            # 添加延迟，避免API限制
            if i < len(image_files) - 1:
                time.sleep(1)
    
    except ImportError:
        log.error("导入OpenAI模块失败，无法生成图片描述")
        for image_path in image_files:
            descriptions[str(image_path)] = "描述生成功能不可用 (OpenAI模块未安装)"
    except Exception as e:
        log.error(f"初始化OpenAI客户端失败: {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        for image_path in image_files:
            descriptions[str(image_path)] = f"描述生成失败: {str(e)}"
    
    log.info(f"所有图片处理完成，共生成 {len(descriptions)} 个描述")
    
    # 最终保存
    if output_file is not None and descriptions:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(descriptions, f, ensure_ascii=False, indent=2)
        log.info(f"所有描述已保存到: {output_file}")
    
    return descriptions

