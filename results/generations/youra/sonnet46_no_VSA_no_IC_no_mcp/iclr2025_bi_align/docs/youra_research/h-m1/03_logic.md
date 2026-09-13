# Logic: H-M1
# RLHF Proxy-Gold Divergence Mechanism Verification

**Hypothesis ID:** H-M1
**Type:** MECHANISM (PoC — INCREMENTAL from H-E1)
**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr

Applied: Statistical pipeline pattern — three independent tests wired through run_analysis() orchestrator
Applied: Guard-clause pattern — fast-fail on structural errors before statistical computation

---

## Codebase Analysis (Serena)

**Project Type:** INCREMENTAL (base: H-E1)
**Status:** H-E1 code analyzed
**Analyzed Path:** `docs/youra_research/h-e1/code/src/`

**Findings:**
- `src/data/loader.py::load_dataset(csv_path, dataset_name) -> pd.DataFrame` — exact signature confirmed; reused as-is
- H-E1's `verify_signal_coexistence()` NOT reused — H-M1 requires different statistical tests (Spearman ρ, peak detection, divergence)
- H-E1 plot patterns (twin y-axis) informing H-M1 `plot_trajectory_dual_axis()` structure

**External Dependencies API (Verified):**
```python
# From h-e1/code/src/data/loader.py — CONFIRMED SIGNATURE
def load_dataset(csv_path: str, dataset_name: str) -> pd.DataFrame:
    """Raises ValueError if required columns missing or < 5 non-null paired rows."""
    ...
```

Note: Archon MCP unavailable (ablation mode). Logic grounded from 02c_experiment_brief.md and 03_prd.md.

Note on "Tensor shapes": This experiment uses pandas DataFrames and numpy 1-D arrays. Shape notation `(N,)` means `N` scalar observations — no neural network tensors.

---

## DataFrame Schemas

### Input DataFrame (both datasets)

| Column | dtype | Range | Notes |
|--------|-------|-------|-------|
| `kl_budget` | float64 | 0.0 – ~10.0 nats | x-axis, strictly increasing after sort |
| `rm_score` | float64 | any | proxy reward (normalized) |
| `gold_preference` | float64 | 0.0 – 1.0 | held-out human preference rate |

**Shape:** `(N, 3)` where N ≥ 5

### Derived Arrays (shape: `(N,)` each)

| Variable | dtype | Notes |
|----------|-------|-------|
| `kl` | float64 | `df["kl_budget"].values` |
| `rm` | float64 | `df["rm_score"].values` |
| `gold` | float64 | `df["gold_preference"].values` |
| `divergence_curve` | float64 | `rm - gold` elementwise |

---

## L-E4-1: run_rm_monotonicity_test() [Parent: E4, Complexity: 16, Budget: 4]

Applied: Hypothesis test pattern — compute statistic, check threshold, return structured result

### API Signature

```python
def run_rm_monotonicity_test(kl: np.ndarray, rm: np.ndarray) -> dict:
    """
    Test whether RM score increases monotonically with KL budget.

    Args:
        kl: KL budget values, shape (N,), sorted ascending
        rm: RM score values, shape (N,)

    Returns:
        {
            "rho_rm_kl":     float,  # Spearman rank correlation [-1, 1]
            "p_rho":         float,  # two-tailed p-value
            "monotone_pass": bool,   # rho > 0.8 AND p < 0.05
            "reason":        str,    # human-readable explanation
        }
    """
```

### Algorithm

```python
from scipy import stats
import numpy as np

RHO_THRESHOLD = 0.8   # from ExperimentConfig.monotonicity_rho_threshold
P_THRESHOLD   = 0.05  # standard significance level

def run_rm_monotonicity_test(kl, rm):
    if len(kl) < 3:
        return {
            "rho_rm_kl": float("nan"), "p_rho": float("nan"),
            "monotone_pass": False,
            "reason": f"Insufficient data: N={len(kl)} (need ≥ 3)"
        }

    rho, p_rho = stats.spearmanr(kl, rm)

    monotone_pass = (rho > RHO_THRESHOLD) and (p_rho < P_THRESHOLD)

    if monotone_pass:
        reason = f"PASS: ρ={rho:.3f} > {RHO_THRESHOLD}, p={p_rho:.4f} < {P_THRESHOLD}"
    elif rho <= RHO_THRESHOLD:
        reason = f"FAIL: ρ={rho:.3f} ≤ {RHO_THRESHOLD} (re-digitize Figure 3)"
    else:
        reason = f"FAIL: p={p_rho:.4f} ≥ {P_THRESHOLD} (insufficient N; need more KL checkpoints)"

    return {
        "rho_rm_kl":     float(rho),
        "p_rho":         float(p_rho),
        "monotone_pass": monotone_pass,
        "reason":        reason,
    }
```

