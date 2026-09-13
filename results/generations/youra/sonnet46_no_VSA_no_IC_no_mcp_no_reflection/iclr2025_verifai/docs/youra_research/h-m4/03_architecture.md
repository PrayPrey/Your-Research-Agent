---
title: "Architecture: H-M4 — Feedback Overhead Efficiency Ratio Measurement"
hypothesis_id: H-M4
phase: 3
date: 2026-08-31
author: yoon303@etri.re.kr
---

# Architecture: H-M4

Applied: timed-verifier-wrapper pattern (perf_counter + subprocess harness)
Applied: bootstrap-BCa efficiency ratio comparison pattern

## Codebase Analysis (Serena)

**Project Type**: green-field (H-M4 specific code folder)
**Status**: No prior H-M3/H-M4 code/ folder exists — ablation mode; green-field implementation
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; verifier patterns derived from experiment briefs

---

## File Organization

- `code/data_loader.py` — unified 538-problem dataset
- `code/verifiers.py` — 4 verifier implementations (execution, static, type, SMT)
- `code/evaluator.py` — TimedFeedbackEvaluator + efficiency ratio computation
- `code/stats.py` — bootstrap BCa, Kruskal-Wallis, Mann-Whitney
- `code/runner.py` — experiment loop with checkpoint/resume
- `code/visualize.py` — 5 required figures
- `code/config.py` — fixed experiment config
- `code/run_experiment.py` — entry point

---

## Modules

### DataLoader (`code/data_loader.py`)

**Dependencies**: datasets (HuggingFace)

```python
def load_humaneval() -> list[dict]: ...
# Returns list of {task_id, prompt, tests, source='humaneval'}

def load_mbpp() -> list[dict]: ...
# Returns list of {task_id, prompt, tests, source='mbpp'}

def load_combined() -> list[dict]: ...
# Returns merged list of 538 problems with unified schema
# MBPP: converts test_list to assertion strings, prepends test_setup_code

def load_baseline_pass(path: str | None = None) -> dict[str, bool]: ...
# Loads H-E1 baseline pass@1 per task_id; re-runs vanilla generation if unavailable
```

---

### Verifiers (`code/verifiers.py`)

**Dependencies**: subprocess, z3, openai, tempfile

```python
def run_execution_verifier(code: str, problem: dict, timeout: float = 10.0) -> tuple[str, bool]: ...
# subprocess execution of code + test assertions; returns (feedback, passed)

def run_static_verifier(code: str, problem: dict) -> tuple[str, bool]: ...
# subprocess.run(['pyright', '--outputjson', tmpfile]); returns (feedback, passed)

def run_type_verifier(code: str, problem: dict) -> tuple[str, bool]: ...
# Same as static (Pyright covers both); returns (feedback, passed)

def run_smt_verifier(code: str, problem: dict, llm_client, timeout: float = 30.0) -> tuple[str, bool]: ...
# LLM constraint generation call + Z3 solve; returns (feedback, passed)
# timeout: 30s hard limit; timeout counts as full overhead + no pass

VERIFIERS: dict[str, callable] = {
    'execution': run_execution_verifier,
    'static': run_static_verifier,
    'type': run_type_verifier,
    'smt': run_smt_verifier,
}
```

---

### TimedFeedbackEvaluator (`code/evaluator.py`)

**Dependencies**: verifiers.py, openai, time

```python
class TimedFeedbackEvaluator:
    def __init__(self, category: str, verifier_fn: callable, llm_client): ...
    # category: 'execution' | 'static' | 'type' | 'smt'

    def run_repair_loop(
        self, problem: dict, initial_code: str, max_iters: int = 3
    ) -> tuple[bool, float, list[float]]: ...
    # Returns (final_pass, total_overhead_s, per_iter_times)
    # Measures: verifier call + LLM repair call per iteration via time.perf_counter()
    # Excludes initial generation time (category-independent)

    def _repair(self, code: str, feedback: str, problem: dict) -> str: ...
    # GPT-4o-mini repair call at temperature=0.0

def compute_efficiency_ratio(
    pass_after: float, pass_baseline: float, mean_overhead_s: float
) -> float: ...
# Δpass@1 / mean overhead seconds; nan if mean_overhead_s <= 0
```

---

### Stats (`code/stats.py`)

**Dependencies**: numpy, scipy.stats

```python
def bootstrap_ratio_comparison(
    ratios_a: np.ndarray, ratios_b: np.ndarray, n_resamples: int = 10000
) -> dict: ...
# BCa bootstrap CI for mean(a) - mean(b); returns {ci_low, ci_high, p_approx}
# p_approx: <0.05 if CI excludes 0

def kruskal_wallis_overhead(overhead_by_cat: dict[str, list[float]]) -> dict: ...
# Returns {statistic, p_value} across 4 categories

def mannwhitney_pairwise(overhead_by_cat: dict[str, list[float]]) -> dict[tuple, dict]: ...
# Pairwise Mann-Whitney U for all category pairs; returns {(cat_a, cat_b): {statistic, p_value}}

def summarize_overhead(overhead_by_cat: dict[str, list[float]]) -> dict[str, dict]: ...
# Per-category: {mean, median, std, min, max, p95}
```

---

### Runner (`code/runner.py`)

**Dependencies**: evaluator.py, verifiers.py, data_loader.py, config.py, openai, json, tqdm

