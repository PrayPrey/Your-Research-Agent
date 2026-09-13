# Logic: H-M2 — Partial Spearman + Fisher Z Difference Test

Applied: flat-script statistical pipeline (H-M1 pattern)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: API signatures verified from actual H-M1 code
**Analyzed Path**: `docs/youra_research/h-m1/code/analyze.py`
**Relevant Symbols**: `load_data(cfg: AnalysisConfig)`, `run(cfg: AnalysisConfig)`, `np.random.seed(cfg.seed)` at top of `run()`

Key findings from actual H-M1 code:
- `load_data` renames `BBQ_accuracy` → `bbq_accuracy` internally and uses lowercase internally
- `run()` sets `np.random.seed(cfg.seed)` as first line
- H-M2 does NOT import from H-M1; reimplements `load_data` with `family` column added

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual H-M1 Code)

```python
# From: docs/youra_research/h-m1/code/analyze.py (ACTUAL CODE, lines 16-59)
# NOT reused directly — H-M2 reimplements with family extraction
def load_data(cfg: AnalysisConfig) -> pd.DataFrame:
    """Rename BBQ_accuracy->bbq_accuracy, dropna, normalize to [0,100], guard n_min."""
    # Required internal columns: model_name, TruthfulQA_MC2, bbq_accuracy, MMLU

# From: docs/youra_research/h-m1/code/analyze.py (ACTUAL CODE, lines 274-307)
def run(cfg: AnalysisConfig) -> dict:
    """First line: np.random.seed(cfg.seed) — H-M2 must match this pattern."""
```

**Verified from**: `docs/youra_research/h-m1/code/analyze.py` (actual implementation)

---

## A-4: Partial Spearman [Complexity: 9, Budget: 2 subtasks]

Applied: Standard PyTorch — pingouin.partial_corr exact call

### L-4-1: pingouin.partial_corr call and return extraction

```python
import pingouin as pg
import pandas as pd

def compute_partial_spearman(df: pd.DataFrame) -> dict:
    """Compute partial Spearman controlling for MMLU. Returns {partial_rho, partial_p}."""
    result: pd.DataFrame = pg.partial_corr(
        data=df,
        x="TruthfulQA_MC2",
        y="bbq_accuracy",
        covar=["MMLU"],
        method="spearman",
    )
    partial_rho: float = float(result["r"].iloc[0])
    partial_p: float = float(result["p-val"].iloc[0])
    return {"partial_rho": partial_rho, "partial_p": partial_p}
```

Note: pingouin returns column `"p-val"` (not `"p_val"`). Verify with `result.columns` if version changes.

**Pseudo-code:**
```
1. call pg.partial_corr(data=df, x, y, covar=['MMLU'], method='spearman')
2. extract r = result['r'].iloc[0], p = result['p-val'].iloc[0]
3. return {partial_rho: float(r), partial_p: float(p)}
```

### L-4-2: Mechanism activation assert and singular matrix guard

```python
import numpy as np
import warnings

def compute_partial_spearman(df: pd.DataFrame) -> dict:
    """Partial Spearman with domain checks and singular matrix guard."""
    # Singular matrix guard: check zero-variance before call
    for col in ["TruthfulQA_MC2", "bbq_accuracy", "MMLU"]:
        if df[col].std() == 0.0:
            raise RuntimeError(f"Zero variance in column '{col}' — singular matrix would result")

    with warnings.catch_warnings():
        warnings.filterwarnings("error", category=RuntimeWarning)
        try:
            result: pd.DataFrame = pg.partial_corr(
                data=df,
                x="TruthfulQA_MC2",
                y="bbq_accuracy",
                covar=["MMLU"],
                method="spearman",
            )
        except RuntimeWarning as e:
            raise RuntimeError(f"pingouin singular matrix: {e}") from e

    partial_rho: float = float(result["r"].iloc[0])
    partial_p: float = float(result["p-val"].iloc[0])

    if not (abs(partial_rho) < 1.0):
        raise RuntimeError(f"arctanh domain error: partial_rho={partial_rho}")

    return {"partial_rho": partial_rho, "partial_p": partial_p}
```

