#!/usr/bin/env python3
"""
Eva SDK Usage Example

Demonstrates how to use Eva SDK to create and execute evaluation tasks
"""

import json
import logging
import time
from typing import List

# Import Eva SDK
from libs.eva import client, types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def my_inference_function(
    case_data_list: List[types.CaseData],
) -> List[types.InferenceResult]:
    results = []
    message_list = []
    for case in case_data_list:
        message_list.append({"role": "user", "content": case["input"].TextData})
        content = f"message list={json.dumps(message_list, ensure_ascii=False)}"
        message_list.append({"role": "assistant", "content": content})
        # Create inference result
        result = types.InferenceResult(
            Content=content,
            CostTokens=100,
            TTFT=101,
        )
        results.append(result)

    return results


def main():
    """Main function: Run complete evaluation example"""

    print("=== Eva SDK Example ===\n")

    # Initialize client
    provider = client.init(
        endpoint="http://33.234.30.131:30040",
        ak="HIAKY3VtRWdDZGtRbnRCZ05zbjJ1bWR1bmo5Zmptb2JlYmc",
        sk="GH9G/EAA30mEd0JJyCkg9Fj/EroJRev/Yw0S30BXZgFrflAi3wLkb1l/1Q==",
        workspace_id="cv60rjfsul75mk1a4hqg",
        app_id="d18li42u8je36l3mcsvg",
    )

    # Prepare evaluation parameters
    dataset_id = "d0jb420ge4sqeo4mvo30"  # Replace with your actual dataset ID
    # Get or create actual ruleset ID
    ruleset_id = "d0jb7roge4sqeo4mvo60"

    target_config = types.ModelAgentConfig(
        Temperature=0.7,
        TopP=0.9,
        MaxTokens=2048,
        RoundsReserved=10,
        RagNum=5,
        MaxIterations=5,
        RagEnabled=False,
        ReasoningMode=False,
        ReasoningSwitch=False,
    )

    try:
        # Run evaluation
        print("Starting evaluation...")
        report = provider.run_evaluation(
            dataset_id=dataset_id,
            task_name=f"simple_eva_{time.strftime('%Y%m%d%H%M%S')}",
            inference_function=my_inference_function,
            ruleset_id=ruleset_id,
            target_config=target_config,
            max_conversations=5,
        )

        # Print results
        print("\n✓ Evaluation completed!")
        print(f"   Task ID: {report.TaskID}")
        print(f"   Task Name: {report.TaskName}")
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

    except Exception as e:
        print(f"✗ Evaluation execution failed: {e}")
        logger.error(f"Evaluation execution failed: {e}", exc_info=True)

    print("\n=== Evaluation Completed ===")


if __name__ == "__main__":
    main()
