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
from enum import Enum
from token import OP
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# Common types
class AgentModeStrategy(str, Enum):
    REACT = "react"
    FUNCTION_CALL = "function_call"
    PLAN_AND_EXECUTE = "plan_and_execute"


class EvaTargetType(str, Enum):
    BUILTIN_MODEL = "BuiltinModel"
    BUILTIN_AGENT = "BuiltinAgent"
    BUILTIN_PROMPT = "BuiltinPrompt"
    CUSTOM_APP = "CustomAPP"


class EvaTaskStatus(str, Enum):
    WAITING = "Waiting"  # Waiting
    PENDING = "Pending"  # Pending
    RUNNING = "Running"  # Running
    SUCCEED = "Succeed"  # Success
    PARTIAL_SUCCEED = "PartialSucceed"  # Partial success
    FAILED = "Failed"  # Failed
    CANCELLING = "Cancelling"  # Cancelling
    CANCELLED = "Cancelled"  # Task cancelled


# New CellContent related types
class CellContentPartType(str, Enum):
    """Cell content part type"""

    TEXT = "text"
    IMAGE_URL = "image_url"
    VIDEO_URL = "video_url"


class ColumnSchemaType(str, Enum):
    """Schema type"""

    TEXT = "Text"
    MULTI_CONTENT = "MultiContent"


class ChatMessageImageURL(BaseModel):
    """Chat message image URL"""

    URL: Optional[str] = Field(default=None, alias="url", description="Image URL")


class ChatMessageVideoURL(BaseModel):
    """Chat message video URL"""

    URL: str = Field(alias="url", description="Video URL")


class CellContentPart(BaseModel):
    """Cell content part"""

    Type: Optional[CellContentPartType] = Field(
        default=None, description="Content part type"
    )
    Text: Optional[str] = Field(default=None, description="Text content")
    ImageURL: Optional[ChatMessageImageURL] = Field(
        default=None, description="Image URL"
    )
    VideoURL: Optional[ChatMessageVideoURL] = Field(
        default=None, description="Video URL"
    )


class CellContent(BaseModel):
    """Cell content"""

    Type: CellContentPartType = Field(
        default=None, alias="type", description="Content part type"
    )
    Text: Optional[str] = Field(default=None, alias="text", description="Text content")
    ImageURL: Optional[ChatMessageImageURL] = Field(
        default=None, alias="image_url", description="Image URL"
    )
    VideoURL: Optional[ChatMessageVideoURL] = Field(
        default=None, alias="video_url", description="Video URL"
    )


class Cell(BaseModel):
    """Repeated data"""

    CellContent: Optional[List[CellContentPart]] = Field(
        default=None, description="Cell content"
    )
    Text: Optional[str] = Field(default=None, description="Text content")


class ModelAgentConfig(BaseModel):
    """Model basic configuration"""

    Temperature: float = Field(..., description="Randomness")
    TopP: float = Field(..., description="Nucleus sampling")
    MaxTokens: int = Field(..., description="Max tokens per response")
    RoundsReserved: int = Field(..., description="Conversation rounds to preserve")
    RagNum: int = Field(..., description="RAG range")
    Strategy: AgentModeStrategy = Field(
        default=AgentModeStrategy.REACT, description="Strategy, default react"
    )
    MaxIterations: int = Field(
        default=5, ge=1, le=5, description="Max iterations, range 1-5, default 5"
    )
    RagEnabled: bool = Field(
        default=False, description="RAG switch, default off: false"
    )
    ReasoningMode: bool = Field(..., description="Deep thinking mode")
    ReasoningSwitch: bool = Field(..., description="Deep thinking switch")


class EvaTargetCustomAPPConfig(BaseModel):
    """CustomAPP target configuration"""

    AppID: str = Field(..., max_length=128, description="Custom APP ID")
    ModelAgentConfig: Optional[Dict[str, Any]] = Field(
        default=None, description="Model basic configuration"
    )


