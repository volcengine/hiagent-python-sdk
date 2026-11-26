## 背景

### UP 怎么验签

UP 不比对客户端交来的签名材料，而是用**自己收到的请求**重算签名，再与 `Authorization` 里的签名比较（iam-server `sdk/helper.go:CheckSignature`）：

```text
Method        收到的请求方法
Path          收到的 URL.Path（Go 按 PathUnescape 解码，"+" 保持字面）
Query         收到的全部 query（含 Action、Version），按 url.ParseQuery 解码（"+" 解为空格），
              按参数名排序，名和值只保留 A-Z a-z 0-9 - _ . ~，其余按 UTF-8 字节写成大写 %XX，
              空格写成 %20
Headers       按 Authorization 中 SignedHeaders 的顺序取 "name:去首尾空白的值"
BodyHash      X-Content-Sha256 头；没有这个头时，服务端读完整个请求体自己算
X-Date        必须在请求头里；缺 X-Date 或 Authorization 直接失败
```

签名串为 `HMAC-SHA256\n<X-Date>\n<yyyyMMdd>/<region>/<service>/request\n<hex(SHA256(canonical))>`，密钥由 SK 依次对日期、region、service、`request` 做 HMAC-SHA256 派生。

`authz.go` 判断"请求是否声明了身份"（`claimsAnIdentity`）也只看请求头里的 `X-Date` 和 `Authorization`，所以 query 签名（`SignerV4.sign_url`）在 UP 看来就是未签名请求。

验签之前还有几条放行路径：匿名开启时的短路、`authz.unsignedActions`，以及 `action == "Download" && c.QueryParam("Key") != ""`。最后这一条**只看 query**，`Key` 放在 JSON 请求体里时不生效。

### UP 怎么绑定这五个 Action 的参数

UP 按 `?Action=<Name>` 反射到同名 handler，不按路径路由（`dispatcher.go:RefAction`）。绑定顺序：

1. 请求体：Action 不在 `skipParseBody` 里时按 JSON 解析；请求体为空时不绑定。`UploadRaw`、`DownloadKey` 在 `skipParseBody` 里，请求体不参与绑定。
2. query：按 `query` tag 取值，echo 先精确匹配，再不区分大小写匹配。
3. header：按 `header` tag 取值，请求里没有该 header 时不覆盖前面的值。
4. 按 `validate` tag 校验，失败返回 400。

| Action | 请求字段（来源） | 响应 |
| --- | --- | --- |
| UploadRaw | `X-Content-Sha256`、`Content-Type`（header）；`Expire`、`Id`（必填）、`Filename`、`ImageCompress`（query）；请求体是文件 | `Path`、`Size`、`Sha256`、`ShortLink`、`PresignKey` |
| LongLive | `Path`、`ID`、`Filename`（JSON） | `Path`、`Size`、`Sha256`、`ShortLink` |
| DownloadKey | `Path`、`Sha256`（query，二选一） | `Key`、`Size`、`ContentType` |
| Download | `Path`、`Sha256`（二选一）、`Key`（必填）、`ID`、`Filename`、`ImageCompress`（JSON 与 query 都有 tag）；`Range`（header） | 文件流；失败时为 JSON 错误信封 |
| Delete | `Sha256`（必填，64 位）、`Id`（必填，8 至 256 位）（JSON） | `Result: {}` |

响应信封是 `{"ResponseMetadata": ..., "Result": ...}`，`Result` 为 `omitempty`，五个 handler 成功时都返回非 nil 响应，所以 `Result` 总是存在（`Delete` 为 `{}`）。

`UploadRaw` 用小写十六进制计算文件哈希并与请求值做字符串比较；`DownloadKey`、`Download`、`Delete` 按哈希查库，库里存的也是小写。

### 现在的 Python 实现错在哪

五个 `ApiInfo` 的方法本来都是 `POST`，问题出在发送路径上：

