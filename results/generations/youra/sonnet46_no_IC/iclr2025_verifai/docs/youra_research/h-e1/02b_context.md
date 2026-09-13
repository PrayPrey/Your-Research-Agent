# Phase 2B Context: H-E1

**Generated:** 2026-08-05 (JIT from 02b_verification_plan.md)
**Hypothesis ID:** h-e1
**Type:** EXISTENCE (MUST_WORK)

---

## Hypothesis Statement

Under HumanEval and MBPP benchmarks, if pylint/mypy static analysis feedback is applied in iterative repair mode at fixed token budget B=1000 output tokens per problem using Llama 3.1 8B Instruct, then a measurable pass@1 delta (positive, near-zero, or negative) over no-feedback baseline is produced, because any feedback mechanism that triggers re-generation creates some opportunity for improvement regardless of signal quality.

---

## Experimental Setup

### Dataset

- **Name:** HumanEval + MBPP
- **Type:** standard
- **Sources:**
  - HumanEval: Chen et al. 2021 (openai/human-eval repo); 164 algorithmic Python problems
  - MBPP: Austin et al. 2021 (google-research/mbpp repo); 374 Python problems
- **Path:** Standard benchmark loaders; available via `openai/openai_humaneval` (HuggingFace) and `evalplus/mbppplus` or direct download
- **Hypothesis Fit:** Both datasets have unit test oracles required for the execution repair condition (H-M1) and problem descriptions for pylint condition (H-E1). Full standard test sets used — 164 + 374 = 538 problems total.

### Model

- **Name:** Llama 3.1 8B Instruct (primary for H-E1)
- **Type:** Open-source instruction-tuned decoder-only transformer
- **Source:** HuggingFace: `meta-llama/Llama-3.1-8B-Instruct`
- **Hypothesis Fit:** 7B-scale instruction-tuned; Arimbur 2026 validates +9.8pp HumanEval gain from execution self-repair with prompting alone, confirming sufficient instruction-following for repair tasks.

---

## Gate Condition

- **Gate Type:** MUST_WORK
- **Pass Condition:** Pylint repair loop runs end-to-end; Δ_pylint is computable and finite (experiment runs without systematic failure)
- **Fail Action:** PIVOT — implement custom 50-100 line Python pylint wrapper if CodeEnhancer adaptation fails; if Llama 3.1 8B fails repair instructions, document and report

---

## Verification Protocol

1. Run no-feedback baseline (greedy decoding, single pass) on all HumanEval (164) and MBPP (374) problems with Llama 3.1 8B; record pass/fail per problem.
2. Run pylint/mypy repair condition: generate code → run pylint+mypy → format warnings as structured feedback → generate repair → repeat until B=1000 total output tokens consumed; record final pass/fail.
3. Compute Δ_pylint = pass@1(pylint_condition) - pass@1(no_feedback_baseline) for HumanEval and MBPP separately.
4. Run pylint+mypy on all no-feedback baseline failure cases without execution; record fraction flagged with at least one warning/error (automated coverage analysis).
5. Report: Δ_pylint value, 95% CI via bootstrap, per-round improvement trajectory (rounds 1-3), and pylint pre-execution failure coverage fraction.

---

## Success Criteria (PoC: Direction-based)

- **Primary:** Δ_pylint is computable and finite (experiment runs end-to-end without systematic failure)
- **Secondary:** |Δ_pylint| > 0 (any measurable effect, positive or negative — null result equally valid)

---

## Dependencies

- **Prerequisites:** None (foundation hypothesis)
- **Blocked By:** None
- **Controls for H-M1:** Provides pylint baseline condition for comparison with execution feedback

---

## Baseline Reference

- No-feedback baseline (greedy decoding): ~67.1% pass@1 on HumanEval for Llama 3.1 8B (Arimbur 2026)
- Execution self-repair upper bound: +9.8pp on HumanEval for Llama 3.1 8B (Arimbur 2026)
- Pylint functional correctness effect on HumanEval: empirically unknown (this experiment's contribution)
