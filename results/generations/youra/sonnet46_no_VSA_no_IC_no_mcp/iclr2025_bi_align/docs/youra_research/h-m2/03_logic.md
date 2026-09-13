# Logic: H-M2
# Calibration-Alignment Divergence Gap Verification

**Hypothesis ID:** H-M2
**Type:** MECHANISM (PoC — INCREMENTAL from H-M1)
**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr

Applied: Statistical pipeline pattern — normalize → gap → gate → visualize wired through run_gap_analysis()
Applied: Guard-clause pattern — fast-fail on degenerate RM range before normalization

---

## Codebase Analysis (Serena)

**Project Type:** INCREMENTAL (base: H-M1)
**Status:** H-M1 code analyzed (manual read — Serena MCP unavailable in ablation mode)
**Analyzed Path:** `docs/youra_research/h-m1/code/src/`

**Findings:**
- `src/data/loader.py::load_dataset(csv_path, dataset_name) -> pd.DataFrame` — confirmed signature; reused pattern for h-m2 loader
- `src/analysis/trajectory.py::run_analysis(df, dataset_name)` — H-M1 orchestrator pattern; H-M2 mirrors with `run_gap_analysis(df, cfg)` 
- `src/visualization/plots.py` — matplotlib dual-axis and gap-curve patterns reused for H-M2 normalized gap plots
- `src/reporting/reporter.py::print_report, save_results` — same pattern replicated for H-M2

**External Dependencies API (Verified from H-M1 code):**
```python
# From h-m1/code/src/data/loader.py — confirmed signature pattern
def load_dataset(csv_path: str) -> pd.DataFrame:
    """
    Load CSV; validate REQUIRED_COLS = [kl_budget, rm_score, gold_preference];
    sort by kl_budget ascending; assert N >= 5 non-null paired rows.
    Raises: ValueError on validation failure.
    """
    ...
```

Note: H-M2 implements its own standalone `load_dataset` following the same pattern.

Note on "Tensor shapes": This experiment uses pandas DataFrames and numpy 1-D arrays. Shape notation `(N,)` means N=10 scalar observations — no neural network tensors.

---

## DataFrame Schemas

### Input DataFrame (h-m1 divergence curve CSV)

| Column | dtype | Range | Notes |
|--------|-------|-------|-------|
| `kl_budget` | float64 | 0.0 – 8.0 nats | x-axis, sorted ascending |
| `rm_score` | float64 | 0.12 – 2.08 | proxy reward (raw digitized units) |
| `gold_preference` | float64 | 0.38 – 0.63 | held-out human preference rate |
| `divergence_gap` | float64 | any | raw gap from H-M1 (not used in H-M2 computation) |

**Shape:** `(10, 4)` — N=10 KL levels

### Derived Arrays (shape: `(N,)` = `(10,)` each)

| Variable | dtype | Notes |
|----------|-------|-------|
| `kl` | float64 | `df["kl_budget"].values` |
| `rm` | float64 | `df["rm_score"].values` |
| `gold` | float64 | `df["gold_preference"].values` |
| `rm_norm` | float64 | min-max normalized to [0, 1] |
| `gap` | float64 | `rm_norm - gold`, range approx [-0.52, 0.62] |
| `high_kl_mask` | bool | `kl > median_kl`; True for KL ∈ {4,5,6,7,8} |
| `gap_high_kl` | float64 | `gap[high_kl_mask]`, shape (5,) |

---

## L-3-1: run_gap_analysis() [Parent: A-3, Complexity: 9]

Applied: Orchestrator pattern — chain normalize → gap → gate into unified result dict

### API Signature

```python
def run_gap_analysis(df: pd.DataFrame, high_kl_min_positive: int = 3) -> dict:
    """
    Full H-M2 gap analysis: normalize RM score, compute divergence gap, verify gate.

    Args:
        df:                    DataFrame with [kl_budget, rm_score, gold_preference],
                               sorted ascending by kl_budget. N=10.
        high_kl_min_positive:  Gate threshold — minimum count of high-KL gaps > 0.
                               Default 3 (from ExperimentConfig).

    Returns:
        {
            # Input arrays
            "kl":                np.ndarray,  # shape (10,)
            "rm":                np.ndarray,  # shape (10,)
            "gold":              np.ndarray,  # shape (10,)

            # Normalization
            "rm_norm":           np.ndarray,  # shape (10,) in [0, 1]
            "rm_min":            float,        # normalization parameter
            "rm_max":            float,        # normalization parameter

            # Gap
            "gap":               np.ndarray,  # shape (10,) = rm_norm - gold

            # High-KL subset
            "median_kl":         float,        # 3.75 nats
            "high_kl_mask":      np.ndarray,  # shape (10,) bool
            "gap_high_kl":       np.ndarray,  # shape (5,) — high-KL gap values

            # Gate metrics
            "n_positive_high_kl": int,          # count(gap_high_kl > 0)
            "rho_gap_kl":         float,         # Spearman ρ(kl, gap)
            "p_rho_gap":          float,         # p-value for rho
            "mean_gap_high_kl":   float,         # mean(gap_high_kl)
            "max_gap":            float,         # max(gap)
            "prop_positive":      float,         # mean(gap > 0)

            # Gate result
            "gate_pass":          bool,           # n_positive_high_kl >= 3 AND rho_gap_kl > 0
            "gate_reason":        str,            # human-readable explanation
        }
    """
```

