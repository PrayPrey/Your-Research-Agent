# Product Requirements Document: H-M2
## RLHF Representation Rigidity Reduces Adversarial Robustness

**Hypothesis ID:** H-M2  
**Type:** MECHANISM (Step 2 of 3-step RLHF causal chain)  
**Gate:** SHOULD_WORK  
**PRD Version:** 1.0  
**Date:** 2026-08-04  
**Author:** Anonymous  
**stepsCompleted:** [prd-step-1, prd-step-2, prd-step-3, prd-step-4, prd-step-5]

---

## 1. Executive Summary

H-M2 tests whether RLHF-induced conservative refusal patterns create representation-level rigidity that is brittle to adversarial perturbations, manifesting as a negative partial Spearman correlation between safety and adversarial robustness dimensions when controlling for model scale and alignment status. This is the second step in the 3-step RLHF causal chain established by H-E1 (correlation structure exists) and H-M1 (RLHF co-optimizes safety+ethics).

H-M2 requires no neural model training. Implementation consists of: (1) extracting the robustness column from pre-computed H-E1 data, (2) computing or reading ρ_partial(safety, robustness) from the pre-computed 6×6 matrix, (3) running within-family Δ_robustness sign tests for LLaMA-2 7B/13B/70B pairs, and (4) optionally running Pythia lm-eval-harness as a scale-only control.

**Gate condition (SHOULD_WORK):** Failure does not stop the pipeline. A positive ρ_partial is itself a publishable null finding.

---

## 2. Problem Statement

### 2.1 Research Question

Does RLHF alignment create a safety-robustness trade-off? Specifically:
- Is ρ_partial(safety, robustness) < -0.4 (p < 0.0033 Bonferroni) when controlling for log(param_count) and RLHF status?
- Do RLHF Chat models score equal or lower than size-matched base models on adversarial robustness?

### 2.2 Mechanism Under Test

RLHF optimizes models toward conservative refusal of harmful requests via preference learning. The hypothesis posits that this produces pattern-matching representations that:
- Are effective at flagging harmful content (high safety scores)
- Are simultaneously brittle to adversarial input perturbations (low robustness scores)

This would manifest as a negative partial correlation between safety and robustness, controlling for scale effects.

### 2.3 Theoretical Grounding

- Vennemeyer et al. 2026 (arXiv:2601.12639): "preference-based fine-tuning tightly couples capability gains to increased adversarial vulnerability"
- Sun et al. 2024 TrustLLM ICML (arXiv:2401.05561): notes over-calibration in LLaMA-2 family
- H-E1 finding: "Robustness uncorrelated with other dims" — consistent with H-M2 negative prediction
- H-E1 silhouette=0.614 for k=2 clusters: safety-robustness in different clusters

### 2.4 Prior Results Context

From H-M1 (prerequisite, PASS):
- ρ_partial(safety, ethics) = 0.841 → positive RLHF cluster confirmed
- 3/3 LLaMA-2 pairs: Δ_safety > 0 AND Δ_ethics > 0
- Dataset cache: h-e1/experiment_results_phase3.json (full 16×6 rho_partial matrix + raw scores)

---

## 3. Scope

### 3.1 In Scope

- Extract adversarial robustness dimension scores from pre-computed H-E1 data
- Read or recompute ρ_partial(safety, robustness) from 6×6 matrix
- Within-family Δ_robustness sign test for LLaMA-2 7B/13B/70B (3 pairs)
- Visualization: heatmap, bar charts, scatter plot, cluster motivation plot
- Optional: Pythia lm-eval-harness AdvGLUE scores as scale-only control
- Generate figures to `h-m2/figures/`
- Save results to `h-m2/experiment_results_h_m2.json`

### 3.2 Out of Scope

- Neural model training or fine-tuning
- New benchmark data collection (TrustLLM scores already cached)
- Multi-GPU computation (pure CPU scipy analysis, <5 seconds)
- H-M3 cluster verification (separate hypothesis)

---

## 4. Data Specification

### 4.1 Primary Dataset: TrustLLM Published Score Tables

