# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-28
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Inline Discussion
- **Gap ID**: gap1
- **Gap Title**: Temporal Dynamics of Spurious Feature Learning
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 12

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 12

**Convergence Reason**: All 6 personas converged on testable hypothesis with effect size criteria

### Key Insights
- Spurious features may dominate due to faster gradient signal, not just simplicity
- Optimization hyperparameters can control spurious timing without group labels
- Loss landscape sharpness may serve as spurious-reliance proxy
- Matched control design isolates spurious-specific effects from general training dynamics

### Breakthrough Moments
- Dr. Nova's racing hypothesis sparked the gradient competition framework
- Prof. Rex's challenge on causal isolation led to matched control design
- Dr. Ally's two-phase approach resolved the ground truth dependency concern

---

## Final Hypothesis

### Title
Temporal SGD Control of Spurious Feature Emergence

### Hypothesis ID
H-TemporalSGD-v1

### Core Claim
Under standard supervised learning on datasets with spurious correlations (Waterbirds, CelebA), if we increase the learning rate or decrease the batch size, then peak spurious feature dominance will occur at later training epochs, because higher learning rates and smaller batches introduce optimization noise that disrupts the fast convergence to spurious feature reliance.

### Mechanism
1. **M1**: Spurious features produce stronger gradient signal than core features due to higher training-set correlation
2. **M2**: Higher LR and smaller batches introduce optimization noise that disrupts spurious gradient advantage
3. **M3**: Delayed spurious dominance allows more epochs for core feature learning, improving worst-group accuracy

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| P1 (Primary) | 10x LR increase shifts peak spurious dominance by >=10% of training epochs | >=5 epoch shift (50-epoch training), p < 0.05 | <=2 epoch shift |
| P2 (Primary) | Peak dominance epoch negatively correlates with worst-group accuracy | Spearman r < -0.5, p < 0.05 | r >= -0.3 |
| P3 (Mechanism) | Sharpness at peak dominance is >=2x higher than at convergence | Eigenvalue ratio >= 2.0 | Ratio < 1.5 |

---

## Novelty

**Key Innovation**: First temporal characterization of spurious feature emergence + single-stage, optimization-only robustification without group labels

**Differentiation**:
- vs. Shah et al. (2020): We measure temporal dynamics across hyperparameters, not just existence of bias
- vs. JTT (2021): Single-stage vs. two-stage; hyperparameter control vs. example reweighting
- vs. SAM (2021): Focus on spurious features, not general generalization; temporal analysis

---

## Experimental Design

| Component | Value |
|-----------|-------|
| **Dataset (Primary)** | Waterbirds |
| **Dataset (Replication)** | CelebA |
| **Model** | ResNet-50 |
| **LR Values** | 0.001, 0.01, 0.1 |
| **Batch Sizes** | 32, 128, 512 |
| **Configurations** | 9 (3 LR x 3 batch) |
| **Seeds per Config** | 5 |
| **Total Runs** | 90 (45 per dataset) |
| **Attribution Methods** | GradCAM, Integrated Gradients |

---

## Limitations

- Ground truth attribution regions needed for measurement (but not for intervention deployment)
- GradCAM may be noisy for complex scenes (mitigated by dual attribution methods)
- Hessian computation expensive at scale (mitigated by power iteration sampling)
- Results may not transfer to non-ResNet architectures or NLP

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 personas converged with STRONG verdicts |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None |

---

*Phase 2A Complete - Ready for Phase 2B*
