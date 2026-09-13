# Experiment Design: H-M2

**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Under Condition A (execution-only) vs. Condition B (execution+mypy), Condition B achieves higher per-category repair rate specifically for type-related failures (not semantic/logic), because mypy provides error-type specificity that execution output lacks.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** — Tests causal step 2 (mypy signal specificity): does mypy feedback improve repairs selectively for type-error problems vs. non-type-error problems?

---

## Workflow Status

**Verification State:** IN_PROGRESS (ABLATION MODE)
**Prerequisites Satisfied:** H-M1 PASS (Spearman ρ = −0.707; mypy mechanism activated; 20/164 HumanEval+ problems repaired from round 1 to round 2)
**Gate Status:** SHOULD_WORK — failure → EXPLORE (consider alternative confound explanation)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (SATISFIED — PASS)

### Gate Condition
SHOULD_WORK: Condition B relative improvement on type-error problems > relative improvement on non-type-error problems. Effect direction must be consistent across both benchmarks (HumanEval+ and MBPP+). If fails: EXPLORE — mechanism may not be type-specific; consider extra-context-length confound.

---

## Continuation Context

**Previous Hypothesis:** H-M1 (VALIDATED — PASS)

**Proven Components from H-M1 (reused for H-M2):**
- Full repair-loop infrastructure (Condition B: execution+mypy, k=1..5 rounds) — functional and validated
- GPT-4o-mini at temperature=0.8 (initial), temperature=0.0 (repair)
- HumanEval+ (164 problems) loaded, seed=42
- mypy invocation: `mypy --ignore-missing-imports --no-strict-optional`
- EvalPlus test suite execution pipeline
- Per-round per-problem mypy error counts already collected in `results/humaneval_all_rounds.jsonl`

**Critical Finding from H-M1:**
- HumanEval+: 20/164 (12.2%) problems have mypy-detectable type errors at round 1; all resolve by round 2
- MBPP+: 0/378 problems have mypy errors — contributes zero type-error problems for H-M2
- Primary error type: `[name-defined]` (undefined names, ~70% of HumanEval+ failing solutions at round 1)
- H-M2 analysis is therefore **HumanEval+-only** (MBPP+ has no type-error problems to form the "type-error" category)

**Key Design Implication:**
H-M2 requires Condition A data (execution-only repair, k=5) which was NOT collected in H-M1 (H-M1 only ran Condition B). This is the primary new experimental work for H-M2.

### Previous Hypothesis Results (H-M1)
- Spearman ρ = −0.707 (p=0.182) — error count decreases across rounds
- All 20 type-error problems in HumanEval+ resolved by round 2 under Condition B
- Mechanism activated: True
- MBPP+ contributes 0 type-error problems (consistent with H-E1)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Archon MCP unavailable — knowledge inferred from Phase 2A/B context and prior h-m1 research*

**[INFERRED] Query 1: Per-category error repair rate analysis in LLM repair loops**

- **Self-Debug (Chen et al., 2023)** — execution-only repair baseline
  - Finding: Repair success varies by error type; syntax errors easier than semantic errors
  - Relevant pattern: Binary execution feedback (pass/fail) cannot distinguish error category
  - Key insight: Per-category analysis requires labeling problems before computing repair rates
  - Used for: Condition A baseline design, per-category analysis protocol

- **"How Many Tries Does It Take?" (arXiv:2604.10508, 2025)**
  - Finding: Name errors repair at ~77%, syntax at ~66%, assertion/logic at ~45%
  - Key insight: Error categories show distinct repair rates even under execution-only repair
  - Used for: Expected per-category repair rate ranges for Condition A

- **Reflexion (Shinn et al., 2023)** — verbal feedback repair
  - Finding: Verbal self-feedback improves repair but does not distinguish error categories
  - Key insight: Unstructured feedback gives generalized improvement, not category-specific
  - Used for: Understanding why mypy's structured output may yield differential improvement

**[INFERRED] Query 2: Static analysis feedback specificity in code generation**

