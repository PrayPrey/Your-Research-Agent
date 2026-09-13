---
hypothesis_id: h-m1
type: MECHANISM
generated_at: 2026-08-21
author: yoon303@etri.re.kr
---

Applied: single-script statistical analysis pattern (no module decomposition needed)

# Architecture: H-M1 — Variance Selection Ranking Signal Validation

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Patterns found from base code (H-E1)
**Analyzed Path**: `docs/youra_research/h-e1/code/profile_mbpp.py`
**Findings**: H-E1 is a single-script profiler. Results JSON uses `problems` dict keyed by task_id (str), each with `p_i`, `variance_i`, `pass_count`, `k`, `rank_by_variance`. Top-level keys: `gate_passed`, `metrics`, `top_ids`, `problems`. No importable modules — H-M1 reads JSON artifact only.

---

## External Dependencies (Base Hypothesis)

| Artifact | Type | Location |
|----------|------|----------|
| Profiling output | JSON file | `docs/youra_research/h-e1/results/mbpp_variance_profile.json` |
| Fallback profiler | Script reference | `docs/youra_research/h-e1/code/profile_mbpp.py` |

**JSON schema (actual)**:
```
{
  "gate_passed": bool,
  "metrics": { "n_problems": int, "k": int, ... },
  "top_ids": [int, ...],         # ranked by variance, descending
  "problems": {
    "<task_id_str>": {
      "p_i": float,
      "variance_i": float,
      "pass_count": int,
      "k": int,
      "rank_by_variance": int
    }, ...
  }
}
```

**Note**: `k=4` in actual H-E1 output (not k=8 as in experiment brief). Script must read `k` from JSON, not assume.

---

## Module Structure

H-M1 is a **single script** — no module decomposition.

### `compare_variance_selection.py` (`code/compare_variance_selection.py`)

**Dependencies**: numpy, scipy.stats, matplotlib, json, pathlib (all stdlib or already-installed)

```python
# ---- top-level functions (interface) ----

def load_profiling_output(json_path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Returns: (problem_ids, p_i, variance_i) — all shape (N,), N=374
    Raises FileNotFoundError if absent (triggers fallback path).
    Validates: values in [0,1] and [0,0.25] respectively.
    """
    ...

def run_fallback_profiling(results_dir: Path) -> Path:
    """
    Reruns H-E1 profiling via subprocess call to profile_mbpp.py.
    Returns path to regenerated JSON.
    Only called if load_profiling_output raises FileNotFoundError.
    """
    ...

def compare_selections(
    variance_i: np.ndarray,
    problem_ids: np.ndarray,
    k: int = 50,
    seed: int = 42,
) -> dict:
    """
    Returns comparison dict:
      gate_passed, mean_var_selected, mean_var_random, difference,
      boundary_gap, mwu_stat, mwu_p, variance_50_ids, random_50_ids, seed
    Runs mechanism verification asserts internally.
    """
    ...

def make_figures(
    variance_i: np.ndarray,
    variance_50_idx: np.ndarray,
    random_50_idx: np.ndarray,
    p_i: np.ndarray,
    figures_dir: Path,
) -> None:
    """
    Saves 4 figures to figures_dir:
      fig1_mean_comparison.png  — bar + strip plot
      fig2_histograms.png       — side-by-side histograms + full-374 grey
      fig3_rank_plot.png        — sorted variance with rank-50 boundary
      fig4_cdf.png              — empirical CDF comparison
    """
    ...

def save_results(results: dict, results_dir: Path) -> None:
    """Saves results to results_dir/comparison_results.json"""
    ...

def main() -> int:
    """
    Returns 0 (PASS) or 1 (FAIL).
    Flow:
      1. load_profiling_output  (fallback: run_fallback_profiling)
      2. compare_selections
      3. make_figures
      4. save_results
      5. print gate summary; return 0 if gate_passed else 1
    """
    ...

if __name__ == "__main__":
    sys.exit(main())
```

---

## File Organization

```
code/
  compare_variance_selection.py   # single script, ~250 lines

docs/youra_research/h-m1/
  figures/
    fig1_mean_comparison.png
    fig2_histograms.png
    fig3_rank_plot.png
    fig4_cdf.png
  results/
    comparison_results.json
  03_architecture.md              # this file
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Script scaffold | File, imports, main() skeleton, arg/path setup | 4 | 1+1+1+1 |
| A-2 | Load & validate JSON | load_profiling_output: parse problems dict → numpy arrays, validate ranges, FileNotFoundError path | 6 | 2+1+2+1 |
| A-3 | Fallback profiling | run_fallback_profiling: subprocess call to h-e1 profile_mbpp.py, wait, return path | 5 | 1+2+1+1 |
| A-4 | Core comparison | compare_selections: argsort top-50, rng random-50, means, boundary_gap, Mann-Whitney U, asserts | 9 | 2+2+3+2 |
| A-5 | Figures (4) | make_figures: bar+strip, histograms, rank plot, CDF — matplotlib, save to figures_dir | 10 | 3+1+4+2 |
| A-6 | Results output & gate | save_results JSON, print gate log line, sys.exit(0/1) | 4 | 1+1+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-4, A-5], Low(4-8): [A-1, A-2, A-3, A-6]

**Total estimated LOC**: ~250 lines. Runtime: ~5s on CPU (primary path).

---

## Data Flow

```
h-e1/results/mbpp_variance_profile.json
  → load_profiling_output()
      → (problem_ids, p_i, variance_i) arrays (N=374)
  → compare_selections()
      → top-50 by argsort(variance_i)[::-1][:50]
      → random-50 by rng(seed=42).choice(374, 50)
      → mannwhitneyu(variance_50_var, random_50_var, alternative='greater')
      → results dict
  → make_figures()       → h-m1/figures/fig{1..4}_*.png
  → save_results()       → h-m1/results/comparison_results.json
  → sys.exit(0 or 1)
```

---

## Implementation Notes

- Parse `problems` dict by iterating sorted task_id keys to build ordered numpy arrays. Do NOT assume `top_ids` order equals argsort order — recompute argsort from `variance_i` array.
- Read actual `k` from `data["metrics"]["k"]` (actual value is 4, not 8).
- `silent_rate(p, G=4) = p**4 + (1-p)**4` — compute inline for fig4 scatter if added; not a separate function.
- `matplotlib.use("Agg")` before import (matches H-E1 pattern, headless server).
- All paths relative to repo root (script run from repo root via `python code/compare_variance_selection.py`).
