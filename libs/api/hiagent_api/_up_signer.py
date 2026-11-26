# coding:utf-8
# Copyright (c) 2024 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Signs UP requests the way UP verifies them.

UP rebuilds the canonical request from what it received, so the signer only
reads the method, URL and ``X-Content-Sha256`` of the request that is about to
be sent. ``host`` is not signed, so a gateway that rewrites Host does not break
verification. Ported from the Java SDK's ``UpSigner``.
"""

import hashlib
import hmac
import re
from datetime import datetime, timezone
from typing import Dict, List, Mapping, Optional, Tuple
from urllib.parse import quote, unquote, unquote_plus, urlsplit

SERVICE = "up"
HEADER_DATE = "X-Date"
HEADER_CONTENT_SHA256 = "X-Content-Sha256"
HEADER_SECURITY_TOKEN = "X-Security-Token"
HEADER_AUTHORIZATION = "Authorization"

_ALGORITHM = "HMAC-SHA256"
_SIGNED_HEADERS = "x-content-sha256;x-date"
_X_DATE_FORMAT = "%Y%m%dT%H%M%SZ"
_SHORT_DATE_LENGTH = 8
_UNRESERVED = "-_.~"
_HEADER_SAFE = re.compile(r"^[\x21-\x7e]+$")


def sign(
    method: str,
    url: str,
    headers: Mapping[str, str],
    *,
    ak: Optional[str],
    sk: Optional[str],
    region: str,
    session_token: Optional[str] = None,
    now: Optional[datetime] = None,
) -> Dict[str, str]:
    """Return a copy of ``headers`` plus ``X-Date``, ``Authorization`` and,
    for STS credentials, ``X-Security-Token``.

    Raises ValueError when the credentials are unusable or the request has no
    ``X-Content-Sha256``. Error messages never contain credential values.
    """
    ak, sk, token = check_credentials(ak, sk, session_token)
    payload_hash = _content_sha256(headers)
    signed_at = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    x_date = signed_at.strftime(_X_DATE_FORMAT)
    short_date = x_date[:_SHORT_DATE_LENGTH]

    canonical = canonical_request(method, url, payload_hash, x_date)
    signature = hmac.new(
        _signing_key(sk, short_date, region),
        string_to_sign(x_date, region, canonical).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    signed = dict(headers)
    signed[HEADER_DATE] = x_date
    signed[HEADER_AUTHORIZATION] = (
        f"{_ALGORITHM} Credential={ak}/{_credential_scope(short_date, region)}, "
        f"SignedHeaders={_SIGNED_HEADERS}, Signature={signature}"
    )
    if token:
        signed[HEADER_SECURITY_TOKEN] = token
    return signed


def canonical_request(method: str, url: str, payload_hash: str, x_date: str) -> str:
    parts = urlsplit(url)
    path = unquote(parts.path) or "/"
    payload_hash = payload_hash.strip()
    return "\n".join(
        [
            method.upper(),
            path,
            canonical_query_string(parts.query),
            f"x-content-sha256:{payload_hash}",
            f"x-date:{x_date}",
            "",
            _SIGNED_HEADERS,
            payload_hash,
        ]
    )


def string_to_sign(x_date: str, region: str, canonical: str) -> str:
    return "\n".join(
        [
            _ALGORITHM,
            x_date,
            _credential_scope(x_date[:_SHORT_DATE_LENGTH], region),
            hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        ]
    )


def canonical_query_string(raw_query: str) -> str:
    """Decode every pair the way Go's url.ParseQuery does ("+" is a space),
    sort by name keeping the order of repeated names, and re-encode."""
    grouped: Dict[str, List[str]] = {}
    for pair in raw_query.split("&"):
        if not pair:
            continue
        name, _, value = pair.partition("=")
        grouped.setdefault(unquote_plus(name), []).append(unquote_plus(value))
    return "&".join(
        f"{sign_encode(name)}={sign_encode(value)}"
        for name in sorted(grouped)
        for value in grouped[name]
    )


def sign_encode(value: str) -> str:
    """RFC 3986: only A-Z a-z 0-9 - _ . ~ stay literal; space is %20."""
    return quote(value, safe=_UNRESERVED)


def check_credentials(
    ak: Optional[str], sk: Optional[str], session_token: Optional[str]
) -> Tuple[str, str, str]:
    """Validate credentials and return (ak, sk, stripped session token)."""
    if not ak or not ak.strip() or not sk or not sk.strip():
        raise ValueError("UP request signing requires both AccessKey and SecretKey")
    # Checked here because requests would quote the whole header value in its
    # InvalidHeader message.
    if not _HEADER_SAFE.match(ak):
        raise ValueError("AccessKey contains characters not allowed in an HTTP header")
    token = (session_token or "").strip()
    if token and not _HEADER_SAFE.match(token):
        raise ValueError(
            "session token contains characters not allowed in an HTTP header"
        )
    return ak, sk, token


def _content_sha256(headers: Mapping[str, str]) -> str:
    for name, value in headers.items():
        if name.lower() == HEADER_CONTENT_SHA256.lower() and value and value.strip():
            return value.strip()
    raise ValueError(f"{HEADER_CONTENT_SHA256} must be set before signing")


def _credential_scope(short_date: str, region: str) -> str:
    return f"{short_date}/{region}/{SERVICE}/request"


def _signing_key(sk: str, short_date: str, region: str) -> bytes:
    key = sk.encode("utf-8")
    for part in (short_date, region, SERVICE, "request"):
        key = hmac.new(key, part.encode("utf-8"), hashlib.sha256).digest()
    return key
