"""Make It Rain integration backend: 4 tool endpoints + ElevenLabs post-call webhook.

Security: tool key (X-RDF-Tool-Key) and webhook HMAC are checked before any parsing/side effect.
Secrets come from config, never from request bodies. Raw webhook JSON/transcripts are never
logged or stored. Success is reported only after authoritative readback."""
from __future__ import annotations
import hashlib, hmac, json, re, time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from .store import (EVENTS, FIXTURES, PARKED, PROJECT_ID, TICKETS, WEBHOOKS, StoreError)

CASE_RE = re.compile(r"^RDF-SYN-(0[01][0-9])$")
ALLOWED_CASES = {f"RDF-SYN-{i:03d}" for i in range(1, 13)}
SIG_TOLERANCE_S = 1800
MAX_BODY = 65536
GUIDE = {"RDF-SYN-TICKET-20261011-V1": "Generic synthetic guidance only: no event-specific credentials or schedules are available. Escalate to staff."}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


@dataclass
class Config:
    tool_key: str
    webhook_secret: str
    agent_id: str
    session_secret: str = ""  # MUST differ from tool_key and webhook_secret; empty => session routes fail closed
    telemetry: Callable[[dict], Any] = lambda rec: None  # sanitized trajectory sink
    clock: Callable[[], float] = time.time


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LookupReq(_Strict):
    query: str = Field(max_length=200)
    guide_version_id: str = Field(max_length=80)


class CreateReq(_Strict):
    case_id: str
    idempotency_key: str = Field(min_length=8, max_length=80)


class StatusReq(_Strict):
    ticket_id: str = Field(max_length=80)


class EscalateReq(_Strict):
    ticket_id: str = Field(max_length=80)
    reason_code: str = Field(pattern=r"^[A-Z_]{3,40}$")


def verify_signature(secret: str, header: str | None, raw: bytes, now_ts: float) -> bool:
    """ElevenLabs format: 'elevenlabs-signature: t=<unix>,v0=<hex hmac_sha256(secret, f"{t}.{body}")>'."""
    if not header or not secret:
        return False
    try:
        parts = dict(p.split("=", 1) for p in header.split(","))
        t, v0 = parts["t"], parts["v0"]
        if abs(now_ts - int(t)) > SIG_TOLERANCE_S:
            return False
    except Exception:
        return False
    expect = hmac.new(secret.encode(), t.encode() + b"." + raw, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expect, v0)


def issue_session_token(secret: str, session_id: str, ttl_s: int, now_ts: float) -> str:
    """Backend-issued opaque principal: '<sid>.<exp>.<hmac>'. The LLM never mints one; it can only replay the
    token its own conversation was given, so it cannot reach another session's tickets."""
    exp = int(now_ts) + ttl_s
    mac = hmac.new(secret.encode(), f"{session_id}.{exp}".encode(), hashlib.sha256).hexdigest()
    return f"{session_id}.{exp}.{mac}"


def verify_session_token(secret: str, token: str | None, now_ts: float) -> str | None:
    if not secret or not token:
        return None
    try:
        sid, exp, mac = token.rsplit(".", 2)
        if int(exp) < now_ts or not re.fullmatch(r"[A-Za-z0-9_-]{8,64}", sid):
            return None
    except Exception:
        return None
    expect = hmac.new(secret.encode(), f"{sid}.{exp}".encode(), hashlib.sha256).hexdigest()
    return sid if hmac.compare_digest(expect, mac) else None


def sign(secret: str, raw: bytes, ts: int) -> str:  # test/helper only
    return f"t={ts},v0=" + hmac.new(secret.encode(), str(ts).encode() + b"." + raw, hashlib.sha256).hexdigest()


