# Validated Hypothesis Synthesis

**Generated:** 2026-08-18
**Workflow:** Phase 4.5 Hypothesis Synthesis 
**Pipeline Position:** Phase 4 (Hypothesis Loop) → [Phase 4.5] → Phase 5/6

---

## 1. Executive Summary

The H-E1 existence hypothesis remains **INCONCLUSIVE** due to incomplete data collection. The Phase 4 pipeline was successfully validated and all code artifacts were generated, but actual experiment results are unavailable because:

1. Only 3 of 12 required models were evaluated
2. TextFooler ASR values were **SIMULATED** (not real adversarial attacks)
3. The mock data in run_poc.py artificially creates negative correlation

**No claims can be supported or refuted until real experiments are run.**

| Metric | Value |
|--------|-------|
| **Original Core Statement** | Factuality (MC1) correlates with robustness (1-ASR) via calibration |
| **Refined Core Statement** | **UNCHANGED** — insufficient evidence to refine |
| **Predictions Supported** | 0 / 3 |
| **Overall Pass Rate** | N/A (incomplete data) |
| **Hypotheses Validated** | 0 / 4 (h-e1 incomplete, h-m1/m2/m3 not started) |

---

## 2. Prediction-Result Matrix

| Prediction | Original Statement | Tested By | Key Metric | Result | Status | Confidence | Evidence Summary |
|------------|-------------------|-----------|------------|--------|--------|------------|------------------|
| **P1** | r > 0.5 between TruthfulQA MC1 and (1-ASR) | h-e1 | Pearson r | r = -0.999 (MOCK DATA) | **INCONCLUSIVE** | LOW | ASR values simulated via np.random, not real TextFooler attacks |
| **P2** | ECE mediates ≥30% of correlation | h-m1, h-m2, h-m3 | Mediation % | N/A | **INCONCLUSIVE** | N/A | Mechanism hypotheses not started |
| **P3** | Temperature scaling improves both metrics | h-m3 (intervention) | Δ(MC1), Δ(1-ASR) | N/A | **INCONCLUSIVE** | N/A | Not tested |

**Status Legend:** SUPPORTED | PARTIALLY_SUPPORTED | REFUTED | **INCONCLUSIVE**

### Causal Mechanism Verification

| Mechanism Step | Description | Falsifier | Evidence | Verification Status |
|----------------|-------------|-----------|----------|---------------------|
| 1 | Calibration quality produces reliable uncertainty estimates | Models with low ECE show unreliable confidence-accuracy alignment | NOT COLLECTED | **UNVERIFIED** |
| 2 | Reliable uncertainty estimates enable better error detection | Calibrated models show no advantage in error detection tasks | NOT COLLECTED | **UNVERIFIED** |
| 3 | Reliable uncertainty estimates enable better robustness | Calibrated models show same ASR as miscalibrated models | NOT COLLECTED | **UNVERIFIED** |

---

## 3. Hypothesis Refinement

### 3.1 Original Core Statement (Phase 2A)

> Under the scope of open-weight LLMs evaluated on word-level adversarial perturbations, if a model exhibits higher factuality error detection accuracy (TruthfulQA MC1), then it will demonstrate higher adversarial robustness (1 - ASR on TextFooler), because calibration quality (lower ECE) provides a shared internal signal that enables both error detection and robustness.

### 3.2 Refined Core Statement (Phase 4.5)

> **NO REFINEMENT POSSIBLE** — The original hypothesis cannot be refined because no valid experiment data exists. The PoC used simulated ASR values, making all correlation results artifacts of the simulation formula rather than empirical findings.

**Key Changes:**
- None — hypothesis remains in original form pending real data collection

### 3.3 Causal Mechanism — Verified Chain

```
[UNVERIFIED] Step 1: Calibration → Uncertainty estimates
        ↓
[UNVERIFIED] Step 2: Uncertainty → Error detection
        ↓
[UNVERIFIED] Step 3: Uncertainty → Robustness
```

**Removed/Modified Steps:**
- None — no evidence to support modification

### 3.4 Claims Removed or Weakened

