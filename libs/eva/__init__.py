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
"""
Eva SDK - Evaluation Service SDK
"""

from hiagent_api.eva import EvaService
from hiagent_api.eva_types import (
    AgentModeStrategy,
    CaseData,
    CreateEvaTaskRequest,
    CreateEvaTaskResponse,
    DatasetTaskConfig,
    EvaDatasetColumn,
    EvaDatasetConversationItem,
    EvaTargetCustomAPPConfig,
    EvaTargetType,
    EvaTaskItem,
    EvaTaskItemDataset,
    EvaTaskItemRuleset,
    EvaTaskItemRulesetRule,
    EvaTaskItemTarget,
    EvaTaskResultTargetContentPair,
    EvaTaskResultUpdateTargetContent,
    EvaTaskStatus,
    EvaTaskTarget,
    ExecEvaTaskRowGroupRequest,
    GetEvaTaskReportRequest,
    GetEvaTaskReportResponse,
    GetEvaTaskRequest,
    GetEvaTaskResponse,
    InferenceResult,
    ListEvaDatasetColumnsRequest,
    ListEvaDatasetColumnsResponse,
    ListDatasetCasesRequest,
    ListDatasetCasesResponse,
    ModelAgentConfig,
)
from .hiagent_eva.client import Client

__version__ = "2.1.0"

__all__ = [
    "Client",
    "EvaService",
    "CreateEvaTaskRequest",
    "ListDatasetCasesRequest",
    "ListEvaDatasetColumnsRequest",
    "ExecEvaTaskRowGroupRequest",
    "GetEvaTaskReportRequest",
    "GetEvaTaskRequest",
    "CreateEvaTaskResponse",
    "ListDatasetCasesResponse",
    "ListEvaDatasetColumnsResponse",
    "GetEvaTaskReportResponse",
    "GetEvaTaskResponse",
    "EvaTaskTarget",
    "DatasetTaskConfig",
    "EvaDatasetColumn",
    "EvaDatasetConversationItem",
    "EvaTaskResultTargetContentPair",
    "EvaTaskResultUpdateTargetContent",
    "InferenceResult",
    "EvaTaskItem",
    "EvaTaskItemRuleset",
    "EvaTaskItemRulesetRule",
    "EvaTaskItemDataset",
    "EvaTaskItemTarget",
    "ModelAgentConfig",
    "EvaTargetCustomAPPConfig",
    "EvaTargetType",
    "EvaTaskStatus",
    "CaseData",
    "AgentModeStrategy",
]
