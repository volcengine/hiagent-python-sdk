## 1. 签名器

- [x] 1.1 复制 Java SDK 的 `up-signature-vectors.json` 到 `libs/api/tests/data/up_signature_vectors.json`，先写样例测试并确认失败。
- [x] 1.2 先写签名器边界测试：`X-Content-Sha256` 大小写不敏感查找、去空白、缺失报错；query 中字面 `+` 解为空格、path 中字面 `+` 保留；不修改入参 headers。
- [x] 1.3 先写凭证校验测试：`ak`/`session_token` 含 `\n`、`\r`、控制字符、空格、非 ASCII 时抛 `ValueError`，异常信息不含凭证值，`__cause__`/`__context__` 为空；`session_token` 尾随换行被去掉。
- [x] 1.4 新增 `libs/api/hiagent_api/_up_signer.py`：凭证校验、query 规范化与编码（`unquote_plus` / `quote(safe="-_.~")`）、path 解码（`unquote`）、canonical request、待签串、派生密钥、`sign()`。
- [x] 1.5 1.1–1.3 全部通过。

## 2. 模型

- [x] 2.1 先写模型测试：旧写法可用、新字段可选、`Id` 仍为必填（缺参时 `ValidationError`）、`LongLiveRequest(Id=...)` 以 `ID` 序列化、`DownloadRequest.SaveTo` 不进入 dump 结果、响应新字段可解析。
- [x] 2.2 按 design 修改 `libs/api/hiagent_api/up_types.py`，补全字段注释（`Expire` 格式与不过期写法、`ContentType` 建议填真实类型、`Sha256` 可省略）。

## 3. UpService

- [x] 3.1 先写请求测试（requests fake adapter），覆盖 design「测试方案」第 3–6 项，包括：
  - 五个方法均为 `POST`，按收到的请求重算签名一致，`X-Content-Sha256` 与请求体一致；
  - query 和请求体形状，`Download` 的 `Key` 在 query、请求体为空；
  - sha256 转小写，`Sha256` 为 `None`/`""`/空白时自动计算；
  - 文件已 seek 到非零偏移时只哈希并上传剩余部分；提供 `Sha256` 时不可 seek 的流也能上传；未提供且不可 seek 时报错；
  - `Id` 空串报错且先于读文件和 `seekable()`，空白 `Id` 照发；`LongLive` 缺 `ID` 不发请求；
  - productCode 有无；用 `CaseInsensitiveDict` 合并 Header，不重复、不修改 `service_info.header`；User-Agent 取自 `volcengine.VERSION`；
  - 初始化后 `set_ak`/`set_sk` 生效；STS token；未配置凭证时不签名照发；只配一半时报错；
  - 五个方法缺 `Result` 时都报错。
- [x] 3.2 实现私有 `_send()`，五个方法改用它；移除对 `SignerV4`、`Service.get/json/prepare_request` 的使用（`ApiInfo` 原本就是 `POST`，保持不变）。
- [x] 3.3 `UploadRaw` 流式计算 sha256 并 seek 回原位置后上传。
- [x] 3.4 修正 `DownloadKey` 的 docstring 与各方法 docstring 中的字段说明。

## 4. 下载落盘

- [x] 4.1 先写落盘测试：
  - 成功下载、自动建目录；
  - 空白 `SaveTo` 不发请求；
  - 非 200 不建文件且释放连接；
  - 中途中断两种（fake adapter）：响应体短于 `Content-Length`、响应流读到一半抛异常；旧文件都不变且没有残留临时文件；
  - 带 `Content-Encoding` 或没有 `Content-Length` 时跳过长度核对；
  - 符号链接、已有文件的权限位保留。
- [x] 4.2 实现：`with` 包住流式响应，临时文件、长度核对、`copymode`、`os.replace`；做两项变异验证：改成直接写目标文件时中断用例必须失败，去掉长度核对时短响应用例必须失败。
- [x] 4.3 自审补充（先写测试，再实现）：AK 尾随换行用 `fullmatch` 拦截；只配 STS token 时报错；不跟随重定向，3xx 和空响应体错误带状态码；`SaveTo` 为目录或非普通文件时发请求前报错；覆盖已有文件时临时文件以 0600 创建。变异验证：临时文件改回 0o666 时 0600 用例失败。

## 5. 调用方、示例与文档

- [x] 5.1 `agent-harness` 的 `test_up_endpoints.py` 补充 `upload_raw_file`、`download_file` 回归用例。
- [x] 5.2 更新 `libs/api/examples/up/*`：`Sha256` 可省略，补新字段用法；`ContentType="plain/text"` 改为 `text/plain`（`up_uploadraw.py`、`up_full.py`）。
- [x] 5.3 新增 `libs/api/tests/test_up_e2e.py`（`e2e` 标记，缺环境变量时跳过）；`.env-sample` 已有 `HIAGENT_UP_UPLOAD_ENDPOINT`、`HIAGENT_UP_DOWNLOAD_ENDPOINT`，确认无需新增。
- [x] 5.4 按 proposal「影响」整理发版说明中的行为变化（仓库没有 CHANGELOG，发版说明以 proposal「影响」为准）。

## 6. 验证

- [x] 6.1 `uv run pytest libs/api/tests -q`。
- [ ] 6.2 `uv run pytest -q`（workspace 回归）被既有问题阻断：agent-harness 4 个测试文件收集时报 `ModuleNotFoundError: cli_anything`，暂存本次改动后同样复现。替代验证：`uv run pytest libs -q` 158 passed / 4 skipped，`PYTHONPATH=agent-harness uv run pytest agent-harness -q` 52 passed。原文：agent-harness 不在 workspace 内，单独执行 `PYTHONPATH=agent-harness uv run pytest agent-harness/cli_anything/hiagent_sdk/tests/test_up_endpoints.py -q`。
- [x] 6.3 `uv run ruff check .`、`git diff --check`。（workspace 未装 ruff，改用 `uvx ruff` 0.17.6；本次新增和改动的文件无告警，其余既有告警未处理。）
- [x] 6.4 `uv build --package hiagent-api`，检查 wheel 内容并记录 `tests/`（含 `tests/data/`）是否被打入（既有打包问题，本次只记录）。结果：构建成功，wheel 中包含 `tests/` 与 `tests/data/up_signature_vectors.json`。
- [ ] 6.5 在关闭匿名访问的 UP 上跑一次 e2e，记录 UP 版本、各步状态码，不记录凭据。（未执行：需要真实环境，开启方式见 `libs/api/tests/test_up_e2e.py`。）
