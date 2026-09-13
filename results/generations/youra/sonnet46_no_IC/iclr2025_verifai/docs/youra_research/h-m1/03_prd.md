---
title: "PRD: H-M1 Execution Test Feedback Iterative Repair — Mechanism Comparison"
hypothesis_id: h-m1
hypothesis_type: MECHANISM
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

# Product Requirements Document: H-M1

## 1. Executive Summary

**Hypothesis:** Under HumanEval and MBPP benchmarks, if execution test feedback is applied in iterative repair mode at B=1000 output tokens per problem using Llama 3.1 8B (compared to pylint/mypy at identical budget), then execution test feedback achieves a statistically significantly larger pass@1 improvement delta over no-feedback baseline (McNemar's test, α=0.05), because execution feedback reveals the full distribution of code errors (expected vs. actual output) while pylint/mypy reveals only a subset (syntax, type, style).

**Gate:** MUST_WORK  
**Pass Condition:** Δ_execution > Δ_pylint with McNemar p<0.05 on HumanEval AND MBPP for Llama 3.1 8B  
**Tier:** FULL (≤30 tasks total, 6-12 Epics)  
**Prerequisite:** H-E1 COMPLETED — pylint infrastructure reused; Δ_pylint already measured

This experiment compares two feedback types at equal token budget, extending H-E1 infrastructure with an execution repair loop. A null result (p>0.05) is a publishable "pylint parity" finding but does not confirm H-M1.

---

## 2. Problem Statement

**Research Gap:** H-E1 established that pylint/mypy repair is measurable (Δ_pylint HumanEval=-4.27pp, MBPP=+18.25pp). The core question for H-M1 is whether execution test feedback dominates pylint feedback at iso-compute (B=1000 tokens). Prior work (Arimbur 2026) shows execution feedback achieves +9.8pp HumanEval / +16.0pp MBPP at 4 rounds, but no prior work compares execution vs. pylint at identical token budget using McNemar's paired statistical test.

**MBPP Risk:** H-E1 Δ_pylint MBPP=+18.25pp is surprisingly large. If Δ_execution MBPP at B=1000 achieves only ~10-12pp, execution feedback may lose on MBPP → gate fails on MBPP. This is a known scientific risk.

**What We Need to Build:** Extend H-E1 infrastructure with:
1. Execution test feedback repair loop (generate → sandbox execute → format error → repair)
2. McNemar's test comparing paired (execution_pass, pylint_pass) outcomes per problem
3. Replication with Qwen2.5-Coder-7B-Instruct
4. Per-round intermediate results saved for H-M3 downstream use
5. Bootstrap 95% CI on delta difference

---

## 3. Functional Requirements

### FR-1: No-Feedback Baseline (Reuse from H-E1)
**Description:** Reuse baseline pass@1 values computed in H-E1. Do NOT re-run baseline generation unless H-E1 results are unavailable.

**Reuse Sources:**
- `docs/youra_research/h-e1/results/baseline_humaneval.jsonl` — per-problem pass/fail
- `docs/youra_research/h-e1/results/baseline_mbpp.jsonl` — per-problem pass/fail
- H-E1 measured: pass@1_baseline_humaneval ≈ 0.671; pass@1_baseline_mbpp (from actual run)

**Fallback (if H-E1 results unavailable):** Re-run baseline using same config as H-E1 FR-1:
- Model: `meta-llama/Llama-3.1-8B-Instruct` (Groq: `llama-3.1-8b-instant`)
- Greedy decoding, temperature=0.0, seed=42, max_new_tokens=1000
- HumanEval (164) + MBPP (374/378)

**Outputs:**
- `results/h-m1/baseline_humaneval.jsonl` (symlink or copy from H-E1)
- `results/h-m1/baseline_mbpp.jsonl`
- `pass@1_baseline_humaneval`: float
- `pass@1_baseline_mbpp`: float

---

### FR-2: Pylint/Mypy Repair Condition (Reuse from H-E1)
**Description:** Reuse pylint repair results from H-E1. These are the comparison baseline for McNemar's test.

**Reuse Sources:**
- `docs/youra_research/h-e1/results/pylint_humaneval.jsonl` — per-problem pass/fail + rounds
- `docs/youra_research/h-e1/results/pylint_mbpp.jsonl`
- H-E1 measured: Δ_pylint HumanEval=-0.0427; Δ_pylint MBPP=+0.1825

**Fallback:** Re-run pylint repair using H-E1 FR-2 protocol if results are unavailable.

**Outputs (for McNemar pairing):**
- `results/h-m1/pylint_humaneval.jsonl` (symlink or copy from H-E1)
- `results/h-m1/pylint_mbpp.jsonl`

---

### FR-3: Execution Test Feedback Repair Loop (Llama 3.1 8B — PRIMARY NEW CONDITION)
**Description:** For each problem, apply iterative execution-based repair within token budget B=1000. Start from Round 0 generation (same as H-E1 baseline), run unit tests in isolated sandbox, feed error message back as repair prompt, repeat up to 3 rounds.

**Algorithm:**
```python
def execution_repair_loop(problem: dict, generate_fn, B: int = 1000) -> dict:
    """Iterative execution feedback repair within token budget B."""
    code = generate_fn(problem["prompt"], max_tokens=min(300, B))  # Round 0
    tokens_used = count_tokens(code)
    exec_result = run_unit_tests_in_sandbox(code, problem["test"])
    round_results = [{"round": 0, "code": code, "passed": exec_result["passed"]}]
    
    repair_round = 1
    while tokens_used < B and not exec_result["passed"]:
        error_msg = exec_result["error"]
        remaining = B - tokens_used
        if remaining < 50:
            break  # Not enough budget for meaningful repair
        
        repair_prompt = (
            f"The following Python function has a bug:\n\n{problem['prompt']}\n\n"
            f"Your previous attempt:\n```python\n{code}\n```\n\n"
            f"Execution error:\n{error_msg}\n\n"
            f"Please fix the function. Return only the corrected Python function."
        )
        repaired_code = generate_fn(repair_prompt, max_tokens=min(300, remaining))
        tokens_used += count_tokens(repaired_code)
        code = repaired_code
        exec_result = run_unit_tests_in_sandbox(code, problem["test"])
        
        round_results.append({
            "round": repair_round, "code": code,
            "passed": exec_result["passed"], "feedback_type": "execution",
            "error_snippet": error_msg[:200] if error_msg else None
        })
        repair_round += 1
    
    return {
        "final_code": code, "passed": exec_result["passed"],
        "rounds": round_results, "tokens_used": tokens_used
    }
```

**Sandbox Execution:**
```python
import subprocess, tempfile, os

def run_unit_tests_in_sandbox(code: str, test_code: str, timeout: int = 15) -> dict:
    combined = code + "\n\n" + test_code
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(combined); tmp_path = f.name
    try:
        result = subprocess.run(
            ["python", "-I", tmp_path],  # -I: isolated mode
            capture_output=True, text=True, timeout=timeout
        )
        passed = result.returncode == 0
        error_output = result.stderr.strip() or result.stdout.strip()
        return {"passed": passed, "error": error_output if not passed else None,
                "returncode": result.returncode}
    except subprocess.TimeoutExpired:
        return {"passed": False, "error": "TimeoutError: execution exceeded 15s", "returncode": -1}
    finally:
        os.unlink(tmp_path)
```

**Outputs (Llama 3.1 8B):**
- `results/h-m1/execution_humaneval_llama.jsonl`: task_id, rounds (list), tokens_used, final_passed
- `results/h-m1/execution_mbpp_llama.jsonl`: same schema
- `results/h-m1/round_results_humaneval_llama.json`: per-round pass@1 (rounds 0-3) — **REQUIRED BY H-M3**
- `results/h-m1/round_results_mbpp_llama.json`: per-round pass@1 — **REQUIRED BY H-M3**
- `pass@1_execution_humaneval_llama`: float
- `pass@1_execution_mbpp_llama`: float

---

### FR-4: Execution Test Feedback Repair Loop (Qwen2.5-Coder-7B — REPLICATION)
**Description:** Same execution repair protocol as FR-3, applied to Qwen2.5-Coder-7B-Instruct. Provides replication check: does the directional ranking (Δ_execution > Δ_pylint) hold for a different 7B-scale model?

**Model Config:**
- `Qwen/Qwen2.5-Coder-7B-Instruct` (local vLLM or Groq if available)
- Greedy decoding, temperature=0.0, seed=42, B=1000 tokens, max 3 repair rounds

**Outputs:**
- `results/h-m1/execution_humaneval_qwen.jsonl`
- `results/h-m1/execution_mbpp_qwen.jsonl`
- `results/h-m1/round_results_humaneval_qwen.json`
- `results/h-m1/round_results_mbpp_qwen.json`
- `pass@1_execution_humaneval_qwen`: float
- `pass@1_execution_mbpp_qwen`: float

---

### FR-5: Statistical Comparison — McNemar's Test
**Description:** Run McNemar's test comparing paired (execution_pass, pylint_pass) per problem. Report p-value, contingency table, direction, and bootstrap 95% CI on delta difference.

**Algorithm:**
```python
from statsmodels.stats.contingency_tables import mcnemar
import numpy as np

def run_mcnemar_test(pylint_results: dict, execution_results: dict, problems: list) -> dict:
    both_pass = pylint_only = exec_only = both_fail = 0
    
    for task_id in problems:
        p = pylint_results[task_id]["passed"]
        e = execution_results[task_id]["passed"]
        if p and e: both_pass += 1
        elif p and not e: pylint_only += 1
        elif not p and e: exec_only += 1
        else: both_fail += 1
    
    table = np.array([[both_pass, pylint_only], [exec_only, both_fail]])
    n_discordant = pylint_only + exec_only
    exact = (n_discordant < 25)
    result = mcnemar(table, exact=exact, correction=not exact)
    
    return {
        "table": table.tolist(),
        "n_discordant": n_discordant,
        "exec_only": exec_only,    # c: execution BETTER
        "pylint_only": pylint_only, # b: pylint BETTER
        "statistic": result.statistic,
        "pvalue": float(result.pvalue),
        "exact": exact,
        "significant": result.pvalue < 0.05,
        "direction": "execution > pylint" if exec_only > pylint_only else "pylint >= execution"
    }

def bootstrap_ci_delta_diff(pylint_pass, exec_pass, baseline_pass, n_bootstrap=10000):
    """95% CI on (Δ_execution - Δ_pylint)."""
    from scipy.stats import bootstrap
    n = len(pylint_pass)
    diffs = []
    for _ in range(n_bootstrap):
        idx = np.random.choice(n, n, replace=True)
        d_exec = exec_pass[idx].mean() - baseline_pass[idx].mean()
        d_pylint = pylint_pass[idx].mean() - baseline_pass[idx].mean()
        diffs.append(d_exec - d_pylint)
    return np.percentile(diffs, [2.5, 97.5])
```

**Outputs:**
- `results/h-m1/mcnemar_humaneval.json`: table, p-value, exec_only, pylint_only, direction, CI
- `results/h-m1/mcnemar_mbpp.json`: same schema
- `results/h-m1/mcnemar_qwen_humaneval.json`: replication model
- `results/h-m1/mcnemar_qwen_mbpp.json`: replication model

---

### FR-6: Metric Computation and Summary Report
**Description:** Compute all primary and secondary metrics; generate structured results file.

**Primary Metrics:**
- `delta_execution_humaneval` = pass@1_execution_humaneval - pass@1_baseline_humaneval
- `delta_execution_mbpp` = pass@1_execution_mbpp - pass@1_baseline_mbpp
- `delta_diff_humaneval` = delta_execution_humaneval - delta_pylint_humaneval
- `delta_diff_mbpp` = delta_execution_mbpp - delta_pylint_mbpp
- `mcnemar_p_humaneval`: McNemar p-value (HumanEval, Llama 3.1 8B)
- `mcnemar_p_mbpp`: McNemar p-value (MBPP, Llama 3.1 8B)
- `gate_passed`: True if both p<0.05 AND exec_only > pylint_only on BOTH benchmarks

**Per-Round Metrics (for H-M3):**
- pass@1 after each repair round (rounds 0-3) for execution condition, both benchmarks
- Saved to `round_results_*.json` — MANDATORY for H-M3 consumption

**Replication Metrics (Qwen):**
- Same metrics for Qwen2.5-Coder-7B-Instruct
- Directional consistency check vs. Llama 3.1 8B

**Output:** `results/h-m1/metrics.json` (all metrics); `results/h-m1/summary.md` (human-readable)

---

### FR-7: Mechanism Verification (Pilot Check)
**Description:** Before full run, verify execution repair loop activates on a 20-problem pilot.

**Check:**
- Execution feedback applied to >20% of pilot problems
- Avg repair rounds > 0 on problems that fail at Round 0
- No systematic sandbox failure (>95% complete without crash)

**Code:**
```python
def verify_mechanism(problems_sample, generate_fn, n=20):
    sample = list(problems_sample.values())[:n]
    feedback_applied = []
    for problem in sample:
        result = execution_repair_loop(problem, generate_fn, B=1000)
        n_feedback = len([r for r in result["rounds"] if r.get("feedback_type") == "execution"])
        feedback_applied.append(n_feedback > 0)
    assert sum(feedback_applied) > 0.2 * n, "MECHANISM NOT ACTIVE"
    print(f"✓ Mechanism verified: feedback applied in {sum(feedback_applied)}/{n} problems")
```

---

### FR-8: Visualization Generation
**Description:** Generate all required figures.

**Figure 1 (MANDATORY):** Delta comparison bar chart — Δ_execution and Δ_pylint for HumanEval and MBPP (4 bars) with 95% CI error bars. Annotate McNemar p-value. Both Llama 3.1 8B and Qwen2.5-Coder-7B panels.

**Figure 2 (MANDATORY):** Per-round pass@1 trajectory — line plot (rounds 0-3) for execution vs. pylint conditions on both benchmarks (Llama 3.1 8B). Pre-data for H-M3.

**Figure 3:** Replication comparison — side-by-side Δ for Llama 3.1 8B vs Qwen2.5-Coder-7B.

**Figure 4:** Token budget distribution — histogram of total tokens used per problem (execution condition).

**Figure 5:** Error type analysis — distribution of error types (AssertionError, NameError, TypeError, etc.) and repair success rates by error type.

**Output location:** `docs/youra_research/h-m1/figures/`

---

### FR-9: Experiment Orchestration
**Description:** Single entry-point script with resume support.

**Script:** `experiments/h-m1/run_experiment.py`

**CLI:**
```bash
python run_experiment.py \
  --model llama-3.1-8b-instant \  # primary
  --backend groq \
  --token-budget 1000 \
  --max-repair-rounds 3 \
  --seed 42 \
  --reuse-h-e1-results \          # reuse baseline + pylint from H-E1
  --output-dir results/h-m1/ \
  --run-replication               # also run Qwen2.5-Coder-7B
```

**Resume support:** If partial results exist (`execution_humaneval_llama.jsonl`), skip already-completed problems (check by task_id).

---

## 4. Data Specification

### Dataset 1: HumanEval
| Field | Value |
|-------|-------|
| Name | HumanEval |
| Source | `evalplus/evalplus` (HuggingFace: `openai/openai_humaneval`) |
| Problems | 164 (full standard test set — same as H-E1) |
| Format | task_id, prompt, canonical_solution, test, entry_point |
| Download | `pip install evalplus` → `get_human_eval_plus()` |
| Evaluation | Sandboxed subprocess execution against test assertions |
| Split | Full test set (no train/val in HumanEval) |

### Dataset 2: MBPP
| Field | Value |
|-------|-------|
| Name | MBPP |
| Source | HuggingFace: `evalplus/mbppplus` |
| Problems | 374/378 (same set as H-E1 for controlled comparison) |
| Format | task_id, text, code, test_list, test_setup_code |
| Download | `evalplus.data.get_mbpp_plus()` |
| Evaluation | Execute test_list assertions via sandboxed subprocess |
| Split | Full test set |

**Total evaluation scale (NEW evaluations for H-M1):**
- Llama 3.1 8B execution condition: 164 + 374 = 538 problems
- Qwen2.5-Coder-7B execution condition: 538 problems
- Reused from H-E1: baseline (538) + pylint (538)
- **Grand total: ~2,152 problem-condition evaluations (538 new for Llama + 538 new for Qwen)**

**No manual download required** — all datasets via evalplus pip package.

---

## 5. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed: 42
- Greedy decoding (temperature=0.0, deterministic)
- All dependencies pinned in `requirements.txt`
- Results saved incrementally per problem (resume on failure)
- H-E1 results reused directly (no re-computation) for controlled comparison

### NFR-2: Execution Safety
- Sandboxed execution: Python subprocess (`python -I`) with 15-second timeout per test
- Temp file cleanup after each sandbox run
- No code injected into main process
- Memory isolation via subprocess (not exec())

### NFR-3: Budget Compliance
- Hard token budget: B=1000 total output tokens per problem (across all repair rounds)
- Token counting before each repair round
- If remaining < 50 tokens: skip repair round
- Max 3 repair rounds (within B=1000 budget)

### NFR-4: Per-Round Data for H-M3
- CRITICAL: Save `round_results_*.json` with per-round (rounds 0-3) pass@1 for ALL problems
- This data is consumed by H-M3 experiment — missing = H-M3 blocked
- Schema: `{task_id: {round_0: bool, round_1: bool, round_2: bool, round_3: bool}}`

### NFR-5: Logging
- FULL tier: JSON output + tqdm progress (no WandB required for PoC)
- Progress: tqdm every 50 problems
- Per-problem logging: task_id, round, tokens_used, passed, error_type

---

## 6. Success Criteria

### PoC Pass (MUST_WORK gate):
1. Execution repair loop runs end-to-end on all 538 problems without systematic failure (≥95% completion)
2. Δ_execution > Δ_pylint with McNemar p<0.05 on HumanEval for Llama 3.1 8B
3. Δ_execution > Δ_pylint with McNemar p<0.05 on MBPP for Llama 3.1 8B
4. Conditions 2 AND 3 BOTH satisfied → gate PASS

### Secondary (informational):
5. Qwen2.5-Coder-7B shows same directional ranking (replication consistency)
6. Per-round data saved for H-M3
7. All 5 figures generated
8. `metrics.json` with all required fields

### Null Result Gate:
- If p>0.05 on either benchmark → EXPLORE routing (publishable as "pylint parity at B=1000")
- If Δ_execution < +1pp on HumanEval → investigate mechanism failure (model not following repair instructions)

### Failure Fallback:
- If sandbox crashes >20% of problems → add memory limits (`resource.setrlimit`) or switch to Docker
- If Groq API unavailable → switch to local vLLM (same H-E1 infrastructure)

---

## 7. Dependencies

### 7.1 Python Packages
```
# Core (inherited from H-E1)
groq>=0.9.0              # Llama 3.1 8B via Groq API (primary inference)
vllm>=0.4.0              # Local inference fallback
transformers>=4.43.0
torch>=2.1.0

# Evaluation
evalplus>=0.3.0
human-eval>=1.0.0

# Statistical testing (NEW for H-M1)
statsmodels>=0.14.0      # McNemar's test
scipy>=1.11.0            # bootstrap CI

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

### 7.2 External References (Reuse from H-E1)
- Johin2/iterative-code-repair: Base execution repair infrastructure (Arimbur 2026)
- openai/human-eval: `evaluate_functional_correctness`
- statsmodels: McNemar's test implementation

### 7.3 API Keys
- `GROQ_API_KEY`: For Llama 3.1 8B / Qwen2.5-Coder-7B via Groq API
- Alternative: Local vLLM (~16GB VRAM for 8B models)

### 7.4 H-E1 Result Dependencies
- `docs/youra_research/h-e1/results/baseline_humaneval.jsonl`
- `docs/youra_research/h-e1/results/baseline_mbpp.jsonl`
- `docs/youra_research/h-e1/results/pylint_humaneval.jsonl`
- `docs/youra_research/h-e1/results/pylint_mbpp.jsonl`

---

## 8. File Structure

```
experiments/h-m1/
├── run_experiment.py              # Main entry point
├── data_loader.py                 # HumanEval + MBPP (reuse/adapt from H-E1)
├── model_client.py                # Groq/vLLM model interface (reuse from H-E1)
├── code_executor.py               # Sandboxed subprocess execution (reuse from H-E1)
├── execution_repair_loop.py       # NEW: execution feedback repair logic
├── pylint_repair_loader.py        # Load H-E1 pylint results for McNemar pairing
├── statistical_tests.py           # NEW: McNemar's test + bootstrap CI
├── evaluator.py                   # pass@1 computation (reuse from H-E1)
├── visualizer.py                  # Figure generation (extend from H-E1)
├── requirements.txt
└── README.md

results/h-m1/
├── execution_humaneval_llama.jsonl
├── execution_mbpp_llama.jsonl
├── execution_humaneval_qwen.jsonl
├── execution_mbpp_qwen.jsonl
├── round_results_humaneval_llama.json  # REQUIRED BY H-M3
├── round_results_mbpp_llama.json       # REQUIRED BY H-M3
├── round_results_humaneval_qwen.json
├── round_results_mbpp_qwen.json
├── mcnemar_humaneval.json
├── mcnemar_mbpp.json
├── mcnemar_qwen_humaneval.json
├── mcnemar_qwen_mbpp.json
└── metrics.json

docs/youra_research/h-m1/figures/
├── figure1_delta_comparison.png
├── figure2_per_round_trajectory.png
├── figure3_replication_comparison.png
├── figure4_token_budget_distribution.png
└── figure5_error_type_analysis.png
```

---

## 9. Out of Scope

- Fine-tuning any model (inference-only experiment)
- Bandit security analysis (not needed for PoC)
- WandB experiment tracking (FULL tier: JSON output sufficient)
- H-M2 error coverage analysis (separate hypothesis — uses H-M1 outputs as inputs)
- H-M3 per-round incremental analysis (uses `round_results_*.json` from this experiment)
- Beam search / sampling decoding (greedy only for reproducibility)
