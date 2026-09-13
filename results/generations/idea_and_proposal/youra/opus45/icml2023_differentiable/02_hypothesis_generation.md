# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-OT-UNI-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under conditions where a model requires heterogeneous discrete operations (categorical selection, sorting, top-k), if discrete operations are encoded as parameterized optimal transport problems with learnable cost matrices C(θ), then a single unified layer can recover the behavior of operation-specific implementations (Gumbel-Softmax, Sinkhorn, top-k selection) while enabling differentiable operation-type selection, because optimal transport provides a universal mathematical framework where these operations emerge as special cases of constrained matching with different cost structures.

**Alternative Hypothesis (H0):**
There is no unified mathematical framework that can subsume categorical selection, sorting, and top-k operations; each discrete operation requires fundamentally incompatible relaxation mechanisms that cannot be parameterized within a single differentiable operator.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Operation type embedding (θ) | Independent | Continuous vector encoding operation type | θ ∈ ℝ^d, d=16-64 |
| Cost matrix parameters | Independent | Learnable parameters controlling C(θ) structure | C ∈ ℝ^{n×n}, sparse patterns |
| Regularization strength (ε) | Independent | Per-operation entropic regularization | ε ∈ [0.01, 1.0] |
| Relaxed output (P) | Dependent | Soft assignment matrix from Sinkhorn | P ∈ [0,1]^{n×n}, rows/cols sum to 1 |
| Gradient quality | Dependent | Gradient SNR, bias/variance | SNR > 1.0, variance < baseline |
| Downstream performance | Dependent | Task-specific accuracy/loss | Comparable to baselines |
| Temperature schedule | Controlled | Annealing schedule | τ: 1.0 → 0.1 |
| Sinkhorn iterations | Controlled | Number of normalization iterations | K = 10-50 |
| Input scale (n) | Controlled | Size of input tensors | n = 10-1024 |

### 1.3 Causal Mechanism

```
[Cost matrix parameterization C(θ)]
    → [Operation-specific constraint structure]
    → [Sinkhorn-relaxed soft assignment]
    → [Gradient flow to operation selection]
```

**Step 1:** Cost matrix parameterization C(θ) encodes operation type through structure:
- Diagonal structure → categorical selection (softmax-like)
- Anti-diagonal structure → sorting/permutation (Sinkhorn)
- Block-sparse structure → top-k selection

**Step 2:** Operation-specific structure enables Sinkhorn relaxation:
- Entropic regularization εH(P) provides differentiable approximation

**Step 3:** Sinkhorn output + Gumbel noise enables gradient flow:
- Soft assignment matrix P is differentiable
- Gumbel reparameterization enables backprop through operation selection

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Gumbel-Sinkhorn (Mena 2018) | Doubly-stochastic constraints recover permutations | Strong |
| Step2 → Step3 | Diff. Sorting Networks (Petersen 2021) | Relaxed operations enable stable training | Strong |
| Step3 → Outcome | Gumbel-Softmax (Jang 2016) | Efficient gradient estimation for discrete choices | Strong |

**Key Tension:**
- **Tension:** Gumbel-Sinkhorn uses fixed operation type (permutation only), while OT-UNI proposes learnable operation types. The question is whether operation-type gradients have acceptable variance.
- **Resolution:** This verification plan tests gradient variance across operation types to determine if end-to-end operation learning is feasible.

### 1.4 Key Assumptions

| # | Assumption | Evidence | If Violated |
|---|------------|----------|-------------|
| A1 | OT subsumes categorical, sorting, top-k as special cases | Gumbel-Sinkhorn (310 citations) | Unification claim fails |
| A2 | Operation embedding space has meaningful structure | Fuzzy Boolean (Liu 2024) | Cannot learn which operation to use |
| A3 | Sinkhorn converges with learnable ε | Standard OT practice | Training instability |
| A4 | Gradient variance through op-selection is trainable | Gumbel-Softmax | End-to-end learning fails |

### 1.5 Scope & Boundaries

**Applies to:**
- ✅ Categorical selection (argmax → softmax relaxation)
- ✅ Sorting and ranking operations
- ✅ Top-k selection with variable k
- ✅ Models requiring multiple discrete operation types

**Does NOT apply to:**
- ❌ Boolean operations (AND/OR/NOT)
- ❌ Arbitrary discrete computations (graphs, trees)
- ❌ Very large scale n > 10,000 without O(N) extensions

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Unification Validation):**
OT-UNI layer recovers baseline behaviors with L2 distance < 0.01 for categorical, sorting, and top-k operations.

**Secondary Predictions:**

**P2 (Learnable Operation Type):**
Operation embedding θ clusters by operation type (k-means purity > 0.8) when trained with downstream loss only.

**P3 (Gradient Quality):**
Gradient SNR ≥ 0.5 × baseline; final performance within 5% of specialized implementations.

**Falsification Criteria:**

1. **Unification Failure**: L2 > 0.1 with diagonal cost (cannot recover Gumbel-Softmax)
2. **Mechanism Failure**: Sinkhorn divergence in >10% of cases
3. **Gradient Failure**: Gradient SNR < 0.1 (10× worse than baselines)
4. **Learning Failure**: Operation embedding purity < 0.5

### 1.7 Statistical Verification Design

| Metric | Test | Requirement |
|--------|------|-------------|
| Unification (L2) | One-sample t-test | Mean L2 < 0.01, p < 0.05 |
| Gradient SNR | Paired t-test vs baseline | SNR ratio > 0.5, p < 0.05 |
| Convergence | Proportion test | Divergence rate < 10% |
| Clustering | k-means purity | Purity > 0.8 |

**Sample size:** n ≥ 20 runs per configuration

---

## 4. Phase 2B Readiness

### Decomposition Preview

**Total sub-hypotheses:** 5 (2 + N where N=3)

**SH1 (Existence):**
"Does OT-UNI successfully recover operation-specific implementations as special cases?"
- Verification: Empirical (L2 distance < 0.01)
- Critical: MUST PASS

**SH2 (Mechanism):**
"Is the 3-step causal mechanism the actual cause of successful unification?"

Decomposes into:
- **H-M1:** Cost matrix parameterization encodes operation type correctly
- **H-M2:** Sinkhorn relaxation produces correct soft assignments
- **H-M3:** Gumbel noise enables gradient flow with acceptable variance

**SH3 (Comparison):**
"Does OT-UNI achieve comparable gradient quality and performance vs baselines?"
- Verification: Comparative empirical

### Readiness Checklist

| # | Requirement | Status |
|---|-------------|--------|
| 1 | Hypothesis in standard format | ✅ |
| 2 | Hypothesis ID assigned (H-OT-UNI-v1) | ✅ |
| 3 | Confidence level (0.82) | ✅ |
| 4 | H0 defined | ✅ |
| 5 | Variables operationalized (9) | ✅ |
| 6 | Causal mechanism with evidence (3 steps) | ✅ |
| 7 | Key tension identified | ✅ |
| 8 | Assumptions with consequences (4) | ✅ |
| 9 | Testable predictions (3) | ✅ |
| 10 | Falsification criteria (4) | ✅ |
| 11 | Baselines identified | ✅ |
| 12 | SH1/SH2/SH3 ready | ✅ |

**Overall:** 12/12 PASSED ✅

### Open Questions

1. **Resource Requirements:** ~50-100 GPU-hours for comprehensive validation
2. **Implementation Priority:** SH1 first as gate; if unification fails, reject hypothesis
3. **Scalability Scope:** Test n ∈ {10, 100, 1024} with efficiency benchmarks

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
