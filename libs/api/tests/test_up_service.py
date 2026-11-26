import io
import json

import pytest
import volcengine
from hiagent_api import up_types
from hiagent_api.product_code import PRODUCT_CODE_HEADER
from up_fakes import (
    AK,
    assert_signed_as_sent,
    envelope,
    make_service,
    response,
    sha256_hex,
)

CONTENT = b"hello up service\n" * 64
UPPER_SHA = "AB" * 32
LOWER_SHA = "ab" * 32
UPLOAD_RESULT = {"Path": "/upload/full/x", "Sha256": LOWER_SHA, "Size": 3}
LONG_LIVE_RESULT = {"Path": "/upload/full/x", "Size": 3}


def _ok(result):
    return lambda sent: envelope(result)


class Untouchable(io.RawIOBase):
    """A file object the SDK must not read, seek or inspect."""

    def read(self, *args):
        raise AssertionError("file was read")

    def seekable(self):
        raise AssertionError("file was inspected")

    def tell(self):
        raise AssertionError("file was inspected")


class OneShotStream(io.RawIOBase):
    """A readable, non-seekable stream."""

    def __init__(self, data: bytes):
        self._buffer = io.BytesIO(data)

    def readable(self):
        return True

    def seekable(self):
        return False

    def readinto(self, b):
        chunk = self._buffer.read(len(b))
        b[: len(chunk)] = chunk
        return len(chunk)


def _call_each_action(service):
    service.UploadRaw(up_types.UploadRawRequest(Id="file-0001"), io.BytesIO(CONTENT))
    service.LongLive(up_types.LongLiveRequest(Path="/p", Id="file-0001"))
    service.DownloadKey(up_types.DownloadKeyRequest(Path="/p"))
    service.Delete(up_types.DeleteRequest(Id="file-0001", Sha256=LOWER_SHA))


def _respond_by_action(sent):
    action = sent.query["Action"]
    if action == "UploadRaw":
        return envelope(UPLOAD_RESULT)
    if action == "LongLive":
        return envelope(LONG_LIVE_RESULT)
    if action == "DownloadKey":
        return envelope({"Key": "k"})
    if action == "Delete":
        return envelope({})
    return response(body=CONTENT, headers={"Content-Length": str(len(CONTENT))})


# --- signing and the shared request shape -----------------------------------


def test_every_action_is_a_signed_post(tmp_path):
    service, adapter = make_service(_respond_by_action)
    _call_each_action(service)
    service.Download(
        up_types.DownloadRequest(Key="k", Path="/p", SaveTo=str(tmp_path / "f"))
    )

    assert [s.query["Action"] for s in adapter.sent] == [
        "UploadRaw",
        "LongLive",
        "DownloadKey",
        "Delete",
        "Download",
    ]
    for sent in adapter.sent:
        assert sent.method == "POST"
        assert sent.query["Version"] == "2022-01-01"
        assert sent.headers["User-Agent"] == "volc-sdk-python/" + volcengine.VERSION
        assert "Signature" not in sent.query and "X-Signature" not in sent.query
        assert "SignedHeaders=x-content-sha256;x-date," in sent.headers["Authorization"]
        assert_signed_as_sent(sent)
    assert [s.path for s in adapter.sent] == ["/up", "/up", "/up", "/up", "/down"]


def test_product_code_is_sent_but_not_signed():
    service, adapter = make_service(_respond_by_action, product_code=" maas ")
    _call_each_action(service)
    for sent in adapter.sent:
        assert sent.headers[PRODUCT_CODE_HEADER] == "maas"
        assert_signed_as_sent(sent)


def test_no_product_code_header_by_default():
    service, adapter = make_service(_respond_by_action)
    _call_each_action(service)
    assert all(PRODUCT_CODE_HEADER not in s.headers for s in adapter.sent)


def test_merges_default_headers_case_insensitively_without_mutating_them():
    service, adapter = make_service(_ok({}))
    service.service_info.header["content-type"] = "text/html"
    before = dict(service.service_info.header)
    service.Delete(up_types.DeleteRequest(Id="file-0001", Sha256=LOWER_SHA))
    sent = adapter.sent[0]
    content_types = [k for k in sent.headers if k.lower() == "content-type"]
    assert len(content_types) == 1
    assert sent.headers["Content-Type"] == "application/json"
    assert service.service_info.header == before


def test_reads_credentials_at_call_time():
    service, adapter = make_service(_ok({}))
    service.set_ak("AKLTrotated")
    service.set_sk("rotated-secret")
    service.Delete(up_types.DeleteRequest(Id="file-0001", Sha256=LOWER_SHA))
    sent = adapter.sent[0]
    assert "Credential=AKLTrotated/" in sent.headers["Authorization"]
    assert_signed_as_sent(sent, ak="AKLTrotated", sk="rotated-secret")


