# Task for Sophia Park — paste into your Kiro CLI/IDE or coding-agent session

We are a two-person team building **Make It Rain** (internal: `rainy-day-fund`) for the October 11, 2026 SFTechWeek MongoDB Atlas hackathon. This is a NEW repo with no code copied from prior research projects. Our target is Recursive Harnessing, and the public product is an accessible, multilingual event-support system.

Your lane: **product interface and agent-provider integration**, in a feature branch `feat/participant-channels` after access is granted. Confirm task ownership with the teammate first. Do not expose credentials in chat or commits.

Build the narrow, judge-critical vertical slice:
- A simple accessible text-first participant entry point (keyboard navigable; proper labels and focus order; simulated caller identity, not real participant verification).
- A ticket create/status/reopen/escalate flow calling our backend contract, using Atlas persistence through the service. Same `session_id` must survive reconnect.
- A replaceable voice adapter to ElevenLabs; if webhooks or phone number are not provisioned, keep the text path fully functional and label voice `NOT_TESTED`.
- A proposal adapter interface: given only a development failure summary and constrained schema, return one candidate change to tool ordering, source version routing, context limits or escalation threshold. Log provider/model, prompt digest, token accounting, actual output, and validation result. Do not allow updates to grading code, ACLs, tool permissions, secrets or database admin controls.
- Write focused unit tests for accessibility routing and negative-control denial. Use synthetic records only.

Coordinate with backend lane on `POST /sessions`, `POST /tickets`, `GET /tickets/{id}`, `POST /proposals`, `GET /runs/{id}` and a canonical event ID scheme. If a contract is not implemented, use typed mock responses only in dev and clearly label them mocks; the final demo must show real Atlas writes.

Deliver: commit SHA(s), branch, files changed, tests run, screenshots/demo evidence (with consent), blockers, a handoff note with `EXECUTED/NOT_TESTED`, and dependencies. No claims of verified ASL, hearing-aid compatibility or production voice until tested. Reserve public release for joint approval. Don't rewrite prior teammates' code without a review.