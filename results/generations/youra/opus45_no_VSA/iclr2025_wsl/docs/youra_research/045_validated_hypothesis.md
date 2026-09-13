# Validated Hypothesis Synthesis

**Generated:** 2026-08-10
**Workflow:** Phase 4.5 Hypothesis Synthesis
**Pipeline Position:** Phase 4 (Hypothesis Loop) → [Phase 4.5] → Phase 5/6

---

## 1. Executive Summary

The original hypothesis that CV_PR (coefficient of variation of participation ratio) correlates **negatively** with model accuracy has been **decisively falsified**. Experiments on 100 timm pretrained models revealed a strong **positive** correlation (r=+0.6065, p=9.24e-11) — the exact opposite of the predicted direction.

H-E1 (extraction feasibility) passed: CV_PR can be reliably extracted from 100+ models using randomized SVD with 20 seeds. H-E2 (correlation test) failed: the MUST_WORK gate was not satisfied because the correlation direction was wrong. Mechanism hypotheses h-m1 and h-m2 were blocked and not tested.

This synthesis documents a **failed hypothesis that produced a genuine empirical finding**: CV_PR positively correlates with accuracy. The pipeline is routing to Phase 0 for hypothesis reformulation based on this unexpected result.

| Metric | Value |
|--------|-------|
| **Original Core Statement** | CV_PR correlates negatively with accuracy (r < -0.3) |
| **Refined Core Statement** | FALSIFIED: CV_PR shows strong positive correlation (r=+0.61) |
| **Predictions Supported** | 0 / 3 |
| **Overall Pass Rate** | 50% (1/2 hypotheses) |
| **Hypotheses Validated** | 1 / 2 (H-E1 pass, H-E2 fail) |

---

## 2. Prediction-Result Matrix

| Prediction | Original Statement | Tested By | Key Metric | Result | Status | Confidence | Evidence Summary |
|------------|-------------------|-----------|------------|--------|--------|------------|------------------|
| **P1** | CV_PR correlates negatively with accuracy (r < -0.3, p < 0.05) | h-e2 | Pearson r | +0.6065 | REFUTED | HIGH | Strong positive correlation, opposite direction; p=9.24e-11; 95% CI [0.506, 0.703] |
| **P2** | Partial correlation CV_PR-accuracy significant after controlling condition number | Not tested | - | - | INCONCLUSIVE | - | Blocked by P1 failure (prerequisite h-e2) |
| **P3** | Within ResNet family, correlation stronger than cross-family | Not tested | - | - | INCONCLUSIVE | - | Blocked by P1 failure (prerequisite h-e2) |

**Status Legend:** SUPPORTED | PARTIALLY_SUPPORTED | REFUTED | INCONCLUSIVE

### Causal Mechanism Verification

| Mechanism Step | Description | Falsifier | Evidence | Verification Status |
|----------------|-------------|-----------|----------|---------------------|
| 1 | Model training shapes weight matrix spectral properties | Random weights show same patterns | h-e1: CV_PR varies systematically across trained models | VERIFIED |
| 2 | Spectral shape affects randomized SVD convergence rate | CV independent of spectral decay | h-e1: 20-seed CV shows meaningful variance | PARTIALLY_VERIFIED |
| 3 | Flat spectra lead to consistent SVD estimates (low CV) | CV uncorrelated with spectral flatness | **FALSIFIED**: Higher CV associated with HIGHER accuracy | FALSIFIED |
| 4 | Flat spectra indicate smooth loss landscapes enabling better generalization | Flat spectra but poor generalization | **FALSIFIED**: Correlation direction opposite to prediction | FALSIFIED |

---

## 3. Hypothesis Refinement

### 3.1 Original Core Statement (Phase 2A)

> Under pretrained image classification models from timm (n >= 100), if we compute the coefficient of variation (CV) of participation ratio across 20 randomized SVD seeds and aggregate layer-wise metrics via mean, then CV_PR correlates negatively with model accuracy (r < -0.3, p < 0.05), because CV reflects spectral shape — flatter decay enables better generalization.

### 3.2 Refined Core Statement (Phase 4.5)

> **FALSIFIED.** The hypothesis is contradicted by empirical evidence. CV_PR shows a strong **positive** correlation with ImageNet accuracy (r=+0.61, p<1e-10) across 94 matched timm models. The original causal mechanism is invalidated. Alternative interpretations: (1) confounding by model size, (2) higher CV reflects richer representations. Pipeline routed to Phase 0 for reformulation.

