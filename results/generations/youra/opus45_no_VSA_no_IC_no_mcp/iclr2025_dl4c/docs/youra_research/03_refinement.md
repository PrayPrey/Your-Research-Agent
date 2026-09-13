# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-28T12:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Tikitaka Loop
- **Gap ID**: gap_1
- **Gap Title**: No Controlled Comparison of Feedback Types on Standard Benchmarks
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 7

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 7

**Convergence Reason**: All convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights
- Reframe from "method comparison" to "signal comparison" enables cleaner experimental conclusions
- Granularity ablation (binary vs detailed feedback) tests the mechanism directly
- Findings generalize to broader RLHF vs RLAIF debate about verifiable rewards

### Breakthrough Moments
- Dr. Nova's reframe: information density and timing perspective
- Prof. Rex's granularity ablation suggestion completed experimental design
- Dr. Sage's positioning as verifiable vs proxy reward study elevated significance

---

## Final Hypothesis

### Title
Execution Feedback vs AI Feedback for Code Generation Alignment

### Hypothesis ID
H-ExecVsAI-v1

### Core Claim
Under iterative code generation refinement on standard benchmarks (HumanEval, MBPP), if feedback is provided by execution (compiler + tests) versus AI critique (instruction-tuned LLM), then execution feedback will yield higher pass@1 rates, because execution provides ground-truth counterfactual error localization that AI critique must approximate.

### Mechanism
1. Execution feedback provides counterfactual information — "if X were different, Y would not have failed"
2. Counterfactual information enables targeted code edits rather than global rewrites
3. Targeted edits have higher probability of fixing bugs than global rewrites

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| P1 (Primary) | Exec-detailed > AI-critic > Exec-binary on pass@1 | Ordering holds on 2/2 benchmarks, p<0.05, d>0.3 | AI matches execution |
| P2 | Execution advantage larger on complex tasks | Significant interaction effect (p<0.05) | Constant or inverted effect |
| P3 | Self-critique approaches execution-detailed | Within 5% of execution-detailed pass@1 | Self-critique at/below random |

---

## Novelty
- **Key Innovation**: First controlled comparison isolating feedback signal (not method) with granularity ablation
- **Differentiation**: Prior work (CodeRL, Self-Refine) compared methods; this compares signals
- **Significance**: Principles transfer to RLHF vs RLAIF debate, math, SQL, formal methods

---

## Experimental Design

| Component | Selection | Rationale |
|-----------|-----------|-----------|
| Benchmarks | HumanEval (164), MBPP (500) | Standard suites with automated tests |
| Models | CodeLlama-7B, StarCoder-7B | Two families for generalization |
| Conditions | Exec-detailed, Exec-binary, AI-critic, Random | 4-way comparison with ablation |
| Iterations | k=3 | Standard refinement setting |

---

## Limitations
- Results may not transfer to larger models (>13B)
- Benchmark tasks may not represent real-world distribution
- AI critic quality depends on underlying model capabilities
- Deferred: SWE-bench (repository-level) to Phase 5

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None |

---

*Phase 2A Complete — Ready for Phase 2B verification protocol design*
