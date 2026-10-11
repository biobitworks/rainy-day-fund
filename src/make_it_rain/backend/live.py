"""Make It Rain LIVE integration API (Vercel/FastAPI): synthetic tickets, event timeline, signed webhook.

Fail-closed rules: tool key / viewer key / operator key / webhook HMAC are checked before any parsing or
side effect; success is reported only after an authoritative store readback; stage statuses are derived from
stored records and default to NOT_TESTED. Transcripts are never stored. Nothing here is Atlas evidence unless
store.kind == "ATLAS"."""
from __future__ import annotations
import hashlib, hmac, json, re, time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from .app import sha, verify_signature, MAX_BODY
from .store import LIVE_EVENTS, LIVE_IDEM, LIVE_TICKETS, LIVE_WEBHOOKS, PROJECT_ID, StoreError

CONV_RE = r"^[A-Za-z0-9_-]{8,80}$"
NOSTORE = {"Cache-Control": "no-store, max-age=0", "Pragma": "no-cache"}
STATES = ("OPEN", "TROUBLESHOOTING_FAILED", "ESCALATION_REQUESTED", "RESOLVED")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class LiveConfig:
    tool_key: str = ""
    viewer_key: str = ""
    operator_key: str = ""
    webhook_secret: str = ""
    agent_id: str = ""
    clock: Callable[[], float] = time.time
    raindrop: Callable[[dict], dict] | None = None      # (user_input, assistant_output, conversation_id, tools) -> receipt
    signed_url: Callable[[str], str] | None = None       # agent_id -> signed websocket URL (server-side API key)
    evaluation: Callable[[], dict | None] = lambda: None


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CreateReq(_Strict):
    idempotency_key: str = Field(min_length=8, max_length=80)
    summary: str = Field(min_length=12, max_length=200, pattern=r"^SYNTHETIC: ")
    channel: str = Field(pattern=r"^(voice|text)$")
    conversation_id: str = Field(pattern=CONV_RE)


class UpdateReq(_Strict):
    idempotency_key: str = Field(min_length=8, max_length=80)
    ticket_id: str = Field(pattern=r"^LIVE-[0-9a-f]{16}$")
    action: str = Field(pattern=r"^(troubleshoot_failed|escalate|resolve)$")
    conversation_id: str = Field(pattern=CONV_RE)
    reason_code: str | None = Field(default=None, pattern=r"^[A-Z_]{3,40}$")


class RaindropReceipt(_Strict):
    conversation_id: str = Field(pattern=CONV_RE)
    trace_id: str = Field(min_length=6, max_length=120)
    judge_verdict: str | None = Field(default=None, max_length=200)


def _eq(a: str, b: str) -> bool:
    return bool(b) and hmac.compare_digest(a.encode(), b.encode())


