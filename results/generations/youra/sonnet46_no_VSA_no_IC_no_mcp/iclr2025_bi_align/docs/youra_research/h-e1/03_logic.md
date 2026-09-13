# Logic: H-E1
# RLHF Dual-Signal Co-existence Verification

**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr

Applied: Strategy pattern — pluggable per-dataset verifier with uniform return schema

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field — no existing code to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch. Serena MCP skipped (green-field). Archon MCP unavailable (ablation mode) — logic grounded from PRD and experiment brief (02c_experiment_brief.md).

Note: "Tensor shapes" in this experiment = DataFrame column dtypes and row counts (no neural network tensors).

---

## DataFrame Schemas

### Input DataFrame (both datasets)

| Column | dtype | Range | Notes |
|--------|-------|-------|-------|
| `kl_budget` | float64 | 0.0 – ~10.0 nats | x-axis (KL divergence from base policy) |
| `rm_score` | float64 | any | proxy reward signal |
| `gold_preference` | float64 | 0.0 – 1.0 | held-out human preference rate |

**Minimum rows:** 5 non-null paired rows (gate condition).

---

## L-E4-1: verify_signal_coexistence() [Complexity: 8, Budget: 1]

Applied: Guard-clause pattern — fail fast on structural errors before statistical checks

### API Signature

```python
def verify_signal_coexistence(df: pd.DataFrame, dataset_name: str) -> dict:
    """
    Verify that RM score and gold preference co-exist as paired time-series.

    Args:
        df: DataFrame with columns [kl_budget, rm_score, gold_preference]
        dataset_name: label for reporting (e.g., "Coste2023", "Gao2023")

    Returns:
        {
            "dataset":       str,   # dataset_name
            "passed":        bool,  # True iff gate_satisfied AND has_variation
            "n_kl_levels":   int,   # number of paired non-null rows
            "rm_variation":  float, # rm_score range (max - min)
            "gold_variation":float, # gold_preference range (max - min)
            "gate_satisfied":bool,  # n_kl_levels >= 5
            "reason":        str,   # human-readable pass/fail explanation
        }
    """
```

### Algorithm

```python
REQUIRED_COLS = ["kl_budget", "rm_score", "gold_preference"]
MIN_KL_LEVELS = 5      # from ExperimentConfig.min_kl_levels
MIN_VARIATION  = 0.01  # from ExperimentConfig.min_variation

def verify_signal_coexistence(df, dataset_name):
    # Step 1: Guard — required columns present
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        return {
            "dataset": dataset_name, "passed": False,
            "n_kl_levels": 0, "rm_variation": 0.0, "gold_variation": 0.0,
            "gate_satisfied": False,
            "reason": f"Missing columns: {missing}"
        }

    # Step 2: Drop unpaired rows (any NaN in the three required columns)
    paired = df[REQUIRED_COLS].dropna()

    # Step 3: Count KL levels
    n_levels = len(paired)
    gate_satisfied = n_levels >= MIN_KL_LEVELS

    # Step 4: Check signal variation (non-constant)
    rm_var   = float(paired["rm_score"].max()        - paired["rm_score"].min())
    gold_var = float(paired["gold_preference"].max() - paired["gold_preference"].min())
    has_variation = (rm_var > MIN_VARIATION) and (gold_var > MIN_VARIATION)

    passed = gate_satisfied and has_variation

    if not gate_satisfied:
        reason = f"Only {n_levels} paired KL levels (need >= {MIN_KL_LEVELS})"
    elif not has_variation:
        reason = (f"Signal variation too low: rm={rm_var:.4f}, "
                  f"gold={gold_var:.4f} (need > {MIN_VARIATION})")
    else:
        reason = f"PASS: {n_levels} paired KL levels, rm_var={rm_var:.4f}, gold_var={gold_var:.4f}"

    return {
        "dataset": dataset_name, "passed": passed,
        "n_kl_levels": n_levels, "rm_variation": rm_var,
        "gold_variation": gold_var, "gate_satisfied": gate_satisfied,
        "reason": reason,
    }
```

### Edge Cases

| Scenario | Behaviour |
|----------|-----------|
| Empty DataFrame | n_levels=0, gate_satisfied=False, passed=False |
| Missing columns | Returns immediately with reason listing missing cols |
| All-NaN in one column | dropna() yields 0 rows → gate_satisfied=False |
| Constant rm_score | rm_variation=0.0 < MIN_VARIATION → passed=False |
| Exactly 5 rows | gate_satisfied=True (boundary inclusive) |

