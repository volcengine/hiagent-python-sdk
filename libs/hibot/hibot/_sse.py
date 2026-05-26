"""SSE decoder (mirrors go/hibot/internal/stream/sse.go)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, List


@dataclass
class Frame:
    event: str = ""
    data: str = ""


def iter_frames(lines: Iterable[str]) -> Iterator[Frame]:
    """Decode SSE frames from a sequence of *already-line-split* strings.

    The input lines should NOT contain the trailing ``\n``/``\r\n``.
    A blank line terminates a frame (empty frames are skipped).
    """
    event = ""
    data: List[str] = []
    for raw in lines:
        line = raw.rstrip("\r\n")
        if line == "":
            if event == "" and not data:
                continue
            yield Frame(event=event, data="\n".join(data))
            event = ""
            data = []
            continue
        if line.startswith(":"):
            continue
        if line.startswith("event:"):
            event = line[len("event:"):].strip()
            continue
        if line.startswith("data:"):
            value = line[len("data:"):]
            # SSE: a single leading space is part of the spec separator.
            if value.startswith(" "):
                value = value[1:]
            data.append(value.strip())
            continue
        # Unknown field — skip per spec.
    if event != "" or data:
        yield Frame(event=event, data="\n".join(data))


class ByteStreamDecoder:
    """Incremental decoder fed with bytes chunks from an HTTP stream."""

    def __init__(self) -> None:
        self._buf = bytearray()
        self._event = ""
        self._data: List[str] = []
        self._frames: List[Frame] = []

    def feed(self, chunk: bytes) -> None:
        if not chunk:
            return
        self._buf.extend(chunk)
        while True:
            idx = self._buf.find(b"\n")
            if idx < 0:
                break
            raw = bytes(self._buf[:idx])
            del self._buf[: idx + 1]
            line = raw.decode("utf-8", "replace").rstrip("\r")
            self._handle_line(line)

    def close(self) -> None:
        # Flush any buffered partial line.
        if self._buf:
            line = bytes(self._buf).decode("utf-8", "replace").rstrip("\r\n")
            self._buf.clear()
            self._handle_line(line)
        # Flush any remaining frame without a terminating blank line.
        if self._event != "" or self._data:
            self._frames.append(Frame(event=self._event, data="\n".join(self._data)))
            self._event = ""
            self._data = []

    def _handle_line(self, line: str) -> None:
        if line == "":
            if self._event == "" and not self._data:
                return
            self._frames.append(Frame(event=self._event, data="\n".join(self._data)))
            self._event = ""
            self._data = []
            return
        if line.startswith(":"):
            return
        if line.startswith("event:"):
            self._event = line[len("event:"):].strip()
            return
        if line.startswith("data:"):
            value = line[len("data:"):]
            if value.startswith(" "):
                value = value[1:]
            self._data.append(value.strip())
            return

    def pop_frames(self) -> List[Frame]:
        out = self._frames
        self._frames = []
        return out


__all__ = ["Frame", "iter_frames", "ByteStreamDecoder"]
