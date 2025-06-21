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

from dotenv import load_dotenv

from hiagent_api.workflow import WorkflowService
from hiagent_api.workflow_types import GetWorkflowRequest

load_dotenv()

def main():
    svc = WorkflowService(
        endpoint=os.getenv('HIAGENT_TOP_ENDPOINT'),
        region='cn-north-1')

    svc.set_app_base_url(os.getenv('HIAGENT_APP_BASE_URL'))

    resp = svc.get_workflow(GetWorkflowRequest(
        id="cvel84kg58epjrfkvtb0",
        workspace_id="cuq0pp9s7366bfl0cns0",
    ))
    print(resp)

if __name__ == '__main__':
    main()
