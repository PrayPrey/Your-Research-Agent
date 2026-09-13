# Logic: H-E1 (EXISTENCE)

**Applied**: No matching KB pattern found (searched "lm-eval-harness decontamination ngram overlap"); used standard scipy/lm-eval-harness patterns.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## Data Structures

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class CheckpointResult:
    size: str            # e.g. "410m"
    step: int            # checkpoint step
    task: str            # benchmark name
    score: float         # primary metric (accuracy)
    wikitext_ppl: float  # perplexity at this checkpoint

@dataclass
class CorrelationResult:
    r: float
    p_value: float
    n: int
    per_benchmark: dict[str, "CorrelationResult"] = field(default_factory=dict)
```

---

## A-2: Eval Pipeline [Complexity: 14, Budget: 5 subtasks]

**Applied**: Standard lm-eval-harness `simple_evaluate` API + JSON disk cache.

### API Signatures

```python
def evaluate_checkpoint(
    size: str,
    step: int,
    tasks: list[str],
    seed: int = 1,
) -> list[CheckpointResult]:
    """Runs lm-eval-harness on one Pythia checkpoint (revision=f"step{step}").
    Returns one CheckpointResult per task, plus wikitext_ppl attached to each.
    """
    ...

def load_cache(cache_path: str) -> dict[str, dict]: ...
def save_cache(cache_path: str, cache: dict[str, dict]) -> None: ...

def run_all_evaluations(
    model_sizes: list[str],
    steps: list[int],
    tasks: list[str],
    wikitext_task: str,
    cache_path: str = "results/eval_cache.json",
) -> list[CheckpointResult]:
    """Iterates size x step x task (72 x 4 = 288 runs), skips cached keys,
    writes cache incrementally after each checkpoint. Returns full list.
    """
    ...
```

### Pseudo-code (caching + resilience)

```
for size in model_sizes:
    for step in steps:
        key = f"{size}_{step}"
        if key in cache: continue
        try:
            model = HFLM(pretrained=f"EleutherAI/pythia-{size}", revision=f"step{step}")
            task_results = lm_eval.simple_evaluate(model, tasks=tasks+[wikitext_task], seed=seed)
            ppl = task_results[wikitext_task]["word_perplexity"]
            for task in tasks:
                score = task_results[task]["acc"]
                results.append(CheckpointResult(size, step, task, score, ppl))
        except Exception as e:
            log.error(f"eval failed {key}: {e}")   # skip checkpoint, continue loop
            continue
        cache[key] = [asdict(r) for r in results if r.size==size and r.step==step]
        save_cache(cache_path, cache)   # incremental, survives crash mid-run
return results
```

### Tensor Shapes

Not applicable (no tensors; scalar metrics per checkpoint x task).

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-A2-1 | HFLM loader | Load Pythia checkpoint by revision string |
| L-A2-2 | Task runner | Call `simple_evaluate` for tasks + wikitext, extract acc/ppl |
| L-A2-3 | Cache I/O | JSON load/save, key by `{size}_{step}` |
| L-A2-4 | Resilience loop | Try/except per checkpoint, log + continue on failure |
| L-A2-5 | Result assembly | Build `list[CheckpointResult]`, flatten cache dict back to dataclasses |

---

## A-3: Contamination Module [Complexity: 10, Budget: 5 subtasks]

**Applied**: lm-eval-harness `decontamination` n-gram overlap against precomputed Pile index.

### API Signatures

```python
def load_ngram_index(index_path: str, n: int = 13) -> "NGramIndex": ...

def compute_ngram_overlap(
    task: str,
    index: "NGramIndex",
    n: int = 13,
) -> float:
    """Returns contamination % (0-100): fraction of task's n-grams found in Pile index."""
    ...

def contamination_by_task(
    tasks: list[str],
    index_path: str,
    n: int = 13,
) -> dict[str, float]:
    """Loads index once, computes overlap % per task."""
    ...
```

### Pseudo-code

```
index = load_ngram_index(index_path, n)   # precomputed Pile 13-gram set/bloom filter
for task in tasks:
    dataset = load_task_test_set(task)     # benchmark test examples (text)
    total_ngrams = 0
    contaminated = 0
    for example in dataset:
        grams = ngrams(tokenize(example.text), n)
        total_ngrams += len(grams)
        contaminated += sum(1 for g in grams if g in index)
    contamination_pct[task] = 100 * contaminated / max(total_ngrams, 1)
