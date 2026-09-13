# Logic Design: H-M3
# Post-Breakpoint CoV Directional Skewness Analysis

**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr
**Hypothesis:** H-M3 (MECHANISM / SHOULD_WORK)
**Budget:** 6 subtasks

Applied: modular-dataclass pattern (SegmentMoments + DirectionalTestResults dataclasses as data contracts between pipeline stages)

---

## Codebase Analysis (Serena)

**Analyzed**: `docs/youra_research/h-m2/code/data_loader.py` (actual implementation)
**Finding**: `load_residual_cov` returns `(paper_counts: np.ndarray[int], residual_cov: np.ndarray[float])` sorted ascending. `load_paper_count_star_idx` takes `(results_json_path: Path, paper_counts: np.ndarray, residual_cov: np.ndarray) -> int` returning 0-based breakpoint index. Both are verbatim-reusable for H-M3.
**H-M2 pattern**: flat module pipeline — data_loader → analyzer → verifier → visualizer → main. H-M3 expands analyzer into `distributional_moments` + `directional_tests` for cleaner separation.

---

## External Dependencies API

### From H-M2 `data_loader.py` (verified from actual code)

```python
# Exact signatures verified from docs/youra_research/h-m2/code/data_loader.py

def load_residual_cov(csv_path: Path) -> Tuple[np.ndarray, np.ndarray]:
    """Returns (paper_counts: np.ndarray[int], residual_cov: np.ndarray[float])
    Sorted ascending by paper_count.
    Raises: FileNotFoundError, ValueError (N not in [100,200], missing cols)
    """

def load_paper_count_star_idx(
    results_json_path: Path,
    paper_counts: np.ndarray,
    residual_cov: np.ndarray,
) -> int:
    """Returns 0-based breakpoint index (int).
    Loads from H-E1 JSON key 'breakpoint_idx'; falls back to PELT if absent.
    Raises: ValueError if idx at boundary or pre_segment < 3 elements.
    """
```

---

## Subtask L-1: visualization.py — plot_gate_metrics (A-5, subtask 1)

### API

```python
def plot_gate_metrics(
    results: DirectionalTestResults,
    gate: GateResult,
    figures_dir: Path,
) -> Path:
    """Bar chart of all 4 directional metrics with pass/fail coloring.
    
    Returns: Path to saved figure (figures_dir / "gate_metrics.png")
    """
```

### Pseudo-code

```python
def plot_gate_metrics(results, gate, figures_dir):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # --- Left panel: skewness direction (metric 1) ---
    ax = axes[0]
    bars = ax.bar(
        ['skew_pre', 'skew_post'],
        [results.skew_pre, results.skew_post],
        color=['#2196F3', '#4CAF50' if results.metric1_pass else '#F44336']
    )
    ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
    ax.set_title(f'Metric 1: Skewness Direction\n{"PASS ✓" if results.metric1_pass else "FAIL ✗"}')
    ax.set_ylabel('Fisher-Pearson G1 skewness (bias=False)')
    # annotate values
    for bar, val in zip(bars, [results.skew_pre, results.skew_post]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                f'{val:.3f}', ha='center', va='bottom')
    
    # --- Right panel: all 4 metrics p-values / thresholds (metric 2-4 + summary) ---
    ax = axes[1]
    metric_labels = ['M1\nskew\ndirection', 'M2\np10\nlower tail', 
                     'M3\nperm p\n(skew diff)', 'M4\nMW p\n(pre>post)']
    # For M1/M2 use binary pass/fail (no p-value), for M3/M4 use actual p-values
    metric_values = [
        1.0 if results.metric1_pass else 0.0,      # binary
        1.0 if results.metric2_pass else 0.0,      # binary (p10 comparison)
        results.perm_p_skew_diff,                  # actual p
        results.mw_pvalue,                          # actual p
    ]
    pass_flags = [results.metric1_pass, results.metric2_pass,
                  results.metric3_pass, results.metric4_pass]
    colors = ['#4CAF50' if p else '#F44336' for p in pass_flags]
    bars = ax.bar(metric_labels, metric_values, color=colors, alpha=0.8)
    # threshold line for p-value metrics
    ax.axhline(0.10, color='orange', linewidth=1.5, linestyle='--', label='p=0.10 threshold')
    ax.set_ylim(0, 1.1)
    ax.set_ylabel('p-value / pass indicator')
    ax.set_title(
        f'Gate: {"PASS ✓" if gate.gate_passed else "EXPLORE ○"} '
        f'({gate.metrics_passed}/4 metrics consistent with H1)'
    )
    ax.legend()
    
    figures_dir.mkdir(parents=True, exist_ok=True)
    out = figures_dir / "gate_metrics.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return out
```

