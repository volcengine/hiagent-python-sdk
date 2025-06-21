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
from typing import List

from langchain_core.callbacks import (
    AsyncCallbackManagerForRetrieverRun,
    CallbackManagerForRetrieverRun,
)
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever as LangChainBaseRetriever

from hiagent_components.retriever.base import BaseRetriever


class LangChainRetriever(LangChainBaseRetriever):
    retriever: BaseRetriever

    @classmethod
    def from_retriever(cls, retriever: BaseRetriever) -> "LangChainRetriever":
        return cls(
            retriever=retriever,
        )

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        resp = self.retriever.invoke(
            {
                "query": query,
            }
        )

        docs = resp.results
        res = []
        for doc in docs:
            res.append(
                Document(
                    page_content=doc.content,
                )
            )
        return res

    async def _aget_relevant_documents(
        self, query: str, *, run_manager: AsyncCallbackManagerForRetrieverRun
    ) -> list[Document]:
        resp = await self.retriever.ainvoke(
            {
                "query": query,
            }
        )

        docs = resp.results
        res = []
        for doc in docs:
            res.append(
                Document(
                    page_content=doc.content,
                )
            )
        return res
