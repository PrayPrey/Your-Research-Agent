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
hypothesis_id: H-M2
hypothesis_type: MECHANISM
tier: FULL
date: 2026-08-26
author: yoon303@ust.ac.kr
phase: 3
base_hypothesis: H-M1
---

# PRD: H-M2 — Mypy Feedback Specificity for Type-Related Failures

## 1. Executive Summary

**Hypothesis:** Under Condition A (execution-only) vs. Condition B (execution+mypy), Condition B achieves higher per-category repair rate specifically for type-related failures (not semantic/logic), because mypy provides error-type specificity that execution output lacks.

**Goal:** Collect Condition A (execution-only) repair data for HumanEval+ (164 problems, k=1..5 rounds), then compare per-category repair rates between Condition A (new data) and Condition B (reused from H-M1) for two problem categories: type-error problems (mypy-flagged at round 0, n=20) and non-type-error problems (~80 failing, mypy-clean). The primary gate metric is `differential = delta_type - delta_non > 0`, confirming mypy specificity.

**Type:** Mechanism verification — tests causal step 3 in the YOURA pipeline. SHOULD_WORK gate: failure triggers EXPLORE (consider extra-context-length confound).

**Scope:**
- NEW data: 164 HumanEval+ problems × 5 rounds (Condition A) ≈ 820 API calls (failing problems only)
- REUSED data: H-M1 Condition B results (`h-m1/results/humaneval_all_rounds.jsonl`)
- Estimated cost: ~$1–2 (GPT-4o-mini)
- Estimated wall time: 30–60 minutes (Condition A data collection)

---

## 2. Problem Statement

### 2.1 Research Question
Does mypy feedback improve repair success *specifically* for type-error problems (mypy-flagged) compared to non-type-error problems (mypy-clean semantic/logic failures), when compared against execution-only repair (Condition A)?

### 2.2 Why This Matters
H-M1 confirmed mypy errors decrease monotonically across rounds under Condition B. H-M2 tests whether this mypy-driven improvement is *type-specific*: if mypy provides general improvement (helps all problems equally), it may simply add context rather than targeted type-error signal. The differential analysis isolates the causal mechanism.

### 2.3 Prior Work
- **Self-Debug (Chen et al., 2023):** Execution-only repair baseline; repair rate varies by error type; name errors repaired at ~77%.
- **"How Many Tries Does It Take?" (arXiv:2604.10508, 2025):** Per-category repair rates under execution-only repair: name errors ~77%, syntax ~66%, assertion/logic ~45%. Basis for expected Condition A type-error repair rate.
- **LLMloop (arXiv:2603.23613, ICSME 2025):** Separate feedback loops per error type each target distinct failure modes; validates mypy as a type-specific signal channel.
- **"Is Three the Magic Number?" (arXiv:2607.05197, 2025):** Repair gains concentrate in first 2–3 rounds for all error types; k=5 is conservative but complete.

### 2.4 Reused Components from H-M1
- Condition B repair loop (full implementation, validated) — `h-m1/code/`
- Condition B results for HumanEval+: `h-m1/results/humaneval_all_rounds.jsonl`
- Category labels: 20 type-error problems (mypy-flagged at round 0), ~80 non-type-error failing problems
- GPT-4o-mini pipeline (temperature, max tokens, seed)
- EvalPlus test suite runner
- mypy invocation (`--ignore-missing-imports --no-strict-optional`)

---

## 3. Functional Requirements

### FR-1: Dataset Loading (Inherited from H-M1)
- **FR-1.1:** Load all 164 HumanEval+ problems via `evalplus.data.get_human_eval_plus()`
- **FR-1.2:** Load all 378 MBPP+ problems via `evalplus.data.get_mbpp_plus()` (secondary control)
- **FR-1.3:** No manual download required — evalplus auto-downloads

### FR-2: Load H-M1 Condition B Results (REUSE)
- **FR-2.1:** Read `docs/youra_research/h-m1/results/humaneval_all_rounds.jsonl` for Condition B HumanEval+ data
- **FR-2.2:** Parse per-round per-problem records: `{task_id, round_k, mypy_error_count, exec_passed}`
- **FR-2.3:** Extract initial mypy error counts (round k=1 before any repair) for category labeling
- **FR-2.4:** Verify 164 problems present in h-m1 results (assert completeness)

