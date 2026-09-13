# Verification Plan: Orbit-PE Cross-Architecture Weight Space Learning

**Date:** 2026-05-20
**Hypothesis ID:** H-OrbitPE-v1
**Confidence:** 0.72
**Total Hypotheses:** 5 (H-E1, H-M1, H-M2, H-M3, H-C1)

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under weight space learning for neural network model property prediction, if sequential positional encodings in SANE's weight tokenizer are replaced with orbit-based positional encodings (orbit-PE) derived from the input/output channel permutation group (architecture-agnostic linear-operator symmetry), then cross-architecture zero-shot τ_retention in CNN→Transformer model property prediction will reach ≥70% (vs <50% for vanilla SANE), because permutation-orbit structure is the dominant transferable symmetry component across neural architecture families — more than 60% of checkpoint variation in weight space lies along permutation orbits rather than GL-type reparameterization orbits.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in cross-architecture τ_retention between SANE with orbit-based positional encodings and vanilla SANE with sequential positional encodings when evaluated zero-shot on the Small Transformer Zoo after training on the Small CNN Zoo. (Statistical test: paired t-test, 5 seeds; Wilcoxon signed-rank; α=0.05)

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Small CNN Zoo + Small Transformer Zoo (standard) | CNN Zoo provides training data (MLP/CNN weight space with permutation symmetry), Transformer Zoo provides zero-shot evaluation data; both have ground-truth accuracy labels enabling Kendall's τ evaluation |
| **Model** | SANE+orbit-PE (SANE with orbit-based positional encodings) | SANE provides the scalable cross-architecture tokenization backbone; orbit-PE replaces sequential positional encodings with permutation-orbit membership vectors, enabling architecture-agnostic weight tokens |

**Dataset Details:**
- Source: Small CNN Zoo from NFN paper [Zhou et al., NeurIPS 2023]; Small Transformer Zoo from Transformer-NFN [Tran-Viet et al., ICLR 2025, 125K checkpoints on MNIST+AGNews]
- Path: Available from AllanYangZhou/nfn and MathematicalAI-NUS/Transformer-NFN repositories

**Model Details:**
- Type: Transformer-backbone autoencoder with reconstruction+contrastive loss
- Source: Built on HSG-AIML/SANE (open source, ICML 2024) with orbit-PE modification using AllanYangZhou/nfn primitives for permutation orbit computation

### 1.4 Baseline Methods (for comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Vanilla SANE | τ_retention < 0.50 (expected cross-arch zero-shot baseline) | Small CNN Zoo → Small Transformer Zoo |
| Transformer-NFN | τ ≈ 0.905–0.910 (within-architecture upper bound) | Small Transformer Zoo (MNIST, AGNews) |
| SANE + random-PE | Dimensionality-matched ablation control | Small CNN Zoo → Small Transformer Zoo |
| NFN | τ = 0.934 (CIFAR-10-GS), τ = 0.931 (SVHN-GS) within CNN | Small CNN Zoo |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Input/output channel permutation is functionally equivalent for MLP, CNN, Transformer linear operators (validation accuracy change <0.1% under canonical permutations) | NFN proves permutation symmetry for MLP/CNN; Transformer-NFN proves S_h symmetry for attention heads | Orbit-PE encodes spurious symmetries; predictions become inconsistent across architecture families |
| A2 | Permutation variance dominates GL variance (Var_perm / (Var_perm + Var_GL) > 0.60) | NFN's τ>0.93 using only permutation equivariance suggests most predictive signal is captured by permutation structure | Orbit-PE ceiling is hard; τ_retention cannot reach ≥0.70; hybrid approach required |
| A3 | SANE's contrastive training is compatible with orbit-PE positional encodings | SANE achieves linear probe accuracy ≥0.978 with contrastive loss; orbit-PE changes only positional encoding | Orbit-PE creates positional conflicts, degrading even within-architecture performance |
| A4 | Small CNN Zoo and Small Transformer Zoo are representative of cross-architecture property prediction (no severe distribution shift) | Both datasets contain models trained to convergence on standard benchmarks; used as reference benchmarks in NFN and Transformer-NFN papers | τ_retention reflects dataset distribution shift rather than symmetry-transfer |
| A5 | Architecture identifiers can be removed without collapsing all predictive signal | Transformer-NFN achieves τ ≈ 0.902 from block structure alone (ablation) | Without architecture labels, τ collapses for both SANE and orbit-PE |

### 1.6 Research Gap & Novelty

**Research Gap:** No existing method provides equivariant cross-architecture weight representations spanning MLP+CNN+Transformer. NFN/Transformer-NFN are architecture-restricted; SANE achieves cross-architecture but with architecture-conditioned sequential positional encodings.

**Novelty:** First use of orbit-based positional encodings for weight tokenization; first cross-architecture zero-shot weight-based model property prediction; first OVR decomposition methodology for measuring symmetry-transfer efficiency in WSL.

**Key Innovation:** Orbit-PE bridges the gap between equivariant NFNs (high within-architecture fidelity, architecture-restricted) and SANE (cross-architecture, non-equivariant) by injecting permutation-orbit structure into tokenization positional encodings — a minimal architectural change with maximal cross-architecture reach.

**Scope Reduction from Established Facts:** 33% reduction — 4 BUILD_ON claims (NFN τ>0.93, Transformer-NFN τ≈0.905-0.910, SANE linear probe 0.978-0.991, Monomial-NFN symmetry proofs) do NOT need re-verification. Only 2 PROVE_NEW claims require experimental validation.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | todo |
| H-M1 | Mechanism | MUST_WORK | H-E1 | todo |
| H-M2 | Mechanism | MUST_WORK | H-M1 | todo |
| H-M3 | Mechanism | MUST_WORK | H-M2 | todo |
| H-C1 | Condition | SHOULD_WORK | H-M2 (parallel) | todo |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Architecture-Agnostic Permutation Symmetry Existence**

**Statement**: Under weight space learning for model property prediction, if canonical input/output channel permutations are applied to both CNN and Transformer checkpoints, then validation accuracy changes by <0.1% for both architecture families, because the input/output channel permutation group is a functionally valid symmetry for any linear operator regardless of architecture.

