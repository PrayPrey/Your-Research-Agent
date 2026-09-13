# Product Requirements Document: H-E1
<!-- stepsCompleted: 1,2,3,4,5 -->

**Hypothesis:** H-E1
**Type:** EXISTENCE (MUST_WORK)
**Date:** 2026-08-22
**Author:** Anonymous
**Source:** 02c_experiment_brief.md

---

## 1. Executive Summary

H-E1 verifies that the 134 EvalPlus failures from h-e1 Run 2 (34 HumanEval+ + 100 MBPP+) are fully recoverable as a fixed problem set. The stored GPT-4o-mini incorrect outputs and failing test cases (`plus_fail_tests`) must be intact and accessible via local JSON files and the `evalplus.data` API. Gate pass unblocks H-M1, H-M2, H-C1.

This is a data integrity verification script — not a machine learning experiment. No model training, no GPU, no new API calls. Runtime < 10 seconds.

---

## 2. Problem Statement

The SpecRepair verification pipeline constructs Condition B and C repair prompts using:
1. The incorrect GPT-4o-mini solution for each failed problem
2. The first failing test case (`plus_fail_tests[0]`) as the concrete counterexample

If the h-e1 Run 2 archive JSON files are missing, corrupted, or schema-incompatible, prompt construction is impossible and downstream hypotheses (H-M1, H-M2, H-C1) cannot run. H-E1 must confirm this data is intact before any downstream API budget is spent.

---

## 3. Functional Requirements

### FR-1: Load HumanEval+ failure records
- Load `humaneval_samples_eval_results.json` from archive path
- Extract records where `plus_status == "fail"`
- **Count must equal exactly 34**

### FR-2: Load MBPP+ failure records
- Load `mbpp_samples_eval_results.json` from archive path
- Extract records where `plus_status == "fail"`
- **Count must equal exactly 100**

### FR-3: Verify total failure count
- Combined HE+ + MBPP+ failures = **134**
- Hard assertion

### FR-4: Verify `solution` field present for all 134
- Each failure record must have non-empty `solution` field
- This is the stored GPT-4o-mini incorrect output needed for Condition B/C prompts

### FR-5: Verify `plus_fail_tests` non-empty for all 134
- Each failure record must have at least one entry in `plus_fail_tests`
- `plus_fail_tests[0]` is the concrete counterexample for reprompting

### FR-6: EvalPlus API accessible
- `from evalplus.data import get_human_eval_plus, get_mbpp_plus` must succeed
- Both functions must return non-empty dicts

### FR-7: All 134 task IDs present in EvalPlus dataset
- Every task_id from HE+ failures must appear in `get_human_eval_plus()` result
- Every task_id from MBPP+ failures must appear in `get_mbpp_plus()` result
- This confirms the problem prompt and docstring are retrievable for Conditions B/C

### FR-8: Generate verification figures
- Bar chart: actual vs. expected counts (HE+ 34/34, MBPP+ 100/100, Total 134/134)
- Failure distribution pie: 34 HE+ (25.4%) vs. 100 MBPP+ (74.6%)
- Data completeness matrix: 134 tasks × {solution_present, plus_fail_tests_present, task_in_api}
- `plus_fail_tests` count distribution histogram
- Save all figures to `h-e1/figures/`

### FR-9: Structured verification report
- Output JSON file with per-check results
- Gate field: "PASS" or "FAIL"
- Summary counts: he_failures, mbpp_failures, total

---

## 4. Data Specification

### 4.1 Primary Dataset: h-e1 Run 2 Archive

| Field | Value |
|-------|-------|
| Type | Local JSON files (no download required) |
| HE+ file | `humaneval_samples_eval_results.json` |
| MBPP+ file | `mbpp_samples_eval_results.json` |
| Archive path | `docs/youra_research/_archive/20260822T150921_routing_recovery/h-e1/results/` |
| Schema | `{"eval": {task_id: [{"plus_status": str, "solution": str, "plus_fail_tests": list, ...}]}}` |
| Auto-download | No — files already on disk |
| Confirmed present | ✅ 34 HE+ + 100 MBPP+ verified by prior Python count |

### 4.2 EvalPlus Benchmark API

| Field | Value |
|-------|-------|
| Type | Python package API (programmatic-api) |
| Package | `evalplus>=0.3.1` |
| Install | `pip install evalplus` |
| HE+ dataset | 164 tasks, 80× augmented tests |
| MBPP+ dataset | 378 tasks, 35× augmented tests |
| Auto-download | Yes (package handles caching) |

---

## 5. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| Runtime | < 10 seconds total |
| GPU | Not required |
| Memory | < 500 MB (JSON load) |
| Determinism | 100% — no randomness |
| Reproducibility | Script produces identical results on any re-run |

---

## 6. Evaluation Metrics

| Check | Target | Type |
|-------|--------|------|
| HE+ failure count | == 34 | Hard assertion |
| MBPP+ failure count | == 100 | Hard assertion |
| Total failures | == 134 | Hard assertion |
| `solution` present | All 134 non-empty | Hard assertion |
| `plus_fail_tests` present | All 134 non-empty list | Hard assertion |
| EvalPlus API accessible | `get_human_eval_plus()` returns dict | Hard assertion |
| Task IDs in EvalPlus | All 134 task IDs present | Hard assertion |

**Success criterion:** All 7 assertions pass → gate = "PASS"
**Failure criterion:** Any assertion fails → gate = "FAIL" → pipeline blocked

---

## 7. Dependencies

### 7.1 Python Packages

```
evalplus>=0.3.1
matplotlib>=3.5.0
numpy>=1.21.0
```

### 7.2 Local Files (must exist prior to execution)

| File | Path |
|------|------|
| HE+ results | `docs/youra_research/_archive/20260822T150921_routing_recovery/h-e1/results/humaneval_samples_eval_results.json` |
| MBPP+ results | `docs/youra_research/_archive/20260822T150921_routing_recovery/h-e1/results/mbpp_samples_eval_results.json` |

### 7.3 External Services

None — H-E1 does not make API calls to OpenAI or any external service.

---

## 8. Success Criteria

**Gate PASS:**
1. Script executes without `AssertionError`, `FileNotFoundError`, `ImportError`, or `KeyError`
2. All 7 data integrity assertions pass
3. `result["gate"] == "PASS"`
4. Log message: `"✅ H-E1 gate PASS: 134 failures loaded (34 HE+ + 100 MBPP+)"`
5. Verification report JSON written to `h-e1/results/verification_report.json`
6. All 4 figures saved to `h-e1/figures/`

**Gate FAIL (any of):**
- Archive JSON files not found
- HE+ failure count ≠ 34
- MBPP+ failure count ≠ 100
- Any `solution` field empty
- Any `plus_fail_tests` empty
- EvalPlus API not importable
- Any task_id not in EvalPlus dataset

---

## 9. Out of Scope

- New GPT-4o-mini API calls (stored outputs only)
- Model fine-tuning or evaluation
- Condition B/C prompt construction (H-M1/H-M2 scope)
- EvalPlus dataset re-generation
- Statistical significance testing (binary pass/fail only)
