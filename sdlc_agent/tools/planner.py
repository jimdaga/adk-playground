import os

from google.genai import types
from google.genai.chats import Chat


def generate_plan(issue_key: str, summary: str, description: str) -> dict:
    """Generate a development plan for a Jira issue.

    Takes the issue details and produces a detailed, actionable
    development plan using Gemini Pro.

    Args:
        issue_key: The Jira issue key (e.g., "GCP-653").
        summary: The issue summary/title.
        description: The full issue description.

    Returns:
        dict: A dictionary with 'status' and 'plan' (markdown string).
    """
    from google import genai

    client = genai.Client(
        vertexai=True,
        project=os.environ.get("GOOGLE_CLOUD_PROJECT", "dev-mgt-us-c1-jimdagad880"),
        location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1"),
    )

    prompt = (
        f"You are a senior software architect. Create a detailed development "
        f"plan for the following Jira issue.\n\n"
        f"## Issue: {issue_key}\n"
        f"**Summary:** {summary}\n\n"
        f"**Description:**\n{description}\n\n"
        f"## Your Plan MUST include:\n"
        f"1. **Problem Summary** — What needs to be done and why\n"
        f"2. **Proposed Approach** — Files to create or modify, key design decisions\n"
        f"3. **Implementation Steps** — Numbered, specific steps\n"
        f"4. **Testing Strategy** — What tests to write, edge cases to cover\n"
        f"5. **Risks & Open Questions** — Anything that needs clarification\n\n"
        f"Format as clean markdown. Be specific and actionable."
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt,
        )
        plan = response.text
        return {"status": "success", "plan": plan, "issue_key": issue_key}
    except Exception as e:
        return {"status": "error", "error_message": f"Plan generation failed: {e}"}