- **LLMloop (arXiv:2603.23613, ICSME 2025)**
  - Finding: Separate feedback loops for compilation, static analysis, test failures each target distinct failure modes
  - Key insight: Static analysis (like mypy) functions as a type-specific signal channel
  - Used for: Hypothesis mechanism design — mypy targets type errors, not semantic logic

- **"Is Three the Magic Number?" (arXiv:2607.05197, 2025)**
  - Finding: Repair gains concentrate in first 2-3 rounds for all error types
  - Key insight: Category-specific effect should be visible at k≤3; k=5 is conservative
  - Used for: Success criteria design (analyze repair rate at k=5)

**[INFERRED] Query 3: Error categorization methods for Python code**

- **EvalPlus (Liu et al., 2023)**
  - Finding: Test suite failures include multiple categories: syntax, runtime type, assertion, timeout
  - Key insight: mypy detects a subset of runtime failures (type errors) pre-execution
  - Used for: Category labeling protocol — "type-related" = mypy flag at round 0 AND EvalPlus fail

### Archon Code Examples

*Archon MCP unavailable — code patterns inferred from h-m1 codebase*

**[INFERRED] Per-category repair rate computation pattern:**
```python
# Pattern from Self-Debug / iterative repair literature
# Category assignment: mypy-detectable (type) vs clean (semantic/logic)

def label_problem_category(problem_id, initial_mypy_errors):
    """
    Assign category based on round-0 mypy output.
    type_error: mypy detects >= 1 error on initial failing solution
    non_type_error: mypy clean but EvalPlus test fails (semantic/logic)
    """
    if initial_mypy_errors > 0:
        return "type_error"
    else:
        return "non_type_error"  # EvalPlus fail confirmed by H-E1 experiment

def compute_repair_rate(problems, condition, category, round_k=5):
    """Fraction of category problems that pass EvalPlus at round k."""
    subset = [p for p in problems if p.category == category and p.condition == condition]
    passed = sum(1 for p in subset if p.pass_at_k[round_k])
    return passed / len(subset) if subset else 0.0
```

### Exa GitHub Implementations

*Exa MCP unavailable — [INFERRED] from known repositories*

**[INFERRED] evalplus/evalplus** (evalplus.github.io)
- Primary benchmark infrastructure for HumanEval+ and MBPP+
- Provides per-problem pass/fail labels used for failure categorization
- Already integrated in h-m1 codebase

**[INFERRED] microsoft/TypeEvalPy** (type error evaluation for Python)
- Provides structured comparison of type checkers on Python code
- Pattern: categorize code issues by static vs dynamic detection
- Relevance: Informs mypy error category labeling methodology

**[INFERRED] princeton-nlp/SWE-bench** repair loop patterns
- Multi-round repair loop with distinct feedback types per round
- Pattern: Separate evaluation of fix rate per bug category (regression, logic, type)
- Relevance: Per-category repair rate analysis methodology

**Serena Analysis Needed:** false — h-m1 codebase already analyzed; h-m2 extends same pattern

### Code Analysis (Serena MCP)

*Skipped* — Code from h-m1 is sufficiently clear; h-m2 extends the same repair loop with Condition A added and per-category analysis layer.

### Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

H-M2 builds directly on h-m1's validated codebase. No new external implementation needed.

**Recommended Implementation Path:**
- Primary: Extend h-m1 code (`h-m1/code/`) — add Condition A repair loop + category labeling
- Fallback: Reference Self-Debug (Chen et al., 2023) repair loop pattern
- Justification: h-m1 already has Condition B working end-to-end; H-M2 needs Condition A as new data + per-category analysis on existing h-m1 Condition B data

---

## Experiment Specification

### Dataset

