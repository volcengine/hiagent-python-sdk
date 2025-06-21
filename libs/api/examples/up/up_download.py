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
import hashlib
import os

from dotenv import load_dotenv

from hiagent_api.up import UpService
from hiagent_api import up_types

load_dotenv()


if __name__ == '__main__':
    up_upload = UpService(
        endpoint=os.getenv('HIAGENT_UP_UPLOAD_ENDPOINT'),
        region='cn-north-1')
    path = 'upload/full/5d/63/1c350f57f9024d9a2f1aa84dc4ac86c555aa066e6e52621a7e230a88e442'
    save_to = os.path.join(os.path.dirname(
        os.path.abspath(__file__)),  'test_data', 'download.txt')
    download_key_resp = up_upload.DownloadKey(
        up_types.DownloadKeyRequest(Path=path))
    assert len(download_key_resp.Key) > 10, "Key length should be greater than 10"

    up_download = UpService(
        endpoint=os.getenv('HIAGENT_UP_DOWNLOAD_ENDPOINT'),
        region='cn-north-1')

    up_download.Download(up_types.DownloadRequest(
        Path=path, Key=download_key_resp.Key, SaveTo=save_to))
    test_file_hash = hashlib.sha256(open(save_to, 'rb').read()).hexdigest()
    assert test_file_hash == '5d631c350f57f9024d9a2f1aa84dc4ac86c555aa066e6e52621a7e230a88e442', "SHA256 mismatch"
