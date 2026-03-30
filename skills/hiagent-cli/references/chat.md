# chat 模块

目标：创建对话、发送消息（支持流式与非流式）。

## 关键点

- `<CMD>` 命令是 `cli-anything-hiagent`
- `chat create` 用于创建 conversation（返回 `app_conversation_id`）
- `chat send` 用于向 conversation 发送 query
- `--user-id` 可省略（会从 config 取默认值），缺省时使用 `cli-user`
- `--stream` 会输出事件列表（JSON 模式下为数组），适合调试；脚本化采集可以优先用非 stream

## 常用命令

创建对话：

```bash
<CMD> --json  chat create \
  --app-key <APP_KEY> \
  --user-id <USER_ID> \
  -v name=my_agent \
  -v version=1.0
```

发送消息（非流式）：

```bash
<CMD> --json  chat send \
  --app-key <APP_KEY> \
  --conversation-id <CONV_ID> \
  --user-id <USER_ID> \
  -q "Hello"
```

发送消息（流式）：

```bash
<CMD> --json  chat send \
  --app-key <APP_KEY> \
  --conversation-id <CONV_ID> \
  --user-id <USER_ID> \
  -q "Hello" \
  --stream
```

## 排障

- `Missing dependency: hiagent-api`：在仓库根目录执行 `uv sync --dev`，或确保安装了 `libs/api` 与 `agent-harness`
- `Failed to create conversation`：检查 app-key、endpoint、region 是否正确；必要时 `config show` 看 effective 配置
