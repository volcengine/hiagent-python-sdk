"""Environment API contract tests."""

from __future__ import annotations

import json
from urllib.parse import parse_qs, urlsplit

import httpx
from hibot import V1EnvironmentNewParams


def _action(req: httpx.Request) -> str:
    return parse_qs(urlsplit(str(req.url)).query).get("Action", [""])[0]


def test_environment_spec_code_and_workspace_catalog(
    client_factory, make_handler, ok_envelope
):
    handler = make_handler(
        [
            ok_envelope({"ID": "env-1"}),
            ok_envelope(
                {
                    "Specs": [
                        {
                            "SpecCode": "vci.u1.2c-4gi",
                            "DisplayName": "Standard",
                            "Cpu": "2",
                            "Memory": "4Gi",
                            "Storage": "20Gi",
                            "IsDefault": True,
                        }
                    ]
                }
            ),
        ]
    )
    client = client_factory(handler)

    env = client.v1.environments.create(
        params=V1EnvironmentNewParams(
            name="runtime",
            image_type="hermes",
            spec_code="vci.u1.2c-4gi",
        )
    )
    specs = client.v1.environments.list_workspace_specs()

    assert env.id == "env-1"
    assert len(specs) == 1
    assert specs[0].spec_code == "vci.u1.2c-4gi"
    assert specs[0].is_default is True
    assert [_action(req) for req in handler.calls] == [
        "CreateEnv",
        "ListWorkspaceSpecs",
    ]
    create_body = json.loads(handler.calls[0].content)
    assert create_body["Payload"]["SpecCode"] == "vci.u1.2c-4gi"
    assert handler.calls[1].headers["x-top-service"] == "hibot-server"
