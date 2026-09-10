"""Pre-flight triage helper for auto-populating structured issue templates."""
from typing import Dict, Any, Optional
from .issue_parser import parse_issue, IssueContext
from .gitlab_client import GitLabClient


def triage_issue(issue_data: Dict[str, Any], gitlab_client: Optional[GitLabClient] = None) -> IssueContext:
    """Analyze issue data. If description is missing or unstructured, auto-populate template structure."""
    issue_ctx = parse_issue(issue_data)
    if not issue_ctx.parse_error and not issue_ctx.is_title_only:
        return issue_ctx

    issue_iid = issue_data.get("iid")
    title = issue_data.get("title", "Untitled Issue")

    # If missing structured sections and a live client is available, try auto-populating
    if (not issue_ctx.goal or not issue_ctx.acceptance_criteria) and gitlab_client and issue_iid:
        formatted_desc = f"""## Goal
{title}

## Acceptance Criteria
- Implement required changes for {title}.
- Pass repository validation checks.

## Permitted Scope
- `src/`
"""
        try:
            gitlab_client._request("PUT", f"/issues/{issue_iid}", data={"description": formatted_desc})
            issue_data["description"] = formatted_desc
            issue_ctx = parse_issue(issue_data)
        except Exception:
            pass

    return issue_ctx
