"""Data classes for V1 API resources.

All result classes are decoded from server responses with PascalCase JSON
field names (mirroring the Go SDK structs). Parameter classes use Python
``snake_case`` attributes; the corresponding service is responsible for
building the wire-format request dict.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# ---------------- Constants (sync with go/hibot/v1/types.go) ----------------

V1_MANAGED_AGENT_MODEL_DOUBAO_SEED_PRO = "doubao-seed-2-0-pro-260215"
V1_RESOURCE_TYPE_DOCUMENT_COLLECTION = "document_collection"
V1_MCP_TRANSPORT_STREAMABLE_HTTP = "streamable_http"

V1_MANAGED_AGENT_SKILL_TOOL_PARAMS_TYPE_SKILL = "skill"
V1_MANAGED_AGENT_MCP_TOOL_PARAMS_TYPE_MCP = "mcp"

V1_SESSION_CHAT_EVENT_DELTA = "delta"
V1_SESSION_CHAT_EVENT_COMPLETED = "completed"
V1_SESSION_CHAT_EVENT_FAILED = "failed"
V1_SESSION_CHAT_EVENT_RUN_CANCELLING = "run_cancelling"
V1_SESSION_CHAT_EVENT_RUN_CANCELLED = "run_cancelled"
V1_SESSION_CHAT_EVENT_APPROVAL_REQUEST = "approval_request"
V1_SESSION_CHAT_EVENT_APPROVAL_RESPONDED = "approval_responded"
V1_SESSION_CHAT_EVENT_TOOL_START = "tool_start"
V1_SESSION_CHAT_EVENT_TOOL_COMPLETE = "tool_complete"


# ---------------- Helpers ----------------


def _from_dict(cls, data):
    """Construct a dataclass instance from a server-side dict, ignoring extras."""
    if data is None:
        return None
    if isinstance(data, cls):
        return data
    if not isinstance(data, dict):
        return None
    fields_map = {f.name: f for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
    kwargs: Dict[str, Any] = {}
    for name, fld in fields_map.items():
        # support PascalCase keys
        for key in (fld.metadata.get("json"), name):
            if key and key in data:
                kwargs[name] = data[key]
                break
    return cls(**kwargs)


def _f(json_name: str):
    return field(default=None, metadata={"json": json_name})


# ---------------- Result types ----------------


@dataclass
class V1Page:
    page_num: Optional[int] = field(default=None, metadata={"json": "PageNum"})
    page_size: Optional[int] = field(default=None, metadata={"json": "PageSize"})
    total: Optional[int] = field(default=None, metadata={"json": "Total"})


@dataclass
class V1UploadBlob:
    blob_id: Optional[str] = field(default=None, metadata={"json": "BlobID"})


@dataclass
class V1Environment:
    id: Optional[str] = field(default=None, metadata={"json": "ID"})
    name: Optional[str] = field(default=None, metadata={"json": "Name"})
    description: Optional[str] = field(default=None, metadata={"json": "Description"})
    image_type: Optional[str] = field(default=None, metadata={"json": "ImageType"})
    env_vars: Optional[Any] = field(default=None, metadata={"json": "EnvVars"})
    cpu_limit: Optional[str] = field(default=None, metadata={"json": "CpuLimit"})
    memory_limit: Optional[str] = field(default=None, metadata={"json": "MemoryLimit"})
    pvc_size: Optional[str] = field(default=None, metadata={"json": "PVCSize"})
    data_path: Optional[str] = field(default=None, metadata={"json": "DataPath"})
    spec_code: Optional[str] = field(default=None, metadata={"json": "SpecCode"})
    created_at: Optional[str] = field(default=None, metadata={"json": "CreatedAt"})
    updated_at: Optional[str] = field(default=None, metadata={"json": "UpdatedAt"})
    created_by: Optional[str] = field(default=None, metadata={"json": "CreatedBy"})
    updated_by: Optional[str] = field(default=None, metadata={"json": "UpdatedBy"})


@dataclass
class V1WorkspaceSpec:
    spec_code: Optional[str] = field(default=None, metadata={"json": "SpecCode"})
    display_name: Optional[str] = field(default=None, metadata={"json": "DisplayName"})
    cpu: Optional[str] = field(default=None, metadata={"json": "Cpu"})
    memory: Optional[str] = field(default=None, metadata={"json": "Memory"})
    storage: Optional[str] = field(default=None, metadata={"json": "Storage"})
    is_default: Optional[bool] = field(default=None, metadata={"json": "IsDefault"})


@dataclass
class V1Model:
    id: Optional[str] = field(default=None, metadata={"json": "ID"})
    name: Optional[str] = field(default=None, metadata={"json": "Name"})
    type: Optional[str] = field(default=None, metadata={"json": "Type"})
    provider: Optional[str] = field(default=None, metadata={"json": "Provider"})
    spec: Optional[str] = field(default=None, metadata={"json": "Spec"})
    model_name: Optional[str] = field(default=None, metadata={"json": "ModelName"})
    description: Optional[str] = field(default=None, metadata={"json": "Description"})
    status: Optional[str] = field(default=None, metadata={"json": "Status"})
    features_config: Optional[Any] = field(
        default=None, metadata={"json": "FeaturesConfig"}
    )
    property: Optional[Any] = field(default=None, metadata={"json": "Property"})
    credential_schema: Optional[Any] = field(
        default=None, metadata={"json": "CredentialSchema"}
    )
    credential: Optional[Dict[str, str]] = field(
        default=None, metadata={"json": "Credential"}
    )
    create_time: Optional[str] = field(default=None, metadata={"json": "CreateTime"})
    update_time: Optional[str] = field(default=None, metadata={"json": "UpdateTime"})


@dataclass
class V1ModelList:
    items: List[V1Model] = field(default_factory=list, metadata={"json": "Items"})
    total: Optional[int] = field(default=None, metadata={"json": "Total"})


@dataclass
class V1ModelProvider:
    id: Optional[str] = field(default=None, metadata={"json": "ID"})
    type: Optional[str] = field(default=None, metadata={"json": "Type"})
    provider: Optional[str] = field(default=None, metadata={"json": "Provider"})
    model_name: Optional[str] = field(default=None, metadata={"json": "ModelName"})
    features_config: Optional[Any] = field(
        default=None, metadata={"json": "FeaturesConfig"}
    )
    property: Optional[Any] = field(default=None, metadata={"json": "Property"})
    credential_schema: Optional[Any] = field(
        default=None, metadata={"json": "CredentialSchema"}
    )


@dataclass
class V1ModelProviderList:
    items: List[V1ModelProvider] = field(
        default_factory=list, metadata={"json": "Models"}
    )
    total: Optional[int] = field(default=None, metadata={"json": "Total"})


@dataclass
class V1Prompt:
    id: Optional[str] = field(default=None, metadata={"json": "ID"})
    name: Optional[str] = field(default=None, metadata={"json": "Name"})
    content: Optional[str] = field(default=None, metadata={"json": "SystemPrompt"})
    created_at: Optional[str] = field(default=None, metadata={"json": "CreatedAt"})
    updated_at: Optional[str] = field(default=None, metadata={"json": "UpdatedAt"})


@dataclass
class V1Resource:
    id: Optional[str] = field(default=None, metadata={"json": "ID"})
    name: Optional[str] = field(default=None, metadata={"json": "Name"})
    type: Optional[str] = field(default=None, metadata={"json": "Type"})
    artifact_id: Optional[str] = field(default=None, metadata={"json": "ArtifactID"})
    size: Optional[int] = field(default=None, metadata={"json": "Size"})
    extension: Optional[str] = field(default=None, metadata={"json": "Extension"})
    workspace_id: Optional[str] = field(default=None, metadata={"json": "WorkspaceID"})
    directory_id: Optional[str] = field(default=None, metadata={"json": "DirectoryID"})
    created_at: Optional[str] = field(default=None, metadata={"json": "CreatedAt"})
    updated_at: Optional[str] = field(default=None, metadata={"json": "UpdatedAt"})
    created_by: Optional[str] = field(default=None, metadata={"json": "CreatedBy"})
    updated_by: Optional[str] = field(default=None, metadata={"json": "UpdatedBy"})


@dataclass
class V1ResourceList:
    items: List[V1Resource] = field(default_factory=list, metadata={"json": "Items"})
    page: Optional[V1Page] = field(default=None, metadata={"json": "Page"})


@dataclass
class V1Directory:
    id: Optional[str] = field(default=None, metadata={"json": "ID"})
    name: Optional[str] = field(default=None, metadata={"json": "Name"})
    workspace_id: Optional[str] = field(default=None, metadata={"json": "WorkspaceID"})
    created_at: Optional[str] = field(default=None, metadata={"json": "CreatedAt"})
    updated_at: Optional[str] = field(default=None, metadata={"json": "UpdatedAt"})
    created_by: Optional[str] = field(default=None, metadata={"json": "CreatedBy"})
    updated_by: Optional[str] = field(default=None, metadata={"json": "UpdatedBy"})
    resource_count: Optional[int] = field(
        default=None, metadata={"json": "ResourceCount"}
    )


@dataclass
class V1DirectoryList:
    items: List[V1Directory] = field(default_factory=list, metadata={"json": "Items"})
    page: Optional[V1Page] = field(default=None, metadata={"json": "Page"})


@dataclass
class V1MCP:
    id: Optional[str] = field(default=None, metadata={"json": "ID"})
    name: Optional[str] = field(default=None, metadata={"json": "Name"})
    description: Optional[str] = field(default=None, metadata={"json": "Description"})
    transport: Optional[str] = field(default=None, metadata={"json": "Transport"})
    endpoint: Optional[str] = field(default=None, metadata={"json": "URL"})
    headers: Optional[Dict[str, str]] = field(
        default=None, metadata={"json": "Headers"}
    )
    env: Optional[Dict[str, str]] = field(default=None, metadata={"json": "Env"})
    command: Optional[str] = field(default=None, metadata={"json": "Command"})
    args: Optional[List[str]] = field(default=None, metadata={"json": "Args"})
    auth_type: Optional[str] = field(default=None, metadata={"json": "AuthType"})
    credential_provider_id: Optional[str] = field(
        default=None, metadata={"json": "CredentialProviderID"}
    )
    tool_allowlist: Optional[List[str]] = field(
        default=None, metadata={"json": "ToolAllowlist"}
    )
    tool_denylist: Optional[List[str]] = field(
        default=None, metadata={"json": "ToolDenylist"}
    )
    tool_prefix: Optional[str] = field(default=None, metadata={"json": "ToolPrefix"})
    timeout: Optional[int] = field(default=None, metadata={"json": "Timeout"})
    status: Optional[str] = field(default=None, metadata={"json": "Status"})
    source: Optional[str] = field(default=None, metadata={"json": "Source"})
    created_at: Optional[str] = field(default=None, metadata={"json": "CreatedAt"})
    updated_at: Optional[str] = field(default=None, metadata={"json": "UpdatedAt"})
    agent_ids: Optional[List[str]] = field(default=None, metadata={"json": "AgentIDs"})
    credential: Optional[Any] = field(default=None, metadata={"json": "Credential"})


@dataclass
class V1MCPTool:
    name: Optional[str] = field(default=None, metadata={"json": "Name"})
    description: Optional[str] = field(default=None, metadata={"json": "Description"})


@dataclass
class V1MCPTestConnectionResult:
    success: bool = field(default=False, metadata={"json": "Success"})
    error: Optional[str] = field(default=None, metadata={"json": "Error"})
    tool_count: int = field(default=0, metadata={"json": "ToolCount"})
    tools: List[V1MCPTool] = field(default_factory=list, metadata={"json": "Tools"})


@dataclass
class V1Skill:
    id: Optional[str] = field(default=None, metadata={"json": "ID"})
    skill_id: Optional[str] = field(default=None, metadata={"json": "SkillID"})
    name: Optional[str] = field(default=None, metadata={"json": "Name"})
    description: Optional[str] = field(default=None, metadata={"json": "Description"})
    source: Optional[str] = field(default=None, metadata={"json": "Source"})
    version: Optional[str] = field(default=None, metadata={"json": "Version"})
    artifact_id: Optional[str] = field(default=None, metadata={"json": "ArtifactID"})
    enabled: Optional[bool] = field(default=None, metadata={"json": "Enabled"})
    slug_id: Optional[str] = field(default=None, metadata={"json": "SlugID"})
    created_at: Optional[str] = field(default=None, metadata={"json": "CreatedAt"})
    updated_at: Optional[str] = field(default=None, metadata={"json": "UpdatedAt"})
    credential_provider_id: Optional[str] = field(
        default=None, metadata={"json": "CredentialProviderID"}
    )
    credential: Optional[Any] = field(default=None, metadata={"json": "Credential"})


@dataclass
class V1SkillVersion:
    id: Optional[str] = field(default=None, metadata={"json": "ID"})
    skill_id: Optional[str] = field(default=None, metadata={"json": "SkillID"})
    name: Optional[str] = field(default=None, metadata={"json": "Name"})
    version: Optional[str] = field(default=None, metadata={"json": "Version"})
    description: Optional[str] = field(default=None, metadata={"json": "Description"})
    source: Optional[str] = field(default=None, metadata={"json": "Source"})
    artifact_id: Optional[str] = field(default=None, metadata={"json": "ArtifactID"})
    enabled: Optional[bool] = field(default=None, metadata={"json": "Enabled"})
    slug_id: Optional[str] = field(default=None, metadata={"json": "SlugID"})
    created_at: Optional[str] = field(default=None, metadata={"json": "CreatedAt"})
    constraint: Optional[str] = None  # client-side only


@dataclass
class V1SkillParseResult:
    name: Optional[str] = field(default=None, metadata={"json": "Name"})
    description: Optional[str] = field(default=None, metadata={"json": "Description"})
    blob_id: Optional[str] = field(default=None, metadata={"json": "BlobID"})


@dataclass
class V1ArkSkillHubSkill:
    slug: Optional[str] = field(default=None, metadata={"json": "Slug"})
    name: Optional[str] = field(default=None, metadata={"json": "Name"})
    description: Optional[str] = field(default=None, metadata={"json": "Description"})
    namespace: Optional[str] = field(default=None, metadata={"json": "Namespace"})
    tags: Optional[List[str]] = field(default=None, metadata={"json": "Tags"})
    banned: Optional[bool] = field(default=None, metadata={"json": "Banned"})
    source_type: Optional[str] = field(default=None, metadata={"json": "SourceType"})
    source_repo: Optional[str] = field(default=None, metadata={"json": "SourceRepo"})
    verify: Optional[bool] = field(default=None, metadata={"json": "Verify"})
    path: Optional[str] = field(default=None, metadata={"json": "Path"})
    created_at: Optional[str] = field(default=None, metadata={"json": "CreatedAt"})
    updated_at: Optional[str] = field(default=None, metadata={"json": "UpdatedAt"})
    skill_markdown: Optional[str] = field(
        default=None, metadata={"json": "SkillMarkdown"}
    )


@dataclass
class V1ArkSkillHubSkillList:
    items: List[V1ArkSkillHubSkill] = field(
        default_factory=list, metadata={"json": "Items"}
    )
    page: Optional[V1Page] = field(default=None, metadata={"json": "Page"})


@dataclass
class V1AgentSkillBinding:
    id: Optional[str] = field(default=None, metadata={"json": "ID"})
    enabled: Optional[bool] = field(default=None, metadata={"json": "Enabled"})


@dataclass
class V1AgentMCPBinding:
    id: Optional[str] = field(default=None, metadata={"json": "ID"})
    enabled: Optional[bool] = field(default=None, metadata={"json": "Enabled"})
    tool_allowlist: Optional[List[str]] = field(
        default=None, metadata={"json": "ToolAllowlist"}
    )
    tool_denylist: Optional[List[str]] = field(
        default=None, metadata={"json": "ToolDenylist"}
    )


@dataclass
class V1AgentRuntimeInstanceStatus:
    name: Optional[str] = field(default=None, metadata={"json": "Name"})
    status: Optional[str] = field(default=None, metadata={"json": "Status"})
    ready: Optional[bool] = field(default=None, metadata={"json": "Ready"})
    reason: Optional[str] = field(default=None, metadata={"json": "Reason"})
    message: Optional[str] = field(default=None, metadata={"json": "Message"})


@dataclass
class V1AgentRuntimeStatus:
    status: Optional[str] = field(default=None, metadata={"json": "Status"})
    ready: Optional[bool] = field(default=None, metadata={"json": "Ready"})
    reason: Optional[str] = field(default=None, metadata={"json": "Reason"})
    message: Optional[str] = field(default=None, metadata={"json": "Message"})
    replicas: Optional[int] = field(default=None, metadata={"json": "Replicas"})
    ready_replicas: Optional[int] = field(
        default=None, metadata={"json": "ReadyReplicas"}
    )
    desired_replicas: Optional[int] = field(
        default=None, metadata={"json": "DesiredReplicas"}
    )
    instances: Optional[List[V1AgentRuntimeInstanceStatus]] = field(
        default=None, metadata={"json": "Instances"}
    )
    updated_at: Optional[str] = field(default=None, metadata={"json": "UpdatedAt"})


@dataclass
class V1Agent:
    id: Optional[str] = field(default=None, metadata={"json": "ID"})
    workspace_id: Optional[str] = field(default=None, metadata={"json": "WorkspaceID"})
    name: Optional[str] = field(default=None, metadata={"json": "Name"})
    description: Optional[str] = field(default=None, metadata={"json": "Description"})
    model_id: Optional[str] = field(default=None, metadata={"json": "ModelID"})
    env_id: Optional[str] = field(default=None, metadata={"json": "EnvID"})
    system_prompt: Optional[str] = field(
        default=None, metadata={"json": "SystemPrompt"}
    )
    skills: Optional[List[V1AgentSkillBinding]] = field(
        default=None, metadata={"json": "Skills"}
    )
    mcps: Optional[List[V1AgentMCPBinding]] = field(
        default=None, metadata={"json": "MCPs"}
    )
    resource_ids: Optional[List[str]] = field(
        default=None, metadata={"json": "ResourceIDs"}
    )
    created_at: Optional[str] = field(default=None, metadata={"json": "CreatedAt"})
    updated_at: Optional[str] = field(default=None, metadata={"json": "UpdatedAt"})
    created_by: Optional[str] = field(default=None, metadata={"json": "CreatedBy"})
    updated_by: Optional[str] = field(default=None, metadata={"json": "UpdatedBy"})
    channels: Optional[List[Any]] = field(default=None, metadata={"json": "Channels"})
    config: Optional[Any] = field(default=None, metadata={"json": "Config"})
    runtime_status: Optional[V1AgentRuntimeStatus] = field(
        default=None, metadata={"json": "RuntimeStatus"}
    )
    session_count: Optional[int] = field(
        default=None, metadata={"json": "SessionCount"}
    )
    metadata: Optional[Dict[str, str]] = field(
        default=None, metadata={"json": "Metadata"}
    )
    memory_stores: Optional[List[Any]] = field(
        default=None, metadata={"json": "MemoryStores"}
    )
    effective_channel_count: Optional[int] = field(
        default=None, metadata={"json": "EffectiveChannelCount"}
    )
    icon: Optional[str] = field(default=None, metadata={"json": "Icon"})
    api_protocol_type: Optional[str] = field(
        default=None, metadata={"json": "ApiProtocolType"}
    )
    model_interactive_mode: Optional[str] = field(
        default=None, metadata={"json": "ModelInteractiveMode"}
    )
    allow_responses_api: Optional[bool] = field(
        default=None, metadata={"json": "AllowResponsesAPI"}
    )
    egress_credentials: Optional[List[Any]] = field(
        default=None, metadata={"json": "EgressCredentials"}
    )


@dataclass
class V1Session:
    id: Optional[str] = field(default=None, metadata={"json": "ID"})
    agent_id: Optional[str] = field(default=None, metadata={"json": "AgentID"})
    session_key: Optional[str] = field(default=None, metadata={"json": "SessionKey"})
    status: Optional[str] = field(default=None, metadata={"json": "Status"})
    channel: Optional[str] = field(default=None, metadata={"json": "Channel"})
    peer_kind: Optional[str] = field(default=None, metadata={"json": "PeerKind"})
    peer_id: Optional[str] = field(default=None, metadata={"json": "PeerID"})
    risk_level: Optional[str] = field(default=None, metadata={"json": "RiskLevel"})
    config: Optional[Any] = field(default=None, metadata={"json": "Config"})
    auth_context: Optional[Any] = field(default=None, metadata={"json": "AuthContext"})
    message_count: Optional[int] = field(
        default=None, metadata={"json": "MessageCount"}
    )
    last_message_at: Optional[str] = field(
        default=None, metadata={"json": "LastMessageAt"}
    )
    last_message_content: Optional[str] = field(
        default=None, metadata={"json": "LastMessageContent"}
    )
    summary: Optional[str] = field(default=None, metadata={"json": "Summary"})
    metadata: Optional[Any] = field(default=None, metadata={"json": "Metadata"})
    created_at: Optional[str] = field(default=None, metadata={"json": "CreatedAt"})
    updated_at: Optional[str] = field(default=None, metadata={"json": "UpdatedAt"})
    archived_at: Optional[str] = field(default=None, metadata={"json": "ArchivedAt"})
    deleted_at: Optional[str] = field(default=None, metadata={"json": "DeletedAt"})


@dataclass
class V1MessageFile:
    file_id: Optional[str] = field(default=None, metadata={"json": "FileID"})
    name: Optional[str] = field(default=None, metadata={"json": "Name"})
    content_type: Optional[str] = field(default=None, metadata={"json": "ContentType"})
    url: Optional[str] = field(default=None, metadata={"json": "URL"})
    uri: Optional[str] = field(default=None, metadata={"json": "URI"})
    storage_path: Optional[str] = field(default=None, metadata={"json": "StoragePath"})
    size_bytes: Optional[int] = field(default=None, metadata={"json": "SizeBytes"})
    # Chat request compatibility; persisted MessageFile responses use URI/storage fields.
    blob_id: Optional[str] = field(default=None, metadata={"json": "BlobID"})


@dataclass
class V1Message:
    id: Optional[str] = field(default=None, metadata={"json": "ID"})
    session_id: Optional[str] = field(default=None, metadata={"json": "SessionID"})
    run_id: Optional[str] = field(default=None, metadata={"json": "RunID"})
    role: Optional[str] = field(default=None, metadata={"json": "Role"})
    content: Optional[str] = field(default=None, metadata={"json": "Content"})
    tool_calls: Optional[Any] = field(default=None, metadata={"json": "ToolCalls"})
    tool_result: Optional[Any] = field(default=None, metadata={"json": "ToolResult"})
    metadata: Optional[Any] = field(default=None, metadata={"json": "Metadata"})
    visibility: Optional[str] = field(default=None, metadata={"json": "Visibility"})
    created_at: Optional[str] = field(default=None, metadata={"json": "CreatedAt"})
    files: Optional[List[V1MessageFile]] = field(
        default=None, metadata={"json": "Files"}
    )
    event_type: Optional[str] = field(default=None, metadata={"json": "EventType"})
    payload: Optional[Any] = field(default=None, metadata={"json": "Payload"})
    sequence: Optional[int] = field(default=None, metadata={"json": "Sequence"})
    payload_json: Optional[str] = field(default=None, metadata={"json": "PayloadJSON"})
    token_count: Optional[int] = field(default=None, metadata={"json": "TokenCount"})
    trace_id: Optional[str] = field(default=None, metadata={"json": "TraceID"})


@dataclass
class V1MessageList:
    items: List[V1Message] = field(default_factory=list, metadata={"json": "Items"})
    page: Optional[V1Page] = field(default=None, metadata={"json": "Page"})
    resume_hint: Optional["V1WebChatResumeHint"] = field(
        default=None, metadata={"json": "ResumeHint"}
    )


@dataclass
class V1WebChatResumeHint:
    run_id: Optional[str] = field(default=None, metadata={"json": "RunID"})
    request_id: Optional[str] = field(default=None, metadata={"json": "RequestID"})
    status: Optional[str] = field(default=None, metadata={"json": "Status"})


@dataclass
class V1ChatCommandResult:
    accepted: Optional[bool] = field(default=None, metadata={"json": "Accepted"})


@dataclass
class V1SessionList:
    items: List[V1Session] = field(default_factory=list, metadata={"json": "Items"})
    page: Optional[V1Page] = field(default=None, metadata={"json": "Page"})


@dataclass
class V1FeishuChannelConfig:
    app_id: Optional[str] = field(default=None, metadata={"json": "AppID"})
    app_secret: Optional[str] = field(default=None, metadata={"json": "AppSecret"})
    encrypt_key: Optional[str] = field(default=None, metadata={"json": "EncryptKey"})
    verification_token: Optional[str] = field(
        default=None, metadata={"json": "VerificationToken"}
    )
    domain: Optional[str] = field(default=None, metadata={"json": "Domain"})
    connection_mode: Optional[str] = field(
        default=None, metadata={"json": "ConnectionMode"}
    )
    webhook_path: Optional[str] = field(default=None, metadata={"json": "WebhookPath"})
    require_mention: Optional[bool] = field(
        default=None, metadata={"json": "RequireMention"}
    )
    render_mode: Optional[str] = field(default=None, metadata={"json": "RenderMode"})
    streaming: Optional[bool] = field(default=None, metadata={"json": "Streaming"})
    reaction_level: Optional[str] = field(
        default=None, metadata={"json": "ReactionLevel"}
    )
    text_chunk_limit: Optional[int] = field(
        default=None, metadata={"json": "TextChunkLimit"}
    )
    media_max_mb: Optional[int] = field(default=None, metadata={"json": "MediaMaxMB"})
    block_reply: Optional[bool] = field(default=None, metadata={"json": "BlockReply"})


@dataclass
class V1WeComChannelConfig:
    bot_id: Optional[str] = field(default=None, metadata={"json": "BotID"})
    secret: Optional[str] = field(default=None, metadata={"json": "Secret"})


@dataclass
class V1Channel:
    id: Optional[str] = field(default=None, metadata={"json": "ID"})
    agent_id: Optional[str] = field(default=None, metadata={"json": "AgentID"})
    name: Optional[str] = field(default=None, metadata={"json": "Name"})
    channel_type: Optional[str] = field(default=None, metadata={"json": "ChannelType"})
    config: Optional[Any] = field(default=None, metadata={"json": "Config"})
    status: Optional[str] = field(default=None, metadata={"json": "Status"})
    assigned_gateway_id: Optional[str] = field(
        default=None, metadata={"json": "AssignedGatewayID"}
    )
    created_at: Optional[str] = field(default=None, metadata={"json": "CreatedAt"})
    updated_at: Optional[str] = field(default=None, metadata={"json": "UpdatedAt"})
    created_by: Optional[str] = field(default=None, metadata={"json": "CreatedBy"})
    updated_by: Optional[str] = field(default=None, metadata={"json": "UpdatedBy"})
    feishu_config: Optional[V1FeishuChannelConfig] = field(
        default=None, metadata={"json": "FeishuConfig"}
    )
    wecom_config: Optional[V1WeComChannelConfig] = field(
        default=None, metadata={"json": "WeComConfig"}
    )


@dataclass
class V1RuntimeAPIKey:
    id: Optional[str] = field(default=None, metadata={"json": "ID"})
    agent_id: Optional[str] = field(default=None, metadata={"json": "AgentID"})
    key_mask: Optional[str] = field(default=None, metadata={"json": "KeyMask"})
    description: Optional[str] = field(default=None, metadata={"json": "Description"})
    expires_at: Optional[str] = field(default=None, metadata={"json": "ExpiresAt"})
    created_at: Optional[str] = field(default=None, metadata={"json": "CreatedAt"})
    updated_at: Optional[str] = field(default=None, metadata={"json": "UpdatedAt"})


@dataclass
class V1RuntimeAPIKeyCreateResult:
    item: Optional[V1RuntimeAPIKey] = field(default=None, metadata={"json": "Item"})
    raw_key: Optional[str] = field(default=None, metadata={"json": "RawKey"})


@dataclass
class V1Run:
    id: Optional[str] = field(default=None, metadata={"json": "ID"})
    tenant_id: Optional[str] = field(default=None, metadata={"json": "TenantID"})
    agent_id: Optional[str] = field(default=None, metadata={"json": "AgentID"})
    session_id: Optional[str] = field(default=None, metadata={"json": "SessionID"})
    status: Optional[str] = field(default=None, metadata={"json": "Status"})
    source: Optional[str] = field(default=None, metadata={"json": "Source"})
    input: Optional[str] = field(default=None, metadata={"json": "Input"})
    output: Optional[str] = field(default=None, metadata={"json": "Output"})
    iterations: Optional[int] = field(default=None, metadata={"json": "Iterations"})
    tool_calls: Optional[int] = field(default=None, metadata={"json": "ToolCalls"})
    tokens_input: Optional[int] = field(default=None, metadata={"json": "TokensInput"})
    tokens_output: Optional[int] = field(
        default=None, metadata={"json": "TokensOutput"}
    )
    metadata: Optional[Any] = field(default=None, metadata={"json": "Metadata"})
    started_at: Optional[str] = field(default=None, metadata={"json": "StartedAt"})
    completed_at: Optional[str] = field(default=None, metadata={"json": "CompletedAt"})
    created_at: Optional[str] = field(default=None, metadata={"json": "CreatedAt"})


@dataclass
class V1CronJob:
    id: Optional[str] = field(default=None, metadata={"json": "ID"})
    workspace_id: Optional[str] = field(default=None, metadata={"json": "WorkspaceID"})
    agent_id: Optional[str] = field(default=None, metadata={"json": "AgentID"})
    name: Optional[str] = field(default=None, metadata={"json": "Name"})
    description: Optional[str] = field(default=None, metadata={"json": "Description"})
    prompt: Optional[str] = field(default=None, metadata={"json": "Prompt"})
    schedule_type: Optional[str] = field(
        default=None, metadata={"json": "ScheduleType"}
    )
    schedule_value: Optional[str] = field(
        default=None, metadata={"json": "ScheduleValue"}
    )
    schedule_timezone: Optional[str] = field(
        default=None, metadata={"json": "ScheduleTimezone"}
    )
    delivery_channel: Optional[str] = field(
        default=None, metadata={"json": "DeliveryChannel"}
    )
    delivery_to: Optional[str] = field(default=None, metadata={"json": "DeliveryTo"})
    enabled: Optional[bool] = field(default=None, metadata={"json": "Enabled"})
    source: Optional[str] = field(default=None, metadata={"json": "Source"})
    next_run_at: Optional[str] = field(default=None, metadata={"json": "NextRunAt"})
    last_status: Optional[str] = field(default=None, metadata={"json": "LastStatus"})
    last_run_at: Optional[str] = field(default=None, metadata={"json": "LastRunAt"})
    last_run_id: Optional[str] = field(default=None, metadata={"json": "LastRunID"})
    config: Optional[Any] = field(default=None, metadata={"json": "Config"})
    created_at: Optional[str] = field(default=None, metadata={"json": "CreatedAt"})
    updated_at: Optional[str] = field(default=None, metadata={"json": "UpdatedAt"})
    created_by: Optional[str] = field(default=None, metadata={"json": "CreatedBy"})
    updated_by: Optional[str] = field(default=None, metadata={"json": "UpdatedBy"})
    created_via: Optional[str] = field(default=None, metadata={"json": "CreatedVia"})
    created_session_id: Optional[str] = field(
        default=None, metadata={"json": "CreatedSessionID"}
    )


@dataclass
class V1CronJobList:
    items: List[V1CronJob] = field(default_factory=list, metadata={"json": "Items"})
    page: Optional[V1Page] = field(default=None, metadata={"json": "Page"})


@dataclass
class V1CronJobRun:
    started_at: Optional[str] = field(default=None, metadata={"json": "StartedAt"})
    finished_at: Optional[str] = field(default=None, metadata={"json": "FinishedAt"})
    status: Optional[str] = field(default=None, metadata={"json": "Status"})
    trigger_type: Optional[str] = field(default=None, metadata={"json": "TriggerType"})
    delivery_channel: Optional[str] = field(
        default=None, metadata={"json": "DeliveryChannel"}
    )
    result: Optional[str] = field(default=None, metadata={"json": "Result"})


@dataclass
class V1CronJobRunSync:
    id: Optional[str] = field(default=None, metadata={"json": "ID"})
    tenant_id: Optional[str] = field(default=None, metadata={"json": "TenantID"})
    workspace_id: Optional[str] = field(default=None, metadata={"json": "WorkspaceID"})
    agent_id: Optional[str] = field(default=None, metadata={"json": "AgentID"})
    cron_job_id: Optional[str] = field(default=None, metadata={"json": "CronJobID"})
    session_id: Optional[str] = field(default=None, metadata={"json": "SessionID"})
    prompt: Optional[str] = field(default=None, metadata={"json": "Prompt"})
    status: Optional[str] = field(default=None, metadata={"json": "Status"})
    scheduled_at: Optional[str] = field(default=None, metadata={"json": "ScheduledAt"})
    trigger_type: Optional[str] = field(default=None, metadata={"json": "TriggerType"})
    started_at: Optional[str] = field(default=None, metadata={"json": "StartedAt"})
    finished_at: Optional[str] = field(default=None, metadata={"json": "FinishedAt"})
    result: Optional[str] = field(default=None, metadata={"json": "Result"})


@dataclass
class V1CronJobRunList:
    items: List[V1CronJobRun] = field(default_factory=list, metadata={"json": "Items"})
    page: Optional[V1Page] = field(default=None, metadata={"json": "Page"})


@dataclass
class V1CronJobRunSyncList:
    items: List[V1CronJobRunSync] = field(
        default_factory=list, metadata={"json": "Items"}
    )
    next_cursor_updated_at: Optional[str] = field(
        default=None, metadata={"json": "NextCursorUpdatedAt"}
    )
    next_cursor_id: Optional[str] = field(
        default=None, metadata={"json": "NextCursorID"}
    )


@dataclass
class V1CronJobCreateResult:
    cron_job_id: Optional[str] = field(default=None, metadata={"json": "CronJobID"})
    next_run_at: Optional[str] = field(default=None, metadata={"json": "NextRunAt"})
    created_at: Optional[str] = field(default=None, metadata={"json": "CreatedAt"})


@dataclass
class V1CronJobRunNowResult:
    cron_job_id: Optional[str] = field(default=None, metadata={"json": "CronJobID"})
    status: Optional[str] = field(default=None, metadata={"json": "Status"})
    trigger_type: Optional[str] = field(default=None, metadata={"json": "TriggerType"})


@dataclass
class V1TraceSummary:
    trace_id: Optional[str] = field(default=None, metadata={"json": "TraceID"})
    name: Optional[str] = field(default=None, metadata={"json": "Name"})
    start_time: Optional[str] = field(default=None, metadata={"json": "StartTime"})
    end_time: Optional[str] = field(default=None, metadata={"json": "EndTime"})
    duration_ms: Optional[int] = field(default=None, metadata={"json": "DurationMs"})
    agent_id: Optional[str] = field(default=None, metadata={"json": "AgentID"})
    agent_name: Optional[str] = field(default=None, metadata={"json": "AgentName"})
    status_code: Optional[str] = field(default=None, metadata={"json": "StatusCode"})
    service_name: Optional[str] = field(default=None, metadata={"json": "ServiceName"})
    attributes: Optional[Any] = field(default=None, metadata={"json": "Attributes"})


@dataclass
class V1SpanSummary:
    trace_id: Optional[str] = field(default=None, metadata={"json": "TraceID"})
    span_id: Optional[str] = field(default=None, metadata={"json": "SpanID"})
    parent_span_id: Optional[str] = field(
        default=None, metadata={"json": "ParentSpanID"}
    )
    name: Optional[str] = field(default=None, metadata={"json": "Name"})
    kind: Optional[str] = field(default=None, metadata={"json": "Kind"})
    start_time: Optional[str] = field(default=None, metadata={"json": "StartTime"})
    end_time: Optional[str] = field(default=None, metadata={"json": "EndTime"})
    duration_ms: Optional[int] = field(default=None, metadata={"json": "DurationMs"})
    status_code: Optional[str] = field(default=None, metadata={"json": "StatusCode"})
    status_message: Optional[str] = field(
        default=None, metadata={"json": "StatusMessage"}
    )
    service_name: Optional[str] = field(default=None, metadata={"json": "ServiceName"})


@dataclass
class V1SpanDetail:
    trace_id: Optional[str] = field(default=None, metadata={"json": "TraceID"})
    span_id: Optional[str] = field(default=None, metadata={"json": "SpanID"})
    parent_span_id: Optional[str] = field(
        default=None, metadata={"json": "ParentSpanID"}
    )
    name: Optional[str] = field(default=None, metadata={"json": "Name"})
    kind: Optional[str] = field(default=None, metadata={"json": "Kind"})
    start_time: Optional[str] = field(default=None, metadata={"json": "StartTime"})
    end_time: Optional[str] = field(default=None, metadata={"json": "EndTime"})
    duration_ms: Optional[int] = field(default=None, metadata={"json": "DurationMs"})
    status_code: Optional[str] = field(default=None, metadata={"json": "StatusCode"})
    status_message: Optional[str] = field(
        default=None, metadata={"json": "StatusMessage"}
    )
    resource: Optional[Any] = field(default=None, metadata={"json": "Resource"})
    attributes: Optional[Any] = field(default=None, metadata={"json": "Attributes"})
    events: Optional[List[Any]] = field(default=None, metadata={"json": "Events"})


@dataclass
class V1TraceList:
    items: List[V1TraceSummary] = field(
        default_factory=list, metadata={"json": "Items"}
    )
    next_scroll_id: Optional[str] = field(
        default=None, metadata={"json": "NextScrollID"}
    )
    total: Optional[int] = field(default=None, metadata={"json": "Total"})


@dataclass
class V1SpanList:
    items: List[V1SpanSummary] = field(default_factory=list, metadata={"json": "Items"})
    next_scroll_id: Optional[str] = field(
        default=None, metadata={"json": "NextScrollID"}
    )
    total: Optional[int] = field(default=None, metadata={"json": "Total"})


@dataclass
class V1Overview:
    summary: Optional[Any] = field(default=None, metadata={"json": "Summary"})
    run_health: Optional[Any] = field(default=None, metadata={"json": "RunHealth"})
    usage: Optional[Any] = field(default=None, metadata={"json": "Usage"})
    risk: Optional[Any] = field(default=None, metadata={"json": "Risk"})


@dataclass
class V1MetricDataPoint:
    time: Optional[str] = field(default=None, metadata={"json": "Time"})
    value: Optional[float] = field(default=None, metadata={"json": "Value"})
    start_timestamp: Optional[int] = field(
        default=None, metadata={"json": "StartTimestamp"}
    )
    end_timestamp: Optional[int] = field(
        default=None, metadata={"json": "EndTimestamp"}
    )


@dataclass
class V1MetricGroupedDataPoint:
    group: Optional[str] = field(default=None, metadata={"json": "Group"})
    points: List[V1MetricDataPoint] = field(
        default_factory=list, metadata={"json": "Points"}
    )


@dataclass
class V1MetricOverview:
    request_count: Optional[int] = field(
        default=None, metadata={"json": "RequestCount"}
    )
    success_rate: Optional[float] = field(
        default=None, metadata={"json": "SuccessRate"}
    )
    avg_latency_ms: Optional[float] = field(
        default=None, metadata={"json": "AvgLatencyMs"}
    )
    latency_p50_ms: Optional[float] = field(
        default=None, metadata={"json": "LatencyP50Ms"}
    )
    latency_p95_ms: Optional[float] = field(
        default=None, metadata={"json": "LatencyP95Ms"}
    )
    token_total: Optional[int] = field(default=None, metadata={"json": "TokenTotal"})
    cost_total: Optional[float] = field(default=None, metadata={"json": "CostTotal"})


@dataclass
class V1MetricOverviewResult:
    data: Optional[V1MetricOverview] = field(default=None, metadata={"json": "Data"})
    effective_step_seconds: Optional[int] = field(
        default=None, metadata={"json": "EffectiveStepSeconds"}
    )


@dataclass
class V1MetricTrendResult:
    series: Optional[List[V1MetricDataPoint]] = field(
        default=None, metadata={"json": "Series"}
    )
    grouped: Optional[List[V1MetricGroupedDataPoint]] = field(
        default=None, metadata={"json": "Grouped"}
    )
    effective_step_seconds: Optional[int] = field(
        default=None, metadata={"json": "EffectiveStepSeconds"}
    )


@dataclass
class V1MetricTopKItem:
    group: Optional[str] = field(default=None, metadata={"json": "Group"})
    value: Optional[float] = field(default=None, metadata={"json": "Value"})


@dataclass
class V1MetricTopKResult:
    items: List[V1MetricTopKItem] = field(
        default_factory=list, metadata={"json": "Items"}
    )
    effective_limit: Optional[int] = field(
        default=None, metadata={"json": "EffectiveLimit"}
    )


@dataclass
class V1MetricBreakdownResult:
    groups: List[V1MetricGroupedDataPoint] = field(
        default_factory=list, metadata={"json": "Groups"}
    )
    effective_step_seconds: Optional[int] = field(
        default=None, metadata={"json": "EffectiveStepSeconds"}
    )


@dataclass
class V1MemoryStore:
    id: Optional[str] = field(default=None, metadata={"json": "ID"})
    workspace_id: Optional[str] = field(default=None, metadata={"json": "WorkspaceID"})
    name: Optional[str] = field(default=None, metadata={"json": "Name"})
    alias: Optional[str] = field(default=None, metadata={"json": "Alias"})
    description: Optional[str] = field(default=None, metadata={"json": "Description"})
    owner_type: Optional[str] = field(default=None, metadata={"json": "OwnerType"})
    owner_id: Optional[str] = field(default=None, metadata={"json": "OwnerID"})
    visibility: Optional[str] = field(default=None, metadata={"json": "Visibility"})
    access: Optional[str] = field(default=None, metadata={"json": "Access"})
    retrieval_mode: Optional[str] = field(
        default=None, metadata={"json": "RetrievalMode"}
    )
    extraction_policy: Optional[Any] = field(
        default=None, metadata={"json": "ExtractionPolicy"}
    )
    quota_policy: Optional[Any] = field(default=None, metadata={"json": "QuotaPolicy"})
    file_count: Optional[int] = field(default=None, metadata={"json": "FileCount"})
    bytes_used: Optional[int] = field(default=None, metadata={"json": "BytesUsed"})
    created_by: Optional[str] = field(default=None, metadata={"json": "CreatedBy"})
    updated_by: Optional[str] = field(default=None, metadata={"json": "UpdatedBy"})
    created_at: Optional[str] = field(default=None, metadata={"json": "CreatedAt"})
    updated_at: Optional[str] = field(default=None, metadata={"json": "UpdatedAt"})


@dataclass
class V1MemoryStoreList:
    items: List[V1MemoryStore] = field(default_factory=list, metadata={"json": "Items"})
    page: Optional[V1Page] = field(default=None, metadata={"json": "Page"})


@dataclass
class V1MemoryFile:
    id: Optional[str] = field(default=None, metadata={"json": "ID"})
    store_id: Optional[str] = field(default=None, metadata={"json": "StoreID"})
    path: Optional[str] = field(default=None, metadata={"json": "Path"})
    artifact_id: Optional[str] = field(default=None, metadata={"json": "ArtifactID"})
    content_sha256: Optional[str] = field(
        default=None, metadata={"json": "ContentSha256"}
    )
    size_bytes: Optional[int] = field(default=None, metadata={"json": "SizeBytes"})
    mime_type: Optional[str] = field(default=None, metadata={"json": "MimeType"})
    revision: Optional[int] = field(default=None, metadata={"json": "Revision"})
    content: Optional[str] = field(default=None, metadata={"json": "Content"})
    created_by: Optional[str] = field(default=None, metadata={"json": "CreatedBy"})
    updated_by: Optional[str] = field(default=None, metadata={"json": "UpdatedBy"})
    created_at: Optional[str] = field(default=None, metadata={"json": "CreatedAt"})
    updated_at: Optional[str] = field(default=None, metadata={"json": "UpdatedAt"})


@dataclass
class V1MemoryFileList:
    items: List[V1MemoryFile] = field(default_factory=list, metadata={"json": "Items"})
    page: Optional[V1Page] = field(default=None, metadata={"json": "Page"})


@dataclass
class V1MemoryFileUpsertResult:
    file_id: Optional[str] = field(default=None, metadata={"json": "FileID"})
    path: Optional[str] = field(default=None, metadata={"json": "Path"})
    content_sha256: Optional[str] = field(
        default=None, metadata={"json": "ContentSha256"}
    )
    revision: Optional[int] = field(default=None, metadata={"json": "Revision"})
    size_bytes: Optional[int] = field(default=None, metadata={"json": "SizeBytes"})


# ---------------- Param types (snake_case input) ----------------


@dataclass
class V1UploadBlobParams:
    filename: str
    content_type: str = "application/octet-stream"


@dataclass
class V1EnvironmentNewParams:
    name: str = ""
    description: str = ""
    image_type: str = ""
    env_vars: Optional[Any] = None
    cpu_limit: str = ""
    memory_limit: str = ""
    pvc_size: str = ""
    data_path: str = ""
    spec_code: str = ""
    workspace_id: str = ""


@dataclass
class V1EnvironmentUpdateParams:
    env_id: str
    workspace_id: str = ""
    name: Optional[str] = None
    description: Optional[str] = None
    image_type: Optional[str] = None
    env_vars: Optional[Any] = None
    cpu_limit: Optional[str] = None
    memory_limit: Optional[str] = None
    pvc_size: Optional[str] = None
    data_path: Optional[str] = None
    spec_code: Optional[str] = None


@dataclass
class V1PageInput:
    page_num: Optional[int] = None
    page_size: Optional[int] = None


@dataclass
class V1ModelGetParams:
    id: str = ""
    ids: Optional[List[str]] = None
    name: str = ""
    model_name: str = ""
    provider: str = ""
    type: str = ""
    spec: str = ""
    workspace_id: str = ""


@dataclass
class V1ModelListParams:
    name: str = ""
    workspace_id: str = ""
    page: Optional[V1PageInput] = None
    sort_by: str = ""
    sort_order: str = ""


@dataclass
class V1ModelNewParams:
    name: str
    type: str
    provider: str = ""
    spec: str = ""
    model_name: str = ""
    description: str = ""
    features_config: Optional[Any] = None
    property: Optional[Any] = None
    credential_schema: Optional[Any] = None
    credential: Optional[Dict[str, str]] = None
    workspace_id: str = ""


@dataclass
class V1ModelUpdateParams:
    id: str
    type: str
    description: str = ""
    provider: str = ""
    spec: str = ""
    model_name: str = ""
    features_config: Optional[Any] = None
    property: Optional[Any] = None
    credential_schema: Optional[Any] = None
    credential: Optional[Dict[str, str]] = None
    workspace_id: str = ""


@dataclass
class V1ModelDeleteParams:
    id: str
    workspace_id: str = ""


@dataclass
class V1ModelProviderListParams:
    provider: str = ""
    type: str = ""
    model_name: str = ""
    features: Optional[List[str]] = None
    workspace_id: str = ""
    page: Optional[V1PageInput] = None
    sort_by: str = ""
    sort_order: str = ""


@dataclass
class V1ModelProviderGetParams:
    ids: List[str]
    workspace_id: str = ""


@dataclass
class V1ModelProviderCredentialSchemaParams:
    provider: str
    type: str
    spec: str = ""
    features: Optional[List[str]] = None
    workspace_id: str = ""


@dataclass
class V1PromptNewParams:
    name: str = ""
    content: str = ""
    workspace_id: str = ""


@dataclass
class V1PromptListParams:
    workspace_id: str = ""


@dataclass
class V1PromptUpdateParams:
    id: str
    name: Optional[str] = None
    content: Optional[str] = None
    workspace_id: str = ""


@dataclass
class V1PromptDeleteParams:
    id: str
    workspace_id: str = ""


@dataclass
class V1ResourceNewParams:
    name: str
    blob_id: str
    type: str = ""
    directory_id: str = ""
    workspace_id: str = ""


@dataclass
class V1ResourceListParams:
    name: str = ""
    directory_id: str = ""
    workspace_id: str = ""
    page: Optional[V1PageInput] = None


@dataclass
class V1ResourceUpdateParams:
    resource_id: str
    name: str = ""
    directory_id: Optional[str] = None
    workspace_id: str = ""


@dataclass
class V1ResourceDeleteParams:
    resource_id: str
    directory_id: str = ""
    workspace_id: str = ""


@dataclass
class V1ResourceGetByNameParams:
    name: str
    directory_id: str = ""
    workspace_id: str = ""


@dataclass
class V1ResourceBatchGetParams:
    ids: List[str]
    workspace_id: str = ""


@dataclass
class V1ResourceBatchCreateItemParams:
    name: str
    blob_id: str
    directory_id: str = ""


@dataclass
class V1ResourceBatchCreateParams:
    items: List[V1ResourceBatchCreateItemParams]
    workspace_id: str = ""


@dataclass
class V1ResourceMoveParams:
    resource_id: str
    old_directory_id: str = ""
    new_directory_id: str = ""
    workspace_id: str = ""


@dataclass
class V1DirectoryNewParams:
    name: str
    workspace_id: str = ""


@dataclass
class V1DirectoryListParams:
    name: str = ""
    workspace_id: str = ""
    page: Optional[V1PageInput] = None


@dataclass
class V1DirectoryUpdateParams:
    directory_id: str
    name: str = ""
    workspace_id: str = ""


@dataclass
class V1DirectoryDeleteParams:
    directory_id: str
    workspace_id: str = ""


@dataclass
class V1DirectoryGetByNameParams:
    name: str
    workspace_id: str = ""


@dataclass
class V1CredentialSecretInputParams:
    secret_id: str = ""
    key_name: str = ""
    description: str = ""
    secret_type: str = ""
    secret_value: str = ""


@dataclass
class V1MCPCredentialInputParams:
    name: str = ""
    description: str = ""
    source: str = ""
    provider_type: str = ""
    config: Optional[Any] = None
    secrets: Optional[List[V1CredentialSecretInputParams]] = None


@dataclass
class V1SkillCredentialInputParams:
    name: str = ""
    description: str = ""
    source: str = ""
    provider_type: str = ""
    config: Optional[Any] = None
    secrets: Optional[List[V1CredentialSecretInputParams]] = None


@dataclass
class V1MCPNewParams:
    name: str
    transport: str = ""
    endpoint: str = ""
    description: str = ""
    headers: Optional[Dict[str, str]] = None
    env: Optional[Dict[str, str]] = None
    command: str = ""
    args: Optional[List[str]] = None
    auth_type: str = ""
    credential_config: Optional[V1MCPCredentialInputParams] = None
    tool_allowlist: Optional[List[str]] = None
    tool_denylist: Optional[List[str]] = None
    tool_prefix: str = ""
    timeout: int = 0
    source: str = ""
    workspace_id: str = ""


@dataclass
class V1MCPListParams:
    keyword: str = ""
    status: str = ""
    source: str = ""
    workspace_id: str = ""
    page: Optional[V1PageInput] = None


@dataclass
class V1MCPGetParams:
    id: str
    workspace_id: str = ""


@dataclass
class V1MCPBatchGetParams:
    ids: List[str]
    workspace_id: str = ""


@dataclass
class V1MCPUpdateParams:
    id: str
    name: Optional[str] = None
    description: Optional[str] = None
    transport: Optional[str] = None
    endpoint: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    env: Optional[Dict[str, str]] = None
    command: Optional[str] = None
    args: Optional[List[str]] = None
    auth_type: Optional[str] = None
    credential_config: Optional[V1MCPCredentialInputParams] = None
    tool_allowlist: Optional[List[str]] = None
    tool_denylist: Optional[List[str]] = None
    tool_prefix: Optional[str] = None
    timeout: Optional[int] = None
    status: Optional[str] = None
    source: Optional[str] = None
    workspace_id: str = ""


@dataclass
class V1MCPDeleteParams:
    id: str
    workspace_id: str = ""


@dataclass
class V1MCPTestConnectionParams:
    transport: str = ""
    endpoint: str = ""
    headers: Optional[Dict[str, str]] = None
    env: Optional[Dict[str, str]] = None
    command: str = ""
    args: Optional[List[str]] = None
    auth_type: str = ""
    credential_config: Optional[V1MCPCredentialInputParams] = None
    timeout: int = 0
    workspace_id: str = ""


@dataclass
class V1MCPResolveParams:
    id: str = ""
    name: str = ""
    workspace_id: str = ""


@dataclass
class V1SkillNewParams:
    name: str
    blob_id: str = ""
    skill_id: str = ""
    description: str = ""
    source: str = "manual"
    enabled: Optional[bool] = None
    version: str = ""
    slug_id: str = ""
    credential_config: Optional[V1SkillCredentialInputParams] = None
    workspace_id: str = ""


@dataclass
class V1SkillParseParams:
    blob_id: str
    workspace_id: str = ""


@dataclass
class V1ArkSkillHubListParams:
    keyword: str = ""
    workspace_id: str = ""
    page: Optional[V1PageInput] = None


@dataclass
class V1ArkSkillHubGetParams:
    slug: str
    workspace_id: str = ""


@dataclass
class V1ArkSkillHubImportParams:
    slug: str
    workspace_id: str = ""


@dataclass
class V1SkillListParams:
    keyword: str = ""
    source: str = ""
    name: str = ""
    slug_id: str = ""
    workspace_id: str = ""
    page: Optional[V1PageInput] = None


@dataclass
class V1SkillGetParams:
    id: str = ""
    skill_id: str = ""
    version: str = ""
    workspace_id: str = ""


@dataclass
class V1SkillBatchGetParams:
    ids: List[str]
    workspace_id: str = ""


@dataclass
class V1SkillUpdateParams:
    id: str = ""
    skill_id: str = ""
    version: str = ""
    description: Optional[str] = None
    source: Optional[str] = None
    artifact_id: Optional[str] = None
    blob_id: Optional[str] = None
    enabled: Optional[bool] = None
    new_version: Optional[str] = None
    slug_id: Optional[str] = None
    credential_config: Optional[V1SkillCredentialInputParams] = None
    workspace_id: str = ""


@dataclass
class V1SkillDeleteParams:
    id: str = ""
    skill_id: str = ""
    version: str = ""
    workspace_id: str = ""


@dataclass
class V1SkillVersionListParams:
    skill_id: str
    sort_by: str = ""
    sort_order: str = ""
    workspace_id: str = ""
    page: Optional[V1PageInput] = None


@dataclass
class V1SkillResolveVersionParams:
    id: str = ""
    name: str = ""
    constraint: str = ""
    workspace_id: str = ""


@dataclass
class V1ManagedAgentModelConfigParams:
    id: str


@dataclass
class V1ManagedAgentSkillToolParams:
    skill_version_id: str
    type: str = V1_MANAGED_AGENT_SKILL_TOOL_PARAMS_TYPE_SKILL
    enabled: Optional[bool] = None


@dataclass
class V1ManagedAgentMCPToolParams:
    id: str
    type: str = V1_MANAGED_AGENT_MCP_TOOL_PARAMS_TYPE_MCP
    enabled: Optional[bool] = None
    tool_allowlist: Optional[List[str]] = None
    tool_denylist: Optional[List[str]] = None


@dataclass
class V1AgentNewParamsToolUnion:
    of_skill: Optional[V1ManagedAgentSkillToolParams] = None
    of_mcp: Optional[V1ManagedAgentMCPToolParams] = None


@dataclass
class V1ManagedAgentResourceRefParams:
    id: str = ""
    directory_id: str = ""


@dataclass
class V1AgentNewParams:
    name: str
    model: V1ManagedAgentModelConfigParams
    system: Optional[str] = None
    env_id: str = ""
    tools: Optional[List[V1AgentNewParamsToolUnion]] = None
    resources: Optional[List[V1ManagedAgentResourceRefParams]] = None
    workspace_id: str = ""
    description: Optional[str] = None
    channels: Optional[List[Any]] = None
    config: Optional[Any] = None
    metadata: Optional[Dict[str, str]] = None
    icon: Optional[str] = None
    api_protocol_type: Optional[str] = None
    model_interactive_mode: Optional[str] = None
    egress_credentials: Optional[List[Any]] = None


@dataclass
class V1AgentListParams:
    keyword: str = ""
    workspace_id: str = ""


@dataclass
class V1AgentGetParams:
    agent_id: str
    workspace_id: str = ""


@dataclass
class V1AgentBatchGetParams:
    agent_ids: List[str]
    workspace_id: str = ""


@dataclass
class V1AgentUpdateParams:
    agent_id: str
    description: Optional[str] = None
    model_id: Optional[str] = None
    env_id: Optional[str] = None
    system: Optional[str] = None
    skills: Optional[List[V1ManagedAgentSkillToolParams]] = None
    mcps: Optional[List[V1ManagedAgentMCPToolParams]] = None
    resources: Optional[List[V1ManagedAgentResourceRefParams]] = None
    reset_resources: bool = False
    workspace_id: str = ""
    config: Optional[Any] = None
    metadata: Optional[Dict[str, str]] = None
    memory_stores: Optional[List[Any]] = None
    icon: Optional[str] = None
    api_protocol_type: Optional[str] = None
    model_interactive_mode: Optional[str] = None
    egress_credentials: Optional[List[Any]] = None


@dataclass
class V1AgentDeleteParams:
    agent_id: str
    workspace_id: str = ""


@dataclass
class V1AgentRetryCreateParams:
    agent_id: str
    workspace_id: str = ""


@dataclass
class V1AgentStopParams:
    agent_id: str
    workspace_id: str = ""


@dataclass
class V1AgentResumeParams:
    agent_id: str
    workspace_id: str = ""


@dataclass
class V1SessionPeerParams:
    # IM 渠道标识（"feishu"/"wecom"/...）。留空时维持 webchat 默认。
    channel: str = ""
    peer_kind: str = ""
    peer_id: str = ""


@dataclass
class V1SessionNewParams:
    agent_id: str
    # peer 仅在显式指定 IM 渠道或按 user 隔离会话时填写；webchat 主流程留空即可。
    peer: Optional[V1SessionPeerParams] = None
    workspace_id: str = ""
    session_key: str = ""
    risk_level: str = ""
    config: Optional[Any] = None
    auth_context: Optional[Any] = None
    metadata: Optional[Any] = None
    conversation_id: str = ""


@dataclass
class V1SessionChatParams:
    input: str = ""
    agent_id: str = ""
    client_message_id: str = ""
    files: Optional[List[V1MessageFile]] = None
    workspace_id: str = ""
    conversation_id: str = ""


@dataclass
class V1SessionListParams:
    agent_id: str = ""
    status: str = ""
    channel: str = ""
    workspace_id: str = ""
    page: Optional[V1PageInput] = None
    session_keys: Optional[List[str]] = None
    user_id: str = ""


@dataclass
class V1SessionBatchGetParams:
    session_ids: List[str]
    workspace_id: str = ""


@dataclass
class V1SessionGetParams:
    session_id: str
    workspace_id: str = ""


@dataclass
class V1SessionGetByKeyParams:
    session_key: str
    agent_id: str = ""
    workspace_id: str = ""


@dataclass
class V1SessionArchiveParams:
    session_id: str
    summary: str = ""
    consolidate: Optional[bool] = None
    workspace_id: str = ""


@dataclass
class V1SessionDeleteParams:
    session_id: str
    workspace_id: str = ""


@dataclass
class V1MessageListParams:
    session_id: str
    visibility: str = ""
    workspace_id: str = ""
    page: Optional[V1PageInput] = None
    display_mode: str = ""
    base_message_id: str = ""


@dataclass
class V1MessageGetParams:
    session_id: str
    message_id: str
    workspace_id: str = ""


@dataclass
class V1MessageInjectParams:
    session_id: str
    role: str = ""
    content: str = ""
    tool_calls: Optional[Any] = None
    tool_result: Optional[Any] = None
    metadata: Optional[Any] = None
    workspace_id: str = ""


@dataclass
class V1ChatResumeParams:
    session_id: str
    agent_id: str = ""
    run_id: str = ""
    request_id: str = ""
    last_event_id: str = ""
    approve: str = ""
    workspace_id: str = ""


@dataclass
class V1ChatApproveParams:
    session_id: str
    run_id: str
    approval_request_id: str
    choice_id: str
    workspace_id: str = ""


@dataclass
class V1ChatCancelRunParams:
    session_id: str
    run_id: str
    reason: str = ""
    workspace_id: str = ""


@dataclass
class V1FeishuChannelConfigParams:
    app_id: str = ""
    app_secret: str = ""
    encrypt_key: Optional[str] = None
    verification_token: Optional[str] = None
    domain: Optional[str] = None
    connection_mode: Optional[str] = None
    webhook_path: Optional[str] = None
    require_mention: Optional[bool] = None
    render_mode: Optional[str] = None
    streaming: Optional[bool] = None
    reaction_level: Optional[str] = None
    text_chunk_limit: Optional[int] = None
    media_max_mb: Optional[int] = None
    block_reply: Optional[bool] = None


@dataclass
class V1WeComChannelConfigParams:
    bot_id: str = ""
    secret: str = ""


@dataclass
class V1ChannelNewParams:
    agent_id: str
    name: str
    channel_type: str = ""
    dm_policy: str = ""
    group_policy: str = ""
    allowlist: Optional[List[str]] = None
    feishu_config: Optional[V1FeishuChannelConfigParams] = None
    wecom_config: Optional[V1WeComChannelConfigParams] = None
    workspace_id: str = ""


@dataclass
class V1ChannelListParams:
    agent_id: str = ""
    workspace_id: str = ""


@dataclass
class V1ChannelGetParams:
    channel_id: str
    workspace_id: str = ""


@dataclass
class V1ChannelUpdateParams:
    channel_id: str
    name: Optional[str] = None
    channel_type: Optional[str] = None
    target_agent_id: Optional[str] = None
    dm_policy: Optional[str] = None
    group_policy: Optional[str] = None
    allowlist: Optional[List[str]] = None
    feishu_config: Optional[V1FeishuChannelConfigParams] = None
    wecom_config: Optional[V1WeComChannelConfigParams] = None
    workspace_id: str = ""


@dataclass
class V1ChannelDeleteParams:
    channel_id: str
    workspace_id: str = ""


@dataclass
class V1RuntimeAPIKeyNewParams:
    agent_id: str
    expired: str
    description: str = ""
    workspace_id: str = ""


@dataclass
class V1RuntimeAPIKeyListParams:
    agent_id: str
    workspace_id: str = ""


@dataclass
class V1RuntimeAPIKeyUserInfoParams:
    user_name: str
    password: str


@dataclass
class V1RuntimeAPIKeyGetParams:
    agent_id: str
    id: str
    user_info: V1RuntimeAPIKeyUserInfoParams
    workspace_id: str = ""


@dataclass
class V1RuntimeAPIKeyUpdateParams:
    agent_id: str
    id: str
    description: Optional[str] = None
    workspace_id: str = ""


@dataclass
class V1RuntimeAPIKeyDeleteParams:
    agent_id: str
    id: str
    workspace_id: str = ""


@dataclass
class V1RunListParams:
    agent_id: str = ""
    session_id: str = ""
    status: str = ""
    workspace_id: str = ""


@dataclass
class V1RunGetParams:
    run_id: str
    workspace_id: str = ""


@dataclass
class V1CronJobListParams:
    agent_id: str = ""
    source: str = ""
    enabled: Optional[bool] = None
    page: Optional[V1PageInput] = None
    workspace_id: str = ""


@dataclass
class V1CronJobRunListParams:
    cron_job_id: str
    page: Optional[V1PageInput] = None
    workspace_id: str = ""


@dataclass
class V1CronJobRunSyncListParams:
    cursor_updated_at: str = ""
    cursor_id: str = ""
    page_size: Optional[int] = None
    workspace_id: str = ""


@dataclass
class V1CronJobGetParams:
    cron_job_id: str
    workspace_id: str = ""


@dataclass
class V1CronJobNewParams:
    agent_id: str
    name: str
    prompt: str
    schedule_type: str
    schedule_value: str
    delivery_channel: str
    delivery_to: str
    description: str = ""
    schedule_timezone: str = ""
    enabled: Optional[bool] = None
    config: Optional[Any] = None
    correlation_id: str = ""
    workspace_id: str = ""


@dataclass
class V1CronJobUpdateParams:
    cron_job_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    prompt: Optional[str] = None
    schedule_type: Optional[str] = None
    schedule_value: Optional[str] = None
    schedule_timezone: Optional[str] = None
    delivery_channel: Optional[str] = None
    delivery_to: Optional[str] = None
    enabled: Optional[bool] = None
    config: Optional[Any] = None
    update_fields: Optional[List[str]] = None
    correlation_id: str = ""
    workspace_id: str = ""


@dataclass
class V1CronJobDeleteParams:
    cron_job_id: str
    cancel_running: Optional[bool] = None
    correlation_id: str = ""
    workspace_id: str = ""


@dataclass
class V1CronJobToggleParams:
    cron_job_id: str
    enabled: bool
    correlation_id: str = ""
    workspace_id: str = ""


@dataclass
class V1CronJobRunNowParams:
    cron_job_id: str
    correlation_id: str = ""
    workspace_id: str = ""


@dataclass
class V1TraceListParams:
    scroll_id: str = ""
    page_size: Optional[int] = None
    session_id: str = ""
    workspace_id: str = ""


@dataclass
class V1SpanListParams:
    trace_id: str
    scroll_id: str = ""
    page_size: Optional[int] = None
    workspace_id: str = ""


@dataclass
class V1SpanGetParams:
    trace_id: str
    span_id: str
    workspace_id: str = ""


@dataclass
class V1MetricAggregatorParams:
    start_time: str
    end_time: str
    step_seconds: Optional[int] = None


@dataclass
class V1MetricFilterParams:
    workspace_id: str = ""
    agent_ids: Optional[List[str]] = None
    channels: Optional[List[str]] = None
    models: Optional[List[str]] = None
    statuses: Optional[List[str]] = None
    response_modes: Optional[List[str]] = None


@dataclass
class V1MetricOverviewParams:
    aggregator: V1MetricAggregatorParams
    filter: V1MetricFilterParams = field(default_factory=V1MetricFilterParams)
    workspace_id: str = ""


@dataclass
class V1MetricTrendParams:
    metric: str
    aggregator: V1MetricAggregatorParams
    filter: V1MetricFilterParams = field(default_factory=V1MetricFilterParams)
    group_by: str = ""
    statistic: str = ""
    workspace_id: str = ""


@dataclass
class V1MetricTopKParams:
    metric: str
    group_by: str
    aggregator: V1MetricAggregatorParams
    limit: int
    filter: V1MetricFilterParams = field(default_factory=V1MetricFilterParams)
    workspace_id: str = ""


@dataclass
class V1MetricBreakdownParams:
    metric: str
    group_by: str
    aggregator: V1MetricAggregatorParams
    filter: V1MetricFilterParams = field(default_factory=V1MetricFilterParams)
    workspace_id: str = ""


@dataclass
class V1MemoryStoreNewParams:
    name: str
    alias: str
    description: str
    access: str = ""
    extraction_policy: Optional[Any] = None
    quota_policy: Optional[Any] = None
    workspace_id: str = ""


@dataclass
class V1MemoryStoreListParams:
    keyword: str = ""
    page: Optional[V1PageInput] = None
    workspace_id: str = ""


@dataclass
class V1MemoryStoreGetParams:
    store_id: str
    workspace_id: str = ""


@dataclass
class V1MemoryStoreUpdateParams:
    store_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    access: Optional[str] = None
    extraction_policy: Optional[Any] = None
    quota_policy: Optional[Any] = None
    workspace_id: str = ""


@dataclass
class V1MemoryStoreDeleteParams:
    store_id: str
    workspace_id: str = ""


@dataclass
class V1MemoryFileListParams:
    store_id: str
    prefix: str = ""
    page: Optional[V1PageInput] = None
    workspace_id: str = ""


@dataclass
class V1MemoryFileSearchParams:
    store_id: str
    keyword: str
    page: Optional[V1PageInput] = None
    workspace_id: str = ""


@dataclass
class V1MemoryFileGetParams:
    store_id: str
    path: str
    include_content: Optional[bool] = None
    workspace_id: str = ""


@dataclass
class V1MemoryFileUpsertParams:
    store_id: str
    path: str
    content: str
    base_sha256: str = ""
    base_revision: Optional[int] = None
    workspace_id: str = ""


@dataclass
class V1MemoryFileDeleteParams:
    store_id: str
    path: str
    base_sha256: str = ""
    base_revision: Optional[int] = None
    workspace_id: str = ""


# Stream event types


@dataclass
class V1SessionTextDelta:
    text: str = ""


@dataclass
class V1SessionChatError:
    code: str = ""
    message: str = ""


@dataclass
class V1SessionChatEvent:
    type: str = ""
    request_id: str = ""
    delta: V1SessionTextDelta = field(default_factory=V1SessionTextDelta)
    error: V1SessionChatError = field(default_factory=V1SessionChatError)
    message: Optional[V1Message] = None
    raw_data: str = ""


__all__ = [
    name for name in globals() if name.startswith("V1") or name.startswith("_from_dict")
]
