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
from typing import Dict, List

from pydantic import BaseModel, Field


class CreateApiTokenRequest(BaseModel):
    WorkspaceID: str = Field(
        title="工作空间 ID", description="工作空间 ID", example="wcxxxxxxxxxxxxxxxxxxx"
    )
    CustomAppID: str = Field(
        title="自定义应用 ID",
        description="自定义应用 ID",
        example="appxxxxxxxxxxxxxxxxxxx",
    )


class CreateApiTokenResponse(BaseModel):
    Token: str = Field(
        title="API Token", description="API Token", example="wcxxxxxxxxxxxxxxxxxxx"
    )
    ExpiresIn: int = Field(
        title="有效时间", description="有效时间，单位为秒", example=3600
    )


class ListTraceSpansRequestSortBy(str, Enum):
    StartTime = "StartTime"
    Latency = "Latency"
    LatencyFirstResp = "LatencyFirstResp"
    TotalTokens = "TotalTokens"


class SortOrderType(str, Enum):
    Desc = "Desc"
    Asc = "Asc"


class ListTraceSpansRequestSort(BaseModel):
    SortOrder: SortOrderType = Field(
        title="排序顺序", description="排序顺序", example=SortOrderType.Desc
    )
    SortBy: ListTraceSpansRequestSortBy = Field(
        title="排序字段",
        description="排序字段",
        example=ListTraceSpansRequestSortBy.StartTime,
    )


class ListTraceSpansRequest(BaseModel):
    WorkspaceID: str = Field(
        title="工作空间 ID", description="工作空间 ID", example="wcxxxxxxxxxxxxxxxxxxx"
    )
    PageSize: int = Field(title="分页大小", description="分页大小", example=10)
    LastID: str = Field(
        title="上一页最后一条记录的 ID",
        description="上一页最后一条记录的 ID",
        example="xxxxxxxxxxxxxxxxxxx",
    )
    Sort: List[ListTraceSpansRequestSort] = Field(
        title="排序条件",
        description="排序条件",
        example=[
            {
                "SortOrder": SortOrderType.Desc,
                "SortBy": ListTraceSpansRequestSortBy.StartTime,
            }
        ],
    )


class TraceSpanContext(BaseModel):
    TraceID: str = Field(
        title="Trace ID",
        description="Trace ID",
        example="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    )
    SpanID: str = Field(
        title="Span ID",
        description="Span ID",
        example="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    )
    ParentSpanID: str = Field(
        title="Parent Span ID",
        description="Parent Span ID",
        example="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    )


class TraceSpanStatusCode(str, Enum):
    Unset = "UNSET"
    OK = "OK"
    Error = "ERROR"
    Unknown = "UNKNOWN"
    Cancelled = "CANCELLED"


class TraceSpanStatus(BaseModel):
    Code: TraceSpanStatusCode = Field(
        title="状态码",
        description="状态码",
    )
    Message: str = Field(
        title="状态信息",
        description="状态信息",
    )


class TraceSpanItem(BaseModel):
    DocID: str = Field(
        title="文档 ID",
        description="文档 ID",
        example="xxxxxxxxxxxxxxxxxxx",
    )
    Context: TraceSpanContext = Field(
        title="Span 上下文信息",
        description="Span 上下文信息",
    )
    Name: str = Field(
        title="Span 名称",
        description="Span 名称",
    )
    Status: TraceSpanStatus = Field(
        title="Span 状态信息",
        description="Span 状态信息",
    )
    StartTime: str = Field(
        title="Span 开始时间",
        description="Span 开始时间",
    )
    EndTime: str = Field(
        title="Span 结束时间",
        description="Span 结束时间",
    )
    Attributes: Dict[str, str] = Field(
        title="Span 属性信息",
        description="Span 属性信息",
    )
    Resource: Dict[str, str] = Field(
        title="Span 资源信息",
        description="Span 资源信息",
    )


class ListTraceSpansResponse(BaseModel):
    Total: int = Field(
        title="总记录数",
        description="总记录数",
        example=1,
    )
    HasMore: bool = Field(
        title="是否有更多数据",
        description="是否有更多数据",
        example=False,
    )
    Items: List[TraceSpanItem] = Field(
        title="Span 列表",
        description="Span 列表",
    )
