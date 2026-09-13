---
stepsCompleted:
  - executive_summary
  - problem_statement
  - functional_requirements
  - nfrs
  - data_specification
  - evaluation_metrics
  - dependencies
  - success_criteria
hypothesis_id: H-Z1
hypothesis_type: EXISTENCE
tier: LIGHT
base_hypothesis: H-E1
date: 2026-08-26
author: yoon303@ust.ac.kr
phase: 3
---

# PRD: H-Z1 — Z3 Formal Counterexample Feedback for LLM Code Repair

## 1. Executive Summary

**Hypothesis:** On a curated subset of ~50 arithmetic-heavy HumanEval problems (after Z3 spec pre-validation), Condition C (execution+mypy+Z3) achieves higher pass@1 than Condition B (execution+mypy), because formal counterexamples from Z3 provide a distinct error signal that complements mypy type-error messages.

**Goal:** Build and run a two-condition repair loop experiment that: (1) curates an arithmetic-heavy HumanEval+ subset and pre-validates Z3 specs for each problem, (2) runs GPT-4o-mini with k=5 repair rounds under Condition B (execution+mypy) and Condition C (execution+mypy+Z3 counterexample), and (3) compares pass@1 between conditions.

**Type:** PoC / Comparison on curated subset — no model training. SHOULD_WORK gate: positive delta (Condition C > Condition B) on ≥30 validated problems.

**Scope:** ~50 curated problems × 2 conditions × (1 initial + 5 repair rounds) × API calls. Estimated wall time: 60-120 min, API cost: ~$3-8. Builds on H-E1 validated setup.

---

## 2. Problem Statement

### 2.1 Research Question
Does adding Z3 formal counterexample feedback (Condition C) improve pass@1 over execution+mypy feedback alone (Condition B) on arithmetic-heavy HumanEval+ problems? This PoC validates whether Z3 counterexample signals are actionable enough to meaningfully complement type-level feedback.

### 2.2 Why This Matters
H-E1 confirmed 70% of failing HumanEval+ solutions have mypy-detectable errors (primarily `name-defined`). Arithmetic-heavy problems have semantic errors beyond type errors — Z3 can encode the arithmetic spec and return a concrete failing input (counterexample) that is more informative than "wrong answer." If Z3 CE feedback improves repair success, it motivates full Z3-augmented repair pipelines (H-M1, H-M2 extensions).

### 2.3 Key H-E1 Finding
- HumanEval+: 70% type error rate in failing solutions → high structural error rate confirms subset is valid target
- MBPP+: 0% type error rate → excluded from H-Z1 (Z3 arithmetic constraints less relevant)
- Primary error category: `name-defined` → structural/semantic errors dominate, Z3 CE provides complementary signal

### 2.4 Prior Work
- Loop Invariant Generation (arXiv 2508.00419): Z3 CE → LLM repair prompt — LLMs respond meaningfully to Z3 witness feedback
- ExVerus (arXiv 2603.25810): Z3 counterexample-driven proof repair — direct evidence Z3 CE improves LLM repair
- LLM-CEGIS-Repair (AAAI 2025): CEGIS loop with formal feedback validates repair loop architecture
- Specification-Guided Arithmetic Repair (arXiv 2507.03659): Arithmetic errors specifically targeted with formal specs

---

## 3. Functional Requirements

### FR-1: Arithmetic Subset Curation
- **FR-1.1:** Load all 164 HumanEval+ problems via `evalplus.data.get_human_eval_plus()`
- **FR-1.2:** Filter to arithmetic-heavy problems meeting ALL criteria:
  - Input types: `int`, `float`, `List[int]`, or str with numeric content only
  - Output type: numeric (`int`, `float`) or bool derived from numeric comparison
  - Primary operation: arithmetic/numeric (no string manipulation as primary)
  - Function is pure (no side effects, no global state, no file I/O)
- **FR-1.3:** Target: ~50 qualifying problems from 164 HumanEval+ problems
- **FR-1.4:** Log each accepted/rejected problem with rejection reason

