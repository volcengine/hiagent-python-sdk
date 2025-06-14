# coding:utf-8
import json
import logging
import threading
from urllib.parse import urlparse

from volcengine.ApiInfo import ApiInfo
from volcengine.base.Service import Service
from volcengine.Credentials import Credentials
from volcengine.ServiceInfo import ServiceInfo

from . import types


class EvaService(Service):
    _instance_lock = threading.Lock()
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = object.__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        endpoint="https://open.volcengineapi.com",
        region="cn-north-1",
        ak="",
        sk="",
    ):
        if self._initialized:
            return

        self.endpoint = endpoint
        self.region = region
        self.ak = ak
        self.sk = sk

        # Keep consistent with observe: create service first with empty AK/SK
        self.service_info = EvaService.get_service_info(endpoint, region, "", "")
        self.api_info = EvaService.get_api_info()
        super(EvaService, self).__init__(self.service_info, self.api_info)

        # Critical fix: keep consistent with observe - use set_ak/set_sk methods to set credentials
        if ak:
            self.set_ak(ak)
        if sk:
            self.set_sk(sk)

        self._initialized = True

    @staticmethod
    def get_service_info(endpoint, region, ak="", sk=""):
        parsed = urlparse(endpoint)
        scheme = parsed.scheme
        if not scheme:
            raise Exception(f"invalid endpoint format: {endpoint}")

        # Fix observe's port handling bug while maintaining consistent architecture
        hostname = parsed.hostname
        if not hostname:
            raise Exception(f"invalid endpoint format: {endpoint}")

        # Robust port handling: only add port when it actually exists
        if parsed.port:
            hostname = f"{hostname}:{parsed.port}"
        # Don't append ":None", this was observe's bug

        # Completely consistent with observe - use empty AK/SK to create Credentials
        service_info = ServiceInfo(
            hostname,
            {"Accept": "application/json"},
            Credentials("", "", service="eva", region=region),  # Empty AK/SK!
            5,
            5,
            scheme=scheme,
        )
        return service_info

    @staticmethod
    def get_api_info():
        api_info = {
            "CreateEvaTask": ApiInfo(
                "POST",
                "/",
                {"Action": "CreateEvaTask", "Version": "2025-02-01"},
                {},
                {},
            ),
            "ListEvaDatasetConversations": ApiInfo(
                "POST",
                "/",
                {"Action": "ListEvaDatasetConversations", "Version": "2025-02-01"},
                {},
                {},
            ),
            "ListEvaDatasetColumns": ApiInfo(
                "POST",
                "/",
                {"Action": "ListEvaDatasetColumns", "Version": "2025-02-01"},
                {},
                {},
            ),
            "ExecEvaTaskRowGroup": ApiInfo(
                "POST",
                "/",
                {"Action": "ExecEvaTaskRowGroup", "Version": "2025-02-01"},
                {},
                {},
            ),
            "GetEvaTaskReport": ApiInfo(
                "POST",
                "/",
                {"Action": "GetEvaTaskReport", "Version": "2025-02-01"},
                {},
                {},
            ),
            "GetEvaTask": ApiInfo(
                "POST",
                "/",
                {"Action": "GetEvaTask", "Version": "2025-02-01"},
                {},
                {},
            ),
        }
        return api_info

    def CreateEvaTask(
        self, params: types.CreateEvaTaskRequest
    ) -> types.CreateEvaTaskResponse:
        """Create evaluation task

        Args:
            params: Create evaluation task request parameters

        Returns:
            CreateEvaTaskResponse: Created evaluation task information
        """
        return types.CreateEvaTaskResponse.model_validate(
            self.__request("CreateEvaTask", params.model_dump())
        )

    def ListEvaDatasetConversations(
        self, params: types.ListEvaDatasetConversationsRequest
    ) -> types.ListEvaDatasetConversationsResponse:
        """Get paginated evaluation dataset conversation list

        Args:
            params: Get dataset conversation list request parameters

        Returns:
            ListEvaDatasetConversationsResponse: Dataset conversation list response
        """
        return types.ListEvaDatasetConversationsResponse.model_validate(
            self.__request("ListEvaDatasetConversations", params.model_dump())
        )

    def ListEvaDatasetColumns(
        self, params: types.ListEvaDatasetColumnsRequest
    ) -> types.ListEvaDatasetColumnsResponse:
        """Get evaluation dataset column information

        Args:
            params: Get dataset column information request parameters

        Returns:
            ListEvaDatasetColumnsResponse: Dataset column information response
        """
        return types.ListEvaDatasetColumnsResponse.model_validate(
            self.__request("ListEvaDatasetColumns", params.model_dump())
        )

    def ExecEvaTaskRowGroup(
        self, params: types.ExecEvaTaskRowGroupRequest
    ) -> types.ExecEvaTaskRowGroupResponse:
        """Submit evaluation task inference results

        Args:
            params: Submit inference results request parameters

        Returns:
            ExecEvaTaskRowGroupResponse: Submission result response
        """
        return types.ExecEvaTaskRowGroupResponse.model_validate(
            self.__request("ExecEvaTaskRowGroup", params.model_dump())
        )

    def GetEvaTaskReport(
        self, params: types.GetEvaTaskReportRequest
    ) -> types.GetEvaTaskReportResponse:
        """Get evaluation task report

        Args:
            params: Get evaluation report request parameters

        Returns:
            GetEvaTaskReportResponse: Evaluation report response
        """
        return types.GetEvaTaskReportResponse.model_validate(
            self.__request("GetEvaTaskReport", params.model_dump())
        )

    def GetEvaTask(self, request: types.GetEvaTaskRequest) -> types.GetEvaTaskResponse:
        """Get evaluation task details

        Args:
            request: Get evaluation task details request parameters

        Returns:
            GetEvaTaskResponse: Evaluation task details response
        """
        return types.GetEvaTaskResponse.model_validate(
            self.__request("GetEvaTask", request.model_dump())
        )

    def CreateEvaRuleset(
        self, params: types.CreateEvaRulesetRequest
    ) -> types.CreateEvaRulesetResponse:
        """
        Create evaluation ruleset

        Args:
            params: Create evaluation ruleset request parameters

        Returns:
            CreateEvaRulesetResponse: Create evaluation ruleset response
        """
        return types.CreateEvaRulesetResponse.model_validate(
            self.__request("CreateEvaRuleset", params.model_dump())
        )

    def ListEvaRulesets(
        self, params: types.ListEvaRulesetsRequest
    ) -> types.ListEvaRulesetsResponse:
        """
        Get evaluation ruleset list

        Args:
            params: Get evaluation ruleset list request parameters

        Returns:
            ListEvaRulesetsResponse: Evaluation ruleset list response
        """
        return types.ListEvaRulesetsResponse.model_validate(
            self.__request("ListEvaRulesets", params.model_dump())
        )

    def __request(self, action, params):
        import time

        logger = logging.getLogger(__name__)

        logger.debug(f"API Request - Action: {action}")
        logger.debug(f"Host: {self.service_info.host}")
        logger.debug(f"Region: {self.service_info.credentials.region}")

        # Construct complete URL
        api_info = self.api_info.get(action)
        if api_info:
            query_params = api_info.query.copy()
            query_string = "&".join([f"{k}={v}" for k, v in query_params.items()])
            full_url = f"{self.service_info.scheme}://{self.service_info.host}{api_info.path}?{query_string}"
            logger.debug(f"Method: {api_info.method}, URL: {full_url}")

        logger.debug(f"Params: {json.dumps(params, ensure_ascii=False)}")

        try:
            logger.debug("Sending HTTP request")
            start_time = time.time()

            res = self.json(action, dict(), json.dumps(params))

            end_time = time.time()

            logger.debug(f"Request completed in {end_time - start_time:.3f}s")
            logger.debug(f"Response: {res}")

            if res == "":
                raise Exception("empty response")

            res_json = json.loads(res)
            if "Result" not in res_json.keys():
                return res_json
            return res_json["Result"]

        except Exception as e:
            logger.error(f"Request failed: {e}")

            # Try to parse error response
            try:
                if isinstance(e.args[0], bytes):
                    error_text = e.args[0].decode("utf-8")
                    logger.debug(f"Error detail: {error_text}")

                    # Try to parse JSON error
                    error_json = json.loads(error_text)
                    if "ResponseMetadata" in error_json:
                        metadata = error_json["ResponseMetadata"]
                        if "Error" in metadata:
                            error_info = metadata["Error"]
                            logger.debug(
                                f"Error code: {error_info.get('Code', 'N/A')}, Message: {error_info.get('Message', 'N/A')}"
                            )
            except Exception:
                pass

            raise
