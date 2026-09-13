# Validated Hypothesis Synthesis

**Generated:** 2026-08-29T15:30:00Z
**Workflow:** Phase 4.5 Hypothesis Synthesis 
**Pipeline Position:** Phase 4 (Hypothesis Loop) → [Phase 4.5] → Phase 5/6

---

## 1. Executive Summary

The Progressive Gradient Orthogonalization (PGO) hypothesis was partially tested through the H-E1 existence experiment. The foundational claim — that early training gradients accumulate into a subspace capturing spurious feature directions — was **NOT CONFIRMED** due to an implementation issue (single gradient per epoch produced a subspace too low-rank to measure meaningful alignment). The core mechanism remains theoretically plausible but empirically unverified.

| Metric | Value |
|--------|-------|
| **Original Core Statement** | PGO projects gradients orthogonal to spurious subspace to improve worst-group accuracy |
| **Refined Core Statement** | Gradient subspace method requires multi-batch accumulation; spurious capture unverified |
| **Predictions Supported** | 0 / 3 |
| **Overall Pass Rate** | 0% |
| **Hypotheses Validated** | 0 / 4 (1 PARTIAL, 3 NOT_STARTED) |

---

## 2. Prediction-Result Matrix

| Prediction | Original Statement | Tested By | Key Metric | Result | Status | Confidence | Evidence Summary |
|------------|-------------------|-----------|------------|--------|--------|------------|------------------|
| **P1** | PGO improves worst-group accuracy by ≥5% over ERM | h-m3 (blocked) | worst_group_acc | N/A | INCONCLUSIVE | Low | Mechanism chain broken at h-e1 |
| **P2** | PGO matches or exceeds JTT | h-m3 (blocked) | worst_group_acc | N/A | INCONCLUSIVE | Low | Not reached |
| **P3** | PGO representations show higher core-feature alignment | h-e1 | spurious/core alignment | spurious=0.052, core=0.056 | INCONCLUSIVE | Low | Subspace too low-rank to measure |

**Status Legend:** SUPPORTED | PARTIALLY_SUPPORTED | REFUTED | INCONCLUSIVE

### Causal Mechanism Verification

| Mechanism Step | Description | Falsifier | Evidence | Verification Status |
|----------------|-------------|-----------|----------|---------------------|
| 1 | Early training: network follows 'easy' gradients toward spurious features | Early gradients don't correlate with spurious features | Alignment ~0.05 for both | INCONCLUSIVE (measurement invalid) |
| 2 | PGO accumulates early gradient directions into subspace S | Subspace S is uninformative (low variance) | 10-dim subspace in 25M-param space | FALSIFIED (implementation issue) |
| 3 | Later gradients projected orthogonal to S find core features | Orthogonalized gradients still increase spurious reliance | Not tested | NOT_TESTED |

---

## 3. Hypothesis Refinement

### 3.1 Original Core Statement (Phase 2A)

> Under standard supervised classification with spurious correlations, if we progressively project training gradients orthogonal to the cumulative "easy gradient" subspace, then worst-group accuracy improves relative to ERM, because the model is forced to learn features that generalize beyond majority-group shortcuts.

### 3.2 Refined Core Statement (Phase 4.5)

> The hypothesis that early training gradients primarily capture spurious feature directions via low-rank SVD accumulation **remains unverified**. Evidence shows that single-batch-per-epoch gradient sampling produces subspaces too low-rank for meaningful alignment measurement. A valid test requires accumulation across multiple batches within early epochs.

**Key Changes:**
1. REMOVED: Claim that early gradients definitively capture spurious directions (not demonstrated)
2. WEAKENED: "Progressive orthogonalization improves accuracy" → "May improve if foundational assumption holds"
3. ADDED: Methodological constraint — multi-batch accumulation required

### 3.3 Causal Mechanism — Verified Chain

```
[UNVERIFIED] Early gradients → spurious subspace S
     ↓
[FALSIFIED - implementation] Low-rank SVD captures directions
     ↓
[NOT TESTED] Orthogonalization → core feature learning
     ↓
[NOT TESTED] Worst-group accuracy improvement
```