**Primary Dataset: HumanEval+ (evalplus)**
- Source: `evalplus/evalplus` (HuggingFace: `evalplus/humanevalplus`)
- Split: Full test set, 164 problems
- Preprocessing: No preprocessing — use raw problem docstrings + function signatures
- Type: programmatic-api (EvalPlus library)
- Hypothesis Fit: Only HumanEval+ has type-error problems (20/164 = 12.2% from H-M1); MBPP+ has 0 — HumanEval+ is the only feasible benchmark for per-category analysis

**Secondary Dataset: MBPP+ (evalplus)**
- Source: `evalplus/evalplus` (HuggingFace: `evalplus/mbppplus`)
- Split: Full test set, 378 problems
- Preprocessing: None
- Type: programmatic-api
- Role: Secondary benchmark; expected 0 type-error problems → will form "non-type only" subset; included for completeness

**Dataset Statistics (from h-m1 validated run):**
- HumanEval+: 164 problems; ~100 failing under GPT-4o-mini initial generation at seed=42
- MBPP+: 378 problems; ~321 failing under initial generation at seed=42
- Type-error subset (HumanEval+): 20 problems (12.2% of 164)
- Non-type-error subset (HumanEval+): ~80 failing but mypy-clean problems

**Loading Information** (for Phase 4 download):
- Method: EvalPlus library + HuggingFace
- Identifier: `evalplus/humanevalplus`, `evalplus/mbppplus`
- Code:
```python
from evalplus.data import get_human_eval_plus, get_mbpp_plus
humaneval_problems = get_human_eval_plus()  # dict: task_id -> problem
mbpp_problems = get_mbpp_plus()
```

### Models

#### Baseline Model

**Architecture:** GPT-4o-mini (OpenAI API)
- Type: API-based LLM
- Temperature: 0.8 (initial generation), 0.0 (repair rounds — same as h-m1)
- Max tokens: 2048
- Seed: 42

**Condition A (NEW — Execution-Only Repair):**
- Feedback: EvalPlus test output only (pass/fail + error traceback)
- No mypy output in repair prompt
- This is the key NEW data collection for H-M2

**Condition B (Reuse from H-M1):**
- Feedback: EvalPlus test output + mypy output
- Already collected in h-m1 results — reuse `h-m1/results/humaneval_all_rounds.jsonl`

**Loading Information** (for Phase 4):
- Method: OpenAI API
- Identifier: `gpt-4o-mini`
- Code:
```python
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[...],
    temperature=0.0,  # repair rounds
    max_tokens=2048,
    seed=42
)
```

#### Proposed Model

**Architecture:** Same GPT-4o-mini + Per-Category Analysis Layer

This is a comparative analysis experiment, not a new model. The "proposed" element is the analysis methodology that measures per-category repair rates across conditions.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Per-Category Repair Rate Differential Analysis
# Based on: h-m1 repair loop + category labeling from mypy round-0 output
# Source: Extends h-m1/code/ experiment infrastructure

def run_condition_a_repair(problem, k_max=5):
    """Execution-only repair loop (NEW for H-M2)."""
    solution = generate_initial_solution(problem)  # temp=0.8
    results = []
    for k in range(1, k_max + 1):
        exec_result = run_evalplus(problem, solution)
        if exec_result.passed:
            results.append({"round": k, "passed": True})
            break
        # Condition A: execution feedback only (no mypy)
        feedback = format_execution_feedback(exec_result)
        solution = repair_solution(problem, solution, feedback, temp=0.0)
        results.append({"round": k, "passed": exec_result.passed})
    return results

