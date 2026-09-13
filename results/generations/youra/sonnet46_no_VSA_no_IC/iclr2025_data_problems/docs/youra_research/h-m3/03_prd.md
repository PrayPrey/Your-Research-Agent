---
stepsCompleted:
  - executive-summary
  - problem-statement
  - functional-requirements
  - non-functional-requirements
  - data-specification
  - success-criteria
  - dependencies
hypothesis_id: H-M3
hypothesis_type: MECHANISM
date: 2026-08-20
author: yoon303b@gmail.com
---

# Product Requirements Document: H-M3
## Panel OLS Regression — Domain Coefficient Benchmark-Specificity

---

## 1. Executive Summary

This experiment tests whether panel OLS regression over the full Pythia training trajectory (2,464 observations: 16 model sizes × 154 checkpoints) reveals benchmark-specific domain coefficients. Specifically, β_Wikipedia > β_Books for MMLU (P1) and β_Books > β_Wikipedia for HellaSwag (P2), with Likelihood Ratio Test (LRT) rejecting a shared-β null model for ≥2 of 6 pairwise benchmark comparisons after FDR correction (P3).

**Key Deliverable:** A panel econometrics pipeline using linearmodels `PanelOLS` with model-size fixed effects and clustered standard errors, fitting 4 benchmark-specific regressions and running LRT against a shared-β pooled model. This is the primary quantitative test of domain-exposure → benchmark-specificity causality in the YOURA hypothesis chain.

**Improvements over H-M2:** Uses the full 16-model × 154-checkpoint panel (2,464 obs) vs H-M2's 3-model subsampled Spearman approach. Entity fixed effects remove model-scale confounds. Clustered SEs handle temporal autocorrelation. LRT provides formal model comparison.

---

## 2. Problem Statement

### 2.1 Background

H-E1 confirmed measurable domain exposure trajectories across 154 Pythia checkpoints. H-M1 confirmed Wikipedia has higher entity density than Books3 (p < 0.05). H-M2 attempted Spearman correlation over 3 model sizes but failed: Books3 zero-variance in the 600k-doc subsample made P2 untestable, and P1 showed directional reversal for 70M (N=10 checkpoints). H-M3 uses the full H-E1 panel output and panel OLS to provide a statistically robust test.

### 2.2 Problem

H-M2's failure was structural: sampling 600k docs was insufficient to capture Books3 cumulative exposure variation. H-M3 addresses this by using all 154 checkpoints × all 16 model sizes, constructing a balanced panel with model-size fixed effects that remove between-entity scale confounds. The research question remains: do domain exposure fractions have benchmark-specific effects after controlling for model scale?

### 2.3 Proposed Solution

Construct a MultiIndex panel DataFrame (model_size, checkpoint) with 2,464 rows. Fit 4 PanelOLS regressions (one per benchmark: MMLU, HellaSwag, ARC-Challenge, WinoGrande) with EntityEffects and clustered SEs by model size. Fit one shared-β pooled model. Run LRT comparing pooled vs benchmark-specific models for all 6 pairwise benchmark pairs. Apply FDR correction (Benjamini-Hochberg). Test P1 and P2 via one-tailed coefficient comparison.

---

## 3. Functional Requirements

### FR-1: Domain Exposure Data Loading (Full H-E1 Panel)

**Description:** Load full H-E1 output covering all 16 model sizes × 154 checkpoints.

**Requirements:**
- FR-1.1: Load `cumulative_domain_fraction[model_i][domain][checkpoint_t]` from H-E1 output — shape per model: (154, 22)
- FR-1.2: Verify coverage: ALL 16 model sizes (70M, 160M, 410M, 1B, 1.4B, 2.8B, 6.9B, 12B + 8 deduped variants); 154 checkpoints; 22 Pile domains
- FR-1.3: Align checkpoint step indices between H-E1 output and lm-eval-harness results (steps: 0,1,2,4,8,16,32,64,128,256,512,1000–143000)
- FR-1.4: Verify domain names match Pile taxonomy (22 domains including "Wikipedia (en)", "Books3", "Github")
- FR-1.5: If any model_size coverage < 100 checkpoints → raise warning but continue with available data
- FR-1.6: CRITICAL: Do NOT use the 600k-doc subsample from H-M2 — load full H-E1 output

### FR-2: Benchmark Evaluation (All 16 Models × 154 Checkpoints)

**Description:** Evaluate MMLU, HellaSwag, ARC-Challenge, WinoGrande for all 154 checkpoints × 16 model sizes.

