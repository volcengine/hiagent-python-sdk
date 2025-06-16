import asyncio
import os

from dotenv import load_dotenv
from hiagent_api.workflow import WorkflowService
from hiagent_components.workflow.base import Workflow

load_dotenv()


def get_workflow_svc() -> WorkflowService:
    svc = WorkflowService(
        endpoint=os.getenv("HIAGENT_TOP_ENDPOINT") or "", region="cn-north-1"
    )

    svc.set_app_base_url(os.getenv("HIAGENT_APP_BASE_URL") or "")

    return svc


def invoke_retryable_workflow():
    app_key = os.getenv("HIAGENT_APP_KEY") or ""
    workflow = Workflow.init(
        svc=get_workflow_svc(),
        app_key=app_key,
        workflow_id="cvel84kg58epjrfkvtb0",
        workspace_id="cuq0pp9s7366bfl0cns0",
        user_id="test",
    )

    resp = workflow.with_retry().invoke(input={"query": "你好"})
    print("invoke workflow:", resp)


async def ainvoke_retryable_workflow():
    app_key = os.getenv("HIAGENT_APP_KEY") or ""
    workflow = await Workflow.ainit(
        svc=get_workflow_svc(),
        app_key=app_key,
        workflow_id="cvel84kg58epjrfkvtb0",
        workspace_id="cuq0pp9s7366bfl0cns0",
        user_id="test",
    )

    resp = await workflow.with_retry().ainvoke(input={"query": "你好"})
    print("ainvoke workflow:", resp)


if __name__ == "__main__":
    invoke_retryable_workflow()

    asyncio.run(ainvoke_retryable_workflow())