### Edge Cases

| Scenario | Behaviour |
|----------|-----------|
| N < 3 | Returns NaN rho, monotone_pass=False, reason explains |
| Constant rm values | scipy returns rho=NaN, p=NaN → guard with nan check → monotone_pass=False |
| Perfect monotone (N=5) | rho=1.0, small p → PASS |
| Non-monotone with noise | rho < 0.8 → FAIL with re-digitize suggestion |

---

## L-E4-2: detect_peak_reversal() [Parent: E4, Complexity: 16, Budget: 4]

Applied: Signal processing pattern — argmax peak detection with boundary validation

### API Signature

```python
def detect_peak_reversal(kl: np.ndarray, gold: np.ndarray) -> dict:
    """
    Detect peak in gold preference and confirm post-peak reversal.

    Args:
        kl:   KL budget values, shape (N,), sorted ascending
        gold: Gold preference values, shape (N,)

    Returns:
        {
            "peak_idx":          int,   # index of maximum gold preference
            "peak_kl":           float, # KL value at peak
            "reversal_confirmed":bool,  # gold[peak_idx] > gold[-1]
            "peak_kl_valid":     bool,  # peak_kl in [1.0, 9.0] (sanity)
            "reason":            str,
        }
    """
```

### Algorithm

```python
PEAK_KL_MIN = 1.0   # from ExperimentConfig.peak_kl_min
PEAK_KL_MAX = 9.0   # from ExperimentConfig.peak_kl_max

def detect_peak_reversal(kl, gold):
    if len(gold) < 3:
        return {
            "peak_idx": -1, "peak_kl": float("nan"),
            "reversal_confirmed": False, "peak_kl_valid": False,
            "reason": f"Insufficient data: N={len(gold)}"
        }

    # Peak detection
    peak_idx = int(np.argmax(gold))
    peak_kl  = float(kl[peak_idx])

    # Reversal check: gold at peak strictly greater than gold at final point
    reversal_confirmed = bool(gold[peak_idx] > gold[-1])

    # Sanity check: peak KL within expected range
    peak_kl_valid = PEAK_KL_MIN <= peak_kl <= PEAK_KL_MAX

    if reversal_confirmed and peak_kl_valid:
        reason = (f"PASS: peak at KL={peak_kl:.2f} nats (valid range [{PEAK_KL_MIN},{PEAK_KL_MAX}]), "
                  f"gold[peak]={gold[peak_idx]:.3f} > gold[final]={gold[-1]:.3f}")
    elif not reversal_confirmed:
        reason = (f"FAIL: no reversal — gold[peak]={gold[peak_idx]:.3f} ≤ gold[final]={gold[-1]:.3f}; "
                  f"re-digitize gold preference curve in Figure 3")
    else:
        reason = (f"WARNING: reversal confirmed but peak_kl={peak_kl:.2f} outside [{PEAK_KL_MIN},{PEAK_KL_MAX}]; "
                  f"possible digitization axis calibration error")

    return {
        "peak_idx":           peak_idx,
        "peak_kl":            peak_kl,
        "reversal_confirmed": reversal_confirmed,
        "peak_kl_valid":      peak_kl_valid,
        "reason":             reason,
    }
```

### Edge Cases

| Scenario | Behaviour |
|----------|-----------|
| Peak at last index | reversal_confirmed=False (gold[-1] == gold[peak_idx]) |
| Peak at first index | Valid if gold[0] > gold[-1] |
| Monotone increasing gold (no peak) | peak_idx = N-1 → reversal_confirmed=False |
| All-equal gold values | peak_idx=0, reversal_confirmed=False |
| Peak outside [1, 9] nats | peak_kl_valid=False, warning in reason |

