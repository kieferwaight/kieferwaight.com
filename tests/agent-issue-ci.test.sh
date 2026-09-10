#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "$0")/.." && pwd)"
test_dir="$(mktemp -d)"
trap 'rm -rf "$test_dir"' EXIT
repo_dir="$test_dir/repo"
bin_dir="$test_dir/bin"
log_file="$test_dir/calls.log"
api_log_file="$test_dir/api.log"
port_pipe="$test_dir/api-port.pipe"

mkdir -p "$repo_dir/src/content" "$bin_dir"
mkfifo "$port_pipe"
git -C "$repo_dir" init -q --initial-branch=main
git -C "$repo_dir" config user.name 'Agent CI Test'
git -C "$repo_dir" config user.email 'agent-ci-test@example.invalid'
touch "$repo_dir/src/content/.keep"
git -C "$repo_dir" add src/content/.keep
git -C "$repo_dir" commit -qm 'test: initialize fixture'
git -C "$repo_dir" remote add origin https://gitlab.example.test/group/project.git
git -C "$repo_dir" update-ref refs/remotes/origin/main HEAD

cat > "$test_dir/gitlab-api.py" <<'PY'
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

log_file = sys.argv[1]

issues = {
  "42": {
    "iid": 42,
    "state": "opened",
    "labels": ["ready-for-agent", "agent:refresh"],
    "title": "Refresh agent test content",
    "description": "",
    "web_url": "https://gitlab.example.test/group/project/-/issues/42",
  },
  "43": {
    "iid": 43,
    "state": "opened",
    "labels": ["ready-for-agent", "agent:content"],
    "title": "No op agent test content",
    "description": "",
    "web_url": "https://gitlab.example.test/group/project/-/issues/43",
  },
}


class Handler(BaseHTTPRequestHandler):
  def _body(self):
    length = int(self.headers.get("Content-Length") or 0)
    if length == 0:
      return {}
    return json.loads(self.rfile.read(length).decode("utf-8"))

  def _send(self, payload, status=200):
    data = json.dumps(payload).encode("utf-8")
    self.send_response(status)
    self.send_header("Content-Type", "application/json")
    self.send_header("Content-Length", str(len(data)))
    self.end_headers()
    self.wfile.write(data)

  def _log(self, extra=""):
    with open(log_file, "a", encoding="utf-8") as handle:
      handle.write(f"{self.command} {self.path} {extra}\n")

  def do_GET(self):
    parsed = urlparse(self.path)
    self._log()
    if parsed.path.endswith("/issues/42"):
      self._send(issues["42"])
    elif parsed.path.endswith("/issues/43"):
      self._send(issues["43"])
    elif parsed.path.endswith("/merge_requests"):
      self._send([])
    else:
      self._send({}, status=404)

  def do_PUT(self):
    body = self._body()
    self._log(json.dumps(body, sort_keys=True))
    issue_iid = self.path.rstrip("/").rsplit("/", 1)[-1]
    if issue_iid in issues:
      labels = body.get("labels")
      if labels is not None:
        issues[issue_iid]["labels"] = [label for label in labels.split(",") if label]
      self._send(issues[issue_iid])
    else:
      self._send({}, status=404)

  def do_POST(self):
    body = self._body()
    self._log(json.dumps(body, sort_keys=True))
    if self.path.endswith("/merge_requests"):
      self._send({"iid": 42, "web_url": "https://gitlab.example.test/group/project/-/merge_requests/42"})
    else:
      self._send({"id": 1})

  def log_message(self, format, *args):
    return


server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
print(server.server_port, flush=True)
server.serve_forever()
PY

python3 "$test_dir/gitlab-api.py" "$api_log_file" > "$port_pipe" 2> "$test_dir/api.err" &
api_pid=$!
trap 'kill "$api_pid" 2>/dev/null || true; rm -rf "$test_dir"' EXIT
IFS= read -r api_port < "$port_pipe"

cat > "$bin_dir/git" <<'STUB'
#!/usr/bin/env bash
set -euo pipefail
original_args=("$@")
if [[ "${1:-}" = "-C" ]]; then
  shift 2
fi
if [[ "$1" = "config" && "${2:-}" = "--global" ]]; then
  exit 0
fi
if [[ "$1" = "ls-remote" ]]; then
  exit 2
fi
if [[ "$1" = "fetch" ]]; then
  exit 0
fi
if [[ "$1" = "remote" && "$2" = "set-url" ]]; then
  exit 0
fi
if [[ "$1" = "push" ]]; then
  printf 'git push %s\n' "$*" >> "$TEST_CALL_LOG"
  exit 0
fi
exec /usr/bin/git "${original_args[@]}"
STUB

cat > "$test_dir/agent-entrypoint" <<'STUB'
#!/usr/bin/env bash
set -euo pipefail
[[ "$1" = "task" ]]
[[ -z "${GITLAB_AGENT_TOKEN:-}" ]]
[[ -z "${CI_JOB_TOKEN:-}" ]]
[[ "$*" = *'Implement this GitLab issue in the current repository.'* ]]
[[ "$*" = *'Issue: #42 Refresh agent test content'* ]]
[[ "$*" != *'task-packet.json'* ]]
printf '%s\n' '---' > src/content/agent-ci-test.md
printf '%s\n' 'title: Agent CI Test' >> src/content/agent-ci-test.md
STUB
chmod +x "$bin_dir/git" "$test_dir/agent-entrypoint"

(
  cd "$repo_dir"
  PATH="$bin_dir:$PATH" \
    TEST_CALL_LOG="$log_file" \
    AGENT_ENTRYPOINT="$test_dir/agent-entrypoint" \
    AGENT_ISSUE_IID=42 \
    GITLAB_AGENT_TOKEN=test-only \
    LITELLM_API_KEY=test-only \
    CI_API_V4_URL="http://127.0.0.1:$api_port/api/v4" \
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
grep -F 'git push push -f origin HEAD:refs/heads/refresh/42-refresh-agent-test-content' "$log_file"
grep -F 'POST /api/v4/projects/123/merge_requests' "$api_log_file"

cat > "$test_dir/noop-agent-entrypoint" <<'STUB'
#!/usr/bin/env bash
set -euo pipefail
[[ -z "${GITLAB_AGENT_TOKEN:-}" ]]
[[ "$*" = *'Issue: #43 No op agent test content'* ]]
[[ "$*" != *'task-packet.json'* ]]
STUB
chmod +x "$test_dir/noop-agent-entrypoint"

if noop_output="$(
  (
    cd "$repo_dir"
    PATH="$bin_dir:$PATH" \
      TEST_CALL_LOG="$log_file" \
      AGENT_ENTRYPOINT="$test_dir/noop-agent-entrypoint" \
      AGENT_ISSUE_IID=43 \
      GITLAB_AGENT_TOKEN=test-only \
      LITELLM_API_KEY=test-only \
      CI_API_V4_URL="http://127.0.0.1:$api_port/api/v4" \
      CI_PROJECT_ID=123 \
      CI_PROJECT_DIR="$repo_dir" \
      CI_SERVER_HOST=gitlab.example.test \
      CI_PROJECT_PATH=group/project \
      CI_DEFAULT_BRANCH=main \
      CI_PIPELINE_ID=100 \
      bash "$project_dir/scripts/agent-issue-ci.sh"
  ) 2>&1
)"; then
  echo 'agent issue CI accepted a no-op agent run' >&2
  exit 1
fi
grep -F 'finished without repository changes' "$api_log_file"
test "$(grep -c '^git push ' "$log_file")" -eq 1

echo 'agent issue CI integration: PASS'
