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

V1_MANAGED_AGENT_MODEL_DOUBAO_SEED_PRO = "doubao-seed-2.0-pro-260215"
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
    created_at: Optional[str] = field(default=None, metadata={"json": "CreatedAt"})
    updated_at: Optional[str] = field(default=None, metadata={"json": "UpdatedAt"})
    created_by: Optional[str] = field(default=None, metadata={"json": "CreatedBy"})
    updated_by: Optional[str] = field(default=None, metadata={"json": "UpdatedBy"})


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
    features_config: Optional[Any] = field(default=None, metadata={"json": "FeaturesConfig"})
    property: Optional[Any] = field(default=None, metadata={"json": "Property"})
    credential_schema: Optional[Any] = field(default=None, metadata={"json": "CredentialSchema"})
    credential: Optional[Dict[str, str]] = field(default=None, metadata={"json": "Credential"})
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
    features_config: Optional[Any] = field(default=None, metadata={"json": "FeaturesConfig"})
    property: Optional[Any] = field(default=None, metadata={"json": "Property"})
    credential_schema: Optional[Any] = field(default=None, metadata={"json": "CredentialSchema"})


@dataclass
class V1ModelProviderList:
    items: List[V1ModelProvider] = field(default_factory=list, metadata={"json": "Models"})
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
    resource_count: Optional[int] = field(default=None, metadata={"json": "ResourceCount"})


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
    headers: Optional[Dict[str, str]] = field(default=None, metadata={"json": "Headers"})
    env: Optional[Dict[str, str]] = field(default=None, metadata={"json": "Env"})
    command: Optional[str] = field(default=None, metadata={"json": "Command"})
    args: Optional[List[str]] = field(default=None, metadata={"json": "Args"})
    auth_type: Optional[str] = field(default=None, metadata={"json": "AuthType"})
    tool_allowlist: Optional[List[str]] = field(default=None, metadata={"json": "ToolAllowlist"})
    tool_denylist: Optional[List[str]] = field(default=None, metadata={"json": "ToolDenylist"})
    tool_prefix: Optional[str] = field(default=None, metadata={"json": "ToolPrefix"})
    timeout: Optional[int] = field(default=None, metadata={"json": "Timeout"})
    status: Optional[str] = field(default=None, metadata={"json": "Status"})
    source: Optional[str] = field(default=None, metadata={"json": "Source"})
    created_at: Optional[str] = field(default=None, metadata={"json": "CreatedAt"})


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
class V1AgentSkillBinding:
    id: Optional[str] = field(default=None, metadata={"json": "ID"})
    enabled: Optional[bool] = field(default=None, metadata={"json": "Enabled"})


@dataclass
class V1AgentMCPBinding:
    id: Optional[str] = field(default=None, metadata={"json": "ID"})
    enabled: Optional[bool] = field(default=None, metadata={"json": "Enabled"})
    tool_allowlist: Optional[List[str]] = field(default=None, metadata={"json": "ToolAllowlist"})
    tool_denylist: Optional[List[str]] = field(default=None, metadata={"json": "ToolDenylist"})


@dataclass
class V1Agent:
    id: Optional[str] = field(default=None, metadata={"json": "ID"})
    workspace_id: Optional[str] = field(default=None, metadata={"json": "WorkspaceID"})
    name: Optional[str] = field(default=None, metadata={"json": "Name"})
    description: Optional[str] = field(default=None, metadata={"json": "Description"})
    model_id: Optional[str] = field(default=None, metadata={"json": "ModelID"})
    env_id: Optional[str] = field(default=None, metadata={"json": "EnvID"})
    system_prompt: Optional[str] = field(default=None, metadata={"json": "SystemPrompt"})
    skills: Optional[List[V1AgentSkillBinding]] = field(default=None, metadata={"json": "Skills"})
    mcps: Optional[List[V1AgentMCPBinding]] = field(default=None, metadata={"json": "MCPs"})
    resource_ids: Optional[List[str]] = field(default=None, metadata={"json": "ResourceIDs"})
    created_at: Optional[str] = field(default=None, metadata={"json": "CreatedAt"})
    updated_at: Optional[str] = field(default=None, metadata={"json": "UpdatedAt"})


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
    message_count: Optional[int] = field(default=None, metadata={"json": "MessageCount"})
    last_message_at: Optional[str] = field(default=None, metadata={"json": "LastMessageAt"})
    last_message_content: Optional[str] = field(default=None, metadata={"json": "LastMessageContent"})
    summary: Optional[str] = field(default=None, metadata={"json": "Summary"})
    created_at: Optional[str] = field(default=None, metadata={"json": "CreatedAt"})
    updated_at: Optional[str] = field(default=None, metadata={"json": "UpdatedAt"})
    archived_at: Optional[str] = field(default=None, metadata={"json": "ArchivedAt"})


@dataclass
class V1MessageFile:
    file_id: Optional[str] = field(default=None, metadata={"json": "FileID"})
    name: Optional[str] = field(default=None, metadata={"json": "Name"})
    content_type: Optional[str] = field(default=None, metadata={"json": "ContentType"})
    url: Optional[str] = field(default=None, metadata={"json": "URL"})
    blob_id: Optional[str] = field(default=None, metadata={"json": "BlobID"})


@dataclass
class V1Message:
    id: Optional[str] = field(default=None, metadata={"json": "ID"})
    session_id: Optional[str] = field(default=None, metadata={"json": "SessionID"})
    run_id: Optional[str] = field(default=None, metadata={"json": "RunID"})
    role: Optional[str] = field(default=None, metadata={"json": "Role"})
    content: Optional[str] = field(default=None, metadata={"json": "Content"})
    visibility: Optional[str] = field(default=None, metadata={"json": "Visibility"})
    created_at: Optional[str] = field(default=None, metadata={"json": "CreatedAt"})
    files: Optional[List[V1MessageFile]] = field(default=None, metadata={"json": "Files"})


@dataclass
class V1MessageList:
    items: List[V1Message] = field(default_factory=list, metadata={"json": "Items"})
    page: Optional[V1Page] = field(default=None, metadata={"json": "Page"})


@dataclass
class V1SessionList:
    items: List[V1Session] = field(default_factory=list, metadata={"json": "Items"})
    page: Optional[V1Page] = field(default=None, metadata={"json": "Page"})


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
class V1SkillUpdateParams:
    id: str = ""
    skill_id: str = ""
    version: str = ""
    description: Optional[str] = None
    source: Optional[str] = None
    artifact_id: Optional[str] = None
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


@dataclass
class V1ManagedAgentMCPToolParams:
    id: str
    type: str = V1_MANAGED_AGENT_MCP_TOOL_PARAMS_TYPE_MCP


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


@dataclass
class V1AgentDeleteParams:
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


@dataclass
class V1SessionChatParams:
    input: str = ""
    agent_id: str = ""
    client_message_id: str = ""
    files: Optional[List[V1MessageFile]] = None
    workspace_id: str = ""


@dataclass
class V1SessionListParams:
    agent_id: str = ""
    status: str = ""
    channel: str = ""
    workspace_id: str = ""
    page: Optional[V1PageInput] = None


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


__all__ = [name for name in globals() if name.startswith("V1") or name.startswith("_from_dict")]
