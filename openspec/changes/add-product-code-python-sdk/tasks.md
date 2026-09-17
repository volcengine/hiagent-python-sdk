## 1. 现状盘点与公共约束

- [x] 1.1 盘点 `libs/api`、`libs/eva`、`libs/hibot`、`libs/observe` 的客户端配置、请求构造和签名边界。
- [x] 1.2 确认 Header 常量、规范化、控制字符校验和显式 Header 优先规则。

## 2. hiagent-api 与 EVA

- [x] 2.1 为普通应用 API 增加 productCode 配置和请求 Header 注入。
- [x] 2.2 为生成式 TOP API 增加签名前共享 Header hook。
- [x] 2.3 让 EVA Client 透传 productCode，并更新 EVA examples。
- [x] 2.4 增加普通请求、TOP 签名和显式覆盖测试。

## 3. Hibot

- [x] 3.1 为 Hibot 配置增加可选 productCode。
- [x] 3.2 在 Hibot 签名前注入 productCode，并保持 stream/raw/action 请求一致。
- [x] 3.3 增加请求头、签名输入、空值和非法值测试。

## 4. Observe

- [x] 4.1 为 Observe Client 增加 productCode 配置。
- [x] 4.2 为 OTLP exporter 注入 productCode，并在刷新重建时保留。
- [x] 4.3 验证 CreateApiToken 请求体不增加 productCode。
- [x] 4.4 更新 Observe sample，并增加导出 Header 测试。

## 5. 验证与文档

- [x] 5.1 更新各模块 README、环境变量示例和版本说明。
- [ ] 5.2 执行 `uv run pytest`、`uv run ruff check` 和 workspace 构建（ruff 未安装；全仓库 pytest 被既有 agent-harness 导入问题阻断，模块测试已通过）。
- [ ] 5.3 使用明确 productCode 执行一次真实环境 smoke test，记录 URL、Header、状态码和响应协议，不记录凭据。
