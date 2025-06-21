# Copyright (c) 2024 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import asyncio
import os

from dotenv import load_dotenv
from hiagent_api.workflow import WorkflowService
from hiagent_components.workflow.base import BlockingWorkflow, Workflow

load_dotenv()


def get_workflow_svc() -> WorkflowService:
    svc = WorkflowService(
        endpoint=os.getenv("HIAGENT_TOP_ENDPOINT") or "", region="cn-north-1"
    )

    svc.set_app_base_url(os.getenv("HIAGENT_APP_BASE_URL") or "")

    return svc


def invoke_workflow():
    app_key = os.getenv("HIAGENT_APP_KEY") or ""
    workflow = Workflow.init(
        svc=get_workflow_svc(),
        app_key=app_key,
        workflow_id="cvel84kg58epjrfkvtb0",
        workspace_id="cuq0pp9s7366bfl0cns0",
        user_id="test",
    )

    resp = workflow.invoke(input={"query": "你好"})
    print("invoke workflow:", resp)


async def ainvoke_workflow():
    app_key = os.getenv("HIAGENT_APP_KEY") or ""
    workflow = await Workflow.ainit(
        svc=get_workflow_svc(),
        app_key=app_key,
        workflow_id="cvel84kg58epjrfkvtb0",
        workspace_id="cuq0pp9s7366bfl0cns0",
        user_id="test",
    )

    resp = await workflow.ainvoke(input={"query": "你好"})
    print("ainvoke workflow:", resp)


def invoke_blocking_workflow():
    app_key = os.getenv("HIAGENT_APP_KEY") or ""
    workflow = BlockingWorkflow.init(
        svc=get_workflow_svc(),
        app_key=app_key,
        workflow_id="cvel84kg58epjrfkvtb0",
        workspace_id="cuq0pp9s7366bfl0cns0",
        user_id="test",
    )

    resp = workflow.invoke(input={"query": "你好"})
    print("invoke blocking workflow:", resp)


async def ainvoke_blocking_workflow():
    app_key = os.getenv("HIAGENT_APP_KEY") or ""
    workflow = await BlockingWorkflow.ainit(
        svc=get_workflow_svc(),
        app_key=app_key,
        workflow_id="cvel84kg58epjrfkvtb0",
        workspace_id="cuq0pp9s7366bfl0cns0",
        user_id="test",
    )

    resp = await workflow.ainvoke(input={"query": "你好"})
    print("ainvoke blocking workflow:", resp)


async def ainvoke_workflow_as_tool():
    app_key = os.getenv("HIAGENT_APP_KEY") or ""
    workflow = await BlockingWorkflow.ainit(
        svc=get_workflow_svc(),
        app_key=app_key,
        workflow_id="cvel84kg58epjrfkvtb0",
        workspace_id="cuq0pp9s7366bfl0cns0",
        user_id="test",
    )

    tool = workflow.as_tool()
    resp = await tool.ainvoke(input={"query": "你好"})
    print("ainvoke workflow as tool:", resp)


async def get_workflow_input_schema():
    app_key = os.getenv("HIAGENT_APP_KEY") or ""
    workflow = await BlockingWorkflow.ainit(
        svc=get_workflow_svc(),
        app_key=app_key,
        workflow_id="cvel84kg58epjrfkvtb0",
        workspace_id="cuq0pp9s7366bfl0cns0",
        user_id="test",
    )
    print(workflow.input_schema)


if __name__ == "__main__":
    asyncio.run(get_workflow_input_schema())

    asyncio.run(ainvoke_workflow_as_tool())

    invoke_workflow()

    asyncio.run(ainvoke_workflow())

    invoke_blocking_workflow()

    asyncio.run(ainvoke_blocking_workflow())

    asyncio.run(ainvoke_workflow_as_tool())
