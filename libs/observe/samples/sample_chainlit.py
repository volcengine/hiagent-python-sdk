import logging
import os
import time
import uuid

import chainlit as cl
from dotenv import load_dotenv
from hiagent_observe import client, helper, semconv
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
from langchain_core.callbacks import BaseCallbackHandler
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
    def __init__(self):
        super().__init__()
        self.start_time = None
        self.first_token_received = False

    def on_llm_start(self, *args, **kwargs):
        self.start_time = time.time()
        self.first_token_received = False
        with helper.start_trace(name="llm_start", provider=provider) as span:
            span.set_attributes(
                {
                    semconv.SemanticConvention.SPAN_TYPE: semconv.SpanType.START.value,
                }
            )

    def on_llm_new_token(self, token: str, **kwargs):
        if not self.first_token_received and self.start_time is not None:
            self.first_token_received = True
            latency = (time.time() - self.start_time) * 1000
            with helper.start_trace(name="llm_new_token", provider=provider) as span:
                span.set_attributes(
                    {
                        semconv.SemanticConvention.LATENCT_FIRST_RESP: latency,
                        semconv.SemanticConvention.SPAN_TYPE: semconv.SpanType.LLM.value,
                    }
                )

    def on_llm_end(self, response, *, run_id, parent_run_id=None, **kwargs):
        output = response.generations[0][0].text
        latency = (time.time() - self.start_time) * 1000
        with helper.start_trace(name="llm_end", provider=provider) as span:
            span.set_attributes(
                {
                    semconv.SemanticConvention.LATENCY: latency,
                    semconv.SemanticConvention.SPAN_TYPE: semconv.SpanType.LLM.value,
                    semconv.SemanticConvention.OUTPUT: output,
                    semconv.SemanticConvention.OUTPUT_RAW: output,
                }
            )
            span.set_status(StatusCode.OK)


@cl.on_message
async def on_message(message: cl.Message):
    runnable: Runnable = cl.user_session.get("runnable")
    conversation_id: str = cl.user_session.get("conversation_id")

    msg = cl.Message(content="")

    with helper.start_trace(name="do-worker", provider=provider) as span:
        span.set_attributes(
            {
                semconv.SemanticConvention.CONVERSATION_ID: conversation_id,
                semconv.SemanticConvention.MESSAGE_ID: str(uuid.uuid4()),
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
                    FirstTokenLatencyCallback(),
                ]
            ),
        ):
            await msg.stream_token(chunk)

        await msg.send()


# chainlit run sample_chainlit.py -w -h
