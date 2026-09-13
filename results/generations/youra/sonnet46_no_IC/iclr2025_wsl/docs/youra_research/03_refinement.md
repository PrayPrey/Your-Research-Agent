# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-05T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Loop (Claude-only, IC-ablation)
- **Gap ID**: gap_1
- **Gap Title**: Unified Symmetry-Complete SSL Framework for Weight Spaces
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All 6 convergence criteria met at exchange 15 (min_exchanges). All 6 personas participated with genuine disagreement and challenge.

### Key Insights
- The gap between equivariant and SSL weight-space methods is strategic, not technical — two communities working in parallel without intersection
- Computational graph representation (not just equivariance) is the key enabler for architecture-agnostic SSL processing
- Scale equivariance contribution to cross-architecture transfer requires careful ablation — it may be smaller than expected
- The SANE-ViT pilot experiment is the critical first step — it calibrates the entire hypothesis before full training

### Breakthrough Moments
- **Exchange 6 (Prof. Rex)**: Identified that the "necessity" claim is unprovable — shifted to comparative effectiveness framing
- **Exchange 7 (Dr. Nova)**: MMD distribution shift as mechanistic evidence — added direct measurement of the proposed mechanism
- **Exchange 9 (Prof. Pax)**: Hierarchical graph representation resolves ViT-scale feasibility
- **Exchange 12 (Dr. Ally)**: Neural-graphs as existing permutation-only ablation baseline — no ScaleGMN modification needed

---

## Final Hypothesis

### Title
EquiSSL: Scale+Permutation Equivariant Self-Supervised Learning for Cross-Architecture Weight Representations

### Hypothesis ID
H-EquiSSL-v1

### Core Claim

Under the weight-space SSL setting using existing MLP+CNN model zoo checkpoints (SANE MultiZoo), if a scale+permutation equivariant graph encoder (ScaleGMN backbone with hierarchical representation for block-structured architectures) is trained with a contrastive autoencoder objective using scale/permutation augmented positive pairs, then the learned representations will achieve property prediction R² on a held-out ViT Model Zoo (no ViT training data) that is at least 0.10 above SANE baseline trained on the same data, because the computational graph representation eliminates architectural distribution shift while scale equivariance normalizes weight magnitude variation across architectures.

### Mechanism

1. **Graph representation eliminates distribution shift**: Any feedforward architecture (MLP, CNN, ViT) maps to the same node/edge schema (node=neuron, edge=weight). ViT attention projections are structurally identical to MLP linear layers at the graph level. SANE's flat tokenizer sees architecture-specific weight statistics; the graph encoder sees the same representation.

2. **Monomial equivariance handles scaling variation**: ScaleGMN's equivariant message passing maps scale-equivalent networks (same function, different neuron magnitudes) to the same invariant latent code. This is exact (by construction), not approximate (unlike SANE's augmentation).

3. **Contrastive autoencoder creates discriminative generative latent space**: NT-Xent contrastive loss separates distinct networks; reconstruction loss enables latent-space interpolation (model editing). Scale/perm augmented positive pairs exploit the natural symmetry structure of weight space.

4. **Cross-architecture generalization**: Trained on MLP+CNN zoo, EquiSSL applies to ViT checkpoints via the same graph schema with hierarchical block representation for attention heads. Linear probe on frozen z achieves meaningful R² on ViT zoo without any ViT training data.

---

## Predictions

### P1 (Primary): Cross-Architecture Property Prediction
- **Statement**: EquiSSL achieves R² on held-out ViT zoo ≥ SANE R² + 0.10
- **Test**: Linear probe on frozen z for accuracy prediction, ViT Model Zoo (250 models, no ViT training data)
- **Success Criterion**: ΔR² ≥ 0.10, p < 0.05 by paired t-test over 5 seeds
- **Falsification**: ΔR² < 0.05 on ViT zoo within noise

### P2 (Mechanism): Distribution Shift Measurement
- **Statement**: MMD(SANE, train→ViT) / MMD(EquiSSL, train→ViT) ≥ 2.0
- **Test**: RBF kernel MMD on latent distributions (MLP+CNN training set vs ViT test set)
- **Success Criterion**: Ratio ≥ 2.0

### P3 (Model Editing): Latent Interpolation
- **Statement**: Decoded midpoint z = (z_A + z_B)/2 achieves higher task accuracy than weight-space averaging (θ_A + θ_B)/2
- **Test**: 100 random MLP pairs from training zoo; graph decoder → functional model
- **Success Criterion**: Mean accuracy improvement > 0, p < 0.05 paired t-test

---

## Novelty

**What's new**: First method combining scale+permutation equivariant weight-space encoding (ScaleGMN backbone) with SSL training objectives, enabling zero-shot cross-architecture transfer to held-out ViT model families.

**vs SANE**: Exact equivariance by construction (not approximate by augmentation); computational graph (not flat tokenizer) eliminates distribution shift.

**vs ScaleGMN**: SSL training (no labels required) vs supervised. Enables application to unlabeled model zoos.

**vs Neural-graphs**: SSL cross-architecture transfer (no architecture-specific labels) vs supervised transfer.

**vs Ballerini 2025**: General model architectures (MLP/CNN/ViT) vs domain-specific (NeRF only).

---

## Experimental Design

### Datasets
- **Training**: SANE MultiZoo (MLP+CNN, ~30k models) — public, github.com/HSG-AIML/MultiZoo-SANE
- **Held-out Test**: ViT Model Zoo (250 ViT models, accuracy labels) — public, arXiv 2504.10231

### Models Compared
| Method | Equivariance | SSL | Cross-arch |
|--------|-------------|-----|-----------|
| EquiSSL | Scale+Perm (monomial) | Contrastive autoencoder | **Proposed** |
| EquiSSL-perm | Perm-only | Contrastive autoencoder | Ablation |
| SANE | None (augmentation) | Masked weight modeling | Baseline |
| ScaleGMN-supervised | Scale+Perm | None (supervised) | Upper bound |

### Experimental Ladder
1. **Pilot** (hours): SANE inference on ViT zoo → calibrate R² success threshold
2. **Training** (48-72h A100): EquiSSL + SANE + EquiSSL-perm on SANE MultiZoo, λ sweep {0.01, 0.1, 1.0, 10.0}
3. **Evaluation P1**: Linear probe on frozen z for ViT zoo accuracy prediction
4. **Evaluation P2**: MMD distribution shift measurement
5. **Evaluation P3**: Latent interpolation for model editing on 100 MLP pairs

---

## Limitations

- **ViT zoo size**: 250 models — higher variance R² estimates than large zoos. Mitigated by supplementing with Hugging Face ViT checkpoints if needed.
- **LLM-scale**: 7B+ parameter models not feasible with full-graph message passing; hierarchical extension is future work.
- **λ sensitivity**: Contrastive/reconstruction tradeoff requires ablation; results may not be robust to extreme λ values.
- **Same-task interpolation only (P3)**: Cross-task model editing not tested; would require separate analysis.

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | Self-judged at exchange 15 (min_exchanges); all 6 criteria met |
| **Clarity Verified** | Yes |
| **Feasibility Constraints** | Met — existing datasets, no new benchmarks, no synthetic data |
| **Remaining Objections** | SANE-ViT pilot required; λ sweep transparency required |

---

*Phase: 2A - Hypothesis Generation (Self-Play Loop, IC-ablation)*
*Gap: gap_1 — Unified Symmetry-Complete SSL Framework for Weight Spaces*
*Ready for: Phase 2B — Hypothesis Verification Planning*
