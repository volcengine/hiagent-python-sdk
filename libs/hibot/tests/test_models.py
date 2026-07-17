"""Contract tests for model Actions hosted by hibot-server."""

from __future__ import annotations

import json
from urllib.parse import parse_qs, urlsplit

from hibot import V1ModelGetParams, V1ModelProviderGetParams, V1ModelProviderListParams


def _action(request) -> str:
    return parse_qs(urlsplit(str(request.url)).query)["Action"][0]


def _version(request) -> str:
    return parse_qs(urlsplit(str(request.url)).query)["Version"][0]


def test_models_use_current_server_actions(client_factory, make_handler, ok_envelope):
    handler = make_handler(
        [
            ok_envelope({"Items": [{"ID": "model-1", "Name": "demo"}], "Total": 1}),
            ok_envelope({"Providers": ["openai"]}),
            ok_envelope({"Models": [{"ID": "provider-1"}], "Total": 1}),
            ok_envelope({"Items": [{"ID": "provider-1"}]}),
        ]
    )
    client = client_factory(handler)

    listing = client.v1.models.list(name="demo")
    providers = client.v1.models.list_providers()
    model_providers = client.v1.models.list_model_providers(V1ModelProviderListParams())
    selected = client.v1.models.get_model_provider(
        V1ModelProviderGetParams(ids=["provider-1"])
    )

    assert listing.items[0].id == "model-1"
    assert providers == ["openai"]
    assert model_providers.items[0].id == "provider-1"
    assert selected[0].id == "provider-1"
    assert [_action(req) for req in handler.calls] == [
        "ListModels",
        "ListProviders",
        "ListModelProviders",
        "GetModelProvider",
    ]
    for request in handler.calls:
        assert _version(request) == "2026-04-23"
        assert request.headers["x-top-service"] == "hibot-server"
        assert json.loads(request.content)["WorkspaceID"] == "ws-1"


def test_get_model_uses_server_action(client_factory, make_handler, ok_envelope):
    handler = make_handler([ok_envelope({"Items": [{"ID": "model-1"}]})])
    client = client_factory(handler)

    model = client.v1.models.get(V1ModelGetParams(id="model-1"))

    assert model.id == "model-1"
    assert _action(handler.calls[0]) == "GetModel"
    assert handler.calls[0].headers["x-top-service"] == "hibot-server"


def test_get_model_by_model_name_scans_server_pages(
    client_factory, make_handler, ok_envelope
):
    first_page = [
        {"ID": f"model-{index}", "ModelName": f"other-{index}"} for index in range(100)
    ]
    handler = make_handler(
        [
            ok_envelope({"Items": first_page, "Total": 101}),
            ok_envelope(
                {
                    "Items": [{"ID": "wanted", "ModelName": "target-model"}],
                    "Total": 101,
                }
            ),
        ]
    )
    client = client_factory(handler)

    model = client.v1.models.get(V1ModelGetParams(model_name="target-model"))

    assert model.id == "wanted"
    assert [_action(request) for request in handler.calls] == [
        "ListModels",
        "ListModels",
    ]
    assert json.loads(handler.calls[0].content)["Page"] == {
        "PageNum": 1,
        "PageSize": 100,
    }
    assert json.loads(handler.calls[1].content)["Page"] == {
        "PageNum": 2,
        "PageSize": 100,
    }
