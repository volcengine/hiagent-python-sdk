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
import os
import json

from dotenv import load_dotenv

from hiagent_api.workflow import WorkflowService
from hiagent_api.workflow_types import QueryWorkflowStatusRequest, RunWorkflowRequest
import asyncio

load_dotenv()

async def main():
    svc = WorkflowService(
        endpoint=os.getenv('HIAGENT_TOP_ENDPOINT'),
        region='cn-north-1')

    app_key = os.getenv('HIAGENT_APP_KEY')

    svc.set_app_base_url(os.getenv('HIAGENT_APP_BASE_URL'))

    resp = await svc.arun_workflow_async(app_key, RunWorkflowRequest(
        input_data=json.dumps({
            "query": "你好"
        }, ensure_ascii=False),
        user_id="test",
        app_key=app_key,
    ))
    print(resp)

    run_id = resp.run_id
    while True:
        resp = await svc.aquery_workflow_status(app_key, QueryWorkflowStatusRequest(
            app_key=app_key,
            run_id=run_id,
            user_id="test",
        ))
        print(resp)
        if resp.status in ["success", "stopped", "failed", "interrupted"]:
            break
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