---

## Subtask L-2: visualization.py — plot_histogram_overlay (A-5, subtask 2)

### API

```python
def plot_histogram_overlay(
    pre_segment: np.ndarray,
    post_segment: np.ndarray,
    pre_moments: SegmentMoments,
    post_moments: SegmentMoments,
    figures_dir: Path,
) -> Path:
    """Overlapping histograms + KDE + vertical p10 lines.
    
    Returns: Path (figures_dir / "histogram_overlay.png")
    """
```

### Pseudo-code

```python
def plot_histogram_overlay(pre_segment, post_segment, pre_moments, post_moments, figures_dir):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # histograms (semi-transparent)
    ax.hist(pre_segment, bins=20, alpha=0.4, color='#F44336', label=f'Pre (n={pre_moments.n})', density=True)
    ax.hist(post_segment, bins=20, alpha=0.4, color='#2196F3', label=f'Post (n={post_moments.n})', density=True)
    
    # KDE overlay using scipy.stats.gaussian_kde
    from scipy.stats import gaussian_kde
    x_range = np.linspace(
        min(pre_segment.min(), post_segment.min()) - 0.05,
        max(pre_segment.max(), post_segment.max()) + 0.05,
        300
    )
    kde_pre = gaussian_kde(pre_segment)
    kde_post = gaussian_kde(post_segment)
    ax.plot(x_range, kde_pre(x_range), color='#C62828', linewidth=2, label='Pre KDE')
    ax.plot(x_range, kde_post(x_range), color='#0D47A1', linewidth=2, label='Post KDE')
    
    # vertical lines at 10th percentile
    ax.axvline(pre_moments.p10, color='#C62828', linestyle=':', linewidth=1.5,
               label=f'Pre p10={pre_moments.p10:.3f}')
    ax.axvline(post_moments.p10, color='#0D47A1', linestyle=':', linewidth=1.5,
               label=f'Post p10={post_moments.p10:.3f}')
    
    ax.set_xlabel('Residual CoV')
    ax.set_ylabel('Density')
    ax.set_title(
        f'Pre vs Post Residual CoV Distribution\n'
        f'skew_pre={pre_moments.skewness:.3f}, skew_post={post_moments.skewness:.3f}'
    )
    ax.legend()
    
    out = figures_dir / "histogram_overlay.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return out
```

---

## Subtask L-3: visualization.py — plot_ecdf (A-5, subtask 3)

### API

```python
def plot_ecdf(
    pre_segment: np.ndarray,
    post_segment: np.ndarray,
    pre_moments: SegmentMoments,
    post_moments: SegmentMoments,
    figures_dir: Path,
) -> Path:
    """Empirical CDF with shaded p10-p25 lower-tail region.
    
    Returns: Path (figures_dir / "ecdf.png")
    """

def plot_qq(
    pre_segment: np.ndarray,
    post_segment: np.ndarray,
    figures_dir: Path,
) -> Path:
    """Pre vs post quantile-quantile plot.
    
    Returns: Path (figures_dir / "qq_plot.png")
    """
```

### Pseudo-code

```python
def plot_ecdf(pre_segment, post_segment, pre_moments, post_moments, figures_dir):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # ECDF for pre
    pre_sorted = np.sort(pre_segment)
    pre_cdf = np.arange(1, len(pre_sorted)+1) / len(pre_sorted)
    ax.step(pre_sorted, pre_cdf, color='#C62828', linewidth=2, label=f'Pre (n={pre_moments.n})')
    
    # ECDF for post
    post_sorted = np.sort(post_segment)
    post_cdf = np.arange(1, len(post_sorted)+1) / len(post_sorted)
    ax.step(post_sorted, post_cdf, color='#0D47A1', linewidth=2, label=f'Post (n={post_moments.n})')
    
    # shade lower-tail region (p10-p25 of combined)
    x_low = min(pre_moments.p10, post_moments.p10)
    x_high = max(pre_moments.p25, post_moments.p25)
    ax.axvspan(x_low, x_high, alpha=0.15, color='gold', label='Lower tail (p10-p25 region)')
    
    # p10 vertical markers
    ax.axvline(pre_moments.p10, color='#C62828', linestyle=':', alpha=0.7)
    ax.axvline(post_moments.p10, color='#0D47A1', linestyle=':', alpha=0.7)
    
    ax.set_xlabel('Residual CoV')
    ax.set_ylabel('Cumulative Probability')
    ax.set_title('Empirical CDF: Pre vs Post Residual CoV (Lower-Tail Focus)')
    ax.legend()
    
    out = figures_dir / "ecdf.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return out


def plot_qq(pre_segment, post_segment, figures_dir):
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # compute quantiles at same probability levels
    n_quantiles = min(len(pre_segment), len(post_segment))
    probs = np.linspace(0, 1, n_quantiles + 2)[1:-1]
    q_pre = np.quantile(pre_segment, probs)
    q_post = np.quantile(post_segment, probs)
    
    ax.scatter(q_pre, q_post, alpha=0.7, color='#7B1FA2', s=40, label='Quantile pairs')
    
    # diagonal reference line
    lo = min(q_pre.min(), q_post.min())
    hi = max(q_pre.max(), q_post.max())
    ax.plot([lo, hi], [lo, hi], 'k--', linewidth=1.2, label='y=x (equal distributions)')
    
    ax.set_xlabel('Pre-segment quantiles')
    ax.set_ylabel('Post-segment quantiles')
    ax.set_title('Q-Q Plot: Pre vs Post Residual CoV\n(Points below diagonal → post concentrated lower)')
    ax.legend()
    
    out = figures_dir / "qq_plot.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return out
```

