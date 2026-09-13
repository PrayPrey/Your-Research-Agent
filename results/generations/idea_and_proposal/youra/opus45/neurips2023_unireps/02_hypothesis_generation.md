# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-SRAT-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under standard supervised learning conditions with overparameterized networks, if neural networks are trained on the same task with different random initializations, then their learned representations will converge to a common similarity (CKA > 0.8) because SGD noise acts as exploration that guides trajectories into overlapping attractor basins in representation space, where the basin structure is determined by task/data statistics.

**Alternative Hypothesis (H0):**
Representation similarity between independently trained networks is random and unpredictable - there is no systematic convergence to common attractors, and observed similarities are artifacts of architecture constraints or measurement biases rather than task-induced attractor dynamics.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Task/Data Distribution | Independent | Same training dataset (e.g., CIFAR-10, ImageNet) and loss function across training runs | Categorical: vision classification, language modeling, etc. |
| Random Initialization Seed | Independent | Different random seeds for weight initialization | Integer seeds (0-99 for statistical power) |
| Architecture Class | Controlled | Fixed architecture type with specified depth/width | CNN (ResNet-18/50), Transformer (ViT-S/B), MLP |
| Optimizer Configuration | Controlled | SGD with fixed learning rate schedule and momentum | LR: 0.01-0.1, momentum: 0.9 |
| Representation Similarity (CKA) | Dependent | Centered Kernel Alignment on penultimate layer activations | 0.0 - 1.0 (expect > 0.8 for convergence) |
| Convergence Timing | Dependent | Epoch at which pairwise CKA exceeds 0.7 threshold | 10-100 epochs depending on task |
| Attractor Basin Size | Dependent | Variance of final CKA values across 10+ training runs | Low variance indicates strong attractor |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Task/Data Statistics → Loss Landscape Geometry
        ↓
Step 2: Loss Landscape + SGD Noise → Trajectory Convergence
        ↓
Step 3: Trajectory Convergence → Representation Similarity (CKA > 0.8)
        ↓
      OUTCOME: Predictable representation convergence
```

**Step 1: Task/Data → Landscape**
The task and data distribution determine the geometry of the loss landscape, creating specific low-loss regions (attractor basins) that are task-optimal.

**Step 2: Landscape + SGD → Convergence**
SGD noise acts as an exploration mechanism. The stochasticity helps different initialization trajectories find common low-loss basins.

**Step 3: Convergence → Similarity**
When training trajectories converge to the same attractor basin, learned representations become functionally similar (CKA > 0.8).

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Lin et al. 2024 (Star-Shaped Connectivity) | Minima connected via linear paths through common center | Strong |
| Step 2 → Step 3 | Chen et al. 2025 (Global Convergence μP) | SGD under μP enables rich feature learning with global convergence | Strong |
| Step 3 → Outcome | Williams 2024 (CKA=RSA=CCA Equivalence) | CKA reliably measures representation similarity | Medium |

**Key Tension:**
Lin et al. (2024) demonstrates star-shaped connectivity suggesting a single attractor center, but Davari et al. (2023) shows CKA can be manipulated without changing functional behavior.

**Resolution:** Verify CKA-measured convergence corresponds to functional similarity (same predictions on held-out data).

### 1.4 Key Assumptions

1. **CKA Validity:** CKA/RSA distances meaningfully characterize representation space geometry
   - If Violated: Must use alternative metrics (probing accuracy, prediction agreement)

2. **SDE Approximation:** Stochastic dynamical systems approximation valid for typical learning rates
   - If Violated: Attractor dynamics framework breaks down

3. **Architecture Class:** Architecture class captures most architecture-specific attractor effects
   - If Violated: Need architecture-specific attractor models

4. **Overparameterization:** Networks must be sufficiently overparameterized
   - If Violated: Multiple disconnected basins may exist

### 1.5 Scope & Boundaries

**Applies To:**
- Supervised learning tasks (classification, regression)
- Overparameterized deep networks
- Standard architectures: CNNs, Transformers, MLPs
- Standard optimizers: SGD, Adam (typical LR 0.001-0.1)

**Does NOT Apply To:**
- Underparameterized regime
- Extreme hyperparameters (divergent training)
- Novel architectures without characterized symmetries
- Self-supervised/unsupervised learning

**Limitations:**
- Grokking and double descent not explained
- CKA computation O(n²) with batch size

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Convergence Existence):** If two networks of the same architecture are trained on the same task with different seeds, then CKA > 0.8.

*Measurement:* CKA on penultimate layer, n ≥ 45 pairs (10 seeds)
*Success:* Mean CKA > 0.8 (p < 0.05), 95% CI lower bound > 0.75

**Secondary Predictions:**

**P2 (Timing Predictability):** Early-epoch CKA predicts final CKA (r > 0.6)

**P3 (Complexity-Basin Relationship):** Higher task complexity → higher CKA variance

**Falsification Criteria:**

1. **Primary Failure:** Mean CKA < 0.6 across same-architecture same-task pairs
2. **Mechanism Failure:** High CKA but low prediction agreement
3. **Timing Failure:** No correlation between early and final CKA (r < 0.3)

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 45 pairs (10 seeds per configuration)
**Test:** One-sample t-test (H0: μ_CKA ≤ 0.8)
**Power:** 0.8, α = 0.05 (Bonferroni corrected)
**Design:** 3 architectures × 3 datasets × 10 seeds = 90 training runs

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Do neural network representations trained on the same task with different seeds converge to CKA > 0.8?"
- Maps to: Primary prediction P1
- Verification type: Empirical measurement
- Critical: MUST PASS for theory validity

**SH2 (Mechanism):**
"Is the proposed 3-step causal mechanism the actual cause of representation similarity?"
- Maps to: Causal chain (N=3, will decompose to H-M1, H-M2, H-M3)
- Verification type: Causal analysis with ablations
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does SRAT's trajectory-based prediction outperform post-hoc CKA comparison?"
- Maps to: Secondary prediction P2
- Verification type: Comparative empirical
- Critical: Determines practical value

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-SRAT-v1
- [x] Confidence level: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] Variables operationalized
- [x] Causal mechanism with evidence (N=3 steps)
- [x] Key tension identified with resolution
- [x] Assumptions with violation consequences
- [x] 3 testable predictions (P1 primary)
- [x] Falsification criteria defined
- [x] Baselines identified
- [x] SH1, SH2, SH3 clear

### Open Questions

1. **Resource Requirements:** ~200 GPU-hours on A100 for 90 training runs
2. **Dataset Accessibility:** MNIST/CIFAR-10 available; ImageNet requires credentials
3. **Priority Order:** SH1 (existence) first, then SH2 (mechanism)

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
