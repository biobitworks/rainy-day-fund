# Decision successor: official Atlas only and post-event rotation

**Project:** RDF-SFTW26-NEW-001  
**Parent:** docs/ATLAS_HARMONIZATION_20261011.md, reviewed at PR #1 head c91904dc763e3339795ecaf13055d96353a386ba.  
**Source of decision:** User confirmation 2026-10-11 (America/Los_Angeles).  
**Status:** team/operator direction; this is not an executed credential rotation or Atlas migration.

## Confirmed scope decision
- Atlas project `6acbcaf68ec2c1911378a336` was an **accidentally created workspace**, not the event-sanctioned Atlas sandbox. It is **out of scope**.
- Use **only** official hackathon Atlas organization `69ef9daf03d2ce35c2657862`, project `6acba49b5c102b1d2b95a0ac`, cluster `Cluster0`, and database `rainy_day_fund_sftw26` for the event application.
- Do not copy data between projects, create a replacement cluster, or seek second-project reconciliation. An earlier recommendation to conduct second-project inventory as a critical path is superseded by this decision.
- Credential rotation is **DEFERRED_BY_OPERATOR_UNTIL_AFTER_HACKATHON**, not completed. The credential exposure is still a known risk; do not paste/reuse it in public artifacts, logs or repository files. Continue only with authorized bounded checks and existing sandbox access; stop and request operator action if authentication or access blocks execution.

## Work in progress
- Bounded model-response schema validation, frozen held-out adjudication and unsafe-patch rejection implemented on review branch.
- A synthetic model-response replay notebook is checked into source and invoked from CI; this does **not** establish a genuine provider-generated proposal.
- Remaining event gates: authenticated application-level Atlas recovery across new process, genuine model-generated candidate with provider receipt, accessible text/voice continuity, sanitization/security review and final demo/submission.
- Preserve no-canonical-root/no-signature status; never infer authority from hashes.

## Turn state
**DECISION:** official sandbox authoritative; accidental workspace ignored; rotation after event.  
**IMPLEMENTED:** source-bound bounded model proposal evaluator, unit tests, synthetic replay notebook, CI execution step.  
**NOT_TESTED:** live model proposal, Atlas worker restart and voice/text continuity.  
**NEXT_ACTION:** verify CI run for implementation commit; connect an approved model transport; execute end-to-end synthetic Atlas recovery without exposing secrets.
