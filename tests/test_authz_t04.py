"""T04 remediation: session-scoped authorization, honest readback labels, synthetic-only export gate, SDK HMAC parity."""
import json, time
from pathlib import Path
import pytest
pytest.importorskip("fastapi")
from fastapi.testclient import TestClient
from make_it_rain.backend.app import Config, create_app, sign, issue_session_token, verify_session_token
from make_it_rain.backend.store import MemoryStore, TICKETS, EVENTS

ROOT = Path(__file__).resolve().parents[1]
FX = [json.loads(l) for l in (ROOT / "integration/three_platform/atlas_ticket_fixtures.jsonl").read_text().splitlines()]
KEY, WH, SS = "tk-1", "wh-secret-1", "session-secret-1"
FAR = 4102444800


def tok(sid, exp_base=0, secret=SS): return issue_session_token(secret, sid, FAR, exp_base)
def hdr(sid): return {"x-rdf-tool-key": KEY, "x-rdf-session": tok(sid)}


class FakeAtlasStore(MemoryStore):
    kind = "ATLAS"  # label only; exercises the true-flag path without a network


def mk(store=None):
    s = store or MemoryStore(FX); return s, TestClient(create_app(s, Config(KEY, WH, "agent_T", session_secret=SS)))


def create(c, sid, idem="idem-t04-0001", case="RDF-SYN-005"):
    return c.post("/api/tools/create_test_ticket", headers=hdr(sid), json={"case_id": case, "idempotency_key": idem})


def test_unscoped_service_key_alone_cannot_read_or_escalate_or_create():
    s, c = mk(); t = create(c, "SESSIONAAAA1").json()["ticket_id"]
    only_key = {"x-rdf-tool-key": KEY}
    assert c.post("/api/tools/get_ticket_status", headers=only_key, json={"ticket_id": t}).status_code == 401
    assert c.post("/api/tools/request_staff_escalation", headers=only_key, json={"ticket_id": t, "reason_code": "NEEDS_STAFF"}).status_code == 401
    assert c.post("/api/tools/create_test_ticket", headers=only_key, json={"case_id": "RDF-SYN-005", "idempotency_key": "idem-t04-0002"}).status_code == 401
    assert s.get(TICKETS, t)["state"] == "OPEN_TEST_ONLY"


def test_cross_session_read_and_escalation_denied_without_existence_oracle():
    s, c = mk(); t = create(c, "SESSIONAAAA1").json()["ticket_id"]
    other = hdr("SESSIONBBBB2")
    missing = c.post("/api/tools/get_ticket_status", headers=other, json={"ticket_id": "SMOKE-doesnotexist"}).json()
    foreign = c.post("/api/tools/get_ticket_status", headers=other, json={"ticket_id": t}).json()
    assert foreign == missing and foreign["status"] == "NOT_FOUND"
    e1 = c.post("/api/tools/request_staff_escalation", headers=other, json={"ticket_id": t, "reason_code": "NEEDS_STAFF"})
    e2 = c.post("/api/tools/request_staff_escalation", headers=other, json={"ticket_id": "SMOKE-nope", "reason_code": "NEEDS_STAFF"})
    assert (e1.status_code, e1.json()) == (e2.status_code, e2.json()) == (404, {"status": "REJECTED", "staff_confirmed": False})
    assert s.get(TICKETS, t)["state"] == "OPEN_TEST_ONLY" and s.count(EVENTS) == 1
    assert c.post("/api/tools/get_ticket_status", headers=hdr("SESSIONAAAA1"), json={"ticket_id": t}).json()["status"] == "SUCCEEDED"


def test_same_idempotency_key_in_two_sessions_makes_two_isolated_tickets():
    s, c = mk()
    a = create(c, "SESSIONAAAA1").json()["ticket_id"]; b = create(c, "SESSIONBBBB2").json()["ticket_id"]
    assert a != b and s.count(TICKETS) == 2


