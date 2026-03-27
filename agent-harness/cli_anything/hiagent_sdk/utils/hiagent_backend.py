import configparser
import os
import uuid
from hashlib import sha256
from pathlib import Path
from typing import Optional

from dotenv import dotenv_values
from hiagent_api import up_types
from hiagent_api.up import UpService


def _read_volc_dotenv() -> dict:
    dotenv_path = Path(os.path.expanduser("~/.volc/.env"))
    if not dotenv_path.is_file():
        return {}
    return dict(dotenv_values(str(dotenv_path)))


def ensure_volc_credentials() -> None:
    ak = os.environ.get("VOLC_ACCESSKEY")
    sk = os.environ.get("VOLC_SECRETKEY")
    if ak and sk:
        return

    dotenv_data = _read_volc_dotenv()
    ak = ak or str(dotenv_data.get("VOLC_ACCESSKEY") or "").strip()
    sk = sk or str(dotenv_data.get("VOLC_SECRETKEY") or "").strip()
    if ak and sk:
        return

    home = os.environ.get("HOME")
    if home:
        cred_path = Path(home) / ".volc" / "credentials"
        if cred_path.is_file():
            parser = configparser.ConfigParser()
            parser.read(str(cred_path))
            if parser.has_section("default"):
                ak = parser.get("default", "access_key_id", fallback="").strip()
                sk = parser.get("default", "secret_access_key", fallback="").strip()
                if ak and sk:
                    return

        cfg_path = Path(home) / ".volc" / "config"
        if cfg_path.is_file():
            try:
                import json

                data = json.loads(cfg_path.read_text(encoding="utf-8"))
                ak = str(data.get("ak", "")).strip()
                sk = str(data.get("sk", "")).strip()
                if ak and sk:
                    return
            except Exception:
                pass

    raise RuntimeError(
        "Volcengine credentials not found.\n"
        "Set env vars:\n"
        "  export VOLC_ACCESSKEY=...\n"
        "  export VOLC_SECRETKEY=...\n"
        "Or configure ~/.volc/.env\n"
    )


def upload_raw_file(
    up_service: UpService,
    file_path: Path,
    file_id: Optional[str] = None,
    expire: str = "15h",
    content_type: str = "application/octet-stream",
) -> dict:
    ensure_volc_credentials()
    if not file_path.is_file():
        raise FileNotFoundError(str(file_path))

    file_id = file_id or f"cli-{uuid.uuid4().hex}"
    digest = sha256(file_path.read_bytes()).hexdigest()

    req = up_types.UploadRawRequest(
        Expire=expire,
        Id=file_id,
        ContentType=content_type,
        Sha256=digest,
    )

    with file_path.open("rb") as f:
        resp = up_service.UploadRaw(req, f)

    return {
        "id": file_id,
        "path": resp.Path,
        "sha256": resp.Sha256,
        "size": resp.Size,
    }


def download_file(
    up_service: UpService,
    path: str,
    save_to: Path,
    key: Optional[str] = None,
) -> dict:
    ensure_volc_credentials()
    save_to.parent.mkdir(parents=True, exist_ok=True)

    if key is None:
        key_resp = up_service.DownloadKey(up_types.DownloadKeyRequest(Path=path))
        key = key_resp.Key

    req = up_types.DownloadRequest(Key=key, Path=path, SaveTo=str(save_to))
    up_service.Download(req)

    size = save_to.stat().st_size if save_to.exists() else 0
    return {
        "path": path,
        "key": key,
        "saved_to": str(save_to),
        "size": size,
    }
