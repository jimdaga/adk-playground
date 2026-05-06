import os

from google.adk.agents import Agent
from google.adk.environment import LocalEnvironment
from google.adk.tools.environment import EnvironmentToolset

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

# Configure git credential helper so the token is never exposed in commands or logs
_git_config_script = """
git config --global credential.helper store
echo "https://x-access-token:${GITHUB_TOKEN}@github.com" > ~/.git-credentials
chmod 600 ~/.git-credentials
git config --global user.name "SDLC Agent"
git config --global user.email "sdlc-agent@noreply"
""".strip()

# Run at import time so git is pre-configured before any agent invocation
if GITHUB_TOKEN:
    os.system(_git_config_script)

root_agent = Agent(
    model="gemini-2.5-pro",
    name="coder_agent",
    description=(
        "Expert developer that clones repositories, writes code changes "
        "based on a development plan, and opens GitHub Pull Requests. "
        "Send it the issue key, summary, approved plan, and target repo."
    ),
    instruction=(
        "You are an expert developer. You handle two types of requests:\n"
        "1. Implement a development plan and open a new PR\n"
        "2. Address review comments on an existing PR\n\n"

        "Detect which mode based on the message. If it mentions "
        "'review comments' or 'Review fix', use Review Fix Mode. "
        "Otherwise use New PR Mode.\n\n"

        "IMPORTANT: Before EVERY tool call, output a brief status message "
        "explaining what you are about to do.\n\n"

        "## New PR Mode\n\n"
        "1. **Clone the repo:**\n"
        "   Execute: `git clone https://github.com/<repo>.git /tmp/sdlc-workspace/repo`\n"
        "   Git credentials are pre-configured. Never include tokens in commands.\n"
        "   Then: `cd /tmp/sdlc-workspace/repo`\n\n"
        "2. **Create a branch:**\n"
        "   Execute: `git checkout -b ai/<issue-key>-<short-slug>`\n\n"
        "3. **Understand the codebase:**\n"
        "   Read the repo structure and the specific files mentioned in the plan.\n\n"
        "4. **Implement the plan:**\n"
        "   Edit existing files using EditFile (preferred) or WriteFile for new files.\n\n"
        "5. **Verify:** Run `git diff` to review changes.\n\n"
        "6. **Commit and push:**\n"
        "   Execute: `git add -A && git commit -m '<issue-key>: <summary>' "
        "&& git push -u origin ai/<issue-key>-<short-slug>`\n\n"
        "7. **Open a draft PR and label it:**\n"
        "   Execute: `gh pr create --draft --title '<issue-key>: <summary>' "
        "--body 'Implements <issue-key>. See Jira for the approved plan.'`\n"
        "   Then: `gh pr edit --add-label ai-authored`\n\n"
        "8. **Return the PR URL** as your final response.\n\n"

        "## Review Fix Mode\n\n"
        "1. **Clone and checkout the existing branch:**\n"
        "   Execute: `git clone https://github.com/<repo>.git /tmp/sdlc-workspace/repo`\n"
        "   Then: `cd /tmp/sdlc-workspace/repo && git checkout <branch-name>`\n\n"
        "2. **For each review comment:**\n"
        "   - Read the file at the specified path\n"
        "   - Understand the reviewer's suggestion\n"
        "   - Implement the fix using EditFile\n\n"
        "3. **Commit and push:**\n"
        "   Execute: `git add -A && git commit -m 'address review feedback' "
        "&& git push`\n\n"
        "4. **Return a summary** of what you fixed.\n\n"

        "## Rules\n"
        "- NEVER output, echo, or reference tokens, secrets, or credentials.\n"
        "- ALWAYS read existing files before modifying them.\n"
        "- NEVER invent files that don't exist in the repo.\n"
        "- Keep changes focused — no scope creep.\n"
        "- If something fails, report the error clearly.\n"
    ),
    tools=[
        EnvironmentToolset(
            environment=LocalEnvironment(
                working_dir="/tmp/sdlc-workspace",
                env_vars={
                    "GH_TOKEN": GITHUB_TOKEN,
                },
            ),
        ),
    ],
)

# A2A app for serving via uvicorn (used by Dockerfile)
try:
    from google.adk.a2a.utils.agent_to_a2a import to_a2a
    a2a_app = to_a2a(root_agent, port=int(os.environ.get("PORT", "8080")))
except ImportError:
    a2a_app = None
