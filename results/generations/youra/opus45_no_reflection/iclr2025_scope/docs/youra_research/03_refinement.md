# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-18T13:50:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap1
- **Gap Title**: Systematic Comparison of Distillation Methods Across Sequence Lengths
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 17

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 17

**Convergence Reason**: All 6 convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights
- Distillation methods encode different theories of what makes attention work
- Length extrapolation is the practical use case for Transformer-to-SSM conversion
- Token-level representations may be more robust to extrapolation than attention maps

### Breakthrough Moments
- Reframing from "which method is best" to "when is each method best"
- Recognizing length extrapolation as the key experimental condition
- Identifying attention entropy as pre-experiment diagnostic

---

## Final Hypothesis

### Title
Length-Dependent Distillation Objectives for Transformer-to-Mamba Conversion

### Hypothesis ID
H-LenDistill-v1

### Core Claim
Under the setting of distilling a pretrained Transformer (Phi-1.5) into a Mamba-based architecture (Phi-Mamba) for long-context NLU tasks, if we compare token-level distillation objectives (CAB-style Q/K→C/B alignment) versus matrix-level objectives (MOHAWK-style attention map matching), then token-level objectives achieve superior F1 retention at extrapolated sequence lengths (≥16K) while matrix-level objectives achieve comparable or better performance at in-distribution lengths (≤4K), because token-level representations capture the functional structure of attention that generalizes to unseen lengths, whereas matrix-level objectives overfit to specific attention values that degrade under length extrapolation.

### Mechanism
1. **Training Distribution Bound**: Phi-1.5 was trained on 2048-length sequences; attention patterns at 16K-32K are extrapolations
2. **Representation Robustness**: Token-level Q/K projections encode local attention "intent" that transfers; full attention maps at extrapolated lengths contain extrapolation noise
3. **Objective-Task Match**: Token-level alignment transfers robust local representations; matrix-level alignment captures noise alongside signal

---

## Predictions

| ID | Primary | Statement | Success Criterion |
|----|---------|-----------|-------------------|
| P1 | Yes | At 4K, matrix-level ≥ token-level (within 2 F1 points) | (Matrix - Token) ≥ -2 |
| P2 | Yes | At 16K, token-level > matrix-level by ≥3 F1 points | (Token - Matrix) ≥ 3 |
| P3 | Yes | At 32K, token-level > matrix-level by ≥5 F1 points | (Token - Matrix) ≥ 5 |
| P4 | No | Hidden state drift slope higher for matrix-level | Significant at p<0.05 |

---

## Novelty

**Key Innovation**: First controlled comparison of distillation objective types (matrix vs token-level) across sequence lengths for Transformer-to-Mamba conversion.

**Differentiation**:
- MOHAWK validates matrix-level at single length; we compare across lengths
- CAB validates token-level; we test against matrix-level under controlled conditions
- Hybrid Analysis compares architectures; we compare distillation objectives

---

## Experimental Design

**Design**: 2×3 factorial (Objective Type × Sequence Length)

| Factor | Levels |
|--------|--------|
| Distillation Objective | Matrix-level, Token-level |
| Sequence Length | 4K, 16K, 32K |

**Setup**:
- Source Model: Phi-1.5 (1.3B parameters)
- Target Architecture: Phi-Mamba (modified Mamba-2)
- Training Data: C4, 1.5B tokens/condition
- Evaluation: LongBench single-document QA

**Compute**: ~9B tokens total, 8×A100, ~4 weeks

---

## Limitations

- Single source model (Phi-1.5) limits generalizability
- C4 training data may not match LongBench evaluation domain
- Hybrid objectives not tested in main hypothesis
- Results may not transfer to Mamba-1 or other SSM variants

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None |

---

*Phase 2A Complete - Ready for Phase 2B*
