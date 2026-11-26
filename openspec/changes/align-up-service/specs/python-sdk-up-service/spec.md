## ADDED Requirements

### Requirement: 签名只针对实际发出的请求

配置了凭证时，`UpService` 的五个方法必须（MUST）对最终发出的请求签名：method、解码后的 path、全部 query 和 `X-Content-Sha256` 都取自实际发出的请求。签名必须放在请求头 `X-Date` 与 `Authorization` 中，SignedHeaders 必须为 `x-content-sha256;x-date`，不得包含 `host`。query 解码必须把 `+` 解为空格，path 解码必须保留字面 `+`。

#### Scenario: 与 UP 服务端签名样例一致

- **WHEN** 用 `up_signature_vectors.json` 中每条样例的 method、URL、`X-Date`、`X-Content-Sha256` 和凭证计算签名
- **THEN** canonical request、待签串和签名必须与样例完全一致

#### Scenario: 按收到的请求重算签名

- **WHEN** 五个方法中的任意一个发出请求
- **THEN** 按收到的 method、URL 和 `X-Content-Sha256` 重算出的签名必须等于收到的 `Authorization` 中的签名
- **AND** 请求头中必须有 `X-Date`，query 中不得出现签名参数

#### Scenario: 经网关改写 Host

- **WHEN** 请求的 `Host` 与 endpoint 主机名不同
- **THEN** 签名结果不受影响

#### Scenario: X-Content-Sha256 的查找

- **WHEN** 请求头中的 `x-content-sha256` 键名大小写不同或值带首尾空白
- **THEN** 签名器必须找到该值并去掉首尾空白后使用
- **AND** 缺失或为空白串时必须抛出 `ValueError`

### Requirement: 凭证校验不泄漏凭证

签名前必须（MUST）去掉 `session_token` 的首尾空白，并校验 `ak`、`session_token` 只含可打印 ASCII。校验失败抛出的 `ValueError` 不得包含凭证值，也不得关联底层异常。

#### Scenario: 凭证含非法字符

- **WHEN** `ak` 或 `session_token` 含换行、控制字符、空格或非 ASCII 字符
- **THEN** SDK 必须在发出请求前抛出 `ValueError`
- **AND** 异常信息中不包含该凭证的值

#### Scenario: AK 带尾随换行

- **WHEN** `ak` 末尾带换行（AK 不做 strip）
- **THEN** SDK 必须在发出请求前抛出 `ValueError`，而不是把它交给 `requests` 在 `InvalidHeader` 中带出 `Authorization` 的值

#### Scenario: STS token 带尾随换行

- **WHEN** `session_token` 末尾带换行
- **THEN** SDK 必须去掉换行后正常发送 `X-Security-Token`

### Requirement: 未配置凭证时的行为

AK、SK、STS token 都未配置时，SDK 必须（MUST）照常发出请求但不签名；配置了其中一部分但 AK、SK 不全时，必须在发请求前抛出 `ValueError`。

#### Scenario: 都未配置

- **WHEN** AK、SK 都为空时调用任意方法
- **THEN** 请求照常发出，不带 `X-Date`、`Authorization`
- **AND** 仍然带 `X-Content-Sha256`

#### Scenario: 只配置一半

- **WHEN** 只配置了 AK 或只配置了 SK，或只配置了 STS token
- **THEN** SDK 必须抛出 `ValueError`，且不发出请求

### Requirement: 统一使用 POST

五个方法都必须（MUST）以 `POST` 发出，签名使用的方法必须与发出的方法一致。

#### Scenario: DownloadKey 与 Download

- **WHEN** 调用 `DownloadKey` 或 `Download`
- **THEN** 实际发出的方法必须是 `POST`
- **AND** 签名的 canonical request 必须以 `POST` 开头

### Requirement: 请求体哈希与请求体一致

每个请求都必须（MUST）发送 `X-Content-Sha256`，值必须等于实际请求体的 SHA-256（小写十六进制）。

