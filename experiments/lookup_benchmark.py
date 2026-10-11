#!/usr/bin/env python3
"""New RDF 2026 exact-ID lookup microbenchmark; DOES NOT evaluate agent speed."""
import csv, io, json, random, statistics, sys, time, zipfile

def run(archive):
    with zipfile.ZipFile(archive) as z:
        names=[x.filename for x in z.infolist() if not x.is_dir()]
        if names != ["dataset-tickets-multi-lang3-4k.csv"]:
            raise ValueError("Wrong or ambiguous input archive")
        with z.open(names[0]) as f:
            rows=list(csv.DictReader(io.TextIOWrapper(f,encoding="utf-8-sig")))
    if len(rows)!=4000: raise ValueError("Expected pinned 4,000 rows")
    ids=random.Random(26011).choices(list(range(len(rows))),k=360)
    def scan(idx):
        for i,row in enumerate(rows):
            if i==idx: return row.get("priority","")
        raise KeyError(idx)
    t0=time.perf_counter_ns()
    by_id={i:r.get("priority","") for i,r in enumerate(rows)}
    build_ms=(time.perf_counter_ns()-t0)/1e6
    scan_times=[]; indexed_times=[]
    for k in range(5):
        queries=ids[k:]+ids[:k]
        t0=time.perf_counter_ns()
        scan_answers=[scan(i) for i in queries]
        scan_times.append((time.perf_counter_ns()-t0)/1e6)
        t0=time.perf_counter_ns()
        indexed_answers=[by_id[i] for i in queries]
        indexed_times.append((time.perf_counter_ns()-t0)/1e6)
        assert scan_answers==indexed_answers
    base=statistics.median(scan_times);idx=statistics.median(indexed_times)
    return dict(dataset_rows=len(rows),queries_per_round=len(ids),rounds=5,
      linear_median_ms=base,indexed_median_ms=idx,index_build_ms=build_ms,
      speedup_excluding_build_x=base/idx,correctness="PASS",
      claim_ceiling="LOCAL_KEYED_LOOKUP_ONLY_NOT_AGENT_OR_FCO_SPEED")
if __name__=="__main__":
    if len(sys.argv)!=2: raise SystemExit("usage: python lookup_benchmark.py /path/to/archive.zip")
    print(json.dumps(run(sys.argv[1]),indent=2))
