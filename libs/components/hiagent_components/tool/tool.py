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
import json
from concurrent.futures import Executor
from typing import Any, Dict, Optional

from hiagent_api.tool import ToolService
from hiagent_api.tool_types import (
    ExecArchivedToolRequest,
    GetArchivedToolRequest,
    GetArchivedToolResponse,
)
from typing_extensions import Self

from hiagent_components.base import Executable
from hiagent_components.tool.base import BaseTool
from hiagent_components.utils.schema import convert_hiagent_schema_to_json_schema


class ExecutableTool(BaseTool):
    def __init__(self, name: str, description: str, executable: Executable):
        self.name = name
        self.description = description
        self.executable = executable

    @property
    def input_schema(self) -> dict[str, Any]:
        return self.executable.input_schema

    @classmethod
    def from_executable(
        cls,
        executable: Executable,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Self:
        if name is None:
            name = executable.name
            if not name:
                name = executable.__class__.__name__

        if description is None:
            description = executable.description

        return cls(
            name=name,
            description=description,
            executable=executable,
        )

    def _invoke(self, input: Dict[str, Any], **kwargs: Any) -> Any:
        return self.executable.invoke(input, **kwargs)

    async def _ainvoke(
        self,
        input: Dict[str, Any],
        executor: Optional[Executor] = None,
        **kwargs: Any,
    ) -> Any:
        return await self.executable.ainvoke(input, executor, **kwargs)


class Tool(BaseTool):
    """
    Tool is a unified encapsulation of tools on the HiAgent platform. You can call a tool by providing the tool ID.
    """

    def __init__(
        self,
        svc: ToolService,
        workspace_id: str,
        plugin_id: str,
        tool_id: str,
        input_schema: dict,
        name:  str,
        description: str,
        credentials: Optional[dict] = None,
    ):
        self.svc = svc
        self.workspace_id = workspace_id
        self.plugin_id = plugin_id
        self.tool_id = tool_id
        self._input_schema = input_schema
        self.name = name
        self.description = description
        self.credentials = credentials

    @property
    def input_schema(self) -> dict[str, Any]:
        return self._input_schema

    @classmethod
    def init(
        cls,
        svc: ToolService,
        workspace_id: str,
        tool_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        credentials: Optional[dict] = None,
    ) -> "Tool":
        resp = svc.get_archived_tool(
            GetArchivedToolRequest(
                workspace_id=workspace_id,
                id=tool_id,
            )
        )
        return cls._init(
            svc=svc,
            workspace_id=workspace_id,
            tool_id=tool_id,
            resp=resp,
            name=name,
            description=description,
            credentials=credentials,
        )

    @classmethod
    async def ainit(
        cls,
        svc: ToolService,
        workspace_id: str,
        tool_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        credentials: Optional[dict] = None,
    ) -> "Tool":
        resp = await svc.aget_archived_tool(
            GetArchivedToolRequest(
                workspace_id=workspace_id,
                id=tool_id,
            )
        )

        return cls._init(
            svc=svc,
            workspace_id=workspace_id,
            tool_id=tool_id,
            resp=resp,
            name=name,
            description=description,
            credentials=credentials,
        )

    @classmethod
    def _init(
        cls,
        svc: ToolService,
        workspace_id: str,
        tool_id: str,
        resp: GetArchivedToolResponse,
        name: Optional[str] = None,
        description: Optional[str] = None,
        credentials: Optional[dict] = None,
    ) -> "Tool":

        if not name:
            name = resp.name
        if not description:
            description = resp.description

        input_schema = {}
        if resp.input_schema and resp.input_schema.sub_parameters:
            input_inner_schema = convert_hiagent_schema_to_json_schema(resp.input_schema.sub_parameters)
            # 参数类型:
            # -1 any, 0 str, 1 int, 2 bool, 3 number,
            # 4 object, 5 array_of_string, 6 array_of_integer, 7 array_of_bool, 8 array_of_number, 9 array_of_object
            # 10 file 11 array_of_file
            if resp.input_schema.type in [4, 10]:
                input_schema = input_inner_schema
            elif resp.input_schema.type in [5, 6, 7, 8, 9, 11]:
                input_schema = {
                    "type": "array",
                    "items": [
                        input_inner_schema,
                    ]
                }
            else:
                raise ValueError("unknown input_schema case")

        return cls(
            svc=svc,
            workspace_id=workspace_id,
            plugin_id=resp.plugin_id,
            tool_id=tool_id,
            input_schema=input_schema,
            name=name,
            description=description,
            credentials=credentials,
        )

    def _invoke(
        self,
        input: dict,
        raise_exception: bool = True,
        **kwargs: Any,
    ) -> str:
        config = ""
        if self.credentials:
            config = json.dumps(self.credentials, ensure_ascii=False)

        resp = self.svc.exec_archived_tool(
            ExecArchivedToolRequest(
                workspace_id=self.workspace_id,
                plugin_id=self.plugin_id,
                tool_id=self.tool_id,
                config=config,
                input_data=json.dumps(input, ensure_ascii=False),
            )
        )

        if not resp.success:
            if raise_exception:
                raise Exception(resp.reason)
            else:
                return resp.reason

        return resp.output

    async def _ainvoke(
        self,
        input: dict,
        raise_exception: bool = True,
        executor: Optional[Executor] = None,
        **kwargs: Any,
    ) -> str:
        config = ""
        if self.credentials:
            config = json.dumps(self.credentials, ensure_ascii=False)

        resp = await self.svc.aexec_archived_tool(
            ExecArchivedToolRequest(
                workspace_id=self.workspace_id,
                plugin_id=self.plugin_id,
                tool_id=self.tool_id,
                config=config,
                input_data=json.dumps(input, ensure_ascii=False),
            )
        )

        if not resp.success:
            if raise_exception:
                raise Exception(resp.reason)
            else:
                return resp.reason
        return resp.output
