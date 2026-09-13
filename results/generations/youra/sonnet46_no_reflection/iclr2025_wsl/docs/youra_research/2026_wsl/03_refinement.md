# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-05-20T23:28:00Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap-1
- **Gap Title**: Incomplete Symmetry Coverage Across Diverse Neural Network Architectures
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All six criteria met — specific core claim, mechanism explained, three testable predictions with pre-registered thresholds, novelty articulated, feasibility confirmed (~22 GPU-hours, existing codebases), major objections addressed (GL gap with pivot strategy, architecture confounds controlled)

### Key Insights

1. **Symmetry-as-PE rather than symmetry-as-layer**: The discussion pivoted (Exchange 7) from "adding symmetry fingerprints to SANE embeddings" to "replacing positional encodings with orbit membership vectors" — a more principled architectural modification that changes inductive bias rather than just feature dimensionality.

2. **Architecture-agnostic group action**: Identifying (input-channel perm × output-channel perm) as the canonical architecture-agnostic linear-operator symmetry (Exchange 13) resolves the cross-architecture alignment challenge. Monomial-NFN and Transformer-NFN are both instances of this general framework.

3. **Cross-architecture transfer as the impact frame**: Dr. Sage reframed (Exchange 5) the scientific contribution from "improve within-architecture τ by X%" to "enable cross-architecture zero-shot model property prediction" — a qualitatively new capability, not an incremental improvement.

### Breakthrough Moments

- **Exchange 7**: Dr. Nova's shift from fingerprint augmentation to orbit-PE — "replace positional encodings" rather than "add features"
- **Exchange 13**: Dr. Ally's identification that Monomial-NFN establishes (input/output channel perm) as the canonical group, resolving the architecture alignment challenge
- **Exchanges 14-15**: Prof. Vera and Prof. Pax's convergence on pre-registered thresholds (P1/P2/P3) and feasibility confirmation — hypothesis becomes executable

---

## Final Hypothesis

### Title
Orbit-PE: Cross-Architecture Weight Space Learning via Permutation-Orbit Positional Encodings

### Hypothesis ID
H-OrbitPE-v1

### Core Claim
Under weight space learning for neural network model property prediction, if sequential positional encodings in SANE's weight tokenizer are replaced with orbit-based positional encodings (orbit-PE) derived from the input/output channel permutation group (architecture-agnostic linear-operator symmetry), then cross-architecture zero-shot τ_retention in CNN→Transformer model property prediction will reach ≥70% (vs <50% for vanilla SANE), because permutation-orbit structure is the dominant transferable symmetry component across neural architecture families (>60% of checkpoint variation lies along permutation orbits).

### Mechanism

SANE [Schürholt et al., ICML 2024] tokenizes neural network weights layer-by-layer into a transformer backbone with reconstruction+contrastive loss. Its sequential positional encodings assign position by layer index — making representations architecture-specific. Orbit-PE replaces these with orbit-membership vectors: for each weight token, encode which permutation orbit under (input-channel perm × output-channel perm) each neuron/filter/head belongs to. This orbit structure is architecture-agnostic — computable for MLP, CNN, and Transformer linear operators using the same canonical group action (established by Monomial-NFN [Tran, Vo et al., 2024] for MLP/CNN and Transformer-NFN [Tran-Viet et al., 2025] for attention heads). With architecture-agnostic positional information, the SANE backbone learns representations that transfer zero-shot across architecture families.

---

## Predictions

### P1 (Primary): Cross-Architecture τ_retention
- **Statement**: SANE+orbit-PE achieves τ_retention ≥ 0.70 in CNN→Transformer zero-shot transfer vs <0.50 for vanilla SANE
- **Test Method**: Train on Small CNN Zoo only; zero-shot eval on Small Transformer Zoo; τ_retention = τ_{CNN→Transformer} / τ_{CNN→CNN}; remove architecture identifiers; match parameter count distributions
- **Success Criterion**: orbit-PE τ_retention ≥ 0.70; absolute improvement ≥ 0.10 over vanilla SANE
- **Falsification**: τ_retention < 0.60 or absolute improvement < 0.10

### P2 (Secondary): OVR Subgroup Isolation
- **Statement**: OVR_perm < 0.05 (permutation invariance) and OVR_GL > 0.15 (not accidentally GL-invariant)
- **Test Method**: Embedding-level OVR under S_h × channel permutations (OVR_perm) and synthetic GL transforms (OVR_GL) on Transformer Zoo checkpoints
- **Falsification**: OVR_perm ≥ 0.05 (fails invariance) or OVR_GL ≤ 0.10 (accidentally GL-invariant)

### P3 (Gating): Permutation Variance Dominance
- **Statement**: Var_perm / (Var_perm + Var_GL) > 0.60 on CNN Zoo checkpoint trajectories
- **Test Method**: Project checkpoint trajectories onto permutation orbit directions and GL orbit directions; verify function preservation <0.1% accuracy change under canonical permutations
- **Falsification**: Var_perm fraction < 0.60 → pivot to hybrid orbit-PE + trace features

---

## Novelty

**Key Innovation**: Orbit-PE is the first weight tokenization method that uses permutation-orbit membership as positional encodings, enabling architecture-agnostic weight representations without redesigning the equivariant layer architecture.

**Differentiation from Prior Work**:
- vs. NFN / Transformer-NFN: Architecture-specific equivariant layers; cannot transfer across MLP/CNN/Transformer. Orbit-PE enables cross-architecture zero-shot transfer.
- vs. SANE: Sequential PE is architecture-conditioned. Orbit-PE provides architecture-agnostic orbit membership. SANE's cross-architecture experiments stay within architecture families.
- vs. Monomial-NFN: Adds scaling/sign-flip symmetries but MLP/CNN only. Orbit-PE uses Monomial-NFN's group structure as positional encoding rather than equivariant layer design.

---

## Experimental Design

**Datasets**: Small CNN Zoo (CIFAR-10, SVHN classifiers, training); Small Transformer Zoo (125K checkpoints, MNIST+AGNews, zero-shot evaluation)

**Models**: SANE+orbit-PE (proposed); vanilla SANE (baseline); random-PE (dimensionality ablation); Transformer-NFN (within-architecture upper-bound reference)

**Compute**: ~22 GPU-hours on single A100 (6h SANE training + 7h orbit-PE training + 9h evaluation/OVR/P3)

**Codebases**: HSG-AIML/SANE (31★), AllanYangZhou/nfn (93★), MathematicalAI-NUS/Transformer-NFN

---

## Limitations

- Orbit-PE handles only permutation subgroup (S_h × channel perms), not full G_U = S_h × GL_{Dk}^h × GL_{Dv}^h × PD × PDA. Expected OVR_GL > 0.15 even on success.
- P3 variance dominance assumption must be validated as gating experiment before large-scale work.
- Cross-architecture experiments require careful parameter count distribution matching to avoid architecture confounds.
- Scope: model property prediction only (generalization accuracy, training epoch, generalization gap). Not weight generation, model merging, or very large models (>1B parameters).

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | Exchange 15 — all six criteria met |
| **Hypothesis ID** | H-OrbitPE-v1 |
| **Clarity Verified** | Yes |
| **Remaining Objections** | GL symmetry gap (acknowledged; pivot plan ready); architecture confounds (controlled in experiment design) |
| **Phase 2B Readiness** | READY |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
*Discussion: 15 exchanges, 6 personas, 5 papers referenced*
*Gap: gap-1 — Incomplete Symmetry Coverage Across Diverse Neural Network Architectures*
