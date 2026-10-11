"""Live bounded synthetic Raindrop emit for one case (no participant data). Prints ids only."""
import json, sys, importlib.metadata
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from make_it_rain.backend.telemetry import RaindropCase
key = next((l.partition("=")[2].strip().strip("\"'") for l in (ROOT / ".env").read_text().splitlines() if l.startswith("RAINDROP_WRITE_KEY=")), "")
assert key, "no write key"
case = sys.argv[1]; conv = sys.argv[2]
fx = {json.loads(l)["_id"]: json.loads(l) for l in (ROOT / "integration/three_platform/atlas_ticket_fixtures.jsonl").read_text().splitlines()}
t = RaindropCase(key, case, conv, "SYNTHETIC: " + fx[case]["scenario_input"])
t.sink({"tool": "create_test_ticket", "input": {"case_id": case}, "output": {"status": "SYNTHETIC_OFFLINE_NOT_ATLAS"}, "duration_ms": 1})
out = t.finish("SYNTHETIC RESPONSE: escalation to staff is requested; no staff confirmation yet.")
out["sdk_version"] = importlib.metadata.version("raindrop-ai"); out["case_id"] = case; out["conversation_id"] = conv
print(json.dumps(out))
