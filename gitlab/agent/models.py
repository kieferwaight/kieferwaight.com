"""Data models for the GitLab Agentic Turn controller, worker, and QA judge."""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any, Tuple


@dataclass
class IssueContext:
    iid: int
    title: str
    description: str
    web_url: str
    labels: List[str]
    state: str = "opened"
    type_kind: Optional[str] = None
    slug: str = ""
    branch_name: str = ""
    goal: str = ""
    acceptance_criteria: List[str] = field(default_factory=list)
    permitted_scope: List[str] = field(default_factory=list)
    relevant_links: List[str] = field(default_factory=list)
    is_title_only: bool = False
    parse_error: Optional[str] = None

    def to_snapshot(self) -> dict:
        return {
            "iid": self.iid,
            "title": self.title,
            "description": self.description,
            "web_url": self.web_url,
            "labels": self.labels,
            "type_kind": self.type_kind,
            "branch_name": self.branch_name,
            "goal": self.goal,
            "acceptance_criteria": self.acceptance_criteria,
            "permitted_scope": self.permitted_scope,
            "relevant_links": self.relevant_links,
            "is_title_only": self.is_title_only,
        }


@dataclass
class TaskPacket:
    issue_snapshot: dict
    acceptance_criteria: List[str]
    repository_instructions: str
    allowed_paths: List[str]
    required_checks: List[str]
    branch_name: str
    prior_qa_findings: Optional[dict] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class QAResult:
    decision: str  # "approve" or "rework"
    evidence: Dict[str, str] = field(default_factory=dict)
    risks: List[str] = field(default_factory=list)
    rationale: str = ""
    raw_response: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "decision": self.decision,
            "evidence": self.evidence,
            "risks": self.risks,
            "rationale": self.rationale,
        }


@dataclass
class EventRecord:
    event: str
    timestamp: str
    run_id: str
    turn_id: str
    issue_iid: Optional[int] = None
    branch: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = {
            "event": self.event,
            "timestamp": self.timestamp,
            "run_id": self.run_id,
            "turn_id": self.turn_id,
        }
        if self.issue_iid is not None:
            d["issue_iid"] = self.issue_iid
        if self.branch is not None:
            d["branch"] = self.branch
        if self.details:
            d.update(self.details)
        return d