**Key Changes:**
- **Direction reversal**: Predicted negative correlation, observed positive
- **Causal mechanism invalidated**: Steps 3-4 falsified
- **Scope unchanged**: Extraction methodology (h-e1) validated; correlation direction wrong

### 3.3 Causal Mechanism — Verified Chain

```
Step 1 [VERIFIED] → Step 2 [PARTIALLY_VERIFIED] → [CHAIN BROKEN] → Step 3 [FALSIFIED] → Step 4 [FALSIFIED]

Note: Chain breaks at Step 3. The assumption that low CV indicates quality is directly contradicted.
```

**Removed/Modified Steps:**
- **Step 3** (Flat spectra → low CV): FALSIFIED — High CV correlated with high accuracy
- **Step 4** (Flat spectra → better generalization): FALSIFIED — The mechanism direction is wrong

### 3.4 Claims Removed or Weakened

| Original Claim | Action | Reason | Evidence |
|----------------|--------|--------|----------|
| CV_PR correlates negatively with accuracy | REMOVED | Opposite direction observed | r=+0.6065 vs predicted <-0.3 |
| Low CV indicates stable spectral properties | REMOVED | High CV associated with better models | Correlation +0.61 |
| CV reflects spectral shape enabling generalization | WEAKENED | May reflect something else (model size?) | Confounding hypothesis |
| CV_PR is a model quality signal | MODIFIED | True, but opposite sign | Strong correlation exists |

### 3.5 Assumptions Status

| Assumption | Original Status | Verification Status | Evidence | Impact if Violated |
|------------|----------------|---------------------|----------|-------------------|
| A1: Randomized SVD variance reflects spectral properties, not noise | Assumed | VERIFIED | CV_PR values are consistent, finite, systematic | Core methodology valid |
| A2: timm models span sufficient diversity | Assumed | VERIFIED | 100+ models, varied architectures and accuracies | Range adequate |
| A3: ImageNet accuracy is valid proxy for generalization | Assumed | UNVERIFIED | Standard assumption, not tested | Results may not transfer |
| A4: Layer-wise mean aggregation preserves signal | Assumed | UNVERIFIED | Not ablated | Better aggregation may exist |
| A5: PR more informative than condition number | Assumed | UNVERIFIED | h-m1 not run | Still unknown |

---

## 4. Theoretical Interpretation

### 4.1 Mechanistic Explanation (Experiment-Verified)

Our experiments demonstrate that CV_PR can be reliably extracted from pretrained image classification models (100% completion, 100 models). The extraction methodology using randomized SVD with 20 seeds produces consistent, finite values in the range [0.0014, 0.0326].

**However**, contrary to our initial expectation that low CV indicates better models, we observed the opposite: higher CV_PR is associated with **higher** accuracy (r=+0.61). This falsifies the proposed causal mechanism that flatter spectra (leading to lower CV) enable better generalization.

We hypothesize that the observed positive correlation may be driven by:
1. **Confounding**: Larger models tend to have both higher accuracy AND more parameter diversity, potentially increasing CV_PR variance
2. **Alternative mechanism**: Higher CV may reflect richer, more diverse feature representations rather than instability

The original mechanistic chain (Steps 1-4) is broken at Step 3.

### 4.2 Unexpected Findings Analysis

#### Finding: Strong Positive Correlation (Opposite Direction)

- **Observation:** Pearson r = +0.6065 (p < 1e-10) between CV_PR and top-1 accuracy
- **Why Unexpected:** Hypothesis predicted r < -0.3 based on theory that flat spectra (low CV) enable generalization
- **Competing Explanations:**
  1. **Confounding by model size:** Larger models have more parameters, higher accuracy, AND potentially more spectral diversity leading to higher CV. (Plausibility: HIGH)
  2. **Richer representations:** Higher CV may indicate diverse feature extraction at different scales, which benefits generalization. This would invert the causal story. (Plausibility: MEDIUM)
  3. **Sample composition bias:** The 100 models selected may not represent a controlled comparison (mixing architectures pools different phenomena). (Plausibility: LOW — 94% match rate, diverse families)
- **Most Likely Interpretation:** Confounding by model size/complexity. Partial correlation controlling for param_count would distinguish.
- **Additional Evidence Needed:** Compute partial correlation CV_PR~accuracy | param_count. If r drops to ~0, confounding is likely. If r remains significant, the mechanism needs reinterpretation.