---

## Subtask L-4: visualization.py — save_all_figures (A-5, subtask 4)

### API

```python
def plot_moments_table(
    pre_moments: SegmentMoments,
    post_moments: SegmentMoments,
    figures_dir: Path,
) -> Path:
    """Side-by-side moments table (mean, variance, skewness, kurtosis).
    
    Returns: Path (figures_dir / "moments_table.png")
    """

def save_all_figures(
    pre_segment: np.ndarray,
    post_segment: np.ndarray,
    pre_moments: SegmentMoments,
    post_moments: SegmentMoments,
    results: DirectionalTestResults,
    gate: GateResult,
    figures_dir: Path,
) -> list:
    """Call all 5 figure functions; return list of saved Paths."""
```

### Pseudo-code

```python
def plot_moments_table(pre_moments, post_moments, figures_dir):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis('off')
    
    rows = ['Mean', 'Variance', 'Skewness', 'Kurtosis (excess)']
    pre_vals = [f'{pre_moments.mean:.4f}', f'{pre_moments.variance:.6f}',
                f'{pre_moments.skewness:.4f}', f'{pre_moments.kurtosis:.4f}']
    post_vals = [f'{post_moments.mean:.4f}', f'{post_moments.variance:.6f}',
                 f'{post_moments.skewness:.4f}', f'{post_moments.kurtosis:.4f}']
    
    table = ax.table(
        cellText=[[r, p, q] for r, p, q in zip(rows, pre_vals, post_vals)],
        colLabels=['Moment', f'Pre (n={pre_moments.n})', f'Post (n={post_moments.n})'],
        cellLoc='center', loc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 1.8)
    ax.set_title('Distribution Moments: Pre vs Post Segments', pad=20, fontsize=14)
    
    out = figures_dir / "moments_table.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return out


def save_all_figures(pre_segment, post_segment, pre_moments, post_moments,
                     results, gate, figures_dir):
    figures_dir.mkdir(parents=True, exist_ok=True)
    paths = [
        plot_gate_metrics(results, gate, figures_dir),
        plot_histogram_overlay(pre_segment, post_segment, pre_moments, post_moments, figures_dir),
        plot_moments_table(pre_moments, post_moments, figures_dir),
        plot_ecdf(pre_segment, post_segment, pre_moments, post_moments, figures_dir),
        plot_qq(pre_segment, post_segment, figures_dir),
    ]
    print(f"Saved {len(paths)} figures to {figures_dir}")
    return paths
```

---

## Subtask L-5: directional_tests.py — permutation_test (A-3, subtask 1)

### Pseudo-code (vectorized skew_diff_stat + permutation_test)

```python
from scipy.stats import permutation_test, skew as scipy_skew, mannwhitneyu
import numpy as np

def _skew_diff_stat(x: np.ndarray, y: np.ndarray, axis: int = 0) -> float:
    """Vectorized statistic: skewness(post) - skewness(pre).
    
    NOTE: permutation_test passes batched arrays when vectorized=True;
    axis parameter is required for vectorized usage.
    scipy_skew bias is NOT controllable via axis call in vectorized mode —
    use bias=False in the non-vectorized outer call for reporting,
    but permutation_test vectorized requires axis-based skew.
    """
    return scipy_skew(y, axis=axis, bias=False) - scipy_skew(x, axis=axis, bias=False)


def _run_permutation_test(
    pre_segment: np.ndarray,
    post_segment: np.ndarray,
    n_resamples: int = 9999,
    random_state: int = 42,
) -> float:
    """Run permutation test on skewness difference; return p-value (two-sided).
    
    Returns:
        perm_p_skew_diff: float — two-sided p-value
    """
    result = permutation_test(
        data=(pre_segment, post_segment),
        statistic=_skew_diff_stat,
        permutation_type='independent',
        vectorized=True,
        n_resamples=n_resamples,
        alternative='two-sided',
        random_state=random_state,
    )
    return float(result.pvalue)
```

