"""A module containing run_csv function for CSV text chunking."""

from typing import List, Any

from graphrag.index.operations.chunk_text.typing import (
    ChunkingConfig, 
    TextChunk
)
from graphrag.logger.progress import ProgressTicker
from graphrag.index.text_splitting.text_splitting import TokenTextSplitter


def run_csv(
    texts: Any,
    config: ChunkingConfig,
    tick: ProgressTicker,
) -> List[TextChunk]:
    """
    按CSV行切分文本, 确保不会切断单行内容，并处理<ROW_SEP>分隔符
    
    参数:
        texts: 要切分的文本列表
        config: 切分配置
        tick: 进度条
        
    返回:
        切分后的文本块列表
    """
    results = []
    
    # 创建TokenTextSplitter用于计算token数量和切分超长文本
    token_splitter = TokenTextSplitter(chunk_size=config.size, chunk_overlap=config.overlap)
    
    # 处理文本列表
    for doc_idx, text in enumerate(texts):
        if not isinstance(text, str) or not text.strip():
            continue
            
        # 使用<ROW_SEP>分隔符拆分文本
        if "<ROW_SEP>" in text:
            rows = text.split("<ROW_SEP>")
            rows = [row.strip() for row in rows if row.strip()]
        else:
            # 如果没有<ROW_SEP>分隔符，按行分割
            rows = text.split("\n")
            rows = [row.strip() for row in rows if row.strip()]
        
        # 当前chunk的信息
        current_chunk_texts = []
        current_chunk_size = 0
        
        # 处理每一个评论块
        for row in rows:
            # 计算当前评论块的token数量
            row_tokens = token_splitter.num_tokens(row)
            
            # 如果单个评论块超过最大长度，使用TokenTextSplitter切分它
            if row_tokens > config.size:
                # 如果当前chunk不为空，先保存当前chunk
                if current_chunk_texts:
                    chunk_text = "\n\n".join(current_chunk_texts)
                    results.append(
                        TextChunk(
                            text_chunk=chunk_text,
                            source_doc_indices=[doc_idx],
                            n_tokens=current_chunk_size
                        )
                    )
                    current_chunk_texts = []
                    current_chunk_size = 0
                
                # 使用TokenTextSplitter切分超长评论块，考虑overlap
                split_chunks = token_splitter.split_text(row)
                
                # 计算每个切分后chunk的token数量
                for chunk in split_chunks:
                    chunk_tokens = token_splitter.num_tokens(chunk)
                    results.append(
                        TextChunk(
                            text_chunk=chunk,
                            source_doc_indices=[doc_idx],
                            n_tokens=chunk_tokens
                        )
                    )
                continue
            
            # 检查添加当前评论块是否会超过chunk_size
            if current_chunk_size + row_tokens > config.size and current_chunk_texts:
                # 保存当前chunk
                chunk_text = "\n\n".join(current_chunk_texts)
                results.append(
                    TextChunk(
                        text_chunk=chunk_text,
                        source_doc_indices=[doc_idx],
                        n_tokens=current_chunk_size
                    )
                )
                current_chunk_texts = []
                current_chunk_size = 0
            
            # 添加当前评论块到chunk
            current_chunk_texts.append(row)
            current_chunk_size += row_tokens
        
        # 保存最后一个chunk
        if current_chunk_texts:
            chunk_text = "\n\n".join(current_chunk_texts)
            results.append(
                TextChunk(
                    text_chunk=chunk_text,
                    source_doc_indices=[doc_idx],
                    n_tokens=current_chunk_size
                )
            )
        
        # 更新进度
        tick()
    
    return results