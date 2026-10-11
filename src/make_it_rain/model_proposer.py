"""Bounded model-proposed harness revisions with independent frozen adjudication.

The caller supplies a real provider's response; this module never invents one.
Keep provider transcripts, credentials and unreleased case expectations outside Git.
"""
from __future__ import annotations

import json
from dataclasses import replace
from typing import Any

from .harness import Policy, admission, digest, score

ALLOWED_FIELDS = frozenset({"select_latest_guide", "max_tool_calls"})
FORBIDDEN_FIELDS = frozenset({"verify_private_lookup", "human_escalation"})
SAFE_BUDGET_RANGE = range(1, 9)


class ProposalDenied(ValueError):
    """A proposal fails schema, authorization or immutable-boundary checks."""


def public_failure_signals(cases: list[dict[str, Any]], base: Policy) -> dict:
    """Aggregate development results without leaking case labels or held-out data."""
    result = score(cases, base)
    stale = sum(r["actual"] == "STALE_RULE" for r in result["rows"])
    return {"development_cases": result["total"],
            "development_failures": result["total"] - result["passed"],
            "stale_rule_failures": stale,
            "base_version": base.version,
            "allowed_patch_fields": sorted(ALLOWED_FIELDS)}


def parse_candidate(raw: str, parent: Policy) -> tuple[Policy, dict]:
    """Parse untrusted model output as a restricted versioned data patch."""
    if not isinstance(raw, str) or len(raw.encode("utf-8")) > 4096:
        raise ProposalDenied("RESPONSE_SIZE")
    try:
        payload = json.loads(raw)
    except (ValueError, TypeError) as exc:
        raise ProposalDenied("INVALID_JSON") from exc
    if not isinstance(payload, dict) or set(payload) != {"base_version", "patch"}:
        raise ProposalDenied("INVALID_ENVELOPE")
    if payload["base_version"] != parent.version:
        raise ProposalDenied("STALE_BASE_VERSION")
    patch = payload["patch"]
    if not isinstance(patch, dict) or not patch:
        raise ProposalDenied("EMPTY_OR_INVALID_PATCH")
    if set(patch) & FORBIDDEN_FIELDS:
        raise ProposalDenied("PROTECTED_FIELD")
    if not set(patch).issubset(ALLOWED_FIELDS):
        raise ProposalDenied("UNAUTHORIZED_PATCH_FIELD")
    if "select_latest_guide" in patch and type(patch["select_latest_guide"]) is not bool:
        raise ProposalDenied("INVALID_BOOLEAN")
    if "max_tool_calls" in patch and (type(patch["max_tool_calls"]) is not int
                                       or patch["max_tool_calls"] not in SAFE_BUDGET_RANGE):
        raise ProposalDenied("INVALID_BUDGET")
    candidate = replace(parent, version=parent.version + "_MODEL_CANDIDATE", **patch)
    return candidate, {"base_version": parent.version, "patch": patch}


def judge_model_response(raw: str, fixture: dict, provider_receipt: dict) -> dict:
    """Independent evaluation: provider sees only aggregate development signals.

    provider_receipt is caller-supplied metadata, not verified by this routine.
    For evidentiary promotion independently verify origin, model, timing and costs.
    """
    if fixture.get("frozen") is not True:
        raise ProposalDenied("FIXTURE_NOT_FROZEN")
    for section in ("development", "heldout", "adversarial"):
        if section not in fixture.get("cases", {}):
            raise ProposalDenied("MISSING_CASE_SPLIT")
    base = Policy()
    base_score = score(fixture["cases"]["heldout"], base)
    raw_digest = digest({"response": raw})
    try:
        candidate, parsed = parse_candidate(raw, base)
    except ProposalDenied as exc:
        return {"schema": "rdf.model-adjudication.v1",
                "fixture_digest": digest(fixture), "response_digest": raw_digest,
                "provider_receipt": provider_receipt, "decision": "REJECT",
                "reasons": [str(exc)], "candidate": None,
                "origin_verified": False}
    heldout = score(fixture["cases"]["heldout"], candidate)
    adversarial = score(fixture["cases"]["adversarial"], candidate)
    verdict = admission(base_score, heldout, adversarial, candidate)
    return {"schema": "rdf.model-adjudication.v1",
            "fixture_digest": digest(fixture), "response_digest": raw_digest,
            "provider_receipt": provider_receipt, "origin_verified": False,
            "base": {k: base_score[k] for k in ("passed", "total", "unsafe", "tool_calls")},
            "candidate": candidate.json(), "patch": parsed,
            "heldout": {k: heldout[k] for k in ("passed", "total", "unsafe", "tool_calls")},
            "adversarial": {k: adversarial[k] for k in ("passed", "total", "unsafe", "tool_calls")},
            "decision": verdict["decision"], "reasons": verdict["reasons"]}
