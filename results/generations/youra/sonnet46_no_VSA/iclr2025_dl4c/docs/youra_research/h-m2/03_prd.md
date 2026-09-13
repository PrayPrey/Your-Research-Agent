# Product Requirements Document: H-M2
# Spearman Correlation: Embedding Alignment vs Pass@1 Rank

**Status:** DRAFT
**Hypothesis:** H-M2 (MECHANISM — SHOULD_WORK)
**Date:** 2026-08-02
**Phase:** 3 — Implementation Planning
**stepsCompleted:** [1, 2, 3, 4, 5, 6, 7]

---

## 1. Executive Summary

This experiment tests whether code-embedding distributional alignment (training source → test benchmark cosine similarity) predicts SFT pass@1 rank order across four source conditions. The mechanism is tested via Spearman rank correlation + permutation test (10,000 shuffles) over pre-computed matrices from H-E1 and H-E2. No model training is required — this is a pure statistical analysis consuming upstream pipeline outputs.

**Gate Type:** SHOULD_WORK — failure weakens mechanistic claim but does not block Phase 5 (H-D1 remains testable through other evidence).

**Gate Condition:** Spearman ρ > 0 AND permutation p < 0.05 for ≥1 (benchmark × encoder × model_size) cell, with both CodeBERT and all-MiniLM-L6-v2 encoders agreeing in direction (ρ > 0) for that cell's benchmark.

---

## 2. Problem Statement

H-E1 confirmed that the four SFT training sources produce measurably distinct code-embedding distributions. H-E2 confirmed that source identity produces a statistically significant main effect on pass@1 at 1.3B scale. H-M2 now asks: does the *rank order* of embedding similarity (source → benchmark proximity) predict the *rank order* of pass@1? If so, this provides mechanistic evidence for the distributional alignment hypothesis (H-D1): models trained on closer-distribution data should perform better on the aligned benchmark.

**Key challenge:** n=4 conditions means the minimum achievable permutation p-value is 1/24 ≈ 0.042. Perfect rank concordance is required for significance. CodeBERT similarity range is highly compressed (0.909–0.980), which may suppress ρ for CodeBERT cells — but MiniLM separation (0.247–0.311) should enable meaningful rank discrimination.

---

## 3. Functional Requirements

### FR-1: Load H-E1 Similarity Matrices

Load pre-computed mean pairwise cosine similarity matrices from H-E1 outputs:

- `docs/youra_research/h-e1/results/similarity_matrix_codebert.npy` → shape (4, 2): [source_conditions × benchmarks]
- `docs/youra_research/h-e1/results/similarity_matrix_minilm.npy` → shape (4, 2): [source_conditions × benchmarks]

**Source condition ordering (rows):** [HumanEval-only, MBPP-only, LeetCode-only, Equal-mix]  
**Benchmark ordering (columns):** [HumanEval+, MBPP+]

Verify shape == (4, 2), no NaNs, and similarity values in [0, 1] range.

### FR-2: Load H-E2 Pass@1 Results

Load pass@1 per condition from H-E2 outputs:

- `docs/youra_research/h-e2/results/pass_at_1_1b.json`
  - Format: `{"source_condition": {"humaneval+": float, "mbpp+": float}}` per seed
  - OR: aggregated means if H-E2 already averaged seeds

Compute mean pass@1 across seeds (3 seeds) per (source_condition × benchmark) → result shape (4, 2).

**H-C1 (optional):** If `docs/youra_research/h-c1/results/pass_at_1_7b.json` exists, load and process identically for 7B scale analysis.

### FR-3: Core Statistical Analysis — Spearman Permutation Test

For each (benchmark × encoder × model_size) cell:

1. Extract sim_vector: shape (4,) — mean similarity for each source condition to this benchmark
2. Extract pass_vector: shape (4,) — mean pass@1 for each source condition on this benchmark
3. Verify rank variation: `len(np.unique(pass_vector)) > 1` — if all identical, mark cell as CANNOT_TEST
4. Run permutation test:
   ```python
   def statistic(x):
       return stats.spearmanr(x, pass_vector).statistic
   result = stats.permutation_test(
       (sim_vector,), statistic,
       permutation_type='pairings',
       n_resamples=10000,
       alternative='greater',
       random_state=42
   )
   ```
