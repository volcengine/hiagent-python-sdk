# coding:utf-8
import os
from typing import Optional

from dotenv import load_dotenv

from hiagent_api.knowledgebase import KnowledgebaseService
from hiagent_api.knowledgebase_types import QueryRequest

load_dotenv()


def query_1(type: int, retrieval_search_method: int, rerank_id: Optional[str] = None):
    svc = KnowledgebaseService(
        endpoint=os.getenv("HIAGENT_TOP_ENDPOINT") or "", region="cn-north-1"
    )

    resp = svc.query(
        QueryRequest(
            workspace_id="cuq0pp9s7366bfl0cns0",
            dataset_ids=["019613e3-f37b-7b80-8e0a-579435bb9870"],
            keywords=["大熊猫的生活习性"],
            top_k=3,
            score_threshold=0.4,
            type=type,
            retrieval_search_method=retrieval_search_method,
            rerank_id=rerank_id,
        )
    )
    print(resp)


if __name__ == "__main__":
    query_1(1, 0)
    query_1(1, 1)
    query_1(1, 2, "d0nd3e7ko7hnmife1eu0")