def test_sts_token_is_sent_stripped():
    service, adapter = make_service(_ok({}))
    service.set_session_token("sts-token\n")
    service.Delete(up_types.DeleteRequest(Id="file-0001", Sha256=LOWER_SHA))
    sent = adapter.sent[0]
    assert sent.headers["X-Security-Token"] == "sts-token"
    assert_signed_as_sent(sent, token="sts-token")


def test_without_any_credentials_requests_go_out_unsigned():
    service, adapter = make_service(_respond_by_action, ak="", sk="")
    _call_each_action(service)
    for sent in adapter.sent:
        assert "Authorization" not in sent.headers
        assert "X-Date" not in sent.headers
        assert sent.headers["X-Content-Sha256"] == sha256_hex(sent.body)


@pytest.mark.parametrize("ak, sk", [(AK, ""), ("", "secret"), ("  ", "secret")])
def test_half_configured_credentials_fail_before_sending(ak, sk):
    service, adapter = make_service(_ok({}), ak=ak, sk=sk)
    with pytest.raises(ValueError):
        service.Delete(up_types.DeleteRequest(Id="file-0001", Sha256=LOWER_SHA))
    assert adapter.sent == []


def test_session_token_without_keys_fails_before_sending():
    service, adapter = make_service(_ok({}), ak="", sk="")
    service.set_session_token("sts-token")
    with pytest.raises(ValueError):
        service.Delete(up_types.DeleteRequest(Id="file-0001", Sha256=LOWER_SHA))
    assert adapter.sent == []


@pytest.mark.parametrize("ak", ["AKLTleaked\n", "AKLT\nleaked"])
def test_invalid_access_key_does_not_leak(ak):
    service, adapter = make_service(_ok({}), ak=ak)
    with pytest.raises(ValueError) as excinfo:
        service.Delete(up_types.DeleteRequest(Id="file-0001", Sha256=LOWER_SHA))
    assert "leaked" not in str(excinfo.value)
    assert adapter.sent == []


def test_non_200_raises_with_body():
    service, _ = make_service(lambda sent: response(400, b'{"error":"bad"}'))
    with pytest.raises(Exception, match="bad"):
        service.Delete(up_types.DeleteRequest(Id="file-0001", Sha256=LOWER_SHA))


def test_non_200_without_body_raises_with_status():
    service, _ = make_service(lambda sent: response(503))
    with pytest.raises(Exception, match="503"):
        service.Delete(up_types.DeleteRequest(Id="file-0001", Sha256=LOWER_SHA))


@pytest.mark.parametrize("status", [301, 302, 307, 308])
def test_redirect_is_not_followed(status):
    location = "https://elsewhere.example.com/up"
    service, adapter = make_service(
        lambda sent: response(status, b"moved", {"Location": location})
    )
    service.set_session_token("sts-token")
    with pytest.raises(Exception) as excinfo:
        service.Delete(up_types.DeleteRequest(Id="file-0001", Sha256=LOWER_SHA))
    assert len(adapter.sent) == 1
    assert str(status) in str(excinfo.value)
    assert location in str(excinfo.value)


@pytest.mark.parametrize("action", ["UploadRaw", "LongLive", "DownloadKey", "Delete"])
def test_missing_result_raises(action):
    service, _ = make_service(_ok(None))
    calls = {
        "UploadRaw": lambda: service.UploadRaw(
            up_types.UploadRawRequest(Id="file-0001"), io.BytesIO(CONTENT)
        ),
        "LongLive": lambda: service.LongLive(
            up_types.LongLiveRequest(Path="/p", Id="file-0001")
        ),
        "DownloadKey": lambda: service.DownloadKey(up_types.DownloadKeyRequest(Path="/p")),
        "Delete": lambda: service.Delete(
            up_types.DeleteRequest(Id="file-0001", Sha256=LOWER_SHA)
        ),
    }
    with pytest.raises(Exception, match="no Result in response"):
        calls[action]()


# --- UploadRaw --------------------------------------------------------------


def test_upload_raw_old_form_sends_header_values_and_query_params():
    service, adapter = make_service(_ok(UPLOAD_RESULT))
    req = up_types.UploadRawRequest(
        Expire="15h", Id="file-0001", ContentType="text/plain", Sha256=" " + UPPER_SHA
    )
    result = service.UploadRaw(req, io.BytesIO(CONTENT))

    sent = adapter.sent[0]
    assert sent.query == {
        "Action": "UploadRaw",
        "Version": "2022-01-01",
        "Expire": "15h",
        "Id": "file-0001",
    }
    assert sent.headers["Content-Type"] == "text/plain"
    assert sent.headers["X-Content-Sha256"] == LOWER_SHA
    assert sent.body == CONTENT
    assert req.Sha256 == " " + UPPER_SHA
    assert result == up_types.UploadRawResponse(**UPLOAD_RESULT)