class EvaTaskTarget(BaseModel):
    Type: str = Field(
        title="Evaluation target type",
        description="Evaluation target type, such as BuiltinModel, BuiltinAgent, BuiltinPrompt, CustomAPP",
    )
    TargetID: str = Field(
        title="Evaluation target ID",
        description="Evaluation target ID",
    )
    TargetName: str = Field(
        title="Evaluation target name",
        description="Evaluation target name",
    )
    TargetIcon: Optional[str] = Field(
        default=None,
        title="Evaluation target avatar",
        description="Evaluation target avatar URL",
    )
    TargetConfig: Dict[str, Any] = Field(
        title="Evaluation target configuration",
        description="Model-related configuration of the evaluation target",
    )
    QPS: int = Field(
        default=1,
        title="QPS configuration",
        description="QPS configuration of the evaluation target",
    )


class DatasetTaskConfig(BaseModel):
    """Dataset task configuration"""

    MaxConversations: int = Field(
        default=100, description="Maximum number of conversations", ge=1, le=10000
    )
    BatchSize: int = Field(
        default=10, description="Batch processing size", ge=1, le=100
    )


# Request types
class CreateEvaTaskRequest(BaseModel):
    WorkspaceID: str = Field(
        title="Workspace ID",
        description="Workspace ID",
    )
    TaskTemplateID: Optional[str] = Field(
        default=None,
        title="Task Template ID",
        description="Task Template ID",
    )
    Name: str = Field(
        title="Task Name",
        description="Evaluation task name",
        min_length=1,
        max_length=100,
    )
    Description: Optional[str] = Field(
        default="",
        title="Task Description",
        description="Evaluation task description",
    )
    Targets: List[EvaTaskTarget] = Field(
        title="Task Evaluation Targets", description="Task evaluation target list"
    )
    DatasetID: str = Field(
        title="Evaluation Dataset ID",
        description="Evaluation dataset ID",
    )
    RulesetID: str = Field(
        title="Task Evaluation Rules",
        description="Task evaluation rule ID",
    )
    RunImmediately: bool = Field(
        default=True,
        title="Run Task Immediately",
        description="Whether to run the task immediately",
    )
    DatasetConfig: Optional[DatasetTaskConfig] = Field(
        default=None,
        title="Dataset Task Configuration",
        description="Dataset task configuration",
    )
    DatasetVersionID: str = Field(
        title="Dataset Version ID",
        description="Dataset version ID",
    )


class CreateEvaTaskResponse(BaseModel):
    TaskID: str = Field(
        title="Evaluation Task ID",
        description="Created evaluation task ID",
    )
    Status: Optional[str] = Field(
        default="created",
        title="Task Status",
        description="Task status",
    )


class ListDatasetCasesRequest(BaseModel):
    WorkspaceID: str = Field(
        title="Workspace ID",
        description="Workspace ID",
    )
    DatasetID: str = Field(title="Dataset ID", description="Dataset ID")
    VersionID: str = Field(title="Dataset Version ID", description="Dataset version ID")
    UseLatestPublishedVersion: bool = Field(
        default=False,
        title="Use Latest Published Version",
        description="Whether to use the latest published version",
    )
    PageNumber: Optional[int] = Field(
        default=1,
        title="Page Number",
        description="Page number, starting from 1",
    )
    PageSize: Optional[int] = Field(
        default=10,
        title="Page Size",
        description="Number of records returned per page",
    )


class DatasetAtomicDataType(str, Enum):
    """Dataset atomic data type"""

    FILE = "File"
    TEXT = "Text"
    IMAGE = "Image"
    HYPERTEXT = "HyperText"


class FileData(BaseModel):
    """File data"""

    URL: str = Field(title="File URL", description="File access address")
    Name: Optional[str] = Field(
        default=None, title="File Name", description="File name"
    )
    Size: Optional[int] = Field(
        default=None, title="File Size", description="File size (bytes)"
    )
    Type: Optional[str] = Field(
        default=None, title="File Type", description="File MIME type"
    )


class EvaDatasetAtomicHyperTextData(BaseModel):
    """Evaluation dataset atomic hypertext data"""

    Content: str = Field(title="Hypertext Content", description="Hypertext content")
    Images: Optional[Dict[str, FileData]] = Field(
        default=None, title="Image List", description="Image list"
    )
    Files: Optional[Dict[str, FileData]] = Field(
        default=None, title="File List", description="File list"
    )


