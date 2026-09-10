#!/usr/bin/env bash
set -euo pipefail

readonly GITLAB_WEB_ORIGIN="https://gitlab.kieferwaight.com"
readonly GITLAB_PROJECT_PATH="kieferwaight/kieferwaight.com"
readonly GITLAB_REMOTE="gitlab"

require_issue_number() {
  local issue_number="${1:-}"
  if [[ ! "$issue_number" =~ ^[1-9][0-9]*$ ]]; then
    echo "Issue number must be a positive integer." >&2
    exit 64
  fi
}

issue_url() {
  local issue_number="$1"
  printf '%s/%s/-/issues/%s\n' "$GITLAB_WEB_ORIGIN" "$GITLAB_PROJECT_PATH" "$issue_number"
}

issue_title() {
  local issue_number="$1"
  local page_title

  if [[ -n "${ISSUE_TITLE:-}" ]]; then
    printf '%s\n' "$ISSUE_TITLE"
    return
  fi

  page_title="$(curl --fail --silent --show-error --location "$(issue_url "$issue_number")" | python3 -c '
import html
import re
import sys

match = re.search(r"<title>(.*?) \(#\d+\)", sys.stdin.read(), flags=re.DOTALL)
print(html.unescape(match.group(1)).strip() if match else "")
')"
  if [[ -z "$page_title" ]]; then
    echo "Could not read the title for issue #$issue_number. Set ISSUE_TITLE and retry." >&2
    exit 69
  fi
  printf '%s\n' "$page_title"
}

slugify() {
  tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed -E 's/^-+|-+$//g'
}

branch_kind() {
  local kind="${ISSUE_BRANCH_KIND:-content}"
  case "$kind" in
    content|refresh|fix) printf '%s\n' "$kind" ;;
    *)
      echo "ISSUE_BRANCH_KIND must be content, refresh, or fix." >&2
      exit 64
      ;;
  esac
}

verify_gitlab_main_is_current() {
  git fetch "$GITLAB_REMOTE" main
  if ! git remote get-url origin >/dev/null 2>&1; then
    return
  fi

  git fetch origin main
  if ! git merge-base --is-ancestor origin/main "$GITLAB_REMOTE/main"; then
    echo "GitLab main is behind GitHub main. Merge the publishing-boundary MR before starting issue branches." >&2
    exit 1
  fi
}

mr_url() {
  local issue_number="$1"
  local branch="$2"
  local encoded_branch
  encoded_branch="$(python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1], safe=""))' "$branch")"
  printf '%s/%s/-/merge_requests/new?merge_request%%5Bsource_branch%%5D=%s&merge_request%%5Btarget_branch%%5D=main&merge_request%%5Bdescription%%5D=Closes%%20%%23%s\n' \
    "$GITLAB_WEB_ORIGIN" "$GITLAB_PROJECT_PATH" "$encoded_branch" "$issue_number"
}

open_url() {
  local url="$1"
  if [[ "${ISSUE_WORKFLOW_NO_OPEN:-0}" == "1" ]]; then
    printf 'MR form: %s\n' "$url"
    return
  fi
  if command -v open >/dev/null; then
    open "$url"
  elif command -v xdg-open >/dev/null; then
    xdg-open "$url"
  else
    printf 'Open this MR form: %s\n' "$url"
  fi
}
