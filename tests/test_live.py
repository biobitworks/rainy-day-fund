import json, time
import pytest
from fastapi.testclient import TestClient
from make_it_rain.backend.app import sign
from make_it_rain.backend.live import LiveConfig, create_live_app
from make_it_rain.backend.store import FaultyStore, MemoryStore, UnconfiguredStore

TK, VK, OK_, WS, AG = "tool-key-xxxxxxxx", "viewer-key-xxxxxxx", "operator-key-xxxxxx", "whsec-test-secret", "agent_test"
CONV = "conv_test_0001abcd"
T, V, O = {"x-rdf-tool-key": TK}, {"x-rdf-viewer-key": VK}, {"x-rdf-operator-key": OK_}


def mk(store=None, raindrop=None):
    calls = []
    def rd(ctx): calls.append(ctx); return {"status": "SDK_FLUSH_CALLED", "sdk_trace_id": "trace-local-1", "cloud_readback": "NOT_TESTED"}
    cfg = LiveConfig(tool_key=TK, viewer_key=VK, operator_key=OK_, webhook_secret=WS, agent_id=AG, raindrop=rd if raindrop is None else raindrop)
    return TestClient(create_live_app(store or MemoryStore(), cfg)), calls


def create(c, key="idem-key-0001", conv=CONV, **kw):
    b = {"idempotency_key": key, "summary": "SYNTHETIC: wifi fails on test badge", "channel": "text", "conversation_id": conv, **kw}
    return c.post("/api/tools/create-ticket", json=b, headers=T)


def upd(c, tid, action, key, conv=CONV):
    return c.post("/api/tools/update-ticket", json={"idempotency_key": key, "ticket_id": tid, "action": action, "conversation_id": conv}, headers=T)


def hook(c, conv=CONV, agent=AG, synthetic=True, ts=None, extra=None):
    body = {"type": "post_call_transcription", "event_timestamp": 1, "data": {"conversation_id": conv, "agent_id": agent,
            "transcript": [{"role": "user", "message": "SYNTHETIC: help"}, {"role": "agent", "message": "ok"}],
            "conversation_initiation_client_data": {"dynamic_variables": {"rdf_synthetic": synthetic}}, **(extra or {})}}
    raw = json.dumps(body).encode()
    return c.post("/api/webhooks/elevenlabs", content=raw, headers={"elevenlabs-signature": sign(WS, raw, ts or int(time.time()))})


def test_health_public_no_secrets():
    c, _ = mk(); r = c.get("/api/health"); assert r.status_code == 200
    assert TK not in r.text and WS not in r.text and r.json()["configured"]["atlas"] is False


@pytest.mark.parametrize("path,m", [("/api/tickets", "get"), ("/api/events", "get")])
def test_viewer_auth_and_nostore(path, m):
    c, _ = mk(); assert c.get(path).status_code == 401 and c.get(path, headers={"x-rdf-viewer-key": "bad"}).status_code == 401
    r = c.get(path, headers=V); assert r.status_code == 200 and "no-store" in r.headers["cache-control"]


def test_tools_require_key():
    c, _ = mk(); assert c.post("/api/tools/create-ticket", json={}).status_code == 401
    assert c.post("/api/tools/create-ticket", json={}, headers={"x-rdf-tool-key": VK}).status_code == 401  # viewer key is not a tool key


def test_create_readback_idempotent_and_conflict():
    s = MemoryStore(); c, _ = mk(s)
    r = create(c); assert r.status_code == 200 and r.json()["status"] == "SUCCEEDED" and r.json()["atlas_readback"] is False
    tid = r.json()["ticket_id"]; r2 = create(c); assert r2.json()["ticket_id"] == tid and r2.json()["replayed"] is True
    assert s.count("live_tickets") == 1
    assert create(c, summary="SYNTHETIC: a different payload entirely").status_code == 409
    assert s.count("live_tickets") == 1
    assert c.get("/api/tickets", headers=V).json()["tickets"][0]["ticket_id"] == tid


def test_non_synthetic_and_extra_fields_rejected():
    c, _ = mk(); assert create(c, summary="my real name is Jane and my phone is 555").status_code == 422
    assert create(c, key="idem-key-0002", staff_confirmed=True).status_code == 422
    assert create(c, key="idem-key-0003", conv="../etc").status_code == 422


