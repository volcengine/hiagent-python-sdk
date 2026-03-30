# knowledge 模块

目标：对知识库数据集执行检索（retrieve）。

## 关键点

- `<CMD>` 命令是 `cli-anything-hiagent`
- 使用 `hiagent_components.retriever.KnowledgeRetriever` 进行检索
- `--dataset-ids` 为逗号分隔：`ds-001,ds-002`
- `--top-k`、`--score-threshold` 控制召回数量与阈值

## 常用命令

```bash
<CMD> --json  knowledge retrieve \
  --workspace-id <WORKSPACE_ID> \
  --dataset-ids ds-001,ds-002 \
  -q "query" \
  --top-k 5 \
  --score-threshold 0.5
```

## 排障

- 返回为空：降低 `--score-threshold` 或提高 `--top-k`；确认 dataset-ids 是否正确
- 依赖缺失：`Missing dependency: hiagent-components` 时需安装 `libs/components`
