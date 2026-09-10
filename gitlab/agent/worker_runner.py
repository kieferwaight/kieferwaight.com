"""Worker agent execution in a sealed workspace without GitLab write tokens."""
import json
import os
import subprocess
from typing import Tuple, Dict, Any, Optional
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
        packet_path = os.path.join(self.state_dir, "task-packet.json")

        # Write read-only task packet file
        with open(packet_path, "w", encoding="utf-8") as f:
            json.dump(task_packet.to_dict(), f, indent=2)
        os.chmod(packet_path, 0o444)

        # Worker prompt focuses ONLY on repository implementation and validation
        prompt = (
            f"Read the task packet at {packet_path}. "
            "Implement the requested issue requirements in the repository. "
            "Work ONLY in the permitted paths. "
            "Run relevant build/validation checks. "
            "Do NOT create branches, commit, push, open merge requests, post comments, or modify remote state."
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

        # If entrypoint script exists, run entrypoint.sh task ...
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
