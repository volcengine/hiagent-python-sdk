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

import email
import subprocess
import tarfile
import zipfile
from pathlib import Path, PurePosixPath

import pytest


@pytest.fixture(scope="module")
def distributions(tmp_path_factory):
    repository = Path(__file__).resolve().parents[3]
    output = tmp_path_factory.mktemp("observe-distributions")
    subprocess.run(
        [
            "uv",
            "build",
            "--offline",
            "--package",
            "hiagent-observe",
            "--out-dir",
            str(output),
        ],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    )
    return output


def test_wheel_paths_and_license(distributions):
    (wheel,) = distributions.glob("*.whl")
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        for entry in archive.infolist():
            path = PurePosixPath(entry.filename)
            normalized = path.as_posix() + ("/" if entry.is_dir() else "")
            assert not path.is_absolute() and ".." not in path.parts
            assert "\\" not in entry.filename
            assert entry.filename == normalized, entry.filename
        assert "hiagent_observe/__init__.py" in names
        assert "hiagent_observe/helper.py" in names
        assert "hiagent_observe/semconv/__init__.py" in names
        assert all(
            name.startswith("hiagent_observe/") or ".dist-info/" in name
            for name in names
        )
        (metadata_path,) = (
            name for name in names if name.endswith(".dist-info/METADATA")
        )
        metadata = email.message_from_bytes(archive.read(metadata_path))
        assert metadata["Name"] == "hiagent-observe"
        assert metadata["License-Expression"] == "Apache-2.0"
        assert "LICENSE" in metadata.get_all("License-File", [])
        license_path = metadata_path.removesuffix("METADATA") + "licenses/LICENSE"
        source_license = Path(__file__).resolve().parents[1] / "LICENSE"
        assert archive.read(license_path) == source_license.read_bytes()


def test_source_archive_paths(distributions):
    (source,) = distributions.glob("*.tar.gz")
    with tarfile.open(source) as archive:
        names = archive.getnames()
        for name in names:
            path = PurePosixPath(name)
            assert not path.is_absolute() and ".." not in path.parts
            assert "\\" not in name
            assert name == path.as_posix(), name
        roots = {PurePosixPath(name).parts[0] for name in names}
        assert len(roots) == 1
        (root,) = roots
        assert f"{root}/LICENSE" in names
        assert f"{root}/hiagent_observe/__init__.py" in names
