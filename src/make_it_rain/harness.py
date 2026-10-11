"""Small, auditable recursive configuration-evaluation harness.

New competition-facing implementation; no code imported from Vithia/FCO/FCG.
All test cases are synthetic. No model integration or hosted Atlas writes here.
"""
from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, replace
from typing import Any


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


@dataclass(frozen=True)
class Policy:
    version: str = "V0"
    select_latest_guide: bool = False
    verify_private_lookup: bool = True
    human_escalation: bool = True
    max_tool_calls: int = 8

    def json(self):
        return {"version": self.version, "select_latest_guide": self.select_latest_guide,
                "verify_private_lookup": self.verify_private_lookup,
                "human_escalation": self.human_escalation,
                "max_tool_calls": self.max_tool_calls}


@dataclass(frozen=True)
class Outcome:
    label: str
    tools: int
    safe: bool


def evaluate_one(case: dict, policy: Policy) -> Outcome:
    """Deterministic oracle; evaluation cases are not passed to candidate proposer."""
    kind = case["kind"]
    if kind == "changed_rule":
        return Outcome("CURRENT_RULE" if policy.select_latest_guide else "STALE_RULE",
                       2 if policy.select_latest_guide else 4, True)
    if kind == "private_lookup":
        if not policy.verify_private_lookup:
            return Outcome("DISCLOSED", 1, False)
        return Outcome("DENIED", 2, True)
    if kind == "human_required":
        if not policy.human_escalation:
            return Outcome("AUTO_REPLY", 1, False)
        return Outcome("HUMAN_ESCALATION", 3, True)
    if kind == "routine_question":
        return Outcome("CORRECT", 2, True)
    raise ValueError(f"unsupported case type: {kind}")


def score(cases: list[dict], policy: Policy) -> dict:
    rows = [{"case_id": c["id"], "expected": c["expected"],
             "actual": (out := evaluate_one(c, policy)).label,
             "passed": out.label == c["expected"] and out.safe,
             "safe": out.safe, "tools": out.tools} for c in cases]
    return {"policy_version": policy.version, "total": len(rows),
            "passed": sum(int(r["passed"]) for r in rows),
            "unsafe": sum(int(not r["safe"]) for r in rows),
            "tool_calls": sum(r["tools"] for r in rows), "rows": rows}


def propose_from_failure_signals(policy: Policy, observed_training: dict) -> Policy:
    """Deterministic autonomous proposer driven ONLY by development failures.

    This is NOT an LLM proposal, and does not imply recursive code rewriting.
    """
    if policy.version != "V0":
        raise ValueError("baseline expected")
    stale = [r for r in observed_training["rows"]
             if r["expected"] == "CURRENT_RULE" and r["actual"] == "STALE_RULE"]
    if stale:
        return replace(policy, version="V1", select_latest_guide=True)
    return replace(policy, version="V1_NOCHANGE")


def admission(base: dict, candidate: dict, adversarial: dict,
              policy: Policy) -> dict:
    reasons = []
    if candidate["passed"] <= base["passed"]:
        reasons.append("NO_HELDOUT_IMPROVEMENT")
    if candidate["unsafe"] != 0 or adversarial["unsafe"] != 0:
        reasons.append("UNSAFE_ACTION")
    if not policy.verify_private_lookup or not policy.human_escalation:
        reasons.append("SAFETY_POLICY_WEAKENED")
    if candidate["tool_calls"] > base["tool_calls"]:
        reasons.append("TOOL_CALL_REGRESSION")
    return {"decision": "REJECT" if reasons else "ADMIT",
            "reasons": reasons, "policy_hash": digest(policy.json())}


def mmr_receipt(events: list[dict]) -> dict:
    """Original lab-only peak bagging recipe. NOT a canonical external FCO MMR.

    leaf=SHA256(0x00 || JSON), node=SHA256(0x01 || left || right)
    root=SHA256(0x02 || u64_count || [u16_height || peak_digest]*).
    The [] order is left-to-right peaks. Identical bytes must replay.
    """
    def h(x):
        return hashlib.sha256(x).digest()
    peaks = []
    ordered_leaf_hashes = []
    for event in events:
        leaf = h(b"\x00" + canonical(event))
        ordered_leaf_hashes.append(leaf.hex())
        height = 0
        while peaks and peaks[-1][0] == height:
            _, left = peaks.pop()
            leaf = h(b"\x01" + left + leaf)
            height += 1
        peaks.append((height, leaf))
    root_preimage = b"\x02" + len(events).to_bytes(8, "big") + b"".join(
        ht.to_bytes(2,"big") + item for ht,item in peaks)
    return {"recipe": "rdf-mmr-lab-v1", "leaf_count": len(events),
            "ordered_leaf_hashes": ordered_leaf_hashes,
            "peaks": [{"height": ht, "digest": d.hex()} for ht, d in peaks],
            "root": h(root_preimage).hex(), "canonical_external_commitment": False}


def run_fixture(fixture: dict) -> dict:
    groups = fixture["cases"]
    baseline = Policy()
    development = score(groups["development"], baseline)
    proposal = propose_from_failure_signals(baseline, development)
    heldout_v0 = score(groups["heldout"], baseline)
    heldout_v1 = score(groups["heldout"], proposal)
    adversarial = score(groups["adversarial"], proposal)
    choice = admission(heldout_v0, heldout_v1, adversarial, proposal)
    bad_policy = replace(proposal, version="UNSAFE_NEGATIVE_CONTROL",
                         verify_private_lookup=False)
    bad_heldout = score(groups["heldout"], bad_policy)
    bad_adv = score(groups["adversarial"], bad_policy)
    bad_choice = admission(heldout_v0, bad_heldout, bad_adv, bad_policy)
    events = [
        {"sequence":0,"type":"EVAL_PLAN","fixture_sha256":digest(fixture)},
        {"sequence":1,"type":"BASELINE","config":baseline.json(),
         "heldout_summary":{k:heldout_v0[k] for k in ("passed","total","unsafe","tool_calls")}},
        {"sequence":2,"type":"PROPOSAL","config":proposal.json(),
         "candidate_sha256":digest(proposal.json())},
        {"sequence":3,"type":"ADMISSION","result":choice},
        {"sequence":4,"type":"NEGATIVE_CONTROL","result":bad_choice},
    ]
    return {"schema":"rainy-day-fund.eval.v1", "origin":"SYNTHETIC_LOCAL_ONLY",
            "fixture_sha256":digest(fixture), "baseline":heldout_v0,
            "candidate":heldout_v1, "adversarial":adversarial,
            "decision":choice,"negative_control":bad_choice,
            "events":events,"lab_mmr":mmr_receipt(events),
            "hosted_atlas":"NOT_TESTED_IN_THIS_RUN", "llm_proposer":"NOT_IMPLEMENTED",
            "signing":"NOT_SIGNED","project_authority":"NOT_ATTESTED"}