**Requirements:**
- FR-2.1: Evaluate all 16 Pythia model sizes at all 154 checkpoint revisions (`revision=step{N}`)
- FR-2.2: MMLU: 5-shot, all 57 subjects, `cais/mmlu`; extract `acc,none` averaged across subjects
- FR-2.3: HellaSwag: 10-shot, normalization scoring, `Rowan/hellaswag`; extract `acc_norm,none`
- FR-2.4: ARC-Challenge: 25-shot, normalization scoring, `ai2_arc`; extract `acc_norm,none`
- FR-2.5: WinoGrande: 5-shot, `winogrande`; extract `acc,none`
- FR-2.6: Check existing evals cache at `EleutherAI/pythia` repo `evals/pythia-v1/` BEFORE running new evaluations
- FR-2.7: Use lm-evaluation-harness CLI/Python API (`lm_eval.simple_evaluate`) for missing checkpoints
- FR-2.8: Batch size: `auto`; dtype: `float` (fp32 for reproducibility)
- FR-2.9: Save results to `results/h-m3/eval_cache/{model_size}/step{N}.json`
- FR-2.10: Resume capability: skip checkpoint if cache file exists and is valid JSON
- FR-2.11: Total evaluations (new): up to 2,464 (16 × 154); use existing cache aggressively

### FR-3: Panel Construction and Preprocessing

**Description:** Construct MultiIndex panel DataFrame and apply preprocessing.

**Requirements:**
- FR-3.1: Construct `pd.DataFrame` with MultiIndex `(model_size, checkpoint)` — 2,464 rows
- FR-3.2: Columns: 22 domain exposure fractions + 4 benchmark scores + `log_params` covariate
- FR-3.3: Floor filtering: exclude checkpoints where ALL benchmark scores < 30% (per model size)
- FR-3.4: Verify ≥ 100 usable checkpoints per model size after floor filtering; raise error if any model fails
- FR-3.5: Apply 13-gram decontamination audit on MMLU and HellaSwag; report contamination rate; apply adjusted scores if delta > 3pp
- FR-3.6: Drop one domain column (least informative, min variance) to break sum-to-1 constraint — 21 covariates remain
- FR-3.7: VIF check: compute VIF for all 21 domain columns; if any VIF > 10 apply PCA (95% variance retained); document which domains become PCA components

### FR-4: VIF Diagnostics

**Description:** Detect and handle multicollinearity from sum-constrained domain fractions.

**Requirements:**
- FR-4.1: Compute VIF using `statsmodels.stats.outliers_influence.variance_inflation_factor` for all 21 domain columns (after dropping 1)
- FR-4.2: If max VIF ≤ 10: proceed with original domain columns; log "VIF check passed"
- FR-4.3: If max VIF > 10: apply `sklearn.decomposition.PCA(n_components=0.95)` to domain columns; use PCA components as regressors; log "PCA applied: {n_components} components retained"
- FR-4.4: If PCA applied: note that Wikipedia/Books3 direct interpretation is lost; P1/P2 tested on PCA loadings instead; document as limitation
- FR-4.5: Save VIF table to `results/h-m3/vif_diagnostics.json`

### FR-5: Panel OLS Regression — Benchmark-Specific Models (H1)

**Description:** Fit 4 separate PanelOLS regressions, one per benchmark.

**Requirements:**
- FR-5.1: For each benchmark b ∈ {MMLU, HellaSwag, ARC-Challenge, WinoGrande}: fit `PanelOLS.from_formula(f"{b} ~ {domain_terms} + EntityEffects", panel_df)`
- FR-5.2: Use `cov_type='clustered', cluster_entity=True` for all fits (handles within-model temporal autocorrelation; N=16 entities, T=154 time periods)
- FR-5.3: Extract: `params` (β coefficients), `std_errors`, `pvalues`, `rsquared_within`, `rsquared_between`
- FR-5.4: Verify: at least one domain |β| > 1 SE (non-trivial effect); log "PanelOLS fit complete for benchmark {b}: N={N}, T={T}, R²_within={r2:.4f}"
- FR-5.5: Verify clustered SEs are finite and non-zero for Wikipedia and Books3 coefficients (or PCA equivalent)
- FR-5.6: Save per-benchmark results to `results/h-m3/panel_results_{benchmark}.json`

### FR-6: Panel OLS Regression — Shared-β Null Model (H0)

**Description:** Fit pooled model with shared domain coefficients across benchmarks.

