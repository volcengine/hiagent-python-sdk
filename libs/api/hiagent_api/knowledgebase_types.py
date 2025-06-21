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
from typing import Optional

from pydantic import Field

from hiagent_api.base import BaseSchema


class QueryRequest(BaseSchema):
    workspace_id: str = Field(
        description="工作空间 id",
        serialization_alias="WorkspaceID",
    )
    dataset_ids: list[str] = Field(
        description="知识库 id",
        serialization_alias="DatasetIds",
    )
    keywords: list[str] = Field(
        description="查询关键词",
        serialization_alias="Keywords",
    )
    top_k: int = Field(
        description="检索结果 top-k",
        serialization_alias="TopK",
        default=5,
    )
    score_threshold: float = Field(
        description="检索分数阈值",
        serialization_alias="ScoreThreshold",
        default=0.5,
    )
    rerank_id: Optional[str] = Field(
        default=None,
        description="rerank 模型的 id",
        serialization_alias="RerankID",
    )
    expand: bool = Field(
        default=False,
        description="膨胀系数开关",
        serialization_alias="Expand",
    )
    expand_num: int = Field(
        default=1,
        description="膨胀系数，默认为 1，最大为 3",
        serialization_alias="ExpandNum",
    )
    type: int = Field(
        default=1,
        description="检索类型，1-知识库，2-问答库，3-术语库",
        serialization_alias="Type",
    )
    retrieval_search_method: int = Field(
        default=0,
        description="检索方法, 0-语义，1-全文，2-混合",
        serialization_alias="RetrievalSearchMethod",
    )


class Result(BaseSchema):
    dataset_id: str = Field(
        description="知识库 id",
        validation_alias="DatasetID",
    )
    dataset_name: str = Field(
        description="知识库名称",
        validation_alias="DatasetName",
    )
    document_id: str = Field(
        description="文档 id",
        validation_alias="DocumentID",
    )
    document_name: str = Field(
        description="文档名称",
        validation_alias="DocumentName",
    )
    segment_id: str = Field(
        description="分段 id",
        validation_alias="SegmentID",
    )
    content: str = Field(
        description="检索结果",
        validation_alias="Content",
    )
    score: float = Field(
        description="检索得分",
        validation_alias="Score",
    )


class QueryResponse(BaseSchema):
    results: list[Result] = Field(
        description="检索结果",
        validation_alias="Results",
    )
