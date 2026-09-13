# Logic Design: H-M3 — Contamination-Accuracy Correlation Analysis

**Date:** 2026-08-25  
**Author:** yoon303@ust.ac.kr  
**Hypothesis:** H-M3 (MECHANISM — SHOULD_WORK)

Applied: scipy.stats Pearson/Spearman correlation pipeline (Shi et al. 2023)
Applied: bootstrap resampling with fixed seed pattern (standard practice)
Applied: matplotlib scatter-regression annotation pattern (standard visualization)
Applied: model-size aggregation for n=16 statistical power (Biderman et al. 2023)
Applied: rank-based correlation visualization pattern (Spearman rank plot)

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** Green-field analysis experiment; no existing codebase to analyze with Serena. All inputs are JSON result files from H-E1/H-M1/H-M2.  
**Analyzed Path:** N/A  
**Findings:** New implementation from scratch. Prior hypotheses produced only result JSON files; no reusable module code exists.

---

## Constants and Types

```python
from dataclasses import dataclass
from typing import Optional
import numpy as np

BENCHMARKS = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]
MODEL_SIZES = ["160m", "410m", "1b", "6.9b"]

@dataclass
class CorrelationResult:
    pearson_r: float
    pearson_p: float
    spearman_rho: float
    spearman_p: float
    n_observations: int
    bootstrap_ci_95: Optional[tuple[float, float]] = None
```

---

## Module: correlation.py (A-2)

### Subtask L-2-1: pearson_spearman

```python
def pearson_spearman(
    cont_vec: np.ndarray,   # shape: (N,) contamination values
    diff_vec: np.ndarray,   # shape: (N,) accuracy differential values
) -> CorrelationResult:
    """Compute Pearson and Spearman correlations on paired vectors."""
```

**Array shapes:**
- Input: `cont_vec` (16,), `diff_vec` (16,) — primary use case
- Also accepts (4,) for per-model-size ablation

**Pseudo-code:**
```
assert len(cont_vec) == len(diff_vec), "Vector length mismatch"
assert not np.any(np.isnan(cont_vec) | np.isnan(diff_vec)), "NaN in inputs"
pearson_r, pearson_p = scipy.stats.pearsonr(cont_vec, diff_vec)
spearman_rho, spearman_p = scipy.stats.spearmanr(cont_vec, diff_vec)
return CorrelationResult(pearson_r, pearson_p, spearman_rho, spearman_p, n=len(cont_vec))
```

**Design notes:** No assumptions about normality for Pearson (n=16 is borderline; Spearman provides nonparametric backup). Both stats always computed together.

---

### Subtask L-2-2: bootstrap_ci

```python
def bootstrap_ci(
    cont_vec: np.ndarray,    # shape: (N,)
    diff_vec: np.ndarray,    # shape: (N,)
    n_resamples: int = 1000,
    seed: int = 42,
) -> tuple[float, float]:
    """Bootstrap 95% CI on Pearson r via resampling with replacement."""
```

**Array shapes:**
- Input: (16,) and (16,)
- Intermediate: `boot_r` list of 1000 floats
- Output: (ci_lower, ci_upper) tuple

**Pseudo-code:**
```
rng = np.random.default_rng(seed)
n = len(cont_vec)
boot_r = []
for _ in range(n_resamples):
    idx = rng.integers(0, n, size=n)
    r, _ = scipy.stats.pearsonr(cont_vec[idx], diff_vec[idx])
    boot_r.append(r)
boot_r = np.array(boot_r)
ci_lower = np.percentile(boot_r, 2.5)
ci_upper = np.percentile(boot_r, 97.5)
return (ci_lower, ci_upper), boot_r  # return distribution for plotting
```

**Design notes:** Return full `boot_r` array alongside CI so visualize.py can plot histogram without re-running bootstrap.

---

### Subtask L-2-3: directional_check

```python
def directional_check(
    cont_vec: np.ndarray,    # shape: (4,) — one value per benchmark
    diff_matrix: np.ndarray, # shape: (4, 4) — (model_sizes, benchmarks)
) -> dict:
    """Check whether high-contamination benchmarks show negative (or smaller) accuracy differential."""
```

**Array shapes:**
- `cont_vec`: (4,) indexed by BENCHMARKS order
- `diff_matrix`: (4 model_sizes, 4 benchmarks)
- Output dict keys: `n_correct_direction`, `benchmark_signs`, `contamination_rank`, `differential_mean_rank`