**Requirements:**
- FR-6.1: Stack all 4 benchmarks into long format: 4 × 2,464 = 9,856 obs
- FR-6.2: Add benchmark dummy interactions; fit `PanelOLS` with `EntityEffects` on stacked panel
- FR-6.3: Alternative approach if linearmodels stacking is awkward: use `statsmodels.OLS` with benchmark dummies and model-size dummies (explicit); compare via LRT
- FR-6.4: Extract log-likelihood for LRT comparison
- FR-6.5: Save shared-β model to `results/h-m3/panel_results_shared_beta.json`

### FR-7: P1 and P2 Directional Tests

**Description:** Test hypothesis-specific directional comparisons.

**Requirements:**
- FR-7.1: P1: extract `β_Wikipedia` and `β_Books3` (or PCA equivalents) from MMLU model; test β_Wikipedia > β_Books3 (one-tailed)
- FR-7.2: P2: extract same coefficients from HellaSwag model; test β_Books3 > β_Wikipedia (one-tailed)
- FR-7.3: For one-tailed test: use Fisher z-test on coefficient difference normalized by pooled clustered SE
- FR-7.4: p-value threshold: p < 0.05 (one-tailed) for SHOULD_WORK gate
- FR-7.5: Record: `p1_direction` (bool), `p1_pvalue`, `p2_direction` (bool), `p2_pvalue`
- FR-7.6: If VIF triggered PCA: map Wikipedia and Books3 to their dominant PCA component loadings; note approximation in results

### FR-8: LRT — Shared-β vs Benchmark-Specific-β (P3)

**Description:** Formal likelihood ratio test for model comparison.

**Requirements:**
- FR-8.1: Run LRT for all 6 pairwise benchmark pairs: {MMLU, HellaSwag, ARC-C, WinoGrande} choose 2 = 6 pairs
- FR-8.2: For each pair (b1, b2): test whether shared β(b1,b2) fits significantly worse than benchmark-specific β_b1, β_b2
- FR-8.3: Use `statsmodels OLSResults.compare_lr_test` or chi-squared test: `lr_stat = 2*(LL_b1 + LL_b2 - LL_shared)`, df = n_domains
- FR-8.4: Apply Benjamini-Hochberg FDR correction to 6 LRT p-values (`statsmodels.stats.multitest.multipletests(method='fdr_bh')`)
- FR-8.5: P3 gate: `n_significant_pairs = sum(reject)` — pass if ≥ 2
- FR-8.6: Save all LRT results + FDR-corrected p-values to `results/h-m3/lrt_results.json`

### FR-9: Robustness Analysis

**Description:** Subgroup and permutation null robustness checks.

**Requirements:**
- FR-9.1: Within-scale subgroup regression: separate fits for small models (70M–410M) vs large models (1B–12B); compare β_Wikipedia and β_Books3 across groups
- FR-9.2: Spearman ρ of domain coefficient rankings: small vs large subgroups; P4 gate: ρ > 0.7
- FR-9.3: Permutation null (1000 shuffles): randomly permute domain labels; refit models; build null distribution of |β_Wikipedia − β_Books3| for P1 and P2; report empirical p-value
- FR-9.4: Fixed numpy seed = 42 for permutation reproducibility
- FR-9.5: R² decomposition: fit domain-only model, scale-only model (log_params only), and full model; compute R²_within for each; report variance explained by domain vs scale
- FR-9.6: Save robustness results to `results/h-m3/robustness_results.json`

### FR-10: Panel Quality Verification

**Description:** Verify panel has sufficient within-entity variation for entity-demeaned estimation.

**Requirements:**
- FR-10.1: For each domain, compute within-model-size variance after entity demeaning: `var(exposure_d - mean_model_i(exposure_d))`
- FR-10.2: Log domains with low within-variation (< 1e-6); raise warning if Wikipedia or Books3 are in this list
- FR-10.3: Verify Books3 is NOT zero-variance (H-M2 root cause): if Books3 within-variance < 1e-6 across all models, raise error "Books3 within-variation insufficient — check H-E1 full output loading"
- FR-10.4: Log `verify_panel_quality()` output for all 21 domains

### FR-11: Visualization

**Description:** Generate required and optional figures.

**Requirements:**
- FR-11.1 (MANDATORY): Bar chart of β_Wikipedia and β_Books3 per benchmark (4 benchmarks) with 95% CI error bars — save to `docs/youra_research/h-m3/figures/fig1_gate_metrics_comparison.png`
- FR-11.2: Domain coefficient heatmap: 22 domains × 4 benchmarks, color = β magnitude — `figures/fig2_domain_coefficient_heatmap.png`
- FR-11.3: P1/P2 directional scatter: β_Wikipedia vs β_Books3 per benchmark with diagonal line — `figures/fig3_directional_scatter.png`
- FR-11.4: R² decomposition bar chart: domain-only, scale-only, full model R²_within per benchmark — `figures/fig4_r2_decomposition.png`
- FR-11.5: Permutation null distribution: histogram of permuted |β_Wikipedia − β_Books3| vs observed (P1 and P2) — `figures/fig5_permutation_null.png`
- FR-11.6: Within-scale subgroup robustness: β_Wikipedia and β_Books3 for small vs large model subgroups — `figures/fig6_subgroup_robustness.png`
- FR-11.7: All figures: 300 DPI, colorblind-safe palette