```python
def run_experiment(
    problems: list[dict],
    categories: list[str],
    checkpoint_path: str,
    baseline_pass: dict[str, bool],
) -> list[dict]: ...
# 538 × 4 = 2,152 repair loop runs
# Per-result schema: {task_id, category, passed, total_overhead_s, per_iter_times, final_pass}
# Checkpoints to JSON after each problem; resumes from checkpoint if exists
# Logs: [H-M4] Category={cat} problem={task_id} overhead={elapsed:.3f}s pass={passed}

def load_checkpoint(path: str) -> list[dict]: ...
def save_checkpoint(results: list[dict], path: str) -> None: ...
```

---

### Visualize (`code/visualize.py`)

**Dependencies**: matplotlib, seaborn, numpy, stats.py

```python
def plot_efficiency_ratios(
    ratios: dict[str, float], ci_bounds: dict[str, tuple], output_dir: str
) -> None: ...
# fig_efficiency_ratios.png — bar chart with bootstrap 95% CI error bars (MANDATORY gate metric)

def plot_overhead_boxplots(overhead_by_cat: dict[str, list[float]], output_dir: str) -> None: ...
# fig_overhead_boxplots.png — log-scale box plots

def plot_overhead_violins(overhead_by_cat: dict[str, list[float]], output_dir: str) -> None: ...
# fig_overhead_violins.png — violin plots across 4 categories

def plot_efficiency_scatter(
    delta_pass: dict[str, float], mean_overhead: dict[str, float], output_dir: str
) -> None: ...
# fig_efficiency_scatter.png — Δpass@1 (y) vs. mean overhead (x) per category

def plot_overhead_heatmap(
    overhead_matrix: np.ndarray, task_ids: list[str], categories: list[str], output_dir: str
) -> None: ...
# fig_overhead_heatmap.png — 538 × 4 heatmap, log-scale overhead

def generate_all_figures(results: list[dict], output_dir: str) -> None: ...
```

---

### Config (`code/config.py`)

```python
CATEGORIES = ['execution', 'static', 'type', 'smt']
MAX_ITERS = 3
SMT_TIMEOUT = 30.0
EXEC_TIMEOUT = 10.0
GENERATION_TEMP = 0.2
REPAIR_TEMP = 0.0
MAX_TOKENS = 1024
N_BOOTSTRAP = 10000
SEED = 1
FIGURES_DIR = "docs/youra_research/h-m4/figures"
RESULTS_PATH = "docs/youra_research/h-m4/results.json"
SUMMARY_PATH = "docs/youra_research/h-m4/summary.json"
CHECKPOINT_PATH = "docs/youra_research/h-m4/checkpoint.json"
```

---

### Entry Point (`code/run_experiment.py`)

**Dependencies**: all modules

```python
def main() -> None: ...
# 1. Load 538 problems
# 2. Load/generate baseline pass@1
# 3. Run experiment with checkpoint/resume
# 4. Compute efficiency ratios + statistical tests
# 5. Save results.json and summary.json
# 6. Generate all 5 figures
# 7. Print sanity checks + gate metric result
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Loading | Implement data_loader.py: HumanEval + MBPP unified 538-problem schema; MBPP test conversion; baseline pass@1 loading/fallback | 9 | 2+2+3+2 |
| A-2 | Execution Verifier | subprocess-based code execution + test assertions with timeout; returns (feedback, passed) | 12 | 3+2+4+3 |
| A-3 | Static/Type Verifiers | Pyright-based static analysis and type checking via subprocess; JSON output parsing | 10 | 2+2+3+3 |
| A-4 | SMT Verifier | LLM constraint generation + Z3 solve with 30s timeout; measure both LLM and Z3 time | 16 | 4+4+5+3 |
| A-5 | TimedFeedbackEvaluator | Core timing wrapper: perf_counter around verifier + repair per iteration; repair loop logic | 14 | 3+3+4+4 |
| A-6 | Config + Entry Point | config.py fixed params; run_experiment.py orchestration entry | 6 | 1+1+2+2 |
| A-7 | Experiment Runner | 2,152 run loop; JSON checkpoint/resume; per-problem logging; tqdm progress | 13 | 3+3+3+4 |
| A-8 | Efficiency Ratio + Stats | compute_efficiency_ratio; bootstrap BCa (scipy); Kruskal-Wallis; pairwise Mann-Whitney | 15 | 3+3+5+4 |
| A-9 | Visualization | 5 required figures (bar, boxplot, violin, scatter, heatmap); log-scale; CI error bars | 12 | 3+2+3+4 |
| A-10 | Results Persistence | results.json (per-problem), summary.json (aggregates + stats); sanity check assertions | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4, A-5, A-8], Medium(9-13): [A-2, A-3, A-7, A-9], Low(4-8): [A-1, A-6, A-10]

---

## Data Flow

- `data_loader.py` → 538 problems list → `runner.py`
- `runner.py` → per problem × category → `evaluator.py` (TimedFeedbackEvaluator)
- `evaluator.py` → calls `verifiers.py` (timed) + OpenAI repair (timed) → `(passed, overhead_s, iter_times)`
- `runner.py` → collects all results → `results.json` (checkpoint)
- `stats.py` → efficiency ratios, bootstrap CI, Kruskal-Wallis, Mann-Whitney → `summary.json`
- `visualize.py` → 5 figures → `docs/youra_research/h-m4/figures/`

## Sanity Check Assertions (post-run)

```python
assert mean_overhead['execution'] > 0.05, "Execution overhead implausibly low"
assert mean_overhead['smt'] > mean_overhead['execution'], "SMT should be slowest"
assert all(r > 0 for r in ratios.values()), "All Δpass@1 should be positive"
```
