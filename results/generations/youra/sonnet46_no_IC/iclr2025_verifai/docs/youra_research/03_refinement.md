# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-05T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Loop (Claude-only, IC-ablation)
- **Gap ID**: gap3
- **Gap Title**: Systematic Ranking of Formal Feedback Signal Types on Standard Code Benchmarks
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: Self-judged convergence at exchange 15; all 6 convergence criteria met; all 6 personas participated with genuine disagreement and adversarial challenge; key tensions resolved through specific operationalizations

### Key Insights
1. The iso-compute framework (fixed total output token budget per problem) is the essential methodological contribution enabling fair comparison between repair modes that differ in pass count.
2. A null result for pylint (near-zero pass@1 delta on HumanEval) is as scientifically valuable as a positive result — definitively establishing the boundary of static analysis feedback utility for functional code generation.
3. Type-constrained decoding (prevention mode) and iterative repair (correction mode) are mechanistically incompatible and must be studied separately to avoid conflation.
4. Automated pylint coverage analysis on baseline failures is a zero-annotation-cost mechanism measurement that explains why the feedback type ranking holds.
5. Production deployment implications are direct: if static analysis achieves X% of execution improvement at lower compute cost, the tradeoff is immediately actionable for coding assistant engineering teams.

### Breakthrough Moments
- **Exchange 6** (Prof. Rex): Exposed that the assumed ranking (execution > static analysis) is directionally unproven and pylint's functional correctness effect on HumanEval/MBPP is empirically unknown — reframed the hypothesis as testing the null
- **Exchange 9** (Dr. Sage): Proposed type-constrained decoding as a separate "prevention baseline" rather than a repair-mode competitor — resolved architectural incompatibility
- **Exchange 10** (Prof. Pax): Confirmed bifurcated design (primary repair comparison + secondary prevention baseline) resolves mechanistic incompatibility cleanly
- **Exchange 13** (Dr. Nova): Converted mechanism claim from assumed explanation to testable, automated measurement (pylint coverage analysis)

---

## Final Hypothesis

### Title
Iso-Compute Feedback Type Comparison for LLM Code Generation on HumanEval/MBPP

### Hypothesis ID
H-IsoComputeFeedback-v1

### Core Claim (Under-If-Then-Because)

**Under** HumanEval and MBPP benchmarks, for open-source instruction-tuned LLMs at 7B scale (Llama 3.1 8B primary; Qwen2.5-Coder-7B replication), in iterative repair mode at fixed token budget B=1000 output tokens per problem instance,

**If** formal feedback type is varied between (A) pylint/mypy static analysis feedback and (B) execution test feedback,

