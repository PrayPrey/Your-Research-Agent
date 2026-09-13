---
hypothesis_id: h-m1
type: MECHANISM
generated_at: 2026-08-21
author: yoon303@etri.re.kr
---

Applied: standard scipy Mann-Whitney U one-sided test pattern

# Logic: H-M1 — Variance Selection Ranking Signal Validation

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual H-E1 code
**Analyzed Path**: `docs/youra_research/h-e1/code/profile_mbpp.py`
**Relevant Symbols**:
- `save_results(results, top50_ids, gate_result, metrics, path)` — top-level JSON output
- `compute_gate(results, cfg)` → `(gate_passed, metrics, top50_ids)` — gate logic
- `profile_all_problems(model, tokenizer, problems, cfg)` → `dict` — profiling loop
- JSON output key: `"top50_ids"` (not `"top_ids"` — verified from actual code line 220)
- JSON structure: `problems[str(task_id)] = {p_i, variance_i, pass_count, k, rank_by_variance}`

---

## External Dependencies API (Base Hypothesis H-E1)

Signatures verified from actual `docs/youra_research/h-e1/code/profile_mbpp.py`:

```python
# H-E1 JSON output schema (from save_results(), lines 209-226)
# Key: "top50_ids" (NOT "top_ids" — architecture doc had wrong key name!)
# metrics keys: count_nonzero_variance, threshold_count, mean_p_top50, gate_passed, total_problems
# problems[str(task_id)]: {p_i, variance_i, pass_count, k, rank_by_variance}
{
    "gate_passed": bool,
    "metrics": {
        "count_nonzero_variance": int,
        "threshold_count": int,
        "mean_p_top50": float,
        "gate_passed": bool,
        "total_problems": int,
    },
    "top50_ids": [int, ...],       # ← verified: "top50_ids", not "top_ids"
    "problems": {
        "<task_id_str>": {
            "p_i": float,
            "variance_i": float,
            "pass_count": int,
            "k": int,
            "rank_by_variance": int,
        }
    }
}

# Fallback subprocess target (from main(), lines 297-343)
# Call: python docs/youra_research/h-e1/code/profile_mbpp.py
# Returns: sys.exit(0 if gate_passed else 1)
# Output written to: docs/youra_research/h-e1/results/mbpp_variance_profile.json
```

---

## A-4: Core Comparison [Complexity: 9, Budget: 1 subtask]

### API Signatures

```python
def compare_selections(
    variance_i: np.ndarray,   # shape (N,) — p_i*(1-p_i), values in [0, 0.25]
    problem_ids: np.ndarray,  # shape (N,) — task_id ints, sorted ascending
    k: int = 50,
    seed: int = 42,
) -> dict:
    """Run variance-vs-random selection comparison. Returns gate + all metrics."""
    ...
```

### Pseudo-code

```
N = len(variance_i)
ranked_idx = np.argsort(variance_i)[::-1]          # (N,) descending
variance_50_idx = ranked_idx[:k]                   # (k,)
rng = np.random.default_rng(seed)
random_50_idx = rng.choice(N, k, replace=False)   # (k,)

variance_50_var = variance_i[variance_50_idx]      # (k,)
random_50_var   = variance_i[random_50_idx]        # (k,)

mean_var_selected = float(np.mean(variance_50_var))
mean_var_random   = float(np.mean(random_50_var))
difference        = mean_var_selected - mean_var_random
boundary_gap      = float(variance_i[ranked_idx[k-1]] - variance_i[ranked_idx[k]])
gate_passed       = difference > 0

mwu_stat, mwu_p = scipy.stats.mannwhitneyu(
    variance_50_var, random_50_var, alternative='greater'
)

# Mechanism verification asserts (FR-7)
assert len(variance_50_idx) == k
assert variance_i[ranked_idx[0]] >= variance_i[ranked_idx[-1]]
assert np.all(variance_i[variance_50_idx] >= variance_i[ranked_idx[k]])

return {
    "gate_passed": gate_passed,
    "mean_var_selected": mean_var_selected,
    "mean_var_random": mean_var_random,
    "difference": difference,
    "boundary_gap": boundary_gap,
    "mwu_stat": float(mwu_stat),
    "mwu_p": float(mwu_p),
    "variance_50_ids": problem_ids[variance_50_idx].tolist(),
    "random_50_ids": problem_ids[random_50_idx].tolist(),
    "seed": seed,
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | compare_selections | argsort top-k, rng random-k, means, boundary_gap, mannwhitneyu, asserts, return dict |

---

## A-5: Figures [Complexity: 10, Budget: 1 subtask]

### API Signatures

```python
def make_figures(
    variance_i: np.ndarray,      # (N,) all variances
    variance_50_idx: np.ndarray, # (k,) indices of variance-selected problems
    random_50_idx: np.ndarray,   # (k,) indices of random-selected problems
    p_i: np.ndarray,             # (N,) pass rates (unused in fig1-4 except fig2)
    figures_dir: Path,
) -> None:
    """Save fig1–fig4 PNGs to figures_dir. Uses matplotlib Agg backend."""
    ...
