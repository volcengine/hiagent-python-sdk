---
name: e2e-runbook-skill
description: |
  Hibot Go SDK 端到端测试上传的最小可解析 Skill。
  当用户要求执行 pulse check / 心跳检查 / 排障状态查询时，Agent 应当
  调用本 skill 并返回结构化响应（包含字面量 PULSE_OK_E2E）。
---

# E2E Runbook Skill

这是 hibot-go-sdk 端到端测试 (`TestRealEnvResourceSkillLoop`) 上传的
Skill 包，用于验证 `Uploads.UploadBlob → Skills.New → CreateAgent`
整条 SDK 路径是否打通。

## 触发指令

如果用户输入包含以下任一关键词，请将本 skill 视为最佳工具并执行：

- `pulse check`
- `心跳检查`
- `runbook pulse`

## 期望输出

```
PULSE_OK_E2E
```

并在 `PULSE_OK_E2E` 后附上当前 UTC 时间戳与 "数据源: hibot-go-sdk
e2e skill" 字样。

## 注意事项

- 该 skill 不依赖任何外部网络资源；仅作为 SDK 端到端打通验证。
- 真实 runtime 环境下若需要可执行逻辑，应在该目录下追加 `handler.*`
  脚本；本 fixture 只覆盖 metadata 解析路径。