### FR-2: Z3 Spec Generation and Pre-Validation
- **FR-2.1:** For each curated problem, call GPT-4o-mini (temperature=0.0) to generate Z3 spec code
- **FR-2.2:** Z3 spec format: Python code using `z3-solver` library that encodes arithmetic constraints
- **FR-2.3:** Validate spec by running against canonical solution with representative EvalPlus test inputs:
  - If spec says UNSAT on canonical solution → reject (false negative)
  - If spec says SAT on failing inputs → accept (correctly identifies violations)
- **FR-2.4:** Discard problems where Z3 spec is invalid (misclassifies canonical solution)
- **FR-2.5:** Minimum viable subset: ≥30 problems with valid Z3 specs (secondary gate)
- **FR-2.6:** Z3 timeout: 10 seconds per validation call
- **FR-2.7:** Save validated subset with Z3 spec code to `results/validated_subset.json`

### FR-3: Initial Solution Generation (Both Conditions)
- **FR-3.1:** Generate one Python solution per validated problem via GPT-4o-mini (temperature=0.8)
- **FR-3.2:** Same initial solution used for BOTH Condition B and Condition C (controlled comparison)
- **FR-3.3:** Parameters: `model="gpt-4o-mini"`, `temperature=0.8`, `max_tokens=2048`, `n=1`, `seed=42`
- **FR-3.4:** Prompt: standard function completion (problem prompt + function stub)
- **FR-3.5:** Extract Python code from LLM response (strip markdown fences if present)

### FR-4: Condition B Repair Loop (execution + mypy)
- **FR-4.1:** For each problem: run up to k=5 repair rounds
- **FR-4.2:** Each round: evaluate solution with EvalPlus test suite
- **FR-4.3:** If PASS: record round number, exit loop
- **FR-4.4:** If FAIL: collect feedback:
  - Execution feedback: error traceback + "N test cases failed"
  - mypy feedback: `mypy --ignore-missing-imports --no-strict-optional` output (timeout=30s)
- **FR-4.5:** Build Condition B repair prompt with execution + mypy feedback
- **FR-4.6:** Call GPT-4o-mini (temperature=0.0) for repair
- **FR-4.7:** Record: `passed: bool`, `rounds_to_pass: int`, `final_solution: str`

### FR-5: Condition C Repair Loop (execution + mypy + Z3)
- **FR-5.1:** Identical to FR-4 with additional Z3 counterexample step each round:
- **FR-5.2:** After collecting execution and mypy feedback, call Z3 with problem's validated spec
- **FR-5.3:** If `solver.check() == sat`: extract counterexample `{input_var: value}` from `solver.model()`
- **FR-5.4:** If `solver.check() != sat`: Z3 finds no violation (solution may be correct semantically)
- **FR-5.5:** Append Z3 CE to repair prompt: "Z3 Formal Counterexample:\n  Input: {ce_inputs}\n  Your output: {actual}\n  Expected behavior: see spec"
- **FR-5.6:** Z3 timeout: 10 seconds per check; if timeout → skip Z3 CE, continue with B-only prompt
- **FR-5.7:** Record: same fields as FR-4, plus `z3_ce_found_count: int` (rounds where CE was found)

### FR-6: Result Aggregation and Comparison
- **FR-6.1:** Compute `pass@1_B`: fraction of problems passed by Condition B after k=5 rounds
- **FR-6.2:** Compute `pass@1_C`: fraction of problems passed by Condition C after k=5 rounds
- **FR-6.3:** Compute delta: `delta = pass@1_C - pass@1_B`
- **FR-6.4:** Compute secondary metrics:
  - Subset size (problems with valid Z3 specs)
  - Z3 spec validity rate (valid specs / curated problems)
  - Z3 CE found rate (rounds where Z3 found CE / total Condition C rounds on failing solutions)
- **FR-6.5:** Save per-problem results to `results/condition_b_results.jsonl` and `results/condition_c_results.jsonl`
- **FR-6.6:** Save aggregate to `results/summary.json`