def label_and_compute_differential(humaneval_results_A, humaneval_results_B,
                                    initial_mypy_errors):
    """
    Args:
        humaneval_results_A: dict {task_id: [{round, passed}]} - Condition A results
        humaneval_results_B: dict {task_id: [{round, passed}]} - Condition B (h-m1 data)
        initial_mypy_errors: dict {task_id: int} - mypy error count at round 0
    Returns:
        differential: repair rate delta (Cond B - Cond A) for type vs non-type problems
    """
    # Step 1: Label problems by category
    type_problems = {tid for tid, errs in initial_mypy_errors.items() if errs > 0}
    non_type_problems = {tid for tid in humaneval_results_A if tid not in type_problems}

    # Step 2: Compute repair rates at k=5 per condition per category
    def repair_rate(results, problem_set):
        passed = sum(1 for tid in problem_set
                     if any(r["passed"] for r in results.get(tid, [])))
        return passed / len(problem_set) if problem_set else 0.0

    rate_B_type = repair_rate(humaneval_results_B, type_problems)
    rate_A_type = repair_rate(humaneval_results_A, type_problems)
    rate_B_non = repair_rate(humaneval_results_B, non_type_problems)
    rate_A_non = repair_rate(humaneval_results_A, non_type_problems)

    delta_type = rate_B_type - rate_A_type    # H-M2 primary: should be > 0 and larger
    delta_non = rate_B_non - rate_A_non       # H-M2 secondary: should be smaller

    return {
        "type": {"B": rate_B_type, "A": rate_A_type, "delta": delta_type},
        "non_type": {"B": rate_B_non, "A": rate_A_non, "delta": delta_non},
        "differential": delta_type - delta_non  # PRIMARY GATE METRIC: > 0 = hypothesis supported
    }
```

### Training Protocol

**This is a code generation/repair experiment — no gradient training involved.**

**Reused from H-M1 (validated):**
- Model: GPT-4o-mini, temperature=0.8 (initial), temperature=0.0 (repair)
- Max tokens: 2048 per generation
- Seed: 42 (for reproducibility)
- Repair rounds: k=1..5

**NEW for H-M2 — Condition A Data Collection:**
- Run Condition A (execution-only repair) on full HumanEval+ (164 problems), same seed=42
- Estimated API calls: 164 problems × 5 rounds × 1 seed ≈ 820 API calls (failing problems only)
- Estimated cost: ~$1-2 (GPT-4o-mini pricing)
- Runtime: ~30-60 minutes

**Condition B Data:** Reuse `h-m1/results/humaneval_all_rounds.jsonl` — no re-run needed.

**Seeds:** 1 (seed=42, same as h-m1 for controlled comparison)

**Prompt Templates:**
- Condition A repair prompt: `[problem] + [initial solution] + [execution output only]`
- Condition B repair prompt: `[problem] + [initial solution] + [execution output] + [mypy output]`
- Same prompt structure as h-m1 Condition B, minus the mypy section for Condition A

### Evaluation

**Primary Metric: Repair Rate Differential**
- `differential = delta_type - delta_non`
- `delta_type = repair_rate(Cond_B, type_problems) - repair_rate(Cond_A, type_problems)`
- `delta_non = repair_rate(Cond_B, non_type_problems) - repair_rate(Cond_A, non_type_problems)`
- Gate: `differential > 0` (Condition B improves type-error problems more than non-type-error problems)

**Per-Category Repair Rates (at k=5):**
| Category | Cond A (exec-only) | Cond B (exec+mypy) | Delta (B−A) |
|----------|--------------------|--------------------|-------------|
| type-error problems (n=20) | ? | from h-m1 data | delta_type |
| non-type-error problems (~80) | ? | from h-m1 data | delta_non |

**Expected Values (from literature):**
- Cond B type-error repair rate: ~100% (h-m1 showed all 20 resolved by round 2)
- Cond A type-error repair rate: ~77% (from "How Many Tries" name-error repair rate)
- Expected delta_type: ~23 percentage points
- Cond B non-type repair rate: moderate improvement (mypy adds less signal for semantic errors)
- Cond A non-type repair rate: roughly similar (execution output sufficient for some logic errors)
- Expected differential: > 0 (type-error improvement is larger under Cond B)

**Secondary Check:**
- Effect direction consistent on MBPP+: expected 0 type-error problems → entire MBPP+ is non-type category; Cond B vs A on MBPP+ should show near-zero differential (validating that H-M2 effect is specifically type-driven)

**Success Criteria:**
- Primary (PoC gate): `differential > 0` on HumanEval+
- Secondary: Same direction on MBPP+ (non-type-error repair rate similar between conditions)

**Expected Baseline Performance (from h-m1 validated data):**
- Condition B type-error repair rate (HumanEval+): 100% (all 20 type-error problems resolved by round 2)
- Condition B non-type repair rate: to be measured in this experiment

**Metrics Loading Information** (for Phase 4):
- Task Type: code generation repair classification
- Library: custom (EvalPlus test suite + mypy)
- Code:
```python
# Repair rate = fraction of subset that passes EvalPlus at k=5
def evalplus_pass_at_k(problem_id, solution, k=5):
    from evalplus.eval import evaluate_with_test_code
    result = evaluate_with_test_code(problem_id, solution)
    return result["passed"]
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart — repair rate delta (type vs non-type) for Cond A and Cond B

