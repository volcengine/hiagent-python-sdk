# coding:utf-8
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
