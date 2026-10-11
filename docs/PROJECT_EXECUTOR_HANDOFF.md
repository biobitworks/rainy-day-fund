# PROJECT EXECUTOR HANDOFF — Make It Rain / rainy-day-fund
**Revision:** RDF-HANDOFF-20261011-004 | **Audience:** Sophia Park (`sophiepark22`), Kiro IDE/CLI/Crew, the separate rainy-day-fund ChatGPT Project | **GitHub:** https://github.com/biobitworks/rainy-day-fund

## Read this first
This is a fresh, 2026-10-11 hackathon project. It is NOT Vithia, Vita DAISY, Antigence, prior Ollarma implementations, or earlier Event Continuum source. Those are prior art / externally separated observer systems; do not vendor/copy their implementation or claim it as newly made today. All published source must be licensed and attributed appropriately. The event requires a public repository, hackathon-provided Atlas, a one-minute video and submission by 5 PM Pacific; demo ONLY event-built features.

**Product:** "Make It Rain", optionally described as a multilingual, accessible event-support harness. **Competition focus:** an agent discovers a regression, proposes a *bounded config change*, tests against frozen held-out cases, independently rejects unsafe behavior, persists state, recovers on a new process, and reports verifiable measurements. Do NOT let a dashboard or basic RAG become the main feature.

## Verified existing system (not a promise)
- Public repository `biobitworks/rainy-day-fund`; `main` retains initial README+Apache-2.0 license. Review branch `review-20261011` has new synthetic harness, tests, notebook, CI, integration docs.
- Draft team PR: https://github.com/biobitworks/rainy-day-fund/pull/1 . Sophia `sophiepark22` has GitHub **write** permission at last read. Team approval was reported verbally by project owner; code-specific approval/review is still pending.
- New-source synthetic local benchmark V0 5/8 to V1 8/8, unsafe control rejected; GitHub Actions passed, including pytest, deterministic independent replay and Jupyter. This is a **deterministic proposer**, NOT an LLM-generated improvement and NOT evidence for real participants.
- MongoDB Atlas official hackathon org `69ef9daf03d2ce35c2657862`, project `6acba49b5c102b1d2b95a0ac`, `Cluster0` (AWS M10); application DB `rainy_day_fund_sftw26` exists with synthetic records. Eight observed collection names: `tickets`, `progress_events`, `proposals`, `eval_plans`, `eval_runs`, `policy_decisions`, `harness_versions`, `recovery_receipts`.
- Atlas connector recovery receipts include a corrected timestamp successor; they DO NOT prove an application process was killed and restarted.
- ElevenLabs **account setup is user-reported**, `agent_id`, authenticated webhook call, inbound phone, text/voice round trip are **NOT_VERIFIED**.
- magicPRObox local working directory `/Users/byron/projects/active/rainy-day-fund` reportedly contains a mode-600 ignored `.env` in TextEdit; **user-reported device-local receipt**, not independently revalidated in this GitHub handoff. Directory initially was not a Git checkout. DO NOT open, read, transmit, paste or commit secret values. Existing file must be preserved if setting up checkout.

## Who does what
| Lane | Proposed owner | Must deliver |
|---|---|---|
| Sophia | UI / ElevenLabs / Kiro | keyboard- and screen-reader-accessible text path; one bounded ElevenLabs voice agent and authenticated backend tool; voice/text refer to same authorized ticket |
| Backend partner | Atlas / data / verification | scoped DB adapter, indexes, idempotent tickets/events, actual new-process recovery, held-out evaluator, signed/unsigned receipt accuracy |
| Joint | Integration | freeze tests, evaluate a **real model-origin proposal**, negative-control denial, user privacy and Apache-2.0 rights review, demo/video/submission |

## Exact data and API contracts
Read `docs/ATLAS_DATA_CONTRACT.md` and `schemas/agent_tools.v1.json`. Do not independently rename fields: `project_id`, `record_id`, `event_time`, `source_version`, `observed_status`, `actor`, `predecessor_id`, `idempotency_key`, `synthetic`; cross-channel keys `session_id`, `ticket_id`, `conversation_id` (where relevant). Pass opaque IDs only, never phone number as authentication.

