# 关于 HiAgent-SDK

[English](README.md) | 中文README

HiAgent-SDK是火山引擎的HiAgent产品的SDK，开发者可使用该SDK，快捷的开发功能，提升开发效率。HiAgent-SDK提供了完整的AI原生应用开发套件，包括丰富的开发组件和应用示例代码。

## 架构

![img.png](img.png)

## 快速开始

```python
import os

from dotenv import load_dotenv
from hiagent_api.chat import ChatService
from hiagent_api.knowledgebase import KnowledgebaseService
from hiagent_api.tool import ToolService
from hiagent_components.agent import Agent
from hiagent_components.integrations.langchain import LangChainTool
from hiagent_components.retriever import KnowledgeRetriever
from hiagent_components.tool import Tool
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.callbacks import StdOutCallbackHandler
from langchain_openai import ChatOpenAI
from langsmith import Client

load_dotenv()


def get_tool_svc() -> ToolService:
    svc = ToolService(
        endpoint=os.getenv("HIAGENT_TOP_ENDPOINT") or "", region="cn-north-1"
    )
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


if __name__ == "__main__":
    tool = Tool.init(
        svc=get_tool_svc(),
        workspace_id="cuq0pp9s7366bfl0cns0",
        tool_id="5njoa3j2m2t5cpaotjlg"
    )

    app_key = os.getenv("HIAGENT_AGENT_APP_KEY") or ""
    agent = Agent.init(
        svc=get_chat_svc(),
        app_key=app_key,
        user_id="test",
        variables={"name": "weather_assistant"},
    )

    retriever = KnowledgeRetriever(
        svc=get_knowledgebase_svc(),
        name="knowledge_tool",
        description="knowledge retriever, used to search knowledge about pandas",
        workspace_id="cuq0pp9s7366bfl0cns0",
        dataset_ids=["019613e3-f37b-7b80-8e0a-579435bb9870"],
        top_k=3,
        score_threshold=0.4,
        retrieval_search_method=0,
    )

    ocr_tool = LangChainTool.from_tool(tool)
    agent_tool = LangChainTool.from_tool(agent.as_tool())
    retriever_tool = LangChainTool.from_tool(retriever.as_tool())
    tools = [ocr_tool, agent_tool, retriever_tool]

    # Pull the prompt template from the hub
    # ReAct = Reason and Action
    # https://smith.langchain.com/hub/hwchase17/react
    client = Client()
    prompt = client.pull_prompt("hwchase17/structured-chat-agent")
    prompt.messages[0].prompt.template += "\n\n## Noice\n\n tool's action_input must be json object rather than string"

    callbacks = [StdOutCallbackHandler()]

    # export OPENAI_API_KEY=xxxx
    # Initialize a ChatOpenAI model
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL"),  # pro
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        callbacks=callbacks,
    )
    agent = create_structured_chat_agent(
        llm=llm,
        tools=tools,
        prompt=prompt,
    )
    # Create an agent executor from the agent and tools
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=False,
        callbacks=callbacks,
    )
    # Run the agent with a test query
    response = agent_executor.invoke(
        {"input": "Is the weather in Shenzhen suitable for going out today?"},
    )

    # Print the response from the agent
    print("response:", response)
```

## License

该项目采用 [Apache-2.0 License](LICENSE) 许可。
