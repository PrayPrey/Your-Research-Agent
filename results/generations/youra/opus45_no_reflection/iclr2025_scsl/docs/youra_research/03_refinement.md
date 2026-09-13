# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-18T23:55:00
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap1_temporal_measurement
- **Gap Title**: Explicit Temporal Measurement of Feature Learning Order
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 9

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 9

**Convergence Reason**: All 6 convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights
- Emergence uniformity (not absolute timing) distinguishes spurious from core features
- CV of probe accuracy trajectories across subsets is a measurable uniformity metric
- Gradient regularization in probe-defined directions can suppress spurious feature learning

### Breakthrough Moments
- Exchange 7: Dr. Nova's reframing from "early = spurious" to "uniform = spurious"
- Exchange 8: Prof. Vera's formalization with CV threshold and falsification criteria

---

## Final Hypothesis

### Title
Emergence Uniformity Regularization (EUR) for Annotation-Free Worst-Group Robustness

### Hypothesis ID
H-EUR-v1

### Core Claim
Under the Waterbirds/CelebA/ColoredMNIST benchmarks where spurious correlations cause poor worst-group performance, if we identify features by their emergence uniformity (low variance in probe learning rates across sample subsets, CV < 0.15) and apply gradient regularization proportional to uniformity, then worst-group accuracy improves by ≥5 percentage points over ERM, because uniform emergence indicates the feature is spuriously correlated with labels rather than discriminative.

### Mechanism
1. **Detection**: Train linear probes on CLIP features at epoch checkpoints. Compute CV of accuracy improvement rates across 5 random 20% sample subsets.
2. **Classification**: Features with CV < 0.15 classified as likely spurious; CV > 0.2 as likely core.
3. **Intervention**: Apply gradient penalty λ*(grad·probe_direction)² to low-CV feature directions.

---

## Predictions

| ID | Statement | Success Criterion |
|----|-----------|-------------------|
| P1 | EUR achieves ≥5 pp worst-group improvement on Waterbirds | Improvement ≥5 pp over ERM |
| P2 | EUR achieves ≥3 pp worst-group improvement on CelebA | Improvement ≥3 pp over ERM |
| P3 | EUR achieves ≥3 pp worst-group improvement on ColoredMNIST | Improvement ≥3 pp over ERM |
| P4 | Average accuracy drop ≤2 pp | Drop ≤2 pp across all datasets |

---

## Novelty

**Key Innovation**: First method to use emergence uniformity (not timing) as spuriousness signal; single-run dynamic regularization unlike JTT's two-stage approach.

**Differentiation from Prior Work**:
- JTT (Liu et al., 2021): Two-stage training → EUR is single-run
- LfF (Nam et al., 2020): Separate biased/debiased networks → EUR uses single network
- Simplicity Bias (Shah et al., 2020): Proves bias exists → EUR exploits it for intervention

---

## Experimental Design

**Primary Dataset**: Waterbirds (95% background-label correlation)
**Additional Datasets**: CelebA (blond hair / gender), ColoredMNIST
**Model**: ResNet-50 (ImageNet-pretrained)
**Feature Extractor**: CLIP ViT-B/16

**Baselines**:
- ERM (lower bound): ~70% worst-group accuracy
- JTT (annotation-free SOTA): ~86% worst-group accuracy
- Group DRO (oracle): ~91% worst-group accuracy

---

## Limitations

- Requires pretrained feature extractor (CLIP or similar)
- CV threshold (0.15) may need tuning for new domains
- Assumes probe directions align with actual feature learning directions
- Does not apply to tasks where core and spurious features have similar complexity

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | CV threshold sensitivity, CLIP bias, λ calibration |

---

## Null Hypothesis

There is no significant difference in worst-group accuracy between EUR (Emergence Uniformity Regularization) and standard ERM training on spurious correlation benchmarks.

---

*Phase 2A Complete. Ready for Phase 2B hypothesis verification planning.*
