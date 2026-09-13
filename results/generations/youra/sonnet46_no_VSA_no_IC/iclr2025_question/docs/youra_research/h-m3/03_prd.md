# Product Requirements Document: H-M3

**Date:** 2026-08-21
**Hypothesis:** H-M3 — AUROC-Based Aggregation Comparison: Min vs. Mean Log-Prob Across Distribution Types
**Phase:** 3 — Implementation Planning
**Gate:** SHOULD_WORK
**Prerequisite:** H-M2 (VALIDATED)

---

## 1. Objective

Verify that AUROC(min) - AUROC(mean) ≥ 0.02 on TriviaQA and NQ, AND AUROC(mean) - AUROC(min) ≥ 0.02 on TruthfulQA, with bootstrap 95% CI lower bounds > 0 for both directions, for both LLaMA-2-7B and Mistral-7B-v0.1. H-M3 operationalizes the Spearman ρ rank-correlation patterns confirmed in H-M2 as AUROC differences, using pre-computed token log-prob aggregation scores from H-E1/H-M2.

This is a **re-analysis experiment**: no new model inference is required. The experiment loads pre-computed AUROC scores from H-E1 and applies bootstrap CI computation to test directional differences.

---

## 2. Background and Motivation

H-M2 confirmed directional rank-order correlation superiority:
- TriviaQA/NQ (peaked distributions): ρ(min) > ρ(mean) by 0.09–0.21, all CI intervals exclude zero
- TruthfulQA (flat distributions): ρ(mean) > ρ(min) by ~0.21, CI excludes zero

H-M3 tests whether these rank-correlation differences translate to AUROC differences with ≥ 0.02 margin. AUROC measures threshold-agnostic ranking ability directly; if aggregation-distribution alignment determines signal quality (as H-M1/H-M2 show), AUROC should replicate the same directional pattern.

Key insight: H-M3 re-uses the AUROC table computed in H-E1. The experiment only adds bootstrap CI computation on pairwise AUROC differences — a statistical re-analysis, not a new inference run.

---

## 3. Scope

### In Scope
- Loading pre-computed per-token log-prob aggregation scores (min, mean, raw_sum) from H-E1/H-M2 output files
- AUROC computation via `sklearn.metrics.roc_auc_score` per (model, dataset, aggregation)
- Bootstrap CI (n=1000, seed=42, percentile method) on each AUROC value and on pairwise differences
- Three datasets: TriviaQA, NQ-Open, TruthfulQA (same Farquhar 2023 splits as H-E1/H-M2)
- Two models: LLaMA-2-7B (primary), Mistral-7B-v0.1 (secondary replication)
- Three aggregation functions: min, mean, raw_sum
- Gate conditions: P1 (min > mean on TriviaQA/NQ), P2 (mean > min on TruthfulQA), P3 (raw-sum < both)
- Figures: 6-group AUROC bar chart (mandatory), AUROC difference heatmap, bootstrap distribution plots, P1/P2/P3 summary table

### Out of Scope
- New model inference (no GPU required for primary path)
- Fine-tuning or weight modification
- Datasets beyond TriviaQA, NQ-Open, TruthfulQA
- Models beyond LLaMA-2-7B and Mistral-7B-v0.1
- Sampling-based decoding

---

## 4. Data Specification

### 4.1 Primary Datasets (Pre-computed — no download required)

All datasets are loaded via H-E1/H-M2 pre-computed output files. **No new dataset download or model inference.**

| Dataset | Source | n (approx) | Pre-computed Output | Role |
|---------|--------|-----------|---------------------|------|
| TriviaQA | H-E1/H-M2 cached | 488 (LLaMA), 476 (Mistral) | `h-e1/results/trivia_qa_scores.pkl` | P1: min > mean |
| NQ-Open | H-E1/H-M2 cached | ≥500 | `h-e1/results/nq_open_scores.pkl` | P1 replication |
| TruthfulQA | H-E1/H-M2 cached | 810 (LLaMA), 796 (Mistral) | `h-e1/results/truthful_qa_scores.pkl` | P2: mean > min |

**Note:** Sample counts match H-M2 splits (same Farquhar 2023 splits). If pre-computed outputs unavailable, fallback to loading from H-M1/H-M2 code output.

