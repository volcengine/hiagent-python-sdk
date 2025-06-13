# coding:utf-8
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