### FR-3: Problem Category Labeling
- **FR-3.1:** Label each HumanEval+ problem as `type_error` or `non_type_error`:
  - `type_error`: mypy error count > 0 at round 0 (initial solution, before any repair) — n=20 from H-M1
  - `non_type_error`: mypy error count = 0 AND EvalPlus test failed at initial generation — ~80 problems
- **FR-3.2:** Use `initial_mypy_errors` from H-M1 Condition B data (round 1 pre-repair mypy counts)
- **FR-3.3:** Verify category counts match H-M1 findings: type_error=20, non_type_error≈80

### FR-4: Condition A Data Collection (PRIMARY NEW WORK)
- **FR-4.1:** For each HumanEval+ problem (164 total), generate initial solution (temp=0.8, seed=42, same prompt as H-M1)
- **FR-4.2:** For each failing problem, run k=1..5 repair rounds using execution-only feedback (NO mypy in prompt)
- **FR-4.3:** Condition A repair prompt format:
  ```
  Problem: {problem_prompt}
  Previous solution:
  {previous_solution}

  Execution feedback:
  {test_failure_output}

  Please fix the above errors and provide a corrected solution.
  ```
  (mypy section explicitly OMITTED vs. Condition B)
- **FR-4.4:** Repair generation: `temperature=0.0`, `max_tokens=2048`
- **FR-4.5:** Early exit: if EvalPlus tests pass at any round, stop repair for that problem
- **FR-4.6:** Record per-problem per-round: `{task_id, round_k, exec_passed}` for all rounds attempted
- **FR-4.7:** Checkpoint/resume: save results incrementally after each problem

### FR-5: Condition A Secondary (MBPP+ Control)
- **FR-5.1:** Run Condition A repair loop on MBPP+ (378 problems, same parameters as FR-4)
- **FR-5.2:** Expected: 0 type-error problems → entire MBPP+ is non-type category
- **FR-5.3:** Compute Condition A vs B differential on MBPP+ as secondary control check

### FR-6: Per-Category Repair Rate Computation
- **FR-6.1:** Compute repair rate at k=5 for each condition × category combination:
  - `rate_A_type`: fraction of type_error problems passing EvalPlus at round 5 under Condition A
  - `rate_B_type`: fraction of type_error problems passing EvalPlus at round 5 under Condition B (from H-M1)
  - `rate_A_non`: fraction of non_type_error problems passing at round 5 under Condition A
  - `rate_B_non`: fraction of non_type_error problems passing at round 5 under Condition B (from H-M1)
- **FR-6.2:** Compute deltas:
  - `delta_type = rate_B_type - rate_A_type`
  - `delta_non = rate_B_non - rate_A_non`
  - `differential = delta_type - delta_non`  ← PRIMARY gate metric
- **FR-6.3:** Compute same for MBPP+ (all non-type → differential expected ≈ 0)

### FR-7: Mechanism Verification
- **FR-7.1:** Evaluate gate: `differential > 0` on HumanEval+
- **FR-7.2:** Check consistency: `delta_type > delta_non` (type problems show larger B-advantage)
- **FR-7.3:** Log: `"[H-M2] type_delta={:.3f}, non_type_delta={:.3f}, differential={:.3f}"`
- **FR-7.4:** Log: `"Mechanism activated: {bool}"` where `activated = differential > 0 and delta_type > delta_non`

### FR-8: Visualization (Required + Autonomous)
- **FR-8.1 (REQUIRED):** Bar chart — `delta_type` vs `delta_non` with zero line. Save to `docs/youra_research/h-m2/figures/gate_metrics.png`
- **FR-8.2 (AUTONOMOUS):** 4-bar chart: Cond A type, Cond B type, Cond A non-type, Cond B non-type repair rates
- **FR-8.3 (AUTONOMOUS):** Differential bar chart: `delta_type` vs `delta_non` side-by-side with error bars (if applicable)
- **FR-8.4 (AUTONOMOUS):** Round-by-round repair curves: cumulative pass rate vs round k, split by category × condition (4 curves)
- **FR-8.5 (AUTONOMOUS):** Confusion matrix-style heatmap: category × condition grid of repair rates
- All figures saved to `docs/youra_research/h-m2/figures/`

