"""V1 chat stream (mirrors go/hibot/v1/stream.go)."""

from __future__ import annotations

import json
from typing import Iterator, List, Optional

from .._response import APIError
from .._sse import ByteStreamDecoder, Frame
from ._helpers import from_dict
from .types import (
    V1_SESSION_CHAT_EVENT_COMPLETED,
    V1_SESSION_CHAT_EVENT_DELTA,
    V1_SESSION_CHAT_EVENT_FAILED,
    V1_SESSION_CHAT_EVENT_TOOL_COMPLETE,
    V1_SESSION_CHAT_EVENT_TOOL_START,
    V1Message,
    V1SessionChatError,
    V1SessionChatEvent,
    V1SessionTextDelta,
)

# Compat event names emitted by gateway legacy delivery + private Hermes runtime.
_MESSAGE_CHUNK_COMPAT = "message.chunk"
_MESSAGE_COMPLETED_COMPAT = "message.completed"
_MESSAGE_FAILED_COMPAT = "message.failed"
_MESSAGE_DELTA_UNDERSCORE = "message_delta"
_MESSAGE_CHUNK_UNDERSCORE = "message_chunk"
_MESSAGE_COMPLETED_UNDERSCORE = "message_completed"
_MESSAGE_FAILED_UNDERSCORE = "message_failed"
_RUN_COMPLETED_UNDERSCORE = "run_completed"
_RUN_FAILED_UNDERSCORE = "run_failed"


def normalize_chat_event_name(name: str) -> str:
    if name in (
        _MESSAGE_CHUNK_COMPAT,
        _MESSAGE_DELTA_UNDERSCORE,
        _MESSAGE_CHUNK_UNDERSCORE,
    ):
        return V1_SESSION_CHAT_EVENT_DELTA
    if name in (
        _MESSAGE_COMPLETED_COMPAT,
        _MESSAGE_COMPLETED_UNDERSCORE,
        _RUN_COMPLETED_UNDERSCORE,
    ):
        return V1_SESSION_CHAT_EVENT_COMPLETED
    if name in (
        _MESSAGE_FAILED_COMPAT,
        _MESSAGE_FAILED_UNDERSCORE,
        _RUN_FAILED_UNDERSCORE,
    ):
        return V1_SESSION_CHAT_EVENT_FAILED
    if name == "tool_started":
        return V1_SESSION_CHAT_EVENT_TOOL_START
    if name == "tool_completed":
        return V1_SESSION_CHAT_EVENT_TOOL_COMPLETE
    return name


def _first_key(payload: dict, *keys: str):
    for k in keys:
        if k in payload:
            return payload[k]
    return None


def decode_chat_event(event_name: str, data: str) -> V1SessionChatEvent:
    event = V1SessionChatEvent(type=normalize_chat_event_name(event_name), raw_data=data or "")
    if not data:
        return event
    try:
        payload = json.loads(data)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"hibot: decode sse data: {exc}") from exc
    if not isinstance(payload, dict):
        return event

    if not event.type:
        raw_type = payload.get("type")
        if isinstance(raw_type, str):
            event.type = normalize_chat_event_name(raw_type)

    rid = _first_key(payload, "request_id", "RequestID", "RequestId")
    if isinstance(rid, str):
        event.request_id = rid

    delta_raw = payload.get("delta")
    if isinstance(delta_raw, dict):
        text = delta_raw.get("text") or delta_raw.get("Text")
        if isinstance(text, str):
            event.delta = V1SessionTextDelta(text=text)
    elif isinstance(delta_raw, str):
        event.delta = V1SessionTextDelta(text=delta_raw)

    if not event.delta.text:
        text = _first_key(payload, "text", "Text")
        if isinstance(text, str):
            event.delta = V1SessionTextDelta(text=text)

    err = _first_key(payload, "error", "Error")
    if isinstance(err, dict):
        code = err.get("code") or err.get("Code") or ""
        message = err.get("message") or err.get("Message") or ""
        event.error = V1SessionChatError(code=str(code or ""), message=str(message or ""))
    elif isinstance(err, str):
        event.error = V1SessionChatError(message=err)

    code = _first_key(payload, "code", "Code")
    if not event.error.code and isinstance(code, str):
        event.error.code = code

    message_raw = _first_key(payload, "message", "Message")
    if isinstance(message_raw, dict):
        msg = from_dict(V1Message, message_raw)
        if msg is not None and (msg.id or msg.content or msg.role):
            event.message = msg
    elif isinstance(message_raw, str) and not event.error.message:
        event.error.message = message_raw

    if event.type == V1_SESSION_CHAT_EVENT_COMPLETED and event.message is None:
        msg = V1Message()
        mid = _first_key(payload, "message_id", "MessageID", "ID")
        if isinstance(mid, str):
            msg.id = mid
        content = _first_key(payload, "content", "Content")
        if isinstance(content, str):
            msg.content = content
        if msg.id or msg.content:
            event.message = msg

    return event