**Pseudo-code:**
```
mean_diff_per_benchmark = diff_matrix.mean(axis=0)  # (4,)
# High contamination → dedup model worse → negative differential (dedup - pile)
# So predicted sign of differential: negative if contamination high
cont_rank = scipy.stats.rankdata(cont_vec)          # higher rank = more contaminated
diff_rank = scipy.stats.rankdata(mean_diff_per_benchmark)  # higher rank = more positive diff
# Predicted: cont_rank and diff_rank should be NEGATIVELY correlated
n_correct = sum(
    (cont_vec[i] > cont_vec[j]) == (mean_diff_per_benchmark[i] < mean_diff_per_benchmark[j])
    for i in range(4) for j in range(i+1, 4)
) / 6  # fraction of pairs with correct ordering
benchmark_signs = {b: float(mean_diff_per_benchmark[i]) for i, b in enumerate(BENCHMARKS)}
return {"n_correct_direction": n_correct, "benchmark_signs": benchmark_signs,
        "contamination_rank": cont_rank.tolist(), "differential_mean_rank": diff_rank.tolist()}
```

---

## Module: ablations.py (A-3)

### Subtask L-3-1: ablation_estimator_comparison

```python
def ablation_estimator_comparison(
    acc_diff: dict[str, dict[str, float]],   # {model: {bench: float}}
    cont_13gram: dict[str, float],            # {bench: float} from H-M1
    mink_diff: Optional[dict[str, float]],   # {bench: float} from H-M2, may be None
) -> dict:
    """Compare 13-gram overlap vs min-k% as contamination predictor."""
```

**Pseudo-code:**
```
cont_vec, diff_flat = build_analysis_vectors(acc_diff, cont_13gram)
result_13gram = pearson_spearman(cont_vec, diff_flat)

if mink_diff is None:
    return {"13gram": result_13gram, "mink": None, "note": "H-M2 results unavailable"}

mink_vec = np.array([mink_diff[b] for b in BENCHMARKS])
mink_repeated = np.tile(mink_vec, len(MODEL_SIZES))
result_mink = pearson_spearman(mink_repeated, diff_flat)

disagreement = abs(result_13gram.pearson_r - result_mink.pearson_r) > 0.3
return {
    "13gram": result_13gram, "mink": result_mink,
    "r_difference": abs(result_13gram.pearson_r - result_mink.pearson_r),
    "estimators_disagree": disagreement
}
```

---

### Subtask L-3-2: ablation_aggregation_strategy

```python
def ablation_aggregation_strategy(
    cont_vec: np.ndarray,    # shape: (4,) one value per benchmark
    diff_matrix: np.ndarray, # shape: (4, 4) — (model_sizes, benchmarks)
) -> dict:
    """Compare n=16 flattened aggregation vs n=4 benchmark-level aggregation."""
```

**Pseudo-code:**
```
# Option A: n=16 (primary)
cont_repeated = np.tile(cont_vec, len(MODEL_SIZES))  # (16,)
diff_flat = diff_matrix.flatten()                     # (16,)
result_n16 = pearson_spearman(cont_repeated, diff_flat)

# Option B: n=4 (benchmark-level mean)
diff_mean = diff_matrix.mean(axis=0)  # (4,)
result_n4 = pearson_spearman(cont_vec, diff_mean)

return {
    "n16": result_n16,
    "n4": result_n4,
    "note": "n=4 requires r>=0.95 for p<0.05; n=16 is primary"
}
```

---

### Subtask L-3-3: ablation_token_vs_step

```python
def ablation_token_vs_step(
    acc_diff_token: dict[str, dict[str, float]],  # token-count matched (primary)
    acc_diff_step: Optional[dict[str, dict[str, float]]],  # step matched (may be None)
    cont_vec: np.ndarray,  # shape: (4,)
) -> dict:
    """Compare correlation under token-count vs step-count checkpoint matching."""
```

**Pseudo-code:**
```
cont_repeated = np.tile(cont_vec, len(MODEL_SIZES))
_, diff_flat_token = build_analysis_vectors(acc_diff_token, dict(zip(BENCHMARKS, cont_vec)))
result_token = pearson_spearman(cont_repeated, diff_flat_token)

if acc_diff_step is None:
    return {"token": result_token, "step": None, "note": "Step-matched results not available from H-E1"}

_, diff_flat_step = build_analysis_vectors(acc_diff_step, dict(zip(BENCHMARKS, cont_vec)))
result_step = pearson_spearman(cont_repeated, diff_flat_step)
return {"token": result_token, "step": result_step}
```