def test_upload_raw_sends_new_query_fields_including_false():
    service, adapter = make_service(_ok(UPLOAD_RESULT))
    req = up_types.UploadRawRequest(
        Id="file-0001", Filename="中文 a+b.pdf", ImageCompress=False
    )
    service.UploadRaw(req, io.BytesIO(CONTENT))
    sent = adapter.sent[0]
    assert sent.query["Filename"] == "中文 a+b.pdf"
    assert sent.query["ImageCompress"] == "false"
    assert "Expire" not in sent.query
    assert "Sha256" not in sent.query and "ContentType" not in sent.query
    assert sent.headers["Content-Type"] == "application/octet-stream"
    assert_signed_as_sent(sent)


@pytest.mark.parametrize("sha", [None, "", "   "])
def test_upload_raw_computes_sha256_when_not_given(sha):
    service, adapter = make_service(_ok(UPLOAD_RESULT))
    service.UploadRaw(up_types.UploadRawRequest(Id="file-0001", Sha256=sha), io.BytesIO(CONTENT))
    sent = adapter.sent[0]
    assert sent.body == CONTENT
    assert sent.headers["X-Content-Sha256"] == sha256_hex(CONTENT)


def test_upload_raw_hashes_and_sends_from_current_position():
    service, adapter = make_service(_ok(UPLOAD_RESULT))
    file = io.BytesIO(CONTENT)
    file.seek(5)
    service.UploadRaw(up_types.UploadRawRequest(Id="file-0001"), file)
    sent = adapter.sent[0]
    assert sent.body == CONTENT[5:]
    assert sent.headers["X-Content-Sha256"] == sha256_hex(CONTENT[5:])


def test_upload_raw_streams_unseekable_input_when_sha256_given():
    service, adapter = make_service(_ok(UPLOAD_RESULT))
    req = up_types.UploadRawRequest(Id="file-0001", Sha256=sha256_hex(CONTENT))
    service.UploadRaw(req, io.BufferedReader(OneShotStream(CONTENT)))
    assert adapter.sent[0].body == CONTENT


def test_upload_raw_rejects_unseekable_input_without_sha256():
    service, adapter = make_service(_ok(UPLOAD_RESULT))
    with pytest.raises(ValueError, match="Sha256"):
        service.UploadRaw(
            up_types.UploadRawRequest(Id="file-0001"),
            io.BufferedReader(OneShotStream(CONTENT)),
        )
    assert adapter.sent == []


def test_upload_raw_rejects_empty_id_before_touching_the_file():
    service, adapter = make_service(_ok(UPLOAD_RESULT))
    with pytest.raises(ValueError, match="Id"):
        service.UploadRaw(up_types.UploadRawRequest(Id=""), Untouchable())
    with pytest.raises(ValueError, match="Id"):
        service.UploadRaw(up_types.UploadRawRequest.model_construct(Id=None), Untouchable())
    assert adapter.sent == []


def test_upload_raw_passes_blank_id_through_to_up():
    service, adapter = make_service(_ok(UPLOAD_RESULT))
    service.UploadRaw(up_types.UploadRawRequest(Id="  "), io.BytesIO(CONTENT))
    assert adapter.sent[0].query["Id"] == "  "
    assert_signed_as_sent(adapter.sent[0])


# --- LongLive / DownloadKey / Delete -----------------------------------------


def test_long_live_sends_upper_id_in_json_body():
    service, adapter = make_service(_ok({**LONG_LIVE_RESULT, "ShortLink": "s"}))
    result = service.LongLive(
        up_types.LongLiveRequest(Path="/p", Id="file-0001", Filename="a.pdf")
    )
    sent = adapter.sent[0]
    assert sent.json() == {"Path": "/p", "ID": "file-0001", "Filename": "a.pdf"}
    assert sent.headers["Content-Type"] == "application/json"
    assert set(sent.query) == {"Action", "Version"}
    assert result.ShortLink == "s"


def test_long_live_rejects_empty_id_without_sending():
    service, adapter = make_service(_ok(LONG_LIVE_RESULT))
    with pytest.raises(ValueError, match="ID"):
        service.LongLive(up_types.LongLiveRequest(Path="/p", Id=""))
    assert adapter.sent == []


def test_download_key_sends_lowercased_query_and_empty_body():
    service, adapter = make_service(_ok({"Key": "k", "Size": 3, "ContentType": "text/plain"}))
    req = up_types.DownloadKeyRequest(Sha256=UPPER_SHA)
    result = service.DownloadKey(req)
    sent = adapter.sent[0]
    assert sent.query["Sha256"] == LOWER_SHA
    assert "Path" not in sent.query
    assert sent.body == b""
    assert req.Sha256 == UPPER_SHA
    assert (result.Key, result.Size, result.ContentType) == ("k", 3, "text/plain")


def test_delete_sends_lowercased_sha256_and_returns_result():
    service, adapter = make_service(_ok({}))
    req = up_types.DeleteRequest(Id="file-0001", Sha256=UPPER_SHA)
    assert service.Delete(req) == {}
    sent = adapter.sent[0]
    assert sent.json() == {"Id": "file-0001", "Sha256": LOWER_SHA}
    assert json.loads(sent.body) == sent.json()
    assert req.Sha256 == UPPER_SHA
