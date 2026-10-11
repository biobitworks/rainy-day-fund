# MongoDB Atlas — verified collection and recovery procedure

Official event **Project ID:** `6acba49b5c102b1d2b95a0ac`
Cluster: `Cluster0`
Database: `rainy_day_fund_sftw26`
Preexisting synthetic collection: `ticket_fixtures`

### Check (first; no writes)

Atlas > Data Explorer > `rainy_day_fund_sftw26` > `ticket_fixtures` > Filter:

```json
{"project_id":"RDF-SFTW26-NEW-001","source_version":"RDF-SYN-TICKET-20261011-V1"}
```

Expected 12 documents. Check exact `_id` `RDF-SYN-001` and `RDF-SYN-012`. Existing first-party Atlas connector already performed this readback in a prior turn. Leave frozen test fixtures alone.

### Restore only if missing or moved to a disposable replacement collection

The file `atlas_ticket_fixtures.jsonl` contains 12 JSON-line records with stable `_id` and scenario versions. It is **not** a full Atlas database backup, and the dataset is already populated in the official cluster. MongoDB Compass can import JSON/JSONL, or a database user with readWrite and IP access can execute:

```bash
# Use a scoped URI from a secure environment variable, never add credentials to shell history or Git.
: "${MONGODB_URI:?Configure MONGODB_URI in private environment first}"
mongoimport --uri "$MONGODB_URI" --db rainy_day_fund_sftw26 \
  --collection ticket_fixtures_restore_test \
  --file atlas_ticket_fixtures.jsonl --type json --mode=insert --stopOnError
```

`ticket_fixtures_restore_test` avoids mutating existing frozen collection. To verify, query `_id` + `source_version` and count 12. Restoration of the authoritative collection needs explicit operator approval.

### Integration readback filters

Test backend should create dedicated `integration_smoke_tickets` and `integration_smoke_observations` collections. It should NOT write fixtures into actual attendee `tickets`.

Example smoke ticket filter:

```json
{"project_id":"RDF-SFTW26-NEW-001","case_id":"RDF-SYN-005","synthetic":true}
```

Example signed webhook observation filter:

```json
{"project_id":"RDF-SFTW26-NEW-001","source_service":"elevenlabs","event_type":"post_call_transcription","synthetic":true}
```

The correct proof requires the *same* real `conversation_id` in ElevenLabs history, the signed webhook receipt, and a saved Raindrop trace. A pre-existing fixture document is insufficient for this join.

Do not call Atlas metadata readback a physical worker restart. Kill an actual backend process, start a clean new process, query the same ID, and verify unchanged state for restart PASS.

Official: https://www.mongodb.com/docs/atlas/import/mongoimport/ and https://www.mongodb.com/docs/atlas/atlas-ui/documents/ .
