## 为什么

`hiagent_api.up.UpService` 的五个公开方法（`UploadRaw`、`LongLive`、`DownloadKey`、`Download`、`Delete`）与 UP 服务端当前的验签方式和接口契约不一致。对照基准是 upload-server `origin/main`（`64723ae0`）的 `idl/upload.thrift`、`idl/download.thrift`、`pkg/server/middlewares/dispatcher/dispatcher.go`、`pkg/server/middlewares/authz/authz.go`，以及它依赖的 iam-server `sdk.CheckSignature`。Java SDK 已在 `fix-up-client-signature`、`align-up-client-models` 两个变更中完成同样的对齐，本变更把 Python 补齐到同一口径；与 Java 不同的取舍在 design 中逐条说明。

### 验签失败

UP 的 `CheckSignature` 只从请求头取 `X-Date` 和 `Authorization`，用自己收到的请求重算签名。

- `UploadRaw` 用 `SignerV4.sign_url` 把签名写进 query，请求头里没有 `X-Date`、`Authorization`。UP 把它当作未签名请求，只有部署开启匿名访问、或 `authz.unsignedActions` 放行 `UploadRaw` 时才成功；关闭匿名（当前安全默认）时被拒。
- `DownloadKey` 的 `ApiInfo` 方法是 `POST`，`Service.get()` 按 `POST` 计算 canonical request 后却发出 `GET`，UP 按 `GET` 重算，结果是 `signature not match`。
- `Download` 有同样的方法错配，只是 query 带非空 `Key` 时 UP 在验签之前放行（`authz.go` 中 `action == "Download" && c.QueryParam("Key") != ""`），所以现在能用。
- 所有方法都使用 volcengine `SignerV4.sign`，它把 `host` 签进去，并对整个请求体重新计算哈希。经域名或七层网关改写 Host 时会失配；上传大文件时只能整个读进内存。

### 模型与契约不一致

- `UploadRawRequest` 的 `Expire`、`ContentType`、`Sha256` 是没有默认值的必填字段，UP 都是可选的；SDK 也不会自动计算 sha256。缺少 `Filename`、`ImageCompress`。
- `UploadRaw` 把 `Sha256`、`ContentType` 也拼进 query，UP 只从 header 读取。
- 响应缺字段：`UploadRaw` 的 `ShortLink`、`PresignKey`；`LongLive` 的 `Sha256`、`ShortLink`；`DownloadKey` 的 `Size`、`ContentType`。pydantic 会静默丢弃这些字段。
- `DownloadKey`、`Download` 只支持 `Path`，UP 支持 `Path` 和 `Sha256` 二选一。`Download` 缺少 `ID`、`Filename`、`ImageCompress`。
- `Download` 把本地路径 `SaveTo` 当成 query 参数发给 UP。
- `LongLive` 的请求键是 `Id`，UP 的 `json` tag 是 `ID`。现在能绑定只是因为 Go `encoding/json` 有不区分大小写的兜底；一旦匹配不上，UP 会建一条 ID 为空、无法通过 `Delete` 释放的关联，且不报错。
- SDK 原样发送调用方的 sha256。UP 存储和比较的都是小写十六进制，大写值会被判为不匹配或查不到。

### 其他缺陷

- `UploadRaw`、`DownloadKey` 在响应缺少 `Result` 时写成了 `Exception(...)`，漏了 `raise`，随后因 `KeyError` 失败。
- `Download` 边收边写 `SaveTo`：传输中断会留下残缺文件，并且已经覆盖了原有文件。
- `libs/api/tests` 中没有任何 UP 测试。

## 变更内容

- 新增包内模块 `hiagent_api/_up_signer.py`，移植 Java `UpSigner`：按最终要发出的请求计算签名；SignedHeaders 固定为 `x-content-sha256;x-date`，不签 `host`；payload hash 取请求自带的 `X-Content-Sha256`。AK、STS token 含非法字符时抛出不含凭证值的 `ValueError`。
- 五个方法统一发 `POST`、请求头签名、每个请求都带 `X-Content-Sha256`。`UploadRaw` 在调用方未提供 sha256（`None` 或空白串）时先流式计算一遍，再流式上传。
- AK、SK 都未配置时不签名直接发送，由 UP 按部署配置决定是否放行。旧版用空凭证照样签名，在 `unsignedActions` 部署上会被拒；不签名是唯一在所有放行路径上都成立的做法。只配置了其中一个时抛 `ValueError`。
- 按 UP 契约补齐请求和响应字段，新字段全部可选，原有字段由必填放宽为可选的不影响旧调用。`Download` 的参数（含 `Key`）继续走 query，保持 UP 在验签前按 `Key` 放行的路径；`SaveTo` 不再发送。`LongLive` 的请求键改为 `ID`，Python 属性名和构造方式不变。
- SDK 发出的所有 sha256 去首尾空白并转小写，不修改调用方的请求对象。
- `UploadRaw` 缺 `Id`、`LongLive` 缺 `ID`、`Download` 缺 `SaveTo` 时在发请求前抛出 `ValueError`。
- `Download` 流式写入 `SaveTo` 所在目录的临时文件，核对写入字节数与 `Content-Length` 后用 `os.replace` 原子替换目标（不依赖 urllib3 版本是否校验长度）；失败时删除临时文件，不留残缺文件、不破坏已有文件。
- 响应缺少 `Result` 时抛出明确的 `Exception`。
- 已配置的 productCode 在五个方法上都发送 `X-Trace-Product-Code`，不参与签名；未配置时不发送。

