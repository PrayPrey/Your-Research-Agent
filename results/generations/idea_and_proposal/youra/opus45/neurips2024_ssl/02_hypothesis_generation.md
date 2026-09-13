# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-CMAD-v1
**Confidence Level:** 0.77

**Main Hypothesis:**
Under standard SSL training conditions (ImageNet-1K, fixed epochs), if auxiliary task difficulty (measured by TDDI) is matched to model capacity (measured by effective parameters), then downstream transfer performance (linear probe accuracy) will be maximized because optimal difficulty forces representation learning in the capacity-utilization sweet spot, avoiding both trivial solutions (too easy) and random guessing (too hard).

**Alternative Hypothesis (H0):**
There is no systematic relationship between TDDI/capacity ratio and downstream transfer performance; SSL task effectiveness is determined by factors independent of difficulty-capacity matching (e.g., purely by augmentation policy or loss function properties).

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Training Dynamics Difficulty Index (TDDI) | Independent | Normalized rate of loss decrease over first 10 epochs: TDDI = (L₀ - L₁₀) / (L₀ × 10) | 0.01 - 0.15 (normalized) |
| Model Capacity | Independent | log(#trainable_params) for encoder backbone | 16-22 (log scale, ~1M-500M params) |
| Linear Probe Accuracy | Dependent | Top-1 accuracy on downstream classification with frozen encoder + linear head | 50-80% (ImageNet) |
| Effective Rank (eRank) | Dependent | eRank(Z) = exp(H(σ)) where σ are normalized singular values of representation matrix Z | 10-500 (higher = better) |
| Dataset | Controlled | Fixed to ImageNet-1K for all experiments | ImageNet-1K |
| Training Budget | Controlled | Fixed epochs across all SSL methods | 100 or 300 epochs |
| Architecture Family | Controlled | Within-family comparisons only | ResNet / ViT |

### 1.3 Causal Mechanism

**Causal Chain (N=3):**

```
Task Difficulty → Training Dynamics (TDDI) → Representation Utilization (eRank) → Downstream Performance
     Step 1              Step 2                       Step 3                          Outcome
```

**Step 1: Task Difficulty → Training Dynamics**
When an SSL task is appropriately difficult relative to model capacity, the model receives meaningful gradient signals throughout training. Tasks that are too easy lead to rapid convergence with trivial solutions; tasks that are too hard lead to noisy gradients and near-random behavior.

**Step 2: Training Dynamics → Representation Utilization**
Meaningful gradient signals force the model to utilize its full representational capacity. This is measurable via effective rank (eRank) of the learned representation matrix.

**Step 3: Representation Utilization → Downstream Performance**
Higher effective rank (better capacity utilization) directly correlates with better downstream linear probe accuracy because more diverse, distributed representations transfer better to novel tasks.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Curriculum Learning + ZPD Theory | Difficulty affects learning signal quality | Medium |
| Step 2 → Step 3 | RankMe (Garrido et al., 2023, ICML) | Effective rank predicts downstream accuracy (R² > 0.8) | Strong |
| Step 3 → Outcome | Shwartz-Ziv & LeCun (2023) + HaoChen & Ma (2022) | Information-theoretic framework; capacity limits structures | Strong |

**Key Tension:**
- **Tension:** Curriculum learning focuses on example-level ordering; our hypothesis focuses on TASK-level difficulty.
- **Resolution:** Test TASK-level effects with example ordering held constant. If task-level effects dominate, hypothesis is supported.

### 1.4 Key Assumptions

1. **Early training dynamics predict final quality**
   - First 10 epochs indicative of final representation quality
   - *Consequence if violated:* TDDI measurement window needs extension

2. **Effective rank correlates with transfer performance**
   - Evidence: RankMe (Garrido et al., 2023)
   - *Consequence if violated:* Need alternative capacity utilization metric

3. **Inverted-U relationship exists**
   - Evidence: ZPD theory from developmental psychology
   - *Consequence if violated:* Simplifies to monotonic "harder/easier is better"

4. **TDDI is comparable across SSL methods**
   - Requires empirical validation
   - *Consequence if violated:* Need method-specific normalization

### 1.5 Scope & Boundaries

**Applies to:**
- Vision SSL methods (SimCLR, MoCo, MAE, DINO, BYOL, SwAV)
- Standard architectures (ResNet-18/50/101, ViT-S/B/L)
- ImageNet-scale datasets

**Does NOT apply to:**
- Language SSL (BERT, GPT)
- Graph SSL
- Multi-modal SSL (CLIP)

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (TDDI-Performance Correlation)**:
TDDI/log(capacity) ratio and downstream linear probe accuracy follow an inverted-U pattern.

*Measurement*: Quadratic regression; negative β₂ coefficient; R² > 0.3
*Success Criteria*: Quadratic fit significantly better than linear (F-test, p < 0.05)

**Secondary Predictions:**

**P2 (Effective Rank Mediator)**:
eRank mediates TDDI → Performance relationship.
*Measurement*: Mediation analysis; Sobel test p < 0.05

**P3 (Capacity Shift)**:
Optimal TDDI shifts higher as model capacity increases.
*Measurement*: TDDI × log(capacity) interaction significant

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:
1. **No Correlation**: |r| < 0.3 between TDDI/capacity and accuracy
2. **No Inverted-U**: Linear fit equally good as quadratic
3. **eRank Not Mediating**: Sobel test p > 0.1
4. **Method Incomparability**: TDDI not comparable across methods

### 1.8 Statistical Verification Design

**Sample Size**: n ≥ 50 (4 methods × 4 architectures × 3+ seeds)
**Primary Test**: Polynomial regression (linear vs quadratic)
**Secondary Test**: Mediation analysis (Baron-Kenny + Sobel)
**Significance**: α = 0.05 with Bonferroni correction

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does the inverted-U relationship between TDDI/capacity ratio and downstream performance exist across SSL methods and architectures?"
- Maps to: Primary prediction P1
- Verification type: Empirical correlation analysis
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the TDDI → eRank → Performance causal chain the actual mechanism?"
- Maps to: Causal mechanism (N=3 steps)
- Will decompose into 3 sub-hypotheses:
  - H-M1: Task difficulty affects training dynamics
  - H-M2: Training dynamics affect representation utilization (eRank)
  - H-M3: Representation utilization predicts downstream performance
- Verification type: Causal/mediation analysis

**SH3 (Comparison):**
"Does TDDI-based task selection outperform random selection or existing heuristics?"
- Maps to: Practical value
- Verification type: Comparative empirical

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-CMAD-v1
- [x] Confidence level specified: 0.77
- [x] Alternative hypothesis (H0) defined
- [x] All variables operationalized
- [x] Causal mechanism with evidence (N=3 steps)
- [x] Causal chain length determined (N=3)
- [x] Key tension identified with resolution
- [x] Assumptions list consequences if violated
- [x] 3 testable predictions (P1 primary)
- [x] 4 falsification criteria defined
- [x] Baselines identified (curriculum learning, self-paced learning)
- [x] SH1, SH2, SH3 defined

### Open Questions

1. **Resource Requirements:** ~50 GPU-days (A100) for full validation; consider using pre-computed vissl checkpoints

2. **Data Availability:** ImageNet-1K accessible; Question: Extract TDDI from existing logs or need fresh runs?

3. **Priority Order:** SH1 → SH2-M3 (RankMe validates this) → SH2-M1/M2 → SH3

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-13*
