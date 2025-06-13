import asyncio
import os

from dotenv import load_dotenv
from hiagent_api.chat import ChatService
from hiagent_components.agent.base import Agent

load_dotenv()


def get_chat_svc() -> ChatService:
    svc = ChatService(
        endpoint=os.getenv("HIAGENT_TOP_ENDPOINT") or "", region="cn-north-1"
    )

    svc.set_app_base_url(os.getenv("HIAGENT_APP_BASE_URL") or "")

    return svc


def invoke_agent():
    app_key = os.getenv("HIAGENT_AGENT_APP_KEY") or ""
    agent = Agent.init(
        svc=get_chat_svc(),
        app_key=app_key,
        user_id="test",
        variables={"name": "天气小助手"},
    )

    output = agent.invoke({"query": "今天深圳的天气怎么样"})

    print(f"agent name: {agent.name}")
    print(f"agent input schema: {agent.input_schema}")
    print(f"agent_output: {output}")


async def ainvoke_agent():
    app_key = os.getenv("HIAGENT_AGENT_APP_KEY") or ""
    agent = await Agent.ainit(
        svc=get_chat_svc(),
        app_key=app_key,
        user_id="test",
        variables={"name": "天气小助手"},
    )

    output = await agent.ainvoke({"query": "今天深圳的天气怎么样"})

    print(f"agent name: {agent.name}")
    print(f"agent input schema: {agent.input_schema}")
    print(f"agent_output: {output}")


def invoke_agent_as_tool():
    app_key = os.getenv("HIAGENT_AGENT_APP_KEY") or ""
    agent = Agent.init(
        svc=get_chat_svc(),
        app_key=app_key,
        user_id="test",
        variables={"name": "天气小助手"},
    )

    tool = agent.as_tool()
    output = tool.invoke({"query": "今天深圳的天气怎么样"})
    print("tool input schema: ", tool.input_schema)
    print("tool name: ", tool.name)
    print("tool description: ", tool.description)
    print("tool output: ", output)


async def ainvoke_agent_as_tool():
    app_key = os.getenv("HIAGENT_AGENT_APP_KEY") or ""
    agent = await Agent.ainit(
        svc=get_chat_svc(),
        app_key=app_key,
        user_id="test",
        variables={"name": "天气小助手"},
    )
    tool = agent.as_tool()
    output = await tool.ainvoke({"query": "今天深圳的天气怎么样"})
    print("tool input schema: ", tool.input_schema)
    print("tool name: ", tool.name)
    print("tool description: ", tool.description)
    print("tool output: ", output)


if __name__ == "__main__":
    invoke_agent()
    asyncio.run(ainvoke_agent())

    invoke_agent_as_tool()
    asyncio.run(ainvoke_agent_as_tool())
