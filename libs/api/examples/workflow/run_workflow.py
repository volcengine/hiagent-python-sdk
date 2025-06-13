# coding:utf-8
import os
import json

from dotenv import load_dotenv

from hiagent_api.workflow import WorkflowService
from hiagent_api.workflow_types import RunWorkflowRequest

load_dotenv()

if __name__ == '__main__':
    svc = WorkflowService(
        endpoint=os.getenv('HIAGENT_TOP_ENDPOINT'),
        region='cn-north-1')

    app_key = os.getenv('HIAGENT_APP_KEY')

    svc.set_app_base_url(os.getenv('HIAGENT_APP_BASE_URL'))

    resp = svc.run_workflow(app_key, RunWorkflowRequest(
        input_data=json.dumps({
            "query": "你好"
        }, ensure_ascii=False),
        user_id="test",
        app_key=app_key,
    ))
    print(resp)