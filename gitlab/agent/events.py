"""Secretless event logger for controller, worker, and judge actions."""
import json
import os
import re
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional

SECRET_PATTERNS = [
    r"glpat-[A-Za-z0-9_\-]{20,}",
    r"sk-proj-[A-Za-z0-9_\-]{20,}",
    r"sk-router-[A-Za-z0-9_\-]{20,}",
    r"https?://[^:@]+:[^@]+@",  # basic auth in URLs
]


def sanitize_value(val: Any) -> Any:
    if isinstance(val, str):
        cleaned = val
        for pattern in SECRET_PATTERNS:
            cleaned = re.sub(pattern, "[REDACTED]", cleaned)
        return cleaned
    elif isinstance(val, dict):
        return {k: sanitize_value(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [sanitize_value(item) for item in val]
    return val


def log_event(
    event_name: str,
    run_id: str,
    turn_id: str,
    state_dir: str,
    issue_iid: Optional[int] = None,
    branch: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> dict:
    os.makedirs(state_dir, exist_ok=True)
    events_file = os.path.join(state_dir, "events.jsonl")

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rec = {
        "event": event_name,
        "run_id": run_id,
        "turn_id": turn_id,
        "timestamp": timestamp,
    }
    if issue_iid is not None:
        rec["issue_iid"] = issue_iid
    if branch is not None:
        rec["branch"] = branch
    if details:
        rec.update(sanitize_value(details))

    line = json.dumps(rec)
    with open(events_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")

    return rec