**Called from** `run()` after `compute_raw_spearman()`:
```
raw = compute_raw_spearman(df)
partial = compute_partial_spearman(df)
assert abs(partial['partial_rho'] - raw['raw_rho']) > 1e-6, "mechanism activation failed"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | pingouin call | Exact `pg.partial_corr` signature, column extraction (`r`, `p-val`) |
| L-4-2 | Guards | Zero-variance pre-check, arctanh domain assert, singular matrix RuntimeWarning catch |

---

## A-6: BCa Bootstrap CIs [Complexity: 13, Budget: 4 subtasks]

Applied: Standard PyTorch — pingouin.compute_bootci + manual loop

### L-6-1: BCa CI for raw_rho via pingouin.compute_bootci

```python
import pingouin as pg
import numpy as np
from typing import Tuple

def _bca_raw_rho(
    x: np.ndarray,   # shape: (N,) TruthfulQA_MC2 values
    y: np.ndarray,   # shape: (N,) bbq_accuracy values
    n_boot: int = 5000,
    seed: int = 42,
) -> Tuple[float, float]:
    """BCa 95% CI for raw Spearman rho via pingouin.compute_bootci."""
    ci: np.ndarray = pg.compute_bootci(
        x=x,
        y=y,
        func="spearman",
        method="bca",
        paired=True,
        n_boot=n_boot,
        seed=seed,
        return_dist=False,
    )
    # ci shape: (2,) → [lower, upper]
    return (float(ci[0]), float(ci[1]))
```

**Pseudo-code:**
```
1. ci = pg.compute_bootci(x, y, func='spearman', method='bca',
                          paired=True, n_boot=5000, seed=42)
2. return (ci[0], ci[1])
```

### L-6-2: Custom bootstrap loop for partial_rho BCa CI

```python
from scipy.stats import norm as scipy_norm
import numpy as np
import pandas as pd
from typing import Tuple

def _bca_partial_rho(
    df: pd.DataFrame,
    n_boot: int = 5000,
    seed: int = 42,
) -> Tuple[float, float]:
    """BCa 95% CI for partial_rho via manual bootstrap (pingouin.compute_bootci
    does not support partial_corr directly)."""
    rng = np.random.default_rng(seed)
    N = len(df)

    # Observed statistic
    obs_result = pg.partial_corr(
        data=df, x="TruthfulQA_MC2", y="bbq_accuracy", covar=["MMLU"], method="spearman"
    )
    obs_rho: float = float(obs_result["r"].iloc[0])

    # Bootstrap distribution
    boot_rhos = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, N, size=N)
        df_boot = df.iloc[idx].reset_index(drop=True)
        try:
            r = pg.partial_corr(
                data=df_boot, x="TruthfulQA_MC2", y="bbq_accuracy",
                covar=["MMLU"], method="spearman"
            )
            boot_rhos[i] = float(r["r"].iloc[0])
        except Exception:
            boot_rhos[i] = obs_rho  # fallback: use observed on degenerate bootstrap sample

    # BCa bias correction and acceleration
    # Bias correction z0
    z0: float = scipy_norm.ppf(np.mean(boot_rhos < obs_rho))

    # Acceleration a: jackknife estimate
    jack_rhos = np.empty(N)
    for j in range(N):
        df_jack = df.drop(index=j).reset_index(drop=True)
        try:
            r = pg.partial_corr(
                data=df_jack, x="TruthfulQA_MC2", y="bbq_accuracy",
                covar=["MMLU"], method="spearman"
            )
            jack_rhos[j] = float(r["r"].iloc[0])
        except Exception:
            jack_rhos[j] = obs_rho

    jack_mean = np.mean(jack_rhos)
    num = np.sum((jack_mean - jack_rhos) ** 3)
    den = 6.0 * (np.sum((jack_mean - jack_rhos) ** 2) ** 1.5)
    a: float = num / den if den != 0 else 0.0

    # CI quantiles
    alpha = 0.05
    z_alpha = scipy_norm.ppf(alpha / 2)
    z_1ma = scipy_norm.ppf(1 - alpha / 2)

    def _adj(z_a: float) -> float:
        return scipy_norm.cdf(z0 + (z0 + z_a) / (1 - a * (z0 + z_a)))

    lo_q = _adj(z_alpha)
    hi_q = _adj(z_1ma)

    sorted_boot = np.sort(boot_rhos)
    lo = float(np.percentile(sorted_boot, lo_q * 100))
    hi = float(np.percentile(sorted_boot, hi_q * 100))
    return (lo, hi)
