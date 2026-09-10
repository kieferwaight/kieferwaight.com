"""Build & Test Agent with On-Error Repair capabilities.

Decouples fast content editing from heavy framework builds and PDF/image assets.
Automatically triggers an On-Error Repair Agent when build checks fail.
"""
import os
import subprocess
from typing import List, Dict, Any, Tuple, Optional
from .deterministic_checker import DeterministicChecker
from .repo_context import RepoContext


class BuildTestAgent:
    def __init__(self, repo_dir: str, state_dir: str, checker: Optional[DeterministicChecker] = None):
        self.repo_dir = repo_dir
        self.state_dir = state_dir
        self.checker = checker or DeterministicChecker(repo_dir)
        self.repo_ctx_mgr = RepoContext(repo_dir)
        self.context = self.repo_ctx_mgr.load_or_build_context()

    def run_fast_editor_checks(
        self, type_kind: str, allowed_paths: Optional[List[str]] = None
    ) -> Tuple[bool, str, List[str]]:
        """Fast checks evaluated immediately after content editor finishes diff."""
        clean_ok, clean_msg = self.checker.check_diff_cleanliness()
        if not clean_ok:
            return False, clean_msg, []

        changed_paths = self.checker.get_changed_paths()
        noop_ok, noop_msg = self.checker.check_no_op(changed_paths)
        if not noop_ok:
            return False, noop_msg, changed_paths

        scope_allowed = allowed_paths or self.context.get("type_scopes", {}).get(type_kind, ["src/", "public/"])
        scope_ok, scope_msg, _ = self.checker.check_scope_policy(changed_paths, scope_allowed)
        if not scope_ok:
            return False, scope_msg, changed_paths

        return True, "Fast editor checks passed cleanly.", changed_paths

    def run_heavy_build_pipeline(
        self, required_checks: Optional[List[str]] = None
    ) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """Runs framework build, asset rendering, and post-build validators."""
        checks = required_checks if required_checks is not None else self.context.get(
            "build_pipeline", {}
        ).get("heavy_checks", ["npm ci", "npm run build"])
        return self.checker.check_build_and_validators(checks)

    def attempt_on_error_repair(self, failure_reason: str, changed_paths: List[str]) -> Tuple[bool, str]:
        """On-Error Repair Agent: Attempts automatic remediation when build fails."""
        # Check for common quick fixes (e.g. missing trailing line endings or formatting)
        clean_ok, _ = self.checker.check_diff_cleanliness()
        if not clean_ok:
            # Run git diff --check fix or format
            p = subprocess.run(
                ["git", "diff", "--check"],
                cwd=self.repo_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if p.returncode != 0:
                # Attempt formatting / whitespace cleanup
                subprocess.run(["npm", "run", "format"], cwd=self.repo_dir, capture_output=True)

        # Re-run heavy build checks to see if repair resolved the issue
        recheck_ok, recheck_msg, _ = self.run_heavy_build_pipeline()
        if recheck_ok:
            return True, f"On-Error Repair succeeded: {recheck_msg}"

        return False, f"On-Error Repair could not auto-resolve build failure: {failure_reason}"
