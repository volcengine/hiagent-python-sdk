from typing import Optional

from hiagent_api.workflow_types import GetWorkflowResponse, Node


def get_start_node_of_workflow(workflow: GetWorkflowResponse) -> Optional[Node]:
    for node in workflow.nodes:
        if node.type == "Start":
            return node

    return None
