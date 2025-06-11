# coding:utf-8
import os
from dotenv import load_dotenv

from hiagent_api.up import UpService
from hiagent_api import up_types

load_dotenv()


if __name__ == '__main__':
    up = UpService(
        endpoint=os.getenv('HIAGENT_UP_UPLOAD_ENDPOINT'),
        region='cn-north-1')
    path = 'upload/full/5d/63/1c350f57f9024d9a2f1aa84dc4ac86c555aa066e6e52621a7e230a88e442'
    resp = up.DownloadKey(up_types.DownloadKeyRequest(Path=path))
    assert len(resp.Key) > 10, "Key length should be greater than 10"
