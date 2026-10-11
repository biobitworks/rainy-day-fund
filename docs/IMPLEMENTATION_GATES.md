# Implementation gates / evidence limits — 2026-10-11

## GitHub custody
- Verified repository: biobitworks/rainy-day-fund (public); initial commit 2434e41270ce021b845fa0e493daea51499ccfe2 at 10:44:49 AM PDT, after hackathon start.
- Initial repo contained README and Apache-2.0 LICENSE only. This review successor must be committed separately.
- Sophia @sophiepark22: user reports verbal approval. GitHub collaborator write access is NOT_VERIFIED. Do not imply her acceptance of specific patches, copyright assignments or license choices.

## Atlas observed
- Official hackathon org 69ef9daf03d2ce35c2657862; project 6acba49b5c102b1d2b95a0ac; Cluster0 AWS M10.
- Database rainy_day_fund_sftw26 exists. A read-only inspection returned counts: tickets=1; progress_events=2; policy_decisions=2; proposals=2; eval_runs=2; eval_plans=1; harness_versions=2; recovery_receipts=2.
- A receipt readback reported a synthetic ticket and ESCALATED state; prior receipt contained an illustrative time corrected by a successor. This DOES NOT prove worker termination/restart or transactionality.
- The older event_continuum_rsi_20261011 namespace is prebuild, excluded from this submission evidence.

## Local source package (separately generated after start)
- Previous standalone starter package path: MAKE_IT_RAIN_RSI_TEAM_STARTER_20261011.zip, supplied in ChatGPT conversation; source files are not automatically part of this GitHub repository.
- Independent rerun here: 6/6 unit tests PASS; baseline 5/8, deterministic candidate 8/8; unsafe candidate REJECT; independent MMR replay PASS; lab root c0e7b49aa2ebff832d2c01600cea910b68dbb7fa2f58b21160866be8b67ce7f8.
- These are synthetic/local test claims and NOT an LLM-generated proposal, hosted cold-restart, canonical custody commitment, or signed receipt.

## Highest-priority executable gates
1. Upload and independently run the new source code and frozen tests as fresh hackathon commits.
2. Verify scoped synthetic Atlas ticket insert/readback + idempotent retry; kill/restart the app worker and replay ticket and two ordered event records.
3. Freeze evaluation oracles, get a real model-proposed bounded configuration, compare V0/V1 on held-out cases, and reject unsafe candidate.
4. Connect ElevenLabs to authenticated tools and have voice and accessible text retrieve the same Atlas ticket. If unavailable, record NOT_TESTED and demo the text path.
5. Provide executable Jupyter notebook(s), actual observed metrics, exact predecessor/order/peaks/root if MMR claimed, and independent replay. Do not claim SIGNED without verified signing authority.
6. Final secret scan, two-person review, public repository, one-minute video and submission confirmation by 5 PM PDT.

## Safety / licensing
- Never include participant reports, PII, venue Wi-Fi credentials, API keys, recordings or private source code in the public repository.
- Published FCO/FCG algorithms and prior papers may be cited as prior art; copying old implementation requires separately verified rights and is not hackathon-original code.
- Atlas Agent Engine policy controls apply only when invoked through its governed wrappers; otherwise implement and explicitly label your own permission gate.
