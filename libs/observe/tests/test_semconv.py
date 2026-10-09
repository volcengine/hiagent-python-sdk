from hiagent_observe.semconv import SpanType


def test_span_type_root_matches_trace_level_root_value():
    assert SpanType.ROOT.value == "root"
