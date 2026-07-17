"""Contract tests for hibot-server capabilities added after the initial SDK."""

from __future__ import annotations

import json
from urllib.parse import parse_qs, urlsplit

import httpx
from hibot import (
    V1ArkSkillHubGetParams,
    V1ArkSkillHubImportParams,
    V1ArkSkillHubListParams,
    V1ChannelDeleteParams,
    V1ChannelGetParams,
    V1ChannelListParams,
    V1ChannelNewParams,
    V1ChannelUpdateParams,
    V1CronJobDeleteParams,
    V1CronJobGetParams,
    V1CronJobListParams,
    V1CronJobNewParams,
    V1CronJobRunListParams,
    V1CronJobRunNowParams,
    V1CronJobRunSyncListParams,
    V1CronJobToggleParams,
    V1CronJobUpdateParams,
    V1MCPBatchGetParams,
    V1MemoryFileDeleteParams,
    V1MemoryFileGetParams,
    V1MemoryFileListParams,
    V1MemoryFileSearchParams,
    V1MemoryFileUpsertParams,
    V1MemoryStoreDeleteParams,
    V1MemoryStoreGetParams,
    V1MemoryStoreListParams,
    V1MemoryStoreNewParams,
    V1MemoryStoreUpdateParams,
    V1MetricAggregatorParams,
    V1MetricBreakdownParams,
    V1MetricOverviewParams,
    V1MetricTopKParams,
    V1MetricTrendParams,
    V1ResourceBatchCreateItemParams,
    V1ResourceBatchCreateParams,
    V1ResourceMoveParams,
    V1RunGetParams,
    V1RunListParams,
    V1RuntimeAPIKeyDeleteParams,
    V1RuntimeAPIKeyGetParams,
    V1RuntimeAPIKeyListParams,
    V1RuntimeAPIKeyNewParams,
    V1RuntimeAPIKeyUpdateParams,
    V1RuntimeAPIKeyUserInfoParams,
    V1SkillBatchGetParams,
    V1SkillParseParams,
    V1SpanGetParams,
    V1SpanListParams,
    V1TraceListParams,
)


def _action(req: httpx.Request) -> str:
    return parse_qs(urlsplit(str(req.url)).query).get("Action", [""])[0]


def _assert_server_calls(calls) -> None:
    for req in calls:
        query = parse_qs(urlsplit(str(req.url)).query)
        assert query["Version"] == ["2026-04-23"]
        assert req.headers["x-top-service"] == "hibot-server"


def test_existing_resource_services_cover_new_server_actions(
    client_factory, make_handler, ok_envelope
):
    handler = make_handler(
        [
            ok_envelope({"Name": "demo", "BlobID": "blob-1"}),
            ok_envelope({"Items": [{"Slug": "demo", "Name": "Demo"}]}),
            ok_envelope({"Skill": {"Slug": "demo", "Name": "Demo"}}),
            ok_envelope({"Name": "Demo", "BlobID": "blob-2"}),
            ok_envelope({"Items": [{"ID": "skill-1"}]}),
            ok_envelope({"Items": [{"ID": "mcp-1"}]}),
            ok_envelope({"Items": [{"ID": "resource-1"}]}),
            ok_envelope({}),
        ]
    )
    client = client_factory(handler)

    parsed = client.v1.skills.parse(V1SkillParseParams(blob_id="blob-1"))
    hub = client.v1.skills.list_ark_skill_hub(V1ArkSkillHubListParams())
    detail = client.v1.skills.get_ark_skill_hub(V1ArkSkillHubGetParams(slug="demo"))
    imported = client.v1.skills.import_ark_skill_hub(
        V1ArkSkillHubImportParams(slug="demo")
    )
    skills = client.v1.skills.batch_get(V1SkillBatchGetParams(ids=["skill-1"]))
    mcps = client.v1.mcps.batch_get(V1MCPBatchGetParams(ids=["mcp-1"]))
    resources = client.v1.resources.batch_create(
        V1ResourceBatchCreateParams(
            items=[V1ResourceBatchCreateItemParams(name="runbook", blob_id="blob-3")]
        )
    )
    client.v1.resources.move(
        V1ResourceMoveParams(
            resource_id="resource-1",
            old_directory_id="old",
            new_directory_id="new",
        )
    )

    assert parsed.name == "demo"
    assert hub.items[0].slug == "demo"
    assert detail.slug == "demo"
    assert imported.blob_id == "blob-2"
    assert skills[0].id == "skill-1"
    assert mcps[0].id == "mcp-1"
    assert resources[0].id == "resource-1"
    assert [_action(req) for req in handler.calls] == [
        "ParseSkill",
        "ListArkSkillHubSkills",
        "GetArkSkillHubSkill",
        "ImportArkSkillHubSkill",
        "BatchGetSkills",
        "BatchGetMCPs",
        "BatchCreateResources",
        "MoveResource",
    ]
    assert json.loads(handler.calls[6].content)["Items"] == [
        {"Name": "runbook", "BlobID": "blob-3"}
    ]
    _assert_server_calls(handler.calls)


