"""Session management for HiAgent SDK CLI."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any, List
from pydantic import BaseModel, Field


def _locked_save_json(path: Path, data: dict, **dump_kwargs) -> None:
    try:
        f = open(path, "r+")
    except FileNotFoundError:
        path.parent.mkdir(parents=True, exist_ok=True)
        f = open(path, "w")

    with f:
        locked = False
        try:
            import fcntl

            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            locked = True
        except (ImportError, OSError):
            locked = False

        try:
            f.seek(0)
            f.truncate()
            json.dump(data, f, **dump_kwargs)
            f.flush()
        finally:
            if locked:
                try:
                    import fcntl

                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                except Exception:
                    pass


class Session(BaseModel):
    """Represents a HiAgent session."""

    name: str
    conversation_id: Optional[str] = None
    workflow_id: Optional[str] = None
    tool_id: Optional[str] = None
    dataset_ids: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class SessionManager:
    """Manages HiAgent sessions."""

    def __init__(self, sessions_dir: Path):
        """Initialize session manager."""
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def _session_file(self, name: str) -> Path:
        """Get session file path."""
        return self.sessions_dir / f"{name}.json"

    def create_session(
        self,
        name: str,
        conversation_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        tool_id: Optional[str] = None,
        dataset_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Session:
        """Create a new session."""
        if self._session_file(name).exists():
            raise ValueError(f"Session '{name}' already exists")

        session = Session(
            name=name,
            conversation_id=conversation_id,
            workflow_id=workflow_id,
            tool_id=tool_id,
            dataset_ids=dataset_ids or [],
            metadata=metadata or {},
        )

        self._save_session(session)
        return session

    def get_session(self, name: str) -> Optional[Session]:
        """Get a session by name."""
        session_file = self._session_file(name)
        if not session_file.exists():
            return None

        try:
            with open(session_file, "r") as f:
                data = json.load(f)
                # Convert ISO datetime strings back to datetime
                if 'created_at' in data:
                    data['created_at'] = datetime.fromisoformat(
                        data['created_at'].replace('Z', '+00:00')
                    )
                if 'updated_at' in data:
                    data['updated_at'] = datetime.fromisoformat(
                        data['updated_at'].replace('Z', '+00:00')
                    )
                return Session(**data)
        except Exception:
            return None

    def list_sessions(self) -> List[str]:
        """List all session names."""
        if not self.sessions_dir.exists():
            return []

        return [f.stem for f in self.sessions_dir.glob("*.json")]

    def save_session(self, session: Session) -> None:
        """Save a session."""
        self._save_session(session)

    def _save_session(self, session: Session) -> None:
        """Internal save method."""
        session.updated_at = datetime.now()
        session_file = self._session_file(session.name)
        _locked_save_json(session_file, session.model_dump(), indent=2, default=str)

    def delete_session(self, name: str) -> bool:
        """Delete a session."""
        session_file = self._session_file(name)
        if session_file.exists():
            session_file.unlink()
            return True
        return False

    def update_session(
        self,
        name: str,
        conversation_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        tool_id: Optional[str] = None,
        dataset_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Session]:
        """Update session properties."""
        session = self.get_session(name)
        if not session:
            return None

        if conversation_id is not None:
            session.conversation_id = conversation_id
        if workflow_id is not None:
            session.workflow_id = workflow_id
        if tool_id is not None:
            session.tool_id = tool_id
        if dataset_ids is not None:
            session.dataset_ids = dataset_ids
        if metadata is not None:
            session.metadata.update(metadata)

        self.save_session(session)
        return session
