## ADDED Requirements

### 需求:客户端 productCode 配置

支持的 Python SDK 客户端必须提供可选的客户端级 `productCode` 配置，并保持已有构造函数和调用方式兼容。

#### 场景:配置 productCode

- **当** 客户端配置 `productCode` 为 `maas`
- **那么** 其适用请求必须携带 `X-Trace-Product-Code: maas`

#### 场景:未配置 productCode

- **当** 客户端使用已有构造方式创建
- **那么** SDK 不得自动添加 `X-Trace-Product-Code`

### 需求:请求级 Header 优先级

SDK 必须保留请求级显式 `X-Trace-Product-Code`，覆盖客户端级默认值；Header 名称比较必须不区分大小写。

#### 场景:显式 Header 覆盖

- **当** 客户端配置 `productCode=hiagent`
- **并且** 请求显式设置 `X-Trace-Product-Code: maas`
- **那么** 实际发送请求必须使用 `maas`

### 需求:签名顺序

使用 Volcengine TOP 签名的客户端必须在 canonical request 和签名生成前注入 productCode Header。

#### 场景:签名包含 productCode

- **当** 签名客户端配置 `productCode=maas` 并构造请求
- **那么** productCode 必须出现在签名输入的 Header 集合中
- **并且** 服务端使用同一签名规则时必须能够校验该请求

### 需求:Observe Token 与 Trace 分离

Observe 支持 productCode 时不得向 `CreateApiToken` 请求体增加 productCode；OTLP Trace 导出请求必须携带配置的 productCode。

#### 场景:Observe 导出

- **当** Observe 客户端配置 `productCode=hiagent` 并初始化、导出 Trace
- **那么** Token 请求体只能包含原有字段
- **并且** OTLP 请求必须携带 `X-Trace-Product-Code: hiagent`

### 需求:安全值处理

SDK 必须将空白 productCode 视为未配置，并在网络请求前拒绝包含 HTTP 控制字符的值。

#### 场景:空白配置

- **当** productCode 只包含空格或制表符
- **那么** 客户端不得发送 productCode Header

#### 场景:非法配置

- **当** productCode 包含 CR、LF 或其他 HTTP 控制字符
- **那么** 客户端创建或配置必须在网络请求前抛出 `ValueError`
