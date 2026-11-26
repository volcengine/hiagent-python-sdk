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
from typing import Optional

from pydantic import BaseModel, Field

_SHA256_EXAMPLE = "84add60e154d3625fa5424bfb98bdc5782a078853a4a2c0845b906985ebceb8c"


class UploadRawRequest(BaseModel):
    Id: str = Field(
        title="文件 ID",
        description="文件 ID，必填。删除文件时需要传同一个 ID",
        example="wcxxxxxxxxxxxxxxxxxxx",
    )
    Expire: Optional[str] = Field(
        default=None,
        title="关联的过期时间",
        description="Go duration 格式，如 15h；不传、空串、0 或 -1 表示不过期",
        example="15h",
    )
    ContentType: Optional[str] = Field(
        default=None,
        title="content type",
        description="文件的真实类型；不传时按 application/octet-stream 上传",
        example="image/png",
    )
    Sha256: Optional[str] = Field(
        default=None,
        title="文件的哈希值",
        description="文件的 SHA-256；不传或为空白时 SDK 先流式计算一遍",
        example=_SHA256_EXAMPLE,
    )
    Filename: Optional[str] = Field(
        default=None, title="文件名", description="文件名", example="hello.pdf"
    )
    ImageCompress: Optional[bool] = Field(
        default=None, title="图片压缩", description="是否开启图片压缩", example=True
    )


class UploadRawResponse(BaseModel):
    Path: str = Field(title="文件路径", description="文件路径", example="/path/to/file")
    Sha256: str = Field(
        title="文件的哈希值", description="文件的哈希值", example=_SHA256_EXAMPLE
    )
    Size: int = Field(
        title="文件的大小", description="文件的大小，单位为字节", example=1024
    )
    ShortLink: Optional[str] = Field(
        default=None, title="文件短链", description="文件短链", example="JAVwLYB3XVr"
    )
    PresignKey: Optional[str] = Field(
        default=None, title="presign key", description="presign key", example="xxxxxxx"
    )


class LongLiveRequest(BaseModel):
    Path: str = Field(title="文件路径", description="文件路径", example="/path/to/file")
    Id: str = Field(
        title="文件 ID",
        description="文件 ID，必填。请求体中按 UP 契约以 ID 发送",
        example="wcxxxxxxxxxxxxxxxxxxx",
        serialization_alias="ID",
    )
    Filename: Optional[str] = Field(
        default=None, title="文件名", description="文件名", example="hello.pdf"
    )


class LongLiveResponse(BaseModel):
    Path: str = Field(title="文件路径", description="文件路径", example="/path/to/file")
    Size: int = Field(
        title="文件的大小", description="文件的大小，单位为字节", example=1024
    )
    Sha256: Optional[str] = Field(
        default=None, title="文件的哈希值", description="文件的哈希值", example=_SHA256_EXAMPLE
    )
    ShortLink: Optional[str] = Field(
        default=None, title="文件短链", description="文件短链", example="JAVwLYB3XVr"
    )


class DownloadKeyRequest(BaseModel):
    Path: Optional[str] = Field(
        default=None,
        title="文件路径",
        description="文件路径，与 Sha256 二选一",
        example="/path/to/file",
    )
    Sha256: Optional[str] = Field(
        default=None,
        title="文件的哈希值",
        description="文件的 SHA-256，与 Path 二选一",
        example=_SHA256_EXAMPLE,
    )


class DownloadKeyResponse(BaseModel):
    Key: str = Field(title="文件 key", description="文件 key", example="filekey")
    Size: Optional[int] = Field(
        default=None, title="文件的大小", description="文件的大小，单位为字节", example=1024
    )
    ContentType: Optional[str] = Field(
        default=None, title="content type", description="content type", example="image/png"
    )


class DownloadRequest(BaseModel):
    Key: str = Field(title="文件 key", description="文件 key", example="filekey")
    Path: Optional[str] = Field(
        default=None,
        title="文件路径",
        description="文件路径，与 Sha256 二选一",
        example="/path/to/file",
    )
    Sha256: Optional[str] = Field(
        default=None,
        title="文件的哈希值",
        description="文件的 SHA-256，与 Path 二选一",
        example=_SHA256_EXAMPLE,
    )
    ID: Optional[str] = Field(
        default=None,
        title="文件 ID",
        description="文件 ID，影响响应中的文件名",
        example="wcxxxxxxxxxxxxxxxxxxx",
    )
    Filename: Optional[str] = Field(
        default=None, title="文件名", description="文件名", example="hello.pdf"
    )
    ImageCompress: Optional[bool] = Field(
        default=None, title="图片压缩", description="是否下载压缩后的图片", example=True
    )
    SaveTo: str = Field(
        title="保存路径",
        description="本地保存路径，只在本地使用，不会发送给 UP",
        example="/path/to/file",
        exclude=True,
    )


class DownloadResponse(BaseModel):
    pass


class DeleteRequest(BaseModel):
    Id: str = Field(
        title="文件 ID", description="文件 ID", example="wcxxxxxxxxxxxxxxxxxxx"
    )
    Sha256: str = Field(
        title="文件的哈希值", description="文件的哈希值", example=_SHA256_EXAMPLE
    )


class DeleteResponse(BaseModel):
    pass
