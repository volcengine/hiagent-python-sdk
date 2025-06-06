# coding:utf-8
from pydantic import BaseModel, Field


class CreateApiTokenRequest(BaseModel):
    WorkspaceID: str = Field(
        title="工作空间 ID",
        description="工作空间 ID",
        example="wcxxxxxxxxxxxxxxxxxxx"
    )
    CustomAppID: str = Field(
        title="自定义应用 ID",
        description="自定义应用 ID",
        example="appxxxxxxxxxxxxxxxxxxx"
    )


class CreateApiTokenResponse(BaseModel):
    Token: str = Field(
        title="API Token",
        description="API Token",
        example="wcxxxxxxxxxxxxxxxxxxx"
    )
    ExpiresIn: int = Field(
        title="有效时间",
        description="有效时间，单位为秒",
        example=3600
    )
