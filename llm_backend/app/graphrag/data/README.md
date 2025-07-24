# GraphRAG 数据目录

这个目录用于存储GraphRAG的数据文件和配置。

## 目录结构

```
data/
├── input/          # 输入文档（.txt, .pdf等）
├── output/         # GraphRAG处理输出
├── cache/          # 缓存文件
├── prompts/        # 自定义提示词模板
└── logs/           # 日志文件
```

## 使用说明

1. **输入文档**: 将需要处理的文档放入 `input/` 目录
2. **配置文件**: 使用 `settings.yaml` 配置GraphRAG参数
3. **运行索引**: 执行 `python -m graphrag.index --root .`
4. **查询**: 执行 `python -m graphrag.query --root . --method local "your question"`

## 注意事项

- 此目录在开源版本中为空，避免包含敏感数据
- 实际使用时会自动创建所需的子目录
- 建议将此目录添加到 `.gitignore` 中（除了README文件）

## 更多信息

请参考项目根目录的 `LARGE_FILES_README.md` 了解如何设置GraphRAG环境。
