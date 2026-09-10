#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/issue-workflow.sh"

issue_number="${1:-}"
require_issue_number "$issue_number"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Worktree must be clean before starting an issue branch." >&2
  exit 1
fi

issue_name="$(issue_title "$issue_number")"
kind="$(branch_kind)"
slug="$(printf '%s' "$issue_name" | slugify)"
if [[ -z "$slug" ]]; then
  echo "Could not derive a branch name from issue #$issue_number." >&2
  exit 1
fi
branch="${kind}/${issue_number}-${slug}"

git fetch "$GITLAB_REMOTE" main
if git show-ref --verify --quiet "refs/heads/$branch"; then
  git switch "$branch"
else
  git switch --create "$branch" "$GITLAB_REMOTE/main"
fi

printf 'Started %s for issue #%s: %s\n' "$branch" "$issue_number" "$issue_name"
printf 'When ready, run: task issue:submit ISSUE=%s\n' "$issue_number"
