# Product Requirements Document: H-M3

**Hypothesis:** H-M3 (MECHANISM — SHOULD_WORK)  
**Date:** 2026-08-25  
**Author:** yoon303@ust.ac.kr  
**Phase:** 3 — Implementation Planning  
**stepsCompleted:** [PRD]

---

## 1. Executive Summary

H-M3 tests whether per-benchmark training-corpus contamination level (13-gram overlap, from H-M1) predicts the per-benchmark accuracy differential between Pythia dedup-Pile and Pile models (from H-E1). This is a **downstream correlation analysis** over pre-computed vectors — no new model training or fine-tuning required. The experiment aggregates 4 benchmarks × 4 model sizes = 16 observations and computes Pearson and Spearman correlations. A secondary robustness check uses min-k% differentials from H-M2 as an alternative contamination predictor.

**H-M2 Limitation Note:** H-M2 (min-k% memorization signal) failed its SHOULD_WORK gate. H-M3 proceeds using H-M1 13-gram contamination estimates as the primary independent variable; H-M2 outputs are used as a secondary robustness check only.

---

## 2. Problem Statement

Prior results established:
- H-E1: Significant per-benchmark accuracy differentials exist between Pile and dedup-Pile Pythia models
- H-M1: Removed documents show higher 13-gram overlap with benchmark test sets; contamination estimates are non-uniform across benchmarks

H-M3 asks: **does the magnitude of contamination predict the magnitude of the accuracy differential?** If contamination is the causal mechanism, benchmarks with higher contamination should show larger accuracy drops under deduplication.

---

## 3. Functional Requirements

### FR-1: Data Loading

**FR-1.1** Load H-E1 accuracy differentials from `docs/youra_research/h-e1/results/accuracy_differentials.json`
- Format: `{model_size: {benchmark: float}}` — dedup-Pile accuracy minus Pile accuracy
- Model sizes: ["160m", "410m", "1b", "6.9b"]
- Benchmarks: ["mmlu", "hellaswag", "arc_challenge", "winogrande"]

**FR-1.2** Load H-M1 13-gram contamination estimates from `docs/youra_research/h-m1/results/contamination_estimates.json`
- Format: `{benchmark: float}` — mean 13-gram overlap rate for removed documents vs benchmark test sets
- 4 values (one per benchmark)

**FR-1.3** Load H-M2 min-k% differentials from `docs/youra_research/h-m2/results/mink_differentials.json` (secondary)
- Format: `{benchmark: float}` — mean min-k% score differential (Pile minus dedup-Pile)
- Status: PARTIAL — use as robustness check; may contain NaN for non-significant benchmarks
- If file missing or NaN: skip robustness check, proceed with primary analysis only

**FR-1.4** Validate all inputs:
- acc_diff_dict contains all 4 model sizes and all 4 benchmarks
- cont_est_dict contains all 4 benchmarks, no NaN values
- Raise ValueError with descriptive message on validation failure

### FR-2: Vector Construction

**FR-2.1** Build 16-observation analysis vectors:
- `cont_repeated`: tile contamination vector across 4 model sizes → shape (16,)
- `diff_flat`: flatten accuracy differential matrix (4 sizes × 4 benchmarks) → shape (16,)

**FR-2.2** Build 4-observation per-benchmark summary:
- Mean and std of accuracy differential across model sizes per benchmark

**FR-2.3** Build per-model-size vectors:
- For each model size: 4-point (contamination, differential) vectors

### FR-3: Correlation Analysis (Primary)

**FR-3.1** Pearson correlation on n=16 observations (cont_repeated vs diff_flat):
- `scipy.stats.pearsonr` → (r, p)

**FR-3.2** Spearman rank correlation on n=16 observations:
- `scipy.stats.spearmanr` → (rho, p)

**FR-3.3** Bootstrap 95% CI on Pearson r:
- 1000 resamples with replacement from 16 observations
- Fixed seed=42
- Report: [CI_lower, CI_upper]

**FR-3.4** Directional check:
- For each benchmark: classify sign of accuracy differential
- Count benchmarks where sign matches contamination-predicted direction
- Expected: high contamination → negative differential (dedup-Pile worse when contamination removed)
- Report: n_correct_direction / 4

