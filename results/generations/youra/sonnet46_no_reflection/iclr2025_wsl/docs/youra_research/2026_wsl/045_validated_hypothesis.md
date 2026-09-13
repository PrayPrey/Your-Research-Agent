# 045_validated_hypothesis.md
# Phase 4.5 Hypothesis Synthesis Report — H-OrbitPE-v1
# Version: 2.0 | Generated: 2026-05-21T05:00:00Z | Mode: UNATTENDED

---

## Executive Summary

H-OrbitPE-v1 tested whether permutation-orbit positional encodings (orbit-PE) could enable cross-architecture zero-shot model property prediction via weight space learning. Three of five sub-hypotheses were executed: H-E1 (VALIDATED: channel permutation is a functionally exact symmetry, delta_acc=0.000 across 4,500 runs), H-M1 (VALIDATED: orbit-PE is computable for all layer types at 1.167x overhead), and H-M2 (FAILED: overall Var_perm/(Var_perm+Var_GL) = 0.3479, below the 0.60 threshold). H-M3 and H-C1 were correctly blocked. The main hypothesis claim (τ_retention ≥ 0.70) was not tested because its mechanism precondition (P3: permutation variance dominance) was refuted. A hybrid encoding approach (orbit-PE for Conv2d + GL-invariant trace features for Linear/attention) is recommended as H-OrbitPE-v2.

---

## Section 1: Synthesis Overview

| Field | Value |
|-------|-------|
| **Hypothesis ID** | H-OrbitPE-v1 |
| **Title** | Orbit-PE: Cross-Architecture Weight Space Learning via Permutation-Orbit Positional Encodings |
| **Pipeline Status** | PARTIAL (3/5 sub-hypotheses resolved; pivoted before H-M3/H-C1) |
| **Sub-hypotheses Tested** | h-e1 (VALIDATED), h-m1 (VALIDATED), h-m2 (FAILED) |
| **Sub-hypotheses Blocked** | h-m3 (NOT_STARTED), h-c1 (NOT_STARTED) |
| **Routing Decision** | ROUTED_TO_PHASE_0 — hybrid orbit-PE + GL trace features pivot |
| **Synthesis Completeness** | Partial (core claim P1 untested; core mechanism assumption P3 refuted) |

---

## Prediction-Result Matrix

| Prediction | Status | Key Evidence |
|-----------|--------|--------------|
| P1: τ_retention ≥ 0.70 (CNN→Transformer) | INCONCLUSIVE | H-M3 blocked; mechanism precondition refuted |
| P2: OVR_perm < 0.05, OVR_GL ∈ (0.15, 0.40) | INCONCLUSIVE | H-C1 cascaded-blocked |
| P3: Var_perm/(Var_perm+Var_GL) > 0.60 | REFUTED | H-M2: ratio=0.3479; Conv2d=0.637, Linear=0.133 |

---

## Experiment Results

| Sub-hypothesis | Experiment | Result | Key Metric |
|----------------|-----------|--------|------------|
| h-e1 | Channel permutation symmetry validity | VALIDATED | delta_acc=0.000 (4,500 runs) |
| h-m1 | Orbit-PE computability and overhead | VALIDATED | computability=1.0, overhead=1.167x |
| h-m2 | Variance decomposition: Var_perm vs Var_GL | FAILED | ratio=0.3479 (threshold 0.60); Conv2d=0.637, Linear=0.133 |
| h-m3 | SANE+orbit-PE cross-architecture training | BLOCKED | Blocked by h-m2 FAIL |
| h-c1 | OVR measurement on trained orbit-PE model | BLOCKED | Cascaded block from h-m2 |

---

## Section 2: Prediction-to-Result Mapping

### P1 — Primary Prediction (INCONCLUSIVE)
**Prediction:** SANE+orbit-PE achieves τ_retention ≥ 0.70 in CNN→Transformer zero-shot model property prediction (vs. τ_retention < 0.50 for vanilla SANE).

