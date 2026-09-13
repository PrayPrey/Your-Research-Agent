# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-05-20T00:00:00
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap_1
- **Gap Title**: No Unified Robustification Framework Spanning Multiple Learning Paradigms
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 16
- **Hypothesis ID**: H-GSB-v1

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 16

**Convergence Reason**: All six convergence criteria met — SPECIFIC core claim, MECHANISM (gradient SNR → representational suppression), PREDICTIONS (P1–P3 with quantitative thresholds), NOVELTY (annotation-free + cross-paradigm + temporal specificity), FEASIBILITY (100–120 GPU-hours on existing benchmarks), OBJECTIONS (clustering validity, pretraining confound, directionality, SSL mediation all addressed).

### Key Insights

1. The gradient SNR mechanism provides a paradigm-agnostic explanation for shortcut learning, unifying supervised ERM, SSL, and contrastive paradigms under one theoretical lens.
2. Annotation-free cluster direction discovery (GEORGE-style penultimate-layer k-means) enables SNR measurement without group labels — making the intervention practical.
3. The "critical period" framing (spectral entropy decrease during epochs 1–10) connects shortcut learning to broader representation learning dynamics.
4. DFR's post-hoc repair success paradoxically validates the mechanism: invariant features ARE richly encoded but suppressed — exactly what GSB addresses preventively.
5. Every challenge from Prof. Rex and Prof. Vera was converted into a sharpened prediction rather than a limitation.

### Breakthrough Moments

- **Exchange 4** (Prof. Rex): Identifying annotation-free direction discovery as the prerequisite for the whole mechanism — not a side detail.
- **Exchange 6** (Dr. Ally): Using DFR's empirical success as positive evidence for invariant feature presence (Assumption A3).
- **Exchange 9** (Prof. Rex): The adversarial-orthogonal direction control — hardest and most creative specificity test.
- **Exchange 10** (Dr. Nova): Augmentation strength as continuous SSL modulation control — elegant natural experiment.
- **Exchange 16** (Dr. Nova): Spectral entropy as scalar "critical period" measure — zero additional compute.

---

## Final Hypothesis

### Title
**Gradient SNR Balancing (GSB): Annotation-Free Early-Phase Intervention for Cross-Paradigm Shortcut Robustification**

### Core Claim
Under spurious-correlation settings with pretrained backbone initialization (supervised ERM, SimCLR-style SSL, and contrastive learning on Waterbirds, CelebA, ColoredMNIST), if gradient SNR is equalized along annotation-free cluster-discovered spurious feature directions during early training (epochs 1–10) via Gradient SNR Balancing (GSB), then worst-group accuracy improves ≥5 percentage points over ERM baseline without average accuracy degradation, because early gradient SNR imbalance causally drives representational suppression of invariant features during the shortcut consolidation critical period.

**H0**: There is no significant difference in worst-group accuracy between early-only GSB and ERM after controlling for matched-magnitude random subspace gradient balancing, and early gradient SNR ratio does not predict final worst-group accuracy with Spearman ρ > 0.5 across paradigms.

### Mechanism

1. **Direction Discovery**: k-means clustering on pretrained penultimate-layer embeddings at epoch 5 recovers spurious feature axes (top-k Fisher subspace, k≤5). Validity: AMI≥0.5, purity≥75% on Waterbirds/CelebA.
2. **SNR Imbalance**: During epochs 1–10, gradient SNR along spurious directions exceeds that along invariant directions (ratio > 1.5) — optimization's "simplicity bias" in gradient geometry.
3. **Critical Period**: Spurious-direction variance rises, invariant-direction variance falls; Fisher eigenspectrum entropy decreases (spectral compression = shortcut consolidation).
4. **GSB Intervention**: Equalizing SNR during this critical window reverses invariant feature suppression, measurable via CKA divergence from ERM and three-curve variance trajectories.

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| **P1** (primary) | Early-only GSB improves worst-group accuracy ≥5pp over ERM and ≥5pp over random-direction control on Waterbirds/CelebA | ≥5pp improvement, p<0.01, ≥5 seeds | GSB ≤ ERM+5pp OR random control achieves ≥70% of GSB's improvement |
| **P2** | Early SNR ratio (epoch 5) predicts final worst-group degradation with Spearman ρ>0.7 across supervised and SSL paradigms without retuning | ρ>0.7 in both paradigms, same threshold | ρ<0.5 in either paradigm, or different thresholds required per dataset |
| **P3** | SimCLR augmentation strength monotonically reduces spurious SNR (ρ≤−0.8) and improves accuracy (ρ≥0.8) with full mediation (direct effect p>0.1 controlling for SNR) | All correlation thresholds met + mediation completeness | Augmentation retains significant direct effect after controlling for SNR |

---

## Novelty

**What's New**: First combination of (a) annotation-free spurious direction discovery, (b) early-phase temporal specificity with critical period evidence, (c) representation-geometry mechanistic evidence via CKA + variance trajectories, and (d) cross-paradigm validation via SSL augmentation modulation. No prior work combines all four.

**vs. GroupDRO**: Requires no group annotations; intervenes at gradient geometry level during representation formation (not loss level)

**vs. DFR**: Preventive (epochs 1–10) rather than post-hoc; extends to SSL; provides mechanistic account

**vs. JTT**: Uses gradient geometry (paradigm-agnostic) rather than loss-based proxy (paradigm-specific)

**vs. Robinson et al. 2023**: Provides an intervention (not just diagnosis) with mechanistic account

---

## Experimental Design

| Component | Specification |
|-----------|---------------|
| **Primary datasets** | Waterbirds (bird-background), CelebA (hair-gender), ColoredMNIST (digit-color) |
| **Architecture** | ResNet-50 (primary), ViT-B (secondary) |
| **Baselines** | ERM, GroupDRO, JTT, DFR, SimCLR+linear probe |
| **Conditions** | ERM, early-only GSB, late-only GSB, full GSB, block-matched random, adversarial-orthogonal |
| **Seeds** | ≥5 per condition |
| **Compute** | ~100–120 GPU-hours on single A100 (1 week) |
| **Annotations needed** | None for training; ground-truth groups used only for evaluation |

**Key Ablations**:
- 2×2 factorial: {pretrained, random init} × {early GSB, ERM baseline} — isolates optimization dynamics from pretraining prior
- Timing ablation: early-only vs. late-only vs. full GSB — establishes critical period
- Three directional controls: isotropic, block-matched, adversarial-orthogonal — establishes directional specificity
- SSL modulation: 5 augmentation strengths × ≥3 seeds + bootstrapped mediation

---

## Limitations

- Pretrained backbone required for epoch-5 cluster validity (tested via factorial but not eliminable)
- Mechanism characterized for binary/low-cardinality spurious attributes; high-cardinality case requires future work
- RL extension explicitly out of scope (requires known state factorization)
- Foundation model scale (LLM/LMM) not tested
- Partial SSL mediation (if found) requires nuanced reporting rather than clean confirmation

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Hypothesis ID** | H-GSB-v1 |
| **Discussion Convergence** | 16 exchanges, all 6 criteria met |
| **Clarity Verified** | Yes |
| **Annotation-Free** | Yes (no group labels for training or discovery) |
| **Existing Benchmarks Only** | Yes (Waterbirds, CelebA, ColoredMNIST) |
| **Remaining Objections** | Pretrained dependency (tested), partial SSL mediation (reportable), RL (out of scope) |
| **Phase 2B Ready** | Yes |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
*Pipeline: YouRA — Spurious Correlations and Shortcut Learning*
*Gap addressed: Gap 1 — No Unified Robustification Framework Spanning Multiple Learning Paradigms*
