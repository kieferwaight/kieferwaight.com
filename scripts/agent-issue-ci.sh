#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd "$script_dir/.." && pwd)"

echo "=== AGENT CI SCRIPT STARTING ==="
echo "AGENT_ISSUE_IID=${AGENT_ISSUE_IID:-unset}"
echo "CI_PROJECT_DIR=${CI_PROJECT_DIR:-unset}"

: "${AGENT_ISSUE_IID:?AGENT_ISSUE_IID is required}"
: "${CI_API_V4_URL:?CI_API_V4_URL is required}"
: "${CI_PROJECT_ID:?CI_PROJECT_ID is required}"
: "${CI_PROJECT_DIR:?CI_PROJECT_DIR is required}"
: "${GITLAB_AGENT_TOKEN:?GITLAB_AGENT_TOKEN is required}"
: "${LITELLM_API_KEY:?LITELLM_API_KEY is required}"

if [[ ! "$AGENT_ISSUE_IID" =~ ^[1-9][0-9]*$ ]]; then
  echo 'AGENT_ISSUE_IID must be a positive issue IID.' >&2
  exit 64
fi

git config --global --add safe.directory "$CI_PROJECT_DIR" || true
git config user.name 'GitLab Agent'
git config user.email 'gitlab-agent@kieferwaight.com'

export PYTHONPATH="${project_root}:${CI_PROJECT_DIR}:${PYTHONPATH:-}"

python3 -m gitlab.agent.cli run "$AGENT_ISSUE_IID" --repo-dir "$CI_PROJECT_DIR" --state-dir "$CI_PROJECT_DIR/.agent-state"
