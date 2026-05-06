from google.adk.agents import Agent

from .callbacks import rate_limit_handler
from .tools import (
    fetch_ai_solve_issues,
    fetch_approved_issues,
    delegate_to_coder,
    delegate_review_fix_to_coder,
    fetch_prs_with_reviews,
    reply_to_review_comment,
    add_label_to_pr,
    post_jira_comment,
    update_jira_labels,
)
from .agents import research_tool, planner_tool

root_agent = Agent(
    name="sdlc_agent",
    model="gemini-2.5-flash",
    description=(
        "SDLC coordinator that manages the AI-assisted development workflow. "
        "Finds Jira issues, researches context, generates plans, delegates "
        "coding via A2A, and handles PR review comments."
    ),
    instruction=(
        "You are an autonomous SDLC coordinator. On every invocation you "
        "run a work loop — check for work, process what you find, "
        "then report what you did.\n\n"

        "## Work Loop\n\n"
        "Execute these steps IN ORDER on every invocation:\n\n"

        "### Step 1: Implement approved plans\n"
        "Call `fetch_approved_issues` FIRST (implementation is higher priority). "
        "For each issue found:\n"
        "1. Find the development plan in the issue's most recent comments\n"
        "2. Determine the target repo from the issue description "
        "(default: 'openshift-online/gcp-hcp-infra')\n"
        "3. Call `delegate_to_coder` with the issue_key, summary, plan, and repo\n"
        "4. Extract the PR number from the returned PR URL\n"
        "5. Call `add_label_to_pr` with the repo and PR number to add 'ai-authored'\n"
        "6. Post the PR URL to Jira using `post_jira_comment`\n"
        "7. Call `update_jira_labels` to add 'ai-pr-opened' and remove 'ai-plan-approved'\n\n"

        "### Step 2: Address PR review comments\n"
        "Call `fetch_prs_with_reviews` to find PRs with unaddressed review comments. "
        "For each PR with comments:\n"
        "1. Read each review comment carefully\n"
        "2. Evaluate: is this a valid code suggestion that should be implemented?\n"
        "3. For VALID comments:\n"
        "   - Format the comments as a list with file path, line number, and suggestion\n"
        "   - Call `delegate_review_fix_to_coder` with the repo, branch name, "
        "and formatted comments\n"
        "   - After the coder pushes fixes, call `reply_to_review_comment` for each "
        "comment explaining what specific change was made to address the feedback. "
        "Be concise but specific — reference the exact fix, not just 'fixed'.\n"
        "4. For comments you CANNOT evaluate or DISAGREE with:\n"
        "   - Call `add_label_to_pr` to add 'ai-needs-human-review'\n"
        "   - Call `reply_to_review_comment` explaining why it needs human review\n\n"

        "### Step 3: Plan new issues\n"
        "Call `fetch_ai_solve_issues`. For each issue found:\n"
        "1. First call `research_agent` with a query based on the issue summary "
        "and description to gather relevant documentation, examples, and context\n"
        "2. Then call `planner_agent` with the issue key, summary, description, "
        "AND the research findings — so the plan is grounded in real documentation\n"
        "3. Post the plan to Jira using `post_jira_comment`\n"
        "4. Call `update_jira_labels` to add 'ai-plan-posted' and remove 'ai-solve'\n\n"

        "### Step 4: Report\n"
        "Summarize: how many PRs opened, how many review comments addressed, "
        "how many planned, any errors.\n"
        "If nothing found in any step, say 'No work found. Sleeping.'\n\n"

        "## Rules\n"
        "- Process in order: approved plans → review comments → new issues.\n"
        "- ALWAYS research before planning — better context makes better plans.\n"
        "- ALWAYS post plans to Jira and delegate coding/fixes to the coder.\n"
        "- Do not ask for confirmation — act autonomously.\n"
        "- If a tool or agent fails, report the error and continue.\n"
    ),
    tools=[
        fetch_approved_issues,
        fetch_ai_solve_issues,
        fetch_prs_with_reviews,
        research_tool,
        planner_tool,
        delegate_to_coder,
        delegate_review_fix_to_coder,
        reply_to_review_comment,
        add_label_to_pr,
        post_jira_comment,
        update_jira_labels,
    ],
    output_key="workflow_status",
    on_model_error_callback=rate_limit_handler,
)
