# Product Requirements Document: h-m4
# Difficulty-Stratified ECE Computation + DELTA_ECE Gate + Temperature Scaling Probe

**stepsCompleted:** ["executive_summary", "problem_statement", "functional_requirements", "nfr", "success_criteria"]
**Hypothesis:** h-m4 (MECHANISM — Step 4 of 4)
**Date:** 2026-03-18
**Author:** Anonymous
**Phase:** 3 — Implementation Planning
**Gate Type:** MUST_WORK
**Type:** FULL tier (30 tasks max)

---

## 1. Executive Summary

h-m4 is the capstone measurement step in the LLM Calibration as Self-Contained Code Verifier pipeline. It measures whether LLM confidence (P(True) logprob-based, from h-m3) is systematically more miscalibrated on hard problems than easy ones — quantified as DELTA_ECE = ECE(hard) - ECE(easy) with M=15 bins, bootstrap 95% CI, and a temperature scaling robustness probe.

This is a **pure statistical analysis experiment** — no new LLM inference is required. All inputs come from validated upstream experiments (h-m1, h-m2, h-m3). The implementation runs on CPU in <5 minutes using numpy/scipy.

**Primary Question:** Does DELTA_ECE ≥ 0.03 with bootstrap 95% CI excluding zero in ≥ 2/3 model families, and does this effect persist after global temperature scaling?

---

## 2. Problem Statement

### Background

LLM confidence signals (P(True) logprob) have been validated as non-degenerate (h-m3: std(c)>0.05 for all 3 models). The core hypothesis of the pipeline is that this confidence is **differentially miscalibrated** across difficulty tiers — i.e., LLMs are more overconfident on hard problems than on easy ones, because their pre-training distribution doesn't encode difficulty-conditioned calibration.

### The Gap

Prior work (h-m1 through h-m3) established:
- k=5 solution generation with full coverage (h-m1)
- Tier stratification with cross-model validity (h-m2: Jaccard > 0.3)
- Non-degenerate P(True) confidence signals (h-m3: std(c) > 0.05)

h-m4 closes the gap by computing the actual calibration error per tier and measuring whether the difference is substantial and statistically significant.

### Scope

- **In scope:** ECE computation per difficulty tier, DELTA_ECE with bootstrap CI, temperature scaling probe, M-sensitivity analysis, null baseline comparison, visualization
- **Out of scope:** New LLM inference, model training, dataset download, hyperparameter search

---

## 3. Functional Requirements

### FR-1: Data Loading and Alignment

**FR-1.1:** Load P(True) confidence scores from `h-m3/results/ptrue_confidence_scores.json`
- Format: `{model_short: {task_id: [c_values]}}` where c ∈ [0,1]
- Must verify file exists; fail early with explicit error if missing

**FR-1.2:** Load tier assignments from `h-m2/results/tier_assignments.csv`
- Format: Wide CSV with 542 rows, columns per model: `{model}_tier ∈ {hard, easy, medium}`
- Filter to hard and easy tiers only (exclude medium)

**FR-1.3:** Load binary correctness labels from `h-e1/results/correctness_{model_short}.json`
- Format: `{task_id: [binary_correctness_per_solution]}` (k=5 solutions)
- Compute per-problem correctness: `y = mean(solutions) > 0 → binary`

**FR-1.4:** Align confidence scores with tier assignments and correctness labels
- Per model: construct aligned arrays `(c_hard, y_hard)` and `(c_easy, y_easy)`
- Validate: `n_hard ≥ 20` AND `n_easy ≥ 20` per model; fail if not met
- Note: CodeLlama has n_easy=0 on HumanEval; use MBPP or combined as primary for CodeLlama

**FR-1.5:** Create 80/20 stratified holdout split per model for temperature fitting
- 80% = ECE evaluation set; 20% = T-fitting holdout
- Use random seed=42 for reproducibility

### FR-2: ECE Computation

