import logging
import os
from typing import List, Optional

import requests

from .jira import _get_secret

log = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
AGENT_MARKER = "[sdlc-agent]"


def _github_headers() -> dict:
    token = _get_secret("github-pat")
    if not token:
        return {}
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }


def fetch_prs_with_reviews() -> dict:
    """Find open PRs labeled 'ai-authored' that have unaddressed review comments.

    Checks all repositories listed in the WATCHED_REPOS environment variable
    (comma-separated, e.g., 'openshift-online/gcp-hcp-infra,org/other-repo').

    Returns:
        dict: A dictionary with 'status' and 'prs' list. Each PR includes
              the repo, number, title, branch, and unaddressed review comments.
    """
    watched = os.environ.get("WATCHED_REPOS", "")
    if not watched:
        return {"status": "success", "prs": [], "message": "No WATCHED_REPOS configured."}

    headers = _github_headers()
    if not headers:
        return {"status": "error", "error_message": "GitHub PAT not configured."}

    repos = [r.strip() for r in watched.split(",") if r.strip()]
    results = []

    for repo in repos:
        try:
            prs = _get_ai_authored_prs(repo, headers)
            for pr in prs:
                unaddressed = _get_unaddressed_comments(repo, pr["number"], headers)
                if unaddressed:
                    results.append({
                        "repo": repo,
                        "number": pr["number"],
                        "title": pr["title"],
                        "branch": pr["head"]["ref"],
                        "url": pr["html_url"],
                        "unaddressed_comments": unaddressed,
                    })
        except requests.RequestException as e:
            log.warning("Failed to check repo %s: %s", repo, e)

    return {"status": "success", "prs": results, "count": len(results)}


def reply_to_review_comment(
    repo: str, pr_number: int, comment_id: int, body: str
) -> dict:
    """Reply to a specific review comment on a pull request.

    Use this after implementing a fix or to explain why a suggestion
    needs human review.

    Args:
        repo: GitHub repo in 'owner/name' format.
        pr_number: The pull request number.
        comment_id: The ID of the review comment to reply to.
        body: The reply text.

    Returns:
        dict: A dictionary with 'status' indicating success or error.
    """
    headers = _github_headers()
    if not headers:
        return {"status": "error", "error_message": "GitHub PAT not configured."}

    try:
        resp = requests.post(
            f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}/comments/{comment_id}/replies",
            headers=headers,
            json={"body": f"{AGENT_MARKER} {body}"},
            timeout=30,
        )
        resp.raise_for_status()
        return {"status": "success", "message": f"Replied to comment {comment_id}."}
    except requests.RequestException as e:
        return {"status": "error", "error_message": f"Failed to reply: {e}"}


def add_label_to_pr(repo: str, pr_number: int, label: str) -> dict:
    """Add a label to a pull request.

    Args:
        repo: GitHub repo in 'owner/name' format.
        pr_number: The pull request number.
        label: The label to add (e.g., 'ai-needs-human-review').

    Returns:
        dict: A dictionary with 'status' indicating success or error.
    """
    headers = _github_headers()
    if not headers:
        return {"status": "error", "error_message": "GitHub PAT not configured."}

    try:
        resp = requests.post(
            f"{GITHUB_API}/repos/{repo}/issues/{pr_number}/labels",
            headers=headers,
            json={"labels": [label]},
            timeout=30,
        )
        resp.raise_for_status()
        return {"status": "success", "message": f"Added label '{label}' to PR #{pr_number}."}
    except requests.RequestException as e:
        return {"status": "error", "error_message": f"Failed to add label: {e}"}


def _get_ai_authored_prs(repo: str, headers: dict) -> list:
    """List open PRs and filter for 'ai-authored' label."""
    resp = requests.get(
        f"{GITHUB_API}/repos/{repo}/pulls",
        headers=headers,
        params={"state": "open", "per_page": 50},
        timeout=30,
    )
    resp.raise_for_status()

    return [
        pr for pr in resp.json()
        if any(l["name"] == "ai-authored" for l in pr.get("labels", []))
    ]


def _get_unaddressed_comments(repo: str, pr_number: int, headers: dict) -> list:
    """Get review comments that the agent hasn't replied to yet."""
    resp = requests.get(
        f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}/comments",
        headers=headers,
        params={"per_page": 100},
        timeout=30,
    )
    resp.raise_for_status()

    comments = resp.json()
    top_level = [c for c in comments if c.get("in_reply_to_id") is None]
    reply_parent_ids = {c["in_reply_to_id"] for c in comments if c.get("in_reply_to_id")}

    agent_replied_ids = set()
    for c in comments:
        if c.get("in_reply_to_id") and AGENT_MARKER in (c.get("body") or ""):
            agent_replied_ids.add(c["in_reply_to_id"])

    unaddressed = []
    for c in top_level:
        if c["id"] in agent_replied_ids:
            continue
        unaddressed.append({
            "id": c["id"],
            "author": c.get("user", {}).get("login", ""),
            "path": c.get("path", ""),
            "line": c.get("line") or c.get("original_line"),
            "body": c.get("body", ""),
            "created_at": c.get("created_at", ""),
        })

    return unaddressed
