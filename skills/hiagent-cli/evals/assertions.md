# hiagent-cli 离线评测断言

这些断言用于在无网络/无鉴权的情况下验证 CLI 基础能力与技能指引的可执行性。

## 断言集合

- **入口可用**：`<CMD> --version` 与 `<CMD> --help` 退出码为 0，且 help 输出包含 `observe`。
- **不进入 REPL**：上述命令不会卡住等待交互输入（即为非交互式 Click 行为）。
- **observe 鉴权前置**：未设置 `VOLC_ACCESSKEY/VOLC_SECRETKEY` 时，`observe token create` 与 `observe trace list` 的 `--json` 输出包含 `"success": false` 且 `message` 含 `Volcengine credentials not found`。
- **observe AI 鉴权前置**：未设置 `VOLC_ACCESSKEY/VOLC_SECRETKEY` 时，`observe trace-ai-process`、`observe trace-ai-history`、`observe alert-ai-process` 的 `--json` 输出包含 `"success": false` 且 `message` 含 `Volcengine credentials not found`。

## 一键运行

在仓库根目录执行：

```bash
python skills/hiagent-cli/scripts/smoke_test.py
```
