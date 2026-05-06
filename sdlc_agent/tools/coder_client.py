import json
import logging
import os
import uuid

import google.auth
import google.auth.transport.requests
import requests

log = logging.getLogger(__name__)

CODER_SERVICE_URL = os.environ.get(
    "CODER_SERVICE_URL", "http://localhost:8001"
)


def _get_id_token(audience: str) -> str:
    """Get an ID token for authenticating to Cloud Run."""
    try:
        from google.oauth2 import id_token
        import google.auth.transport.requests
        request = google.auth.transport.requests.Request()
        token = id_token.fetch_id_token(request, audience)
        return token
    except Exception as e:
        log.warning("Failed to get ID token: %s", e)
        return ""


def delegate_to_coder(
    issue_key: str,
    summary: str,
    plan: str,
    repo: str = "openshift-online/gcp-hcp-infra",
) -> dict:
    """Send a coding task to the remote coder agent via A2A protocol.

    The coder agent will clone the repo, implement the plan, and open
    a GitHub Pull Request. Returns the PR URL when complete.

    Args:
        issue_key: The Jira issue key (e.g., "GCP-653").
        summary: The issue summary/title.
        plan: The full approved development plan text.
        repo: Target GitHub repo in 'owner/name' format.

    Returns:
        dict: A dictionary with 'status' and 'pr_url' on success,
              or 'error_message' on failure.
    """
    message = (
        f"Implement the following approved plan and open a Pull Request.\n\n"
        f"**Issue:** {issue_key}\n"
        f"**Summary:** {summary}\n"
        f"**Target Repo:** {repo}\n\n"
        f"**Approved Plan:**\n{plan}"
    )

    task_id = str(uuid.uuid4())

    a2a_request = {
        "jsonrpc": "2.0",
        "method": "message/send",
        "id": task_id,
        "params": {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": message}],
                "messageId": str(uuid.uuid4()),
            },
        },
    }

    headers = {"Content-Type": "application/json"}

    token = _get_id_token(CODER_SERVICE_URL)
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        resp = requests.post(
            CODER_SERVICE_URL,
            headers=headers,
            json=a2a_request,
            timeout=540,
        )
        resp.raise_for_status()
        result = resp.json()

        response_text = ""
        if "result" in result:
            r = result["result"]
            if isinstance(r, dict):
                artifacts = r.get("artifacts", [])
                for artifact in artifacts:
                    for part in artifact.get("parts", []):
                        if part.get("kind") == "text":
                            response_text += part.get("text", "")
                status_msg = r.get("status", {}).get("message", {})
                if isinstance(status_msg, dict):
                    for part in status_msg.get("parts", []):
                        if part.get("kind") == "text":
                            response_text += part.get("text", "")

        if not response_text:
            response_text = json.dumps(result)

        pr_url = ""
        for line in response_text.split("\n"):
            if "github.com" in line and "/pull/" in line:
                for word in line.split():
                    if "github.com" in word and "/pull/" in word:
                        pr_url = word.strip("()`[]<>")
                        break

        if pr_url:
            return {"status": "success", "pr_url": pr_url, "response": response_text}
        else:
            return {"status": "success", "response": response_text, "pr_url": "not found in response"}

    except requests.Timeout:
        return {"status": "error", "error_message": "Coder agent timed out after 540s."}
    except requests.RequestException as e:
        return {"status": "error", "error_message": f"A2A call failed: {e}"}


def delegate_review_fix_to_coder(
    repo: str,
    branch_name: str,
    review_comments: str,
) -> dict:
    """Send review comments to the coder agent for fixing.

    The coder will clone the repo, checkout the existing PR branch,
    implement fixes for the review comments, and push to the same branch.

    Args:
        repo: GitHub repo in 'owner/name' format.
        branch_name: The existing PR branch to check out.
        review_comments: Formatted string of review comments to address,
            including file paths, line numbers, and comment text.

    Returns:
        dict: A dictionary with 'status' and 'response' from the coder.
    """
    message = (
        f"Address the following review comments on an existing PR.\n\n"
        f"**Mode:** Review fix (do NOT create a new branch or PR)\n"
        f"**Target Repo:** {repo}\n"
        f"**Branch:** {branch_name} (checkout this existing branch)\n\n"
        f"**Review Comments to Address:**\n{review_comments}\n\n"
        f"Clone the repo, checkout the branch, fix each comment, "
        f"commit as 'address review feedback', and push."
    )

    task_id = str(uuid.uuid4())
    a2a_request = {
        "jsonrpc": "2.0",
        "method": "message/send",
        "id": task_id,
        "params": {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": message}],
                "messageId": str(uuid.uuid4()),
            },
        },
    }

    headers = {"Content-Type": "application/json"}
    token = _get_id_token(CODER_SERVICE_URL)
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        resp = requests.post(
            CODER_SERVICE_URL,
            headers=headers,
            json=a2a_request,
            timeout=540,
        )
        resp.raise_for_status()
        result = resp.json()

        response_text = ""
        if "result" in result:
            r = result["result"]
            if isinstance(r, dict):
                for key in ("artifacts", ):
                    for item in r.get(key, []):
                        for part in item.get("parts", []):
                            if part.get("kind") == "text":
                                response_text += part.get("text", "")
                status_msg = r.get("status", {}).get("message", {})
                if isinstance(status_msg, dict):
                    for part in status_msg.get("parts", []):
                        if part.get("kind") == "text":
                            response_text += part.get("text", "")

        if not response_text:
            response_text = json.dumps(result)

        return {"status": "success", "response": response_text}

    except requests.Timeout:
        return {"status": "error", "error_message": "Coder agent timed out."}
    except requests.RequestException as e:
        return {"status": "error", "error_message": f"A2A call failed: {e}"}
