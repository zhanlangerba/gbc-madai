@echo off
chcp 65001 >nul
echo 🚀 开始设置GraphRAG环境...

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.8或更高版本
    pause
    exit /b 1
)

echo ✅ Python检查通过

REM 创建虚拟环境
echo 📦 创建虚拟环境...
python -m venv venv

REM 激活虚拟环境
echo 🔄 激活虚拟环境...
call venv\Scripts\activate.bat

REM 升级pip
echo ⬆️ 升级pip...
python -m pip install --upgrade pip

REM 安装GraphRAG核心依赖
echo 📚 安装GraphRAG依赖...
pip install graphrag==0.3.0

REM 安装数据处理依赖
echo 📊 安装数据处理依赖...
pip install pandas numpy pyarrow

REM 安装向量数据库依赖
echo 🔍 安装向量数据库依赖...
pip install lancedb

REM 安装机器学习依赖
echo 🤖 安装机器学习依赖...
pip install scikit-learn

REM 安装文本处理依赖
echo 📝 安装文本处理依赖...
pip install nltk spacy

REM 创建GraphRAG配置目录
echo 📁 创建配置目录...
if not exist "data" mkdir data
if not exist "output" mkdir output
if not exist "cache" mkdir cache

REM 创建示例配置文件
echo ⚙️ 创建示例配置文件...
(
echo # GraphRAG配置文件示例
echo # 请根据实际需求修改
echo.
echo encoding_model: cl100k_base
echo skip_workflows: []
echo llm:
echo   api_key: ${GRAPHRAG_API_KEY}
echo   type: openai_chat
echo   model: ${GRAPHRAG_MODEL_NAME:gpt-4o-mini}
echo   model_supports_json: true
echo   max_tokens: 4000
echo   temperature: 0
echo   top_p: 1
echo.
echo parallelization:
echo   stagger: 0.3
echo   num_threads: 50
echo.
echo async_mode: threaded
echo.
echo embeddings:
echo   async_mode: threaded
echo   llm:
echo     api_key: ${Embedding_API_KEY}
echo     type: openai_embedding
echo     model: ${Embedding_MODEL_NAME:text-embedding-3-small}
echo     max_tokens: 8191
echo.
echo input:
echo   type: file
echo   file_type: text
echo   base_dir: "data"
echo   file_encoding: utf-8
echo   file_pattern: ".*\\.txt$"
echo.
echo cache:
echo   type: file
echo   base_dir: "cache"
echo.
echo storage:
echo   type: file
echo   base_dir: "output"
echo.
echo chunk:
echo   size: 300
echo   overlap: 100
echo   group_by_columns: [id]
echo.
echo entity_extraction:
echo   prompt: "prompts/entity_extraction.txt"
echo   entity_types: [organization,person,geo,event]
echo   max_gleanings: 0
echo.
echo summarize_descriptions:
echo   prompt: "prompts/summarize_descriptions.txt"
echo   max_length: 500
echo.
echo claim_extraction:
echo   prompt: "prompts/claim_extraction.txt"
echo   description: "Any claims or facts that could be relevant to information discovery."
echo   max_gleanings: 0
echo.
echo community_report:
echo   prompt: "prompts/community_report.txt"
echo   max_length: 2000
echo   max_input_length: 8000
echo.
echo cluster_graph:
echo   max_cluster_size: 10
echo.
echo embed_graph:
echo   enabled: false
echo.
echo umap:
echo   enabled: false
echo.
echo snapshots:
echo   graphml: false
echo   raw_entities: false
echo   top_level_nodes: false
echo.
echo local_search:
echo   text_unit_prop: 0.5
echo   community_prop: 0.1
echo   conversation_history_max_turns: 5
echo   top_k_mapped_entities: 10
echo   top_k_relationships: 10
echo   max_tokens: 12000
echo.
echo global_search:
echo   max_tokens: 12000
echo   data_max_tokens: 12000
echo   map_max_tokens: 1000
echo   reduce_max_tokens: 2000
echo   concurrency: 32
) > settings.yaml

echo ✅ GraphRAG环境设置完成！
echo.
echo 📋 下一步操作：
echo 1. 配置环境变量 (.env 文件):
echo    GRAPHRAG_API_KEY=your-api-key
echo    GRAPHRAG_MODEL_NAME=gpt-4o-mini
echo    Embedding_API_KEY=your-embedding-key
echo    Embedding_MODEL_NAME=text-embedding-3-small
echo.
echo 2. 将文本文件放入 data/ 目录
echo 3. 运行索引构建: python -m graphrag.index --root .
echo 4. 运行查询: python -m graphrag.query --root . --method local "your question"
echo.
echo 🔗 更多信息请参考: https://github.com/microsoft/graphrag
echo.
pause
