"""Run isolated synthetic baseline and emit inspectable evidence."""
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from make_it_rain.harness import run_fixture
p=ROOT/'benchmarks/frozen_cases.json'
fixture=json.loads(p.read_text(encoding='utf-8'))
r=run_fixture(fixture)
output=ROOT/'results'
output.mkdir(exist_ok=True)
(output/'local_synthetic_evaluation.json').write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
summary={"baseline":f"{r['baseline']['passed']}/{r['baseline']['total']}",
         "candidate":f"{r['candidate']['passed']}/{r['candidate']['total']}",
         "decision":r['decision']['decision'],"negative_control":r['negative_control']['decision'],
         "lab_root":r['lab_mmr']['root']}
print(json.dumps(summary,indent=2))