### Algorithm

```python
import numpy as np
from scipy import stats

def normalize_rm(rm: np.ndarray) -> np.ndarray:
    rm_min, rm_max = rm.min(), rm.max()
    if rm_max <= rm_min:
        raise ValueError(f"Degenerate RM range: min={rm_min}, max={rm_max}")
    return (rm - rm_min) / (rm_max - rm_min)

def compute_gap(rm_norm: np.ndarray, gold: np.ndarray) -> np.ndarray:
    return rm_norm - gold

def run_gap_analysis(df, high_kl_min_positive=3):
    df = df.sort_values("kl_budget").reset_index(drop=True)
    kl   = df["kl_budget"].values       # shape (10,)
    rm   = df["rm_score"].values         # shape (10,)
    gold = df["gold_preference"].values  # shape (10,)

    # Step 1: Normalize RM to [0, 1]
    rm_min, rm_max = float(rm.min()), float(rm.max())
    rm_norm = normalize_rm(rm)           # shape (10,)

    # Step 2: Compute calibration-alignment divergence gap
    gap = compute_gap(rm_norm, gold)     # shape (10,)

    # Step 3: Identify high-KL subset
    median_kl    = float(np.median(kl))              # 3.75 nats
    high_kl_mask = kl > median_kl                    # shape (10,) bool
    gap_high_kl  = gap[high_kl_mask]                 # shape (5,)

    # Step 4: Gate metrics
    n_positive_high_kl = int(np.sum(gap_high_kl > 0))
    rho_gap_kl, p_rho_gap = stats.spearmanr(kl, gap)
    rho_gap_kl = float(rho_gap_kl)
    p_rho_gap  = float(p_rho_gap)
    mean_gap_high_kl = float(np.mean(gap_high_kl))
    max_gap          = float(np.max(gap))
    prop_positive    = float(np.mean(gap > 0))

    # Step 5: Gate decision
    gate_pass = (n_positive_high_kl >= high_kl_min_positive) and (rho_gap_kl > 0)

    if gate_pass:
        gate_reason = (
            f"PASS: n_positive_high_kl={n_positive_high_kl}/{len(gap_high_kl)} "
            f">= {high_kl_min_positive}; rho_gap_kl={rho_gap_kl:.3f} > 0"
        )
    elif n_positive_high_kl < high_kl_min_positive:
        gate_reason = (
            f"FAIL: only {n_positive_high_kl}/{len(gap_high_kl)} high-KL gaps > 0 "
            f"(need >= {high_kl_min_positive}); recheck normalization range"
        )
    else:
        gate_reason = (
            f"FAIL: rho_gap_kl={rho_gap_kl:.3f} <= 0; "
            f"gap does not grow with KL — check data loading order"
        )

    return {
        "kl": kl, "rm": rm, "gold": gold,
        "rm_norm": rm_norm, "rm_min": rm_min, "rm_max": rm_max,
        "gap": gap,
        "median_kl": median_kl, "high_kl_mask": high_kl_mask,
        "gap_high_kl": gap_high_kl,
        "n_positive_high_kl": n_positive_high_kl,
        "rho_gap_kl": rho_gap_kl, "p_rho_gap": p_rho_gap,
        "mean_gap_high_kl": mean_gap_high_kl,
        "max_gap": max_gap,
        "prop_positive": prop_positive,
        "gate_pass": gate_pass,
        "gate_reason": gate_reason,
    }
```

### Edge Cases

| Scenario | Behaviour |
|----------|-----------|
| Degenerate RM (all equal) | `normalize_rm` raises `ValueError` before any computation |
| Gap non-monotone | `rho_gap_kl <= 0` → gate_pass=False, reason explains |
| All high-KL gaps negative | `n_positive_high_kl=0` → gate_pass=False, suggests reframing |
| N < 5 | Caught by loader validation before reaching run_gap_analysis |

---

## L-4-1: plot_gap_curve() and plot_dual_line() [Parent: A-4, Complexity: 10]

Applied: Line plot with horizontal reference line and shaded region pattern
Applied: Dual-line same-axis overlay pattern — both curves in [0,1]

### plot_gap_curve() API

