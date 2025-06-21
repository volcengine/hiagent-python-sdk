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
import json
import time
from concurrent.futures import Executor
from typing import Any, Optional

from hiagent_api.workflow import WorkflowService
from hiagent_api.workflow_types import (
    GetWorkflowRequest,
    QueryWorkflowStatusRequest,
    RunWorkflowRequest,
)
from strenum import StrEnum

from hiagent_components.base import Executable
from hiagent_components.utils.schema import (
    convert_hiagent_schema_to_json_schema,
)
from hiagent_components.workflow.utils import get_start_node_of_workflow


class WorkflowStatus(StrEnum):
    TO_START = "to_start"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    INTERRUPTED = "interrupted"
    STOPPED = "stopped"


WorkflowCompleteStatus = [
    WorkflowStatus.SUCCESS,
    WorkflowStatus.FAILED,
    WorkflowStatus.INTERRUPTED,
    WorkflowStatus.STOPPED,
]


class Workflow(Executable):
    def __init__(
        self,
        svc: WorkflowService,
        app_key: str,
        user_id: str,
        input_schema: dict,
        name: str,
        description: str,
    ) -> None:
        self.svc = svc
        self.app_key = app_key
        self.user_id = user_id
        self.name = name or ""
        self.description = description or ""
        self._input_schema = input_schema

    @property
    def input_schema(self) -> dict:
        return self._input_schema

    @classmethod
    def init(
        cls,
        svc: WorkflowService,
        app_key: str,
        workspace_id: str,
        workflow_id: str,
        user_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> "Workflow":
        """get workflow and init it's name, description and input schema.
        if name is None, fetch workflow name as name.
        if description is None, fetch workflow description as description.
        """
        resp = svc.get_workflow(
            GetWorkflowRequest(
                id=workflow_id,
                workspace_id=workspace_id,
            )
        )
        if not name:
            name = resp.name
        if not description:
            description = resp.description

        start_node = get_start_node_of_workflow(resp)
        if start_node is None:
            raise ValueError("workflow has no start node")

        if start_node.node_config is None or start_node.node_config.start_node is None:
            raise ValueError("workflow start node config is None")

        input_schema = convert_hiagent_schema_to_json_schema(
            start_node.node_config.start_node.input_schema
        )

        workflow = cls(
            svc=svc,
            app_key=app_key,
            user_id=user_id,
            input_schema=input_schema,
            name=name,
            description=description,
        )

        return workflow

    @classmethod
    async def ainit(
        cls,
        svc: WorkflowService,
        app_key: str,
        workspace_id: str,
        workflow_id: str,
        user_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> "Workflow":
        """get workflow and init it's name, description and input schema.
        if name is None, fetch workflow name as name.
        if description is None, fetch workflow description as description.
        """
        resp = await svc.aget_workflow(
            GetWorkflowRequest(
                id=workflow_id,
                workspace_id=workspace_id,
            )
        )
        if not name:
            name = resp.name
        if not description:
            description = resp.description

        start_node = get_start_node_of_workflow(resp)
        if start_node is None:
            raise ValueError("workflow has no start node")

        if start_node.node_config is None or start_node.node_config.start_node is None:
            raise ValueError("workflow start node config is None")

        input_schema = convert_hiagent_schema_to_json_schema(
            start_node.node_config.start_node.input_schema
        )

        workflow = cls(
            svc=svc,
            app_key=app_key,
            user_id=user_id,
            input_schema=input_schema,
            name=name,
            description=description,
        )

        return workflow

    def invoke(self, input: dict, **kwargs: Any) -> str:
        resp = self.svc.run_workflow_async(
            self.app_key,
            RunWorkflowRequest(
                input_data=json.dumps(input, ensure_ascii=False),
                user_id=self.user_id,
                app_key=self.app_key,
            ),
        )
        run_id = resp.run_id
        while True:
            resp = self.svc.query_workflow_status(
                self.app_key,
                QueryWorkflowStatusRequest(
                    app_key=self.app_key,
                    run_id=run_id,
                    user_id=self.user_id,
                ),
            )
            if resp.status in WorkflowCompleteStatus:
                if resp.status == WorkflowStatus.SUCCESS:
                    return resp.output
                else:
                    raise Exception(f"workflow completed with status {resp.status}")
            time.sleep(1)

    async def ainvoke(
        self, input: dict, executor: Optional[Executor] = None, **kwargs: Any
    ) -> str:
        resp = await self.svc.arun_workflow_async(
            self.app_key,
            RunWorkflowRequest(
                input_data=json.dumps(input, ensure_ascii=False),
                user_id=self.user_id,
                app_key=self.app_key,
            ),
        )
        run_id = resp.run_id
        while True:
            resp = await self.svc.aquery_workflow_status(
                self.app_key,
                QueryWorkflowStatusRequest(
                    app_key=self.app_key,
                    run_id=run_id,
                    user_id=self.user_id,
                ),
            )
            if resp.status in WorkflowCompleteStatus:
                if resp.status == WorkflowStatus.SUCCESS:
                    return resp.output
                else:
                    raise Exception(f"workflow completed with status {resp.status}")
            await asyncio.sleep(1)


class BlockingWorkflow(Workflow):
    def invoke(self, input: dict, **kwargs: Any) -> str:
        resp = self.svc.run_workflow(
            self.app_key,
            RunWorkflowRequest(
                app_key=self.app_key,
                input_data=json.dumps(input, ensure_ascii=False),
                user_id=self.user_id,
            ),
        )
        if resp.status == WorkflowStatus.SUCCESS:
            return resp.output
        else:
            raise Exception(f"workflow completed with status {resp.status}")

    async def ainvoke(
        self, input: dict, executor: Optional[Executor] = None, **kwargs: Any
    ) -> str:
        resp = await self.svc.arun_workflow(
            self.app_key,
            RunWorkflowRequest(
                app_key=self.app_key,
                input_data=json.dumps(input, ensure_ascii=False),
                user_id=self.user_id,
            ),
        )
        if resp.status == WorkflowStatus.SUCCESS:
            return resp.output
        else:
            raise Exception(f"workflow completed with status {resp.status}")
