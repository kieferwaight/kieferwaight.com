"""Worker agent execution without GitLab write tokens."""
import os
import subprocess
from typing import Tuple, Optional
from .models import TaskPacket


class WorkerRunner:
    def __init__(
        self,
        repo_dir: str,
        state_dir: str,
        agent_cli: Optional[str] = None,
        agent_model: Optional[str] = None,
        entrypoint_script: Optional[str] = None,
    ):
        self.repo_dir = repo_dir
        self.state_dir = state_dir
        self.agent_cli = agent_cli or os.getenv("AGENT_CLI", "codex")
        self.agent_model = agent_model or os.getenv("AGENT_MODEL", "gemini-2.5-flash")
        self.entrypoint_script = entrypoint_script or os.getenv("AGENT_ENTRYPOINT", "/usr/local/bin/agent-entrypoint")

    def run_worker(self, task_packet: TaskPacket) -> Tuple[int, str, str]:
        os.makedirs(self.state_dir, exist_ok=True)
        issue = task_packet.issue_snapshot
        acceptance = "\n".join(f"- {item}" for item in task_packet.acceptance_criteria) or "- Use the issue content as the requirement."
        links = "\n".join(f"- {item}" for item in issue.get("relevant_links", [])) or "- None"
        prompt = (
            "Implement this GitLab issue in the current repository.\n\n"
            f"Issue: #{issue.get('iid')} {issue.get('title')}\n"
            f"URL: {issue.get('web_url') or 'Unavailable'}\n"
            f"Branch: {task_packet.branch_name}\n\n"
            f"Goal:\n{issue.get('goal') or issue.get('description') or issue.get('title')}\n\n"
            f"Description:\n{issue.get('description') or issue.get('title')}\n\n"
            f"Acceptance Criteria:\n{acceptance}\n\n"
            f"Relevant Links:\n{links}\n\n"
            "Mutate the working tree to satisfy the issue. Run relevant build or validation checks when practical. "
            "Do not create branches, commit, push, open merge requests, post comments, or modify remote state."
        )

        # Prepare environment stripped of GitLab write tokens and credentials
        env = dict(os.environ)
        for key in ["GITLAB_AGENT_TOKEN", "CI_JOB_TOKEN", "OPENBAO_SECRET", "OPENBAO_TOKEN"]:
            env.pop(key, None)

        env["AGENT_REPO_DIR"] = self.repo_dir
        env["AGENT_STATE_DIR"] = self.state_dir
        env["AGENT_CLI"] = self.agent_cli
        env["AGENT_MODEL"] = self.agent_model
        env["AGENT_SANDBOX"] = os.getenv("AGENT_SANDBOX", "workspace-write")

        # Ensure git remote in repository is read-only (no tokens embedded)
        server_host = os.getenv("CI_SERVER_HOST", "gitlab.kieferwaight.com")
        project_path = os.getenv("CI_PROJECT_PATH", "kieferwaight/kieferwaight.com")
        read_only_remote = f"https://{server_host}/{project_path}.git"
        
        try:
            subprocess.run(
                ["git", "-C", self.repo_dir, "remote", "set-url", "origin", read_only_remote],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        except Exception:
            pass

        cmd = [self.entrypoint_script, "task", prompt] if os.path.exists(self.entrypoint_script) else ["bash", "entrypoint.sh", "task", prompt]

        p = subprocess.run(
            cmd,
            cwd=self.repo_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        return p.returncode, p.stdout, p.stderr
