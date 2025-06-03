import time
import os

import requests
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.propagate import set_global_textmap
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from libs.api.observe import ObserveService
from . import VERSION


class AuthSession(requests.Session):
    def __init__(self, endpoint: str, ak: str, sk: str, workspace_id: str):
        super().__init__()
        self.endpoint = endpoint
        self.ak = ak
        self.sk = sk
        self.workspace_id = workspace_id
        self.token = None
        self.expires_at = 0
        self.observe_svc = ObserveService(
            endpoint=os.getenv('HIAGENT_ENDPOINT'), region='cn-north-1')

    def get_token(self):
        token_resp = self.observe_svc.CreateApiToken(
            {"WorkspaceID": self.workspace_id})
        self.token = token_resp.Token

        # 预留一些空间提前过期
        self.expires_at = time.time() + token_resp.ExpitesIn - 100

    def is_token_expired(self):
        return time.time() >= self.expires_at

    def refresh_token_if_needed(self):
        if not self.token or self.is_token_expired():
            self.get_token()

    def request(self, method, url, headers=None, **kwargs):
        self.refresh_token_if_needed()

        headers = headers or {}
        headers['Authorization'] = f'Bearer {self.token}'

        response = super().request(method, url, headers=headers, **kwargs)

        # 如果 token 失效，尝试重新获取并重试一次
        if response.status_code == 401:
            self.get_token()
            headers['Authorization'] = f'Bearer {self.token}'
            response = super().request(method, url, headers=headers, **kwargs)

        return response


class Client:
    def __init__(self, trace_endpoint: str, top_endpoint: str, ak: str, sk: str, workspace_id: str, **kwargs):
        self.auth_session = AuthSession(top_endpoint, ak, sk, workspace_id)
        self.trace_endpoint = trace_endpoint

        exporter = OTLPSpanExporter(
            endpoint=f'${trace_endpoint}/v1/traces', session=self.auth_session)

        resource = Resource.create({
            ResourceAttributes.SERVICE_NAME: 'HIAGENT_OBSERVE_SDK',
            ResourceAttributes.SERVICE_VERSION: VERSION,
        })

        provider = TracerProvider(
            resource=resource,
        )
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)

        set_global_textmap(
            CompositePropagator([
                TraceContextTextMapPropagator(),
            ])
        )
