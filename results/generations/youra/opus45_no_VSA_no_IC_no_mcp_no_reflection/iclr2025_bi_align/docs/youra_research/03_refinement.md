# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-28T22:15:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Self-Play Loop
- **Gap ID**: gap-1
- **Gap Title**: No Empirical Testing of Bidirectional Alignment Signals in Training
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 7

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 7

**Convergence Reason**: All 6 convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights
- Controllability and helpfulness are complementary signals, not competing objectives
- IFEval constraint satisfaction rate is a valid differentiable proxy for controllability
- Three-baseline design (SFT-only, AlpacaEval RLHF, quality-only RLHF) cleanly isolates controllability contribution
- Explicit→implicit constraint generalization is the key mechanism requiring validation

### Breakthrough Moments
- Dr. Nova's reframing of bidirectional alignment as "conditional helpfulness"
- Prof. Pax's validation that IFEval constraint satisfaction rate is mathematically valid reward
- Prof. Rex's challenge leading to held-out evaluation design and B3 baseline

---

## Final Hypothesis

### Title
Bidirectional Alignment Training (H-BiAlign-v1)

### Core Claim
Under standard RLHF fine-tuning conditions, if we augment the helpfulness reward with IFEval-derived controllability signals (R_combined = α·R_AlpacaEval + β·R_IFEval_rate), then the resulting model will achieve higher held-out instruction-following scores, maintain helpfulness, AND improve safety benchmark performance, because explicit constraint training builds general constraint-following capacity that transfers to implicit safety constraints.

### Mechanism
1. IFEval constraint satisfaction rate computed as continuous reward signal
2. Combined reward R = α·R_helpfulness + β·R_controllability optimized via PPO
3. Model learns to satisfy explicit constraints (format, length, structure)
4. Explicit constraint capacity generalizes to implicit safety constraints

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| P1 | Bidirectional models score higher on held-out IFEval | Ti > max(B1,B2,B3) + 2pp | All Ti ≤ max baselines |
| P2 | Bidirectional models maintain helpfulness | Best Ti ≥ 0.95 × B2 AlpacaEval | All Ti < 0.95 × B2 |
| P3 | Bidirectional models improve safety benchmarks | Ti improves ≥2pp on TruthfulQA OR BBQ | No ≥2pp improvement |

---

## Novelty

**Key Innovation**: Using IFEval constraint satisfaction rate as a differentiable training reward alongside helpfulness — first empirical test of Sun et al. 2024's bidirectional alignment framework.

**Differentiation from Prior Work**:
- InstructGPT: helpfulness-only RLHF; no explicit controllability signal
- Sun et al. 2024: theoretical framework without training methodology
- Constitutional AI: AI self-critique for safety; we use human-defined constraints

---

## Experimental Design

**Base Model**: Llama-3-8B-Instruct

**Datasets**:
- IFEval (70% train / 30% held-out test)
- UltraFeedback (RLHF preference pairs)
- TruthfulQA, BBQ (safety evaluation)

**Baselines**:
- B1: SFT-only (no RLHF)
- B2: RLHF with AlpacaEval reward (helpfulness)
- B3: RLHF with quality-only reward (excluding instruction adherence)

**Treatment Conditions**:
- T1-T4: RLHF with combined AlpacaEval + IFEval at α ∈ {0.2, 0.4, 0.6, 0.8}

---

## Limitations

- IFEval constraint types may not cover all controllability dimensions
- AlpacaEval GPT-4 judge has known biases (verbosity, formatting)
- Safety benchmarks are static and may be partially saturated
- Single α/β per training run; adaptive weighting not explored
- Scope limited to 7B-13B parameter range; larger models may differ

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (all addressed) |

---

*Phase 2A Complete — Ready for Phase 2B*