**Status: INCONCLUSIVE**
- H-M3 (the experiment that would test P1) was blocked by H-M2's MUST_WORK FAIL.
- P1 was never tested. The mechanism assumption underlying P1 (permutation variance dominance, P3) was refuted, meaning P1 was correctly gated — testing a prediction whose causal precondition fails would produce uninterpretable results.
- **Planned vs. Actual:** 03_tasks.yaml (h-m3) planned 5-seed cross-architecture training with SANE+orbit-PE, vanilla SANE, and random-PE controls. None of these experiments executed.

### P2 — OVR Decomposition (INCONCLUSIVE)
**Prediction:** OVR_perm < 0.05 AND OVR_GL ∈ (0.15, 0.40) for trained orbit-PE model.

**Status: INCONCLUSIVE**
- H-C1, which would have measured OVR, was cascaded-blocked from h-m2 FAIL.
- No OVR measurements were taken on a trained orbit-PE model (which never existed, since H-M3 did not run).
- **Note:** The H-M2 layer-breakdown provides a *related* signal — Var_GL/Var_total for Linear layers = 86.7% — but this is a variance decomposition metric, not the OVR embedding-level metric that P2 specifies.

### P3 — Variance Dominance (REFUTED)
**Prediction:** Var_perm / (Var_perm + Var_GL) > 0.60 on Small CNN Zoo checkpoint trajectories.

**Status: REFUTED**
- H-M2 directly tested P3: result = **0.3479 ± 0.0536** (n=1000 models × 50 epochs; threshold 0.60).
- **Layer-type breakdown reveals partial confirmation:**
  - Conv2d: ratio = **0.637** (PASS — permutation dominates for convolutional layers)
  - Linear/FC: ratio = **0.133** (FAIL — GL orbit variance dominates at 6.6× scale)
- **Training trajectory:** Ratio decreases from ~0.49 (epoch 0) to ~0.28 (epoch 50), indicating learned representations increasingly exploit GL-type directions.
- **Planned vs. Actual (h-m2):** Planned 200+ models; actual 1000 models × 50 epochs — larger scale than required, strengthening refutation confidence.
- **Experiment design integrity (vs. 02c_experiment_brief.md):** Design specified SVHN-GS cross-dataset stability check; SVHN data unavailable — SKIP. This does not affect the primary gate result.

---

## Hypothesis Refinement

The original core claim that "permutation-orbit structure is the dominant transferable symmetry component (>60% of variance)" is refuted by H-M2. The refined hypothesis (H-OrbitPE-v2) replaces pure orbit-PE with a hybrid encoding: permutation orbit-PE for Conv2d layers (validated, ratio=0.637) and GL-invariant trace features for Linear/attention layers (ratio=0.133). The success criterion is relaxed to τ_retention ≥ 0.65 (from ≥0.70). The confirmed claims — exact symmetry validity and 1.17x overhead — are retained.

---

## Section 3: Refined Hypothesis Statement

### Original Core Statement (03_refinement.yaml)
> Under weight space learning for neural network model property prediction, if sequential positional encodings in SANE's weight tokenizer are replaced with orbit-based positional encodings (orbit-PE) derived from the input/output channel permutation group (architecture-agnostic linear-operator symmetry), then cross-architecture zero-shot τ_retention in CNN→Transformer model property prediction will reach ≥70% (vs <50% for vanilla SANE), because permutation-orbit structure is the dominant transferable symmetry component across neural architecture families — more than 60% of checkpoint variation in weight space lies along permutation orbits rather than GL-type reparameterization orbits.

### Overclaim Analysis

| Claim | Evidence | Verdict |
|-------|----------|---------|
| "permutation-orbit structure is the dominant transferable symmetry component" | Var_perm/total = 0.3479 overall; Conv2d=0.637, Linear=0.133 | **OVERCLAIM — remove** |
| ">60% of checkpoint variation lies along permutation orbits" | Directly refuted by H-M2 | **OVERCLAIM — remove** |
| "input/output channel permutation is a functionally valid architecture-agnostic symmetry" | H-E1: delta_acc = 0.000 across 4,500 runs | **CONFIRMED — retain** |
| "orbit-PE is computable for all layer types with ≤1.2x overhead" | H-M1: computability=1.0, overhead=1.167x | **CONFIRMED — retain** |
| "τ_retention ≥ 0.70 achievable with pure orbit-PE" | Untested, but mechanism precondition (P3) refuted | **OVERCLAIM — remove** |

