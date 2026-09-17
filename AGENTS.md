# HiAgent Python SDK 开发约束

本文档适用于 `/Users/bytedance/Documents/workspace/SDK/hiagent-python-sdk`，约束 SDK 源码、示例、测试、构建和依赖变更。仓库内更具体的 `AGENTS.md` 约定优先于本文档。

## 工程结构与目录边界

这是一个由 `uv` 管理的 Python workspace。业务代码按独立 SDK 包放在 `libs/` 下，各包拥有自己的 `pyproject.toml`、源码目录和测试目录。

| 目录 | 职责 | 修改边界 |
| --- | --- | --- |
| `libs/api/hiagent_api` | 通用 API 客户端、请求构造、TOP 签名、SSE、Observe/EVA/UP API 封装 | 公共请求协议和 API 行为的首要实现位置；改动请求头、签名或公共模型时必须检查所有调用方 |
| `libs/api/tests` | `hiagent_api` 的单元测试 | 与 `libs/api/hiagent_api` 的请求路径、签名和序列化行为同步维护；默认不得访问外网 |
| `libs/api/examples` | API 包的可运行示例，按 `knowledgebase`、`observe`、`tool`、`up`、`workflow` 分组 | 只调用公开 API；示例行为改变时同步修改环境变量样例和文档 |
| `libs/eva/hiagent_eva` | EVA 领域客户端和对 `hiagent_api` 的封装 | 不复制通用签名逻辑；EVA 特有行为在本包实现，通用协议变化要回查 `libs/api` |
| `libs/eva/tests` | EVA 客户端测试 | 当前目录可能尚不存在；修改 `libs/eva` 时必须创建并维护该目录，不能用 sample 代替测试 |
| `libs/eva/samples` | EVA 示例程序 | 只用于手工验证和演示，不计入默认单元测试覆盖；真实调用必须由环境变量显式开启 |
| `libs/hibot/hibot` | 独立的 HiBot/TOP 客户端、HTTP 请求和签名实现 | 这是独立签名链路，不能假定 `libs/api` 的 `Service` 实现会自动生效；改动头部或签名必须单独验证 |
| `libs/hibot/tests` | HiBot 客户端、签名和资源 API 测试 | 请求头、canonical request、签名包含的 Header 必须有断言 |
| `libs/hibot/testdata` | HiBot 测试固定数据 | 只放脱敏、稳定的测试输入；禁止放真实 AK/SK、Token 或线上响应 |
| `libs/observe/hiagent_observe` | OpenTelemetry 初始化、鉴权会话、Trace/OTLP 导出 | Token 请求协议和 Trace 导出协议分开处理；不能因增加 Trace Header 而擅自改变 Token 请求体 |
| `libs/observe/tests` | Observe 客户端、鉴权和导出测试 | 使用 mock 验证请求 URL、Header、请求体和生命周期；默认不得发送真实遥测数据 |
| `libs/observe/samples` | Observe 手工运行示例及相关资源 | 示例必须支持缺省可选配置；凭据从环境变量读取，禁止写入源码 |
| `libs/components/hiagent_components` | 可复用组件和集成能力 | 依赖其他 SDK 时只能使用其公开 API，不得跨包导入私有模块 |
| `libs/components/tests` | Components 单元测试 | 组件输入、输出和与 SDK 公共 API 的集成行为同步维护 |
| `libs/components/examples` | Components 示例 | 只展示公开用法，不承担协议回归测试职责 |
| `openspec/` | OpenSpec 变更提案、设计、规格和任务清单 | 协议或公共 API 变更先更新规格，再实施代码；不要把临时笔记混入规格目录 |
| `docs/`、`README*`、`.env-sample` | 用户文档、示例配置和环境变量说明 | 公共 API、初始化参数或示例配置改变时同步修改 |
| 根目录 `pyproject.toml`、`uv.lock`、`Makefile` | workspace、依赖锁定和统一构建入口 | 根配置只处理 workspace 级事项；包级依赖写入对应包的 `pyproject.toml`，再用 `uv` 更新锁文件 |

根目录不放具体 SDK 业务实现。公共逻辑应归属到实际拥有该协议的包，不能为了省事放进根目录工具文件。

## 跨包依赖规则

- 各包的公共入口以该包的公开导出和 README 为准。不得从其他包导入以下划线开头的模块、类、函数或常量。
- `libs/eva`、`libs/observe`、`libs/components` 可以依赖 `libs/api` 的公开能力，但不能依赖 `hiagent_api` 的内部实现细节。
- `libs/hibot` 保持自己的 HTTP 和签名实现。修改 `libs/api` 不代表 HiBot 自动获得同样行为，反之亦然。
- 修改共享协议（Header、URL、签名、错误码、请求体、序列化规则）时，先搜索所有包的请求入口，再逐个确认受影响的客户端、示例、文档和测试。
- 不直接修改生成代码、第三方源码、虚拟环境或缓存目录。若生成文件确实属于发布产物，修改生成源和生成步骤，并在验证记录中说明。
- 不用 `pip install` 直接改项目依赖。依赖变更应修改对应包的 `pyproject.toml`，使用 `uv` 解析并更新 `uv.lock`。

## SDK 公共 API 兼容性

