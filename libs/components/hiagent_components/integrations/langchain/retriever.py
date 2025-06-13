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
