# Project-scoped sync and conversation custody policy

Project: `RDF-SFTW26-NEW-001`. Public repository: `biobitworks/rainy-day-fund`. Branches: `main` (submission target), `review-20261011` (team review).

## Durable update rule
After each **material implementation or audit step**, propose or implement a successor commit containing only publishable original, licensed content, then verify the GitHub branch head and CI. Chat messages by themselves are NOT authoritative state; receipt-bearing repo files and database records are.

**Never copy full raw chat conversations, all attachments, personal communications, private Google docs, event Wi-Fi credentials, private accessible-support incident detail, model inputs containing personal data, or local .env into the public repository.** Provide redacted decision summaries, source URLs, public code, synthetic fixtures, allowed citations, and explicit gaps. Preserve private items outside Git in approved restricted storage only when authorized; publish only opaque references and declared relationship types. A hash of a secret may itself be sensitive.

## Breakpoint requirements
Each meaningful update should record project/repo binding, predecessor commit, what sources were observed, proposed and executed work, test commands and raw receipts, failure successors, confidence limits, user/team decisions, and NEXT_ACTION. Exact identity hashes are not scientific validation; FCG edges are typed declared relations and MMR inclusion is custody, not truth.

## PR review & merge
- Protect current `main` baseline. Work on review branch with peer review; don't claim Sophia's verbal approval is GitHub write authorization.
- Validate `python -m pytest -q`, `python scripts/run_local.py`, `python scripts/independent_verify.py`, notebook CI, public secret gate, hosted dependency constraints.
- Record a successful upstream push (commit SHA + GitHub readback), not just local changes. Never force-push over another teammate's work.
- Before merging, review ownership, Apache-2.0 compatibility, privacy, new-work provenance and demo claims.
- When live external tools are unavailable, record BLOCKED/NOT_TESTED and continue other independent work.
- This protocol is project-level guidance, not a claim of persistent automated background syncing. A turn cannot auto-push when no authorized execution exists.

## Separate stores
- GitHub: public source, synthetic fixtures, deidentified execution summaries and notebooks.
- Atlas: application tickets, outbox, harness/evaluation state; real people only with explicit consent and authorization.
- MagicPro host-local `.env`: credentials owner-only, ignored by Git, never serialized in receipts.
- ElevenLabs: voice adapter; backend verifies calls and binds pseudonymous session IDs.
- External FCO/FCG research: optional read-only receipt verification of allowed sanitized artifacts; existing source remains separate.

LAST_KNOWN: user reported local .env created/opened, and masked metadata inspection observed owner-only mode 600. ElevenLabs key and MongoDB URI fields SET; agent ID and webhook secret EMPTY. Authentication NOT_VERIFIED. Provider authentication check BLOCKED by remote-tool safety control. No secret bytes read back to the conversation.

NEXT_ACTION: execute an authenticated provider request locally through approved operator tooling, start ElevenLabs agent configuration, run Atlas new-process readback, then append receipts on an authorized new commit.
