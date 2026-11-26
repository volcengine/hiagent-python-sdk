import pydantic
import pytest
from hiagent_api import up_types


def test_upload_raw_request_old_form_still_works():
    req = up_types.UploadRawRequest(
        Expire="15h", Id="file-0001", ContentType="text/plain", Sha256="ab" * 32
    )
    assert (req.Expire, req.Id, req.ContentType, req.Sha256) == (
        "15h",
        "file-0001",
        "text/plain",
        "ab" * 32,
    )


def test_upload_raw_request_only_requires_id():
    req = up_types.UploadRawRequest(Id="file-0001")
    assert req.Expire is None
    assert req.ContentType is None
    assert req.Sha256 is None
    assert req.Filename is None
    assert req.ImageCompress is None
    with pytest.raises(pydantic.ValidationError):
        up_types.UploadRawRequest()


def test_validation_error_is_a_value_error():
    assert issubclass(pydantic.ValidationError, ValueError)


def test_long_live_request_serializes_id_as_upper_id():
    req = up_types.LongLiveRequest(Path="/p", Id="file-0001", Filename="a.pdf")
    assert req.Id == "file-0001"
    assert req.model_dump(by_alias=True, exclude_none=True) == {
        "Path": "/p",
        "ID": "file-0001",
        "Filename": "a.pdf",
    }
    with pytest.raises(pydantic.ValidationError):
        up_types.LongLiveRequest(Path="/p")


def test_download_key_request_accepts_path_or_sha256():
    assert up_types.DownloadKeyRequest(Path="/p").Sha256 is None
    assert up_types.DownloadKeyRequest(Sha256="ab" * 32).Path is None


def test_download_request_never_dumps_save_to():
    req = up_types.DownloadRequest(
        Key="k", Sha256="ab" * 32, ID="file-0001", SaveTo="/tmp/x", ImageCompress=False
    )
    dumped = req.model_dump(by_alias=True, exclude_none=True)
    assert "SaveTo" not in dumped
    assert dumped == {
        "Key": "k",
        "Sha256": "ab" * 32,
        "ID": "file-0001",
        "ImageCompress": False,
    }
    assert req.SaveTo == "/tmp/x"
    assert up_types.DownloadRequest(Key="k", Path="/p", SaveTo="x").Path == "/p"


def test_responses_parse_new_fields_and_default_to_none():
    upload = up_types.UploadRawResponse.model_validate(
        {
            "Path": "/p",
            "Sha256": "ab" * 32,
            "Size": 3_000_000_000,
            "ShortLink": "s",
            "PresignKey": "pk",
        }
    )
    assert (upload.Size, upload.ShortLink, upload.PresignKey) == (3_000_000_000, "s", "pk")
    assert up_types.UploadRawResponse.model_validate(
        {"Path": "/p", "Sha256": "ab" * 32, "Size": 1}
    ).ShortLink is None

    long_live = up_types.LongLiveResponse.model_validate(
        {"Path": "/p", "Size": 1, "Sha256": "ab" * 32, "ShortLink": "s"}
    )
    assert (long_live.Sha256, long_live.ShortLink) == ("ab" * 32, "s")
    assert up_types.LongLiveResponse.model_validate({"Path": "/p", "Size": 1}).Sha256 is None

    key = up_types.DownloadKeyResponse.model_validate(
        {"Key": "k", "Size": 1, "ContentType": "text/plain"}
    )
    assert (key.Size, key.ContentType) == (1, "text/plain")
    assert up_types.DownloadKeyResponse.model_validate({"Key": "k"}).Size is None
