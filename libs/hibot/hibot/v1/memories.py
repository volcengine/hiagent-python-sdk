"""V1 memory store and memory file service."""

from __future__ import annotations

from ._helpers import from_dict, list_from_items
from ._server_service import ServerService, encode_page, put_if
from .types import (
    V1MemoryFile,
    V1MemoryFileDeleteParams,
    V1MemoryFileGetParams,
    V1MemoryFileList,
    V1MemoryFileListParams,
    V1MemoryFileSearchParams,
    V1MemoryFileUpsertParams,
    V1MemoryFileUpsertResult,
    V1MemoryStore,
    V1MemoryStoreDeleteParams,
    V1MemoryStoreGetParams,
    V1MemoryStoreList,
    V1MemoryStoreListParams,
    V1MemoryStoreNewParams,
    V1MemoryStoreUpdateParams,
    V1Page,
)


class MemoriesService(ServerService):
    def create_store(self, params: V1MemoryStoreNewParams) -> V1MemoryStore:
        if not params.name or not params.alias or not params.description:
            raise ValueError(
                "hibot: memory store name, alias, and description are required"
            )
        body = {
            "Name": params.name,
            "Alias": params.alias,
            "Description": params.description,
        }
        put_if(body, "Access", params.access)
        put_if(body, "ExtractionPolicy", params.extraction_policy)
        put_if(body, "QuotaPolicy", params.quota_policy)
        put_if(body, "WorkspaceID", params.workspace_id)
        result = self._action("CreateMemoryStore", body)
        new_id = result.get("ID") if isinstance(result, dict) else None
        if not new_id:
            raise ValueError("hibot: create memory store response missing ID")
        return V1MemoryStore(id=new_id, name=params.name, alias=params.alias)

    def list_stores(
        self, params: V1MemoryStoreListParams = V1MemoryStoreListParams()
    ) -> V1MemoryStoreList:
        body = {}
        put_if(body, "Keyword", params.keyword)
        put_if(body, "Page", encode_page(params.page))
        put_if(body, "WorkspaceID", params.workspace_id)
        result = self._action("ListMemoryStores", body)
        out = V1MemoryStoreList()
        if isinstance(result, dict):
            out.items = list_from_items(V1MemoryStore, result)
            out.page = from_dict(V1Page, result.get("Page"))
        return out

    def get_store(self, params: V1MemoryStoreGetParams) -> V1MemoryStore:
        if not params.store_id:
            raise ValueError("hibot: memory store id is required")
        body = {"StoreID": params.store_id}
        put_if(body, "WorkspaceID", params.workspace_id)
        result = self._action("GetMemoryStore", body)
        decoded = from_dict(V1MemoryStore, result) or V1MemoryStore()
        if not decoded.id:
            raise ValueError("hibot: get memory store response missing ID")
        return decoded

    def update_store(self, params: V1MemoryStoreUpdateParams) -> None:
        if not params.store_id:
            raise ValueError("hibot: memory store id is required")
        body = {"StoreID": params.store_id}
        for key, value in (
            ("Name", params.name),
            ("Description", params.description),
            ("Access", params.access),
            ("ExtractionPolicy", params.extraction_policy),
            ("QuotaPolicy", params.quota_policy),
        ):
            put_if(body, key, value, allow_empty=True)
        put_if(body, "WorkspaceID", params.workspace_id)
        self._action("UpdateMemoryStore", body)

    def delete_store(self, params: V1MemoryStoreDeleteParams) -> None:
        if not params.store_id:
            raise ValueError("hibot: memory store id is required")
        body = {"StoreID": params.store_id}
        put_if(body, "WorkspaceID", params.workspace_id)
        self._action("DeleteMemoryStore", body)

    def list_files(self, params: V1MemoryFileListParams) -> V1MemoryFileList:
        if not params.store_id:
            raise ValueError("hibot: memory store id is required")
        body = {"StoreID": params.store_id}
        put_if(body, "Prefix", params.prefix)
        put_if(body, "Page", encode_page(params.page))
        put_if(body, "WorkspaceID", params.workspace_id)
        return self._file_list("ListMemoryFiles", body)

    def search_files(self, params: V1MemoryFileSearchParams) -> V1MemoryFileList:
        if not params.store_id or not params.keyword:
            raise ValueError("hibot: memory store id and keyword are required")
        body = {"StoreID": params.store_id, "Keyword": params.keyword}
        put_if(body, "Page", encode_page(params.page))
        put_if(body, "WorkspaceID", params.workspace_id)
        return self._file_list("SearchMemoryFiles", body)

    def get_file(self, params: V1MemoryFileGetParams) -> V1MemoryFile:
        if not params.store_id or not params.path:
            raise ValueError("hibot: memory store id and path are required")
        body = {"StoreID": params.store_id, "Path": params.path}
        put_if(body, "IncludeContent", params.include_content, allow_empty=True)
        put_if(body, "WorkspaceID", params.workspace_id)
        result = self._action("GetMemoryFile", body)
        decoded = from_dict(V1MemoryFile, result) or V1MemoryFile()
        if not decoded.id:
            raise ValueError("hibot: get memory file response missing ID")
        return decoded

    def upsert_file(self, params: V1MemoryFileUpsertParams) -> V1MemoryFileUpsertResult:
        if not params.store_id or not params.path:
            raise ValueError("hibot: memory store id and path are required")
        body = {
            "StoreID": params.store_id,
            "Path": params.path,
            "Content": params.content,
        }
        put_if(body, "BaseSha256", params.base_sha256)
        put_if(body, "BaseRevision", params.base_revision, allow_empty=True)
        put_if(body, "WorkspaceID", params.workspace_id)
        result = self._action("UpsertMemoryFile", body)
        return from_dict(V1MemoryFileUpsertResult, result) or V1MemoryFileUpsertResult()

    def delete_file(self, params: V1MemoryFileDeleteParams) -> None:
        if not params.store_id or not params.path:
            raise ValueError("hibot: memory store id and path are required")
        body = {"StoreID": params.store_id, "Path": params.path}
        put_if(body, "BaseSha256", params.base_sha256)
        put_if(body, "BaseRevision", params.base_revision, allow_empty=True)
        put_if(body, "WorkspaceID", params.workspace_id)
        self._action("DeleteMemoryFile", body)

    def _file_list(self, action: str, body: dict) -> V1MemoryFileList:
        result = self._action(action, body)
        out = V1MemoryFileList()
        if isinstance(result, dict):
            out.items = list_from_items(V1MemoryFile, result)
            out.page = from_dict(V1Page, result.get("Page"))
        return out


__all__ = ["MemoriesService"]
