# ElevenLabs integration — Sophia executor playbook

Status: **CONFIGURATION NOT VERIFIED / E2E NOT_TESTED**. The user reports their ElevenLabs account is set up. The instructions here are a build plan, not a claim of connected service.

## Minimal valuable demo
1. In ElevenLabs Agents, create a NEW agent "Make It Rain" (not an official event-staff agent). Set a short disclosure: "I am a hackathon demonstration assistant, not an official organizer."
2. Give the agent narrow event-support instructions: answer only from explicit approved event-guide versions. For accessibility seating, safety, event admission and identity/registration disputes, open an escalation ticket and route to a real human.
3. In agent Tools, add authenticated **webhook tools**, not direct database credentials. Supported tool names: `get_public_event_fact`, `open_synthetic_ticket`, `get_authorized_ticket`, `escalate_synthetic_ticket`. Do not enable unbounded arbitrary HTTP or dynamic Mongo queries.
4. Define tool schemas: `ticket_id` opaque ID; `session_id` pseudonymous; `source_version` exact approved guide; `idempotency_key` server-validated; `category` allowlisted; `language` BCP47; `consent` explicit.
5. Configure bearer authentication using ElevenLabs **Workspace Auth Connection** or a header of type **Secret**. The backend must verify auth independently, never accept a caller-supplied authority claim, use least-privileged Atlas credentials, and apply a per-session rate limit. Do not paste bearer values in Git or screenshots.
6. Bind `conversation_id` and pseudonymous `session_id` through runtime dynamic variables. The session ID must resolve to the same authorized Atlas ticket across voice and accessible text. A telephone number is NOT authentication.
7. Test in web-agent voice first. If phone-number access is available, import an inbound-capable purchased Twilio number. Verified caller IDs are outbound-only; do not claim inbound works without an actual call.
8. Provide equivalent **text-only mode** / accessible web chat. Text is the mandatory fallback; live ASL translation, custom phone haptics and hearing-device integrations are NOT_TESTED.
9. Test synthetic caller: ask about a rule change → create `RDF-DEMO-...` synthetic ticket → switch to text and retrieve identical ticket → attempt unauthorized private record retrieval (deny) → human escalation.
10. Capture exact ElevenLabs `agent_id`, nonsecret `conversation_id`, versioned prompt digest, call/tool outcome status, Atlas ticket ID, trace timestamps and consent state. Mask transcripts/personal data and save synthetic test artifacts only.

## Source documentation
- Webhook tools: https://elevenlabs.io/docs/eleven-agents/customization/tools/webhook-tools
- Dynamic variables and secret variables: https://elevenlabs.io/docs/eleven-agents/customization/personalization/dynamic-variables
- Text-only chat mode: https://elevenlabs.io/docs/eleven-agents/guides/chat-mode
- Twilio inbound integration: https://elevenlabs.io/docs/eleven-agents/phone-numbers/twilio-integration/native-integration/
- Twilio personalization webhook: https://elevenlabs.io/docs/eleven-agents/phone-numbers/twilio-integration/customising-calls

## Important limitations
ElevenLabs' Code Tools are enterprise-only in its current docs, so do not make the demo depend on that feature. Use standard webhook tools where available. Do not call the integration working until a real instrumented request has succeeded.

## Sophia acceptance test
Record a synthetic `session_id`, `ticket_id`, two channel observations, the Atlas readback, privacy denial, and measured tool latency. If either channel fails, log FAIL and demonstrate the working fallback; do not invent success.