### 4.2 Fallback Dataset Loading (If Pre-computed Files Unavailable)

If H-E1 pre-computed scores are unavailable, load datasets via HuggingFace (auto-download):
- `load_dataset("trivia_qa", "rc.nocontext", split="validation")` — auto-downloads, no manual step
- `load_dataset("nq_open", split="validation")` — auto-downloads
- `load_dataset("truthful_qa", "generation", split="validation")` — auto-downloads

**No manual dataset download tasks required** — all HuggingFace datasets are auto-downloaded.

### 4.3 Score File Format

Pre-computed score files from H-E1/H-M2:
```python
# Expected format (pickle or JSON):
scores = {
    "model": "llama-2-7b",
    "dataset": "trivia_qa",
    "samples": [
        {
            "id": "sample_id",
            "y_true": 1,           # Binary correctness label
            "min_log_prob": -2.3,  # Min token log-prob aggregation
            "mean_log_prob": -1.8, # Mean token log-prob aggregation
            "raw_sum": -36.4,      # Raw sum token log-prob
        },
        ...
    ]
}
```

---

## 5. Functional Requirements

### FR-1: Score Loading
- Load pre-computed scores from H-E1/H-M2 output directory
- Support both pickle (.pkl) and JSON (.json) formats
- Extract: `y_true` (binary), `min_log_prob`, `mean_log_prob`, `raw_sum` arrays
- Validate: n ≥ 400 samples per (model, dataset) pair; both classes present in `y_true`

### FR-2: AUROC Computation
- Compute `roc_auc_score(y_true, scores)` for each (model, dataset, aggregation) combination
- Handle sign convention: higher scores should predict correct; negate log-prob scores if needed (min/mean log-probs are negative — higher magnitude = more hallucinated; use `-log_prob` or directly if positive)
- 6 AUROC values per model: 3 datasets × {min, mean, raw_sum} = 9 per model, 18 total

### FR-3: Bootstrap CI on AUROC Values
- Bootstrap n=1000, seed=42, percentile method (consistent with H-E1/H-M1/H-M2)
- Resample with replacement; skip resamples where only one class present
- Per-AUROC CI: (ci_lower_2.5%, ci_upper_97.5%)
- Required for all 18 (model, dataset, aggregation) AUROC values

### FR-4: Bootstrap CI on Pairwise AUROC Differences
- Compute bootstrap CI on AUROC(min) - AUROC(mean) per (model, dataset)
- 6 pairwise difference CIs (3 datasets × 2 models)
- Method: paired bootstrap (resample same indices for both aggregations)

### FR-5: Gate Condition Verification
- P1: AUROC(min) - AUROC(mean) ≥ 0.02 AND CI lower > 0 for TriviaQA AND NQ, for both models
- P2: AUROC(mean) - AUROC(min) ≥ 0.02 AND CI lower > 0 for TruthfulQA, for both models
- P3: AUROC(raw_sum) < AUROC(min) AND AUROC(raw_sum) < AUROC(mean) for all datasets (directional, no threshold)
- Report gate pass/fail/partial with numeric evidence

### FR-6: Results Table Generation
- Full results table: rows = (model, dataset), columns = AUROC(min), AUROC(mean), AUROC(raw_sum), diff(min-mean), CI(diff)
- Gate conditions summary row (PASS/FAIL per condition)
- Save to `h-m3/results/auroc_table.csv` and `h-m3/results/auroc_table.json`

### FR-7: Visualization
- **Mandatory Figure 1:** 6-group AUROC bar chart — 3 benchmarks × 2 models; bars = min/mean/raw_sum per group; bootstrap 95% CI error bars; threshold lines at ±0.02 difference from reference bar
- **Figure 2:** AUROC difference heatmap — rows=model, columns=benchmark; cell = AUROC(min)-AUROC(mean); color-coded (blue=min wins, red=mean wins); CI annotation per cell
- **Figure 3:** Bootstrap distribution plots — histogram of bootstrap AUROC differences with CI bounds; one plot per key (model, dataset) comparison for P1/P2 conditions (4 plots: 2 models × {TriviaQA, TruthfulQA})
- **Figure 4:** P1/P2/P3 summary table rendered as styled figure
- All figures saved to `h-m3/figures/` directory

