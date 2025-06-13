import logging
import time

import requests
from hiagent_api.observe import ObserveService, observe_types
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from hiagent_observe import VERSION

logger = logging.getLogger(__name__)


class AuthSession(requests.Session):
    def __init__(self, endpoint: str, ak: str, sk: str, workspace_id: str, app_id: str):
        super().__init__()
        self.workspace_id = workspace_id
        self.app_id = app_id
        self.token = None
        self.expires_at = 0
        self.observe_svc = ObserveService(endpoint=endpoint, region="cn-north-1")
        self.observe_svc.set_ak(ak)
        self.observe_svc.set_sk(sk)

    def get_token(self) -> str:
        token_resp = self.observe_svc.CreateApiToken(
            observe_types.CreateApiTokenRequest(
                WorkspaceID=self.workspace_id, CustomAppID=self.app_id
            )
        )
        self.token = token_resp.Token

        # 预留一些空间提前过期
        self.expires_at = time.time() + token_resp.ExpiresIn - 100

        return self.token

    def is_token_expired(self):
        return time.time() >= self.expires_at

    def refresh_token_if_needed(self):
        if not self.token or self.is_token_expired():
            logger.debug("token expired or not set, refreshing...")
            self.get_token()

    def request(self, method, url, headers=None, **kwargs):
        self.refresh_token_if_needed()

        headers = headers or {}
        headers["Authorization"] = f"Bearer {self.token}"
        logger.debug(f"requesting {url} to export trace data")

        response = super().request(method, url, headers=headers, **kwargs)

        # 如果 token 失效，尝试重新获取并重试一次
        if response.status_code == 401:
            self.get_token()
            headers["Authorization"] = f"Bearer {self.token}"
            response = super().request(method, url, headers=headers, **kwargs)

        return response


def init(
    trace_endpoint: str,
    top_endpoint: str,
    ak: str,
    sk: str,
    workspace_id: str,
    app_id: str,
):
    auth_session = AuthSession(top_endpoint, ak, sk, workspace_id, app_id)

    try:
        token = auth_session.get_token()
        logger.debug(f"got initial token: {token}")
    except Exception as e:
        raise RuntimeError(f"failed to get initial token: {e}")

    exporter = OTLPSpanExporter(
        endpoint=f"{trace_endpoint}/v1/traces", session=auth_session
    )

    resource = Resource.create(
        {
            ResourceAttributes.SERVICE_NAME: "HIAGENT_OBSERVE_SDK",
            ResourceAttributes.SERVICE_VERSION: VERSION,
        }
    )
    provider = TracerProvider(
        resource=resource,
    )
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    set_global_textmap(
        CompositePropagator(
            [
                TraceContextTextMapPropagator(),
            ]
        )
    )

    return provider
