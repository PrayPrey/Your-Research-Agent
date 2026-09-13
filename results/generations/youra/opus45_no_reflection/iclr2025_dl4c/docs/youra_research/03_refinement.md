# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-18T13:45:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap_1_controlled_comparison
- **Gap Title**: No Controlled Comparison of Execution vs AI Feedback
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All 6 convergence criteria met: SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS

### Key Insights
- Execution feedback and AI feedback operate along **orthogonal dimensions** (fidelity vs semantic richness), not as direct competitors
- Verification gating can convert low-fidelity AI feedback to high-fidelity signals
- Problem error type (syntactic vs semantic) **moderates** feedback type effectiveness

### Breakthrough Moments
- Exchange 7: Dr. Nova proposed EVAF as creative synthesis of execution gating + AI feedback
- Exchange 9: Dr. Sage framed as RLVF (RL from Verified Feedback) paradigm
- Exchange 12: Prof. Rex identified accept rate as key diagnostic metric

---

## Final Hypothesis

### Title
Execution-Verified AI Feedback for Code Generation (H-EVAF-v1)

### Core Claim
Under post-training alignment of code generation models using CodeT5-770M on HumanEval/MBPP benchmarks, if we apply Execution-Verified AI Feedback (EVAF)—where AI-generated code critiques are filtered through unit test execution before being used as training signals—then EVAF will achieve significantly higher pass@1 than pure execution feedback on problems where the baseline model primarily fails due to semantic errors (incorrect logic rather than syntax/runtime errors), because EVAF combines ground-truth verification (filtering out hallucinated AI suggestions) with rich semantic guidance (explaining WHY code is wrong), addressing the orthogonal dimensions of signal fidelity and semantic richness that neither pure approach satisfies alone.

### Mechanism
1. AI feedback generator produces semantically rich code critique
2. Some AI suggestions are incorrect (~61% wrong fix rate per Self-Refine analysis)
3. Execution gating applies AI suggestion tentatively and runs unit tests
4. Suggestions that break tests are rejected; those maintaining correctness are accepted
5. Filtered feedback retains semantic richness while achieving high fidelity
6. Model learns both WHAT to fix (execution) and HOW to fix it (semantic guidance)

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| P1 | On semantic-error-prone problems, EVAF > Exec-Fine | OR ≥ 1.5, p < 0.05 | EVAF ≤ Exec-Fine or CI includes 1.0 |
| P2 | On semantic-error-prone problems, EVAF > AI-Only | p < 0.05 | EVAF ≤ AI-Only |
| P3 | On syntactic-error-prone problems, Exec-Fine ≈ EVAF | Within 3pp | EVAF >> Exec-Fine |

---

## Novelty

**Key Innovation**: The fidelity × richness decomposition—execution and AI feedback are not competitors but operate along orthogonal dimensions. EVAF uses execution as a gating mechanism for AI feedback rather than as an alternative to it.

**Differentiation from Prior Work**:
- vs CodeRL/RLTF: These use pure execution feedback; lack semantic richness
- vs Self-Refine: Uses pure AI feedback; lacks fidelity guarantee (61% wrong fix rate)
- vs CodeT: Uses LLM-generated tests for ranking, not AI feedback for training

---

## Experimental Design

### Conditions
| Condition | Fidelity | Richness | Implementation |
|-----------|----------|----------|----------------|
| Exec-Coarse | High | Low | CodeRL-style episode reward |
| Exec-Fine | High | Medium | RLTF-style line-level error |
| AI-Only | Variable | High | Self-Refine distilled to training |
| EVAF | High | High | AI feedback + execution gate |

### Benchmarks
- **Primary**: HumanEval (164 problems)
- **Transfer**: MBPP (500 test problems)
- **Headroom**: APPS (5000 test problems)

### Statistical Analysis
Mixed-effects logistic regression with problem-level random effects. Report odds ratios with 95% confidence intervals.

---

## Limitations

- Execution gating only works for correctness-affecting suggestions (not style/design)
- Test suite completeness limits verification quality (~7 tests/problem in HumanEval)
- AI feedback generator quality bounds maximum improvement
- Computational overhead: 2x inference + test execution
- Accept rate may be too low, causing EVAF to degenerate to pure execution feedback

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met after 15 exchanges |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Accept rate monitoring; benchmark saturation on HumanEval |

---

*Phase 2A Complete. Ready for Phase 2B.*
