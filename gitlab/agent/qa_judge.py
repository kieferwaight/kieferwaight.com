"""Hybrid QA Judge using LiteLLM to evaluate MR diff against issue criteria."""
import json
import os
import re
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any, List, Optional
from .models import QAResult


class QAJudge:
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.base_url = (base_url or os.getenv("LITELLM_BASE_URL") or "https://litellm.kieferwaight.com/v1").rstrip("/")
        self.api_key = api_key or os.getenv("LITELLM_API_KEY") or ""
        self.model = model or os.getenv("AGENT_MODEL") or "gemini-2.5-flash"

    def evaluate(
        self,
        issue_title: str,
        goal: str,
        acceptance_criteria: List[str],
        changed_files: List[str],
        git_diff: str,
        deterministic_test_results: List[Dict[str, Any]],
        repository_conventions: str = "Astro portfolio conventions",
    ) -> QAResult:
        prompt = f"""You are an expert QA Judge evaluating a code/content pull request against issue requirements.

CRITICAL JUDGE REJECTION RULES:
1. Reject ('rework') any changes containing unsupported or accidental deletions of existing content/sources.
2. Reject ('rework') any fabricated claims or evidence not strictly supported by the diff.
3. Reject ('rework') any content that fails to satisfy the issue acceptance criteria.
4. Reject ('rework') changes that technically build/compile but do not satisfy the requested outcome.

Issue Title: {issue_title}
Goal: {goal}

Acceptance Criteria:
{json.dumps(acceptance_criteria, indent=2)}

Changed Files ({len(changed_files)} files):
{json.dumps(changed_files, indent=2)}

Deterministic Test Results:
{json.dumps(deterministic_test_results, indent=2)}

Git Diff:
```diff
{git_diff[:15000]}
```

Repository Conventions:
{repository_conventions}

Respond ONLY with a valid JSON object matching this schema:
{{
  "decision": "approve" | "rework",
  "evidence": {{
    "<criterion_text>": "<verifiable evidence in diff>"
  }},
  "risks": ["<risk or deficiency identified>"],
  "rationale": "<concise reviewer-facing explanation of approval or required rework>"
}}
"""

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an objective QA judge. Return valid JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.0,
        }

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        body_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=body_bytes, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req) as resp:
                res_body = resp.read().decode("utf-8")
                res_data = json.loads(res_body)
                content = res_data["choices"][0]["message"]["content"]
                return self.parse_judge_response(content, acceptance_criteria)
        except Exception as e:
            return QAResult(
                decision="rework",
                evidence={},
                risks=[f"QA Judge execution error: {str(e)}"],
                rationale=f"QA Judge failed to execute or return valid result: {str(e)}",
                raw_response=None,
            )

    @staticmethod
    def parse_judge_response(content: str, acceptance_criteria: List[str]) -> QAResult:
        raw = content
        # Strip markdown code blocks if wrapped in ```json ... ```
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
        if match:
            content = match.group(1)
        else:
            # Find first { and last }
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and end > start:
                content = content[start : end + 1]

        try:
            data = json.loads(content)
            decision = str(data.get("decision", "")).strip().lower()
            if decision not in ("approve", "rework"):
                decision = "rework"

            evidence = data.get("evidence")
            if not isinstance(evidence, dict):
                evidence = {ac: "No evidence provided." for ac in acceptance_criteria}

            risks = data.get("risks")
            if not isinstance(risks, list):
                risks = []

            rationale = str(data.get("rationale", "")).strip() or "QA evaluation complete."

            return QAResult(
                decision=decision,
                evidence=evidence,
                risks=[str(r) for r in risks],
                rationale=rationale,
                raw_response=raw,
            )
        except Exception as e:
            return QAResult(
                decision="rework",
                evidence={},
                risks=[f"Failed to parse QA Judge JSON output: {str(e)}"],
                rationale=f"QA Judge produced invalid JSON output. Response: {raw[:300]}",
                raw_response=raw,
            )
