# PRD: h-m3 — Execution+mypy vs Execution-only Repair on HumanEval+ and MBPP+

**Hypothesis ID:** h-m3
**Date:** 2026-08-26
**Type:** MECHANISM (INCREMENTAL — extends h-m2)
**Gate:** MUST_WORK — p < 0.05 on MBPP+ AND absolute pass@1 improvement ≥ 1%

---

## 1. Executive Summary

Implement and evaluate a 2-condition iterative LLM code repair experiment on full HumanEval+ (164) and MBPP+ (378) benchmarks using GPT-4o-mini:

- **Condition A (Baseline):** Execution-only feedback, k=5 repair rounds
- **Condition B (Proposed):** Execution + mypy type-checking feedback, k=5 repair rounds

Primary claim: Condition B achieves strictly higher pass@1 averaged over k=1..5 rounds than Condition A on MBPP+ (p < 0.05, absolute delta ≥ 1%).

---

## 2. Problem Statement

Self-repair LLMs improve pass@1 through iterative feedback. Current SOTA uses execution error messages only (Condition A). mypy type-checking provides structured, line-specific error signal (error type, expected vs actual types) that execution output may not surface. This experiment tests whether that additional signal produces a measurable aggregate pass@1 improvement across all problem categories on standard benchmarks.

**Context from prerequisites:**
- h-m1 (VALIDATED): mypy error count decreases monotonically across repair rounds (Spearman ρ < 0) — mechanism is active
- h-m2 (FAILED, SHOULD_WORK): Ceiling effect on type-error category (90.9%/90.9%). Extra-context-length identified as primary confound to track. Aggregate pass@1 gain may still exist.

---

## 3. Scope

**In Scope:**
- Full HumanEval+ (164 problems) and MBPP+ (378 problems) evaluation
- 3 seeds × 5 repair rounds × 2 conditions (A, B) × 2 datasets
- mypy subprocess integration in permissive mode
- Token count logging per condition (confound control)
- mypy error count logging per round (h-m1 cross-validation)
- Visualization: 5 figures per experiment brief spec

**Out of Scope:**
- Fine-tuning or weight updates
- Other models (GPT-4, Claude, etc.)
- Other static analyzers (pylint, flake8)

---

## 4. Data Specification

### 4.1 Primary Dataset: MBPP+ (EvalPlus v0.2.0)

| Field | Value |
|-------|-------|
| Name | MBPP+ |
| Size | 378 problems |
| Source | evalplus PyPI package |
| Loading | `from evalplus.data import get_mbpp_plus` |
| Manual download | NO — auto-download |
| Split | Full benchmark (no train/test split) |
| Task type | code_generation_pass@k |

### 4.2 Secondary Dataset: HumanEval+ (EvalPlus)

| Field | Value |
|-------|-------|
| Name | HumanEval+ |
| Size | 164 problems (80x more tests than original) |
| Source | evalplus PyPI package |
| Loading | `from evalplus.data import get_human_eval_plus` |
| Manual download | NO — auto-download |
| Split | Full benchmark |
| Task type | code_generation_pass@k |

**Note:** Both datasets auto-download — no data preparation task needed.

---

## 5. Functional Requirements

### FR-1: Initial Code Generation (Condition 0 / No-Repair Baseline)
- Generate initial solution for all problems on both benchmarks
- Model: GPT-4o-mini, temperature=0.8, max_tokens=2048
- Seeds: 3 (for statistical variance estimation)
- Record: initial code per (problem_id, seed, dataset)
- Evaluate pass@1 from initial generation (k=0) — no-repair baseline

### FR-2: Condition A — Execution-Only Repair Loop
- For each (problem, seed): run k=5 repair rounds
- Feedback: execution error + stdout/stderr only
- Repair LLM: GPT-4o-mini, temperature=0.0 (greedy)
- Record: pass@1 at each round k=1..5, final code, token count per prompt

### FR-3: Condition B — Execution + mypy Repair Loop
- For each (problem, seed): run k=5 repair rounds
- Feedback: execution error + mypy type-checker output (permissive mode)
- mypy flags: `--ignore-missing-imports --no-strict-optional --no-error-summary`
- Repair LLM: GPT-4o-mini, temperature=0.0 (greedy)
- Record: pass@1 at each round k, final code, mypy error count per round, token count per prompt
- Mechanism log: "MYPY_FEEDBACK_ADDED: {n_errors} errors for problem {task_id} round {k}"

