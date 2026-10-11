"""Raindrop instrumentation for one synthetic case. Input = current user message only;
output = full final assistant text; tool trajectories are the backend's sanitized records.
A returned SDK/trace id proves local SDK registration only; cloud receipt needs separate readback."""
from __future__ import annotations
import datetime as dt

import json
from pathlib import Path

PROJECT_ID = "RDF-SFTW26-NEW-001"
_FIXTURES = Path(__file__).resolve().parents[3] / "integration/three_platform/atlas_ticket_fixtures.jsonl"


class ExportDenied(Exception):
    """Raised before any SDK call when input is not admitted as synthetic-only."""


def _frozen_inputs() -> dict[str, str]:
    return {d["_id"]: d["scenario_input"] for d in map(json.loads, _FIXTURES.read_text().splitlines()) if d.get("synthetic") is True}


def admit_export(case_id: str, user_message: str, privacy_class: str) -> None:
    """Default deny. Only an explicit SYNTHETIC_ONLY class AND text equal to the frozen synthetic fixture input
    for that case (optionally prefixed 'SYNTHETIC: ') may leave the process."""
    if privacy_class != "SYNTHETIC_ONLY":
        raise ExportDenied("privacy_class must be SYNTHETIC_ONLY")
    expected = _frozen_inputs().get(case_id)
    if expected is None or user_message.removeprefix("SYNTHETIC: ") != expected:
        raise ExportDenied("input is not the frozen synthetic fixture text for this case")


class RaindropCase:
    def __init__(self, write_key: str, case_id: str, conversation_id: str, user_message: str, model: str = "elevenlabs-agent", privacy_class: str = "UNKNOWN"):
        admit_export(case_id, user_message, privacy_class)  # before SDK import/init
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
