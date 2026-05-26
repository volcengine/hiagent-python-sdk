"""Hibot Managed Agent Python SDK.

Public surface: :class:`Hibot` / :class:`Client` constructors, :class:`Config`,
:class:`APIError`, plus the entire :mod:`hibot.v1` namespace re-exported
under the ``V1*`` prefix for convenience::

    import hibot

    cfg = hibot.Config(
        endpoint="https://open.volcengineapi.com",
        access_key="AK",
        secret_key="SK",
        workspace_id="WS123",
    )
    with hibot.Hibot(cfg) as client:
        agents = client.v1.agents.list()
"""

from __future__ import annotations

from . import v1
from ._config import Config
from ._response import APIError
from ._version import (
    AIGW_SERVICE,
    CHAT_VERSION,
    DEFAULT_REGION,
    GATEWAY_SERVICE,
    MODEL_VERSION,
    SERVER_SERVICE,
    SERVER_VERSION,
    UP_SERVICE,
    UP_VERSION,
)
from .client import Client, Hibot
from .v1 import (  # noqa: F401 — re-export public types
    BASE_MODEL_PROVIDER_BYTEPLUS,
    BASE_MODEL_PROVIDER_OPENAI,
    BASE_MODEL_PROVIDER_VOLCENGINE,
    BASE_MODEL_PROVIDER_VOLCENGINE_AICC,
    BASE_MODEL_TYPE_AUDIO,
    BASE_MODEL_TYPE_EMBEDDINGS,
    BASE_MODEL_TYPE_RERANKING,
    BASE_MODEL_TYPE_TEXT_GENERATION,
    BASE_MODEL_TYPE_VISION,
    BASE_MODELS,
    Services,
    V1Client,
    V1SessionChatStream,
)
from .v1.types import *  # noqa: F401,F403

__version__ = "1.0.0"

__all__ = [
    "Hibot",
    "Client",
    "Config",
    "APIError",
    "v1",
    "Services",
    "V1Client",
    "V1SessionChatStream",
    "BASE_MODELS",
    "BASE_MODEL_TYPE_TEXT_GENERATION",
    "BASE_MODEL_TYPE_EMBEDDINGS",
    "BASE_MODEL_TYPE_VISION",
    "BASE_MODEL_TYPE_AUDIO",
    "BASE_MODEL_TYPE_RERANKING",
    "BASE_MODEL_PROVIDER_VOLCENGINE",
    "BASE_MODEL_PROVIDER_BYTEPLUS",
    "BASE_MODEL_PROVIDER_VOLCENGINE_AICC",
    "BASE_MODEL_PROVIDER_OPENAI",
    "DEFAULT_REGION",
    "SERVER_SERVICE",
    "GATEWAY_SERVICE",
    "AIGW_SERVICE",
    "UP_SERVICE",
    "SERVER_VERSION",
    "CHAT_VERSION",
    "MODEL_VERSION",
    "UP_VERSION",
    "__version__",
]
