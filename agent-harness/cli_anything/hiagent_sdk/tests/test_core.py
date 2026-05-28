"""Unit tests for core modules with synthetic data."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from cli_anything.hiagent_sdk.core.project import Project, ProjectConfig
from cli_anything.hiagent_sdk.core.session import SessionManager, Session
from cli_anything.hiagent_sdk.core.services import ServiceManager
from cli_anything.hiagent_sdk.core.export import Exporter
from cli_anything.hiagent_sdk.utils.hiagent_backend import ensure_volc_credentials


class TestProject:
    """Test project configuration module."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Project(Path(tmpdir))

    def test_project_create(self, temp_project):
        """Test project directory structure creation."""
        assert temp_project.project_root.exists()
        assert temp_project.config_file.parent.exists()
        assert temp_project.session_dir.exists()

    def test_project_config_load(self, temp_project):
        """Test configuration loading from file."""
        # Save config first
        config = ProjectConfig(app_key="test-key", workspace_id="ws-123")
        temp_project.save_config(config)

        # Load in new project instance
        project2 = Project(temp_project.project_root)
        assert project2.config.app_key == "test-key"
        assert project2.config.workspace_id == "ws-123"

    def test_project_config_save(self, temp_project):
        """Test configuration saving to file."""
        config = ProjectConfig(
            app_key="test-key",
            workspace_id="ws-123",
            endpoint="https://test.com",
        )
        temp_project.save_config(config)

        # Verify file exists and contains correct data
        assert temp_project.config_file.exists()
        data = json.loads(temp_project.config_file.read_text())
        assert data["app_key"] == "test-key"
        assert data["workspace_id"] == "ws-123"

    def test_project_config_update(self, temp_project):
        """Test individual configuration value updates."""
        temp_project.update_config(app_key="key1", workspace_id="ws-1")
        assert temp_project.config.app_key == "key1"
        assert temp_project.config.workspace_id == "ws-1"

        temp_project.update_config(app_key="key2")
        assert temp_project.config.app_key == "key2"
        assert temp_project.config.workspace_id == "ws-1"  # unchanged

    def test_project_env_config(self, temp_project):
        """Test environment variable configuration override."""
        os.environ["HIAGENT_TOP_ENDPOINT"] = "https://env-test.com"
        os.environ["HIAGENT_AGENT_APP_KEY"] = "env-key"
        os.environ["HIAGENT_WORKSPACE_ID"] = "env-ws"

        try:
            env_config = temp_project.get_env_config()
            assert env_config["endpoint"] == "https://env-test.com"
            assert env_config["app_key"] == "env-key"
            assert env_config["workspace_id"] == "env-ws"
        finally:
            del os.environ["HIAGENT_TOP_ENDPOINT"]
            del os.environ["HIAGENT_AGENT_APP_KEY"]
            del os.environ["HIAGENT_WORKSPACE_ID"]

    def test_project_env_config_from_volc_dotenv(self, temp_project, monkeypatch):
        with tempfile.TemporaryDirectory() as tmp_home:
            volc_dir = Path(tmp_home) / ".volc"
            volc_dir.mkdir(parents=True, exist_ok=True)
            (volc_dir / ".env").write_text(
                "\n".join(
                    [
                        "HIAGENT_TOP_ENDPOINT=https://dotenv-test.com",
                        "HIAGENT_APP_KEY=dotenv-app-key",
                        "WORKSPACE_ID=dotenv-ws",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            monkeypatch.setenv("HOME", tmp_home)
            monkeypatch.delenv("HIAGENT_TOP_ENDPOINT", raising=False)
            monkeypatch.delenv("HIAGENT_AGENT_APP_KEY", raising=False)
            monkeypatch.delenv("HIAGENT_APP_KEY", raising=False)
            monkeypatch.delenv("HIAGENT_WORKSPACE_ID", raising=False)
            monkeypatch.delenv("WORKSPACE_ID", raising=False)

            env_config = temp_project.get_env_config()
            assert env_config["endpoint"] == "https://dotenv-test.com"
            assert env_config["app_key"] == "dotenv-app-key"
            assert env_config["workspace_id"] == "dotenv-ws"

    def test_volc_credentials_from_volc_dotenv(self, monkeypatch):
        with tempfile.TemporaryDirectory() as tmp_home:
            volc_dir = Path(tmp_home) / ".volc"
            volc_dir.mkdir(parents=True, exist_ok=True)
            (volc_dir / ".env").write_text(
                "\n".join(
                    [
                        "VOLC_ACCESSKEY=dotenv-ak",
                        "VOLC_SECRETKEY=dotenv-sk",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            monkeypatch.setenv("HOME", tmp_home)
            monkeypatch.delenv("VOLC_ACCESSKEY", raising=False)
            monkeypatch.delenv("VOLC_SECRETKEY", raising=False)

            ensure_volc_credentials()

    def test_project_effective_config(self, temp_project, monkeypatch):
        """Test effective configuration (env vars override project config)."""
        with tempfile.TemporaryDirectory() as tmp_home:
            monkeypatch.setenv("HOME", tmp_home)
            monkeypatch.delenv("HIAGENT_WORKSPACE_ID", raising=False)
            monkeypatch.delenv("WORKSPACE_ID", raising=False)
            monkeypatch.delenv("HIAGENT_AGENT_APP_KEY", raising=False)
            monkeypatch.delenv("HIAGENT_APP_KEY", raising=False)

            temp_project.update_config(app_key="project-key", workspace_id="project-ws")
            monkeypatch.setenv("HIAGENT_AGENT_APP_KEY", "env-key")

            effective = temp_project.get_effective_config()
            assert effective["app_key"] == "env-key"  # env overrides project
            assert effective["workspace_id"] == "project-ws"  # project value preserved

    def test_project_session_file(self, temp_project):
        """Test session file creation."""
        session_file = temp_project.create_session_file("test-session")
        assert session_file.parent.exists()
        assert session_file.name == "test-session.json"

    def test_project_list_sessions(self, temp_project):
        """Test listing sessions."""
        # Create some session files
        (temp_project.session_dir / "session1.json").write_text('{"name": "session1"}')
        (temp_project.session_dir / "session2.json").write_text('{"name": "session2"}')

        sessions = temp_project.list_sessions()
        assert "session1" in sessions
        assert "session2" in sessions


class TestSessionManager:
    """Test session management module."""

    @pytest.fixture
    def temp_session_manager(self):
        """Create a temporary session manager."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield SessionManager(Path(tmpdir))

    def test_session_create(self, temp_session_manager):
        """Test creating a new session."""
        session = temp_session_manager.create_session(
            name="test-session",
            conversation_id="conv-123",
            workflow_id="wf-456",
            tool_id="tool-789",
            dataset_ids=["ds-001", "ds-002"],
        )

        assert session.name == "test-session"
        assert session.conversation_id == "conv-123"
        assert session.workflow_id == "wf-456"
        assert session.tool_id == "tool-789"
        assert session.dataset_ids == ["ds-001", "ds-002"]

    def test_session_create_duplicate(self, temp_session_manager):
        """Test creating duplicate session raises error."""
        temp_session_manager.create_session(name="test-session")

        with pytest.raises(ValueError, match="already exists"):
            temp_session_manager.create_session(name="test-session")

    def test_session_get(self, temp_session_manager):
        """Test retrieving a session."""
        created = temp_session_manager.create_session(
            name="test-session", conversation_id="conv-123"
        )

        retrieved = temp_session_manager.get_session("test-session")
        assert retrieved is not None
        assert retrieved.name == created.name
        assert retrieved.conversation_id == "conv-123"

    def test_session_get_nonexistent(self, temp_session_manager):
        """Test retrieving nonexistent session returns None."""
        session = temp_session_manager.get_session("nonexistent")
        assert session is None

    def test_session_list(self, temp_session_manager):
        """Test listing all sessions."""
        temp_session_manager.create_session(name="session1")
        temp_session_manager.create_session(name="session2")
        temp_session_manager.create_session(name="session3")

        sessions = temp_session_manager.list_sessions()
        assert len(sessions) == 3
        assert "session1" in sessions
        assert "session2" in sessions
        assert "session3" in sessions


    def test_session_delete(self, temp_session_manager):
        """Test deleting a session."""
        temp_session_manager.create_session(name="test-session")
        assert temp_session_manager.get_session("test-session") is not None

        success = temp_session_manager.delete_session("test-session")
        assert success is True
        assert temp_session_manager.get_session("test-session") is None

    def test_session_delete_nonexistent(self, temp_session_manager):
        """Test deleting nonexistent session returns False."""
        success = temp_session_manager.delete_session("nonexistent")
        assert success is False

    def test_session_update(self, temp_session_manager):
        """Test updating session properties."""
        temp_session_manager.create_session(name="test-session", conversation_id="conv-123")

        updated = temp_session_manager.update_session(
            name="test-session",
            conversation_id="conv-456",
            workflow_id="wf-789",
            metadata={"key": "value"},
        )

        assert updated is not None
        assert updated.conversation_id == "conv-456"
        assert updated.workflow_id == "wf-789"
        assert updated.metadata["key"] == "value"

    def test_session_update_nonexistent(self, temp_session_manager):
        """Test updating nonexistent session returns None."""
        updated = temp_session_manager.update_session(
            name="nonexistent", conversation_id="conv-123"
        )
        assert updated is None

    def test_session_metadata(self, temp_session_manager):
        """Test metadata storage in sessions."""
        session = temp_session_manager.create_session(
            name="test-session", metadata={"key": "value", "count": 42}
        )

        assert session.metadata["key"] == "value"
        assert session.metadata["count"] == 42

        # Update metadata
        session.metadata["new_key"] = "new_value"
        temp_session_manager.save_session(session)

        retrieved = temp_session_manager.get_session("test-session")
        assert retrieved is not None
        assert retrieved.metadata["new_key"] == "new_value"


def test_service_manager_sets_chat_app_base_url(monkeypatch):
    import sys
    import types

    class _DummyChatService:
        def __init__(self, endpoint: str, region: str):
            self.endpoint = endpoint
            self.region = region
            self.base_url = None

        def set_app_base_url(self, base_url: str):
            self.base_url = base_url

    pkg = types.ModuleType("hiagent_api")
    mod = types.ModuleType("hiagent_api.chat")
    mod.ChatService = _DummyChatService

    monkeypatch.setitem(sys.modules, "hiagent_api", pkg)
    monkeypatch.setitem(sys.modules, "hiagent_api.chat", mod)

    manager = ServiceManager(
        {"endpoint": "https://test.com", "region": "cn-north-1", "app_base_url": "http://base"}
    )
    svc = manager.get_chat_service()
    assert svc.base_url == "http://base"


class TestServiceManager:
    """Test service manager module."""

    def test_service_initialization(self):
        """Test service creation with configuration."""
        config = {"endpoint": "https://test.com", "region": "us-west-1"}
        manager = ServiceManager(config)

        assert manager.config == config
        assert manager.get_endpoint() == "https://test.com"
        assert manager.get_region() == "us-west-1"

    def test_service_caching(self):
        """Test service instance caching."""
        config = {"endpoint": "https://test.com", "region": "cn-north-1"}
        manager = ServiceManager(config)

        # Get service twice
        chat1 = manager.get_chat_service()
        chat2 = manager.get_chat_service()

        # Should be same instance
        assert chat1 is chat2

        tool1 = manager.get_tool_service()
        tool2 = manager.get_tool_service()
        assert tool1 is tool2

    def test_service_config_access(self):
        """Test configuration retrieval from service manager."""
        config = {"endpoint": "https://custom.com", "region": "eu-west-1", "app_key": "test-key"}
        manager = ServiceManager(config)

        assert manager.get_endpoint() == "https://custom.com"
        assert manager.get_region() == "eu-west-1"

    @patch("cli_anything.hiagent_sdk.core.services.Agent")
    def test_agent_initialization(self, mock_agent_class):
        """Test agent component initialization."""
        mock_agent = Mock()
        mock_agent_class.init.return_value = mock_agent

        config = {"endpoint": "https://test.com", "region": "cn-north-1"}
        manager = ServiceManager(config)

        agent = manager.init_agent(
            app_key="app-key",
            user_id="user-123",
            variables={"name": "test"},
        )

        mock_agent_class.init.assert_called_once()
        assert agent == mock_agent

    @patch("cli_anything.hiagent_sdk.core.services.Tool")
    def test_tool_initialization(self, mock_tool_class):
        """Test tool component initialization."""
        mock_tool = Mock()
        mock_tool_class.init.return_value = mock_tool

        config = {"endpoint": "https://test.com", "region": "cn-north-1"}
        manager = ServiceManager(config)

        tool = manager.init_tool(
            workspace_id="ws-123",
            tool_id="tool-456",
        )

        mock_tool_class.init.assert_called_once()
        assert tool == mock_tool

    @patch("cli_anything.hiagent_sdk.core.services.Workflow")
    def test_workflow_initialization(self, mock_workflow_class):
        """Test workflow component initialization."""
        mock_workflow = Mock()
        mock_workflow_class.init.return_value = mock_workflow

        config = {"endpoint": "https://test.com", "region": "cn-north-1"}
        manager = ServiceManager(config)

        workflow = manager.init_workflow(
            app_key="app-key",
            workspace_id="ws-123",
            workflow_id="wf-456",
            user_id="user-123",
        )

        mock_workflow_class.init.assert_called_once()
        assert workflow == mock_workflow

    @patch("cli_anything.hiagent_sdk.core.services.KnowledgeRetriever")
    def test_retriever_initialization(self, mock_retriever_class):
        """Test retriever component initialization."""
        mock_retriever = Mock()
        mock_retriever_class.return_value = mock_retriever

        config = {"endpoint": "https://test.com", "region": "cn-north-1"}
        manager = ServiceManager(config)

        retriever = manager.init_retriever(
            workspace_id="ws-123",
            dataset_ids=["ds-001", "ds-002"],
            name="test-retriever",
            top_k=5,
        )

        mock_retriever_class.assert_called_once()
        assert retriever == mock_retriever


class TestExportModule:
    """Test export/output formatting module."""

    def test_json_export(self):
        """Test JSON output formatting."""
        exporter = Exporter(json_mode=True)

        import io
        import sys
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            exporter.print_result({"key": "value"}, True, "Success message")

        output = f.getvalue()
        data = json.loads(output.strip())

        assert data["success"] is True
        assert data["message"] == "Success message"
        assert data["data"]["key"] == "value"

    def test_human_export(self):
        """Test human-readable output formatting."""
        exporter = Exporter(json_mode=False)

        import io
        import sys
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            exporter.print_result({"key": "value"}, True, "Success message")

        output = f.getvalue()
        assert "✓ Success message" in output
        assert "key:" in output
        assert "value" in output

    def test_export_serialization(self):
        """Test data serialization from pydantic models."""
        from pydantic import BaseModel

        class TestModel(BaseModel):
            name: str
            count: int

        model = TestModel(name="test", count=42)
        exporter = Exporter(json_mode=True)

        import io
        import sys
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            exporter.print_result(model.model_dump(), True, "Serialized")

        output = f.getvalue()
        data = json.loads(output.strip())
        assert data["data"]["name"] == "test"
        assert data["data"]["count"] == 42

    def test_export_table(self):
        """Test table formatting for lists."""
        exporter = Exporter(json_mode=False)

        data = [
            {"id": 1, "name": "item1"},
            {"id": 2, "name": "item2"},
            {"id": 3, "name": "item3"},
        ]

        import io
        import sys
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            exporter.print_result(data, True, "Items list")

        output = f.getvalue()
        assert "Items list" in output
        assert "item1" in output
        assert "item2" in output
        assert "item3" in output

    def test_export_file_operations(self, tmp_path):
        """Test JSON file read/write operations."""
        test_file = tmp_path / "test.json"
        test_data = {"key": "value", "nested": {"a": 1, "b": 2}}

        # Write
        exporter = Exporter(json_mode=True)
        test_file.write_text(json.dumps(test_data))

        # Read and verify
        loaded = json.loads(test_file.read_text())
        assert loaded == test_data
        assert loaded["nested"]["a"] == 1
        assert loaded["nested"]["b"] == 2
