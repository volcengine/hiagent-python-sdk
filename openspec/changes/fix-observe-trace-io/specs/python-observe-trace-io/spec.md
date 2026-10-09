## 新增需求

### 需求：Python Observe 示例输出可展示的 Trace 输入输出

Python Observe 示例必须将根 Span 标记为 `root`，并将页面需要展示的输入输出写入当前 trace-level 聚合器可以读取的 Span。

#### 场景：Trace 列表展示输入和输出

- **当**使用 `sample_chainlit.py` 生成一条新的 Trace
- **并且**查询 Observe trace-level 列表
- **那么**返回项的 `Attributes.input` 必须是有效 JSON 文本
- **并且**返回项的 `Attributes.output` 必须是有效 JSON 文本
- **并且** `input_raw` 和 `output_raw` 必须保留原始文本

#### 场景：Span 详情展示子 Span 输入输出

- **当**选择 `llm_new_token` 或 `llm_end` 子 Span
- **那么** `GetTraceSpanDetail` 必须返回所选 Span 自身的属性
- **并且**输入或输出字段存在时，详情面板可以展示对应内容
