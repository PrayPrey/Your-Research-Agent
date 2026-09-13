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
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
tier: LIGHT
date: 2026-08-26
author: yoon303@ust.ac.kr
phase: 3
---

# PRD: H-E1 — Type Error Prevalence in LLM-Generated Python Code

## 1. Executive Summary

**Hypothesis:** Under GPT-4o-mini generation on HumanEval+ and MBPP+ (temperature=0.8, single shot), a non-trivial fraction (≥10%) of failing solutions will have mypy-detectable type errors.

**Goal:** Build and run an observational measurement pipeline that: (1) generates Python solutions via GPT-4o-mini, (2) evaluates them using EvalPlus test suites, and (3) applies mypy static analysis to failing solutions. The result is a fraction estimate with statistical uncertainty across 3 seeds.

**Type:** PoC / Observational — no model training. MUST_WORK gate: failure (< 5%) stops the pipeline.

**Scope:** 542 problems × 3 seeds = 1,626 API calls. ~35-45% expected failure rate → ~570-730 mypy analyses. Estimated wall time: 30-60 min, API cost: ~$2-5.

---

## 2. Problem Statement

### 2.1 Research Question
Do mypy-detectable type errors appear in a non-trivial fraction (≥10%) of failing LLM-generated Python solutions? This PoC validates whether type errors are a sufficiently common failure mode to justify a type-error-guided repair mechanism (H-M1, H-M2, H-M3).

### 2.2 Why This Matters
If type errors are rare (< 5%), downstream repair hypotheses become moot — the pipeline stops here. If type errors are common (≥10%), targeted repair loops using type feedback become viable.

### 2.3 Prior Work
- EvalPlus (Liu et al. 2023): augmented test suites reveal higher failure rates on HumanEval/MBPP. Expected GPT-4o-mini pass@1 ≈ 55-65% (HumanEval+), 50-60% (MBPP+).
- General Python type-error analysis literature: 15-30% of failing LLM solutions expected to have ≥1 mypy error.

---

## 3. Functional Requirements

### FR-1: Dataset Loading
- **FR-1.1:** Load all 378 MBPP+ problems via `evalplus.data.get_mbpp_plus()`
- **FR-1.2:** Load all 164 HumanEval+ problems via `evalplus.data.get_human_eval_plus()`
- **FR-1.3:** No local file download required — evalplus auto-downloads on first call

### FR-2: Code Generation
- **FR-2.1:** Generate one Python solution per problem per seed via GPT-4o-mini API
- **FR-2.2:** Parameters: `model="gpt-4o-mini"`, `temperature=0.8`, `max_tokens=1024`, `n=1`
- **FR-2.3:** Seeds: 3 runs with `seed` values `[42, 123, 456]`
- **FR-2.4:** Prompt format: standard function completion (problem description + function stub)
- **FR-2.5:** Extract Python code block from LLM response (strip markdown fences if present)

### FR-3: Functional Correctness Evaluation
- **FR-3.1:** Run EvalPlus test suite on each generated solution
- **FR-3.2:** Mark each solution as PASS or FAIL based on test suite result
- **FR-3.3:** Only failing solutions proceed to mypy analysis (FR-4)

### FR-4: mypy Type Error Analysis
- **FR-4.1:** For each failing solution, write code to a temporary `.py` file
- **FR-4.2:** Run: `mypy --ignore-missing-imports --no-strict-optional <tempfile>`
- **FR-4.3:** Timeout: 30 seconds per mypy call
- **FR-4.4:** On timeout: log and count as "no error" (conservative — avoids false positives)
- **FR-4.5:** Record: `has_mypy_error: bool` (returncode != 0), `error_count: int` (lines containing `"error:"`)
- **FR-4.6:** Delete temporary file after each mypy run

### FR-5: Mechanism Verification
- **FR-5.1:** Verify mypy pipeline activated: at least one failing solution analyzed and at least one error found
- **FR-5.2:** Check `sample_size_sufficient`: ≥50 failing solutions analyzed
- **FR-5.3:** Log `"mypy analysis: {N} errors in {task_id}"` for each analyzed solution

### FR-6: Result Aggregation
- **FR-6.1:** Per benchmark per seed: compute `type_error_fraction = count(has_mypy_error=True) / count(failing)`
- **FR-6.2:** Across 3 seeds: compute mean ± std for each benchmark
- **FR-6.3:** Store per-solution results in structured format (JSONL or CSV)
- **FR-6.4:** Optional: breakdown by mypy error category (name-error, type-error, attribute-error, return-value)

### FR-7: Visualization
- **FR-7.1 (REQUIRED):** Bar chart: type_error_fraction vs 10% threshold for MBPP+ and HumanEval+, with std error bars across 3 seeds. Save to `docs/youra_research/h-e1/figures/gate_metrics.png`
- **FR-7.2 (AUTONOMOUS):** Error type distribution pie/bar chart
- **FR-7.3 (AUTONOMOUS):** Error count histogram (mypy errors per failing solution)
- **FR-7.4 (AUTONOMOUS):** Seed consistency box plot (type_error_fraction across seeds)
- All figures saved to `docs/youra_research/h-e1/figures/`

