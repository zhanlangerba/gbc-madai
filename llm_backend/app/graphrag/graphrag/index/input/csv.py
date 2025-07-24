# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""A module containing load method definition."""

import logging
from io import BytesIO

import pandas as pd

from graphrag.config.models.input_config import InputConfig
from graphrag.index.input.util import load_files, process_data_columns
from graphrag.logger.base import ProgressLogger
from graphrag.storage.pipeline_storage import PipelineStorage

log = logging.getLogger(__name__)


async def load_csv(
    config: InputConfig,
    progress: ProgressLogger | None,
    storage: PipelineStorage,
) -> pd.DataFrame:
    """Load csv inputs from a directory."""
    log.info("Loading csv files from %s", config.base_dir)

    print(f"Loading csv files from {config.base_dir}")
    async def load_file(path: str, group: dict | None) -> pd.DataFrame:
        if group is None:
            group = {}
        buffer = BytesIO(await storage.get(path, as_bytes=True))
        data = pd.read_csv(buffer, encoding=config.encoding)
        # 这段代码会检查 group 字典中是否有额外的键（即额外的列）。如果有，它会将这些额外的键的值添加到 DataFrame 中，作为新的列。
        # 其中group字典中的键 就是我们之前讲的：通过file_pattern + file_filter过滤出来的列
        additional_keys = group.keys()
        if len(additional_keys) > 0:
            data[[*additional_keys]] = data.apply(
                lambda _row: pd.Series([group[key] for key in additional_keys]), axis=1
            )

        data = process_data_columns(data, config, path)
        
        creation_date = await storage.get_creation_date(path)
        data["creation_date"] = data.apply(lambda _: creation_date, axis=1)
        return data
 
    return await load_files(load_file, config, storage, progress)
