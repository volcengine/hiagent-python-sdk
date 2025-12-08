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
# !/usr/bin/env python3
"""
Eva SDK Usage Example

Demonstrates how to use Eva SDK to create and execute evaluation tasks
"""

import argparse
import logging
import os

from dotenv import load_dotenv

# Import Eva SDK
from hiagent_eva import client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def main():
    """Main function: Run complete evaluation example"""

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Eva SDK Pause Example")
    parser.add_argument("-n", "--name", required=True, help="Task name")
    args = parser.parse_args()

    print("=== Eva SDK Example ===\n")

    # Initialize client
    provider = client.init(
        endpoint=os.getenv("HIAGENT_TOP_ENDPOINT"),
        ak=os.getenv("VOLC_ACCESSKEY"),
        sk=os.getenv("VOLC_SECRETKEY"),
        workspace_id=os.getenv("WORKSPACE_ID"),
        app_id=os.getenv("CUSTOM_APP_ID"),
    )

    # Use command line arguments
    task_name = args.name

    try:
        # Run evaluation
        print("Starting pause...")
        provider.pause_task(task_name)

        print("\n=== Pause Completed ===")

    except Exception as e:
        logger.error(f"Evaluation execution failed: {e}", exc_info=True)
        print(f"✗ Evaluation execution failed: {e}")


if __name__ == "__main__":
    main()
