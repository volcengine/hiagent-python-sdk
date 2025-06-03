# coding:utf-8
import hashlib
import os
import uuid

from dotenv import load_dotenv

from libs.api.up import UpService
from libs.api import up_types

load_dotenv()


if __name__ == '__main__':
    up = UpService(
        endpoint=os.getenv('HIAGENT_UP_UPLOAD_ENDPOINT'),
        region='cn-north-1')
    path = 'upload/full/5d/63/1c350f57f9024d9a2f1aa84dc4ac86c555aa066e6e52621a7e230a88e442'
    test_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "test_data/test.txt")
    test_file_hash = hashlib.sha256(open(test_file, 'rb').read()).hexdigest()

    path = 'upload/full/5d/63/1c350f57f9024d9a2f1aa84dc4ac86c555aa066e6e52621a7e230a88e442'
    id = uuid.uuid4().hex
    resp = up.LongLive(up_types.LongLiveRequest(
        Path=path, Id=id))

    up.Delete(up_types.DeleteRequest(Sha256=test_file_hash, Id=id))
