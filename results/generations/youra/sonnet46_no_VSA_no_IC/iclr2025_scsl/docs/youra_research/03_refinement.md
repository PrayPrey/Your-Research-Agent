# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-21T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Independent-Controller Ablation)
- **Gap ID**: gap1
- **Gap Title**: SAM and Geometry-Aware Optimization During SSL Pre-Training for Shortcut Reduction
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 10
- **Hypothesis ID**: H-SAMSSL-v1

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 10

**Convergence Reason**: All 6 criteria met at Exchange 10. Prof. Rex raised 3 fundamental objections (annotation-free measurement requires group labels, Gatmiry's theory predicts MORE shortcuts from SAM, fake flat minima risk) — all resolved by Exchange 10 with concrete mechanisms.

### Key Insights

1. **Gatmiry conflict as empirical motivation**: Gatmiry et al. (2024) prove SAM → rank-1 simplicity bias under supervised cross-entropy. InfoNCE's uniform distribution pressure creates qualitatively different landscape dynamics. This theoretical conflict converts from a barrier into an empirical question — the central scientific motivation for the experiment.

2. **Annotation-free measurement fix**: The original approach (Izmailov spurious_feature_learning subspace extraction) requires group labels. Resolution: use linear probe loss variance as annotation-free spurious direction proxy — the same mechanism LFR (Ghaznavi 2023) validated on Waterbirds/CelebA.

3. **Distinguishable failure modes**: Fake flat minima (DGSAM failure) produces uniform landscape flattening with no worst-group improvement. True shortcut reduction produces selective flattening + improvement. Diagnostically separable by checking majority accuracy preservation.

### Breakthrough Moments

- **Exchange 6**: Prof. Rex identified that Gatmiry's theory predicts SAM increases shortcuts (rank-1 = simpler = spurious) and that the annotation-free measurement violated its own constraint
- **Exchange 7**: Dr. Nova proposed the InfoNCE landscape distinction (no single rank-1 attractor) and the LFR-proxy fix — converting both critical blockers into addressable design decisions

---

## Final Hypothesis

### Title
SAM-SSL Sharpness Anisotropy Hypothesis for Spurious Correlation Reduction

### Core Claim
Under standard SSL pre-training (SimCLR/MoCo/DINO) on spurious correlation benchmarks (Waterbirds/CelebA/CMNIST), if SAM is used as the optimizer instead of SGD/Adam during contrastive pre-training, then worst-group accuracy improves by ≥2pp on at least 2 of 3 benchmarks without group annotations, **because** SAM preferentially reduces Hessian sharpness along spurious feature directions (identified via linear-probe loss variance proxy, annotation-free), and this sharpness anisotropy reduction corresponds to reduced reliance on shortcut features in the learned SSL representations.

### Mechanism

1. **SSL pre-training creates anisotropic loss landscape**: Spurious features (low-rank, simple) correspond to sharper curvature directions than core features in the contrastive loss landscape.
2. **Linear probe loss variance identifies spurious directions without group labels**: High-loss samples under a downstream linear probe are predominantly minority group members — LFR-validated proxy mechanism.
3. **SAM reduces spurious sharpness**: In InfoNCE's landscape (distinct from supervised cross-entropy), SAM's perturbation-based optimization flattens sharper directions — potentially targeting spurious features preferentially.
4. **Reduced anisotropy → improved worst-group accuracy**: SSL representations after SAM pre-training encode spurious features less prominently → linear probe achieves higher worst-group accuracy.

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|------------------|---------------|
| **P1** (primary) | SGD-trained SSL models exhibit sharpness anisotropy (spurious > random direction sharpness), correlating negatively with worst-group accuracy | Ratio > 1.2, |r| > 0.5, p < 0.05 in ≥7/9 model-dataset pairs | Ratio ≈ 1.0 or |r| < 0.2 |
| **P2** | SAM training reduces anisotropy ratio ≥15% vs. SGD, preserving majority accuracy within 2pp | SAM ratio ≤ 0.85 × SGD ratio AND majority drop < 2pp in ≥2/3 datasets | SAM ratio ≥ SGD OR majority drop > 5pp (fake flat minima) |
| **P3** | SAM-trained SSL improves worst-group accuracy ≥2pp over SGD on ≥2/3 datasets | ≥2pp improvement on ≥2/3 datasets for ≥1 SSL method | < 1pp on all 3 datasets for all methods |

---

## Novelty

No prior paper has:
1. Measured Hessian sharpness anisotropy along spurious vs. core feature directions in SSL models
2. Applied SAM to SSL pre-training (SimCLR/MoCo/DINO) on Waterbirds/CelebA/CMNIST

Key differentiators from closest related work:
- **vs. G2-SAM**: G2-SAM requires group labels; we are annotation-free and target SSL pre-training
- **vs. DGSAM**: DGSAM targets domain generalization; we target spurious correlation within-distribution subgroup accuracy
- **vs. Cross-Variant SSL**: Augmentation-based; we are optimizer-based — orthogonal mechanism
- **vs. LFR/EVaLS**: Post-hoc on fixed representations; we intervene during pre-training

---

## Experimental Design

**Models**: SimCLR, MoCo-v2, DINO (all ResNet-50, 200 epochs)

**Datasets**: Waterbirds (primary), CelebA (secondary), CMNIST (secondary)

**Optimizer conditions**: SGD (baseline), SAM (rho=0.05), ASAM (rho=0.5 adaptive)

**Measurement pipeline**:
1. Train SSL model → train linear probe → identify high-loss-variance directions
2. Measure SAM perturbation loss increase: spurious directions vs. 100 random directions
3. Compute anisotropy ratio; correlate with worst-group accuracy across checkpoints
4. Evaluate worst-group accuracy via kohpangwei/group_DRO protocol

**Implementation**: davda54/sam + p-giakoumoglou/pyssl + kohpangwei/group_DRO + izmailovpavel/spurious_feature_learning

**Annotation-free constraint**: Fully satisfied — group labels used ONLY for final evaluation metrics

---

## Limitations

- ResNet-50 results may not generalize to ViT architectures (different loss landscape geometry)
- Linear probe loss variance proxy precision/recall vs. ground-truth group membership is unknown — should be validated in evaluation-only mode
- The InfoNCE landscape theoretical argument (no rank-1 attractor) is not proven — empirical outcome may show SAM increases simplicity bias even under InfoNCE
- Standard augmentation (crop/jitter/flip) does not remove spurious background content — SAM must overcome shortcuts that survive augmentation
- UrbanCars excluded from primary analysis (multi-attribute complexity)

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Hypothesis ID** | H-SAMSSL-v1 |
| **Discussion Convergence** | 10 exchanges, all 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | InfoNCE argument needs empirical confirmation (built into P1/P2); proxy precision/recall validation recommended; include ASAM variant |
| **Phase 2B Ready** | Yes |
