"""V1 Cron job service."""

from __future__ import annotations

from ._helpers import from_dict, list_from_items
from ._server_service import ServerService, encode_page, put_if
from .types import (
    V1CronJob,
    V1CronJobCreateResult,
    V1CronJobDeleteParams,
    V1CronJobGetParams,
    V1CronJobList,
    V1CronJobListParams,
    V1CronJobNewParams,
    V1CronJobRun,
    V1CronJobRunList,
    V1CronJobRunListParams,
    V1CronJobRunNowParams,
    V1CronJobRunNowResult,
    V1CronJobRunSync,
    V1CronJobRunSyncList,
    V1CronJobRunSyncListParams,
    V1CronJobToggleParams,
    V1CronJobUpdateParams,
    V1Page,
)


class CronJobsService(ServerService):
    def list(
        self, params: V1CronJobListParams = V1CronJobListParams()
    ) -> V1CronJobList:
        body = {}
        put_if(body, "AgentID", params.agent_id)
        put_if(body, "Source", params.source)
        put_if(body, "Enabled", params.enabled, allow_empty=True)
        put_if(body, "Page", encode_page(params.page))
        put_if(body, "WorkspaceID", params.workspace_id)
        result = self._action("ListCronJobs", body)
        out = V1CronJobList()
        if isinstance(result, dict):
            out.items = list_from_items(V1CronJob, result)
            out.page = from_dict(V1Page, result.get("Page"))
        return out

    def list_runs(self, params: V1CronJobRunListParams) -> V1CronJobRunList:
        if not params.cron_job_id:
            raise ValueError("hibot: cron job id is required")
        body = {"CronJobID": params.cron_job_id}
        put_if(body, "Page", encode_page(params.page))
        put_if(body, "WorkspaceID", params.workspace_id)
        result = self._action("ListCronJobRuns", body)
        out = V1CronJobRunList()
        if isinstance(result, dict):
            out.items = list_from_items(V1CronJobRun, result)
            out.page = from_dict(V1Page, result.get("Page"))
        return out

    def list_runs_for_sync(
        self, params: V1CronJobRunSyncListParams = V1CronJobRunSyncListParams()
    ) -> V1CronJobRunSyncList:
        body = {}
        put_if(body, "CursorUpdatedAt", params.cursor_updated_at)
        put_if(body, "CursorID", params.cursor_id)
        put_if(body, "PageSize", params.page_size, allow_empty=True)
        put_if(body, "WorkspaceID", params.workspace_id)
        result = self._action("ListCronJobRunsForSync", body)
        out = from_dict(V1CronJobRunSyncList, result) or V1CronJobRunSyncList()
        if isinstance(result, dict):
            out.items = list_from_items(V1CronJobRunSync, result)
        return out

    def get(self, params: V1CronJobGetParams) -> V1CronJob:
        if not params.cron_job_id:
            raise ValueError("hibot: cron job id is required")
        body = {"CronJobID": params.cron_job_id}
        put_if(body, "WorkspaceID", params.workspace_id)
        result = self._action("GetCronJob", body)
        decoded = from_dict(V1CronJob, result) or V1CronJob()
        if not decoded.id:
            raise ValueError("hibot: get cron job response missing ID")
        return decoded

    def create(self, params: V1CronJobNewParams) -> V1CronJobCreateResult:
        required = (
            params.agent_id,
            params.name,
            params.prompt,
            params.schedule_type,
            params.schedule_value,
            params.delivery_channel,
            params.delivery_to,
        )
        if not all(required):
            raise ValueError("hibot: cron job required fields are missing")
        body = {
            "AgentID": params.agent_id,
            "Name": params.name,
            "Prompt": params.prompt,
            "ScheduleType": params.schedule_type,
            "ScheduleValue": params.schedule_value,
            "DeliveryChannel": params.delivery_channel,
            "DeliveryTo": params.delivery_to,
        }
        for key, value in (
            ("Description", params.description),
            ("ScheduleTimezone", params.schedule_timezone),
            ("Enabled", params.enabled),
            ("Config", params.config),
            ("CorrelationID", params.correlation_id),
            ("WorkspaceID", params.workspace_id),
        ):
            put_if(
                body,
                key,
                value,
                allow_empty=value is not None and not isinstance(value, str),
            )
        result = self._action("CreateCronJob", body)
        decoded = from_dict(V1CronJobCreateResult, result) or V1CronJobCreateResult()
        if not decoded.cron_job_id:
            raise ValueError("hibot: create cron job response missing CronJobID")
        return decoded

    def update(self, params: V1CronJobUpdateParams) -> None:
        if not params.cron_job_id:
            raise ValueError("hibot: cron job id is required")
        body = {"CronJobID": params.cron_job_id}
        for key, value in (
            ("Name", params.name),
            ("Description", params.description),
            ("Prompt", params.prompt),
            ("ScheduleType", params.schedule_type),
            ("ScheduleValue", params.schedule_value),
            ("ScheduleTimezone", params.schedule_timezone),
            ("DeliveryChannel", params.delivery_channel),
            ("DeliveryTo", params.delivery_to),
            ("Enabled", params.enabled),
            ("Config", params.config),
            ("UpdateFields", params.update_fields),
        ):
            put_if(body, key, value, allow_empty=True)
        put_if(body, "CorrelationID", params.correlation_id)
        put_if(body, "WorkspaceID", params.workspace_id)
        self._action("UpdateCronJob", body)

    def delete(self, params: V1CronJobDeleteParams) -> None:
        if not params.cron_job_id:
            raise ValueError("hibot: cron job id is required")
        body = {"CronJobID": params.cron_job_id}
        put_if(body, "CancelRunning", params.cancel_running, allow_empty=True)
        put_if(body, "CorrelationID", params.correlation_id)
        put_if(body, "WorkspaceID", params.workspace_id)
        self._action("DeleteCronJob", body)

    def toggle(self, params: V1CronJobToggleParams) -> V1CronJob:
        if not params.cron_job_id:
            raise ValueError("hibot: cron job id is required")
        body = {"CronJobID": params.cron_job_id, "Enabled": params.enabled}
        put_if(body, "CorrelationID", params.correlation_id)
        put_if(body, "WorkspaceID", params.workspace_id)
        result = self._action("ToggleCronJob", body)
        return from_dict(V1CronJob, result) or V1CronJob()

    def run_now(self, params: V1CronJobRunNowParams) -> V1CronJobRunNowResult:
        if not params.cron_job_id:
            raise ValueError("hibot: cron job id is required")
        body = {"CronJobID": params.cron_job_id}
        put_if(body, "CorrelationID", params.correlation_id)
        put_if(body, "WorkspaceID", params.workspace_id)
        result = self._action("RunCronJobNow", body)
        return from_dict(V1CronJobRunNowResult, result) or V1CronJobRunNowResult()


__all__ = ["CronJobsService"]