### FR-8: Experiment Runner
- Single entry point: `python run_experiment.py --config config.yaml`
- Hydra or argparse config; reproducible with `seed=42`
- Logs gate conditions to stdout and to `h-m3/results/gate_conditions.json`

---

## 6. Non-Functional Requirements

### NFR-1: Reproducibility
- All random operations seeded with seed=42
- Bootstrap results deterministic given fixed seed
- Results files saved with timestamp and config hash

### NFR-2: No GPU Required (Primary Path)
- Primary path: statistical re-analysis of pre-computed scores — CPU only
- Fallback path (if recomputing scores from scratch): requires ~24GB VRAM (7B models in fp16)

### NFR-3: Runtime
- Primary path (re-analysis): < 2 minutes on CPU
- Fallback path (new inference): 2–4 hours per model on single GPU

### NFR-4: Code Organization
- `h-m3/code/` directory mirrors H-M2 structure
- Reuse H-M2 data loading utilities where possible
- New code: bootstrap CI on AUROC differences only

---

## 7. Dependencies

### 7.1 Python Packages

```
numpy>=1.24
scipy>=1.11
scikit-learn>=1.3
matplotlib>=3.7
seaborn>=0.12
pandas>=2.0
tqdm>=4.65
pyyaml>=6.0
```

**Optional (fallback inference path only):**
```
torch>=2.0
transformers>=4.35
datasets>=2.18
accelerate>=0.25
```

### 7.2 Internal Dependencies

| Dependency | Source | Purpose |
|------------|--------|---------|
| H-E1 pre-computed scores | `h-e1/results/` | Primary input — AUROC table |
| H-M2 score files | `h-m2/results/` | Fallback if H-E1 scores unavailable |
| H-M2 data loading utils | `h-m2/code/data_utils.py` | Reuse for dataset loading (fallback path) |
| Farquhar 2023 splits | `jlko/semantic_uncertainty` (cached) | Dataset split indices |

### 7.3 External Repositories (Reference Only)

| Repository | URL | Used For |
|------------|-----|---------|
| jlko/semantic_uncertainty | https://github.com/jlko/semantic_uncertainty | Official dataset splits (cached in H-E1) |
| jacobgil/confidenceinterval | https://github.com/jacobgil/confidenceinterval | Bootstrap CI implementation reference |
| IINemo/lm-polygraph | https://github.com/IINemo/lm-polygraph | AUROC baseline reference values |

---

## 8. Success Criteria

| Criterion | Threshold | Gate |
|-----------|-----------|------|
| P1: AUROC(min) > AUROC(mean) on TriviaQA AND NQ | diff ≥ 0.02, CI lower > 0 | Both models |
| P2: AUROC(mean) > AUROC(min) on TruthfulQA | diff ≥ 0.02, CI lower > 0 | Both models |
| P3: raw_sum AUROC < min AND mean | directional (no threshold) | All datasets |
| All figures generated and saved | 4 figures in h-m3/figures/ | Required |
| Results table saved | auroc_table.csv + .json | Required |
| Code runs end-to-end from cached scores | < 2 min runtime | Required |

**Gate Outcomes:**
- **PASS:** P1 AND P2 confirmed on both models → H-M3 VALIDATED
- **PARTIAL / PIVOT:** P1 OR P2 (not both) → narrowed claim, document direction
- **FAIL / EXPLORE:** Neither P1 nor P2 → document as negative result, EXPLORE at larger scale

---

## 9. Acceptance Criteria

- [ ] `03_tasks.yaml` generated with ≤30 tasks
- [ ] AUROC table saved to `h-m3/results/auroc_table.csv`
- [ ] Gate conditions logged to `h-m3/results/gate_conditions.json`
- [ ] All 4 figures saved to `h-m3/figures/`
- [ ] `04_validation.md` records gate PASS/FAIL/PARTIAL with numeric evidence
- [ ] Bootstrap CI computed on all 18 AUROC values and 6 pairwise differences
- [ ] Code runs reproducibly from fixed seed=42
