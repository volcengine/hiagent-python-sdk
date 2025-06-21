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
import asyncio
import os

from dotenv import load_dotenv
from hiagent_api.knowledgebase import KnowledgebaseService
from hiagent_components.retriever.base import KnowledgeRetriever

load_dotenv()


def get_knowledgebase_svc() -> KnowledgebaseService:
    svc = KnowledgebaseService(
        endpoint=os.getenv("HIAGENT_TOP_ENDPOINT") or "", region="cn-north-1"
    )

    return svc


def invoke_retriever():
    retriever = KnowledgeRetriever(
        svc=get_knowledgebase_svc(),
        name="knowledge_tool",
        description="知识库工具，用来检索大熊猫的相关知识",
        workspace_id="cuq0pp9s7366bfl0cns0",
        dataset_ids=["019613e3-f37b-7b80-8e0a-579435bb9870"],
        top_k=3,
        score_threshold=0.4,
        retrieval_search_method=0,
    )

    output = retriever.invoke({"query": "大熊猫的生活习性"})

    print(f"retriever input schema: {retriever.input_schema}")
    print(f"retriever output: {output}")


async def ainvoke_retriever():
    retriever = KnowledgeRetriever(
        svc=get_knowledgebase_svc(),
        name="knowledge_tool",
        description="知识库工具，用来检索大熊猫的相关知识",
        workspace_id="cuq0pp9s7366bfl0cns0",
        dataset_ids=["019613e3-f37b-7b80-8e0a-579435bb9870"],
        top_k=3,
        score_threshold=0.4,
        retrieval_search_method=0,
    )

    output = await retriever.ainvoke({"query": "大熊猫的生活习性"})

    print(f"retriever input schema: {retriever.input_schema}")
    print(f"retriever output: {output}")


def invoke_retriever_as_tool():
    retriever = KnowledgeRetriever(
        svc=get_knowledgebase_svc(),
        name="knowledge_tool",
        description="知识库工具，用来检索大熊猫的相关知识",
        workspace_id="cuq0pp9s7366bfl0cns0",
        dataset_ids=["019613e3-f37b-7b80-8e0a-579435bb9870"],
        top_k=3,
        score_threshold=0.4,
        retrieval_search_method=0,
    )

    tool = retriever.as_tool()
    output = tool.invoke({"query": "大熊猫的生活习性"})

    print(f"retriever tool input schema: {tool.input_schema}")
    print(f"retriever tool output: {output}")


async def ainvoke_retriever_as_tool():
    retriever = KnowledgeRetriever(
        svc=get_knowledgebase_svc(),
        name="knowledge_tool",
        description="知识库工具，用来检索大熊猫的相关知识",
        workspace_id="cuq0pp9s7366bfl0cns0",
        dataset_ids=["019613e3-f37b-7b80-8e0a-579435bb9870"],
        top_k=3,
        score_threshold=0.4,
        retrieval_search_method=0,
    )

    tool = retriever.as_tool()
    output = await tool.ainvoke({"query": "大熊猫的生活习性"})

    print(f"retriever tool input schema: {tool.input_schema}")
    print(f"retriever tool output: {output}")


if __name__ == "__main__":
    invoke_retriever()
    asyncio.run(ainvoke_retriever())

    invoke_retriever_as_tool()
    asyncio.run(ainvoke_retriever_as_tool())