| Attribute | Value |
|-----------|-------|
| Name | TrustLLM Published Score Tables (16-model × 6-dimension) |
| Type | Standard (published benchmark, ICML 2024) |
| Source | HowieHwong/TrustLLM GitHub — results/*.json |
| Cache Path | h-e1/experiment_results_phase3.json (primary) |
| Verified | true (reused from H-E1 and H-M1) |
| Download Required | NO — already cached from H-E1 |
| Models | 16 models including LLaMA-2 7B/13B/70B base+Chat |
| Dimensions | 6: safety, robustness, truthfulness, fairness, privacy, machine_ethics |

**Robustness dimension sub-tasks (composites aggregated to single score):**

| Sub-task | Dataset | N Samples | Metric |
|----------|---------|-----------|--------|
| Natural Noise (AdvGLUE) | AdvGLUE | 912 | ASR (↓), RS (↑) |
| Natural Noise (AdvInstruction) | AdvInstruction | variable | Embedding similarity (↑) |
| OOD Detection | Custom | variable | RtA (↑) |
| OOD Generalization | Custom | variable | Micro F1 (↑) |

**Loading code:**
```python
import json
with open("../h-e1/experiment_results_phase3.json") as f:
    h_e1_results = json.load(f)

rho_matrix = h_e1_results["rho_partial_matrix"]    # 6×6 dict
model_scores = h_e1_results["model_scores"]         # {model_name: {dim: score}}
```

### 4.2 Model Metadata (Required for OLS Covariates)

```python
model_metadata = {
    "llama_2_7b":        {"log_params": 6.845, "is_RLHF": 0},
    "llama_2_7b_chat":   {"log_params": 6.845, "is_RLHF": 1},
    "llama_2_13b":       {"log_params": 7.114, "is_RLHF": 0},
    "llama_2_13b_chat":  {"log_params": 7.114, "is_RLHF": 1},
    "llama_2_70b":       {"log_params": 7.845, "is_RLHF": 0},
    "llama_2_70b_chat":  {"log_params": 7.845, "is_RLHF": 1},
    # + 10 additional TrustLLM models (from H-E1 annotations)
}
```

### 4.3 Optional Dataset: Pythia Scale-Only Control

| Attribute | Value |
|-----------|-------|
| Name | Pythia scaling series lm-eval-harness results |
| Type | Programmatic-API (EleutherAI/lm-evaluation-harness) |
| Models | pythia-70m, 160m, 410m, 1b, 1.4b, 2.8b, 6.9b, 12b (8 checkpoints) |
| Task | AdvGLUE (ANLI adversarial NLI subset) |
| Purpose | Verify ρ(safety_proxy, robustness) near zero for RLHF=False series |
| Download Required | Conditional — check h-e1 cache first; skip if unavailable |
| If Unavailable | Skip, note as limitation; primary gate unaffected |

**Preprocessing:** None required — TrustLLM scores are pre-computed composite scores per dimension, normalized [0,1]. Pythia scores require lm-eval-harness task-specific normalization (task handles this).

---

## 5. Functional Requirements

### FR-1: Data Loading and Validation

**Priority:** Critical  
**Source:** Phase 2C §Dataset, §Training Protocol Step 1

- FR-1.1: Load h-e1/experiment_results_phase3.json and validate JSON structure
- FR-1.2: Extract rho_partial_matrix (6×6 dict) and model_scores (16 models × 6 dims)
- FR-1.3: Validate robustness column present for all 16 models
- FR-1.4: Validate model_metadata (log_params, is_RLHF) for all 16 models
- FR-1.5: Validate LLaMA-2 family present: llama_2_7b, llama_2_7b_chat, llama_2_13b, llama_2_13b_chat, llama_2_70b, llama_2_70b_chat

### FR-2: Primary Gate — ρ_partial(safety, robustness)

**Priority:** Critical  
**Source:** Phase 2C §Training Protocol Step 2, §Evaluation

- FR-2.1: Read ρ_partial(safety, robustness) from pre-computed H-E1 matrix (direct lookup preferred)
- FR-2.2: If value missing or needing verification, recompute using OLS residualization:
  ```python
  def compute_partial_spearman(scores, dim_x, dim_y, covariates):
      # OLS residualization (established in H-E1, reuse exact pattern)
      models = sorted(scores.keys())
      x = np.array([scores[m][dim_x] for m in models])
      y = np.array([scores[m][dim_y] for m in models])
      Z = np.column_stack([[scores[m][c] for m in models] for c in covariates])
      def residualize(v, Z):
          reg = LinearRegression(fit_intercept=True).fit(Z, v)
          return v - reg.predict(Z)
      x_res, y_res = residualize(x, Z), residualize(y, Z)
      rho, _ = stats.spearmanr(x_res, y_res)
      n, k = len(models), Z.shape[1]
      t_stat = rho * np.sqrt((n - 2 - k) / (1 - rho**2))
      p_val = 2 * stats.t.sf(abs(t_stat), df=n-2-k)
      return rho, p_val
  ```
- FR-2.3: Apply t-distribution p-value (df=n-2-k=16-2-2=12, NOT scipy default)
- FR-2.4: Apply Bonferroni threshold: alpha=0.05/15=0.0033
- FR-2.5: Evaluate primary gate: rho_sr < -0.4 AND p_sr < 0.0033
- FR-2.6: Cross-validate with pingouin.partial_corr for consistency check
- FR-2.7: Report gate result as PASS/FAIL/EXPLORE

### FR-3: Secondary Gate — Within-Family Δ_robustness Sign Test

**Priority:** High  
**Source:** Phase 2C §Training Protocol Step 3, §Mechanism Verification

- FR-3.1: Compute Δ_robustness for each LLaMA-2 scale pair:
  - Δ_robustness_7B = llama_2_7b_chat.robustness − llama_2_7b.robustness
  - Δ_robustness_13B = llama_2_13b_chat.robustness − llama_2_13b.robustness
  - Δ_robustness_70B = llama_2_70b_chat.robustness − llama_2_70b.robustness
- FR-3.2: Count pairs with Δ_robustness ≤ 0 (RLHF does not improve robustness)
- FR-3.3: Evaluate secondary gate: n_nonpositive ≥ 2 (out of 3 pairs)
- FR-3.4: Report exact Δ values, directions, and gate result

### FR-4: Pythia Scale-Only Control (Optional)

**Priority:** Medium  
**Source:** Phase 2C §Training Protocol Step 4, §Dataset

- FR-4.1: Check h-e1/experiment_results_phase3.json for Pythia results; check h-e1/code/ for cached lm-eval results
- FR-4.2: If available, compute ρ(robustness_proxy, log_scale) for Pythia series (RLHF=False)
- FR-4.3: If not available, attempt lm-eval-harness run:
  ```bash
  lm_eval --model hf --model_args pretrained=EleutherAI/pythia-{size} --tasks advglue --device cpu
  ```
- FR-4.4: If Pythia entirely unavailable: skip, note as limitation, primary gate unaffected
- FR-4.5: Report ρ(Pythia_robustness, log_scale) — expected near-zero (scale only, no RLHF)

### FR-5: Visualization

**Priority:** High  
**Source:** Phase 2C §Visualization Requirements

All figures saved to `h-m2/figures/`.

- FR-5.1: **Gate Metrics Bar Chart** (mandatory): ρ_partial(safety, robustness) vs -0.4 threshold; Δ_robustness bars for 3 LLaMA-2 scales vs 0 threshold
- FR-5.2: **Within-Family Δ_robustness Grouped Bar Chart**: Δ_safety vs Δ_robustness side-by-side for LLaMA-2 7B/13B/70B (shows directional divergence)
- FR-5.3: **6×6 ρ_partial Heatmap**: full correlation matrix with safety-robustness cell highlighted (contrast with safety-ethics positive cell)
- FR-5.4: **Safety vs Robustness Scatter**: 16 models, color by RLHF status, with partial regression trend lines
- FR-5.5: **Cluster Motivation Plot** (optional): 2D projection showing RLHF-sensitive vs RLHF-insensitive cluster separation

### FR-6: Results Persistence

**Priority:** Critical  
**Source:** Phase 2C §State Information, Phase 4 integration

- FR-6.1: Save all results to `h-m2/experiment_results_h_m2.json`:
  ```json
  {
    "hypothesis_id": "h-m2",
    "rho_partial_safety_robustness": <float>,
    "p_value_safety_robustness": <float>,
    "primary_gate_pass": <bool>,
    "delta_robustness": {"7B": <float>, "13B": <float>, "70B": <float>},
    "n_nonpositive_delta": <int>,
    "secondary_gate_pass": <bool>,
    "overall_gate": "PASS|PARTIAL_PASS|FAIL",
    "pythia_rho_robustness_scale": <float|null>,
    "figure_paths": [...]
  }
  ```
- FR-6.2: Print gate verification messages per Phase 2C §Mechanism Verification Code

---

## 6. Non-Functional Requirements

### NFR-1: Performance
- Runtime < 10 seconds for primary analysis (pure numpy/scipy, no GPU required)
- Pythia lm-eval optional; may take 10-30 minutes per checkpoint if re-run

### NFR-2: Reproducibility
- Seed: 1 (deterministic statistical analysis — no randomness)
- Environment: youra-h-m1 conda (reuse: Python 3.10, scipy 1.11.0, sklearn, numpy, pandas)

### NFR-3: Continuity with H-E1/H-M1
- OLS residualization must use identical pattern to H-E1 (same function signature)
- Model annotations must be identical (same log_params values, same is_RLHF flags)
- If recomputed rho differs from H-E1 matrix value by >0.001, log warning and use H-E1 value

### NFR-4: SHOULD_WORK Gate Compliance
- Code must NOT terminate on primary gate failure
- Failure result must be saved and reported (publishable null finding)
- Pipeline continuation checkpoint must be written regardless of gate result

---

## 7. Dependencies

### 7.1 Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| scipy | 1.11.0 | spearmanr, t-distribution |
| scikit-learn | latest | LinearRegression (OLS residualization) |
| numpy | latest | Array operations |
| pandas | latest | Data management |
| pingouin | latest | partial_corr cross-validation |
| matplotlib | latest | Figures |
| seaborn | latest | Heatmap |
| json | stdlib | Data loading |

**Environment:** Reuse `youra-h-m1` conda environment (all packages already installed)

### 7.2 External Repositories

| Repository | Purpose | Access |
|------------|---------|--------|
| HowieHwong/TrustLLM | Primary data source (already cached) | h-e1/experiment_results_phase3.json |
| raphaelvallat/pingouin | partial_corr cross-validation | pip install pingouin |
| EleutherAI/lm-evaluation-harness | Pythia AdvGLUE scores (optional) | pip install lm-eval |

### 7.3 Prerequisite Files

| File | Source | Required |
|------|--------|---------|
| h-e1/experiment_results_phase3.json | H-E1 Phase 4 output | YES — primary data |
| h-m1/04_validation.md | H-M1 Phase 4 output | Reference only |
| h-e1/04_validation.md | H-E1 Phase 4 output | Reference only |

---

## 8. Success Criteria

### 8.1 Primary Gate (SHOULD_WORK)

| Metric | Threshold | Expected |
|--------|-----------|---------|
| ρ_partial(safety, robustness) | < -0.4 | Negative (H-E1 silhouette evidence) |
| p-value (Bonferroni-corrected) | < 0.0033 | Significant |

### 8.2 Secondary Gate

| Metric | Threshold | Expected |
|--------|-----------|---------|
| LLaMA-2 pairs Δ_robustness ≤ 0 | ≥ 2/3 pairs | Consistent with over-calibration |

### 8.3 Outcome Classification

| Result | Condition | Action |
|--------|-----------|--------|
| PASS | Both primary AND secondary | Report positive mechanism confirmation |
| PARTIAL_PASS | Primary satisfied, secondary fails (or vice versa) | Document and continue pipeline |
| FAIL/EXPLORE | Primary fails (ρ_partial > 0 or p > 0.0033) | Report null finding; SHOULD_WORK = pipeline continues |

### 8.4 PoC Pass Condition

1. Code runs without error
2. ρ_partial(safety, robustness) value computed and compared to -0.4 threshold
3. Δ_robustness computed for all 3 LLaMA-2 pairs
4. Results saved to experiment_results_h_m2.json
5. All mandatory figures generated

---

## 9. Ablation Variants

### Ablation A1: Uncontrolled Spearman (No OLS)
- Compute raw Spearman(safety, robustness) without controlling for log_params and is_RLHF
- Compare with partial Spearman to quantify confound contribution
- Expected: uncontrolled rho will differ due to scale confound

### Ablation A2: Alternative Covariates
- Re-run OLS residualization with only log_params (no is_RLHF covariate)
- Re-run with only is_RLHF (no log_params covariate)
- Purpose: Identify which covariate drives the partial correlation

### Ablation A3: pingouin Cross-Validation
- Compute partial_corr via pingouin rank-transform method
- Expected: agrees with OLS method within ±0.01 (methods should converge)
- If discrepancy: report both and note methodological uncertainty

---

## 10. Implementation Notes

### 10.1 Code Structure

```
h-m2/
├── code/
│   ├── run_h_m2.py          # Main analysis script
│   ├── utils.py             # Shared OLS + stats utilities (reuse from H-M1)
│   └── visualize.py         # Figure generation
├── figures/
│   ├── gate_metrics.png     # FR-5.1
│   ├── delta_robustness.png # FR-5.2
│   ├── rho_heatmap.png      # FR-5.3
│   └── safety_rob_scatter.png # FR-5.4
└── experiment_results_h_m2.json
```

### 10.2 Key Design Decision: Direct Matrix Read vs Recomputation

H-E1 already computed the full 6×6 rho_partial matrix. Implementation should:
1. **First**: Read ρ_partial(safety, robustness) directly from h-e1/experiment_results_phase3.json
2. **Then**: Cross-validate by recomputing (to catch any JSON structure mismatch)
3. **If mismatch > 0.001**: Log warning, use recomputed value, document discrepancy

### 10.3 SHOULD_WORK Gate Behavior

This is the **first mechanism test that could fail** (vs H-E1/H-M1 which both passed). Code must:
- Never raise exception on gate failure
- Always write results JSON regardless of outcome
- Write clear EXPLORE message if primary gate fails: "ρ_partial(safety,robustness) = {value:.4f} — positive correlation; null finding for H-M2 mechanism"
