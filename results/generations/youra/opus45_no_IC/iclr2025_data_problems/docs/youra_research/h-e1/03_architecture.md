# Architecture: H-E1 (EXISTENCE)

**Applied**: No matching KB pattern found (searched "DL experiment architecture pipeline"); used standard analysis-pipeline structure.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. Correlation-analysis experiment (no model architecture), so Serena inspection not applicable.

---

## Overview

Analysis pipeline (not model training): evaluate 72 Pythia checkpoints with lm-eval-harness, compute 13-gram contamination overlap, detrend by capability (WikiText perplexity), correlate contamination vs. inflation residual via Spearman.

## File Structure

- `code/config.py` — fixed experiment config (models, steps, tasks)
- `code/evaluate.py` — run lm-eval-harness across checkpoints, cache results
- `code/contamination.py` — 13-gram overlap computation
- `code/analysis.py` — capability detrending + Spearman correlation
- `code/visualize.py` — required + additional figures
- `code/run.py` — orchestrates full pipeline end-to-end
- `figures/` — output plots

---

## Modules

### Config (`code/config.py`)

**Dependencies**: none

```python
MODEL_SIZES = ["410m", "1b", "1.4b", "2.8b", "6.9b", "12b"]
CHECKPOINT_STEPS = [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 143000]
TASKS = ["mmlu", "arc_challenge", "hellaswag", "winogrande"]
WIKITEXT_TASK = "wikitext"
SEED = 1
```

### Evaluator (`code/evaluate.py`)

**Dependencies**: Config, lm_eval

```python
def evaluate_checkpoint(size: str, step: int, tasks: list[str]) -> dict: ...
def run_all_evaluations(model_sizes: list[str], steps: list[int]) -> list[dict]:
    """Returns list of {size, step, task, score, wikitext_ppl}. Caches to results/eval_cache.json"""
```

### Contamination (`code/contamination.py`)

**Dependencies**: Config, lm_eval.decontamination

```python
def compute_ngram_overlap(task: str, n: int = 13) -> float:
    """Returns contamination % using lm-eval-harness decontamination module against Pile 13-gram index."""

def contamination_by_task(tasks: list[str]) -> dict[str, float]: ...
```

### Analysis (`code/analysis.py`)

**Dependencies**: Evaluator output, Contamination output, scipy, numpy

```python
def fit_capability_regression(wikitext_ppl: np.ndarray, scores: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Returns (coeffs, expected_scores) from score ~ log(1/ppl)."""

def compute_inflation_residuals(scores: np.ndarray, expected_scores: np.ndarray) -> np.ndarray: ...

def compute_correlation(contamination_pct: np.ndarray, inflation_residuals: np.ndarray) -> tuple[float, float]:
    """Returns (spearman_r, p_value)."""

def run_full_analysis(checkpoints_data: list[dict]) -> dict:
    """Orchestrates detrend + correlation. Returns {r, p, residuals, per_benchmark: {...}}"""
```

### Visualize (`code/visualize.py`)

**Dependencies**: Analysis output, matplotlib, seaborn

```python
def plot_gate_scatter(contamination: np.ndarray, residuals: np.ndarray, r: float, p: float, out_path: str) -> None: ...
def plot_contamination_by_benchmark(contamination_by_task: dict, out_path: str) -> None: ...
def plot_checkpoint_trajectory(checkpoints_data: list[dict], out_path: str) -> None: ...
def plot_capability_detrending(wikitext_ppl: np.ndarray, scores: np.ndarray, out_path: str) -> None: ...
def plot_residual_distribution(residuals: np.ndarray, out_path: str) -> None: ...
```

### Run (`code/run.py`)

**Dependencies**: all modules above

```python
def main() -> None:
    """1) run_all_evaluations 2) contamination_by_task 3) run_full_analysis 4) generate all figures 5) print r, p, pass/fail vs gate (r>0.2, p<0.05)"""
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config setup | Define model sizes, steps, tasks | 3 | 1+1+1+0 |
| A-2 | Eval pipeline | lm-eval-harness runner over 72 checkpoints w/ caching | 14 | 3+4+3+4 |
| A-3 | Contamination module | 13-gram overlap via decontamination module | 10 | 3+3+3+1 |
| A-4 | Capability detrending | Linear regression score~log(1/ppl), residuals | 7 | 2+1+3+1 |
| A-5 | Correlation analysis | Spearman r/p, per-benchmark + aggregate | 6 | 2+2+2+0 |
| A-6 | Visualization | 5 required/additional figures | 8 | 3+2+1+2 |
| A-7 | Orchestration | run.py end-to-end + gate check output | 6 | 2+3+1+0 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-2], Medium(9-13): [A-3, A-6], Low(4-8): [A-1, A-4, A-5, A-7]
