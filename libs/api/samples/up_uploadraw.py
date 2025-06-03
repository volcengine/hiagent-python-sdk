# coding:utf-8
import hashlib
import os
import uuid

from dotenv import load_dotenv

from libs.api.up import UpService
from libs.api.up_types import UploadRawRequest

load_dotenv()

if __name__ == '__main__':
    up = UpService(
        endpoint=os.getenv('HIAGENT_UP_UPLOAD_ENDPOINT'),
        region='cn-north-1')
    test_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "test_data/test.txt")
    test_file_hash = hashlib.sha256(open(test_file, 'rb').read()).hexdigest()
    req_params = UploadRawRequest(Id=uuid.uuid4().hex,
                                  ContentType="plain/text",
                                  Expire="15h",
                                  Sha256=test_file_hash)
    with open(test_file, "rb") as f:
        resp = up.UploadRaw(req_params, file=f)
        assert resp.Sha256 == test_file_hash, "SHA256 mismatch"
