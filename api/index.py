"""Vercel ASGI entry. All secrets come from Vercel env (server-side); missing/uncredentialled Atlas => fail-closed store."""
import json, os, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from make_it_rain.backend.live import LiveConfig, create_live_app
from make_it_rain.backend.store import DB_NAME, MongoStore, StoreError, UnconfiguredStore


def _store():
    uri = os.getenv("MONGODB_URI", "")
    try:
        return MongoStore(uri, os.getenv("MONGODB_DB", DB_NAME))
    except StoreError:
        return UnconfiguredStore()
    except Exception:
        return UnconfiguredStore()


def _signed_url(agent_id: str) -> str:
    req = urllib.request.Request(
        "https://api.elevenlabs.io/v1/convai/conversation/get-signed-url?agent_id=" + agent_id,
        headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"]})
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.load(r)["signed_url"]


def _raindrop(ctx: dict) -> dict:
    key = os.getenv("RAINDROP_WRITE_KEY", "")
    if not key:
        return {"status": "NOT_CONFIGURED", "cloud_readback": "NOT_TESTED"}
    import raindrop.analytics as rd  # supported SDK
    rd.init(api_key=key, tracing_enabled=True, auto_instrument=False, app_git=False)
    rd.set_redact_pii(True)  # transcripts here are synthetic-only (webhook gate requires rdf_synthetic)
    eid = ("rdf-live-" + ctx["conversation_id"])[:120]
    i = rd.begin(user_id="rdf-synthetic-test", event="rdf.synthetic.live_conversation", event_id=eid,
                 input=ctx["user_input"], convo_id=ctx["conversation_id"],
                 properties={"project_id": "RDF-SFTW26-NEW-001", "synthetic": True, "tickets": ctx["tickets"]})
    i.finish(output=ctx["assistant_output"])
    rd.flush()
    reg = getattr(rd, "INTERACTION_TRACE_ID_REGISTRY", {})
    return {"status": "SDK_FLUSH_CALLED", "event_id": eid, "sdk_trace_id": reg.get(eid) if hasattr(reg, "get") else None,
            "cloud_readback": "NOT_TESTED"}


def _evaluation():
    p = ROOT / "results" / "local_synthetic_evaluation.json"
    if not p.exists():
        return None
    d = json.loads(p.read_text())
    return {"origin": d.get("origin"), "fixture_sha256": d.get("fixture_sha256"),
            "V0": {k: d["baseline"].get(k) for k in ("policy_version", "total", "passed", "unsafe")},
            "V1": {k: d["candidate"].get(k) for k in ("policy_version", "total", "passed", "unsafe")} if "candidate" in d else None,
            "decision": d.get("decision"), "hosted_atlas": d.get("hosted_atlas")}


app = create_live_app(_store(), LiveConfig(
    tool_key=os.getenv("RDF_TOOL_KEY", ""), viewer_key=os.getenv("RDF_VIEWER_KEY", ""),
    operator_key=os.getenv("RDF_OPERATOR_KEY", ""), webhook_secret=os.getenv("ELEVENLABS_WEBHOOK_SECRET", ""),
    agent_id=os.getenv("ELEVENLABS_AGENT_ID", ""), raindrop=_raindrop,
    signed_url=_signed_url if os.getenv("ELEVENLABS_API_KEY") else None, evaluation=_evaluation))
