"""Rainy Day Fund: fail-closed Vercel ASGI entry for synthetic ElevenLabs tests.

This is an integration adapter, not authorization to process real attendee data.
Secrets are supplied exclusively by the deployment environment.
"""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from make_it_rain.backend.app import ALLOWED_CASES, Config, create_app
from make_it_rain.backend.store import DB_NAME, MongoStore, StoreError


class UnconfiguredStore:
    kind = "UNCONFIGURED_NOT_ATLAS"

    def get(self, *args, **kwargs):
        raise StoreError("Atlas not connected")

    def insert_if_absent(self, *args, **kwargs):
        raise StoreError("Atlas not connected")

    def update(self, *args, **kwargs):
        raise StoreError("Atlas not connected")

    def count(self, *args, **kwargs):
        raise StoreError("Atlas not connected")


def get_store():
    uri = os.environ.get("MONGODB_URI", "")
    if not uri:
        return UnconfiguredStore()
    try:
        store = MongoStore(uri, os.getenv("MONGODB_DB", DB_NAME))
        store.db.command("ping")
        return store
    except Exception:
        # Never include connection strings or authentication diagnostics in responses/logs.
        return UnconfiguredStore()


def sanitized_tool_telemetry(rec: dict):
    """Optional Raindrop tool trace; not an ElevenLabs turn or a cloud readback."""
    key = os.getenv("RAINDROP_WRITE_KEY", "")
    case_id = rec.get("case_id")
    if not key or case_id not in ALLOWED_CASES:
        return
    import raindrop.analytics as rd
    rd.init(api_key=key, tracing_enabled=True, auto_instrument=False, app_git=False)
    rd.set_redact_pii(True)
    event_id = "rdf-tool-" + uuid.uuid4().hex
    i = rd.begin(
        user_id="rdf-synthetic-test",
        event="rdf.synthetic.backend_tool",
        event_id=event_id,
        input=rec.get("input", {}),
        convo_id=rec.get("conversation_id") or event_id,
        model="backend-tools",
        properties={"project_id": "RDF-SFTW26-NEW-001", "case_id": case_id, "synthetic": True},
    )
    i.finish(output=rec.get("output", {}))
    rd.flush()


app = create_app(
    get_store(),
    Config(
        tool_key=os.getenv("RDF_TOOL_API_KEY", ""),
        session_secret=os.getenv("RDF_SESSION_SECRET", ""),
        webhook_secret=os.getenv("ELEVENLABS_WEBHOOK_SECRET", ""),
        agent_id=os.getenv("ELEVENLABS_AGENT_ID", ""),
        telemetry=sanitized_tool_telemetry,
    ),
)