### FR-12: Results Reporting

**Description:** Generate structured results output.

**Requirements:**
- FR-12.1: Save full panel regression summary to `results/h-m3/panel_summary.json`
- FR-12.2: Save gate evaluation to `results/h-m3/gate_summary.json` (P1, P2, P3, P4 with pass/fail)
- FR-12.3: Save final results summary to `docs/youra_research/h-m3/04_results_summary.md`
- FR-12.4: All intermediate results cached for reproducibility

---

## 4. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed numpy seed = 42 for permutation null
- Deterministic panel construction from H-E1 output
- All checkpoint evaluations cached; results versioned

### NFR-2: Performance
- Benchmark evaluation (most expensive step): check existing eval cache first; estimated GPU time 48–120h (5×H100 NVL) if starting from scratch
- Panel regression (fast): < 5 min total for 4 PanelOLS fits
- Permutation null (1000 shuffles): < 2h on CPU
- Resume capability for checkpoint evaluation

### NFR-3: Fault Tolerance
- If Books3 within-variance ≈ 0 after loading full H-E1: raise explicit error (do not silently proceed)
- If any model_size has < 100 usable checkpoints: warn and continue with remaining models
- If PCA triggered: document clearly; note P1/P2 interpret via PCA loadings not raw domain coefficients
- All intermediate results saved; pipeline resumable from any step

### NFR-4: Modularity
- Separate modules: `data_loader.py`, `panel_builder.py`, `panel_regression.py`, `lrt_analysis.py`, `robustness.py`, `visualization.py`, `reporter.py`
- Each module independently testable

### NFR-5: Logging
- Log panel construction: N_obs, N_entities, T_per_entity
- Log VIF diagnostics: max VIF, PCA trigger decision
- Log each PanelOLS fit: benchmark, N, T, R²_within
- Log Books3 within-variance (critical check from H-M2 failure)
- Python `logging` module at INFO level

---

## 5. Data Specification

### 5.1 Input Data

| Dataset | Source | Access Method | Notes |
|---------|--------|---------------|-------|
| Domain exposure fractions | H-E1 full output | Local file load | Shape: (154, 22) per model × 16 models |
| Pythia checkpoints | HuggingFace Hub | `revision=step{N}` | All 16 model sizes |
| Existing eval cache | EleutherAI/pythia repo | `evals/pythia-v1/` | Check first — may cover many checkpoints |
| MMLU test set | `cais/mmlu` (HF) | lm-eval auto | 14,042 questions, 57 subjects |
| HellaSwag validation | `Rowan/hellaswag` (HF) | lm-eval auto | 10,042 examples |
| ARC-Challenge | `ai2_arc` (HF) | lm-eval auto | Standard split |
| WinoGrande | `winogrande` (HF) | lm-eval auto | Standard split |
| Pile dataloader indices | `EleutherAI/pythia_deduped_pile_idxmaps` | numpy memmap | For decontamination |

### 5.2 Output Data

| Output | Path | Format | Size Estimate |
|--------|------|--------|---------------|
| Eval cache | `results/h-m3/eval_cache/` | JSON per checkpoint | ~2,464 files × 50KB = ~120MB |
| VIF diagnostics | `results/h-m3/vif_diagnostics.json` | JSON | ~10KB |
| Panel results (per benchmark) | `results/h-m3/panel_results_{b}.json` | JSON | ~4 × 50KB |
| Shared-β model | `results/h-m3/panel_results_shared_beta.json` | JSON | ~50KB |
| LRT results | `results/h-m3/lrt_results.json` | JSON | ~20KB |
| Robustness results | `results/h-m3/robustness_results.json` | JSON | ~50KB |
| Gate summary | `results/h-m3/gate_summary.json` | JSON | ~5KB |
| Figures | `docs/youra_research/h-m3/figures/` | PNG 300 DPI | ~6 files |
| Results summary | `docs/youra_research/h-m3/04_results_summary.md` | Markdown | ~5KB |

### 5.3 Data Dependencies

