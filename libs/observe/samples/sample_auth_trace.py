import os
import time

from dotenv import load_dotenv
from opentelemetry import trace

from libs import observe

load_dotenv()


def do_work(tracer):
    with tracer.start_as_current_span("do-work") as span:
        span.set_attributes(
            {
                "http.method": "GET",
                "http.route": "/api/work",
                "http.status_code": 200,
            }
        )


if __name__ == "__main__":
    try:
        client = observe.init(
            trace_endpoint=os.getenv("HIAGENT_TRACE_ENDPOINT"),
            top_endpoint=os.getenv("HIAGENT_TOP_ENDPOINT"),
            ak=os.getenv("VOLC_ACCESSKEY"),
            sk=os.getenv("VOLC_SECRETKEY"),
            workspace_id=os.getenv("WORKSPACE_ID"),
            app_id=os.getenv("CUSTOM_APP_ID"),
        )
        print(client.token)
    except Exception as e:
        raise RuntimeError(e)

    tracer = trace.get_tracer("example-tracer")

    for i in range(100000):
        with tracer.start_as_current_span("main-operation") as root_span:
            do_work(tracer)
        print("push trace")
        time.sleep(2)
