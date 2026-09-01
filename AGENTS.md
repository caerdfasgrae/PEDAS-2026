# AGENTS INSTRUCTION GUIDE: PeDaS 2026 Phishing Detection
> Auto-read file for autonomous AI coding agents (Antigravity, Hermes Agent, Claude Code, Cursor).
> Full instructions detailed in [HERMES.md](file:///c:/Users/SMI-CPU014/Documents/Abyan/PEDAS-2026/HERMES.md).

## Quick Context
- **Competition**: Pesta Data Nasional (PeDaS 2026) - APTIKOM Fest x PANDI
- **Case**: Deteksi Phishing domain `.id`
- **Core Rules**: Python ONLY, Deterministic (`RANDOM_STATE = 42`), No domain group leakage (`StratifiedGroupKFold`).
- **Test Command**: `.\.venv\Scripts\python.exe -m pytest tests/ -v`
- **Evaluation Command**: `.\.venv\Scripts\python.exe run_baseline.py --model ensemble --ngram-stacking`
- **Benchmark Data Output**: `data/benchmark/benchmark_expanded_id.csv`
- **Brand Dictionary**: `config/indonesian_brands.yaml`