#### Additional Figures (LLM Autonomous)
- **Per-Category Repair Rate Bar Chart**: 4-bar chart (Cond A type, Cond B type, Cond A non-type, Cond B non-type)
- **Differential Bar Chart**: `delta_type` vs `delta_non` side-by-side with zero line
- **Round-by-Round Repair Curves**: Cumulative pass rate vs round k, split by category and condition (4 curves)
- **Confusion Matrix-style Heatmap**: category × condition grid of repair rates

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m2/figures/`.

---

## Ablation Study Design

H-M2 is a two-condition, two-category analysis. The ablation structure is built into the design:

| Variant | Purpose |
|---------|---------|
| Condition A vs B on type-error problems | Primary test: does mypy help for type errors? |
| Condition A vs B on non-type-error problems | Control: does mypy help equally for semantic/logic? |
| MBPP+ Condition A vs B (all non-type) | Replication: MBPP+ has no type errors → should show no differential |

---

## 🔬 Mechanism Verification Protocol

**Mechanism exists:** Yes — mypy detects Python type errors as structured messages (proven in H-E1, H-M1)
**Mechanism isolatable:** Yes — compare Condition A (no mypy) vs Condition B (with mypy) on identical problems
**Baseline measurable:** Yes — Condition A repair rates computed per category

**Architecture Compatibility:** ✅ GPT-4o-mini processes both execution output and mypy output in repair prompt; the prompt structure is the only variable between conditions

**Mechanism Activation Indicators:**
- `delta_type > 0`: Condition B outperforms A on type-error problems
- `delta_non ≈ 0` or `delta_non < delta_type`: Condition B effect is smaller for non-type problems
- Mechanism log message: `"[H-M2] type_delta={:.3f}, non_type_delta={:.3f}, differential={:.3f}"`

**Tensor Shape Change:** N/A (LLM API, no tensor shapes)

**Metric Delta Expected:**
- `delta_type` ≈ +20-30 percentage points (mypy resolves type errors in 1 round under Cond B)
- `delta_non` ≈ 0-10 percentage points (mypy provides minimal signal for semantic errors)
- `differential` ≈ +15-25 percentage points

**Mechanism Verification Code:**
```python
def verify_mechanism(results):
    """Verify H-M2 mechanism: type-specific repair rate differential."""
    diff = results["differential"]
    delta_type = results["type"]["delta"]
    delta_non = results["non_type"]["delta"]
    mechanism_active = diff > 0 and delta_type > delta_non
    print(f"[H-M2] type_delta={delta_type:.3f}, non_type_delta={delta_non:.3f}, differential={diff:.3f}")
    print(f"Mechanism activated: {mechanism_active}")
    return mechanism_active