```python
def plot_gap_curve(
    kl: np.ndarray,
    gap: np.ndarray,
    high_kl_mask: np.ndarray,
    max_gap: float,
    figs_dir: str,
    dpi: int = 150,
) -> str:
    """
    Line chart of normalized gap = RM_norm - gold_preference vs KL budget.
    Zero reference line. Shaded positive region (where gap > 0).
    max_gap annotated. High-KL region boundary marked.
    Returns: absolute path to saved PNG.
    """
```

### plot_gap_curve() Algorithm

```python
import matplotlib.pyplot as plt
from pathlib import Path

def plot_gap_curve(kl, gap, high_kl_mask, max_gap, figs_dir, dpi=150):
    fig, ax = plt.subplots(figsize=(9, 5))

    ax.plot(kl, gap, marker="o", color="royalblue", linewidth=2,
            label="Divergence Gap (RM_norm − gold)")
    ax.axhline(y=0, color="black", linestyle="--", alpha=0.6, label="Zero line")

    # Shade positive region
    ax.fill_between(kl, gap, 0, where=(gap > 0),
                    alpha=0.15, color="royalblue", label="Positive gap region")

    # Annotate max_gap
    max_idx = int(gap.argmax())
    ax.annotate(
        f"max_gap={max_gap:.3f}",
        xy=(kl[max_idx], gap[max_idx]),
        xytext=(10, -15), textcoords="offset points",
        fontsize=9, arrowprops=dict(arrowstyle="->", color="gray")
    )

    # Mark high-KL boundary
    if high_kl_mask.any():
        boundary_kl = kl[high_kl_mask].min()
        ax.axvline(x=boundary_kl, color="orange", linestyle=":",
                   alpha=0.7, label=f"High-KL boundary (KL>{boundary_kl:.2f})")

    ax.set_xlabel("KL Budget (nats)")
    ax.set_ylabel("gap = RM_norm − gold_preference")
    ax.set_title("H-M2: Calibration-Alignment Divergence Gap vs KL Budget")
    ax.legend(fontsize=9)
    fig.tight_layout()

    Path(figs_dir).mkdir(parents=True, exist_ok=True)
    out_path = str(Path(figs_dir) / "gap_curve.png")
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)
    return out_path
```

### plot_dual_line() API

```python
def plot_dual_line(
    kl: np.ndarray,
    rm_norm: np.ndarray,
    gold: np.ndarray,
    figs_dir: str,
    dpi: int = 150,
) -> str:
    """
    Dual-line plot: RM_norm and gold_preference on same [0,1] y-axis vs KL.
    Crossover point annotated where rm_norm first exceeds gold.
    Returns: absolute path to saved PNG.
    """
```

### plot_dual_line() Algorithm

```python
def plot_dual_line(kl, rm_norm, gold, figs_dir, dpi=150):
    fig, ax = plt.subplots(figsize=(9, 5))

    ax.plot(kl, rm_norm, marker="o", color="steelblue", linewidth=2,
            label="RM Score (normalized)")
    ax.plot(kl, gold, marker="s", linestyle="--", color="crimson", linewidth=2,
            label="Gold Preference Rate")

    # Annotate crossover (first point where rm_norm > gold)
    crossover = (rm_norm > gold)
    if crossover.any():
        cx_idx = int(crossover.argmax())
        ax.annotate(
            f"Crossover\nKL≈{kl[cx_idx]:.1f}",
            xy=(kl[cx_idx], rm_norm[cx_idx]),
            xytext=(10, 15), textcoords="offset points",
            fontsize=8, arrowprops=dict(arrowstyle="->", color="gray")
        )

    ax.set_xlabel("KL Budget (nats)")
    ax.set_ylabel("Value [0, 1]")
    ax.set_ylim(-0.05, 1.05)
    ax.set_title("H-M2: RM_norm vs Gold Preference — Same [0,1] Scale")
    ax.legend(fontsize=9)
    fig.tight_layout()

    Path(figs_dir).mkdir(parents=True, exist_ok=True)
    out_path = str(Path(figs_dir) / "dual_line.png")
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)
    return out_path
```

---

## L-4-2: plot_gap_scatter() and plot_gate_metrics() [Parent: A-4, Complexity: 10]

Applied: Scatter with Spearman annotation pattern
Applied: Bar chart with threshold lines pattern (mirrors H-M1 gate_metrics plot)

### plot_gap_scatter() API

```python
def plot_gap_scatter(
    kl: np.ndarray,
    gap: np.ndarray,
    rho: float,
    high_kl_mask: np.ndarray,
    figs_dir: str,
    dpi: int = 150,
) -> str:
    """
    Scatter of gap vs KL budget. High-KL points marked distinctly.
    Spearman ρ annotated in title. OLS trend line overlay.
    Returns: absolute path to saved PNG.
    """
```

### plot_gap_scatter() Algorithm

