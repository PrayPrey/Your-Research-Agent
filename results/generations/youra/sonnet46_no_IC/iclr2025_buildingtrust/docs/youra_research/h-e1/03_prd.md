# Product Requirements Document: H-E1
## Partial Spearman Correlation Structure in LLM Trustworthiness Dimensions

**Hypothesis:** H-E1  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-08-04  
**Phase:** 3 — Implementation Planning  
**Gate:** MUST_WORK — ≥1 of 15 |ρ_partial| > 0.5, p < 0.0033 (Bonferroni-corrected)

---

## 1. Executive Summary

H-E1 tests whether LLM trustworthiness dimensions are statistically dependent after controlling for model scale and RLHF status. Using the TrustLLM 16-model × 6-dimension evaluation dataset, we compute partial Spearman rank correlations for all 15 dimension pairs controlling for log(param_count) and RLHF status (binary). The experiment succeeds if at least one partial correlation is statistically significant (|ρ_partial| > 0.5, p < 0.0033 Bonferroni-corrected for 15 tests).

**This is a statistical analysis experiment — no model training required.**

---

## 2. Problem Statement

LLM evaluation frameworks (TrustLLM, HELM) measure trustworthiness across multiple dimensions independently. It is unknown whether these dimensions are structurally correlated after removing confounds (model size, RLHF training). If significant partial correlations exist, it implies that evaluation frameworks are measuring overlapping constructs, which has implications for efficient evaluation set design (fewer dimensions can capture equivalent information).

**Baseline approach:** Raw Spearman correlation conflates scale confound — larger models score higher on all dimensions, inflating apparent correlations.

**Proposed approach:** OLS residualization removes scale (log10_params) and RLHF (binary) effects before computing Spearman on residuals, isolating genuine dimension co-movement.

---

## 3. Functional Requirements

### FR-1: Data Loading and Assembly
- Clone HowieHwong/TrustLLM GitHub repository
- Parse `results/*.json` files to extract per-model per-dimension aggregate scores
- Assemble 16×6 DataFrame (rows=models, cols=6 trustworthiness dimensions)
- Add model annotation columns: `log10_params`, `is_RLHF` (see annotation table in Section 4)
- Validate: no missing values, score ranges [0,1], VIF check for covariates

### FR-2: Baseline Correlation (Raw Spearman)
- Compute all 15 pairwise Spearman ρ values on raw 16×6 score matrix
- Store 6×6 ρ_raw matrix and p-value matrix
- No significance filtering applied — display full matrix

### FR-3: Partial Spearman Correlation (Primary Analysis)
- For each of 15 dimension pairs:
  - OLS-residualize both dimensions on covariates [log10_params, is_RLHF]
  - Compute Spearman ρ on residuals
  - Compute t-statistic with df = n - 2 - k = 12 (n=16, k=2 covariates)
  - Compute two-sided p-value from t-distribution
- Apply Bonferroni correction: α_corrected = 0.05 / 15 = 0.0033
- Output: 6×6 ρ_partial matrix, p-value matrix, list of significant pairs
- **Gate condition:** ≥1 pair with |ρ_partial| > 0.5 AND p < 0.0033

### FR-4: Hierarchical Clustering (Secondary Analysis)
- Compute distance matrix: D = 1 - |ρ_partial|, set diagonal to 0
- Apply average-linkage hierarchical clustering (k=2) with precomputed distance
- Compute silhouette score for k=2 solution
- Success criterion: silhouette > 0.3

### FR-5: Sensitivity Check
- Compute partial Pearson correlation matrix (for comparison)
- Flag if Spearman and Pearson partial correlations diverge in sign for any pair
- Report VIF for [log10_params, is_RLHF] covariates (flag if VIF > 5)

### FR-6: Visualization
- **Required:** Bar chart of |ρ_partial| for all 15 pairs, Bonferroni threshold line at 0.5
- **Additional:** Side-by-side heatmaps (raw vs partial correlation matrices)
- **Additional:** Dendrogram from hierarchical clustering
- **Additional:** Scatter plot of top correlated pair (before/after residualization, colored by RLHF)
- Output location: `h-e1/figures/`

### FR-7: Results Serialization
- Save all numeric results to JSON: ρ_raw matrix, ρ_partial matrix, p-values, significant pairs, silhouette score, cluster labels
- Save to `h-e1/experiment_results_phase3.json`

---

## 4. Data Specification

### Primary Dataset
**Name:** TrustLLM Published Score Tables  
**Source:** https://github.com/HowieHwong/TrustLLM (results/ folder)  
**Version:** v0.3.0 (ICML 2024, Sun et al., 2024)  
**Format:** JSON files per dimension per model  
**Size:** N=16 models × 6 dimensions (full evaluation set — no subsampling)

