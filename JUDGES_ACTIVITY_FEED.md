# Make It Rain — judge-facing activity feed

**Primary track:** Recursive Harnessing · **Project:** `RDF-SFTW26-NEW-001` · **Database:** `rainy_day_fund_sftw26`

[Project submission packet](SUBMISSION_2026-10-11.md) · [Public app walkthrough](https://rainy-day-fund-sftw26.vercel.app/) · [Machine-readable activity snapshot](evidence/2026-10-11/project_activity_feed.json) · [Reproducible public evidence](evidence/2026-10-11/README.md)

## What judges can inspect

This feed contains **20 synthetic, project-scoped records**, independently read back from the **event-provided MongoDB Atlas sandbox**. It includes proposed operating rules, frozen local evaluations, policy decisions, recovery receipts, state versions and Atlas-only integration probes. The latest checked sandbox snapshot contained:

| Source | Observed count | What it means |
|---|---:|---|
| Support corpus | 4000 | Synthetic-labelled multilingual examples stored in Atlas; not live attendee interactions |
| Frozen test fixtures | 12 | Fixed development, held-out and adversarial cases |
| Candidate graph objects | 6 | Newly authored FCO-like metadata **candidates**, not canonical FCO admission |
| Candidate graph edges | 5 | Typed candidate relationships; not a verified external FCG commitment |
| Candidate graph receipt | 1 | Candidate projection receipt; **MMR NOT_COMMITTED** |

### Actual activity timeline

The JSON snapshot lists each **stored record ID, source version, source event time and observed status**. The event timestamps are source-authored values, not independently proven database insertion times. All 20 activity records are synthetic or synthetic test records.

- **Proposals and policy decisions:** replay/admit/reject and corrective audit records are visible, including retained failures.
- **Eval runs:** local frozen synthetic replay records exist. These are not validated improvements in live user resolution time.
- **Recovery receipts:** Atlas readback and a stateless recovery test are recorded. These are not broad cross-provider recovery guarantees.
- **Integration probes:** the two currently listed records are **direct Atlas tests**, explicitly **not provider webhooks**.

### What is not established

- A verified ElevenLabs conversation → signed webhook → Atlas ticket chain.
- A Raindrop Cloud trace and Judge result independently linked to the same conversation.
- A functioning production live-updating Vercel ticket dashboard or measured end-to-end response-time gain.
- Canonical FCO/FCG admission, MMR commitment or an authorized signature.
- A completed submission on the event portal or a verified public one-minute video URL.

## Why the uploaded organization audit log was excluded

A separately uploaded 50-entry organization activity export was reviewed. Its project scopes **did not match** this Make It Rain project. It contains third-party user identities and network addresses. **No row of that export was published or claimed as Make It Rain activity.**

## Provenance and verification

This is a **static, point-in-time snapshot** from read-only Atlas queries, not a live dashboard or event stream. It is a judge navigation aid and does not substitute for a signed provider receipt. Source records remain in Atlas. Raw uploaded data and private user media are not redistributed.

**Source status:** OBSERVED PROJECT-SCOPED ATLAS READBACK. **Provider end-to-end:** NOT_VERIFIED. **Public release:** sanitized metadata only.
