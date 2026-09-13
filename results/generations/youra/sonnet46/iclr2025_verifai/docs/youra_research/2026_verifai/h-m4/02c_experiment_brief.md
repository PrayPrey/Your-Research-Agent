# Experiment Design: h-m4

**Date:** 2026-03-18
**Author:** Anonymous
**Hypothesis Statement:** Under M=15-bin ECE computation per difficulty tier using P(True) confidence from H-M3, if DELTA_ECE = ECE(hard) - ECE(easy) is measured with 1000-sample bootstrap 95% CIs and compared to a tier-specific null baseline (constant confidence = tier accuracy), then DELTA_ECE >= 0.03 (CI excluding zero) in >=2/3 model families AND persists after global temperature scaling (T fitted on 20% holdout), because LLM confidence from pre-training does not align with difficulty structure and global T cannot correct difficulty-conditioned miscalibration.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (Step 4 of 4)** - Core calibration measurement: DELTA_ECE per difficulty tier + temperature scaling probe.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** h-m3 COMPLETED (MUST_WORK PASS — std(c)>0.05 for all 3 models, n=5730 pairs)
**Gate Status:** MUST_WORK — DELTA_ECE >= 0.03 in >=2/3 models with CI excluding zero; persists post-T-scaling

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m4
- **Type:** MECHANISM (Step 4 of 4)
- **Prerequisites:** h-m3 (COMPLETED, PASS)

### Gate Condition

**Gate Type:** MUST_WORK

**Pass Criteria (ALL required):**
- **P1 (Primary):** DELTA_ECE = ECE(hard) - ECE(easy) >= 0.03 in >=2/3 model families, with bootstrap 95% CI excluding zero
- **P2 (Secondary):** Excess ECE (above tier-null baseline) is larger in hard tier than easy tier (p<0.05 bootstrap)
- **P3 (Temperature Probe):** DELTA_ECE >= 0.03 persists after global temperature scaling (T fitted on 20% holdout)

**Failure Interpretation:**
- DELTA_ECE <= 0: Publish as null result — LLM confidence is uniform across difficulty levels
- DELTA_ECE collapses after T: Publish as "globally correctable" finding — T scaling is sufficient for VerifAI pipelines
- Both outcomes are publishable measurement contributions

---

## Continuation Context

### Previous Hypothesis Results

**h-m3 (COMPLETED, MUST_WORK PASS):**
- P(True) logprob elicitation validated for all 3 models (std(c)>0.05)
- 5,730 (problem, solution) pairs processed with confidence scores c ∈ [0, 1]
- Key findings:
  - llama3_8b: mean_c=0.4989, std_c=0.0669, hard mean_c=0.488, easy mean_c=0.514
  - codellama_7b: mean_c=0.3682, std_c=0.0618, hard mean_c=0.366, easy mean_c=0.385
  - deepseek_6.7b: mean_c=0.6480, std_c=0.0781, hard mean_c=0.652, easy mean_c=0.644
  - deepseek shows near-zero correctness correlation (-0.046, p=0.048) — confidence less aligned
  - codellama has unbalanced tier split (185 easy vs 1705 hard) — note in ECE analysis
- Output: `h-m3/results/ptrue_confidence_scores.json` (697 KB) — primary input for h-m4

**h-m2 (COMPLETED, SHOULD_WORK PASS):**
- Tier assignments: `h-m2/results/tier_assignments.csv` (wide-format, 542 rows)
- Hard-tier sizes: llama3_8b(≈78-150 per benchmark), codellama_7b(≈142-199), deepseek_6.7b(≈68-105)

**h-m1 (COMPLETED, MUST_WORK PASS):**
- Correctness files: `h-e1/results/correctness_{model_short}.json` (binary, per problem)
- pass_at_1 data: `h-m1/results/pass_at_1_hm1_verified.json` (542 problems × 3 models)

**Reuse Strategy:** h-m4 is a pure analysis/computation task — NO new LLM inference required.
All data from h-m3 results is loaded and processed with numpy/scipy only (CPU-only experiment).

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "ECE calibration temperature scaling LLM"**
- Archon KB returned low-similarity results (0.41 aggregate similarity) from unrelated domains (diffusers, CUDA docs)
- No directly relevant ECE calibration papers indexed in this Archon KB instance
- **Key Takeaway:** Archon KB does not contain ECE-specific literature for this project; relying on Exa findings for implementation guidance

