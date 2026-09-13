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
hypothesis_id: H-M1
hypothesis_type: MECHANISM
tier: FULL
date: 2026-08-26
author: yoon303@ust.ac.kr
phase: 3
base_hypothesis: H-E1
---

# PRD: H-M1 — Monotonic Mypy Error Reduction via Execution+Mypy Repair Loop

## 1. Executive Summary

**Hypothesis:** Under execution+mypy repair (Condition B, k=1..5 rounds), the mean mypy error count per problem decreases monotonically from round 1 to round 5, because LLM uses structured mypy error messages to generate subsequent repair attempts with fewer type violations.

**Goal:** Extend the H-E1 pipeline with an iterative repair loop (Condition B: execution feedback + mypy feedback) applied to all MBPP+ (378) and HumanEval+ (164) problems. Run k=1..5 repair rounds per problem, record per-round mypy error counts, and compute Spearman ρ between round number and mean error count. If ρ < 0, the mypy feedback channel demonstrably reduces type errors across rounds.

**Type:** Mechanism verification — tests causal step 2→3 in the YOURA pipeline. MUST_WORK gate: if Spearman ρ ≥ 0 on MBPP+, pipeline stops (H-M2/H-M3 blocked).

**Scope:** 542 problems × 5 rounds = 2,710 repair calls (+ 542 initial generations) ≈ 3,252 total API calls. Estimated API cost: ~$10-15 (GPT-4o-mini). Estimated wall time: 90-150 minutes.

---

## 2. Problem Statement

### 2.1 Research Question
Does execution+mypy feedback (Condition B) produce a monotonic decrease in mean mypy error count across repair rounds k=1..5? This validates whether the mypy feedback channel is causally active — i.e., the LLM uses mypy error messages to generate progressively fewer type violations.

### 2.2 Why This Matters
H-E1 confirmed type errors are prevalent (70% of HumanEval+ failing solutions). H-M1 tests whether feeding mypy output back into the repair prompt actually reduces subsequent type errors. Without this mechanism being active, mypy-guided repair (H-M2, H-M3) cannot work.

### 2.3 Prior Work
- "Is Three the Magic Number?" (arXiv:2607.05197): first 3-4 repair iterations capture most gains; k=5 provides complete trajectory.
- "How Many Tries Does It Take?" (arXiv:2604.10508): name errors repaired at ~77%; first 2 rounds capture 76-95% of total improvement. Expected sharp drop rounds 1→2.
- LLMloop (arXiv:2603.23613): static analysis as distinct feedback channel — validates Condition B design.
- PyTy (ICSE 2024): mypy error format (line:col + expected vs actual type) directly usable in LLM repair prompts.

### 2.4 Reused Components from H-E1
- EvalPlus test suite runner (`evaluate_solution`)
- mypy subprocess invocation (`run_mypy` with `--ignore-missing-imports --no-strict-optional`)
- GPT-4o-mini generation pipeline
- Dataset loading (`get_mbpp_plus`, `get_human_eval_plus`)

---

## 3. Functional Requirements

### FR-1: Dataset Loading (Inherited from H-E1)
- **FR-1.1:** Load all 378 MBPP+ problems via `evalplus.data.get_mbpp_plus()`
- **FR-1.2:** Load all 164 HumanEval+ problems via `evalplus.data.get_human_eval_plus()`
- **FR-1.3:** No local file download required — evalplus auto-downloads on first call

### FR-2: Initial Code Generation (Inherited from H-E1)
- **FR-2.1:** Generate one initial Python solution per problem via GPT-4o-mini
- **FR-2.2:** Parameters: `model="gpt-4o-mini"`, `temperature=0.8`, `max_tokens=2048`, `n=1`
- **FR-2.3:** Seed: 1 fixed seed (seed=42) — mechanism check, not power study
- **FR-2.4:** Extract Python code block from LLM response

### FR-3: Repair Loop — Condition B (Core New Requirement)
- **FR-3.1:** For each problem, run k=1..5 repair rounds (or until execution passes)
- **FR-3.2:** Each repair round records mypy error count BEFORE generating the repair
- **FR-3.3:** Round k=1: evaluate initial solution (no repair yet), record mypy error count
- **FR-3.4:** Repair prompt includes BOTH execution feedback AND mypy feedback (Condition B)
- **FR-3.5:** Repair generation parameters: `temperature=0.0` (deterministic), `max_tokens=2048`
- **FR-3.6:** Early exit: if EvalPlus tests pass at any round, stop repair for that problem
- **FR-3.7:** Record `(problem_id, round_k, mypy_error_count)` for ALL problems at ALL rounds attempted

