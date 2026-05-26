"""V1 Uploads service."""

from __future__ import annotations

from typing import Union

from .._request import Action
from .._version import UP_VERSION
from ._helpers import from_dict
from .types import V1UploadBlob, V1UploadBlobParams


class UploadsService:
    def __init__(self, v1) -> None:
        self._v1 = v1

    def upload_blob(
        self,
        params: Union[V1UploadBlobParams, dict],
        body: bytes,
    ) -> V1UploadBlob:
        if isinstance(params, dict):
            params = V1UploadBlobParams(**params)
        if not params.filename:
            raise ValueError("hibot: upload filename is required")
        result = self._v1.requester.do_raw_action(
            Action(
                service=self._v1.services.up,
                version=UP_VERSION,
                action="UploadBlob",
            ),
            body or b"",
            params.content_type or "application/octet-stream",
            {"Filename": params.filename},
        )
        decoded = from_dict(V1UploadBlob, result) or V1UploadBlob()
        if not decoded.blob_id:
            raise ValueError("hibot: upload blob response missing BlobID")
        return decoded