**Rationale**: This existence hypothesis validates the foundational claim that orbit-PE is computable and meaningful across architecture families. Without confirmed symmetry validity (H-E1), all downstream mechanism hypotheses (H-M1–H-M3) are void. It corresponds to P3's function preservation test and the Monomial-NFN/Transformer-NFN theoretical frameworks.

**Variables**:
- Independent: Architecture type (CNN vs Transformer)
- Dependent: |Δ validation accuracy| under canonical channel permutation; orbit-PE computability success rate for all layer types
- Controlled: Checkpoint source (Small CNN Zoo / Small Transformer Zoo), permutation sampling procedure, evaluation dataset

**Verification Protocol**:
1. Sample 500 CNN Zoo checkpoints and 500 Transformer Zoo checkpoints from standard repositories.
2. Apply 10 random canonical channel permutations (g ∈ input-channel perm × output-channel perm) to each checkpoint.
3. Measure mean |Δ acc| on held-out validation set per checkpoint and report mean ± std.
4. Verify orbit-PE is computable for Linear, Conv2d, and MultiheadAttention layers using nfn library primitives.
5. Report orbit membership encoding success rate and any layer types requiring custom handling.

**Success Criteria**:
- Primary: Mean |Δ acc| < 0.1% for both CNN Zoo and Transformer Zoo (function preservation confirmed)
- Secondary: Orbit-PE encoding succeeds for 100% of layer types without architecture-specific code

**Failure Response**:
- IF fails (|Δ acc| > 0.1%): PIVOT — investigate which architecture's symmetry is violated; consider restricting orbit-PE to subgroup that preserves functionality

**Dependencies**: None (foundation experiment; must run first)

**Source**: Phase 2A Section 1.6 P3 (function preservation), Section 1.3 Causal Step 1, phase2b_readiness.sh1_existence

---

**H-M1: Input/Output Channel Permutation Group Architecture-Agnostic Computability**

**Statement**: Under weight space learning, if the input/output channel permutation group is applied as the canonical symmetry group for all linear operators across MLP, CNN, and Transformer architectures, then orbit membership vectors are computable with identical dimensionality and structural interpretation for all layer types, because the (input-channel perm × output-channel perm) group action collapses to the same mathematical structure at the linear-operator level regardless of architecture.

**Rationale**: H-M1 tests the first causal step: that the permutation group action is architecture-agnostic at implementation level, not just theoretically. This validates that Monomial-NFN's MLP/CNN group structure and Transformer-NFN's S_h group structure are unified instances of the same (input-channel perm × output-channel perm) action, enabling orbit-PE to be a single, shared codebase component.

**Variables**:
- Independent: Layer type (Linear, Conv2d, MultiheadAttention)
- Dependent: Orbit membership vector dimensionality consistency; computation time overhead (target ≤1.2× vanilla SANE)
- Controlled: nfn library version, orbit computation algorithm, random seed for permutation sampling

**Verification Protocol**:
1. Implement orbit-PE computation module using AllanYangZhou/nfn primitives for all three layer types.
2. For 100 sampled checkpoints per architecture, compute orbit membership vectors for all layers.
3. Verify orbit vector dimensionality is identical (or padded to fixed size) across CNN and Transformer layers.
4. Measure wall-clock time for orbit-PE computation vs sequential-PE assignment per checkpoint.
5. Confirm that orbit-PE computation adds ≤1.2× overhead relative to vanilla SANE tokenization.

**Success Criteria**:
- Primary: Orbit-PE computable for all layer types with unified codebase (no architecture-conditional branches)
- Secondary: Computation overhead ≤1.2× vanilla SANE

**Failure Response**:
- IF fails (layer type requires custom code): EXPLORE — document required architecture-specific handling; assess whether parameterized orbit-PE (with architecture adapter) is acceptable

**Dependencies**: H-E1 (symmetry existence confirmed)

**Source**: Phase 2A Section 1.3 Causal Step 1, evidence: Monomial-NFN + Transformer-NFN

---

**H-M2: Permutation Variance Dominance in Model Zoo Checkpoint Geometry**

**Statement**: Under weight space analysis on Small CNN Zoo checkpoint trajectories, if weight vectors are projected onto permutation orbit directions and GL orbit directions, then Var_perm / (Var_perm + Var_GL) > 0.60, because NFN's success (τ>0.93) using only permutation equivariance implies that permutation orbits capture the dominant functional variation in model zoo checkpoint geometry.

**Rationale**: H-M2 is the critical gating experiment for the entire hypothesis: if permutation variance does not dominate (< 60%), the theoretical ceiling of orbit-PE is too low to achieve τ_retention ≥ 0.70, and a hybrid approach (orbit-PE + GL trace features) becomes mandatory before running H-M3. This experiment de-risks the main experiment and validates assumption A2.

**Variables**:
- Independent: Variance decomposition method (projection onto permutation orbit vs GL orbit manifold)
- Dependent: Var_perm / (Var_perm + Var_GL) ratio across CNN Zoo checkpoint trajectories
- Controlled: CNN Zoo checkpoint set (full Small CNN Zoo, CIFAR-10 + SVHN classifiers), projection algorithm, trajectory length

**Verification Protocol**:
1. Load all available Small CNN Zoo checkpoint trajectories (training progress checkpoints, not just final models).
2. For each checkpoint W_t in each trajectory, compute projection onto permutation orbit: Var_perm = E_t ||W_t - Π_{O_perm}(W_t)||².
3. Compute GL orbit projection analogously: Var_GL = E_t ||W_t - Π_{O_GL}(W_t)||².
4. Report Var_perm / (Var_perm + Var_GL) across all trajectories (mean ± std).
5. **GATE**: If ratio < 0.60, trigger hybrid pivot (add tr(W^Q W^{K,T}) traces to orbit-PE) before proceeding to H-M3.

**Success Criteria**:
- Primary: Var_perm / (Var_perm + Var_GL) > 0.60 (permutation variance dominance confirmed)
- Secondary: Ratio stable across CIFAR-10 and SVHN model families (not dataset-specific)

**Failure Response**:
- IF fails (ratio < 0.60): PIVOT — implement hybrid orbit-PE + low-degree GL invariant polynomial traces (tr(W^Q W^{K,T})); re-run H-M3 with hybrid model

**Dependencies**: H-E1 (orbit structure computable), H-M1 (orbit-PE implementation ready)

**Source**: Phase 2A Section 1.3 Causal Step 2, Section 1.4 Assumption A2, Section 1.6 P3

