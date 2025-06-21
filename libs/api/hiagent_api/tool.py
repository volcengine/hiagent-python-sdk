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
from urllib.parse import urlparse

from volcengine.ApiInfo import ApiInfo
from volcengine.Credentials import Credentials
from volcengine.ServiceInfo import ServiceInfo

from hiagent_api import tool_types
from hiagent_api.base import AppAPIMixin, Service


class ToolService(Service, AppAPIMixin):
    def __init__(self, endpoint="https://open.volcengineapi.com", region="cn-north-1"):
        self.service_info = ToolService.get_service_info(endpoint, region)
        self.api_info = ToolService.get_api_info()
        super().__init__(self.service_info, self.api_info)
        AppAPIMixin.__init__(self, self.http_client, self.async_http_client)

    @staticmethod
    def get_service_info(endpoint: str, region: str):
        parsed = urlparse(endpoint)
        scheme, hostname = parsed.scheme, parsed.hostname + ":" + str(parsed.port)
        if not scheme or not hostname:
            raise Exception(f"invalid endpoint format: {endpoint}")
        service_info = ServiceInfo(
            hostname,
            {"Accept": "application/json"},
            Credentials("", "", "app", region),
            connection_timeout=5,
            socket_timeout=5 * 60,
            scheme=scheme,
        )
        return service_info

    @staticmethod
    def get_api_info():
        api_info = {
            "GetArchivedTool": ApiInfo(
                "POST",
                "/",
                {
                    "Action": "GetArchivedTool",
                    "Version": "2023-08-01",
                },
                {},
                {},
            ),
            "ExecArchivedTool": ApiInfo(
                "POST",
                "/",
                {
                    "Action": "ExecArchivedTool",
                    "Version": "2023-08-01",
                },
                {},
                {},
            ),
        }
        return api_info

    def get_archived_tool(
        self, params: tool_types.GetArchivedToolRequest
    ) -> tool_types.GetArchivedToolResponse:
        """获取 tool 详情
        Args:
            params: GetArchivedToolRequest
        Returns:
            GetArchivedToolResponse
        """
        return tool_types.GetArchivedToolResponse.model_validate(
            self._request("GetArchivedTool", params.model_dump(by_alias=True)),
            by_alias=True,
        )

    async def aget_archived_tool(
        self, params: tool_types.GetArchivedToolRequest
    ) -> tool_types.GetArchivedToolResponse:
        """获取 tool 详情
        Args:
            params: GetArchivedToolRequest
        Returns:
            GetArchivedToolResponse
        """
        resp = await self._arequest("GetArchivedTool", params.model_dump(by_alias=True))
        return tool_types.GetArchivedToolResponse.model_validate(
            resp,
            by_alias=True,
        )

    def exec_archived_tool(
        self, params: tool_types.ExecArchivedToolRequest
    ) -> tool_types.ExecArchivedToolResponse:
        """运行 tool
        Args:
            params: ExecArchivedToolRequest
        Returns:
            ExecArchivedToolResponse
        """
        return tool_types.ExecArchivedToolResponse.model_validate(
            self._request("ExecArchivedTool", params.model_dump(by_alias=True)),
            by_alias=True,
        )

    async def aexec_archived_tool(
        self, params: tool_types.ExecArchivedToolRequest
    ) -> tool_types.ExecArchivedToolResponse:
        """运行 tool
        Args:
            params: RunWorkflowRequest
        Returns:
            RunWorkflowResponse
        """
        return tool_types.ExecArchivedToolResponse.model_validate(
            await self._arequest("ExecArchivedTool", params.model_dump(by_alias=True)),
            by_alias=True,
        )
