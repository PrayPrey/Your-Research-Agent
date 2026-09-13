---
title: "PRD: H-M4 — Feedback Overhead Efficiency Ratio Measurement"
hypothesis_id: H-M4
hypothesis_type: MECHANISM
gate_type: SHOULD_WORK
phase: 3
stepsCompleted: [1, 2, 3, 4, 5, 6, 7]
date: 2026-08-31
author: yoon303@etri.re.kr
---

# Product Requirements Document: H-M4

## 1. Executive Summary

This experiment measures wall-clock overhead for all 4 feedback categories (execution monitoring, static analysis, type checking, SMT solving) on 538 coding problems (HumanEval 164 + MBPP 374) with GPT-4o-mini, then computes correctness-per-overhead efficiency ratios (Δpass@1 / mean_wall_clock_seconds). The primary claim: execution monitoring achieves the highest efficiency ratio (≥1.5× next-best, bootstrap p<0.05). Secondary: overhead ordering follows execution < static ≈ type < SMT.

## 2. Problem Statement

Prior hypotheses (H-E1, H-M1, H-M2) established that feedback-augmented repair improves pass@1 vs. vanilla generation, and H-M2 confirmed feedback specificity ordering. H-M3 tested whether per-iteration repair quality correlates with specificity (FAILED). H-M4 addresses the complementary question: even if repair quality doesn't differ by category, do overhead differences alone create distinct efficiency ratios that would guide practical system design? Measuring this requires precise timing instrumentation wrapping the existing 4-category verifier infrastructure.

## 3. Goals and Non-Goals

### Goals
- Measure per-problem wall-clock overhead for all 4 feedback categories across 538 problems
- Compute efficiency ratios (Δpass@1 / mean overhead) per category
- Statistically test whether execution monitoring achieves ≥1.5× ratio advantage (bootstrap p<0.05)
- Confirm overhead ordering (Kruskal-Wallis + pairwise Mann-Whitney U)
- Produce publication-quality figures for paper section on overhead-efficiency trade-offs

### Non-Goals
- Re-training or fine-tuning any model
- Testing on additional LLM backends beyond GPT-4o-mini
- Changing verifier logic from previous hypotheses (H-E1/H-M1/H-M2 implementations reused)
- Optimizing verifier speed (measurement only, not improvement)

## 4. Data Specification

### 4.1 Primary Dataset 1: HumanEval

| Property | Value |
|---|---|
| Name | OpenAI HumanEval |
| Version | Standard (164 problems) |
| Source | `openai/openai_humaneval` (HuggingFace) |
| Split | test (full set, 164 problems) |
| Format | task_id, prompt (function signature + docstring), canonical_solution, test, entry_point |
| Preprocessing | Use prompt as-is; strip trailing whitespace; wrap in standard execution harness |
| Download | Auto via HuggingFace datasets (no manual download required) |

```python
from datasets import load_dataset
humaneval = load_dataset("openai/openai_humaneval", split="test")  # 164 problems
```

### 4.2 Primary Dataset 2: MBPP (Sanitized)

| Property | Value |
|---|---|
| Name | Mostly Basic Programming Problems |
| Version | Sanitized split |
| Source | `google-research-datasets/mbpp` (HuggingFace), `sanitized` config |
| Split | test (374 problems from standard protocol: problems 11-510) |
| Format | task_id, text (problem description), code (solution), test_list, test_setup_code |
| Preprocessing | Convert test_list to assertion-based harness; use 'text' as prompt |
| Download | Auto via HuggingFace datasets (no manual download required) |

```python
mbpp = load_dataset("google-research-datasets/mbpp", "sanitized", split="test")  # 374 problems
```

### 4.3 Combined Dataset

- Total: 538 problems (HumanEval 164 + MBPP 374)
- Experiment runs: 538 × 4 categories = 2,152 repair loop executions

### 4.4 Baseline Data