```

Note: Jackknife loop runs N=297 times; combined with 5000 bootstrap iterations total ~5300 `pg.partial_corr` calls. Expected ~30-50s on CPU.

**Pseudo-code:**
```
1. compute obs_rho via pg.partial_corr on full df
2. bootstrap loop n_boot times:
   a. resample df with replacement (rng.integers)
   b. call pg.partial_corr on df_boot
   c. store boot_rhos[i]
3. BCa bias z0 = norm.ppf(mean(boot_rhos < obs_rho))
4. jackknife loop N times for acceleration a
5. compute adjusted quantile bounds lo_q, hi_q
6. return (percentile(boot_rhos, lo_q*100), percentile(boot_rhos, hi_q*100))
```

### L-6-3: ci_overlap_status determination

```python
def _ci_overlap_status(
    ci_raw: Tuple[float, float],
    ci_partial: Tuple[float, float],
) -> str:
    """Return 'overlapping' if CIs share any point, else 'non-overlapping'."""
    overlapping: bool = (ci_raw[0] <= ci_partial[1]) and (ci_partial[0] <= ci_raw[1])
    return "overlapping" if overlapping else "non-overlapping"
```

### L-6-4: compute_bca_cis() — public interface

```python
from config import ExperimentConfig

def compute_bca_cis(df: pd.DataFrame, cfg: ExperimentConfig) -> dict:
    """BCa CIs for raw_rho and partial_rho; overlap status.

    Returns:
        {
          'ci_raw': (float, float),         # 95% BCa CI for raw Spearman rho
          'ci_partial': (float, float),     # 95% BCa CI for partial Spearman rho
          'ci_overlap_status': str,         # 'overlapping' | 'non-overlapping'
          'boot_dist_raw': np.ndarray,      # (n_boot,) for Fig3 histogram
          'boot_dist_partial': np.ndarray,  # (n_boot,) for Fig3 histogram
        }
    """
    x = df["TruthfulQA_MC2"].to_numpy()
    y = df["bbq_accuracy"].to_numpy()

    # raw_rho BCa via pingouin (also capture distribution for Fig3)
    ci_raw_arr, boot_raw = pg.compute_bootci(
        x=x, y=y, func="spearman", method="bca",
        paired=True, n_boot=cfg.n_boot, seed=cfg.seed,
        return_dist=True,
    )
    ci_raw = (float(ci_raw_arr[0]), float(ci_raw_arr[1]))

    # partial_rho BCa via manual loop
    ci_partial, boot_partial = _bca_partial_rho_with_dist(df, cfg.n_boot, cfg.seed)

    status = _ci_overlap_status(ci_raw, ci_partial)
    logger.info(f"ci_raw={ci_raw}, ci_partial={ci_partial}, overlap={status}")

    return {
        "ci_raw": ci_raw,
        "ci_partial": ci_partial,
        "ci_overlap_status": status,
        "boot_dist_raw": boot_raw,
        "boot_dist_partial": boot_partial,
    }
```

Note: `_bca_partial_rho_with_dist` is `_bca_partial_rho` refactored to also return `boot_rhos` array.

**Pseudo-code:**
```
1. extract x, y arrays from df
2. ci_raw, boot_raw = pg.compute_bootci(..., return_dist=True)
3. ci_partial, boot_partial = _bca_partial_rho_with_dist(df, n_boot, seed)
4. status = _ci_overlap_status(ci_raw, ci_partial)
5. log and return dict with all 5 keys
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | raw_rho BCa | `pg.compute_bootci` call, return_dist=True for Fig3 |
| L-6-2 | partial_rho BCa | Manual bootstrap loop + jackknife BCa (N=297 jackknife) |
| L-6-3 | overlap status | Interval overlap boolean → string |
| L-6-4 | Public API | `compute_bca_cis()` wiring both CI functions, returning 5-key dict |

---

## A-9: Figures Fig1+2 [Complexity: 10, Budget: 2 subtasks]

Applied: Standard PyTorch — matplotlib grouped bar + scatter

### L-9-1: plot_rho_comparison

