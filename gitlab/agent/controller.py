"""Simple GitLab issue-to-agent controller."""
import json
import os
import subprocess
import sys
import uuid
from typing import Optional, List, Tuple

from .models import IssueContext, TaskPacket
from .issue_parser import DEFAULT_ALLOWED_PATHS, parse_issue, parse_description_sections, slugify
from .gitlab_client import GitLabClient
from .deterministic_checker import DeterministicChecker
from .worker_runner import WorkerRunner
from .events import log_event


class AgentController:
    def __init__(
        self,
        repo_dir: str = ".",
        state_dir: str = ".agent-state",
        gitlab_client: Optional[GitLabClient] = None,
        qa_judge: object = None,
        run_id: Optional[str] = None,
        turn_id: Optional[str] = None,
        kiefer_username: Optional[str] = None,
    ):
        self.repo_dir = os.path.abspath(repo_dir)
        self.state_dir = os.path.abspath(state_dir)
        self.gitlab = gitlab_client or GitLabClient()
        self.run_id = run_id or os.getenv("AGENT_RUN_ID") or f"run-{uuid.uuid4().hex[:8]}"
        self.turn_id = turn_id or f"turn-{uuid.uuid4().hex[:8]}"
        self.kiefer_username = kiefer_username or os.getenv("KIEFER_USERNAME") or "kieferwaight"
        self.checker = DeterministicChecker(self.repo_dir)

    def _run_git(self, args: List[str]) -> Tuple[int, str, str]:
        p = subprocess.run(
            ["git", "-C", self.repo_dir] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return p.returncode, p.stdout, p.stderr

    def _write_context(self, issue_ctx: IssueContext, status: str, mr_iid: Optional[int] = None) -> None:
        _, branch, _ = self._run_git(["branch", "--show-current"])
        _, commit, _ = self._run_git(["rev-parse", "HEAD"])
        context = {
            "run_id": self.run_id,
            "turn_id": self.turn_id,
            "repository": self.repo_dir,
            "branch": branch.strip() or issue_ctx.branch_name,
            "commit": commit.strip(),
            "status": status,
            "issue_iid": issue_ctx.iid,
            "issue_title": issue_ctx.title,
            "mr_iid": mr_iid,
        }
        os.makedirs(self.state_dir, exist_ok=True)
        with open(os.path.join(self.state_dir, "context.json"), "w", encoding="utf-8") as f:
            json.dump(context, f, indent=2)

    def _issue_context(self, issue_json: dict) -> IssueContext:
        try:
            issue_ctx = parse_issue(issue_json)
            if not issue_ctx.parse_error and not issue_ctx.is_title_only:
                return issue_ctx
        except Exception:
            issue_ctx = None

        iid = int(issue_json.get("iid") or issue_json.get("id"))
        title = (issue_json.get("title") or f"Issue {iid}").strip()
        description = issue_json.get("description") or ""
        labels = issue_json.get("labels") or []
        sections = parse_description_sections(description)
        inferred_type = "fix" if title.lower().startswith("fix") or " fix " in title.lower() else (
            "refresh" if title.lower().startswith("refresh") or " refresh " in title.lower() else "content"
        )
        type_kind = getattr(issue_ctx, "type_kind", None) or next(
            (
                kind
                for label, kind in (
                    ("agent:content", "content"),
                    ("agent:fix", "fix"),
                    ("agent:refresh", "refresh"),
                )
                if label in labels
            ),
            inferred_type,
        )
        slug = slugify(title)
        return IssueContext(
            iid=iid,
            title=title,
            description=description,
            web_url=issue_json.get("web_url") or issue_json.get("webUrl") or "",
            labels=labels,
            state=issue_json.get("state") or "opened",
            type_kind=type_kind,
            slug=slug,
            branch_name=f"{type_kind}/{iid}-{slug}",
            goal=sections.get("goal") or description.strip() or title,
            acceptance_criteria=sections.get("acceptance_criteria") or [],
            permitted_scope=sections.get("permitted_scope") or DEFAULT_ALLOWED_PATHS.get(type_kind, ["src/", "public/"]),
            relevant_links=sections.get("relevant_links") or [],
        )

    def _build_task_packet(self, issue_ctx: IssueContext) -> TaskPacket:
        return TaskPacket(
            issue_snapshot=issue_ctx.to_snapshot(),
            acceptance_criteria=issue_ctx.acceptance_criteria,
            repository_instructions=(
                "Use the configured CLI agent to implement the GitLab issue in this repository. "
                "Mutate the working tree as needed, run relevant checks when practical, and stop without committing, "
                "pushing, opening merge requests, or commenting on GitLab."
            ),
            allowed_paths=issue_ctx.permitted_scope,
            required_checks=[],
            branch_name=issue_ctx.branch_name,
        )

    def run_issue(self, issue_iid: int, turn_count: int = 1) -> bool:
        try:
            issue_json = self.gitlab.get_issue(issue_iid)
        except Exception as e:
            print(f"Error fetching issue #{issue_iid}: {e}", file=sys.stderr)
            return False

        issue_ctx = self._issue_context(issue_json)

        self.gitlab.update_issue_labels(
            issue_iid,
            add_labels=["agent:running"],
            remove_labels=["agent:blocked"],
        )
        log_event(
            "controller_started",
            self.run_id,
            self.turn_id,
            self.state_dir,
            issue_iid=issue_iid,
            branch=issue_ctx.branch_name,
            details={"type_kind": issue_ctx.type_kind},
        )
        self._write_context(issue_ctx, "running")

        target_branch = os.getenv("CI_DEFAULT_BRANCH", "main")
        existing_mr = self.gitlab.get_open_mr_for_branch(issue_ctx.branch_name)

        if existing_mr:
            self._run_git(["fetch", "origin", issue_ctx.branch_name])
            self._run_git(["checkout", issue_ctx.branch_name])
        else:
            self._run_git(["fetch", "origin", target_branch])
            self._run_git(["checkout", "-B", issue_ctx.branch_name, f"origin/{target_branch}"])

        task_packet = self._build_task_packet(issue_ctx)

        log_event(
            "prompt_prepared",
            self.run_id,
            self.turn_id,
            self.state_dir,
            issue_iid=issue_iid,
            branch=issue_ctx.branch_name,
            details={"agent_cli": os.getenv("AGENT_CLI", "codex")},
        )

        log_event(
            "worker_started",
            self.run_id,
            self.turn_id,
            self.state_dir,
            issue_iid=issue_iid,
            branch=issue_ctx.branch_name,
        )

        runner = WorkerRunner(self.repo_dir, self.state_dir)
        worker_code, worker_out, worker_err = runner.run_worker(task_packet)

        log_event(
            "worker_finished",
            self.run_id,
            self.turn_id,
            self.state_dir,
            issue_iid=issue_iid,
            branch=issue_ctx.branch_name,
            details={"exit_code": worker_code},
        )

        if worker_code != 0:
            message = f"Agent CLI failed for issue #{issue_iid}:\n```\n{(worker_err or worker_out)[:2000]}\n```"
            self.gitlab.post_issue_comment(issue_iid, message)
            self.gitlab.update_issue_labels(issue_iid, add_labels=["agent:blocked"], remove_labels=["agent:running"])
            self._write_context(issue_ctx, "worker_failed")
            log_event(
                "agent_failed",
                self.run_id,
                self.turn_id,
                self.state_dir,
                issue_iid=issue_iid,
                branch=issue_ctx.branch_name,
                details={"reason": "worker_failed"},
            )
            return False

        changed_paths = self.checker.get_changed_paths()
        if not changed_paths:
            message = "Agent CLI finished without repository changes; no commit or merge request was created."
            self.gitlab.post_issue_comment(issue_iid, message)
            self.gitlab.update_issue_labels(issue_iid, add_labels=["agent:blocked"], remove_labels=["agent:running"])
            self._write_context(issue_ctx, "no_changes")
            log_event(
                "agent_failed",
                self.run_id,
                self.turn_id,
                self.state_dir,
                issue_iid=issue_iid,
                branch=issue_ctx.branch_name,
                details={"reason": "no_changes"},
            )
            return False

        log_event(
            "changes_detected",
            self.run_id,
            self.turn_id,
            self.state_dir,
            issue_iid=issue_iid,
            branch=issue_ctx.branch_name,
            details={"changed_paths": changed_paths},
        )

        commit_msg = f"{issue_ctx.type_kind}: {issue_ctx.title} (refs #{issue_iid})"
        self._run_git(["add", "-A"])
        commit_code, _, commit_err = self._run_git(["commit", "-m", commit_msg])
        if commit_code != 0:
            self.gitlab.post_issue_comment(issue_iid, f"Failed to commit agent changes:\n```\n{commit_err[:2000]}\n```")
            self.gitlab.update_issue_labels(issue_iid, add_labels=["agent:blocked"], remove_labels=["agent:running"])
            self._write_context(issue_ctx, "commit_failed")
            return False

        token = os.getenv("GITLAB_PAT") or os.getenv("GITLAB_AGENT_TOKEN") or ""
        server_host = os.getenv("CI_SERVER_HOST", "gitlab.kieferwaight.com")
        project_path = os.getenv("CI_PROJECT_PATH", "kieferwaight/kieferwaight.com")

        _, current_origin, _ = self._run_git(["remote", "get-url", "origin"])
        current_origin = current_origin.strip()

        if current_origin.startswith("http://") or current_origin.startswith("https://"):
            if token:
                push_url = f"https://oauth2:{token}@{server_host}/{project_path}.git"
            else:
                push_url = f"https://{server_host}/{project_path}.git"
            self._run_git(["remote", "set-url", "origin", push_url])

        push_code, _, push_err = self._run_git(["push", "-f", "origin", f"HEAD:refs/heads/{issue_ctx.branch_name}"])

        if push_code != 0 and current_origin:
            if "does not appear to be a git repository" not in push_err and "Could not resolve host" not in push_err:
                self.gitlab.post_issue_comment(issue_iid, f"Failed to push branch to remote:\n```\n{push_err[:2000]}\n```")
                self.gitlab.update_issue_labels(issue_iid, add_labels=["agent:blocked"], remove_labels=["agent:running"])
                self._write_context(issue_ctx, "push_failed")
                return False

        log_event(
            "commit_pushed",
            self.run_id,
            self.turn_id,
            self.state_dir,
            issue_iid=issue_iid,
            branch=issue_ctx.branch_name,
        )

        mr_title = f"Draft: {issue_ctx.title}"
        mr_desc = f"Closes #{issue_iid}\n\nAutomated MR generated by GitLab Agent turn (Run ID: {self.run_id})."

        if existing_mr:
            mr_info = self.gitlab.update_mr(existing_mr["iid"], title=mr_title, description=mr_desc)
            mr_iid = existing_mr["iid"]
        else:
            mr_info = self.gitlab.create_draft_mr(
                source_branch=issue_ctx.branch_name,
                target_branch=target_branch,
                title=mr_title,
                description=mr_desc,
            )
            mr_iid = mr_info.get("iid") or mr_info.get("id")

        log_event(
            "mr_upserted",
            self.run_id,
            self.turn_id,
            self.state_dir,
            issue_iid=issue_iid,
            branch=issue_ctx.branch_name,
            details={"mr_iid": mr_iid, "mr_url": mr_info.get("web_url")},
        )

        # Post deterministic summary comment
        _, diff_stat, _ = self._run_git(["diff", f"origin/{target_branch}...HEAD", "--stat"])
        summary_comment = (
            f"### Agent Execution Summary\n\n"
            f"- **Issue**: #{issue_iid} ([{issue_ctx.title}]({issue_ctx.web_url}))\n"
            f"- **Branch**: `{issue_ctx.branch_name}`\n"
            f"- **Model / Run ID**: `{os.getenv('AGENT_MODEL', 'gemini-2.5-flash')}` / `{self.run_id}`\n"
            f"- **Changed Files ({len(changed_paths)})**:\n"
            + "\n".join(f"  - `{p}`" for p in changed_paths)
            + f"\n\n**Diff Stat**:\n```\n{diff_stat.strip()}\n```\n\n"
        )
        if mr_iid:
            self.gitlab.post_mr_comment(mr_iid, summary_comment)

        self.gitlab.update_issue_labels(
            issue_iid,
            add_labels=["agent:ready-for-review"],
            remove_labels=["agent:running", "agent:blocked"],
        )
        self._write_context(issue_ctx, "ready_for_review", mr_iid=mr_iid)

        log_event(
            "decision_applied",
            self.run_id,
            self.turn_id,
            self.state_dir,
            issue_iid=issue_iid,
            branch=issue_ctx.branch_name,
            details={"status": "ready_for_review", "mr_iid": mr_iid},
        )
        return True