**Then** execution test feedback achieves a statistically significantly larger pass@1 improvement delta over no-feedback baseline than pylint/mypy feedback (McNemar's test, α=0.05 on HumanEval/MBPP),

**Because** execution feedback covers the full distribution of code errors (logic, runtime, type, syntax) while static analysis covers a subset with lower correlation to the specific logical failures that dominate HumanEval/MBPP problem types — as evidenced by automated pylint coverage analysis showing pylint detects a significantly lower fraction of HumanEval baseline failures pre-execution than execution test feedback catches.

### Null Hypothesis (H0)
There is no statistically significant difference in pass@1 improvement delta between pylint/mypy static analysis feedback and execution test feedback at equal token budget (B=1000 output tokens per problem) on HumanEval/MBPP for 7B instruction-tuned LLMs. (H0: Δ_pylint = Δ_execution)

### Mechanism (Testable Prediction)
The fraction of HumanEval/MBPP baseline failures that pylint/mypy detects pre-execution is significantly lower than the fraction that execution test feedback catches, explaining the pass@1 delta gap. Operationalized as: automated pylint+mypy run on all baseline failure cases, fraction flagged with at least one warning/error, compared to execution coverage (100% by definition).

---

## Predictions

### P1 (Primary — Ranking Comparison)
**Statement:** Execution test feedback achieves a statistically significantly larger pass@1 improvement delta than pylint/mypy feedback on HumanEval at B=1000 output tokens, using Llama 3.1 8B.  
**Test Method:** McNemar's test on paired binary outcomes (pass/fail per problem). α=0.05.  
**Success Criterion:** Δ_execution > Δ_pylint, p<0.05 on HumanEval (164 problems) AND MBPP (374 problems).  
**Falsification:** p>0.05 or Δ_pylint ≥ Δ_execution → pylint is as effective as execution (publishable null result).

### P2 (Secondary — Mechanism)
**Statement:** The fraction of HumanEval baseline failures that pylint detects pre-execution is significantly lower than what execution catches.  
**Test Method:** Automated pylint+mypy analysis on all no-feedback baseline failures; count flagged fraction.  
**Success Criterion:** Pylint flags <50% of HumanEval baseline failures, supporting the mechanism.  
**Falsification:** pylint flags >80% → informativeness gap is small, undermining mechanism claim.

### P3 (Secondary — Prevention Baseline)
**Statement:** Type-constrained decoding achieves positive pass@1 delta over unconstrained one-pass generation on HumanEval.  
**Test Method:** One-pass comparison (eth-sri implementation, Llama 3.1 8B, B=1000 tokens).  
**Success Criterion:** Δ_type_constrained > 0 (positive improvement).  
**Falsification:** Δ_type_constrained ≤ 0 → type constraints don't help on HumanEval (consistent with logic-error dominance).

---

## Novelty

**What's New:** First iso-compute head-to-head comparison of execution feedback vs. pylint/mypy static analysis feedback in iterative repair mode on standard Python functional correctness benchmarks (HumanEval, MBPP) — with automated mechanism analysis (pylint failure coverage).

**How it differs from FeedbackEval [Dai et al., 2025]:** FeedbackEval uses compiler/syntax errors (not semantic pylint/mypy); does not normalize by token budget; excludes type-constrained decoding. This paper adds semantic static analysis condition and iso-compute normalization.

**How it differs from Blyth et al. [2025]:** Blyth et al. test pylint on PythonSecurityEval (security metric, not pass@k). This paper tests on HumanEval/MBPP functional correctness and directly compares to execution feedback.

**How it differs from Mündler et al. [2025]:** Type-constrained decoding compared only to unconstrained generation. This paper treats type-constrained decoding as a separate prevention baseline and focuses the primary comparison on repair modes.

---

## Experimental Design

| Dimension | Specification |
|---|---|
| Benchmarks | HumanEval (164 problems), MBPP (374 problems) |
| Models | Llama 3.1 8B Instruct (primary), Qwen2.5-Coder-7B-Instruct (replication) |
| Token budget | B=1000 total output tokens per problem instance |
| Conditions | (1) no-feedback baseline; (2) pylint/mypy repair; (3) execution repair; (4) type-constrained one-pass [secondary] |
| Metric | pass@1 delta vs. baseline; McNemar's test (α=0.05) |
| Mechanism measure | Automated pylint coverage analysis on baseline failures |
| Repos | Johin2/iterative-code-repair (execution); cyb3rlab/CodeEnhancer adapted (pylint); eth-sri (type-constrained) |
| New benchmarks? | No — HumanEval + MBPP only |
| Human annotation? | No — all measurements automated |

---

## Limitations

- 7B-only model scope — results may not generalize to 70B models or RL-trained models
- Two models (Llama 3.1 8B, Qwen2.5-Coder-7B) provides replication but not statistical meta-analysis across model families
- Token budget B=1000 is one point; other budget values require separate experiments
- Default pylint rules (not tuned for code generation feedback utility) — future work can ablate rule categories
- HumanEval has 164 problems — adequate for 10pp detection but low power for effects <5pp
- Type-constrained decoding secondary study is one-pass only; iterative type-constrained repair would require additional engineering

---

## Decision

| Item | Status |
|---|---|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | Self-judged at exchange 15; all 6 criteria PASS; all 6 personas participated |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Pylint null result risk (expected, publishable); CodeEnhancer adaptation (2-4 days engineering); 7B generalizability scope |

---

*Phase 2A Complete — Proceeding to Phase 2B Planning*
