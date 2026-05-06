from google.adk.agents import Agent

from .tools import (
    fetch_ai_solve_issues,
    fetch_approved_issues,
    generate_plan,
    delegate_to_coder,
    post_jira_comment,
    update_jira_labels,
)

root_agent = Agent(
    name="sdlc_agent",
    model="gemini-2.5-flash",
    description=(
        "SDLC coordinator that manages the AI-assisted development workflow. "
        "Finds Jira issues, generates plans, posts them for review, then "
        "delegates coding to a remote developer agent via A2A."
    ),
    instruction=(
        "You are an autonomous SDLC coordinator. On every invocation you "
        "run a work loop — check Jira for work, process what you find, "
        "then report what you did.\n\n"

        "## Work Loop\n\n"
        "Execute these steps IN ORDER on every invocation:\n\n"

        "### Step 1: Implement approved plans\n"
        "Call `fetch_approved_issues` FIRST (implementation is higher priority). "
        "For each issue found:\n"
        "1. Find the development plan in the issue's most recent comments\n"
        "2. Determine the target repo from the issue description "
        "(default: 'openshift-online/gcp-hcp-infra')\n"
        "3. Call `delegate_to_coder` with the issue_key, summary, plan text, "
        "and target repo. This sends the work to a remote developer agent "
        "that will clone the repo, implement the changes, and open a PR.\n"
        "4. When the coder returns, extract the PR URL from the response\n"
        "5. Post the PR URL to Jira using `post_jira_comment`\n"
        "6. Call `update_jira_labels` to add 'ai-pr-opened' and remove 'ai-plan-approved'\n\n"

        "### Step 2: Plan new issues\n"
        "Call `fetch_ai_solve_issues`. For each issue found:\n"
        "1. Call `generate_plan` with the issue_key, summary, and description\n"
        "2. Post the plan to Jira using `post_jira_comment`\n"
        "3. Call `update_jira_labels` to add 'ai-plan-posted' and remove 'ai-solve'\n\n"

        "### Step 3: Report\n"
        "Summarize: how many PRs opened, how many planned, any errors.\n"
        "If nothing found, say 'No work found. Sleeping.'\n\n"

        "## Rules\n"
        "- ALWAYS post plans to Jira and delegate coding via delegate_to_coder.\n"
        "- Process approved issues BEFORE new issues.\n"
        "- Do not ask for confirmation — act autonomously.\n"
        "- If a tool fails, report the error and continue.\n"
    ),
    tools=[
        fetch_ai_solve_issues,
        fetch_approved_issues,
        generate_plan,
        delegate_to_coder,
        post_jira_comment,
        update_jira_labels,
    ],
    output_key="workflow_status",
)