**Query 2: "Expected Calibration Error bin computation bootstrap confidence interval"**
- Results: Low-similarity matches (0.36 max) from image generation/MiDaS repositories
- No bootstrap ECE implementations found in KB
- **Key Takeaway:** ECE/bootstrap CI implementation must be sourced from Exa/literature directly

**Query 3: "difficulty stratification code benchmark calibration"**
- Results: Low-similarity matches (0.42 max) from CUDA and gist repositories
- No difficulty-stratified calibration implementations in KB
- **Key Takeaway:** Novel intersection — no past Archon cases for this exact pattern

**Assessment:** Archon KB is indexed with diffusion model / image generation content and does not contain LLM calibration literature. Primary research guidance comes from Exa GitHub search results below.

### Archon Code Examples

**Query: "ECE calibration Python temperature scaling"**
- Results: Diffusion model calibration code (Optimum Quanto), image generation pipelines — not relevant to ECE/LLM calibration
- No usable ECE code snippets in Archon KB

**Query: "bootstrap confidence interval calibration metrics"**
- Results: FID/PPL metric configurations for GANs — not relevant
- No bootstrap CI implementations in KB

**Assessment:** Archon code examples are domain-mismatched for this hypothesis. All pseudo-code derived from Exa GitHub sources.

---

### Exa GitHub Implementations

**Query 1: "Expected Calibration Error ECE Python implementation temperature scaling LLM calibration"**

**Source 1 — ECE Formula Reference:**
- **URL:** https://mbrenndoerfer.com/writing/calibration-machine-learning-confidence-accuracy-ece
- **Relevance:** Standard ECE formulation: `ECE = Σ (n_m/n) * |acc(B_m) - conf(B_m)|` with M uniform bins
- **Key insight:** Bin weighting by `n_m/n` (bin population fraction) is the standard approach per Guo et al. 2017
- **Used for:** Core ECE computation formula in pseudo-code

**Source 2 — ECE Python Implementation (Numpy):**
- **URL:** https://towardsdatascience.com/expected-calibration-error-ece-a-step-by-step-visual-explanation-with-python-code-c3e9aa12937d/
```python
def expected_calibration_error(samples, true_labels, M=15):
    bin_boundaries = np.linspace(0, 1, M + 1)
    bin_lowers = bin_boundaries[:-1]
    bin_uppers = bin_boundaries[1:]
    confidences = np.max(samples, axis=1)  # For binary: c directly
    predicted_label = np.argmax(samples, axis=1)
    ece = np.zeros(1)
    for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
        in_bin = np.logical_and(confidences > bin_lower, confidences <= bin_upper)
        prob_in_bin = in_bin.mean()
        ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prob_in_bin
    return ece
```
- **Used for:** Binary ECE template (adapted for P(True) c values vs. binary correctness)

**Source 3 — ECE Library with Bootstrap CIs:**
- **URL:** https://github.com/p-lambda/verified_calibration (MIT, Python)
- **Relevance:** `cal.get_ece(model_probs, labels)` with bootstrap confidence intervals — CRITICAL for h-m4
- **Key feature:** Bootstrap resampling for calibration error CI estimation, more accurate than plugin estimator
- **Used for:** Bootstrap 95% CI implementation pattern

**Source 4 — Temperature Scaling Reference (Gpleiss et al.):**
- **URL:** https://github.com/gpleiss/temperature_scaling (1167 stars, MIT, now unmaintained)
- **Relevance:** Canonical temperature scaling implementation; fit T on validation set by minimizing NLL
```python
class ModelWithTemperature(nn.Module):
    def __init__(self, model):
        self.temperature = nn.Parameter(torch.ones(1) * 1.5)
    def temperature_scale(self, logits):
        return logits / self.temperature
    def set_temperature(self, valid_loader):
        # Optimize NLL on validation set
        nll_criterion = nn.CrossEntropyLoss()
        # LBFGS optimization of T
```
- **Note:** gpleiss repo is unmaintained; use `dholzmueller/probmetrics` for production (`'temp-scaling'` method)
- **Used for:** Temperature scaling conceptual design (adapted for logit space)

