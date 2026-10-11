# Make It Rain — SF Tech Week 2026 submission packet

**Status (October 11, 2026):** Public submission documentation; **not a claim of completed submission or three-platform end-to-end integration**.

- **Project title:** Make It Rain
- **Subtitle:** An event support agent that tests whether it can improve its own troubleshooting
- **Track:** Recursive Harnessing (primary); Long Horizon Engineering (secondary, limited to demonstrated duration)
- **Presenter/team status:** Solo submission, per project-owner update on 2026-10-11. Older collaboration references are historical, not active team membership.
- **Submission cutoff:** 5:00 PM PDT on October 11, 2026, per the locally available event participant guide. Portal receipt: **NOT_OBSERVED**.
- **Event:** [Harness Engineering & Model Wrangling #SFTechWeek Hackathon](https://cerebralvalley.ai/e/mongodb-sftw-hackathon)

## Permanent project links

| Item | URL | Evidence qualification |
|---|---|---|
| Public repository | https://github.com/biobitworks/rainy-day-fund | Public, observed |
| Repository's public landing README | https://github.com/biobitworks/rainy-day-fund/blob/main/README.md | Submission narrative, not an execution receipt |
| Implemented backend, tests and dashboard branch | https://github.com/biobitworks/rainy-day-fund/tree/review-20261011 | Review branch, not merged to main |
| Backend routes | https://github.com/biobitworks/rainy-day-fund/blob/review-20261011/src/make_it_rain/backend/live.py | Source implementation, not provider execution |
| Offline integration tests | https://github.com/biobitworks/rainy-day-fund/blob/review-20261011/tests/test_live.py | Tests against local doubles |
| Accessible dashboard | https://github.com/biobitworks/rainy-day-fund/blob/review-20261011/public/index.html | Frontend source; live behavior unverified |
| Static public evidence walkthrough | https://rainy-day-fund-sftw26.vercel.app/ | Production static walkthrough, not connected dashboard |
| Separate protected preview | https://rainy-day-fund-sftw26-cohw995ik-biobitworks.vercel.app/ | Preview route smoke was reported; protected by Vercel SSO |
| One-minute YouTube video | **PENDING—insert actual public video URL after upload and verification** | Do not invent a link |

> Use the public static walkthrough for an accessible public link. Do not advertise the protected preview as an unauthenticated, working app. A video being edited or recorded is not a publicly verifiable video permalink.

## Suggested submission text (accurate claim ceiling)

**Make It Rain** is an accessible event-support agent prototype designed for conferences, festivals, campus events and other venues. Attendees can request help with check-in, connectivity, microphones or accessibility. The design preserves synthetic support tickets and progress in MongoDB Atlas, supports voice with a text fallback, and escalates only after an explicit unsuccessful troubleshooting step.

The distinctive engineering problem is **recursive harnessing**: propose a bounded change to the assistant's operational strategy, test it against frozen synthetic cases and adversarial checks, then admit, reject or quarantine the candidate without allowing the agent to rewrite graders, authorize itself or conceal failures. State changes and their provenance are intended to survive interruption and support independent replay.

The new backend, dashboard and authentication controls were implemented on a review branch and tested offline. A live cross-provider conversation → signed webhook → Atlas → Raindrop Cloud → dashboard receipt was **not** achieved by this submission snapshot. The deployment preview fails closed without credentials. We preserve those gaps and the evidence that does exist rather than presenting a simulated workflow as a production result.

## Sponsor / platform implementation trail

### MongoDB Atlas — persistent, authoritative event state
1. Chose the event-provided Atlas project and **Cluster0** and isolated the new application database as `rainy_day_fund_sftw26`; excluded the pre-build `event_continuum_rsi_20261011` database.
2. Created/stored synthetic tickets, fixture datasets, progress events, proposals, evaluation runs, policy decisions, and recovery receipts, with source versions, event/actor references, and explicit statuses.
3. Independently confirmed connection, 22 available collections, and a synthetic direct Atlas write/readback with an exact field match and a successor receipt. This proves **direct Atlas persistence only**, not the ElevenLabs ingress.
4. Implemented a fail-closed backend store path that declines to report success without a configured authenticated Atlas URI. The effective local URI supplied to the later backend lacked username/password; hosted preview Atlas operations therefore remained **BLOCKED_CREDENTIALS**.

### ElevenLabs — voice and accessible text agent
1. Prepared attendee guide lookup, voice support, text fallback and tool/webhook integration contract.
2. Earlier test conversations and microphone/text fallback were reported; this is not equivalent to a completed provider-to-Atlas ticket.
3. Implemented candidate endpoints for signed `post_call_transcription` receipt ingestion and idempotent ticket creation/update, with stale-signature rejection, payload conflict detection, synthetic-only gating and no retained transcripts.
4. **NOT_TESTED:** Live authenticated agent ID and webhook secret, successful provider-signed request, actual conversation-to-Atlas readback or cross-channel recovery. Real credentials must be installed securely, never committed.

### Raindrop.ai — observability, trace and Judge feedback
1. Instrumented local SDK/Workshop traces and inspected earlier smoke traces; identified the requirement to distinguish current-user input and full assistant output from logging envelopes.
2. The review backend prepares Raindrop SDK handoff from verified webhook content; an operator receipt route may record cloud trace/Judge evidence only after an actual verified webhook exists.
3. Existing Raindrop SDK smoke tests include two known failures in the handoff report.
4. **NOT_TESTED:** Matching provider conversation ID → Cloud trace → Judge verdict → Atlas receipt. Do **not** label a local SDK invocation as verified cloud ingestion or improved latency.

### Kiro / harness workflow — constrained development and testing
1. Wrote implementation gates and a reviewable repository handoff for agent-assisted development.
2. Implemented frozen synthetic cases and local bounded proposal/evaluation logic with policies that block self-changing graders, permissions or credentials.
3. Maintained predecessor-linked records and explicit ADMIT / REJECT / QUARANTINE outcomes. Local and Atlas records do not prove a general-purpose self-improving agent or a long-horizon production run.
4. **NOT_TESTED:** Broad autonomous hosted propose-test-admit cycles with an independently verified worker restart.

### Vercel — intended single public application
1. Deployed a **static public evidence walkthrough** to the production hostname.
2. Implemented Python backend routes and a dashboard with accessible text controls and 2-second authenticated polling on `review-20261011`.
3. A subsequent **SSO-protected preview** was reported to serve `GET /api/health` and reject unauthorized dashboard reads. Its health status was `UNCONFIGURED_FAIL_CLOSED`.
4. **BLOCKED:** A working production backend, Atlas URI credentials, ElevenLabs agent ID, webhook secret and independently verified dashboard update. The production website was **not replaced** by the preview.

## Actual test and demonstration results

| Assertion | Status | Source / ceiling |
|---|---|---|
| Direct synthetic Atlas insert and exact readback | **EXECUTED / OBSERVED PASS** | Independent Atlas connector probe on 2026-10-11; receipt persisted in `integration_observations` |
| Synthetic dataset and evaluation records exist in Atlas | **OBSERVED** | Atlas collection/record inspections; not provider-generated |
| Focused backend tests | **USER-REPORTED OFFLINE PASS, 14/14** | Development handoff; independent fresh rerun NOT_TESTED in this packet |
| Full offline suite | **USER-REPORTED: 102 passed, 2 failed, 1 skipped** | The two existing failures concern Raindrop SDK smoke tests |
| Preview `/api/health` 200 and `/api/tickets` 401 without key | **USER-REPORTED EXECUTED** | Authenticated `vercel curl`; full Atlas backend not configured |
| Real ElevenLabs conversation to signed webhook | **NOT_TESTED** | Missing local agent ID and webhook secret |
| Signed webhook to authoritative Atlas live ticket | **NOT_TESTED / BLOCKED_CREDENTIALS** | Effective URI incomplete; not attempted live |
| Raindrop Cloud trace correlated with conversation + Judge verdict | **NOT_TESTED** | No independent cloud receipt |
| End-to-end troubleshooting time or improvement over V0 | **NOT_DEMONSTRATED** | Synthetic procedure evaluations and lookup-only benchmark are not end-to-end latency metrics |
| Live dashboard polling latency and microphone failover | **NOT_TESTED** | Offline UI code not production observation |
| Full three-platform integration | **NOT_ACHIEVED** | Honest disclosure |
| Production promotion of preview | **NOT_EXECUTED** | Static production preserved |
| Canonical project MMR root and authorized signature | **NOT_COMPUTED / NOT_SIGNED** | No canonical custody claim |

## One-minute video: suggested chapter structure

A public 60-second video should show **what was genuinely observed**, and put `NOT_TESTED` beside unverified integrations. Suggested chapters:

- **0:00–0:08 — Problem:** Attendees run into microphone, access and connectivity problems; voice alone is insufficient.
- **0:08–0:20 — Atlas:** Show an authorized, redacted synthetic record and readback receipt, not private participant data.
- **0:20–0:32 — ElevenLabs:** Show an actual recorded voice/text fallback if consent and publication review permit; label unverified ticket webhook `NOT_TESTED`.
- **0:32–0:43 — Raindrop:** Show only a real available local trace or SDK output; explicitly distinguish Cloud Judge receipt `NOT_TESTED`.
- **0:43–0:54 — Recursive harness:** Show a frozen baseline, bounded candidate, tested result, and policy admit/reject using actual synthetic receipts. Avoid claiming real-world speedups.
- **0:54–1:00 — Honest finish:** Public Vercel evidence walkthrough, protected preview, remaining integration block and repository URL.

Before publishing, verify the exact YouTube video is public and one minute long; check permissions, license/attribution, absent secrets, participant consent and an actually reachable URL. Do not insert an unverified URL.

## Next integration gate (not a submission success claim)

Restore authorized local command access, add **scoped** Atlas credentials and ElevenLabs secret material using private environment settings, provision separate operator/tool/viewer keys, deploy preview backend, then run one synthetic conversation with signed webhook, exact Atlas readback and correlated Raindrop trace. Independently measure dashboard polling if successful. **No silent production promotion.**

## Provenance and exclusions

This document is a later submission-documentation successor and does not overwrite historical test results. Previously developed FCO/FCG/Seedgraph work remains external inspiration, not bundled implementation. Historical collaboration files do not denote current team members. Personal contact data, private media, full transcripts and credential bytes do not belong in this public repository. Public Apache-2.0 license and rights/asset audit must be interpreted within actual contributor ownership; publication approval is not implied by this document.
