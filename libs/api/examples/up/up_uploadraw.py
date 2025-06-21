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
import uuid

from dotenv import load_dotenv

from hiagent_api.up import UpService
from hiagent_api.up_types import UploadRawRequest

load_dotenv()

if __name__ == '__main__':
    up = UpService(
        endpoint=os.getenv('HIAGENT_UP_UPLOAD_ENDPOINT'),
        region='cn-north-1')
    test_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "test_data/test.txt")
    test_file_hash = hashlib.sha256(open(test_file, 'rb').read()).hexdigest()
    req_params = UploadRawRequest(Id=uuid.uuid4().hex,
                                  ContentType="plain/text",
                                  Expire="15h",
                                  Sha256=test_file_hash)
    with open(test_file, "rb") as f:
        resp = up.UploadRaw(req_params, file=f)
        assert resp.Sha256 == test_file_hash, "SHA256 mismatch"
