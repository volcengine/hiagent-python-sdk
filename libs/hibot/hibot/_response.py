"""TOP envelope decoding & APIError (mirrors go/hibot/internal/response)."""

from __future__ import annotations

import json
from typing import Any, Optional


class APIError(Exception):
    """Raised on Hibot TOP API errors (non-2xx response or non-empty Error)."""

    def __init__(
        self,
        *,
        status_code: int,
        request_id: str = "",
        code: str = "",
        message: str = "",
    ) -> None:
        self.status_code = status_code
        self.request_id = request_id
        self.code = code
        self.message = message
        super().__init__(self._fmt())

    def _fmt(self) -> str:
        if not self.code and not self.message:
            return f"hibot: api error status={self.status_code} request_id={self.request_id}"
        return (
            f"hibot: api error status={self.status_code} "
            f"request_id={self.request_id} code={self.code} message={self.message}"
        )


def decode_top(status_code: int, body: bytes) -> Optional[Any]:
    """Decode a TOP envelope. Returns ``Result`` (json-decoded) or None.

    Raises APIError on non-2xx status or non-empty ``ResponseMetadata.Error``.
    """
    try:
        env = json.loads(body) if body else {}
    except (ValueError, TypeError):
        if status_code >= 400:
            raise APIError(status_code=status_code, message=body.decode("utf-8", "replace"))
        raise

    if not isinstance(env, dict):
        env = {}
    metadata = env.get("ResponseMetadata") or {}
    request_id = metadata.get("RequestId", "") or metadata.get("RequestID", "")
    err = metadata.get("Error")

    if status_code >= 400 or err:
        code = ""
        message = ""
        if isinstance(err, dict):
            code = err.get("Code", "") or ""
            message = err.get("Message", "") or ""
        elif status_code >= 400 and not env:
            message = body.decode("utf-8", "replace") if body else ""
        raise APIError(
            status_code=status_code,
            request_id=request_id,
            code=code,
            message=message,
        )

    result = env.get("Result")
    if result is None:
        return None
    return result


__all__ = ["APIError", "decode_top"]