**Source 5 — Temperature Scaling for LLMs (Adaptive):**
- **URL:** https://github.com/johnathan-xie/adaptive-temperature-scaling (Apache-2.0)
- **Relevance:** Calibrating language models with temperature on logits; ECE-based evaluation
- **Key insight:** "calibration model class wraps any HuggingFace causal language model and operates on top of the output logits" — applicable to P(True) logprob elicitation
- **Used for:** Temperature scaling probe design for h-m4

**Source 6 — Generalized/Stratified ECE:**
- **URL:** https://github.com/cmu-sei/gce (Python, MIT)
- **Relevance:** Context-specific calibration error framework — enables stratification by difficulty tier
- **Key feature:** Custom calibration metric components (perfect for tier-stratified ECE)
- **Used for:** Conceptual basis for tier-stratified ECE computation

**Query 2: "P True logprob confidence calibration difficulty stratified ECE"**

**Source 7 — P(True) Logprob for Binary Classification:**
- **URL:** https://ericjinks.com/blog/2025/logprobs/
- **Relevance:** Binary classification with logprob confidence; using exp(logprob) as confidence score
- **Key code pattern:** `confidence = Math.exp(trueOrFalseLogprob.logprob)` — same normalization as h-m3
- **Used for:** Confirming c value interpretation for ECE input

**Source 8 — Calibration Methods Overview:**
- **URL:** https://www.rohan-paul.com/p/ml-interview-q-series-probability-95f
- **Key insight:** "Stratified calibration for minority classes: validation set stratified to ensure adequate coverage" — relevant for unbalanced hard/easy tiers
- **Used for:** Tier-stratified ECE design justification

**Serena Analysis Needed:** false — ECE and temperature scaling implementations are sufficiently documented through standard numpy/scipy patterns.

### 🎯 Implementation Priority Assessment

**CRITICAL: This is a pure analysis experiment — no new LLM inference required.**

**Recommended Implementation Path:**
- **Primary:** Custom numpy/scipy implementation of ECE, bootstrap CI, and temperature scaling using validated h-m3 outputs
- **Fallback:** `p-lambda/verified_calibration` library (`pip install calibration`) for ECE + bootstrap CIs
- **Justification:** h-m4 is a statistical analysis task on pre-computed confidence scores. Standard numpy ECE computation is straightforward, well-understood, and testable. No GPU required. Custom implementation gives full control over tier-stratified computation and bootstrap resampling.

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear for ECE and temperature scaling implementation. All required patterns are standard numpy/scipy operations documented in multiple well-known sources (Guo et al. 2017, p-lambda/verified_calibration, gpleiss/temperature_scaling). No complex codebase analysis required.

---

## Experiment Specification

### Dataset

**Name:** Pre-computed P(True) confidence scores from h-m3 + tier assignments from h-m2 + correctness labels from h-e1
**Type:** programmatic-api (real data via pipeline results from validated upstream experiments)
**Source:** Results from h-m3, h-m2, h-m1, h-e1 experiments in this pipeline
**Coverage:** 542 problems (HumanEval+ 164 + MBPP+ 378) × 3 models = 5,730 (problem, model) pairs

**Data Inputs:**

| File | Source | Content | Size |
|------|--------|---------|------|
| `h-m3/results/ptrue_confidence_scores.json` | h-m3 Phase 4 | Per-model {task_id: [c_values]} for hard+easy pairs | 697 KB |
| `h-m2/results/tier_assignments.csv` | h-m2 Phase 4 | Wide-format tier assignments (hard/easy/medium per model) | ~30 KB |
| `h-e1/results/correctness_{model}.json` | h-e1 Phase 4 | Binary correctness per (problem, solution, model) | ~50 KB each |
| `h-m1/results/pass_at_1_hm1_verified.json` | h-m1 Phase 4 | Pass@1 per (problem, model) | ~20 KB |

**No download required** — all inputs exist in pipeline results directory.

**Tier Sizes (from h-m2 validation):**

| Model | n_hard (HE) | n_hard (MBPP) | n_easy (HE) | n_easy (MBPP) |
|-------|-------------|----------------|-------------|----------------|
| llama3_8b | 78 | 150 | 39 | 128 |
| codellama_7b | 142 | 199 | 0 | 37 |
| deepseek_6.7b | 68 | 105 | 24 | 176 |

