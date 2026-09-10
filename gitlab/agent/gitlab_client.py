"""GitLab API client for issues, merge requests, labels, and comments."""
import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error
from typing import Optional, Dict, Any, List


class GitLabClient:
    def __init__(
        self,
        api_url: Optional[str] = None,
        project_id: Optional[str] = None,
        token: Optional[str] = None,
    ):
        self.api_url = (api_url or os.getenv("CI_API_V4_URL") or "https://gitlab.kieferwaight.com/api/v4").rstrip("/")
        pid = str(project_id or os.getenv("CI_PROJECT_ID") or os.getenv("CI_PROJECT_PATH") or "kieferwaight/kieferwaight.com")
        self.project_id = urllib.parse.quote(pid, safe="")
        self.token = token or os.getenv("GITLAB_PAT") or os.getenv("GITLAB_AGENT_TOKEN") or ""

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["PRIVATE-TOKEN"] = self.token
        return headers

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        url = f"{self.api_url}/projects/{self.project_id}{endpoint}"
        if params:
            query = urllib.parse.urlencode(params)
            url = f"{url}?{query}"

        body_bytes = None
        if data is not None:
            body_bytes = json.dumps(data).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=body_bytes,
            headers=self._headers(),
            method=method,
        )

        try:
            with urllib.request.urlopen(req) as resp:
                res_body = resp.read().decode("utf-8")
                if res_body:
                    return json.loads(res_body)
                return {}
        except urllib.error.HTTPError as e:
            err_text = e.read().decode("utf-8") if e.fp else ""
            if e.code in (401, 403) and method != "GET":
                print(f"[GitLabClient] Notice: HTTP {e.code} on {method} {url} (no write token). Continuing locally.", file=sys.stderr)
                return {"status": "unauthenticated_local_run"}
            raise RuntimeError(f"GitLab API HTTP {e.code} error on {method} {url}: {err_text}") from e

    def get_issue(self, iid: int) -> dict:
        return self._request("GET", f"/issues/{iid}")

    def post_issue_comment(self, iid: int, body: str) -> dict:
        return self._request("POST", f"/issues/{iid}/notes", data={"body": body})

    def update_issue_labels(
        self,
        iid: int,
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None,
    ) -> dict:
        current_issue = self.get_issue(iid)
        current_labels = set(current_issue.get("labels") or [])

        if remove_labels:
            for l in remove_labels:
                current_labels.discard(l)
        if add_labels:
            for l in add_labels:
                current_labels.add(l)

        new_labels_str = ",".join(sorted(current_labels))
        return self._request(
            "PUT",
            f"/issues/{iid}",
            data={"labels": new_labels_str},
        )

    def get_open_mr_for_branch(self, source_branch: str) -> Optional[dict]:
        res = self._request(
            "GET",
            "/merge_requests",
            params={"state": "opened", "source_branch": source_branch},
        )
        if isinstance(res, list) and len(res) > 0:
            return res[0]
        return None

    def create_draft_mr(
        self,
        source_branch: str,
        target_branch: str,
        title: str,
        description: str,
    ) -> dict:
        if not title.startswith("Draft:"):
            title = f"Draft: {title}"
        return self._request(
            "POST",
            "/merge_requests",
            data={
                "source_branch": source_branch,
                "target_branch": target_branch,
                "title": title,
                "description": description,
            },
        )

    def update_mr(
        self,
        mr_iid: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        assignee_id: Optional[int] = None,
    ) -> dict:
        data: Dict[str, Any] = {}
        if title is not None:
            data["title"] = title
        if description is not None:
            data["description"] = description
        if assignee_id is not None:
            data["assignee_id"] = assignee_id
        return self._request("PUT", f"/merge_requests/{mr_iid}", data=data)

    def post_mr_comment(self, mr_iid: int, body: str) -> dict:
        return self._request("POST", f"/merge_requests/{mr_iid}/notes", data={"body": body})

    def assign_user_to_mr(self, mr_iid: int, username: str) -> dict:
        # Search user by username
        user_url = f"{self.api_url}/users?username={urllib.parse.quote(username)}"
        req = urllib.request.Request(user_url, headers=self._headers(), method="GET")
        try:
            with urllib.request.urlopen(req) as resp:
                users = json.loads(resp.read().decode("utf-8"))
                if users and len(users) > 0:
                    user_id = users[0]["id"]
                    return self.update_mr(mr_iid, assignee_id=user_id)
        except Exception:
            pass
        # Fallback: post comment mentioning assignment if user lookup failed
        self.post_mr_comment(mr_iid, f"assigned to @{username}")
        return {"assigned": username}
