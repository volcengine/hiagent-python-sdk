## 背景

页面 table 的输入列读取 `Attributes.input`，并把它解析为 JSON；输出列读取 `Attributes.output`。当前服务端 trace-level 聚合器对 `start` Span 提取 `input/output`，对 `end` Span 只提取 `output_raw`。

## 方案

Python 示例使用以下属性约定：

```text
root
├── start + input JSON
└── start + output JSON
```

`llm_start` 保存输入，`llm_new_token` 只保存首 token 延迟，`llm_end` 使用聚合器当前支持的 `start` 类型并写入输出。根 `do-worker` 显式设置为 `root`，并将输入以 JSON 形式写入。

## 兼容性

- 现有 `SpanType` 成员保持不变，只新增 `ROOT`。
- 仅调整示例和语义枚举，不改变 Observe Client 的公开初始化参数。
- `input_raw/output_raw` 继续保留原始文本。

## 验证

- 运行 Observe 测试和 Python 语法编译检查。
- 用新示例生成新 Trace，确认列表中的 input/output 及 JSON 预览可见。