class V1SessionChatStream:
    """Synchronous SSE stream for chat events.

    Supports iterator protocol (``for event in stream``) and context-manager
    protocol (``with stream as s: ...``). Use ``final_message()`` after the
    stream completes, or ``accumulate()`` to drain into a single message.
    """

    def __init__(self, resp=None, *, error: Optional[BaseException] = None) -> None:
        self._resp = resp
        self._decoder = ByteStreamDecoder()
        self._iter: Optional[Iterator[bytes]] = None
        self._pending: List[Frame] = []
        self._eof = False
        self._closed = False
        self._current: Optional[V1SessionChatEvent] = None
        self._final: Optional[V1Message] = None
        self._error: Optional[BaseException] = error
        if resp is not None and not error:
            self._iter = iter(resp.iter_bytes())

    # iterator protocol -------------------------------------------------
    def __iter__(self) -> "V1SessionChatStream":
        return self

    def __next__(self) -> V1SessionChatEvent:
        if self.next():
            return self._current  # type: ignore[return-value]
        raise StopIteration

    # context manager protocol -----------------------------------------
    def __enter__(self) -> "V1SessionChatStream":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    # public API --------------------------------------------------------
    @property
    def current(self) -> Optional[V1SessionChatEvent]:
        return self._current

    @property
    def err(self) -> Optional[BaseException]:
        return self._error

    def next(self) -> bool:
        if self._error is not None:
            return False
        while True:
            if self._pending:
                frame = self._pending.pop(0)
                try:
                    event = decode_chat_event(frame.event, frame.data)
                except Exception as exc:  # noqa: BLE001
                    self._error = exc
                    return False
                self._current = event
                if event.message is not None:
                    self._final = event.message
                return True
            if self._eof:
                return False
            if self._iter is None:
                self._eof = True
                return False
            try:
                chunk = next(self._iter)
            except StopIteration:
                self._eof = True
                self._decoder.close()
                self._pending.extend(self._decoder.pop_frames())
                continue
            except Exception as exc:  # noqa: BLE001
                self._error = exc
                return False
            self._decoder.feed(chunk or b"")
            self._pending.extend(self._decoder.pop_frames())

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._resp is not None:
            try:
                self._resp.close()
            except Exception:  # noqa: BLE001
                pass

    def final_message(self) -> V1Message:
        if self._error is not None:
            raise self._error
        if self._final is not None:
            return self._final
        if self._current is not None and self._current.message is not None:
            return self._current.message
        raise ValueError("hibot: final message is not available")

    def accumulate(self) -> V1Message:
        buf: List[str] = []
        final_msg: Optional[V1Message] = None
        while self.next():
            event = self._current
            if event is None:
                continue
            if event.type == V1_SESSION_CHAT_EVENT_FAILED:
                msg = event.error.message or event.error.code or "unknown error"
                raise APIError(status_code=0, message=f"hibot: chat failed: {msg}")
            if event.type == V1_SESSION_CHAT_EVENT_DELTA:
                if event.delta.text:
                    buf.append(event.delta.text)
            elif event.type == V1_SESSION_CHAT_EVENT_COMPLETED:
                if event.message is not None:
                    final_msg = event.message
        if self._error is not None:
            raise self._error
        if final_msg is None:
            final_msg = self._final
        if final_msg is None:
            if not buf:
                raise ValueError("hibot: final message is not available")
            return V1Message(role="assistant", content="".join(buf))
        if not final_msg.content and buf:
            final_msg.content = "".join(buf)
        return final_msg


__all__ = [
    "V1SessionChatStream",
    "decode_chat_event",
    "normalize_chat_event_name",
]
