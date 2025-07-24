# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""Input loading module."""

import numpy as np
import pandas as pd

from graphrag.callbacks.noop_workflow_callbacks import NoopWorkflowCallbacks
from graphrag.config.models.graph_rag_config import GraphRagConfig
from graphrag.index.input.factory import create_input
from graphrag.index.workflows.create_base_text_units import create_base_text_units
from graphrag.language_model.manager import ModelManager
from graphrag.language_model.protocol.base import EmbeddingModel
from graphrag.logger.base import ProgressLogger
from graphrag.prompt_tune.defaults import (
    LIMIT,
    N_SUBSET_MAX,
    K,
)
from graphrag.prompt_tune.types import DocSelectionType


async def _embed_chunks(
    text_chunks: pd.DataFrame,
    embedding_llm: EmbeddingModel,
    n_subset_max: int = N_SUBSET_MAX,
) -> tuple[pd.DataFrame, np.ndarray]:
    """Convert text chunks into dense text embeddings."""

    # 使用min(n_subset_max, len(text_chunks))确保不会尝试采样超过实际文本块数量的样本
    # 如果文本块数量少于n_subset_max，则使用所有文本块
    # 如果文本块数量多于n_subset_max，则随机采样n_subset_max个文本块
    sampled_text_chunks = text_chunks.sample(n=min(n_subset_max, len(text_chunks)))
    # 将文本单元转换为密集的文本嵌入
    embeddings = await embedding_llm.aembed_batch(sampled_text_chunks["text"].tolist())
    return text_chunks, np.array(embeddings)


def _sample_chunks_from_embeddings(
    text_chunks: pd.DataFrame,
    embeddings,
    k: int = K,
) -> pd.DataFrame:
    """Sample text chunks from embeddings."""

    # 通过计算所有文本嵌入的平均值，得到嵌入空间的中心点
    center = np.mean(embeddings, axis=0)
    # 计算每个文本嵌入与中心点之间的欧氏距离    
    distances = np.linalg.norm(embeddings - center, axis=1)
    # 根据距离排序，选择最近的 k 个文本嵌入
    nearest_indices = np.argsort(distances)[:k]

    return text_chunks.iloc[nearest_indices]


async def load_docs_in_chunks(
    root: str,
    config: GraphRagConfig,
    select_method: DocSelectionType,
    limit: int,
    logger: ProgressLogger,
    chunk_size: int,
    overlap: int,
    n_subset_max: int = N_SUBSET_MAX,
    k: int = K,
) -> list[str]:
    """Load docs into chunks for generating prompts."""
    embeddings_llm_settings = config.get_language_model_config(
        config.embed_text.model_id
    )

    # 1. 加载 input 下的源文档数据
    dataset = await create_input(config.input, logger, root)
    chunk_config = config.chunks

    # 2. 将源文档切分成多个 text_unit
    chunks_df = create_base_text_units(
        documents=dataset,
        callbacks=NoopWorkflowCallbacks(),
        group_by_columns=chunk_config.group_by_columns,
        size=chunk_size,
        overlap=overlap,
        encoding_model=chunk_config.encoding_model,
        strategy=chunk_config.strategy,
        prepend_metadata=chunk_config.prepend_metadata,
        chunk_size_includes_metadata=chunk_config.chunk_size_includes_metadata,
    )

    # 限制 选择的 text_unit 数量
    if limit <= 0 or limit > len(chunks_df):
        logger.warning(f"Limit out of range, using default number of chunks: {LIMIT}")  # noqa: G004
        limit = LIMIT

    # 3. 根据选择的文本单元类型，选择文本单元，其中：
    # 如果选择 DocSelectionType.TOP，则选择前 limit 个文本单元
    # 如果选择 DocSelectionType.RANDOM，则随机选择 limit 个文本单元
    # 如果选择 DocSelectionType.AUTO，则使用 k 和 n_subset_max 选择文本单元
    if select_method == DocSelectionType.TOP:
        chunks_df = chunks_df[:limit]
    elif select_method == DocSelectionType.RANDOM:
        chunks_df = chunks_df.sample(n=limit)
    elif select_method == DocSelectionType.AUTO:
        if k is None or k <= 0:
            msg = "k must be an integer > 0"
            raise ValueError(msg)
        
        # 注册 embedding 模型
        embedding_llm = ModelManager().register_embedding(
            name="prompt_tuning_embeddings",
            model_type=embeddings_llm_settings.type,
            config=embeddings_llm_settings,
            callbacks=NoopWorkflowCallbacks(),
            cache=None,
        )

        # 将 text_unit 转换为密集的文本嵌入
        chunks_df, embeddings = await _embed_chunks(
            chunks_df, embedding_llm, n_subset_max=n_subset_max
        )
        
        # 根据嵌入空间中的中心点，选择最近的 k 个文本单元
        chunks_df = _sample_chunks_from_embeddings(chunks_df, embeddings, k=k)

    # Convert the dataset to list form, so we have a list of documents
    return chunks_df["text"].tolist()
