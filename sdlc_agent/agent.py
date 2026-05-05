from google.adk.agents import Agent

from .tools import (
    fetch_ai_solve_issues,
    fetch_approved_issues,
    generate_plan,
    post_jira_comment,
    update_jira_labels,
)

root_agent = Agent(
    name="sdlc_agent",
    model="gemini-2.5-flash",
    description=(
        "SDLC coordinator that manages the AI-assisted development workflow. "
        "Finds Jira issues, generates plans, and posts them to Jira."
    ),
    instruction=(
        "You are an autonomous SDLC coordinator. On every invocation you "
        "run a work loop — check Jira for work, process what you find, "
        "then report what you did.\n\n"

        "## Work Loop\n\n"
        "Execute these steps IN ORDER on every invocation:\n\n"

        "### Step 1: Check for new issues to plan\n"
        "Call `fetch_ai_solve_issues`. For each issue found:\n"
        "1. Call `generate_plan` with the issue_key, summary, and description\n"
        "2. Take the plan from the result and post it to Jira using "
        "`post_jira_comment` with the issue_key and the plan text\n"
        "3. Call `update_jira_labels` to add 'ai-plan-posted' and remove 'ai-solve'\n"
        "Complete ALL three sub-steps for each issue.\n\n"

        "### Step 2: Check for approved plans\n"
        "Call `fetch_approved_issues`. Report any issues found.\n\n"

        "### Step 3: Report\n"
        "Summarize: how many planned, how many approved, any errors.\n"
        "If nothing found in either step, say 'No work found. Sleeping.'\n\n"

        "## Rules\n"
        "- ALWAYS post the plan to Jira. Never just show it in chat.\n"
        "- Do not ask for confirmation — act autonomously.\n"
        "- If a tool fails, report the error and continue.\n"
    ),
    tools=[
        fetch_ai_solve_issues,
        fetch_approved_issues,
        generate_plan,
        post_jira_comment,
        update_jira_labels,
    ],
    output_key="workflow_status",
)
