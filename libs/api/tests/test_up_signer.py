import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from hiagent_api import _up_signer

VECTORS = json.loads(
    (Path(__file__).parent / "data" / "up_signature_vectors.json").read_text("utf-8")
)
EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
NOW = datetime(2026, 11, 6, 8, 0, 0, tzinfo=timezone.utc)


def _x_date_to_datetime(x_date):
    return datetime.strptime(x_date, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)


def _sign(url="https://up.example.com/up?Action=Delete", payload_hash=EMPTY_SHA256, **overrides):
    kwargs = {
        "ak": "AKLTtest",
        "sk": "secret",
        "region": "cn-north-1",
        "session_token": None,
        "now": NOW,
    }
    kwargs.update(overrides)
    return _up_signer.sign("POST", url, payload_hash, **kwargs)


@pytest.mark.parametrize("vector", VECTORS["vectors"], ids=lambda v: v["name"])
def test_matches_vectors_generated_by_up_verifier(vector):
    canonical = _up_signer.canonical_request(
        vector["method"], vector["url"], vector["contentSha256"], vector["xDate"]
    )
    assert canonical == vector["canonicalRequest"]
    assert (
        _up_signer.string_to_sign(vector["xDate"], VECTORS["region"], canonical)
        == vector["stringToSign"]
    )

    signed = _up_signer.sign(
        vector["method"],
        vector["url"],
        vector["contentSha256"],
        ak=VECTORS["accessKey"],
        sk=VECTORS["secretKey"],
        region=VECTORS["region"],
        now=_x_date_to_datetime(vector["xDate"]),
    )
    assert signed["X-Date"] == vector["xDate"]
    assert signed["Authorization"] == (
        f"HMAC-SHA256 Credential={VECTORS['accessKey']}/{vector['xDate'][:8]}/"
        f"{VECTORS['region']}/up/request, SignedHeaders={vector['signedHeaders']}, "
        f"Signature={vector['signature']}"
    )


def test_query_decodes_plus_as_space_but_path_keeps_literal_plus():
    canonical = _up_signer.canonical_request(
        "POST", "https://h/a+b?Name=x+y&Other=1%2B1", EMPTY_SHA256, "20261106T080000Z"
    )
    path, query = canonical.split("\n")[1:3]
    assert path == "/a+b"
    assert query == "Name=x%20y&Other=1%2B1"


def test_query_sorted_by_name_keeping_duplicate_order():
    canonical = _up_signer.canonical_request(
        "post", "https://h/?b=2&a=z&a=y&B=1", EMPTY_SHA256, "20261106T080000Z"
    )
    method, _, query = canonical.split("\n")[:3]
    assert method == "POST"
    assert query == "B=1&a=z&a=y&b=2"


def test_empty_path_is_root():
    canonical = _up_signer.canonical_request(
        "POST", "https://h?Action=A", EMPTY_SHA256, "20261106T080000Z"
    )
    assert canonical.split("\n")[1] == "/"


def test_returns_only_signing_headers_and_does_not_sign_host():
    signed = _sign()
    assert set(signed) == {"X-Date", "Authorization"}
    assert "SignedHeaders=x-content-sha256;x-date," in signed["Authorization"]
    other_host = _sign(url="https://other.example.com/up?Action=Delete")
    assert other_host["Authorization"] == signed["Authorization"]


def test_default_now_is_current_utc():
    signed = _sign(now=None)
    signed_at = _x_date_to_datetime(signed["X-Date"])
    assert abs((datetime.now(timezone.utc) - signed_at).total_seconds()) < 60


def test_session_token_is_stripped_and_not_signed():
    plain = _sign()
    with_token = _sign(session_token="token-value\n")
    assert with_token["X-Security-Token"] == "token-value"
    assert with_token["Authorization"] == plain["Authorization"]
    assert "X-Security-Token" not in plain
    assert "X-Security-Token" not in _sign(session_token="  \n")


@pytest.mark.parametrize("ak", ["", "   ", None])
def test_requires_access_key(ak):
    with pytest.raises(ValueError):
        _sign(ak=ak)


@pytest.mark.parametrize("sk", ["", "   ", None])
def test_requires_secret_key(sk):
    with pytest.raises(ValueError):
        _sign(sk=sk)


@pytest.mark.parametrize(
    "field, value",
    [
        ("ak", "AKLT\nleak"),
        ("ak", "AKLTleak\n"),
        ("ak", "AKLT\rleak"),
        ("ak", "AKLT leak"),
        ("ak", "AKLT\x01leak"),
        ("ak", "AKLTlé"),
        ("session_token", "tok\nleak-secret"),
        ("session_token", "tok\x7fleak-secret"),
        ("session_token", "tok中leak-secret"),
    ],
)
def test_invalid_credential_error_hides_value(field, value):
    with pytest.raises(ValueError) as excinfo:
        _sign(**{field: value})
    message = str(excinfo.value)
    assert "leak" not in message
    assert value not in message
    assert excinfo.value.__cause__ is None
    assert excinfo.value.__context__ is None