def test_channels_runtime_api_keys_and_runs(client_factory, make_handler, ok_envelope):
    handler = make_handler(
        [
            ok_envelope({"ID": "channel-1"}),
            ok_envelope({"Items": [{"ID": "channel-1"}]}),
            ok_envelope({"ID": "channel-1", "Name": "web"}),
            ok_envelope({}),
            ok_envelope({}),
            ok_envelope(
                {
                    "Item": {"ID": "key-1", "AgentID": "agent-1"},
                    "RawKey": "raw-once",
                }
            ),
            ok_envelope({"Items": [{"ID": "key-1"}]}),
            ok_envelope({"RawKey": "raw-revealed"}),
            ok_envelope({}),
            ok_envelope({}),
            ok_envelope({"Items": [{"ID": "run-1"}]}),
            ok_envelope({"ID": "run-1", "Status": "succeeded"}),
        ]
    )
    client = client_factory(handler)

    channel = client.v1.channels.create(
        V1ChannelNewParams(agent_id="agent-1", name="web")
    )
    channels = client.v1.channels.list(V1ChannelListParams(agent_id="agent-1"))
    detail = client.v1.channels.get(V1ChannelGetParams(channel_id="channel-1"))
    client.v1.channels.update(
        V1ChannelUpdateParams(channel_id="channel-1", name="renamed")
    )
    client.v1.channels.delete(V1ChannelDeleteParams(channel_id="channel-1"))

    created_key = client.v1.runtime_api_keys.create(
        V1RuntimeAPIKeyNewParams(agent_id="agent-1", expired="30d")
    )
    keys = client.v1.runtime_api_keys.list(
        V1RuntimeAPIKeyListParams(agent_id="agent-1")
    )
    raw_key = client.v1.runtime_api_keys.reveal(
        V1RuntimeAPIKeyGetParams(
            agent_id="agent-1",
            id="key-1",
            user_info=V1RuntimeAPIKeyUserInfoParams(
                user_name="tester",
                password="password",
            ),
        )
    )
    client.v1.runtime_api_keys.update(
        V1RuntimeAPIKeyUpdateParams(
            agent_id="agent-1",
            id="key-1",
            description="rotated",
        )
    )
    client.v1.runtime_api_keys.delete(
        V1RuntimeAPIKeyDeleteParams(agent_id="agent-1", id="key-1")
    )
    runs = client.v1.runs.list(V1RunListParams(agent_id="agent-1"))
    run = client.v1.runs.get(V1RunGetParams(run_id="run-1"))

    assert channel.id == channels[0].id == detail.id == "channel-1"
    assert created_key.item is not None
    assert created_key.item.id == "key-1"
    assert created_key.raw_key == "raw-once"
    assert keys[0].id == "key-1"
    assert raw_key == "raw-revealed"
    assert runs[0].id == run.id == "run-1"
    assert [_action(req) for req in handler.calls] == [
        "CreateChannel",
        "ListChannels",
        "GetChannel",
        "UpdateChannel",
        "DeleteChannel",
        "CreateRuntimeAPIKey",
        "ListRuntimeAPIKeys",
        "GetRuntimeAPIKey",
        "UpdateRuntimeAPIKey",
        "DeleteRuntimeAPIKey",
        "ListRuns",
        "GetRun",
    ]
    _assert_server_calls(handler.calls)


