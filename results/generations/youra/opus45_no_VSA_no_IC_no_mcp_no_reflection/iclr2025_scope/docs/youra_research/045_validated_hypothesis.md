# Validated Hypothesis Synthesis

**Generated:** 2026-08-31
**Workflow:** Phase 4.5 Hypothesis Synthesis 
**Pipeline Position:** Phase 4 (Hypothesis Loop) → [Phase 4.5] → Phase 5/6

---

## 1. Executive Summary

The DG-CAD hypothesis was partially tested through two sub-hypotheses. **h-e1 (EXISTENCE)** validated that Mamba-2 duality equations produce numerically stable SSM parameters from Transformer attention weights. However, **h-m1 (MECHANISM)** failed: duality-initialized parameters showed 2.13% higher reconstruction error than random initialization (p < 0.0001), contradicting the core assumption that duality preserves meaningful attention structure.

The main hypothesis remains **partially supported** at the existence level but **refuted** at the mechanism level. The causal chain breaks at Step 2: while valid parameters are produced, they do not provide a "better starting point" than random initialization for output reconstruction.

| Metric | Value |
|--------|-------|
| **Original Core Statement** | Duality-guided cross-architecture distillation achieves ≤1.5x degradation vs same-arch KD |
| **Refined Core Statement** | Duality equations produce valid SSM params but do not capture attention structure for output alignment |
| **Predictions Supported** | 0 / 3 |
| **Overall Pass Rate** | 50% (1/2 hypotheses) |
| **Hypotheses Validated** | 1 / 2 tested |

---

## 2. Prediction-Result Matrix

| Prediction | Original Statement | Tested By | Key Metric | Result | Status | Confidence | Evidence Summary |
|------------|-------------------|-----------|------------|--------|--------|------------|------------------|
| **P1** | DG-CAD outperforms naive KD by ≥1% on LongBench 8K | h-m3 (blocked) | Accuracy difference | N/A | INCONCLUSIVE | N/A | Blocked by h-m1 failure |
| **P2** | Attention heads with entropy <median convert with <5% error | h-c1 (not started) | Spearman correlation | N/A | INCONCLUSIVE | N/A | Dependent on h-m1 |
| **P3** | Calibration on ≤1K tokens generalizes to 8K with <2x degradation | h-c2 (not started) | Accuracy ratio | N/A | INCONCLUSIVE | N/A | Dependent on h-m2 |

**Status Legend:** SUPPORTED | PARTIALLY_SUPPORTED | REFUTED | INCONCLUSIVE

### Causal Mechanism Verification

| Mechanism Step | Description | Falsifier | Evidence | Verification Status |
|----------------|-------------|-----------|----------|---------------------|
| 1 | Closed-form init derives SSM params from attention using duality equations | Init produces NaN/Inf or divergent magnitudes | h-e1: 100% stable, magnitude ratio 0.11x | ✅ VERIFIED |
| 2 | Layer-wise optimization refines SSM params to minimize reconstruction error | Reconstruction error does not decrease with duality init | h-m1: Duality error 91.45 > random error 89.54 (-2.13%) | ❌ FALSIFIED |
| 3 | Fine-tuning aligns converted model with task distribution | Performance degrades instead of improves | NOT TESTED (blocked by Step 2 failure) | ⏸️ BLOCKED |

---

## 3. Hypothesis Refinement

### 3.1 Original Core Statement (Phase 2A)

> Under standard NLP tasks (classification, QA, summarization), if Transformer attention layers are converted to SSM layers using Mamba-2 duality-inspired closed-form initialization followed by layer-wise optimization, then the resulting sub-quadratic model achieves performance within 1.5x the degradation of same-architecture distillation, because the duality-preserving initialization provides a strong starting point that reduces optimization difficulty and preserves long-context reasoning structure.

### 3.2 Refined Core Statement (Phase 4.5)

> Mamba-2 duality equations can produce numerically stable SSM parameters from Transformer attention weights (validated). However, these parameters do not capture meaningful attention structure in terms of output alignment: duality-initialized SSM produces 2.13% higher reconstruction error than random initialization. The hypothesis that duality provides a "better starting point" for distillation is refuted under the zero-shot output Frobenius norm metric.

**Key Changes:**
- REMOVED: "provides a strong starting point" — directly contradicted by h-m1 results
- REMOVED: "reduces optimization difficulty" — not tested, blocked by mechanism failure
- REMOVED: "preserves long-context reasoning structure" — not tested
- ADDED: Qualification that stability ≠ structure preservation
- ADDED: Explicit metric scope (output Frobenius norm)

