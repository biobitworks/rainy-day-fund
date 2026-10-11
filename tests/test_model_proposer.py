"""These are transport-independent, synthetic model-response boundary tests."""
import json
import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from make_it_rain.harness import Policy
from make_it_rain.model_proposer import (
    ProposalDenied, judge_model_response, parse_candidate, public_failure_signals
)
FIXTURE = json.loads((Path(__file__).resolve().parents[1] / "benchmarks/frozen_cases.json").read_text())
META = {"provider": "MOCK_ONLY", "model": "fixture", "request_verified": False}

def wrapped(patch, base_version="V0"):
    return json.dumps({"base_version": base_version, "patch": patch})

def test_safe_candidate_admitted_against_frozen_heldout():
    record = judge_model_response(wrapped({"select_latest_guide": True}), FIXTURE, META)
    assert record["decision"] == "ADMIT"
    assert record["heldout"]["passed"] > record["base"]["passed"]
    assert record["origin_verified"] is False
    assert record["candidate"]["verify_private_lookup"]

@pytest.mark.parametrize("patch, reason", [
    ({"verify_private_lookup": False}, "PROTECTED_FIELD"),
    ({"human_escalation": False}, "PROTECTED_FIELD"),
    ({"version": "V2"}, "UNAUTHORIZED_PATCH_FIELD"),
    ({"max_tool_calls": 300}, "INVALID_BUDGET"),
    ({"select_latest_guide": 1}, "INVALID_BOOLEAN"),
    ({"max_tool_calls": True}, "INVALID_BUDGET"),
])
def test_reject_unauthorized_model_patch(patch, reason):
    result = judge_model_response(wrapped(patch), FIXTURE, META)
    assert result["decision"] == "REJECT"
    assert reason in result["reasons"]

def test_reject_stale_and_malformed():
    with pytest.raises(ProposalDenied, match="STALE_BASE_VERSION"):
        parse_candidate(wrapped({"select_latest_guide": True}, "OLD"), Policy())
    assert judge_model_response("not JSON", FIXTURE, META)["decision"] == "REJECT"

def test_no_improvement_is_rejected():
    result = judge_model_response(wrapped({"max_tool_calls": 7}), FIXTURE, META)
    assert result["decision"] == "REJECT"
    assert "NO_HELDOUT_IMPROVEMENT" in result["reasons"]

def test_require_frozen_fixture():
    with pytest.raises(ProposalDenied, match="FIXTURE_NOT_FROZEN"):
        judge_model_response(wrapped({"select_latest_guide": True}), {**FIXTURE, "frozen": False}, META)

def test_no_heldout_exposure_in_public_signals():
    response = public_failure_signals(FIXTURE["cases"]["development"], Policy())
    assert set(response) == {"development_cases","development_failures",
                              "stale_rule_failures","base_version","allowed_patch_fields"}
    assert not any(case["id"] in str(response) for case in FIXTURE["cases"]["heldout"])