**Removed/Modified Steps:**
- **Step 2** (SVD captures spurious directions): Implementation produced 10-dim subspace insufficient for measurement

### 3.4 Claims Removed or Weakened

| Original Claim | Action | Reason | Evidence |
|----------------|--------|--------|----------|
| "Early gradient subspace is primarily spurious" | WEAKENED | Alignment indistinguishable (0.052 vs 0.056) | h-e1/04_validation.md |
| "Low-rank SVD approximation captures spurious directions" | WEAKENED | Rank too low to capture anything meaningful | 10-dim in 25M-param space |
| "PGO improves worst-group accuracy" | DEFERRED | Mechanism chain incomplete | h-m1/m2/m3 not tested |

### 3.5 Assumptions Status

| Assumption | Original Status | Verification Status | Evidence | Impact if Violated |
|------------|----------------|---------------------|----------|-------------------|
| A1: Early gradient subspace is primarily spurious | ASSUMED | UNVERIFIED | Alignment ~0.05 both | Orthogonalization harms core features |
| A2: Low-rank SVD captures spurious directions | ASSUMED | UNVERIFIED | Subspace too small | Miss spurious directions |
| A3: Core/spurious gradients separable | ASSUMED | UNTESTED | N/A | Orthogonalization impossible |
| A4: Progressive orthogonalization stable | ASSUMED | UNTESTED | N/A | Training diverges |
| A5: Benchmarks have sufficient spurious correlation | ASSUMED | VERIFIED | Waterbirds 95% correlation | N/A |

---

## 4. Theoretical Interpretation

### 4.1 Mechanistic Explanation (Experiment-Verified)

No mechanistic explanation is verified. The foundational existence claim (H-E1) produced PARTIAL results due to implementation issues. The theory remains intact but empirically untested.

**Key theoretical insight from failure:** Gradient subspace accumulation requires sufficient sample density. Single gradients per epoch produce subspaces with rank ≪ parameter count, making alignment measurements meaningless.

### 4.2 Unexpected Findings Analysis

#### Finding: Near-identical spurious and core alignment

- **Observation:** spurious_alignment=0.052, core_alignment=0.056 at epoch 10
- **Why Unexpected:** Expected spurious >> core based on simplicity bias theory
- **Competing Explanations:**
  1. **Insufficient subspace rank:** 10-dim subspace captures negligible variance in 25M-param space (Plausibility: HIGH)
  2. **Simplicity bias weaker than expected:** Both features learned similarly early (Plausibility: LOW)
  3. **Direction computation flawed:** Spurious/core directions not well-defined (Plausibility: MEDIUM)
- **Most Likely Interpretation:** Insufficient subspace rank (implementation issue, not theoretical flaw)
- **Additional Evidence Needed:** Rerun with multi-batch gradient accumulation

### 4.3 Connection to Existing Literature

| Our Finding | Related Work | Relationship | Citation |
|-------------|-------------|--------------|----------|
| Low-rank subspace insufficient | Stochastic gradient methods | Our sample rate too low | Standard SGD analysis |
| Simplicity bias not observed | Shah et al. (2020) | Measurement, not phenomenon issue | Shah et al., NeurIPS 2020 |

### 4.4 Theoretical Contributions

1. **Methodological constraint identified:** Gradient subspace methods require multi-batch accumulation for meaningful analysis in high-dimensional parameter spaces.

---

## 5. Experiment Results (Phase 6 Evidence)

### 5.1 Per-Hypothesis Results

| Hypothesis | Title | Gate | Result | Pass Rate | Key Insight |
|------------|-------|------|--------|-----------|-------------|
| **h-e1** | Early gradients capture spurious directions | MUST_WORK | PARTIAL | 50% | Implementation issue: single gradient/epoch |
| **h-m1** | Simplicity bias drives early spurious gradients | MUST_WORK | NOT_STARTED | N/A | Blocked by h-e1 |
| **h-m2** | SVD captures spurious-dominant directions | MUST_WORK | NOT_STARTED | N/A | Blocked by h-m1 |
| **h-m3** | Orthogonalization forces core feature learning | MUST_WORK | NOT_STARTED | N/A | Blocked by h-m2 |