### FR-9: Results Persistence
- **FR-9.1:** Save Condition A per-problem per-round results: `docs/youra_research/h-m2/results/condition_a_humaneval.jsonl`
  - Record: `{task_id, round_k, exec_passed, condition: "A"}`
- **FR-9.2:** Save Condition A MBPP+ results: `docs/youra_research/h-m2/results/condition_a_mbpp.jsonl`
- **FR-9.3:** Save aggregate summary: `docs/youra_research/h-m2/results/summary.json`
  - Include: `{rate_A_type, rate_B_type, rate_A_non, rate_B_non, delta_type, delta_non, differential, gate_passed, mechanism_activated}`
- **FR-9.4:** Save category labels: `docs/youra_research/h-m2/results/category_labels.json`
  - Include: `{type_error: [task_ids], non_type_error: [task_ids]}`

---

## 4. Data Specification

### 4.1 HumanEval+ (Primary)

| Field | Value |
|-------|-------|
| Name | HumanEval+ (EvalPlus augmented) |
| Source | `evalplus` Python package |
| Load call | `get_human_eval_plus()` |
| Problems | 164 |
| Download | Auto (no manual step needed) |
| Split | All 164 problems |
| Preprocessing | None |
| Type-error subset | 20 problems (from H-M1 category labels) |
| Non-type-error failing subset | ~80 problems (failing but mypy-clean) |

### 4.2 MBPP+ (Secondary/Control)

| Field | Value |
|-------|-------|
| Name | MBPP+ (EvalPlus augmented) |
| Source | `evalplus` Python package |
| Load call | `get_mbpp_plus()` |
| Problems | 378 |
| Download | Auto (no manual step needed) |
| Split | All 378 problems |
| Preprocessing | None |
| Type-error subset | 0 problems (from H-M1; contributes only non-type category) |

### 4.3 H-M1 Results (Reuse — Condition B Data)

| Field | Value |
|-------|-------|
| File | `docs/youra_research/h-m1/results/humaneval_all_rounds.jsonl` |
| Format | JSONL: `{task_id, round_k, mypy_error_count, exec_passed}` |
| Coverage | All 164 HumanEval+ problems, rounds 1–5 |
| Purpose | Condition B repair rates + initial mypy error counts for labeling |

**Note:** Both evalplus datasets auto-download. No data-preparation task needed. H-M1 results are local — no download required.

---

## 5. Evaluation Metrics

### 5.1 Primary Metric
- **Differential (HumanEval+):** `differential = delta_type - delta_non`
  - `delta_type = rate_B_type - rate_A_type`
  - `delta_non = rate_B_non - rate_A_non`
- Gate: `differential > 0` (SHOULD_WORK)

### 5.2 Secondary Metrics
- `delta_type` (absolute): expected ~+20–30 pp (mypy resolves all type errors in 1 round under Cond B)
- `delta_non` (absolute): expected ~0–10 pp (mypy adds minimal signal for semantic errors)
- MBPP+ differential: expected ≈ 0 (all MBPP+ is non-type; both conditions should perform similarly)
- Per-category repair rates at k=5: `rate_A_type`, `rate_B_type`, `rate_A_non`, `rate_B_non`

### 5.3 Gate Evaluation

| Result | Condition | Action |
|--------|-----------|--------|
| PASS | `differential > 0` on HumanEval+ | Proceed to H-M3 |
| FAIL | `differential ≤ 0` on HumanEval+ | EXPLORE — consider extra-context-length confound |

---

## 6. Non-Functional Requirements

### 6.1 Reproducibility
- Initial generation: `seed=42` via OpenAI `seed` parameter (same as H-M1 for controlled comparison)
- Repair rounds: `temperature=0.0` (deterministic given same prompt)
- mypy flags fixed: `--ignore-missing-imports --no-strict-optional`

