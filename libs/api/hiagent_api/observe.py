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
import json
import threading
from urllib.parse import urlparse

from volcengine.ApiInfo import ApiInfo
from volcengine.base.Service import Service
from volcengine.Credentials import Credentials
from volcengine.ServiceInfo import ServiceInfo

from hiagent_api import observe_types


class ObserveService(Service):
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(ObserveService, "_instance"):
            with ObserveService._instance_lock:
                if not hasattr(ObserveService, "_instance"):
                    ObserveService._instance = object.__new__(cls)
        return ObserveService._instance

    def __init__(self, endpoint="https://open.volcengineapi.com", region="cn-north-1"):
        self.service_info = ObserveService.get_service_info(endpoint, region)
        self.api_info = ObserveService.get_api_info()
        super(ObserveService, self).__init__(self.service_info, self.api_info)

    @staticmethod
    def get_service_info(endpoint, region):
        parsed = urlparse(endpoint)
        scheme, hostname = parsed.scheme, parsed.hostname + ":" + str(parsed.port)
        if not scheme or not hostname:
            raise Exception(f"invalid endpoint format: {endpoint}")
        service_info = ServiceInfo(
            hostname,
            {"Accept": "application/json"},
            Credentials("", "", "observe", region),
            5,
            5,
            scheme=scheme,
        )
        return service_info

    @staticmethod
    def get_api_info():
        api_info = {
            "CreateApiToken": ApiInfo(
                "POST",
                "/",
                {"Action": "CreateApiToken", "Version": "2025-05-01"},
                {},
                {},
            ),
            "ListTraceSpans": ApiInfo(
                "POST",
                "/",
                {"Action": "ListTraceSpans", "Version": "2025-05-01"},
                {},
                {},
            ),
        }
        return api_info

    def CreateApiToken(
        self, params: observe_types.CreateApiTokenRequest
    ) -> observe_types.CreateApiTokenResponse:
        """创建 api token

        Args:
            params (Dict):

                `WorkspaceID (str)`: 必选, 工作空间 ID
                    示例值: wcxxxxxxxxxxxxxxxxxxx

                `CustomAppID (str)`: 必选, 自定义应用 ID
                    示例值: appxxxxxxxxxxxxxxxxxxx

        Returns:
            Dict:

                `Token (str)`: token
                    示例值: wcxxxxxxxxxxxxxxxxxxx

                `ExpiresIn (int)`: 有效时间，单位为秒
                    示例值: 3600

        """
        return observe_types.CreateApiTokenResponse.model_validate(
            self.__request("CreateApiToken", params.model_dump())
        )

    def ListTraceSpans(
        self, params: observe_types.ListTraceSpansRequest
    ) -> observe_types.ListTraceSpansResponse:
        """
        获取 trace spans

        Args:
            params (observe_types.CreateApiTokenRequest):

        Raises:
            Exception:

        Returns:
            Dict:

        """
        return observe_types.ListTraceSpansResponse.model_validate(
            self.__request("ListTraceSpans", params)
        )

    def __request(self, action, params):
        res = self.json(action, dict(), json.dumps(params))
        if res == "":
            raise Exception("empty response")
        res_json = json.loads(res)
        if "Result" not in res_json.keys():
            return res_json
        return res_json["Result"]