**Notes:**
- CodeLlama has n_easy=0 on HumanEval — use MBPP as primary or combined analysis for CodeLlama
- All models have sufficient n>=20 for hard tier on both benchmarks
- Medium-difficulty problems (0.0 < pass@1 < 0.6) are excluded from ECE analysis

**Loading Information** (for Phase 4):
- Method: Direct JSON/CSV load (no download needed)
- Identifier: Relative paths from h-m4/ folder
- Code:
```python
import json, pandas as pd, numpy as np
confidence_scores = json.load(open("../h-m3/results/ptrue_confidence_scores.json"))
tier_df = pd.read_csv("../h-m2/results/tier_assignments.csv")
correctness = json.load(open("../h-e1/results/correctness_llama3_8b.json"))
```

### Models

#### Baseline Model

**Architecture:** Tier-null calibrator (constant confidence = tier accuracy — the trivial calibration baseline)

**Purpose:** The null baseline represents a model that predicts confidence equal to the empirical accuracy of each tier. This controls for the base-rate accuracy difference between hard and easy tiers.

- Hard-tier null: confidence(hard) = mean_accuracy(hard tier) ≈ 0.0 (by definition: hard = pass@1=0.0)
- Easy-tier null: confidence(easy) = mean_accuracy(easy tier) ≈ 0.6-1.0

**Loading Information:**
- Method: Computed from tier assignments + correctness labels (no pretrained model)
- Code:
```python
# Compute null baseline confidence per tier
null_conf_hard = np.mean([correctness[tid] for tid in hard_tier_ids])  # ≈ 0.0
null_conf_easy = np.mean([correctness[tid] for tid in easy_tier_ids])   # ≈ 0.6+
```

#### Proposed Model

**Architecture:** P(True) logprob-based confidence calibration (actual model confidence from h-m3)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Difficulty-Stratified ECE + DELTA_ECE Computation + Temperature Scaling Probe
# Based on: Guo et al. 2017 (ECE formula), p-lambda/verified_calibration (bootstrap CIs)
# Adapted for: Binary P(True) confidence c ∈ [0,1] vs. binary correctness labels

import numpy as np
from scipy.optimize import minimize_scalar

def compute_ece(confidences, labels, M=15):
    """Compute Expected Calibration Error.
    Args:
        confidences: np.array of shape (N,) with c ∈ [0,1]
        labels: np.array of shape (N,) with binary correctness {0,1}
        M: number of equal-width bins
    Returns: ECE scalar
    """
    bins = np.linspace(0, 1, M + 1)
    ece = 0.0
    for i in range(M):
        in_bin = (confidences > bins[i]) & (confidences <= bins[i+1])
        n_bin = in_bin.sum()
        if n_bin == 0:
            continue
        acc_bin = labels[in_bin].mean()
        conf_bin = confidences[in_bin].mean()
        ece += (n_bin / len(confidences)) * abs(acc_bin - conf_bin)
    return ece

def compute_delta_ece_bootstrap(c_hard, y_hard, c_easy, y_easy, n_boot=1000, M=15, seed=42):
    """Bootstrap 95% CI for DELTA_ECE = ECE(hard) - ECE(easy).
    Returns: delta_ece (point), ci_lower, ci_upper, p_value
    """
    rng = np.random.default_rng(seed)
    delta_ece_obs = compute_ece(c_hard, y_hard, M) - compute_ece(c_easy, y_easy, M)
    boot_deltas = np.zeros(n_boot)
    for b in range(n_boot):
        idx_h = rng.integers(0, len(c_hard), len(c_hard))
        idx_e = rng.integers(0, len(c_easy), len(c_easy))
        boot_deltas[b] = compute_ece(c_hard[idx_h], y_hard[idx_h], M) \
                        - compute_ece(c_easy[idx_e], y_easy[idx_e], M)
    ci_lower, ci_upper = np.percentile(boot_deltas, [2.5, 97.5])
    p_value = np.mean(boot_deltas <= 0)  # one-sided P(DELTA_ECE <= 0 under bootstrap)
    return delta_ece_obs, ci_lower, ci_upper, p_value

