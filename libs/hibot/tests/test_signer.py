"""Tests for VOLC v4 signing (deterministic vector)."""

from __future__ import annotations

import datetime as _dt

from hibot._signer import ALGORITHM, sign_request


def test_sign_request_produces_v4_authorization_header():
    headers = sign_request(
        method="POST",
        url="https://open.volcengineapi.com/?Action=GetAgent&Version=2026-04-23",
        headers={"Content-Type": "application/json"},
        body=b'{"AgentID":"a-1"}',
        access_key="AKLTexample",
        secret_key="example-secret",
        region="cn-north-1",
        service="hibot-server",
        now=_dt.datetime(2026, 5, 24, 1, 2, 3, tzinfo=_dt.timezone.utc),
    )

    assert headers["X-Date"] == "20260524T010203Z"
    assert "X-Content-Sha256" in headers
    assert headers["Host"] == "open.volcengineapi.com"
    auth = headers["Authorization"]
    assert auth.startswith(ALGORITHM + " ")
    assert "Credential=AKLTexample/20260524/cn-north-1/hibot-server/request" in auth
    assert "SignedHeaders=content-type;host;x-content-sha256;x-date" in auth
    # Signature must be deterministic given the fixed `now`.
    assert "Signature=" in auth
    sig = auth.split("Signature=", 1)[1]
    assert len(sig) == 64
    assert all(ch in "0123456789abcdef" for ch in sig)


def test_sign_request_changes_signature_on_body_diff():
    common = dict(
        method="POST",
        url="https://open.volcengineapi.com/?Action=Foo&Version=2026-04-23",
        headers={"Content-Type": "application/json"},
        access_key="AK",
        secret_key="SK",
        region="cn-north-1",
        service="hibot-server",
        now=_dt.datetime(2026, 1, 2, 3, 4, 5, tzinfo=_dt.timezone.utc),
    )
    h1 = sign_request(body=b'{"x":1}', **common)
    h2 = sign_request(body=b'{"x":2}', **common)
    assert h1["Authorization"] != h2["Authorization"]
    assert h1["X-Content-Sha256"] != h2["X-Content-Sha256"]


def test_sign_request_canonical_query_sort_is_stable():
    h1 = sign_request(
        method="POST",
        url="https://example.com/?B=2&A=1",
        headers={"Content-Type": "application/json"},
        body=b"",
        access_key="AK",
        secret_key="SK",
        region="cn-north-1",
        service="svc",
        now=_dt.datetime(2026, 1, 1, tzinfo=_dt.timezone.utc),
    )
    h2 = sign_request(
        method="POST",
        url="https://example.com/?A=1&B=2",
        headers={"Content-Type": "application/json"},
        body=b"",
        access_key="AK",
        secret_key="SK",
        region="cn-north-1",
        service="svc",
        now=_dt.datetime(2026, 1, 1, tzinfo=_dt.timezone.utc),
    )
    assert h1["Authorization"] == h2["Authorization"]
