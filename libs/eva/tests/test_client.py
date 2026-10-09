from types import SimpleNamespace

from hiagent_eva.client import Client


class CapturingEvaService:
    def __init__(self):
        self.request = None

    def CreateEvaTask(self, request):
        self.request = request
        return SimpleNamespace(TaskID="task-id")


def test_create_task_wraps_custom_app_configuration():
    client = Client(
        endpoint="http://eva.example.test",
        ak="ak",
        sk="sk",
        workspace_id="workspace-id",
        app_id="app-id",
    )
    service = CapturingEvaService()
    client.eva_service = service

    response = client.create_task(
        dataset_id="dataset-id",
        dataset_version_id="dataset-version-id",
        task_name="task-name",
        ruleset_id="ruleset-id",
        run_immediately=False,
    )

    assert response.TaskID == "task-id"
    assert service.request.Targets[0].TargetConfig == {
        "CustomAPPConfig": {
            "AppID": "app-id",
            "ModelAgentConfig": None,
        }
    }
