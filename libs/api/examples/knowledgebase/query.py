# coding:utf-8
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