---

**H-M3: Orbit-PE Enables Cross-Architecture Zero-Shot Property Prediction**

**Statement**: Under cross-architecture weight space learning, if SANE's sequential positional encodings are replaced with orbit-PE and the model is trained only on Small CNN Zoo, then zero-shot evaluation on Small Transformer Zoo achieves τ_retention = τ_{CNN→Transformer} / τ_{CNN→CNN} ≥ 0.70 compared to τ_retention < 0.50 for vanilla SANE, because permutation-orbit encoding removes the primary architecture-specific barrier in SANE's positional representation.

**Rationale**: H-M3 is the primary empirical test of the main hypothesis (P1). It directly validates the core claim that orbit-PE enables cross-architecture transfer. Success here confirms that permutation-orbit positional encodings are sufficient to bridge the CNN→Transformer zero-shot gap, validating both the mechanism (causal step 3) and the PROVE_NEW claim about cross-architecture zero-shot property prediction.

**Variables**:
- Independent: Positional encoding type — sequential-PE (vanilla SANE), orbit-PE (proposed), random-PE (ablation)
- Dependent: τ_retention = τ_{CNN→Transformer} / τ_{CNN→CNN} for model property prediction (generalization accuracy, training epoch)
- Controlled: SANE backbone, training data (Small CNN Zoo only), architecture identifiers removed, parameter count distributions matched between CNN Zoo and Transformer Zoo subsets, 5 random seeds

**Verification Protocol**:
1. Train SANE+orbit-PE, vanilla SANE, and SANE+random-PE on full Small CNN Zoo (5 seeds each; standard train/val split).
2. Remove architecture identifiers and match parameter count distributions between CNN Zoo and Transformer Zoo subsets.
3. Evaluate zero-shot on full Small Transformer Zoo (125K checkpoints); compute Kendall's τ for generalization accuracy and training epoch prediction.
4. Compute τ_retention = τ_{CNN→Transformer} / τ_{CNN→CNN} per model per seed; report mean ± std.
5. Run label-permutation sanity check (shuffle Transformer Zoo accuracy labels — τ should collapse to ≈0).

**Success Criteria**:
- Primary: orbit-PE τ_retention ≥ 0.70 AND vanilla SANE τ_retention < 0.50 AND absolute improvement ≥ 0.10
- Secondary: random-PE τ_retention < orbit-PE τ_retention (confirms symmetry information, not just dimensionality)

**Failure Response**:
- IF orbit-PE τ_retention < 0.60: PIVOT — if H-M2 ratio was borderline (0.55–0.60), attempt hybrid orbit-PE + GL traces; if H-M2 ratio was clearly > 0.60, EXPLORE alternative mechanisms
- IF orbit-PE τ_retention in [0.60, 0.70): EXPLORE — partial success; report with discussion of GL ceiling

**Dependencies**: H-E1, H-M1, H-M2 (all must pass before H-M3 execution)

**Source**: Phase 2A Section 1.6 P1 (primary prediction), Section 1.1 core_hypothesis_statement, phase2b_readiness.sh2_mechanism

---

**H-C1: GL Symmetry Gap Boundary Condition (OVR_GL Ceiling)**

**Statement**: Under orbit-PE model evaluation on Transformer Zoo checkpoints, if synthetic GL-type transforms (A ∈ GL_{Dk}^h × GL_{Dv}^h) are applied to checkpoints and OVR_GL is measured, then OVR_GL ∈ (0.15, 0.40) for the trained orbit-PE model, confirming that a non-negligible GL symmetry gap exists as a known theoretical ceiling — and that orbit-PE does not accidentally become GL-invariant.

**Rationale**: H-C1 characterizes the boundary condition and ceiling of the orbit-PE approach. OVR_GL ≤ 0.10 would mean orbit-PE accidentally approximates GL invariance, falsifying the mechanism claim. OVR_GL > 0.40 (combined with Var_perm < 0.60) would trigger the hybrid pivot. This hypothesis validates the theoretical framework's completeness and provides pre-registered pivot criteria.

**Variables**:
- Independent: Symmetry subgroup tested (S_h × neuron permutations vs GL_{Dk}^h × GL_{Dv}^h synthetic transforms)
- Dependent: OVR_GL = E_g ||f(g·W) - f(W)||_2 / E_{W'≠W} ||f(W') - f(W)||_2 for orbit-PE model; OVR_perm for comparison
- Controlled: Trained orbit-PE model from H-M3, Transformer Zoo checkpoint sample (500), GL transform sampling procedure

**Verification Protocol**:
1. Use trained orbit-PE SANE model from H-M3 (no retraining needed).
2. Sample 500 Transformer Zoo checkpoints and apply 20 random synthetic GL transforms per checkpoint (det(A) ≠ 0).
3. Compute OVR_GL = E ||f(A·W) - f(W)||_2 / E_{W'≠W} ||f(W') - f(W)||_2; report mean ± std.
4. Compute OVR_perm (same formula, g ∈ S_h × neuron permutations) for comparison; confirm OVR_perm < 0.05.
5. Apply pivot criterion: if OVR_GL > 0.40 AND Var_perm < 0.60 (from H-M2), document hybrid approach recommendation.

**Success Criteria**:
- Primary: OVR_GL ∈ (0.15, 0.40) — GL gap confirmed as theoretically expected but manageable
- Secondary: OVR_perm < 0.05 — permutation invariance encoded correctly by orbit-PE

**Failure Response**:
- IF OVR_GL ≤ 0.10: EXPLORE — orbit-PE is accidentally GL-invariant; mechanism claim needs revision
- IF OVR_GL > 0.40 AND Var_perm < 0.60 (from H-M2): PIVOT — implement hybrid orbit-PE + GL trace features

**Dependencies**: H-M2 (Var_perm fraction needed for pivot criterion), H-M3 (trained orbit-PE model required)

