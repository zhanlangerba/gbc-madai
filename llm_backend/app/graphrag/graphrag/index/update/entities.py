# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""Entity related operations and utils for Incremental Indexing."""

import itertools

import numpy as np
import pandas as pd

from graphrag.data_model.schemas import ENTITIES_FINAL_COLUMNS


def _group_and_resolve_entities(
    old_entities_df: pd.DataFrame, delta_entities_df: pd.DataFrame
) -> tuple[pd.DataFrame, dict]:
    """Group and resolve entities.

    Parameters
    ----------
    old_entities_df : pd.DataFrame
        The first dataframe.
    delta_entities_df : pd.DataFrame
        The delta dataframe.

    Returns
    -------
    pd.DataFrame
        The resolved dataframe.
    dict
        The id mapping for existing entities. In the form of {df_b.id: df_a.id}.
    """
    # 基于 title 字段合并新旧实体， 创建新旧ID的映射关系 {新ID: 旧ID}
    merged = delta_entities_df[["id", "title"]].merge(
        old_entities_df[["id", "title"]],
        on="title",
        suffixes=("_B", "_A"),
        copy=False,
    )
    id_mapping = dict(zip(merged["id_B"], merged["id_A"], strict=True))

    # Increment human readable id in b by the max of a
    initial_id = old_entities_df["human_readable_id"].max() + 1
    delta_entities_df["human_readable_id"] = np.arange(
        initial_id, initial_id + len(delta_entities_df)
    )
    # Concat A and B
    combined = pd.concat(
        [old_entities_df, delta_entities_df], ignore_index=True, copy=False
    )

    aggregated = (
        combined.groupby("title")
        .agg({
            "id": "first",                # 保留第一个ID
            "type": "first",             # 保留第一个类型
            "human_readable_id": "first", # 保留第一个人类可读ID
            "description": lambda x: list(x.astype(str)),  # 所有描述转为列表
            "text_unit_ids": lambda x: list(itertools.chain(*x.tolist())), # 合并文本单元ID
            "degree": "first",           # 保留第一个度数
            "x": "first",                # 保留第一个x坐标
            "y": "first",                # 保留第一个y坐标
        })
        .reset_index()
    )

    # recompute frequency to include new text units
    aggregated["frequency"] = aggregated["text_unit_ids"].apply(len)

    # Force the result into a DataFrame
    resolved: pd.DataFrame = pd.DataFrame(aggregated)

    # Modify column order to keep consistency
    resolved = resolved.loc[:, ENTITIES_FINAL_COLUMNS]

    return resolved, id_mapping
