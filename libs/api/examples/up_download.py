# coding:utf-8
import hashlib
import os

from dotenv import load_dotenv

from hiagent_api.up import UpService
from hiagent_api import up_types

load_dotenv()


if __name__ == '__main__':
    up_upload = UpService(
        endpoint=os.getenv('HIAGENT_UP_UPLOAD_ENDPOINT'),
        region='cn-north-1')
    path = 'upload/full/5d/63/1c350f57f9024d9a2f1aa84dc4ac86c555aa066e6e52621a7e230a88e442'
    save_to = os.path.join(os.path.dirname(
        os.path.abspath(__file__)),  'test_data', 'download.txt')
    download_key_resp = up_upload.DownloadKey(
        up_types.DownloadKeyRequest(Path=path))
    assert len(download_key_resp.Key) > 10, "Key length should be greater than 10"

    up_download = UpService(
        endpoint=os.getenv('HIAGENT_UP_DOWNLOAD_ENDPOINT'),
        region='cn-north-1')

    up_download.Download(up_types.DownloadRequest(
        Path=path, Key=download_key_resp.Key, SaveTo=save_to))
    test_file_hash = hashlib.sha256(open(save_to, 'rb').read()).hexdigest()
    assert test_file_hash == '5d631c350f57f9024d9a2f1aa84dc4ac86c555aa066e6e52621a7e230a88e442', "SHA256 mismatch"
