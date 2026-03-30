# session 模块

目标：在本地持久化一组常用上下文（conversation/workflow/tool/dataset_ids），便于重复调用。

## 关键点

- `<CMD>` 命令是 `cli-anything-hiagent`
- 会话落盘路径：`<PROJECT_ROOT>/.hiagent/sessions/<NAME>.json`
- 建议全程加 `--json`，方便脚本化与可测试

## 常用命令

创建会话：

```bash
<CMD> --json  session create <NAME> \
  --conversation-id <CONV_ID> \
  --workflow-id <WF_ID> \
  --tool-id <TOOL_ID> \
  --dataset-ids ds-001,ds-002
```

列出会话：

```bash
<CMD> --json  session list
```

查看会话：

```bash
<CMD> --json  session show <NAME>
```

删除会话：

```bash
<CMD> --json  session delete <NAME>
```

## 常见错误

- Session 已存在：换一个 `<NAME>`，或先 `session delete <NAME>`
- Session 不存在：先 `session list` 确认名称，再 `show/delete`