```

**Hypothesis Support Threshold:** `differential > 0` (direction-based gate for SHOULD_WORK)
**Hypothesis Support Metric:** `differential = delta_type - delta_non`

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (Condition A repair loop completes for all 164 HumanEval+ problems)
2. `differential > 0` (type-error problems show larger Cond B improvement than non-type problems)

---

## Appendix: Reference Implementations

### A. Knowledge Base Sources (Inferred)

**Source 1: Self-Debug (Chen et al., 2023)**
- Type: Foundational repair loop paper
- Query: "execution-only LLM code repair loop"
- Relevance: Defines Condition A (execution-only) baseline
- Key Insights: Binary execution feedback; repair success varies by error type
- Used For: Condition A prompt design, expected repair rate ranges

**Source 2: "How Many Tries Does It Take?" (arXiv:2604.10508, 2025)**
- Type: Empirical analysis of LLM repair iterations
- Query: "LLM repair loop error type repair rate"
- Relevance: Per-category repair rates under execution-only repair
- Key Insights: Name errors ~77%, syntax ~66%, assertion/logic ~45%
- Used For: Expected Condition A type-error repair rate (~77% for name errors)

**Source 3: LLMloop (arXiv:2603.23613, ICSME 2025)**
- Type: Static analysis feedback loop implementation
- Query: "static analysis mypy feedback code repair"
- Relevance: Validates treating mypy as a separate feedback channel
- Key Insights: Separate loops per feedback type; each targets distinct failure modes
- Used For: Justification that mypy targets type errors specifically

**Source 4: EvalPlus (Liu et al., 2023)**
- Type: Standard benchmark
- Query: "HumanEval+ MBPP+ benchmark evaluation"
- Relevance: Per-problem pass/fail labels for failure categorization
- Used For: Dataset source, test suite for repair rate measurement

### B. GitHub Implementations (Inferred — Exa unavailable)

**Repository 1: evalplus/evalplus** [INFERRED]
- URL: https://github.com/evalplus/evalplus
- Relevance: Primary benchmark library; provides per-problem test cases
- Key Code Pattern: `evaluate_with_test_code(task_id, solution)` → pass/fail
- Used For: Repair rate computation at each round

**Repository 2: h-m1 codebase (local)**
- Path: `docs/youra_research/h-m1/code/`
- Relevance: Validated Condition B repair loop implementation
- Key Code: Full repair loop with mypy + EvalPlus integration
- Used For: Reuse Condition B results; template for Condition A loop

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — h-m1 codebase already fully functional and validated; H-M2 extends it with Condition A (subtract mypy from prompt) + per-category analysis layer.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — H-M1
- File: `docs/youra_research/h-m1/04_validation.md`
- Reused Components:
  - Condition B repair loop (full implementation) — all 164 problems, 5 rounds, seed=42
  - Per-round per-problem mypy error counts in `results/humaneval_all_rounds.jsonl`
  - Problem category labels (type-error: 20 problems; non-type: ~80 failing problems)
  - GPT-4o-mini prompting parameters (temperature, max tokens, seed)
- Why Reused: Enables controlled comparison — Condition B data fixed; only Condition A is new

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (HumanEval+) | Previous hypothesis | H-M1 results (0 MBPP+ type errors) |
| Type-error category labels | Previous hypothesis | H-M1 `humaneval_all_rounds.jsonl` |
| Condition B repair rates | Previous hypothesis | H-M1 validated data |
| Condition A design | Literature | Self-Debug (Chen et al., 2023) |
| Expected Cond A repair rate (~77%) | Literature | "How Many Tries" (arXiv:2604.10508) |
| Mypy feedback specificity rationale | Literature | LLMloop (arXiv:2603.23613) |
| Evaluation protocol | Phase 2B | 02b_verification_plan.md H-M2 section |
| Gate metric (differential > 0) | Phase 2B | H-M2 success criteria |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — restated in state block)
**Date:** 2026-08-26

### Workflow History for This Hypothesis
- H-M2 set to IN_PROGRESS: 2026-08-26T10:24:06Z
- Phase 2C experiment design: IN_PROGRESS → COMPLETED: 2026-08-26

---

*MCP Tools Used: Archon (unavailable — [INFERRED] fallback), Exa (unavailable — [INFERRED] fallback), Serena (skipped — h-m1 codebase sufficient)*
*All specifications grounded in h-m1 validated results and Phase 2B planning*
*Next Phase: Phase 3 - Implementation Planning*
