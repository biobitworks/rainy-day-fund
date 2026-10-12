# Make It Rain — rainy-day-fund

## SF Tech Week submission — October 11, 2026

**Solo project · Recursive Harnessing · honest integration status**

- **[Submission details, sponsor-by-sponsor build trail, evidence table and 60-second video outline](SUBMISSION_2026-10-11.md)**
- **[Judge-facing activity feed: 20 verified, synthetic Atlas records and clear claim limits](JUDGES_ACTIVITY_FEED.md)**
- **[Machine-readable Atlas project activity snapshot](evidence/2026-10-11/project_activity_feed.json)**
- **[Full implemented backend, tests and accessible live-dashboard source (`review-20261011`)](https://github.com/biobitworks/rainy-day-fund/tree/review-20261011)**
- **[Protected Vercel preview](https://rainy-day-fund-sftw26-cohw995ik-biobitworks.vercel.app/)** — reported route smoke; `UNCONFIGURED_FAIL_CLOSED`; not a public working integration
- **[Watch the Make It Rain demo video on YouTube](https://youtu.be/EJx0vBP40A4)** — user-provided link; anonymous playback, visibility and exact runtime not independently verified.

| Platform | Work completed | Honest boundary |
|---|---|---|
| **MongoDB Atlas** | Event sandbox database, synthetic tickets/evals, direct exact write-and-readback and receipts | End-to-end provider ingestion **NOT_TESTED** |
| **ElevenLabs** | Voice/text design, recorded testing, signed webhook adapter and tool endpoints on review branch | Provider-signed call to Atlas **NOT_TESTED** |
| **Raindrop.ai** | Local SDK/Workshop instrumentation, cloud-receipt guard in backend | Correlated cloud trace/Judge verdict **NOT_TESTED** |
| **Kiro / recursive harness** | Agent-assisted implementation process, bounded synthetic evaluation and policies | Hosted autonomous improvement **NOT_DEMONSTRATED** |
| **Vercel** | Public static evidence walkthrough and protected Python API/dashboard preview | Atlas credentials missing on preview; production remains static |

The development handoff **reports** 14/14 targeted offline tests passing; full suite 102 passed, 2 failed, 1 skipped. Those are not new independent hosted-test claims. The three-platform flow (ElevenLabs → Atlas → Raindrop) **has not succeeded**. Credentials remain outside Git. See the [submission packet](SUBMISSION_2026-10-11.md) for each step, exact links and known failures.

**SF Tech Week 2026 · Harness Engineering & Model Wrangling Hackathon · Recursive Harnessing**

Make It Rain is an evidence-first, accessible event-support assistant prototype. It uses synthetic troubleshooting cases to evaluate **bounded changes to the agent's operating procedure**: propose a change, test against fixed cases, record a policy decision, and retain predecessor and failure history.

## Links

- [YouTube demo video](https://youtu.be/EJx0vBP40A4)
- [Deployed evidence walkthrough](https://rainy-day-fund-sftw26.vercel.app)
- [Evidence and limitations](evidence/2026-10-11/README.md)
- [Corrected measured lookup benchmark](evidence/2026-10-11/lookup_benchmark_v2_corrected.json)
- [Reproducible benchmark script](experiments/lookup_benchmark.py)

## What actually works

**MongoDB Atlas** is the authoritative hackathon application store. In `rainy_day_fund_sftw26.ticket_fixtures`, **12 frozen synthetic cases** were independently read back. Local synthetic evaluation and policy records are also stored.

**ElevenLabs** voice/text tests were observed, including microphone troubleshooting and text fallback. The **Raindrop Workshop CLI** was independently installed and exercised in an isolated environment.

## Evidence boundaries

At the last production audit, the Vercel page was a **static evidence walkthrough**, not a real-time ticket dashboard: `/api/health`, `/api/tickets`, and `/api/events` returned HTTP 404. An ElevenLabs-to-Atlas webhook and corresponding Raindrop Cloud trace correlation have **not** been independently verified. Faster end-to-end attendee troubleshooting has **not** been demonstrated.

A local FCO/FCG metadata candidate was projected into Atlas, but no canonical graph admission, project MMR commitment or signature is claimed. Historical research implementations were not imported into this application.

## Reproduce the bounded benchmark

Python 3.11+. Obtain an authorized copy of the *exact* original dataset archive **outside Git**, then run:

```bash
python3 experiments/lookup_benchmark.py /private/path/to/archive.zip
```

This measures exact-ID lookup versus linear scanning. **It does not measure** agent reasoning, webhook latency, FCO/FCG computation or real-world ticket-resolution speed. Results vary by machine.

## Safety and provenance

- Frozen synthetic fixtures are not real attendee tickets or verified real-world outcomes.
- Do not commit API keys, credentials, private conversation data, raw recordings, participant contact details, or unreviewed third-party datasets.
- All unsupported performance or provider claims remain explicitly NOT_TESTED until an independent receipt exists.
- Earlier FCO/FCG/Seedgraph projects are pre-existing inspiration and not application dependencies.

This repository contains newly authored public evidence and a bounded reproduction script. See [evidence notes](evidence/2026-10-11/README.md) for exact limitations.