5. Record: rho, pvalue, significant (pvalue < 0.05), null_distribution

**Fallback for ties:** If Spearman returns NaN (tied ranks), use `stats.kendalltau` as primary metric instead.

### FR-4: Bootstrap Confidence Intervals

For each cell compute 95% bootstrap CI for ρ:

```python
bootstrap_rhos = []
rng = np.random.default_rng(42)
for _ in range(1000):
    idx = rng.integers(0, 4, size=4)
    if len(np.unique(idx)) < 2:
        continue
    bootstrap_rhos.append(stats.spearmanr(sim_vector[idx], pass_vector[idx]).statistic)
ci_lo, ci_hi = np.nanpercentile(bootstrap_rhos, [2.5, 97.5])
```

### FR-5: Supplementary Kendall's τ Analysis

For each cell compute Kendall's τ as robustness check:
```python
tau, tau_p = stats.kendalltau(sim_vector, pass_vector, alternative='greater')
```
Report alongside ρ — concordance between Spearman and Kendall strengthens evidence.

### FR-6: Pretraining-vs-SFT Null Check (Falsification)

If baseline pretraining similarity data is available (or can be approximated from H-E1 base model embeddings), compute whether pretraining corpus similarity predicts pass@1 better than SFT-source similarity. If pretraining beats SFT alignment, the mechanism claim is weakened.

**Implementation:** Optional — if H-E1 outputs do not include pretrain similarity matrices, document as "not testable" in results.

### FR-7: Dual-Encoder Concordance Validation

Gate requires both encoders to agree in direction (ρ > 0) for a benchmark. Compute:
- `concordant`: bool — (ρ_codebert > 0) AND (ρ_minilm > 0) for same benchmark

At least 1 benchmark must show concordance AND significance.

### FR-8: Results Persistence

Save all results to `docs/youra_research/h-m2/results/`:

| File | Content |
|------|---------|
| `correlation_results.json` | Full per-cell results (rho, pvalue, ci, tau, etc.) |
| `rank_comparison_table.csv` | Source conditions × rank columns for embedding and pass@1 |
| `gate_evaluation.json` | Gate satisfied/falsified, supporting evidence |
| `null_distributions/cell_*.npy` | Null distribution arrays per cell |

### FR-9: Visualization

Save all figures to `docs/youra_research/h-m2/figures/`:

| Figure | Description |
|--------|-------------|
| `fig1_rho_bar_chart.png` | Bar chart of ρ per cell, significance markers (* p<0.05) |
| `fig2_scatter_panels.png` | Scatter (embedding rank vs pass@1 rank), one panel per cell |
| `fig3_null_distribution.png` | Null ρ histogram for most significant cell, observed ρ marked |
| `fig4_rank_heatmap.png` | Heatmap of condition rankings (embedding vs performance) |
| `fig5_dual_encoder.png` | Scatter of CodeBERT ρ vs MiniLM ρ per benchmark |

---

## 4. Data Specification

| Input | Source | Path | Format | Size |
|-------|--------|------|--------|------|
| Similarity matrix (CodeBERT) | H-E1 output | `h-e1/results/similarity_matrix_codebert.npy` | numpy float32 | 4×2 |
| Similarity matrix (MiniLM) | H-E1 output | `h-e1/results/similarity_matrix_minilm.npy` | numpy float32 | 4×2 |
| Pass@1 at 1.3B | H-E2 output | `h-e2/results/pass_at_1_1b.json` | JSON dict | 4×2×3 seeds |
| Pass@1 at 7B (optional) | H-C1 output | `h-c1/results/pass_at_1_7b.json` | JSON dict | 4×2×3 seeds |

**No new dataset downloads required.** All inputs are pipeline artifacts.

**Conditions:**
- Source conditions (n=4): HumanEval-only (HE), MBPP-only (MB), LeetCode-only (LC), Equal-mix (EQ)
- Benchmarks (n=2): HumanEval+ (164 problems), MBPP+ (374 problems)
- Encoders (n=2): CodeBERT, MiniLM
- Model sizes: 1.3B (required), 7B (optional, H-C1)

---

## 5. Evaluation Metrics

### Primary Metrics (Gate Conditions)

