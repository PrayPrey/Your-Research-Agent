# Logic Design: H-M2
# Post-Breakpoint Residual CoV Variance Compression Validation — API Signatures, Pseudo-code

**Hypothesis:** H-M2 (MECHANISM / INCREMENTAL — extends H-M1)
**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr
**Budget:** 4 subtasks (A-5 × 2, A-8 × 2)

Applied: segment-split reuse pattern (data_loader.py copied verbatim from H-M1; analyzer extends run_brown_forsythe to primary gate with variance ratio)

---

## Codebase Analysis (Serena)

**Analyzed Path:** `docs/youra_research/h-m1/code/`
**Method:** Direct file reads (Read tool; actual implementation verified)

**Key findings from H-M1 actual code:**

- `data_loader.py`: `load_residual_cov(csv_path: Path) -> (paper_counts, residual_cov)` — returns both arrays sorted ascending; H-M2 copies verbatim, no changes needed
- `data_loader.py`: `load_paper_count_star_idx(results_json_path, paper_counts, residual_cov) -> int` — reads `breakpoint_idx` (0-based int) from H-E1 JSON; PELT fallback if missing; H-M2 copies verbatim
- `analyzer.py`: `run_brown_forsythe(pre, post) -> (float, float)` — `stats.levene(pre, post, center="median")`; returns (bf_stat, bf_p). H-M2 EXTENDS this to primary gate with variance ratio and one-tailed logic
- `analyzer.py`: `split_segments(residual_cov, idx) -> (pre, post)` — guards `len(pre) < 3`; H-M2 adds `len(post) < 3` guard
- `experiment_results.json` (H-E1): contains `"breakpoint_idx": 34` (0-based integer) — this is paper_count_star_idx

**Reuse decision:** data_loader.py copied verbatim from H-M1. analyzer.py rewritten for H-M2 primary gate (BF pre-vs-post + variance ratio + piecewise F-test). verifier.py rewritten with H-M2 indicators.

---

## External Dependencies API

### From H-E1 experiment_results.json (verified from actual file)

```json
{
  "paper_count_star": 47.0,
  "breakpoint_idx": 34,
  "n_bkps_detected": 1,
  "permutation_p": 0.023,
  "gate_passed": true
}
```

**Key field:** `breakpoint_idx` (int, 0-based index into sorted residual_cov array)

### From H-M1 data_loader.py (verified from actual code — lines 11-95)

```python
# Copied verbatim to h-m2/code/data_loader.py — no changes required

def load_residual_cov(
    csv_path: Path,
) -> tuple[np.ndarray, np.ndarray]:
    """Returns (paper_counts, residual_cov) sorted by paper_count ascending.
    paper_counts: shape (N,) dtype int
    residual_cov: shape (N,) dtype float
    """

def load_paper_count_star_idx(
    results_json_path: Path,    # H-E1 experiment_results.json
    paper_counts: np.ndarray,   # shape (N,) from load_residual_cov
    residual_cov: np.ndarray,   # shape (N,) from load_residual_cov
) -> int:
    """Reads breakpoint_idx from JSON; PELT fallback if missing.
    Returns 0-based int in open interval (0, N).
    """
```

**Note:** H-M1 actual code uses `h_e1_results.get("breakpoint_idx")` (not `"paper_count_star_idx"`). H-M2 must use the same key.

---

## Subtask L-5-1: `run_piecewise_f_test()` — Nested OLS F-Test API

**Parent Epic:** A-5 (piecewise regression F-test, complexity=12)
**File:** `h-m2/code/analyzer.py`

### API Signature

```python
def run_piecewise_f_test(
    paper_counts: np.ndarray,       # shape (N,) int — sorted ascending
    residual_cov: np.ndarray,       # shape (N,) float — OLS-detrended CoV
    paper_count_star_idx: int,      # 0-based breakpoint index
) -> tuple[float, float]:
    """
    Compare nested OLS models via F-test (statsmodels).

    Baseline model: residual_cov ~ 1 + paper_count  (2 params)
    Piecewise model: residual_cov ~ 1 + paper_count + regime + paper_count*regime  (4 params)

    Where: regime = (paper_counts >= paper_counts[paper_count_star_idx]).astype(int)

    F-statistic: F = ((RSS_base - RSS_piece) / q) / (RSS_piece / (N - p_piece))
    where q = p_piece - p_base = 2 (additional parameters), N = 111

    Returns:
        f_stat: float — F-statistic for piecewise vs baseline
        f_p: float — p-value from F(q, N-p_piece) distribution

    Raises:
        ValueError: if paper_count_star_idx not in (0, N)
        ImportError: if statsmodels not installed
    """
```

### Pseudo-code

