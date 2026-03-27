# 排障与开发态说明

## 入口与安装

优先用已安装命令：

```bash
cli-anything-hiagent --version
```

如果 PATH 找不到命令，使用模块入口（在 `agent-harness` 目录执行最稳）：

```bash
python -m cli_anything.hiagent_sdk --version
```

## 本仓库开发态依赖

常见报错：

- `Missing dependency: hiagent-api`
- `Missing dependency: hiagent-components`

在仓库根目录的一般修复路径：

```bash
uv sync --dev
uv pip install -e agent-harness
```

或分别安装：

```bash
pip install -e libs/api
pip install -e libs/components
pip install -e agent-harness
```

## hiagent_api 导入路径（monorepo 特殊处理）

CLI 启动时会尝试将以下候选目录加入 `sys.path`（若存在 `hiagent_api/`）：

- `<repo_root>/libs/api`
- `<cwd>/libs/api`

因此在 monorepo 中从仓库根目录或 `agent-harness` 目录执行通常都能找到 `hiagent_api`。

## --project 与落盘

如果用户说“我不想写入当前目录”，给出明确的 `--project`，并解释会在 `<project>/.hiagent/` 下创建文件。

## JSON 输出与脚本化

推荐 `--json`，输出结构为：

```json
{
  "success": true,
  "data": {},
  "message": "…",
  "timestamp": "…"
}
```

排查时优先看：

- `success` 是否为 true
- `message` 是否包含错误原因
