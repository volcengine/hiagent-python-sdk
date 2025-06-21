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
from hiagent_api.workflow_types import FieldDefinition


class GetArchivedToolRequest(BaseSchema):
    workspace_id: str = Field(
        description="工作空间 id",
        serialization_alias="WorkspaceID"
    )
    id: str = Field(
        description="工具 id",
        serialization_alias="ID"
    )

class GetArchivedToolResponse(BaseSchema):
    plugin_id: str = Field(
        description="工具所属插件 id",
        validation_alias="PluginID"
    )
    name: str = Field(
        description="工具名称",
        validation_alias="Name"
    )
    description: str = Field(
        description="工具描述",
        validation_alias="Description"
    )
    input_schema: Optional[FieldDefinition] = Field(
        default=None,
        description="输入参数的 schema",
        validation_alias="InputSchema"
    )

class ExecArchivedToolRequest(BaseSchema):
    workspace_id: str = Field(
        description="工作空间 id",
        serialization_alias="WorkspaceID"
    )
    plugin_id: str = Field(
        description="工具所属插件 id",
        serialization_alias="PluginID"
    )
    tool_id: str = Field(
        description="工具 id",
        serialization_alias="ToolID"
    )
    config: str = Field(
        description="插件临时授权信息, 如果不填, 则使用插件授权信息",
        serialization_alias="Config",
    )
    input_data: str = Field(
        description="输入json",
        serialization_alias="InputData"
    )

class ExecArchivedToolResponse(BaseSchema):
    output: str = Field(
        description="工具运行的输出",
        validation_alias="Output"
    )
    success: bool = Field(
        description="是否调试成功",
        validation_alias="Success"
    )
    reason: str = Field(
        description="失败的原因",
        validation_alias="Reason"
    )
