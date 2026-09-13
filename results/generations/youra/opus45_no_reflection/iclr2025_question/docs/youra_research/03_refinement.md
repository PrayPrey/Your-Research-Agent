# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-18
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap-1
- **Gap Title**: Efficient Token+Semantic Combination for Uncertainty Quantification
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 20

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 20

**Convergence Reason**: All 6 convergence criteria met: SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS

### Key Insights
- Hidden states may encode "knowledge confidence" distinct from output softmax confidence
- Middle layers (60% depth) are optimal based on SEP prior
- Confident-wrong detection is the critical distinguishing test
- Direct correctness prediction is a paradigm shift from uncertainty estimation

### Breakthrough Moments
- Dr. Nova's insight: probe for correctness directly, not uncertainty proxy
- Prof. Vera's falsifiability framework: inverted-U layer prediction
- Prof. Rex's stress-test: confident-wrong cases are the critical test
- Dr. Ally's synthesis: 6 pre-registered predictions with thresholds

---

## Final Hypothesis

### Title
CorrectnessProbe: Single-Pass Factual Correctness Prediction via Hidden State Probing

### Core Claim
Under the scope of factual QA tasks with objective ground-truth answers, if we train a linear probe on middle-layer (60% depth) hidden states from a transformer LLM, then the probe will predict factual correctness with AUROC >= 0.75, because middle-layer representations encode semantic knowledge before task-specific output formatting compresses this information.

### Mechanism
1. LLM receives question, generates answer through forward pass
2. Middle layers (L ≈ 0.6 × depth) encode semantic knowledge representation
3. Linear probe maps hidden states → correctness probability
4. Probe captures "knowledge confidence" distinct from output softmax confidence

---

## Predictions

| ID | Prediction | Success Criterion | Falsification |
|----|------------|-------------------|---------------|
| P1 | Middle layer (60%) achieves highest AUROC | L60% > L100% and L60% > L25% | Final layer is best |
| P2 | Early layers (12.5%) AUROC < 0.60 | L12.5% < 0.60 | L12.5% > 0.65 |
| P3 | Probe > token entropy by >= 5 pts | AUROC gap >= 5 | Gap <= 0 |
| P4 | Probe within 3 pts of 5-sample SE | Gap <= 3 | Gap > 5 |
| P5 | Confident-wrong detection AUROC > 0.60 | AUROC > 0.60 | AUROC <= 0.55 |
| P6 | TruthfulQA transfer AUROC >= 0.70 | AUROC >= 0.70 | AUROC < 0.65 |

---

## Novelty

**Key Innovation**: First work to train probes for direct factual correctness prediction rather than uncertainty estimation.

**Differentiation**:
- SEP (Kossen, 2024) predicts semantic entropy; we predict correctness directly
- Token entropy uses output distribution; we use hidden states with richer signal
- Multi-sample SE requires 5-20 samples; we achieve similar AUROC in one pass

---

## Experimental Design

**Dataset**: TriviaQA (train), TriviaQA dev + Natural Questions + TruthfulQA (test)

**Model**: Llama-3-8B-Instruct

**Baselines**:
- Token entropy (~0.65 AUROC)
- Sequence probability
- 5-sample semantic entropy (~0.80 AUROC)

**Compute**: ~30-40 GPU-hours on A100

---

## Limitations

- Single model family (Llama-3) - cross-architecture generalization not validated
- Exact-match labels may penalize correct answers with different phrasing
- Training requires labeled QA data
- Small sample sizes in TruthfulQA stratified buckets

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