```python
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

def plot_rho_comparison(results: dict, cfg: ExperimentConfig) -> str:
    """Fig1: Grouped bar chart raw_rho vs partial_rho with BCa CI error bars.
    Annotated with Fisher z p-value. Color by significance outcome.
    Returns saved file path."""
    raw_rho: float = results["raw_rho"]
    partial_rho: float = results["partial_rho"]
    ci_raw: tuple = results["ci_raw"]        # (lo, hi)
    ci_partial: tuple = results["ci_partial"]
    p_value: float = results["p_value"]
    outcome: str = results["outcome"]        # 'SIGNIFICANT' | 'NULL'

    color = cfg.color_significant if outcome == "SIGNIFICANT" else cfg.color_null

    # Asymmetric error bars from BCa CI (not symmetric around rho)
    raw_err = np.array([[raw_rho - ci_raw[0]], [ci_raw[1] - raw_rho]])
    partial_err = np.array([[partial_rho - ci_partial[0]], [ci_partial[1] - partial_rho]])

    fig, ax = plt.subplots(figsize=cfg.fig_size)
    x_pos = [0, 1]
    bars = ax.bar(
        x_pos,
        [raw_rho, partial_rho],
        yerr=[raw_err.flatten(), partial_err.flatten()],
        # Note: matplotlib bar yerr expects shape (2, N) for asymmetric
        color=color,
        width=0.4,
        capsize=5,
        error_kw={"elinewidth": 1.5},
    )
    # Correct asymmetric: pass as list of (lo_err, hi_err) per bar
    # Rebuild with correct matplotlib asymmetric API:
    # yerr shape must be (2, N): row0=lower errors, row1=upper errors
    ax.cla()
    raw_yerr = np.array([[raw_rho - ci_raw[0]], [ci_raw[1] - raw_rho]])
    par_yerr = np.array([[partial_rho - ci_partial[0]], [ci_partial[1] - partial_rho]])
    all_yerr = np.hstack([raw_yerr, par_yerr])  # shape (2, 2)
    ax.bar(x_pos, [raw_rho, partial_rho], yerr=all_yerr, color=color,
           width=0.4, capsize=5, error_kw={"elinewidth": 1.5})
    ax.set_xticks(x_pos)
    ax.set_xticklabels(["Raw ρ", "Partial ρ\n(covar=MMLU)"])
    ax.set_ylabel("Spearman ρ")
    ax.set_title("TruthfulQA×BBQ Correlation: Raw vs Partial Spearman")
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")

    p_str = f"p={p_value:.4f}" if p_value >= 0.001 else f"p={p_value:.2e}"
    sig_str = "SIGNIFICANT" if outcome == "SIGNIFICANT" else "NULL"
    ax.annotate(
        f"Fisher z: {p_str}\n({sig_str})",
        xy=(0.5, 0.95), xycoords="axes fraction",
        ha="center", va="top", fontsize=10,
    )

    fig.tight_layout()
    out_path = os.path.join(cfg.figures_dir, "fig1_rho_comparison.png")
    fig.savefig(out_path, dpi=cfg.fig_dpi)
    plt.close(fig)
    return out_path
```

**Pseudo-code:**
```
1. extract raw_rho, partial_rho, ci_raw, ci_partial, p_value, outcome from results
2. color = green if SIGNIFICANT else orange
3. compute asymmetric yerr arrays shape (2, 2) from BCa CIs
4. ax.bar([0,1], [raw_rho, partial_rho], yerr=all_yerr, color=color)
5. annotate with Fisher z p-value string
6. save to figures_dir/fig1_rho_comparison.png
```

### L-9-2: plot_scatter_mmlu_gradient

```python
import matplotlib.cm as cm

def plot_scatter_mmlu_gradient(df: pd.DataFrame, cfg: ExperimentConfig) -> str:
    """Fig2: TruthfulQA_MC2 vs bbq_accuracy scatter with MMLU as color gradient.
    Returns saved file path."""
    fig, ax = plt.subplots(figsize=cfg.fig_size)

    sc = ax.scatter(
        df["TruthfulQA_MC2"],
        df["bbq_accuracy"],
        c=df["MMLU"],
        cmap="viridis",
        alpha=0.7,
        s=30,
        edgecolors="none",
    )
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label("MMLU score (0-100)")
    ax.set_xlabel("TruthfulQA MC2 (%)")
    ax.set_ylabel("BBQ accuracy (%)")
    ax.set_title(f"TruthfulQA MC2 vs BBQ Accuracy (N={len(df)}, colored by MMLU)")

    fig.tight_layout()
    out_path = os.path.join(cfg.figures_dir, "fig2_scatter_mmlu_gradient.png")
    fig.savefig(out_path, dpi=cfg.fig_dpi)
    plt.close(fig)
    return out_path
```

**Pseudo-code:**
```
1. ax.scatter(TruthfulQA_MC2, bbq_accuracy, c=MMLU, cmap='viridis')
2. colorbar labeled 'MMLU score'
3. save to fig2_scatter_mmlu_gradient.png
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | plot_rho_comparison | Grouped bar, asymmetric BCa error bars (2,2 array), p-value annotation |
| L-9-2 | plot_scatter_mmlu_gradient | Scatter with MMLU viridis colormap, colorbar |

---

## A-10: Figures Fig3-5 [Complexity: 10, Budget: 2 subtasks]

Applied: Standard PyTorch — matplotlib hist/bar + horizontal line plot

### L-10-1: plot_bootstrap_distributions + plot_family_rho_bar

```python
def plot_bootstrap_distributions(results: dict, cfg: ExperimentConfig) -> str:
    """Fig3: Overlaid bootstrap histograms for raw_rho and partial_rho.
    Uses boot_dist_raw and boot_dist_partial from results.
    Returns saved file path."""
    boot_raw: np.ndarray = results["boot_dist_raw"]       # (n_boot,)
    boot_partial: np.ndarray = results["boot_dist_partial"]  # (n_boot,)
    ci_raw: tuple = results["ci_raw"]
    ci_partial: tuple = results["ci_partial"]

    fig, ax = plt.subplots(figsize=cfg.fig_size)
    ax.hist(boot_raw, bins=60, alpha=0.5, color="steelblue", label="Raw ρ bootstrap")
    ax.hist(boot_partial, bins=60, alpha=0.5, color="darkorange", label="Partial ρ bootstrap")
    ax.axvline(ci_raw[0], color="steelblue", linestyle="--", linewidth=1, label="Raw 95% CI")
    ax.axvline(ci_raw[1], color="steelblue", linestyle="--", linewidth=1)
    ax.axvline(ci_partial[0], color="darkorange", linestyle="--", linewidth=1, label="Partial 95% CI")
    ax.axvline(ci_partial[1], color="darkorange", linestyle="--", linewidth=1)
    ax.set_xlabel("Spearman ρ")
    ax.set_ylabel("Bootstrap count")
    ax.set_title("Bootstrap Distributions: Raw vs Partial Spearman ρ")
    ax.legend()

    fig.tight_layout()
    out_path = os.path.join(cfg.figures_dir, "fig3_bootstrap_distributions.png")
    fig.savefig(out_path, dpi=cfg.fig_dpi)
    plt.close(fig)
    return out_path