### FR-8: Results Persistence
- **FR-8.1:** Save per-solution results to `docs/youra_research/h-e1/results/results_{benchmark}_{seed}.jsonl`
- **FR-8.2:** Save aggregate summary to `docs/youra_research/h-e1/results/summary.json`
- **FR-8.3:** Format: `{"benchmark": "mbpp+", "seed": 42, "n_failing": int, "n_type_errors": int, "fraction": float}`

---

## 4. Data Specification

### 4.1 MBPP+ (Primary)

| Field | Value |
|-------|-------|
| Name | MBPP+ (EvalPlus augmented) |
| Source | `evalplus` Python package |
| Load call | `get_mbpp_plus()` |
| Problems | 378 |
| Download | Auto (no manual step needed) |
| Split | All problems (no train/test split) |
| Preprocessing | None |

### 4.2 HumanEval+ (Secondary)

| Field | Value |
|-------|-------|
| Name | HumanEval+ (EvalPlus augmented) |
| Source | `evalplus` Python package |
| Load call | `get_human_eval_plus()` |
| Problems | 164 |
| Download | Auto (no manual step needed) |
| Split | All problems |
| Preprocessing | None |

**Note:** Both datasets are auto-downloaded by the evalplus package on first use. No data-preparation task needed.

---

## 5. Evaluation Metrics

### 5.1 Primary Metric
- **`type_error_fraction_mbpp`**: `count(failing AND has_mypy_error) / count(failing)` on MBPP+
- Reported as mean ± std across 3 seeds

### 5.2 Secondary Metric
- **`type_error_fraction_humaneval`**: Same formula on HumanEval+
- Reported as mean ± std across 3 seeds

### 5.3 Reference Metrics (context)
- `pass_at_1_mbpp`: pass@1 for GPT-4o-mini on MBPP+
- `pass_at_1_humaneval`: pass@1 for GPT-4o-mini on HumanEval+

### 5.4 Gate Evaluation
| Result | Condition | Action |
|--------|-----------|--------|
| PASS | `type_error_fraction_mbpp ≥ 0.10` | Continue to H-M1, H-M2, H-M3 |
| BORDERLINE | 0.05 ≤ fraction < 0.10 | Continue with reduced expectations |
| FAIL | fraction < 0.05 | Pipeline stops; downstream hypotheses moot |

---

## 6. Non-Functional Requirements

### 6.1 Reproducibility
- Seeds must be set via OpenAI `seed` parameter (not random)
- Results must be deterministic given same seed

### 6.2 Error Handling
- OpenAI API errors: retry with exponential backoff (max 3 retries); log and skip if persistent
- mypy `FileNotFoundError`: FAIL immediately with install instructions
- mypy `TimeoutExpired` (30s): log and count as "no error"
- `ImportError` for evalplus: FAIL immediately with install instructions
- Zero failing solutions: FAIL with diagnostic message

### 6.3 Performance
- Estimated wall time: 30-60 minutes
- No GPU required
- Rate limiting: respect OpenAI API rate limits

### 6.4 Logging
- Log generation progress: `"Generating {task_id} seed={seed} ({i}/{total})"`
- Log evaluation results: `"task_id={task_id} seed={seed} passed={bool}"`
- Log mypy results: `"mypy analysis: {N} errors in {task_id}"`

---

## 7. Dependencies

### 7.1 Python Packages (pip install)

| Package | Purpose |
|---------|---------|
| `evalplus` | Dataset loading + test suite evaluation |
| `openai` | GPT-4o-mini API client |
| `mypy` | Static type error analysis |
| `matplotlib` | Figure generation |
| `tqdm` | Progress bar |
| `python-dotenv` | Load OPENAI_API_KEY from .env |

### 7.2 Environment Variables
- `OPENAI_API_KEY`: Required — OpenAI API access for GPT-4o-mini

### 7.3 External References
- evalplus/evalplus: https://github.com/evalplus/evalplus — official dataset + evaluation
- openai/openai-python: https://github.com/openai/openai-python — API client

### 7.4 System Requirements
- Python 3.9+
- Network access to OpenAI API
- No GPU required

---

## 8. Success Criteria

| Criterion | Threshold | Status |
|-----------|-----------|--------|
| Pipeline runs end-to-end | No unhandled exceptions | Required |
| Sample size | ≥50 failing solutions analyzed by mypy | Required |
| Mechanism activated | `mypy_ran=True AND errors_found=True` | Required |
| **PASS gate** | `type_error_fraction_mbpp ≥ 0.10` | Primary gate |
| Secondary gate | `type_error_fraction_humaneval ≥ 0.10` | Informational |
| Figures generated | `gate_metrics.png` exists | Required |
| Results persisted | `summary.json` exists | Required |

---

## 9. File Structure

```
docs/youra_research/h-e1/
├── 02c_experiment_brief.md    # Phase 2C input
├── 03_prd.md                  # This file
├── 03_architecture.md         # Phase 3 output
├── 03_logic.md                # Phase 3 output
├── 03_config.md               # Phase 3 output
├── 03_tasks.yaml              # Phase 3 task list
├── figures/
│   ├── gate_metrics.png       # Required
│   └── *.png                  # Autonomous
└── results/
    ├── results_mbpp_42.jsonl
    ├── results_mbpp_123.jsonl
    ├── results_mbpp_456.jsonl
    ├── results_humaneval_42.jsonl
    ├── results_humaneval_123.jsonl
    ├── results_humaneval_456.jsonl
    └── summary.json
```