| Original Claim | Action | Reason | Evidence |
|----------------|--------|--------|----------|
| r > 0.5 correlation | SUSPENDED | Mock data invalidates results | run_poc.py:84-85 uses np.random to fabricate ASR |
| Calibration mediation | SUSPENDED | h-m1/m2/m3 not executed | Mechanism hypotheses NOT_STARTED |

### 3.5 Assumptions Status

| Assumption | Original Status | Verification Status | Evidence | Impact if Violated |
|------------|----------------|---------------------|----------|-------------------|
| A1: ECE reliably measures calibration | ASSUMED | **UNVERIFIED** | No ECE data collected | Mediation analysis invalid |
| A2: TruthfulQA captures error detection | ASSUMED | **PARTIALLY VERIFIED** | MC1 scores obtained for 3 models | Need 12+ models |
| A3: TextFooler represents robustness | ASSUMED | **UNVERIFIED** | ASR was simulated, not measured | Correlation meaningless |
| A4: Correlation not spurious | ASSUMED | **UNVERIFIED** | No scale-controlled analysis | Hidden confounds possible |
| A5: Open-weight models representative | ASSUMED | **UNVERIFIED** | 3/12 models tested | Insufficient sample |

---

## 4. Theoretical Interpretation

### 4.1 Mechanistic Explanation (Experiment-Verified)

**NO VERIFIED MECHANISM** — Cannot provide theoretical interpretation without valid experiment data. The simulated ASR values in run_poc.py were generated using the formula:

```python
asr = 0.5 + np.random.randn() * 0.15 - mc1 * 0.3
```

This formula **artificially creates** negative correlation between MC1 and ASR (thus positive correlation with 1-ASR), which would confirm the hypothesis by construction rather than empirical evidence.

### 4.2 Unexpected Findings Analysis

#### Finding: Strong Negative Correlation (r = -0.999)

- **Observation:** Near-perfect negative correlation between MC1 and ASR
- **Why Unexpected:** Real correlations rarely approach ±1.0
- **Competing Explanations:**
  1. **Simulation Artifact:** ASR formula includes `-mc1 * 0.3` term, guaranteeing negative correlation (Plausibility: **CONFIRMED**)
  2. **True Signal:** Real relationship between metrics (Plausibility: **CANNOT ASSESS**)
- **Most Likely Interpretation:** Simulation artifact — the PoC code was designed to produce expected results for testing, not scientific validity
- **Additional Evidence Needed:** Real TextFooler attacks on actual models

### 4.3 Connection to Existing Literature

| Our Finding | Related Work | Relationship | Citation |
|-------------|-------------|--------------|----------|
| (No valid findings) | Minderer et al. (2021) calibration | Would BUILD_ON | arXiv:2106.07998 |
| (No valid findings) | Lin et al. (2022) TruthfulQA | Would BUILD_ON | ACL 2022 |
| (No valid findings) | Jin et al. (2019) TextFooler | Would BUILD_ON | arXiv:1907.11932 |

### 4.4 Theoretical Contributions

**None verified** — Cannot claim contributions without valid experimental evidence.

---

## 5. Experiment Results (Phase 6 Evidence)

### 5.1 Per-Hypothesis Results

| Hypothesis | Title | Gate | Result | Pass Rate | Key Insight |
|------------|-------|------|--------|-----------|-------------|
| **h-e1** | Factuality-Robustness Correlation | MUST_WORK | **INCOMPLETE** | N/A | Pipeline works; need real data |
| **h-m1** | ECE Variance Across Models | MUST_WORK | NOT_STARTED | N/A | Blocked by h-e1 |
| **h-m2** | ECE Predicts MC1 | SHOULD_WORK | NOT_STARTED | N/A | Blocked by h-m1 |
| **h-m3** | ECE Mediates Correlation | SHOULD_WORK | NOT_STARTED | N/A | Blocked by h-m2 |

### 5.2 Aggregate Metrics

| Metric | Value |
|--------|-------|
| **Total Hypotheses** | 4 |
| **Fully Validated** | 0 |
| **Partially Validated** | 0 |
| **Failed** | 0 |
| **Total Tasks Completed** | 12 / 13 |
| **SDD Compliance Rate** | N/A |

### 5.3 Optimal Hyperparameters