---

## L-E4-3: compute_divergence() [Parent: E4, Complexity: 16, Budget: 4]

Applied: Elementwise subtraction — proxy minus gold at each KL level

### API Signature

```python
def compute_divergence(rm: np.ndarray, gold: np.ndarray) -> dict:
    """
    Compute proxy-gold divergence at each KL level.

    Args:
        rm:   RM score values, shape (N,)
        gold: Gold preference values, shape (N,)

    Returns:
        {
            "divergence_curve":    np.ndarray,  # shape (N,) = rm - gold
            "divergence_final":    float,        # divergence_curve[-1]
            "divergence_positive": bool,         # divergence_final > 0
            "divergence_max":      float,        # max of divergence_curve
            "reason":              str,
        }
    """
```

### Algorithm

```python
def compute_divergence(rm, gold):
    divergence_curve = rm - gold                    # shape: (N,)
    divergence_final = float(divergence_curve[-1])
    divergence_max   = float(divergence_curve.max())
    divergence_positive = divergence_final > 0.0

    if divergence_positive:
        reason = f"PASS: divergence_final={divergence_final:.3f} > 0 (RM exceeds gold at max KL)"
    else:
        reason = (f"WARNING: divergence_final={divergence_final:.3f} ≤ 0; "
                  f"unexpected pattern (gold ≥ RM at final KL)")

    return {
        "divergence_curve":    divergence_curve,
        "divergence_final":    divergence_final,
        "divergence_positive": divergence_positive,
        "divergence_max":      divergence_max,
        "reason":              reason,
    }
```

---

## L-E4-4: run_analysis() [Parent: E4, Complexity: 16, Budget: 4]

Applied: Orchestrator pattern — wire three independent tests into unified result dict

### API Signature

```python
def run_analysis(df: pd.DataFrame, dataset_name: str = "Coste2023") -> dict:
    """
    Orchestrate full H-M1 statistical analysis on a digitized dataset.

    Args:
        df:           DataFrame with [kl_budget, rm_score, gold_preference], sorted by kl_budget
        dataset_name: Label for reporting

    Returns:
        Merged result dict with all fields from sub-tests PLUS:
        {
            "dataset":      str,
            "n_kl_levels":  int,
            "baseline_rm":  float,  # rm at min(kl_budget)
            "baseline_gold":float,  # gold at min(kl_budget)
            "gate_pass":    bool,   # monotone_pass AND reversal_confirmed
        }
    """
```

### Algorithm

```python
def run_analysis(df, dataset_name="Coste2023"):
    df = df.sort_values("kl_budget").reset_index(drop=True)
    kl   = df["kl_budget"].values
    rm   = df["rm_score"].values
    gold = df["gold_preference"].values

    mono_result  = run_rm_monotonicity_test(kl, rm)
    peak_result  = detect_peak_reversal(kl, gold)
    div_result   = compute_divergence(rm, gold)

    gate_pass = mono_result["monotone_pass"] and peak_result["reversal_confirmed"]

    return {
        "dataset":       dataset_name,
        "n_kl_levels":   len(kl),
        "baseline_rm":   float(rm[0]),
        "baseline_gold": float(gold[0]),
        "gate_pass":     gate_pass,
        **mono_result,
        **{k: v for k, v in peak_result.items() if k != "reason"},
        "peak_reason":   peak_result["reason"],
        **{k: v for k, v in div_result.items() if k not in ("reason", "divergence_curve")},
        "divergence_curve": div_result["divergence_curve"],
        "mono_reason":   mono_result["reason"],
        "div_reason":    div_result["reason"],
    }
```

---

## L-E5-1: plot_trajectory_dual_axis() [Parent: E5, Complexity: 14, Budget: 4]

Applied: Dual y-axis matplotlib pattern with vertical peak marker — extends H-E1 plot_dual_axis()

### API Signature

```python
def plot_trajectory_dual_axis(
    df: pd.DataFrame,
    results: dict,
    out_dir: str,
    dpi: int = 150,
) -> str:
    """
    Dual-axis trajectory plot: RM (left, steelblue) + gold (right, crimson) vs KL.
    Vertical dashed line at peak_kl. Peak gold point annotated.

    Returns: absolute path to saved PNG.
    """
```

### Algorithm