def test_forged_expired_tampered_and_wrong_secret_tokens_rejected():
    s, c = mk()
    good = tok("SESSIONAAAA1", exp_base=time.time()); sid, exp, mac = good.rsplit(".", 2)
    bad = [f"SESSIONBBBB2.{exp}.{mac}", f"{sid}.{int(exp)+1}.{mac}", tok("SESSIONAAAA1", secret="other-secret"),
           issue_session_token(SS, "SESSIONAAAA1", -10, time.time()), "garbage", "", "a.b.c", "../x.9999999999.00"]
    for t in bad:
        r = c.post("/api/tools/create_test_ticket", headers={"x-rdf-tool-key": KEY, "x-rdf-session": t},
                   json={"case_id": "RDF-SYN-005", "idempotency_key": "idem-t04-0003"})
        assert r.status_code == 401, t
    assert s.count(TICKETS) == 0


def test_llm_supplied_session_id_in_body_or_header_is_not_authorization():
    s, c = mk()
    r = c.post("/api/tools/create_test_ticket", headers={"x-rdf-tool-key": KEY, "x-rdf-session": "SESSIONAAAA1"},
               json={"case_id": "RDF-SYN-005", "idempotency_key": "idem-t04-0004"})
    assert r.status_code == 401
    r = c.post("/api/tools/create_test_ticket", headers=hdr("SESSIONAAAA1"), json={"case_id": "RDF-SYN-005", "idempotency_key": "idem-t04-0004", "session_id": "SESSIONBBBB2"})
    assert r.status_code == 422  # extra fields forbidden


def test_adversarial_case_ids_rejected_and_fixtures_not_ticket_ids():
    s, c = mk()
    for case in ("RDF-SYN-013", "rdf-syn-005", "RDF-SYN-005 ", "../RDF-SYN-005", "RDF-SYN-005\n"):
        assert create(c, "SESSIONAAAA1", case=case).status_code == 422, case
    assert c.post("/api/tools/get_ticket_status", headers=hdr("SESSIONAAAA1"), json={"ticket_id": "RDF-SYN-005"}).json()["status"] == "NOT_FOUND"


def test_replay_same_request_same_session_is_idempotent():
    s, c = mk(); a = create(c, "SESSIONAAAA1").json(); b = create(c, "SESSIONAAAA1").json()
    assert a == b and s.count(TICKETS) == 1


def test_session_secret_must_be_distinct_and_unset_fails_closed():
    with pytest.raises(ValueError):
        create_app(MemoryStore(FX), Config(KEY, WH, "a", session_secret=KEY))
    with pytest.raises(ValueError):
        create_app(MemoryStore(FX), Config(KEY, WH, "a", session_secret=WH))
    c = TestClient(create_app(MemoryStore(FX), Config(KEY, WH, "a")))  # no session secret
    assert c.post("/api/tools/create_test_ticket", headers=hdr("SESSIONAAAA1"), json={"case_id": "RDF-SYN-005", "idempotency_key": "idem-t04-0005"}).status_code == 401
    assert verify_session_token("", tok("SESSIONAAAA1", secret=""), 0) is None


def test_issue_session_requires_tool_key_and_yields_usable_distinct_tokens():
    s, c = mk()
    assert c.post("/api/sessions").status_code == 401
    a = c.post("/api/sessions", headers={"x-rdf-tool-key": KEY}).json(); b = c.post("/api/sessions", headers={"x-rdf-tool-key": KEY}).json()
    assert a["session_id"] != b["session_id"]
    r = c.post("/api/tools/create_test_ticket", headers={"x-rdf-tool-key": KEY, "x-rdf-session": a["session_token"]}, json={"case_id": "RDF-SYN-005", "idempotency_key": "idem-t04-0006"})
    assert r.json()["status"] == "SUCCEEDED"


