import json, os, subprocess, sys, time
from pathlib import Path
import pytest
pytest.importorskip("fastapi"); pytest.importorskip("httpx")
from fastapi.testclient import TestClient
from make_it_rain.backend.app import Config, create_app, sign
from make_it_rain.backend.store import FaultyStore, FileStore, MemoryStore, TICKETS, EVENTS, WEBHOOKS, PARKED

ROOT = Path(__file__).resolve().parents[1]
FX = [json.loads(l) for l in (ROOT / "integration/three_platform/atlas_ticket_fixtures.jsonl").read_text().splitlines()]
KEY, SECRET, AGENT = "test-tool-key", "test-webhook-secret", "agent_TEST"
H = {"x-rdf-tool-key": KEY}


def mk(store=None, traces=None, now=None):
    store = store or MemoryStore(FX)
    cfg = Config(KEY, SECRET, AGENT, telemetry=(traces.append if traces is not None else (lambda r: None)),
                 clock=(lambda: now) if now else time.time)
    return store, TestClient(create_app(store, cfg))


def hook(conv="conv_1", case="RDF-SYN-005", agent=AGENT, synthetic=True, ts=None):
    body = {"type": "post_call_transcription", "event_timestamp": 1, "data": {
        "conversation_id": conv, "agent_id": agent, "transcript": [{"message": "SECRET TRANSCRIPT"}],
        "conversation_initiation_client_data": {"dynamic_variables": {"rdf_case_id": case, "rdf_synthetic": synthetic}}}}
    raw = json.dumps(body).encode()
    return raw, {"elevenlabs-signature": sign(SECRET, raw, ts or int(time.time()))}


def test_fixtures_are_the_12_frozen():
    assert len(FX) == 12 and {f["_id"] for f in FX} == {f"RDF-SYN-{i:03d}" for i in range(1, 13)}


def test_tool_auth_required():
    _, c = mk()
    assert c.post("/api/tools/create_test_ticket", json={"case_id": "RDF-SYN-005", "idempotency_key": "k" * 8}).status_code == 401
    assert c.post("/api/tools/create_test_ticket", headers={"x-rdf-tool-key": "x"}, json={}).status_code == 401


def test_create_idempotent_one_ticket_and_frozen_untouched():
    s, c = mk(); before = json.dumps(s.data["ticket_fixtures"], sort_keys=True)
    b = {"case_id": "RDF-SYN-005", "idempotency_key": "idem-0001", "conversation_id": "conv_1"}
    r1 = c.post("/api/tools/create_test_ticket", headers=H, json=b).json()
    r2 = c.post("/api/tools/create_test_ticket", headers=H, json=b).json()
    assert r1["status"] == r2["status"] == "SUCCEEDED" and r1["atlas_readback"] and r1["ticket_id"] == r2["ticket_id"]
    assert s.count(TICKETS) == 1 and s.count(EVENTS) == 1
    assert json.dumps(s.data["ticket_fixtures"], sort_keys=True) == before


def test_idempotency_key_reuse_with_other_case_conflicts():
    s, c = mk()
    c.post("/api/tools/create_test_ticket", headers=H, json={"case_id": "RDF-SYN-005", "idempotency_key": "idem-0001"})
    r = c.post("/api/tools/create_test_ticket", headers=H, json={"case_id": "RDF-SYN-006", "idempotency_key": "idem-0001"})
    assert r.status_code == 409 and r.json()["status"] == "REJECTED" and s.count(TICKETS) == 1


def test_unknown_case_rejected():
    s, c = mk()
    r = c.post("/api/tools/create_test_ticket", headers=H, json={"case_id": "RDF-SYN-099", "idempotency_key": "idem-0002"})
    assert r.status_code == 422 and s.count(TICKETS) == 0


def test_status_is_live_not_echo():
    s, c = mk()
    assert c.post("/api/tools/get_ticket_status", headers=H, json={"ticket_id": "SMOKE-fake"}).json()["status"] == "NOT_FOUND"
    t = c.post("/api/tools/create_test_ticket", headers=H, json={"case_id": "RDF-SYN-005", "idempotency_key": "idem-0003"}).json()["ticket_id"]
    assert c.post("/api/tools/get_ticket_status", headers=H, json={"ticket_id": t}).json()["state"] == "OPEN_TEST_ONLY"


def test_escalation_is_request_only_and_staff_fields_rejected():
    s, c = mk()
    t = c.post("/api/tools/create_test_ticket", headers=H, json={"case_id": "RDF-SYN-005", "idempotency_key": "idem-0004"}).json()["ticket_id"]
    r = c.post("/api/tools/request_staff_escalation", headers=H, json={"ticket_id": t, "reason_code": "NEEDS_STAFF"}).json()
    assert r == {"status": "PENDING", "staff_confirmed": False}
    forged = c.post("/api/tools/request_staff_escalation", headers=H, json={"ticket_id": t, "reason_code": "X_Y", "staff_confirmed": True, "close": True})
    assert forged.status_code == 422
    assert s.get(TICKETS, t)["state"] == "ESCALATION_REQUESTED"
    assert c.post("/api/tools/request_staff_escalation", headers={"x-rdf-tool-key": "nope"}, json={"ticket_id": t, "reason_code": "AAA"}).status_code == 401


