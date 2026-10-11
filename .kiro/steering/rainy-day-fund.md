---
inclusion: always
---
# Make It Rain — Kiro steering
Project: `RDF-SFTW26-NEW-001` / public repo `biobitworks/rainy-day-fund`.
Read `AGENTS.md`, `docs/PROJECT_EXECUTOR_HANDOFF.md`, `docs/ATLAS_DATA_CONTRACT.md` and `docs/EXECUTOR_FIRST_PROMPT.md` before any edit.
- Primary: recursive harness; secondary: durable long-horizon recovery. Keep actual event-built source distinct from prior research.
- Core is independent Python (see `src/make_it_rain/harness.py`, `benchmarks/frozen_cases.json`, `tests/test_harness.py`, `notebooks/00_recursive_test.ipynb`).
- Official Atlas project `6acba49b5c102b1d2b95a0ac`, database `rainy_day_fund_sftw26`; no arbitrary Atlas cluster.
- Authenticated ElevenLabs webhook tools MUST call your backend, never Atlas directly. Scoped synthetic ticket only for public demos. Text path is mandatory fallback.
- Local `.env` is private and may be outside repo. Never read, print, send, publish, or overwrite its values. Source `.env` in shell locally only when authorized. Prefer `MONGODB_URI` env name.
- Tests before implementations: freeze fixture/oracle; model can propose config but cannot modify oracle, credentials, privileges or historical state. Commit new evidence and corrected successors; preserve failures.
- All experiments and protocols have top-to-bottom Jupyter notebooks and independent receipt replay. Claims must be status-labeled.
- Push small reviewable commits to a feature branch and share a PR with Sophia; avoid force push.
- Never represent MMR/root as canonical SIGNED or committed unless complete ordered-leaf, peaks/root, construction and verified signer receipts exist.
