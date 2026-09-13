# Phase 4 Validation Report: H-M1

**Generated:** 2026-07-30T07:22:40Z  
**Execution Mode:** UNATTENDED  
**Pipeline Position:** Phase 3 → [Phase 4] → Phase 5  
**Hypothesis Type:** MECHANISM  
**Gate Type:** MUST_WORK  

---

## Hypothesis Summary

| Field | Value |
|-------|-------|
| **ID** | H-M1 |
| **Statement** | Under the joint dataset of N≥30 open-weight LLMs (H-E1 passed), MMLU Spearman rho² with TruthfulQA MC2 and with BBQ accuracy will both exceed 0.05, confirming MMLU as a valid scale covariate |
| **Type** | MECHANISM — verifies causal pre-condition |
| **Prerequisites** | H-E1 (VALIDATED, N=297, match_rate=1.000) |
| **Duration** | < 1 second (CPU-only statistical analysis) |

---

## Code Generation Summary

### Task Statistics

| Metric | Value |
|--------|-------|
| Total Tasks | 11 |
| Completed | 11 |
| Coder-Validator Cycles | 1/5 |
| SDD Phases (TEST→IMPL→VERIFY) | All passed |

### Generated Files

| File | Description |
|------|-------------|
| `code/config.py` | AnalysisConfig dataclass (data paths, gate thresholds, figure settings) |
| `code/analyze.py` | All analysis logic: load_data, compute_correlations, verify_mechanism_activated, 4 plot functions, save_results, run orchestrator |
| `code/main.py` | Entry point: loads config, calls run(), prints gate result |
| `code/requirements.txt` | scipy≥1.10, pingouin≥0.5, pandas≥1.5, numpy≥1.23, matplotlib≥3.6, seaborn≥0.12 |
| `code/tests/test_analyze.py` | 12 spec compliance tests |
| `code/results/h_m1_results.json` | Structured experiment results |
| `code/results/h_m1_summary.txt` | Human-readable summary |

---

## Code Quality Checklist

- [✓] Syntax validation passed (12/12 pytest tests pass)
- [✓] API signatures match 03_logic.md exactly
- [✓] AnalysisConfig fields match 03_config.md
- [✓] File structure matches 03_architecture.md
- [✓] Real data used (H-E1 LLM CSV + BBQ per-model scores joined via exact merge)
- [✓] Gate computation matches 02c spec exactly
- [✓] Mechanism activation verified

**Note:** H-E1 joint CSV did not include `bbq_accuracy` column (H-E1 used ARC Challenge proxy per spec). H-M1 correctly joins `h-e1/code/data/bbq_scores/bbq_per_model.csv` (N=300 models) with LLM Leaderboard via exact `model_name` join, yielding N=299 matched → N=296 after dropna.

---

## Experiment Results

### Primary Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| N (complete rows) | 296 | ≥ 30 | ✅ PASS |
| R²(MMLU × TruthfulQA MC2) | **0.4927** | > 0.05 | ✅ PASS (9.9× threshold) |
| R²(MMLU × BBQ accuracy) | **0.7634** | > 0.05 | ✅ PASS (15.3× threshold) |

### Detailed Correlation Results

| Pair | rho | R² | p-value |
|------|-----|-----|---------|
| MMLU × TruthfulQA MC2 | 0.7019 | 0.4927 | 3.15e-45 |
| MMLU × BBQ accuracy | 0.8737 | 0.7634 | 5.01e-94 |
| TruthfulQA × BBQ (baseline for H-M2) | 0.7322 | — | 5.83e-51 |

### Mechanism Activation Indicators

| Indicator | Status |
|-----------|--------|
| N ≥ 30 | ✅ True (N=296) |
| R²(MMLU×TruthfulQA) non-NaN, in [0,1] | ✅ True |
| R²(MMLU×BBQ) non-NaN, in [0,1] | ✅ True |
| gate_pass key computed | ✅ True |
| baseline rho(TruthfulQA, BBQ) computed | ✅ True |

---

## Gate Evaluation

| Field | Value |
|-------|-------|
| **Gate Type** | MUST_WORK |
| **Criterion 1** | R²(MMLU×TruthfulQA) > 0.05 |
| **Criterion 2** | R²(MMLU×BBQ) > 0.05 |
| **Result** | **PASS** |
| **Satisfied** | **True** |
| **Reason** | Both R² values greatly exceed threshold (0.493, 0.763 vs 0.05) |

**Interpretation:** MMLU is strongly correlated with both TruthfulQA MC2 (rho=0.70) and BBQ accuracy (rho=0.87) in the joint dataset. Controlling for MMLU in H-M2 partial Spearman analysis is justified — MMLU functions as a valid scale covariate for both alignment benchmarks.

---

## Figures Generated

| Figure | Path | Description |
|--------|------|-------------|
| R² Bar Chart | `figures/h_m1_r2_bar.png` | R²(MMLU×TruthfulQA) and R²(MMLU×BBQ) vs 0.05 threshold (both green) |
| Scatter MMLU×TruthfulQA | `figures/h_m1_scatter_mmlu_truthqa.png` | 296 points, rho=0.702 annotated |
| Scatter MMLU×BBQ | `figures/h_m1_scatter_mmlu_bbq.png` | 296 points, rho=0.874 annotated |
| Correlation Heatmap | `figures/h_m1_heatmap.png` | Spearman matrix {MMLU, TruthfulQA, BBQ} |