def fit_temperature(logits_holdout, labels_holdout):
    """Fit global temperature T on 20% holdout by minimizing NLL."""
    def nll(T):
        scaled_logits = logits_holdout / T
        probs = np.exp(scaled_logits) / np.exp(scaled_logits).sum()  # binary softmax
        return -np.mean(labels_holdout * np.log(probs + 1e-8) + (1-labels_holdout) * np.log(1-probs + 1e-8))
    result = minimize_scalar(nll, bounds=(0.01, 10.0), method='bounded')
    return result.x  # optimal T

# Main experiment flow:
# 1. Load c_values, tier_ids, correctness labels
# 2. Split: 80% test / 20% T-fitting holdout
# 3. Compute ECE(hard), ECE(easy), DELTA_ECE with bootstrap CI
# 4. Fit T on holdout; scale c by T; recompute DELTA_ECE
# 5. Compare pre/post T-scaling DELTA_ECE (P3 persistence check)
# 6. Repeat for all 3 models; count families with DELTA_ECE >= 0.03
```

### Training Protocol

**Type:** Pure statistical analysis — NO model training or GPU required

h-m4 is a computation-only experiment on pre-computed confidence scores. There is no training loop.

**Computation Protocol:**

| Step | Operation | Input | Output |
|------|-----------|-------|--------|
| 1 | Load data | h-m3/results/, h-m2/results/, h-e1/results/ | Aligned (c, y, tier) tuples per model |
| 2 | Tier split | tier_assignments.csv | hard_pairs, easy_pairs per model |
| 3 | T-fitting holdout | 20% random stratified split of hard+easy combined | holdout set per model |
| 4 | ECE computation | c values + binary labels, M=15 bins | ECE(hard), ECE(easy) per model |
| 5 | DELTA_ECE | ECE(hard) - ECE(easy) | Point estimate per model |
| 6 | Bootstrap CI | 1000 bootstrap samples on DELTA_ECE | 95% CI per model |
| 7 | Null baseline | Tier accuracy as constant confidence | Excess ECE: ECE(tier) - ECE(null_tier) |
| 8 | Temperature fit | NLL minimization on holdout | T* per model |
| 9 | Post-T ECE | Scale c by T*, recompute all metrics | Post-T DELTA_ECE per model |
| 10 | Sensitivity | M ∈ {10, 15, 20} | DELTA_ECE stability across M |

**Random Seeds:** 42 (fixed for bootstrap and holdout split)
**Infrastructure:** CPU-only; numpy, scipy, pandas — no GPU needed
**Estimated Runtime:** < 5 minutes for all 3 models

**Software Stack:**
```
numpy >= 1.24
scipy >= 1.10
pandas >= 1.5
matplotlib >= 3.6
seaborn >= 0.12
```

### Evaluation

**Primary Metrics:**

| Metric | Definition | Success Threshold (MUST_WORK P1) |
|--------|-----------|----------------------------------|
| DELTA_ECE | ECE(hard) - ECE(easy) per model (M=15) | >= 0.03 in >= 2/3 models |
| CI Lower Bound | Bootstrap 95% CI lower bound of DELTA_ECE | > 0 (CI excludes zero) |
| Models Passing | Count of models with DELTA_ECE >= 0.03 AND CI excludes zero | >= 2 |

**Secondary Metrics:**

| Metric | Definition | Success Threshold (P2) |
|--------|-----------|------------------------|
| Excess ECE (hard) | ECE(hard) - ECE(null_hard) | > 0 for >= 2/3 models |
| Excess ECE (easy) | ECE(easy) - ECE(null_easy) | Excess_hard > Excess_easy |
| Bootstrap p-value | P(DELTA_ECE <= 0) under bootstrap | < 0.05 |

**Temperature Scaling Probe:**

| Metric | Definition | Success Threshold (P3) |
|--------|-----------|------------------------|
| Post-T DELTA_ECE | DELTA_ECE after global T scaling | Still >= 0.03 in >= 2/3 models |
| T* (fitted temperature) | Optimal temperature per model | Reported, not gated |
| ECE reduction | Global ECE reduction after T | Reported as secondary |

**M-Sensitivity:**

| M value | Report | Gate |
|---------|--------|------|
| M=10 | DELTA_ECE, CI | Not gated |
| M=15 | DELTA_ECE, CI | PRIMARY GATE |
| M=20 | DELTA_ECE, CI | Not gated |

**Expected Baseline Performance** (from h-m3 data, pre-experiment estimates):
- ECE(overall, no stratification) from Run 3: llama3-8b=0.4895, codellama-7b=0.5218, deepseek-coder=0.1358
- h-m3 hard vs easy mean_c difference: llama3=0.026, codellama=0.019, deepseek=-0.008
- Note: Small mean_c differences don't preclude larger DELTA_ECE — ECE is bin-weighted, not mean-difference

**Success Criteria:**
```
GATE PASS: DELTA_ECE >= 0.03 AND CI excludes zero in >= 2/3 models
GATE FAIL (null): DELTA_ECE <= 0 in >= 2/3 models → publish as null result
GATE FAIL (collapses): DELTA_ECE < 0.03 everywhere → publish as "below threshold"
```

**Metrics Loading Information:**
- Task Type: binary calibration analysis (P(True) confidence vs. binary correctness)
- Library: numpy, scipy.optimize (custom ECE implementation), matplotlib for visualization
- Code:
```python
# Core ECE: custom numpy (see pseudo-code above)
# Bootstrap CI: np.percentile on boot samples
# Temperature fit: scipy.optimize.minimize_scalar
# Visualization: matplotlib + seaborn
```

### Visualization Requirements

#### Required Figures (Mandatory)

1. **Gate Metrics: DELTA_ECE per Model** — Bar chart with 95% CI error bars, threshold line at 0.03, per model. Clear pass/fail indication.

2. **ECE Calibration Diagrams (Reliability Diagrams)** — Per model × tier (hard/easy): confidence vs. accuracy across 15 bins, diagonal = perfect calibration, actual ECE bar plot.

3. **Temperature Scaling Effect** — Pre vs. post-T DELTA_ECE comparison per model; T* values annotated; persistence check visualization.

#### Additional Figures (LLM Autonomous)

The Phase 4 Coder SHOULD autonomously generate informative figures relevant to the experimental findings. Suggested additional figures:

4. **ECE Null Baseline Comparison** — ECE(tier) vs. ECE(null_tier) grouped bar chart per model per tier; shows excess calibration error above accuracy-mediated baseline.

5. **M-Sensitivity Analysis** — Line plot of DELTA_ECE vs. M ∈ {10, 15, 20} per model; shows stability of finding across bin count choices.

6. **Bootstrap Distribution of DELTA_ECE** — Histogram of 1000 bootstrap DELTA_ECE samples per model; with 95% CI shading; vertical line at 0 and 0.03 thresholds.

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m4/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `DELTA_ECE >= 0.03` AND `CI lower bound > 0` in >= 2/3 model families

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | P(True) confidence scores c ∈ [0,1] exist for all 3 models (h-m3 validated) | TRUE — 5,730 pairs confirmed |
| Mechanism Isolatable | ECE can be computed independently per tier (hard/easy) and compared | TRUE — tier CSV has explicit tier labels |
| Baseline Measurable | Null baseline (constant confidence = tier accuracy) can be computed from same data | TRUE — correctness labels available from h-e1 |

### Architecture Compatibility Check

**This is a computation-only experiment** — no neural network architecture is involved. ECE computation applies to pre-computed scalar confidence values c ∈ [0,1].

**Required inputs (pre-conditions):**
- ✅ c_values per (problem, solution, model): `ptrue_confidence_scores.json` (h-m3 validated)
- ✅ binary correctness labels: `correctness_{model}.json` (h-e1 validated)
- ✅ tier assignments: `tier_assignments.csv` (h-m2 validated, wide-format)
- ✅ n_hard >= 20 AND n_easy >= 20 per model per benchmark (h-e1 validated)

**Incompatible situations:**
- h-m3 confidence scores not generated (gated by h-m3 MUST_WORK PASS — already satisfied)
- Tier assignments corrupt or missing (h-m2 SHOULD_WORK PASS — already satisfied)

> ⚠️ If any input file is missing, Phase 4 MUST fail early with explicit error message!

---

### Mechanism Activation Indicators

**How to detect if ECE computation is actually working:**

| Indicator Type | Expected Signal | Code Location |
|----------------|-----------------|---------------|
| Log Message | "ECE(hard)={value:.4f}, ECE(easy)={value:.4f}, DELTA_ECE={value:.4f}" | evaluate.py:compute_tier_ece() |
| Data Shape | hard_pairs: n >= 68 (min deepseek HE), easy_pairs: n >= 24 (min deepseek HE) | data_loader.py:load_tier_pairs() |
| Metric Delta | DELTA_ECE != 0.0 (non-trivial, not identical) | evaluate.py:compute_delta_ece() |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(ece_hard, ece_easy, delta_ece, n_hard, n_easy, ci_lower, ci_upper):
    """Verify ECE computation mechanism actually activated with real data."""
    indicators = {
        "data_loaded": n_hard >= 20 and n_easy >= 20,
        "ece_computed": ece_hard > 0.0 and ece_easy > 0.0,
        "delta_nontrivial": abs(delta_ece) > 1e-6,  # not identical
        "ci_computed": ci_upper > ci_lower,
        "effect_measured": True  # always measured, gate determines direction
    }
    all_pass = all(indicators.values())
    return all_pass, indicators
```

