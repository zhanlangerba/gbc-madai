#!/bin/bash

# GraphRAG环境设置脚本
# 用于在没有预构建虚拟环境的情况下设置GraphRAG功能

echo "🚀 开始设置GraphRAG环境..."

# 检查Python版本
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ 错误: 需要Python 3.8或更高版本，当前版本: $python_version"
    exit 1
fi

echo "✅ Python版本检查通过: $python_version"

# 创建虚拟环境
echo "📦 创建虚拟环境..."
python3 -m venv venv

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "⬆️ 升级pip..."
pip install --upgrade pip

# 安装GraphRAG核心依赖
echo "📚 安装GraphRAG依赖..."
pip install graphrag==0.3.0

# 安装数据处理依赖
echo "📊 安装数据处理依赖..."
pip install pandas numpy pyarrow

# 安装向量数据库依赖
echo "🔍 安装向量数据库依赖..."
pip install lancedb

# 安装机器学习依赖
echo "🤖 安装机器学习依赖..."
pip install scikit-learn

# 安装文本处理依赖
echo "📝 安装文本处理依赖..."
pip install nltk spacy

# 创建GraphRAG配置目录
echo "📁 创建配置目录..."
mkdir -p data
mkdir -p output
mkdir -p cache

# 创建示例配置文件
echo "⚙️ 创建示例配置文件..."
cat > settings.yaml << 'EOF'
# GraphRAG配置文件示例
# 请根据实际需求修改

encoding_model: cl100k_base
skip_workflows: []
llm:
  api_key: ${GRAPHRAG_API_KEY}
  type: openai_chat
  model: ${GRAPHRAG_MODEL_NAME:gpt-4o-mini}
  model_supports_json: true
  max_tokens: 4000
  temperature: 0
  top_p: 1

parallelization:
  stagger: 0.3
  num_threads: 50

async_mode: threaded

embeddings:
  async_mode: threaded
  llm:
    api_key: ${Embedding_API_KEY}
    type: openai_embedding
    model: ${Embedding_MODEL_NAME:text-embedding-3-small}
    max_tokens: 8191

input:
  type: file
  file_type: text
  base_dir: "data"
  file_encoding: utf-8
  file_pattern: ".*\\.txt$"

cache:
  type: file
  base_dir: "cache"

storage:
  type: file
  base_dir: "output"

chunk:
  size: 300
  overlap: 100
  group_by_columns: [id]

entity_extraction:
  prompt: "prompts/entity_extraction.txt"
  entity_types: [organization,person,geo,event]
  max_gleanings: 0

summarize_descriptions:
  prompt: "prompts/summarize_descriptions.txt"
  max_length: 500

claim_extraction:
  prompt: "prompts/claim_extraction.txt"
  description: "Any claims or facts that could be relevant to information discovery."
  max_gleanings: 0

community_report:
  prompt: "prompts/community_report.txt"
  max_length: 2000
  max_input_length: 8000

cluster_graph:
  max_cluster_size: 10

embed_graph:
  enabled: false

umap:
  enabled: false

snapshots:
  graphml: false
  raw_entities: false
  top_level_nodes: false

local_search:
  text_unit_prop: 0.5
  community_prop: 0.1
  conversation_history_max_turns: 5
  top_k_mapped_entities: 10
  top_k_relationships: 10
  max_tokens: 12000

global_search:
  max_tokens: 12000
  data_max_tokens: 12000
  map_max_tokens: 1000
  reduce_max_tokens: 2000
  concurrency: 32
EOF

echo "✅ GraphRAG环境设置完成！"
echo ""
echo "📋 下一步操作："
echo "1. 配置环境变量 (.env 文件):"
echo "   GRAPHRAG_API_KEY=your-api-key"
echo "   GRAPHRAG_MODEL_NAME=gpt-4o-mini"
echo "   Embedding_API_KEY=your-embedding-key"
echo "   Embedding_MODEL_NAME=text-embedding-3-small"
echo ""
echo "2. 将文本文件放入 data/ 目录"
echo "3. 运行索引构建: python -m graphrag.index --root ."
echo "4. 运行查询: python -m graphrag.query --root . --method local \"your question\""
echo ""
echo "🔗 更多信息请参考: https://github.com/microsoft/graphrag"