```python
def plot_trajectory_dual_axis(df, results, out_dir, dpi=150):
    fig, ax1 = plt.subplots(figsize=(9, 5))

    # Left axis: RM score
    ax1.set_xlabel("KL Divergence (nats)")
    ax1.set_ylabel("RM Score (proxy)", color="steelblue")
    ax1.plot(df["kl_budget"], df["rm_score"],
             marker="o", color="steelblue", label="RM Score")
    ax1.tick_params(axis="y", labelcolor="steelblue")

    # Right axis: gold preference
    ax2 = ax1.twinx()
    ax2.set_ylabel("Gold Preference Rate", color="crimson")
    ax2.plot(df["kl_budget"], df["gold_preference"],
             marker="s", linestyle="--", color="crimson", label="Gold Preference")
    ax2.tick_params(axis="y", labelcolor="crimson")

    # Peak KL marker
    peak_kl = results["peak_kl"]
    ax1.axvline(x=peak_kl, color="gray", linestyle=":", alpha=0.7,
                label=f"Peak KL = {peak_kl:.1f} nats")

    # Combined legend + title
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=9)

    status = "PASS ✓" if results["gate_pass"] else "FAIL ✗"
    ax1.set_title(f"H-M1: Proxy-Gold Trajectory — Coste 2023 [{status}]")
    fig.tight_layout()

    out_path = Path(out_dir) / "trajectory_dual_axis.png"
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)
    return str(out_path)
```

---

## L-E5-2: plot_divergence_gap() [Parent: E5, Complexity: 14, Budget: 4]

Applied: Line plot with horizontal reference line pattern

### API Signature

```python
def plot_divergence_gap(
    kl: np.ndarray,
    divergence_curve: np.ndarray,
    out_dir: str,
    dpi: int = 150,
) -> str:
    """
    Plot divergence_curve (RM − gold) vs KL budget.
    Horizontal zero line as reference. Final value annotated.
    Returns: absolute path to saved PNG.
    """
```

### Algorithm

```python
def plot_divergence_gap(kl, divergence_curve, out_dir, dpi=150):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(kl, divergence_curve, marker="D", color="darkorange", linewidth=2,
            label="RM − Gold Preference")
    ax.axhline(y=0, color="black", linestyle="--", alpha=0.5, label="Zero line")
    ax.fill_between(kl, divergence_curve, 0,
                    where=(divergence_curve > 0), alpha=0.15, color="darkorange")
    ax.set_xlabel("KL Divergence (nats)")
    ax.set_ylabel("Divergence (RM Score − Gold Preference)")
    ax.set_title("H-M1: Proxy-Gold Divergence Gap vs KL Budget")
    ax.legend()
    # Annotate final value
    ax.annotate(f"Final: {divergence_curve[-1]:.3f}",
                xy=(kl[-1], divergence_curve[-1]),
                xytext=(-40, 10), textcoords="offset points",
                fontsize=9, arrowprops=dict(arrowstyle="->", color="gray"))
    fig.tight_layout()
    out_path = Path(out_dir) / "divergence_gap.png"
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)
    return str(out_path)
```

---

## L-E5-3: plot_spearman_scatter() [Parent: E5, Complexity: 14, Budget: 4]

Applied: Scatter plot with linear trend overlay pattern

### API Signature

```python
def plot_spearman_scatter(
    kl: np.ndarray,
    rm: np.ndarray,
    rho: float,
    p_rho: float,
    out_dir: str,
    dpi: int = 150,
) -> str:
    """
    Scatter: RM vs KL; linear trend line (OLS); ρ and p annotated.
    Returns: absolute path to saved PNG.
    """
```

### Algorithm

```python
from scipy import stats as _stats

def plot_spearman_scatter(kl, rm, rho, p_rho, out_dir, dpi=150):
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(kl, rm, color="steelblue", zorder=5, s=60, label="Observations")

    # OLS trend line for visual reference
    slope, intercept, *_ = _stats.linregress(kl, rm)
    kl_line = np.linspace(kl.min(), kl.max(), 100)
    ax.plot(kl_line, slope * kl_line + intercept,
            color="navy", linestyle="--", alpha=0.6, label="OLS trend")

    ax.set_xlabel("KL Divergence (nats)")
    ax.set_ylabel("RM Score")
    p_str = f"p={p_rho:.4f}" if p_rho >= 0.001 else "p<0.001"
    ax.set_title(f"H-M1: RM Score vs KL Budget\nSpearman ρ={rho:.3f}, {p_str}")
    ax.legend()
    fig.tight_layout()
    out_path = Path(out_dir) / "spearman_scatter.png"
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)
    return str(out_path)
```

