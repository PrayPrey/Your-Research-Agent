# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-18
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap1_architecture_comparison
- **Gap Title**: Systematic Architecture Comparison for Data Attribution
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 7

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 7

**Convergence Reason**: All convergence criteria met: SPECIFIC core claim, MECHANISM explained, PREDICTIONS with criteria, NOVELTY articulated, FEASIBILITY established, OBJECTIONS addressed

### Key Insights
- Attention structure (bidirectional vs causal), not architecture label, is the key variable
- Different attribution methods have different sensitivity to attention structure due to approximation assumptions
- TRAK's random projections may be uniquely architecture-invariant

### Breakthrough Moments
- Prof. Pax's reframe: efficiency bottleneck is approximation method assumptions, not attention structure itself
- Dr. Ally's synthesis: method-specific predictions rather than single architecture ranking

---

## Final Hypothesis

### Title
Architecture-Aware Data Attribution: Attention Structure Determines Method Efficiency

### Hypothesis ID
H-ArchAttr-v1

### Core Claim
Under matched architectures (BERT-base 12L vs GPT-2 12L, ~110-125M params) and text classification tasks (SST-2 mislabeled detection), if we compare TRAK, EK-FAC, and TracIn attribution methods, then decoder-only GPT-2 will show better efficiency-accuracy trade-offs for EK-FAC, encoder-only BERT will show better trade-offs for TracIn, and TRAK will show minimal architecture variance, because attention structure interacts differently with each method's approximation mechanism.

### Mechanism
1. Encoder-only models (BERT) have bidirectional attention creating dense O(n²) gradient dependencies
2. Decoder-only models (GPT-2) have causal attention creating block-diagonal gradient structure
3. EK-FAC's Kronecker factorization assumption fits causal structure better
4. TracIn's gradient-only approach benefits from encoder's denser gradient signal
5. TRAK's random projections are architecture-agnostic by design

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| P1 (Primary) | EK-FAC achieves higher mislabeled detection AUC on GPT-2 than BERT at matched compute | p < 0.05, Cohen's d > 0.3 | p > 0.05 OR d < 0.3 |
| P2 | TracIn achieves higher AUC on BERT than GPT-2 at matched compute | p < 0.05, Cohen's d > 0.3 | p > 0.05 OR d < 0.3 |
| P3 | TRAK shows minimal architecture variance | p > 0.05, |diff| < 2% | p < 0.05 AND |diff| > 5% |

---

## Novelty

**Key Innovation**: First matched cross-architecture comparison of data attribution efficiency-accuracy trade-offs with predictive theory based on attention-curvature-approximation interaction.

**Differentiation from Prior Work**:
- Grosse et al. 2023: Tested EK-FAC only on decoder-only (LLaMA-2)
- Park et al. 2023: Tested TRAK on BERT and CLIP separately
- This work: Systematic matched comparison with predictive framework

---

## Experimental Design

### Models
- BERT-base-uncased (110M params, 12 layers)
- GPT-2 (124M params, 12 layers)

### Dataset
- SST-2 (GLUE benchmark) with 5% synthetic label noise

### Attribution Methods
- TRAK (random projection, via trak library)
- EK-FAC (Kronecker-factored curvature, via kronfluence)
- TracIn (first-order checkpoints, custom implementation)

### Baselines
- Random attribution
- Loss-based attribution

---

## Limitations

- **Scope**: Limited to encoder-only vs decoder-only (encoder-decoder deferred)
- **Scale**: Limited to ~100M param models (larger models deferred)
- **Tasks**: Primary evaluation on SST-2 (secondary: AG News, MNLI)
- **Generalization**: Results may not transfer to instruction-tuned or RLHF models

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (all addressed with mitigations) |

---

*Phase 2A Complete | Ready for Phase 2B*
