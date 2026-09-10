"""Deterministic gates for repository changes: clean diff, scope policy, build, and validators."""
import os
import subprocess
from typing import List, Tuple, Dict, Any, Optional


class DeterministicChecker:
    def __init__(self, repo_dir: str):
        self.repo_dir = repo_dir

    def _run_cmd(self, cmd: List[str], cwd: Optional[str] = None) -> Tuple[int, str, str]:
        p = subprocess.run(
            cmd,
            cwd=cwd or self.repo_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return p.returncode, p.stdout, p.stderr

    def get_changed_paths(self) -> List[str]:
        # Tracked modified files
        code1, out1, _ = self._run_cmd(["git", "diff", "--name-only"])
        # Untracked new files
        code2, out2, _ = self._run_cmd(["git", "ls-files", "--others", "--exclude-standard"])

        paths = set()
        if code1 == 0:
            for line in out1.splitlines():
                p = line.strip()
                if p and not p.startswith(".agent-state/"):
                    paths.add(p)
        if code2 == 0:
            for line in out2.splitlines():
                p = line.strip()
                if p and not p.startswith(".agent-state/"):
                    paths.add(p)

        return sorted(list(paths))

    def check_diff_cleanliness(self) -> Tuple[bool, str]:
        code, out, err = self._run_cmd(["git", "diff", "--check"])
        if code != 0:
            return False, f"Git diff --check failed:\n{err or out}"
        return True, "Diff cleanliness check passed."

    def check_no_op(self, changed_paths: List[str]) -> Tuple[bool, str]:
        if not changed_paths:
            return False, "No repository changes detected (no-op run)."
        return True, f"Detected {len(changed_paths)} changed file(s)."

    def check_scope_policy(
        self, changed_paths: List[str], allowed_paths: List[str]
    ) -> Tuple[bool, str, List[str]]:
        out_of_scope = []
        for path in changed_paths:
            matched = False
            for allowed in allowed_paths:
                allowed_clean = allowed.rstrip("/")
                if allowed.endswith("/"):
                    if path.startswith(allowed) or path.startswith(allowed_clean + "/"):
                        matched = True
                        break
                else:
                    if path == allowed_clean:
                        matched = True
                        break
            if not matched:
                out_of_scope.append(path)

        if out_of_scope:
            return (
                False,
                f"Changed file(s) outside permitted scope: {', '.join(out_of_scope)}.",
                out_of_scope,
            )
        return True, "All changed files comply with permitted scope.", []

    def check_build_and_validators(
        self, required_checks: List[str]
    ) -> Tuple[bool, str, List[Dict[str, Any]]]:
        results = []
        all_passed = True

        for check in required_checks:
            cmd = check.split()
            # If npm ci or npm run build, check if package.json exists
            if check.startswith("npm") and not os.path.exists(os.path.join(self.repo_dir, "package.json")):
                results.append({"check": check, "status": "skipped", "message": "No package.json found."})
                continue

            code, out, err = self._run_cmd(cmd)
            if code == 0:
                results.append({"check": check, "status": "passed", "stdout": out[:1000]})
            else:
                all_passed = False
                results.append({"check": check, "status": "failed", "error": err or out})
                break

        if not all_passed:
            failed_check = next((r for r in results if r["status"] == "failed"), None)
            err_msg = failed_check["error"] if failed_check else "Build validator failed."
            return False, f"Check '{failed_check['check'] if failed_check else 'validator'}' failed:\n{err_msg}", results

        return True, "All required build and validation checks passed.", results