```

### Pseudo-code

```
figures_dir.mkdir(parents=True, exist_ok=True)

var_selected = variance_i[variance_50_idx]   # (k,)
var_random   = variance_i[random_50_idx]     # (k,)
N = len(variance_i)

# Fig 1: bar + strip plot (means comparison)
fig, ax = subplots()
ax.bar(["variance-50", "random-50"], [mean(var_selected), mean(var_random)])
ax.scatter([0]*k, var_selected, alpha=0.4)   # strip
ax.scatter([1]*k, var_random,   alpha=0.4)
save → "fig1_mean_comparison.png"

# Fig 2: side-by-side histograms + full-374 grey overlay
fig, axes = subplots(1, 2, sharey=True)
axes[0].hist(variance_i, bins=10, range=[0,0.25], color='grey', alpha=0.4, label='all-374')
axes[0].hist(var_selected, bins=10, range=[0,0.25], label='variance-50')
axes[1].hist(variance_i, bins=10, range=[0,0.25], color='grey', alpha=0.4, label='all-374')
axes[1].hist(var_random,   bins=10, range=[0,0.25], label='random-50')
save → "fig2_histograms.png"

# Fig 3: rank plot — sorted variance with rank-k boundary
sorted_var = variance_i[argsort(variance_i)[::-1]]   # (N,) descending
fig, ax = subplots()
ax.plot(range(1, N+1), sorted_var)
ax.axvline(k, color='red', linestyle='--', label=f'rank-{k} boundary')
ax.axvspan(1, k, alpha=0.1, color='green', label='selected')
save → "fig3_rank_plot.png"

# Fig 4: empirical CDF comparison
for arr, label in [(sorted(var_selected), 'variance-50'), (sorted(var_random), 'random-50')]:
    y = linspace(0, 1, len(arr))
    ax.plot(arr, y, label=label)
save → "fig4_cdf.png"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | make_figures | 4 matplotlib figures: bar+strip, histograms, rank plot, empirical CDF |

---

## Supporting Functions (Low Complexity — No Subtask Budget Used)

```python
def load_profiling_output(json_path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Parse H-E1 JSON → (problem_ids, p_i, variance_i), all shape (N,).
    Keys sorted ascending by int(task_id) for deterministic array order.
    Raises FileNotFoundError if json_path missing (triggers fallback).
    Validates p_i in [0,1], variance_i in [0,0.25].
    Note: JSON key is 'top50_ids' (not 'top_ids') — verified from h-e1 code.
    """
    # sorted_keys = sorted(data["problems"].keys(), key=int)
    # arrays built in that order → problem_ids, p_i, variance_i
    ...

def run_fallback_profiling(results_dir: Path) -> Path:
    """Subprocess call to h-e1/code/profile_mbpp.py. Returns regenerated JSON path."""
    # subprocess.run([sys.executable, "docs/youra_research/h-e1/code/profile_mbpp.py"], check=True)
    ...

def save_results(results: dict, results_dir: Path) -> None:
    """Write results dict → results_dir/comparison_results.json."""
    ...

def main() -> int:
    """Orchestrate: load → compare → figures → save → print gate → return 0/1."""
    ...
```

### Critical Implementation Notes

- `matplotlib.use("Agg")` before any `import matplotlib.pyplot` (headless; matches H-E1 pattern)
- Read `k` from `data["metrics"]` — but H-E1 `metrics` dict has no `"k"` key (verified). Use `k=50` as fixed parameter for H-M1 selection; H-E1's profiling `k=8` is unrelated.
- JSON key is `"top50_ids"` not `"top_ids"` — the architecture doc was wrong, actual H-E1 code (line 220) writes `"top50_ids"`.
- Array order: sort `problems.keys()` by `int(key)` for reproducibility — do NOT rely on JSON dict order.
- `mannwhitneyu` import: `from scipy.stats import mannwhitneyu`