**FR-2.1:** Implement `compute_ece(confidences, labels, M=15)` using standard Guo et al. 2017 formula
- M equal-width bins over [0,1]
- `ECE = Σ (n_m/n) * |acc(B_m) - conf(B_m)|`
- Skip empty bins; handle edge case of all-empty model tier

**FR-2.2:** Compute ECE per difficulty tier per model:
- `ECE_hard[model]` = ECE on hard-tier pairs (80% eval set)
- `ECE_easy[model]` = ECE on easy-tier pairs (80% eval set)
- `DELTA_ECE[model]` = `ECE_hard[model] - ECE_easy[model]`

**FR-2.3:** Compute M-sensitivity for M ∈ {10, 15, 20}:
- Report DELTA_ECE for each M value per model
- Primary gate uses M=15 only

### FR-3: Bootstrap Confidence Intervals

**FR-3.1:** Implement `compute_delta_ece_bootstrap(c_hard, y_hard, c_easy, y_easy, n_boot=1000, M=15, seed=42)`
- Bootstrap resampling with replacement on hard and easy tier samples independently
- Compute 1000 bootstrap DELTA_ECE values
- Return: `(delta_ece_obs, ci_lower, ci_upper, p_value)`
  - `ci_lower, ci_upper` = percentile [2.5, 97.5] of bootstrap samples
  - `p_value` = P(DELTA_ECE ≤ 0) = fraction of boot samples ≤ 0

**FR-3.2:** Gate evaluation per model:
- PASS if: `DELTA_ECE ≥ 0.03` AND `ci_lower > 0`
- Count models passing: `n_pass ∈ {0, 1, 2, 3}`
- GATE PASS if `n_pass ≥ 2`

### FR-4: Null Baseline Comparison

**FR-4.1:** Compute tier-null baseline confidence:
- `null_conf_hard[model]` = mean accuracy of hard tier (≈ 0.0 by definition)
- `null_conf_easy[model]` = mean accuracy of easy tier (≈ 0.6+)

**FR-4.2:** Compute null baseline ECE:
- `ECE_null_hard[model]` = ECE where confidence is constant = null_conf_hard
- `ECE_null_easy[model]` = ECE where confidence is constant = null_conf_easy

**FR-4.3:** Compute excess ECE above null baseline:
- `excess_ECE_hard[model]` = `ECE_hard[model] - ECE_null_hard[model]`
- `excess_ECE_easy[model]` = `ECE_easy[model] - ECE_null_easy[model]`
- Secondary gate (P2): `excess_ECE_hard > excess_ECE_easy` in ≥ 2/3 models

### FR-5: Temperature Scaling Probe

**FR-5.1:** Fit global temperature T* per model on 20% holdout set:
- Objective: minimize NLL(c/T, y_holdout) via `scipy.optimize.minimize_scalar`
- Bounds: T ∈ [0.01, 10.0]
- `scaled_c = c / T*` (clipped to [0,1])

**FR-5.2:** Recompute ECE and DELTA_ECE after T-scaling:
- Apply T* to all confidence scores (eval set only, not holdout)
- Compute `post_T_ECE_hard[model]`, `post_T_ECE_easy[model]`, `post_T_DELTA_ECE[model]`
- Bootstrap CI on post-T DELTA_ECE

**FR-5.3:** T-scaling robustness (P3 gate):
- PASS if post-T DELTA_ECE ≥ 0.03 in ≥ 2/3 models with CI excluding zero
- Report T* values for all models

### FR-6: Mechanism Verification

**FR-6.1:** Implement `verify_mechanism_activated(ece_hard, ece_easy, delta_ece, n_hard, n_easy, ci_lower, ci_upper)` per spec in 02c_experiment_brief.md
- Checks: data_loaded, ece_computed, delta_nontrivial, ci_computed, effect_measured
- Log all indicator values