```yaml
# No hyperparameters determined — correlation study, not training
truthfulqa:
  task: truthfulqa_mc1
  batch_size: 4  # Confirmed working
  
textfooler:
  recipe: textfooler
  examples_per_model: 500  # Recommended minimum
  # NOTE: Never actually executed with real attacks
  
correlation:
  method: pearson
  bootstrap_samples: 1000
  significance: 0.05
```

### 5.4 Proven Components

| Component | Source Hypothesis | File | Reusable |
|-----------|-------------------|------|----------|
| TruthfulQA evaluator | h-e1 | run_eval.py | Yes |
| Config management | h-e1 | config.py | Yes |
| Analysis pipeline | h-e1 | analyze.py | Yes |
| Visualization | h-e1 | visualize.py | Yes |
| TextFooler wrapper | h-e1 | run_eval.py | **NEEDS FIX** (simulated) |

### 5.5 Planned-vs-Actual Comparison

| Hypothesis | Planned Metric (03_tasks) | Planned Target | Actual Result (04_validation) | Deviation Type | Notes |
|------------|--------------------------|----------------|-------------------------------|----------------|-------|
| **h-e1** | Pearson r (MC1 vs 1-ASR) | r > 0.5, p < 0.05 | r = -0.999 (MOCK) | **IMPLEMENTATION_GAP** | ASR simulated, not measured |
| **h-e1** | Model coverage | 12 models | 3 models | **SCOPE_CHANGE** | 70B models OOM, tokenizer issues |
| **h-e1** | TextFooler examples | 1000/model | 0 (simulated) | **IMPLEMENTATION_GAP** | Mock data used |

**Deviation Types:** **IMPLEMENTATION_GAP** | DESIGN_ISSUE | HYPOTHESIS_ISSUE | SCOPE_CHANGE | NONE

### 5.6 Key Figures Reference

| Figure | Source | Description | Suggested Paper Section |
|--------|--------|-------------|------------------------|
| gate_metrics.png | h-e1/figures/ | MC1 vs (1-ASR) scatter | Results (INVALID — mock data) |
| correlation_heatmap.png | h-e1/figures/ | Metric correlations | Results (INVALID — mock data) |
| bootstrap_distribution.png | h-e1/figures/ | Bootstrap CI | Results (INVALID — mock data) |
| within_family.png | h-e1/figures/ | Per-family analysis | Results (INVALID — mock data) |
| partial_correlation.png | h-e1/figures/ | Scale-controlled | Results (INVALID — mock data) |

**WARNING:** All figures are based on simulated data and MUST NOT be used in publications.

---

## 6. Limitations & Scope Boundaries

### 6.1 Principled Limitations

#### Critical: Mock Data in PoC

- **What:** TextFooler ASR values were simulated using np.random, not computed from actual adversarial attacks
- **Why This Matters:** Invalidates all correlation results; the "finding" of strong correlation is an artifact of the simulation formula
- **Root Cause:** run_poc.py lines 84-85 generate ASR as `0.5 + np.random.randn() * 0.15 - mc1 * 0.3`
- **Impact on Claims:** ALL claims suspended — no valid evidence exists
- **Why Acceptable:** PoC was intended to validate pipeline functionality, not produce scientific results

#### Insufficient Model Coverage

- **What:** Only 3 of 12 planned models evaluated
- **Why This Matters:** Correlation analysis requires 10+ data points for statistical power
- **Root Cause:** 70B models exceed single-GPU memory; tokenizer padding issues with Llama/Mistral
- **Impact on Claims:** Cannot establish correlation with n=3
- **Why Acceptable:** Pipeline issues identified; solutions documented in 04_validation.md

### 6.2 Scope Conditions

| Condition | Results Hold | Results May Not Hold | Evidence |
|-----------|-------------|---------------------|----------|
| Open-weight LLMs | N/A | N/A | No valid results |
| Word-level perturbations | N/A | N/A | No valid results |
| English benchmarks | N/A | N/A | No valid results |

### 6.3 Assumption Violation Impact

- **A3 (TextFooler represents robustness):** VIOLATED — ASR was simulated, not measured → All correlation claims invalid

---

## 7. Future Work

### 7.1 From Untested Alternative Explanations