| 方法 | 现在的做法 | 问题 |
| --- | --- | --- |
| UploadRaw | `SignerV4.sign_url`，签名在 query；`model_dump()` 全部进 query | UP 视为未签名；`Sha256`、`ContentType` 多余地进了 query |
| LongLive | `Service.json()`，POST + 头签名 | 签了 `host`；请求键是 `Id` |
| DownloadKey | `Service.get()`：按 `ApiInfo` 的 `POST` 签名，发出 `GET` | 方法错配，验签必然失败 |
| Download | 同上，`GET` + query，`SaveTo` 进 query | 方法错配（query 带 `Key` 时被 UP 提前放行）；本地路径外泄；边收边写 |
| Delete | `Service.json()`，POST + 头签名 | 签了 `host`；sha256 未规范化 |

## 方案

### 原则：签名只针对最终发出的请求

问题的根源是"签名材料"和"发出的请求"是两份东西。新增包内模块 `hiagent_api/_up_signer.py`，从 Java `UpSigner` 移植，只有一个入口：

```python
def sign(method: str, url: str, headers: Mapping[str, str], *, ak: str, sk: str,
         region: str, session_token: str | None = None,
         now: datetime | None = None) -> dict[str, str]
```

- 输入就是要交给 `requests` 的 `method`、完整 `url`、`headers`，返回在 `headers` 基础上新增 `X-Date`、`Authorization`（使用 STS 时再加 `X-Security-Token`，不参与签名）的新 dict，不修改入参。
- path：`urllib.parse.unquote(urlsplit(url).path)`，与 Go 的 `URL.Path` 一致，`+` 保持字面；空路径按 `/`。
- query：取 `urlsplit(url).query` 原文，按 `&` 拆对，名和值都用 `urllib.parse.unquote_plus` 解码（与 Go `url.ParseQuery`、Java `URLDecoder` 一致，`+` 解为空格），按参数名排序（同名保持原顺序），再用 `urllib.parse.quote(s, safe="-_.~")` 编码，与 Java `signEncode` 等价。
- payload hash：按不区分大小写的方式查找 `X-Content-Sha256`，去首尾空白后使用；缺失或为空白串时抛 `ValueError`，不提供任何"另算一份哈希"的路径。
- 时间：`now` 只供测试注入固定时间，生产调用不传，取 `datetime.now(timezone.utc)`；传入时先 `astimezone(timezone.utc)`。`X-Date` 格式为 `%Y%m%dT%H%M%SZ`。
- SignedHeaders 固定为 `x-content-sha256;x-date`。不签 `host`，经网关改写 Host 时不会失配；不签 `X-Trace-Product-Code`，productCode 有无不影响签名。
- credential scope 的 service 固定为 `up`，与现在 `UpService` 的 `Credentials("", "", "up", region)` 一致。

### 凭证校验

`requests` 设置含 `\r`、`\n` 或首部空白的 Header 时抛出的 `InvalidHeader` 会把整个 Header 值写进异常信息。会进入 Header 的凭证只有 AK（写进 `Authorization`）和 STS token（`X-Security-Token`）；其中真正的秘密是 STS token，常见出错方式是从文件读入时带了尾随换行。所以只做两件事：

- `session_token` 先去首尾空白，去完为空则视为没有 STS。
- `ak`、`session_token` 只能包含可打印 ASCII（`0x21`–`0x7e`），否则抛 `ValueError`。异常信息只说明是哪一项不合法，不包含值，并用 `from None` 断开原始异常。

不另做的校验：SK 不进入任何 Header，只参与 HMAC；region 来自构造参数，不是凭据，写错只会导致服务端验签失败。AK、SK 是否为空由下一节的规则处理。

### 未配置凭证

旧版在没有凭证时，volcengine 会用空 AK 照样签名并发出请求。可选的做法有三种，只有"不签名"在所有放行路径上都成立：