def test_failed_troubleshooting_then_authorized_escalation():
    c, _ = mk(); tid = create(c).json()["ticket_id"]
    assert upd(c, tid, "escalate", "idem-esc-0001").status_code == 409          # escalation before failed troubleshooting denied
    assert upd(c, tid, "troubleshoot_failed", "idem-ts-0001").json()["state"] == "TROUBLESHOOTING_FAILED"
    r = upd(c, tid, "escalate", "idem-esc-0002"); assert r.json()["state"] == "ESCALATION_REQUESTED" and r.json()["staff_confirmed"] is False
    assert upd(c, tid, "escalate", "idem-esc-0002").json()["replayed"] is True   # duplicate delivery
    types = [e["type"] for e in c.get("/api/events", headers=V).json()["events"]]
    assert {"TICKET_CREATED", "TROUBLESHOOTING_FAILED", "STAFF_ESCALATION_REQUESTED"} <= set(types)


def test_cross_conversation_update_denied():
    c, _ = mk(); tid = create(c).json()["ticket_id"]
    assert upd(c, tid, "troubleshoot_failed", "idem-x-0001", conv="conv_other_9999abcd").status_code == 404
    assert upd(c, "LIVE-0000000000000000", "resolve", "idem-x-0002").status_code == 404


def test_store_failure_is_not_success():
    c, _ = mk(FaultyStore(MemoryStore(), fail_writes=True)); r = create(c)
    assert r.status_code == 503 and r.json()["status"] == "FAILED" and r.json()["ticket_id"] is None


def test_unconfigured_store_fails_closed():
    c, _ = mk(UnconfiguredStore()); assert create(c).status_code == 503
    r = c.get("/api/events", headers=V); assert r.status_code == 503 and r.json()["stages"]["mongodb_write_readback"] == "BLOCKED_NO_CREDENTIALS"


def test_webhook_verified_links_and_duplicate():
    c, calls = mk(); tid = create(c).json()["ticket_id"]
    r = hook(c); assert r.json()["status"] == "STORED" and r.json()["linked_tickets"] == 1
    assert hook(c).json()["status"] == "DUPLICATE_IGNORED" and len(calls) == 1   # raindrop fires once
    assert calls[0]["assistant_output"] == "ok" and calls[0]["user_input"] == "SYNTHETIC: help"
    E = c.get("/api/events", headers=V).json()
    assert E["stages"]["signed_webhook"].startswith("VERIFIED") and E["stages"]["elevenlabs_conversation_id"] == "VERIFIED_BY_SIGNED_WEBHOOK"
    assert E["stages"]["raindrop_trace"] == "SDK_REGISTERED_CLOUD_NOT_TESTED"   # never cloud-verified without readback
    assert E["stages"]["raindrop_judge_verdict"] == "NOT_TESTED"
    assert "SYNTHETIC: help" not in json.dumps(E["webhooks"]) and E["webhooks"][0]["transcript_stored"] is False


def test_webhook_negative_security():
    c, calls = mk(); body = b'{"type":"post_call_transcription","data":{"conversation_id":"conv_test_0001abcd","agent_id":"agent_test"}}'
    assert c.post("/api/webhooks/elevenlabs", content=body).status_code == 401
    assert c.post("/api/webhooks/elevenlabs", content=body, headers={"elevenlabs-signature": sign("wrong", body, int(time.time()))}).status_code == 401
    good = sign(WS, body, int(time.time()))
    assert c.post("/api/webhooks/elevenlabs", content=body + b" ", headers={"elevenlabs-signature": good}).status_code == 401  # tampered body
    assert hook(c, ts=int(time.time()) - 7200).status_code == 401                                                              # replay of stale signature
    assert hook(c, agent="agent_other").json()["status"] == "PARKED" and hook(c, synthetic=False).json()["status"] == "PARKED"
    assert calls == []


def test_webhook_same_conversation_changed_body_conflicts():
    c, _ = mk(); assert hook(c).status_code == 200
    assert hook(c, extra={"extra_field": 1}).status_code == 409


def test_operator_raindrop_receipt_requires_key_and_webhook():
    c, _ = mk(); b = {"conversation_id": CONV, "trace_id": "trace-cloud-abc"}
    assert c.post("/api/operator/raindrop-receipt", json=b, headers=T).status_code == 401
    assert c.post("/api/operator/raindrop-receipt", json=b, headers=O).status_code == 404   # no webhook yet: refuse to fabricate
    create(c); hook(c)
    assert c.post("/api/operator/raindrop-receipt", json={**b, "judge_verdict": "PASS"}, headers=O).status_code == 200
    s = c.get("/api/events", headers=V).json()["stages"]
    assert s["raindrop_trace"] == "CLOUD_VERIFIED" and s["raindrop_trace_ids"] == ["trace-cloud-abc"] and s["raindrop_judge_verdict"] == "PASS"
