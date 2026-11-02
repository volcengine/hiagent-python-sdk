from importlib.metadata import version

from hiagent_observe import VERSION


def test_runtime_version_matches_installed_distribution():
    assert VERSION.removeprefix("v") == version("hiagent-observe")
