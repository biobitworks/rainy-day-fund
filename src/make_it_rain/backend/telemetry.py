"""Raindrop instrumentation for one synthetic case. Input = current user message only;
output = full final assistant text; tool trajectories are the backend's sanitized records.
A returned SDK/trace id proves local SDK registration only; cloud receipt needs separate readback."""
from __future__ import annotations
import datetime as dt

PROJECT_ID = "RDF-SFTW26-NEW-001"


class RaindropCase:
    def __init__(self, write_key: str, case_id: str, conversation_id: str, user_message: str, model: str = "elevenlabs-agent"):
        if not user_message.strip():
            raise ValueError("current user message must be nonempty")
        import raindrop.analytics as rd
        self.rd = rd
        rd.init(api_key=write_key, tracing_enabled=True, auto_instrument=False, app_git=False)
        rd.set_redact_pii(True)
        self.event_id = f"rdf-{case_id}-{conversation_id}"[:120]
        self.i = rd.begin(user_id="rdf-synthetic-test", event="rdf.synthetic.agent_turn", event_id=self.event_id,
                          input=user_message, convo_id=conversation_id, model=model,
                          properties={"project_id": PROJECT_ID, "case_id": case_id, "conversation_id": conversation_id, "synthetic": True})

    def sink(self, rec: dict):  # pass as Config.telemetry
        self.i.track_tool(name=rec["tool"], input=rec["input"], output=rec["output"], duration_ms=rec["duration_ms"])

    def finish(self, assistant_output: str, atlas_readback: dict | None = None) -> dict:
        if atlas_readback is not None:
            self.i.set_properties({"atlas_ticket_id": atlas_readback.get("ticket_id"), "atlas_state": atlas_readback.get("state")})
        self.i.finish(output=assistant_output)
        self.rd.flush()
        reg = getattr(self.rd, "INTERACTION_TRACE_ID_REGISTRY", {})
        return {"event_id": self.event_id, "sdk_trace_id": (reg.get(self.event_id) if hasattr(reg, "get") else None),
                "flushed_at": dt.datetime.now(dt.timezone.utc).isoformat(), "cloud_readback": "NOT_TESTED"}