| 做法 | 匿名开启 | `unsignedActions` 放行 | 关闭匿名 |
| --- | --- | --- | --- |
| 用空凭证照样签名（旧版） | 放行，但后台验签观测会记一次失败 | **被拒**：`unsigned.allows(action) && !claimsAnIdentity(...)` 只放行完全不带签名材料的请求 | 被拒 |
| 本地直接报错（Java） | 本可成功的调用失败 | 本可成功的调用失败 | 报错更早 |
| 不签名 | 放行 | 放行 | 被拒，与旧版相同 |

所以：

- AK、SK 都为空（`None` 或空白串）：不调用签名器，请求不带 `X-Date`、`Authorization`，其余部分（含 `X-Content-Sha256`）照常发送。UP 的 `claimsAnIdentity` 会把它当作完全未签名的请求，交给部署配置决定是否放行。
- 只配置了其中一个：在发请求前抛 `ValueError`，避免半套配置被静默降级成匿名请求。
- 两个都配置了：按上文签名，并做凭证校验。

### `UpService` 的请求构造

五个方法共用一个私有方法 `_send(action, query, body, content_type, content_sha256, stream=False)`：

```text
URL      <scheme>://<host><ApiInfo.path>?Action=<A>&Version=2022-01-01&<参数...>
         参数名和值用签名同一套编码写进 URL，发出的字节就是被签名的字节；
         值为 None 的参数不发送；bool 写成 true/false
Method   一律 POST
Headers  CaseInsensitiveDict(service_info.header)（Accept、已配置的 X-Trace-Product-Code），
         在这份副本上设置 Content-Type、X-Content-Sha256、User-Agent，
         不会出现同名不同大小写的重复 Header，也不修改 service_info.header
         User-Agent 为 "volc-sdk-python/" + volcengine.VERSION（与 volcengine 原逻辑相同，VERSION 自带 v 前缀）
签名     每次调用时读取 service_info.credentials 的 ak、sk、session_token、region，
         所以初始化之后再调用 set_ak/set_sk/set_session_token 也会生效
发送     self.session.post(url, headers=..., data=body,
                           timeout=(connection_timeout, socket_timeout), stream=stream)
响应     非 200：raise Exception(resp.text)，与现在一致
         200：解析 JSON；没有 Result 时 raise Exception("no Result in response: ...")
```

- `UpService` 继续继承 volcengine `Service`，`set_ak`、`set_sk`、`set_session_token`、`session`、`set_product_code` 全部照旧可用。`get_api_info()` 的五个 `ApiInfo` 原本就是 `POST`，保持不变，`_send` 从中读取 path 与 `Action`/`Version`。
- 路径保持现在的 `/up`（`Download` 为 `/down`），endpoint 解析逻辑不变。
- 不再使用 `Service.get/json/prepare_request` 与 `SignerV4`，避免再次出现"签一份、发一份"。

### 各方法的请求形状

| 方法 | query（Action、Version 之外） | 请求体与 Content-Type | 本地检查（按顺序，都在发请求前） |
| --- | --- | --- | --- |
| UploadRaw | `Expire`、`Id`、`Filename`、`ImageCompress` | 文件对象；`ContentType` 或 `application/octet-stream` | `Id` 非空 → 凭证 → 需要自动计算时检查可 seek |
| LongLive | 无 | `{"Path","ID","Filename"}`；`application/json` | `ID` 非空 → 凭证 |
| DownloadKey | `Path`、`Sha256` | `b""`；`application/json` | 凭证 |
| Download | `Key`、`Path`、`Sha256`、`ID`、`Filename`、`ImageCompress` | `b""`；`application/json` | `SaveTo` 非空白 → 凭证 |
| Delete | 无 | `{"Sha256","Id"}`；`application/json` | 凭证 |

- 只有 `LongLive`、`Delete` 两个 Action 带 JSON 请求体，用 `model_dump(by_alias=True, exclude_none=True)` 生成、规范化 sha256 后，`json.dumps(...).encode("utf-8")`；`X-Content-Sha256` 对这份最终字节计算。
- `Download` 的参数全部走 query，原因有两个：UP 只在 query 带 `Key` 时于验签前放行，参数放进请求体会让带 `Key` 的下载改走完整验签；这也和旧版 Python 的线上形状一致。请求体为空，UP 不做 JSON 绑定。这一点与 Java（参数放在 JSON 请求体）不同，是有意的取舍。
- `DownloadKey` 的二选一、`Delete` 的长度约束交给 UP 判断，SDK 不另立规则（与 Java 一致）。