return contamination_pct
```

### Error Handling

- Missing index file -> raise `FileNotFoundError` with clear message (fail fast, no silent fallback).
- Empty task dataset -> return 0.0 with warning log (avoid div-by-zero).

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-A3-1 | Index loader | Load precomputed Pile 13-gram index (set/bloom filter) |
| L-A3-2 | N-gram extraction | Tokenize + sliding-window n-grams per example |
| L-A3-3 | Overlap counter | Count matched vs. total n-grams per task |
| L-A3-4 | Task iteration | Aggregate `contamination_by_task` dict across all 4 benchmarks |
| L-A3-5 | Error handling | FileNotFoundError on missing index, zero-division guard |

---

## A-4: Capability Detrending [Complexity: 7]

**Applied**: Standard scipy/numpy linear regression (`np.polyfit`).

### API Signatures

```python
import numpy as np

def fit_capability_regression(
    wikitext_ppl: np.ndarray,   # [N]
    scores: np.ndarray,         # [N]
) -> tuple[np.ndarray, np.ndarray]:
    """Fits scores ~ log(1/ppl) via least squares. Returns (coeffs[2], expected_scores[N])."""
    x = np.log(1.0 / wikitext_ppl)      # [N]
    coeffs = np.polyfit(x, scores, deg=1)   # [slope, intercept]
    expected_scores = np.polyval(coeffs, x)  # [N]
    return coeffs, expected_scores

def compute_inflation_residuals(
    scores: np.ndarray,          # [N]
    expected_scores: np.ndarray, # [N]
) -> np.ndarray:
    """residual = actual - expected. [N]"""
    return scores - expected_scores
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| wikitext_ppl | [N] | N = num checkpoints (up to 72) |
| scores | [N] | benchmark accuracy per checkpoint |
| coeffs | [2] | [slope, intercept] |
| residuals | [N] | inflation residual (actual - expected) |

---

## A-5: Correlation Analysis [Complexity: 6]

**Applied**: scipy.stats.spearmanr.

### API Signatures

```python
from scipy.stats import spearmanr

def compute_correlation(
    contamination_pct: np.ndarray,   # [N]
    inflation_residuals: np.ndarray, # [N]
) -> tuple[float, float]:
    """Returns (spearman_r, p_value)."""
    r, p = spearmanr(contamination_pct, inflation_residuals)
    return float(r), float(p)

def run_full_analysis(
    checkpoints_data: list[CheckpointResult],
    contamination_by_task_pct: dict[str, float],
) -> CorrelationResult:
    """Per-benchmark: detrend + correlate. Aggregate: pool all (task, checkpoint) pairs."""
    ...
```

### Pseudo-code

```
per_benchmark = {}
for task in tasks:
    rows = [c for c in checkpoints_data if c.task == task]
    ppl = np.array([r.wikitext_ppl for r in rows])
    scores = np.array([r.score for r in rows])
    _, expected = fit_capability_regression(ppl, scores)
    residuals = compute_inflation_residuals(scores, expected)
    contam = np.full(len(rows), contamination_by_task_pct[task])
    r_val, p_val = compute_correlation(contam, residuals)
    per_benchmark[task] = CorrelationResult(r_val, p_val, n=len(rows))

# aggregate: pool all tasks' (contamination, residual) pairs
all_contam = concat of per-task contam arrays
all_resid  = concat of per-task residuals
agg_r, agg_p = compute_correlation(all_contam, all_resid)
return CorrelationResult(agg_r, agg_p, n=len(all_contam), per_benchmark=per_benchmark)
```

---

## A-6: Visualization [Complexity: 8]

**Applied**: matplotlib + seaborn, standard scatter/bar/line plots.

### API Signatures

```python
def plot_gate_scatter(contamination: np.ndarray, residuals: np.ndarray, r: float, p: float, out_path: str) -> None: ...
def plot_contamination_by_benchmark(contamination_by_task: dict[str, float], out_path: str) -> None: ...
def plot_checkpoint_trajectory(checkpoints_data: list[CheckpointResult], out_path: str) -> None: ...
def plot_capability_detrending(wikitext_ppl: np.ndarray, scores: np.ndarray, out_path: str) -> None: ...
def plot_residual_distribution(residuals: np.ndarray, out_path: str) -> None: ...
```

No non-trivial algorithm; direct matplotlib calls (scatter + `np.polyfit` line overlay, seaborn barplot, line plot grouped by `size`).

---

## A-7: Orchestration [Complexity: 6]

### API Signatures

```python
def main() -> None:
    """
    1. results = run_all_evaluations(MODEL_SIZES, CHECKPOINT_STEPS, TASKS, WIKITEXT_TASK)
    2. contam = contamination_by_task(TASKS, index_path)
    3. analysis = run_full_analysis(results, contam)
    4. generate all 5 figures via visualize.*
    5. print(f"r={analysis.r:.3f} p={analysis.p_value:.4f}")
       gate_pass = analysis.r > 0.2 and analysis.p_value < 0.05
       print("PASS" if gate_pass else "FAIL")
    """
    ...
```

### Error Handling

- Any stage raising an unhandled exception aborts `main()` with non-zero exit (fail fast at orchestration level; per-checkpoint failures already isolated in A-2).