## 非目标

- 不新增 Action（`BatchDelete`、`Version`、分片上传、Blob、Artifact、Presign 等），不新增异步接口。
- 国密（HMAC-SM3 签名、SM3 文件哈希）。
- 中间代理改写路径（如 ingress `rewrite-target`）的部署形态：UP 按收到的路径验签，客户端无法签对。
- 不暴露 `Download` 的 `Range` 和 `IsAnonymous`，原因与 Java `align-up-client-models` 相同：续传需要按 `Content-Range` 偏移写入；匿名是部署级开关，不引导调用方依赖它。
- 不改 `UploadRaw` 未设置 `ContentType` 时的默认值 `application/octet-stream`（UP 开启 `contentType.mustMatch` 时按扩展名推断反而可能被拒）。
- 不改 `Version` query 参数的值（`2022-01-01`），UP 不校验它。
- 不迁移到 `hiagent_api.base` 的 httpx 实现，`UpService` 继续继承 volcengine `Service`。
- 不改 `hibot`、`eva`、`observe`、`components`。不改版本号，随下一个补丁版本发布。
- 不处理 `hiagent-api` wheel 会带上 `tests/` 的既有打包问题（`packages = ["."]`），只在构建时检查并记录。

## 功能 (Capabilities)

### 新增功能

- `python-sdk-up-service`: `UpService` 的请求签名、凭证校验、请求体哈希、字段契约、哈希规范化与下载落盘。

### 修改功能

无。

## 影响

- 代码：`libs/api/hiagent_api/up.py`、`up_types.py`，新增 `_up_signer.py`；新增 `libs/api/tests/test_up_*.py` 与测试数据 `libs/api/tests/data/up_signature_vectors.json`（取自 Java SDK，由 UP 服务端验签库离线生成）。
- 示例与文档：`libs/api/examples/up/*` 说明 `Sha256` 可省略并补充新字段，`ContentType="plain/text"` 改为标准的 `text/plain`；`agent-harness` 调用方式不变，补回归测试。
- 公开 API：只有新增字段和"必填放宽为可选"，原有构造与调用方式保持可用。
- 线上行为变化（需写进发版说明）：
  - 所有方法改为 `POST` + 请求头签名；`DownloadKey`、`Download` 由 `GET` 改为 `POST`。
  - `UploadRaw` 的 query 不再携带 `Sha256`、`ContentType`；`Download` 的 query 不再携带 `SaveTo`，其余参数仍在 query。
  - `LongLive` 请求体的键由 `Id` 变为 `ID`。
  - 调用方传入大写 sha256 时，SDK 发出小写；`UploadRawRequest.Sha256` 为空白串时改为自动计算，不再原样发送空值。
  - `UploadRaw` 缺 `Id`、`LongLive` 缺 `ID`、`Download` 的 `SaveTo` 为空白时，本地抛 `ValueError`，不再发请求。
  - `UploadRaw` 未提供 `Sha256` 且文件对象不可 seek 时，本地抛 `ValueError`。
  - 只配置了 AK、SK 其中之一，或 AK、STS token 含控制字符、空格或非 ASCII 字符时，本地抛 `ValueError`。
  - 未配置凭证时请求不再带空凭证签名，而是完全不签名。
  - `Delete` 收到不含 `Result` 的 200 响应时改为抛 `Exception`（原先返回整个响应 JSON）。UP 的 `Delete` 成功时总是返回 `"Result": {}`，只影响 mock 或非 UP 实现。
  - `Download` 成功后 `SaveTo` 是一个新文件（经原子替换）：`SaveTo` 为符号链接时替换的是链接指向的文件；目标已存在时保留其权限位。
  - `Download` 需要目标文件所在目录可写（要在那里创建临时文件）；原先只要求目标文件本身可写。
  - `Download` 收到的字节数少于声明的 `Content-Length` 时抛异常；原先在 urllib3 1.26 上会静默写出残缺文件。
