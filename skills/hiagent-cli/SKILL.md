# hiagent-cli

> 当用户想管理 HiAgent 配置、观测(observe)时、会话(session)、对话(chat)、工作流(workflow)、工具(tool)、知识库(knowledge)、文件上传下载(up)时，务必使用这个技能给出可直接执行的命令与排障步骤。尤其适用于用户提到 agent-harness、cli_anything、--project、--json、app-key、workspace-id、VOLC_ACCESSKEY/VOLC_SECRETKEY、.hiagent/config.json，以及希望用命令行(cli-anything-hiagent / python -m cli_anything.hiagent_sdk)。

## 作用域

- 用户提到以下任一关键词时优先使用本技能：
  - `cli-anything-hiagent`、`cli_anything`、`agent-harness`
  - `hiagent`、`HiAgent`、`hi-agent`
  - `--project`、`--json`、`app-key`、`workspace-id`
  - `VOLC_ACCESSKEY`、`VOLC_SECRETKEY`
  - `.hiagent/config.json`
  - `session`、`chat`、`workflow`、`tool`、`knowledge`、`up`、`observe`

## 快速开始（环境准备）

### 1. 安装 CLI 工具

```bash
# 检查是否已安装，已经安装则跳过安装
which cli-anything-hiagent

# 安装方式
# 方式1: 通过仓库路径安装
pip install git+https://github.com/volcengine/hiagent-python-sdk.git#subdirectory=agent-harness

# 方式2: 本地开发安装
cd 到下载的 hiagent-python-sdk 目录, 执行以下命令安装
pip install -e agent-harness
```

### 2. 配置环境变量

```bash
# 优先使用环境变量，若未配置则使用配置文件
# 配置文件路径：~/.volc/.env（优先推荐） 或 ~/.volc/credentials 或 ~/.volc/config

# 必须配置
export VOLC_ACCESSKEY="your_access_key"
export VOLC_SECRETKEY="your_secret_key"

# 可选配置
export HIAGENT_PROJECT="default"           # 默认项目
export HIAGENT_WORKSPACE="your_workspace"  # 默认工作空间
```

### 3. 初始化配置

```bash
# 配置项目
cli-anything-hiagent config set-project your_project
```

## 常用命令速查

### Session 管理

```bash
# 列出会话
cli-anything-hiagent session list --project your_project

# 创建会话
cli-anything-hiagent session create --project your_project --name "新会话"

# 获取会话详情
cli-anything-hiagent session get --project your_project --session-id xxx

# 删除会话
cli-anything-hiagent session delete --project your_project --session-id xxx
```

### Chat 对话

```bash
# 发送消息
cli-anything-hiagent chat send --project your_project --session-id xxx --message "你好"

# 流式对话
cli-anything-hiagent chat send --project your_project --session-id xxx --message "你好" --stream
```

### Workflow 工作流

```bash
# 列出工作流
cli-anything-hiagent workflow list --project your_project

# 运行工作流
cli-anything-hiagent workflow run --project your_project --workflow-id xxx --input '{"key": "value"}'

# 获取工作流详情
cli-anything-hiagent workflow get --project your_project --workflow-id xxx
```

### Tool 工具

```bash
# 列出工具
cli-anything-hiagent tool list --project your_project

# 调用工具
cli-anything-hiagent tool call --project your_project --tool-id xxx --params '{"param1": "value1"}'
```

### Knowledge 知识库

```bash
# 列出知识库
cli-anything-hiagent knowledge list --project your_project

# 上传文档
cli-anything-hiagent knowledge upload --project your_project --knowledge-id xxx --file /path/to/file.pdf

# 搜索知识库
cli-anything-hiagent knowledge search --project your_project --knowledge-id xxx --query "搜索内容"
```

### Observe 观测

```bash
# 生成 API Token，
# --workspace-id 空间id，必填参数;
# --custom-app-id 自定义应用id，必填参数
cli-anything-hiagent observe token create --workspace-id your_workspace_id --custom-app-id your_custom_app_id
```

```bash
# 列出 Trace Spans, trace 详情
# 输出 JSON 格式，--workspace-id 必填参数，其他参数可选填
cli-anything-hiagent --json observe trace list \
  --workspace-id your_workspace_id \
  --page-size 10 \
  --sort-by StartTime \
  --sort-order Desc
```

### 文件上传下载 (up)

```bash
# 上传文件
cli-anything-hiagent up upload --project your_project --file /path/to/file

# 下载文件
cli-anything-hiagent up download --project your_project --file-id xxx --output /path/to/save
```

## 全局参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--project` | 项目名称 | `--project my-project` |
| `--json` | 输出 JSON 格式 | `--json` |
| `--debug` | 开启调试模式 | `--debug` |
| `--config` | 指定配置文件 | `--config ~/.hiagent/config.json` |

## 排障指南

### 问题1: `401 Unauthorized`

**原因**: AK/SK 无效或过期

**解决**:
```bash
# 检查环境变量
echo $VOLC_ACCESSKEY
echo $VOLC_SECRETKEY

# 重新设置
export VOLC_ACCESSKEY="your_new_key"
export VOLC_SECRETKEY="your_new_secret"
```

### 问题2: `Project not found`

**原因**: 项目不存在或无权限

**解决**:
```bash
# 查看可用项目
cli-anything-hiagent project list

# 切换项目
cli-anything-hiagent config set-project correct_project
```

### 问题3: `Workspace not found`

**原因**: 工作空间 ID 错误

**解决**:
```bash
# 在项目配置中查看正确的工作空间 ID
cli-anything-hiagent config show
```

### 问题4: 命令找不到

**原因**: 未安装或不在 PATH

**解决**:
```bash
# 检查是否已安装，已经安装则跳过安装
which cli-anything-hiagent

# 安装方式
# 方式1: 通过仓库路径安装
pip install git+https://github.com/volcengine/hiagent-python-sdk.git#subdirectory=agent-harness

# 方式2: 本地开发安装
cd 到下载的 hiagent-python-sdk 目录, 执行以下命令安装
pip install -e agent-harness
```