- 当前最低 Python 版本以各包 `pyproject.toml` 为准，当前 workspace 按 Python 3.10 兼容。
- 新增可选配置时，保留原有构造函数、工厂函数和调用方式；新增参数放在参数列表末尾，并提供兼容的缺省值。
- 默认行为不能因为新增可选参数而改变。缺省值必须在文档、示例和测试中明确。
- 请求级配置覆盖客户端级默认配置时，要保持现有 Header 的大小写不敏感规则，并避免重复 Header。
- 不能硬编码 productCode、AK、SK、Token 或其他环境凭据，也不能在日志中输出它们。

## productCode 约定

- productCode 通过 Header `X-Trace-Product-Code` 传递，Header 名称比较不区分大小写。
- 客户端级 productCode 必须是可选配置；`None` 或去除首尾空白后的空字符串表示不发送该 Header。
- 配置值应在进入网络请求前统一 `strip()`，包含 HTTP 控制字符时立即抛出明确异常。
- 请求级显式 Header 优先于客户端级默认值。覆盖逻辑必须在测试中验证，包括不同大小写的 Header 名称。
- TOP 签名客户端必须在 canonical request 和签名生成前加入 productCode Header，否则服务端验签输入与实际请求不一致。
- Observe 的 CreateApiToken 请求体保持现有字段；productCode 按服务端协议加入 Trace/OTLP 导出请求，不得为了传递 Header 修改鉴权 Token 请求体。
- productCode 缺省时必须保持旧版调用行为；随机或未知 productCode 是否被服务端接受属于服务端校验问题，SDK 不得自行伪造有效性判断。

## SDK 改动与测试同步规则

这是硬性要求：新增或修改 SDK 源码，必须在同一变更中新增或修改对应测试，并实际运行测试。只改源码、不补测试，视为未完成。

### 修改前

1. 先确定改动归属的包、公开入口和真实请求路径。
2. 搜索相关 Header、URL、签名、请求体和调用方，确认是否同时影响 `api`、`eva`、`hibot`、`observe` 或 `components`。
3. 若是协议或公共 API 变更，先更新 `openspec/changes/<change-id>/` 下的 proposal、design、spec 和 tasks，并运行 OpenSpec 校验。
4. 先写失败测试或补充现有测试，再实现代码；测试应验证行为，不要只断言内部字段。

### 修改中

- 源码文件和测试文件按包一一对应：
  - `libs/api/hiagent_api/**` → `libs/api/tests/**`
  - `libs/eva/hiagent_eva/**` → `libs/eva/tests/**`；目录不存在就创建
  - `libs/hibot/hibot/**` → `libs/hibot/tests/**`
  - `libs/observe/hiagent_observe/**` → `libs/observe/tests/**`
  - `libs/components/hiagent_components/**` → `libs/components/tests/**`
- 新增或修改 API 参数，至少覆盖：显式传参、缺省值下的兼容行为、非法或边界输入。涉及请求的测试还要断言最终 URL、Header、请求体和签名输入。
- 修改签名、Header 注入、重试、SSE 或异步路径时，不能只测同步主路径；所有会发出请求的入口都要检查。
- 修改初始化配置时，必须测试配置从入口传到实际 client/service/request 的完整链路，不能只测配置对象自身。
- 若示例需要增加环境变量或初始化参数，同步修改对应 `examples`/`samples`、`.env-sample` 和 README；示例不替代单元测试。
- 默认测试使用 mock、fixture 或本地 fake server，不得依赖网络、账号、环境变量中的真实凭据。真实 API smoke test 必须显式启用，并单独标记为 e2e 或手工测试。

### 修改后必须运行

先运行受影响包的定向测试，再运行包级测试和构建。命令按实际改动选择，但至少要有一条对应测试命令：

```bash
# 定向测试
uv run pytest libs/<package>/tests/<test_file>.py -q

# 受影响包的完整测试
uv run pytest libs/api/tests -q
uv run pytest libs/eva/tests -q
uv run pytest libs/hibot/tests -q
uv run pytest libs/observe/tests -q
uv run pytest libs/components/tests -q

# workspace 回归测试
uv run pytest -q

# 构建受影响包；跨包或发布级改动执行 make build
uv build --package hiagent-api
uv build --package hiagent-eva
uv build --package hibot
uv build --package hiagent-observe
uv build --package hiagent-components
make build
```

上面命令中的包和测试目录按实际改动执行，不要求无关包重复构建；但 `uv run pytest -q` 应在公共协议或 workspace 级变更后尝试运行。静态检查工具可用时运行 `uv run ruff check .`。工具缺失、依赖下载失败或已有测试阻塞时，必须在交付说明中写出实际命令、实际错误和未覆盖范围，不能写成“已通过”。

### 交付前检查

- `git diff --check` 无空白错误。
- `git status --short` 中没有误改缓存、虚拟环境、凭据或无关生成文件。
- 新增文件已包含在 diff 中，测试文件和源码文件没有因为同名导致 pytest collection 冲突。
- 测试通过、跳过、失败和环境阻塞分别报告；没有实际运行的命令不作通过结论。
- 如果只修改文档或 OpenSpec 文本，可以不新增代码测试，但必须运行格式/校验命令，并说明没有 SDK 行为变更。

## 提交前的最小验收清单

1. 改动是否落在正确的 `libs/<package>` 边界内？
2. 每个 SDK 源码改动是否都有对应测试改动？
3. 缺省值、兼容调用、异常输入和真实请求线上的 Header 是否都有验证？
4. 受影响包测试、workspace 测试和构建是否实际运行？
5. 示例、README、`.env-sample` 和 OpenSpec 是否与实现一致？
6. 交付说明是否区分了通过、失败、跳过和未验证项目？
