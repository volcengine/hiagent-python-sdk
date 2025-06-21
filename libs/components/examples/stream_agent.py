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
from hiagent_components.agent.base import Agent

load_dotenv()


def get_chat_svc() -> ChatService:
    svc = ChatService(
        endpoint=os.getenv("HIAGENT_TOP_ENDPOINT") or "", region="cn-north-1"
    )

    svc.set_app_base_url(os.getenv("HIAGENT_APP_BASE_URL") or "")

    return svc


def stream_agent():
    app_key = os.getenv("HIAGENT_AGENT_APP_KEY") or ""
    agent = Agent.init(
        svc=get_chat_svc(),
        app_key=app_key,
        user_id="test",
        variables={},
    )
    print(f"agent name: {agent.name}")
    print(f"agent input schema: {agent.input_schema}")

    g = agent.stream({"query": "今天深圳的天气怎么样"})

    for event in g:
        print(event)


async def astream_agent():
    app_key = os.getenv("HIAGENT_AGENT_APP_KEY") or ""
    agent = await Agent.ainit(
        svc=get_chat_svc(),
        app_key=app_key,
        user_id="test",
        variables={"name": "天气小助手"},
    )
    print(f"agent name: {agent.name}")
    print(f"agent input schema: {agent.input_schema}")

    g = agent.astream({"query": "今天深圳的天气怎么样"})
    async for event in g:
        print(event)


if __name__ == "__main__":
    stream_agent()

    asyncio.run(astream_agent())
