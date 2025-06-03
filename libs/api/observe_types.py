# coding:utf-8
from pydantic import BaseModel, Field


class CreateApiTokenRequest(BaseModel):
    """工作空间 ID"""
    WorkspaceID: str = Field(
        title="工作空间 ID",
        description="工作空间 ID",
        example="wcxxxxxxxxxxxxxxxxxxx"
    )


class CreateApiTokenResponse(BaseModel):
    """API Token 响应"""
    Token: str = Field(
        title="API Token",
        description="API Token",
        example="wcxxxxxxxxxxxxxxxxxxx"
    )
    """有效时间"""
    ExpitesIn: int = Field(
        title="有效时间",
        description="有效时间，单位为秒",
        example=3600
    )
