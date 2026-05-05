import json
import os
import subprocess
import tempfile
from typing import Dict


def create_github_pr(
    repo: str,
    branch_name: str,
    title: str,
    body: str,
    files: Dict[str, str],
) -> dict:
    """Create a GitHub Pull Request with the provided files.

    Clones the repo, creates a branch, writes the files, commits,
    pushes, and opens a PR.

    Args:
        repo: GitHub repo in 'owner/name' format (e.g., 'openshift-online/gcp-hcp-infra').
        branch_name: Name for the new branch (e.g., 'ai/GCP-123-fix-etcd').
        title: PR title (should include the Jira issue key).
        body: PR description in markdown.
        files: Dictionary mapping file paths to their content.
               Example: {"src/main.py": "print('hello')", "tests/test_main.py": "..."}

    Returns:
        dict: A dictionary with 'status' and 'pr_url' on success,
              or 'error_message' on failure.
    """
    if not files:
        return {"status": "error", "error_message": "No files provided."}

    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            _run(["gh", "repo", "clone", repo, tmpdir, "--", "--depth=1"], cwd=None)
            _run(["git", "checkout", "-b", branch_name], cwd=tmpdir)

            for path, content in files.items():
                full_path = os.path.join(tmpdir, path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w") as f:
                    f.write(content)

            _run(["git", "add", "-A"], cwd=tmpdir)
            _run(
                ["git", "commit", "-m", title],
                cwd=tmpdir,
                env={**os.environ, "GIT_AUTHOR_NAME": "SDLC Agent", "GIT_AUTHOR_EMAIL": "sdlc-agent@noreply"},
            )
            _run(["git", "push", "-u", "origin", branch_name], cwd=tmpdir)

            result = _run(
                ["gh", "pr", "create", "--repo", repo, "--title", title, "--body", body, "--head", branch_name],
                cwd=tmpdir,
            )
            pr_url = result.stdout.strip()

            return {"status": "success", "pr_url": pr_url, "files_committed": list(files.keys())}

        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "error_message": f"GitHub operation failed: {e.stderr or e.stdout or str(e)}",
            }


def _run(cmd, cwd=None, env=None):
    return subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=True,
        timeout=120,
    )
