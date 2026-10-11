# Make It Rain — Provider Setup and Evidence Protocol (2026-10-11)

**Use existing official Atlas project** `6acba49b5c102b1d2b95a0ac`, **cluster** `Cluster0`, **database** `rainy_day_fund_sftw26`.

## First

1. **Atlas:** In Data Explorer, query `ticket_fixtures` using `{"project_id":"RDF-SFTW26-NEW-001","source_version":"RDF-SYN-TICKET-20261011-V1"}`. Count should be **12**; do NOT re-import if present. Download the JSONL as a portability backup only. Do not edit frozen scenarios or upload into `tickets`.
2. **ElevenLabs:** In ElevenAgents create/choose a **test agent**. Paste `elevenlabs_system_prompt.md` as system instructions. Upload `elevenlabs_knowledge_base.md` to Knowledge Base and attach to the agent. Verify the only facts asserted are generic fixture guidance (not event-specific Wi-Fi credentials/schedules). Use the Test AI Agent interface. Follow `02_ELEVENLABS_SETUP.md` for the exact test sequence.
3. **Raindrop:** In Raindrop create/select the correct project. Create behavioral Signals using `01_RAINDROP_JUDGES_AND_SIGNALS.md`. Attach `raindrop_eval_dataset.csv` as a **local or hosted evaluation input set where supported**, not as evidence of actual scored traces. Run a replay using the Query SDK and an authorized live agent callback after its credentials and SDK are verified. See `03_CLAUDE_LINK_ALL_THREE.md`.
4. **Integration test:** Implement/deploy the HTTPS app endpoints, then test signed ElevenLabs post-call delivery and ticket tool calls using the same scenario IDs, and verify Atlas readback. A Raindrop trace requires separately instrumented backend or supported telemetry bridge. **Do not claim a three-provider round trip until the Raindrop trace ID is confirmed.**

## What's verified vs not

- VERIFIED_PREVIOUS_TURN: Atlas `ticket_fixtures` 12 inserted and 12 independently read back by Atlas connector; original readback receipt included.
- VERIFIED_LOCAL_THIS_PACKAGE: files exist, schema row counts and fixture matching and offline evidence checks.
- NOT_TESTED: ElevenLabs agent save/test, real call, signed webhook to deployed server, Raindrop cloud trace, Raindrop judge run, Ollarma/Seedgraph completion, physical process restart.

## Files

| Name | Purpose |
| --- | --- |
| `raindrop_eval_dataset.csv` | 12 synthetic expected cases (original frozen evaluation inputs) |
| `01_RAINDROP_JUDGES_AND_SIGNALS.md` | Paste into Signal/judge fields and review examples |
| `elevenlabs_system_prompt.md` | Paste into agent's system prompt |
| `elevenlabs_knowledge_base.md` | Upload under knowledge base, attach to agent |
| `02_ELEVENLABS_SETUP.md` | Tool endpoint and post-call webhook instructions |
| `atlas_ticket_fixtures.jsonl` | MongoDB seed fixture backup, NOT a full database backup |
| `04_MONGODB_SETUP.md` | Atlas filters, import only when needed, readback instructions |
| `03_CLAUDE_LINK_ALL_THREE.md` | Developer execution prompt for end-to-end bridge |
| `sample_integration_receipt.json` | Unexecuted contract, **not** successful evidence |
| `receipt_checks.py`, `test_receipt_checks.py` | Offline validator and passing unit tests |
| `manifest_sha256.json` | Local file inventory/digests, not attestation of remote provenance |

Docs consulted Oct 11 2026:
- https://elevenlabs.io/docs/eleven-agents/quickstart
- https://elevenlabs.io/docs/eleven-agents/customization/knowledge-base/manage-documents
- https://elevenlabs.io/docs/eleven-agents/customization/tools/webhook-tools
- https://elevenlabs.io/docs/eleven-agents/workflows/post-call-webhooks
- https://docs.raindrop.ai/signals/
- https://docs.raindrop.ai/workshop/
- https://www.npmjs.com/package/raindrop-ai
- https://www.mongodb.com/docs/atlas/import/mongoimport/

Privacy: test only on synthetic fixtures; no actual attendee audio/transcripts/PII in CSV, Git or monitoring until authorized and access-scoped. No credentials in docs. Apache-2.0 license in public GitHub repo is not retroactive approval for unreviewed joint work.