### 3.3 Causal Mechanism — Verified Chain

```
Step 1: attention_weights → duality_equations → ssm_params ✅ VERIFIED
        (produces valid, stable parameters)
        
Step 2: ssm_params → forward_pass → reconstruction ❌ FALSIFIED
        (duality params produce WORSE reconstruction than random)
        
Step 3: reconstruction → optimization → task_performance ⏸️ BLOCKED
        (not tested due to Step 2 failure)
```

**Removed/Modified Steps:**
- **Step 2** (Layer-wise optimization reduces error): FALSIFIED — duality init does not provide better starting point

### 3.4 Claims Removed or Weakened

| Original Claim | Action | Reason | Evidence |
|----------------|--------|--------|----------|
| Duality-preserving init provides strong starting point | REFUTED | h-m1: duality error > random error | Cohen's d = -4.56 (large negative effect) |
| Reduces optimization difficulty | UNVERIFIED | Optimization phase never tested | Blocked by mechanism failure |
| Preserves long-context reasoning structure | UNVERIFIED | Long-context tests not executed | h-c2 not started |
| Achieves ≤1.5x degradation vs same-arch KD | UNVERIFIED | End-to-end comparison not run | h-m3 blocked |

### 3.5 Assumptions Status

| Assumption | Original Status | Verification Status | Evidence | Impact if Violated |
|------------|----------------|---------------------|----------|-------------------|
| A1: Mamba-2 duality conditions hold for BERT attention | Assumed | VIOLATED | h-m1: duality init worse than random | Core hypothesis fails |
| A2: Layer-wise conversion preserves gradient flow | Assumed | UNTESTED | Optimization not run | Unknown |
| A3: Calibration on 512-4096 tokens generalizes to 8K+ | Assumed | UNTESTED | h-c2 not started | Unknown |
| A4: 768-dim SSM state sufficient for 768-dim Transformer | Assumed | PARTIALLY_VERIFIED | h-e1: outputs stable at 0.11x magnitude | May need state expansion |
| A5: Attention entropy correlates with conversion difficulty | Assumed | UNTESTED | h-c1 not started | Unknown |

---

## 4. Theoretical Interpretation

### 4.1 Mechanistic Explanation (Experiment-Verified)

The Mamba-2 duality framework establishes theoretical equivalence between linear attention and SSM under specific conditions. Our experiments show:

1. **Duality equations produce valid parameters**: The SVD-based decomposition of QK^T yields stable A matrix (negative eigenvalues), normalized B and C matrices, and reasonable D skip connection (h-e1).

2. **Validity ≠ structure preservation**: Despite producing stable parameters, the duality mapping does not minimize output reconstruction error. The SSM output diverges MORE from attention output when initialized via duality than via random init.

3. **Possible explanation**: The Mamba-2 duality is proven for scalar-times-identity A matrix and 1-semiseparable causal masks. BERT's multi-head attention with learned position embeddings may not satisfy these conditions.

### 4.2 Unexpected Findings Analysis

#### Finding: Duality Initialization Increases Reconstruction Error

- **Observation:** Mean duality error 91.45 vs random error 89.54 (-2.13% improvement, i.e., 2.13% worse)
- **Why Unexpected:** Duality equations should extract meaningful structure; random init has no knowledge of attention
- **Competing Explanations:**
  1. **Metric mismatch:** Frobenius norm on raw outputs may not be the right metric. MOHAWK uses matrix alignment (CB^T vs QK^T), not output alignment. (Plausibility: HIGH)
  2. **Architecture mismatch:** BERT multi-head attention with residual connections differs from SSD assumptions (single-head, scalar A). (Plausibility: HIGH)
  3. **Scale mismatch:** Duality-derived parameters may have correct structure but wrong scale for matching attention outputs. (Plausibility: MEDIUM)
  4. **Implementation flaw:** SVD-based decomposition may not correctly implement Mamba-2 duality equations. (Plausibility: MEDIUM)
- **Most Likely Interpretation:** Combination of metric mismatch (1) and architecture mismatch (2). The duality may still hold for matrix structure but not for output alignment.
- **Additional Evidence Needed:** Run MOHAWK Stage 1 metric (CB^T vs QK^T alignment) instead of output Frobenius norm.

### 4.3 Connection to Existing Literature