**6 Dimensions:**
1. truthfulness
2. safety
3. fairness
4. robustness
5. privacy
6. machine_ethics

**Model Annotation Table:**
| Model | log10_params | is_RLHF |
|-------|-------------|---------|
| LLaMA-2-7b-base | 9.845 | 0 |
| LLaMA-2-7b-chat | 9.845 | 1 |
| LLaMA-2-13b-base | 10.114 | 0 |
| LLaMA-2-13b-chat | 10.114 | 1 |
| LLaMA-2-70b-base | 10.845 | 0 |
| LLaMA-2-70b-chat | 10.845 | 1 |
| Mistral-7b | 9.845 | 0 |
| Falcon-7b | 9.845 | 0 |
| Vicuna-7b | 9.845 | 1 |
| Vicuna-13b | 10.114 | 1 |
| Vicuna-33b | 10.519 | 1 |
| GPT-3.5-turbo | 11.176 | 1 |
| GPT-4 | 11.903 | 1 |
| Claude-2 | 11.699 | 1 |
| ChatGLM2 | 9.845 | 1 |
| Koala-13b | 10.114 | 1 |

**Preprocessing Steps:**
1. Clone HowieHwong/TrustLLM: `git clone https://github.com/HowieHwong/TrustLLM.git`
2. Navigate to `results/` directory; identify per-model JSON files
3. For each model, extract per-dimension aggregate scalar score (float [0,1])
4. Build 16×6 pandas DataFrame (rows=models, cols=dimensions)
5. Add log10_params and is_RLHF columns per annotation table
6. Check for missing values (impute with dimension mean if <3 missing; error if ≥3)
7. Check floor/ceiling effects: if any dimension >20% at 0 or 1, report both Spearman and Pearson

**Manual Download Required:** Yes — GitHub clone

### No Training Data / No Validation Split
This experiment uses the full 16-model evaluation set (no train/val/test split). All 16 models used for correlation analysis.

---

## 5. Baseline Models

### Baseline: Raw Spearman Correlation
- **Description:** Standard pairwise Spearman ρ on 16×6 score matrix, no confound control
- **Purpose:** Show that naive correlation inflates apparent structure due to scale confound
- **Implementation:** `scipy.stats.spearmanr` on all 15 pairs
- **Expected behavior:** Mostly positive correlations due to scale effect (larger models score higher everywhere)

---

## 6. Proposed Model / Method

### Partial Spearman Correlation via OLS Residualization
- **Core Algorithm:** OLS-residualize each dimension on [log10_params, is_RLHF], then compute Spearman ρ on residuals
- **Significance Testing:** t-distribution with df = n - 2 - k = 12
- **Multiple Testing Correction:** Bonferroni α = 0.0033 (0.05/15)
- **Gate Threshold:** |ρ_partial| > 0.5

---

## 7. Non-Functional Requirements

### NFR-1: Compute
- CPU-only, runtime < 1 minute
- No GPU required

### NFR-2: Reproducibility
- Deterministic (no random seeds needed — pure statistical analysis)
- Results fully reproducible given same TrustLLM dataset version

### NFR-3: Outputs
- All figures saved to PNG at 300 DPI
- All numeric results serialized to JSON
- Summary printed to console and `h-e1/experiment.log`

---

## 8. Success Criteria

| Criterion | Threshold | Type |
|-----------|-----------|------|
| PoC Gate | ≥1 pair: |ρ_partial|>0.5 AND p<0.0033 | MUST_WORK |
| Silhouette (k=2) | >0.3 | Secondary |
| Code runs without error | True | Required |
| All 15 pairs computed | count=15 | Required |

---

## 9. Dependencies

### Python Packages
```
numpy>=1.24
pandas>=1.5
scipy>=1.10
scikit-learn>=1.2
networkx>=3.0
statsmodels>=0.14
matplotlib>=3.7
seaborn>=0.12
pingouin>=0.5  # optional: cross-validation of partial correlation
```

### External Repositories
- HowieHwong/TrustLLM (primary data source)

### Internal Dependencies
- None (H-E1 is the foundation hypothesis)

---

## 10. Out of Scope

- Model training or fine-tuning
- HELM dataset analysis (Phase H-M3)
- Pythia scaling series analysis (Phase H-M2)
- Bootstrap stability analysis (Phase H-E2)
- Any dataset larger than the 16-model TrustLLM set

---

*Generated by Phase 3 Implementation Planning (UNATTENDED mode)*  
*Source: h-e1/02c_experiment_brief.md*