```python
from scipy import stats as _stats

def plot_gap_scatter(kl, gap, rho, high_kl_mask, figs_dir, dpi=150):
    fig, ax = plt.subplots(figsize=(8, 5))

    # Low-KL points
    ax.scatter(kl[~high_kl_mask], gap[~high_kl_mask],
               color="steelblue", s=70, zorder=5, label="Low-KL levels")
    # High-KL points (distinct)
    ax.scatter(kl[high_kl_mask], gap[high_kl_mask],
               color="darkorange", s=90, marker="D", zorder=6, label="High-KL levels")

    # OLS trend
    slope, intercept, *_ = _stats.linregress(kl, gap)
    kl_line = np.linspace(kl.min(), kl.max(), 100)
    ax.plot(kl_line, slope * kl_line + intercept,
            color="navy", linestyle="--", alpha=0.5, label="OLS trend")
    ax.axhline(y=0, color="black", linestyle=":", alpha=0.4)

    ax.set_xlabel("KL Budget (nats)")
    ax.set_ylabel("gap = RM_norm − gold_preference")
    ax.set_title(f"H-M2: Gap Growth vs KL Budget  |  Spearman ρ = {rho:.3f}")
    ax.legend(fontsize=9)
    fig.tight_layout()

    Path(figs_dir).mkdir(parents=True, exist_ok=True)
    out_path = str(Path(figs_dir) / "gap_scatter.png")
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)
    return out_path
```

### plot_gate_metrics() API

```python
def plot_gate_metrics(results: dict, figs_dir: str, dpi: int = 150) -> str:
    """
    Bar chart comparing gate metrics to their thresholds:
    - n_positive_high_kl (value) vs threshold 3
    - rho_gap_kl (value) vs threshold 0
    - prop_positive (value) vs threshold 0.5
    Green bar = PASS, red bar = FAIL.
    Returns: absolute path to saved PNG.
    """
```

### plot_gate_metrics() Algorithm

```python
def plot_gate_metrics(results, figs_dir, dpi=150):
    metrics = {
        "n_positive\nhigh_kl": (results["n_positive_high_kl"], 3,
                                 results["n_positive_high_kl"] >= 3),
        "ρ(KL,gap)":           (results["rho_gap_kl"], 0.0,
                                 results["rho_gap_kl"] > 0),
        "prop_positive":        (results["prop_positive"], 0.5,
                                 results["prop_positive"] > 0.5),
    }

    fig, ax = plt.subplots(figsize=(8, 5))
    x = list(range(len(metrics)))
    colors = ["forestgreen" if v[2] else "tomato" for v in metrics.values()]
    ax.bar(x, [v[0] for v in metrics.values()], color=colors, alpha=0.75, width=0.5)

    for i, (label, (val, threshold, passed)) in enumerate(metrics.items()):
        ax.hlines(y=threshold, xmin=i - 0.3, xmax=i + 0.3,
                  colors="black", linestyles="--", linewidth=1.5)
        ax.text(i, threshold + 0.03, f"threshold={threshold}",
                ha="center", fontsize=8)
        ax.text(i, val + 0.05, f"{val:.3f}" if isinstance(val, float) else str(val),
                ha="center", fontsize=9, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(list(metrics.keys()))
    ax.set_ylabel("Metric Value")
    gate = "PASS ✓" if results["gate_pass"] else "FAIL ✗"
    ax.set_title(f"H-M2 Gate Metrics — {gate}")
    fig.tight_layout()

    Path(figs_dir).mkdir(parents=True, exist_ok=True)
    out_path = str(Path(figs_dir) / "gate_metrics.png")
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)
    return out_path
```

---

## External Dependencies API (H-M1 Verified)

```python
# H-M1 data output consumed by H-M2 — CSV schema confirmed
# File: h-m1/results/h_m1_divergence_curve.csv
# Columns: kl_budget (float), rm_score (float), gold_preference (float), divergence_gap (float)
# N=10 rows, KL range [0, 8] nats; no NaN values (validated in H-M1 Phase 4)

# H-M2 standalone loader (mirrors H-M1 pattern):
def load_dataset(csv_path: str) -> pd.DataFrame:
    """
    Load h-m1 divergence curve CSV; validate columns; sort by kl_budget; assert N >= 5.
    Raises: FileNotFoundError if path missing; ValueError if columns absent or N < 5.
    """
    ...
```

---

## Subtask Summary [3/3 used from logic budget]

| ID | Parent Epic | Complexity | Description |
|----|-------------|-----------|-------------|
| L-3-1 | A-3 (9) | Medium | run_gap_analysis() — normalize, gap, gate orchestrator |
| L-4-1 | A-4 (10) | Medium | plot_gap_curve() + plot_dual_line() |
| L-4-2 | A-4 (10) | Medium | plot_gap_scatter() + plot_gate_metrics() |
