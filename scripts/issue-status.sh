#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/issue-workflow.sh"

issue_number="${1:-}"
require_issue_number "$issue_number"

branch="$(git branch --show-current)"
printf 'Branch: %s\n' "$branch"
printf 'Issue: %s\n' "$(issue_url "$issue_number")"
printf 'MR form: %s\n' "$(mr_url "$issue_number" "$branch")"
