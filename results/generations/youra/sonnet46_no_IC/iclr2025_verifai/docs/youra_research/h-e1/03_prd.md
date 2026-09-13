---
title: "PRD: H-E1 Pylint/Mypy Iterative Repair PoC"
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
phase: 3
date: "2026-08-05"
status: complete
stepsCompleted:
  - executive_summary
  - problem_statement
  - functional_requirements
  - non_functional_requirements
  - success_criteria
  - data_specification
  - dependencies
---

# Product Requirements Document: H-E1

## 1. Executive Summary

**Hypothesis:** Under HumanEval and MBPP benchmarks, if pylint/mypy static analysis feedback is applied in iterative repair mode at fixed token budget B=1000 output tokens per problem using Llama 3.1 8B Instruct, then a measurable pass@1 delta (positive, near-zero, or negative) over no-feedback baseline is produced.

**Gate:** MUST_WORK (EXISTENCE PoC)  
**Pass Condition:** Δ_pylint is computable and finite on all 538 problems  
**Tier:** LIGHT (≤15 tasks total, 4-8 Epics)

This PoC establishes baseline measurement infrastructure for the full VerifAI verification chain (H-E1 → H-M1 → H-M2 → H-M3). A null result (Δ_pylint ≈ 0) is as valid as a positive result.

---

## 2. Problem Statement

**Research Gap:** No prior work has measured whether pylint/mypy static analysis feedback, when used as the repair signal in an iterative LLM code repair loop, improves functional correctness (pass@1) on HumanEval/MBPP benchmarks. Existing work (Arimbur 2026, Blyth et al. 2025) shows:
- Execution feedback: +9.8pp HumanEval, +16.0pp MBPP with Llama 3.1 8B (Arimbur 2026)
- Pylint feedback: reduces static analysis violations but effect on functional correctness is UNKNOWN (Blyth et al. 2025)

**What We Need to Build:** An end-to-end experiment system that:
1. Generates Python solutions for HumanEval + MBPP using Llama 3.1 8B (greedy)
2. Runs pylint + mypy on generated code
3. Feeds static analysis feedback into repair prompts
4. Re-generates within token budget B=1000
5. Evaluates pass@1 for both no-feedback baseline and pylint repair conditions
6. Produces Δ_pylint = pass@1(pylint) - pass@1(baseline) for both benchmarks

---

## 3. Functional Requirements

### FR-1: No-Feedback Baseline Evaluation
**Description:** Evaluate Llama 3.1 8B Instruct on HumanEval (164 problems) and MBPP (374 problems) using single-shot greedy generation (no repair). This is the control condition.

**Inputs:**
- HumanEval: `evalplus.data.get_human_eval_plus()` or `openai/openai_humaneval` (HuggingFace)
- MBPP: `evalplus.data.get_mbpp_plus()` or `evalplus/mbppplus` (HuggingFace)

**Outputs:**
- `results/baseline_humaneval.jsonl`: task_id, prompt, generated_code, passed (bool)
- `results/baseline_mbpp.jsonl`: task_id, prompt, generated_code, passed (bool)
- `pass@1_baseline_humaneval`: float (expected ~0.671 per Arimbur 2026)
- `pass@1_baseline_mbpp`: float (expected ~0.556 per Arimbur 2026)

**Evaluation:** `evaluate_functional_correctness` (human-eval package) for HumanEval; test_list assertion execution for MBPP

**Model Config:**
- `meta-llama/Llama-3.1-8B-Instruct` (Groq API preferred: `llama-3.1-8b-instant`)
- temperature=0.0, do_sample=False, seed=42, max_new_tokens=1000

---

### FR-2: Pylint/Mypy Iterative Repair Condition
**Description:** For each problem, apply iterative pylint/mypy repair within token budget B=1000 total output tokens. Start from the same greedy generation as baseline (Round 0), then repair up to 3 times using pylint/mypy feedback.

**Algorithm:**
```python
def pylint_repair_loop(problem, model, B=1000):
    code = generate_code(problem, model)  # Round 0
    tokens_used = count_tokens(code)
    
    for repair_round in range(1, 4):  # max 3 repair rounds
        if tokens_used >= B:
            break
        feedback = run_pylint_mypy(code)
        if feedback is None:
            break  # no static issues
        remaining = B - tokens_used
        repaired_code = generate_repair(code, feedback, model, max_tokens=remaining)
        tokens_used += count_tokens(repaired_code)
        code = repaired_code
    
    return code
```

**Pylint/Mypy Runner:**
- subprocess call to `pylint --output-format=text --score=no {tmp_file}`
- subprocess call to `mypy --ignore-missing-imports {tmp_file}`
- timeout: 30 seconds per tool
- feedback=None if both tools return no issues

**Repair Prompt Template:**
```
The following Python code has static analysis issues:
{previous_code}

Static analysis feedback:
{pylint_mypy_output}

Please fix the code to address these issues while maintaining functional correctness.
Return only the corrected function.
```

**Outputs:**
- `results/pylint_humaneval.jsonl`: task_id, rounds, tokens_used, per_round_results, final_passed
- `results/pylint_mbpp.jsonl`: same schema
- `pass@1_pylint_humaneval`: float
- `pass@1_pylint_mbpp`: float
- `results/pylint_coverage.jsonl`: for each baseline failure, did pylint/mypy flag it? (pre-execution)

---

### FR-3: Metric Computation and Reporting
**Description:** Compute all primary metrics and generate structured results.

**Metrics:**
- `delta_pylint_humaneval` = pass@1_pylint_humaneval - pass@1_baseline_humaneval
- `delta_pylint_mbpp` = pass@1_pylint_mbpp - pass@1_baseline_mbpp
- `per_round_pass@1`: pass@1 at each repair round (0, 1, 2, 3) for pylint condition
- `pylint_coverage_fraction`: fraction of baseline failures receiving ≥1 pylint/mypy warning/error
- `token_budget_distribution`: histogram of total tokens used per problem

**Output:** `results/metrics.json` with all metrics; `results/summary.md` with human-readable summary

---

### FR-4: Visualization Generation
**Description:** Generate all required figures.

**Figure 1 (MANDATORY):** Bar chart — pass@1 for baseline vs pylint condition on HumanEval and MBPP (4 bars)

**Figure 2:** Line plot — per-round pass@1 trajectory (rounds 0-3) for pylint condition on both benchmarks

**Figure 3:** Histogram — token budget distribution (total tokens used per problem)

**Figure 4:** Bar chart — pylint coverage analysis (fraction of baseline failures flagged by pylint by category: Error/Warning/Convention vs not flagged)

**Output location:** `docs/youra_research/h-e1/figures/`

---

### FR-5: Experiment Orchestration
**Description:** Single entry-point script to run the full experiment reproducibly.

**Script:** `experiments/h-e1/run_experiment.py`

**CLI:**
```bash
python run_experiment.py \
  --model llama-3.1-8b-instant \
  --backend groq \
  --token-budget 1000 \
  --max-repair-rounds 3 \
  --seed 42 \
  --output-dir results/
```

**Resume support:** If partial results exist, skip already-completed problems.

---

## 4. Data Specification

### Dataset 1: HumanEval
| Field | Value |
|-------|-------|
| Name | HumanEval |
| Source | `evalplus/evalplus` (HuggingFace: `openai/openai_humaneval`) |
| Problems | 164 (full standard test set) |
| Format | task_id, prompt, canonical_solution, test, entry_point |
| Download | `pip install evalplus` then `get_human_eval_plus()` |
| Evaluation | `evaluate_functional_correctness` from `openai/human-eval` package |
| Split | Full test set (no train/val split in HumanEval) |

### Dataset 2: MBPP
| Field | Value |
|-------|-------|
| Name | MBPP (Sanitized) |
| Source | HuggingFace: `evalplus/mbppplus` |
| Problems | 374 (full standard test set per Phase 2B spec) |
| Format | task_id, text, code, test_list, test_setup_code |
| Download | `evalplus.data.get_mbpp_plus()` |
| Evaluation | Execute test_list assertions in namespace with generated code |
| Split | Full test set |

