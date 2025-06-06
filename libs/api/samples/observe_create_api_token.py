# coding:utf-8
import os

from dotenv import load_dotenv

from libs.api.observe import ObserveService

load_dotenv()


if __name__ == '__main__':
    observe = ObserveService(
        endpoint=os.getenv('HIAGENT_TOP_ENDPOINT'),
        region='cn-north-1')

    token = observe.CreateApiToken({"WorkspaceID": os.getenv('WORKSPACE_ID')})

    print(token)