### FR-4: mypy Integration (Inherited + Extended)
- **FR-4.1:** Reuse `run_mypy(code)` from H-E1 (`--ignore-missing-imports --no-strict-optional`)
- **FR-4.2:** Timeout: 10 seconds per mypy call (reduced from H-E1's 30s for throughput)
- **FR-4.3:** On timeout: count as 0 errors (conservative)
- **FR-4.4:** mypy stderr included verbatim in repair prompt (Condition B)

### FR-5: Repair Prompt Construction
- **FR-5.1:** Format:
  ```
  Problem: {problem_prompt}
  Previous solution:
  {previous_solution}

  Execution feedback:
  {test_failure_output}

  Type checker (mypy) feedback:
  {mypy_stderr}

  Please fix the above errors and provide a corrected solution.
  ```
- **FR-5.2:** If execution passed (early exit), do not construct repair prompt
- **FR-5.3:** Include full mypy stdout (not just error count) in prompt

### FR-6: Metric Computation
- **FR-6.1:** For each round k=1..5, compute `mean_errors_k` = mean mypy error count across all problems that had ≥1 mypy error at round 1 (on the dataset being analyzed)
- **FR-6.2:** Compute Spearman ρ between `[1,2,3,4,5]` and `[mean_errors_1,...,mean_errors_5]`
- **FR-6.3:** Compute separately for MBPP+ and HumanEval+
- **FR-6.4:** Compute `round5_mean < round1_mean` as secondary check
- **FR-6.5:** Report p-value alongside ρ (informational)

### FR-7: Mechanism Verification
- **FR-7.1:** Log `"mypy_errors_round_{k}: {count}"` per problem per round (activation indicator)
- **FR-7.2:** `verify_mechanism_activated(round_error_counts)` returns `(activated, indicators)` where `activated = log_found AND rho_negative`
- **FR-7.3:** Log mechanism activation result

### FR-8: Visualization (Required + Autonomous)
- **FR-8.1 (REQUIRED):** Bar chart — mean mypy error count per round k=1..5 for MBPP+ and HumanEval+. Save to `docs/youra_research/h-m1/figures/gate_metrics.png`
- **FR-8.2 (AUTONOMOUS):** Line plot of mean ± std mypy error count vs round k for both datasets
- **FR-8.3 (AUTONOMOUS):** Per-problem heatmap (problems × rounds) of mypy error count
- **FR-8.4 (AUTONOMOUS):** Box plots of per-problem mypy error count distribution at each round
- All figures saved to `docs/youra_research/h-m1/figures/`

### FR-9: Results Persistence
- **FR-9.1:** Save per-round per-problem results: `docs/youra_research/h-m1/results/results_{benchmark}.jsonl`
  - Record: `{task_id, round_k, mypy_error_count, exec_passed, repaired}`
- **FR-9.2:** Save aggregate summary: `docs/youra_research/h-m1/results/summary.json`
  - Include: `{benchmark, mean_errors_by_round, spearman_rho, p_value, round5_less_than_round1, gate_passed}`
- **FR-9.3:** Optional: save generated/repaired solutions for inspection

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
| Split | All 378 problems |
| Preprocessing | None |

### 4.2 HumanEval+ (Secondary)

| Field | Value |
|-------|-------|
| Name | HumanEval+ (EvalPlus augmented) |
| Source | `evalplus` Python package |
| Load call | `get_human_eval_plus()` |
| Problems | 164 |
| Download | Auto (no manual step needed) |
| Split | All 164 problems |
| Preprocessing | None |

**Note:** Both datasets auto-download via evalplus on first use. No data-preparation task needed (same as H-E1).

---

## 5. Evaluation Metrics

### 5.1 Primary Metric
- **Spearman ρ (MBPP+):** Spearman correlation between round number `[1,2,3,4,5]` and `[mean_errors_1,...,mean_errors_5]`
- Gate: ρ < 0 required (negative correlation = error count decreases with round)

### 5.2 Secondary Metrics
- **Spearman ρ (HumanEval+):** Same computation on HumanEval+ subset
- **round5_mean < round1_mean:** Boolean check on both datasets
- **Mean error trajectory:** `[mean_errors_k for k in 1..5]` for both datasets

### 5.3 Gate Evaluation

| Result | Condition | Action |
|--------|-----------|--------|
| PASS | `Spearman ρ < 0` on MBPP+ | Continue to H-M2, H-M3 |
| FAIL | `Spearman ρ ≥ 0` on MBPP+ | Pipeline stops; H-M2/H-M3 blocked |

---

## 6. Non-Functional Requirements

### 6.1 Reproducibility
- Initial generation: `seed=42` via OpenAI `seed` parameter
- Repair rounds: `temperature=0.0` (deterministic given same prompt)
- mypy flags fixed: `--ignore-missing-imports --no-strict-optional`

### 6.2 Error Handling (Extended from H-E1)
- OpenAI API errors: exponential backoff (max 3 retries); log and skip if persistent
- mypy `FileNotFoundError`: FAIL immediately with install instructions
- mypy `TimeoutExpired` (10s): log and count as 0 errors
- EvalPlus exceptions: treat as FAIL (conservative)
- Checkpoint/resume: save results incrementally to allow restart after interruption

### 6.3 Performance
- Estimated wall time: 90-150 minutes (542 × 5 rounds × ~2s avg LLM call)
- No GPU required
- API rate limiting: respect OpenAI rate limits (use `time.sleep` between calls if needed)

### 6.4 Logging
- Per problem: `"problem={task_id} round={k} mypy_errors={count} exec_passed={bool}"`
- Progress: `"[{benchmark}] {i}/{total} problems complete"`
- Mechanism: `"mypy_errors_round_{k}: {count}"` (activation indicator)

---

## 7. Dependencies

### 7.1 Python Packages (pip install)

| Package | Purpose |
|---------|---------|
| `evalplus` | Dataset loading + test suite evaluation (inherited from H-E1) |
| `openai` | GPT-4o-mini API client (inherited from H-E1) |
| `mypy` | Static type error analysis (inherited from H-E1) |
| `scipy` | Spearman ρ computation (`scipy.stats.spearmanr`) |
| `matplotlib` | Figure generation (inherited from H-E1) |
| `tqdm` | Progress bar |
| `python-dotenv` | Load OPENAI_API_KEY from .env |

### 7.2 Environment Variables
- `OPENAI_API_KEY`: Required — OpenAI API access for GPT-4o-mini

### 7.3 External References (for repair loop pattern)
- Johin2/iterative-code-repair: GitHub — iterative repair on HumanEval/MBPP with k=5 rounds
- sola-st/PyTy: GitHub — mypy-driven type error repair pattern
- H-E1 codebase: `docs/youra_research/h-e1/code/` — reuse `evaluate_solution`, `run_mypy`, dataset loading

### 7.4 System Requirements
- Python 3.9+
- Network access to OpenAI API
- No GPU required

---

## 8. Success Criteria

| Criterion | Threshold | Status |
|-----------|-----------|--------|
| Repair loop runs end-to-end | No unhandled exceptions, k=1..5 for all problems | Required |
| mypy errors recorded per round | All (problem, round) pairs logged | Required |
| Mechanism activation | `mypy_errors_round_{k}` logged AND ρ < 0 | Required |
| **PASS gate** | `Spearman ρ < 0` on MBPP+ | Primary gate (MUST_WORK) |
| Secondary check | `round5_mean < round1_mean` on both datasets | Informational |
| Figures generated | `gate_metrics.png` exists | Required |
| Results persisted | `summary.json` exists | Required |

---

## 9. File Structure

```
docs/youra_research/h-m1/
├── 02c_experiment_brief.md    # Phase 2C input
├── 03_prd.md                  # This file
├── 03_architecture.md         # Phase 3 output
├── 03_logic.md                # Phase 3 output
├── 03_config.md               # Phase 3 output
├── 03_tasks.yaml              # Phase 3 task list
├── code/
│   ├── repair_loop.py         # Condition B repair loop (new)
│   ├── pipeline.py            # Extended pipeline orchestration
│   ├── analysis.py            # Spearman ρ computation, trajectory analysis
│   ├── visualize.py           # Figure generation
│   └── run.py                 # CLI entry point
├── figures/
│   ├── gate_metrics.png       # Required
│   └── *.png                  # Autonomous
└── results/
    ├── results_mbpp.jsonl
    ├── results_humaneval.jsonl
    └── summary.json
```
