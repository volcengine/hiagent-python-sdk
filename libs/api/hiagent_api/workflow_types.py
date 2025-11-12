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
from typing import Optional

from pydantic import Field

from hiagent_api.base import BaseSchema


class GetWorkflowRequest(BaseSchema):
    id: str = Field(
        description="工作流 id",
        serialization_alias="ID",
    )
    workspace_id: str = Field(
        description="工作空间 id",
        serialization_alias="WorkspaceID",
    )


class FieldDefinition(BaseSchema):
    name: str = Field(
        description="参数名",
        validation_alias="Name",
    )
    desc: Optional[str] = Field(
        default=None,
        description="参数描述",
        validation_alias="Desc",
    )
    required: Optional[bool] = Field(
        default=None,
        description="参数是否必填",
        validation_alias="Required",
    )
    type: int = Field(
        description="参数类型, -1 any, 0 str, 1 int, 2 bool, 3 number, 4 object, 5 array_of_string, 6 array_of_integer, 7 array_of_bool, 8 array_of_number, 9 array_of_object, 10 file 11 array_of_file",
        validation_alias="Type",
    )
    default: Optional[str] = Field(
        default=None,
        description="默认值",
        validation_alias="Default",
    )
    sub_parameters: Optional[list["FieldDefinition"]] = Field(
        default=None,
        description="子参数,如果类型是 Object 或 Array<Object> 则可以配置 SubParameters",
        validation_alias="SubParameters",
    )


class StartNodeConfig(BaseSchema):
    input_schema: list[FieldDefinition] = Field(
        default_factory=list,
        description="输入参数",
        validation_alias="InputSchema",
    )


class NodeConfig(BaseSchema):
    """
    NodeConfig 有很多字段，目前只关注开始节点的配置，通过开始节点可以获取到 workflow 的 input schema
    """

    start_node: Optional[StartNodeConfig] = Field(
        default=None,
        description="开始节点配置",
        validation_alias="StartNode",
    )


class Node(BaseSchema):
    id: str = Field(
        description="节点 ID",
        validation_alias="ID",
    )

    flow_id: str = Field(
        description="工作流 ID",
        validation_alias="FlowID",
    )

    type: str = Field(
        description="节点类型, Start, End ...",
        validation_alias="Type",
    )

    name: str = Field(
        description="节点名称",
        validation_alias="Name",
    )

    node_config: Optional[NodeConfig] = Field(
        default=None,
        description="节点配置",
        validation_alias="NodeConfig",
    )


class GetWorkflowResponse(BaseSchema):
    name: str = Field(
        description="工作流名称",
        validation_alias="Name",
    )

    description: str = Field(
        description="描述",
        validation_alias="Description",
    )

    status: str = Field(
        description="状态，值为 Published 和 Unpublished",
        validation_alias="Status",
    )

    runtime_status: str = Field(
        description="流水线运行状态，Init, Running, Failed, Succeed",
        validation_alias="RuntimeStatus",
    )

    run_id: Optional[str] = Field(
        description="上一次运行状态，如果没有则返回为空",
        validation_alias="runId",
        default=None,
    )

    nodes: list[Node] = Field(
        description="工作流节点",
        validation_alias="Nodes",
    )


class RunWorkflowRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    input_data: str = Field(
        description="输入参数",
        serialization_alias="InputData",
    )
    user_id: str = Field(
        description="用户 id",
        serialization_alias="UserID",
    )
    no_debug: bool = Field(
        default=True,
        description="是否不调试",
        serialization_alias="NoDebug",
    )


class RunWorkflowResponse(BaseSchema):
    run_id: str = Field(
        description="运行 id",
        validation_alias="runId",
    )
    status: str = Field(
        description="运行状态, success, stopped, failed, interrupted, processing",
    )
    output: str = Field(description="end 节点的输出，是一个 json 字符串")
    cost_ms: int = Field(description="耗时", validation_alias="costMs", default=0)


class AsyncRunWorkflowResponse(BaseSchema):
    run_id: str = Field(description="运行 id", validation_alias="runId")


class QueryWorkflowStatusRequest(BaseSchema):
    run_id: str = Field(
        description="运行 id",
        serialization_alias="RunID",
    )
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )
