# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-29T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Tikitaka Loop
- **Gap ID**: gap-1-static-analysis-pass-k
- **Gap Title**: Static Analysis Impact on Functional Correctness Unquantified
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 11

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 11

**Convergence Reason**: All 6 criteria met: SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS

### Key Insights
- Static analysis provides mechanistic feedback ("why" not just "where") enabling targeted repairs
- Static analysis may help even on passing solutions (patchwork problem insight)
- Non-overlap between static and execution signals is the key assumption to validate

### Breakthrough Moments
- Dr. Nova's insight that static analysis contributes EVEN WHEN TESTS PASS
- Prof. Vera's formalization of dual threshold (absolute + relative) for robustness
- Prof. Rex's stress test leading to non-inferiority check inclusion

---

## Final Hypothesis

### Title
Static Analysis Feedback for LLM Code Repair

### Core Claim
Under the condition of iterative LLM code repair on HumanEval/MBPP, if static analyzer feedback (pylint/mypy) is integrated alongside execution feedback, then pass@k will improve compared to execution-only feedback, because static analysis provides mechanistic error explanations and catches issues before execution.

### Mechanism
1. Static analyzer runs on LLM-generated code → produces warnings
2. LLM receives mechanistic feedback ("variable may be undefined") vs just location
3. More targeted repairs → higher pass@k

---

## Predictions

| ID | Primary | Statement | Success Criterion |
|----|---------|-----------|-------------------|
| P1 | ✅ | pass@1(static+exec) > pass@1(exec-only) | ≥2% absolute OR ≥5% relative |
| P2 | | Improvement concentrated in static-detectable errors | Stratified analysis shows concentration |
| P3 | | No improvement for pure logic errors | No difference on zero-warning subset |

---

## Novelty

**Key Innovation**: First study to measure static analysis impact on functional correctness (pass@k)

**Differentiation**:
- vs Blyth et al.: They measured quality; we measure pass@k
- vs Self-Debug: They use execution-only; we add static analysis

---

## Experimental Design

| Component | Selection |
|-----------|-----------|
| Dataset | HumanEval (164 problems), MBPP (974 problems) |
| Model | GPT-4 or CodeLlama-34B |
| Baseline | Self-Debug (execution-only) |
| Intervention | Add pylint warnings to repair prompt |
| Metric | pass@1, pass@5, pass@10 |

---

## Limitations

- Effect size may be small (<5%) if few HumanEval errors are static-detectable
- Model-dependent: stronger models may already capture static-like reasoning
- False positive filtering strategy needs tuning
- Pilot study required to validate signal quality

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (addressed via pilot study recommendation) |

---

*Phase 2A Complete — Ready for Phase 2B*