def test_local_stores_never_claim_atlas_readback_and_atlas_kind_may():
    s, c = mk(); r = create(c, "SESSIONAAAA1")
    assert r.json()["atlas_readback"] is False and r.headers["x-rdf-readback-source"] == "LOCAL_MEMORY_NOT_ATLAS"
    t = r.json()["ticket_id"]; g = c.post("/api/tools/get_ticket_status", headers=hdr("SESSIONAAAA1"), json={"ticket_id": t})
    assert g.json()["atlas_readback"] is False and s.get(TICKETS, t)["readback_source"] == "LOCAL_MEMORY_NOT_ATLAS"
    _, c2 = mk(FakeAtlasStore(FX)); r2 = create(c2, "SESSIONAAAA1")
    assert r2.json()["atlas_readback"] is True and r2.headers["x-rdf-readback-source"] == "ATLAS"


# ---- Raindrop export gate (no SDK import happens before admission) ----
from make_it_rain.backend import telemetry as T


@pytest.mark.parametrize("cls,case,msg", [
    ("UNKNOWN", "RDF-SYN-005", "My microphone is muted for the talk. Can you help?"),
    ("", "RDF-SYN-005", "My microphone is muted for the talk. Can you help?"),
    ("PUBLIC", "RDF-SYN-005", "My microphone is muted for the talk. Can you help?"),
    ("SYNTHETIC_ONLY", "RDF-SYN-005", "Hi I'm Jane Doe, call me at 555-0100"),
    ("SYNTHETIC_ONLY", "RDF-SYN-999", "My microphone is muted for the talk. Can you help?"),
    ("SYNTHETIC_ONLY", "RDF-SYN-010", "My microphone is muted for the talk. Can you help?"),
])
def test_raindrop_export_default_deny(monkeypatch, cls, case, msg):
    import sys
    monkeypatch.setitem(sys.modules, "raindrop.analytics", None)  # any SDK import would raise ImportError, not ExportDenied
    with pytest.raises(T.ExportDenied):
        T.RaindropCase("k", case, "conv-1", msg, privacy_class=cls)


def test_raindrop_export_admits_only_frozen_synthetic_text(monkeypatch):
    import sys, types
    calls = {}
    fake = types.SimpleNamespace(init=lambda **k: calls.setdefault("init", k), set_redact_pii=lambda v: None,
                                 begin=lambda **k: calls.setdefault("begin", k) and types.SimpleNamespace(), INTERACTION_TRACE_ID_REGISTRY={})
    monkeypatch.setitem(sys.modules, "raindrop", types.SimpleNamespace(analytics=fake)); monkeypatch.setitem(sys.modules, "raindrop.analytics", fake)
    T.RaindropCase("k", "RDF-SYN-005", "conv-1", "SYNTHETIC: My microphone is muted for the talk. Can you help?", privacy_class="SYNTHETIC_ONLY")
    assert calls["begin"]["input"].endswith("Can you help?") and calls["begin"]["properties"]["synthetic"] is True


# ---- ElevenLabs SDK parity for the signed webhook ----
def test_hmac_matches_elevenlabs_sdk_construct_event():
    el = pytest.importorskip("elevenlabs.client"); w = el.ElevenLabs(api_key="x").webhooks
    raw = json.dumps({"type": "post_call_transcription", "data": {"conversation_id": "c"}}).encode()
    ts = int(time.time()); good = sign(WH, raw, ts)
    assert w.construct_event(raw.decode(), good, WH)["type"] == "post_call_transcription"
    from make_it_rain.backend.app import verify_signature
    assert verify_signature(WH, good, raw, time.time())
    for bad_raw, bad_sig, secret in [(raw + b" ", good, WH), (raw, good, "wrong"), (raw, sign(WH, raw, ts - 7200), WH), (raw, "t=1,v0=00", WH)]:
        with pytest.raises(Exception):
            w.construct_event(bad_raw.decode(), bad_sig, secret)
        assert not verify_signature(secret, bad_sig, bad_raw, time.time())
