# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-TGC-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under resource-constrained ML deployment conditions (limited compute, memory, data), if a unified Trustworthy Gradient Checkpoint (TGC) layer is applied that combines per-sample gradient modulation for privacy (DP clipping), fairness (group reweighting), robustness (adversarial filtering), and calibration (focal loss), then the resulting model will achieve Pareto-superior trade-offs across all four trustworthiness dimensions compared to independent mechanisms, because unified gradient-level processing enables shared resource utilization and eliminates redundant computations across objectives.

**Alternative Hypothesis (H0):**
A unified gradient checkpoint approach provides no significant advantage over independent mechanisms for each trustworthiness dimension. The Pareto frontier achieved by TGC is equivalent to or worse than the frontier achieved by combining separate DP-SGD, fairness reweighting, adversarial training, and temperature scaling mechanisms.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| TGC modulation parameters | Independent | Privacy ε (DP noise scale), fairness λ (group weight), robustness τ (gradient filter threshold), focal γ (calibration focus) | ε: 0.1-10, λ: 0-1, τ: 0.01-0.1, γ: 0-5 |
| Resource constraints | Independent | Compute budget (GPU-hours), memory limit (GB), training data size (samples) | Compute: 1-100 GPU-hrs, Memory: 4-32 GB, Data: 1k-100k samples |
| Trustworthiness Pareto position | Dependent | ε-DP achieved, Demographic Parity Gap, PGD adversarial accuracy, Expected Calibration Error (ECE) | ε: lower better, DPGap: <0.1, PGD: >50%, ECE: <0.1 |
| Total resource consumption | Dependent | Training time (hours), peak GPU memory (GB), total FLOPs | Time: measured, Memory: measured, FLOPs: computed |
| Model architecture | Controlled | Fixed architecture per experiment (ResNet-18 for images, MLP for tabular) | ResNet-18 or 3-layer MLP |
| Training procedure | Controlled | Optimizer, batch size, learning rate schedule, total epochs | SGD, batch=64, cosine LR, 100 epochs |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: TGC Layer Access → Unified Pipeline
        ↓
Step 2: Unified Pipeline → Composed 4D Gradients
        ↓
Step 3: Composed Gradients → Pareto Navigation
        ↓
