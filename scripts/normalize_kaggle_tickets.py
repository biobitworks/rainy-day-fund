#!/usr/bin/env python3
"""Deterministic (no LLM) normalization of data.csv -> V2 ticket schema. Local/private output only.
Rules are heuristics and are labelled as such: category/action/tier are NOT verified event labels."""
import csv, hashlib, json, re, sys, collections
from pathlib import Path

SRC = Path(sys.argv[1]); OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
PID, SOURCE_ID, RULES = "RDF-SFTW26-NEW-001", "RDF-CSV-KAGGLE-DATA-01", "kaggle-norm-rules-v1"
csv.field_size_limit(10**7)
raw = SRC.read_bytes(); src_sha = hashlib.sha256(raw).hexdigest()
rows = list(csv.DictReader(open(SRC, newline="", encoding="utf-8")))

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"); PHONE = re.compile(r"(?<!\w)\+?\d[\d\s().-]{8,}\d(?!\w)")
INJECT = re.compile(r"ignore (all |any )?(previous|prior) instructions|system prompt|you are now|reveal .*(password|credential|key)", re.I)
CRED = re.compile(r"\b(password|passwort|contraseña|mot de passe|senha|credential|api key|token|2fa|otp)\b", re.I)
OTHER_ACCT = re.compile(r"\b(another|someone else|other (user|customer|account)|third party)\b", re.I)
KW = [("wifi", re.compile(r"wi-?fi|wlan|wireless|hotspot", re.I)),
      ("checkin", re.compile(r"check-?in|registration|badge|qr code|ticket scan", re.I)),
      ("accessibility", re.compile(r"accessib|screen reader|wheelchair|step-free|captions?|interpreter", re.I)),
      ("schedule", re.compile(r"schedule|session time|agenda|reschedul|maintenance window", re.I))]
QUEUE_CAT = {"Technical Support": "technical", "IT Support": "technical", "Product Support": "technical",
             "Service Outages and Maintenance": "technical"}  # everything else -> other
TIER = {"low": "T0", "medium": "T1", "high": "T2"}


def redact(s):
    s, e = EMAIL.subn("[EMAIL]", s); s, p = PHONE.subn("[PHONE]", s); return s, e + p


def classify(r):
    text = f"{r['subject']} {r['body']}"
    cat = next((c for c, rx in KW if rx.search(text)), None) or QUEUE_CAT.get(r["queue"], "other")
    inj = bool(INJECT.search(text)); cred = bool(CRED.search(text)); other = bool(OTHER_ACCT.search(text))
    if inj or (cred and other): action, split_force = "DENY_AND_ESCALATE", "adversarial"
    elif cred or cat in ("accessibility", "checkin"): action, split_force = "ESCALATE_STAFF", None
    else: action, split_force = "VERIFY_SOURCE", None   # no event-verified source exists for external tickets
    return cat, action, split_force


out, side, seen = [], [], set()
for i, r in enumerate(rows):
    tid = f"RDF-V2-KGL-{i:05d}"
    subj, n1 = redact(r["subject"]); body, n2 = redact(r["body"])
    cat, action, force = classify(r)
    bucket = int(hashlib.sha256(tid.encode()).hexdigest(), 16) % 10
    split = force or ("heldout" if bucket < 2 else "development")
    out.append({"project_id": PID, "ticket_id": tid, "source_id": SOURCE_ID, "source_version": "v2", "category": cat,
                "issue_description": (subj + " | " + body).strip(), "verified_context": [], "proposed_resolution": None,
                "expected_action": action, "escalation_tier": TIER.get(r["priority"], "T1"), "supporting_source_ids": [],
                "synthetic": False, "evaluation_split": split, "status": "UNEXECUTED"})
    side.append({"ticket_id": tid, "row_index": i, "language": r["language"], "orig_type": r["type"], "orig_queue": r["queue"],
                 "orig_priority": r["priority"], "answer_sha256": hashlib.sha256(r["answer"].encode()).hexdigest(),
                 "redactions": n1 + n2, "rules": RULES})

KEYS = {"project_id","ticket_id","source_id","source_version","category","issue_description","verified_context","proposed_resolution",
        "expected_action","escalation_tier","supporting_source_ids","synthetic","evaluation_split","status"}
ENUM_C = {"wifi","checkin","accessibility","technical","schedule","other"}
ENUM_A = {"SAFE_GUIDANCE","VERIFY_SOURCE","ESCALATE_STAFF","TEXT_ROUTE","DENY_AND_ESCALATE"}
checks = {"schema_keys": all(set(t) == KEYS for t in out), "enums": all(t["category"] in ENUM_C and t["expected_action"] in ENUM_A and t["escalation_tier"] in {"T0","T1","T2"} for t in out),
          "unique_ids": len({t["ticket_id"] for t in out}) == len(out), "no_fabricated_resolution": all(t["proposed_resolution"] is None for t in out),
          "no_email_after_redaction": not any(EMAIL.search(t["issue_description"]) for t in out)}
J = lambda rows_: "".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n" for x in rows_)
(OUT / "normalized_tickets_v2.jsonl").write_text(J(out)); (OUT / "normalized_tickets_v2.sidecar.jsonl").write_text(J(side))
rec = {"source_sha256": src_sha, "rules_version": RULES, "rows_in": len(rows), "rows_out": len(out), "checks": checks,
       "output_sha256": hashlib.sha256((OUT / "normalized_tickets_v2.jsonl").read_bytes()).hexdigest(),
       "category": dict(collections.Counter(t["category"] for t in out)), "expected_action": dict(collections.Counter(t["expected_action"] for t in out)),
       "split": dict(collections.Counter(t["evaluation_split"] for t in out)), "tier": dict(collections.Counter(t["escalation_tier"] for t in out)),
       "redacted_spans": sum(s["redactions"] for s in side), "synthetic_flag": "false (external dataset; synthetic status unverified)",
       "heuristic_notice": "category/action/tier derive from keyword+queue+priority rules, not verified event labels; answers NOT used as resolutions",
       "licensing": "UNRESOLVED - private only"}
(OUT / "normalization_receipt.json").write_text(json.dumps(rec, indent=2)); print(json.dumps(rec, indent=1))
