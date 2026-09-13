# Phase 2B: Verification Plan

**Generated:** 2026-07-09  
**Main Hypothesis:** H-BenchmarkVarianceStability-v1  
**Pipeline Project ID:** 86a566c9-634f-45ad-be94-b962450e1c89

---

## Main Hypothesis

**Title:** Benchmark Score Variance Predicts Cross-Benchmark Stability

**Statement:** Under trust benchmark evaluation with multi-model leaderboards (TrustLLM, HaluBench, TruthfulQA, FinTrust, MultiTrust, n≥10 models each), if benchmark coefficient of variation (CV = σ/μ across model scores) is computed and compared with mean cross-benchmark ranking agreement (Spearman ρ), then CV correlates negatively with ρ (Pearson r < -0.5, p < 0.05), because high score variance indicates inconsistent model differentiation, reducing benchmark reliability as a stable ranking instrument.

**Phase 2A Source:** `03_refinement.yaml` (converged after 7 exchanges, all 6 criteria met)

---

## Sub-Hypotheses

### H-E1: CV-Stability Correlation Exists (MUST_WORK)

**Type:** EXISTENCE  
**Statement:** Pearson correlation between benchmark CV and mean cross-benchmark Spearman ρ is negative and moderate-to-strong (r < -0.5) with statistical significance (p < 0.05) across 5-10 trust benchmarks.

**Gate:** MUST_WORK (foundation hypothesis - if this fails, the entire approach is invalid)

**Test Method:**
1. Extract model scores from published leaderboards (TrustLLM Table 4-5, HaluBench supplement, TruthfulQA GitHub, FinTrust paper, MultiTrust sources)
2. For each benchmark: Compute CV = σ/μ where σ = std(scores), μ = mean(scores)
3. For each benchmark pair with ≥5 shared models: Compute Spearman ρ on shared model rankings
4. For each benchmark: Average pairwise ρ values to get mean_ρ
5. Run Pearson correlation test: `r, p = scipy.stats.pearsonr(CV_values, mean_ρ_values)`

**Success Criterion:**
- r < -0.5 (negative moderate-to-strong correlation)
- p < 0.05 (statistical significance)
- Statistical power: 70-90% at n=5-10 for r=-0.5 to -0.7

**Falsification:** If r ≥ -0.5 OR p ≥ 0.05, variance does not predict stability; H₀ is retained.

**Prerequisites:** None (can start immediately)

**Archon Task ID:** d336d4f3-c0ea-456e-8f67-9381d1b83a51

---

### H-M1: High Variance Indicates Measurement Noise (SHOULD_WORK)

**Type:** MECHANISM  
**Statement:** High-CV benchmarks exhibit heterogeneous task difficulty, unstable capability measurement, or small effective sample size, indicating noise-sensitive measurement.

