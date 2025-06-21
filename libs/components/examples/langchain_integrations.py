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
from hiagent_api.chat import ChatService
from hiagent_api.knowledgebase import KnowledgebaseService
from hiagent_api.workflow import WorkflowService
from hiagent_components.agent.base import Agent
from hiagent_components.integrations.langchain import LangChainRetriever
from hiagent_components.integrations.langchain.tool import LangChainTool
from hiagent_components.retriever.base import KnowledgeRetriever
from hiagent_components.workflow.base import Workflow

load_dotenv()


def get_workflow_svc() -> WorkflowService:
    svc = WorkflowService(
        endpoint=os.getenv("HIAGENT_TOP_ENDPOINT") or "", region="cn-north-1"
    )

    svc.set_app_base_url(os.getenv("HIAGENT_APP_BASE_URL") or "")

    return svc


def get_chat_svc() -> ChatService:
    svc = ChatService(
        endpoint=os.getenv("HIAGENT_TOP_ENDPOINT") or "", region="cn-north-1"
    )

    svc.set_app_base_url(os.getenv("HIAGENT_APP_BASE_URL") or "")

    return svc


def get_knowledgebase_svc() -> KnowledgebaseService:
    svc = KnowledgebaseService(
        endpoint=os.getenv("HIAGENT_TOP_ENDPOINT") or "", region="cn-north-1"
    )

    return svc


async def ainvoke_workflow_as_langchain_tool():
    app_key = os.getenv("HIAGENT_APP_KEY") or ""
    workflow = await Workflow.ainit(
        svc=get_workflow_svc(),
        app_key=app_key,
        workflow_id="cvel84kg58epjrfkvtb0",
        workspace_id="cuq0pp9s7366bfl0cns0",
        user_id="test",
    )

    tool = LangChainTool.from_tool(workflow.as_tool())
    print(f"workflow langchain tool input schema: {tool.args_schema}")

    output = await tool.arun(tool_input={"query": "你好"})
    print("invoke workflow as langchain tool: ", output)


def invoke_agent_as_langchain_tool():
    app_key = os.getenv("HIAGENT_AGENT_APP_KEY") or ""
    agent = Agent.init(
        svc=get_chat_svc(),
        app_key=app_key,
        user_id="test",
        variables={"name": "天气小助手"},
    )
    tool = LangChainTool.from_tool(agent.as_tool())

    output = tool.run(tool_input={"query": "今天深圳的天气怎么样"})
    print(f"agent langchain tool input schema: {tool.input_schema}")
    print("invoke agent as langchain tool output: ", output)


async def ainvoke_retriever_as_langchain_tool():
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

    tool = LangChainTool.from_tool(retriever.as_tool())
    output = await tool.arun(tool_input={"query": "大熊猫的生活习性"})

    print(f"retriever langchain tool input schema: {tool.input_schema}")
    print(f"invoke retriever as langchain tool output: {output}")


async def ainvoke_retriever_as_langchain_retriever():
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

    retriever = LangChainRetriever.from_retriever(retriever)
    output = await retriever.ainvoke("大熊猫的生活习性")

    print(f"invoke retriever as langchain tool output: {output}")


if __name__ == "__main__":
    asyncio.run(ainvoke_workflow_as_langchain_tool())
    invoke_agent_as_langchain_tool()
    asyncio.run(ainvoke_retriever_as_langchain_retriever())
    asyncio.run(ainvoke_retriever_as_langchain_tool())