### 6.2 Controlled Comparison
- Condition A initial solutions MUST use same seed=42 and same prompts as H-M1 Condition B initial solutions
- Only difference between Condition A and B: presence/absence of mypy output in repair prompt
- Category labeling MUST use H-M1 round-0 mypy data (not re-run mypy on Condition A solutions)

### 6.3 Error Handling
- OpenAI API errors: exponential backoff (max 3 retries); log and skip if persistent
- mypy `TimeoutExpired` (10s): count as 0 errors
- EvalPlus exceptions: treat as FAIL (conservative)
- Checkpoint/resume: save Condition A results incrementally; allow restart without re-running completed problems

### 6.4 Performance
- Estimated wall time: 30–60 minutes (Condition A, HumanEval+ only; failing problems × 5 rounds)
- Additional: 30–60 minutes for MBPP+ Condition A (378 problems)
- No GPU required

### 6.5 Logging
- Per-problem: `"[Cond A] problem={task_id} round={k} exec_passed={bool}"`
- Progress: `"[{benchmark}] {i}/{total} problems complete"`
- Mechanism: `"[H-M2] type_delta={:.3f}, non_type_delta={:.3f}, differential={:.3f}"`

---

## 7. Dependencies

### 7.1 Python Packages (pip install)

| Package | Purpose |
|---------|---------|
| `evalplus` | Dataset loading + test suite evaluation (inherited from H-M1) |
| `openai` | GPT-4o-mini API client (inherited from H-M1) |
| `mypy` | Static type error analysis (inherited; used for category labeling from H-M1 data) |
| `matplotlib` | Figure generation |
| `numpy` | Repair rate computation |
| `tqdm` | Progress bar |
| `python-dotenv` | Load OPENAI_API_KEY from .env |

### 7.2 Environment Variables
- `OPENAI_API_KEY`: Required — OpenAI API access for GPT-4o-mini

### 7.3 External References
- H-M1 codebase: `docs/youra_research/h-m1/code/` — reuse Condition B repair loop, mypy runner, evalplus runner
- H-M1 results: `docs/youra_research/h-m1/results/humaneval_all_rounds.jsonl` — Condition B data (no re-run)
- Self-Debug (Chen et al., 2023): Condition A (execution-only) prompt design pattern

### 7.4 System Requirements
- Python 3.9+
- Network access to OpenAI API
- No GPU required

---

## 8. Success Criteria

| Criterion | Threshold | Status |
|-----------|-----------|--------|
| Condition A runs end-to-end | No unhandled exceptions, k=1..5 for all 164 HumanEval+ problems | Required |
| Category labels verified | type_error=20, non_type_error≈80 (matching H-M1) | Required |
| Condition B data loaded | H-M1 humaneval_all_rounds.jsonl parsed successfully | Required |
| Mechanism log present | `[H-M2] type_delta=... differential=...` logged | Required |
| **PASS gate** | `differential > 0` on HumanEval+ | Primary gate (SHOULD_WORK) |
| Secondary consistency | `delta_type > delta_non` | Informational |
| MBPP+ control | MBPP+ differential ≈ 0 | Informational |
| Figures generated | `gate_metrics.png` exists | Required |
| Results persisted | `summary.json` exists | Required |

---

## 9. File Structure

```
docs/youra_research/h-m2/
├── 02c_experiment_brief.md     # Phase 2C input
├── 03_prd.md                   # This file
├── 03_architecture.md          # Phase 3 output
├── 03_logic.md                 # Phase 3 output
├── 03_config.md                # Phase 3 output
├── 03_tasks.yaml               # Phase 3 task list
├── code/
│   ├── condition_a_runner.py   # Condition A repair loop (NEW)
│   ├── load_condition_b.py     # Load and parse H-M1 results
│   ├── category_labeling.py    # Problem categorization logic
│   ├── analysis.py             # Differential repair rate computation
│   ├── visualize.py            # Figure generation
│   └── run.py                  # CLI entry point
├── figures/
│   ├── gate_metrics.png        # Required
│   └── *.png                   # Autonomous figures
└── results/
    ├── condition_a_humaneval.jsonl
    ├── condition_a_mbpp.jsonl
    ├── category_labels.json
    └── summary.json
```