- Vanilla pass@1 (no repair): from H-E1 run results
- If H-E1 results unavailable: re-run vanilla generation (temperature=0.2, 1 sample per problem)

## 5. Functional Requirements

### FR-1: Environment Setup
- Python 3.10+, OPENAI_API_KEY environment variable set
- Install: `openai`, `datasets`, `numpy`, `scipy`, `z3-solver`, `pyright` (via npm or pip), `matplotlib`, `seaborn`

### FR-2: Dataset Loader
- Load HumanEval (164 problems) and MBPP sanitized (374 problems) via HuggingFace
- Merge into unified 538-problem list with consistent schema: `{task_id, prompt, tests}`
- For MBPP: convert `test_list` to Python assertion strings; prepend `test_setup_code` if present

### FR-3: Verifier Infrastructure (Reuse from H-E1/H-M1/H-M2)
Implement or reuse all 4 verifier categories:

| Category | Implementation | Expected Overhead |
|---|---|---|
| Execution monitoring | subprocess execution of generated code + test assertions | ~100-500ms/problem |
| Static analysis | `subprocess.run(['pyright', '--outputjson', tmpfile])` | ~5-50ms/problem |
| Type checking | Same as static analysis (Pyright covers both) | ~5-50ms/problem |
| SMT solving | LLM constraint generation call + Z3 solve | ~700ms-10s/problem |

- SMT timeout: 30 seconds per problem (timeout = full overhead penalty + no pass)
- Each verifier returns `(feedback: str, passed: bool)`

### FR-4: Timing Instrumentation (Core H-M4 Contribution)
Implement `TimedFeedbackEvaluator` wrapping each verifier with `time.perf_counter()`:

```python
class TimedFeedbackEvaluator:
    def run_repair_loop(self, problem, initial_code, max_iters=3):
        """Returns (final_pass: bool, total_overhead_s: float, per_iter_times: list)"""
```

- Measure: wall-clock time for verifier call + LLM repair call per iteration
- Do NOT include initial code generation time in overhead (category-independent)
- Per-problem overhead = sum of all iteration times across max 3 iterations

### FR-5: Efficiency Ratio Computation

```python
def compute_efficiency_ratio(pass_after, pass_baseline, mean_overhead_s):
    """Δpass@1 / mean overhead seconds — higher = more efficient."""
    delta = pass_after - pass_baseline
    return delta / mean_overhead_s if mean_overhead_s > 0 else float('nan')
```

- Compute per category across all 538 problems
- Also compute per-problem ratios for bootstrap CI

### FR-6: Statistical Tests
- **Primary (P1):** Bootstrap CI (BCa method, 10,000 resamples, scipy.stats.bootstrap) for ratio(execution) − ratio(next-best), test CI excludes 0
- **Secondary:** Kruskal-Wallis test on per-problem overhead distributions across 4 categories (p<0.05), followed by pairwise Mann-Whitney U for ordering confirmation

### FR-7: Experiment Runner
- Loop: for each problem × each category → run `TimedFeedbackEvaluator.run_repair_loop()`
- Save per-problem results: `{task_id, category, passed, total_overhead_s, per_iter_times, final_pass}`
- Checkpoint intermediate results to JSON (resume capability)
- Total: 2,152 repair loop runs

### FR-8: Ablation Variants (All 4 Categories Must Run)
- Execution monitoring (baseline verifier category)
- Static analysis (Pyright static checks)
- Type checking (Pyright type annotations)
- SMT solving (Z3 constraint-based verification)

### FR-9: Visualization
Generate all figures to `docs/youra_research/h-m4/figures/`:

| Figure | Type | Description |
|---|---|---|
| fig_efficiency_ratios.png | Bar chart | Efficiency ratios per category with bootstrap 95% CI error bars (MANDATORY gate metric) |
| fig_overhead_boxplots.png | Box plot | Per-problem wall-clock overhead by category (log scale) |
| fig_overhead_violins.png | Violin plot | Overhead distributions across 4 categories |
| fig_efficiency_scatter.png | Scatter | Δpass@1 (y) vs. mean overhead (x) per category |
| fig_overhead_heatmap.png | Heatmap | 538 problems × 4 categories, log-scale overhead |