---

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Input file missing | File not found on load | FAIL EARLY: "h-m3/results/ptrue_confidence_scores.json not found" |
| Empty tier (n=0) | Tier DataFrame is empty after filter | FAIL: "n_{tier}=0 for model {name}" |
| ECE=NaN | All bins empty (extreme confidence values) | WARN: Report model as degenerate, skip from gate count |
| Bootstrap collapse | All 1000 samples identical | WARN: Seed issue; try different seed |
| T-fitting divergence | minimize_scalar fails to converge | WARN: Report T-scaling result as INCONCLUSIVE |

---

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Data loaded | n_hard >= 20 AND n_easy >= 20 per model | Tier split verification |
| ECE computed | ECE(hard) > 0, ECE(easy) > 0 for all models | Numeric check |
| Hypothesis Supported (P1) | DELTA_ECE >= 0.03 AND CI lower > 0 in >= 2 of 3 models | Gate evaluation |
| Temperature robustness (P3) | Post-T DELTA_ECE >= 0.03 in >= 2 of 3 models | Post-T recomputation |

**Hypothesis Support Threshold:** DELTA_ECE >= 0.03 in >= 2/3 models with bootstrap 95% CI excluding zero
**Hypothesis Support Metric:** DELTA_ECE = ECE(hard) - ECE(easy), M=15 bins, 1000-sample bootstrap

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Assessment:** Archon KB (source 8b1c7f40739544a6) contains diffusion model / image generation content and does not have directly relevant LLM calibration literature. All 5 queries returned low-similarity results (<0.42 aggregate similarity) from unrelated domains. No Archon sources are used in the final specification.

