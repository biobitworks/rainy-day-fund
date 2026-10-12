# Make It Rain — rainy-day-fund

**SF Tech Week Harness Engineering & Model Wrangling Hackathon · October 11, 2026**

**Current team:** Solo submission (user-reported); former team handoff files are historical. See [team-status successor](docs/TEAM_STATUS_SUCCESSOR_20261011.md). Active project work is not an official Cerebral Valley attendee-support service.

**Primary track:** Recursive Harnessing. **Secondary focus:** Long Horizon Engineering, only within experimentally supported bounds.

## Submission-ready links

- **[Public repository and evidence overview (`main`)](https://github.com/biobitworks/rainy-day-fund)**
- **[Submission packet: sponsor contributions, implementation steps, status evidence, demo storyboard, and blockers](https://github.com/biobitworks/rainy-day-fund/blob/main/SUBMISSION_2026-10-11.md)**
- **[Public static Vercel walkthrough](https://rainy-day-fund-sftw26.vercel.app/)** (not a connected attendee dashboard)
- **[Protected preview of the Python API and live-dashboard UI](https://rainy-day-fund-sftw26-cohw995ik-biobitworks.vercel.app/)** (SSO; integration remains unconfigured)
- **One-minute YouTube video:** **PENDING** final editing, public upload and verified URL.

The available participant guide requires a public repository and 60-second video by **5:00 PM PDT on October 11, 2026**. This branch does not assert submission receipt.

## Sponsors and the verified claim boundary

| Platform | Implemented / observed | Not achieved |
|---|---|---|
| **MongoDB Atlas** | Authoritative `rainy_day_fund_sftw26` sandbox, synthetic tickets and evaluation receipts; independent direct insert/readback | Provider webhook → Atlas live ticket readback |
| **ElevenLabs** | Voice/text support design, tested dialogue, signed webhook and ticket tool adapters | Configured live agent ID/secret and signed conversation-to-Atlas test |
| **Raindrop.ai** | Local SDK/Workshop instrumentation; SDK handoff and guarded operator receipt code | Independently correlated cloud trace and Judge result |
| **Kiro / harness** | New repo workflows, frozen cases, bounded proposed-policy tests and decisions | Broad autonomous hosted improvement or tested long-horizon recovery |
| **Vercel** | Static production walkthrough; guarded FastAPI routes and authenticated polling dashboard on protected preview | Fully configured and promoted production live app |

**Critical result:** Three-platform success **NOT_ACHIEVED**. The effective local `MONGODB_URI` lacked user/password. `ELEVENLABS_AGENT_ID` and `ELEVENLABS_WEBHOOK_SECRET` were not set locally; preview environment configuration was also missing. The backend intentionally fails closed. Production was **not** promoted or modified by the backend preview build.

## Implemented code

- [`src/make_it_rain/backend/live.py`](src/make_it_rain/backend/live.py): `GET /api/health`, `/api/tickets`, `/api/events`; `POST /api/tools/create-ticket`, `/api/tools/update-ticket`, `/api/webhooks/elevenlabs`; plus guarded operator evidence recording. Signed webhook verifies the raw body and replay age; duplicate deliveries are idempotent; content transcripts are not persisted.
- [`src/make_it_rain/backend/store.py`](src/make_it_rain/backend/store.py): MongoDB store, local doubles and unconfigured-store refusal behavior. Synthetic-only ticket controls, separate tool/viewer/operator authentication, no-store responses.
- [`public/index.html`](public/index.html): Accessible voice/text controls, 2-second authenticated `no-store` polling, tickets and event timeline, policy/evaluation stages and a polling-latency label (not push streaming).
- [`tests/test_live.py`](tests/test_live.py): Local auth, duplicate and conflict, safety and signature checks. Webhook transcript privacy test asserts the **specific user content** is not retained (not merely absence of a field name).
- [`api/index.py`](api/index.py), [`vercel.json`](vercel.json), [`requirements.txt`](requirements.txt), [`.vercelignore`](.vercelignore): deployment entry point and dependency contract.

## Executed versus not tested

The development handoff reports **14/14** focused offline backend tests passing; full suite **102 passed, 2 failed, 1 skipped** (two pre-existing Raindrop SDK smoke-test failures). These are **reported tests**, not newly independently replayed in this documentation update.

A separate authenticated MongoDB connector test was **EXECUTED** and independently **OBSERVED** exact synthetic write/readback (1/1) plus persisted successor receipt. This is not evidence of a successful ElevenLabs webhook.

- **OFFLINE PASS (reported):** auth denial, payload conflict, stale/tampered signature rejection, duplicate/replayed webhook, cross-conversation isolation, synthetic-only filtering, fail-closed store, escalation gate.
- **PREVIEW ONLY (reported):** `/api/health` HTTP 200 `UNCONFIGURED_FAIL_CLOSED`, `/api/tickets` HTTP 401 without viewer key, static dashboard served under SSO.
- **NOT_TESTED:** Real ElevenLabs conversation and signed webhook; live Atlas provider write/readback; Raindrop Cloud trace/Judge; measured dashboard latency; real microphone-failure fallback in the integrated app.
- **NOT_COMPUTED / NOT_SIGNED:** canonical project MMR root and authorized signature. Earlier lab-only roots do not validate external behavior.

## Isolated environment and offline tests

Keep credentials outside Git and use an isolated environment on the authorized local development machine:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-dev.txt
PYTHONPATH=src python -m pytest -q tests/test_live.py
PYTHONPATH=src python -m pytest -q
```

These are **instructions**, not commands newly executed by this README update. A full passing unit suite still cannot prove a live cross-provider integration. Do not put `.env`, voice recordings, provider keys, or attendee personal data into the public repository.

## Older synthetic harness and recovery experiments

See [implementation gates](docs/IMPLEMENTATION_GATES.md), [Atlas/ElevenLabs interface](docs/ATLAS_ELEVENLABS_SETUP.md), and [sync and custody discipline](docs/SYNC_AND_CUSTODY.md). Earlier deterministic synthetic improvement comparisons are **not** real-world latency or model-proposed production adaptation. Preserve frozen fixtures, failed candidates and predecessor evidence. Previously developed FCO/FCG/Seedgraph implementations remain separately licensed and are not bundled dependencies.

**Publication/ownership caveat:** Existing LICENSE and historical team documents are not proof of copyright assignments, contributor-specific approvals or rights for all media. Asset/security review remains necessary.

**NEXT_ACTION:** Obtain credentials and configured provider endpoints by a secure local path; deploy and independently test an authorized synthetic conversation → signed webhook → Atlas readback → Raindrop cloud receipt before claiming live integration. Keep production static until promotion explicitly authorized.
