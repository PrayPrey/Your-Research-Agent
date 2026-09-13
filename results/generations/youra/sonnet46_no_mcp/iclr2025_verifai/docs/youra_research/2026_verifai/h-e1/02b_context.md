# Phase 2B Context: H-E1 (JIT Generated)

**Hypothesis ID:** h-e1
**Type:** EXISTENCE
**Gate:** MUST_WORK
**Status:** IN_PROGRESS

---

## Hypothesis Statement

Under the Python-native evaluation environment with HumanEval (164 problems) and MBPP (374 problems), if SynCode, z3-solver, and mypy/ast are pip-installed and CodeLlama-7B is loaded via HuggingFace with device='auto', then all three formal repair tools operate correctly on Python code generation tasks (SynCode reduces ast.parse failures, z3-solver encodes ≥15% of HumanEval problems as SMT constraints, mypy.api.run() returns structured type errors) because these tools are pip-installable with Python-native APIs confirmed operational in prior work.

## Rationale

H-E1 establishes the existence precondition for all mechanism hypotheses. Without confirmed tool operationality and benchmark infrastructure, no complementarity measurement is possible. This is the foundational MUST_WORK gate — failure means the experiment cannot proceed at all.

## Variables

- **Independent:** Formal repair tool identity (SynCode / z3-solver / mypy/ast)
- **Dependent:** Tool operational status (ast.parse failure rate under SynCode, Z3 encoding eligibility rate, mypy structured error output)
- **Controlled:** CodeLlama-7B (fixed weights, device=auto), HumanEval + MBPP benchmark access via evalplus pip

## Experimental Setup (from Phase 2A Dialogue)

**Dataset:**
- Name: HumanEval (164 problems) + MBPP (374 problems)
- Type: standard
- Source: openai/human-eval GitHub; evalplus/evalplus GitHub; via `pip install evalplus`
- Path: Available via evalplus pip package (`evalplus.data.get_human_eval_plus()`, `evalplus.data.get_mbpp_plus()`)
- Hypothesis Fit: Python-native test runners with no Docker dependency; existing pass@k evaluation infrastructure; MBPP provides held-out test set for RSS evaluation

**Model:**
- Name: CodeLlama-7B
- Type: Decoder-only LLM (code-specialized)
- Source: HuggingFace: codellama/CodeLlama-7b-hf
- Loading: `AutoModelForCausalLM.from_pretrained("codellama/CodeLlama-7b-hf", device_map="auto")`
- Hypothesis Fit: Available via HuggingFace with device='auto' CPU fallback; SynCode supports HuggingFace models via LogitsProcessor wrapper

## Baseline & Comparison Targets

- **SynCode:** Expected to reduce ast.parse failure rate (directional improvement from baseline)
- **Z3:** Encoding eligibility ≥15% of HumanEval problems (scope condition for cascade claim)
- **mypy:** Structured error output on ≥90% of attempted problems
- **Baseline (unconstrained CodeLlama-7B):** ~30–45% pass@1 on HumanEval [INFERRED]

## Prerequisites

None (H-E1 is the foundation hypothesis — first in chain)

## Success Criteria

**Primary (PoC: Direction-based):**
- SynCode-generated code shows lower ast.parse failure rate than baseline (directional, any reduction)

**Secondary:**
- Z3 eligibility ≥ 15% of HumanEval problems (scope condition for cascade claim)
- mypy.api.run() returns parseable structured errors on ≥ 90% of attempts

## Failure Response

- IF Z3 eligibility < 15%: SCOPE REDUCTION — drop cascade/Z3 claims; focus on SynCode + mypy complementarity
- IF SynCode has no effect: PIVOT — reassess SynCode integration with current CodeLlama-7B version
- IF mypy API fails: EXPLORE — alternative static analysis (pyflakes, ast-only) as fallback

## Verification Protocol (from Phase 2B)

1. Install all tools (syncode, z3-solver, mypy, evalplus) via pip and verify import success
2. Generate frozen baseline pool: CodeLlama-7B, N=20 samples per problem, T=0.8, fixed seeds, serialized to disk
3. Measure SynCode operationality: compare ast.parse failure rate on SynCode-generated vs baseline-generated pool
4. Measure Z3 eligibility: attempt SMT encoding on baseline pool; record per-problem encoding success/failure rate
5. Verify mypy/ast feedback loop: run mypy.api.run() on sample problems; confirm structured error output

## Dependencies

- H-E1 must PASS before H-M1 through H-M4 (provides validated tool infrastructure for all subsequent experiments)

*Generated: 2026-05-09 | Phase 2B JIT context extraction from 02b_verification_plan.md*
