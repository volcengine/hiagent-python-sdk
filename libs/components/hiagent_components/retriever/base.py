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
from concurrent.futures import Executor
from typing import Any, Optional

from hiagent_api.knowledgebase import KnowledgebaseService
from hiagent_api.knowledgebase_types import QueryRequest, QueryResponse

from hiagent_components.base import Executable


class BaseRetriever(Executable):
    def __init__(
        self,
        svc: KnowledgebaseService,
        name: str,
        description: str,
        workspace_id: str,
        dataset_ids: list[str],
        top_k: int = 5,
        score_threshold: float = 0.5,
        rerank_id: Optional[str] = None,
        expand: bool = False,
        expand_num: int = 1,
        type: int = 1,
        retrieval_search_method: int = 0,
    ):
        """
        初始化
        Args:
            svc: KnowledgebaseService
            name: 知识库名称
            description: 知识库描述
            workspace_id: 工作空间 id
            dataset_ids: 知识库 id
            top_k: top k
            score_threshold: 分数阈值 0~1
            rerank_id: rerank 模型 id，混合检索时需要
            expand: 膨胀系数开关
            expand_num: 膨胀系数，1~3
            type: 检索类型, 1-知识库，2-问答库, 3-术语库
            retrieval_search_method: 检索方法 0-语义检索，1-全文检索，2-混合检索
        """
        self.svc = svc
        self.dataset_ids = dataset_ids
        self.top_k = top_k
        self.score_threshold = score_threshold
        self.rerank_id = rerank_id
        self.expand = expand
        self.expand_num = expand_num
        self.type = type
        self.retrieval_search_method = retrieval_search_method
        self.name = name
        self.description = description
        self.workspace_id = workspace_id

    @property
    def input_schema(self):
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "要检索的语句或关键词",
                },
            },
            "required": ["query"],
        }

    def invoke(self, input: dict, **kwargs: Any) -> QueryResponse:
        query = input.get("query")
        if not query:
            raise ValueError("retriever invoke input should contains 'query'")

        resp = self.svc.query(
            QueryRequest(
                workspace_id=self.workspace_id,
                dataset_ids=self.dataset_ids,
                keywords=[query],
                top_k=self.top_k,
                score_threshold=self.score_threshold,
                rerank_id=self.rerank_id,
                expand=self.expand,
                expand_num=self.expand_num,
                type=self.type,
                retrieval_search_method=self.retrieval_search_method,
            )
        )

        return resp

    async def ainvoke(
        self, input: dict, executor: Optional[Executor] = None, **kwargs: Any
    ) -> QueryResponse:
        query = input.get("query")
        if not query:
            raise ValueError("retriever invoke input should contains 'query'")

        resp = await self.svc.aquery(
            QueryRequest(
                workspace_id=self.workspace_id,
                dataset_ids=self.dataset_ids,
                keywords=[query],
                top_k=self.top_k,
                score_threshold=self.score_threshold,
                rerank_id=self.rerank_id,
                expand=self.expand,
                expand_num=self.expand_num,
                type=self.type,
                retrieval_search_method=self.retrieval_search_method,
            )
        )

        return resp


class KnowledgeRetriever(BaseRetriever):
    def __init__(
        self,
        svc: KnowledgebaseService,
        name: str,
        description: str,
        workspace_id: str,
        dataset_ids: list[str],
        top_k: int = 5,
        score_threshold: float = 0.5,
        rerank_id: Optional[str] = None,
        expand: bool = False,
        expand_num: int = 1,
        retrieval_search_method: int = 0,
    ):
        super().__init__(
            svc=svc,
            name=name,
            description=description,
            workspace_id=workspace_id,
            dataset_ids=dataset_ids,
            top_k=top_k,
            score_threshold=score_threshold,
            rerank_id=rerank_id,
            expand=expand,
            expand_num=expand_num,
            retrieval_search_method=retrieval_search_method,
            type=1,
        )


class QARetriever(BaseRetriever):
    def __init__(
        self,
        svc: KnowledgebaseService,
        name: str,
        description: str,
        workspace_id: str,
        dataset_ids: list[str],
        top_k: int = 5,
        score_threshold: float = 0.5,
        rerank_id: Optional[str] = None,
        expand: bool = False,
        expand_num: int = 1,
        retrieval_search_method: int = 0,
    ):
        super().__init__(
            svc=svc,
            name=name,
            description=description,
            workspace_id=workspace_id,
            dataset_ids=dataset_ids,
            top_k=top_k,
            score_threshold=score_threshold,
            rerank_id=rerank_id,
            expand=expand,
            expand_num=expand_num,
            retrieval_search_method=retrieval_search_method,
            type=2,
        )


class TerminologyRetriever(BaseRetriever):
    def __init__(
        self,
        svc: KnowledgebaseService,
        name: str,
        description: str,
        workspace_id: str,
        dataset_ids: list[str],
        top_k: int = 5,
        score_threshold: float = 0.5,
        rerank_id: Optional[str] = None,
        expand: bool = False,
        expand_num: int = 1,
        retrieval_search_method: int = 0,
    ):
        super().__init__(
            svc=svc,
            name=name,
            description=description,
            workspace_id=workspace_id,
            dataset_ids=dataset_ids,
            top_k=top_k,
            score_threshold=score_threshold,
            rerank_id=rerank_id,
            expand=expand,
            expand_num=expand_num,
            retrieval_search_method=retrieval_search_method,
            type=3,
        )
