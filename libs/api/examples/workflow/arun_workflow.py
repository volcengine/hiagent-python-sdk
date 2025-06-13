# coding:utf-8
import os
import json

from dotenv import load_dotenv

from hiagent_api.workflow import WorkflowService
from hiagent_api.workflow_types import RunWorkflowRequest
import asyncio

load_dotenv()

async def main():
    svc = WorkflowService(
        endpoint=os.getenv('HIAGENT_TOP_ENDPOINT'),
        region='cn-north-1')

    app_key = os.getenv('HIAGENT_APP_KEY')

    svc.set_app_base_url(os.getenv('HIAGENT_APP_BASE_URL'))

    resp = await svc.arun_workflow(app_key, RunWorkflowRequest(
        input_data=json.dumps({
            "query": "你好"
        }, ensure_ascii=False),
        user_id="test",
        app_key=app_key,
    ))
    print(resp)

if __name__ == '__main__':
    asyncio.run(main())
