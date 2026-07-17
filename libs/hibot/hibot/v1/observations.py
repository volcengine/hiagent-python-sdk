"""V1 trace and span observation service."""

from __future__ import annotations

from ._helpers import from_dict
from ._server_service import ServerService, put_if
from .types import (
    V1SpanDetail,
    V1SpanGetParams,
    V1SpanList,
    V1SpanListParams,
    V1TraceList,
    V1TraceListParams,
)


class ObservationsService(ServerService):
    def list_traces(
        self, params: V1TraceListParams = V1TraceListParams()
    ) -> V1TraceList:
        body = {}
        put_if(body, "ScrollID", params.scroll_id)
        put_if(body, "PageSize", params.page_size, allow_empty=True)
        if params.session_id:
            body["Filter"] = {"SessionID": params.session_id}
        put_if(body, "WorkspaceID", params.workspace_id)
        return from_dict(V1TraceList, self._action("ListTraces", body)) or V1TraceList()

    def list_trace_spans(self, params: V1SpanListParams) -> V1SpanList:
        if not params.trace_id:
            raise ValueError("hibot: trace id is required")
        body = {"TraceID": params.trace_id}
        put_if(body, "ScrollID", params.scroll_id)
        put_if(body, "PageSize", params.page_size, allow_empty=True)
        put_if(body, "WorkspaceID", params.workspace_id)
        return (
            from_dict(V1SpanList, self._action("ListTraceSpans", body)) or V1SpanList()
        )

    def get_span_detail(self, params: V1SpanGetParams) -> V1SpanDetail:
        if not params.trace_id or not params.span_id:
            raise ValueError("hibot: trace id and span id are required")
        body = {"TraceID": params.trace_id, "SpanID": params.span_id}
        put_if(body, "WorkspaceID", params.workspace_id)
        result = self._action("GetSpanDetail", body)
        span = result.get("Span") if isinstance(result, dict) else None
        decoded = from_dict(V1SpanDetail, span) or V1SpanDetail()
        if not decoded.span_id:
            raise ValueError("hibot: get span detail response missing SpanID")
        return decoded


__all__ = ["ObservationsService"]
