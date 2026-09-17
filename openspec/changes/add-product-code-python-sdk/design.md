## 上下文

Python SDK 是 workspace monorepo，包含 `libs/api`、`libs/eva`、`libs/hibot` 和 `libs/observe`。当前 `hiagent-api` 的普通应用请求在 `base.py` 中构造，生成式 TOP 请求在 `api.py`/各服务文件中签名；Hibot 在 `hibot/_request.py` 中统一构造并签名；Observe 使用 `hiagent_api.observe` 获取 Token，并由 OpenTelemetry OTLP HTTP exporter 导出 Trace；EVA 复用 `hiagent-api` 的签名客户端。

服务端约定的 Header 为 `X-Trace-Product-Code`。Header 必须出现在签名前的请求头集合中。Observe 的 `CreateApiToken` 请求体继续只包含现有字段，productCode 通过 Trace 导出请求传递。

## 目标 / 非目标

**目标：**

- 各 Python SDK 模块支持可选客户端级 productCode。
- productCode 经过统一的去空白和控制字符校验。
- 普通请求、TOP 签名请求和 OTLP 请求都按边界注入 Header。
- 请求级显式 Header 覆盖客户端默认值。
- 旧构造函数和未配置 productCode 的行为保持兼容。

**非目标：**

- 不在 SDK 中维护 productCode 白名单或验证业务有效性。
- 不修改 Observe Token 请求体和服务响应协议。
- 不修改服务端网关、IAM 或 observe 服务实现。
- 不将 productCode 写入请求 JSON body。

## 决策

1. **统一 Header 常量和规范化函数。** 在 `hiagent-api` 提供可复用的 productCode 工具；独立包（Hibot 若不依赖 api）在本包内提供等价的轻量工具，避免引入不必要的循环依赖。
2. **在签名边界注入。** `hiagent-api` 和 Hibot 在调用 Volcengine/自有 signer 前加入 Header；EVA 通过 `ApiClient` 的共享 hook 自动继承，不在每个 API 方法中重复添加。
3. **保留兼容构造方式。** Python 公开 Client 构造函数新增末尾可选参数或配置字段，默认 `None`；已有位置参数和调用代码不需要修改。
4. **大小写不敏感的覆盖规则。** 默认 Header 仅在请求头不存在同名字段时加入；显式请求头优先，避免不同 HTTP 客户端对 Header 大小写处理不一致。
5. **Observe 分离 Token 与 Trace。** Token 请求模型不增加 productCode；OTLP exporter 的 headers 统一添加 productCode，并确保 exporter 刷新/重建时继续保留。
6. **配置时拒绝危险值。** `None`/空白值视为未配置；包含 CR、LF 或其他 HTTP 控制字符的值立即抛出 `ValueError`。

## 风险 / 权衡

- [不同子包的配置模型不一致] → 分别在各包的公开配置入口适配，并用请求级测试覆盖最终 wire headers。
- [第三方 signer 只签固定 Header 集合] → 增加签名测试，确认 productCode 出现在签名 Header 列表和 Authorization 前的 canonical 输入中。
- [Observe exporter 重建时丢失 Header] → 将 productCode 保存在 exporter 实例字段，每次创建底层 exporter 都重新注入。
- [服务端暂不校验 productCode] → 测试只验证 Header 是否发出，不把随机/未知 productCode 视为客户端错误。

## 迁移计划

1. 先合并单元测试和请求构造改造。
2. 使用 `uv run pytest`、`uv run ruff check` 和 workspace 构建验证。
3. 由配置了有效凭据的环境执行可选 smoke test，日志不得输出凭据。
4. 如需回滚，移除客户端级 productCode 配置并恢复旧请求头集合；旧调用方式仍可继续运行。

## 开放问题

- 服务端是否会在后续版本强制校验 productCode 的业务合法性，需要由网关/IAM 协议进一步确认。
- 是否需要将 productCode 暴露为环境变量，仅作为 examples 的配置便利，不影响 SDK API 设计。