**Source**: Phase 2A Section 1.6 P2, Section 1.5 known_limitations, Section 1.3 key_tension

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 (GATE) → H-M3
                    ↘
                    H-C1 (parallel, after H-M2 + uses H-M3 model)
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Mean |Δacc| < 0.1% for CNN + Transformer; orbit-PE computable for all layer types | STOP pipeline; reassess symmetry assumption |
| H-M1 | MUST_WORK | Orbit-PE unified codebase (no arch-specific branches); overhead ≤ 1.2× SANE | SCOPE to simpler architectures; document limitation |
| H-M2 | MUST_WORK (GATE) | Var_perm/(Var_perm+Var_GL) > 0.60 on CNN Zoo trajectories | PIVOT to hybrid orbit-PE + GL traces; re-run H-M3 with hybrid |
| H-M3 | MUST_WORK | τ_retention ≥ 0.70 AND vanilla SANE < 0.50 AND absolute improvement ≥ 0.10 | PIVOT (if near threshold) or EXPLORE (partial success) |
| H-C1 | SHOULD_WORK | OVR_GL ∈ (0.15, 0.40) AND OVR_perm < 0.05 | Document GL ceiling; recommend hybrid if OVR_GL > 0.40 |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1 — Foundation | H-E1 | Weeks 1–2 |
| Phase 2 — Mechanisms | H-M1 | Weeks 3–4 |
| Phase 2 — Mechanisms | H-M2 (GATE) | Week 5 |
| Phase 2 — Mechanisms | H-M3 | Week 6 |
| Phase 3 — Conditions | H-C1 (parallel) | Weeks 6–7 |

**Total Duration:** 7 weeks (nominal) / 8–9 weeks (with R2 pivot buffer)

---

## 4. Risk Analysis

Five risks identified from Phase 2A assumptions A1–A5 via multi-expert collaborative analysis. R2 (permutation variance dominance) is CRITICAL — it gates H-M3 entirely. Execution order must respect gating: H-E1 → H-M1 → H-M2 (gate) → H-M3 ∥ H-C1.

**Risk Register:**

**R1 — MHA Joint Permutation Validity** (Source: A1)
- Description: MHA has interdependent Q/K/V/O projection matrices; applying independent channel permutations without coordinating their joint symmetry may produce functionally different (not equivalent) models.
- Severity: HIGH | Likelihood: MEDIUM → **High**
- Affected: H-E1, H-M1

**R2 — Permutation Variance Non-Dominance** (Source: A2)
- Description: Var_perm/(Var_perm+Var_GL) < 0.60 on CNN Zoo checkpoint trajectories — GL-type reparameterizations (W_Q→W_Q A⁻¹, W_K→W_K A⁻ᵀ) may account for >40% of variance, capping orbit-PE's theoretical reach below τ_retention ≥ 0.70.
- Severity: CRITICAL | Likelihood: MEDIUM → **Critical**
- Affected: H-M2, H-M3

**R3 — SANE Contrastive Loss Disruption** (Source: A3)
- Description: SANE's positional encoding is architecturally baked into the transformer backbone's attention patterns; replacing sequential-PE with orbit-PE vectors of different dimensionality/semantics may disrupt learned position-to-content associations, degrading even within-architecture performance.
- Severity: HIGH | Likelihood: LOW → **Medium**
- Affected: H-M1, H-M2, H-M3

**R4 — Cross-Task Evaluation Confound** (Source: A4)
- Description: CNN Zoo (CIFAR-10/SVHN image classifiers) → Transformer Zoo (MNIST/AGNews — different modalities) introduces cross-task label distribution confound; τ_retention suppression may reflect task dissimilarity, not symmetry failure.
- Severity: MEDIUM | Likelihood: MEDIUM → **Medium**
- Affected: H-M3, H-C1

**R5 — Implicit Architecture Signal Leakage** (Source: A5)
- Description: Even after removing architecture identifiers, implicit signals leak through weight tensor rank (rank-4 Conv vs rank-2 Linear/Attention) and token count; architecture-blind evaluation is not fully guaranteed by identifier removal alone.
- Severity: MEDIUM | Likelihood: MEDIUM → **Medium**
- Affected: All hypotheses (confound)

### 4.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: MHA Joint Permutation Validity | A1 | H-E1, H-M1 | High |
| R2: Permutation Variance Non-Dominance | A2 | H-M2, H-M3 | **Critical** |
| R3: SANE Contrastive Loss Disruption | A3 | H-M1, H-M2, H-M3 | Medium |
| R4: Cross-Task Evaluation Confound | A4 | H-M3, H-C1 | Medium |
| R5: Implicit Architecture Signal Leakage | A5 | H-E1, H-M1, H-M2, H-M3, H-C1 | Medium |

### 4.2 Mitigation Strategies

**R1 Mitigation — MHA Joint Permutation Validity**
1. Prevention: Implement coordinated Q/K/V/O joint permutation (not independent per-matrix) following Transformer-NFN's G_U group action; use nfn library's MHA-specific permutation primitives.
2. Detection: Run H-E1 function preservation test on Transformer checkpoints first; flag any |Δacc| > 0.05% as early warning.
3. Response: If MHA permutation fails for specific layer configs, SCOPE to single-head attention Transformers that have simpler S_h group action.

**R2 Mitigation — Permutation Variance Non-Dominance (CRITICAL GATE)**
1. Prevention: Execute H-M2 (P3 gating experiment) BEFORE committing to H-M3 training runs; pre-register pivot threshold at Var_perm < 0.60.
2. Detection: Var_perm/(Var_perm+Var_GL) ratio measured on CNN Zoo trajectories — if < 0.60, pivot triggers automatically.
3. Response: PIVOT to hybrid orbit-PE + low-degree GL invariant polynomial traces (tr(W^Q W^{K,T}), tr(W^V W^{V,T})); re-run H-M3 with hybrid model. This pivot is pre-planned and does not constitute hypothesis failure.

**R3 Mitigation — SANE Contrastive Loss Disruption**
1. Prevention: Initialize orbit-PE adapter as a learned linear projection from orbit membership vectors to the same dimensionality as sequential-PE; warm-start from vanilla SANE weights.
2. Detection: Monitor within-architecture τ (CNN→CNN) for orbit-PE vs vanilla SANE — if orbit-PE degrades within-architecture performance by >5%, contrastive loss disruption is occurring.
3. Response: EXPLORE dimensionality-matched warm-start adapter; if still degraded, use random-PE as upper-bound diagnostic to isolate cause.

