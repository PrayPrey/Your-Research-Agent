# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-28T12:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Tikitaka (Independent Controller Ablation)
- **Gap ID**: Gap-1
- **Gap Title**: Static Analysis Feedback Formatting for LLM Consumption
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 10

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 10

**Convergence Reason**: All 6 convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights

1. Raw compiler errors may be suboptimal for LLM consumption due to representational mismatch with training distribution
2. Verbose-raw baseline essential to isolate format effects from length effects
3. Scrambled condition tests whether section structure itself matters vs just information content
4. Fix specificity likely shows inverted-U pattern based on HCI research on worked examples

### Breakthrough Moments

1. Dr. Nova: "LLMs aren't compilers, so format errors for language models not compilers"
2. Prof. Rex: Addition of scrambled condition to isolate structure vs verbosity
3. Dr. Ally: Operationalization of fix specificity into 4 levels (none, general, pattern, exact)

---

## Final Hypothesis

### Title
Structured Error Formatting for LLM Self-Repair

### Core Claim
Under the setting of LLM self-repair on code generation benchmarks (HumanEval+, MBPP+), if static analysis errors are formatted as structured templates with intermediate-specificity fix suggestions, then repair success rates will improve over raw compiler output, because structured formatting reduces the representational gap between compiler output and LLM training distribution while intermediate hints provide useful direction without creating copy-paste dependency.

### Mechanism
1. **Representational Alignment**: Structured templates transform compiler output toward LLM training distribution
2. **Information Preservation**: All diagnostic content retained, verified by reconstruction test
3. **Scaffolded Guidance**: Intermediate-specificity hints activate model knowledge without bypassing reasoning

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| P1 (Primary) | Structured > Raw/Verbose-Raw/Scrambled for repair success | p < 0.05 (BH-FDR) | Structured <= Raw OR Structured = Scrambled |
| P2 | Inverted-U fix specificity (Levels 1-2 > 0, 3) | Significant quadratic term | Monotonic OR no effect |
| P3 | Larger format benefits for smaller models | Significant interaction | No interaction OR reversed |

---

## Novelty

**Key Innovation**: First systematic study of error message FORMAT for LLM self-repair. Prior work focuses on WHETHER to include compiler feedback; we study HOW to format it.

**Differentiation**:
- CompCoder (2024): Studies training-time feedback; we study inference-time formatting
- Self-Repair (ICLR 2024): Varies repair presence; we vary format with repair constant
- InspectCoder (2025): Compares static vs dynamic; we vary format within static

---

## Experimental Design

**Dataset**: HumanEval+, MBPP+ (EvalPlus) - 80x more test cases than original

**Models**: CodeLlama-7B, CodeLlama-34B, GPT-4

**Design**: 4 (Format) x 4 (Fix Specificity) x 3 (Model) x 3 (Error Type) factorial

**Baseline**: Raw compiler output via theoxo/self-repair codebase

**Primary Metric**: Repair success rate (fixed / attempted)

---

## Limitations

1. Results may not generalize to production codebases (longer, more complex)
2. Format preferences may differ across model families (only testing CodeLlama + GPT-4)
3. Does not address whether format preferences are learnable vs fixed
4. Python only; other languages not tested

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (addressed during discussion) |

---

## Phase 2B Readiness

- **SH1 (Existence)**: Error format transformation mechanism implementable as preprocessing
- **SH2 (Mechanism)**: Representational alignment + scaffolded guidance
- **SH3 (Comparison)**: Compare against raw compiler output baseline

**Open Questions for Future Work**:
- Are format preferences universal or model-family-specific?
- Can optimal formats be learned automatically?
- Does format interact with repair strategy (single-shot vs iterative)?
