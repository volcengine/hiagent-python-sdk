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
import os
import time

from dotenv import load_dotenv
from hiagent_observe import client
from opentelemetry import trace

load_dotenv()


if __name__ == "__main__":
    try:
        client.init(
            trace_endpoint=os.getenv("HIAGENT_TRACE_ENDPOINT"),
            top_endpoint=os.getenv("HIAGENT_TOP_ENDPOINT"),
            ak=os.getenv("VOLC_ACCESSKEY"),
            sk=os.getenv("VOLC_SECRETKEY"),
            workspace_id=os.getenv("WORKSPACE_ID"),
            app_id=os.getenv("CUSTOM_APP_ID"),
        )
    except Exception as e:
        raise RuntimeError(e)

    tracer = trace.get_tracer("example-tracer")

    for i in range(100000):
        with tracer.start_as_current_span("main-operation") as root_span:
            with tracer.start_as_current_span("do-work") as span:
                span.set_attributes(
                    {
                        "http.method": "GET",
                        "http.route": "/api/work",
                        "http.status_code": 200,
                    }
                )
        print("push trace")
        time.sleep(2)