**R4 Mitigation — Cross-Task Evaluation Confound**
1. Prevention: Report τ_retention stratified by Transformer Zoo task (MNIST vs AGNews) separately; verify that within-task τ (e.g., CNN-CIFAR10 → Transformer-MNIST) is also computed.
2. Detection: If orbit-PE τ_retention differs by >0.10 between MNIST and AGNews Transformer subsets, cross-task confound is present.
3. Response: SCOPE conclusions to within-modality cross-architecture transfer (CNN-image→Transformer-image); report cross-modality results as supplementary.

**R5 Mitigation — Implicit Architecture Signal Leakage**
1. Prevention: Apply per-layer shape normalization before tokenization (pad/truncate weight tokens to fixed size); use architecture-blind evaluation protocol (no rank-4/rank-2 shape info in token sequence).
2. Detection: Train a binary architecture classifier on weight tokens alone — if accuracy > 60%, implicit leakage is present.
3. Response: Add explicit architecture-type scrambling augmentation during training; if leakage persists, document as limitation and report lower-bound τ_retention estimates.

### 4.3 Risk Summary

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | MHA joint permutation breaks functional equivalence | A1 | High | H-E1, H-M1 | Coordinated Q/K/V/O joint permutation; nfn MHA primitives |
| R2 | Permutation variance < 60% (GL variance dominates) | A2 | **Critical** | H-M2, H-M3 | H-M2 gating before H-M3; pre-registered pivot to hybrid orbit-PE + GL traces |
| R3 | SANE contrastive loss disrupted by orbit-PE | A3 | Medium | H-M1–H-M3 | Warm-start from vanilla SANE; dimensionality-matched adapter; random-PE diagnostic |
| R4 | Cross-task confound suppresses τ_retention | A4 | Medium | H-M3, H-C1 | Stratified evaluation by Transformer Zoo task (MNIST vs AGNews) |
| R5 | Implicit architecture leakage through token shape | A5 | Medium | All | Per-layer shape normalization; architecture-blind evaluation protocol |

Critical Risks: 1 (R2)
High Risks: 1 (R1)
Medium Risks: 3 (R3, R4, R5)
Low Risks: 0

---

## 5. Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) — H-OrbitPE-v1 (5 Hypotheses)
═══════════════════════════════════════════════════════════════════

[Level 0 — Foundation]
    ┌─────────────────────────────────────────────┐
    │  H-E1: Architecture-Agnostic Perm Symmetry  │
    │  Gate: MUST_WORK                            │
    │  Prerequisites: None                        │
    └──────────────────────────┬──────────────────┘
                               │  GATE 1: H-E1 MUST PASS
                               ▼
[Level 1 — Mechanism Step 1]
    ┌─────────────────────────────────────────────┐
    │  H-M1: Orbit-PE Architecture-Agnostic       │
    │  Computability Verification                 │
    │  Gate: MUST_WORK                            │
    │  Prerequisites: H-E1                        │
    └──────────────────────────┬──────────────────┘
                               │  GATE 2: H-M1 MUST PASS
                               ▼
[Level 2 — Mechanism Step 2 — CRITICAL GATE]
    ┌─────────────────────────────────────────────┐
    │  H-M2: Permutation Variance Dominance       │
    │  Var_perm / (Var_perm + Var_GL) > 0.60      │
    │  Gate: MUST_WORK (GATES H-M3 execution)     │
    │  Prerequisites: H-E1, H-M1                  │
    └────────────┬─────────────────────┬──────────┘
                 │  H-M2 GATE PASS     │  H-C1 can start
                 ▼                     ▼  (uses H-M3 model)
[Level 3 — Primary Transfer Test]   [Level 3 — Parallel Condition]
    ┌────────────────────────┐       ┌──────────────────────────┐
    │  H-M3: Orbit-PE CNN→   │       │  H-C1: GL Symmetry Gap   │
    │  Transformer Zero-Shot │       │  Boundary Condition      │
    │  τ_retention ≥ 0.70    │       │  OVR_GL ∈ (0.15, 0.40)  │
    │  Gate: MUST_WORK       │       │  Gate: SHOULD_WORK       │
    │  Prerequisites:        │       │  Prerequisites: H-M2,    │
    │  H-E1, H-M1, H-M2     │       │  H-M3 (trained model)    │
    └────────────────────────┘       └──────────────────────────┘
                 │                               │
                 └──────────────┬────────────────┘
                                ▼
                    [VERIFICATION COMPLETE]
                    Pipeline → Phase 2C per hypothesis

═══════════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 (gate) → H-M3
Parallel Track: H-C1 (starts after H-M2, uses H-M3 trained model)
═══════════════════════════════════════════════════════════════════

Dependency Map:
  H-E1  → []
  H-M1  → [H-E1]
  H-M2  → [H-E1, H-M1]
  H-M3  → [H-E1, H-M1, H-M2]
  H-C1  → [H-M2, H-M3]  (H-M3 dependency is for trained model access)
