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
import json
import logging
import os
from time import sleep
from typing import List

from dotenv import load_dotenv

# Import Eva SDK
from hiagent_api import eva_types
from hiagent_eva import client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


def my_inference_function(
    case_data_list: List[eva_types.CaseData],
) -> List[eva_types.InferenceResult]:
    results = []
    message_list = []
    for case in case_data_list:
        input = case["input"].CellContent[0].Text
        message_list.append({"role": "user", "content": input})
        content = f"message list={json.dumps(message_list, ensure_ascii=False)}"
        message_list.append({"role": "assistant", "content": content})
        # Create inference result
        result = eva_types.InferenceResult(
            Content=content,
            CostTokens=100,
            TTFT=101,
        )
        results.append(result)
    sleep(0.5)

    return results


def main():
    """Main function: Run complete evaluation example"""

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Eva SDK Evaluation Example")
    parser.add_argument(
        "-d", "--dataset-id", required=True, help="Dataset ID for evaluation"
    )
    parser.add_argument(
        "-r", "--ruleset-id", required=True, help="Ruleset ID for evaluation"
    )
    parser.add_argument("-n", "--name", required=True, help="Task name")
    parser.add_argument(
        "-v", "--dataset-version-id", required=True, help="Dataset version ID"
    )
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
    dataset_id = args.dataset_id
    dataset_version_id = args.dataset_version_id
    ruleset_id = args.ruleset_id
    task_name = args.name

    try:
        # Run evaluation
        print("Starting inference and evaluation...")
        print(f"Dataset ID: {dataset_id}")
        print(f"Dataset Version ID: {dataset_version_id}")
        print(f"Ruleset ID: {ruleset_id}")
        report = provider.run_inference_and_evaluation(
            dataset_id=dataset_id,
            dataset_version_id=dataset_version_id,
            task_name=task_name,
            inference_function=my_inference_function,
            ruleset_id=ruleset_id,
            max_conversations=5,
        )

        # Print results
        print("\n✓ Evaluation completed!")
        print(f"   Task Name: {task_name}")
        print(f"   Status: {report.Status}")
        print(f"   Number of Rules: {len(report.Rules)}")
        print(f"   Number of Targets: {len(report.Targets)}")
        print(f"   Created At: {report.CreatedAt}")
        print(f"   Updated At: {report.UpdatedAt}")

        # Display target information
        if report.Targets:
            print("\nInference Information:")
            for target in report.Targets:
                print(f"   • Target ID: {target.TargetID}")
                print(f"     Target Name: {target.TargetDetail.TargetName}")
                print(f"     Average Token Cost: {target.AvgCostTokens}")
                print(f"     Average TTFT: {target.AvgTTFT}ms")
                print(f"     Average Duration: {target.AvgDuration}ms")
                print(f"     Total Token Cost: {target.CostTokens}")

        # Display rule information
        if report.Rules:
            print("\nRule Information:")
            for rule in report.Rules:
                print(f"   • Rule ID: {rule.RuleID}")
                for rule_target in rule.Targets:
                    print(f"     Target: {rule_target.TargetDetail.TargetName}")
                    print(f"     Average Score: {rule_target.AvgScore}")
                    print(f"     Percentage: {rule_target.Percent}%")

        print("\n=== Evaluation Completed ===")

    except Exception as e:
        logger.error(f"Evaluation execution failed: {e}", exc_info=True)
        print(f"✗ Evaluation execution failed: {e}")


if __name__ == "__main__":
    main()