**Gate:** SHOULD_WORK (mechanism validation - failure doesn't invalidate the correlation)

**Test Method:**
1. For high-CV benchmarks (top tertile): Analyze item-level variance if available
2. Compute task difficulty distributions (percent of models getting each item correct)
3. Test for heterogeneity: SD of item difficulty > threshold (e.g., 0.3)
4. Compare high-CV vs low-CV benchmarks on heterogeneity metrics

**Success Criterion:**
- High-CV benchmarks show significantly higher task heterogeneity (Cohen's d > 0.5)
- Item difficulty distribution is bimodal or highly dispersed (SD > 0.3)

**Falsification:** If high-CV benchmarks have uniform task difficulty and large item pools, this mechanism fails.

**Prerequisites:** H-E1 (no point analyzing mechanism if correlation doesn't exist)

**Archon Task ID:** 59d819a8-f6f0-4fd8-a07b-9133c967ea52

---

### H-M2: Noise-Driven Rankings Fail to Replicate (SHOULD_WORK)

**Type:** MECHANISM  
**Statement:** Noise-sensitive benchmarks (high CV) produce rankings that depend on which noise-amplifying items dominate evaluation, failing to replicate across benchmarks sampling different item/context distributions.

**Gate:** SHOULD_WORK (causal chain validation - failure doesn't invalidate correlation)

**Test Method:**
1. For each benchmark: Compute within-benchmark ranking stability (split-half reliability if data available, or bootstrapped sampling)
2. Test whether high-CV benchmarks have lower within-benchmark stability than low-CV benchmarks
3. Verify causal chain: high CV → low within-benchmark stability → low cross-benchmark ρ

**Success Criterion:**
- High-CV benchmarks show lower split-half reliability (r < 0.7) than low-CV benchmarks (r > 0.8)
- Mediation analysis confirms: CV → within-stability → cross-benchmark ρ path is significant

**Falsification:** If high-CV benchmarks show stable rankings across item subsets (ρ > 0.7), variance doesn't predict instability.

**Prerequisites:** H-E1

**Archon Task ID:** b1e13569-6031-4850-a887-3ce7fd4276b8

---

### H-C1: Effect Persists After Controlling Confounds (SHOULD_WORK)

**Type:** CONDITION  
**Statement:** The CV-stability correlation holds after controlling for benchmark age (years since publication), n-models threshold (≥10), and model overlap (≥5 shared models).

**Gate:** SHOULD_WORK (robustness check - failure suggests confound issues but doesn't invalidate primary finding)

**Test Method:**
1. Collect confound variables: benchmark age (2020-2025), n-models per benchmark, mean model overlap across pairs
2. Run partial correlation: `partial_r = partial_corr(CV, mean_ρ, control=[age, n_models, overlap])`
3. Compare partial_r with zero-order r to assess confound impact
4. Alternative: Multiple regression with CV, age, n_models, overlap as predictors of mean_ρ

**Success Criterion:**
- Partial correlation r_partial < -0.4 (allowing slight weakening from confound control)
- CV remains significant predictor (p < 0.05) in regression model

**Falsification:** If partial correlation r_partial ≥ -0.3 or loses significance, the relationship is confound-driven.

**Prerequisites:** H-E1

**Archon Task ID:** a3d85cff-5d34-4d3f-b212-44d370f5b347

---

## Dependency Graph (DAG)

```
H-E1 (MUST_WORK)
  ├── H-M1 (SHOULD_WORK)
  ├── H-M2 (SHOULD_WORK)
  └── H-C1 (SHOULD_WORK)
```

**Execution Order:**
1. **Phase 1:** H-E1 (foundation) - 1-2 weeks
2. **Phase 2:** H-M1, H-M2, H-C1 in parallel - 1 week each

**Critical Path:** H-E1 → Phase 5 baseline comparison

---

## Risk Analysis

### H-E1 Risks
- **Medium Risk:** Small sample size (n=5-10 benchmarks) limits statistical power to 70-90%
- **Mitigation:** Power analysis confirmed feasibility; use continuous variables (not group comparison) for higher power
- **Impact if FAIL:** MUST_WORK gate fails → Pipeline routes to Phase 0 (fundamental flaw)

### H-M1 Risks
- **Low Risk:** Item-level data may not be publicly available for all benchmarks
- **Mitigation:** Use published task difficulty statistics where available; treat as exploratory
- **Impact if FAIL:** SHOULD_WORK gate → does not block Phase 5, but mechanism unclear

### H-M2 Risks
- **Low Risk:** Split-half reliability requires raw item-level scores (may not be available)
- **Mitigation:** Use bootstrapped sampling or skip if data unavailable
- **Impact if FAIL:** SHOULD_WORK gate → does not block Phase 5

### H-C1 Risks
- **Low Risk:** Standard confound control, well-established methods
- **Mitigation:** Use both partial correlation and regression for robustness
- **Impact if FAIL:** SHOULD_WORK gate → suggests confound issue but primary finding (H-E1) still stands

---

## Timeline & Resource Estimate

**Total Duration:** 3-4 weeks (LIGHT tier)

**Week 1-2: H-E1 (Foundation)**
- Data extraction: 2-3 days (manual extraction from papers)
- CV computation: 1 day (straightforward descriptive stats)
- Cross-benchmark ρ computation: 2-3 days (pairwise correlations across 5-10 benchmarks)
- Statistical test & visualization: 1 day

**Week 3: H-M1, H-M2, H-C1 (Parallel)**
- H-M1: 1-2 days (item-level analysis if data available)
- H-M2: 2-3 days (within-benchmark stability, mediation test)
- H-C1: 1-2 days (partial correlation, regression)

**Week 4: Synthesis & Reporting**
- Write Phase 4 validation report
- Retrospective validation (FAVABENCH case study)
- Phase 5 preparation

---

## Dataset Requirements

### Primary Data Source
**Trust Benchmark Leaderboard Corpus**
- TrustLLM (Sun et al.): Table 4-5 (16 models across 8 dimensions)
- HaluBench (PatronusAI): Leaderboard supplement (model count TBD from paper)
- TruthfulQA (Lin et al.): GitHub repo leaderboard (~12 models)
- FinTrust (Hu et al.): Paper leaderboard (model count TBD)
- MultiTrust: Documented in Phase 1 (source TBD)

**Extraction Strategy:**
1. Manual table extraction from PDFs (TrustLLM, FinTrust)
2. GitHub CSV download (TruthfulQA)
3. Supplement PDF extraction (HaluBench)
4. Verify n-models ≥ 10 threshold for each benchmark

**Controlled Variables (from Phase 2A):**
- Dataset: Trust benchmark leaderboard corpus (fixed)
- Model: N/A (meta-analysis, not model training)
- Metrics: CV (computed), Spearman ρ (computed)

---

## Baseline Comparison (Phase 5)

**Baseline Method:** Manual benchmark inspection (current practice)

**Comparison Metrics:**
- **Time:** CV computation (5 min) vs. expert review (hours)
- **Retrospective Validation:** Would CV have flagged FAVABENCH (h-e1 Run 3 failure) as risky?
  - Test: FAVABENCH CV > 75th percentile of TrustLLM/TruthfulQA CVs
  - If yes: CV-based tool would have prevented failure
  - If no: Tool fails retrospective smoke test

**Success Criterion (DETERMINES_SUCCESS):**
- CV-based verification is faster AND catches h-e1 Run 3 failure retrospectively
- Enables prospective risk scoring before Phase 3 commitment

---

## Novelty & Innovation

**Key Innovation:** First predictive meta-feature for benchmark quality - CV computable from any leaderboard in 5 minutes, zero domain expertise required.

**Differentiation from Prior Work:**
- mmjerge (TMLR 2025): Documents fragmentation, doesn't predict reliability
- Kulkarni et al. (arXiv:2504.18114): Shows metric variability, doesn't identify predictors
- h-e1 Run 3: Post-hoc diagnosis vs. our prospective CV-based verification

**Meta-Science Contribution:** Shifts Gap 1 from "build verification tool" to "test if variance predicts reliability" - empirical validation of benchmark quality signals.

---

## Dialectical Synthesis

**Thesis:** Benchmark CV predicts cross-benchmark stability (our hypothesis)

**Antithesis:** Variance is cosmetic and doesn't predict ranking consistency (null hypothesis H₀)

**Synthesis:** If H-E1 passes (r < -0.5, p < 0.05):
- CV becomes a universal zero-cost verification signal
- Researchers can prospectively assess benchmark risk in 5 minutes
- Standard pre-Phase-3 practice: "Compute CV before committing to benchmark"

If H-E1 fails (r ≥ -0.5 or p ≥ 0.05):
- Manual benchmark inspection remains necessary
- No simple meta-feature predicts reliability
- Route to Phase 0: explore alternative quality signals (e.g., inter-rater agreement, task diversity)

---

## Phase 2B Completion

**Status:** ✅ VALIDATED  
**Next Phase:** Phase 2C (Experiment Design for H-E1)  
**Execution Mode:** UNATTENDED  
**Archon Project:** Created and linked to verification_state.yaml