---

### Subtask L-3-4: ablation_per_model_size

```python
def ablation_per_model_size(
    acc_diff: dict[str, dict[str, float]],  # {model: {bench: float}}
    cont_vec: np.ndarray,                   # shape: (4,)
) -> dict[str, CorrelationResult]:
    """Run Pearson separately for each model size (n=4 per size)."""
```

**Pseudo-code:**
```
results = {}
for model_size in MODEL_SIZES:
    diff_vec = np.array([acc_diff[model_size][b] for b in BENCHMARKS])  # (4,)
    result = pearson_spearman(cont_vec, diff_vec)
    results[model_size] = result
# Expected: larger models show stronger correlation (6.9b > 1b > 410m > 160m)
return results
```

---

## Module: visualize.py (A-4)

### Subtask L-4-1: plot_scatter

```python
def plot_scatter(
    cont_vec: np.ndarray,    # shape: (4,) one value per benchmark
    diff_mean_vec: np.ndarray, # shape: (4,) mean differential per benchmark
    pearson_r: float,
    pearson_p: float,
    benchmark_labels: list[str],  # BENCHMARKS
    save_path: str,
) -> None:
    """Scatter plot: contamination estimate vs mean accuracy differential with regression line."""
```

**Pseudo-code:**
```
fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(cont_vec, diff_mean_vec, s=100, zorder=3)
for i, label in enumerate(benchmark_labels):
    ax.annotate(label, (cont_vec[i], diff_mean_vec[i]), textcoords="offset points", xytext=(5,5))
# Regression line
m, b = np.polyfit(cont_vec, diff_mean_vec, 1)
x_line = np.linspace(cont_vec.min(), cont_vec.max(), 100)
ax.plot(x_line, m*x_line + b, 'r--', alpha=0.7)
ax.set_xlabel("13-gram Contamination Overlap Rate")
ax.set_ylabel("Mean Accuracy Differential (dedup-Pile − Pile)")
ax.set_title(f"Contamination vs Accuracy Differential\nPearson r={pearson_r:.3f}, p={pearson_p:.4f}")
ax.axhline(0, color='gray', linestyle=':', alpha=0.5)
plt.tight_layout()
plt.savefig(save_path, dpi=150, bbox_inches='tight')
plt.close()
```

---

### Subtask L-4-2: plot_correlation_heatmap

```python
def plot_correlation_heatmap(
    r_matrix: np.ndarray,        # shape: (2, 4) — [estimator, model_size]
    estimator_labels: list[str], # ["13-gram", "min-k%"]
    model_size_labels: list[str], # MODEL_SIZES
    save_path: str,
) -> None:
    """Heatmap of Pearson r values by estimator × model size."""
```

**Array shapes:** `r_matrix` (2 estimators, 4 model sizes)

**Pseudo-code:**
```
fig, ax = plt.subplots(figsize=(8, 3))
im = ax.imshow(r_matrix, vmin=-1, vmax=1, cmap='RdYlGn', aspect='auto')
plt.colorbar(im, ax=ax, label='Pearson r')
ax.set_xticks(range(len(model_size_labels))); ax.set_xticklabels(model_size_labels)
ax.set_yticks(range(len(estimator_labels))); ax.set_yticklabels(estimator_labels)
for i in range(2):
    for j in range(4):
        ax.text(j, i, f"{r_matrix[i,j]:.3f}", ha='center', va='center', fontsize=10)
ax.set_title("Pearson r by Estimator × Model Size")
plt.tight_layout()
plt.savefig(save_path, dpi=150, bbox_inches='tight')
plt.close()
```

---

### Subtask L-4-3: plot_per_benchmark_bars

```python
def plot_per_benchmark_bars(
    diff_matrix: np.ndarray,   # shape: (4, 4) — (model_sizes, benchmarks)
    cont_levels: np.ndarray,   # shape: (4,) — contamination per benchmark (for color)
    benchmark_labels: list[str],
    model_size_labels: list[str],
    save_path: str,
) -> None:
    """Grouped bar chart: 4 benchmarks × 4 model sizes, colored by contamination level."""
```

**Array shapes:** `diff_matrix` (4 model_sizes, 4 benchmarks)