| Metric | Target | Cell |
|--------|--------|------|
| Spearman ρ | > 0 | All cells |
| Permutation p-value | < 0.05 | ≥1 cell |
| Dual-encoder concordance | ρ > 0 for both encoders | ≥1 benchmark |

### Secondary Metrics

| Metric | Purpose |
|--------|---------|
| Kendall's τ | Robustness check alongside ρ |
| Bootstrap 95% CI for ρ | Uncertainty quantification |
| Null distribution spread | Visualize permutation test |
| Pretraining vs SFT comparison | Falsification attempt |

### Gate Evaluation

```
GATE_SATISFIED:
  ρ > 0 AND p < 0.05 for ≥1 cell
  AND both encoders ρ > 0 for same benchmark

GATE_FALSIFIED:
  ρ ≤ 0 OR p ≥ 0.05 for ALL cells
  OR pretraining similarity predicts pass@1 better than SFT similarity

GATE_CANNOT_TEST:
  All pass@1 values identical (no rank variation)
  OR H-E1/H-E2 result files missing
```

---

## 6. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seed (`np.random.seed(42)` + `random_state=42` in permutation test)
- All results saved to JSON/CSV for exact reproduction

### NFR-2: Runtime
- Total wall-clock time: <60 seconds (pure statistical computation, no model inference)
- Permutation test with 10,000 shuffles on n=4: <1 second per cell

### NFR-3: Dependency Minimality
- Required: `scipy>=1.7.0`, `numpy>=1.21`, `matplotlib>=3.4`, `seaborn>=0.11`
- All packages likely already installed from H-E1/H-E2 experiments

### NFR-4: Graceful Degradation
- If H-C1 not available → skip 7B cells, report 1.3B only
- If CodeBERT similarity range too compressed for meaningful ρ → document as known limitation, do not falsify gate on this basis alone
- If any cell has NaN ρ (ties) → switch to Kendall's τ for that cell

### NFR-5: Logging
- Log message format: `"Permutation test: ρ={rho:.3f}, p={pvalue:.4f} [{encoder}/{benchmark}/{model_size}]"`
- One line per cell, clearly marking significance

---

## 7. Dependencies

### 7.1 Python Packages

```
scipy>=1.7.0
numpy>=1.21
matplotlib>=3.4
seaborn>=0.11
pandas>=1.3
```

### 7.2 Pipeline Dependencies

| Upstream | Required Output | Status |
|----------|-----------------|--------|
| H-E1 | similarity_matrix_codebert.npy, similarity_matrix_minilm.npy | VALIDATED ✅ |
| H-E2 | pass_at_1_1b.json | VALIDATED ✅ |
| H-C1 | pass_at_1_7b.json | Optional (pending) |

### 7.3 Compute Requirements

- CPU-only: all computation is numpy/scipy matrix ops and statistical tests
- Memory: <1 GB (n=4 matrices are trivially small)
- Storage: <50 MB (results + figures)

---

## 8. Success Criteria

| Criterion | Condition |
|-----------|-----------|
| Code runs without error | All FRs execute to completion |
| Gate evaluated | SATISFIED, FALSIFIED, or CANNOT_TEST determined |
| Results saved | correlation_results.json, gate_evaluation.json exist |
| Figures generated | 5 figures in h-m2/figures/ |
| Logging complete | Per-cell log messages for all 4-8 cells |

**Minimal success scenario:** MiniLM cells C3 or C4 show p≈0.042 (perfect rank concordance) — gate satisfied even if CodeBERT cells are non-significant.

---

## 9. Implementation Notes

- **No training loop:** Entire implementation is ~80 lines of Python (load → compute → save → plot)
- **Green-field:** No base hypothesis code to reuse — H-M2 is a new statistical analysis script
- **Key scipy note:** For n=4, `permutation_type='pairings'` computes all 4!=24 distinct pairings when `n_resamples` ≥ 24. Use `n_resamples=10000` to match protocol specification.
- **Critical risk:** CodeBERT similarity range (0.909–0.980) may be too compressed for meaningful Spearman discrimination. MiniLM (0.247–0.311) provides much better rank separation. Both encoders must agree in direction, but significance from MiniLM alone is sufficient for gate.