| Our Finding | Related Work | Relationship | Citation |
|-------------|-------------|--------------|----------|
| Duality produces stable SSM params | Mamba-2 SSD theory | SUPPORTS theory at existence level | Dao & Gu (2024) arXiv:2405.21060 |
| Output reconstruction error higher | MOHAWK Stage 1 | SUGGESTS different metric needed | Waleffe et al. (2024) arXiv:2408.10189 |
| Multi-head attention ≠ SSD assumptions | Mamba-2 limitations | CONSISTENT with theoretical scope | Dao & Gu (2024) Section 3 |
| Random init competitive | General SSM training | CONSISTENT — Mamba trains from scratch well | Gu & Dao (2023) Mamba paper |

### 4.4 Theoretical Contributions

1. **Negative result with clear boundary:** Mamba-2 duality equations produce stable SSM parameters but do not capture attention structure for output-level reconstruction. This clarifies the scope of the duality theory.

2. **Metric sensitivity:** The choice between output Frobenius norm vs matrix alignment (CB^T vs QK^T) fundamentally affects whether duality shows benefit. Future work should compare these metrics.

3. **Architecture compatibility evidence:** BERT's multi-head attention may not satisfy the scalar-A, 1-semiseparable assumptions required for exact duality.

---

## 5. Experiment Results (Phase 6 Evidence)

### 5.1 Per-Hypothesis Results