```

### 5.1 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type | Phase | Risk |
|-------|-----------|---------------|-----------|-------|------|
| 0 | H-E1: Permutation Symmetry Existence | None | MUST_WORK | Foundation | R1 |
| 1 | H-M1: Orbit-PE Computability | H-E1 | MUST_WORK | Core Mechanisms | R1, R3 |
| 2 | H-M2: Var_perm Dominance (GATE) | H-E1, H-M1 | MUST_WORK | Core Mechanisms | R2 |
| 3 | H-M3: CNN→Transformer Zero-Shot Transfer | H-E1, H-M1, H-M2 | MUST_WORK | Primary Test | R2, R3, R4, R5 |
| 3∥ | H-C1: GL Symmetry Gap Boundary | H-M2, H-M3 | SHOULD_WORK | Conditions | R4, R5 |

**Verification Phases:**

| Phase | Hypotheses | Gate Condition | Fail Action |
|-------|-----------|----------------|-------------|
| Phase 1 — Foundation | H-E1 | MUST PASS: |Δacc| < 0.1% for CNN + Transformer | STOP — reassess entire hypothesis |
| Phase 2 — Mechanism (1) | H-M1 | MUST PASS: orbit-PE computable for all layer types | SCOPE to simpler architectures |
| Phase 2 — Mechanism (2 GATE) | H-M2 | MUST PASS: Var_perm > 0.60 OR pivot to hybrid | PIVOT to hybrid orbit-PE + GL traces |
| Phase 3 — Primary Test | H-M3 | MUST PASS: τ_retention ≥ 0.70 | EXPLORE partial success; PIVOT if near threshold |
| Phase 3∥ — Condition | H-C1 | SHOULD PASS: OVR_GL ∈ (0.15, 0.40) | Document ceiling; recommend hybrid |

---

## 6. Timeline Planning

### 6.1 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE — H-OrbitPE-v1 (5 Hypotheses)
═══════════════════════════════════════════════════════════════════════════════
Phase / Hypothesis      │ W1-2    │ W3-4    │ W5      │ W6      │ W7
────────────────────────┼─────────┼─────────┼─────────┼─────────┼──────────
PHASE 1: Foundation     │         │         │         │         │
  H-E1 (Perm Symmetry) │ ████████│         │         │         │
  [Gate 1 ◆ MUST PASS] │        ◆│         │         │         │
────────────────────────┼─────────┼─────────┼─────────┼─────────┼──────────
PHASE 2: Mechanisms     │         │         │         │         │
  H-M1 (Orbit-PE Impl) │         │ ████████│         │         │
  [Gate 2 ◆ MUST PASS] │         │        ◆│         │         │
  H-M2 (Var_perm Gate) │         │         │ ████    │         │
  [Gate 2b◆ CRITICAL]  │         │         │    ◆    │         │
  H-M3 (CNN→Trans Xfer)│         │         │         │ ████████│
  [Gate 3 ◆ MUST PASS] │         │         │         │        ◆│
────────────────────────┼─────────┼─────────┼─────────┼─────────┼──────────
PHASE 3: Conditions     │         │         │         │         │
  H-C1 (OVR_GL Bound.) │         │         │         │ ░░░░░░░░│ ████
    (parallel; needs    │         │         │         │         │
     H-M3 trained model)│         │         │         │         │
  [Gate 3.5 ◆ SHOULD]  │         │         │         │         │    ◆
────────────────────────┼─────────┼─────────┼─────────┼─────────┼──────────
═══════════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ░░░░ = Waiting for dependency | ◆ = Gate decision
Critical Path Duration: 6 weeks (W1→W6 for H-M3 completion)
Total with H-C1: 7 weeks
═══════════════════════════════════════════════════════════════════════════════

Estimated GPU Hours (reference from Phase 2A feasibility): ≈22 GPU-hours total
  H-E1 + H-M1: ~2 GPU-hours (symmetry checks, orbit-PE implementation verification)
  H-M2 (P3 Var_perm): ~2 GPU-hours (projection computations on CNN Zoo trajectories)
  H-M3 (5 seeds × 3 models): ~15 GPU-hours (SANE training × 3 × 5 seeds)
  H-C1 (OVR measurement): ~3 GPU-hours (embedding computation on 500 checkpoints)
```

### 6.2 Critical Path Analysis

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3 (6 weeks)

**Duration breakdown:**
- H-E1: Weeks 1–2 (2 weeks) — symmetry verification + orbit-PE computability check
- H-M1: Weeks 3–4 (2 weeks) — orbit-PE implementation + overhead measurement
- H-M2: Week 5 (1 week) — Var_perm/(Var_perm+Var_GL) ratio computation on CNN Zoo trajectories; **GATE**
- H-M3: Week 6 (1 week) — SANE+orbit-PE training (5 seeds × 3 models) + zero-shot Transformer Zoo evaluation

**Slack:** H-C1 runs in parallel during Week 6 (waiting on H-M3 trained model) and completes in Week 7. No slack on critical path — all sequential gated.

**Critical Gate:** H-M2 (Week 5) is the critical gate decision. If Var_perm < 0.60, pivot to hybrid model adds ~1–2 weeks to H-M3.

**Risk Buffer:** If R2 (pivot) triggers: +1–2 weeks for hybrid orbit-PE + GL trace feature implementation and re-training. Revised total: 8–9 weeks.

### 6.3 Resource Summary

| Resource | Requirement | Notes |
|----------|------------|-------|
| GPU | 1× GPU (single GPU per CLAUDE.md policy) | Select lowest memory usage GPU via nvidia-smi |
| GPU Hours | ~22 total (nominal) / ~30–35 (with R2 pivot buffer) | H-M3 dominates: 15 GPU-hrs for 5-seed × 3-model training |
| Datasets | Small CNN Zoo (AllanYangZhou/nfn) + Small Transformer Zoo (MathematicalAI-NUS/Transformer-NFN) | Both publicly available; download required |
| Codebase | HSG-AIML/SANE (base) + AllanYangZhou/nfn (orbit-PE primitives) | MIT / Apache licenses |
| Implementation | orbit-PE module (new), OVR measurement module (new), variance decomposition module (new) | 3 new modules; builds on SANE + nfn |
| Total Duration (nominal) | 6 weeks critical path + 1 week H-C1 = 7 weeks | With R2 pivot buffer: 8–9 weeks |
| Hypotheses | 5 total: H-E1, H-M1, H-M2, H-M3, H-C1 | 1 Existence, 3 Mechanism, 1 Condition |
| Phases | 3 phases (Foundation, Mechanisms, Conditions) | Phases 1–2 fully sequential; Phase 3 parallel |

### 6.4 Execution Order

1. **Week 1–2: Execute H-E1** — Sample 500 CNN + 500 Transformer checkpoints; apply canonical channel permutations; measure |Δacc|; verify orbit-PE computability for Linear/Conv2d/MHA. **Gate 1 decision at Week 2 end.**
2. **Week 3–4: Execute H-M1** — Implement unified orbit-PE module using nfn primitives; compute orbit membership vectors for all layer types; measure overhead vs vanilla SANE. **Gate 2 decision at Week 4 end.**
3. **Week 5: Execute H-M2 (CRITICAL GATE)** — Compute Var_perm/(Var_perm+Var_GL) on CNN Zoo checkpoint trajectories. **Gate 2b decision at Week 5 end: if < 0.60, trigger hybrid pivot (adds 1–2 weeks). If ≥ 0.60, proceed to H-M3.**
4. **Week 6: Execute H-M3** — Train SANE+orbit-PE, vanilla SANE, SANE+random-PE on full CNN Zoo (5 seeds each); zero-shot evaluate on full Transformer Zoo; compute τ_retention. **Gate 3 decision at Week 6 end.**
5. **Week 6–7 (parallel): Execute H-C1** — Use trained orbit-PE model from H-M3; sample 500 Transformer Zoo checkpoints; apply synthetic GL transforms; compute OVR_GL and OVR_perm. **Gate 3.5 decision at Week 7 end.**
6. **Verification Complete** → Output 04_validation.md per hypothesis → Phase 2C for each PASS hypothesis.

