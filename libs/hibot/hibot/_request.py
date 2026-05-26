"""HTTP request layer for TOP Action calls (mirrors go/hibot/internal/request)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Iterator, Mapping, Optional
from urllib.parse import urlencode, urlsplit, urlunsplit

import httpx

from ._config import Config
from ._response import APIError, decode_top
from ._signer import sign_request


@dataclass
class Action:
    service: str
    version: str
    action: str
    body: Any = None
    stream: bool = False


class Requester:
    """Synchronous TOP request executor shared by all V1 resource services."""

    def __init__(self, config: Config) -> None:
        self._cfg = config
        self._client: Optional[httpx.Client] = None
        if config.http_client is not None and isinstance(config.http_client, httpx.Client):
            self._client = config.http_client
            self._owns_client = False
        else:
            self._client = httpx.Client(timeout=config.timeout)
            self._owns_client = True

    @property
    def config(self) -> Config:
        return self._cfg

    def close(self) -> None:
        if self._owns_client and self._client is not None:
            self._client.close()
            self._client = None

    # -------- public ops --------

    def do_action(self, action: Action) -> Optional[Any]:
        body_bytes = self._marshal_body(action.body)
        url, headers = self._build_request(action, body_bytes, "application/json", None)
        resp = self._client.request("POST", url, content=body_bytes, headers=headers)
        return decode_top(resp.status_code, resp.content)

    def do_raw_action(
        self,
        action: Action,
        body: bytes,
        content_type: str,
        query: Optional[Mapping[str, str]] = None,
    ) -> Optional[Any]:
        url, headers = self._build_request(action, body or b"", content_type or "application/octet-stream", query)
        resp = self._client.request("POST", url, content=body or b"", headers=headers)
        return decode_top(resp.status_code, resp.content)

    def stream_action(self, action: Action) -> "_StreamResponse":
        body_bytes = self._marshal_body(action.body)
        action.stream = True
        url, headers = self._build_request(action, body_bytes, "application/json", None)
        # SSE streams may run beyond the default timeout.
        ctx = self._client.stream("POST", url, content=body_bytes, headers=headers, timeout=None)
        resp = ctx.__enter__()
        return _StreamResponse(ctx, resp)

    # -------- internals --------

    def _marshal_body(self, body: Any) -> bytes:
        m = _to_map(body)
        if self._cfg.workspace_id and _workspace_missing(m.get("WorkspaceID")):
            m["WorkspaceID"] = self._cfg.workspace_id
        return json.dumps(m, separators=(",", ":")).encode("utf-8")

    def _build_request(
        self,
        action: Action,
        body: bytes,
        content_type: str,
        query: Optional[Mapping[str, str]],
    ):
        # Compose URL: TOP gateway hosts the up service under /up
        # subpath; other services share the root path.
        parts = urlsplit(self._cfg.endpoint)
        path = parts.path or ""
        if action.service == self._cfg.up_service or action.service == "up":
            path = path.rstrip("/") + "/up"
        q = {}
        # Preserve any pre-existing query on the endpoint (rare).
        if parts.query:
            from urllib.parse import parse_qsl
            q.update(dict(parse_qsl(parts.query, keep_blank_values=True)))
        q["Action"] = action.action
        q["Version"] = action.version
        if query:
            q.update(query)
        encoded = urlencode(q)
        url = urlunsplit((parts.scheme, parts.netloc, path, encoded, ""))

        headers: Dict[str, str] = {
            "Content-Type": content_type,
            "X-Top-Service": action.service,
        }
        if action.stream:
            headers["Accept"] = "text/event-stream"

        signed = sign_request(
            method="POST",
            url=url,
            headers=headers,
            body=body,
            access_key=self._cfg.access_key,
            secret_key=self._cfg.secret_key,
            region=self._cfg.region,
            service=action.service,
        )
        return url, signed


class _StreamResponse:
    """Wrapper that owns the httpx stream context manager."""

    def __init__(self, ctx, resp: httpx.Response) -> None:
        self._ctx = ctx
        self._resp = resp
        self._closed = False

    @property
    def status_code(self) -> int:
        return self._resp.status_code

    def read_all(self) -> bytes:
        return self._resp.read()

    def iter_bytes(self) -> Iterator[bytes]:
        return self._resp.iter_raw()

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            self._ctx.__exit__(None, None, None)
        except Exception:  # noqa: BLE001
            pass


def _to_map(v: Any) -> Dict[str, Any]:
    if v is None:
        return {}
    if isinstance(v, dict):
        # Ensure we deep-copy via JSON so callers don't get aliasing of injected keys.
        return json.loads(json.dumps(v, default=_default_encoder))
    # Encode arbitrary objects via JSON serializer (dataclasses etc.)
    return json.loads(json.dumps(v, default=_default_encoder))


def _default_encoder(o: Any) -> Any:
    if hasattr(o, "to_dict") and callable(o.to_dict):
        return o.to_dict()
    if hasattr(o, "__dict__"):
        return {k: v for k, v in o.__dict__.items() if not k.startswith("_") and v is not None}
    raise TypeError(f"hibot: cannot encode object of type {type(o).__name__}")


def _workspace_missing(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, str):
        return v == ""
    return False


__all__ = ["Requester", "Action", "APIError"]
