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
from hiagent_api.tool import ToolService
from hiagent_api.tool_types import ExecArchivedToolRequest, GetArchivedToolRequest

load_dotenv()

def main():
    svc = ToolService(
        endpoint=os.getenv('HIAGENT_TOP_ENDPOINT'),
        region='cn-north-1')

    tool_id = "rgnadh3poolns0v5sa10"
    workspace_id = "cuq0pp9s7366bfl0cns0"

    resp = svc.get_archived_tool(GetArchivedToolRequest(
        id=tool_id,
        workspace_id=workspace_id,
    ))
    print(resp)

    resp = svc.exec_archived_tool(ExecArchivedToolRequest(
        workspace_id=workspace_id,
        plugin_id=resp.plugin_id,
        tool_id=tool_id,
        config="",
        input_data='{"query": "llm"}'
    ))

    print(resp)

if __name__ == '__main__':
    main()
