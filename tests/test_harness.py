import json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from make_it_rain.harness import Policy, score, propose_from_failure_signals, admission, mmr_receipt, run_fixture, canonical, digest

FIXTURE=json.loads((Path(__file__).resolve().parents[1]/'benchmarks/frozen_cases.json').read_text())

def test_deterministic():
    assert canonical({'z':1,'a':2}) == canonical({'a':2,'z':1})
    assert digest({'z':1,'a':2}) == digest({'a':2,'z':1})

def test_improvement_and_negative_control():
    r=run_fixture(FIXTURE)
    assert r['decision']['decision']=='ADMIT'
    assert r['negative_control']['decision']=='REJECT'
    assert r['candidate']['passed'] > r['baseline']['passed']
    assert r['candidate']['unsafe']==0

def test_no_leak():
    from dataclasses import replace
    t=score(FIXTURE['cases']['adversarial'],replace(Policy(),verify_private_lookup=False))
    assert t['unsafe']>0

def test_mmr_incremental_and_tamper():
    ev=[{'index':i,'x':i*i} for i in range(11)]
    r=mmr_receipt(ev)
    assert r==mmr_receipt(ev)
    assert r['ordered_leaf_hashes'][:7] == mmr_receipt(ev[:7])['ordered_leaf_hashes']
    changed=list(ev); changed[4]={'index':4,'x':-1}
    assert mmr_receipt(changed)['root']!=r['root']
    assert sum(1<<p['height'] for p in r['peaks'])==11

def test_frozen():
    assert FIXTURE['frozen'] is True
    assert all(c['id'] for section in FIXTURE['cases'].values() for c in section)

def test_receipts_not_misrepresented():
    r=run_fixture(FIXTURE)
    assert r['hosted_atlas']=='NOT_TESTED_IN_THIS_RUN'
    assert r['llm_proposer']=='NOT_IMPLEMENTED'
    assert r['signing']=='NOT_SIGNED'
