import io
import os
import stat
import sys

import pytest
from hiagent_api import up_types
from up_fakes import BrokenStream, assert_signed_as_sent, make_service, response

CONTENT = b"downloaded bytes " * 1024
OLD = b"previous content that must survive"
UPPER_SHA = "AB" * 32
LOWER_SHA = "ab" * 32


def _serve(body=CONTENT, status=200, headers=None, raw=None):
    if headers is None:
        headers = {"Content-Length": str(len(body))}
    served = []

    def respond(sent):
        resp = response(status, body, headers, raw)
        served.append(resp)
        return resp

    respond.served = served
    return respond


def _download(service, save_to, **fields):
    req = up_types.DownloadRequest(Key="k", Path="/p", SaveTo=str(save_to), **fields)
    return service.Download(req)


def _listing(directory):
    return sorted(os.listdir(directory))


def test_writes_file(tmp_path):
    service, adapter = make_service(_serve())
    target = tmp_path / "file.bin"
    assert _download(service, target) is None
    assert target.read_bytes() == CONTENT
    assert _listing(tmp_path) == ["file.bin"]
    assert_signed_as_sent(adapter.sent[0])


def test_missing_parent_directory_is_not_created(tmp_path):
    service, _ = make_service(_serve())
    with pytest.raises(FileNotFoundError):
        _download(service, tmp_path / "missing" / "file.bin")
    assert _listing(tmp_path) == []


def test_parameters_go_in_query_with_empty_body_and_no_save_to(tmp_path):
    service, adapter = make_service(_serve())
    req = up_types.DownloadRequest(
        Key="k",
        Sha256=UPPER_SHA,
        ID="file-0001",
        Filename="a.pdf",
        ImageCompress=False,
        SaveTo=str(tmp_path / "f"),
    )
    service.Download(req)
    sent = adapter.sent[0]
    assert sent.path == "/down"
    assert sent.query == {
        "Action": "Download",
        "Version": "2022-01-01",
        "Key": "k",
        "Sha256": LOWER_SHA,
        "ID": "file-0001",
        "Filename": "a.pdf",
        "ImageCompress": "false",
    }
    assert sent.body == b""
    assert str(tmp_path) not in sent.url
    assert req.Sha256 == UPPER_SHA


@pytest.mark.parametrize("save_to", ["", "   "])
def test_blank_save_to_fails_before_sending(save_to):
    service, adapter = make_service(_serve())
    with pytest.raises(ValueError, match="SaveTo"):
        service.Download(up_types.DownloadRequest(Key="k", Path="/p", SaveTo=save_to))
    assert adapter.sent == []


def test_error_response_creates_no_file(tmp_path):
    service, _ = make_service(_serve(body=b'{"error":"key expired"}', status=403, headers={}))
    target = tmp_path / "f"
    with pytest.raises(Exception, match="key expired"):
        _download(service, target)
    assert _listing(tmp_path) == []


def test_short_body_keeps_old_file_and_leaves_nothing_behind(tmp_path):
    target = tmp_path / "f"
    target.write_bytes(OLD)
    service, _ = make_service(_serve(headers={"Content-Length": str(len(CONTENT) + 10)}))
    with pytest.raises(Exception, match="Content-Length"):
        _download(service, target)
    assert target.read_bytes() == OLD
    assert _listing(tmp_path) == ["f"]


def test_interrupted_stream_keeps_old_file_and_leaves_nothing_behind(tmp_path):
    target = tmp_path / "f"
    target.write_bytes(OLD)
    respond = _serve(headers={}, raw=BrokenStream(CONTENT[:100]))
    service, _ = make_service(respond)
    with pytest.raises(ConnectionResetError):
        _download(service, target)
    assert target.read_bytes() == OLD
    assert _listing(tmp_path) == ["f"]
    assert respond.served[0].raw.closed


@pytest.mark.parametrize(
    "headers",
    [{}, {"Content-Length": "1", "Content-Encoding": "gzip"}],
    ids=["no-content-length", "content-encoded"],
)
def test_length_check_only_applies_to_plain_declared_bodies(tmp_path, headers):
    service, _ = make_service(
        lambda sent: response(200, CONTENT, headers, io.BytesIO(CONTENT))
    )
    target = tmp_path / "f"
    _download(service, target)
    assert target.read_bytes() == CONTENT


def test_symlink_target_is_replaced_and_link_kept(tmp_path):
    real = tmp_path / "real.bin"
    real.write_bytes(OLD)
    link = tmp_path / "link.bin"
    link.symlink_to(real)
    service, _ = make_service(_serve())
    _download(service, link)
    assert link.is_symlink()
    assert real.read_bytes() == CONTENT


def test_existing_file_mode_is_kept(tmp_path):
    target = tmp_path / "private.bin"
    target.write_bytes(OLD)
    target.chmod(0o600)
    service, _ = make_service(_serve())
    _download(service, target)
    assert stat.S_IMODE(target.stat().st_mode) == 0o600
    assert target.read_bytes() == CONTENT


def test_new_file_mode_follows_umask_like_open(tmp_path):
    reference = tmp_path / "reference"
    reference.write_bytes(b"")
    service, _ = make_service(_serve())
    target = tmp_path / "new.bin"
    _download(service, target)
    assert stat.S_IMODE(target.stat().st_mode) == stat.S_IMODE(reference.stat().st_mode)


def test_directory_save_to_fails_before_sending(tmp_path):
    service, adapter = make_service(_serve())
    with pytest.raises(IsADirectoryError):
        _download(service, tmp_path)
    assert adapter.sent == []


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="needs mkfifo")
def test_non_regular_save_to_fails_before_sending(tmp_path):
    fifo = tmp_path / "pipe"
    os.mkfifo(fifo)
    service, adapter = make_service(_serve())
    with pytest.raises(ValueError, match="regular file"):
        _download(service, fifo)
    assert adapter.sent == []
    assert stat.S_ISFIFO(os.lstat(fifo).st_mode)


def test_redirect_is_not_followed_and_creates_no_file(tmp_path):
    location = "https://elsewhere.example.com/down"
    service, adapter = make_service(
        _serve(body=b"", status=302, headers={"Location": location})
    )
    with pytest.raises(Exception, match="302"):
        _download(service, tmp_path / "f")
    assert len(adapter.sent) == 1
    assert _listing(tmp_path) == []


class _ModeProbe(io.RawIOBase):
    """Records the modes of partial files present while the body is read."""

    def __init__(self, directory, body):
        self.directory = directory
        self.body = body
        self.modes = []

    def readable(self):
        return True

    def read(self, size=-1):
        for name in os.listdir(self.directory):
            if name.endswith(".part"):
                self.modes.append(stat.S_IMODE(os.stat(self.directory / name).st_mode))
        body, self.body = self.body, b""
        return body


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX modes")
def test_partial_file_is_private_while_overwriting_private_file(tmp_path):
    target = tmp_path / "private.bin"
    target.write_bytes(OLD)
    target.chmod(0o600)
    probe = _ModeProbe(tmp_path, CONTENT)
    service, _ = make_service(_serve(raw=probe))
    _download(service, target)
    assert probe.modes and set(probe.modes) == {0o600}
    assert stat.S_IMODE(target.stat().st_mode) == 0o600
    assert target.read_bytes() == CONTENT