Step 4: Pareto Navigation → 4D Trustworthy Model
```

**Detailed Mechanism:**

1. **Step 1 (Gradient Access):** TGC layer intercepts per-sample gradients → Initiates unified modulation pipeline
   - *Evidence:* Opacus Fast Gradient Clipping achieves 50% memory reduction
   - *Falsification:* Breaks if per-sample gradients unavailable or memory exceeded

2. **Step 2 (Gradient Composition):** Unified pipeline → Privacy+Fairness+Robustness+Calibration computed in single pass
   - *Evidence:* FedFDP demonstrates fairness-aware gradient clipping under DP
   - *Falsification:* Breaks if operations have destructive interference

3. **Step 3 (Pareto Navigation):** Composed gradients → Smooth Tchebycheff scalarization adaptively weights objectives
   - *Evidence:* Lin et al. (2024) shows lightweight gradient-based Pareto navigation
   - *Falsification:* Breaks if Pareto frontier is non-navigable

4. **Step 4 (Model Update):** Pareto-navigated gradient → Model achieves 4D trustworthiness
   - *Evidence:* TrustFed, FairTrade demonstrate 3-objective Pareto optimization feasibility
   - *Falsification:* Breaks if one objective dominates despite adaptive weighting

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Opacus (PyTorch) | Per-sample gradients accessible with 50% memory savings | Strong |
| Step2 → Step3 | FedFDP, Zhang et al. (2022) | DP clipping composable with fairness; focal loss improves calibration | Strong |
| Step3 → Step4 | Smooth Tchebycheff (Lin 2024) | Gradient-based Pareto navigation with O(1) overhead | Strong |
| Step4 → Outcome | TrustFed, FairTrade | 3-objective Pareto optimization achieves balanced trade-offs | Medium |

**Key Tension:**
- **Tension:** Zhang et al. (2022) shows DP-SGD causes miscalibration due to gradient clipping, yet we propose integrating calibration into the same pipeline.
- **Resolution:** We replace post-hoc temperature scaling with in-training focal loss, which modifies gradients directly.

### 1.4 Key Assumptions

1. **Per-sample gradient availability:** Opacus-style infrastructure provides efficient access.
   - *If violated:* TGC cannot operate; must fall back to batch-level approximations

2. **Gradient operation composability:** Privacy clipping, fairness reweighting, robustness filtering, and focal scaling can be applied sequentially without destructive interference.
   - *If violated:* 4D unification fails; must use independent pipelines

3. **Pareto frontier navigability:** Trade-offs between 4 objectives form a navigable Pareto frontier.
   - *If violated:* Multi-objective optimization degenerates to single-objective dominance

4. **Focal loss calibration effectiveness:** Focal loss improves calibration during training.
   - *If violated:* Must add separate calibration stage, losing unified advantage

### 1.5 Scope & Boundaries

**Applies to:**
- Classification tasks (binary and multi-class)
- Datasets with demographic group annotations
- Moderate-scale training: 1k-100k samples, <100 GPU-hours
- Standard architectures: CNNs for images, MLPs for tabular

**Does NOT apply to:**
- Generative models (GANs, diffusion, LLMs)
- Regression tasks
- Extremely large-scale training (>1M samples)
- Tasks without group structure

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Pareto Hypervolume Improvement):**
TGC will achieve Pareto frontier hypervolume ≥10% larger than baseline of independent mechanisms under equivalent resource constraints.

*Measurement:* Hypervolume over 4D space (ε, DPGap, 1-PGD_acc, ECE), paired t-test, n=5 seeds, p<0.05

*Success Criteria:* Hypervolume(TGC) > 1.1 × Hypervolume(Baseline) with p<0.05

**Secondary Predictions:**

**P2 (Resource Efficiency):**
TGC achieves equivalent 4D trustworthiness while consuming ≤60% of resources required by independent mechanisms.

**P3 (Ablation Validation):**
Removing any single TGC component degrades corresponding metric by >10% while maintaining others within 5%.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure:** Pareto hypervolume(TGC) ≤ Pareto hypervolume(Baseline)
2. **Mechanism Failure:** Ablation shows removing a component does NOT affect corresponding metric
3. **Resource Failure:** TGC requires >120% of baseline resources for equivalent trustworthiness
4. **Interference Failure:** Any single metric degrades >25% compared to independent-mechanism baseline

### 1.7 SOTA Baseline

*Not applicable - Novel framework proposal.*

**Comparison Baselines:**
- Independent mechanisms: Opacus + AIF360 + PGD-AT + Temperature Scaling
- Multi-objective FL: TrustFed, FairTrade, CMOFL

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 5 random seeds per configuration
**Effect Size Target:** Cohen's d ≥ 0.8 (large effect)
**Statistical Power:** 0.8

**Test Specification:**
- Method: Paired t-test (same random seeds)
- Significance level: α = 0.05 (one-tailed)
- Report format: Mean ± Std Dev, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does unified gradient modulation for 4D trustworthiness produce valid Pareto trade-offs under resource constraints?"
- Maps to: Primary prediction (P1)
- Verification type: Empirical
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the proposed 4-step causal chain the actual mechanism producing 4D trustworthiness?"
- Maps to: Causal mechanism (N=4 steps)
- Phase 2B will decompose into 4 sub-hypotheses:
  - H-M1: Per-sample gradient access enables unified processing
  - H-M2: Gradient operations compose without destructive interference
  - H-M3: Smooth Tchebycheff navigates 4D Pareto frontier
  - H-M4: Unified update achieves balanced 4D trustworthiness
- Verification type: Ablation studies

**SH3 (Comparison):**
"Does TGC outperform independent mechanisms on Pareto hypervolume under equivalent resource constraints?"
- Maps to: Secondary predictions (P2, P3)
- Verification type: Comparative empirical

**Total sub-hypotheses in Phase 2B:** 2 + 4 = 6 (SH1 + 4×SH2 + SH3)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-TGC-v1
- [x] Confidence level specified: 0.85
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (4 steps)
- [x] Causal chain length (N=4) determined
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions with primary marked
- [x] Falsification criteria defined
- [x] Baselines identified for comparison
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Resource Requirements:** What is the minimum compute budget required for meaningful Pareto improvement?

2. **Dataset Selection:** Should we prioritize tabular (Adult, COMPAS) or image (CelebA, CIFAR-10) for initial validation?

3. **Ablation Order:** For 4-way ablation, should we run all 4 in parallel or sequential based on expected difficulty?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
