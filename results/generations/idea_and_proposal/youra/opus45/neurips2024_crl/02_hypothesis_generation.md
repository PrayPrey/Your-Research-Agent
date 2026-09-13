# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (Round 1 - T-CausalVAE)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-TCausalVAE-v1
**Confidence Level:** 0.78

**Main Hypothesis:**
Under the condition that video data has temporally consistent latent causal structure, if consecutive video frames are processed through a VAE with temporal consistency constraints and explicit DAG learning (NOTEARS-style), then the model will recover identifiable causal representations (measured by SHD < baseline and MCC > 0.7) because temporal ordering provides causal direction asymmetry that substitutes for interventional data.

**Alternative Hypothesis (H0):**
Temporal multi-view structure in video does NOT provide sufficient information for causal representation identifiability; the learned representations will be statistically indistinguishable from standard VAE disentanglement (no causal structure recovery).

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Temporal frame pairs (t, t+1) | Independent | Consecutive video frames sampled at fixed intervals from video datasets (Kinetics, Something-Something) | Frame gap: 1-10 frames |
| Causal graph structure (SHD) | Dependent | Structural Hamming Distance between learned and ground-truth DAG adjacency matrices | 0 (perfect) to d² (worst), target: < baseline |
| Latent variable recovery (MCC) | Dependent | Mean Correlation Coefficient between learned and true latent variables | 0.0-1.0, target: > 0.7 |
| Frame sampling rate | Controlled | Fixed temporal gap between frame pairs | Fixed at 5 frames (tunable) |
| Video domain | Controlled | Dataset source (synthetic vs real) | Synthetic for GT, real for generalization |
| Latent dimensionality (d) | Controlled | Fixed number of latent causal variables | d = 10 (default) |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Temporal Frame Pairs → Shared Latent Structure Detection
    ↓
Step 2: Shared Latent Structure → Temporal Consistency Constraint
    ↓
Step 3: Temporal Consistency + DAG Constraint → Identifiable Causal Representation
    ↓
Outcome: Recovered causal graph (low SHD) + Disentangled latents (high MCC)
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Yao et al. 2023 (ICLR) | Multi-view partial observability enables identifiability via contrastive learning | Strong |
| Step2 → Step3 | Heurtebise 2025 | Multi-view causal discovery without non-Gaussianity requirement | Medium |
| Step3 → Outcome | CausalVAE (Yang 2020) | VAE + causal layer achieves counterfactual generation on CelebA | Strong |

**Key Tension:**
- **Tension:** Yao et al. (2023) uses contrastive learning for multi-view CRL, while T-CausalVAE proposes generative VAE approach.
- **Resolution:** This verification plan tests whether VAE-based approach can match contrastive learning identifiability while adding generative capability.

### 1.4 Key Assumptions

1. **Shared Causal Skeleton:** Consecutive video frames share the same underlying latent causal structure
   - Consequence if violated: Model will learn frame-specific structures, losing identifiability

2. **Independent Observation Noise:** Frame-specific observation noise is independent across frames
   - Consequence if violated: Correlated noise could be mistaken for causal structure

3. **DAG Structure:** Latent causal variables follow a directed acyclic graph structure
   - Consequence if violated: NOTEARS constraint will fail; cyclic structures require different methods

4. **Temporal Causal Direction:** Temporal ordering reflects causal direction (cause precedes effect)
   - Consequence if violated: Learned graph may have reversed edges; SHD will increase

### 1.5 Scope & Boundaries

**Applies to:** Video data with stable causal structure, synthetic video with known GT, temporal sequences with shared latent structure

**Does NOT apply to:** Static images, videos with rapidly changing causal structure, data where causal direction ≠ temporal direction

**Limitations:** Requires GT for quantitative eval, scalability to d>20 untested, DAG constraint computational cost

### 1.6 Testable Predictions

**Primary Prediction (P1 - Causal Structure Recovery):**
T-CausalVAE will achieve significantly lower SHD than single-frame baselines on synthetic video with known GT.
- Success: SHD reduction ≥ 20% vs baseline (p < 0.05)
- Falsification: SHD not significantly different from baseline

**Secondary Predictions:**
- P2: MCC > 0.7 with ground-truth latents, outperforming standard VAE
- P3: Plausible counterfactual video generation (FID < 1.5× reconstruction FID)

**Falsification Criteria:**
1. Primary Failure: SHD(T-CausalVAE) ≥ SHD(baseline)
2. Mechanism Failure: MCC < 0.5
3. Comparative Failure: Significantly worse than Yao 2023 on shared benchmark

### 1.8 Statistical Verification Design

- Effect size: ~0.6 (medium)
- Required runs: n ≥ 25
- Test: Paired t-test, α = 0.05 (one-tailed)
- Datasets: Temporal Causal3DIdent (synthetic), MPI3D (semi-synthetic), Kinetics (real, qualitative)

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does temporal multi-view structure in video enable identification of shared latent causal variables?"
- Maps to: P1 (SHD improvement)
- Critical: MUST PASS

**SH2 (Mechanism):**
"Is temporal consistency + DAG learning the actual cause of improved identifiability?"
- Decomposition: H-M1 (Step1), H-M2 (Step2), H-M3 (Step3)
- Total: 3 sub-hypotheses via ablation studies

**SH3 (Comparison):**
"Does T-CausalVAE match/outperform Yao 2023 while adding generative capability?"
- Maps to: P2, P3

**Total sub-hypotheses in Phase 2B:** 2 + 3 = 5

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-TCausalVAE-v1
- [x] Confidence: 0.78
- [x] H0 defined
- [x] Variables operationalized
- [x] Causal mechanism (N=3) with evidence
- [x] Key tension + resolution
- [x] Assumptions with consequences
- [x] Testable predictions (1 primary, 2 secondary)
- [x] Falsification criteria (3 conditions)
- [x] Baselines identified (CausalVAE, iVAE, Yao 2023)
- [x] SH1/SH2/SH3 clear

### Open Questions

1. **Data:** Does suitable synthetic video dataset with GT causal graphs exist?
2. **Compute:** GPU memory/time requirements for video VAE + DAG constraint?
3. **Order:** Prioritize SH1 first or run ablations (SH2) in parallel?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work (7 sources)

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-13*
