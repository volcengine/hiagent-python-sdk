---
name: hiagent-cli
description: 当用户想使用 HiAgent 观测(observe)能力（API Token、Trace Spans 查询）时，务必使用这个技能给出可直接执行的 cli-anything-hiagent observe 命令与排障步骤。尤其适用于用户提到 agent-harness、cli_anything、--json、workspace-id、custom-app-id、VOLC_ACCESSKEY/VOLC_SECRETKEY、observe token、observe trace，以及希望用命令行(cli-anything-hiagent / python -m cli_anything.hiagent_sdk)。trace-ai-process / trace-ai-history / alert-ai-process / RuleID / IsStream
---

# hiagent-cli

## 作用域

- 用户提到以下任一关键词时优先使用本技能：
  - `cli-anything-hiagent`、`cli_anything`、`agent-harness`
  - `hiagent`、`HiAgent`、`hi-agent`
  - `--json`、`workspace-id`、`custom-app-id`
  - `VOLC_ACCESSKEY`、`VOLC_SECRETKEY`
  - `observe`、`observe token`、`observe trace`
  - `trace-ai-process`
  - `trace-ai-history`
  - `alert-ai-process`
  - `RuleID`
  - `IsStream`
  - `AI 分析`

> 本技能仅覆盖 `cli-anything-hiagent observe ...` 开头的命令；其他子命令不在范围内。

## 快速开始（环境准备）

### 1. 安装 CLI 工具

```bash
# 检查是否已安装，已经安装则跳过安装
which cli-anything-hiagent

# 安装方式
# 方式1: 通过仓库路径安装
pip install git+https://github.com/volcengine/hiagent-python-sdk.git@feat/skill#subdirectory=agent-harness

# 方式2: 本地开发安装
# 如果未下载仓库，先下载仓库
git clone https://github.com/volcengine/hiagent-python-sdk.git@feat/skill
# 到 hiagent-python-sdk 目录下执行以下命令
pip install -e agent-harness
```

### 2. 配置环境变量

```bash
# 优先使用环境变量，若未配置则使用配置文件
# 配置文件路径：~/.volc/.env（优先推荐） 或 ~/.volc/credentials 或 ~/.volc/config

# 必须配置（observe 模块强制要求）
export VOLC_ACCESSKEY="your_access_key"
export VOLC_SECRETKEY="your_secret_key"
```

## 常用命令速查

### Observe 观测

```bash
# 生成 API Token
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

### Observe AI 分析

```bash
# 对一个或多个 TraceID 触发 AI 分析（默认 SSE 流式）
cli-anything-hiagent --json observe trace-ai-process \
  --workspace-id your_workspace_id \
  --trace-id your_trace_id
```

```bash
# 查询某 TraceID 的 AI 分析历史记录
cli-anything-hiagent --json observe trace-ai-history \
  --workspace-id your_workspace_id \
  --trace-id your_trace_id \
  --page-size 10
```

```bash
# 对一条告警规则触发 AI 分析
cli-anything-hiagent --json observe alert-ai-process \
  --workspace-id your_workspace_id \
  --rule-id your_rule_id
```

详细说明见 references/observe-ai.md。

## 全局参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--json` | 输出 JSON 格式 | `--json` |

## 排障指南

### 问题1: `Volcengine credentials not found`

**原因**: AK/SK 未配置或未读取到

**解决**:
```bash
# 检查环境变量
echo $VOLC_ACCESSKEY
echo $VOLC_SECRETKEY

# 重新设置
export VOLC_ACCESSKEY="your_new_key"
export VOLC_SECRETKEY="your_new_secret"

# 或写入 ~/.volc/.env
```

### 问题2: 命令找不到

**原因**: 未安装或不在 PATH

**解决**:
```bash
# 检查是否已安装，已经安装则跳过安装
which cli-anything-hiagent

# 安装方式
# 方式1: 通过仓库路径安装
pip install git+https://github.com/volcengine/hiagent-python-sdk.git@feat/skill#subdirectory=agent-harness

# 方式2: 本地开发安装
# 如果未下载仓库，先下载仓库
git clone https://github.com/volcengine/hiagent-python-sdk.git@feat/skill
# 到 hiagent-python-sdk 目录下执行以下命令
pip install -e agent-harness
```