def test_cron_job_server_actions(client_factory, make_handler, ok_envelope):
    handler = make_handler(
        [
            ok_envelope({"Items": [{"ID": "cron-1"}], "Page": {"Total": 1}}),
            ok_envelope({"Items": [{"Status": "succeeded"}]}),
            ok_envelope(
                {
                    "Items": [{"ID": "run-1", "CronJobID": "cron-1"}],
                    "NextCursorUpdatedAt": "100",
                    "NextCursorID": "run-1",
                }
            ),
            ok_envelope({"ID": "cron-1", "Name": "daily"}),
            ok_envelope({"CronJobID": "cron-2", "NextRunAt": "tomorrow"}),
            ok_envelope({}),
            ok_envelope({}),
            ok_envelope({"ID": "cron-1", "Enabled": False}),
            ok_envelope(
                {
                    "CronJobID": "cron-1",
                    "Status": "pending",
                    "TriggerType": "manual",
                }
            ),
        ]
    )
    client = client_factory(handler)

    listing = client.v1.cron_jobs.list(V1CronJobListParams(enabled=True))
    run_listing = client.v1.cron_jobs.list_runs(
        V1CronJobRunListParams(cron_job_id="cron-1")
    )
    sync_listing = client.v1.cron_jobs.list_runs_for_sync(
        V1CronJobRunSyncListParams(cursor_updated_at="0")
    )
    detail = client.v1.cron_jobs.get(V1CronJobGetParams(cron_job_id="cron-1"))
    created = client.v1.cron_jobs.create(
        V1CronJobNewParams(
            agent_id="agent-1",
            name="daily",
            prompt="summarize",
            schedule_type="cron",
            schedule_value="0 9 * * *",
            delivery_channel="webchat",
            delivery_to="user-1",
        )
    )
    client.v1.cron_jobs.update(
        V1CronJobUpdateParams(cron_job_id="cron-1", prompt="new prompt")
    )
    client.v1.cron_jobs.delete(V1CronJobDeleteParams(cron_job_id="cron-2"))
    toggled = client.v1.cron_jobs.toggle(
        V1CronJobToggleParams(cron_job_id="cron-1", enabled=False)
    )
    triggered = client.v1.cron_jobs.run_now(V1CronJobRunNowParams(cron_job_id="cron-1"))

    assert listing.items[0].id == detail.id == "cron-1"
    assert run_listing.items[0].status == "succeeded"
    assert sync_listing.items[0].id == "run-1"
    assert sync_listing.next_cursor_id == "run-1"
    assert created.cron_job_id == "cron-2"
    assert toggled.enabled is False
    assert triggered.trigger_type == "manual"
    assert [_action(req) for req in handler.calls] == [
        "ListCronJobs",
        "ListCronJobRuns",
        "ListCronJobRunsForSync",
        "GetCronJob",
        "CreateCronJob",
        "UpdateCronJob",
        "DeleteCronJob",
        "ToggleCronJob",
        "RunCronJobNow",
    ]
    _assert_server_calls(handler.calls)