### 4.3 Connection to Existing Literature

| Our Finding | Related Work | Relationship | Citation |
|-------------|-------------|--------------|----------|
| CV_PR positively correlates with accuracy | Unterthiner et al. 2020 (weight statistics predict accuracy R²>0.98) | CONSISTENT_WITH | [Unterthiner20] |
| Randomized SVD produces consistent PR estimates | Halko et al. 2011 (randomized SVD theory) | BUILDS_ON | [Halko11] |
| Spectral properties relate to model quality | Martin & Mahoney 2019 (spectral analysis of trained NNs) | EXTENDS (opposite direction) | [Martin19] |

### 4.4 Theoretical Contributions

1. **Methodological (Validated):** CV_PR extraction methodology using randomized SVD with 20 seeds is reliable and scalable to 100+ models
2. **Empirical (Negative Result):** The hypothesis that low CV indicates model quality is falsified; if anything, the relationship is inverted
3. **Practical (Phase 0 Input):** The unexpected positive correlation provides a concrete starting point for reformulated hypotheses

---

## 5. Experiment Results (Phase 6 Evidence)

### 5.1 Per-Hypothesis Results

| Hypothesis | Title | Gate | Result | Pass Rate | Key Insight |
|------------|-------|------|--------|-----------|-------------|
| **h-e1** | CV_PR extraction feasibility | MUST_WORK | PASS | 100% | Extraction works: 100/100 models, CV_PR ∈ [0.0014, 0.0326] |
| **h-e2** | CV_PR negative correlation with accuracy | MUST_WORK | FAIL | 0% | Strong POSITIVE correlation (r=+0.61), opposite direction |
| **h-m1** | Partial correlation after controlling κ | SHOULD_WORK | NOT_STARTED | - | Blocked by h-e2 failure |
| **h-m2** | Within-ResNet correlation stronger | SHOULD_WORK | NOT_STARTED | - | Blocked by h-e2 failure |

### 5.2 Aggregate Metrics

| Metric | Value |
|--------|-------|
| **Total Hypotheses** | 4 |
| **Fully Validated** | 1 (h-e1) |
| **Partially Validated** | 0 |
| **Failed** | 1 (h-e2) |
| **Not Started (Blocked)** | 2 (h-m1, h-m2) |
| **Total Tasks Completed** | 15 / 15 |
| **SDD Compliance Rate** | 100% |

### 5.3 Optimal Hyperparameters

```yaml
extraction:
  n_seeds: 20
  svd_rank: 50
  layer_types: [conv2d, linear]
  aggregation: mean_across_layers
statistics:
  cv_pr_mean: 0.0116
  cv_pr_std: 0.0059
  cv_pr_range: [0.0014, 0.0326]
  models_processed: 100
```

### 5.4 Proven Components

| Component | Source Hypothesis | File | Reusable |
|-----------|-------------------|------|----------|
| Randomized SVD extraction | h-e1 | h-e1/code/model.py | YES |
| Participation ratio computation | h-e1 | h-e1/code/model.py | YES |
| CV aggregation pipeline | h-e1 | h-e1/code/extract.py | YES |
| Model matching (timm → accuracy) | h-e2 | h-e2/code/correlate.py | YES |

### 5.5 Planned-vs-Actual Comparison

| Hypothesis | Planned Metric (03_tasks) | Planned Target | Actual Result (04_validation) | Deviation Type | Notes |
|------------|--------------------------|----------------|-------------------------------|----------------|-------|
| **h-e1** | Extraction completion rate | ≥95% | 100% | NONE | Exceeded target |
| **h-e1** | CV_PR finite range | (0, 10) | [0.0014, 0.0326] | NONE | Well within range |
| **h-e2** | Pearson r | < -0.3 | +0.6065 | HYPOTHESIS_ISSUE | **Opposite direction** |
| **h-e2** | p-value | < 0.05 | 9.24e-11 | NONE | Statistically significant |

**Deviation Types:** IMPLEMENTATION_GAP | DESIGN_ISSUE | HYPOTHESIS_ISSUE | SCOPE_CHANGE | NONE

### 5.6 Key Figures Reference