**Queries executed:**
- Q1: "ECE calibration temperature scaling LLM" — No relevant results
- Q2: "Expected Calibration Error bin computation bootstrap confidence interval" — No relevant results
- Q3: "difficulty stratification code benchmark calibration" — No relevant results
- Q4 (code): "ECE calibration Python temperature scaling" — No relevant results
- Q5 (code): "bootstrap confidence interval calibration metrics" — No relevant results

### B. GitHub Implementations (Exa)

**Repository 1**: p-lambda/verified_calibration (MIT, Python)
- **URL:** https://github.com/p-lambda/verified_calibration
- **Query Used:** "Expected Calibration Error ECE Python implementation temperature scaling LLM calibration"
- **Relevance:** Bootstrap CI for ECE — exactly what h-m4 needs for confidence intervals on DELTA_ECE
- **Key Pattern:** `cal.get_ece(model_probs, labels)` with Bootstrap resampling
- **Used For:** Bootstrap CI design (pattern adapted into custom numpy implementation)

**Repository 2**: gpleiss/temperature_scaling (1167 stars, MIT, archived)
- **URL:** https://github.com/gpleiss/temperature_scaling
- **Query Used:** "ECE calibration temperature scaling difficulty stratified LLM code verification Python implementation GitHub" (web search)
- **Relevance:** Canonical temperature scaling — minimize NLL on validation set to find T*
- **Key Pattern:** `T* = argmin_T NLL(valid_set, logits/T)`; `softmax(logits/T)` applied at test time
- **Note:** Archived; modern equivalent: dholzmueller/probmetrics
- **Used For:** Temperature scaling probe design (T fitted on 20% holdout, NLL objective)