### `Id` 的检查口径

- `UploadRawRequest.Id`、`LongLiveRequest.Id` 保持 `str` 必填。缺参或传 `None` 时 pydantic 在构造阶段就抛 `ValidationError`，它是 `ValueError` 的子类。
- 方法入口再检查一次空串（以及 `model_construct` 绕过校验得到的 `None`），抛 `ValueError`。口径与 UP 的 `validate:"required"` 一致：只拒绝 `None` 和空串，不拒绝空白串。
- `UploadRaw` 的 `Id` 检查排在所有读文件、`seekable()` 判断之前。

### 请求体哈希

- `UploadRaw`：
  - `Sha256` 去首尾空白后非空：转小写后放进 `X-Content-Sha256`，UP 会用它校验文件内容。文件对象不需要可 seek，直接流式上传。
  - `Sha256` 为 `None` 或去空白后为空：视为未提供（与 Java `UpClient` 一致，兼容旧代码传 `""`）。记录 `file.tell()`，按 64 KiB 分块读到末尾算 SHA-256，再 `seek` 回原位置后上传。所以从非零偏移开始的文件对象只会哈希并上传剩余字节。IO 两遍，内存占用固定。不能"边读边算"，因为哈希要先写进请求头并参与签名。
  - 未提供 `Sha256` 且文件对象不可 seek（没有 `seekable`、返回假或抛错）：抛 `ValueError`，提示调用方提供 `Sha256`。
- `DownloadKey`、`Download`：请求体为空，`X-Content-Sha256` 为空串的 SHA-256。
- JSON 请求：对最终发送的字节计算。
- 每个请求都发送 `X-Content-Sha256`。不发时 UP 会在鉴权中间件里读完整个请求体来算哈希，大文件会占满服务端内存。

### sha256 规范化

规则：去首尾空白，转小写。覆盖 SDK 发出的所有 sha256：`UploadRaw` 的 `X-Content-Sha256`、`DownloadKey` 和 `Download` 的 `Sha256` query、`Delete` 请求体里的 `Sha256`。在 dump 出的 dict 上改写，调用方的模型对象不变。

只规范化上传会造成不一致：大写哈希的上传从失败变成成功，同一个哈希的 `Delete` 却在大小写敏感的库上什么也没删、也不报错。所以全部规范化。

### 模型变更

全部基于 pydantic v2，新字段默认 `None`。

| 模型 | 变更 |
| --- | --- |
| `UploadRawRequest` | `Expire`、`ContentType`、`Sha256` 改为 `Optional[str] = None`；`Id` 保持 `str` 必填；新增 `Filename: Optional[str]`、`ImageCompress: Optional[bool]`。`ContentType` 为 `None` 或空串时发送 `application/octet-stream`，与现在一致 |
| `UploadRawResponse` | 新增 `ShortLink`、`PresignKey`（可选） |
| `LongLiveRequest` | Python 属性名仍为 `Id`（`str` 必填），只加 `serialization_alias="ID"`，构造方式不变；新增 `Filename`。不额外接受 `ID=` 构造：没有调用方需要，属于过度设计 |
| `LongLiveResponse` | 新增 `Sha256`、`ShortLink`（可选） |
| `DownloadKeyRequest` | `Path` 改为可选；新增 `Sha256` |
| `DownloadKeyResponse` | 新增 `Size`、`ContentType`（可选） |
| `DownloadRequest` | `Path` 改为可选；新增 `Sha256`、`ID`、`Filename`、`ImageCompress`；`SaveTo` 保持 `str` 必填，用 `Field(exclude=True)` 排除，不进入 query |
| `DeleteRequest` | 不变 |