### FR-10: Results Logging
- Print: `[H-M4] Category={cat} problem={task_id} overhead={elapsed:.3f}s pass={passed}`
- Save final results to `docs/youra_research/h-m4/results.json`
- Save summary statistics to `docs/youra_research/h-m4/summary.json`

## 6. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed=1 for any stochastic elements
- All GPT-4o-mini repair calls at temperature=0.0 (deterministic)
- Initial generation at temperature=0.2 (if re-running baseline)

### NFR-2: Timing Accuracy
- Use `time.perf_counter()` (monotonic, sub-microsecond resolution)
- Measure wall-clock at the outermost point (include subprocess spawn overhead for execution monitoring)
- SMT: measure both LLM constraint-generation call AND Z3 solve time as total SMT overhead

### NFR-3: Cost Management
- 538 problems × 4 categories × up to 3 repair iterations × 2 calls (verify + repair) ≈ max ~12,912 API calls
- Checkpoint after each problem to enable resume (avoid re-running on API failure)
- Expected cost: ~$5-15 USD at GPT-4o-mini rates

### NFR-4: Runtime Estimate
- Execution monitoring: 538 × ~300ms avg = ~2.7 min
- Static/type: 538 × ~25ms = ~0.2 min each
- SMT: 538 × ~2s avg (with timeouts) = ~18 min
- Total experiment runtime: ~25-30 min (sequential); ~10 min (parallelized per category)

## 7. Dependencies

### 7.1 Python Packages
```
openai>=1.0.0
datasets>=2.14.0
numpy>=1.24.0
scipy>=1.11.0
z3-solver>=4.12.0
matplotlib>=3.7.0
seaborn>=0.12.0
tqdm>=4.65.0
```

### 7.2 External Tools
- `pyright` (Node.js-based): install via `npm install -g pyright` or `pip install pyright`
- OpenAI API key: `OPENAI_API_KEY` environment variable

### 7.3 External Repositories (Reference)
- openai/human-eval: execution harness pattern (`check_correctness` with subprocess + timeout)
- evalplus/evalplus: MBPP evaluation harness reference

### 7.4 Inherited from Prior Hypotheses
- Verifier implementations from H-E1/H-M1/H-M2 (reuse if available in `code/` folders)
- Baseline pass@1 results from H-E1 (avoid re-running generation if possible)
- Problem set: same 538 problems used in H-M1/H-M2/H-M3

## 8. Success Criteria

### Primary Success Criterion (Gate P1)
- `efficiency_ratio[execution_monitoring]` > all other categories
- `ratio(execution) ≥ 1.5 × ratio(next-best)`, bootstrap CI (BCa, 10k resamples, 95%) excludes 0

### Secondary Success Criterion
- Mean overhead ordering confirmed: `mean_overhead[execution] < mean_overhead[static] ≈ mean_overhead[type] < mean_overhead[smt]`
- Kruskal-Wallis p<0.05 across 4 overhead distributions
- Pairwise Mann-Whitney U confirms ordering

### Failure Response
- IF SMT achieves highest efficiency ratio: PIVOT — reframe as "SMT efficient for logic-error-rich distributions"
- IF all ratios within 1.5×: SCOPE — report efficiency rankings without strong ordering claim; focus on overhead profiling

## 9. Sanity Checks

```python
# Post-data-collection sanity checks
assert mean_overhead['execution'] > 0.05, "Execution overhead implausibly low"
assert mean_overhead['smt'] > mean_overhead['execution'], "SMT should be slowest"
assert all(r > 0 for r in ratios.values()), "All Δpass@1 should be positive"
print(f"Overhead ordering: {sorted(mean_overhead.items(), key=lambda x: x[1])}")
print(f"Efficiency ratios: {ratios}")
```
