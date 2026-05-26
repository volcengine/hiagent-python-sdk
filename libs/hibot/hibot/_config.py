"""SDK Config (mirrors go/hibot/config.go)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from . import _version as _v


@dataclass
class Config:
    endpoint: str
    access_key: str
    secret_key: str
    workspace_id: str
    region: str = _v.DEFAULT_REGION
    server_service: str = _v.SERVER_SERVICE
    gateway_service: str = _v.GATEWAY_SERVICE
    model_service: str = _v.AIGW_SERVICE
    up_service: str = _v.UP_SERVICE
    timeout: float = 30.0
    # Optional pre-built httpx.Client / httpx.AsyncClient — leave None to let
    # SDK build defaults internally.
    http_client: Optional[object] = None
    async_http_client: Optional[object] = None

    def __post_init__(self) -> None:
        self.endpoint = (self.endpoint or "").strip()
        self.access_key = (self.access_key or "").strip()
        self.secret_key = (self.secret_key or "").strip()
        self.workspace_id = (self.workspace_id or "").strip()
        self.region = (self.region or "").strip() or _v.DEFAULT_REGION
        self.server_service = (self.server_service or "").strip() or _v.SERVER_SERVICE
        self.gateway_service = (self.gateway_service or "").strip() or _v.GATEWAY_SERVICE
        self.model_service = (self.model_service or "").strip() or _v.AIGW_SERVICE
        self.up_service = (self.up_service or "").strip() or _v.UP_SERVICE

        if not self.endpoint:
            raise ValueError("hibot: endpoint is required")
        if not self.access_key:
            raise ValueError("hibot: access key is required")
        if not self.secret_key:
            raise ValueError("hibot: secret key is required")
        if not self.workspace_id:
            raise ValueError("hibot: workspace id is required")
