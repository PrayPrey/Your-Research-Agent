# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-24T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Self-Play)
- **Gap ID**: gap1-lora-rank-scaling
- **Gap Title**: Scale-Dependent LoRA Rank Optimization
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 10

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 10

**Convergence Reason**: All convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights
- Architecture confound between model families is a critical methodological concern requiring same-family comparison
- Phase transition hypothesis differentiates this from incremental tuning studies
- Attention entropy may serve as proxy for rank selection without expensive sweeps

### Breakthrough Moments
- Switching from Phi/Llama mix to Pythia-only design eliminated architecture confound
- Recognizing that 3 model sizes are insufficient for reliable α estimation (need 4+)
- Defining optimal rank operationally as 99% of rank-128 performance

---

## Final Hypothesis

### Title
Sub-Linear Scaling Law for Optimal LoRA Rank

### Hypothesis ID
H-LoRARankScaling-v1

### Core Claim
Under the Pythia model family (1B-12B parameters), if we measure optimal LoRA rank across QA tasks, then r_opt ∝ N^α where α ∈ (0.3, 0.7), because task-relevant subspace dimensionality grows sub-linearly with model capacity.

### Null Hypothesis
Optimal LoRA rank does not systematically vary with model size: α = 0 (constant rank) or α = 1 (linear scaling).

### Mechanism
Larger models have increasingly redundant parameters. Task-specific adaptation can be captured in a lower-dimensional subspace relative to total model size. This explains why low-rank adapters remain effective at scale.

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| P1 | α ∈ (0.3, 0.7) | 95% CI excludes 0 and 1 | CI includes 0 or 1 |
| P2 | Rank sensitivity >2x at 12B vs 1B | Sensitivity ratio > 2.0 | Ratio ≤ 2.0 |
| P3 | Attention entropy correlates with r_opt | r > 0.6, p < 0.05 | r ≤ 0.6 or p ≥ 0.05 |

---

## Novelty

**Key Innovation**: First systematic scaling law for LoRA rank as function of model size.

**Differentiation**:
- vs LoRA (Hu et al. 2021): LoRA introduced adaptation; we characterize optimal rank scaling
- vs RoRA (2025): RoRA fixed α/√r; we study model-size-dependent optimal rank
- vs LoRA-drop (2024): LoRA-drop prunes post-hoc; we predict optimal rank a priori

---

## Experimental Design

### Models
- Pythia-1B, Pythia-2.8B, Pythia-6.9B, Pythia-12B (same architecture family)

### Datasets
- SQuAD-v2 (single-hop QA)
- HotpotQA (multi-hop QA)
- Natural Questions (held-out validation)

### Baselines
1. Constant rank=16 (current practice)
2. Linear scaling r ∝ N
3. Full fine-tuning (upper bound)

### Design
4 model sizes × 6 LoRA ranks × 2 QA tasks = 48 experimental conditions

---

## Limitations

- **Architecture Scope**: Results apply to Pythia family only; may not transfer to Llama, Mistral, MoE
- **Task Scope**: QA tasks only; generalization to summarization, coding, generation unknown
- **Model Age**: Pythia is older architecture; modern models may behave differently

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 personas converged |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (scoped limitations acknowledged) |

---

## Phase 2B Readiness

- **SH1 (Existence)**: Sub-linear relationship exists between optimal rank and model size
- **SH2 (Mechanism)**: Task-relevant subspace dimensionality grows slower than capacity
- **SH3 (Comparison)**: Compare against constant-rank and linear-scaling baselines

**Status**: READY for Phase 2B verification protocol design
