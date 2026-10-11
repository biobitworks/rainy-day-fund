"""Pure offline fixture/receipt validation; NO cloud provider calls."""
import csv, json, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
EXPECTED_IDS={f'RDF-SYN-{i:03d}' for i in range(1,13)}

def load_and_check():
    with (ROOT/'raindrop_eval_dataset.csv').open(encoding='utf-8',newline='') as f:
        rows=list(csv.DictReader(f))
    fixtures=[json.loads(line) for line in (ROOT/'atlas_ticket_fixtures.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    ids={r['case_id'] for r in rows}; mongo_ids={r['_id'] for r in fixtures}
    assert len(rows)==len(fixtures)==len(EXPECTED_IDS)==12
    assert ids==mongo_ids==EXPECTED_IDS
    assert len(ids)==len(rows)
    assert {r['split'] for r in rows}=={'dev','heldout','adversarial'}
    counts={k:sum(r['split']==k for r in rows) for k in ('dev','heldout','adversarial')}
    assert counts=={'dev':6,'heldout':4,'adversarial':2},counts
    assert all(r['synthetic'].lower()=='true' for r in rows)
    for r in rows:
        f=next(x for x in fixtures if x['_id']==r['case_id'])
        assert f['scenario_input']==r['input']
        assert f['expected_action']==r['expected_action']
        assert f['status']=='UNEXECUTED_SCENARIO'
        assert f['source_version']==r['source_version']
    return counts

def check_receipt(receipt):
    assert receipt['project_id']=='RDF-SFTW26-NEW-001'
    assert receipt['synthetic'] is True
    assert receipt['case_id'] in EXPECTED_IDS
    if receipt['status']=='PASS_E2E':
        required=('conversation_id','agent_id','tool_call_id','atlas_ticket_id',
                  'postcall_event_id','raindrop_trace_id','raindrop_eval_run_id')
        assert all(receipt.get(k) for k in required),'Incomplete provider receipt'
        assert receipt.get('atlas_readback') is True
        assert receipt.get('webhook_signature_valid') is True
    return True
if __name__=='__main__':
    print('OFFLINE_FIXTURE_INTEGRITY_PASS',load_and_check())
    r=json.loads((ROOT/'sample_integration_receipt.json').read_text())
    check_receipt(r)
    print('TEMPLATE_VALID; CLOUD_INTEGRATION_NOT_TESTED')
