"""GitLab issue-event webhook relay and idempotency lock manager."""
import json
import os
import hashlib
from typing import Tuple, Dict, Any, Optional


def compute_event_hash(payload: dict) -> str:
    object_attributes = payload.get("object_attributes", {})
    issue_id = object_attributes.get("id") or object_attributes.get("iid", "")
    updated_at = object_attributes.get("updated_at", "")
    labels = sorted([l.get("title") if isinstance(l, dict) else str(l) for l in payload.get("labels", [])])
    raw_str = f"{issue_id}:{updated_at}:{','.join(labels)}"
    return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()[:16]


def is_event_idempotent(state_dir: str, issue_iid: int, event_hash: str) -> bool:
    lock_dir = os.path.join(state_dir, "idempotency")
    os.makedirs(lock_dir, exist_ok=True)
    lock_file = os.path.join(lock_dir, f"{issue_iid}-{event_hash}.json")
    if os.path.exists(lock_file):
        return False
    
    with open(lock_file, "w", encoding="utf-8") as f:
        json.dump({"issue_iid": issue_iid, "event_hash": event_hash}, f)
    return True


def get_openbao_credential() -> str:
    """
    Retrieves GitLab API token from OpenBao if configured,
    or falls back to environment variable GITLAB_AGENT_TOKEN.
    """
    openbao_secret = os.getenv("OPENBAO_SECRET")
    if openbao_secret:
        return openbao_secret.strip()

    bao_addr = os.getenv("OPENBAO_ADDR")
    bao_token = os.getenv("OPENBAO_TOKEN")
    bao_secret_path = os.getenv("OPENBAO_SECRET_PATH", "secret/data/gitlab/agent")

    if bao_addr and bao_token:
        try:
            import urllib.request
            req = urllib.request.Request(
                f"{bao_addr.rstrip('/')}/v1/{bao_secret_path}",
                headers={"X-Vault-Token": bao_token},
                method="GET",
            )
            with urllib.request.urlopen(req) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                secret_data = res.get("data", {}).get("data", {})
                token = secret_data.get("GITLAB_PAT") or secret_data.get("GITLAB_AGENT_TOKEN") or secret_data.get("token")
                if token:
                    return token
        except Exception:
            pass

    return os.getenv("GITLAB_PAT") or os.getenv("GITLAB_AGENT_TOKEN") or ""


def process_webhook_payload(
    payload: dict,
    state_dir: str = ".agent-state",
) -> Tuple[bool, str, Optional[int]]:
    """
    Processes incoming GitLab webhook event.
    Returns (should_run, reason_or_message, issue_iid).
    """
    object_kind = payload.get("object_kind")
    if object_kind != "issue":
        return False, f"Ignored event object_kind '{object_kind}' (expected 'issue').", None

    attrs = payload.get("object_attributes", {})
    issue_iid = attrs.get("iid") or attrs.get("id")
    if not issue_iid:
        return False, "Missing issue IID in webhook payload.", None

    state = attrs.get("state", "opened")
    if state != "opened":
        return False, f"Issue #{issue_iid} state is '{state}' (must be 'opened').", issue_iid

    labels_data = payload.get("labels") or attrs.get("labels") or []
    labels = []
    for l in labels_data:
        if isinstance(l, dict):
            labels.append(l.get("title", ""))
        else:
            labels.append(str(l))

    if "ready-for-agent" not in labels:
        return False, f"Issue #{issue_iid} does not have label 'ready-for-agent'.", issue_iid

    event_hash = compute_event_hash(payload)
    if not is_event_idempotent(state_dir, issue_iid, event_hash):
        return False, f"Duplicate webhook event for issue #{issue_iid} (event hash {event_hash}).", issue_iid

    return True, f"Qualifying issue event received for issue #{issue_iid}.", issue_iid
