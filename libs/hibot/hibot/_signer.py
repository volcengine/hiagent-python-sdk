"""TOP / VOLC v4 request signer.

Mirrors github.com/volcengine/volc-sdk-golang/base.Credentials.Sign — algorithm
"HMAC-SHA256" with credential scope ``<date>/<region>/<service>/request``.

The reference Python implementation lives in
``github.com/volcengine/volc-sdk-python``; the algorithm is identical to the
public AWS Signature V4 with the algorithm string changed from
``AWS4-HMAC-SHA256`` to ``HMAC-SHA256`` (no ``AWS4`` prefix on the signing
key derivation, no ``aws4_request`` terminator).
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import hmac
from typing import Dict, Iterable, Mapping, Optional, Tuple
from urllib.parse import quote, urlsplit

ALGORITHM = "HMAC-SHA256"
SIGNED_HEADERS_INCLUDE = ("content-type", "host", "x-content-sha256", "x-date")


def _utcnow() -> _dt.datetime:
    return _dt.datetime.now(_dt.timezone.utc)


def _hmac_sha256(key: bytes, msg: str) -> bytes:
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_query(query: str) -> str:
    if not query:
        return ""
    pairs = []
    for raw in query.split("&"):
        if not raw:
            continue
        if "=" in raw:
            k, _, v = raw.partition("=")
        else:
            k, v = raw, ""
        # Re-encode keys & values strictly per RFC 3986 (do not encode "~").
        pairs.append((quote(k, safe="-_.~"), quote(v, safe="-_.~")))
    pairs.sort()
    return "&".join(f"{k}={v}" for k, v in pairs)


def _canonical_uri(path: str) -> str:
    if not path:
        return "/"
    # Each segment must be percent-encoded once. Slashes are preserved.
    segments = path.split("/")
    encoded = [quote(seg, safe="-_.~") for seg in segments]
    return "/".join(encoded)


def _canonical_headers(headers: Mapping[str, str], include: Iterable[str]) -> Tuple[str, str]:
    lower = {k.lower(): v for k, v in headers.items()}
    keys = sorted(k for k in include if k in lower)
    canonical = "".join(f"{k}:{lower[k].strip()}\n" for k in keys)
    signed = ";".join(keys)
    return canonical, signed


def sign_request(
    *,
    method: str,
    url: str,
    headers: Dict[str, str],
    body: bytes,
    access_key: str,
    secret_key: str,
    region: str,
    service: str,
    now: Optional[_dt.datetime] = None,
) -> Dict[str, str]:
    """Sign an HTTP request in-place style (returns a new headers dict).

    The returned dict contains all original headers plus ``Host``, ``X-Date``,
    ``X-Content-Sha256`` and ``Authorization``. Callers should set this as the
    request's headers.
    """
    if now is None:
        now = _utcnow()
    amzdate = now.strftime("%Y%m%dT%H%M%SZ")
    datestamp = now.strftime("%Y%m%d")

    parts = urlsplit(url)
    host = parts.netloc
    path = parts.path or "/"
    query = parts.query

    body = body or b""
    payload_hash = _sha256_hex(body)

    out_headers = dict(headers)
    out_headers.setdefault("Host", host)
    out_headers["X-Date"] = amzdate
    out_headers["X-Content-Sha256"] = payload_hash

    canonical_headers, signed_headers = _canonical_headers(out_headers, SIGNED_HEADERS_INCLUDE)
    canonical_request = "\n".join([
        method.upper(),
        _canonical_uri(path),
        _canonical_query(query),
        canonical_headers,
        signed_headers,
        payload_hash,
    ])

    credential_scope = f"{datestamp}/{region}/{service}/request"
    string_to_sign = "\n".join([
        ALGORITHM,
        amzdate,
        credential_scope,
        _sha256_hex(canonical_request.encode("utf-8")),
    ])

    k_date = _hmac_sha256(secret_key.encode("utf-8"), datestamp)
    k_region = _hmac_sha256(k_date, region)
    k_service = _hmac_sha256(k_region, service)
    k_signing = _hmac_sha256(k_service, "request")
    signature = hmac.new(k_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

    authorization = (
        f"{ALGORITHM} "
        f"Credential={access_key}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, "
        f"Signature={signature}"
    )
    out_headers["Authorization"] = authorization
    return out_headers


__all__ = ["sign_request", "ALGORITHM"]
