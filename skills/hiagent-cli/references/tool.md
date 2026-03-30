# tool 模块

目标：执行已归档工具（archived tool）。支持 `--input` 内联 JSON 或 `@file.json`。

## 关键点

- `<CMD>` 命令是 `cli-anything-hiagent`
- 必填：`--workspace-id`、`--tool-id`
- 可选：`--plugin-id`、`--name`，不传时 CLI 会先调用 `get_archived_tool` 补齐
- `--input` 为 JSON 字符串，或 `@path/to/input.json`

## 常用命令

内联 JSON 输入：

```bash
<CMD> --json  tool execute \
  --workspace-id <WORKSPACE_ID> \
  --tool-id <TOOL_ID> \
  --input '{"input":"test"}'
```

文件输入：

```bash
<CMD> --json  tool execute \
  --workspace-id <WORKSPACE_ID> \
  --tool-id <TOOL_ID> \
  --input @input.json
```

显式指定 plugin/name（避免额外请求）：

```bash
<CMD> --json  tool execute \
  --workspace-id <WORKSPACE_ID> \
  --tool-id <TOOL_ID> \
  --plugin-id <PLUGIN_ID> \
  --name "<TOOL_NAME>" \
  --input @input.json
```

## 排障

- JSON 解析失败：检查引号与转义；建议改用 `@input.json`
- tool_id 不存在：确认 workspace-id 是否正确；必要时在控制台查询工具列表再重试