class EvaDatasetAtomicData(BaseModel):
    """Evaluation dataset atomic data"""

    Type: DatasetAtomicDataType = Field(
        title="Data Type", description="Conversation column data type"
    )
    ImageData: Optional[List[FileData]] = Field(
        default=None, title="Image Data", description="Image data"
    )
    TextData: Optional[str] = Field(
        default=None, title="Text Data", description="Text data", max_length=8000
    )
    Files: Optional[List[FileData]] = Field(
        default=None, title="File Data", description="File data"
    )
    HyperTextData: Optional[EvaDatasetAtomicHyperTextData] = Field(
        default=None, title="Hypertext Data", description="Hypertext data"
    )


class EvaDatasetConversationData(BaseModel):
    """Evaluation dataset conversation round data"""

    AtomicData: EvaDatasetAtomicData = Field(
        title="Atomic Data", description="Evaluation dataset conversation round data"
    )
    Round: int = Field(
        title="Round", description="Evaluation dataset conversation round"
    )


class EvaDatasetColumnCell(BaseModel):
    """Evaluation dataset column cell data"""

    ConversationGroup: List[EvaDatasetConversationData] = Field(
        title="Conversation Group",
        description="Evaluation dataset conversation round data",
    )


class EvaDatasetColumn(BaseModel):
    """Evaluation dataset column definition"""

    ID: str = Field(title="Column ID", description="Column ID")
    Name: str = Field(title="Column Name", description="Column name")
    SchemaType: Optional[ColumnSchemaType] = Field(
        title="Schema Type", description="Schema type"
    )


class ListColumnsRequest(BaseModel):
    """Get evaluation dataset column list request"""

    WorkspaceID: str = Field(
        title="Workspace ID",
        description="Workspace ID",
    )
    DatasetID: str = Field(title="Dataset ID", description="Dataset ID")
    VersionID: str = Field(title="Dataset Version ID", description="Dataset version ID")


class InferenceResult(BaseModel):
    """Inference result (simplified version)"""

    Content: Optional[str] = Field(
        default=None, title="Content", description="Content generated by inference"
    )
    ContentThought: Optional[str] = Field(
        default=None,
        title="Thought Process",
        description="Thought process of inference",
    )
    CostTokens: Optional[int] = Field(
        default=None,
        title="Cost Tokens",
        description="Number of tokens consumed by inference",
    )
    TTFT: Optional[int] = Field(
        default=None,
        title="Time to First Token",
        description="Time to first token, in milliseconds",
    )


class CaseData(BaseModel):
    """Case data"""

    model_config = {"extra": "allow"}  # Allow dynamic fields

    def get_column_data(self, column_name: str) -> Optional[Cell]:
        """
        Get data from specified column

        Args:
            column_name: Column name

        Returns:
            Cell content of the column, returns None if not exists
        """
        # In Pydantic v2, extra fields are stored in __pydantic_extra__
        if hasattr(self, "__pydantic_extra__"):
            return self.__pydantic_extra__.get(column_name)
        return None

    def list_columns(self) -> List[str]:
        """
        Get all column names included in current round

        Returns:
            List of column names
        """
        # In Pydantic v2, extra fields are stored in __pydantic_extra__
        if hasattr(self, "__pydantic_extra__"):
            return list(self.__pydantic_extra__.keys())
        return []

    # Dictionary-style operation support
    def __getitem__(self, column_name: str) -> Optional[Cell]:
        """
        Support case_data[column_name] access pattern

        Args:
            column_name: Column name

        Returns:
            Cell content of the column
        """
        return self.get_column_data(column_name)

    def __setitem__(self, column_name: str, value: Cell):
        """
        Support case_data[column_name] = value assignment pattern

        Args:
            column_name: Column name
            value: Cell content
        """
        if not hasattr(self, "__pydantic_extra__"):
            self.__pydantic_extra__ = {}
        self.__pydantic_extra__[column_name] = value

    def __contains__(self, column_name: str) -> bool:
        """
        Support column_name in case_data check pattern

        Args:
            column_name: Column name

        Returns:
            Whether the column is included
        """
        return column_name in self.list_columns()

    def __iter__(self):
        """
        Support for column_name in case_data iteration pattern

        Returns:
            Iterator of column names
        """
        return iter(self.list_columns())

    def items(self):
        """
        Support for column_name, data in case_data.items() iteration pattern

        Returns:
            Iterator of (column_name, cell_content) tuples
        """
        for column_name in self.list_columns():
            yield column_name, self.get_column_data(column_name)

    def keys(self) -> List[str]:
        """
        Get all column names

        Returns:
            List of column names
        """
        return self.list_columns()

    def values(self) -> List[Optional[Cell]]:
        """
        Get data from all columns

        Returns:
            List of cell content
        """
        return [self.get_column_data(column_id) for column_id in self.list_columns()]

    def get(self, column_name: str, default=None):
        """
        Get column data, return default value if not exists

        Args:
            column_name: Column name
            default: Default value

        Returns:
            Cell content or default value
        """
        data = self.get_column_data(column_name)
        return data if data is not None else default


