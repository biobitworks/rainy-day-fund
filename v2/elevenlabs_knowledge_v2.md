# Make It Rain — support knowledge v2 (EVIDENCE-LINKED, UNDEPLOYED)

Only cards whose quote was verified verbatim in a source file are listed. Statements are model paraphrases (NOT_VERIFIED); the quote is authoritative.

## Session ID Verification
- card: `KC-9bb565ebc7` source: `SRC-a70ff379` sha256 `c8d9a138ad61`
- statement (paraphrase): Backend issues `session_id` after verifying a browser session or explicit demo token; phone number alone does not authorize private ticket access.
- evidence: "Backend issues `session_id` after verifying a browser session or explicit demo token; phone number alone does not authorize private ticket access."

## Ticket Retrieval
- card: `KC-570f690dc5` source: `SRC-a70ff379` sha256 `c8d9a138ad61`
- statement (paraphrase): Using authorized session, retrieve exact `ticket_id`, latest state and source version. Record exact results, no private transcript.
- evidence: "Using authorized session, retrieve exact `ticket_id`, latest state and source version. Record exact results, no private transcript."

## Backend Service Down and Restore
- card: `KC-b838b0e644` source: `SRC-a70ff379` sha256 `c8d9a138ad61`
- statement (paraphrase): Take backend service down and restore it, retrieve same ticket; compare independently measured state digest.
- evidence: "Take backend service down and restore it, retrieve same ticket; compare independently measured state digest."

## Least-Privilege Atlas DB User
- card: `KC-6af187169b` source: `SRC-a70ff379` sha256 `c8d9a138ad61`
- statement (paraphrase): Use least-privilege Atlas DB user and session-bound TTL/retention controls before real participant data.
- evidence: "Use least-privilege Atlas DB user and session-bound TTL/retention controls before real participant data."

## Redacted Receipt
- card: `KC-607bc16d2e` source: `SRC-a70ff379` sha256 `c8d9a138ad61`
- statement (paraphrase): A redacted receipt shows actual ElevenLabs conversation ID, synthetic ticket ID, auth result, two channel interactions, source version, measured response time, Atlas readback, unauthorized action denial and regression notebook. Any missing component is NOT_TESTED.
- evidence: "A redacted receipt shows actual ElevenLabs conversation ID, synthetic ticket ID, auth result, two channel interactions, source version, measured response time, Atlas readback, unauthorized action denial and regression notebook. Any missing component is NOT_TESTED."

## GitHub Repository Setup
- card: `KC-34f05b744f` source: `SRC-e4ae4e8e` sha256 `ed0ddce8c8ac`
- statement (paraphrase): The process involves creating a new private repository and setting up Git identity.
- evidence: "Use https://github.com/new, PRIVATE, new empty repo, no fork."

## Atlas Database Configuration
- card: `KC-2f395808d5` source: `SRC-e4ae4e8e` sha256 `ed0ddce8c8ac`
- statement (paraphrase): The database must be created with specific collections and fields.
- evidence: "Suggested collections: `guide_versions`, `sessions`, `tickets`, `harness_versions`, `proposals`, `eval_plans`, `eval_runs`, `policy_decisions`, `progress_events`, `recovery_receipts`, `outbox`."

## ElevenLabs Voice Agent Setup
- card: `KC-34d73b6f44` source: `SRC-e4ae4e8e` sha256 `ed0ddce8c8ac`
- statement (paraphrase): A new agent should be created for the `make-it-rain` event with specific permissions.
- evidence: "In ElevenLabs Agents, create a **new** agent for `make-it-rain` scoped to event-support purpose."

## Service Interface Authentication
- card: `KC-6e9c8badea` source: `SRC-e4ae4e8e` sha256 `ed0ddce8c8ac`
- statement (paraphrase): All paths in the service interface require independent authentication and authorization.
- evidence: "All paths authenticate and authorize independently of the agent's instructions."

## Atlas Recovery Smoke Test
- card: `KC-5e4ee92975` source: `SRC-e4ae4e8e` sha256 `ed0ddce8c8ac`
- statement (paraphrase): The smoke test script validates readback and persistence but does not establish full recovery.
- evidence: "This smoke validates direct readback and new-process persistence; it does **not** establish backup recovery, multi-host independent verification or full service fault tolerance."

## GitHub Repository Public State
- card: `KC-2470304f63` source: `SRC-e4ae4e8e` sha256 `ed0ddce8c8ac`
- statement (paraphrase): The repository must be made public by submission time and undergo secret scans.
- evidence: "Make repo public by submission time; secret-scan every commit and GitHub Actions log."

## Not covered
No verified source for Wi-Fi, check-in procedure, schedule, or accessibility accommodations. Agent must ESCALATE_STAFF or VERIFY_SOURCE; it must not answer from memory.