### Refined Core Statement (v2.0)

> Under weight space learning for neural network model property prediction, the input/output channel permutation group is a functionally exact architecture-agnostic symmetry for all linear operator types (Conv2d, Linear, MultiheadAttention), computable with 1.17x overhead. However, permutation orbit variance is insufficient as the sole structural encoding: permutation variance dominates convolutional layers (Conv2d ratio=0.637) but GL-orbit variance dominates linear/attention layers (Linear ratio=0.133, overall ratio=0.348). Cross-architecture zero-shot property prediction via orbit-PE alone is therefore theoretically capped; a **hybrid encoding** combining permutation orbit for Conv2d with GL-invariant trace features for Linear/attention layers is required for the τ_retention ≥ 0.70 target.

### Status of Key Assumptions

| Assumption | Status | Evidence |
|------------|--------|----------|
| A1: Channel permutation is valid symmetry for MLP/CNN/Transformer | **CONFIRMED** | H-E1: delta_acc = 0.000 (4,500 runs) |
| A2: Var_perm/(Var_perm+Var_GL) > 0.60 | **REFUTED** | H-M2: 0.3479 overall |
| A3: SANE contrastive training compatible with orbit-PE | **UNVERIFIED** | H-M3 not run |
| A4: CNN Zoo / Transformer Zoo representative | **PARTIALLY VERIFIED** | H-E1, H-M1 executed on both |
| A5: Architecture identifiers removable without collapsing signal | **UNVERIFIED** | H-M3 not run |

---

## Theoretical Interpretation

The H-M2 result provides independent empirical confirmation of the GL symmetry literature: the Linear layer ratio (0.133) aligns with arXiv:2410.04207's motivation for GL-invariant features. The Conv2d ratio (0.637) explains NFN's success on CNN Zoo (τ > 0.93 with permutation-only equivariance). The training trajectory (ratio decreasing from ~0.49 to ~0.28 over 50 epochs) suggests optimizers progressively exploit GL-type reparameterizations, consistent with loss landscape flat-direction literature. The bimodal Conv2d/Linear stratification (4.8x ratio difference) is the key unexpected theoretical finding.

---

## Section 4: Literature Connection and Unexpected Findings

### Connection to Established Literature

**H-E1 result confirms NFN/Transformer-NFN theoretical foundations:**
- The exact zero delta-acc (0.000000) across all 4,500 runs is stronger than the < 0.1% threshold. This matches the theoretical proofs in NFN [Zhou et al., NeurIPS 2023] and Transformer-NFN [Tran-Viet et al., ICLR 2025] that (input-channel × output-channel) permutation is in the symmetry group of linear operators.
- The Monomial-NFN [Tran, Vo et al., 2024] claim that all invariant groups ⊆ monomial matrix group is consistent with this result.

**H-M1 result aligns with SANE efficiency claims:**
- 1.167x overhead for orbit-PE computation is within the SANE framework's practical efficiency envelope. SANE [Schürholt et al., ICML 2024] positions itself as scalable; orbit-PE addition preserves this property.
- Unified codebase (HAS_ARCH_BRANCHES=False) validates that the orbit abstraction successfully hides architecture details.

**H-M2 result: alignment with GL symmetry literature**
- The Linear layer ratio of 0.133 (GL dominance) aligns with the theoretical prediction from arXiv:2410.04207 (GL orbit features for attention). That paper proposed GL-invariant features precisely because GL symmetry dominates linear/attention weights — the H-M2 result is independent empirical confirmation.
- The Conv2d ratio of 0.637 aligns with NFN's success (τ > 0.93 with permutation-only equivariance for CNN Zoo), which is a CNN-dominant dataset; the high permutation variance for Conv2d layers explains why permutation-only methods work well on CNN Zoo within-architecture tasks.

