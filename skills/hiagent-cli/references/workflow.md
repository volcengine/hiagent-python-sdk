# workflow 模块

目标：获取工作流信息、运行工作流（同步/异步/流式）、查询 run 状态。

## 关键点

- `workflow get`：查看工作流元信息（优先用它确认 inputs 结构，避免猜字段）
- `workflow run`：
  - `--stream`：返回事件列表（调试友好）
  - `--async`：立刻返回 `run_id`，后续配合 `workflow status`
- `--input`：JSON 字符串或 `@file.json`

## 常用命令

获取工作流信息：

```bash
<CMD> --json --project <PROJECT_ROOT> workflow get \
  --workspace-id <WORKSPACE_ID> \
  --workflow-id <WF_ID>
```

同步运行（非流式）：

```bash
<CMD> --json --project <PROJECT_ROOT> workflow run \
  --app-key <APP_KEY> \
  --workspace-id <WORKSPACE_ID> \
  --workflow-id <WF_ID> \
  --user-id <USER_ID> \
  --input @input.json
```

流式运行：

```bash
<CMD> --json --project <PROJECT_ROOT> workflow run \
  --app-key <APP_KEY> \
  --workspace-id <WORKSPACE_ID> \
  --workflow-id <WF_ID> \
  --user-id <USER_ID> \
  --input @input.json \
  --stream
```

异步运行 + 查询状态：

```bash
<CMD> --json --project <PROJECT_ROOT> workflow run \
  --app-key <APP_KEY> \
  --workspace-id <WORKSPACE_ID> \
  --workflow-id <WF_ID> \
  --user-id <USER_ID> \
  --input @input.json \
  --async

<CMD> --json --project <PROJECT_ROOT> workflow status \
  --app-key <APP_KEY> \
  --run-id <RUN_ID> \
  --user-id <USER_ID>
```

## 排障

- 运行失败但无明确原因：先 `workflow get` 检查 inputs/参数是否匹配
- `user_id` 不一致：统一通过 `--user-id` 或 `config set --user-id ...`
