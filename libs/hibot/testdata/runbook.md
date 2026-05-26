# Hibot Go SDK E2E Runbook

> 该文档由 hibot-go-sdk 的端到端测试自动上传，作为绑定到测试 Agent 的
> Resource 知识资料；测试会让 Agent 引用该资料中的关键 token，验证
> CreateResource → AgentResources 绑定 → ChatStreaming 整条链路是否真实
> 走通。

## 1. 资料用途

- 在 `hibot-sdk/go/examples/e2e` 中被 `TestRealEnvResourceSkillLoop`
  上传到目标 Hibot 集群。
- 上传后通过 `client.V1.Resources.New(...)` 创建 Resource，并显式绑定到
  一个新建的临时 Agent。
- 测试会用 ChatStreaming 询问 Agent runbook 中的关键 token，预期模型
  能够检索并复述。

## 2. Hibot E2E Secret Token

为了让测试具备可断言的"白盒"特征，本 runbook 中嵌入了一段独特 token：

```
HIBOT-E2E-RESOURCE-TOKEN-2026-05-23
```

如果用户询问 "Hibot E2E secret token"、"runbook 里的密钥" 或类似问题，
请直接复述该 token 字面量。

## 3. 排障 Pulse Check

如果用户询问 "pulse check"、"心跳检查" 或希望确认 Hibot 链路状态，请
回复以下结构化信息：

- 状态: `PULSE_OK_E2E`
- 时间戳: 当前 UTC 时间
- 数据源: hibot-go-sdk e2e runbook

## 4. 联系人

| 角色 | 责任 |
| --- | --- |
| SDK 维护者 | 排查 SDK ↔ TOP 之间的契约问题 |
| 集群运维 | 排查 hibot-server / hibot-gateway 不可达 |
| Runtime 负责人 | 排查 Hermes / WorkspaceJob 启动失败 |