| Figure | Source | Description | Suggested Paper Section |
|--------|--------|-------------|------------------------|
| scatter_cv_pr_vs_accuracy.png | h-e2/figures/ | CV_PR vs top-1 accuracy scatter with regression line | Results (Figure 1) |
| cv_pr_distribution.png | h-e1/figures/ | Histogram of CV_PR values across models | Methods |

---

## 6. Limitations & Scope Boundaries

### 6.1 Principled Limitations

#### Complete Hypothesis Falsification

- **What:** The primary hypothesis (negative CV_PR-accuracy correlation) is empirically falsified
- **Why This Matters:** The entire causal chain (Steps 3-4) is invalidated; mechanism assumptions were wrong
- **Root Cause:** The intuition that "flat spectra → stability → generalization" does not match empirical reality for pretrained models
- **Impact on Claims:** Cannot make ANY claim about CV_PR as a negative quality indicator; must reformulate
- **Why Acceptable:** Negative results are scientifically valuable; the positive correlation finding provides a new direction

#### Confounding Not Controlled

- **What:** Model size (param_count) may confound the CV_PR-accuracy relationship
- **Why This Matters:** If larger models have both higher accuracy AND higher CV, the observed correlation may be spurious
- **Root Cause:** Experiment design did not include partial correlation controlling for param_count
- **Impact on Claims:** Cannot determine if CV_PR has independent predictive value
- **Why Acceptable:** This was a MUST_WORK gate test; confound analysis planned for h-m1 (now blocked)

#### Mechanism Hypotheses Untested

- **What:** h-m1 (partial correlation) and h-m2 (within-family) were not executed
- **Why This Matters:** The mechanism for WHY CV_PR relates to accuracy remains unknown
- **Root Cause:** MUST_WORK failure on h-e2 blocked dependent hypotheses
- **Impact on Claims:** No mechanism validation; only correlation observed
- **Why Acceptable:** Proper gate enforcement — don't waste effort on mechanism when existence fails

### 6.2 Scope Conditions

| Condition | Results Hold | Results May Not Hold | Evidence |
|-----------|-------------|---------------------|----------|
| Architecture type | ResNet, ViT, EfficientNet, ConvNeXt (tested) | Language models, GAN generators | Only image classifiers tested |
| Training dataset | ImageNet-1K pretrained | Other datasets, fine-tuned | All models pretrained on same data |
| Model scale | 1M-300M params | Very small (<1M) or very large (>1B) | Sample concentrated in mid-range |
| Correlation direction | Positive (observed) | Negative (original hypothesis) | h-e2 directly contradicts prediction |

### 6.3 Assumption Violation Impact

- **A1 (SVD variance is signal, not noise):** VERIFIED — no violation, methodology sound
- **A3 (ImageNet accuracy proxy):** UNVERIFIED — results may not transfer to other quality metrics
- **A4 (Mean aggregation optimal):** UNVERIFIED — better aggregation schemes unexplored
- **A5 (PR > condition number):** UNVERIFIED — h-m1 not run, comparison unknown

---

## 7. Future Work

### 7.1 From Untested Alternative Explanations

- **Alternative:** Confounding by model size drives the positive correlation
  - **Why Not Yet Tested:** Experiment design did not include partial correlation
  - **Proposed Experiment:** Compute partial_corr(CV_PR, accuracy | param_count)
  - **Expected Outcome:** If r drops to ~0, confounding confirmed; if r remains significant (|r|>0.3), CV_PR has independent signal

- **Alternative:** Higher CV reflects richer representations
  - **Why Not Yet Tested:** No direct measure of representation diversity
  - **Proposed Experiment:** Correlate CV_PR with representation metrics (e.g., rank, effective dimension)
  - **Expected Outcome:** If CV_PR correlates with representation richness, reframe mechanism

### 7.2 From Unverified Assumptions

- **Assumption:** Layer-wise mean aggregation preserves signal
  - **Current Status:** UNVERIFIED
  - **Proposed Test:** Ablation comparing mean, median, max, weighted-by-size aggregation
  - **If Violated:** Better aggregation may strengthen or weaken observed correlation

- **Assumption:** PR more informative than condition number alone
  - **Current Status:** UNVERIFIED
  - **Proposed Test:** Run h-m1 with reformulated hypothesis (positive correlation)
  - **If Violated:** Simpler metric (κ) may suffice

### 7.3 From Scope Extension Opportunities