class EvaDatasetConversationItem(BaseModel):
    """Evaluation dataset conversation item"""

    DatasetCaseID: str = Field(
        title="Dataset Case ID", description="Evaluation dataset case ID"
    )
    RepeatedData: List[Dict[str, Cell]] = Field(
        title="Repeated Data", description="Evaluation dataset case data"
    )


class EvaConversationStatus(str, Enum):
    """Evaluation conversation status"""

    SUCCEED = "Succeed"
    FAILED = "Failed"
    PROCESSING = "Processing"
    PENDING = "Pending"


class EvaTaskResultTargetContentPair(BaseModel):
    """Evaluation task result target content pair"""

    Content: Optional[str] = Field(
        default=None,
        title="Output Content",
        description="Output content of the evaluation target",
    )
    ContentThought: Optional[str] = Field(
        default=None,
        title="Output Thought",
        description="Thought process of the evaluation target output",
    )
    Round: int = Field(
        title="Round", description="Evaluation dataset conversation round"
    )
    MessageID: Optional[str] = Field(
        default=None, title="Message ID", description="Message ID of the conversation"
    )
    ConversationID: Optional[str] = Field(
        default=None,
        title="Conversation ID",
        description="ConversationID of the conversation",
    )
    Status: EvaConversationStatus = Field(
        title="Status", description="Evaluation dataset conversation status"
    )
    StatusMessage: Optional[str] = Field(
        default=None, title="Status Message", description="Status message description"
    )
    CostTokens: Optional[int] = Field(
        default=None,
        title="Cost Tokens",
        description="Number of tokens consumed by evaluation",
    )
    InferenceDuration: Optional[int] = Field(
        default=None,
        title="Inference Duration",
        description="Time consumed by inference, in milliseconds",
    )
    RuleDuration: Optional[int] = Field(
        default=None,
        title="Rule Duration",
        description="Time consumed by evaluation rules, in milliseconds",
    )
    TTFT: Optional[int] = Field(
        default=None,
        title="Time to First Token",
        description="Time to first token of the evaluation target, in milliseconds",
    )


class EvaTaskResultUpdateTargetContent(BaseModel):
    """Evaluation task result update target content"""

    TargetType: EvaTargetType = Field(
        title="Target Type", description="Type of the evaluation target"
    )
    TargetID: str = Field(title="Target ID", description="ID of the evaluation target")
    Results: List[EvaTaskResultTargetContentPair] = Field(
        title="Evaluation Results", description="Evaluation results"
    )


class ExecEvaTaskRowGroupRequest(BaseModel):
    """Execute evaluation task row group request"""

    WorkspaceID: str = Field(
        title="Workspace ID",
        description="Workspace ID",
    )
    TaskID: str = Field(
        title="Evaluation Task ID",
        description="Evaluation task ID",
    )
    RowID: str = Field(title="Row ID", description="Row ID")
    TargetResults: Optional[List[EvaTaskResultUpdateTargetContent]] = Field(
        default=None,
        title="Target Results",
        description="Target results for the row group",
    )


class ExecEvaTaskRowGroupResponse(BaseModel):
    """Execute evaluation task row group response"""

    pass


class GetEvaTaskReportRequest(BaseModel):
    WorkspaceID: str = Field(
        title="Workspace ID",
        description="Workspace ID",
    )
    TaskID: str = Field(
        title="Evaluation Task ID",
        description="Evaluation task ID",
    )