### FR-4: Robustness Checks (Secondary)

**FR-4.1** Ablation 1 — Contamination estimator comparison:
- Repeat FR-3.1–FR-3.3 using H-M2 min-k% differential as contamination predictor
- Compare r values (13-gram vs min-k%); flag if they disagree (|r_13gram - r_mink| > 0.3)

**FR-4.2** Ablation 2 — Aggregation strategy comparison:
- Option A: n=16 flattened (primary, FR-3.1)
- Option B: n=4 benchmark-level (average across model sizes first, then Pearson)
- Report both; note that n=4 requires r≥0.95 for p<0.05 significance

**FR-4.3** Ablation 3 — Token-count vs step-count matching:
- If H-E1 provides step-matched differentials: repeat correlation under step matching
- If not available: note as future work

**FR-4.4** Ablation 4 — Per-model-size breakdown:
- Run Pearson separately for each model size (n=4 per size)
- Report r per size; expect 6.9B > 1B > 410M > 160M

### FR-5: Visualization

**FR-5.1** Required figure: Scatter plot (contamination estimate vs accuracy differential)
- x-axis: contamination estimate (13-gram overlap rate per benchmark)
- y-axis: accuracy differential (dedup-Pile minus Pile, averaged across model sizes)
- Points labeled by benchmark name
- Linear regression line with r value and p-value annotated
- Saved to `docs/youra_research/h-m3/figures/scatter_contamination_vs_differential.png`

**FR-5.2** Correlation heatmap: Pearson r by model_size × contamination estimator (2 estimators × 4 model sizes)
- Saved to `docs/youra_research/h-m3/figures/correlation_heatmap.png`

**FR-5.3** Per-benchmark accuracy differential bar chart (4 benchmarks × 4 model sizes, colored by contamination level)
- Saved to `docs/youra_research/h-m3/figures/per_benchmark_differential.png`

**FR-5.4** Bootstrap CI plot: histogram of Pearson r distribution under 1000 bootstrap resamples
- Saved to `docs/youra_research/h-m3/figures/bootstrap_ci.png`

**FR-5.5** Spearman rank visualization: contamination rank vs differential rank for 4 benchmarks
- Saved to `docs/youra_research/h-m3/figures/spearman_ranks.png`

### FR-6: Results Serialization

**FR-6.1** Save primary results to `docs/youra_research/h-m3/results/correlation_results.json`:
```json
{
  "pearson_r": float,
  "pearson_p": float,
  "spearman_rho": float,
  "spearman_p": float,
  "bootstrap_ci_95": [float, float],
  "n_observations": 16,
  "n_correct_direction": int,
  "contamination_vector": {benchmark: float},
  "accuracy_differential_matrix": {model_size: {benchmark: float}}
}
```

**FR-6.2** Save ablation results to `docs/youra_research/h-m3/results/ablation_results.json`

**FR-6.3** Save per-benchmark summary to `docs/youra_research/h-m3/results/per_benchmark_summary.json`

**FR-6.4** Save gate verdict to `docs/youra_research/h-m3/results/gate_verdict.json`:
```json
{
  "gate_type": "SHOULD_WORK",
  "primary_pass": bool,  // pearson_r >= 0.5 AND pearson_p < 0.05
  "spearman_pass": bool,
  "directional_pass": bool,  // n_correct_direction >= 3
  "overall_verdict": "PASS" | "PARTIAL" | "EXPLORE",
  "notes": str
}
```

**FR-6.5** Generate markdown report at `docs/youra_research/h-m3/results/report.md`

---

## 4. Data Specification

### Primary Inputs (Inherited — File-Based)

| Dataset | Source | Path | Format |
|---------|--------|------|--------|
| Accuracy differentials | H-E1 results | `h-e1/results/accuracy_differentials.json` | {model: {bench: float}} |
| Contamination estimates | H-M1 results | `h-m1/results/contamination_estimates.json` | {bench: float} |
| Min-k% differentials | H-M2 results | `h-m2/results/mink_differentials.json` | {bench: float} (optional) |

### Benchmark Coverage

