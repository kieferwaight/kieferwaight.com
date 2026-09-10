#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/issue-workflow.sh"

issue_number="${1:-}"
require_issue_number "$issue_number"

branch="$(git branch --show-current)"
if [[ ! "$branch" =~ ^(content|refresh|fix)/${issue_number}- ]]; then
  echo "Current branch '$branch' is not an issue #$issue_number workflow branch." >&2
  exit 1
fi

git diff --check
npm run test:quality

git add --all
if git diff --cached --quiet; then
  echo "No changes to submit." >&2
  exit 1
fi
git diff --cached --check

issue_name="$(issue_title "$issue_number")"
git commit -m "${branch%%/*}: ${issue_name} (refs #${issue_number})"
git push --set-upstream "$GITLAB_REMOTE" "$branch"

open_url "$(mr_url "$issue_number" "$branch")"
