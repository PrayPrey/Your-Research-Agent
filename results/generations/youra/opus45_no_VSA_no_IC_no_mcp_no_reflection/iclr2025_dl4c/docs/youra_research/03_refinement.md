# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-29T12:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Self-Play)
- **Gap ID**: gap-1
- **Gap Title**: No Controlled Comparison of Feedback Granularities
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 12

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 12

**Convergence Reason**: All 6 convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights
- Feedback granularity should be conceptualized as information bandwidth (bits per gradient update)
- Error types form natural ordering reflecting distance-to-correct solution
- Process supervision principles from math reasoning transfer to code via free execution feedback

### Breakthrough Moments
- Exchange 7: Information bandwidth reframe resolved the density vs. granularity confound
- Exchange 9: Distance-to-correct principle provided principled error scoring justification
- Exchange 10: Recognition that first controlled study is contribution regardless of result direction

---

## Final Hypothesis

### Title
Reward Information Bandwidth for Code LLM Training

### Core Claim
Under PPO training of CodeLlama-7B on MBPP with fixed compute budget, if reward function provides higher information bandwidth (continuous + categorical vs. binary), then model reaches pass@1 > 0.3 in fewer training samples, because denser feedback enables gradient updates to more precisely target error-inducing code patterns.

### Mechanism
1. Higher bandwidth rewards provide more bits of information per gradient update
2. Error-type scoring creates ordered feedback: syntax=0.0, runtime=0.33, assertion=0.67, pass=1.0
3. Model learns which code patterns cause which error types (precise credit assignment)
4. Faster convergence results from more informative gradient directions

---

## Predictions

| ID | Primary | Statement | Success Criterion |
|----|---------|-----------|-------------------|
| P1 | Yes | HIGH reaches threshold faster than LOW | p < 0.05, HIGH < LOW |
| P2 | No | MEDIUM converges faster than LOW | p < 0.05, MEDIUM < LOW |
| P3 | No | HIGH shows different error distribution | Fewer syntax errors in HIGH |

---

## Novelty

**Key Innovation**: Information bandwidth framing—first to conceptualize feedback granularity as bits per gradient update.

**Differentiation from Prior Work**:
- CodeRL (2022): Binary only, no comparison
- RLTF (2023): Multi-granularity but uncontrolled infrastructure
- Let's Verify Step by Step (2023): Math domain, requires explicit annotation

---

## Experimental Design

| Component | Specification |
|-----------|---------------|
| **Model** | CodeLlama-7B-Instruct |
| **Training** | MBPP (500+ problems) |
| **Evaluation** | HumanEval (164 problems) |
| **RL Algorithm** | PPO via TRL |
| **Conditions** | LOW (binary), MEDIUM (pass_rate), HIGH (error_type + pass_rate) |
| **Seeds** | 5 per condition (15 total runs) |
| **Compute** | ~180 GPU-hours (A100) |
| **Statistics** | One-way ANOVA + Tukey HSD |

---

## Limitations

- 0.5/0.5 weighting between pass_rate and error_score is heuristic (documented, not learned)
- Single model size tested (7B)—scaling dynamics unknown
- Python-specific execution environment
- Threshold selection (pass@1 > 0.3) requires sensitivity check with 0.35

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Documented as limitations |

---

*Phase 2A Complete — Ready for Phase 2B*
