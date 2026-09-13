# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-26T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Independent-Controller Ablation — no external LLM)
- **Gap ID**: gap-1
- **Gap Title**: Incomplete Symmetry Coverage — Scaling and Sign-Flip Beyond Permutation
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 8
- **Convergence at**: Exchange 8
- **Recursive Entry**: v2 (superseded h-e1)

---

## Research Dialogue Context

**Participants**: Dr. Nova (Novelty), Prof. Vera (Falsifiability), Dr. Sage (Significance), Prof. Pax (Feasibility), Dr. Ally (Synthesis), Prof. Rex (Critique)

**Total Exchanges**: 8

**Convergence Reason**: All 6 convergence criteria met at Exchange 8 — SPECIFIC core claim, MECHANISM causal chain, PREDICTIONS (P1-P3), NOVELTY (first empirical ablation), FEASIBILITY (confirmed working infrastructure), OBJECTIONS (all concerns addressed)

**Controller Mode**: Independent-controller ablation (Claude self-plays all personas; no external LLM)

### Key Insights
- NFT baseline ρ~0.11 from h-e1 is the launch pad — zero new infrastructure needed
- Scaling/sign-flip symmetries create within-orbit variance that equivariant encoders must overcome implicitly
- Canonicalization as encoder-agnostic preprocessing applies to any encoder without architectural modification
- The geometric claim (PCA concentration) makes this a mechanistic finding, not just an engineering improvement
- M=2 scope (MNIST zoo) makes sign-flip canonicalization well-defined and immediately implementable

### Breakthrough Moments
- **Exchange 4 (Prof. Pax)**: Sign-flip canonicalization for M=2 is well-defined — only one consecutive layer pair, uniquely determined by majority sign rule
- **Exchange 5 (Dr. Ally)**: 7-condition design synthesized (A raw, B scaling, C sign-flip, D both, E random-norm, F flat_mlp+both, G PCA) into coherent experimental package
- **Exchange 7 (Dr. Nova)**: Condition G (PCA concentration) added as mechanism-level evidence independent of encoder performance
- **Exchange 8 (Prof. Vera)**: Formal convergence — all 6 criteria simultaneously satisfied

---

## Final Hypothesis

### Title
**SymCanon-WSL: Symmetry Canonicalization for Weight Space Property Prediction**

**Hypothesis ID:** H-SymCanon-v1

### Core Claim

Under the Schürholt model zoo benchmark setting (MNIST MLP zoo, 2-layer networks, ~50k models), if MLP weight vectors are canonicalized to remove scaling and sign-flip symmetry orbits before encoding with a permutation-equivariant encoder (NFT), then Spearman rank correlation with held-out model properties (test accuracy, generalization gap, learning rate recovery) increases by Δρ ≥ 0.05 relative to raw weight encoding, because canonical representations concentrate property-relevant geometric information by eliminating symmetry-induced variance that dilutes the prediction signal.

**H₀:** No significant difference in Spearman ρ between canonicalized-weight NFT and raw-weight NFT (Δρ < 0.05).

### Mechanism

1. **Orbit variance exists**: Raw weights contain within-orbit variance from scaling/sign-flip symmetries — functionally irrelevant (same network function) but geometrically present in weight space.

2. **Encoder capacity allocated to invariance**: NFT's permutation-equivariant encoder must allocate capacity to learn implicit invariance to this within-orbit variance, reducing capacity for property-predictive features.

3. **Canonicalization concentrates signal**: Explicit orbit collapse to canonical representatives eliminates within-orbit variance, concentrating property-relevant information and freeing encoder capacity for property prediction.

---

## Predictions

