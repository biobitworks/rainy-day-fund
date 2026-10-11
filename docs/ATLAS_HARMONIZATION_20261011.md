# Atlas harmonization — verified successor, 2026-10-11

**Project:** `RDF-SFTW26-NEW-001`  
**Parent:** `RDF-ENV-002-SUCCESSOR` and PR #1 head `2bbe325205d4947b8c645d195fa7c5b1b58cde7f` (before this document)  
**Execution context:** MagicPro local source checks + connected MongoDB Atlas read-only discovery + GitHub CI + ElevenLabs authenticated metadata requests  
**Scope:** synthetic records only; this is an observation receipt, **not** a migration, new Atlas write, or an assertion of worker recovery.

## Decision and identity

- Official event Atlas organization: `69ef9daf03d2ce35c2657862`.
- Official event Atlas project: `6acba49b5c102b1d2b95a0ac`.
- Official event cluster: `Cluster0`, dedicated M10, AWS `US_WEST_1`, MongoDB `8.0.34`, state `IDLE` observed.
- Authoritative application database: `rainy_day_fund_sftw26`.
- Application's MagicPro `MONGODB_URI` host is `cluster0.wvfyho.mongodb.net` (matches official Atlas cluster); the parsed URI had no embedded username/password. Driver authentication from MagicPro **NOT_TESTED**.
- A separately provided Atlas browser link points to **different project** `6acbcaf68ec2c1911378a336`. Connected Atlas API denied listing clusters and DB users for that project (permission denied or project not found); its contents, owner, cluster and `byron_db_user` account are **NOT_VERIFIED**.
- **DECISION:** no cross-project migration, mirroring, alias, destructive schema change or production synchronization without an authorized read-only inventory plus explicit team approval. Atlas official project remains authoritative.

## Observations (not predictions)

1. Atlas live listDatabases included `rainy_day_fund_sftw26` and a distinct prebuild database `event_continuum_rsi_20261011`; no prior-project data was moved.
2. Application DB listCollections returned: `tickets`, `progress_events`, `proposals`, `eval_plans`, `eval_runs`, `policy_decisions`, `harness_versions`, `recovery_receipts` (8/8).
3. Synthetic, scoped readbacks with `project_id=RDF-SFTW26-NEW-001` included `SYN-TICKET-001`, ordered events `SYN-EVENT-001`/`SYN-EVENT-002`, and records for evaluation/proposal/admission/rejection/recovery receipts. Previous recovery receipt status represented connector readback only, not process-restart recovery.
4. GitHub PR #1 is open, draft, **unmerged**; head SHA `2bbe325205d4947b8c645d195fa7c5b1b58cde7f`. GitHub Actions run `38163606753` concluded `success`. Sophia `sophiepark22` has repository `write` permission.
5. MagicPro source HEAD matched pre-document PR head; local `python3 -m pytest -q tests` returned **8 passed**. Local deterministic synthetic harness reported baseline **5/8**, candidate **8/8**, `ADMIT`, unsafe control `REJECT`. This is not a real LLM-generated policy revision. Local runner reported a lab-only computed MMR root; **canonical external/project root NOT_COMPUTED**, **SIGNATURE NOT_SIGNED**.
6. ElevenLabs API `GET /v1/user` returned HTTP 200; list-agents returned HTTP 200, one agent in first page. MagicPro `ELEVENLABS_AGENT_ID` was empty at check time. Live voice/text continuity, webhooks, and per-session persistence **NOT_TESTED**.
7. MagicPro had untracked `provider_probe.py` and `provider_probe_receipt.json`. Not committed, and output was not accepted as verified evidence. A diagnostic attempt to parse the receipt as a single JSON document **FAILED** (`JSONDecodeError: Extra data`). Retain privately pending security and provenance review.
8. MagicPro did not have `pymongo` in the examined Python environment; the opt-in two-process Atlas smoke test **NOT_EXECUTED**. Existing notebook defaults to `NOT_TESTED`, not a pass.

## Required harmonization handshake for Sophia's agent

**Do not share passwords or tokens in chat, PR, logs, transcripts, or screenshots.** A database credential was pasted into chat; rotate it before any adoption. Create a dedicated least-privilege account for the specific selected project/cluster rather than reusing or assuming the credentials work across projects.

1. **Identify project:** Return sanitized organization ID, Atlas project ID, cluster ID/name, provider/region, database names, Atlas user roles and cluster-scoped access **without secret values**. Confirm whether the new browser-link project is a second workspace or meant to replace the official event sandbox.
2. **Choose one authority:** Both collaborators must approve the project and the database; until then use official `rainy_day_fund_sftw26` as authoritative. Do not write to both Atlas projects. Any cross-project copy requires explicit mapping and approved backfill protocol, not an unobserved claim of harmonization.
3. **Shared schema:** Freeze the record envelope `schema_version`, `project_id`, immutable `record_id`, `source_version`, `event_time`, `observed_status`, `actor`, `predecessor_id`, `idempotency_key`, `synthetic`, `contains_personal_data`; note that old fixtures do not necessarily conform. Read `docs/ATLAS_DATA_CONTRACT.md`.
4. **Deterministic transformation boundary:** New FCG/FC0-style bridge is an isolated, sanitized, read-only observer. Normalize allowlisted record fields with schema/version tags, stable sort order, UTC time representation, canonical UTF-8 JSON (sorted keys, compact separators, no NaN), and explicit null handling; capture exact ordered leaves, SHA-256 recipe, and independent recomputation only when executed. A hash proves identity/integrity, not physical energy, truth or causality. No copied FCO/FCG implementation, unverified signer, or invented external canonical MMR.
5. **Authorization boundary:** Voice and text use one scoped Atlas session/ticket ID; a phone number is a contact handle, not identity. Deny cross-session reads; do not create real participant tickets without consent. Staff-only transitions need human approval.
6. **Executable acceptance:** Two separate processes must write and recover one synthetic ticket with readback digest; actual worker crash/restart is a separate stronger test. Freeze the eval plan before an independently provider-generated typed proposal; run V0, candidate V1 and unsafe negative control on frozen held-out/adversarial splits; preserve rejected candidates. Pin all steps in top-to-bottom Jupyter with sanitized outputs.
7. **Deliver to PR #1:** Commit code, migrations (if approved), replay notebook, sanitized tests, run/check IDs, negative cases, and exact status classification. Keep PR draft/unmerged until both lane reviews. Do not push the private local `.env` or untracked probe files.

## Status

`VERIFIED_NEW`: Official Atlas project/cluster/database/collections/scoped synthetic readbacks; matching MagicPro URI host; GitHub CI success; local 8 tests; ElevenLabs auth metadata; Sophia GitHub write permission.

`EXECUTED`: Atlas metadata and scoped synthetic reads; local tests and synthetic runner; ElevenLabs account and agent-list metadata requests.

`OBSERVED`: Separate provided project ID inaccessible under the currently connected Atlas account. Application URI did not contain embedded DB credentials. No local `pymongo`. No configured ElevenLabs agent ID.

`FAILURES`: Secondary-project access denied; private probe receipt did not parse as a single JSON document. No secret-values disclosed.

`NOT_TESTED`: Authenticated MagicPro MongoDB driver connection, provider-generated RSI, worker crash/restart, text/voice continuity, cross-project migration or synchronization, canonical external FCO MMR.

`NEXT_ACTION`: Rotate pasted DB credential; Sophia supplies sanitized second-project inventory and explicit authority decision; configure a scoped authenticated URI on the chosen Atlas project; install pinned driver and run separate-process recovery; run authentic provider-proposed RSI and notebook evaluation; review both lanes before merging.