### FR-7: Visualization
- **FR-7.1 (REQUIRED):** Bar chart — pass@1 Condition B vs Condition C on validated arithmetic subset. Save to `figures/gate_metrics.png`
- **FR-7.2 (AUTONOMOUS):** Z3 Validation Funnel: stacked bar — curated (N~50) → Z3 spec generated → validated → used in experiment
- **FR-7.3 (AUTONOMOUS):** Per-round pass@1 curve: line chart — Condition B vs C across repair rounds k=1..5
- **FR-7.4 (AUTONOMOUS):** Z3 CE found rate: histogram — fraction of rounds where CE found per problem
- **FR-7.5 (AUTONOMOUS):** Problem difficulty scatter: X = Condition B pass, Y = Condition C pass
- All figures saved to `docs/youra_research/h-z1/figures/`

### FR-8: Results Persistence
- **FR-8.1:** Save per-problem B results to `results/condition_b_results.jsonl`
- **FR-8.2:** Save per-problem C results to `results/condition_c_results.jsonl`
- **FR-8.3:** Save validated subset to `results/validated_subset.json`
- **FR-8.4:** Save summary to `results/summary.json`
- **FR-8.5:** Summary format: `{"pass_at_1_B": float, "pass_at_1_C": float, "delta": float, "subset_size": int, "z3_validity_rate": float, "z3_ce_found_rate": float}`

---

## 4. Data Specification

### 4.1 HumanEval+ Arithmetic Subset (Primary)

| Field | Value |
|-------|-------|
| Name | HumanEval+ Arithmetic-Heavy Curated Subset |
| Source | `evalplus` Python package |
| Load call | `get_human_eval_plus()` |
| Full size | 164 problems |
| Curated subset | ~50 arithmetic-heavy problems |
| After Z3 validation | ≥30 problems (minimum viable) |
| Download | Auto (no manual step needed) |
| Split | Curated subset only (no train/val/test split) |
| Preprocessing | Curation filter + Z3 spec generation |

**Curation Criteria:**
1. Input types: `int`, `float`, `List[int]`, or str with numeric content only
2. Output type: numeric (`int`, `float`) or bool derived from numeric comparison
3. Primary operation: arithmetic (fibonacci, factorial, gcd, digit operations, sequence sums)
4. Pure function (no side effects, no global state, no file I/O)
5. No string manipulation as primary operation

**Note:** MBPP+ excluded per H-E1 finding (0% type error rate; Z3 arithmetic constraints less relevant).

### 4.2 No Manual Download Required
Both HumanEval+ and Z3 spec generation use API/library calls only. No data preparation task needed.

---

## 5. Evaluation Metrics

### 5.1 Primary Metric
- **`delta = pass@1_C - pass@1_B`**: Delta in pass@1 between Condition C (execution+mypy+Z3) and Condition B (execution+mypy) on validated arithmetic subset after k=5 repair rounds
- Gate: `delta > 0` (positive delta = PoC success)

### 5.2 Secondary Metrics
- **`subset_size`**: Number of problems with valid Z3 specs (must be ≥30)
- **`z3_validity_rate`**: `valid_z3_specs / curated_problems` (fraction of curated problems with valid specs)
- **`z3_ce_found_rate`**: `rounds_with_ce / total_c_rounds_on_failing` (fraction of failing rounds where Z3 found CE)

### 5.3 Reference Metrics (context)
- `pass_at_1_B`: absolute pass@1 for Condition B (baseline)
- `pass_at_1_C`: absolute pass@1 for Condition C (proposed)
- `rounds_distribution_B/C`: distribution of rounds to first pass

### 5.4 Gate Evaluation

| Result | Condition | Action |
|--------|-----------|--------|
| PASS | `pass@1_C > pass@1_B` AND `subset_size ≥ 30` | Z3 CE signal validated → continue to Z3-augmented repair |
| BORDERLINE | `pass@1_C == pass@1_B` AND `subset_size ≥ 30` | No improvement but Z3 operational — note limitation |
| FAIL | `pass@1_C < pass@1_B` OR `subset_size < 30` | Z3 CE does not improve repair on this subset |

---

## 6. Non-Functional Requirements

### 6.1 Reproducibility
- Seed: `seed=42` (single seed PoC)
- Deterministic repair via `temperature=0.0`
- Z3 spec code saved in `validated_subset.json` for re-use

