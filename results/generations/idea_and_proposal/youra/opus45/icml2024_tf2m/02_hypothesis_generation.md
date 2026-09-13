# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-TARD-NC-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under the condition of trained neural network weights with computable Fisher information, if we apply task-aware rate-distortion optimization with Fisher-weighted distortion metrics, then we can establish fundamental compression limits tighter than MSE-based bounds, because task-relevant parameters (high Fisher information) require higher bit allocation while task-irrelevant parameters can be aggressively compressed.

**Alternative Hypothesis (H0):**
Task-aware Fisher-weighted distortion provides no improvement over standard MSE-based distortion metrics for neural network compression bounds; the additional computational cost of Fisher information does not yield actionable improvements in rate-distortion tradeoffs.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Compression Rate (R) | Independent | Bits per parameter (bpp) allocated to model weights | 1-8 bpp (practical range for quantization) |
| Task Distortion (D_task) | Dependent | Accuracy degradation measured as Δ accuracy from uncompressed baseline on held-out test set | 0-10% accuracy drop |
| Fisher Information Weights (F_ii) | Controlled | Diagonal Fisher information computed via gradient outer products on training data | Normalized to [0,1] per layer |
| Weight Distribution (p_w) | Controlled | Empirical distribution or mixture of Gaussians fit to layer weights | Layer-specific, typically Gaussian-like with long tails |
| Architecture Type | Controlled | MLP, CNN, or Transformer with specified depth and width | Fixed per experiment |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Weight Entropy Estimation
    ↓ (establishes information content)
Step 2: Fisher-Weighted Distortion Metric
    ↓ (captures task relevance)
Step 3: R-D Optimization with D_task
    ↓ (yields optimal allocation)
Outcome: Fundamental Compression Limits + Optimality Certificates
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Gao et al. 2019 (ICML) | R-D lower bound exists for model compression; optimal for single-layer ReLU | Strong |
| Step 1 → Step 2 | Radio (Young 2025) | R-D theory validated at LLM scale (100B+ params) | Strong |
| Step 2 → Step 3 | Xie et al. 2025 (TAIR) | Task-aware information ratio improves KD by +7.3pp accuracy | Strong |
| Step 2 → Step 3 | Fisher information theory | Standard importance measure in natural gradient optimization | Strong |
| Step 3 → Outcome | Lei et al. 2025 | Lattice coding achieves R-D-P optimality with shared randomness | Strong |
| Step 3 → Outcome | Shannon 1959 | R(D) function is the fundamental limit for lossy compression | Foundational |

**Key Tension:**
- **Tension:** Gao 2019 proves R-D bounds for single-layer ReLU networks, but real networks are deep and structured. Radio 2025 validates at scale but uses scalar quantization, not the full Fisher-weighted framework.
- **Resolution:** This verification plan will test whether Fisher-weighted D_task provides tighter bounds than scalar R-D across multiple architectures (MLP, CNN, Transformer) to determine if the task-aware extension adds value beyond existing approaches.

### 1.4 Key Assumptions

1. **Weight Distribution Estimability**
   - Assumption: Weight distributions can be estimated empirically or via mixture models with sufficient accuracy for R-D computation
   - Evidence: Standard practice in compression literature; mixture models capture heavy tails
   - Consequence if violated: R-D bounds become unreliable; framework requires better distribution modeling

2. **Fisher Information Tractability**
   - Assumption: Fisher information is computationally tractable via diagonal approximation (or KFAC) without losing critical task-relevance information
   - Evidence: Diagonal Fisher widely used in natural gradient methods; KFAC captures layer-wise correlations
   - Consequence if violated: Computational cost exceeds compression benefit; need more efficient approximations

3. **R-D Extension Validity**
   - Assumption: Rate-distortion theory extends to structured (non-i.i.d.) weight matrices with acceptable bound looseness
   - Evidence: Radio (Young 2025) validates at 100B+ params; Gao 2019 proves for ReLU networks
   - Consequence if violated: Bounds too loose (>10x) to provide actionable guidance; need structured R-D theory

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Neural networks with differentiable architectures (MLP, CNN, Transformer)
- Post-training compression scenarios (weights are fixed)
- Any compression method: quantization, pruning, or knowledge distillation
- Models with well-defined Fisher information (gradient-based training)

**Where Hypothesis Does NOT Apply:**
- Models without gradients (e.g., symbolic AI, decision trees)
- Training-time compression (dynamic weights)
- Non-differentiable components (hard attention, discrete operations)
- Extremely sparse models where Fisher is degenerate

