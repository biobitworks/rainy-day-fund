"""Offline validation of an Atlas import JSONL (no network, no Atlas). Writes a receipt; never claims persistence."""
import json, re, sys, hashlib, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from make_it_rain.backend.store import MemoryStore
p = Path(sys.argv[1]); rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
REQ = {"schema_version","project_id","record_id","event_time","observed_status","actor","source_version","idempotency_key","predecessor_id","synthetic","contains_personal_data","run_id","body"}
ALLOWED = {"v2_sources","v2_knowledge_cards","v2_tickets"}
PII = re.compile(r"(/Users/[A-Za-z0-9_.-]+|[\w.+-]+@[\w-]+\.[\w.-]+|\b\d{3}[-. ]\d{3}[-. ]\d{4}\b|mongodb(\+srv)?://)")
errs, seen_id, seen_idem, pii_hits = [], set(), set(), []
for i, r in enumerate(rows):
    d = r.get("document", {})
    if r.get("collection") not in ALLOWED: errs.append((i, "collection"))
    if REQ - set(d): errs.append((i, "missing:" + ",".join(sorted(REQ - set(d)))))
    if d.get("project_id") != "RDF-SFTW26-NEW-001": errs.append((i, "project_id"))
    if d.get("observed_status") != "PROPOSED": errs.append((i, "status"))
    k = (r.get("collection"), d.get("record_id"))
    if k in seen_id: errs.append((i, "dup_id"))
    seen_id.add(k)
    if d.get("idempotency_key") in seen_idem: errs.append((i, "dup_idem"))
    seen_idem.add(d.get("idempotency_key"))
    if PII.search(json.dumps(d)): pii_hits.append({"line": i, "collection": r.get("collection"), "record_id": d.get("record_id")})
st = MemoryStore(); first = second = 0
for r in rows: first += st.insert_if_absent(r["collection"], {"_id": r["document"]["record_id"], **r["document"]})
for r in rows: second += st.insert_if_absent(r["collection"], {"_id": r["document"]["record_id"], **r["document"]})
rec = {"file": str(p), "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "docs": len(rows), "schema_errors": errs[:20], "schema_error_count": len(errs),
  "unique_ids": len(seen_id), "unique_idempotency_keys": len(seen_idem), "first_pass_inserts": first, "second_pass_inserts": second,
  "idempotent_reimport_offline": second == 0 and first == len(rows), "pii_pattern_hits": pii_hits,
  "atlas_persistence": "NOT_TESTED", "store_used": st.kind, "observed_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
Path(sys.argv[2]).write_text(json.dumps(rec, indent=2)); print(json.dumps({k: v for k, v in rec.items() if k != "pii_pattern_hits"}, indent=1)); print("pii hits:", pii_hits)