#### Scenario: UploadRaw 未提供 Sha256

- **WHEN** 调用方传入可 seek 的文件对象，且 `Sha256` 为 `None`、空串或空白串
- **THEN** SDK 必须流式计算文件从当前位置到末尾的 SHA-256，并把这部分内容完整上传

#### Scenario: UploadRaw 文件不可 seek

- **WHEN** 调用方传入不可 seek 的流，且未提供 `Sha256`
- **THEN** SDK 必须在发出请求前抛出 `ValueError`

#### Scenario: UploadRaw 提供 Sha256 时不要求可 seek

- **WHEN** 调用方提供了 `Sha256`，且传入不可 seek 的流
- **THEN** SDK 必须正常流式上传

#### Scenario: 其他请求

- **WHEN** 调用 `LongLive`、`DownloadKey`、`Download` 或 `Delete`
- **THEN** `X-Content-Sha256` 必须等于实际发出的请求体字节（可能为空）的 SHA-256

### Requirement: sha256 规范化

SDK 发出的所有 sha256 都必须（MUST）去掉首尾空白并转小写，且不得修改调用方的请求对象。

#### Scenario: 大写哈希

- **WHEN** 调用方向 `UploadRaw`、`DownloadKey`、`Download` 或 `Delete` 传入大写 sha256
- **THEN** 发出的 `X-Content-Sha256`、`Sha256` query 或请求体中的 `Sha256` 必须是小写
- **AND** 调用方模型里的值保持不变

### Requirement: 请求字段与 UP 契约一致

请求参数必须（MUST）按 UP 的绑定方式发送：`UploadRaw` 的 `Expire`、`Id`、`Filename`、`ImageCompress` 放在 query；`DownloadKey` 的 `Path`、`Sha256` 放在 query；`Download` 的 `Key`、`Path`、`Sha256`、`ID`、`Filename`、`ImageCompress` 放在 query 且请求体为空；`LongLive`、`Delete` 的字段放在 JSON 请求体，键名与 UP 的 `json` tag 一致。值为 `None` 的字段不得发送。

#### Scenario: UploadRaw 的 query

- **WHEN** 调用 `UploadRaw`
- **THEN** query 中不得出现 `Sha256` 和 `ContentType`
- **AND** `ImageCompress=False` 必须以 `false` 发送

#### Scenario: LongLive 的 ID

- **WHEN** 用 `LongLiveRequest(Id="x")` 调用 `LongLive`
- **THEN** 请求体的键必须是 `ID`

#### Scenario: Download 保持 Key 在 query

- **WHEN** 调用 `Download`
- **THEN** `Key` 必须出现在 query 中，请求体为空
- **AND** 请求体和 query 中都不得出现 `SaveTo`

### Requirement: 模型兼容与新字段

原有构造与调用方式必须（MUST）保持可用。`UploadRawRequest` 的 `Expire`、`ContentType`、`Sha256` 必须是可选字段；新增的请求和响应字段必须是可选字段，默认值为 `None`。

#### Scenario: 旧写法

- **WHEN** 调用方像旧版一样传入 `Expire`、`Id`、`ContentType`、`Sha256` 四个字段调用 `UploadRaw`
- **THEN** 请求必须成功发出，`Content-Type` 与 `X-Content-Sha256` 取调用方给的值（sha256 规范化后）

#### Scenario: 新响应字段

- **WHEN** UP 返回 `ShortLink`、`PresignKey`、`Sha256`、`Size`、`ContentType` 等字段
- **THEN** 对应响应模型必须能读取这些字段
- **AND** UP 未返回时字段值为 `None`

#### Scenario: ContentType 缺省

- **WHEN** `UploadRawRequest.ContentType` 为 `None` 或空串
- **THEN** 必须以 `Content-Type: application/octet-stream` 发送

### Requirement: 发请求前的必填检查