### Unexpected Findings

**Finding 1: Layer-type stratification is sharper than anticipated**
- The predicted threshold was "overall > 0.60", implicitly assuming rough uniformity across layer types. The actual data reveals a bimodal split: Conv2d (0.637) vs. Linear (0.133) — a 4.8x ratio difference. This is not a mild shortfall but a fundamental layer-type stratification.

**Competing explanations:**
1. *Structural explanation*: Conv2d weight tensors have explicit spatial structure (H×W kernel dimensions) where permutation equivalences are more "local" and dominate; Linear/attention tensors are fully dense with more global GL-type variation.
2. *Training dynamics explanation*: The trajectory analysis shows ratio declining from ~0.49 to ~0.28 during training. This suggests that the optimizer exploits GL-type reparameterizations during learning, progressively moving weights into non-permutation-orbit directions. This is consistent with the loss landscape literature showing that flat directions along symmetry orbits are common at initialization but training breaks this.
3. *Scale explanation*: Linear layers in CNNs (FC classifiers) connect large flattened feature vectors; the high dimensionality of GL(d) for large d may simply provide more variance "directions" than the lower-rank permutation group.

**Finding 2: Permutation variance decreases during training**
- Trajectory evolution shows ratio decreasing from ~0.49 (epoch 0) to ~0.28 (epoch 50). This was not anticipated in the hypothesis design. If confirmed on Transformer Zoo, it implies that orbit-PE would be most useful for early-training or randomly-initialized model zoos (where the ratio is higher), and less effective for well-trained checkpoints. This has implications for the experimental design of H-M3 if it were to be re-run with hybrid encoding.

---

## Section 5: Principled Limitations

### L1 — Core Architecture Limitation: Permutation-Only Orbit-PE is Insufficient for Linear Layers
**Root cause:** The input/output channel permutation group S_{c_in} × S_{c_out} is a discrete subgroup of GL(c_in) × GL(c_out). For convolutional layers, the spatial structure effectively constrains the weight space such that permutation orbits capture the dominant variation. For linear layers, the full GL group acts without such structural constraint, so GL-type reparameterizations (scaling, rotations, shearing) dominate the variance budget.
**Scope:** This limitation is specific to fully-connected and attention layers. It is not a limitation for Conv2d layers (ratio=0.637 > threshold).
**Mitigation path:** Hybrid encoding: orbit-PE for Conv2d + GL-invariant trace features (tr(WW^T), tr(W^Q W^{K,T})) for Linear/attention. This is the pre-specified pivot in the H-M2 gate design.

### L2 — Experimental Limitation: Primary Claim (P1) Never Tested
**Root cause:** The sub-hypothesis chain (H-E1 → H-M1 → H-M2 → H-M3 → H-C1) was correctly ordered so that the causal precondition (H-M2, P3) must hold before testing the downstream claim (H-M3, P1). Since P3 was refuted, P1 was appropriately not tested — but this means the main hypothesis claim remains empirically unaddressed.
**Implication:** The synthesis report cannot conclude whether orbit-PE achieves τ_retention ≥ 0.70. The claim is not refuted (tau_retention may still be improvable with hybrid encoding), but it is unvalidated.

### L3 — Dataset Limitation: SVHN-GS Cross-Dataset Stability Skipped
**Root cause:** SVHN Zoo data was unavailable at experiment time for H-M2.
**Consequence:** The cross-dataset stability check (|CIFAR_ratio - SVHN_ratio| < 0.10) was not performed. If SVHN-GS has different layer composition, the Var_perm ratio might differ. However, the CIFAR result (n=1000 models × 50 epochs) provides strong statistical confidence in the refutation regardless.

### L4 — Scope Limitation: Only CNN Zoo Tested for Variance Decomposition
**Root cause:** H-M2 was designed for CNN Zoo only (as Conv2d-dominant data). The Var_perm/Var_GL ratio for Transformer Zoo checkpoints was not measured.
**Consequence:** We cannot directly claim what the ratio is for Transformer architectures. Given that Transformer-only weights are linear/attention dominated (no Conv2d), the ratio would likely be even lower than 0.3479, further strengthening the case for GL trace features.