- **Extension:** Test reformulated hypothesis with POSITIVE correlation
  - **Current Evidence Suggesting Feasibility:** r=+0.61 is strong effect
  - **Required Resources:** Same code, re-run with updated prediction

- **Extension:** Architecture-stratified analysis
  - **Current Evidence Suggesting Feasibility:** Sample includes multiple families
  - **Required Resources:** Subset analysis per family (ResNet, ViT, etc.)

---

## 8. Implications for Phase 6 (Paper Writing)

### 8.1 Recommended Narrative Hook

**Hook:** "We set out to prove that stable spectral properties indicate model quality — and proved the exact opposite."

**Hook Strategy:** Counterintuitive finding / Honest negative result
**Why This Hook:** The reversal from r<-0.3 to r=+0.61 is striking. Negative results that reveal unexpected phenomena are scientifically valuable and memorable.

### 8.2 Key Insight (Experiment-Verified)

> CV_PR (coefficient of variation of participation ratio) shows a strong positive correlation with model accuracy (r=+0.61, p<1e-10), directly contradicting the hypothesis that spectral stability indicates quality.

**Verification Evidence:** 94 matched timm models, 95% CI [0.506, 0.703] excludes zero and all negative values

### 8.3 Strongest Claims (Paper-Ready)

1. **CV_PR extraction methodology is reliable and scalable**
   - Evidence: 100% completion rate, consistent finite values across 100 models
   - Confidence: HIGH
   - Suggested Section: Methods

2. **CV_PR positively correlates with ImageNet accuracy**
   - Evidence: r=+0.6065, p=9.24e-11, 95% CI [0.506, 0.703]
   - Confidence: HIGH
   - Suggested Section: Results

3. **The "flat spectra → stability → quality" hypothesis is falsified**
   - Evidence: Correlation direction opposite to prediction
   - Confidence: HIGH
   - Suggested Section: Discussion

### 8.4 Honest Limitations (Must Include in Paper)

1. **Confounding by model size not controlled**
   - Why Acceptable: This was existence test; partial correlation is natural follow-up
   - Suggested Framing: "Future work should control for param_count to isolate CV_PR's independent contribution"

2. **Mechanism hypotheses untested**
   - Why Acceptable: Proper gate enforcement; don't validate mechanism when existence fails
   - Suggested Framing: "The causal mechanism remains an open question for reformulated hypotheses"

### 8.5 Evidence Highlights (Most Persuasive)

1. **Strong positive correlation**
   - Data: r=+0.6065, p=9.24e-11, n=94
   - "So What": Effect is in opposite direction, highly significant
   - Suggested Figure/Table: Scatter plot with regression line and confidence band

2. **95% CI excludes original hypothesis**
   - Data: [0.506, 0.703], hypothesis required r<-0.3
   - "So What": Not a borderline miss — complete contradiction
   - Suggested Figure/Table: CI visualization with hypothesis threshold marked

3. **Reliable extraction methodology**
   - Data: 100% completion, CV_PR ∈ [0.001, 0.033]
   - "So What": The metric works; the theory doesn't
   - Suggested Figure/Table: Histogram of CV_PR distribution

---

## Source Files Reference

| File | Hypothesis | Purpose |
|------|------------|---------|
| `h-e1/04_validation.md` | h-e1 | Extraction feasibility results |
| `h-e1/04_checkpoint.yaml` | h-e1 | Pass rate, metrics |
| `h-e1/03_tasks.yaml` | h-e1 | Planned extraction tasks |
| `h-e1/02c_experiment_brief.md` | h-e1 | Experiment design |
| `h-e2/04_validation.md` | h-e2 | Correlation results (FAIL) |
| `h-e2/04_checkpoint.yaml` | h-e2 | Gate outcome |
| `h-e2/02c_experiment_brief.md` | h-e2 | Correlation experiment design |
| `03_refinement.yaml` | Main | Original hypothesis definition |
| `verification_state.yaml` | Pipeline | State tracking |

**Input files per hypothesis:**
- `h-{id}/04_validation.md` — Experiment results, gate outcomes, lessons learned
- `h-{id}/04_checkpoint.yaml` — Pass rate, failed checks, SDD metrics
- `h-{id}/03_tasks.yaml` — Planned tasks, expected metrics, success criteria
- `h-{id}/02c_experiment_brief.md` — Experiment design, variables, evaluation protocol

---

*Anonymous Research Pipeline — Evidence-refined hypothesis with theoretical interpretation*
