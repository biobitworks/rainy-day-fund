# Kiro ↔ backend ↔ ElevenLabs — contract v1
**Status:** DOCUMENTED, not live-verified.

## Runtime ownership
- **Kiro IDE/CLI/Crew**: developer/executor; reads repository, edits code and runs tests with approval. It is NOT an authority to expand production tool permissions.
- **ElevenLabs Agents**: realtime voice UX; local voice account setup USER_REPORTED; verified agent/webhook call NOT_TESTED.
- **Backend (new code)**: authenticates channel calls, issues opaque `session_id`, authorizes `ticket_id`, applies allowlisted tool schema, maps idempotency and calls MongoDB using the server-only secret.
- **MongoDB Atlas**: authoritative operational state and evaluation receipts, official event cluster.
- **Ollarma (optional)**: routed local model inference with host+model digest and bounded queue. Not canonical persistence; no silent "works on billions of tokens" claim without counters.
- **FCO/FCG observer (external)**: approved redacted progress event stream only. No direct access to participant data or write privileges on application Atlas.

## Tool-to-endpoint mapping (new backend; not currently deployed)
| ElevenLabs tool | HTTP endpoint | Backend operation | Authorization |
|---|---|---|---|
| `get_public_event_fact` | `POST /api/tools/get-public-event-fact` | approved guide version lookup | service secret + bounded public field allowlist |
| `open_synthetic_ticket` | `POST /api/tools/open-synthetic-ticket` | idempotent new synthetic ticket + event | service secret + verified session; synthetic only |
| `get_authorized_ticket` | `POST /api/tools/get-authorized-ticket` | session-scoped ticket and ordered history | service secret + ticket/session membership |
| `escalate_synthetic_ticket` | `POST /api/tools/escalate-synthetic-ticket` | staff queue flag and audit event | service secret + verified session and rule |

Contracts in `schemas/agent_tools.v1.json` are preliminary request/response definitions. Do not claim built endpoints until a runner tests them.

## Voice-first test with mandatory text equivalent
1. Create new agent `Make It Rain`; disclose it is a hackathon demo assistant, not a Cerebral Valley/SHACK15 organizer.
2. Configure auth for server tools using ElevenLabs' secret/header configuration, never put `ELEVENLABS_WEBHOOK_SECRET` in a model prompt.
3. Backend issues `session_id` after verifying a browser session or explicit demo token; phone number alone does not authorize private ticket access.
4. Start synthetic voice call in Spanish/English; request support. Backend creates ticket in `rainy_day_fund_sftw26`.
5. Switch to keyboard/screen-reader-accessible text view. Using authorized session, retrieve exact `ticket_id`, latest state and source version. Record exact results, no private transcript.
6. Attempt another ticket or restricted participant lookup. Expect `DENIED` and a recorded policy receipt.
7. Take backend service down and restore it, retrieve same ticket; compare independently measured state digest.
8. If voice unavailable, leave tool simulated and claim only verified text + Atlas success; do not fabricate speaker/avatar/ASL/haptic support.

## Deployment/settings
- Local `.env` keys: `ELEVENLABS_API_KEY`, `ELEVENLABS_AGENT_ID`, `ELEVENLABS_WEBHOOK_SECRET`, `MONGODB_URI`. User reports file mode 600 on magicPRObox.
- The `MONGODB_URI` value is backend-only. Git tracked `.env.example` shows empty placeholders. The committed Atlas smoke script currently calls `load_env()` and expects the private `.env` in its checkout root. If both MongoDB URI variable aliases are set, the code currently prefers `ATLAS_MONGODB_URI`; set just one.
- No unverified voice storage/recording. Ask consent before using live attendee voice; prefer synthetic input.
- Use least-privilege Atlas DB user and session-bound TTL/retention controls before real participant data.

## Definition of done
A redacted receipt shows actual ElevenLabs conversation ID, synthetic ticket ID, auth result, two channel interactions, source version, measured response time, Atlas readback, unauthorized action denial and regression notebook. Any missing component is NOT_TESTED.
