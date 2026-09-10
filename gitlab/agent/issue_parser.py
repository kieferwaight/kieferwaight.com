"""Issue parsing, label validation, branch naming, and task packet construction."""
import re
from typing import List, Tuple, Optional, Dict, Any
from .models import IssueContext, TaskPacket

CONTROLLED_TYPES = {
    "agent:content": "content",
    "agent:fix": "fix",
    "agent:refresh": "refresh",
}

DEFAULT_ALLOWED_PATHS = {
    "content": [
        "src/content/",
        "src/data/project-photo-collections.json",
        "public/project-images/",
        "public/assets/img/",
        "public/decks/",
    ],
    "fix": [
        "src/",
        "public/",
    ],
    "refresh": [
        "src/",
        "public/",
    ],
}


def slugify(text: str) -> str:
    cleaned = text.lower()
    cleaned = re.sub(r"[^a-z0-9]+", "-", cleaned)
    cleaned = cleaned.strip("-")
    return cleaned or "issue"


def parse_labels(labels: List[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Validates issue labels.
    Requires 'ready-for-agent' and EXACTLY ONE controlled type label.
    Returns (type_kind, error_message).
    """
    if "ready-for-agent" not in labels:
        return None, "Missing required label 'ready-for-agent'."

    matched_types = []
    unknown_agent_labels = []

    for l in labels:
        if l in CONTROLLED_TYPES:
            matched_types.append(CONTROLLED_TYPES[l])
        elif l.startswith("agent:") and l not in (
            "agent:running",
            "agent:qa",
            "agent:rework",
            "agent:blocked",
            "agent:ready-for-review",
        ):
            unknown_agent_labels.append(l)

    if unknown_agent_labels:
        return None, f"Unknown agent label(s) present: {', '.join(unknown_agent_labels)}."

    if len(matched_types) == 0:
        return None, "No controlled type label found. Exactly one of 'agent:content', 'agent:fix', or 'agent:refresh' is required."

    if len(matched_types) > 1:
        return None, f"Multiple controlled type labels found: {', '.join(matched_types)}. Exactly one is permitted."

    return matched_types[0], None


def parse_description_sections(description: str) -> Dict[str, Any]:
    """
    Parses structured sections from issue description:
    Goal, Acceptance Criteria, Permitted Scope / Scope, Relevant Links / Links.
    """
    if not description or not description.strip():
        return {
            "goal": "",
            "acceptance_criteria": [],
            "permitted_scope": [],
            "relevant_links": [],
            "is_title_only": True,
        }

    # Split into headings
    lines = description.splitlines()
    sections: Dict[str, List[str]] = {
        "goal": [],
        "acceptance_criteria": [],
        "scope": [],
        "links": [],
        "other": [],
    }

    current_section = "other"

    for line in lines:
        lower_line = line.strip().lower()
        if re.match(r"^#+\s*goal", lower_line) or lower_line.startswith("goal:"):
            current_section = "goal"
            content = re.sub(r"^(#+\s*goal:?|goal:?)", "", line, flags=re.IGNORECASE).strip()
            if content:
                sections["goal"].append(content)
        elif re.match(r"^#+\s*acceptance criteria", lower_line) or lower_line.startswith("acceptance criteria:"):
            current_section = "acceptance_criteria"
            content = re.sub(r"^(#+\s*acceptance criteria:?|acceptance criteria:?)", "", line, flags=re.IGNORECASE).strip()
            if content:
                sections["acceptance_criteria"].append(content)
        elif re.match(r"^#+\s*(permitted\s+)?scope", lower_line) or lower_line.startswith("scope:") or lower_line.startswith("permitted scope:"):
            current_section = "scope"
            content = re.sub(r"^(#+\s*(permitted\s+)?scope:?|(permitted\s+)?scope:?)", "", line, flags=re.IGNORECASE).strip()
            if content:
                sections["scope"].append(content)
        elif re.match(r"^#+\s*(relevant\s+)?links", lower_line) or lower_line.startswith("links:") or lower_line.startswith("relevant links:"):
            current_section = "links"
            content = re.sub(r"^(#+\s*(relevant\s+)?links:?|(relevant\s+)?links:?)", "", line, flags=re.IGNORECASE).strip()
            if content:
                sections["links"].append(content)
        else:
            sections[current_section].append(line)

    goal_text = "\n".join(sections["goal"]).strip()
    
    # Process items into lists for AC, Scope, Links
    def extract_items(lines_list: List[str]) -> List[str]:
        items = []
        for l in lines_list:
            cleaned = l.strip()
            if not cleaned:
                continue
            # Strip bullet points
            cleaned = re.sub(r"^[\*\-\+]\s+", "", cleaned)
            cleaned = re.sub(r"^\d+\.\s+", "", cleaned)
            if cleaned:
                items.append(cleaned)
        return items

    ac_items = extract_items(sections["acceptance_criteria"])
    scope_items = extract_items(sections["scope"])
    link_items = extract_items(sections["links"])

    # If Goal or Acceptance Criteria are completely missing, treat as title-only / unstructured
    is_title_only = not (goal_text or ac_items)

    return {
        "goal": goal_text or description.strip(),
        "acceptance_criteria": ac_items,
        "permitted_scope": scope_items,
        "relevant_links": link_items,
        "is_title_only": is_title_only,
    }


def parse_issue(issue_json: dict) -> IssueContext:
    iid = int(issue_json.get("iid") or issue_json.get("id"))
    title = issue_json.get("title", "").strip()
    description = issue_json.get("description") or ""
    web_url = issue_json.get("web_url") or issue_json.get("webUrl") or ""
    labels = issue_json.get("labels") or []
    state = issue_json.get("state") or "opened"

    type_kind, label_err = parse_labels(labels)
    if label_err and "ready-for-agent" in labels and not any(l.startswith("agent:") for l in labels):
        # Fallback type inference from title
        title_lower = title.lower()
        if title_lower.startswith("fix") or " fix " in title_lower:
            type_kind = "fix"
        elif title_lower.startswith("refresh") or " refresh " in title_lower:
            type_kind = "refresh"
        else:
            type_kind = "content"
        label_err = None

    if label_err:
        return IssueContext(
            iid=iid,
            title=title,
            description=description,
            web_url=web_url,
            labels=labels,
            state=state,
            parse_error=label_err,
        )

    desc_sections = parse_description_sections(description)
    if desc_sections["is_title_only"]:
        return IssueContext(
            iid=iid,
            title=title,
            description=description,
            web_url=web_url,
            labels=labels,
            state=state,
            type_kind=type_kind,
            is_title_only=True,
            parse_error="Structured issue description containing Goal and Acceptance Criteria is required. Title-only or unstructured issues cannot start an agent turn.",
        )

    slug = slugify(title)
    branch_name = f"{type_kind}/{iid}-{slug}"

    # Determine permitted scope paths
    permitted = desc_sections["permitted_scope"]
    if not permitted:
        permitted = DEFAULT_ALLOWED_PATHS.get(type_kind, ["src/", "public/"])

    return IssueContext(
        iid=iid,
        title=title,
        description=description,
        web_url=web_url,
        labels=labels,
        state=state,
        type_kind=type_kind,
        slug=slug,
        branch_name=branch_name,
        goal=desc_sections["goal"],
        acceptance_criteria=desc_sections["acceptance_criteria"],
        permitted_scope=permitted,
        relevant_links=desc_sections["relevant_links"],
        is_title_only=False,
    )


def build_task_packet(issue_ctx: IssueContext, prior_qa_findings: Optional[dict] = None) -> TaskPacket:
    allowed_paths = issue_ctx.permitted_scope or DEFAULT_ALLOWED_PATHS.get(
        issue_ctx.type_kind or "content", ["src/", "public/"]
    )

    repo_instructions = (
        "Implement the issue requirements in the repository. "
        "Work ONLY within the allowed paths listed in this task packet. "
        "Do not modify CI configuration, workflow files, credentials, branch protection, or Git remotes. "
        "Validate all changes using project check scripts or npm run build before finishing. "
        "Do not commit, push, create merge requests, or comment on GitLab."
    )

    # Heavy framework builds, diagram rendering (puppeteer), and site builds run in post-agent CI stages.
    required_checks = []

    return TaskPacket(
        issue_snapshot=issue_ctx.to_snapshot(),
        acceptance_criteria=issue_ctx.acceptance_criteria,
        repository_instructions=repo_instructions,
        allowed_paths=allowed_paths,
        required_checks=required_checks,
        branch_name=issue_ctx.branch_name,
        prior_qa_findings=prior_qa_findings,
    )