**Pseudo-code:**
```
x = np.arange(len(benchmark_labels))
width = 0.2
colors = plt.cm.Reds(cont_levels / cont_levels.max())  # color by contamination
fig, ax = plt.subplots(figsize=(10, 5))
for i, (model, color) in enumerate(zip(model_size_labels, ['#1f77b4','#ff7f0e','#2ca02c','#d62728'])):
    bars = ax.bar(x + i*width, diff_matrix[i], width, label=model, alpha=0.8, color=color)
ax.set_xticks(x + width*1.5); ax.set_xticklabels(benchmark_labels)
ax.set_xlabel("Benchmark"); ax.set_ylabel("Accuracy Differential (dedup − pile)")
ax.set_title("Per-Benchmark Accuracy Differential by Model Size\n(colored annotations = contamination level)")
ax.axhline(0, color='black', linewidth=0.8)
ax.legend(); plt.tight_layout()
plt.savefig(save_path, dpi=150, bbox_inches='tight')
plt.close()
```

---

### Subtask L-4-4: plot_bootstrap_ci + plot_spearman_ranks

```python
def plot_bootstrap_ci(
    boot_r_dist: np.ndarray,  # shape: (1000,) bootstrap Pearson r values
    ci_lower: float,
    ci_upper: float,
    observed_r: float,
    save_path: str,
) -> None:
    """Histogram of bootstrap Pearson r distribution with 95% CI marked."""
```

**Pseudo-code:**
```
fig, ax = plt.subplots(figsize=(7, 4))
ax.hist(boot_r_dist, bins=40, color='steelblue', alpha=0.7, edgecolor='white')
ax.axvline(observed_r, color='red', lw=2, label=f"Observed r={observed_r:.3f}")
ax.axvline(ci_lower, color='orange', lw=1.5, linestyle='--', label=f"95% CI [{ci_lower:.3f}, {ci_upper:.3f}]")
ax.axvline(ci_upper, color='orange', lw=1.5, linestyle='--')
ax.set_xlabel("Bootstrap Pearson r"); ax.set_ylabel("Count")
ax.set_title("Bootstrap Distribution of Pearson r (n=1000 resamples)")
ax.legend(); plt.tight_layout()
plt.savefig(save_path, dpi=150, bbox_inches='tight')
plt.close()

def plot_spearman_ranks(
    cont_vec: np.ndarray,      # shape: (4,) contamination values
    diff_mean_vec: np.ndarray, # shape: (4,) mean differential per benchmark
    benchmark_labels: list[str],
    save_path: str,
) -> None:
    """Rank plot: contamination rank vs differential rank for 4 benchmarks."""
    cont_ranks = scipy.stats.rankdata(cont_vec)
    diff_ranks = scipy.stats.rankdata(diff_mean_vec)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(cont_ranks, diff_ranks, s=120, zorder=3)
    for i, label in enumerate(benchmark_labels):
        ax.annotate(label, (cont_ranks[i], diff_ranks[i]), textcoords="offset points", xytext=(5,5))
    ax.set_xlabel("Contamination Rank"); ax.set_ylabel("Differential Rank")
    ax.set_title("Spearman Rank Visualization (n=4 benchmarks)")
    ax.set_xticks([1,2,3,4]); ax.set_yticks([1,2,3,4])
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
```

---

## Tensor Shape Summary

| Variable | Shape | Description |
|----------|-------|-------------|
| `cont_vec` | (4,) | Contamination estimate per benchmark |
| `diff_matrix` | (4, 4) | Accuracy differential (model_sizes × benchmarks) |
| `cont_repeated` | (16,) | Tiled contamination for n=16 analysis |
| `diff_flat` | (16,) | Flattened differential for n=16 analysis |
| `boot_r_dist` | (1000,) | Bootstrap Pearson r distribution |
| `r_matrix` | (2, 4) | Pearson r heatmap (estimators × model_sizes) |

---

## Error Handling Contracts

| Function | Input Guard | On Failure |
|----------|-------------|------------|
| `pearson_spearman` | assert no NaN, equal lengths | raise ValueError |
| `bootstrap_ci` | same as above | raise ValueError |
| `ablation_estimator_comparison` | mink_diff may be None | graceful skip |
| `ablation_token_vs_step` | acc_diff_step may be None | graceful skip |
| `plot_*` | create figure dir if missing | os.makedirs(exist_ok=True) |