### FR-4: Statistical Analysis
- Metric: per-problem delta = mean_{seeds,rounds} pass@1(B) − mean_{seeds,rounds} pass@1(A)
- Test: Welch's t-test (unequal variance) on per-problem delta vector, MBPP+
- Secondary: same test on HumanEval+ (positive direction sufficient)
- Report: t_stat, p_value, absolute_improvement, 95% CI

### FR-5: Confound Control Logging (from h-m2)
- Log token count per repair prompt per condition per round
- Compute mean token delta (Condition B − Condition A) per round
- Report: "Context-length delta: {mean_delta} tokens per prompt" for transparency

### FR-6: Visualization (5 figures)
- F1 (MANDATORY): Bar chart — pass@1 Condition A vs B on MBPP+ and HumanEval+ with error bars (±1 std across seeds)
- F2: Line plot — mean pass@1 per round k (k=0..5) for Conditions A, B, Baseline, both benchmarks
- F3: Histogram — per-problem (B−A) delta distribution on MBPP+
- F4: Line plot — mean mypy error count per round k for Condition B
- F5: Bar chart — mean prompt token count per round for Condition A vs B
- Output folder: `docs/youra_research/h-m3/figures/`

### FR-7: Mechanism Verification
- Assert: `mypy_triggered_count > 0` (mechanism activated on at least 1 problem)
- Log: fraction of repair attempts where mypy produced non-empty output
- Cross-check h-e1: at least 10% of failing solutions should trigger mypy

---

## 6. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| Reproducibility | temperature=0.0 for repair; seeds fixed; results JSON-serialized |
| Safety | mypy runs in temp file (no code executed in main process for mypy) |
| Budget | API calls: ~7,400–10,000 at GPT-4o-mini pricing (~$10–15 total) |
| Performance | Parallelism across problems optional (API rate limits apply) |
| Logging | Structured JSON log: problem_id, seed, round, condition, pass, tokens, mypy_errors |
| Infrastructure | FULL tier: YAML config + dataclass, structured logging, unit tests |

---

## 7. Dependencies

### 7.1 Python Packages

```
evalplus>=0.3.0        # dataset loading and pass@1 evaluation
openai>=1.0.0          # GPT-4o-mini API
mypy>=1.0.0            # type checker (subprocess call)
scipy>=1.10.0          # Welch's t-test
numpy>=1.24.0          # array ops
matplotlib>=3.7.0      # visualization
pyyaml>=6.0            # config loading
dataclasses            # stdlib
tempfile               # stdlib (mypy temp file)
subprocess             # stdlib (mypy invocation)
```

### 7.2 External References (no manual download)

- evalplus/evalplus: dataset + evaluation framework (auto-download)
- Johin2/iterative-code-repair: implementation reference pattern
- arxiv 2508.00422: mypy feedback format reference

### 7.3 Environment Variables

```
OPENAI_API_KEY   # required for GPT-4o-mini API
```

---

## 8. Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| MUST_WORK gate (MBPP+) | p < 0.05 AND Δpass@1 ≥ 1% | Welch's t-test on per-problem delta |
| Secondary (HumanEval+) | positive delta (direction only) | same test, p-value informational |
| Mechanism active | mypy_triggered_count > 0 | assertion in verification code |
| Confound logged | token delta reported | structured log present |

**Failure route:** PIVOT or ABANDON if gate not met.

---

## 9. Ablation Variants

| Variant | Description |
|---------|-------------|
| Condition 0 | No repair (initial generation only, k=0) |
| Condition A | Execution-only repair, k=5 (baseline) |
| Condition B | Execution + mypy repair, k=5 (proposed) |

All 3 ablation variants MUST be run and reported.

---

## 10. Incremental Context (from h-m2 base)

| Item | h-m2 Implementation | h-m3 Change |
|------|--------------------|----|
| Datasets | HumanEval+ (164) only | + MBPP+ (378) primary |
| Conditions | type-error category split | aggregate pass@1 across all categories |
| Seeds | 3 | 3 (same) |
| k | 5 | 5 (same) |
| Token logging | No | Yes (new — confound control) |
| mypy error logging | Yes | Yes (reuse) |