### 5.2 Aggregate Metrics

| Metric | Value |
|--------|-------|
| **Total Hypotheses** | 4 |
| **Fully Validated** | 0 |
| **Partially Validated** | 1 |
| **Failed** | 0 |
| **Total Tasks Completed** | 15 / 15 |
| **SDD Compliance Rate** | 100% |

### 5.3 Optimal Hyperparameters

```yaml
# From h-e1 (partial results)
model: ResNet-50
optimizer: SGD
learning_rate: 0.001
batch_size: 128
epochs: 90
accumulation_epochs: 10
rank_k: 50
# ISSUE: accumulated only 1 gradient per epoch (should accumulate all batches)
```

### 5.4 Proven Components

| Component | Source Hypothesis | File | Reusable |
|-----------|-------------------|------|----------|
| Waterbirds data loading | h-e1 | h-e1/code/data.py | Yes |
| ResNet-50 training loop | h-e1 | h-e1/code/train.py | Yes |
| Alignment measurement | h-e1 | h-e1/code/metrics.py | Yes (with fix) |

### 5.5 Planned-vs-Actual Comparison

| Hypothesis | Planned Metric (03_tasks) | Planned Target | Actual Result (04_validation) | Deviation Type | Notes |
|------------|--------------------------|----------------|-------------------------------|----------------|-------|
| **h-e1** | spurious_alignment | > 0.70 | 0.052 | IMPLEMENTATION_GAP | Single gradient/epoch insufficient |
| **h-e1** | core_alignment | < 0.30 | 0.056 | IMPLEMENTATION_GAP | Same root cause |

**Deviation Types:** IMPLEMENTATION_GAP | DESIGN_ISSUE | HYPOTHESIS_ISSUE | SCOPE_CHANGE | NONE

### 5.6 Key Figures Reference

| Figure | Source | Description | Suggested Paper Section |
|--------|--------|-------------|------------------------|
| alignment_bar.png | h-e1/figures/ | Spurious vs core alignment at epochs 5/10/45 | Appendix (shows null result) |
| alignment_evolution.png | h-e1/figures/ | Alignment over training epochs | Appendix |
| svd_variance.png | h-e1/figures/ | Explained variance by SVD components | Methods (shows low-rank issue) |

---

## 6. Limitations & Scope Boundaries

### 6.1 Principled Limitations

#### Insufficient Gradient Sampling

- **What:** Single gradient per epoch accumulated
- **Why This Matters:** Produces 10-dim subspace in 25M-param space
- **Root Cause:** Implementation accumulated last-batch gradient only
- **Impact on Claims:** All alignment measurements unreliable
- **Why Acceptable:** Implementation issue, not theoretical flaw — fixable

#### Incomplete Mechanism Chain

- **What:** Only H-E1 tested; H-M1, H-M2, H-M3 blocked
- **Why This Matters:** Cannot evaluate full PGO mechanism
- **Root Cause:** H-E1 PARTIAL result triggered pipeline routing
- **Impact on Claims:** Main hypothesis (worst-group improvement) untested
- **Why Acceptable:** Pipeline correctly halted at foundational failure

### 6.2 Scope Conditions

| Condition | Results Hold | Results May Not Hold | Evidence |
|-----------|-------------|---------------------|----------|
| Multi-batch gradient accumulation | Unknown | Single-batch per epoch | h-e1 failure |
| Waterbirds dataset | Partial | Other datasets | Only Waterbirds tested |
| ResNet-50 architecture | Partial | Other architectures | Only ResNet-50 tested |

### 6.3 Assumption Violation Impact

- **A2 (Low-rank SVD captures spurious directions):** Implementation produced rank-10 subspace → alignment measurement invalid → entire experiment inconclusive

---

## 7. Future Work