def test_observation_metrics_overview_and_memory_actions(
    client_factory, make_handler, ok_envelope
):
    handler = make_handler(
        [
            ok_envelope({"Items": [{"TraceID": "trace-1"}], "Total": 1}),
            ok_envelope({"Items": [{"SpanID": "span-1"}], "Total": 1}),
            ok_envelope({"Span": {"TraceID": "trace-1", "SpanID": "span-1"}}),
            ok_envelope({"Summary": {"AgentTotal": 1}}),
            ok_envelope(
                {
                    "Data": {"RequestCount": 3, "SuccessRate": 1.0},
                    "EffectiveStepSeconds": 60,
                }
            ),
            ok_envelope(
                {
                    "Series": [{"Time": "2026-01-01T00:00:00Z", "Value": 3}],
                    "EffectiveStepSeconds": 60,
                }
            ),
            ok_envelope(
                {
                    "Items": [{"Group": "agent-1", "Value": 3}],
                    "EffectiveLimit": 5,
                }
            ),
            ok_envelope(
                {
                    "Groups": [
                        {
                            "Group": "succeeded",
                            "Points": [{"Time": "2026-01-01T00:00:00Z", "Value": 3}],
                        }
                    ],
                    "EffectiveStepSeconds": 60,
                }
            ),
            ok_envelope({"ID": "store-1"}),
            ok_envelope({"Items": [{"ID": "store-1"}], "Page": {"Total": 1}}),
            ok_envelope({"ID": "store-1", "Alias": "project"}),
            ok_envelope({}),
            ok_envelope({}),
            ok_envelope({"Items": [{"ID": "file-1"}], "Page": {"Total": 1}}),
            ok_envelope({"Items": [{"ID": "file-1"}], "Page": {"Total": 1}}),
            ok_envelope({"ID": "file-1", "Path": "/notes.md"}),
            ok_envelope(
                {
                    "FileID": "file-1",
                    "Path": "/notes.md",
                    "ContentSha256": "sha",
                    "Revision": 1,
                }
            ),
            ok_envelope({}),
        ]
    )
    client = client_factory(handler)

    traces = client.v1.observations.list_traces(
        V1TraceListParams(session_id="session-1")
    )
    spans = client.v1.observations.list_trace_spans(
        V1SpanListParams(trace_id="trace-1")
    )
    span = client.v1.observations.get_span_detail(
        V1SpanGetParams(trace_id="trace-1", span_id="span-1")
    )
    overview = client.v1.overview.get()

    aggregator = V1MetricAggregatorParams(
        start_time="2026-01-01T00:00:00Z",
        end_time="2026-01-01T01:00:00Z",
    )
    metric_overview = client.v1.metrics.overview(
        V1MetricOverviewParams(aggregator=aggregator)
    )
    trend = client.v1.metrics.trend(
        V1MetricTrendParams(metric="chat_request", aggregator=aggregator)
    )
    top_k = client.v1.metrics.top_k(
        V1MetricTopKParams(
            metric="chat_request",
            group_by="agent",
            aggregator=aggregator,
            limit=5,
        )
    )
    breakdown = client.v1.metrics.breakdown(
        V1MetricBreakdownParams(
            metric="chat_request",
            group_by="status",
            aggregator=aggregator,
        )
    )

    store = client.v1.memories.create_store(
        V1MemoryStoreNewParams(
            name="Project",
            alias="project",
            description="Shared project memory",
        )
    )
    stores = client.v1.memories.list_stores(V1MemoryStoreListParams())
    store_detail = client.v1.memories.get_store(
        V1MemoryStoreGetParams(store_id="store-1")
    )
    client.v1.memories.update_store(
        V1MemoryStoreUpdateParams(store_id="store-1", description="Updated")
    )
    client.v1.memories.delete_store(V1MemoryStoreDeleteParams(store_id="store-2"))
    files = client.v1.memories.list_files(V1MemoryFileListParams(store_id="store-1"))
    searched = client.v1.memories.search_files(
        V1MemoryFileSearchParams(store_id="store-1", keyword="notes")
    )
    file_detail = client.v1.memories.get_file(
        V1MemoryFileGetParams(store_id="store-1", path="/notes.md")
    )
    upserted = client.v1.memories.upsert_file(
        V1MemoryFileUpsertParams(
            store_id="store-1",
            path="/notes.md",
            content="hello",
        )
    )
    client.v1.memories.delete_file(
        V1MemoryFileDeleteParams(store_id="store-1", path="/notes.md")
    )

    assert traces.items[0].trace_id == "trace-1"
    assert spans.items[0].span_id == span.span_id == "span-1"
    assert overview.summary["AgentTotal"] == 1
    assert metric_overview.data is not None
    assert metric_overview.data.request_count == 3
    assert trend.series is not None and trend.series[0].value == 3
    assert top_k.items[0].group == "agent-1"
    assert breakdown.groups[0].points[0].value == 3
    assert store.id == stores.items[0].id == store_detail.id == "store-1"
    assert files.items[0].id == searched.items[0].id == file_detail.id == "file-1"
    assert upserted.file_id == "file-1"
    assert [_action(req) for req in handler.calls] == [
        "ListTraces",
        "ListTraceSpans",
        "GetSpanDetail",
        "GetOverview",
        "GetMetricOverview",
        "GetMetricTrend",
        "GetMetricTopK",
        "GetMetricBreakdown",
        "CreateMemoryStore",
        "ListMemoryStores",
        "GetMemoryStore",
        "UpdateMemoryStore",
        "DeleteMemoryStore",
        "ListMemoryFiles",
        "SearchMemoryFiles",
        "GetMemoryFile",
        "UpsertMemoryFile",
        "DeleteMemoryFile",
    ]
    _assert_server_calls(handler.calls)