**FR-6.2:** Log per-model diagnostic output to stdout:
```
Model: {model_name}
  n_hard={n_hard}, n_easy={n_easy}
  ECE_hard={ece_hard:.4f}, ECE_easy={ece_easy:.4f}
  DELTA_ECE={delta_ece:.4f}, CI=[{ci_lower:.4f}, {ci_upper:.4f}], p={p_value:.4f}
  T*={T_star:.3f}, post_T_DELTA_ECE={post_t_delta:.4f}
  Gate P1: {"PASS" if gate_p1 else "FAIL"}, P3: {"PASS" if gate_p3 else "FAIL"}
```

### FR-7: Visualization

**FR-7.1 (MANDATORY):** DELTA_ECE bar chart with 95% CI error bars
- Per model, bar heights = DELTA_ECE, error bars = bootstrap 95% CI
- Horizontal dashed lines at y=0 and y=0.03
- Color coding: green = PASS (≥0.03, CI>0), red = FAIL
- Save to: `h-m4/figures/fig1_delta_ece_gate.png`

**FR-7.2 (MANDATORY):** Reliability diagrams per model × tier
- 3 models × 2 tiers (hard/easy) = 6 subplots
- Confidence vs. accuracy across 15 bins; diagonal = perfect calibration
- Annotate ECE value per subplot
- Save to: `h-m4/figures/fig2_reliability_diagrams.png`

**FR-7.3 (MANDATORY):** Temperature scaling effect visualization
- Pre vs. post-T DELTA_ECE comparison per model
- T* values annotated; persistence check visual (before/after bars)
- Save to: `h-m4/figures/fig3_temperature_scaling.png`

**FR-7.4 (ADDITIONAL):** ECE null baseline comparison bar chart
- ECE(tier) vs. ECE(null_tier) per model per tier
- Save to: `h-m4/figures/fig4_null_baseline.png`

**FR-7.5 (ADDITIONAL):** M-sensitivity line plot
- DELTA_ECE vs. M ∈ {10, 15, 20} per model
- Save to: `h-m4/figures/fig5_m_sensitivity.png`

**FR-7.6 (ADDITIONAL):** Bootstrap DELTA_ECE distribution histograms
- 1000 bootstrap DELTA_ECE per model, histogram with 95% CI shading
- Vertical lines at 0 and 0.03
- Save to: `h-m4/figures/fig6_bootstrap_distribution.png`

### FR-8: Results Persistence

**FR-8.1:** Save gate result to `h-m4/results/delta_ece_results.json`:
```json
{
  "gate_overall": "PASS" | "FAIL",
  "n_models_passing_p1": int,
  "models": {
    "{model_short}": {
      "n_hard": int, "n_easy": int,
      "ece_hard": float, "ece_easy": float,
      "delta_ece": float,
      "ci_lower": float, "ci_upper": float,
      "p_value": float,
      "gate_p1": bool,
      "T_star": float,
      "post_T_delta_ece": float,
      "gate_p3": bool,
      "excess_ece_hard": float, "excess_ece_easy": float
    }
  },
  "m_sensitivity": {
    "{model_short}": {"M10": float, "M15": float, "M20": float}
  },
  "gate_p2_count": int,
  "gate_p3_count": int,
  "seed": 42,
  "n_boot": 1000,
  "M_primary": 15
}
```

**FR-8.2:** Results directory structure:
```
h-m4/
  results/
    delta_ece_results.json    # Primary gate results
  figures/
    fig1_delta_ece_gate.png
    fig2_reliability_diagrams.png
    fig3_temperature_scaling.png
    fig4_null_baseline.png
    fig5_m_sensitivity.png
    fig6_bootstrap_distribution.png
  src/
    data_loader.py
    evaluate.py
    temperature_scaling.py
    visualize.py
    run_experiment.py
  tests/
    test_ece.py
    test_bootstrap.py
    test_temperature.py
    test_data_loader.py
```

---

## 4. Non-Functional Requirements

**NFR-1: Reproducibility**
- All random operations use seed=42
- Results must be bit-identical across runs given same seed
- No GPU required; CPU-only with numpy/scipy

