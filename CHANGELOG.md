# 更新日志

所有项目的显著变更都将记录在此文件中。


## [v3.0] - 【AssistGen】
### 基础知识
- DeepSeek Function Calling 工具调用


### 功能版本
- 用户历史会话记录管理
  - 会话删除
  - 会话名称修改


### 功能优化
- 问答/深度思考接口增加user_id、conversation_id参数
- 问答/深度思考接口增加回调机制
- 问答/深度思考接口增加redis上下文缓存管理

### 问题修复
- 解决 init_db.py脚本异步运行问题



## [v3.0] - 【AssistGen】
### 基础知识
- DeepSeek API 硬盘上下文缓存 
- Redis 内存数据库安装及启动方法
- 基于 Redis 的Prompt cache缓存管理
    - 完全匹配规则
    - 基于语义的向量匹配规则

### 功能版本
- 用户历史会话记录管理
  - Mysql 会话表、消息表结构设计与接入
  - 左侧会话记录列表展示


### 功能优化
- 问答/深度思考接口增加user_id、conversation_id参数
- 问答/深度思考接口增加回调机制
- 问答/深度思考接口增加redis上下文缓存管理

### 问题修复
- 解决 init_db.py脚本异步运行问题

## [v2.0] - 【AssistGen】Ch 2.1 ~ Ch 2.5
### 基础知识
- FastAPI基础知识
- Mysql 数据库接入
- Ollama 压力测试

### 功能版本
- Mysql 表结构设计与初始化脚本 - 用户表
- 实现用户注册、登入、登出
- 实现 DeepSeek v3 & Ollama + 问答类模型（如 qwen2.5）流式问答
- 实现 DeepSeek R1 & Ollama + Deepseek r1  深度思考流式问答 
- 实现 Deepseek v3  + Serper API 实时联网检索 Baseline
- 实现 Deepseek v3 + sentence-transformers 本地知识库问答 Baseline

### 功能优化
- 优化项目启动文件`run.py`

## [v1.0] - 【AssistGen】Ch 1.1 ~ Ch 1.6
### 基础知识
- Ollama 本地部署 DeepSeek R1 模型完整流程
- Ollama REST API 核心接口：api/generate & api/chat
- Ollama 兼容 OpenAI API 接口规范
- Deepseek v3 & R1 在线 API 调用方法