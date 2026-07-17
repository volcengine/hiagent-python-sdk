"""V1 client (mirrors go/hibot/v1/client.go)."""

from __future__ import annotations

from dataclasses import dataclass

from .._request import Requester


@dataclass
class Services:
    server: str
    up: str


class V1Client:
    """Container for all V1 resource services."""

    def __init__(self, requester: Requester, services: Services) -> None:
        self.requester = requester
        self.services = services

        # Lazy import to avoid circular references.
        from .agents import AgentsService
        from .channels import ChannelsService
        from .cron_jobs import CronJobsService
        from .environments import EnvironmentsService
        from .mcps import MCPsService
        from .memories import MemoriesService
        from .metrics import MetricsService
        from .models import ModelsService
        from .observations import ObservationsService
        from .overview import OverviewService
        from .prompts import PromptsService
        from .resources import ResourcesService
        from .runs import RunsService
        from .runtime_api_keys import RuntimeAPIKeysService
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
        self.channels = ChannelsService(self)
        self.sessions = SessionsService(self)
        self.runtime_api_keys = RuntimeAPIKeysService(self)
        self.runs = RunsService(self)
        self.cron_jobs = CronJobsService(self)
        self.observations = ObservationsService(self)
        self.overview = OverviewService(self)
        self.metrics = MetricsService(self)
        self.memories = MemoriesService(self)

    @property
    def workspace_id(self) -> str:
        return self.requester.config.workspace_id
