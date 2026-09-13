# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-19T00:01:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: GAP-1
- **Gap Title**: Systematic Comparison of Verification Signal Types
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 17

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 17

**Convergence Reason**: All 6 convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights

- Signal effectiveness is not monolithic—Actionable Specificity decomposes it into measurable components (Localization, State Exposure, Causal Context)
- Causal context (traces) may matter more than raw state exposure (variable values)
- Optimal information level may exist—too much trace can overwhelm context
- Error category is a confound that must be controlled, not a variable of interest

### Breakthrough Moments

- Exchange 3: Dr. Sage reframed from "which signal" to "why signals work"
- Exchange 5: Dr. Ally proposed AS formula as objective operationalization
- Exchange 7: Dr. Nova proposed manipulation check (signal variants) for causality
- Exchange 13: Dr. Nova proposed learning AS weights from data (empirical finding)

---

## Final Hypothesis

### Title
Actionable Specificity: Decomposing Feedback Effectiveness for LLM Code Repair

### Core Claim
Under LLM-based iterative code repair on standard benchmarks (HumanEval, MBPP), if verification signals provide higher Actionable Specificity—decomposed into Localization (AS_loc), State Exposure (AS_state), and Causal Context (AS_causal)—then single-attempt repair success rates increase, because informationally richer feedback enables the model to localize bugs and infer correct fixes.

### Mechanism
1. Verification signal generated from failed test execution
2. Signal encodes AS components: location (file:line), variable states, execution trace
3. LLM parses AS information to localize bug and infer correction
4. Higher AS → more precise localization → higher single-attempt repair success

---

## Predictions

| ID | Statement | Test Method | Success Criterion |
|----|-----------|-------------|-------------------|
| P1 (Primary) | AS components collectively predict repair success | Likelihood ratio test | p < 0.05 |
| P2 | Full trace > error message by ≥5pp on assertion errors | Two-proportion z-test | Δ ≥ 5pp, p < 0.05 |
| P3 | Value-masked trace > syntax baseline by ≥5pp | Two-proportion z-test | Δ ≥ 5pp, p < 0.05 |
| P4 | Optimal trace length exists (~20-50 lines) | Quadratic term test | β_AS² < 0, p < 0.05 |

---

## Novelty

**Key Innovation**: Actionable Specificity framework—first systematic decomposition of feedback effectiveness into measurable components with empirical quantification of relative importance.

**Differentiation from Prior Work**:
- DebugRepair [2026]: Showed traces > messages but didn't decompose mechanism
- TyFlow [2025]: Type-specific; AS framework generalizes across all signal types
- How Many Tries [2026]: Measured difficulty by error category; AS explains via feedback properties

---

## Experimental Design

**Datasets**: HumanEval (164 problems), MBPP (500 problems)

**Model**: GPT-4 or Claude 3.5 Sonnet (temperature=0)

**Conditions** (6-level factorial):
| Condition | Description | AS_loc | AS_state | AS_causal |
|-----------|-------------|--------|----------|-----------|
| C1 | Full runtime trace | 1 | High | High |
| C2 | Truncated trace (10 lines) | 1 | Medium | Medium |
| C3 | Value-masked trace | 1 | 0 | High |
| C4 | Runtime error message | 1 | Low | 0 |
| C5 | Static analysis (mypy/pylint) | 1 | Low | 0 |
| C6 | Syntax error only | 1 | 0 | 0 |

**Analysis**: Mixed-effects logistic regression + Cox survival model

---

## Limitations

- Single LLM tested (may not generalize across models)
- Python-specific (trace mechanisms differ by language)
- Academic benchmarks (may not reflect production code complexity)
- API cost limits sample size for exploratory analyses

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | 17 exchanges, all criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None |

---

*Phase: 2A - Hypothesis Generation (Dialogue)*
*Ready for: Phase 2B - Research Planning*