**Repository 3**: dholzmueller/probmetrics (PyPI: `pip install probmetrics`)
- **URL:** https://github.com/dholzmueller/probmetrics
- **Relevance:** Modern maintained alternative; `'ece-15'` metric, `get_calibrator('temp-scaling')`
- **Used For:** Reference implementation for ECE with M=15 bins (fallback if custom ECE has issues)

**Repository 4**: saurabhgarg1996/calibration (MIT)
- **URL:** https://github.com/saurabhgarg1996/calibration
- **Relevance:** Simple ECE loss; `cal.ece_loss(model_logits, labels)`
- **Used For:** ECE formula validation reference

**Repository 5**: cmu-sei/gce — Generalized Calibration Error (MIT)
- **URL:** https://github.com/cmu-sei/gce
- **Relevance:** Context-specific/stratified calibration — concept basis for tier-stratified ECE
- **Used For:** Conceptual framing of difficulty-stratified ECE as specialized GCE metric

**Repository 6**: johnathan-xie/adaptive-temperature-scaling (Apache-2.0)
- **URL:** https://github.com/johnathan-xie/adaptive-temperature-scaling
- **Relevance:** LLM-specific temperature scaling calibration; evaluated with ECE on HuggingFace models
- **Used For:** Confirming temperature scaling approach is applicable to LLM logprob-based confidence

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results was sufficiently clear. All ECE computation and temperature scaling patterns are standard numpy/scipy operations documented in multiple well-known sources.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Reports for h-m1, h-m2, h-m3

- **h-m3 output files** — Primary data source for h-m4:
  - `h-m3/results/ptrue_confidence_scores.json` — confidence c per (task_id, model)
  - `h-m3/results/ptrue_hm3_verified.json` — gate result with model statistics
  - **Reused because:** Contains the P(True) confidence values that are the input to ECE computation

- **h-m2 output files** — Tier assignment source:
  - `h-m2/results/tier_assignments.csv` — hard/easy/medium assignments (wide-format, 542 rows)
  - **Reused because:** Tier labels are the stratification variable for ECE

- **h-e1/h-m1 output files** — Correctness labels:
  - `h-e1/results/correctness_{model}.json` — binary correctness per (task_id, model)
  - **Reused because:** Binary labels needed for ECE computation (y ∈ {0,1})

- **Why reused:** Enables controlled analysis — only the ECE statistical computation changes, not the underlying data or models. h-m4 is the natural culmination of the h-e1→h-m1→h-m2→h-m3 chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|---------------|-------------|------------------|
| Input data (confidence scores) | Previous hypothesis | h-m3/results/ptrue_confidence_scores.json |
| Input data (tier assignments) | Previous hypothesis | h-m2/results/tier_assignments.csv |
| Input data (correctness labels) | Previous hypothesis | h-e1/results/correctness_{model}.json |
| ECE formula (M=15 bins) | Exa/Literature | Guo et al. 2017; Sources B.1, B.4 |
| Bootstrap CI (1000 samples) | Exa GitHub | p-lambda/verified_calibration (B.1) |
| Temperature scaling (T fitted on holdout) | Exa GitHub | gpleiss/temperature_scaling (B.2) |
| Null baseline (tier accuracy as confidence) | Phase 2B | 02b_verification_plan.md (H-M4 protocol step 3) |
| M-sensitivity {10,15,20} | Phase 2B | 02b_verification_plan.md (H-M4 protocol step 5) |
| Gate threshold DELTA_ECE >= 0.03 | Phase 2A/2B | H-CalibDiff-v1 hypothesis, P1 prediction |
| Tier sizes n_hard, n_easy | Previous hypothesis | h-e1/h-m2 validation results |
| Visualization patterns | Phase 2B | Protocol + Exa ECE blog references |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-18T11:04:22+00:00

### Workflow History for This Hypothesis

- **2026-03-18T11:04:22:** h-m4 set to IN_PROGRESS (External loop starting Phase 2C → 3 → 4 for h-m4)
- **2026-03-18:** Phase 2C experiment design initiated for h-m4

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code — no relevant results found), Exa (GitHub — 6+ repositories), Serena (Code Analysis — skipped, not needed)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