---

## 7. Dialectical Analysis

Dialectical analysis performed via ClearThought structured argumentation (3-stage: Thesis → Antithesis → Synthesis). The dialectic resolves the central tension: can permutation-orbit structure alone bridge the CNN→Transformer architectural gap, or do GL-type reparameterizations and cross-task confounds dominate?

**Dialectic Confidence Summary:**
- Thesis confidence: 0.72 (matches Phase 2A convergence confidence)
- Antithesis confidence: 0.35 (H0 is plausible but requires specific violation of A2 or A3)
- Synthesis confidence: 0.82 (verification plan is robust regardless of outcome)

### 7.1 Thesis

**Core Claim:** Orbit-PE enables cross-architecture zero-shot model property prediction (τ_retention ≥ 0.70) because permutation-orbit structure is the dominant transferable symmetry across neural architecture families.

**Supporting Evidence:**
1. NFN's τ>0.93 on CNN Zoo using only permutation equivariance — permutation structure captures dominant predictive signal (established, BUILD_ON)
2. Transformer-NFN's S_h and Monomial-NFN's (input-channel perm × output-channel perm) are the same architecture-agnostic group action at linear-operator level (established theory, BUILD_ON)
3. SANE's tokenization backbone + orbit-PE positional encoding = minimal architectural change with maximal cross-architecture reach (architectural insight, Phase 2A Exchange 7)

**Strengths:**
- Grounded in four established methods with strong empirical track records
- Minimal architectural modification: only positional encoding layer changed
- Clear, pre-registered falsification thresholds (P1/P2/P3)
- Architecture-agnostic symmetry group is mathematically well-defined

**Expected Outcomes:** P1 (τ_retention ≥ 0.70), P2 (OVR_perm < 0.05, OVR_GL > 0.15), P3 (Var_perm > 0.60)

### 7.2 Antithesis

**H0:** There is no significant difference in cross-architecture τ_retention between SANE+orbit-PE and vanilla SANE on the Small Transformer Zoo.

**Counter-Arguments:**
1. GL-type reparameterizations (W_Q→W_Q A⁻¹, W_K→W_K A⁻ᵀ) may account for >40% of weight-space variance, capping orbit-PE below τ_retention ≥ 0.70 (R2 — CRITICAL)
2. SANE's contrastive loss trained with sequential-PE may conflict with orbit-PE's different semantic structure, degrading within-architecture baseline too (R3)
3. Cross-task confound: CNN Zoo (image) vs Transformer Zoo (image+text) — τ suppression may reflect task dissimilarity, not symmetry failure (R4)

**Conditions Supporting H0:**
- If Var_perm/(Var_perm+Var_GL) < 0.60 on CNN Zoo trajectories (P3 fails → R2 triggered)
- If orbit-PE τ_retention < 0.60 AND within-architecture τ also degrades (R3 triggered)
- If orbit-PE τ_retention improvement < 0.10 over vanilla SANE (insufficient effect size for P1)
- If random-PE achieves similar τ_retention as orbit-PE (dimensionality, not symmetry, drives gains)

### 7.3 Synthesis

The verification plan resolves the thesis-antithesis dialectic through sequential, gate-controlled design. H-M2 (Var_perm gating) directly tests R2 — the core antithesis concern — before committing to H-M3's expensive training runs. The random-PE ablation controls R3 (separates dimensionality from symmetry effects). Stratified evaluation by Transformer Zoo task (MNIST vs AGNews) tests R4. Per-layer shape normalization addresses R5.

**Resolution Path:**
1. H-E1: Establishes symmetry existence before mechanism — early exit if A1 is violated
2. H-M2 (Gate): Directly tests A2 (Var_perm dominance) — the strongest antithesis premise; pivot plan activates if < 0.60
3. H-M3: Primary transfer test with three controls (random-PE, architecture-blind protocol, stratified evaluation)
4. H-C1: Characterizes GL symmetry ceiling — converts potential weakness into a reported finding

**Nuanced Outcome Possibilities:**
- **Full Thesis Support** (P1/P2/P3 all pass): orbit-PE achieves τ_retention ≥ 0.70 → first cross-architecture zero-shot WSL method
- **Partial Support** (P1 in [0.60, 0.70)): orbit-PE improves over SANE but below threshold → characterize GL ceiling; report as partial success with hybrid recommendation
- **Pivot Support** (H-M2 fails, hybrid orbit-PE + GL traces passes): antithesis partially correct on GL variance → hybrid method validates with revised mechanism claim
- **H0 Support** (H-M1 or H-M3 fail with no improvement over random-PE): orbit-PE mechanism is incorrect → report OVR decomposition methodology as standalone contribution

**Key finding:** The synthesis confidence (0.82) is higher than the thesis confidence (0.72) because the verification plan is robust regardless of outcome — every outcome produces scientifically informative results about the symmetry structure of weight space.

### 7.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Symmetry Existence (A1) | Perm group is architecture-agnostic | MHA joint permutation may break equivalence | H-E1 function preservation test (MUST_WORK gate) |
| Variance Dominance (A2) | Var_perm > 60% inferred from NFN success | GL variance may dominate for Transformers | H-M2 gating experiment (CRITICAL gate before H-M3) |
| Training Compatibility (A3) | Orbit-PE compatible with SANE contrastive loss | SANE sequential-PE assumption may be disrupted | Random-PE ablation + warm-start from vanilla SANE |
| Evaluation Validity (A4) | CNN/Transformer Zoos are representative | Cross-task confound (image vs text) | Stratified τ_retention by Transformer Zoo task |
| Identifier Removal (A5) | Architecture info removed successfully | Implicit leakage through token shape | Per-layer shape normalization + architecture-blind protocol |

**Overall Robustness Score:** Medium-High
- Gate structure directly tests the two strongest antithesis premises (R1 via H-E1, R2 via H-M2)
- Three control conditions (random-PE ablation, architecture-blind evaluation, stratified reporting)
- Pre-registered pivot plan ensures scientifically informative outcome in all scenarios

