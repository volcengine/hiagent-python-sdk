"""V1 page metrics query service."""

from __future__ import annotations

from ._helpers import from_dict
from ._server_service import ServerService, put_if
from .types import (
    V1MetricAggregatorParams,
    V1MetricBreakdownParams,
    V1MetricBreakdownResult,
    V1MetricFilterParams,
    V1MetricOverviewParams,
    V1MetricOverviewResult,
    V1MetricTopKParams,
    V1MetricTopKResult,
    V1MetricTrendParams,
    V1MetricTrendResult,
)


def _aggregator(params: V1MetricAggregatorParams) -> dict:
    if not params.start_time or not params.end_time:
        raise ValueError("hibot: metric start_time and end_time are required")
    body = {"StartTime": params.start_time, "EndTime": params.end_time}
    put_if(body, "StepSeconds", params.step_seconds, allow_empty=True)
    return body


def _filter(params: V1MetricFilterParams) -> dict:
    body = {}
    for key, value in (
        ("WorkspaceID", params.workspace_id),
        ("AgentIDs", params.agent_ids),
        ("Channels", params.channels),
        ("Models", params.models),
        ("Statuses", params.statuses),
        ("ResponseModes", params.response_modes),
    ):
        put_if(body, key, value)
    return body


class MetricsService(ServerService):
    def overview(self, params: V1MetricOverviewParams) -> V1MetricOverviewResult:
        body = {
            "Filter": _filter(params.filter),
            "Aggregator": _aggregator(params.aggregator),
        }
        put_if(body, "WorkspaceID", params.workspace_id)
        result = self._action("GetMetricOverview", body)
        return from_dict(V1MetricOverviewResult, result) or V1MetricOverviewResult()

    def trend(self, params: V1MetricTrendParams) -> V1MetricTrendResult:
        if not params.metric:
            raise ValueError("hibot: metric name is required")
        body = {
            "Metric": params.metric,
            "Filter": _filter(params.filter),
            "Aggregator": _aggregator(params.aggregator),
        }
        put_if(body, "GroupBy", params.group_by)
        put_if(body, "Statistic", params.statistic)
        put_if(body, "WorkspaceID", params.workspace_id)
        result = self._action("GetMetricTrend", body)
        return from_dict(V1MetricTrendResult, result) or V1MetricTrendResult()

    def top_k(self, params: V1MetricTopKParams) -> V1MetricTopKResult:
        if not params.metric or not params.group_by or params.limit <= 0:
            raise ValueError("hibot: metric, group_by, and positive limit are required")
        body = {
            "Metric": params.metric,
            "GroupBy": params.group_by,
            "Filter": _filter(params.filter),
            "Aggregator": _aggregator(params.aggregator),
            "Limit": params.limit,
        }
        put_if(body, "WorkspaceID", params.workspace_id)
        result = self._action("GetMetricTopK", body)
        return from_dict(V1MetricTopKResult, result) or V1MetricTopKResult()

    def breakdown(self, params: V1MetricBreakdownParams) -> V1MetricBreakdownResult:
        if not params.metric or not params.group_by:
            raise ValueError("hibot: metric and group_by are required")
        body = {
            "Metric": params.metric,
            "GroupBy": params.group_by,
            "Filter": _filter(params.filter),
            "Aggregator": _aggregator(params.aggregator),
        }
        put_if(body, "WorkspaceID", params.workspace_id)
        result = self._action("GetMetricBreakdown", body)
        return from_dict(V1MetricBreakdownResult, result) or V1MetricBreakdownResult()


__all__ = ["MetricsService"]
