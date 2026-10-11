# New application contracts and exact setup

## Repo ownership / GitHub
1. Decide owner with Sophia. Existing repos named `make-it-rain` under unrelated users do not prevent a new owner namespace. Use https://github.com/new, PRIVATE, new empty repo, no fork.
2. After agreement only: `gh repo create OWNER/make-it-rain --private --source=. --remote=origin --push`. Set Git identity deliberately; retain exact initial SHA and `git log --reverse --format=fuller` creation history. Don't publish until both approve.
3. Make repo public by submission time; secret-scan every commit and GitHub Actions log. Do not commit `.env`, CSVs with personal data, signing keys, participants' contacts or recordings.

## Atlas (mandatory)
Official project ID: `6acba49b5c102b1d2b95a0ac` under hackathon organization `69ef9daf03d2ce35c2657862`; cluster: `Cluster0`. New DB `rainy_day_fund_sftw26`; old prebuild DB `event_continuum_rsi_20261011` excluded.

Suggested collections: `guide_versions`, `sessions`, `tickets`, `harness_versions`, `proposals`, `eval_plans`, `eval_runs`, `policy_decisions`, `progress_events`, `recovery_receipts`, `outbox`.

Required fields: `_id` deterministic, `project_id`, `schema_version`, `created_at`, `actor`, `source_id`, `source_version`, `predecessor_event_id`, `run_id`, `privacy_class`. Unique indexes on per-project event ID and idempotency keys. Separate public state from private participant contact records.

First end-to-end proof: synthetic `ticket_id` insert → exact readback → create authorized escalation event → kill worker process → restart from persisted `ticket_id` → compare recovered payload and ordered event IDs → attempt duplicate insert with same idempotency key (must not create second ticket) → negative private lookup (must deny). Record Atlas response and timing receipts; local-memory recovery is insufficient.

## ElevenLabs (optional voice; account user-reported set up)
1. In ElevenLabs Agents, create a **new** agent for `make-it-rain` scoped to event-support purpose. Do not claim official organizer authority.
2. Use the exact current event-guide version for informational answers; human-escalate accessibility requests, registration and policy disputes. Do not leak venue network passwords in public logs.
3. Configure signed/authenticated server tool/webhook calls to new backend; tool routes `get_ticket`, `open_ticket`, `escalate_ticket`, `get_public_event_fact` with least privilege; do not pass Atlas admin credentials or private participant data to the model.
4. Start with a web-based voice client if no telephone number exists; phone provisioning and international calling/SMS require separate verified configuration and consent controls.
5. Require an equivalent keyboard/screen-reader friendly accessible text interface with same `session_id` and ticket source-of-truth in Atlas. Voice transcripts require explicit notice, retention policy and consent.

## Service interface (contract, not deployed)
POST /sessions -> {session_id}
POST /tickets {session_id, category, source_version, idempotency_key} -> {ticket_id,status}
GET /tickets/{id}?session_id= -> {ticket_id,status,authorized_fields}
POST /tickets/{id}/escalations {reason} -> {event_id,queue}
POST /proposals {failure_summary,allowed_fields} -> {proposal_id,config_candidate}
GET /eval_runs/{id} -> {metrics,admission,provenance}

All paths authenticate and authorize independently of the agent's instructions. Persistent services must handle retries and disconnections. Crew/Ollarma cannot bypass policy gates; Kiro is implementation tooling, not product authority.

## Runnable Atlas recovery smoke (intentionally NOT executed in starter package)

```bash
pip install -r requirements-atlas.txt
export ATLAS_MONGODB_URI='mongodb+srv://...'; export MONGODB_DB='rainy_day_fund_sftw26'
python scripts/atlas_smoke.py write RDF-DEMO-20261011-001
# Terminate this Python process. A second invocation is a genuinely fresh process:
python scripts/atlas_smoke.py read RDF-DEMO-20261011-001
# Repeat write with same ID to observe idempotent existing record:
python scripts/atlas_smoke.py write RDF-DEMO-20261011-001
```

Never put the URI in notebooks, commits or screenshots. This smoke validates direct readback and new-process persistence; it does **not** establish backup recovery, multi-host independent verification or full service fault tolerance. For stronger cold recovery, stop and restart the actual application worker after a committed write, then verify ticket + event ordering and active harness version.