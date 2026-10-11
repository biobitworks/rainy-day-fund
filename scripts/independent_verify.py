"""Independent MMR replay from receipt ordered input events, no harness imports."""
import json, hashlib
from pathlib import Path
r = Path(__file__).resolve().parents[1] / 'results' / 'local_synthetic_evaluation.json'
d = json.loads(r.read_text())
sha=lambda b: hashlib.sha256(b).digest()
def jbytes(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')
leaves = [sha(bytes([0])+jbytes(e)) for e in d['events']]
assert [x.hex() for x in leaves] == d['lab_mmr']['ordered_leaf_hashes']
forest=[]
for leaf in leaves:
    level=0
    while forest and forest[-1][0]==level:
        level_, lhs=forest.pop()
        leaf=sha(bytes([1])+lhs+leaf)
        level=level_+1
    forest.append((level,leaf))
assert [{'height':height,'digest':h.hex()} for height,h in forest] == d['lab_mmr']['peaks']
root=sha(bytes([2])+len(leaves).to_bytes(8,'big')+b''.join(level.to_bytes(2,'big')+hash_ for level,hash_ in forest)).hex()
assert root==d['lab_mmr']['root']
assert d['decision']['decision']=='ADMIT'
assert d['negative_control']['decision']=='REJECT'
print(json.dumps({'independent_lab_replay':'PASS','leaf_count':len(leaves),'root':root,'canonical_commitment':False,'signature':'NOT_SIGNED'},indent=2))
