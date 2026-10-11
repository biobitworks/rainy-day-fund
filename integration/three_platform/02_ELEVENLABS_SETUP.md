# ElevenLabs — exact test agent setup

1. Open https://elevenlabs.io/app and open ElevenAgents.
2. Create a new **test** agent named `Make It Rain — synthetic integration test`.
3. Under Agent / System Prompt, paste entire `elevenlabs_system_prompt.md`. Greeting may be: `Hello. I can help with event check-in, schedules, accessibility, and technical issues. Voice or text are available. How can I help?`
4. Under Knowledge Base, **Add document** > File. Upload `elevenlabs_knowledge_base.md` (Markdown supported). Attach to agent. Do not attach unreviewed photos or real participant data.
5. Model/voice: use an accessible voice, prefer short low-latency responses; record exact selected model/voice ID in private test receipt, without presuming model availability.
6. Test AI Agent first, without tools: `I need instructions in text`, `I cannot find my badge`, `What is the Wi-Fi password?`, `I need a step-free route.` Confirm safe refusals/escalations and text path.
7. **Only after HTTPS backend exists** configure webhook Tools with authenticated server endpoints. The `tools_contract.json` file is a contract for developers, not guaranteed to be an ElevenLabs UI import format. Configure in the UI according to the current tool schema:
   - POST `https://YOUR-APP-DOMAIN.example/api/tools/lookup_guide`
   - POST `https://YOUR-APP-DOMAIN.example/api/tools/create_test_ticket`
   - POST `https://YOUR-APP-DOMAIN.example/api/tools/get_ticket_status`
   - POST `https://YOUR-APP-DOMAIN.example/api/tools/request_staff_escalation`
   - Attach a secret header managed in the platform (never paste Atlas URI or token in prompt/knowledge).
   - Tool result must distinguish `SUCCEEDED`, `REJECTED`, `NOT_FOUND`, `FAILED`, `PENDING` and contain the Atlas authoritative ticket readback where applicable.
   - In **test** endpoint only allow IDs from the 12 synthetic frozen cases. Real attendee tickets need consent/privacy review.
8. Test tool behavior with `RDF-SYN-005` (AV mute) and `RDF-SYN-010` (badge replacement). The agent must not claim authorized replacement or ticket closure.
9. Configure workspace/agent **Post-call Webhook** (transcription, not audio): `https://YOUR-APP-DOMAIN.example/api/webhooks/elevenlabs`. Enable HMAC, save generated secret securely in app environment `ELEVENLABS_WEBHOOK_SECRET`, enable retries. Do not enable audio data. Use official SDK `elevenlabs.webhooks.construct_event(rawBody=...,sig_header=...,secret=...)` on unmodified body and reject bad signature before processing. Webhook event type `post_call_transcription`; conversation ID is in `data.conversation_id`.
10. Upon valid webhook, store allowlisted **synthetic/test metadata** only, de-duplicate by event type + conversation ID; use durable insert/outbox before returning HTTP 200. For actual user content, consent, retention, and redaction controls are prerequisites. This webhook arrives after a call; use server tools for realtime Atlas interactions.
11. Verify in ElevenLabs conversation history: real conversation ID, agent ID, tool call result, and webhook delivery outcome. Then query Atlas matching the exact `conversation_id` and confirm one ingestion receipt after retry. Raindrop event ID must be independently verified; leave null until observed.

**Testing shortcut:** You do not need a phone number to run dashboard Test AI Agent. A telephone test needs an actual assigned number and recorded consent; no number has been verified here.

Docs: https://elevenlabs.io/docs/eleven-agents/quickstart , https://elevenlabs.io/docs/eleven-agents/customization/knowledge-base/manage-documents , https://elevenlabs.io/docs/eleven-agents/customization/tools/webhook-tools , https://elevenlabs.io/docs/eleven-agents/workflows/post-call-webhooks .
