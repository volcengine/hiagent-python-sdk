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

from hiagent_api import workflow_types
from hiagent_api.base import AppAPIMixin, Service


class WorkflowService(Service, AppAPIMixin):
    def __init__(self, endpoint="https://open.volcengineapi.com", region="cn-north-1"):
        self.service_info = WorkflowService.get_service_info(endpoint, region)
        self.api_info = WorkflowService.get_api_info()
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
            "GetWorkflow": ApiInfo(
                "POST",
                "/",
                {
                    "Action": "GetWorkflow",
                    "Version": "2023-08-01",
                },
                {},
                {},
            )
        }
        return api_info

    def get_workflow(
        self, params: workflow_types.GetWorkflowRequest
    ) -> workflow_types.GetWorkflowResponse:
        """获取 workflow 详情
        Args:
            params: GetWorkflowRequest
        Returns:
            GetWorkflowResponse
        """
        return workflow_types.GetWorkflowResponse.model_validate(
            self._request("GetWorkflow", params.model_dump(by_alias=True)),
            by_alias=True,
        )

    async def aget_workflow(
        self, params: workflow_types.GetWorkflowRequest
    ) -> workflow_types.GetWorkflowResponse:
        """获取 workflow 详情
        Args:
            params: GetWorkflowRequest
        Returns:
            GetWorkflowResponse
        """
        return workflow_types.GetWorkflowResponse.model_validate(
            await self._arequest("GetWorkflow", params.model_dump(by_alias=True)),
            by_alias=True,
        )

    def run_workflow(
        self, app_key: str, params: workflow_types.RunWorkflowRequest
    ) -> workflow_types.RunWorkflowResponse:
        """同步运行 workflow
        Args:
            app_key: app key
            params: RunWorkflowRequest
        Returns:
            RunWorkflowResponse
        """
        res = self._post(
            app_key, "sync_run_app_workflow", params.model_dump(by_alias=True)
        )

        return workflow_types.RunWorkflowResponse.model_validate_json(
            res, by_alias=True
        )

    async def arun_workflow(
        self, app_key: str, params: workflow_types.RunWorkflowRequest
    ) -> workflow_types.RunWorkflowResponse:
        """同步运行 workflow
        Args:
            params: RunWorkflowRequest
        Returns:
            RunWorkflowResponse
        """
        res = await self._apost(
            app_key, "sync_run_app_workflow", params.model_dump(by_alias=True)
        )
        return workflow_types.RunWorkflowResponse.model_validate_json(
            res, by_alias=True
        )

    def run_workflow_async(
        self, app_key: str, params: workflow_types.RunWorkflowRequest
    ) -> workflow_types.AsyncRunWorkflowResponse:
        """异步运行 workflow
        Args:
            params: RunWorkflowRequest
        Returns:
            AsyncRunWorkflowResponse
        """
        res = self._post(app_key, "run_app_workflow", params.model_dump(by_alias=True))
        return workflow_types.AsyncRunWorkflowResponse.model_validate_json(
            res, by_alias=True
        )

    async def arun_workflow_async(
        self, app_key: str, params: workflow_types.RunWorkflowRequest
    ) -> workflow_types.AsyncRunWorkflowResponse:
        """异步运行 workflow
        Args:
            params: RunWorkflowRequest
        Returns:
            AsyncRunWorkflowResponse
        """
        res = await self._apost(
            app_key, "run_app_workflow", params.model_dump(by_alias=True)
        )
        return workflow_types.AsyncRunWorkflowResponse.model_validate_json(
            res, by_alias=True
        )

    def query_workflow_status(
        self, app_key: str, params: workflow_types.QueryWorkflowStatusRequest
    ) -> workflow_types.RunWorkflowResponse:
        """查询 workflow 运行状态
        Args:
            params: QueryWorkflowStatusRequest
        Returns:
            RunWorkflowResponse
        """
        res = self._post(
            app_key, "query_run_app_process", params.model_dump(by_alias=True)
        )
        return workflow_types.RunWorkflowResponse.model_validate_json(
            res, by_alias=True
        )

    async def aquery_workflow_status(
        self, app_key: str, params: workflow_types.QueryWorkflowStatusRequest
    ) -> workflow_types.RunWorkflowResponse:
        """查询 workflow 运行状态
        Args:
            params: QueryWorkflowStatusRequest
        Returns:
            RunWorkflowResponse
        """
        res = await self._apost(
            app_key, "query_run_app_process", params.model_dump(by_alias=True)
        )
        return workflow_types.RunWorkflowResponse.model_validate_json(
            res, by_alias=True
        )