**Total evaluation scale:** 538 problems × 2 conditions = 1,076 problem-condition evaluations

**No manual download required** — both datasets load via pip package.

---

## 5. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed: 42
- Greedy decoding (temperature=0.0, deterministic)
- All dependencies pinned in `requirements.txt`
- Results saved incrementally (resume on failure)

### NFR-2: Execution Safety
- Sandboxed execution: Python subprocess with 15-second timeout per test case
- Isolated subprocess for pylint/mypy (no code injected into main process)
- Temp file cleanup after each pylint/mypy run

### NFR-3: Budget Compliance
- Hard token budget: B=1000 total output tokens per problem
- Token counting before each repair round
- If remaining < 100 tokens: skip repair round

### NFR-4: Logging
- LIGHT tier: CSV/JSON output + print progress (no WandB required)
- Progress: tqdm or print every 50 problems
- Per-problem logging: task_id, round, tokens_used, passed, pylint_issues_count

---

## 6. Success Criteria

### PoC Pass (MUST_WORK gate):
1. Pylint repair loop runs end-to-end on all 538 problems without systematic failure (≥95% completion)
2. Δ_pylint is computable and finite (not NaN, not systematic None)

### Secondary (informational):
3. |Δ_pylint| > 0 on at least one benchmark (any measurable effect)
4. All 4 figures generated successfully
5. `metrics.json` contains all required fields

### Failure Gate:
- If pylint subprocess crashes on ≥50% of problems → PIVOT to custom 50-100 line wrapper per Phase 2B fallback plan

---

## 7. Dependencies

### 7.1 Python Packages
```
# Core
groq>=0.9.0              # Llama 3.1 8B via Groq API (primary inference)
transformers>=4.43.0     # HuggingFace fallback
torch>=2.1.0             # PyTorch (fallback local inference)

# Evaluation
evalplus>=0.3.0          # HumanEval/MBPP loading and evaluation
human-eval>=1.0.0        # evaluate_functional_correctness

# Static analysis
pylint>=3.0.0
mypy>=1.8.0

# Data
datasets>=2.20.0
numpy>=1.24.0
pandas>=2.0.0

# Visualization
matplotlib>=3.7.0

# Utilities
tqdm>=4.65.0
pyyaml>=6.0
```

### 7.2 External References
- Johin2/iterative-code-repair: Base infrastructure pattern (Arimbur 2026)
- cyb3rlab/CodeEnhancer: Pylint integration pattern
- openai/human-eval: evaluate_functional_correctness implementation

### 7.3 API Keys
- `GROQ_API_KEY`: Required for Llama 3.1 8B via Groq API
- Alternative: Local HuggingFace inference (GPU required, ~16GB VRAM for 8B model)

---

## 8. File Structure

```
experiments/h-e1/
├── run_experiment.py          # Main entry point
├── data_loader.py             # HumanEval + MBPP loading
├── model_client.py            # Groq/HuggingFace model interface
├── code_executor.py           # Sandboxed execution (15s timeout)
├── static_analyzer.py         # pylint + mypy subprocess runner
├── repair_loop.py             # Iterative repair logic
├── evaluator.py               # pass@1 computation
├── visualizer.py              # Figure generation
├── requirements.txt
└── README.md

results/
├── baseline_humaneval.jsonl
├── baseline_mbpp.jsonl
├── pylint_humaneval.jsonl
├── pylint_mbpp.jsonl
├── pylint_coverage.jsonl
└── metrics.json

docs/youra_research/h-e1/figures/
├── figure1_pass_at_1_comparison.png
├── figure2_per_round_trajectory.png
├── figure3_token_budget_distribution.png
└── figure4_pylint_coverage_analysis.png
```

---

## 9. Out of Scope

- Fine-tuning Llama 3.1 8B (inference-only experiment)
- Multiple model comparison (H-M1 scope)
- Execution feedback condition (H-M1 scope)
- Qwen2.5-Coder-7B replication (H-M1 scope)
- Statistical significance testing / McNemar's test (H-M1 scope)
- Bandit security analysis (not needed for PoC)
- WandB experiment tracking (LIGHT tier: CSV output sufficient)
