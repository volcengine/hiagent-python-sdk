# cli-anything-hiagent

HiAgent Python SDK 的命令行封装（cli-anything harness 风格），支持：

- 配置管理（project config + env override）
- 会话管理（session create/list/show/delete）
- Chat / Workflow / Tool / Knowledge 的 API 调用
- UP 文件上传/下载（调用真实 UP 服务）
- 默认 REPL（无子命令时进入）

## 安装

```bash
cd agent-harness
pip install -e .
或者 uv pip install -e agent-harness
```

## 前置依赖（硬依赖）

- Python >= 3.10
- `hiagent-api`、`hiagent-components`
- 火山引擎鉴权（用于签名请求）
  - 推荐使用环境变量：
    ```bash
    export VOLC_ACCESSKEY=...
    export VOLC_SECRETKEY=...
    ```
  - 或配置 `~/.volc/.env`

## 配置

支持环境变量覆盖项目配置（env 优先）：

```bash
export HIAGENT_TOP_ENDPOINT="https://open.volcengineapi.com"
export HIAGENT_REGION="cn-north-1"
export HIAGENT_AGENT_APP_KEY="your-app-key"
export HIAGENT_WORKSPACE_ID="your-workspace-id"
```

也可以写入项目配置：

```bash
cli-anything-hiagent config set --app-key "your-app-key" --workspace-id "your-workspace-id"
cli-anything-hiagent config show
```

## 使用

### REPL

```bash
cli-anything-hiagent
```

### JSON 输出

```bash
cli-anything-hiagent --json session list
```

### UP 文件

上传（返回 `path`，用于后续下载）：

```bash
cli-anything-hiagent file upload --file ./a.txt --expire 15h
```

下载（不传 `--key` 时会先自动获取 DownloadKey）：

```bash
cli-anything-hiagent file download --path "/path/from/upload" --output ./a-down.txt
```

## 测试

```bash
cd agent-harness
pip install -e ".[dev]"
python -m pytest cli_anything/hiagent_sdk/tests/ -v -s
或者 uv run python -m pytest agent-harness/cli_anything/hiagent_sdk/tests -v --tb=no

开启真实 UP E2E（可选）：
- export CLI_ANYTHING_E2E_REAL_API=1
- 配好 VOLC_ACCESSKEY/VOLC_SECRETKEY （或 ~/.volc/.env ）
- uv run python -m pytest agent-harness/cli_anything/hiagent_sdk/tests/test_full_e2e.py -v -s -m e2e
```

