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

from hiagent_api.base import Service
from hiagent_api.knowledgebase_types import QueryRequest, QueryResponse


class KnowledgebaseService(Service):
    def __init__(self, endpoint="https://open.volcengineapi.com", region="cn-north-1"):
        self.service_info = KnowledgebaseService.get_service_info(endpoint, region)
        self.api_info = KnowledgebaseService.get_api_info()
        super().__init__(self.service_info, self.api_info)

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
            socket_timeout=30,
            scheme=scheme,
        )
        return service_info

    @staticmethod
    def get_api_info():
        api_info = {
            "Query": ApiInfo(
                "POST",
                "/",
                {
                    "Action": "Query",
                    "Version": "2023-08-01",
                },
                {},
                {},
            )
        }
        return api_info

    def query(self, params: QueryRequest) -> QueryResponse:
        """
        检索知识库
        Args:
            params: QueryRequest
        Returns:
            QueryResponse
        """
        return QueryResponse.model_validate(
            self._request("Query", params.model_dump(by_alias=True, exclude_none=True)),
            by_alias=True,
        )

    async def aquery(self, params: QueryRequest) -> QueryResponse:
        """
        检索知识库
        Args:
            params: QueryRequest
        Returns:
            QueryResponse
        """
        return QueryResponse.model_validate(
            await self._arequest(
                "Query", params.model_dump(by_alias=True, exclude_none=True)
            ),
            by_alias=True,
        )