# New evaluation report related types, based on actual API return structure
class EvaReportTargetDetail(BaseModel):
    """Evaluation report target details"""

    Type: str = Field(title="Target Type", description="Target type")
    TargetID: str = Field(title="Target ID", description="Target ID")
    TargetName: str = Field(title="Target Name", description="Target name")
    TargetIcon: str = Field(title="Target Icon", description="Target icon")
    TargetConfig: Dict[str, Any] = Field(
        title="Target Configuration", description="Target configuration"
    )
    QPS: int = Field(title="QPS", description="QPS limit")


class EvaReportRuleTarget(BaseModel):
    """Evaluation report rule target"""

    TargetID: str = Field(title="Target ID", description="Target ID")
    TargetDetail: EvaReportTargetDetail = Field(
        title="Target Details", description="Target details"
    )
    AvgScore: Optional[float] = Field(
        title="Average Score", description="Average score"
    )
    Percent: Optional[float] = Field(title="Percentage", description="Percentage")
    ScoreMap: Optional[Dict[str, Any]] = Field(
        title="Score Map", description="Score mapping"
    )
    Duration: int = Field(title="Duration", description="Duration in milliseconds")
    CostTokens: int = Field(
        title="Cost Tokens", description="Number of tokens consumed"
    )


class EvaReportRule(BaseModel):
    """Evaluation report rule"""

    RuleID: str = Field(title="Rule ID", description="Rule ID")
    Targets: List[EvaReportRuleTarget] = Field(
        title="Target List", description="List of targets under the rule"
    )


class EvaReportTarget(BaseModel):
    """Evaluation report target"""

    TargetID: str = Field(title="Target ID", description="Target ID")
    TargetDetail: EvaReportTargetDetail = Field(
        title="Target Details", description="Target details"
    )
    Duration: int = Field(title="Duration", description="Duration in milliseconds")
    CostTokens: int = Field(
        title="Total Cost Tokens", description="Total number of tokens consumed"
    )
    AvgCostTokens: float = Field(
        title="Average Cost Tokens", description="Average number of tokens consumed"
    )
    AvgDuration: float = Field(
        title="Average Duration", description="Average duration in milliseconds"
    )
    AvgTTFT: float = Field(
        title="Average Time to First Token",
        description="Average time to first token in milliseconds",
    )


class GetEvaTaskReportResponse(BaseModel):
    """Get evaluation task report response"""

    Rules: List[EvaReportRule] = Field(
        title="Rules List", description="Evaluation rules list"
    )
    Targets: List[EvaReportTarget] = Field(
        title="Targets List", description="Evaluation targets list"
    )
    CreatedAt: str = Field(title="Created At", description="Creation time")
    UpdatedAt: str = Field(title="Updated At", description="Update time")
    CreatedBy: str = Field(title="Created By", description="Creator")
    UpdatedBy: str = Field(title="Updated By", description="Updater")

    # For compatibility, add some properties
    @property
    def Status(self) -> str:
        """Task status (inferred from data)"""
        return "completed" if self.Rules else "running"

    @property
    def TaskID(self) -> Optional[str]:
        """Task ID (get from targets if available)"""
        return None  # Actual API doesn't return this field

    @property
    def TaskName(self) -> Optional[str]:
        """Task name (actual API doesn't return this field)"""
        return None


# Ruleset related types
class CreateEvaRulesetRequest(BaseModel):
    WorkspaceID: str = Field(
        title="Workspace ID",
        description="Workspace ID",
    )
    Name: str = Field(
        title="Evaluation Ruleset Name",
        description="Evaluation ruleset name",
    )
    Description: Optional[str] = Field(
        default=None,
        title="Evaluation Ruleset Description",
        description="Evaluation ruleset description",
    )


class CreateEvaRulesetResponse(BaseModel):
    RulesetID: str = Field(
        title="Evaluation Ruleset ID",
        description="Created evaluation ruleset ID",
    )


class ListEvaRulesetsRequest(BaseModel):
    WorkspaceID: str = Field(
        title="Workspace ID",
        description="Workspace ID",
    )
    PageNumber: Optional[int] = Field(
        default=1,
        title="Page Number",
        description="Page number, starting from 1",
    )
    PageSize: Optional[int] = Field(
        default=10,
        title="Page Size",
        description="Number of records returned per page",
    )


