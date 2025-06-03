import os

from dotenv import load_dotenv

from libs.api.observe import ObserveService
from libs.observe.client import Client

load_dotenv()


if __name__ == '__main__':
    Client(
        trace_endpoint=os.getenv('HIAGENT_TOP_ENDPOINT'),
        top_endpoint=os.getenv('HIAGENT_TRACE_ENDPOINT'),
        ak=os.getenv('VOLC_ACCESSKEY'),
        sk=os.getenv('VOLC_SECRETKEY'),
        workspace_id=os.getenv('WORKSPACE_ID')
    )
    observe = ObserveService(
        endpoint=os.getenv('HIAGENT_ENDPOINT'), region='cn-north-1')

    token = observe.CreateApiToken({"WorkspaceID": "d0m7h41u1vks72oifgig"})

    print(token)
