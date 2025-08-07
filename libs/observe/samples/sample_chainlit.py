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
import json
import logging
import os
import time
import uuid
from typing import Any, Optional
from uuid import UUID

import chainlit as cl
import tiktoken
from dotenv import load_dotenv
from hiagent_observe import client, helper, semconv
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_ollama import OllamaLLM
from opentelemetry.trace import StatusCode

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

try:
    global provider
    provider = client.init(
        trace_endpoint=os.getenv("HIAGENT_TRACE_ENDPOINT"),
        top_endpoint=os.getenv("HIAGENT_TOP_ENDPOINT"),
        ak=os.getenv("VOLC_ACCESSKEY"),
        sk=os.getenv("VOLC_SECRETKEY"),
        workspace_id=os.getenv("WORKSPACE_ID"),
        app_id=os.getenv("CUSTOM_APP_ID"),
    )
except Exception as e:
    raise RuntimeError(e)


def count_tokens_openai(text: str, model: str = "gpt-3.5-turbo") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    if (username, password) == ("admin", "Admin@123"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None


model_id = str(uuid.uuid4())
model_name = "gemma3:1b"


@cl.on_chat_start
async def on_chat_start():
    model = OllamaLLM(model=model_name)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You're a very knowledgeable historian who provides accurate and eloquent answers to historical questions.",
            ),
            ("human", "{question}"),
        ]
    )

    runnable = prompt | model | StrOutputParser()
    cl.user_session.set("runnable", runnable)
    cl.user_session.set("conversation_id", str(uuid.uuid4()))


class FirstTokenLatencyCallback(BaseCallbackHandler):
    def __init__(self, message_id: str):
        super().__init__()
        self.start_time = None
        self.first_token_received = False
        self.input = ""
        self.latency_first_resp = None
        self.message_id = message_id

    def on_llm_start(
        self,
        serialized: dict[str, Any],
        prompts: list[str],
        *,
        run_id: UUID,
        **kwargs: Any,
    ):
        self.start_time = time.time()
        self.first_token_received = False
        self.input = prompts[0]
        with helper.start_trace(name="llm_start", provider=provider) as span:
            span.set_attributes(
                {
                    semconv.SemanticConvention.SPAN_TYPE: semconv.SpanType.START.value,
                }
            )

    def on_llm_new_token(self, token: str, *, run_id: UUID, **kwargs):
        if not self.first_token_received and self.start_time is not None:
            self.first_token_received = True
            latency = (time.time() - self.start_time) * 1000
            self.latency_first_resp = round(latency, 1)
            with helper.start_trace(name="llm_new_token", provider=provider) as span:
                span.set_attributes(
                    {
                        semconv.SemanticConvention.LATENCT_FIRST_RESP: round(
                            latency, 1
                        ),
                        semconv.SemanticConvention.INPUT: json.dumps(
                            {
                                "input": self.input,
                            },
                            ensure_ascii=False,
                        ),
                        semconv.SemanticConvention.INPUT_RAW: self.input,
                    }
                )

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ):
        output = response.generations[0][0].text
        latency = (time.time() - self.start_time) * 1000
        with helper.start_trace(name="llm_end", provider=provider) as span:
            span.set_attributes(
                {
                    semconv.SemanticConvention.MESSAGE_ID: self.message_id,
                    semconv.SemanticConvention.LATENCY: round(latency, 1),
                    semconv.SemanticConvention.LATENCT_FIRST_RESP: self.latency_first_resp,
                    semconv.SemanticConvention.MODEL_ID: model_id,
                    semconv.SemanticConvention.MODEL_NAME: model_name,
                    semconv.SemanticConvention.SPAN_TYPE: semconv.SpanType.LLM.value,
                    semconv.SemanticConvention.INPUT: json.dumps(
                        {
                            "input": self.input,
                        },
                        ensure_ascii=False,
                    ),
                    semconv.SemanticConvention.INPUT_RAW: self.input,
                    semconv.SemanticConvention.INPUT_TOKENS: count_tokens_openai(
                        self.input
                    ),
                    semconv.SemanticConvention.OUTPUT: json.dumps(
                        {
                            "output": output,
                        },
                        ensure_ascii=False,
                    ),
                    semconv.SemanticConvention.OUTPUT_RAW: output,
                    semconv.SemanticConvention.OUTPUT_TOKENS: count_tokens_openai(
                        output
                    ),
                    semconv.SemanticConvention.INPUT_TOKENS: count_tokens_openai(
                        self.input
                    ),
                    semconv.SemanticConvention.OUTPUT_TOKENS: count_tokens_openai(
                        output
                    ),
                    semconv.SemanticConvention.OUTPUT_PRICE: 2.3,
                    semconv.SemanticConvention.PRICE_UNIT: 0.1,
                    semconv.SemanticConvention.INPUT_PRICE: 34.5,
                    semconv.SemanticConvention.CURRENCY: "USD",
                }
            )
            span.set_status(status=StatusCode.OK, description="")


@cl.on_message
async def on_message(message: cl.Message):
    runnable: Runnable = cl.user_session.get("runnable")
    conversation_id: str = cl.user_session.get("conversation_id")

    msg = cl.Message(content="")

    message_id = str(uuid.uuid4())
    with helper.start_trace(name="do-worker", provider=provider) as span:
        span.set_attributes(
            {
                semconv.SemanticConvention.CONVERSATION_ID: conversation_id,
                semconv.SemanticConvention.MESSAGE_ID: message_id,
                semconv.SemanticConvention.INPUT: message.content,
                semconv.SemanticConvention.INPUT_RAW: message.content,
                semconv.SemanticConvention.MODEL_ID: model_id,
                semconv.SemanticConvention.MODEL_NAME: model_name,
            }
        )
        async for chunk in runnable.astream(
            {"question": message.content},
            config=RunnableConfig(
                callbacks=[
                    cl.LangchainCallbackHandler(),
                    FirstTokenLatencyCallback(message_id=message_id),
                ]
            ),
        ):
            await msg.stream_token(chunk)

        await msg.send()


# chainlit run sample_chainlit.py -w -h