class EvaRulesetItem(BaseModel):
    TenantID: str = Field(title="Tenant ID", description="Tenant ID")
    WorkspaceID: str = Field(title="Workspace ID", description="Workspace ID")
    RulesetID: str = Field(
        title="Evaluation Ruleset ID", description="Evaluation ruleset ID"
    )
    Name: str = Field(
        title="Evaluation Ruleset Name", description="Evaluation ruleset name"
    )
    Description: Optional[str] = Field(
        default=None,
        title="Evaluation Ruleset Description",
        description="Evaluation ruleset description",
    )
    RuleCount: Optional[int] = Field(
        default=None,
        title="Evaluation Rule Count",
        description="Number of evaluation rules",
    )
    CreatedAt: str = Field(title="Created At", description="Creation time")
    UpdatedAt: str = Field(title="Updated At", description="Update time")
    CreatedBy: str = Field(title="Created By", description="Creator")
    UpdatedBy: str = Field(title="Updated By", description="Updater")


class ListEvaRulesetsResponse(BaseModel):
    Items: List[EvaRulesetItem] = Field(
        title="Evaluation Ruleset List", description="Evaluation ruleset list"
    )
    Total: int = Field(title="Total", description="Total number of rulesets")


# GetEvaTask related type definitions
class EvaTaskItemTaskTemplate(BaseModel):
    """Task template information"""

    TaskTemplateID: str = Field(
        title="Task Template ID", description="Task template ID"
    )
    TaskTemplateName: str = Field(
        title="Task Template Name", description="Task template name"
    )
    IsDeleted: bool = Field(
        title="Is Deleted", description="Whether it has been deleted"
    )


class EvaTaskItemRulesetRule(BaseModel):
    """Rules in task ruleset"""

    RuleID: str = Field(title="Evaluation Rule ID", description="Evaluation rule ID")
    Name: str = Field(title="Evaluation Rule Name", description="Evaluation rule name")
    Type: str = Field(title="Evaluation Rule Type", description="Evaluation rule type")
    Config: Dict[str, Any] = Field(
        title="Evaluation Rule Configuration",
        description="Evaluation rule configuration",
    )


class EvaTaskItemRuleset(BaseModel):
    """Task ruleset"""

    RulesetID: str = Field(
        title="Evaluation Ruleset ID", description="Evaluation ruleset ID"
    )
    RulesetName: str = Field(
        title="Evaluation Ruleset Name", description="Evaluation ruleset name"
    )
    IsDeleted: bool = Field(
        title="Is Deleted", description="Whether it has been deleted"
    )
    Rules: Optional[List[EvaTaskItemRulesetRule]] = Field(
        default=None,
        title="All Rules in Evaluation Ruleset",
        description="All rules in the evaluation ruleset",
    )


class EvaTaskItemDatasetColumn(BaseModel):
    """Task dataset column"""

    ColumnID: str = Field(title="Dataset Column ID", description="Dataset column ID")
    ColumnName: str = Field(
        title="Dataset Column Name", description="Dataset column name"
    )


class EvaTaskOfficialCollection(BaseModel):
    """Official evaluation collection information"""

    CollectionID: Optional[str] = Field(
        default=None,
        title="Official Evaluation Collection ID",
        description="Official evaluation collection ID",
    )
    CollectionName: Optional[str] = Field(
        default=None,
        title="Official Evaluation Collection Name",
        description="Official evaluation collection name",
    )


class EvaTaskItemDataset(BaseModel):
    """Task dataset"""

    DatasetID: str = Field(title="Dataset ID", description="Dataset ID")
    DatasetName: str = Field(title="Dataset Name", description="Dataset name")
    Columns: Optional[List[EvaTaskItemDatasetColumn]] = Field(
        default=None,
        title="Dataset Column Information",
        description="Dataset column information",
    )
    IsDeleted: bool = Field(
        title="Is Deleted", description="Whether it has been deleted"
    )
    DatasetSource: Optional[str] = Field(
        default=None, title="Dataset Source", description="Dataset source"
    )
    DatasetConfig: Optional[Dict[str, Any]] = Field(
        default=None,
        title="Dataset Task Configuration",
        description="Dataset task configuration",
    )
    SourceDataTotal: Optional[int] = Field(
        default=None,
        title="Source Dataset Total",
        description="Total amount of source dataset",
    )
    OfficialCollection: Optional[EvaTaskOfficialCollection] = Field(
        default=None,
        title="Official Evaluation Collection Information",
        description="Official evaluation collection information",
    )


