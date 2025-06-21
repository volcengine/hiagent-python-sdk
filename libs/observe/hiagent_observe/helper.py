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
import logging
from contextlib import contextmanager
from functools import wraps
from typing import Dict

from hiagent_observe.semconv import SemanticConvention
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import Span, SpanKind, Status, StatusCode


def tracable(wrapped):
    """
    Generates a telemetry wrapper for messages to collect metrics.
    """
    if not callable(wrapped):
        raise TypeError(
            f"@trace can only be applied to callable objects, got {type(wrapped).__name__}"
        )

    try:
        __trace = trace.get_tracer_provider()
        tracer = __trace.get_tracer(__name__)
    except Exception as tracer_exception:
        logging.error(
            "Failed to initialize tracer: %s", tracer_exception, exc_info=True
        )
        raise

    @wraps(wrapped)
    def wrapper(*args, **kwargs):
        with tracer.start_as_current_span(
            name=wrapped.__name__,
            kind=SpanKind.CLIENT,
        ) as span:
            response = None
            try:
                response = wrapped(*args, **kwargs)
                span.set_attribute(
                    SemanticConvention.GEN_AI_CONTENT_COMPLETION, response or ""
                )
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.record_exception(e)
                span.set_status(status=Status(StatusCode.ERROR), description=str(e))
                logging.error("Error in %s: %s", wrapped.__name__, e, exc_info=True)
                raise

            try:
                span.set_attribute("function.args", str(args))
                span.set_attribute("function.kwargs", str(kwargs))
                # span.set_attribute(
                #     SERVICE_NAME,
                #     OpenlitConfig.application_name,
                # )
                # span.set_attribute(DEPLOYMENT_ENVIRONMENT, OpenlitConfig.environment)
            except Exception as meta_exception:
                logging.error(
                    "Failed to set metadata for %s: %s",
                    wrapped.__name__,
                    meta_exception,
                    exc_info=True,
                )

            return response

    return wrapper


class TracedSpan:
    def __init__(self, span: Span):
        self._span: Span = span

    def __enter__(self):
        return self

    def set_attribute(self, key: str, value: str):
        self._span.set_attribute(key, value)
        self._span.set_status(Status(StatusCode.OK))

    def set_status(self, status: StatusCode, description: str):
        self._span.set_status(status=status, description=description)

    def set_attributes(self, attributes: Dict):
        for key, value in attributes.items():
            self.set_attribute(key, value)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._span.end()


@contextmanager
def start_trace(name: str, provider: TracerProvider):
    if provider is None:
        provider = trace.get_tracer_provider()
    with provider.get_tracer(__name__).start_as_current_span(
        name,
        kind=SpanKind.CLIENT,
    ) as span:
        yield TracedSpan(span)
