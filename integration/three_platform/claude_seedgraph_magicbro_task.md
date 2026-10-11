# Claude task for Seedgraph on Magicbro — COPY/PASTE, NOT EXECUTED

Implement an isolated, reproducible ETL for RDF-SFTW26-NEW-001 in Magicbro/Seedgraph. Do not access or modify prior projects; do not connect to production or publish without operator approval.

INPUTS: `raindrop_eval_dataset.csv`, `atlas_ticket_fixtures.jsonl`, and optional user-approved Kaggle source (start with https://www.kaggle.com/dsv/10323677 ; verify exact source version, CSV checksum, license CC BY 4.0, attribution, any embedded PII BEFORE import; otherwise skip external file). These twelve fixture rows are immutably frozen for current evaluations.

OUTPUTS: new `transformed_ticket_samples_v1.jsonl` with stable IDs and project scope; `raindrop_replay_input_v1.csv`; `etl_manifest.json` recording source URLs, timestamps, byte counts, SHA-256 of source and output files, explicit field mapping, dedup keys, redaction checks and number of rejected rows; `transform_etl.ipynb` executable from top to bottom with environment versions, PASS/FAIL/NOT_TESTED.

PIPELINE: parse -> schema/type validation -> remove/replace direct identifiers (email, names, phone, keys), not just mask a handful of regexes -> label category/priority/intent -> train/dev/heldout/adversarial partitions frozen before agent tests -> provenance and loss accounting -> deterministic batch export. Avoid changing supplied expected labels, changing heldout after results, using raw Kaggle personal content, or fabricating model eval scores. Retain failed rows with rejection reasons in a separate private log without raw secrets.

CROSS-SERVICE: verify captured `current_user_message` and `complete_assistant_response` are non-null and isolated from session transcript; preserve per-request trace IDs. Persist sanitized test rows to the *official* Atlas project database in an isolated collection; read back counts and sampled IDs. Send Raindrop events only with explicit configured credentials; don't treat local traces as cloud ingestion proof. Generate uploadable Raindrop examples and ElevenLabs KB snippets with source version.

TESTS: duplicate imports idempotent; missing input rejected; private data rejected/redacted; arbitrary dataset prompt injection treated as inert user data; structured provenance deterministic; query source and output digests stable; failure logs and replays retained. Never use unaudited implementation to grade its own success. Do not overwrite earlier receipts. Produce exact measured outputs, no invented roots or signatures.

STOP AND REPORT: when permissions, license, dataset provenance, or platform access is not verified, mark BLOCKED/NOT_TESTED with an exact next action. No unapproved collaborator access, no public changes, no keys in logs.