```python
def run_piecewise_f_test(
    paper_counts: np.ndarray,
    residual_cov: np.ndarray,
    paper_count_star_idx: int,
) -> tuple[float, float]:
    import statsmodels.api as sm
    from scipy import stats as scipy_stats

    N = len(paper_counts)

    # Step 1: Regime indicator (post = 1, pre = 0)
    regime = (paper_counts >= paper_counts[paper_count_star_idx]).astype(int)

    # Step 2: Baseline model — cov ~ 1 + paper_count (2 params)
    X_base = sm.add_constant(paper_counts.astype(float))
    model_base = sm.OLS(residual_cov, X_base).fit()
    rss_base = float(model_base.ssr)
    p_base = X_base.shape[1]  # = 2

    # Step 3: Piecewise model — cov ~ 1 + paper_count + regime + paper_count*regime (4 params)
    interaction = paper_counts.astype(float) * regime
    X_piece = np.column_stack([
        np.ones(N),
        paper_counts.astype(float),
        regime,
        interaction,
    ])
    model_piece = sm.OLS(residual_cov, X_piece).fit()
    rss_piece = float(model_piece.ssr)
    p_piece = X_piece.shape[1]  # = 4

    # Step 4: F-statistic (manual; avoids statsmodels anova_lm column name issues)
    q = p_piece - p_base  # = 2 (additional params)
    df_num = q
    df_den = N - p_piece  # = 111 - 4 = 107
    if df_den <= 0 or q <= 0:
        raise ValueError(f"Degenerate F-test: df_num={df_num}, df_den={df_den}")

    f_stat = ((rss_base - rss_piece) / q) / (rss_piece / df_den)
    f_p = float(1.0 - scipy_stats.f.cdf(f_stat, df_num, df_den))

    print(f"Piecewise regression F-test: F={f_stat:.4f}, p={f_p:.4f} (df={df_num},{df_den})")
    return float(f_stat), f_p
```

### Statistical Notes
- Baseline RSS - piecewise RSS >= 0 always (piecewise is less restricted); negative F possible only due to numerical error → clamp to 0 if needed
- regime uses `>=` (paper_count_star_idx maps to the POST segment boundary index)
- interaction term allows different slopes pre/post breakpoint

### Edge Cases
- `paper_count_star_idx` at boundary (0 or N-1): regime is all-0 or all-1 → X_piece rank-deficient → statsmodels may warn; raise if RSS diff is negative
- All paper_counts identical (degenerate data): skip — H-E1 already validated variety

---

## Subtask L-5-2: `run_piecewise_f_test()` — Construction Details

**Parent Epic:** A-5 (piecewise regression F-test, complexity=12)

### Regime Indicator Construction

```
paper_count_star_idx = 34  (0-based; from H-E1)
paper_counts[34] = 47     (the actual paper_count value at the breakpoint)

regime[i] = 1  if paper_counts[i] >= paper_counts[34]  (i.e., paper_count >= 47)
regime[i] = 0  if paper_counts[i] < paper_counts[34]   (i.e., paper_count < 47)
```

### Design Matrix Layout

```
X_piece columns (N=111 rows × 4 cols):
  col 0: [1, 1, 1, ..., 1]                         # intercept (const)
  col 1: [1, 2, 3, ..., N_papers]                  # paper_count (continuous)
  col 2: [0, 0, ..., 0, 1, 1, ..., 1]              # regime indicator
  col 3: [0, 0, ..., 0, 47, 48, ..., N_papers]     # paper_count * regime (interaction)
```

### Interpretation
- β_0: baseline intercept (pre-segment)
- β_1: baseline slope (pre-segment paper_count effect)
- β_2: regime shift in intercept (post-segment level change)
- β_3: regime change in slope (post-segment paper_count effect change)

If β_3 ≠ 0 → different slopes pre/post → structural break confirmed by regression

---

## Subtask L-8-1: Visualizer API — All 5 Figure Functions

**Parent Epic:** A-8 (visualizer, complexity=10)
**File:** `h-m2/code/visualizer.py`

### Figure Function Signatures