**Known Limitations:**
- Diagonal Fisher approximation may miss important weight correlations
- Bounds may be loose for highly structured weight matrices (e.g., convolutional filters)
- Computational overhead of Fisher estimation may limit practical applicability for very large models

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (TARD Bounds vs MSE Bounds):**
TARD bounds with Fisher-weighted distortion will be at least 15% tighter than MSE-based R-D bounds for the same target accuracy, as measured by the rate reduction at fixed distortion.

*Measurement*:
- Compute R(D_MSE) and R(D_task) for identical models and accuracy targets
- Rate improvement = (R(D_MSE) - R(D_task)) / R(D_MSE) × 100%
- Statistical test: Paired comparison across 5+ architectures, p < 0.05

*Basis*:
Fisher weighting prioritizes task-critical parameters, reducing "wasted" bits on irrelevant weights. Similar task-aware approaches (Xie 2025 TAIR) show +7.3pp improvement in KD.

*Success Criteria for Phase 2B*:
- Primary: Rate improvement ≥ 15% (p < 0.05)
- Falsification: Rate improvement < 5% triggers hypothesis revision

**Secondary Predictions:**

**P2 (Layer-Specific Allocation Improvement):**
Optimized layer-specific rate allocation via reverse water-filling will improve compression efficiency by 10-20% compared to uniform bit allocation across layers.

**P3 (Optimality Gap Actionability):**
The optimality gap metric (Current Rate - TARD Bound) / TARD Bound will correctly identify which compression methods have improvement potential (gap > 20%) vs. near-optimal methods (gap < 10%).

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure**: TARD bounds show < 5% improvement over MSE bounds across all tested architectures

2. **Mechanism Failure**: Fisher-weighted distortion does NOT correlate with actual task performance degradation (r < 0.5 between predicted and actual accuracy drop)

3. **Actionability Failure**: Optimality gap metric fails to distinguish improvable from near-optimal methods (AUC < 0.6 for gap vs. improvement classification)

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

*Not applicable - This is a theoretical framework hypothesis, not a performance comparison.*

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Architectures: 5 (MLP, CNN, ResNet, ViT, GPT-2 small)
- Compression methods per architecture: 3 (quantization, pruning, KD)
- Runs per configuration: 5 (different random seeds)
- Total experiments: 75 configurations

**Test Specification:**
- Method: Paired t-test for P1 (TARD vs MSE bounds on same model)
- Significance level: α = 0.05 (two-tailed)
- Effect size target: Cohen's d > 0.8 (large effect)
- Report format: Mean improvement ± std, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Do fundamental rate-distortion limits exist for neural network compression with task-aware distortion metrics?"
- Maps to: Primary prediction P1
- Verification type: Theoretical derivation + empirical validation
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the Fisher-weighted distortion metric the key mechanism enabling tighter compression bounds?"
- Maps to: Causal mechanism (3 sub-hypotheses: H-M1 entropy, H-M2 Fisher weighting, H-M3 R-D optimization)
- Verification type: Ablation studies and correlation analysis
- Critical: Determines explanatory power
- **Note:** Phase 2B will decompose into 3 sub-hypotheses (H-M1, H-M2, H-M3)

**SH3 (Comparison):**
"Does TARD-NC provide actionable improvement over existing MSE-based compression analysis?"
- Maps to: Secondary predictions P2, P3
- Verification type: Comparative empirical evaluation
- Critical: Determines practical value

**Total sub-hypotheses in Phase 2B:** 2 + 3 = 5 (SH1 + 3×SH2 + SH3)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned (H-TARD-NC-v1)
- [x] Confidence level specified (0.82)
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=3 steps, evidence_for_links table)
- [x] Causal chain length (N=3) determined and stored
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (P1 primary, P2/P3 secondary)
- [x] Falsification criteria are defined
- [x] Baselines are identified for comparison
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Resource Requirements:** What is the computational overhead of Fisher information estimation at scale? Is diagonal approximation sufficient or is KFAC necessary?

2. **Data Availability:** Which pretrained models and datasets should be used for validation? Recommendation: ImageNet-pretrained ResNet/ViT, WikiText-pretrained GPT-2

3. **Priority Verification Order:** Should SH1 (existence) be proven theoretically first, or validated empirically alongside SH2 (mechanism)?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (YOLO Mode)*
*2026-02-12*
