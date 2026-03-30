# config 模块

目标：写入/读取项目级配置，理解 effective（环境变量覆盖后）与 project（落盘）两层配置来源。

## 关键点

- `<CMD>` 命令是 `cli-anything-hiagent`
- 配置落盘路径：`<PROJECT_ROOT>/.hiagent/config.json`
- effective 优先级：环境变量与 `~/.volc/.env` 覆盖项目配置
- 推荐始终显式使用 ``，避免污染当前目录

## 常用命令

查看两层配置：

```bash
<CMD> --json  config show
```

写入项目配置（只写入你传入的字段）：

```bash
<CMD> --json  config set \
  --app-key <APP_KEY> \
  --workspace-id <WORKSPACE_ID> \
  --endpoint <HIAGENT_TOP_ENDPOINT> \
  --region <HIAGENT_REGION> \
  --app-base-url <APP_BASE_URL> \
  --user-id <USER_ID>
```

## 环境变量速查

```bash
export HIAGENT_TOP_ENDPOINT="https://open.volcengineapi.com"
export HIAGENT_REGION="cn-north-1"
export HIAGENT_AGENT_APP_KEY="<APP_KEY>"
export HIAGENT_WORKSPACE_ID="<WORKSPACE_ID>"
export HIAGENT_USER_ID="<USER_ID>"
```

如果用户反馈“我明明 set 了，但 show 里不是我想要的值”，优先判断是否被环境变量覆盖。
