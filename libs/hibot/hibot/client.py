"""Top-level Hibot client (mirrors go/hibot/hibot.go + v1/client.go)."""

from __future__ import annotations

from ._config import Config
from ._request import Requester
from .v1 import Services, V1Client


class Client:
    """Synchronous Hibot SDK client.

    Acquire via :class:`Hibot` (alias) or directly with a :class:`Config`::

        client = hibot.Hibot(config)
        agents = client.v1.agents.list()
    """

    def __init__(self, config: Config) -> None:
        self._config = config
        self._requester = Requester(config)
        services = Services(
            server=config.server_service,
            gateway=config.gateway_service,
            model=config.model_service,
            up=config.up_service,
        )
        self.v1 = V1Client(self._requester, services)

    @property
    def config(self) -> Config:
        return self._config

    def close(self) -> None:
        self._requester.close()

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


# Alias requested by the spec (Go's *hibot.Hibot ~ Python's Hibot()).
Hibot = Client


__all__ = ["Client", "Hibot"]