### 6.2 Error Handling
- OpenAI API errors: retry with exponential backoff (max 3 retries); log and skip if persistent
- Z3 timeout (10s): log and continue round without CE (Condition C degrades to B gracefully)
- Z3 spec invalid: discard problem from experiment subset (do not include in comparison)
- mypy timeout (30s): log and count as "no error"
- Zero valid Z3 specs: FAIL with message "Z3 spec validation failed for all curated problems"
- `ImportError` for z3, evalplus: FAIL immediately with install instructions

### 6.3 Performance
- Estimated wall time: 60-120 minutes
- No GPU required; API-based inference only
- Z3 timeout guard prevents solver hang on complex formulas

### 6.4 Logging
- Log curation: `"Accepted {task_id}: arithmetic problem"` / `"Rejected {task_id}: {reason}"`
- Log Z3 validation: `"Z3 spec valid for {task_id}"` / `"Z3 spec rejected for {task_id}: {reason}"`
- Log repair progress: `"[B/C] {task_id} round {r}: PASS/FAIL, CE_found={bool}"`
- Log Z3 CE: `"Z3 CE found for {task_id}: input={ce}"`

---

## 7. Dependencies

### 7.1 Python Packages (pip install)

| Package | Purpose |
|---------|---------|
| `evalplus` | Dataset loading + test suite evaluation (reused from H-E1) |
| `openai` | GPT-4o-mini API client (reused from H-E1) |
| `mypy` | Static type error analysis (reused from H-E1) |
| `z3-solver` | Z3 SMT solver for spec encoding and CE extraction (NEW) |
| `matplotlib` | Figure generation (reused from H-E1) |
| `tqdm` | Progress bar (reused from H-E1) |
| `python-dotenv` | Load OPENAI_API_KEY from .env (reused from H-E1) |

### 7.2 Environment Variables
- `OPENAI_API_KEY`: Required — OpenAI API access for GPT-4o-mini (same as H-E1)

### 7.3 External References
- evalplus/evalplus: https://github.com/evalplus/evalplus
- z3-solver: https://pypi.org/project/z3-solver/
- Z3Prover API docs: https://z3prover.github.io/api/html/z3.z3.html
- pmorvalho/LLM-CEGIS-Repair (reference architecture): https://github.com/pmorvalho/LLM-CEGIS-Repair

### 7.4 System Requirements
- Python 3.9+
- Network access to OpenAI API
- No GPU required
- z3-solver requires C++ runtime (pip install handles this automatically)

### 7.5 Inherited from H-E1
The following components are REUSED from H-E1 code:
- EvalPlus dataset loading utilities
- GPT-4o-mini API client wrapper
- mypy runner (FR-4 → mypy feedback collection)
- Results persistence utilities

---

## 8. Success Criteria

| Criterion | Threshold | Status |
|-----------|-----------|--------|
| Pipeline runs end-to-end | No unhandled exceptions for both conditions | Required |
| Subset size | ≥30 problems with valid Z3 specs | Required (secondary gate) |
| Z3 operational | ≥1 problem where Z3 finds CE during Condition C | Required |
| **PoC Pass gate** | `pass@1_C > pass@1_B` on validated subset | Primary gate (SHOULD_WORK) |
| Figures generated | `gate_metrics.png` exists | Required |
| Results persisted | `summary.json`, condition B/C result files exist | Required |

---

## 9. File Structure

```
docs/youra_research/h-z1/
├── 02c_experiment_brief.md    # Phase 2C input
├── 03_prd.md                  # This file
├── 03_architecture.md         # Phase 3 output
├── 03_logic.md                # Phase 3 output
├── 03_config.md               # Phase 3 output
├── 03_tasks.yaml              # Phase 3 task list
├── figures/
│   ├── gate_metrics.png       # Required
│   ├── z3_validation_funnel.png
│   ├── per_round_pass_curve.png
│   ├── z3_ce_found_rate.png
│   └── problem_difficulty_scatter.png
└── results/
    ├── validated_subset.json         # Z3-validated problem subset + specs
    ├── condition_b_results.jsonl     # Per-problem Condition B results
    ├── condition_c_results.jsonl     # Per-problem Condition C results
    └── summary.json                  # Aggregate comparison metrics
```