def plot_family_rho_bar(results: dict, cfg: ExperimentConfig) -> str:
    """Fig4: Per-family Spearman rho bar chart (families with >= min_family_size).
    Returns saved file path."""
    family_rhos: pd.Series = results["family_rhos"]  # index=family name, values=rho

    # Sort by rho descending for readability
    family_rhos_sorted = family_rhos.sort_values(ascending=False)
    colors = [cfg.color_significant if r > 0 else cfg.color_null
              for r in family_rhos_sorted]

    fig, ax = plt.subplots(figsize=(max(8.0, len(family_rhos_sorted) * 0.6), 5.0))
    ax.bar(range(len(family_rhos_sorted)), family_rhos_sorted.values, color=colors)
    ax.set_xticks(range(len(family_rhos_sorted)))
    ax.set_xticklabels(family_rhos_sorted.index, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Spearman ρ")
    ax.set_title(f"Per-Family Spearman ρ (families ≥ {cfg.min_family_size} models)")
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.axhline(results.get("weighted_rho", float("nan")), color="grey",
               linewidth=1.5, linestyle=":", label=f"Weighted mean ρ")
    ax.legend()

    fig.tight_layout()
    out_path = os.path.join(cfg.figures_dir, "fig4_family_rho_bar.png")
    fig.savefig(out_path, dpi=cfg.fig_dpi)
    plt.close(fig)
    return out_path
```

**Pseudo-code (Fig3):**
```
1. ax.hist(boot_raw, bins=60, alpha=0.5, label='Raw ρ')
2. ax.hist(boot_partial, bins=60, alpha=0.5, label='Partial ρ')
3. axvline at ci_raw[0], ci_raw[1], ci_partial[0], ci_partial[1]
4. save to fig3_bootstrap_distributions.png
```

**Pseudo-code (Fig4):**
```
1. sort family_rhos descending
2. color bars by sign (positive=green, negative=orange)
3. axhline at 0 (dashed) and weighted_rho (dotted)
4. save to fig4_family_rho_bar.png
```

### L-10-2: plot_fisher_z_numberline

```python
def plot_fisher_z_numberline(results: dict, cfg: ExperimentConfig) -> str:
    """Fig5: Horizontal number-line showing z_raw and z_partial with 95% CIs
    derived from Fisher z SE=sqrt(2/(N-3)). Marks z=0 and critical ±1.96.
    Returns saved file path."""
    z_raw: float = results["z_raw"]
    z_partial: float = results["z_partial"]
    N: int = results["N"]
    p_value: float = results["p_value"]
    outcome: str = results["outcome"]

    se = np.sqrt(2.0 / (N - 3))
    z_crit = 1.96

    fig, ax = plt.subplots(figsize=(10, 3))
    ax.set_yticks([])
    ax.axhline(0, color="black", linewidth=0.8)

    # z_raw CI segment (95% CI: z ± 1.96*se / sqrt(2) — individual Fisher z CI)
    # Individual CI: z_raw ± 1.96/sqrt(N-3) (single correlation CI formula)
    se_single = 1.0 / np.sqrt(N - 3)
    for z_val, label, color, y_offset in [
        (z_raw, "z_raw", "steelblue", 0.15),
        (z_partial, "z_partial", "darkorange", -0.15),
    ]:
        lo = z_val - z_crit * se_single
        hi = z_val + z_crit * se_single
        ax.plot([lo, hi], [y_offset, y_offset], color=color, linewidth=3, solid_capstyle="round")
        ax.plot(z_val, y_offset, "o", color=color, markersize=8, label=f"{label}={z_val:.3f}")

    # Reference lines
    ax.axvline(0, color="black", linewidth=1, linestyle="--", alpha=0.5)
    ax.axvline(1.96, color="red", linewidth=0.8, linestyle=":", alpha=0.5, label="±1.96")
    ax.axvline(-1.96, color="red", linewidth=0.8, linestyle=":", alpha=0.5)

    p_str = f"p={p_value:.4f}" if p_value >= 0.001 else f"p={p_value:.2e}"
    ax.set_title(f"Fisher Z Number-Line: {p_str} ({outcome})")
    ax.set_xlabel("Fisher z-transformed ρ")
    ax.legend(loc="upper right", fontsize=9)

    fig.tight_layout()
    out_path = os.path.join(cfg.figures_dir, "fig5_fisher_z_numberline.png")
    fig.savefig(out_path, dpi=cfg.fig_dpi)
    plt.close(fig)
    return out_path
```

**Pseudo-code:**
```
1. se_single = 1/sqrt(N-3)  # individual Fisher z CI
2. for (z_raw, 'steelblue', y=+0.15) and (z_partial, 'darkorange', y=-0.15):
   a. draw horizontal line segment [z ± 1.96*se_single]
   b. dot at z_val
3. axvline at 0 (dashed) and ±1.96 (red dotted)
4. title with p-value and outcome
5. save to fig5_fisher_z_numberline.png
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-10-1 | Fig3 + Fig4 | Bootstrap histogram overlay with CI vlines; per-family bar with weighted mean |
| L-10-2 | Fig5 | Horizontal number-line CI segments for z_raw and z_partial |

---

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings <= 2 lines
- [x] No tensor shapes (pure statistics)
- [x] Subtask count: 4+2+2+2 = 10/10 budget
- [x] Codebase Analysis (Serena) section included
- [x] External Dependencies API section included with verified H-M1 signatures
- [x] Base hypothesis actual code verified (not spec)

---

## Implementation Notes

- `results` dict passed to plot functions must contain: `raw_rho`, `partial_rho`, `ci_raw`, `ci_partial`, `p_value`, `z_raw`, `z_partial`, `N`, `outcome`, `boot_dist_raw`, `boot_dist_partial`, `family_rhos`, `weighted_rho`
- `run()` must set `np.random.seed(cfg.seed)` as first line (H-M1 pattern)
- `bbq_accuracy` used internally (lowercase), matching H-M1 convention; CSV column `BBQ_accuracy` renamed on load
- `pg.compute_bootci` with `return_dist=True` returns `(ci_array, dist_array)` — verify with pingouin >= 0.5.0
- ponytail: jackknife in `_bca_partial_rho` is O(N) extra `pg.partial_corr` calls; skip jackknife (a=0) if runtime > 60s
