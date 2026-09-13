# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-29T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Tikitaka Loop
- **Gap ID**: gap-1-cross-arch-generalization
- **Gap Title**: Cross-Architecture Generalization of Weight Features
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 7

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 7

**Convergence Reason**: All 6 criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights
- Architecture-invariant features should target learning dynamics (heavy-tailed distributions), not architecture specifics
- Must explicitly beat parameter-count baseline to claim meaningful contribution
- Heavy-tailed theory for ViT is a testable sub-hypothesis, not an assumption

### Breakthrough Moments
- Prof. Rex's identification of model-size confound led to explicit baseline requirement
- Reframing from "universal features" to "transfer across architecture families"

---

## Final Hypothesis

### Title
Cross-Architecture Weight Feature Generalization for Accuracy Prediction

### Core Claim
Under collections of pretrained vision models on Hugging Face Model Hub (ResNet, ViT, ConvNeXt families), if we extract architecture-agnostic weight statistics (heavy-tailed exponent α, mean spectral norm ratio, normalized Frobenius norm) and train a single regression model, then this unified predictor achieves R² at least 0.15 higher than a parameter-count baseline when predicting ImageNet validation accuracy across architecture families, because well-trained models exhibit similar implicit self-regularization signatures (per Martin & Mahoney) regardless of architecture.

### Mechanism
1. Well-trained networks develop implicit self-regularization during training, manifesting as heavy-tailed weight distributions
2. Self-regularization signatures encode generalization quality in an architecture-invariant way
3. A unified regressor can learn the mapping from weight statistics to accuracy across architectures

---

## Predictions

| ID | Statement | Success Criterion |
|----|-----------|-------------------|
| P1 | Heavy-tailed exponents computable with bounded variance for ViT models | σ(α) < 0.5 |
| P2 | Unified regressor outperforms baseline on held-out architecture | R² ≥ baseline R² + 0.15 |
| P3 | Top 20% predicted ∩ top 20% actual > 80% per architecture | Overlap > 80% |

---

## Novelty

**Key Innovation**: First systematic evaluation of weight-feature prediction transfer across CNN/Transformer boundary

**Differentiation**:
- Unterthiner et al. (2020): Focused on CNNs only; we test cross-architecture transfer
- Martin & Mahoney (2021): Theoretical framework on older CNNs; we validate on modern architectures

---

## Experimental Design

**Dataset**: Hugging Face Model Hub (100+ models per architecture family)

**Models**: ResNet variants, ViT variants, ConvNeXt variants, Swin variants

**Baselines**:
- Parameter count regression (log scale)
- FLOPs regression
- Architecture-specific weight regressors

---

## Limitations

- Cannot control for training procedure variation without metadata
- Heavy-tailed exponent computation may be noisy for small models
- Cross-architecture transfer assumes all architectures encode similar information in weights

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Training procedure confound; effect size uncertainty |

---

*Phase 2A Complete — Ready for Phase 2B*