**Confidence in Verification Plan:** 0.82 (synthesis) / 0.72 (hypothesis) — plan is more robust than hypothesis confidence alone

---

## 8. Executive Summary & Conclusions

**Main Hypothesis:** Replace SANE's sequential-PE with orbit-based positional encodings (orbit-PE) from the input/output channel permutation group → CNN→Transformer zero-shot τ_retention ≥ 0.70.
- ID: H-OrbitPE-v1 | Confidence: 0.72 | Mode: Incremental (33% scope reduction from 4 BUILD_ON facts)

**Verification Structure:**
- 5 sub-hypotheses: H-E1 (Existence), H-M1–H-M3 (Mechanism), H-C1 (Condition)
- 3 phases over 7 weeks (nominal) | 4 gate decision points
- Critical gate: H-M2 (Var_perm dominance) gates H-M3 execution
- ~22 GPU-hours total | Single GPU required

**Risk Assessment:** Medium-High
- Primary concerns: R2 (Var_perm < 60% may cap τ_retention — CRITICAL), R1 (MHA joint permutation validity — HIGH)
- Pre-registered pivot: hybrid orbit-PE + GL traces if R2 triggers

**Immediate Action:** Execute H-E1 (function preservation test + orbit-PE computability) — Weeks 1–2

### 8.1 Final Summary

**Key Achievements of This Plan:**
- 5 hypotheses defined with pre-registered quantitative thresholds and falsification criteria
- H0 addressed dialectically: thesis (orbit-PE works) vs antithesis (GL variance / confounds dominate) → synthesis (gate-controlled plan robust to all outcomes)
- 33% scope reduction from Phase 2A established facts (4 BUILD_ON claims excluded from verification)
- Critical gate (H-M2) identified — de-risks $15 GPU-hour H-M3 commitment

**Verification Execution Order:**

Phase 1 — Foundation (Weeks 1–2): H-E1 — function preservation + orbit-PE computability. Gate: MUST PASS.

Phase 2 — Mechanisms (Weeks 3–6):
- H-M1 (Weeks 3–4): Orbit-PE unified codebase + overhead verification. Gate: MUST PASS.
- H-M2 (Week 5, GATE): Var_perm/(Var_perm+Var_GL) > 0.60 on CNN Zoo. Gate: MUST PASS or PIVOT.
- H-M3 (Week 6): SANE+orbit-PE CNN→Transformer zero-shot τ_retention. Gate: MUST PASS.

Phase 3 — Conditions (Weeks 6–7, parallel): H-C1 — OVR_GL characterization. Gate: SHOULD PASS.

**Critical Decision Points:**
1. Gate 1 (H-E1, Week 2): FAIL → STOP, symmetry assumption invalid
2. Gate 2 (H-M1, Week 4): FAIL → SCOPE to simpler architectures
3. Gate 2b (H-M2, Week 5 — CRITICAL): FAIL → PIVOT to hybrid orbit-PE + GL traces (+1–2 weeks)
4. Gate 3 (H-M3, Week 6): FAIL → EXPLORE partial success; report GL ceiling as finding

**Open Questions (from Phase 2A):**
- Does Var_perm fraction > 0.60 hold empirically? (H-M2 answers this)
- What is the optimal orbit-PE embedding dimensionality? (H-M1/H-M3 sensitivity analysis)
- Does compute overhead stay ≤1.2× vanilla SANE? (H-M1 overhead measurement)

**Recommendations:**
1. Immediate: Download Small CNN Zoo and Small Transformer Zoo datasets; set up SANE + nfn codebases
2. Resource: Allocate single GPU with lowest memory usage (nvidia-smi); plan 22 GPU-hours
3. Sequencing: Do NOT skip H-M2 gating experiment before starting H-M3 training runs
4. Controls: Always train random-PE ablation alongside orbit-PE (same compute budget per seed)
5. Failure management: Pre-register all pivot criteria before experiment start; execute hybrid plan if R2 triggers

### 8.2 Conclusions

Phase 2B verification planning for H-OrbitPE-v1 is complete. The plan decomposes the main hypothesis into 5 sub-hypotheses with a gate-controlled sequential execution order, 5 pre-registered risk mitigations, and a dialectically-robust synthesis position (confidence 0.82). The plan is ready for Phase 2C experiment design execution, beginning with H-E1.

### 8.3 Appendices

**A. Phase 2A Source Reference**
- Primary: `docs/youra_research/20260521_wsl/03_refinement.yaml` (H-OrbitPE-v1, schema v10.0.0)
- Supplementary: `02_synthesis.yaml`, `01_round_table/final_opinions.yaml`
- Phase 2A workflow: phase2a-dialogue v10.0.0, 15 exchanges, 6 personas, convergence met

**B. MCP Tool Usage Summary**
- `mcp__clearThought__scientificmethod`: 3 calls (H-E1, H-M-integrated, H-C1)
- `mcp__clearThought__collaborativereasoning`: 1 call (risk analysis, 3-expert panel)
- `mcp__clearThought__structuredargumentation`: 3 calls (thesis, antithesis, synthesis)
- `mcp__archon__*`: pipeline status check + task management (steps 0, 10)
- Total MCP calls: 10

**C. Established Facts (BUILD_ON — DO NOT RE-VERIFY)**
- NFN τ>0.93 on CNN Zoo [Zhou et al., NeurIPS 2023]
- Transformer-NFN τ≈0.905–0.910 within Transformer Zoo [Tran-Viet et al., ICLR 2025]
- SANE linear probe accuracy 0.978–0.991 [Schürholt et al., ICML 2024]
- Monomial-NFN extends NFN to scaling+sign-flip symmetries [Tran, Vo et al., 2024]

---

## 9. Finalization Status

- Verification State: ✅ `verification_state.yaml` created — 5 sub-hypotheses (H-E1: READY; H-M1, H-M2, H-M3, H-C1: NOT_STARTED), schema v3.5
- Pipeline Tasks Updated: ✅ Phase 2B → done | Phase 2C → doing (Archon project 858b6bf8)
- Hypothesis Tasks Created: ✅ 5 tasks created in Archon (H-E1: 0c72e9c2, H-M1: 6833e885, H-M2: d61fb66e, H-M3: fc2b7eca, H-C1: 23fa3031)

---

*Generated by YouRA Phase 2B (v7.7.0) | 2026-05-20*
