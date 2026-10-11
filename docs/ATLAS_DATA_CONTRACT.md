# MongoDB Atlas — observed schema, proposed contracts and executable acceptance criteria
**Scope:** org `69ef9daf03d2ce35c2657862` / project `6acba49b5c102b1d2b95a0ac` / cluster `Cluster0` / DB `rainy_day_fund_sftw26`. **Environment:** official 2026 SFTechWeek hackathon Atlas sandbox. **Status:** read-only collection/schema inspection; no index changes or production writes were made for this document.

## Collections already OBSERVED
| Collection | Existing observed document keys (sample, not exhaustive) | Purpose |
|---|---|---|
| `tickets` | `project_id, record_id, ticket_id, session_id, scope, state, owner_role, source_version, event_time, observed_status, actor, idempotency_key, predecessor_id, synthetic, contains_personal_data` | ticket state snapshots |
| `progress_events` | `project_id, record_id, ticket_id, sequence, event_type, source_version, observed_status, synthetic` | ordered changes |
| `proposals` | `project_id, record_id, parent_harness_version, candidate, proposer_kind, basis_digest, change, idempotency_key, synthetic` | bounded harness candidates |
| `eval_plans` | `project_id, record_id, fixture_digest, oracle_version, split_manifest, immutable_since, synthetic` | frozen evaluation oracle |
| `eval_runs` | `project_id, record_id, metrics, observed_status, actor, synthetic` | measured comparisons |
| `policy_decisions` | `project_id, record_id, proposal_id, outcome, reason, oracle_version, synthetic` | admit/reject history |
| `harness_versions` | `project_id, record_id, version, config, config_digest, admission, synthetic` | immutable configurations |
| `recovery_receipts` | `project_id, record_id, ticket_id, recovered_state, readback_ids, event_count, observed_at, correction, synthetic` | recovery claim/observations |

Existing collections use server-generated ObjectIds for `_id`. All business queries should also filter by `project_id`. **Caveat:** different fixtures and later code may use different shapes; no global schema validation is yet verified.

Readback examples: existing synthetic `SYN-TICKET-001` has `state=ESCALATED`; two ordered progress events have sequence 1/2; a correction-successor recovery receipt describes the timestamp repair. THESE ARE CONNECTOR REPLAY OBSERVATIONS, NOT process-failure recovery.

## Proposed strict shared envelope for NEW records
```json
{
  "schema_version": "rdf.event.v1",
  "project_id": "RDF-SFTW26-NEW-001",
  "record_id": "RDF-EVT-demo-0001",
  "event_time": "2026-10-11T18:00:00Z",
  "observed_status": "EXECUTED",
  "actor": "model-bridge:local",
  "source_version": "GUIDE-V0-SYNTHETIC",
  "idempotency_key": "RDF:demo:0001",
  "predecessor_id": null,
  "synthetic": true,
  "contains_personal_data": false
}
```
Use this as new record shape only; do **not** claim historical fixture rows conform. `record_id` is identity within project; `idempotency_key` protects retries; `predecessor_id` is a declared lineage pointer; `event_time` should be actually measured, never invented in execution receipts. A public demo must use wholly synthetic data.

## Proposed indexes (NOT VERIFIED APPLIED)
- All eight: unique `{project_id:1, record_id:1}` where data are known unique; inspect/preflight duplicates before creation.
- `tickets`: `{project_id:1, ticket_id:1}` unique as applicable; `{project_id:1, session_id:1}`.
- `progress_events`: `{project_id:1, ticket_id:1, sequence:1}` unique if backfill validates; `{project_id:1, event_time:1}`.
- `proposals`: `{project_id:1, parent_harness_version:1}`.
- `eval_runs`: `{project_id:1, record_id:1}`, `{project_id:1, observed_status:1}`.
- `recovery_receipts`: `{project_id:1, ticket_id:1, observed_at:-1}`.
- `sessions`, `guide_versions`, `channel_observations`, `outbox`: proposed collections; create only when actually needed and authorized.

## Recommended document lifecycle
1. `Session` is opened with a pseudonymous server-issued ID. Phone/caller ID is not authentication, and transport-channel preference is not identity.
2. `Ticket` created with verified session authorization, a unique idempotency key, `synthetic=true` for demo, and a recorded source version.
3. Every state change appends a `progress_events` record in sequence. Never claim atomicity unless code enforces transactional writes; maintain a tested retry/idempotency strategy.
4. `Proposal` carries base-harness ID, allowed typed change and proposer/model receipt (provider, model, prompt digest, token usage when measurable).
5. `EvalPlan` and held-out cases frozen before exposing development signals. Evaluator computes results independently; agent cannot change oracle.
6. `PolicyDecision` records ADMIT/REJECT/ABSTAIN and reasons. `HarnessVersion` adds a successor only if gates pass; never mutates predecessor.
7. `RecoveryReceipt` records actual process identity before and after restart, ordered event IDs, expected/observed digests, timestamp, explicit PASS/FAIL.
8. External FCO observer may consume ONLY approved redacted hashes, timestamps and status events; it does not control active Atlas state or establish causality.

## Public demo flow and expected measurements
- Create `RDF-DEMO-...` ticket in Atlas (scope-limited, synthetic); retry same idempotency key, assert one ticket.
- Append escalation event and read ordered history.
- Terminate the worker; reconnect from another process; recover exact canonical ticket state and ordered event list.
- Propose stale-rule fix through a real model-generated structured output; evaluate frozen baseline/candidate and unsafe negative control; record accuracy, tool calls, duration, cost/tokens when actually measured.
- Through ElevenLabs agent + accessible text, resolve one authorized session to the same `ticket_id`; deny attempt to read a different session's ticket.
- Link a versioned guide atom → source occurrence → ticket and decision → evidence record → demo claim; retain unknown attribution and failed experiments.

## Privacy and secret boundaries
Never store passwords, signing keys, API tokens, real phone numbers, medical/accessibility narratives, caller recordings or user-provided private documents in public GitHub or synthetic fixtures. Consent and intended data use must be documented before collecting live participant records. Keep environment variables in ignored `.env` with mode 600; ensure Git history is scanned before publication.