---

## L-E5-1: plot_dual_axis() [Complexity: 9, Budget: 1]

Applied: Dual-axis matplotlib pattern — twin y-axes for signals with different scales

### API Signature

```python
def plot_dual_axis(
    df: pd.DataFrame,
    dataset_name: str,
    out_dir: str,
    dpi: int = 150,
) -> str:
    """
    Plot RM score and gold preference on twin y-axes vs KL budget.

    Args:
        df:           DataFrame with [kl_budget, rm_score, gold_preference]
        dataset_name: label used in title and filename (e.g., "Coste2023")
        out_dir:      directory to save figure
        dpi:          figure resolution (default 150)

    Returns:
        Absolute path to saved figure file.
    """
```

### Algorithm

```python
import matplotlib.pyplot as plt
from pathlib import Path

def plot_dual_axis(df, dataset_name, out_dir, dpi=150):
    fig, ax1 = plt.subplots(figsize=(8, 5))

    # Left y-axis: RM score (blue)
    color_rm = "steelblue"
    ax1.set_xlabel("KL Divergence (nats)")
    ax1.set_ylabel("RM Score (proxy)", color=color_rm)
    ax1.plot(df["kl_budget"], df["rm_score"],
             marker="o", color=color_rm, label="RM Score")
    ax1.tick_params(axis="y", labelcolor=color_rm)

    # Right y-axis: gold preference (crimson)
    ax2 = ax1.twinx()
    color_gold = "crimson"
    ax2.set_ylabel("Gold Preference Rate", color=color_gold)
    ax2.plot(df["kl_budget"], df["gold_preference"],
             marker="s", linestyle="--", color=color_gold, label="Gold Preference")
    ax2.tick_params(axis="y", labelcolor=color_gold)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    ax1.set_title(f"H-E1: Dual Signal Co-existence — {dataset_name}")
    fig.tight_layout()

    out_path = Path(out_dir) / f"dual_axis_{dataset_name.lower()}.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)
    return str(out_path)
```

---

## L-E5-2: plot_comparison() [Complexity: 9, Budget: 1]

Applied: Multi-panel subplot pattern — side-by-side dataset comparison with PASS/FAIL annotation

### API Signature

```python
def plot_comparison(
    results: list[dict],
    dfs: list[pd.DataFrame],
    dataset_names: list[str],
    out_dir: str,
    dpi: int = 150,
) -> str:
    """
    Generate side-by-side comparison figure for both datasets.

    Args:
        results:       list of dicts from verify_signal_coexistence() (one per dataset)
        dfs:           list of DataFrames (same order as results)
        dataset_names: list of dataset name strings
        out_dir:       directory to save figure
        dpi:           figure resolution

    Returns:
        Absolute path to saved figure file.
    """
```

### Algorithm

```python
def plot_comparison(results, dfs, dataset_names, out_dir, dpi=150):
    n = len(dfs)
    fig, axes = plt.subplots(1, n, figsize=(7 * n, 5), sharey=False)
    if n == 1:
        axes = [axes]

    for ax, df, res, name in zip(axes, dfs, results, dataset_names):
        ax.plot(df["kl_budget"], df["rm_score"],
                marker="o", color="steelblue", label="RM Score")
        ax2 = ax.twinx()
        ax2.plot(df["kl_budget"], df["gold_preference"],
                 marker="s", linestyle="--", color="crimson", label="Gold Pref")

        status = "PASS ✓" if res["passed"] else "FAIL ✗"
        color  = "green"  if res["passed"] else "red"
        ax.set_title(f"{name}\n{status} ({res['n_kl_levels']} KL levels)",
                     color=color, fontweight="bold")
        ax.set_xlabel("KL Divergence (nats)")
        ax.set_ylabel("RM Score", color="steelblue")
        ax2.set_ylabel("Gold Preference", color="crimson")

    fig.suptitle("H-E1 Gate: Dual Signal Co-existence Verification", fontsize=13)
    fig.tight_layout()

    out_path = Path(out_dir) / "comparison_both_datasets.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)
    return str(out_path)
```

---

## Subtask Summary [3/3 used]

| ID | Parent Epic | Complexity | Description |
|----|-------------|-----------|-------------|
| L-E4-1 | E4 (8) | Medium | verify_signal_coexistence() full spec + edge cases |
| L-E5-1 | E5 (9) | Medium | plot_dual_axis() dual-axis time series figure |
| L-E5-2 | E5 (9) | Medium | plot_comparison() side-by-side gate figure |
