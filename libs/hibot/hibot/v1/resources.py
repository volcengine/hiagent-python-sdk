"""V1 Resources & Directories services."""

from __future__ import annotations

from typing import List

from .._request import Action
from .._version import SERVER_VERSION
from ._helpers import from_dict, list_from_items
from .types import (
    V1Directory,
    V1DirectoryDeleteParams,
    V1DirectoryGetByNameParams,
    V1DirectoryList,
    V1DirectoryListParams,
    V1DirectoryNewParams,
    V1DirectoryUpdateParams,
    V1Resource,
    V1ResourceBatchGetParams,
    V1ResourceDeleteParams,
    V1ResourceGetByNameParams,
    V1ResourceList,
    V1ResourceListParams,
    V1ResourceNewParams,
    V1ResourceUpdateParams,
)


class _BaseService:
    def __init__(self, v1) -> None:
        self._v1 = v1

    def _action(self, name: str, body):
        return self._v1.requester.do_action(
            Action(service=self._v1.services.server, version=SERVER_VERSION, action=name, body=body)
        )


class DirectoriesService(_BaseService):
    def create(self, params: V1DirectoryNewParams) -> V1Directory:
        if not params.name:
            raise ValueError("hibot: directory name is required")
        body = {"Name": params.name}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("CreateDirectory", body)
        new_id = result.get("ID") if isinstance(result, dict) else None
        if not new_id:
            raise ValueError("hibot: create directory response missing ID")
        return V1Directory(id=new_id, name=params.name, workspace_id=params.workspace_id)

    def list(self, params: V1DirectoryListParams = V1DirectoryListParams()) -> V1DirectoryList:
        body = {}
        if params.name:
            body["Name"] = params.name
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        if params.page is not None:
            body["Page"] = {"PageNum": params.page.page_num, "PageSize": params.page.page_size}
        result = self._action("ListDirectories", body)
        out = V1DirectoryList()
        if isinstance(result, dict):
            out.items = list_from_items(V1Directory, result)
        return out

    def update(self, params: V1DirectoryUpdateParams) -> None:
        if not params.directory_id:
            raise ValueError("hibot: directory id is required")
        body = {"DirectoryID": params.directory_id}
        if params.name:
            body["Name"] = params.name
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        self._action("UpdateDirectory", body)

    def delete(self, params: V1DirectoryDeleteParams) -> None:
        if not params.directory_id:
            raise ValueError("hibot: directory id is required")
        body = {"DirectoryID": params.directory_id}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        self._action("DeleteDirectory", body)

    def get_by_name(self, params: V1DirectoryGetByNameParams) -> V1Directory:
        if not params.name:
            raise ValueError("hibot: directory name is required")
        body = {"Name": params.name}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("GetDirectoryByName", body)
        d = result.get("Directory") if isinstance(result, dict) else None
        decoded = from_dict(V1Directory, d) or V1Directory()
        if not decoded.id:
            raise ValueError("hibot: get directory by name response missing ID")
        return decoded


class ResourcesService(_BaseService):
    def __init__(self, v1) -> None:
        super().__init__(v1)
        self.directories = DirectoriesService(v1)

    def create(self, params: V1ResourceNewParams) -> V1Resource:
        if not params.name:
            raise ValueError("hibot: resource Name is required")
        if not params.blob_id:
            raise ValueError("hibot: resource BlobID is required (call uploads.upload_blob first)")
        body = {"Name": params.name, "BlobID": params.blob_id}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        if params.directory_id:
            body["DirectoryID"] = params.directory_id
        result = self._action("CreateResource", body)
        new_id = result.get("ID") if isinstance(result, dict) else None
        if not new_id:
            raise ValueError("hibot: create resource response missing ID")
        return V1Resource(
            id=new_id,
            name=params.name,
            type=params.type,
            directory_id=params.directory_id,
        )

    def list(self, params: V1ResourceListParams = V1ResourceListParams()) -> V1ResourceList:
        body = {}
        if params.directory_id:
            body["DirectoryID"] = params.directory_id
        if params.name:
            body["Name"] = params.name
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        if params.page is not None:
            body["Page"] = {"PageNum": params.page.page_num, "PageSize": params.page.page_size}
        result = self._action("ListResources", body)
        out = V1ResourceList()
        if isinstance(result, dict):
            out.items = list_from_items(V1Resource, result)
        return out

    def update(self, params: V1ResourceUpdateParams) -> None:
        if not params.resource_id:
            raise ValueError("hibot: resource id is required")
        body = {"ResourceID": params.resource_id, "Name": params.name}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        if params.directory_id is not None:
            body["DirectoryID"] = params.directory_id
        self._action("UpdateResource", body)

    def delete(self, params: V1ResourceDeleteParams) -> None:
        if not params.resource_id:
            raise ValueError("hibot: resource id is required")
        body = {"ResourceID": params.resource_id}
        if params.directory_id:
            body["DirectoryID"] = params.directory_id
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        self._action("DeleteResource", body)

    def get_by_name(self, params: V1ResourceGetByNameParams) -> V1Resource:
        if not params.name:
            raise ValueError("hibot: resource name is required")
        body = {"Name": params.name}
        if params.directory_id:
            body["DirectoryID"] = params.directory_id
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("GetResourceByName", body)
        r = result.get("Resource") if isinstance(result, dict) else None
        decoded = from_dict(V1Resource, r) or V1Resource()
        if not decoded.id:
            raise ValueError("hibot: get resource by name response missing ID")
        return decoded

    def batch_get(self, params: V1ResourceBatchGetParams) -> List[V1Resource]:
        if not params.ids:
            raise ValueError("hibot: resource IDs are required")
        body = {"IDs": list(params.ids)}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("BatchGetResources", body)
        return list_from_items(V1Resource, result)
