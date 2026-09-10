#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "$0")/.." && pwd)"
test_dir="$(mktemp -d)"
trap 'rm -rf "$test_dir"' EXIT
repo_dir="$test_dir/repo"
bin_dir="$test_dir/bin"
log_file="$test_dir/calls.log"

mkdir -p "$repo_dir/src/content" "$bin_dir"
git -C "$repo_dir" init -q --initial-branch=main
git -C "$repo_dir" config user.name 'Agent CI Test'
git -C "$repo_dir" config user.email 'agent-ci-test@example.invalid'
touch "$repo_dir/src/content/.keep"
git -C "$repo_dir" add src/content/.keep
git -C "$repo_dir" commit -qm 'test: initialize fixture'
git -C "$repo_dir" remote add origin https://gitlab.example.test/group/project.git
git -C "$repo_dir" update-ref refs/remotes/origin/main HEAD

cat > "$bin_dir/curl" <<'STUB'
#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' "$*" >> "$TEST_CALL_LOG"
if [[ " $* " = *' --request POST '* ]]; then
  printf '%s\n' '{"web_url":"https://gitlab.example.test/group/project/-/merge_requests/42"}'
else
  printf '%s\n' '{"state":"opened","labels":["ready-for-agent"],"title":"Refresh agent test content"}'
fi
STUB

cat > "$bin_dir/git" <<'STUB'
#!/usr/bin/env bash
set -euo pipefail
if [[ "$1" = "config" && "${2:-}" = "--global" ]]; then
  exit 0
fi
if [[ "$1" = "ls-remote" ]]; then
  exit 2
fi
if [[ "$1" = "remote" && "$2" = "set-url" ]]; then
  exit 0
fi
if [[ "$1" = "push" ]]; then
  printf 'git push %s\n' "$*" >> "$TEST_CALL_LOG"
  exit 0
fi
exec /usr/bin/git "$@"
STUB

cat > "$test_dir/agent-entrypoint" <<'STUB'
#!/usr/bin/env bash
set -euo pipefail
[[ "$1" = "task" ]]
[[ -z "${GITLAB_AGENT_TOKEN:-}" ]]
[[ -z "${CI_JOB_TOKEN:-}" ]]
printf '%s\n' '---' > src/content/agent-ci-test.md
printf '%s\n' 'title: Agent CI Test' >> src/content/agent-ci-test.md
STUB
chmod +x "$bin_dir/curl" "$bin_dir/git" "$test_dir/agent-entrypoint"

(
  cd "$repo_dir"
  PATH="$bin_dir:$PATH" \
    TEST_CALL_LOG="$log_file" \
    AGENT_ENTRYPOINT="$test_dir/agent-entrypoint" \
    AGENT_ISSUE_IID=42 \
    GITLAB_AGENT_TOKEN=test-only \
    LITELLM_API_KEY=test-only \
    CI_API_V4_URL=https://gitlab.example.test/api/v4 \
    CI_PROJECT_ID=123 \
    CI_PROJECT_DIR="$repo_dir" \
    CI_SERVER_HOST=gitlab.example.test \
    CI_PROJECT_PATH=group/project \
    CI_DEFAULT_BRANCH=main \
    CI_PIPELINE_ID=99 \
    bash "$project_dir/scripts/agent-issue-ci.sh"
)

test "$(git -C "$repo_dir" branch --show-current)" = 'refresh/42-refresh-agent-test-content'
git -C "$repo_dir" show --quiet --format=%s HEAD | grep -F 'refresh: Refresh agent test content (refs #42)'
git -C "$repo_dir" show HEAD:src/content/agent-ci-test.md | grep -F 'title: Agent CI Test'
grep -F 'git push push origin HEAD:refs/heads/refresh/42-refresh-agent-test-content' "$log_file"
grep -F -- '--request POST' "$log_file"

cat > "$test_dir/forbidden-agent-entrypoint" <<'STUB'
#!/usr/bin/env bash
set -euo pipefail
[[ -z "${GITLAB_AGENT_TOKEN:-}" ]]
printf '%s\n' '# forbidden test mutation' >> .gitlab-ci.yml
STUB
chmod +x "$test_dir/forbidden-agent-entrypoint"

if forbidden_output="$(
  (
    cd "$repo_dir"
    PATH="$bin_dir:$PATH" \
      TEST_CALL_LOG="$log_file" \
      AGENT_ENTRYPOINT="$test_dir/forbidden-agent-entrypoint" \
      AGENT_ISSUE_IID=43 \
      GITLAB_AGENT_TOKEN=test-only \
      LITELLM_API_KEY=test-only \
      CI_API_V4_URL=https://gitlab.example.test/api/v4 \
      CI_PROJECT_ID=123 \
      CI_PROJECT_DIR="$repo_dir" \
      CI_SERVER_HOST=gitlab.example.test \
      CI_PROJECT_PATH=group/project \
      CI_DEFAULT_BRANCH=main \
      CI_PIPELINE_ID=100 \
      bash "$project_dir/scripts/agent-issue-ci.sh"
  ) 2>&1
)"; then
  echo 'agent issue CI accepted an out-of-scope mutation' >&2
  exit 1
fi
printf '%s\n' "$forbidden_output" | grep -F 'Agent changed a file outside the content-only scope'
test "$(grep -c '^git push ' "$log_file")" -eq 1

echo 'agent issue CI integration: PASS'