---

## L-E5-4: plot_gao_overlay() and plot_gate_metrics() [Parent: E5, Complexity: 14, Budget: 4]

Applied: Multi-panel subplot pattern; bar chart with threshold lines pattern

### plot_gao_overlay() Signature

```python
def plot_gao_overlay(
    gao_df: pd.DataFrame,
    out_dir: str,
    dpi: int = 150,
) -> str:
    """
    Separate panel dual-axis plot for Gao 2023 data. Labeled "Preliminary Check".
    Returns: absolute path to saved PNG.
    """
```

### plot_gate_metrics() Signature

```python
def plot_gate_metrics(results: dict, out_dir: str, dpi: int = 150) -> str:
    """
    Bar chart of gate metrics vs thresholds:
    - rho_rm_kl vs 0.8
    - reversal_confirmed (0 or 1) vs 1 threshold
    - divergence_final vs 0 threshold
    Returns: absolute path to saved PNG.
    """
```

### plot_gate_metrics() Algorithm

```python
def plot_gate_metrics(results, out_dir, dpi=150):
    metrics = {
        "ρ(KL,RM)": (results["rho_rm_kl"], 0.8, results["monotone_pass"]),
        "Reversal\nConfirmed": (float(results["reversal_confirmed"]), 1.0, results["reversal_confirmed"]),
        "Divergence\nFinal": (results["divergence_final"], 0.0, results["divergence_positive"]),
    }

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["forestgreen" if v[2] else "tomato" for v in metrics.values()]
    x = list(range(len(metrics)))
    bars = ax.bar(x, [v[0] for v in metrics.values()], color=colors, alpha=0.7, width=0.5)

    # Threshold lines
    for i, (label, (val, threshold, passed)) in enumerate(metrics.items()):
        ax.hlines(y=threshold, xmin=i-0.3, xmax=i+0.3,
                  colors="black", linestyles="--", linewidth=1.5)
        ax.text(i, threshold + 0.02, f"threshold={threshold}", ha="center", fontsize=8)

    ax.set_xticks(x)
    ax.set_xticklabels(list(metrics.keys()))
    ax.set_ylabel("Value")
    gate = "PASS ✓" if results["gate_pass"] else "FAIL ✗"
    ax.set_title(f"H-M1 Gate Metrics — {gate}")
    fig.tight_layout()

    out_path = Path(out_dir) / "gate_metrics.png"
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)
    return str(out_path)
```

---

## External Dependencies API (H-E1 Verified)

```python
# From h-e1/code/src/data/loader.py — signature CONFIRMED from architecture review
def load_dataset(csv_path: str, dataset_name: str) -> pd.DataFrame:
    """
    Load CSV; validate REQUIRED_COLS = [kl_budget, rm_score, gold_preference];
    assert ≥ 5 non-null paired rows.
    Raises: ValueError on validation failure.
    """
```

---

## Subtask Summary [8/8 used from logic budget]

| ID | Parent Epic | Complexity | Description |
|----|-------------|-----------|-------------|
| L-E4-1 | E4 (16) | High | run_rm_monotonicity_test() — Spearman ρ test |
| L-E4-2 | E4 (16) | High | detect_peak_reversal() — argmax + reversal check |
| L-E4-3 | E4 (16) | High | compute_divergence() — divergence_curve computation |
| L-E4-4 | E4 (16) | High | run_analysis() — orchestrator wiring all 3 tests |
| L-E5-1 | E5 (14) | High | plot_trajectory_dual_axis() — dual-axis with peak marker |
| L-E5-2 | E5 (14) | High | plot_divergence_gap() — divergence gap curve |
| L-E5-3 | E5 (14) | High | plot_spearman_scatter() — scatter with trend + ρ |
| L-E5-4 | E5 (14) | High | plot_gao_overlay() + plot_gate_metrics() |
