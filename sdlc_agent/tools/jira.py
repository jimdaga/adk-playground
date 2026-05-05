import base64
import logging
import os
from typing import List, Optional

import requests

JIRA_BASE_URL = "https://redhat.atlassian.net"
JIRA_PROJECT = "GCP"
_GCP_PROJECT = "dev-mgt-us-c1-jimdagad880"

log = logging.getLogger(__name__)

_secret_cache: dict = {}


def _get_secret(secret_id: str) -> str:
    """Read a secret from Secret Manager, falling back to env vars for local dev."""
    if secret_id in _secret_cache:
        return _secret_cache[secret_id]

    try:
        from google.cloud import secretmanager
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{_GCP_PROJECT}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        value = response.payload.data.decode("UTF-8")
        _secret_cache[secret_id] = value
        return value
    except Exception as e:
        log.warning("Secret Manager unavailable for %s: %s. Trying env var.", secret_id, e)

    env_key = secret_id.upper().replace("-", "_")
    env_val = os.environ.get(env_key, "")
    if env_val:
        _secret_cache[secret_id] = env_val
        return env_val

    return ""


def _jira_headers() -> dict:
    email = _get_secret("jira-user-email")
    token = _get_secret("jira-api-token")
    if not email or not token:
        return {}
    creds = base64.b64encode(f"{email}:{token}".encode()).decode()
    return {
        "Authorization": f"Basic {creds}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def fetch_ai_solve_issues() -> dict:
    """Fetch Jira issues labeled 'ai-solve' from the GCP project.

    Searches for issues with the 'ai-solve' label that are ready
    for AI-assisted development planning.

    Returns:
        dict: A dictionary with 'status' and 'issues' list containing
              key, summary, description, labels, and priority for each issue.
    """
    jql = f'project = {JIRA_PROJECT} AND labels = "ai-solve" ORDER BY priority DESC'
    url = f"{JIRA_BASE_URL}/rest/api/3/search/jql"
    params = {
        "jql": jql,
        "fields": "summary,description,labels,priority,status,issuetype",
        "maxResults": 20,
    }

    headers = _jira_headers()
    if not headers:
        return {"status": "error", "error_message": "JIRA_USER_EMAIL and JIRA_API_TOKEN environment variables are required."}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        issues = []
        for issue in data.get("issues", []):
            fields = issue.get("fields", {})
            desc = fields.get("description")
            if isinstance(desc, dict):
                desc = _adf_to_text(desc)
            issues.append({
                "key": issue["key"],
                "summary": fields.get("summary", ""),
                "description": desc or "",
                "labels": fields.get("labels", []),
                "priority": fields.get("priority", {}).get("name", ""),
                "status": fields.get("status", {}).get("name", ""),
                "type": fields.get("issuetype", {}).get("name", ""),
            })

        return {"status": "success", "issues": issues, "count": len(issues)}

    except requests.RequestException as e:
        return {"status": "error", "error_message": f"Jira API error: {e}"}


def fetch_approved_issues() -> dict:
    """Fetch Jira issues labeled 'ai-plan-approved' that are ready for coding.

    Returns:
        dict: A dictionary with 'status' and 'issues' list.
    """
    jql = f'project = {JIRA_PROJECT} AND labels = "ai-plan-approved" ORDER BY priority DESC'
    url = f"{JIRA_BASE_URL}/rest/api/3/search/jql"
    params = {
        "jql": jql,
        "fields": "summary,description,labels,priority,status,comment",
        "maxResults": 20,
    }

    headers = _jira_headers()
    if not headers:
        return {"status": "error", "error_message": "Jira credentials not configured."}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        issues = []
        for issue in data.get("issues", []):
            fields = issue.get("fields", {})
            desc = fields.get("description")
            if isinstance(desc, dict):
                desc = _adf_to_text(desc)

            comments = []
            for c in fields.get("comment", {}).get("comments", []):
                body = c.get("body")
                if isinstance(body, dict):
                    body = _adf_to_text(body)
                comments.append({
                    "author": c.get("author", {}).get("displayName", ""),
                    "body": body or "",
                    "created": c.get("created", ""),
                })

            issues.append({
                "key": issue["key"],
                "summary": fields.get("summary", ""),
                "description": desc or "",
                "labels": fields.get("labels", []),
                "comments": comments[-5:],
            })

        return {"status": "success", "issues": issues, "count": len(issues)}

    except requests.RequestException as e:
        return {"status": "error", "error_message": f"Jira API error: {e}"}


def post_jira_comment(issue_key: str, comment: str) -> dict:
    """Post a comment to a Jira issue.

    Use this to post development plans or status updates to an issue.

    Args:
        issue_key: The Jira issue key (e.g., "GCP-123").
        comment: The comment text in markdown format.

    Returns:
        dict: A dictionary with 'status' indicating success or error.
    """
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/comment"
    body = {
        "body": {
            "version": 1,
            "type": "doc",
            "content": [
                {
                    "type": "codeBlock",
                    "attrs": {"language": "markdown"},
                    "content": [{"type": "text", "text": comment}],
                }
            ],
        }
    }

    headers = _jira_headers()
    if not headers:
        return {"status": "error", "error_message": "Jira credentials not configured."}

    try:
        resp = requests.post(url, headers=headers, json=body, timeout=30)
        resp.raise_for_status()
        return {"status": "success", "message": f"Comment posted to {issue_key}."}
    except requests.RequestException as e:
        return {"status": "error", "error_message": f"Failed to post comment: {e}"}


def update_jira_labels(
    issue_key: str,
    add_labels: Optional[List[str]] = None,
    remove_labels: Optional[List[str]] = None,
) -> dict:
    """Add or remove labels on a Jira issue.

    Used to transition issues through the AI workflow stages:
    ai-solve → ai-plan-posted → ai-plan-approved → ai-pr-opened

    Args:
        issue_key: The Jira issue key (e.g., "GCP-123").
        add_labels: Labels to add to the issue.
        remove_labels: Labels to remove from the issue.

    Returns:
        dict: A dictionary with 'status' indicating success or error.
    """
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"

    update_body: dict = {"update": {"labels": []}}
    for label in (add_labels or []):
        update_body["update"]["labels"].append({"add": label})
    for label in (remove_labels or []):
        update_body["update"]["labels"].append({"remove": label})

    if not update_body["update"]["labels"]:
        return {"status": "error", "error_message": "No labels to add or remove."}

    headers = _jira_headers()
    if not headers:
        return {"status": "error", "error_message": "Jira credentials not configured."}

    try:
        resp = requests.put(url, headers=headers, json=update_body, timeout=30)
        resp.raise_for_status()
        return {
            "status": "success",
            "message": f"Labels updated on {issue_key}.",
            "added": add_labels or [],
            "removed": remove_labels or [],
        }
    except requests.RequestException as e:
        return {"status": "error", "error_message": f"Failed to update labels: {e}"}


def _adf_to_text(adf: dict) -> str:
    """Convert Atlassian Document Format to plain text."""
    parts = []
    for block in adf.get("content", []):
        for inline in block.get("content", []):
            if inline.get("type") == "text":
                parts.append(inline.get("text", ""))
        parts.append("\n")
    return "".join(parts).strip()
