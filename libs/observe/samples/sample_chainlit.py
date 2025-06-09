import time
import uuid

import chainlit as cl
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
from langchain_core.callbacks import BaseCallbackHandler
from langchain_ollama import OllamaLLM


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    print(username, password)
    if (username, password) == ("admin", "Admin@123"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None


@cl.on_chat_start
async def on_chat_start():
    model = OllamaLLM(model="gemma3:1b")
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

    def on_llm_new_token(self, token: str, **kwargs):
        if not self.first_token_received and self.start_time is not None:
            latency = time.time() - self.start_time
            print(f"TTFT: {latency:.4f}s")
            self.first_token_received = True


@cl.on_message
async def on_message(message: cl.Message):
    runnable: Runnable = cl.user_session.get("runnable")
    conversation_id: str = cl.user_session.get("conversation_id")

    print(message.content, conversation_id)

    msg = cl.Message(content="")

    async for chunk in runnable.astream(
        {"question": message.content},
        config=RunnableConfig(
            callbacks=[cl.LangchainCallbackHandler(), FirstTokenLatencyCallback()]
        ),
    ):
        await msg.stream_token(chunk)

    await msg.send()


# chainlit run sample_chainlit.py -w