**NFR-2: Performance**
- Total runtime < 5 minutes on a single CPU core
- Memory usage < 2 GB

**NFR-3: Error Handling**
- Fail early with explicit error messages if any input file is missing
- Warn (do not fail) on degenerate ECE (NaN bins), bootstrap collapse, T-fitting divergence
- Exclude degenerate models from gate count with explicit warning

**NFR-4: Code Quality**
- Modular structure: data_loader.py, evaluate.py, temperature_scaling.py, visualize.py
- Each module independently testable
- Test coverage ≥ 80% via pytest

**NFR-5: Documentation**
- Inline docstrings for all public functions
- README with run instructions

---

## 5. Data Dependencies

| Input File | Source | Required | Fallback |
|------------|--------|----------|---------|
| `h-m3/results/ptrue_confidence_scores.json` | h-m3 Phase 4 | YES | FAIL EARLY |
| `h-m2/results/tier_assignments.csv` | h-m2 Phase 4 | YES | FAIL EARLY |
| `h-e1/results/correctness_{model}.json` | h-e1 Phase 4 | YES | FAIL EARLY |
| `h-m1/results/pass_at_1_hm1_verified.json` | h-m1 Phase 4 | Optional | Use correctness only |

**Model Short Names:**
- `llama3_8b` → `NousResearch/Meta-Llama-3-8B`
- `codellama_7b` → `codellama/CodeLlama-7b-hf`
- `deepseek_6.7b` → `deepseek-ai/deepseek-coder-6.7b-base`

---

## 6. Success Criteria

### Gate: MUST_WORK

**P1 (Primary — REQUIRED):**
- DELTA_ECE = ECE(hard) - ECE(easy) ≥ 0.03 in ≥ 2/3 model families
- Bootstrap 95% CI lower bound > 0 for those models
- Confidence: M=15 bins, 1000-sample bootstrap, seed=42

**P2 (Secondary — informational):**
- Excess ECE (above null baseline) larger in hard tier than easy tier in ≥ 2/3 models
- Bootstrap p-value < 0.05

**P3 (Temperature Robustness — REQUIRED for full pass):**
- Post-T DELTA_ECE ≥ 0.03 in ≥ 2/3 models with CI excluding zero
- T fitted on 20% holdout via NLL minimization

**Combined GATE PASS:** P1 AND P3 satisfied

**Failure Interpretations (both publishable):**
- DELTA_ECE ≤ 0: Null result — confidence is uniform across difficulty levels
- DELTA_ECE collapses after T: "Globally correctable" — T scaling suffices for VerifAI pipelines

### Code Quality
- All tests pass (pytest)
- No hardcoded paths — use relative paths from h-m4/ folder
- Results JSON validates against schema in FR-8.1

---

## 7. Implementation Constraints

- **No new LLM inference** — all inputs pre-computed
- **No GPU** — CPU-only numpy/scipy implementation
- **Base hypothesis:** h-m3 (architecture, logic, config from h-m3/03_*.md provide reuse context)
- **Incremental:** Reuse data loading patterns from h-m3; extend with tier-stratified computation

---

## 8. Phase 2C Completeness Checklist

| Item | Status |
|------|--------|
| ✅ Baseline model (null calibrator) | Covered in FR-4 |
| ✅ Proposed model (P(True) confidence) | Covered in FR-2 |
| ✅ Primary metric DELTA_ECE | Covered in FR-2, FR-3 |
| ✅ Bootstrap CI (1000 samples) | Covered in FR-3 |
| ✅ Temperature scaling probe | Covered in FR-5 |
| ✅ Null baseline comparison (P2) | Covered in FR-4 |
| ✅ M-sensitivity {10, 15, 20} | Covered in FR-2.3 |
| ✅ All 3 models | Covered throughout |
| ✅ CodeLlama special case | Noted in FR-1.4 |
| ✅ 6 required figures | Covered in FR-7 |
| ✅ Results JSON schema | Covered in FR-8.1 |