---

## Subtask L-6: directional_tests.py — full run_directional_tests (A-3, subtask 2)

### Full API implementation pseudo-code

```python
def run_directional_tests(
    pre_segment: np.ndarray,
    post_segment: np.ndarray,
    pre_moments: "SegmentMoments",
    post_moments: "SegmentMoments",
    n_resamples: int = 9999,
    random_state: int = 42,
    p_threshold: float = 0.10,
) -> DirectionalTestResults:
    """Compute all 4 directional metrics for H-M3 SHOULD_WORK gate.
    
    Metric 1: Skewness direction (skew_post < skew_pre OR skew_post < 0)
    Metric 2: Lower-tail concentration (p10_post < p10_pre)
    Metric 3: Permutation test skewness difference (p < p_threshold)
    Metric 4: Mann-Whitney stochastic dominance pre>post (p < p_threshold)
    """
    # Metric 1: skewness direction — use pre-computed moments (no recompute)
    skew_pre = pre_moments.skewness
    skew_post = post_moments.skewness
    metric1_pass = bool((skew_post < skew_pre) or (skew_post < 0.0))
    print(f"Metric 1 (skewness direction): skew_pre={skew_pre:.4f}, "
          f"skew_post={skew_post:.4f}, pass={metric1_pass}")

    # Metric 2: lower-tail (10th percentile)
    p10_pre = pre_moments.p10
    p10_post = post_moments.p10
    metric2_pass = bool(p10_post < p10_pre)
    print(f"Metric 2 (lower tail): p10_pre={p10_pre:.4f}, p10_post={p10_post:.4f}, "
          f"pass={metric2_pass}")

    # Metric 3: permutation test on skewness difference
    perm_p = _run_permutation_test(pre_segment, post_segment, n_resamples, random_state)
    metric3_pass = bool(perm_p < p_threshold)
    print(f"Metric 3 (perm test skewness diff): p={perm_p:.4f}, pass={metric3_pass}")

    # Metric 4: Mann-Whitney U (pre stochastically > post)
    mw_result = mannwhitneyu(
        pre_segment,
        post_segment,
        alternative='greater',   # H1: pre > post stochastically
        method='auto',           # exact for small N, asymptotic otherwise
    )
    metric4_pass = bool(mw_result.pvalue < p_threshold)
    print(f"Metric 4 (Mann-Whitney, pre>post): p={mw_result.pvalue:.4f}, "
          f"statistic={mw_result.statistic:.1f}, pass={metric4_pass}")

    return DirectionalTestResults(
        skew_pre=skew_pre,
        skew_post=skew_post,
        metric1_pass=metric1_pass,
        p10_pre=p10_pre,
        p10_post=p10_post,
        metric2_pass=metric2_pass,
        perm_p_skew_diff=perm_p,
        metric3_pass=metric3_pass,
        mw_pvalue=float(mw_result.pvalue),
        mw_statistic=float(mw_result.statistic),
        metric4_pass=metric4_pass,
    )
```

---

## Data Contracts Summary

### SegmentMoments (from distributional_moments.py)
```python
@dataclass
class SegmentMoments:
    n: int
    mean: float
    variance: float       # ddof=1 (sample variance, from scipy.stats.describe)
    skewness: float       # Fisher-Pearson G1, bias=False (adjusted for small N)
    kurtosis: float       # excess kurtosis (0 = normal), bias=False
    p10: float            # np.percentile(segment, 10)
    p25: float            # np.percentile(segment, 25)
    p75: float            # np.percentile(segment, 75)
```

### DirectionalTestResults (from directional_tests.py)
```python
@dataclass
class DirectionalTestResults:
    skew_pre: float; skew_post: float; metric1_pass: bool
    p10_pre: float; p10_post: float; metric2_pass: bool
    perm_p_skew_diff: float; metric3_pass: bool
    mw_pvalue: float; mw_statistic: float; metric4_pass: bool
```

### GateResult (from verifier.py)
```python
@dataclass
class GateResult:
    metrics_passed: int
    gate_passed: bool       # metrics_passed >= 2
    gate_type: str          # "PASS" or "EXPLORE"
    verdict_message: str
```
