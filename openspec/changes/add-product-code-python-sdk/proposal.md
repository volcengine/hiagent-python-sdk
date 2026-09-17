## 为什么

TOP 网关和 Observe Trace 链路新增了按产品路由/识别的 `productCode` Header。Python SDK 当前各模块没有统一配置入口，导致普通 API、签名 TOP 请求、Hibot 和 Observe 的行为不一致，应用无法稳定传递产品标识。

## 变更内容

- 为 Python SDK 的客户端配置增加可选 `productCode`。
- 统一使用 `X-Trace-Product-Code` Header。
- 在签名生成前注入 productCode，确保 Header 纳入 canonical request。
- 支持 `hiagent-api`、`hiagent-eva`、`hibot` 和 `hiagent-observe` 的请求链路。
- 保持现有构造函数、请求体和无 productCode 时的行为兼容。
- 增加请求构造、签名、空值和非法字符测试，并提供示例配置。

## 功能 (Capabilities)

### 新增功能

- `python-sdk-product-code`: Python SDK 客户端统一传递 productCode。

### 修改功能

无。

## 影响

- 影响 `libs/api`、`libs/eva`、`libs/hibot`、`libs/observe` 的配置和请求构造代码。
- 可能影响 examples、README 和公开构造函数签名，但不删除现有调用方式。
- 不新增运行时依赖；依赖现有 `httpx`、Volcengine 签名和 OpenTelemetry 组件。
