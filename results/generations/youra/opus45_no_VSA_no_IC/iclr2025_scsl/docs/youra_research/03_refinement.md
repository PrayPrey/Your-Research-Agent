# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-25T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Self-Play)
- **Gap ID**: gap-1
- **Gap Title**: Unified Compression Pipeline Optimization
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 10

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 10

**Convergence Reason**: All 6 convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights
- Compression ordering effects are established but not currently predictable
- Weight distribution statistics (sparsity, kurtosis) are cheap to compute and may carry predictive signal
- Simplified scope (prune vs quantize only) enables rigorous, focused testing

### Breakthrough Moments
- Exchange 7: Simplified from 6 permutations to 2 orderings by excluding distillation
- Exchange 8: Formalized Under-If-Then-Because hypothesis structure with clear falsification

---

## Final Hypothesis

### Title
Architecture-Aware Compression Sequencing (AACS)

### Hypothesis ID
H-AACS-v1

### Core Claim
Under standard CNN architectures (ResNet-18/34), if we measure pre-compression weight distribution statistics (sparsity, kurtosis) per layer, then we can predict whether prune-first or quantize-first ordering yields higher accuracy at a fixed operating point (50% parameter reduction + INT8 quantization), because sparsity indicates noise-dominated weights that pruning removes efficiently while bimodal distributions indicate structure that quantization preserves better.

### Mechanism
1. Pre-compression weight statistics encode layer-specific structure
2. Compression techniques interact differently with weight distributions (non-commutative)
3. Layer features predict which ordering preserves accuracy better

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| P1 | Weight features correlate with ordering preference | r > 0.3 | r < 0.3 |
| P2 | Simple classifier predicts ordering | Accuracy > 55% | Accuracy ≤ 55% |
| P3 | Predicted ordering beats default | Wins >70% comparisons | No advantage |

---

## Novelty

**Key Innovation**: First predictive framework for compression ordering selection based on pre-compression weight features.

**Differentiation**:
- Prior work compares orderings empirically (arXiv 2604.04988)
- Intel/neural-compressor provides multi-technique support without ordering guidance
- This hypothesis adds the predictive component

---

## Experimental Design

| Component | Selection |
|-----------|-----------|
| **Dataset** | ImageNet-1K (10% subset) |
| **Model** | ResNet-18 (pretrained) |
| **Compression** | 50% param reduction + INT8 |
| **Features** | Weight sparsity, kurtosis |
| **Baselines** | Fixed prune-first, random, oracle |

**Total Compute**: <10 GPU-hours

---

## Limitations

- Single operating point (50%+INT8) may not generalize
- Static features only; dynamic features may be more predictive
- Layer-level analysis ignores cross-layer interactions
- CNN scope; Transformers are future work

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Layer interactions, operating point generalization |

---

## Prior Failure Context

This hypothesis explicitly avoids h-m2's failure mode:
- **No Hessian computation** (gradient/weight features only)
- **Small model** (ResNet-18, not ResNet-50)
- **Fast analysis** (<10 hours total, not hours per checkpoint)

---

*Phase 2A Complete | Ready for Phase 2B*
