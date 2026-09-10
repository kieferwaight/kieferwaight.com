"""Three-Stage Controller Orchestrator for GitLab Agentic Turn."""
import json
import os
import subprocess
import sys
import uuid
from typing import Optional, Dict, Any, List, Tuple

from .models import IssueContext, TaskPacket, QAResult
from .issue_parser import parse_issue, build_task_packet
from .triage import triage_issue
from .gitlab_client import GitLabClient
from .deterministic_checker import DeterministicChecker
from .worker_runner import WorkerRunner
from .qa_judge import QAJudge
from .events import log_event
from .repo_context import RepoContext
from .build_test_agent import BuildTestAgent


class AgentController:
    def __init__(
        self,
        repo_dir: str = ".",
        state_dir: str = ".agent-state",
        gitlab_client: Optional[GitLabClient] = None,
        qa_judge: Optional[QAJudge] = None,
        run_id: Optional[str] = None,
        turn_id: Optional[str] = None,
        kiefer_username: Optional[str] = None,
    ):
        self.repo_dir = os.path.abspath(repo_dir)
        self.state_dir = os.path.abspath(state_dir)
        self.gitlab = gitlab_client or GitLabClient()
        self.qa_judge = qa_judge or QAJudge()
        self.run_id = run_id or os.getenv("AGENT_RUN_ID") or f"run-{uuid.uuid4().hex[:8]}"
        self.turn_id = turn_id or f"turn-{uuid.uuid4().hex[:8]}"
        self.kiefer_username = kiefer_username or os.getenv("KIEFER_USERNAME") or "kieferwaight"
        self.checker = DeterministicChecker(self.repo_dir)
        self.repo_ctx_mgr = RepoContext(self.repo_dir)
        self.repo_context = self.repo_ctx_mgr.load_or_build_context()
        self.build_test_agent = BuildTestAgent(self.repo_dir, self.state_dir, checker=self.checker)

    def _run_git(self, args: List[str]) -> Tuple[int, str, str]:
        p = subprocess.run(
            ["git", "-C", self.repo_dir] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return p.returncode, p.stdout, p.stderr

    def run_issue(self, issue_iid: int, turn_count: int = 1) -> bool:
        # 1. Fetch issue context
        try:
            issue_json = self.gitlab.get_issue(issue_iid)
        except Exception as e:
            print(f"Error fetching issue #{issue_iid}: {e}", file=sys.stderr)
            return False

        issue_ctx = triage_issue(issue_json, gitlab_client=self.gitlab)

        # 2. Check label / description validation
        if issue_ctx.parse_error or issue_ctx.is_title_only:
            reason = issue_ctx.parse_error or "Title-only issue without structured requirements."
            comment_body = (
                f"🛑 **Agent Execution Blocked**\n\n"
                f"Issue #{issue_iid} cannot be processed by the agent:\n"
                f"> {reason}\n\n"
                f"Please update the issue with required labels (`ready-for-agent` + exactly one type label e.g. `agent:content`) "
                f"and a structured description (Goal, Acceptance Criteria, Scope)."
            )
            self.gitlab.post_issue_comment(issue_iid, comment_body)
            self.gitlab.update_issue_labels(
                issue_iid,
                add_labels=["agent:blocked"],
                remove_labels=["agent:running", "agent:qa", "agent:rework", "ready-for-agent"],
            )
            log_event(
                "agent_blocked",
                self.run_id,
                self.turn_id,
                self.state_dir,
                issue_iid=issue_iid,
                details={"reason": reason, "title_only": issue_ctx.is_title_only},
            )
            return False

        # 3. Transition state to agent:running
        self.gitlab.update_issue_labels(
            issue_iid,
            add_labels=["agent:running"],
            remove_labels=["agent:rework", "agent:qa", "agent:blocked"],
        )
        log_event(
            "controller_started",
            self.run_id,
            self.turn_id,
            self.state_dir,
            issue_iid=issue_iid,
            branch=issue_ctx.branch_name,
            details={"type_kind": issue_ctx.type_kind, "turn_count": turn_count},
        )

        target_branch = os.getenv("CI_DEFAULT_BRANCH", "main")

        # 4. Check existing branch and MR
        existing_mr = self.gitlab.get_open_mr_for_branch(issue_ctx.branch_name)
        prior_qa_findings = None

        if turn_count > 1 or existing_mr:
            if turn_count > 2:
                # Escalation: Second rejection or max turns exceeded
                return self._escalate_and_block(
                    issue_iid,
                    existing_mr.get("iid") if existing_mr else None,
                    issue_ctx,
                    "Exceeded maximum permitted agent turns (1 initial + 1 correction turn).",
                )
            # Fetch prior QA findings from MR notes if present
            if existing_mr:
                prior_qa_findings = {"message": "Prior turn requested rework."}

            # Checkout existing branch
            self._run_git(["fetch", "origin", issue_ctx.branch_name])
            self._run_git(["checkout", issue_ctx.branch_name])
        else:
            # Create branch from target branch before worker starts
            self._run_git(["fetch", "origin", target_branch])
            self._run_git(["checkout", "-B", issue_ctx.branch_name, f"origin/{target_branch}"])

        # 5. Build task packet
        task_packet = build_task_packet(issue_ctx, prior_qa_findings)
        packet_path = os.path.join(self.state_dir, "task-packet.json")
        os.makedirs(self.state_dir, exist_ok=True)
        with open(packet_path, "w", encoding="utf-8") as f:
            json.dump(task_packet.to_dict(), f, indent=2)

        log_event(
            "task_packet_created",
            self.run_id,
            self.turn_id,
            self.state_dir,
            issue_iid=issue_iid,
            branch=issue_ctx.branch_name,
            details={"allowed_paths": task_packet.allowed_paths},
        )

        # 6. Execute Stage 2: Worker Agent
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
            return self._handle_worker_failure(
                issue_iid,
                existing_mr.get("iid") if existing_mr else None,
                issue_ctx,
                worker_err or worker_out,
                turn_count,
            )

        # 7. Post-Worker Fast Editor Checks
        fast_ok, fast_msg, changed_paths = self.build_test_agent.run_fast_editor_checks(
            issue_ctx.type_kind or "content",
            allowed_paths=task_packet.allowed_paths,
        )
        if not fast_ok:
            return self._handle_validation_failure(
                issue_iid, existing_mr.get("iid") if existing_mr else None, issue_ctx, fast_msg, turn_count
            )

        build_results = [{"check": "git diff --check & scope policy", "status": "passed"}]

        # 8. Post-Worker Checks (Heavy builds & puppeteer run in subsequent CI pipeline stages)
        if task_packet.required_checks:
            build_ok, build_msg, build_results = self.build_test_agent.run_heavy_build_pipeline(
                task_packet.required_checks
            )
            if not build_ok:
                # Trigger On-Error Repair Agent
                repair_ok, repair_msg = self.build_test_agent.attempt_on_error_repair(build_msg, changed_paths)
                if not repair_ok:
                    return self._handle_validation_failure(
                        issue_iid, existing_mr.get("iid") if existing_mr else None, issue_ctx, repair_msg, turn_count
                    )

        log_event(
            "deterministic_checks_passed",
            self.run_id,
            self.turn_id,
            self.state_dir,
            issue_iid=issue_iid,
            branch=issue_ctx.branch_name,
            details={"changed_paths": changed_paths},
        )

        # 8. Controller Commit, Push & Draft MR Upsert
        commit_msg = f"{issue_ctx.type_kind}: {issue_ctx.title} (refs #{issue_iid})"
        self._run_git(["add", "-A"])
        self._run_git(["commit", "-m", commit_msg])

        # Push branch
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
                return self._handle_validation_failure(
                    issue_iid,
                    existing_mr.get("iid") if existing_mr else None,
                    issue_ctx,
                    f"Failed to push branch to remote: {push_err}",
                    turn_count,
                )

        log_event(
            "commit_pushed",
            self.run_id,
            self.turn_id,
            self.state_dir,
            issue_iid=issue_iid,
            branch=issue_ctx.branch_name,
        )

        # Create or update Draft MR
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
            f"### 🤖 Controller Execution Summary (Turn {turn_count})\n\n"
            f"- **Issue**: #{issue_iid} ([{issue_ctx.title}]({issue_ctx.web_url}))\n"
            f"- **Branch**: `{issue_ctx.branch_name}`\n"
            f"- **Model / Run ID**: `{os.getenv('AGENT_MODEL', 'gemini-2.5-flash')}` / `{self.run_id}`\n"
            f"- **Changed Files ({len(changed_paths)})**:\n"
            + "\n".join(f"  - `{p}`" for p in changed_paths)
            + f"\n\n**Diff Stat**:\n```\n{diff_stat.strip()}\n```\n\n"
            f"**Deterministic Checks Passed**:\n"
            + "\n".join(f"- ✅ `{r['check']}`" for r in build_results)
        )
        if mr_iid:
            self.gitlab.post_mr_comment(mr_iid, summary_comment)

        # 9. Execute Stage 3: Hybrid QA Judge
        self.gitlab.update_issue_labels(
            issue_iid,
            add_labels=["agent:qa"],
            remove_labels=["agent:running"],
        )
        log_event(
            "qa_judge_started",
            self.run_id,
            self.turn_id,
            self.state_dir,
            issue_iid=issue_iid,
            branch=issue_ctx.branch_name,
        )

        _, full_diff, _ = self._run_git(["diff", f"origin/{target_branch}...HEAD"])

        qa_result = self.qa_judge.evaluate(
            issue_title=issue_ctx.title,
            goal=issue_ctx.goal,
            acceptance_criteria=issue_ctx.acceptance_criteria,
            changed_files=changed_paths,
            git_diff=full_diff,
            deterministic_test_results=build_results,
        )

        log_event(
            "qa_judge_finished",
            self.run_id,
            self.turn_id,
            self.state_dir,
            issue_iid=issue_iid,
            branch=issue_ctx.branch_name,
            details={"decision": qa_result.decision, "rationale": qa_result.rationale},
        )

        # 10. Apply QA Decision
        if qa_result.decision == "approve":
            # Approve
            if mr_iid:
                self.gitlab.assign_user_to_mr(mr_iid, self.kiefer_username)
                qa_comment = (
                    f"### ✅ Hybrid QA Judge: APPROVED\n\n"
                    f"**Rationale**: {qa_result.rationale}\n\n"
                    f"**Acceptance Criteria Evidence**:\n"
                    + "\n".join(f"- **{ac}**: {ev}" for ac, ev in qa_result.evidence.items())
                    + (f"\n\n**Identified Risks**: {', '.join(qa_result.risks)}" if qa_result.risks else "")
                    + f"\n\nAssigned reviewer @{self.kiefer_username} for final human review."
                )
                self.gitlab.post_mr_comment(mr_iid, qa_comment)

            self.gitlab.update_issue_labels(
                issue_iid,
                add_labels=["agent:ready-for-review"],
                remove_labels=["agent:running", "agent:qa", "agent:rework"],
            )

            log_event(
                "decision_applied",
                self.run_id,
                self.turn_id,
                self.state_dir,
                issue_iid=issue_iid,
                branch=issue_ctx.branch_name,
                details={"status": "approved", "assigned_to": self.kiefer_username},
            )
            return True

        elif turn_count == 1:
            # Rework requested on turn 1 -> relaunch correction turn
            rework_comment = (
                f"### ⚠️ Hybrid QA Judge: REWORK REQUIRED (Turn 1)\n\n"
                f"**Rationale**: {qa_result.rationale}\n\n"
                f"**Evidence / Findings**:\n"
                + "\n".join(f"- **{ac}**: {ev}" for ac, ev in qa_result.evidence.items())
                + (f"\n\n**Risks**: {', '.join(qa_result.risks)}" if qa_result.risks else "")
                + f"\n\nRelaunching one constrained correction turn..."
            )
            if mr_iid:
                self.gitlab.post_mr_comment(mr_iid, rework_comment)
            self.gitlab.post_issue_comment(issue_iid, rework_comment)

            self.gitlab.update_issue_labels(
                issue_iid,
                add_labels=["agent:rework"],
                remove_labels=["agent:running", "agent:qa"],
            )

            # Relaunch correction turn (Turn 2)
            return self.run_issue(issue_iid, turn_count=2)

        else:
            # Second rejection (turn_count >= 2) -> escalate and block
            return self._escalate_and_block(
                issue_iid,
                mr_iid,
                issue_ctx,
                f"QA Judge rejected changes on correction turn (Turn {turn_count}): {qa_result.rationale}",
                qa_result=qa_result,
            )

    def _handle_worker_failure(
        self, issue_iid: int, mr_iid: Optional[int], issue_ctx: IssueContext, error_msg: str, turn_count: int
    ) -> bool:
        if turn_count == 1:
            self.gitlab.post_issue_comment(
                issue_iid, f"⚠️ **Worker Execution Failed (Turn 1)**:\n```\n{error_msg[:1000]}\n```\nRelaunching correction turn..."
            )
            self.gitlab.update_issue_labels(issue_iid, add_labels=["agent:rework"], remove_labels=["agent:running"])
            return self.run_issue(issue_iid, turn_count=2)
        else:
            return self._escalate_and_block(
                issue_iid, mr_iid, issue_ctx, f"Worker execution failed on correction turn:\n{error_msg}"
            )

    def _handle_validation_failure(
        self, issue_iid: int, mr_iid: Optional[int], issue_ctx: IssueContext, failure_msg: str, turn_count: int
    ) -> bool:
        if turn_count == 1:
            comment = f"⚠️ **Deterministic Validation Failed (Turn 1)**:\n> {failure_msg}\n\nRelaunching correction turn..."
            self.gitlab.post_issue_comment(issue_iid, comment)
            if mr_iid:
                self.gitlab.post_mr_comment(mr_iid, comment)
            self.gitlab.update_issue_labels(issue_iid, add_labels=["agent:rework"], remove_labels=["agent:running"])
            return self.run_issue(issue_iid, turn_count=2)
        else:
            return self._escalate_and_block(
                issue_iid, mr_iid, issue_ctx, f"Deterministic validation failed on correction turn:\n{failure_msg}"
            )

    def _escalate_and_block(
        self,
        issue_iid: int,
        mr_iid: Optional[int],
        issue_ctx: IssueContext,
        reason: str,
        qa_result: Optional[QAResult] = None,
    ) -> bool:
        block_msg = (
            f"🚫 **Automation Blocked & Escalated**\n\n"
            f"**Reason**: {reason}\n\n"
            + (
                f"**QA Rationale**: {qa_result.rationale}\n"
                f"**QA Evidence**: {json.dumps(qa_result.evidence, indent=2)}\n"
                if qa_result
                else ""
            )
            + f"\nAssigned @{self.kiefer_username} for manual intervention."
        )

        self.gitlab.post_issue_comment(issue_iid, block_msg)
        if mr_iid:
            self.gitlab.post_mr_comment(mr_iid, block_msg)
            self.gitlab.assign_user_to_mr(mr_iid, self.kiefer_username)

        self.gitlab.update_issue_labels(
            issue_iid,
            add_labels=["agent:blocked"],
            remove_labels=["agent:running", "agent:qa", "agent:rework", "ready-for-agent"],
        )

        log_event(
            "decision_applied",
            self.run_id,
            self.turn_id,
            self.state_dir,
            issue_iid=issue_iid,
            branch=issue_ctx.branch_name,
            details={"status": "blocked", "reason": reason, "assigned_to": self.kiefer_username},
        )
        return False
