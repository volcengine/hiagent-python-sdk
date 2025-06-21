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
import logging
import time
from typing import Callable, Dict, List, Optional

from tenacity import before_sleep_log, retry, stop_after_attempt, wait_fixed

from libs.observe.hiagent_observe.client import AuthSession

from ..api.hiagent_api import eva_types
from ..api.hiagent_api.eva import EvaService

logger = logging.getLogger(__name__)


def init(endpoint: str, ak: str, sk: str, workspace_id: str, app_id: str):
    """
    Initialize client configuration
    """
    return Client(endpoint, ak, sk, workspace_id, app_id)


class Client:
    """Eva SDK Client Class"""

    def __init__(self, endpoint: str, ak: str, sk: str, workspace_id: str, app_id: str):
        """
        Initialize client configuration

        Args:
            endpoint: API endpoint
            ak: Access Key
            sk: Secret Key
            workspace_id: Workspace ID
            app_id: Application ID
        """
        self.endpoint = endpoint
        self.workspace_id = workspace_id
        self.app_id = app_id
        self.logger = logging.getLogger(__name__)

        # Initialize Eva service
        self.eva_service = EvaService(endpoint=endpoint)

        self.eva_service.set_ak(ak)
        self.eva_service.set_sk(sk)

        self.logger.info(f"Eva client initialized with endpoint: {endpoint}")

    def create_task(
        self,
        dataset_id: str,
        task_name: str,
        ruleset_id: str,
        description: str = "",
        model_agent_config: Optional[eva_types.ModelAgentConfig] = None,
        run_immediately: bool = True,
    ) -> eva_types.CreateEvaTaskResponse:
        """
        Create evaluation task

        Args:
            dataset_id: Dataset ID
            task_name: Task name
            ruleset_id: Ruleset ID
            description: Task description
            model_agent_config: Model agent configuration (optional, will be automatically assembled into complete configuration using app_id)
            run_immediately: Whether to run immediately

        Returns:
            CreateEvaTaskResponse: Create task response
        """
        if not self.eva_service:
            raise ValueError("Client not initialized. Call init() first.")

        # Automatically create evaluation target, using app_id as target_id
        # If ModelAgentConfig is provided, assemble it into complete EvaTargetCustomAPPConfig
        if model_agent_config:
            target_config = eva_types.EvaTargetCustomAPPConfig(
                AppID=self.app_id, ModelAgentConfig=model_agent_config.model_dump()
            )
            target_config_dict = target_config.model_dump()
        else:
            target_config_dict = {}

        targets = [
            eva_types.EvaTaskTarget(
                Type="CustomAPP",
                TargetID=self.app_id,
                TargetName=f"App-{self.app_id}",
                TargetConfig=target_config_dict,
                QPS=1,
            )
        ]

        request = eva_types.CreateEvaTaskRequest(
            WorkspaceID=self.workspace_id,
            Name=task_name,
            Description=description,
            Targets=targets,
            DatasetID=dataset_id,
            RulesetID=ruleset_id,
            RunImmediately=run_immediately,
        )

        return self.eva_service.CreateEvaTask(request)

    def list_dataset_conversations(
        self, dataset_id: str, page_number: int = 1, page_size: int = 20
    ) -> eva_types.ListEvaDatasetConversationsResponse:
        """
        List dataset conversations

        Args:
            dataset_id: Dataset ID
            page_number: Page number
            page_size: Page size

        Returns:
            ListEvaDatasetConversationsResponse: Dataset conversation response
        """
        if not self.eva_service:
            raise ValueError("Client not initialized. Call init() first.")

        request = eva_types.ListEvaDatasetConversationsRequest(
            WorkspaceID=self.workspace_id,
            DatasetID=dataset_id,
            PageNumber=page_number,
            PageSize=page_size,
        )

        return self.eva_service.ListEvaDatasetConversations(request)

    def list_dataset_columns(
        self, dataset_id: str
    ) -> eva_types.ListEvaDatasetColumnsResponse:
        """
        Get dataset column information

        Args:
            dataset_id: Dataset ID

        Returns:
            ListEvaDatasetColumnsResponse: Dataset column information response
        """
        if not self.eva_service:
            raise ValueError("Client not initialized. Call init() first.")

        request = eva_types.ListEvaDatasetColumnsRequest(
            WorkspaceID=self.workspace_id,
            DatasetID=dataset_id,
        )

        return self.eva_service.ListEvaDatasetColumns(request)

    def submit_task_row_group_results(
        self,
        task_id: str,
        row_id: str,
        target_results: Optional[
            List[eva_types.EvaTaskResultUpdateTargetContent]
        ] = None,
    ) -> eva_types.ExecEvaTaskRowGroupResponse:
        """
        Submit evaluation task row group results

        Args:
            task_id: Task ID
            row_id: Row ID
            target_results: Target results list

        Returns:
            ExecEvaTaskRowGroupResponse: Execution response
        """
        if not self.eva_service:
            raise ValueError("Client not initialized. Call init() first.")

        request = eva_types.ExecEvaTaskRowGroupRequest(
            WorkspaceID=self.workspace_id,
            TaskID=task_id,
            RowID=row_id,
            TargetResults=target_results,
        )

        return self.eva_service.ExecEvaTaskRowGroup(request)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(1),
        before_sleep=before_sleep_log(logger, logging.INFO),
    )
    def get_task_report(self, task_id: str) -> eva_types.GetEvaTaskReportResponse:
        """
        Get task report (with retry mechanism: 1 second interval, 3 attempts)

        Args:
            task_id: Task ID

        Returns:
            GetEvaTaskReportResponse: Task report response
        """
        if not self.eva_service:
            raise ValueError("Client not initialized. Call init() first.")

        request = eva_types.GetEvaTaskReportRequest(
            WorkspaceID=self.workspace_id, TaskID=task_id
        )

        return self.eva_service.GetEvaTaskReport(request)

    def _convert_to_case_data_list(
        self,
        conversation_item: eva_types.EvaDatasetConversationItem,
        columns: List[eva_types.EvaDatasetColumn],
    ) -> List[eva_types.CaseData]:
        """
        Convert raw conversation item to case data list

        Args:
            conversation_item: Raw conversation item
            columns: Column information

        Returns:
            Converted case data list
        """
        # Create column ID to column name mapping
        column_map = {col.ID: col.Name for col in columns}

        # Organize data by rounds
        rounds_data: Dict[int, Dict[str, eva_types.CellContent]] = {}

        for data_cell in conversation_item.DataRow:
            column_name = column_map.get(
                data_cell.ColumnID, f"Column_{data_cell.ColumnID}"
            )

            for conv_data in data_cell.ConversationGroup:
                round_num = conv_data.Round
                if round_num not in rounds_data:
                    rounds_data[round_num] = {}
                rounds_data[round_num][column_name] = self._convert_to_cell_content(
                    conv_data.AtomicData
                )

        # Create CellContent list in round order
        sorted_rounds = sorted(rounds_data.keys())
        case_data_list = []

        for round_num in sorted_rounds:
            case_data = eva_types.CaseData(**rounds_data[round_num])
            case_data_list.append(case_data)

        return case_data_list

    def _convert_to_cell_content(
        self, atomic_data: eva_types.EvaDatasetAtomicData
    ) -> eva_types.CellContent:
        """
        Convert atomic data to cell content
        """
        content = []
        if atomic_data.Type == eva_types.DatasetAtomicDataType.TEXT:
            content.append(
                eva_types.CellContentPart(
                    Type=eva_types.CellContentPartType.TEXT,
                    Text=atomic_data.TextData,
                )
            )
        elif atomic_data.Type == eva_types.DatasetAtomicDataType.IMAGE:
            content.extend(
                [
                    eva_types.CellContentPart(
                        Type=eva_types.CellContentPartType.IMAGE_URL,
                        ImageURL=image.URL,
                    )
                    for image in atomic_data.ImageData
                ]
            )
        elif atomic_data.Type == eva_types.DatasetAtomicDataType.FILE:
            content.extend(
                [
                    eva_types.CellContentPart(
                        Type=eva_types.CellContentPartType.VIDEO_URL,
                        VideoURL=file.URL,
                    )
                    for file in atomic_data.Files
                ]
            )
        return content

    def run_evaluation(
        self,
        dataset_id: str,
        task_name: str,
        inference_function: Callable[
            [List[eva_types.CaseData]], List[eva_types.InferenceResult]
        ],
        ruleset_id: str,
        target_config: Optional[eva_types.ModelAgentConfig] = None,
        max_conversations: int = 10,
    ) -> eva_types.GetEvaTaskReportResponse:
        """
        Run complete evaluation process

        Args:
            dataset_id: Dataset ID
            task_name: Task name
            inference_function: Inference function that receives case data list and returns user inference results list
            ruleset_id: Ruleset ID
            target_config: Model agent configuration (optional)
            max_conversations: Maximum number of conversations

        Returns:
            GetEvaTaskReportResponse: Evaluation report
        """
        try:
            # 1. Create evaluation task
            self.logger.info(f"Creating evaluation task: {task_name}")
            task_response = self.create_task(
                dataset_id=dataset_id,
                task_name=task_name,
                ruleset_id=ruleset_id,
                model_agent_config=target_config,
            )
            task_id = task_response.TaskID
            self.logger.info(f"Task created successfully: {task_id}")

            # 2. Get dataset column information
            self.logger.info("Fetching dataset columns...")
            columns_response = self.list_dataset_columns(dataset_id)
            columns = columns_response.Columns
            self.logger.info(
                f"Fetched {len(columns)} columns: {[col.Name for col in columns]}"
            )

            # 3. Get dataset conversations
            self.logger.info("Fetching dataset conversations...")
            conversations_response = self.list_dataset_conversations(
                dataset_id=dataset_id, page_size=max_conversations
            )
            conversation_items = conversations_response.Items
            self.logger.info(f"Fetched {len(conversation_items)} conversation items")

            # 4. Execute inference and submit results
            self.logger.info("Running inference and submitting results...")
            time.sleep(2)
            for conversation_item in conversation_items:
                # Convert to case data list
                case_data_list = self._convert_to_case_data_list(
                    conversation_item, columns
                )

                # Call inference function, passing case data list
                target_content_pairs = self._execute_inference_with_wrapper(
                    inference_function, case_data_list, conversation_item.RowID
                )

                # Create target results
                target_results = [
                    eva_types.EvaTaskResultUpdateTargetContent(
                        TargetType=eva_types.EvaTargetType.CUSTOM_APP,
                        TargetID=self.app_id,
                        Results=target_content_pairs,
                    )
                ]

                # Submit results
                self.submit_task_row_group_results(
                    task_id, conversation_item.RowID, target_results
                )
                self.logger.debug(
                    f"Results submitted for row {conversation_item.RowID}"
                )

            # 5. Wait for processing to complete
            self.logger.info("Waiting for evaluation to complete...")
            self._wait_task_finished(task_id=task_id)

            # 6. Get evaluation report
            report = self.get_task_report(task_id)
            self.logger.info(f"Evaluation completed with status: {report.Status}")

            return report

        except Exception as e:
            self.logger.error(f"Evaluation failed: {e}", exc_info=True)
            raise

    def _execute_inference_with_wrapper(
        self,
        inference_function: Callable[
            [List[eva_types.CaseData]], List[eva_types.InferenceResult]
        ],
        case_data_list: List[eva_types.CaseData],
        row_id: str,
    ) -> List[eva_types.EvaTaskResultTargetContentPair]:
        """
        Execute inference function and wrap results

        Args:
            inference_function: User-provided inference function
            case_data_list: Case data list
            row_id: Row ID

        Returns:
            Wrapped target content pair list
        """
        import time

        start_time = time.time()
        round_counter = 1
        target_content_pairs = []

        try:
            # Execute user's inference function, passing case data list
            user_results = inference_function(case_data_list)
            end_time = time.time()
            inference_duration = int((end_time - start_time) * 1000)

            # Wrap each result
            for user_result in user_results:
                target_content_pair = eva_types.EvaTaskResultTargetContentPair(
                    Content=user_result.Content,
                    ContentThought=user_result.ContentThought,
                    Round=round_counter,
                    MessageID=None,  # Not needed
                    ConversationID=None,  # Not needed
                    Status=eva_types.EvaConversationStatus.SUCCEED,  # Success status
                    StatusMessage=None,
                    CostTokens=user_result.CostTokens,
                    InferenceDuration=inference_duration,
                    RuleDuration=None,  # Not needed
                    TTFT=user_result.TTFT,
                )
                target_content_pairs.append(target_content_pair)
                round_counter += 1

        except Exception as e:
            # If there's an exception, create a failed status result
            end_time = time.time()
            inference_duration = int((end_time - start_time) * 1000)

            target_content_pair = eva_types.EvaTaskResultTargetContentPair(
                Content=None,
                ContentThought=None,
                Round=1,
                MessageID=None,
                ConversationID=None,
                Status=eva_types.EvaConversationStatus.FAILED,
                StatusMessage=str(e),  # Exception message as status message
                CostTokens=None,
                InferenceDuration=inference_duration,
                RuleDuration=None,
                TTFT=None,
            )
            target_content_pairs.append(target_content_pair)

            self.logger.error(f"Inference failed for row {row_id}: {e}")

        return target_content_pairs

    def _wait_task_finished(self, task_id: str):
        request = eva_types.GetEvaTaskRequest(
            WorkspaceID=self.workspace_id, TaskID=task_id
        )
        task = self.eva_service.GetEvaTask(request)
        while task.Status not in [
            eva_types.EvaTaskStatus.SUCCEED,
            eva_types.EvaTaskStatus.FAILED,
            eva_types.EvaTaskStatus.CANCELLED,
            eva_types.EvaTaskStatus.PARTIAL_SUCCEED,
        ]:
            time.sleep(1)
            task = self.eva_service.GetEvaTask(request)
