"""Opt-in live Atlas smoke/recovery using a NEW synthetic ticket.

Usage in two SEPARATE Python processes:
  python scripts/atlas_smoke.py write RDF-DEMO-20261011-001
  python scripts/atlas_smoke.py read RDF-DEMO-20261011-001

This script WILL WRITE only when explicitly invoked with 'write' and a
configured ATLAS_MONGODB_URI. Not executed in the packaged local evaluation.
"""
import argparse, hashlib, json, os, sys
from datetime import datetime, timezone

p=argparse.ArgumentParser()
p.add_argument('operation',choices=['write','read'])
p.add_argument('run_id')
a=p.parse_args()
uri=os.getenv('ATLAS_MONGODB_URI')
if not uri:
    sys.exit('NOT_TESTED: ATLAS_MONGODB_URI not configured')
try:
    from pymongo import MongoClient
except ImportError:
    sys.exit('NOT_TESTED: pip install -r requirements-atlas.txt')

project='RDF-SFTW26-NEW-001'
db_name=os.getenv('MONGODB_DB','rainy_day_fund_sftw26')
if db_name!='rainy_day_fund_sftw26':
    sys.exit('DENIED: expected isolated hackathon DB')
if len(a.run_id)>80 or not a.run_id.startswith('RDF-'):
    sys.exit('DENIED: synthetic run ID must begin RDF- and be at most 80 chars')
cli=MongoClient(uri,serverSelectionTimeoutMS=12000)
cli.admin.command('ping')
col=cli[db_name]['tickets']
_id=f'{project}:{a.run_id}:SYNTHETIC'
payload={'_id':_id,'project_id':project,'run_id':a.run_id,
         'origin':'SYNTHETIC_TEST','category':'guide_version_change',
         'status':'OPEN','source_version':'GUIDE-V0-TEST',
         'predecessor_event_id':None, 'schema_version':'1'}
serialized=json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf8')
expected=hashlib.sha256(serialized).hexdigest()
if a.operation=='write':
    result=col.update_one({'_id':_id},{'$setOnInsert':{**payload,'created_at':datetime.now(timezone.utc)}},upsert=True)
    action='INSERTED' if result.upserted_id is not None else 'EXISTING_IDEMPOTENT'
else:
    action='READ_EXISTING'
found=col.find_one({'_id':_id})
if found is None:
    sys.exit('FAIL: no matching ticket in Atlas')
observed={k:found.get(k) for k in payload}
actual=hashlib.sha256(json.dumps(observed,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf8')).hexdigest()
assert actual==expected, 'FAIL: Atlas readback mismatch'
print(json.dumps({'status':'PASS_ATLAS_READBACK','operation':a.operation,'action':action,
                  'run_id':a.run_id,'ticket_id':_id,
                  'preimage_sha256':expected,'readback_sha256':actual,
                  'recovery':'PASS_NEW_PROCESS' if a.operation=='read' else 'NOT_TESTED_IN_THIS_PROCESS'},indent=2))