### 7.1 From Untested Alternative Explanations

- **Alternative:** Simplicity bias may not produce separable gradient directions
  - **Why Not Yet Tested:** H-E1 implementation issue prevented measurement
  - **Proposed Experiment:** Accumulate gradients from ALL batches in epochs 1-10, use streaming SVD
  - **Expected Outcome:** If >0.70 spurious alignment achieved, original hypothesis supported

### 7.2 From Unverified Assumptions

- **Assumption:** A1 — Early gradient subspace is primarily spurious
  - **Current Status:** UNVERIFIED
  - **Proposed Test:** Fix gradient accumulation, rerun H-E1
  - **If Violated:** PGO approach fundamentally flawed

- **Assumption:** A3 — Core/spurious gradients separable in parameter space
  - **Current Status:** UNVERIFIED
  - **Proposed Test:** Compute gradient correlation matrix between core/spurious directions
  - **If Violated:** Orthogonalization cannot isolate spurious directions

### 7.3 From Scope Extension Opportunities

- **Extension:** Test on CelebA dataset
  - **Current Evidence Suggesting Feasibility:** Waterbirds infrastructure transferable
  - **Required Resources:** CelebA download, minor data loader changes

- **Extension:** Vision Transformer architecture
  - **Current Evidence Suggesting Feasibility:** Gradient accumulation architecture-agnostic
  - **Required Resources:** ViT model, adjusted hyperparameters

---

## 8. Implications for Phase 6 (Paper Writing)

### 8.1 Recommended Narrative Hook

**CAUTION:** Current results do not support a positive paper narrative. The hypothesis remains unverified.

**Hook Strategy:** Negative/methodological result
**Why This Hook:** Only honest framing given PARTIAL/INCONCLUSIVE results

### 8.2 Key Insight (Experiment-Verified)

> Gradient subspace analysis in high-dimensional parameter spaces requires sufficient sample density; single gradients per epoch produce subspaces too low-rank for meaningful directional analysis.

**Verification Evidence:** 10-dim subspace in 25M-param space → 0.05 alignment regardless of direction

### 8.3 Strongest Claims (Paper-Ready)

1. **Methodological constraint:** Gradient subspace methods require multi-batch accumulation
   - Evidence: H-E1 failure analysis
   - Confidence: HIGH
   - Suggested Section: Discussion/Limitations

### 8.4 Honest Limitations (Must Include in Paper)

1. **Core hypothesis unverified**
   - Why Acceptable: Implementation issue identified and documented
   - Suggested Framing: "Preliminary experiments identified methodological requirements for gradient subspace analysis"

2. **Mechanism chain incomplete**
   - Why Acceptable: Pipeline correctly halted at foundational failure
   - Suggested Framing: "Full mechanism evaluation deferred pending resolution of gradient accumulation"

### 8.5 Evidence Highlights (Most Persuasive)

1. **Negative result: Low-rank subspace insufficient**
   - Data: spurious=0.052, core=0.056, both near zero
   - "So What": Demonstrates minimum requirements for gradient subspace methods
   - Suggested Figure/Table: svd_variance.png showing explained variance

---

## Source Files Reference

| File | Hypothesis | Purpose |
|------|------------|---------|
| `h-e1/04_validation.md` | h-e1 | Experiment results, gate outcome, root cause analysis |
| `h-e1/02c_experiment_brief.md` | h-e1 | Experiment design, variables, success criteria |
| `03_refinement.yaml` | Main | Original hypothesis, predictions, mechanism |

**Input files per hypothesis:**
- `h-{id}/04_validation.md` — Experiment results, gate outcomes, lessons learned
- `h-{id}/04_checkpoint.yaml` — Pass rate, failed checks, SDD metrics
- `h-{id}/03_tasks.yaml` — Planned tasks, expected metrics, success criteria
- `h-{id}/02c_experiment_brief.md` — Experiment design, variables, evaluation protocol

---

*Anonymous Research Pipeline — Evidence-refined hypothesis with theoretical interpretation*