def test_atlas_write_failure_reports_failed_not_success():
    s, c = mk(FaultyStore(MemoryStore(FX), fail_writes=True))
    r = c.post("/api/tools/create_test_ticket", headers=H, json={"case_id": "RDF-SYN-005", "idempotency_key": "idem-0005"})
    assert r.status_code == 503 and r.json()["status"] == "FAILED" and r.json()["atlas_readback"] is False


def test_atlas_read_failure_status_failed():
    s, c = mk(FaultyStore(MemoryStore(FX), fail_reads=True))
    assert c.post("/api/tools/get_ticket_status", headers=H, json={"ticket_id": "x"}).status_code == 503


def test_webhook_rejects_unsigned_bad_and_stale():
    s, c = mk()
    raw, h = hook()
    assert c.post("/api/webhooks/elevenlabs", content=raw).status_code == 401
    assert c.post("/api/webhooks/elevenlabs", content=raw, headers={"elevenlabs-signature": "t=1,v0=deadbeef"}).status_code == 401
    assert c.post("/api/webhooks/elevenlabs", content=raw + b" ", headers=h).status_code == 401  # body tampered
    raw2, h2 = hook(ts=int(time.time()) - 7200)
    assert c.post("/api/webhooks/elevenlabs", content=raw2, headers=h2).status_code == 401
    assert s.count(WEBHOOKS) == 0 and s.count(PARKED) == 0


def test_webhook_stores_metadata_only_and_is_duplicate_safe():
    s, c = mk(); raw, h = hook()
    r1 = c.post("/api/webhooks/elevenlabs", content=raw, headers=h).json()
    r2 = c.post("/api/webhooks/elevenlabs", content=raw, headers=h).json()
    assert r1["status"] == "STORED" and r2["status"] == "DUPLICATE_IGNORED" and s.count(WEBHOOKS) == 1
    assert "SECRET TRANSCRIPT" not in json.dumps(s.data)
    assert s.get(WEBHOOKS, r1["webhook_record_id"])["conversation_id"] == "conv_1"


def test_webhook_parks_nonsynthetic_or_wrong_agent():
    s, c = mk()
    for kw in ({"synthetic": False}, {"agent": "agent_OTHER"}, {"case": "RDF-SYN-999"}):
        raw, h = hook(conv="c" + str(kw), **kw)
        assert c.post("/api/webhooks/elevenlabs", content=raw, headers=h).json()["status"] == "PARKED"
    assert s.count(WEBHOOKS) == 0 and s.count(PARKED) == 3


def test_webhook_store_failure_is_not_200():
    s, c = mk(FaultyStore(MemoryStore(FX), fail_writes=True)); raw, h = hook()
    assert c.post("/api/webhooks/elevenlabs", content=raw, headers=h).status_code == 503


def test_telemetry_sanitized_and_failure_isolated():
    tr = []; s, c = mk(traces=tr)
    c.post("/api/tools/create_test_ticket", headers=H, json={"case_id": "RDF-SYN-005", "idempotency_key": "idem-0006", "conversation_id": "conv_1"})
    assert tr and tr[0]["tool"] == "create_test_ticket" and tr[0]["conversation_id"] == "conv_1" and KEY not in json.dumps(tr)
    cfg = Config(KEY, SECRET, AGENT, telemetry=lambda r: 1 / 0)
    c2 = TestClient(create_app(MemoryStore(FX), cfg))
    assert c2.post("/api/tools/create_test_ticket", headers=H, json={"case_id": "RDF-SYN-005", "idempotency_key": "idem-0007"}).json()["status"] == "SUCCEEDED"


def test_restart_fresh_process_reads_same_state(tmp_path):
    p = tmp_path / "state.json"
    _, c = mk(FileStore(p, FX))
    t = c.post("/api/tools/create_test_ticket", headers=H, json={"case_id": "RDF-SYN-005", "idempotency_key": "idem-0008"}).json()["ticket_id"]
    code = ("import sys,json;from make_it_rain.backend.store import FileStore;"
            "import os;print(os.getpid(), json.dumps(FileStore(sys.argv[1]).get('integration_smoke_tickets',sys.argv[2]), sort_keys=True))")
    out = subprocess.run([sys.executable, "-c", code, str(p), t], capture_output=True, text=True,
                         env={**os.environ, "PYTHONPATH": str(ROOT / "src")}).stdout.split(" ", 1)
    assert int(out[0]) != os.getpid() and json.loads(out[1])["state"] == "OPEN_TEST_ONLY"