class EvaTaskItemProgress(BaseModel):
    """Task progress"""

    Total: int = Field(title="Total Quantity", description="Total quantity")
    Completed: int = Field(
        title="Completed Quantity",
        description="Completed quantity, including failed ones",
        alias="Done",
    )


class EvaTaskItemTarget(BaseModel):
    """Task evaluation target"""

    Target: EvaTaskTarget = Field(
        title="Evaluation Target", description="Evaluation target"
    )
    IsDeleted: bool = Field(
        title="Is Deleted", description="Whether it has been deleted"
    )


class EvaTaskItem(BaseModel):
    """Evaluation task details"""

    TenantID: str = Field(title="Tenant ID", description="Tenant ID")
    WorkspaceID: str = Field(title="Workspace ID", description="Workspace ID")
    TaskID: str = Field(title="Task ID", description="Task ID")
    Name: str = Field(title="Task Name", description="Task name")
    Description: Optional[str] = Field(
        default=None, title="Task Description", description="Task description"
    )
    TaskTemplate: Optional[EvaTaskItemTaskTemplate] = Field(
        default=None, title="Task Template", description="Task template"
    )
    TargetType: str = Field(title="Task Type", description="Task type")
    Ruleset: EvaTaskItemRuleset = Field(
        title="Task Evaluation Ruleset", description="Task evaluation ruleset"
    )
    Dataset: EvaTaskItemDataset = Field(
        title="Task Evaluation Dataset", description="Task evaluation dataset"
    )
    Targets: Optional[List[EvaTaskItemTarget]] = Field(
        default=None,
        title="Task Evaluation Targets",
        description="Task evaluation targets",
    )
    StartedAt: Optional[str] = Field(
        default=None, title="Task Start Time", description="Task start time"
    )
    CompletedAt: Optional[str] = Field(
        default=None, title="Task End Time", description="Task end time"
    )
    Duration: int = Field(
        title="Task Execution Duration",
        description="Task execution duration in milliseconds",
    )
    CostTokens: Optional[int] = Field(
        default=None,
        title="Task Completion Token Cost",
        description="Tokens consumed for task completion",
    )
    Progress: Optional[EvaTaskItemProgress] = Field(
        default=None, title="Task Progress", description="Task progress"
    )
    Status: EvaTaskStatus = Field(title="Task Status", description="Task status")
    StatusMessage: Optional[str] = Field(
        default=None,
        title="Task Status Description",
        description="Task status description",
    )
    CreatedAt: str = Field(title="Created At", description="Creation time")
    UpdatedAt: str = Field(title="Updated At", description="Update time")
    CreatedBy: str = Field(title="Created By", description="Creator")
    UpdatedBy: str = Field(title="Updated By", description="Updater")


class GetEvaTaskRequest(BaseModel):
    """Get evaluation task request"""

    WorkspaceID: str = Field(title="Workspace ID", description="Workspace ID")
    TaskID: Optional[str] = Field(default=None, title="Task ID", description="Task ID")
    TaskName: Optional[str] = Field(
        default=None, title="Task Name", description="Task name"
    )


# GetEvaTaskResponse 就是 EvaTaskItem
GetEvaTaskResponse = EvaTaskItem


class ListColumnsResponse(BaseModel):
    """Get evaluation dataset column list response"""

    Columns: List[EvaDatasetColumn] = Field(
        title="Evaluation Dataset Column List",
        description="Evaluation dataset column list",
    )


class ListDatasetCasesResponse(BaseModel):
    """Evaluation dataset conversation list response"""

    Items: Optional[List[EvaDatasetConversationItem]] = Field(
        title="Conversation List", description="Evaluation dataset conversation list"
    )
    Total: int = Field(
        title="Total", description="Total number of evaluation dataset conversations"
    )