| Benchmark | Full Test Set Size | Split Used |
|-----------|-------------------|------------|
| MMLU | ~14,000 items | Full test |
| HellaSwag | ~10,000 items | Full test |
| ARC-Challenge | ~1,172 items | Full test |
| WinoGrande | ~1,267 items | Full test |

**No manual data download required** — all inputs are pre-computed result files from H-E1 and H-M1.

### Output Directory Structure

```
docs/youra_research/h-m3/
├── results/
│   ├── correlation_results.json
│   ├── ablation_results.json
│   ├── per_benchmark_summary.json
│   ├── gate_verdict.json
│   └── report.md
├── figures/
│   ├── scatter_contamination_vs_differential.png
│   ├── correlation_heatmap.png
│   ├── per_benchmark_differential.png
│   ├── bootstrap_ci.png
│   └── spearman_ranks.png
└── code/
    ├── analyze.py          # Main analysis pipeline
    ├── data_loader.py      # Load H-E1/H-M1/H-M2 results
    ├── correlation.py      # Pearson/Spearman + bootstrap
    ├── ablations.py        # Ablation 1–4 runners
    ├── visualize.py        # All figure generation
    └── report_generator.py # Markdown report
```

---

## 5. Non-Functional Requirements

**NFR-1:** Analysis must complete in < 60 seconds on CPU (no GPU required)  
**NFR-2:** Bootstrap CI uses fixed seed=42 for reproducibility  
**NFR-3:** All result files in UTF-8 JSON with 4-decimal float precision  
**NFR-4:** Graceful degradation — if H-M2 results unavailable, skip robustness checks without crashing  
**NFR-5:** Code is self-contained; no external API calls at runtime  
**NFR-6:** Result JSON files must be backward-compatible (add fields, never remove)

---

## 6. Success Criteria

### Gate Metrics (SHOULD_WORK)

| Metric | Threshold | Pass |
|--------|-----------|------|
| Pearson r | ≥ 0.5 | Primary gate |
| Pearson p | < 0.05 | Primary gate |
| Spearman ρ | ≥ 0.5 | Supporting |
| Spearman p | < 0.05 | Supporting |
| Directional | ≥ 3/4 benchmarks correct | Supporting |

**PASS:** Pearson r ≥ 0.5 AND p < 0.05  
**PARTIAL:** 0.3 ≤ r < 0.5 AND p < 0.05 (or directional ≥ 3/4)  
**EXPLORE:** r < 0.3 → try additional benchmarks; investigate data-volume confound  
**Failure gate type:** SHOULD_WORK — does not block H-M4

---

## 7. Dependencies

### 7.1 Python Packages

```
numpy>=1.24
scipy>=1.10
pandas>=2.0
matplotlib>=3.7
seaborn>=0.12
```

### 7.2 External Repositories (Reference Only)

- EleutherAI/lm-evaluation-harness — used in H-E1 (inherited results)
- google-research/deduplicate-text-datasets — used in H-M1 (inherited results)
- swj0419/detect-pretrain-code — used in H-M2 (inherited results, secondary)

### 7.3 Prerequisite Results

| Prerequisite | Required Files | Status |
|-------------|----------------|--------|
| H-E1 | `h-e1/results/accuracy_differentials.json` | MUST EXIST |
| H-M1 | `h-m1/results/contamination_estimates.json` | MUST EXIST |
| H-M2 | `h-m2/results/mink_differentials.json` | OPTIONAL (graceful degradation) |

---

## 8. Constraints and Assumptions

- No model training required — purely analytical
- H-E1 and H-M1 outputs are treated as ground truth; no re-evaluation needed
- With n=16, Pearson p<0.05 requires r≥0.50 (achievable; verified analytically)
- With n=4 (per-benchmark only), Pearson p<0.05 requires r≥0.95 — this is why n=16 aggregation is primary
- Contamination estimates from H-M1 are per-benchmark scalar values (not per-item)
- The experiment is deterministic given fixed seed=42

---

## 9. Out of Scope

- Re-running lm-evaluation-harness (H-E1 already computed)
- Re-running contamination estimation (H-M1 already computed)
- Model fine-tuning or new checkpoint evaluation
- Additional benchmark sets beyond the 4 defined (unless EXPLORE mode triggered)
- Real-time or streaming analysis
