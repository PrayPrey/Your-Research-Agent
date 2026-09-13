# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-24T05:15:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (INLINE Self-Play)
- **Gap ID**: gap1-judge-execution-correlation
- **Gap Title**: Quantified Judge-Execution Correlation Across Model Scales
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 11

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 11

**Convergence Reason**: All six convergence criteria met - SPECIFIC claim, MECHANISM explained, PREDICTIONS defined (P1-P4), NOVELTY articulated, FEASIBILITY confirmed, OBJECTIONS addressed

### Key Insights
- Judge-execution disagreement may be informative signal, not just noise
- Different model scales likely fail on different code properties (FP vs FN patterns)
- Using scale disagreement as a confidence signal connects to ensemble uncertainty quantification
- Simplified FP/FN taxonomy is objective and unambiguous

### Breakthrough Moments
- Exchange 1: Reframing disagreement as signal, not noise
- Exchange 5: Simplifying error taxonomy to objective FP/FN categories
- Exchange 8: Formalizing P4 (unanimous agreement = higher confidence)

---

## Final Hypothesis

### Title
Scale-Dependent Error Patterns in LLM Code Judges

### Core Claim
Under standardized code correctness evaluation settings (fixed prompt, zero temperature, HumanEval+/MBPP+ benchmarks), if we compare LLM judges of varying scale (7B/70B/proprietary), then:
1. Judge-execution agreement increases with scale but with diminishing returns
2. Different scales exhibit systematically different FP/FN error patterns
3. Scale-ensemble outperforms the best individual judge
4. Unanimous scale agreement indicates higher verdict reliability

Because larger models develop complementary correctness heuristics during training on different code distributions.

### Mechanism
1. Models at different scales are trained on overlapping but not identical code distributions
2. Smaller models rely more on surface patterns (syntax, structure)
3. Larger models capture deeper semantic relationships but may over-generalize
4. This creates complementary error patterns
5. Ensemble combination exploits complementarity; unanimous agreement filters high-confidence cases

---

## Predictions

| ID | Prediction | Success Criterion | Falsification |
|----|------------|-------------------|---------------|
| P1 | Scale ordering with diminishing returns | 7B < 70B < proprietary; (70B-7B) > (proprietary-70B) | Linear or reversed ordering |
| P2 | Error type clustering by scale | Chi-square p < 0.05 | p > 0.10 |
| P3 | Ensemble improvement | Majority vote > best single by ≥3% | Improvement < 2% |
| P4 | Agreement = confidence | Unanimous ≥10% more accurate than split | Difference < 5% |

---

## Novelty

**Key Innovation**: First scale-controlled analysis of judge-execution error patterns, with novel insight that scale disagreement serves as a confidence signal.

**Differentiation from Prior Work**:
- Crupi et al. (2025): Tested 8 LLMs but not scale-controlled
- Wang et al. (2025) MCTS-Judge: Single-model improvement, no ensemble
- Moon et al. (2025): Identified biases but not how they differ BY scale

---

## Experimental Design

**Benchmarks**: HumanEval+ (164 problems), MBPP+ (500 problems)

**Models**:
- 7B tier: DeepSeek-Coder-7B-Instruct, CodeLlama-7B-Instruct
- 70B tier: CodeLlama-70B-Instruct
- Proprietary: GPT-4

**Baselines**:
- Random (50%)
- CodeBERTScore (~58%)
- MCTS-Judge (80%)

**Controls**: Fixed prompt (pilot-selected), temperature 0, EvalPlus execution framework

---

## Limitations

- Scope limited to algorithmic coding problems (HumanEval+/MBPP+ style)
- Python language only
- Zero-shot prompting only
- Single-function code snippets
- May not generalize to enterprise code, multi-file projects, or other languages

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None |

---

## Phase 2B Readiness

| Sub-Hypothesis | Description |
|----------------|-------------|
| SH1 (Existence) | Scale-dependent error patterns exist and are statistically detectable |
| SH2 (Mechanism) | Different scales have complementary FP/FN biases |
| SH3 (Comparison) | Deferred to Phase 5 baseline comparison |

**Open Questions**:
- Does architecture confound scale effect within 7B tier?
- How does prompt wording affect absolute accuracy levels?
- Do results hold for non-Python languages?

---

*Phase 2A Complete - Ready for Phase 2B*