def create_live_app(store, cfg: LiveConfig) -> FastAPI:
    app = FastAPI(title="rdf-live", docs_url=None, redoc_url=None, openapi_url=None)

    def auth(request: Request, header: str, key: str) -> bool:
        return _eq(request.headers.get(header, ""), key)

    def j(body: dict, code: int = 200, extra: dict | None = None):
        return JSONResponse(body, status_code=code, headers={**NOSTORE, "X-RDF-Store": store.kind, **(extra or {})})

    def deny(code=401, status="UNAUTHORIZED"):
        return j({"status": status}, code)

    async def parse(request: Request, model):
        raw = await request.body()
        if len(raw) > MAX_BODY:
            return None
        try:
            return model.model_validate_json(raw)
        except Exception:
            return None

    def event(tid: str, typ: str, seq_hint: int, conv: str | None, extra: dict | None = None):
        ts = now()
        doc = {"_id": f"EVT-{tid}-{typ}-{sha((ts + str(seq_hint)).encode())[:8]}" if typ == "NOTE" else f"EVT-{tid}-{typ}",
               "project_id": PROJECT_ID, "ticket_id": tid, "type": typ, "conversation_id": conv,
               "created_at": ts, "synthetic": True, **(extra or {})}
        store.insert_if_absent(LIVE_EVENTS, doc)
        return doc

    @app.get("/api/health")
    def health():
        return j({"status": "ok", "project_id": PROJECT_ID, "store": store.kind,
                  "configured": {"tool_key": bool(cfg.tool_key), "viewer_key": bool(cfg.viewer_key),
                                 "webhook_secret": bool(cfg.webhook_secret), "agent_id": bool(cfg.agent_id),
                                 "raindrop_sink": cfg.raindrop is not None,
                                 "atlas": store.kind == "ATLAS"},
                  "server_now": now()})

    @app.get("/api/tickets")
    def tickets(request: Request):
        if not auth(request, "x-rdf-viewer-key", cfg.viewer_key): return deny()
        try:
            rows = store.list(LIVE_TICKETS, 100)
        except StoreError as e:
            return j({"status": "STORE_UNAVAILABLE", "error": str(e)[:60], "tickets": [], "server_now": now()}, 503)
        for r in rows: r.pop("_id", None); r.pop("idempotency_key", None)
        return j({"status": "OK", "server_now": now(), "tickets": rows})

    @app.get("/api/events")
    def events(request: Request):
        if not auth(request, "x-rdf-viewer-key", cfg.viewer_key): return deny()
        try:
            ev = store.list(LIVE_EVENTS, 200); wh = store.list(LIVE_WEBHOOKS, 50, "received_at"); tk = store.list(LIVE_TICKETS, 100)
        except StoreError as e:
            return j({"status": "STORE_UNAVAILABLE", "error": str(e)[:60], "stages": stages([], [], [], False), "server_now": now()}, 503)
        for r in ev + wh: r.pop("_id", None)
        return j({"status": "OK", "server_now": now(), "events": ev, "webhooks": wh,
                  "stages": stages(tk, ev, wh, True), "evaluation": cfg.evaluation()})

    def stages(tk, ev, wh, reachable) -> dict:
        NT = "NOT_TESTED"
        atlas = store.kind == "ATLAS"
        convs = {t.get("conversation_id") for t in tk if t.get("conversation_id")}
        verified = [w for w in wh if w.get("verified")]
        wh_convs = {w.get("conversation_id") for w in verified}
        rd = [w.get("raindrop") or {} for w in verified]
        return {
            "store": store.kind,
            "mongodb_write_readback": ("VERIFIED_ATLAS_READBACK" if atlas and any(t.get("readback_ok") for t in tk)
                                       else "LOCAL_DOUBLE_NOT_ATLAS" if reachable and not atlas and store.kind != "UNCONFIGURED_FAIL_CLOSED"
                                       else "BLOCKED_NO_CREDENTIALS" if store.kind == "UNCONFIGURED_FAIL_CLOSED" else NT),
            "elevenlabs_conversation_id": ("VERIFIED_BY_SIGNED_WEBHOOK" if convs & wh_convs else "ASSERTED_BY_TOOL_CALL_ONLY" if convs else NT),
            "conversation_ids": sorted(convs)[:10],
            "signed_webhook": f"VERIFIED x{len(verified)}" if verified else NT,
            "raindrop_trace": ("CLOUD_VERIFIED" if any(r.get("cloud_readback") == "VERIFIED" for r in rd)
                               else "SDK_REGISTERED_CLOUD_NOT_TESTED" if any(r.get("sdk_trace_id") for r in rd) else NT),
            "raindrop_trace_ids": [r.get("cloud_trace_id") or r.get("sdk_trace_id") for r in rd if r.get("cloud_trace_id") or r.get("sdk_trace_id")][:5],
            "raindrop_judge_verdict": next((r.get("judge_verdict") for r in rd if r.get("judge_verdict")), NT),
        }

    # ------------------------------------------------------------------ tools
    @app.post("/api/tools/create-ticket")
    async def create_ticket(request: Request):
        if not auth(request, "x-rdf-tool-key", cfg.tool_key): return deny()
        req = await parse(request, CreateReq)
        if req is None: return j({"status": "REJECTED", "ticket_id": None}, 422)
        digest = sha(json.dumps(req.model_dump(exclude={"idempotency_key"}), sort_keys=True).encode())
        iid = "IDEM-" + sha(f"create|{req.idempotency_key}".encode())[:24]
        tid = "LIVE-" + sha(f"{PROJECT_ID}|{req.idempotency_key}".encode())[:16]
        t0 = time.perf_counter()
        try:
            claimed = store.insert_if_absent(LIVE_IDEM, {"_id": iid, "project_id": PROJECT_ID, "tool": "create",
                                                          "payload_digest": digest, "ticket_id": tid, "created_at": now()})
            prior = store.get(LIVE_IDEM, iid)
            if prior is None: raise StoreError("idempotency readback empty")
            if prior["payload_digest"] != digest:
                return j({"status": "IDEMPOTENCY_CONFLICT", "ticket_id": None}, 409)
            ts = now()
            store.insert_if_absent(LIVE_TICKETS, {"_id": tid, "project_id": PROJECT_ID, "ticket_id": tid,
                "record_type": "LIVE_SYNTHETIC_TICKET", "summary": req.summary, "channel": req.channel,
                "conversation_id": req.conversation_id, "state": "OPEN", "created_at": ts, "updated_at": ts,
                "synthetic": True, "contains_personal_data": False, "readback_source": store.kind, "idempotency_key": req.idempotency_key})
            rb = store.get(LIVE_TICKETS, tid)  # authoritative readback
            if rb is None: raise StoreError("readback empty")
            ms = round((time.perf_counter() - t0) * 1000, 1)
            store.update(LIVE_TICKETS, tid, {"readback_ok": True, "write_readback_ms": ms})
            event(tid, "TICKET_CREATED", 1, req.conversation_id, {"channel": req.channel})
        except StoreError as e:
            return j({"status": "FAILED", "ticket_id": None, "error": str(e)[:60]}, 503)
        return j({"status": "SUCCEEDED", "ticket_id": tid, "state": rb["state"], "replayed": not claimed,
                  "atlas_readback": store.kind == "ATLAS", "write_readback_ms": ms})

    @app.post("/api/tools/update-ticket")
    async def update_ticket(request: Request):
        if not auth(request, "x-rdf-tool-key", cfg.tool_key): return deny()
        req = await parse(request, UpdateReq)
        if req is None: return j({"status": "REJECTED"}, 422)
        digest = sha(json.dumps(req.model_dump(exclude={"idempotency_key"}), sort_keys=True).encode())
        iid = "IDEM-" + sha(f"update|{req.idempotency_key}".encode())[:24]
        try:
            claimed = store.insert_if_absent(LIVE_IDEM, {"_id": iid, "project_id": PROJECT_ID, "tool": "update",
                                                          "payload_digest": digest, "ticket_id": req.ticket_id, "created_at": now()})
            prior = store.get(LIVE_IDEM, iid)
            if prior is None: raise StoreError("idempotency readback empty")
            if prior["payload_digest"] != digest: return j({"status": "IDEMPOTENCY_CONFLICT"}, 409)
            t = store.get(LIVE_TICKETS, req.ticket_id)
            # a tool call may only touch tickets opened by the SAME conversation (no cross-conversation IDOR)
            if t is None or t.get("conversation_id") != req.conversation_id:
                return j({"status": "REJECTED", "staff_confirmed": False}, 404)
            cur = t["state"]
            target = {"troubleshoot_failed": "TROUBLESHOOTING_FAILED", "escalate": "ESCALATION_REQUESTED", "resolve": "RESOLVED"}[req.action]
            if not claimed and cur == target:  # duplicate delivery of an already-applied update
                return j({"status": "SUCCEEDED", "ticket_id": t["ticket_id"], "state": cur, "replayed": True, "staff_confirmed": False})
            ok = {"troubleshoot_failed": cur == "OPEN",
                  "escalate": cur == "TROUBLESHOOTING_FAILED",  # authorized only after a recorded failed troubleshooting step
                  "resolve": cur in ("OPEN", "TROUBLESHOOTING_FAILED")}[req.action]
            if not ok:
                return j({"status": "REJECTED_TRANSITION", "state": cur, "action": req.action, "staff_confirmed": False}, 409)
            new = target
            store.update(LIVE_TICKETS, req.ticket_id, {"state": new, "updated_at": now()})
            rb = store.get(LIVE_TICKETS, req.ticket_id)
            if rb is None or rb["state"] != new: raise StoreError("readback mismatch")
            event(req.ticket_id, {"TROUBLESHOOTING_FAILED": "TROUBLESHOOTING_FAILED", "ESCALATION_REQUESTED": "STAFF_ESCALATION_REQUESTED",
                                  "RESOLVED": "TICKET_RESOLVED"}[new], 2, req.conversation_id, {"reason_code": req.reason_code})
        except StoreError as e:
            return j({"status": "FAILED", "error": str(e)[:60]}, 503)
        return j({"status": "SUCCEEDED", "ticket_id": req.ticket_id, "state": new, "replayed": False,
                  "staff_confirmed": False, "atlas_readback": store.kind == "ATLAS"})  # never claims staff approval

    # --------------------------------------------------------------- webhook
    @app.post("/api/webhooks/elevenlabs")
    async def webhook(request: Request):
        raw = await request.body()
        if len(raw) > MAX_BODY: return j({"status": "TOO_LARGE"}, 413)
        if not verify_signature(cfg.webhook_secret, request.headers.get("elevenlabs-signature"), raw, cfg.clock()):
            return deny(401, "INVALID_SIGNATURE")  # stale timestamp (replay) also lands here
        try:
            body = json.loads(raw); data = body["data"]; conv = data["conversation_id"]; agent = data["agent_id"]; typ = body["type"]
            if not re.fullmatch(CONV_RE, conv): raise ValueError
        except Exception:
            return j({"status": "MALFORMED"}, 400)
        digest = sha(raw)
        dv = ((data.get("conversation_initiation_client_data") or {}).get("dynamic_variables") or {})
        synthetic = dv.get("rdf_synthetic") in (True, "true")
        if typ != "post_call_transcription" or agent != cfg.agent_id or not synthetic:
            return j({"status": "PARKED", "reason": "NOT_SYNTHETIC_OR_AGENT_MISMATCH_OR_TYPE"}, 200)
        wid = f"WH-{sha((typ + '|' + conv).encode())[:20]}"
        try:
            existing = store.get(LIVE_WEBHOOKS, wid)
            if existing is not None:
                if existing["event_digest"] != digest:
                    return j({"status": "CONFLICT", "webhook_record_id": wid}, 409)
                return j({"status": "DUPLICATE_IGNORED", "webhook_record_id": wid})
            linked = [t["ticket_id"] for t in store.list(LIVE_TICKETS, 200) if t.get("conversation_id") == conv]
            rd = {"status": "NOT_CONFIGURED", "cloud_readback": "NOT_TESTED"}
            if cfg.raindrop is not None:
                try:
                    tr = data.get("transcript") or []
                    users = [m.get("message") for m in tr if m.get("role") == "user" and m.get("message")]
                    agents = [m.get("message") for m in tr if m.get("role") == "agent" and m.get("message")]
                    rd = cfg.raindrop({"conversation_id": conv, "user_input": users[-1] if users else "",
                                       "assistant_output": "\n".join(agents), "tickets": linked})
                except Exception as e:
                    rd = {"status": "FAILED", "error": type(e).__name__, "cloud_readback": "NOT_TESTED"}
            store.insert_if_absent(LIVE_WEBHOOKS, {"_id": wid, "project_id": PROJECT_ID, "event_type": typ, "conversation_id": conv,
                "agent_id": agent, "event_digest": digest, "received_at": now(), "verified": True, "signature_scheme": "t=,v0= HMAC-SHA256",
                "linked_ticket_ids": linked, "raindrop": rd, "transcript_stored": False, "synthetic": True})
            if store.get(LIVE_WEBHOOKS, wid) is None: raise StoreError("readback empty")
            for tid in linked: event(tid, "WEBHOOK_VERIFIED", 3, conv, {"webhook_record_id": wid})
        except StoreError:
            return j({"status": "FAILED"}, 503)  # non-2xx so ElevenLabs retries
        return j({"status": "STORED", "webhook_record_id": wid, "linked_tickets": len(linked)})

    # -------------------------------------------------------------- operator
    @app.post("/api/operator/raindrop-receipt")
    async def raindrop_receipt(request: Request):
        """Operator records a trace id they independently read back from Raindrop Cloud. Requires an existing verified webhook."""
        if not auth(request, "x-rdf-operator-key", cfg.operator_key): return deny()
        req = await parse(request, RaindropReceipt)
        if req is None: return j({"status": "REJECTED"}, 422)
        wid = f"WH-{sha(('post_call_transcription|' + req.conversation_id).encode())[:20]}"
        try:
            w = store.get(LIVE_WEBHOOKS, wid)
            if w is None: return j({"status": "REJECTED", "reason": "NO_VERIFIED_WEBHOOK_FOR_CONVERSATION"}, 404)
            rd = {**(w.get("raindrop") or {}), "cloud_readback": "VERIFIED", "cloud_trace_id": req.trace_id,
                  **({"judge_verdict": req.judge_verdict} if req.judge_verdict else {}), "recorded_at": now()}
            store.update(LIVE_WEBHOOKS, wid, {"raindrop": rd})
        except StoreError:
            return j({"status": "FAILED"}, 503)
        return j({"status": "RECORDED"})

    @app.get("/api/conversation/signed-url")
    def signed_url(request: Request):
        if not auth(request, "x-rdf-viewer-key", cfg.viewer_key): return deny()
        if cfg.signed_url is None or not cfg.agent_id: return j({"status": "NOT_CONFIGURED"}, 503)
        try:
            return j({"status": "OK", "signed_url": cfg.signed_url(cfg.agent_id), "agent_id": cfg.agent_id})
        except Exception as e:
            return j({"status": "FAILED", "error": type(e).__name__}, 502)

    return app
