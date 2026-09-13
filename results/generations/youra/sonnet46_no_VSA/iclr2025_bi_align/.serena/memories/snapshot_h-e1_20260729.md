# Hypothesis Completion Snapshot: h-e1

**Date:** 2026-07-29T21:20:00+00:00
**Hypothesis:** h-e1
**Statement:** MMLU aggregate score is a valid scale covariate for AlpacaEval-LC win rate: R²(MMLU → AlpacaEval-LC) > 0.10, confirming MMLU captures the scale signal for the preference-based metric
**Final Status:** COMPLETED
**Gate Result:** PASS
**Gate Type:** MUST_WORK

## Results
- Spearman r = 0.5656
- R² = 0.3199 (gate threshold > 0.10 → PASS, 3.2× above threshold)
- p-value = 0.0017 (gate threshold < 0.05 → PASS)
- N = 28 matched models (WARNING: < MIN_N=30)

## Key Findings
- MMLU explains 32% of AlpacaEval-LC rank variance — valid covariate for h-m1 partial Spearman
- AlpacaEval v1 leaderboard used (data_AlpacaEval/, NOT data_AlpacaEval_2/ which 404s)
- N=28 underpowered vs MIN_N=30; h-m1 should use lower fuzzy threshold or add data sources

## Proven Components (reusable)
- loader.py: load_alpaca_eval(), load_llm_leaderboard()
- joiner.py: fuzzy_join() with rapidfuzz WRatio threshold=80
- analyzer.py: run_spearman_gate() with scipy.stats.spearmanr
- visualizer.py: 4 matplotlib figures
- exporter.py: JSON + CSV export

## Data Sources
- AlpacaEval-LC v1: https://raw.githubusercontent.com/tatsu-lab/alpaca_eval/main/src/alpaca_eval/leaderboards/data_AlpacaEval/alpaca_eval_gpt4_leaderboard.csv
- Open LLM LB: https://huggingface.co/datasets/optimum-benchmark/llm-perf-leaderboard/raw/d9316a118b84d1cdc97518e92b29f22af7a63678/llm-df.csv

---
*Per-hypothesis snapshot for Phase 2A reference*