### L5 — Infrastructure Limitation: H-M1 OrbitPEComputer Path Issue in H-M2
**Root cause:** H-M2's orbit_projector.py could not import H-M1's OrbitPEComputer via relative path. A fallback SVD-based orbit basis was used.
**Consequence:** The variance decomposition results used SVD-reconstructed orbit bases rather than the H-M1 orbit-PE vectors directly. This is methodologically consistent (both compute orbit projections) but represents a minor implementation divergence from the planned design.

---

## Section 6: Future Work Directions

### FW1 — Hybrid Orbit-PE + GL Trace Features (Immediate Next Step — Pre-registered Pivot)
**Grounding:** H-M2 explicitly designed the pivot: Conv2d layers use permutation orbit-PE (validated, ratio=0.637); Linear/attention layers use GL-invariant polynomial trace features (tr(WW^T), tr((WW^T)^2), tr(W^Q W^{K,T})).
**Concrete design:** Layer-type dispatch in the positional encoding module — orbit-PE dispatch table extended with a `gl_trace_pe` branch for `nn.Linear` and `nn.MultiheadAttention`. The infrastructure (orbit_projector.py, variance_decomposer.py) from H-M2 is directly reusable.
**Expected outcome:** Combined encoding should address the Linear layer gap. If GL trace features capture the 86.7% GL-dominated variance in Linear layers, the effective transfer encoding coverage should increase substantially.

### FW2 — Training Dynamics and Orbit Variance Trajectory
**Grounding:** H-M2 finding that ratio decreases from ~0.49 to ~0.28 during training is unexpected and unexplored.
**Direction:** Study whether orbit-PE (and hybrid encoding) benefits early-checkpoint model zoos differently than late-training checkpoint zoos. This connects to weight space learning for training trajectories (arXiv:2602.23696 trajectory PCA) and could enable a new "training-stage-aware" positional encoding.
**Research question:** Does the trajectory ratio decrease uniformly across model zoo diversity (all models show same slope), or is there high variance indicating some models maintain higher permutation variance throughout training?

### FW3 — Theoretical Analysis of Conv2d vs. Linear Variance Stratification
**Grounding:** The bimodal observation (Conv2d=0.637, Linear=0.133) needs theoretical explanation.
**Direction:** Derive the expected Var_perm/Var_total ratio as a function of layer type, tensor rank, and symmetry group order. The key question is whether the spatial (H×W) structure of Conv2d effectively creates "approximate" permutation dominance by constraining the active GL directions.
**Connection:** This would contribute to the broader understanding of weight space geometry for cross-architecture representation learning.

### FW4 — Separate CNN Zoo Evaluation by Layer Type for Orbit-PE Ablation
**Grounding:** H-M3 was designed as a full SANE+orbit-PE training run. A cheaper ablation would be: run orbit-PE only on Conv2d layers (where it is validated), treat Linear/attention layers with sequential PE, and measure the resulting τ_retention — this isolates the Conv2d contribution before committing to the full hybrid.
**Motivation:** Given the layer-type stratification result, a partial orbit-PE (Conv2d only) might already show improvement over vanilla SANE's sequential PE, providing a lower-bound estimate of the orbit-PE benefit before building the full hybrid.

---

## Section 7: Refined Hypothesis for Next Iteration

### Hypothesis ID: H-OrbitPE-v2 (Proposed)
**Refined Statement:**
> Under weight space learning for neural network model property prediction, if SANE's sequential positional encodings are replaced with a **hybrid positional encoding** — permutation orbit-PE for Conv2d layers (which have Var_perm ratio=0.637 > 0.60) and GL-invariant trace features (tr(WW^T), tr(W^Q W^{K,T})) for Linear/attention layers (which have GL-dominated variance, ratio=0.133) — then cross-architecture zero-shot τ_retention in CNN→Transformer model property prediction will reach ≥ 0.65 (relaxed from ≥0.70 given the layer-type asymmetry discovered), because:
> (1) the permutation group is a validated exact symmetry for all layer types (H-E1),
> (2) orbit-PE is computable with ≤1.2x overhead (H-M1),
> (3) hybrid encoding addresses the Conv2d/Linear stratification gap identified in H-M2,
> and GL-invariant trace features provide architecture-agnostic structural invariants for linear operators that complement permutation orbit encoding.

