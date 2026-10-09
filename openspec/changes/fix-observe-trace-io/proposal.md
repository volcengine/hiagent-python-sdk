## 为什么

Observe 页面 trace 列表读取 trace-level 记录中的 `Attributes.input` 和 `Attributes.output`。Python 的 `sample_chainlit.py` 把输入写在没有 `span_type` 的 token Span，把输出写在 `core_llm` Span，当前聚合器无法将这些字段写入页面使用的 trace-level 属性。

## 变更内容

- 增加 `SpanType.ROOT`，让 Python 示例显式标记根 Span。
- 将输入写入 `start` Span，并使用 JSON 字符串格式，支持页面 JSON 预览。
- 将示例输出写入当前聚合器会提取的 `start` Span。
- 更新 Chainlit 示例的 root、start 和 output 属性。

## 非目标

- 不修改 OTLP 协议、Observe API 或服务端聚合器。
- 不改变 Observe Client 的鉴权、导出 Header 和 Token 请求体。
