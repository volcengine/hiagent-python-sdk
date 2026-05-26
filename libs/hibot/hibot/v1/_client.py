"""V1 client (mirrors go/hibot/v1/client.go)."""

from __future__ import annotations

from dataclasses import dataclass

from .._request import Requester


@dataclass
class Services:
    server: str
    gateway: str
    model: str
    up: str


class V1Client:
    """Container for all V1 resource services."""

    def __init__(self, requester: Requester, services: Services) -> None:
        self.requester = requester
        self.services = services

        # Lazy import to avoid circular references.
        from .agents import AgentsService
        from .environments import EnvironmentsService
        from .mcps import MCPsService
        from .models import ModelsService
        from .prompts import PromptsService
        from .resources import ResourcesService
        from .sessions import SessionsService
        from .skills import SkillsService
        from .uploads import UploadsService

        self.uploads = UploadsService(self)
        self.environments = EnvironmentsService(self)
        self.models = ModelsService(self)
        self.prompts = PromptsService(self)
        self.resources = ResourcesService(self)
        self.mcps = MCPsService(self)
        self.skills = SkillsService(self)
        self.agents = AgentsService(self)
        self.sessions = SessionsService(self)

    @property
    def workspace_id(self) -> str:
        return self.requester.config.workspace_id
