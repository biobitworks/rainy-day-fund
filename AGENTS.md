# Make It Rain — engineering agent instructions

Treat docs/IMPLEMENTATION_GATES.md and PROJECT_SETTINGS_COPY_PASTE.md as current handoff, plus source-based event rules. New hackathon work ONLY; preserve earlier work as references, never vendored imports.

Use official Atlas project 6acba49b5c102b1d2b95a0ac, Cluster0; database rainy_day_fund_sftw26. No real participant data or secret material in Git. ElevenLabs is a replaceable adapter; text equivalent is required.

Build a bounded observe→propose→test→admit/reject→persist→recover loop. Freeze oracles first. Proposers cannot modify graders, widen capabilities, read private data or change credentials. Save full failed candidates and predecessors. Every experiment needs executable Jupyter notebook and machine-readable receipt.

Use statuses PROPOSED, EXECUTED, VERIFIED, FAILED, NOT_TESTED, NOT_COMPUTED, NOT_SIGNED precisely. Root/signature require ordered leaves, domain-separation recipe, peaks, independent verification, verified signing key/authority. Link to actual commits. Never infer causality or truth from hashing.

## Repository update discipline
Every material turn must produce or reference a reviewable successor Git commit **when authorized and useful**. See `docs/SYNC_AND_CUSTODY.md`. Never auto-publish raw chats or attachments. Protect private `.env` and user/participant data; use sanitized checkpoint summaries. If syncing fails, record NOT_PUSHED and exact blocker; do not assert success. Preserve teammate commits and require GitHub CI and peer review before `main` merge.