def create_app(store, cfg: Config) -> FastAPI:
    if cfg.session_secret and cfg.session_secret in (cfg.tool_key, cfg.webhook_secret):
        raise ValueError("session_secret must be distinct from tool_key and webhook_secret")
    app = FastAPI(title="rdf-integration-backend", docs_url=None, redoc_url=None, openapi_url=None)

    def trace(tool: str, inp: dict, out: dict, started: float, case_id=None, conv=None):
        try:
            cfg.telemetry({"tool": tool, "input": inp, "output": out, "case_id": case_id,
                           "conversation_id": conv, "duration_ms": round((time.perf_counter() - started) * 1000, 2)})
        except Exception:
            pass  # telemetry never blocks or alters a tool outcome

    def tool_auth(request: Request) -> bool:
        k = request.headers.get("x-rdf-tool-key", "")
        return bool(cfg.tool_key) and hmac.compare_digest(k.encode(), cfg.tool_key.encode())

    async def parse(request: Request, model):
        if len(await request.body()) > MAX_BODY:
            return None
        try:
            return model.model_validate_json(await request.body())
        except Exception:
            return None

    def session_of(request: Request) -> str | None:
        return verify_session_token(cfg.session_secret, request.headers.get("x-rdf-session"), cfg.clock())

    def readback_flag() -> bool:  # only a real Atlas store may claim an Atlas readback
        return store.kind == "ATLAS"

    def respond(out: dict, code: int = 200):
        return JSONResponse(out, status_code=code, headers={"X-RDF-Readback-Source": store.kind})

    def deny(code=401, status="UNAUTHORIZED"):
        return JSONResponse({"status": status}, status_code=code)

    @app.get("/healthz")
    def health():
        return {"status": "ok", "store": store.kind}

    @app.post("/api/sessions")
    async def issue_session(request: Request):
        """DEMO issuance (tool-key protected). Production must bind this to real attendee authentication."""
        if not tool_auth(request) or not cfg.session_secret: return deny()
        sid = "S" + sha(f"{time.time_ns()}|{id(request)}".encode())[:24]
        return {"session_id": sid, "session_token": issue_session_token(cfg.session_secret, sid, 3600, cfg.clock())}

    @app.post("/api/tools/lookup_guide")
    async def lookup_guide(request: Request):
        if not tool_auth(request): return deny()
        t0 = time.perf_counter(); req = await parse(request, LookupReq)
        if req is None: return JSONResponse({"status": "FAILED", "source_version": None, "excerpt": None}, status_code=422)
        txt = GUIDE.get(req.guide_version_id)
        out = ({"status": "SUCCEEDED", "source_version": req.guide_version_id, "excerpt": txt} if txt
               else {"status": "NOT_FOUND", "source_version": None, "excerpt": None})
        trace("lookup_guide", {"guide_version_id": req.guide_version_id}, out, t0)
        return out

    @app.post("/api/tools/create_test_ticket")
    async def create_test_ticket(request: Request):
        if not tool_auth(request): return deny()
        sid = session_of(request)
        if sid is None: return deny(401, "UNAUTHORIZED")  # no backend-issued session => no ticket
        t0 = time.perf_counter(); req = await parse(request, CreateReq)
        conv = request.headers.get("x-rdf-conversation-id", "")[:80] or None  # optional extension header, outside contract body
        if req is None or req.case_id not in ALLOWED_CASES:
            return JSONResponse({"status": "REJECTED", "ticket_id": None, "state": "OPEN_TEST_ONLY", "atlas_readback": False}, status_code=422)
        tid = "SMOKE-" + sha(f"{PROJECT_ID}|{sid}|{req.idempotency_key}".encode())[:16]
        try:
            fx = store.get(FIXTURES, req.case_id)
            if fx is None or fx.get("synthetic") is not True:
                raise StoreError("fixture missing")
            doc = {"_id": tid, "project_id": PROJECT_ID, "record_type": "INTEGRATION_SMOKE_TICKET",
                   "ticket_id": tid, "case_id": req.case_id, "session_id": sid, "readback_source": store.kind, "fixture_source_version": fx["source_version"],
                   "state": "OPEN_TEST_ONLY", "idempotency_key": req.idempotency_key,
                   "conversation_id": conv, "created_at": now(), "synthetic": True,
                   "contains_personal_data": False, "predecessor_id": req.case_id}
            inserted = store.insert_if_absent(TICKETS, doc)
            rb = store.get(TICKETS, tid)  # authoritative readback
            if rb is None:
                raise StoreError("readback empty")
            if rb["case_id"] != req.case_id:  # same key reused for different case
                out = {"status": "REJECTED", "ticket_id": None, "state": "OPEN_TEST_ONLY", "atlas_readback": False}
                trace("create_test_ticket", {"case_id": req.case_id}, out, t0, req.case_id, conv)
                return JSONResponse(out, status_code=409)
            store.insert_if_absent(EVENTS, {"_id": f"EVT-{tid}-created", "project_id": PROJECT_ID, "ticket_id": tid,
                                            "sequence": 1, "type": "TICKET_CREATED", "event_time": now(), "synthetic": True})
        except StoreError as e:
            out = {"status": "FAILED", "ticket_id": None, "state": "OPEN_TEST_ONLY", "atlas_readback": False}
            trace("create_test_ticket", {"case_id": req.case_id}, {**out, "error": str(e)[:40]}, t0, req.case_id, conv)
            return JSONResponse(out, status_code=503)
        out = {"status": "SUCCEEDED", "ticket_id": tid, "state": rb["state"], "atlas_readback": readback_flag()}
        trace("create_test_ticket", {"case_id": req.case_id, "created_new": inserted}, out, t0, req.case_id, conv)
        return respond(out)

    @app.post("/api/tools/get_ticket_status")
    async def get_ticket_status(request: Request):
        if not tool_auth(request): return deny()
        sid = session_of(request)
        if sid is None: return deny(401, "UNAUTHORIZED")
        t0 = time.perf_counter(); req = await parse(request, StatusReq)
        if req is None: return JSONResponse({"status": "FAILED", "ticket_id": None, "state": None, "atlas_readback": False}, status_code=422)
        try:
            d = store.get(TICKETS, req.ticket_id)  # live store query, never echoes input
        except StoreError:
            return JSONResponse({"status": "FAILED", "ticket_id": None, "state": None, "atlas_readback": False}, status_code=503)
        if d is not None and d.get("session_id") != sid:
            d = None  # not the caller's ticket: indistinguishable from nonexistent (no existence oracle)
        out = ({"status": "SUCCEEDED", "ticket_id": d["ticket_id"], "state": d["state"], "atlas_readback": readback_flag()} if d
               else {"status": "NOT_FOUND", "ticket_id": None, "state": None, "atlas_readback": False})
        trace("get_ticket_status", {"ticket_id": req.ticket_id}, out, t0, d and d.get("case_id"))
        return respond(out)

    @app.post("/api/tools/request_staff_escalation")
    async def request_staff_escalation(request: Request):
        if not tool_auth(request): return deny()
        sid = session_of(request)
        if sid is None: return deny(401, "UNAUTHORIZED")
        t0 = time.perf_counter(); req = await parse(request, EscalateReq)  # extra fields (e.g. staff_confirmed) rejected
        if req is None: return JSONResponse({"status": "REJECTED", "staff_confirmed": False}, status_code=422)
        try:
            d = store.get(TICKETS, req.ticket_id)
            if d is None or d.get("session_id") != sid:  # same answer for missing and not-yours
                return JSONResponse({"status": "REJECTED", "staff_confirmed": False}, status_code=404)
            ok = store.insert_if_absent(EVENTS, {"_id": f"EVT-{req.ticket_id}-esc-{req.reason_code}", "project_id": PROJECT_ID,
                "ticket_id": req.ticket_id, "sequence": 2, "type": "STAFF_ESCALATION_REQUESTED",
                "reason_code": req.reason_code, "event_time": now(), "synthetic": True})
            if store.get(EVENTS, f"EVT-{req.ticket_id}-esc-{req.reason_code}") is None:
                raise StoreError("readback empty")
            store.update(TICKETS, req.ticket_id, {"state": "ESCALATION_REQUESTED"})
        except StoreError:
            return JSONResponse({"status": "FAILED", "staff_confirmed": False}, status_code=503)
        out = {"status": "PENDING", "staff_confirmed": False}  # never claims staff approval
        trace("request_staff_escalation", {"ticket_id": req.ticket_id, "reason_code": req.reason_code}, out, t0, d.get("case_id"))
        return out

    @app.post("/api/webhooks/elevenlabs")
    async def elevenlabs_webhook(request: Request):
        raw = await request.body()
        if len(raw) > MAX_BODY:
            return JSONResponse({"status": "TOO_LARGE"}, status_code=413)
        if not verify_signature(cfg.webhook_secret, request.headers.get("elevenlabs-signature"), raw, cfg.clock()):
            return deny(401, "INVALID_SIGNATURE")
        try:
            body = json.loads(raw)
            data = body["data"]; conv = data["conversation_id"]; agent = data["agent_id"]
            typ = body["type"]; ev_ts = body.get("event_timestamp")
        except Exception:
            return JSONResponse({"status": "MALFORMED"}, status_code=400)
        digest = sha(raw)
        dv = ((data.get("conversation_initiation_client_data") or {}).get("dynamic_variables") or {})
        case_id = dv.get("rdf_case_id")
        meta = {"project_id": PROJECT_ID, "event_type": typ, "conversation_id": conv, "agent_id": agent,
                "event_timestamp": ev_ts, "event_digest": digest, "received_at": now(), "case_id": case_id}
        try:
            if typ != "post_call_transcription" or agent != cfg.agent_id or case_id not in ALLOWED_CASES or dv.get("rdf_synthetic") not in (True, "true"):
                store.insert_if_absent(PARKED, {"_id": f"PARK-{digest[:24]}", **{k: meta[k] for k in ("project_id", "event_type", "event_digest", "received_at")},
                                                "reason": "NO_SYNTHETIC_ASSERTION_OR_AGENT_MISMATCH", "synthetic": False})
                return {"status": "PARKED"}
            wid = f"WH-{sha((typ + '|' + conv).encode())[:20]}"  # unique event key => duplicate delivery is idempotent
            inserted = store.insert_if_absent(WEBHOOKS, {"_id": wid, **meta, "synthetic": True, "transcript_stored": False})
            rb = store.get(WEBHOOKS, wid)
            if rb is None:
                raise StoreError("readback empty")
            if rb["event_digest"] != digest:  # same conversation+type, different signed body
                store.insert_if_absent(PARKED, {"_id": f"PARK-{digest[:24]}", "project_id": PROJECT_ID, "event_type": typ,
                    "event_digest": digest, "received_at": now(), "reason": "DIGEST_MISMATCH_FOR_EXISTING_EVENT_KEY", "synthetic": False})
                return JSONResponse({"status": "CONFLICT_PARKED"}, status_code=409)
        except StoreError:
            return JSONResponse({"status": "FAILED"}, status_code=503)  # non-200 so ElevenLabs retries
        return {"status": "STORED" if inserted else "DUPLICATE_IGNORED", "webhook_record_id": wid}

    return app
