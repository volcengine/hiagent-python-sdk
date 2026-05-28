"""Project management for HiAgent SDK CLI."""

from pathlib import Path
from typing import Dict, Optional, Any
import os
import json
from pydantic import BaseModel, Field
from dotenv import dotenv_values


def _read_volc_dotenv() -> dict:
    dotenv_path = Path(os.path.expanduser("~/.volc/.env"))
    if not dotenv_path.is_file():
        return {}
    return dict(dotenv_values(str(dotenv_path)))


class ProjectConfig(BaseModel):
    """Project configuration for HiAgent SDK."""

    app_key: Optional[str] = Field(default=None, description="HiAgent App Key")
    workspace_id: Optional[str] = Field(default=None, description="HiAgent Workspace ID")
    endpoint: str = Field(
        default="https://open.volcengineapi.com", description="HiAgent API endpoint"
    )
    region: str = Field(default="cn-north-1", description="HiAgent region")
    app_base_url: Optional[str] = Field(default=None, description="HiAgent App Base URL")
    up_upload_endpoint: Optional[str] = Field(default=None, description="UP upload endpoint")
    up_download_endpoint: Optional[str] = Field(default=None, description="UP download endpoint")
    user_id: Optional[str] = Field(default=None, description="Default user ID")
    conversation_id: Optional[str] = Field(default=None, description="Default conversation ID")
    tool_id: Optional[str] = Field(default=None, description="Default tool ID")
    workflow_id: Optional[str] = Field(default=None, description="Default workflow ID")
    dataset_ids: list = Field(default_factory=list, description="Default knowledge dataset IDs")

    class Config:
        """Pydantic config."""


class Project:
    """Manages HiAgent project configuration and session state."""

    def __init__(self, project_root: Path):
        """Initialize project."""
        self.project_root = Path(project_root)
        self.config_file = self.project_root / ".hiagent" / "config.json"
        self.session_dir = self.project_root / ".hiagent" / "sessions"
        self._config: Optional[ProjectConfig] = None

        # Ensure directories exist
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.session_dir.mkdir(parents=True, exist_ok=True)

    @property
    def config(self) -> ProjectConfig:
        """Get project configuration."""
        if self._config is None:
            self._config = self._load_config()
        return self._config

    def _load_config(self) -> ProjectConfig:
        """Load configuration from file."""
        if not self.config_file.exists():
            return ProjectConfig()

        try:
            with open(self.config_file, "r") as f:
                data = json.load(f)
                return ProjectConfig(**data)
        except Exception:
            return ProjectConfig()

    def save_config(self, config: Optional[ProjectConfig] = None) -> None:
        """Save configuration to file."""
        if config:
            self._config = config

        config_to_save = self._config or ProjectConfig()
        with open(self.config_file, "w") as f:
            json.dump(config_to_save.model_dump(), f, indent=2)

    def update_config(self, **kwargs) -> ProjectConfig:
        """Update configuration with new values."""
        if self._config is None:
            self._config = self._load_config()

        for key, value in kwargs.items():
            if value is not None:
                setattr(self._config, key, value)

        self.save_config()
        return self._config

    def get_env_config(self) -> Dict[str, Any]:
        """Get configuration from environment variables."""
        dotenv_data = _read_volc_dotenv()
        return {
            "endpoint": os.getenv("HIAGENT_TOP_ENDPOINT")
            or str(dotenv_data.get("HIAGENT_TOP_ENDPOINT") or "").strip()
            or "https://open.volcengineapi.com",
            "region": os.getenv("HIAGENT_REGION")
            or str(dotenv_data.get("HIAGENT_REGION") or "").strip()
            or "cn-north-1",
            "app_base_url": os.getenv("HIAGENT_APP_BASE_URL")
            or str(dotenv_data.get("HIAGENT_APP_BASE_URL") or "").strip()
            or None,
            "up_upload_endpoint": os.getenv("HIAGENT_UP_UPLOAD_ENDPOINT")
            or str(dotenv_data.get("HIAGENT_UP_UPLOAD_ENDPOINT") or "").strip()
            or None,
            "up_download_endpoint": os.getenv("HIAGENT_UP_DOWNLOAD_ENDPOINT")
            or str(dotenv_data.get("HIAGENT_UP_DOWNLOAD_ENDPOINT") or "").strip()
            or None,
            "app_key": os.getenv("HIAGENT_AGENT_APP_KEY")
            or os.getenv("HIAGENT_APP_KEY")
            or str(dotenv_data.get("HIAGENT_AGENT_APP_KEY") or "").strip()
            or str(dotenv_data.get("HIAGENT_APP_KEY") or "").strip()
            or None,
            "workspace_id": os.getenv("HIAGENT_WORKSPACE_ID")
            or os.getenv("WORKSPACE_ID")
            or str(dotenv_data.get("HIAGENT_WORKSPACE_ID") or "").strip()
            or str(dotenv_data.get("WORKSPACE_ID") or "").strip()
            or None,
            "user_id": os.getenv("HIAGENT_USER_ID")
            or str(dotenv_data.get("HIAGENT_USER_ID") or "").strip()
            or "cli-user",
        }

    def get_effective_config(self) -> Dict[str, Any]:
        """Get effective configuration (env vars override project config)."""
        env_config = self.get_env_config()
        project_config = self.config.model_dump()

        effective = dict(project_config)
        for k, v in env_config.items():
            if v is not None:
                effective[k] = v

        # Filter out None values
        return {k: v for k, v in effective.items() if v is not None}

    def create_session_file(self, name: str) -> Path:
        """Create a session file."""
        session_file = self.session_dir / f"{name}.json"
        session_file.parent.mkdir(parents=True, exist_ok=True)
        return session_file

    def list_sessions(self) -> list:
        """List all session files."""
        if not self.session_dir.exists():
            return []

        return [f.stem for f in self.session_dir.glob("*.json")]