| ID | Primary | Statement | Success Criterion |
|----|---------|-----------|-------------------|
| P1 | ✅ YES | Condition D (both canonicalizations → NFT) achieves Δρ ≥ 0.05 above Condition A (raw → NFT) on ≥ 2/3 tasks | Δρ ≥ 0.05 on accuracy; ≥ 2/3 tasks show improvement; non-overlapping 95% CIs |
| P2 | NO | Condition D > Condition E (random norm control) on ≥ 2/3 tasks | ρ_D > ρ_E with non-overlapping CIs; confirms symmetry-specific effect |
| P3 | NO (exploratory) | If SVHN/CIFAR zoos available, improvement from canonicalization ≥ MNIST improvement | Conditional on zoo availability; Δρ_deeper ≥ Δρ_MNIST or at minimum > 0 |

---

## Novelty

**What's new:** First empirical ablation of scaling and sign-flip symmetry contribution to model property prediction accuracy via a preprocessing intervention on a real model zoo benchmark.

**Key innovation:** Symmetry canonicalization as an encoder-agnostic preprocessing step — applicable to any equivariant or non-equivariant encoder without architectural modification.

**Differentiation from prior work:**

| Prior Work | Gap |
|-----------|-----|
| NFN (Zhou 2023) | Permutation equivariance only; scaling/sign-flip not handled or empirically measured |
| DWSNets (Navon 2023) | Scaling theoretically characterized but not empirically ablated; M>2 constraint fails on MNIST zoo (h-e1 failure) |
| Hyper-Representations (Schürholt 2022) | Self-supervised pretraining; symmetry group coverage not addressed |
| Layer stats (Unterthiner 2020) | Permutation-agnostic; no geometric structure |

---

## Experimental Design

**Dataset:** Schürholt MNIST Model Zoo (~50k 2-layer MLPs, 784→64→10, ground-truth: accuracy/gen_gap/lr_recovery). Confirmed loadable from h-e1.

**Primary encoder:** NFT (Neural Functional Transformer). Confirmed working on zoo, ρ~0.11 baseline.

**7-Condition Ablation:**

| Condition | Description | Purpose |
|-----------|-------------|---------|
| A | Raw weights → NFT | Baseline (h-e1 confirmed) |
| B | Scaling-canonicalized → NFT | Scaling-only contribution |
| C | Sign-flip-canonicalized → NFT | Sign-flip-only contribution |
| D | Both canonicalizations → NFT | **Primary treatment** |
| E | Random normalization → NFT | Normalization artifact control |
| F | Both canonicalizations → flat_mlp | Encoder-agnosticism test |
| G | PCA on canonical vs raw weights, R² with property labels | Mechanism test |

**Sub-experiment:** Frozen NFT encoder (trained on raw weights) + canonical inputs; only final regressor retrained. Separates representation quality from optimization dynamics.

**Runtime:** CPU hours. Implementation: ~50-60 lines PyTorch. Timeline: 2-3 days.

---

## Limitations

- **M=2 scope**: Sign-flip canonicalization is well-defined for 2-layer MLPs (MNIST zoo) only. Extension to M>2 requires additional algorithm design (future work).
- **Low baseline ρ**: NFT ρ~0.11 leaves limited room; bootstrap CI pre-check mandatory before committing to Δρ=0.05 threshold.
- **SVHN/CIFAR availability**: P3 cross-zoo experiment is exploratory — zoo availability unverified.
- **Not competing with layer stats**: ρ~0.9 (layer stats) remains the ceiling; this hypothesis targets equivariant encoder improvement, not overall property prediction SOTA.

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria at Exchange 8 |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Implementation checkpoints only (bootstrap CI, frozen encoder, zoo availability) |
| **Ready for Phase 2B** | Yes |

### Pre-Experiment Mandatory Checkpoints (from Prof. Rex)
1. Bootstrap CI on Condition A baseline — verify power for Δρ=0.05 detection
2. Frozen-encoder sub-experiment — mandatory, not optional
3. Verify SVHN/CIFAR zoo availability before claiming P3 testability
4. Scope sign-flip to M=2 in all write-ups; flag M>2 as future work

---

*Phase: 2A - Dialogue*  
*Participants: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex*  
*Architecture: Self-Contained Tikitaka Loop (Independent-Controller Ablation)*  
*Superseded: h-e1 (DWSNets M>2 hard constraint)*  
