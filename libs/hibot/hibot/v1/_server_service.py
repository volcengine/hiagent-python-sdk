"""Shared helpers for hibot-server V1 services."""

from __future__ import annotations

from typing import Any, Optional

from .._request import Action
from .._version import SERVER_VERSION
from .types import V1PageInput


class ServerService:
    def __init__(self, v1) -> None:
        self._v1 = v1

    def _action(self, name: str, body: Any):
        return self._v1.requester.do_action(
            Action(
                service=self._v1.services.server,
                version=SERVER_VERSION,
                action=name,
                body=body,
            )
        )


def encode_page(page: Optional[V1PageInput]) -> Optional[dict]:
    if page is None:
        return None
    return {"PageNum": page.page_num, "PageSize": page.page_size}


def put_if(body: dict, key: str, value: Any, *, allow_empty: bool = False) -> None:
    if value is None:
        return
    if not allow_empty and value == "":
        return
    body[key] = value


__all__ = ["ServerService", "encode_page", "put_if"]