`UploadRaw` 的 `Id`、`LongLive` 的 `ID` 为 `None` 或空串时，`Download` 的 `SaveTo` 为空白串时，SDK 必须（MUST）在读取文件或发出请求前抛出 `ValueError`。

#### Scenario: 缺 Id

- **WHEN** 以空串 `Id` 调用 `UploadRaw`，或以空串 `ID` 调用 `LongLive`
- **THEN** SDK 必须抛出 `ValueError`
- **AND** 不得读取文件、不得发出任何请求

#### Scenario: 缺 SaveTo

- **WHEN** 以空白串 `SaveTo` 调用 `Download`
- **THEN** SDK 必须抛出 `ValueError`，且不发出请求

### Requirement: productCode 注入

已配置 productCode 时，五个方法都必须（MUST）发送 `X-Trace-Product-Code`，且该 Header 不得进入 SignedHeaders；未配置时不得发送。

#### Scenario: 已配置 productCode

- **WHEN** 调用 `set_product_code("maas")` 后调用任意方法
- **THEN** 请求必须携带 `X-Trace-Product-Code: maas`
- **AND** 签名仍然有效

#### Scenario: 未配置 productCode

- **WHEN** 未调用 `set_product_code`，或设置为空白串
- **THEN** 请求不得携带 `X-Trace-Product-Code`

### Requirement: 响应处理

非 200 响应必须（MUST）以 `Exception` 抛出并带上响应体，响应体为空时带上状态码；200 响应缺少 `Result` 时，五个方法都必须抛出说明缺少 `Result` 的 `Exception`。SDK 不得跟随重定向。

#### Scenario: 收到重定向

- **WHEN** 任意方法收到带 `Location` 的 301/302/307/308 响应
- **THEN** SDK 只发出这一个请求，不跟随重定向
- **AND** 抛出的 `Exception` 包含状态码和 `Location`

#### Scenario: 非 200 且响应体为空

- **WHEN** 任意方法收到响应体为空的非 200 响应
- **THEN** 抛出的 `Exception` 包含状态码

#### Scenario: 缺少 Result

- **WHEN** 任意方法收到不含 `Result` 的 200 JSON 响应
- **THEN** SDK 必须抛出信息中包含 `no Result in response` 的 `Exception`，而不是 `KeyError`，也不是返回整个响应

### Requirement: 下载原子落盘

`Download` 必须（MUST）先把响应流式写入 `SaveTo` 目标所在目录的临时文件，完整收到后再原子替换目标，并在任何情况下释放响应连接。失败时不得留下临时文件，也不得改动已有的目标文件。

#### Scenario: 下载成功

- **WHEN** `Download` 收到 200 响应
- **THEN** 目标文件内容必须与响应体一致，缺失的父目录会被自动创建

#### Scenario: 下载中断

- **WHEN** 响应在传输中途中断（实际字节少于未压缩响应声明的 `Content-Length`，或读取时抛出异常），且 `SaveTo` 处已有文件
- **THEN** SDK 必须抛出异常，且不依赖所装 urllib3 版本是否校验长度
- **AND** 已有文件内容保持不变，目录中不残留临时文件

#### Scenario: 下载失败

- **WHEN** `Download` 收到非 200 响应
- **THEN** SDK 抛出 `Exception`，且不创建目标文件

#### Scenario: SaveTo 是符号链接

- **WHEN** `SaveTo` 指向一个符号链接
- **THEN** 写入的必须是链接指向的文件，链接本身保留

#### Scenario: SaveTo 不是普通文件

- **WHEN** `SaveTo`（解析符号链接后）是目录，或是设备文件、FIFO 等非普通文件
- **THEN** SDK 必须在发出请求前抛出异常（目录为 `IsADirectoryError`，其余为 `ValueError`），不改动该路径

#### Scenario: 覆盖私有文件

- **WHEN** `SaveTo` 处已有权限为 0600 的文件
- **THEN** 下载过程中的临时文件权限必须是 0600，完成后目标权限仍为 0600