---

## Next Steps

**Gate PASSED → Proceed to Phase 5 (Baseline Comparison)**

H-M2 (partial Spearman analysis) is now authorized to proceed:
- Raw baseline: rho(TruthfulQA, BBQ) = 0.7322 (for Fisher z difference test in H-M2)
- MMLU confirmed as valid covariate: partial Spearman controlling for MMLU will be meaningful

---

## Phase 2C Handoff

### Proven Components

| Component | File | Evidence |
|-----------|------|----------|
| `load_data()` | `code/analyze.py` | Loads 296 real LLM models, joins BBQ scores, normalizes correctly |
| `compute_correlations()` | `code/analyze.py` | Correct scipy.stats.spearmanr usage; R²=rho²; gate evaluated |
| `verify_mechanism_activated()` | `code/analyze.py` | All 5 checks passed |
| `AnalysisConfig` | `code/config.py` | Dataclass with all required fields; path resolution works |
| Figure generation (×4) | `code/analyze.py` | All 4 figures saved to `figures/` |
| `save_results()` | `code/analyze.py` | JSON + TXT saved successfully |
| `run()` orchestrator | `code/analyze.py` | End-to-end flow verified |
| `main.py` | `code/main.py` | Entry point with argparse; exits 0 on gate PASS or publishable null |

### Optimal Hyperparameters

```yaml
# H-M1 is parameter-free (statistical analysis)
data:
  n_join: 299  # models matched between LLM LB v1 and BBQ scores
  n_complete: 296  # after dropna
gate:
  r2_threshold: 0.05  # confirmed well-exceeded
seed: 42
```

### Key Scientific Findings

- **R²(MMLU×TruthfulQA) = 0.493** — MMLU explains ~49% of variance in TruthfulQA ranking
- **R²(MMLU×BBQ) = 0.763** — MMLU explains ~76% of variance in BBQ accuracy ranking
- Both correlations are extraordinarily statistically significant (p < 10⁻⁴⁴)
- **Baseline rho(TruthfulQA, BBQ) = 0.732** — strong raw correlation; H-M2 will test if this survives MMLU partialing

### Lessons Learned

**What Worked:**
- Exact merge on `model_name` between LLM Leaderboard and BBQ per-model scores (N=299, ~100% match rate)
- scipy.stats.spearmanr handles ties via rank averaging — appropriate for benchmark scores
- Single-file flat analysis structure (mirrored from H-E1) keeps complexity minimal

**What Didn't Work:**
- Initial `data_path` pointed to single CSV without BBQ column — H-E1 joint CSV only has TruthfulQA+MMLU, not BBQ. Fixed by joining `bbq_scores/bbq_per_model.csv`.

**Key Insight:**
- The BBQ data was already available in H-E1's data directory (`h-e1/code/data/bbq_scores/bbq_per_model.csv` with N=300 model scores). No new download was required — the data was pre-cached by H-E1.

### Recommendations for Dependent Hypotheses (H-M2)

- **Reuse:** `code/analyze.py` functions `load_data()`, `compute_correlations()` are directly reusable
- **Input for H-M2:** `raw_rho_truth_bbq = 0.7322` (Fisher z baseline); use `experiment_results.json` as input
- **Data path:** `h-e1/code/data/llm_leaderboard_v1/llm.csv` + `h-e1/code/data/bbq_scores/bbq_per_model.csv` — same join pattern applies
- **Warning:** bbq_accuracy is stored as fraction [0,1] in `bbq_per_model.csv`; H-M2 code must normalize to [0,100] or work in [0,1] — the normalization in `load_data()` handles this

---

## Appendix

### Files Reference

```
docs/youra_research/h-m1/
├── 04_validation.md          ← This file
├── experiment_results.json   ← Structured results
├── figures/
│   ├── h_m1_r2_bar.png
│   ├── h_m1_scatter_mmlu_truthqa.png
│   ├── h_m1_scatter_mmlu_bbq.png
│   └── h_m1_heatmap.png
└── code/
    ├── config.py
    ├── analyze.py
    ├── main.py
    ├── requirements.txt
    ├── results/
    │   ├── h_m1_results.json
    │   └── h_m1_summary.txt
    └── tests/
        └── test_analyze.py
```

### Data Lineage

| Source | File | N |
|--------|------|---|
| LLM Leaderboard v1 | `h-e1/code/data/llm_leaderboard_v1/llm.csv` | 500 models |
| BBQ per-model scores | `h-e1/code/data/bbq_scores/bbq_per_model.csv` | 300 models |
| Inner join (model_name) | — | 299 models |
| After dropna | — | **296 models** |

### Gate Compliance

**MUST_WORK gate criteria:**
1. R²(MMLU, TruthfulQA MC2) > 0.05 → **0.4927 ✅**
2. R²(MMLU, BBQ accuracy) > 0.05 → **0.7634 ✅**

**Gate: PASS → H-M2 authorized to proceed**
