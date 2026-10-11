# Higher-order operational evidence — new project type contract

The project is independent of earlier Vithia/FCO/FCG repositories. These new edge names are original application metadata and **do not** copy upstream implementation code.

Each record carries (a) content identity, (b) context/occurrence identity, (c) source/version identity, (d) actor/host/tool, (e) observed lifecycle status and timestamp, (f) privacy class, and (g) optional cryptographic receipt. Do not treat graph edges as causal proof.

## Proposed typed relationships
- `SESSION_FROM_CHANNEL(session_id, channel_observation_id)`: origin voice/text/web (channel is not identity).
- `TICKET_OPENED_IN_SESSION(ticket_id, session_id)`: authorized new ticket creation.
- `REPLY_USED_GUIDE_VERSION(output_id, guide_version_id)`: evidence of exactly which approved guide informed a response.
- `PROPOSAL_BASED_ON_FAILURE(proposal_id, failure_trace_id)`: declared derivation, not proof of causation.
- `CANDIDATE_TESTED_BY(proposal_id, eval_run_id)`: frozen oracle and raw metrics.
- `DECISION_APPLIES_TO_PROPOSAL(policy_decision_id, proposal_id)`: admit/reject/quarantine.
- `STATE_RESTORED_FROM(recovery_receipt_id, persisted_state_id)`: exact replay claim only after testing.
- `CONVERSATION_REFERENCES_TICKET(conversation_id, ticket_id)`: nonsecret pointer, authorization required for dereference.
- `EXTERNAL_OBSERVER_REVIEWED(receipt_id, sanitized_event_id)`: custody check only, never authority over live operations.

## Required live tests
1. Bounded Atlas write/lookup/index enforcement, duplicate idempotency, ordered event replay and new-process recovery.
2. Version mismatch / stale guide regression that drives a bounded independent proposal and held-out replay.
3. Fail-closed private lookup and deny unauthorized tool escalation.
4. Channel continuity (ElevenLabs voice ↔ accessible text) without phone-number-only authentication.
5. Budgeted inference and host/tool attribution when Kiro, Claude, ChatGPT, or Ollarma participate.
6. Jupyter replay, MMR ordered leaves+peaks+root+independent verifier and signed project authority only if actually established.

Any uncertain provenance is UNKNOWN. Lab hashes establish bytes and custody, not actual accessibility efficacy or natural-language correctness.

## Competition claim boundary
**Pre-existing research is background and must never count as today’s newly built implementation.** The new GitHub commits and GitHub Actions evidence are the admissible software work product. A useful phone UI alone does not satisfy recursive-harness improvement. The decision-generating, automatically evaluated and safety-gated successor is the prize-critical feature.