Python 的 `int` 没有溢出问题，`Size` 不需要 Java 那样的 `Long` 兼容处理。

返回值保持现状：`Delete` 返回 `Result` 的内容（UP 返回 `{}`）；`Download` 返回 `None`。唯一变化是 `Delete` 收到不含 `Result` 的 200 响应时，和其他方法一样抛异常，不再返回整个响应 JSON。UP 的 `Delete` 成功时总带 `"Result": {}`，这只影响 mock 或非 UP 实现，作为发版说明中的行为变化。

### `Download` 落盘

1. 发请求前：`SaveTo` 为空白串时抛 `ValueError`。如果不拦，`os.path.realpath("")` 会返回当前目录，整个文件下载完后才在替换时报 `IsADirectoryError`。
2. 用 `with self.session.post(..., stream=True) as resp:` 包住整个处理过程，非 200 或中途异常时都会释放连接。
3. 响应非 200：读取响应体作为错误信息抛出，不创建任何文件。
4. 用 `os.path.realpath(SaveTo)` 得到最终目标，这样 `SaveTo` 是符号链接时，替换的是它指向的文件，与原先 `open(SaveTo, "wb")` 的效果一致。目标的父目录不存在时自动创建（与 Java 一致）。
5. 在目标同一目录下用 `os.open(tmp, O_WRONLY | O_CREAT | O_EXCL, 0o666)` 创建随机名的临时文件。权限按进程 umask 生成，与普通 `open()` 相同；不用 `mkstemp`，因为它固定创建 0600。
6. 用 `resp.iter_content` 按块写入临时文件并累计字节数。
7. 长度核对：响应带 `Content-Length` 且没有 `Content-Encoding` 时，写入字节数必须等于 `Content-Length`，否则抛异常。不能只依赖 urllib3：本仓库 lock 的是 2.6.3，它默认校验长度；但 requests 允许用户装 urllib3 1.26，1.26 默认不校验，短读会被当成正常结束，残缺文件随后被原子替换上去，"失败不破坏旧文件"就失效了。UP 未加密时总会声明 `Content-Length`（压缩时为压缩后的大小），加密输出不声明，此时跳过核对。
8. 目标已存在时用 `shutil.copymode` 把原有权限位带到临时文件，然后 `os.replace(tmp, target)` 原子替换。保留权限位不是可有可无：否则一个 0600 的私有文件被替换后会按 umask 变成 0644。不做 `fsync`：它解决的是断电后的持久性，不是这次要解决的"传输失败不破坏旧文件"，测不出效果，还会拖慢大文件下载。
9. 任一步出错（网络中断、长度不符、写盘失败）：删除临时文件，原有目标文件保持原样，异常向上抛出。

### 与其他签名代码的关系

仓库里会有三份 V4 签名实现：volcengine `SignerV4`（其他 TOP 服务继续使用）、`hibot/_signer.py`、`hiagent_api/_up_signer.py`。`hibot` 是独立包，按 AGENTS.md 不能跨包导入它的私有模块，而且它签 `host`、要求传入完整请求体字节，不适合 UP。容易出错的 query 编码由下文的服务端样例固定。

### 被否决的方案

- **沿用 `SignerV4.sign`，只修方法与 query**：它签 `host`，并且会把 `X-Content-Sha256` 覆盖为 `sha256(request.body)`，上传只能把整个文件读进内存；它的 query 编码也没有经过服务端样例验证。
- **迁移到 `hiagent_api.base` 的 httpx `Service`**：改动面大，并且会改变 `UpService` 的基类和 `session` 类型，不属于这次对齐的范围。
- **`Download` 参数放进 JSON 请求体（Java 现状）**：会让带 `Key` 的下载从"验签前放行"变成"完整验签"，改变鉴权路径。
- **`Download` 整体读进内存再写（Java 现状）**：大文件会占满内存；临时文件加原子替换在 Python 里代价很小。
- **未配置凭证时直接报错（Java 现状）、或用空凭证照样签名（Python 旧版）**：见上文"未配置凭证"中的对比表，两者在 `unsignedActions` 部署上都会失败。
- **下载后用 `ETag` 校验内容哈希**：UP 把 `ETag` 设为文件哈希，看上去能顺带发现 UP"200 但内容为空或不完整"的已知问题（`docs/oncall/runbooks/download-size-mismatch.md`）。但部署可能开启国密（`useSM`，哈希为 SM3），`ImageCompress` 时返回的是压缩文件的哈希，客户端固定按 sha256 比对会把正常下载判为失败。不做。
- **用本地 `http.server` 验证截断**：验证的是 urllib3 的行为，不是 SDK 的；而且在 urllib3 1.26 上，这条保证本来就不成立。改为由 SDK 自己核对长度，用 fake adapter 构造虚报 `Content-Length` 的响应来测。

