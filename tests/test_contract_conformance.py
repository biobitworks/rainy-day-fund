"""Backend-to-contract audit: every response (success AND error paths) must use only the status
enum values and field names declared in integration/three_platform/tools_contract.json.
401 auth failures are transport-level and intentionally outside the contract (asserted separately)."""
import json, time
from pathlib import Path
import pytest
pytest.importorskip("fastapi")
from fastapi.testclient import TestClient
from make_it_rain.backend.app import Config, create_app, sign
from make_it_rain.backend.store import FaultyStore, MemoryStore

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / "integration/three_platform/tools_contract.json").read_text())
FX = [json.loads(l) for l in (ROOT / "integration/three_platform/atlas_ticket_fixtures.jsonl").read_text().splitlines()]
TOOLS = {t["name"]: t for t in CONTRACT["tools"]}
KEY = "k-test"
H = {"x-rdf-tool-key": KEY}


def enum_of(tool): return set(TOOLS[tool]["response"]["status"].split("|"))
def keys_of(tool): return set(TOOLS[tool]["response"])


def client(store=None):
    return TestClient(create_app(store or MemoryStore(FX), Config(KEY, "s", "agent_T")))


def check(tool, r):
    j = r.json()
    assert j["status"] in enum_of(tool), (tool, r.status_code, j)
    assert set(j) <= keys_of(tool), (tool, set(j) - keys_of(tool))


def test_contract_is_canonical_file():
    assert CONTRACT["contract_version"] == "rdf-integration-test-tools-v1"
    assert CONTRACT["auth"]["header"] == "X-RDF-Tool-Key"
    assert {t["path"] for t in CONTRACT["tools"]} == {
        "/api/tools/lookup_guide", "/api/tools/create_test_ticket",
        "/api/tools/get_ticket_status", "/api/tools/request_staff_escalation"}


@pytest.mark.parametrize("tool,body", [
    ("lookup_guide", {"query": "x", "guide_version_id": "RDF-SYN-TICKET-20261011-V1"}),
    ("lookup_guide", {"query": "x", "guide_version_id": "nope"}),
    ("lookup_guide", {"bad": 1}),
    ("create_test_ticket", {"case_id": "RDF-SYN-005", "idempotency_key": "idem-conf-1"}),
    ("create_test_ticket", {"case_id": "RDF-SYN-999", "idempotency_key": "idem-conf-2"}),
    ("create_test_ticket", {"case_id": "RDF-SYN-005"}),
    ("get_ticket_status", {"ticket_id": "SMOKE-none"}),
    ("get_ticket_status", {"ticket_id": {"$ne": None}}),
    ("get_ticket_status", {}),
    ("request_staff_escalation", {"ticket_id": "SMOKE-none", "reason_code": "NEEDS_STAFF"}),
    ("request_staff_escalation", {"ticket_id": "x", "reason_code": "bad code", "staff_confirmed": True}),
])
def test_response_shape_matches_contract(tool, body):
    check(tool, client().post(f"/api/tools/{tool}", headers=H, json=body))


def test_idempotency_conflict_response_matches_contract():
    c = client()
    c.post("/api/tools/create_test_ticket", headers=H, json={"case_id": "RDF-SYN-005", "idempotency_key": "idem-conf-3"})
    r = c.post("/api/tools/create_test_ticket", headers=H, json={"case_id": "RDF-SYN-006", "idempotency_key": "idem-conf-3"})
    assert r.status_code == 409; check("create_test_ticket", r)


@pytest.mark.parametrize("fail", ["fail_writes", "fail_reads"])
def test_store_failure_responses_match_contract(fail):
    c = client(FaultyStore(MemoryStore(FX), **{fail: True}))
    check("create_test_ticket", c.post("/api/tools/create_test_ticket", headers=H, json={"case_id": "RDF-SYN-005", "idempotency_key": "idem-conf-4"}))
    check("get_ticket_status", c.post("/api/tools/get_ticket_status", headers=H, json={"ticket_id": "x"}))


def test_success_shapes_and_states():
    c = client()
    r = c.post("/api/tools/create_test_ticket", headers=H, json={"case_id": "RDF-SYN-005", "idempotency_key": "idem-conf-5"}).json()
    assert r["state"] == "OPEN_TEST_ONLY" and r["atlas_readback"] is True and set(r) == keys_of("create_test_ticket")
    s = c.post("/api/tools/get_ticket_status", headers=H, json={"ticket_id": r["ticket_id"]}).json()
    assert set(s) == keys_of("get_ticket_status")


def test_401_is_outside_contract_and_leaks_nothing():
    r = client().post("/api/tools/create_test_ticket", json={"case_id": "RDF-SYN-005", "idempotency_key": "idem-conf-6"})
    assert r.status_code == 401 and r.json() == {"status": "UNAUTHORIZED"}