All ElevenLabs tools call the **backend**, not Atlas directly. Tools: `get_public_event_fact`, `open_synthetic_ticket`, `get_authorized_ticket`, `escalate_synthetic_ticket`. Authorization is server-side with a configured secret and session authorization/consent; all writes idempotent. `synthetic=true` for publicly shareable test data.

**Observed vs proposed:** the eight existing Atlas collections are observed. `sessions`, `guide_versions`, `channel_observations`, `outbox` are PROPOSED and should not be presented as existing until created/read back. Links are declarations, not proof of causality.

## Credential instructions — no secret values in Git
Device-local `.env` keys reported by user:
```dotenv
ELEVENLABS_API_KEY=
ELEVENLABS_AGENT_ID=
ELEVENLABS_WEBHOOK_SECRET=
MONGODB_URI=
```
The repository currently accepts `MONGODB_URI` or `ATLAS_MONGODB_URI` via `src/make_it_rain/config.py`. If both are set, existing code prefers `ATLAS_MONGODB_URI`; conflict-denial validation is NOT_IMPLEMENTED. Set only one. The current Atlas smoke script calls `load_env()` to read a mode-600 `.env` in the checkout root; an `.env` residing in the separate pre-checkout folder will NOT be automatically loaded. Preserve and transfer it locally only, never through Git or chat. Do not run `cat .env` or send secrets to a chat/log. API keys are not evidence of a successful call; verify with a non-secret status response. Use restrictive database credentials, not an Atlas organization-admin key.

## Kiro and device handoff
1. In Kiro, open the cloned repo and read `AGENTS.md`, `.kiro/steering/rainy-day-fund.md`, this handoff and `docs/EXECUTOR_FIRST_PROMPT.md`.
2. On magicPRObox, **inspect whether `.git` exists first**. If not a checkout, clone into a NEW directory, then **move/copy the pre-existing ignored `.env` locally with mode 600** after the clone. Do not clone over, overwrite, or delete the current secret-containing directory.
3. Work on a new branch from the current review branch or submit your own PR. Keep changes separately attributable and avoid force push or rewriting predecessor commits.
4. Run `python -m pytest -q`, `python scripts/run_local.py`, `python scripts/independent_verify.py`, the Jupyter notebook(s). Include platform, Python, dependency versions and observed outputs in receipts.
5. Before live Atlas writes, run opt-in `scripts/atlas_smoke.py write RDF-<unique-synthetic-id>` on a configured host, followed by `read` in a **new process** and compare digests; do not reuse past fixture IDs. Label synthetic-only.
6. Expose backend tools only behind authenticated HTTPS, restrict them to the event project DB, and verify one synthetic voice→text ticket continuity trace.
7. Freeze the evaluation set and programmatically record proposal/model origin, change diff, held-out metrics, guardrail outcome and predecessor. A scripted policy selector alone does not meet the full autonomous RSI target.
8. Before public demo, inspect code, licenses, assets, recording consent, Git history, CI receipts, and submit only once explicitly approved.

## Priority order
P0: live Atlas worker recovery + actual model-origin bounded proposal + safety denial + notebooks.
P1: accessible text and ElevenLabs voice/text continuity.
P2: external FCO observer, Ollarma multi-host fallback, live ASL avatar, haptics and smart-cane support. Keep optional integrations out of the critical-path unless genuinely working.

## What cannot be claimed yet
No successful live phone call; no official organizer endorsement; no real attendee accessibility resolution; no arbitrary billion-token empirical run; no signed canonical FCO/MMR commitment; no scientifically validated agent; no Atlas process crash-recovery test; no complete event submission. Record observed failures as immutable successors, not overwritten success.

## Evidence and progress reporting
Each meaningful change must record `ConversationFCO/turn` equivalent: PARENT | repo/branch/commit | actors | source/version | executed actions | observations | failures | proposals | NOT_TESTED | NEXT_ACTION. Use exact event and source IDs where possible. Content hash != semantic identity; FCG relationships != causality; Merkle inclusion != truth. Do not claim SIGNED without verified signer, and MMR_COMMITTED requires exact leaf order, peaks, construction, root and independent receipt.

## Next action
Sophia: implement verified, least-privilege tool path, then show the same synthetic ticket via accessible text and ElevenLabs. Backend: run real new-process Atlas recovery and instrument a provider-origin harness improvement. Each lane pushes to GitHub and opens/updates a reviewable PR with raw test receipts.
