# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-29T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Tikitaka (independent-controller ablation)
- **Gap ID**: gap-1
- **Gap Title**: Cross-Architecture Distillation Methodology
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 12

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 12

**Convergence Reason**: All 6 convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights
- Mamba-2 duality is not just theoretical—it provides a recipe for principled Transformer→SSM conversion
- Layer-wise conversion is more tractable than end-to-end optimization
- Attention pattern entropy may predict conversion difficulty
- Success threshold should be relative to same-architecture distillation, not arbitrary absolute

### Breakthrough Moments
- Realizing closed-form SSM initialization can be derived from Mamba-2 duality equations
- Framing the underdetermined system as an optimization problem rather than exact solution
- Defining success relative to same-arch baseline (1.5x gap) rather than absolute threshold

---

## Final Hypothesis

### Title
Duality-Guided Cross-Architecture Distillation (DG-CAD)

### Core Claim
Under standard NLP tasks (classification, QA, summarization), if Transformer attention layers are converted to SSM layers using Mamba-2 duality-inspired closed-form initialization followed by layer-wise optimization, then the resulting sub-quadratic model achieves performance within 1.5x the degradation of same-architecture distillation, because the duality-preserving initialization provides a strong starting point that reduces optimization difficulty and preserves long-context reasoning structure.

### Mechanism
1. **Closed-form initialization**: Derive SSM parameters (A, B, C, Δ) from attention weights using Mamba-2 duality equations
2. **Layer-wise optimization**: Refine SSM parameters to minimize reconstruction error (100 steps/layer, calibration set 1000 samples)
3. **Fine-tuning**: Train full model on downstream task with soft labels from teacher (3 epochs)

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| P1 | DG-CAD outperforms naive KD by ≥1% on LongBench 8K | Accuracy diff ≥1%, p<0.05 | If <1% or p>0.05, no value |
| P2 | Low-entropy heads convert with <5% error | Spearman ρ ≥0.5 | If ρ<0.3, entropy not predictive |
| P3 | Short calibration generalizes to 8K | 8K/4K ratio ≥0.5 | If <0.5, poor generalization |

---

## Novelty

**Key Innovation**: First operationalization of Mamba-2 duality for practical Transformer→SSM distillation

**Differentiation**:
- vs DistilBERT: Same-architecture only → we enable cross-architecture
- vs Mamba-2: Theory only → we operationalize for practical transfer
- vs Naive KD: Black-box matching → we preserve computational structure

---

## Experimental Design

| Component | Specification |
|-----------|---------------|
| Teacher | BERT-base (12 layers, 768 dim) |
| Student | Mamba-12 (12 SSM layers, 768 state dim) |
| Calibration | 1000 sequences, 512-4096 tokens |
| Benchmarks | GLUE (short), LongBench (4K, 8K, 16K) |
| Baselines | Naive KD, Same-arch DistilBERT |

---

## Limitations

- Requires access to teacher model internals (attention weights)
- Calibration set needed (1000-5000 samples)
- Does not apply to Vision Transformers or MoE models
- Entropy threshold needs empirical calibration from data

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (minor refinements: entropy threshold, calibration size ablation) |

---

*Phase 2A Complete | Ready for Phase 2B*
