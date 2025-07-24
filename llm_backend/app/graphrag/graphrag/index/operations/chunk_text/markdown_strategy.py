# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""Markdown-based text chunking strategy."""

import re
from collections.abc import Iterable
import logging
import csv
import os
from datetime import datetime
import json

from graphrag.config.models.chunking_config import ChunkingConfig
from graphrag.index.operations.chunk_text.typing import TextChunk
from graphrag.logger.progress import ProgressTicker
from graphrag.index.text_splitting.text_splitting import TokenTextSplitter

log = logging.getLogger(__name__)

def run_markdown(
    input: list[str],
    config: ChunkingConfig,
    tick: ProgressTicker,
) -> Iterable[TextChunk]:
    """Chunks text based on Markdown structure, keeping tables and images with their context."""
    
    # 导入TokenTextSplitter用于计算token数量
    token_splitter = TokenTextSplitter(chunk_size=config.size, chunk_overlap=config.overlap)
    
    # 创建一个列表来收集所有分块结果
    all_chunks = []
    
    # 增加块大小容忍度，允许块大幅超过配置的大小，以保持相同标题下的内容在一起
    size_tolerance = int(config.size * 0.5)  # 允许超过50%
    max_size_with_tolerance = config.size + size_tolerance
    
    # 设置一个绝对上限，防止块过大导致处理问题
    absolute_max_size = config.size * 2  # 最大不超过配置大小的2倍
    
    # 解析Markdown并提取元数据
    parsed_docs = []
    for doc_idx, text in enumerate(input):
        if not text:
            tick(1)
            continue
        
        # 解析文档，提取元数据
        parsed_elements = parse_markdown_with_metadata(text)
        parsed_docs.append({
            "doc_idx": doc_idx,
            "elements": parsed_elements,
            "original_text": text
        })
    
    # 预处理：按标题分组元素
    def group_by_headings(elements):
        groups = []
        current_group = []
        current_headings = []
        header_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        
        for element in elements:
            content = element["content"]
            header_match = header_pattern.match(content.strip())
            
            if header_match:
                # 如果是一级标题，开始新的组
                header_level = len(header_match.group(1))
                if header_level == 1 and current_group:
                    groups.append((current_headings, current_group))
                    current_group = []
                    current_headings = [content]
                else:
                    # 更新当前标题层次
                    while current_headings and len(header_pattern.match(current_headings[-1].strip()).group(1)) >= header_level:
                        current_headings.pop()
                    current_headings.append(content)
                    current_group.append(element)
            else:
                current_group.append(element)
        
        # 添加最后一组
        if current_group:
            groups.append((current_headings, current_group))
        
        return groups
    
    # 对每个解析后的文档进行分块
    for parsed_doc in parsed_docs:
        doc_idx = parsed_doc["doc_idx"]
        elements = parsed_doc["elements"]
        
        # 按标题分组
        grouped_elements = group_by_headings(elements)
        
        for headings, group_elements in grouped_elements:
            # 处理每个组
            current_chunk = []
            current_metadata = {}
            
            for element in group_elements:
                content = element["content"]
                metadata = element.get("metadata", {})
                
                # 添加内容到当前块
                current_chunk.append(content)
                
                # 合并元数据
                current_metadata.update(metadata)
                
                # 检查块大小
                chunk_text = "\n\n".join(current_chunk)
                chunk_size = token_splitter.num_tokens(chunk_text)
                
                # 如果块大小超过绝对上限，则分割
                if chunk_size > absolute_max_size:
                    # 创建一个新块
                    chunk_metadata = current_metadata.copy()
                    chunk_metadata["parent_headings"] = headings
                    
                    # 将元数据字典转换为字符串
                    metadata_str = json.dumps(chunk_metadata, ensure_ascii=False, indent=2)
                    full_text = f"METADATA:\n{metadata_str}\n\nCONTENT:\n{chunk_text}"
                    
                    # 收集分块结果
                    chunk = TextChunk(
                        text_chunk=full_text,
                        source_doc_indices=[doc_idx],
                        n_tokens=chunk_size,
                    )
                    all_chunks.append(chunk)
                    
                    # 返回分块结果
                    yield chunk
                    
                    # 重置当前块
                    current_chunk = []
                    current_metadata = {}
            
            # 处理组中的最后一个块
            if current_chunk:
                chunk_text = "\n\n".join(current_chunk)
                chunk_metadata = current_metadata.copy()
                chunk_metadata["parent_headings"] = headings
                
                # 将元数据字典转换为字符串
                metadata_str = json.dumps(chunk_metadata, ensure_ascii=False, indent=2)
                full_text = f"METADATA:\n{metadata_str}\n\nCONTENT:\n{chunk_text}"
                
                # 计算token数量
                n_tokens = token_splitter.num_tokens(chunk_text)
                
                # 收集分块结果
                chunk = TextChunk(
                    text_chunk=full_text,
                    source_doc_indices=[doc_idx],
                    n_tokens=n_tokens,
                )
                all_chunks.append(chunk)
                
                # 返回分块结果
                yield chunk
        
        tick(1)

    # 在所有分块完成后，将结果写入CSV文件
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = f"chunk_results_{timestamp}.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['doc_idx', 'chunk_idx', 'n_tokens', 'text_chunk'])
            
            for i, chunk in enumerate(all_chunks):
                csv_writer.writerow([
                    chunk.source_doc_indices[0] if chunk.source_doc_indices else 0,
                    i + 1,
                    chunk.n_tokens,
                    chunk.text_chunk
                ])
        
        print(f"分块结果已保存到: {os.path.abspath(csv_path)}")
        print(f"总共生成了 {len(all_chunks)} 个文本块")
    except Exception as e:
        print(f"保存CSV文件时出错: {str(e)}")

def parse_markdown_with_metadata(markdown: str) -> list[dict]:
    """解析Markdown文本，提取元数据和内容"""
    import re
    import json
    
    elements = []
    
    # 分割文本为段落
    paragraphs = markdown.split('\n\n')
    
    # 元数据模式，匹配HTML注释中的元数据
    metadata_pattern = re.compile(r'<!-- METADATA\n(.*?)\n-->', re.DOTALL)
    
    i = 0
    while i < len(paragraphs):
        paragraph = paragraphs[i]
        
        # 检查是否包含元数据
        metadata_match = metadata_pattern.search(paragraph)
        
        if metadata_match:
            # 提取元数据
            metadata_str = metadata_match.group(1)
            try:
                # 解析JSON格式的元数据
                metadata = json.loads(metadata_str)
                
                # 获取下一个段落作为内容
                if i + 1 < len(paragraphs):
                    content = paragraphs[i + 1]
                    elements.append({
                        "content": content,
                        "metadata": metadata
                    })
                    i += 2  # 跳过元数据和内容
                else:
                    # 如果没有下一个段落，只添加元数据
                    elements.append({
                        "content": "",
                        "metadata": metadata
                    })
                    i += 1
            except json.JSONDecodeError:
                # 如果元数据解析失败，将其作为普通内容处理
                elements.append({
                    "content": paragraph,
                    "metadata": {}
                })
                i += 1
        else:
            # 普通内容
            elements.append({
                "content": paragraph,
                "metadata": {}
            })
            i += 1
    
    return elements
    