## 兼容性

- 公开类、方法名、方法签名不变；模型只有新增字段和"必填放宽为可选"，旧的构造方式（包括 `LongLiveRequest(Id=...)`）照常可用。
- 未配置 productCode 时不发送 `X-Trace-Product-Code`。
- 未配置凭证时仍然发出请求（不签名），与旧版效果一致。
- 新增的本地检查抛 `ValueError`，它是 `Exception` 的子类，调用方原有的 `except Exception` 仍能捕获。
- `Download` 的 query 参数与旧版一致，只少了 `SaveTo`，UP 的放行路径不变。
- `agent-harness` 的 `hiagent_backend.upload_raw_file`、`download_file` 调用方式不变。
- 依赖不变（`volcengine`、`requests`、`pydantic>=2.11.5`）。

## 测试方案

默认测试全部离线运行，放在 `libs/api/tests/`：

1. **服务端签名样例（主验收）**：复制 Java SDK 的 `up-signature-vectors.json` 到 `libs/api/tests/data/up_signature_vectors.json`。这份样例由 UP 服务端验签用的签名库离线生成，覆盖文本与非法 UTF-8 二进制请求体、根路径与 `/up/` 路径、含 `/`、空格、`+`、`=`、`&`、`!'()*`、中文的 query 值、大小写混合的参数名排序。逐条断言 canonical request、待签串、签名完全一致。另补一条：原始 URL 的 query 和 path 中都有字面 `+` 时的解码结果。
2. **签名器边界**：`X-Content-Sha256` 用不同大小写的键都能找到、首尾空白被去掉、缺失或空白时报错；不修改入参 headers。
3. **凭证**：`ak`、`session_token` 含 `\n`、`\r`、控制字符、空格或非 ASCII 字符时抛 `ValueError`，异常信息里**不包含**凭证值，`__cause__` 和 `__context__` 都为空；`session_token` 带尾随换行时去掉后正常签名；只配 AK 或只配 SK 时抛 `ValueError` 且没有发请求；AK、SK 都未配置时发出的请求不带 `X-Date`、`Authorization`。
4. **签的就是发出去的请求**：给 `UpService.session` 挂一个 requests 的 fake adapter，截下五个方法实际发出的 `PreparedRequest`，按**收到的** method、URL、`X-Content-Sha256` 用已被样例验证的签名器重算签名，必须等于收到的 `Authorization`；并校验 `X-Content-Sha256` 等于实际请求体的 SHA-256。初始化后调用 `set_ak`/`set_sk` 会用新凭证签名。
5. **请求形状**：方法均为 `POST`；`UploadRaw` 的 query 不含 `Sha256`、`ContentType`，`ImageCompress=False` 写成 `false` 照发，`None` 字段不发；`LongLive` 的键是 `ID`；`Download` 的 `Key` 等参数在 query、请求体为空、任何地方都没有 `SaveTo`；大写 sha256 发出时为小写且调用方模型不变；productCode 已配置时发送、未配置时不发送、不在 SignedHeaders 中；`service_info.header` 里已有小写 `content-type` 等键时不产生重复 Header，且 `service_info.header` 本身不被修改；User-Agent 为 `volc-sdk-python/` + `volcengine.VERSION`；STS token 生效；签名不含 `host`。
6. **兼容与边界**：
   - 旧写法（四个字段全传）的 `UploadRaw` 照常工作；
   - `Sha256` 为 `None`、`""`、`"   "` 时都自动计算，上传内容完整；
   - 文件对象已 seek 到非零偏移时，只哈希并上传剩余字节；
   - 提供了 `Sha256` 时，不可 seek 的流照常流式上传；
   - 未提供 `Sha256` 且流不可 seek 时抛 `ValueError`，没有发请求；
   - `UploadRaw` 的 `Id` 为空串时抛 `ValueError`，且发生在读文件和 `seekable()` 判断之前（用一个读取即报错的文件对象验证）；`Id` 为空白串时照常发送；
   - `LongLive` 的 `ID` 为空串时不发请求；`LongLiveRequest(Id=...)` 序列化后的键是 `ID`；
   - 响应缺 `Result` 时五个方法都抛含 `no Result in response` 的异常；新响应字段能解析，缺失时为 `None`。