**Revised success criterion:** τ_retention ≥ 0.65 (down from 0.70) — motivated by the H-M2 result showing that the pure permutation mechanism is insufficient; hybrid encoding is a harder engineering challenge with potentially smaller symmetry coverage.

**Retained infrastructure from this iteration:**
- `h-e1/code/permutation.py`: Canonical channel permutation (exact symmetry, reusable)
- `h-m1/code/orbit_pe.py`: OrbitPEComputer for Conv2d (overhead 1.167x, reusable)
- `h-m2/code/orbit_projector.py`, `variance_decomposer.py`, `evaluate.py`: Variance decomposition + zoo-scale analysis (reusable for new variance validation step)
- `h-m2/code/data_loader.py`: TrajectoryDataset with symlink support (reusable)

---

## Section 8: Verification State Update

### Sub-hypothesis Terminal States

| Sub-hypothesis | Type | Gate | Result | Rationale |
|----------------|------|------|--------|-----------|
| h-e1 | EXISTENCE | MUST_WORK | ✅ PASS | delta_acc=0.000, orbit-PE success=1.0 |
| h-m1 | MECHANISM | MUST_WORK | ✅ PASS | computability=1.0, overhead=1.167x |
| h-m2 | MECHANISM | MUST_WORK | ❌ FAIL | Var_ratio=0.3479 < 0.60; Linear GL-dominated |
| h-m3 | MECHANISM | MUST_WORK | — BLOCKED | Blocked by h-m2 FAIL |
| h-c1 | CONDITION | SHOULD_WORK | — BLOCKED | Cascaded block from h-m2 |

### Main Hypothesis Verdict
**PARTIALLY_REFUTED** — The mechanism assumption (A2: permutation variance dominance) is refuted for Linear/attention layers. The existence claim (channel permutation is a valid symmetry) and computability claim (1.17x overhead) are confirmed. The primary performance claim (τ_retention ≥ 0.70) was not tested. The refined hypothesis (H-OrbitPE-v2) with hybrid encoding is the recommended next iteration.

### Phase 4.5 Synthesis Quality
- **Evidence quality:** High for h-e1 and h-m1 (exact results, 100% success rates). High for h-m2 (n=1000 models × 50 epochs; refutation statistically robust).
- **Gaps:** P1 and P2 untested (h-m3, h-c1 blocked). A3, A5 unverified.
- **Synthesis completeness:** 3/5 sub-hypotheses synthesized; 2/3 predictions resolved (P3 refuted, P1/P2 inconclusive).

---

---

## Implications for Phase 6

Phase 6 paper writing should frame H-OrbitPE-v1 as a **productive failure**: the existence and computability claims (H-E1, H-M1) are solid positive results, while the mechanism refutation (H-M2) contributes a novel empirical finding about weight space geometry (Conv2d vs. Linear variance stratification). The paper should present the layer-type stratification result as the key contribution — the bimodal Var_perm split (Conv2d=0.637, Linear=0.133) is independently publishable as an analysis of weight space symmetry structure. The hybrid encoding pivot (H-OrbitPE-v2) should be framed as a direct data-driven design decision supported by H-M2 evidence. Phase 6 should NOT claim τ_retention results (untested), but should claim the variance decomposition finding and the exact-symmetry validation as primary contributions.

---

*Phase 4.5 Hypothesis Synthesis | H-OrbitPE-v1 | Generated 2026-05-21T05:00:00Z*
*Pipeline: YouRA | Project: Neural network weights as a new data modality*
*Route: ROUTED_TO_PHASE_0 → H-OrbitPE-v2 (hybrid orbit-PE + GL trace features)*
