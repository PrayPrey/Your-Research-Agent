# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-SP-DA-MLIP-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under conditions of training on mixed bulk and surface/interface atomic configurations, if universal MLIP architectures (MACE) are augmented with shared-private domain-adaptive representation learning where shared representations are trained with domain adversarial loss and private representations are domain-conditioned, then out-of-distribution energy prediction errors on surfaces and interfaces will decrease by >30% (MAE reduction) compared to baseline MACE, because domain adversarial training forces the shared encoder to learn domain-invariant atomic representations while the private encoder captures domain-specific physics, and gated fusion adaptively combines both for final energy prediction.

**Alternative Hypothesis (H0):**
The shared-private domain-adaptive architecture will NOT improve OOD generalization, either because: (a) domain-invariant atomic features do not exist or are insufficient for accurate energy prediction, (b) domain adversarial training destabilizes the primary energy prediction task, or (c) the computational/architectural overhead negates any representational benefits.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Shared-private split ratio | Independent | Proportion of message passing layers in shared vs private encoders | 30/70, 50/50, 70/30 |
| Domain adversarial weight (λ) | Independent | Gradient reversal layer scaling factor | 0.0 → 1.0 (scheduled) |
| Gating architecture | Independent | Sigmoid vs attention-based fusion mechanism | Binary choice |
| Domain embedding design | Independent | Local atomic environment statistics (coordination, distances, angles) | Feature vector dimension 32-128 |
| Surface/interface energy MAE | Dependent | Mean absolute error on OC20 surface benchmark | Target: <0.7× baseline |
| Bulk energy MAE | Dependent | Mean absolute error on MP bulk structures | Target: <1.03× baseline |
| Force MAE | Dependent | Mean absolute error on forces | Target: <1.05× baseline |
| Domain classifier accuracy | Dependent | Classification accuracy on held-out test | Target: <60% (random = 50%) |
| Base architecture (MACE) | Controlled | Fixed MACE with 128 hidden channels, 2 layers | Fixed |
| Training data | Controlled | Materials Project + OC20, fixed splits | Fixed |
| E(3)-equivariance | Controlled | Preserved via e3nn library | Fixed |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: Mixed bulk/surface training data
   ↓ (Domain adversarial training via GRL)
Step 2: Shared encoder learns domain-invariant atomic features
   ↓ (Domain embedding provides context)
Step 3: Private encoder learns domain-specific corrections
   ↓ (Gated fusion combines representations)
Step 4: Domain-adaptive combined representation
   ↓ (Energy prediction head)
Outcome: Improved surface/interface MAE with maintained bulk accuracy
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Ganin et al. 2016 (DANN) | Gradient reversal forces domain-invariant features | Strong |
| Step 2 → Step 3 | Tang 2024 (GNN+DA) | Domain adaptation works with GNNs | Medium |
| Step 3 → Step 4 | Han 2025 (domain-shift) | Sparse fine-tuning preserves shared representations | Medium |
| Step 4 → Outcome | Focassio 2024 | "Errors correlated to out-of-domain distance" | Strong |

**Key Tension:**
- **Tension:** Deng 2025 identifies "systematic softening" - is it (a) training data bias, (b) architectural limitation, or (c) loss function issue?
- **Resolution:** This hypothesis tests option (a). If hypothesis fails but mechanism tests show domain-invariance is achieved, points to (b) or (c).

### 1.4 Key Assumptions

1. **Domain embeddings computable from local environment statistics**
   - Consequence if violated: Need explicit domain labels → reduces scalability

2. **Domain-invariant features exist for energy prediction**
   - Consequence if violated: Shared encoder learns nothing useful → approach fails

3. **Gating mechanism can learn appropriate combination weights**
   - Consequence if violated: Gating collapses → marginal improvement only

4. **Domain adversarial training doesn't destabilize energy prediction**
   - Consequence if violated: Training instability → hyperparameter sensitivity increases

### 1.5 Scope & Boundaries

**Applies to:** Inorganic crystals, surfaces, interfaces, point defects, systems <500 atoms

**Does NOT apply to:** Organic molecules, amorphous materials, highly disordered systems, reactive dynamics

**Limitations:** Requires surface data in training, heuristic domain embedding, additional hyperparameters, ~1.3-1.5× computational overhead

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Surface Energy MAE vs Baseline MACE)**:
SP-DA-MLIP will achieve surface energy MAE < 0.70× baseline MACE MAE on OC20-IS2RE validation.

*Measurement*: Paired t-test, n ≥ 15 runs (5 seeds × 3 configurations), p < 0.05
*Falsification*: Surface MAE ≥ 0.95× baseline triggers rejection

**Secondary Predictions:**

**P2 (Bulk Maintained)**: Bulk MAE < 1.03× baseline (no catastrophic forgetting)
**P3 (Domain Invariance)**: Domain classifier accuracy decreases from >90% to <60%
**P4 (Representation)**: t-SNE shows domain overlap in shared, separation in private encoder

**Falsification Criteria:**

The hypothesis will be **REJECTED** if ANY occur:
1. Surface MAE ≥ 0.95× baseline
2. Bulk MAE > 1.20× baseline (catastrophic forgetting)
3. Domain classifier accuracy remains >85% (mechanism failure)
4. >50% training runs diverge (instability)

### 1.8 Statistical Verification Design

- **Effect size**: Cohen's d ~0.8 (large)
- **Required runs**: n ≥ 15
- **Test**: Paired t-test, α = 0.05 (one-tailed)
- **Correction**: Bonferroni for 4 predictions (α' = 0.0125)
- **Ablations**: Shared-only, Private-only, No-gating

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does domain-adversarial training on shared MACE encoder achieve domain-invariant representations (classifier accuracy <60%)?"

**SH2 (Mechanism):**
"Is the 4-step causal mechanism the actual cause of surface MAE reduction?"
- Phase 2B decomposes into: H-M1 (GRL→invariance), H-M2 (embedding→specialization), H-M3 (gating→adaptive), H-M4 (combined→prediction)

**SH3 (Comparison):**
"Does SP-DA-MLIP outperform baseline MACE on surfaces while maintaining bulk?"

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-SP-DA-MLIP-v1
- [x] Confidence level: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] Variables operationalized (11 total)
- [x] Causal mechanism with evidence (N=4 steps)
- [x] Key tension identified with resolution
- [x] Assumptions with consequences (4)
- [x] Testable predictions (4, P1 primary)
- [x] Falsification criteria (4 conditions)
- [x] Baselines: MACE-MP-0, CHGNet
- [x] SH1, SH2, SH3 defined

### Open Questions

1. **Data:** Is OC20-IS2RE sufficient or need additional surface datasets?
2. **Implementation:** How to implement GRL in e3nn/MACE without breaking equivariance?
3. **Hyperparameters:** Optimal λ schedule and split ratio? Grid search vs Bayesian optimization?
4. **Overhead:** Is ~1.3-1.5× overhead acceptable? Optimization strategies?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