7. **下载落盘**：
   - 内容正确，自动创建父目录；
   - `SaveTo` 为空白串时抛 `ValueError`，没有发请求；
   - 非 200 时不创建文件，连接被释放；
   - 中途中断，用 fake adapter 构造两种情况：响应体比声明的 `Content-Length` 短（SDK 自己的长度核对会报错，不依赖 urllib3 版本），以及响应流读到一半抛异常。两种情况下旧文件内容都不变，目录里也不残留临时文件；
   - 带 `Content-Encoding` 或没有 `Content-Length` 的响应跳过长度核对；
   - `SaveTo` 为符号链接时写入链接目标；已有文件的权限位保留。
   - 变异验证：把实现改成直接写目标文件，中断用例必须失败。
8. **真实环境 e2e**：`libs/api/tests/test_up_e2e.py`，标记 `e2e`，只有设置 `HIAGENT_UP_UPLOAD_ENDPOINT`、`HIAGENT_UP_DOWNLOAD_ENDPOINT` 和 AK/SK 时才运行；跑一遍上传、长期化、获取下载 Key、下载、删除，上传之后的断言都放在 `try` 里，`finally` 里删除已上传的文件。最好在关闭匿名访问的 UP 上执行一次。

`agent-harness` 不在 uv workspace 里，它的 `test_up_endpoints.py` 补一条用例：通过 fake adapter 验证 `upload_raw_file`、`download_file` 在新实现下仍然正常。运行时需要加 `PYTHONPATH=agent-harness`。

## 风险与边界

- 只在直连 UP、或中间代理不改写路径时成立。
- UP 会把 `application/x-www-form-urlencoded` 请求体当作表单参数并入 query，`UploadRaw` 不支持以该类型上传。
- 国密环境不支持。
- `DownloadKey`、`Download` 由 `GET` 改为 `POST`：UP 对这两个 Action 不限制方法。`DownloadKey` 的请求体不参与绑定；`Download` 请求体为空，参数全部从 query 绑定，与旧版相同。
- 临时文件与目标在同一目录，要求该目录可写；原先只要求目标文件可写。目标所在目录只读、但文件本身可写的情况会由成功变为失败，已列入 proposal 的发版说明。
- 未配置凭证时请求不签名，能否成功取决于部署的匿名和 `unsignedActions` 配置；旧版在这些部署上本来就能发出同样的请求，不是新开的口子。
- 长度核对只能发现"实际字节少于声明"。UP 的已知问题是声明的长度本身偏小（库里的 size 错了），客户端收到的字节数和声明一致，但内容不完整，SDK 发现不了；这需要在服务端修数据，见 UP 的 `download-size-mismatch` runbook。
- `hiagent-api` 的 wheel 配置是 `packages = ["."]`，新增的 `tests/data/` 会随 `tests/` 一起进入 wheel。这是既有问题，在 6.4 构建后检查 wheel 内容并记录，不在本次修。
