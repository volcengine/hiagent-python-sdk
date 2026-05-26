"""V1 Models service."""

from __future__ import annotations

from typing import List, Optional

from .._request import Action
from .._version import MODEL_VERSION
from ._helpers import list_from_items
from .types import (
    V1Model,
    V1ModelDeleteParams,
    V1ModelGetParams,
    V1ModelList,
    V1ModelNewParams,
    V1ModelProvider,
    V1ModelProviderCredentialSchemaParams,
    V1ModelProviderGetParams,
    V1ModelProviderList,
    V1ModelProviderListParams,
    V1ModelUpdateParams,
)


class ModelsService:
    def __init__(self, v1) -> None:
        self._v1 = v1

    def _action(self, name: str, body):
        return self._v1.requester.do_action(
            Action(service=self._v1.services.model, version=MODEL_VERSION, action=name, body=body)
        )

    def get(self, params: Optional[V1ModelGetParams] = None, **kwargs) -> V1Model:
        if params is None:
            params = V1ModelGetParams(**kwargs)
        ids = list(params.ids or [])
        if params.id and not ids:
            ids = [params.id]
        if not ids:
            if not (params.name or params.model_name or params.provider or params.type or params.spec):
                raise ValueError(
                    "hibot: model id is required (or provide Name/ModelName/Provider/Type/Spec)"
                )
            return self._find_by_filter(params)
        body = {"IDs": ids}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("GetModel", body)
        items = list_from_items(V1Model, result)
        if not items:
            raise ValueError("hibot: model not found")
        matched = self._match(items, params)
        if matched is None:
            raise ValueError("hibot: model not found matching filter")
        return matched

    def _find_by_filter(self, params: V1ModelGetParams) -> V1Model:
        listing = self.list(name=params.name, workspace_id=params.workspace_id)
        if not listing.items:
            raise ValueError("hibot: model not found")
        matched = self._match(listing.items, params)
        if matched is None:
            raise ValueError("hibot: model not found matching filter")
        return matched

    @staticmethod
    def _match(items: List[V1Model], params: V1ModelGetParams) -> Optional[V1Model]:
        for m in items:
            if params.name and m.name != params.name:
                continue
            if params.model_name and m.model_name != params.model_name:
                continue
            if params.provider and m.provider != params.provider:
                continue
            if params.type and m.type != params.type:
                continue
            if params.spec and m.spec != params.spec:
                continue
            return m
        if not (params.name or params.model_name or params.provider or params.type or params.spec):
            return items[0]
        return None

    def list(self, *, name: str = "", workspace_id: str = "", page=None, sort_by: str = "", sort_order: str = "") -> V1ModelList:
        body = {}
        if workspace_id:
            body["WorkspaceID"] = workspace_id
        if page is not None:
            body["Page"] = page if isinstance(page, dict) else {"PageNum": page.page_num, "PageSize": page.page_size}
        if sort_by:
            body["SortBy"] = sort_by
        if sort_order:
            body["SortOrder"] = sort_order
        if name:
            body["Filter"] = {"Name": name}
        result = self._action("ListModel", body)
        ml = V1ModelList()
        if isinstance(result, dict):
            ml.items = list_from_items(V1Model, result)
            ml.total = result.get("Total")
        return ml

    def create(self, params: V1ModelNewParams) -> V1Model:
        if not params.name:
            raise ValueError("hibot: model Name is required")
        if not params.type:
            raise ValueError("hibot: model Type is required")
        body = {
            "Name": params.name,
            "Type": params.type,
        }
        if params.description:
            body["Description"] = params.description
        if params.provider:
            body["Provider"] = params.provider
        if params.spec:
            body["Spec"] = params.spec
        if params.model_name:
            body["ModelName"] = params.model_name
        if params.features_config is not None:
            body["FeaturesConfig"] = params.features_config
        if params.property is not None:
            body["Property"] = params.property
        if params.credential_schema is not None:
            body["CredentialSchema"] = params.credential_schema
        if params.credential is not None:
            body["Credential"] = params.credential
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("CreateModel", body)
        new_id = result.get("ID") if isinstance(result, dict) else None
        if not new_id:
            raise ValueError("hibot: create model response missing ID")
        return V1Model(
            id=new_id,
            name=params.name,
            type=params.type,
            provider=params.provider,
            spec=params.spec,
            model_name=params.model_name,
        )

    def update(self, params: V1ModelUpdateParams) -> None:
        if not params.id:
            raise ValueError("hibot: model id is required")
        if not params.type:
            raise ValueError("hibot: model Type is required")
        body = {"ID": params.id, "Type": params.type}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        if params.description:
            body["Description"] = params.description
        if params.provider:
            body["Provider"] = params.provider
        if params.spec:
            body["Spec"] = params.spec
        if params.model_name:
            body["ModelName"] = params.model_name
        if params.features_config is not None:
            body["FeaturesConfig"] = params.features_config
        if params.property is not None:
            body["Property"] = params.property
        if params.credential_schema is not None:
            body["CredentialSchema"] = params.credential_schema
        if params.credential is not None:
            body["Credential"] = params.credential
        self._action("UpdateModel", body)

    def delete(self, params: V1ModelDeleteParams) -> None:
        if not params.id:
            raise ValueError("hibot: model id is required")
        body = {"ID": params.id}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        self._action("DeleteModel", body)

    def list_providers(self) -> List[str]:
        result = self._action("ListProvider", {})
        if isinstance(result, dict):
            return list(result.get("Providers") or [])
        return []

    def list_model_providers(self, params: V1ModelProviderListParams) -> V1ModelProviderList:
        body = {}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        if params.page is not None:
            body["Page"] = {"PageNum": params.page.page_num, "PageSize": params.page.page_size}
        if params.sort_by:
            body["SortBy"] = params.sort_by
        if params.sort_order:
            body["SortOrder"] = params.sort_order
        flt = {}
        if params.provider:
            flt["Provider"] = params.provider
        if params.type:
            flt["Type"] = params.type
        if params.model_name:
            flt["ModelName"] = params.model_name
        if params.features:
            flt["Features"] = list(params.features)
        if flt:
            body["Filter"] = flt
        result = self._action("ListModelProvider", body)
        out = V1ModelProviderList()
        if isinstance(result, dict):
            out.items = list_from_items(V1ModelProvider, result, key="Models")
            out.total = result.get("Total")
        return out

    def get_model_provider(self, params: V1ModelProviderGetParams) -> List[V1ModelProvider]:
        if not params.ids:
            raise ValueError("hibot: provider IDs are required")
        body = {"IDs": list(params.ids)}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("GetProvider", body)
        return list_from_items(V1ModelProvider, result)

    def get_model_provider_credential_schema(self, params: V1ModelProviderCredentialSchemaParams):
        if not params.provider:
            raise ValueError("hibot: provider is required")
        if not params.type:
            raise ValueError("hibot: model type is required")
        body = {"Provider": params.provider, "Type": params.type}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        if params.spec:
            body["Spec"] = params.spec
        if params.features:
            body["Features"] = list(params.features)
        result = self._action("GetModelProviderCredentialSchema", body)
        if isinstance(result, dict):
            return result.get("CredentialSchema")
        return result