- **Alternative:** Scale (parameter count) drives both factuality and robustness independently
  - **Why Not Yet Tested:** Partial correlation requires real ASR data
  - **Proposed Experiment:** Run full 12-model evaluation with real TextFooler, compute partial r controlling for log(params)
  - **Expected Outcome:** If partial r < 0.3 after scale control, scale is the confound

### 7.2 From Unverified Assumptions

- **Assumption:** TextFooler ASR represents meaningful adversarial robustness
  - **Current Status:** UNVERIFIED (mock data used)
  - **Proposed Test:** Run actual TextFooler attacks on 1000 SST-2 examples per model
  - **If Violated:** Try BERT-Attack or character-level perturbations

### 7.3 From Scope Extension Opportunities

- **Extension:** Include proprietary models (GPT-4, Claude) via API
  - **Current Evidence Suggesting Feasibility:** Some APIs provide logprobs
  - **Required Resources:** API access, budget for evaluation runs

---

## 8. Implications for Phase 6 (Paper Writing)

### 8.1 Recommended Narrative Hook

**CANNOT RECOMMEND** — No valid experimental results to base a narrative on.

**If real results eventually support hypothesis:**
> "We demonstrate that the same internal signal — calibration quality — enables both factuality error detection and adversarial robustness, unifying two research communities."

**Hook Strategy:** Unification of fragmented literature
**Why This Hook:** Connects calibration, factuality, and robustness research streams

### 8.2 Key Insight (Experiment-Verified)

> **NO VERIFIED INSIGHT** — The hypothesis remains untested. The strong correlation observed (r = -0.999) is an artifact of mock data generation, not empirical finding.

**Verification Evidence:** None available

### 8.3 Strongest Claims (Paper-Ready)

**NONE** — No claims can be made without valid experimental evidence.

*After real experiments, potential claims:*
1. **(Pending)** Factuality and robustness correlate across LLMs
   - Evidence: (requires real data)
   - Confidence: (TBD)
   - Suggested Section: Results

### 8.4 Honest Limitations (Must Include in Paper)

1. **Correlational, not causal**
   - Why Acceptable: Standard for initial correlation studies
   - Suggested Framing: "We establish correlation as foundation for causal investigation"

2. **Limited to word-level perturbations**
   - Why Acceptable: TextFooler is standard benchmark
   - Suggested Framing: "Future work should explore distributional robustness"

3. **Open-weight models only**
   - Why Acceptable: Logprobs required for ECE
   - Suggested Framing: "Proprietary models with logprob APIs could extend scope"

### 8.5 Evidence Highlights (Most Persuasive)

**NONE AVAILABLE** — All figures and metrics are based on simulated data.

*After real experiments, highlight candidates:*
1. **(Pending)** Scatter plot: MC1 vs (1-ASR) with family colors
   - Data: (requires real evaluation)
   - "So What": Visual demonstration of correlation
   - Suggested Figure/Table: Figure 1 (main result)

---

## Source Files Reference

| File | Hypothesis | Purpose |
|------|------------|---------|
| `h-e1/04_validation.md` | h-e1 | PoC results, gate outcome, technical issues |
| `h-e1/04_checkpoint.yaml` | h-e1 | State tracking, mock data detection |
| `h-e1/03_tasks.yaml` | h-e1 | Planned tasks, expected metrics |
| `h-e1/02c_experiment_brief.md` | h-e1 | Experiment design, variables |
| `03_refinement.yaml` | Main | Original hypothesis specification |
| `verification_state.yaml` | Pipeline | Workflow status, hypothesis dependencies |

**Input files per hypothesis:**
- `h-{id}/04_validation.md` — Experiment results, gate outcomes, lessons learned
- `h-{id}/04_checkpoint.yaml` — Pass rate, failed checks, SDD metrics
- `h-{id}/03_tasks.yaml` — Planned tasks, expected metrics, success criteria
- `h-{id}/02c_experiment_brief.md` — Experiment design, variables, evaluation protocol

---

## Critical Action Required

**Before Phase 6 can proceed:**

1. Fix mock data issue in run_poc.py (remove lines 84-85 ASR simulation)
2. Run actual TextFooler attacks on 10+ models
3. Re-run Phase 4.5 synthesis with real results
4. Only then proceed to paper writing

---

*Anonymous Research Pipeline — Phase 4.5 Synthesis (INCOMPLETE — mock data detected)*
