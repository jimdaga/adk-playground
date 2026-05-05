from typing import Any, Dict, Optional

from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext

BLOCKED_RESOURCE_TYPES = {"secrets", "secret"}


def redaction_guardrail(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """Prevents access to sensitive resource types and sanitizes tool arguments.

    Blocks any attempt to list, describe, or retrieve Kubernetes Secrets.
    This mirrors the production agent's security rule: never access or
    output credential material.
    """
    resource_type = args.get("resource_type", "")
    if resource_type.lower() in BLOCKED_RESOURCE_TYPES:
        return {
            "status": "error",
            "error_message": (
                "Security policy: Access to Secret resources is not permitted. "
                "Investigate the issue using other resource types."
            ),
        }

    return None
