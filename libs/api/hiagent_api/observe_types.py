# coding:utf-8
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
from pydantic import BaseModel, Field


class CreateApiTokenRequest(BaseModel):
    WorkspaceID: str = Field(
        title="工作空间 ID",
        description="工作空间 ID",
        example="wcxxxxxxxxxxxxxxxxxxx"
    )
    CustomAppID: str = Field(
        title="自定义应用 ID",
        description="自定义应用 ID",
        example="appxxxxxxxxxxxxxxxxxxx"
    )


class CreateApiTokenResponse(BaseModel):
    Token: str = Field(
        title="API Token",
        description="API Token",
        example="wcxxxxxxxxxxxxxxxxxxx"
    )
    ExpiresIn: int = Field(
        title="有效时间",
        description="有效时间，单位为秒",
        example=3600
    )