- **H-E1 full output (REQUIRED):** `cumulative_domain_fraction` for all 16 model sizes × 154 checkpoints — NOT the 600k-doc subsample
- **H-M1 context (informational):** Domain taxonomy confirming Wikipedia/Books3 as focal domains
- **H-M2 context:** Established Books3 zero-variance as root failure cause; H-M3 must verify Books3 has adequate within-variation

---

## 6. Success Criteria

### Primary Gate (SHOULD_WORK)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| P1 | β_Wikipedia > β_Books3 for MMLU (one-tailed) | p < 0.05 one-tailed |
| P2 | β_Books3 > β_Wikipedia for HellaSwag (one-tailed) | p < 0.05 one-tailed |
| P3 | LRT rejects shared-β model | FDR q < 0.05 for ≥2 of 6 pairwise comparisons |
| Books3 variance check | Books3 within-variation > 0 | within_var(Books3) > 1e-6 |
| Panel adequacy | ≥100 usable checkpoints per model size | n_valid ≥ 100 for all 16 sizes |

### Secondary Criteria

| Criterion | Target | Notes |
|-----------|--------|-------|
| P4 | Spearman ρ(small vs large group coefficients) > 0.7 | Scale robustness |
| R²_within (full model) | > 0.1 for at least 1 benchmark | Non-trivial domain predictive power |
| Permutation p-value (P1) | < 0.05 empirical | Null distribution confirmation |
| Decontamination delta | < 3pp shift | If > 3pp, use adjusted scores |

### Failure Routes

- **MINIMUM PASS (P1 OR P2 confirmed):** EXPLORE route — refine scope to confirmed benchmark pair
- **P1/P2 fail, P3 passes:** EXPLORE — some benchmark pairs differentiate; refine scope
- **All tests fail:** PIVOT — test without temporal autocorrelation correction; if still null, publishable null finding; route to Phase 0
- **VIF > 10 after PCA:** Document PCA substitution as limitation; interpret PCA loadings

---

## 7. Dependencies

### 7.1 Python Packages

```
# Panel regression (primary)
linearmodels>=4.0         # PanelOLS with EntityEffects, clustered SEs

# Standard statistical tools
statsmodels>=0.13         # variance_inflation_factor, OLSResults.compare_lr_test, multipletests
scipy>=1.7                # stats.t, Fisher z-test
numpy>=1.20               # array operations, seed=42 for permutation

# Data processing
pandas>=1.5               # MultiIndex DataFrame construction
sklearn>=1.0              # PCA fallback (sklearn.decomposition.PCA)

# Benchmark evaluation
lm_eval>=0.4.0            # lm-evaluation-harness
torch>=2.0                # PyTorch (GPU required for 6.9B–12B)
transformers>=4.35        # HuggingFace model loading
datasets>=2.14            # HuggingFace datasets
huggingface_hub>=0.17     # Checkpoint revision access

# Visualization
matplotlib>=3.7
seaborn>=0.12

# Decontamination
nltk>=3.8                 # 13-gram tokenization

# Utilities
tqdm>=4.65
pyyaml>=6.0
```

### 7.2 External Repositories

| Repository | URL | Usage |
|-----------|-----|-------|
| bashtage/linearmodels | https://github.com/bashtage/linearmodels | Primary panel regression library |
| EleutherAI/lm-evaluation-harness | https://github.com/EleutherAI/lm-evaluation-harness | Benchmark evaluation framework |
| EleutherAI/pythia | https://github.com/EleutherAI/pythia | Checkpoint access, existing eval cache at `evals/` |
| EleutherAI/pythia_deduped_pile_idxmaps | HuggingFace | Pile dataloader indices (decontamination) |

### 7.3 Previous Hypothesis Outputs

| Hypothesis | Output Required | Path | Notes |
|-----------|-----------------|------|-------|
| H-E1 | Full domain exposure fractions (154×22×16 array) | `docs/youra_research/h-e1/` | FULL output, not subsample |
| H-M1 | Focal domain confirmation (Wikipedia, Books3) | Informational | Theoretical grounding for P1/P2 |
| H-M2 | Root cause: Books3 zero-variance in subsample | `docs/youra_research/h-m2/04_validation.md` | Lesson: load full H-E1 |

### 7.4 Hardware Requirements

- GPU: ≥16GB VRAM for Pythia-6.9B and 12B evaluation; 8GB for ≤2.8B
- Disk: ≥150GB for checkpoint cache + eval results (16 models)
- CPU: Multi-core (panel regression and robustness analysis are CPU-only)
- Network: HuggingFace Hub access for missing checkpoint evaluations
