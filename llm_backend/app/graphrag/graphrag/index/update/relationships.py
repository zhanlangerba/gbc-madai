# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""Relationship related operations and utils for Incremental Indexing."""

import itertools

import numpy as np
import pandas as pd

from graphrag.data_model.schemas import RELATIONSHIPS_FINAL_COLUMNS


def _update_and_merge_relationships(
    old_relationships: pd.DataFrame, delta_relationships: pd.DataFrame
) -> pd.DataFrame:
    """Update and merge relationships.

    Parameters
    ----------
    old_relationships : pd.DataFrame
        The old relationships.
    delta_relationships : pd.DataFrame
        The delta relationships.

    Returns
    -------
    pd.DataFrame
        The updated relationships.
    """
    # Increment the human readable id in b by the max of a
    # Ensure both columns are integers
    delta_relationships["human_readable_id"] = delta_relationships[
        "human_readable_id"
    ].astype(int)
    old_relationships["human_readable_id"] = old_relationships[
        "human_readable_id"
    ].astype(int)

    # Adjust delta_relationships IDs to be greater than any in old_relationships
    initial_id = old_relationships["human_readable_id"].max() + 1
    delta_relationships["human_readable_id"] = np.arange(
        initial_id, initial_id + len(delta_relationships)
    )

    # 简单拼接新旧关系数据
    merged_relationships = pd.concat(
        [old_relationships, delta_relationships], ignore_index=True, copy=False
    )


    # 按源和目标分组：groupby(["source", "target"])
    aggregated = (
        merged_relationships.groupby(["source", "target"])
        .agg({
            "id": "first",              # 保留第一个ID
            "human_readable_id": "first", # 保留第一个可读ID
            "description": lambda x: list(x.astype(str)),  # 所有描述转为列表
            "text_unit_ids": lambda x: list(itertools.chain(*x.tolist())), # 合并文本单元ID
            "weight": "mean",           # 取权重平均值
            "combined_degree": "sum",   # 度数求和
        })
        .reset_index()
    )
    # Force the result into a DataFrame
    final_relationships: pd.DataFrame = pd.DataFrame(aggregated)

    # 重新计算源节点度数
    final_relationships["source_degree"] = final_relationships.groupby("source")[
        "target"
    ].transform("count")
    # 重新计算目标节点度数
    final_relationships["target_degree"] = final_relationships.groupby("target")[
        "source"
    ].transform("count")

    # 计算组合度数（源度数 + 目标度数）
    final_relationships["combined_degree"] = (
        final_relationships["source_degree"] + final_relationships["target_degree"]
    )

    return final_relationships.loc[
        :,
        RELATIONSHIPS_FINAL_COLUMNS,
    ]
