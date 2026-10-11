# Make It Rain — isolated, synthetic/aggregate evidence (2026-10-11)

**Scope:** new work in RDF-SFTW26-NEW-001, built after the hackathon start. No pre-existing FCO/FCG implementation is imported.

## Verified
- Official event Atlas `rainy_day_fund_sftw26` readback: **6 newly authored metadata-only candidate FCO projection records**, **5 typed graph edges**, **1 receipt**.
- Local user-provided CSV archive: 4,000 multilingual *synthetic* tickets, aggregate distribution only; no raw ticket descriptions or answer texts published.
- Four private screen recordings re-encoded to 960px / 3 fps H.264 MP4 **without audio**. Media compression achieved **98.39% size reduction** (326,299,686 to 5,266,623 bytes); decode check PASS. These files are **not public**, because screenshots may contain personal information or credentials.
- Local **exact-ID lookup** microbenchmark: 360 queries, 5 rounds; index and linear scan returned identical results. Measured median timings in `lookup_benchmark_v2_corrected.json` (the original benchmark file was explicitly retracted and remains in Git history).

## Claims ceiling
This benchmark measures **local in-memory keyed lookup only**, not FCO/FCG acceleration, ElevenLabs response speed, Raindrop grading speed, or end-to-end ticket resolution. The 12 frozen synthetic event fixtures were not modified.

The candidate graph is an **isolated newly authored metadata projection**. Its independently recomputed local digest is *not* an official FCO/FCG commitment, and no MMR was appended. Atlas projections are not byte-identical to the locally sealed graph.

## Withheld
Original `.mov` recordings, compressed videos, screenshots, original uploaded Kaggle CSV, private code/data from other projects, participant contact details, audio, account interfaces, and private graph content. These must pass explicit rights, privacy, attribution and security approval before public publication.

## Dataset provenance
User-uploaded `archive.zip` contained `dataset-tickets-multi-lang3-4k.csv`. It resembles the [Kaggle Customer IT Support ticket dataset](https://www.kaggle.com/datasets/tobiasbueck/multilingual-customer-support-tickets), but exact archive-to-upstream provenance and redistribution license remain **UNVERIFIED**. No source rows are included here.

## Reproduce
Download an authorized copy of the exact CSV archive, keep it **outside Git**, and run `python experiments/lookup_benchmark.py /private/path/to/archive.zip`. Environment and benchmark timings will vary. Graph verification notebook and private-source media are provided separately to the authorized operator.

**Release:** Only originally authored text, code and aggregate metrics here. Do not interpret artifact hashes as scientific truth or graph edges as proof of causality.
