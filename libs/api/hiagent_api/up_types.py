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
from pydantic import BaseModel, Field


class UploadRawRequest(BaseModel):
    Expire: str = Field(
        title="文件的过期时间", description="文件的过期时间", example="15h"
    )
    Id: str = Field(
        title="文件 ID", description="文件 ID", example="wcxxxxxxxxxxxxxxxxxxx"
    )
    ContentType: str = Field(
        title="content type",
        description="content type",
        example="application/octet-stream",
    )
    Sha256: str = Field(
        title="文件的哈希值", description="文件的哈希值", example="sha256hashvalue"
    )


class UploadRawResponse(BaseModel):
    Path: str = Field(title="文件路径", description="文件路径", example="/path/to/file")
    Sha256: str = Field(
        title="文件的哈希值", description="文件的哈希值", example="sha256hashvalue"
    )
    Size: int = Field(
        title="文件的大小", description="文件的大小，单位为字节", example=1024
    )


class LongLiveRequest(BaseModel):
    Path: str = Field(title="文件路径", description="文件路径", example="/path/to/file")
    Id: str = Field(
        title="文件 ID", description="文件 ID", example="wcxxxxxxxxxxxxxxxxxxx"
    )


class LongLiveResponse(BaseModel):
    Path: str = Field(title="文件路径", description="文件路径", example="/path/to/file")
    Size: int = Field(
        title="文件的大小", description="文件的大小，单位为字节", example=1024
    )


class DownloadKeyRequest(BaseModel):
    Path: str = Field(title="文件路径", description="文件路径", example="/path/to/file")


class DownloadKeyResponse(BaseModel):
    Key: str = Field(title="文件 key", description="文件 key", example="filekey")


class DownloadRequest(BaseModel):
    Key: str = Field(title="文件 key", description="文件 key", example="filekey")
    Path: str = Field(title="文件路径", description="文件路径", example="/path/to/file")
    SaveTo: str = Field(
        title="保存路径", description="保存路径", example="/path/to/file"
    )


class DownloadResponse(BaseModel):
    pass


class DeleteRequest(BaseModel):
    Id: str = Field(
        title="文件 ID", description="文件 ID", example="wcxxxxxxxxxxxxxxxxxxx"
    )
    Sha256: str = Field(
        title="文件的哈希值", description="文件的哈希值", example="sha256hashvalue"
    )


class DeleteResponse(BaseModel):
    pass
