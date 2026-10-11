# Sophia — team handoff (Make It Rain)

Public demo brand: **Make It Rain**. Internal project: **rainy-day-fund**. New-source-only competition, MongoDB hackathon environment, 5 PM PDT public repo + one-minute video deadline.

**What is ready:** a newly authored runnable deterministic policy-proposal fixture, basic deny/escalate gate, negative-control regression, laboratory MMR implementation and executed notebook. This is an engineering starter, **not** a live AI self-modifying agent or ElevenLabs-connected service.

**Proposed split (confirm together):**
- Sophia: accessible text-first user interface, ElevenLabs interface and model proposer integration, end-user demonstration.
- Partner: Atlas authoritative state and recovery, fixture and evaluation, admission gate, evidence/notebook integration.
- Both: review privacy, code/IP ownership, public-license choice, and final submission.

**Synchronize on these interfaces:** `session_id`, `ticket_id`, `guide_version_id`, `proposal_id`, `eval_run_id` and event `sequence`; endpoints in `docs/ATLAS_ELEVENLABS_SETUP.md`.

**Commit protocol:** branch per lane; make new work identifiable by time/commit; never import older private research source or notebooks. Record actual runtime failures instead of editing old evidence. Reserve a merge freeze before demo recording.

**Ask each other once before public release:** Who owns repo? Is Apache-2.0 acceptable for jointly authored new code? Are personal data, credentials and prior work absent from all history? Are both consenting to publish? Who submits and verifies the submission acknowledgement?

**Next hour:** run the starter; agree repo ownership; connect the real Atlas service; demonstrate failure→candidate→evaluation→admission→restart; keep voice optional until end-to-end validated.