```python
from pathlib import Path
from typing import List
import numpy as np
from analyzer import VarianceCompressionResults


def plot_gate_metrics(
    results: VarianceCompressionResults,
    out_dir: Path,
) -> Path:
    """
    Bar chart comparing gate metrics to thresholds.
    - Bar 1: bf_p_two_tailed vs threshold 0.05 (annotate PASS/FAIL)
    - Bar 2: variance_ratio vs threshold 1.0 (annotate PASS/FAIL)

    Returns: path to saved PNG (out_dir / "gate_metrics.png")
    Figure size: 8×6 in, DPI 150
    """


def plot_boxplots(
    pre: np.ndarray,   # shape (n_pre,) — pre-breakpoint residual_cov
    post: np.ndarray,  # shape (n_post,) — post-breakpoint residual_cov
    out_dir: Path,
) -> Path:
    """
    Side-by-side box plots: pre-segment (orange) vs post-segment (blue).
    Title: "Residual CoV Distribution by Regime"
    Annotate with variance values: var_pre={x:.4f}, var_post={x:.4f}

    Returns: path to saved PNG (out_dir / "boxplots_pre_post.png")
    Figure size: 8×6 in, DPI 150
    """


def plot_variance_bars(
    results: VarianceCompressionResults,
    out_dir: Path,
) -> Path:
    """
    Horizontal bar: var_pre (orange) vs var_post (blue) with ratio annotation.
    Title: "Variance Comparison: Pre vs Post Breakpoint"
    Annotation: f"ratio={results['variance_ratio']:.3f} (post/pre)"

    Returns: path to saved PNG (out_dir / "variance_bars.png")
    Figure size: 8×6 in, DPI 150
    """


def plot_scatter_regime(
    paper_counts: np.ndarray,          # shape (N,) int sorted ascending
    residual_cov: np.ndarray,          # shape (N,) float
    paper_count_star_idx: int,         # 0-based breakpoint index
    results: VarianceCompressionResults,
    out_dir: Path,
) -> Path:
    """
    Scatter of N=111 points colored by regime: pre=orange, post=blue.
    Overlay: mean ± 1 SD bands for each regime (horizontal shaded bands).
    Vertical dashed line at breakpoint paper_count value.
    Title: "Residual CoV by Regime (N=111)"

    Returns: path to saved PNG (out_dir / "scatter_regime.png")
    Figure size: 10×6 in, DPI 150
    """


def plot_f_distribution(
    results: VarianceCompressionResults,
    out_dir: Path,
) -> Path:
    """
    Annotated F(1, N-2) distribution with BF test statistic position.
    - PDF of F(1, 109) distribution
    - Vertical line at bf_stat value
    - Shaded region: p-value area (right tail from bf_stat onward)
    - Annotate: f"BF stat={bf_stat:.4f}, p={bf_p_two_tailed:.4f}"
    - Mark critical value at alpha=0.05

    Returns: path to saved PNG (out_dir / "f_distribution.png")
    Figure size: 8×5 in, DPI 150
    """


def save_all_figures(
    paper_counts: np.ndarray,
    residual_cov: np.ndarray,
    paper_count_star_idx: int,
    results: VarianceCompressionResults,
    out_dir: Path,
) -> List[Path]:
    """
    Run all 5 figure functions; create out_dir if missing; return saved paths.

    Returns: list of 5 Path objects [gate_metrics, boxplots, variance_bars,
                                      scatter_regime, f_distribution]
    """
```

---

## Subtask L-8-2: `save_all_figures()` — Orchestration and Naming

**Parent Epic:** A-8 (visualizer, complexity=10)

### Pseudo-code

```python
def save_all_figures(
    paper_counts: np.ndarray,
    residual_cov: np.ndarray,
    paper_count_star_idx: int,
    results: VarianceCompressionResults,
    out_dir: Path,
) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    # Reconstruct segments for boxplots
    pre = residual_cov[:paper_count_star_idx]
    post = residual_cov[paper_count_star_idx:]

    saved = []
    saved.append(plot_gate_metrics(results, out_dir))
    saved.append(plot_boxplots(pre, post, out_dir))
    saved.append(plot_variance_bars(results, out_dir))
    saved.append(plot_scatter_regime(paper_counts, residual_cov, paper_count_star_idx, results, out_dir))
    saved.append(plot_f_distribution(results, out_dir))

    print(f"Saved {len(saved)} figures to {out_dir}")
    return saved
```

### Figure Naming Convention

| Function | Output File |
|----------|-------------|
| `plot_gate_metrics` | `gate_metrics.png` |
| `plot_boxplots` | `boxplots_pre_post.png` |
| `plot_variance_bars` | `variance_bars.png` |
| `plot_scatter_regime` | `scatter_regime.png` |
| `plot_f_distribution` | `f_distribution.png` |

All saved to `docs/youra_research/h-m2/figures/` at DPI=150.

---

## Array Shape Summary

| Variable | Shape | dtype | Notes |
|----------|-------|-------|-------|
| paper_counts (input) | (111,) | int | sorted ascending, from H-E1 CSV |
| residual_cov (input) | (111,) | float | OLS-detrended CoV, from H-E1 CSV |
| pre_segment | (n_pre,) | float | n_pre = paper_count_star_idx (expect ~34-70) |
| post_segment | (n_post,) | float | n_post = 111 - paper_count_star_idx |
| regime | (111,) | int {0,1} | 0=pre, 1=post |
| interaction | (111,) | float | paper_counts * regime |
| X_piece | (111, 4) | float | design matrix for piecewise OLS |
| variance_ratio | scalar | float | var_post / var_pre; gate: < 1.0 |
| bf_stat | scalar | float | Brown-Forsythe W-statistic |
| bf_p_two_tailed | scalar | float | two-tailed p from levene(center='median') |
| f_stat (piecewise) | scalar | float | nested OLS F-statistic |
