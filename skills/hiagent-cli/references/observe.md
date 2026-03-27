# observe 模块（重点）

目标：使用 Observe 观测服务进行 API Token 管理与 Trace/Span 查询。

对应子命令：

- `observe token create`
- `observe trace list`

## 前置条件（常见踩坑点）

observe 模块会显式调用 `ensure_volc_credentials()`，因此必须满足以下任一方式：

- 环境变量：
  - `VOLC_ACCESSKEY`
  - `VOLC_SECRETKEY`
- 或 `~/.volc/.env` 文件包含以上两项
- 或 `~/.volc/credentials`（default profile）
- 或 `~/.volc/config`（JSON，包含 ak/sk）

如果不满足，会报错：

- `Volcengine credentials not found.`

## observe token create

用途：为 observe 观测服务创建 API Token（通常用于后续观测/埋点系统对接）。

必填参数：

- `--workspace-id <WORKSPACE_ID>`
- `--custom-app-id <CUSTOM_APP_ID>`

命令：

```bash
<CMD> --json observe token create \
  --workspace-id <WORKSPACE_ID> \
  --custom-app-id <CUSTOM_APP_ID>
```

输出要点（JSON 模式）：

- `success`：是否成功
- `message`：成功时会包含 expires 信息
- `data.Token`：API Token（不要在团队沟通中随意转发 token）
- `data.ExpiresIn`：有效期（秒）

## observe trace list

用途：列出 trace spans，支持分页与排序。

必填参数：

- `--workspace-id <WORKSPACE_ID>`

可选参数：

- `--page-size <N>`：默认 10
- `--last-id <ID>`：用于分页，默认空字符串
- `--sort-by`：`StartTime` | `Latency` | `LatencyFirstResp` | `TotalTokens`
- `--sort-order`：`Asc` | `Desc`

命令（按开始时间倒序）：

```bash
<CMD> --json observe trace list \
  --workspace-id <WORKSPACE_ID> \
  --page-size 10 \
  --sort-by StartTime \
  --sort-order Desc
```

分页（使用上一页返回的 last-id 继续）：

```bash
<CMD> --json observe trace list \
  --workspace-id <WORKSPACE_ID> \
  --page-size 20 \
  --last-id "<LAST_ID>" \
  --sort-by StartTime \
  --sort-order Desc
```

`<LAST_ID>` 取值建议使用上一页最后一条 item 的 `DocID`。

输出结构（JSON 模式）：

- `data.total`：总量
- `data.has_more`：是否还有下一页
- `data.items`：span 列表（每个元素为 model_dump 后的 dict）

item 关键字段（便于排查与筛选）：

- `DocID`：分页游标候选值
- `Context.TraceID` / `Context.SpanID`：链路定位
- `Status.Code` / `Status.Message`：错误原因
- `StartTime` / `EndTime`：耗时计算依据

## 排障清单（按优先级）

1. 鉴权错误：先确认 `VOLC_ACCESSKEY/VOLC_SECRETKEY` 或 `~/.volc/.env`
2. workspace 不匹配：确认 `--workspace-id` 与当前环境一致
3. endpoint/region 错误：用 `config show` 查看 effective 配置（环境变量可能覆盖项目配置）
4. 依赖缺失：`Missing dependency: hiagent-api` 时需安装 `libs/api`
