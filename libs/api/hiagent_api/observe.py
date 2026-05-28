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
from volcengine.auth.SignerV4 import SignerV4
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
            300,
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
            "TraceAIProcess": ApiInfo(
                "POST",
                "/",
                {"Action": "TraceAIProcess", "Version": "2025-05-01"},
                {},
                {},
            ),
            "GetTraceAIProcessHistory": ApiInfo(
                "POST",
                "/",
                {"Action": "GetTraceAIProcessHistory", "Version": "2025-05-01"},
                {},
                {},
            ),
            "AlertAIProcess": ApiInfo(
                "POST",
                "/",
                {"Action": "AlertAIProcess", "Version": "2025-05-01"},
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
        if hasattr(params, "model_dump"):
            params = params.model_dump()
        return observe_types.CreateApiTokenResponse.model_validate(
            self.__request("CreateApiToken", params)
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
        if hasattr(params, "model_dump"):
            params = params.model_dump()
        if isinstance(params, dict) and params.get("LastID", None) == "":
            params.pop("LastID", None)
        return observe_types.ListTraceSpansResponse.model_validate(
            self.__request("ListTraceSpans", params)
        )

    def TraceAIProcess(self, params, on_event=None):
        if bool(params.get("IsStream")):
            return self.__stream_request("TraceAIProcess", params, on_event=on_event)
        return self.__request("TraceAIProcess", params)

    def GetTraceAIProcessHistory(
        self, params: observe_types.GetTraceAIProcessHistoryRequest
    ) -> observe_types.GetTraceAIProcessHistoryResponse:
        """获取 trace AI 分析历史

        Args:
            params (Dict):

                `WorkspaceID (str)`: 必选, 工作空间 ID

                `TraceID (str)`: 必选, trace ID

                `PageSize (int)`: 可选, 单页数量

        Returns:
            Dict:

                `Items (List[TraceSpanItem])`: trace span 列表

        """
        if hasattr(params, "model_dump"):
            params = params.model_dump()
        return observe_types.GetTraceAIProcessHistoryResponse.model_validate(
            self.__request("GetTraceAIProcessHistory", params)
        )

    def AlertAIProcess(self, params, on_event=None):
        if bool(params.get("IsStream")):
            return self.__stream_request("AlertAIProcess", params, on_event=on_event)
        return self.__request("AlertAIProcess", params)

    def __request(self, action, params):
        res = self.json(action, dict(), json.dumps(params))
        if res == "":
            raise Exception("empty response")
        res_json = json.loads(res)
        if "Result" not in res_json.keys():
            return res_json
        return res_json["Result"]

    def __stream_request(self, action, params, on_event=None):
        """Send a streaming (SSE) request and aggregate it into the final
        AIProcessResponse-shaped dict produced by the server-side `done` event.
        Falls back to aggregating delta events if `done` is missing.
        """
        if action not in self.api_info:
            raise Exception("no such api")
        api_info = self.api_info[action]
        body = json.dumps(params)
        r = self.prepare_request(api_info, dict())
        r.headers["Content-Type"] = "application/json"
        r.headers["Accept"] = "text/event-stream"
        r.body = body
        SignerV4.sign(r, self.service_info.credentials)
        url = r.build()
        with self.session.post(
            url,
            headers=r.headers,
            data=r.body,
            stream=True,
            timeout=(self.service_info.connection_timeout, self.service_info.socket_timeout),
        ) as resp:
            if resp.status_code != 200:
                raise Exception(resp.text.encode("utf-8"))

            final = None
            content_parts = []
            reasoning_parts = []
            err_message = None
            event = ""
            data_buf = []

            def handle_event(event_name, data_str):
                nonlocal final, err_message
                if not event_name and not data_str:
                    return
                payload = None
                if data_str:
                    try:
                        payload = json.loads(data_str)
                    except json.JSONDecodeError:
                        payload = data_str
                if on_event is not None:
                    try:
                        on_event(event_name, payload)
                    except Exception:
                        # 回调异常不应影响主流程
                        pass
                if event_name == "done":
                    if isinstance(payload, dict):
                        final = payload
                elif event_name == "content":
                    if isinstance(payload, dict) and payload.get("content"):
                        content_parts.append(payload["content"])
                elif event_name == "reasoning":
                    if isinstance(payload, dict) and payload.get("reasoning_content"):
                        reasoning_parts.append(payload["reasoning_content"])
                elif event_name == "error":
                    if isinstance(payload, dict):
                        err_message = payload.get("err_message") or json.dumps(payload)

            for raw_line in resp.iter_lines(decode_unicode=True):
                if raw_line is None:
                    continue
                if raw_line == "":
                    handle_event(event, "\n".join(data_buf))
                    event = ""
                    data_buf = []
                    continue
                if raw_line.startswith(":"):
                    continue
                if raw_line.startswith("event:"):
                    event = raw_line[len("event:"):].strip()
                elif raw_line.startswith("data:"):
                    data_buf.append(raw_line[len("data:"):].lstrip())

            if event or data_buf:
                handle_event(event, "\n".join(data_buf))

            if final is not None:
                return final
            if err_message is not None:
                raise Exception(err_message)
            return {
                "content": "".join(content_parts),
                "reasoning_content": "".join(reasoning_parts),
            }
