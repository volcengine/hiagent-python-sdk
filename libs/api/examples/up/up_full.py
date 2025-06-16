# coding:utf-8
import hashlib
import os
import uuid
from dotenv import load_dotenv

from hiagent_api.up import UpService
from hiagent_api import up_types

load_dotenv()


if __name__ == '__main__':
    up_upload = UpService(
        endpoint=os.getenv('HIAGENT_UP_UPLOAD_ENDPOINT'),
        region='cn-north-1')

    up_download = UpService(
        endpoint=os.getenv('HIAGENT_UP_DOWNLOAD_ENDPOINT'),
        region='cn-north-1')

    # 1. 上传文件
    test_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "test_data/test.txt")
    test_file_hash = hashlib.sha256(open(test_file, 'rb').read()).hexdigest()
    req_params = up_types.UploadRawRequest(Id=uuid.uuid4().hex,
                                           ContentType="plain/text",
                                           Expire="15h",
                                           Sha256=test_file_hash)
    uploadraw_resp = {}
    with open(test_file, "rb") as f:
        uploadraw_resp = up_upload.UploadRaw(req_params, file=f)
        assert uploadraw_resp.Sha256 == test_file_hash, "SHA256 mismatch"

    # 2. 对文件持久化
    id = uuid.uuid4().hex
    longlive_resp = up_upload.LongLive(up_types.LongLiveRequest(
        Path=uploadraw_resp.Path, Id=id))
    assert longlive_resp.Path == uploadraw_resp.Path, "Path mismatch"

    # 3. 获取下载密钥
    downloadkey_resp = up_upload.DownloadKey(
        up_types.DownloadKeyRequest(Path=uploadraw_resp.Path))
    assert len(downloadkey_resp.Key) > 10, "Key length should be greater than 10"

    # 4. 下载文件
    save_to = os.path.join(os.path.dirname(
        os.path.abspath(__file__)),  'test_data', 'download.txt')
    up_download.Download(up_types.DownloadRequest(
        Path=uploadraw_resp.Path, Key=downloadkey_resp.Key, SaveTo=save_to))
    test_file_hash = hashlib.sha256(open(save_to, 'rb').read()).hexdigest()
    assert test_file_hash == '5d631c350f57f9024d9a2f1aa84dc4ac86c555aa066e6e52621a7e230a88e442', "SHA256 mismatch"

    # 5. 删除文件
    up_upload.Delete(up_types.DeleteRequest(Sha256=test_file_hash, Id=id))
