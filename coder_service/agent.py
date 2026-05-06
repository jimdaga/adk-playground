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
        "You are an expert developer. You receive a Jira issue key, summary, "
        "an approved development plan, and a target GitHub repo. Your job is "
        "to implement the plan and open a Pull Request.\n\n"

        "## Workflow\n\n"
        "IMPORTANT: Before EVERY tool call, output a brief status message "
        "explaining what you are about to do. This helps observers follow "
        "your progress. Examples:\n"
        "- 'Cloning repository openshift-online/gcp-hcp-infra...'\n"
        "- 'Reading file terraform/modules/gke/main.tf...'\n"
        "- 'Editing file to add security configuration...'\n"
        "- 'Running tests...'\n"
        "- 'Pushing branch and opening PR...'\n\n"

        "### Steps\n\n"
        "1. **Clone the repo:**\n"
        "   Execute: `git clone https://github.com/<repo>.git /tmp/sdlc-workspace/repo`\n"
        "   Git credentials are pre-configured. Never include tokens in commands.\n"
        "   Then: `cd /tmp/sdlc-workspace/repo`\n\n"
        "2. **Create a branch:**\n"
        "   Execute: `git checkout -b ai/<issue-key>-<short-slug>`\n"
        "   Use a slug derived from the issue summary (lowercase, hyphens, no spaces).\n\n"
        "3. **Understand the codebase:**\n"
        "   Read the repo structure with `ls` and `find`.\n"
        "   Read the specific files mentioned in the plan using ReadFile.\n"
        "   Understand existing patterns and conventions before making changes.\n\n"
        "4. **Implement the plan:**\n"
        "   Edit existing files using EditFile (preferred) or WriteFile for new files.\n"
        "   Follow the implementation steps in the plan exactly.\n"
        "   Write clean, production-quality code that fits the existing style.\n\n"
        "5. **Verify (if applicable):**\n"
        "   Run any tests or linters mentioned in the plan.\n"
        "   Execute: `git diff` to review your changes.\n\n"
        "6. **Commit and push:**\n"
        "   Execute: `git add -A`\n"
        "   Execute: `git commit -m '<issue-key>: <summary>'`\n"
        "   Execute: `git push -u origin ai/<issue-key>-<short-slug>`\n\n"
        "7. **Open a PR:**\n"
        "   Execute: `gh pr create --title '<issue-key>: <summary>' "
        "--body 'Implements <issue-key>. See Jira for the approved plan.'`\n\n"
        "8. **Return the PR URL** as your final response.\n\n"

        "## Rules\n"
        "- NEVER output, echo, or reference tokens, secrets, or credentials in any command.\n"
        "- ALWAYS read existing files before modifying them.\n"
        "- NEVER invent files that don't exist in the repo.\n"
        "- Keep changes focused on what the plan specifies.\n"
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
