# hiagent-cli 离线评测断言

这些断言用于在无网络/无鉴权的情况下验证 CLI 基础能力与技能指引的可执行性。

## 断言集合

- **入口可用**：`<CMD> --version` 与 `<CMD> --help` 退出码为 0，且 help 输出包含 `config`/`session`。
- **不进入 REPL**：上述命令不会卡住等待交互输入（即为非交互式 Click 行为）。
- **配置可落盘**：`config set` 会在 `<project>/.hiagent/config.json` 写入 `app_key`/`workspace_id`。
- **配置可读取**：`config show --json` 的 `data` 同时包含 `effective` 与 `project` 两层配置。
- **会话可管理**：`session create/list/show/delete --json` 能完成完整生命周期，且 list 的 `data` 反映增删变化。

## 一键运行

在仓库根目录执行：

```bash
python skills/hiagent-cli/scripts/smoke_test.py
```