| Hypothesis | Title | Gate | Result | Pass Rate | Key Insight |
|------------|-------|------|--------|-----------|-------------|
| **h-e1** | SSM Parameter Validity | MUST_WORK | PASS | 100% | Duality conversion produces valid, stable SSM params (0% NaN/Inf, 0.11x magnitude) |
| **h-m1** | Reconstruction Error Comparison | MUST_WORK | FAIL | 0% | Duality init 2.13% WORSE than random (Cohen's d = -4.56) |
| **h-m2** | Layer-wise Optimization | SHOULD_WORK | NOT_TESTED | N/A | Blocked by h-m1 failure |
| **h-c1** | Entropy-Conversion Correlation | SHOULD_WORK | NOT_TESTED | N/A | Blocked by h-m1 failure |
| **h-c2** | Short-to-Long Generalization | SHOULD_WORK | NOT_TESTED | N/A | Blocked by h-m2 |
| **h-m3** | Fine-Tuning Task Alignment | MUST_WORK | NOT_TESTED | N/A | Blocked by h-m2 |

### 5.2 Aggregate Metrics

| Metric | Value |
|--------|-------|
| **Total Hypotheses** | 6 |
| **Fully Validated** | 1 (h-e1) |
| **Partially Validated** | 0 |
| **Failed** | 1 (h-m1) |
| **Blocked/Not Tested** | 4 |
| **Total Tasks Completed** | ~30 |
| **SDD Compliance Rate** | N/A |

### 5.3 Optimal Hyperparameters

```yaml
# From h-e1 (validated)
d_state: 64  # SSM state dimension
d_model: 768  # Matches BERT hidden size
D_init: 0.1  # Skip connection weight
A_derivation: SVD of QK^T, negative eigenvalues
B_C_normalization: L2 norm to 1.0
sequence_length: 64-512 tokens

# From h-m1 (for reference, not validated)
error_metric: Frobenius norm on outputs  # May need revision
```

### 5.4 Proven Components

| Component | Source Hypothesis | File | Reusable |
|-----------|-------------------|------|----------|
| Duality conversion function | h-e1 | `duality_conversion.py` | Yes (produces stable params) |
| Selective scan reference impl | h-e1 | `selective_scan.py` | Yes |
| Stability validation | h-e1 | `stability_validation.py` | Yes |
| WikiText-103 data loader | h-e1 | `data_loader.py` | Yes |

### 5.5 Planned-vs-Actual Comparison

| Hypothesis | Planned Metric (03_tasks) | Planned Target | Actual Result (04_validation) | Deviation Type | Notes |
|------------|--------------------------|----------------|-------------------------------|----------------|-------|
| **h-e1** | NaN/Inf rate, magnitude ratio | 0%, <10x | 0%, 0.11x | NONE | Met criteria |
| **h-m1** | Reconstruction error reduction | >0% (duality < random) | -2.13% (duality > random) | HYPOTHESIS_ISSUE | Core assumption violated |

**Deviation Types:** IMPLEMENTATION_GAP | DESIGN_ISSUE | HYPOTHESIS_ISSUE | SCOPE_CHANGE | NONE

### 5.6 Key Figures Reference

| Figure | Source | Description | Suggested Paper Section |
|--------|--------|-------------|------------------------|
| gate_metrics.png | h-e1/figures/ | Bar chart of NaN/Inf rate and magnitude ratio | Methods: Stability validation |
| bar_comparison.png | h-m1/figures/ | Duality vs random reconstruction error | Results: Negative finding |
| per_layer_comparison.png | h-m1/figures/ | Per-layer error comparison (all 12 layers worse) | Results: Consistency of failure |
| effect_size_per_layer.png | h-m1/figures/ | Cohen's d per layer (all large negative) | Results: Effect magnitude |

---

## 6. Limitations & Scope Boundaries

### 6.1 Principled Limitations

#### Metric Selection

- **What:** Used output Frobenius norm instead of MOHAWK's matrix alignment (CB^T vs QK^T)
- **Why This Matters:** Different metrics may show different results; MOHAWK explicitly uses matrix alignment
- **Root Cause:** Experiment design interpreted "reconstruction error" as output-level, not matrix-level
- **Impact on Claims:** Results may not transfer to matrix alignment metric
- **Why Acceptable:** Output alignment is a reasonable interpretation of "reconstruction"; future work can test matrix alignment

#### Architecture Scope

- **What:** Tested only BERT-base (encoder-only, 12 layers, 12 heads) → Mamba-12
- **Why This Matters:** Other architectures (decoder-only, larger models) may behave differently
- **Root Cause:** Scope limited for PoC validation
- **Impact on Claims:** Results apply to BERT-style encoders only
- **Why Acceptable:** BERT is standard benchmark; generalization is future work

#### Duality Conditions

- **What:** BERT multi-head attention may not satisfy Mamba-2 SSD conditions (scalar A, 1-semiseparable)
- **Why This Matters:** Duality is only proven under specific conditions
- **Root Cause:** Theoretical limitation of Mamba-2 duality framework
- **Impact on Claims:** Duality may work for architectures that satisfy conditions
- **Why Acceptable:** This identifies the boundary of the approach

### 6.2 Scope Conditions

| Condition | Results Hold | Results May Not Hold | Evidence |
|-----------|-------------|---------------------|----------|
| BERT-base encoder | Yes | GPT-style decoders | Only tested on BERT |
| Output Frobenius norm metric | Yes | Matrix alignment metric | h-m1 used output norm |
| Zero-shot (no optimization) | Yes | After optimization | Only tested init quality |
| WikiText-103 calibration | Yes | Other domains | Single dataset |

### 6.3 Assumption Violation Impact

- **A1 (Duality conditions):** VIOLATED — BERT attention does not satisfy SSD conditions → Core mechanism fails at output alignment level
- **A4 (State dimension):** PARTIALLY_VIOLATED — 64-dim state produced 0.11x magnitude ratio, may be too conservative

---

## 7. Future Work

### 7.1 From Untested Alternative Explanations

- **Alternative:** Use MOHAWK matrix alignment metric (CB^T vs QK^T) instead of output Frobenius norm
  - **Why Not Yet Tested:** Original experiment design used output-level comparison
  - **Proposed Experiment:** Implement MOHAWK Stage 1 loss, rerun h-m1
  - **Expected Outcome:** Duality may show benefit at matrix structure level

- **Alternative:** Test duality after minimal optimization (10-100 steps) instead of zero-shot
  - **Why Not Yet Tested:** h-m1 tested zero-shot initialization quality only
  - **Proposed Experiment:** Run brief optimization, compare convergence speed
  - **Expected Outcome:** Duality init may converge faster even if zero-shot is worse

### 7.2 From Unverified Assumptions

- **Assumption:** A5 — Attention entropy correlates with conversion difficulty
  - **Current Status:** UNVERIFIED (h-c1 not started)
  - **Proposed Test:** Compute per-head entropy, correlate with per-head reconstruction error
  - **If Violated:** Need alternative metrics for predicting conversion quality

- **Assumption:** A3 — Short calibration generalizes to long context
  - **Current Status:** UNVERIFIED (h-c2 not started)
  - **Proposed Test:** Calibrate on ≤1K tokens, evaluate at 4K and 8K
  - **If Violated:** Must include long sequences in calibration

### 7.3 From Scope Extension Opportunities

- **Extension:** Test on decoder-only models (GPT-2, Pythia)
  - **Current Evidence Suggesting Feasibility:** Duality equations architecture-agnostic in theory
  - **Required Resources:** Additional model loading, same experimental setup

- **Extension:** Per-head conversion (preserve multi-head structure)
  - **Current Evidence Suggesting Feasibility:** Current whole-layer conversion loses head structure
  - **Required Resources:** Modify duality_conversion.py to operate per-head

---

## 8. Implications for Phase 6 (Paper Writing)

### 8.1 Recommended Narrative Hook

> "We tested whether Mamba-2's theoretical duality between attention and SSM enables practical knowledge transfer from pretrained Transformers. Our experiments reveal a surprising finding: while duality equations produce numerically stable SSM parameters, they capture less attention structure than random initialization at the output level."

**Hook Strategy:** Lead with negative result as contribution
**Why This Hook:** Negative results with clear methodology are valuable; clarifies scope of Mamba-2 duality for practitioners

### 8.2 Key Insight (Experiment-Verified)

> Numerical stability (no NaN/Inf, bounded magnitude) does not imply structural fidelity: duality-derived SSM parameters are stable but reconstruct attention outputs 2.13% worse than random initialization (p < 0.0001, Cohen's d = -4.56).

**Verification Evidence:** h-e1 (100% stable), h-m1 (all 12 layers show negative effect)

### 8.3 Strongest Claims (Paper-Ready)

1. **Mamba-2 duality equations produce valid SSM parameters from BERT attention weights**
   - Evidence: 100/100 samples stable, 0% NaN/Inf, 0.11x magnitude ratio
   - Confidence: HIGH
   - Suggested Section: Results 4.1

2. **Output reconstruction error is higher for duality init than random init**
   - Evidence: 91.45 vs 89.54 Frobenius norm, p < 0.0001, Cohen's d = -4.56
   - Confidence: HIGH
   - Suggested Section: Results 4.2

3. **Negative effect is consistent across all 12 BERT layers**
   - Evidence: Per-layer Cohen's d ranges from -4.15 to -5.97, all large negative
   - Confidence: HIGH
   - Suggested Section: Results 4.2

### 8.4 Honest Limitations (Must Include in Paper)

1. **Only tested output Frobenius norm, not MOHAWK matrix alignment**
   - Why Acceptable: Output alignment is a reasonable metric; matrix alignment is future work
   - Suggested Framing: "Our results use output-level reconstruction; matrix-level alignment may show different properties"

2. **Zero-shot evaluation only — no optimization**
   - Why Acceptable: Tests initialization quality directly
   - Suggested Framing: "We evaluate initialization quality; convergence speed during optimization is future work"

3. **Single architecture (BERT-base) and dataset (WikiText-103)**
   - Why Acceptable: Standard benchmark; establishes methodology
   - Suggested Framing: "Generalization to other architectures and domains is future work"

### 8.5 Evidence Highlights (Most Persuasive)

1. **100% Stability with 0.11x Magnitude**
   - Data: 100/100 samples, no NaN/Inf, magnitude ratio well under 10x threshold
   - "So What": Duality equations DO produce valid parameters — the issue is structure, not validity
   - Suggested Figure/Table: Bar chart (h-e1/figures/gate_metrics.png)

2. **Consistent Negative Effect Across All Layers**
   - Data: All 12 layers show duality worse than random, Cohen's d = -4.15 to -5.97
   - "So What": Not a fluke — the duality mapping systematically fails at output reconstruction
   - Suggested Figure/Table: Per-layer comparison (h-m1/figures/per_layer_comparison.png)

3. **Large Effect Size with High Significance**
   - Data: p < 0.0001, Cohen's d = -4.56 (large effect)
   - "So What": Result is highly reliable; not due to noise or small sample
   - Suggested Figure/Table: Effect size plot (h-m1/figures/effect_size_per_layer.png)

---

## Source Files Reference

| File | Hypothesis | Purpose |
|------|------------|---------|
| `h-e1/04_validation.md` | h-e1 | Stability validation results |
| `h-e1/02c_experiment_brief.md` | h-e1 | Experiment design |
| `h-m1/04_validation.md` | h-m1 | Reconstruction error comparison |
| `h-m1/02c_experiment_brief.md` | h-m1 | Experiment design |
| `03_refinement.yaml` | Main | Original hypothesis definition |

**Input files per hypothesis:**
- `h-{id}/04_validation.md` — Experiment results, gate outcomes, lessons learned
- `h-{id}/04_checkpoint.yaml` — Pass rate, failed checks, SDD metrics
- `h-{id}/03_tasks.yaml` — Planned tasks, expected metrics, success criteria
- `h-{id}/02c_experiment_brief.md` — Experiment design, variables, evaluation protocol

---

*Anonymous Research Pipeline — Evidence-refined hypothesis with theoretical interpretation*
