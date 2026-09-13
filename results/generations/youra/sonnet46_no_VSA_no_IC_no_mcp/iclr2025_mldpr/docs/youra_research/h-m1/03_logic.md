---
hypothesis_id: H-M1
document_type: Logic
phase: "Phase 3"
date: "2026-08-25"
---

# Logic: H-M1 — Temporal Structure Analysis API Design

Applied: functional-pipeline-pattern (pure functions, no classes, single-file)
Applied: scipy-statistical-correlation-api (spearmanr with rank-tie handling)

## Codebase Analysis (Serena)

**Status:** Serena MCP unavailable in this execution environment.
**Analyzed Path:** docs/youra_research/h-e1/ (architecture doc only — H-E1 code not yet written)
**Findings:** H-M1 is green-field statistical pipeline. No existing symbols to analyze. Single-file implementation in `code/run.py`. All functions are pure (no side effects except file I/O in plot/save functions).

---

## Full API Reference

### load_timeseries(csv_path: str) -> tuple[np.ndarray, np.ndarray]

```python
def load_timeseries(csv_path: str) -> tuple[np.ndarray, np.ndarray]:
    """
    Load and validate H-E1 cleaned timeseries CSV.

    Args:
        csv_path: Path to cleaned CSV (e.g. "data/glue_timeseries_clean.csv")
                  Expected columns: months (int64), monthly_max (float64)

    Returns:
        times:  np.ndarray shape (N,) dtype int64  — months since release, sorted ascending
        scores: np.ndarray shape (N,) dtype float64 — monthly max normalized score [0,1]

    Raises:
        FileNotFoundError: if csv_path does not exist
            Message: "H-E1 output not found: {csv_path}. Re-run H-E1 data pipeline."
        ValueError: if required columns missing, or validation assertions fail
    """
    if not Path(csv_path).exists():
        raise FileNotFoundError(
            f"H-E1 output not found: {csv_path}. Re-run H-E1 data pipeline."
        )
    df = pd.read_csv(csv_path)
    # Column validation
    required = {"months", "monthly_max"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {missing}. Got: {list(df.columns)}")
    df = df.sort_values("months").reset_index(drop=True)
    times  = df["months"].to_numpy(dtype=np.int64)
    scores = df["monthly_max"].to_numpy(dtype=np.float64)
    # Sanity assertions
    time_span = int(times.max() - times.min())
    if time_span < MIN_MONTHS_SPAN:
        raise ValueError(f"Time span {time_span} months < required {MIN_MONTHS_SPAN}. Check H-E1 output.")
    if len(scores) < MIN_OBS:
        raise ValueError(f"Only {len(scores)} observations < required {MIN_OBS}.")
    if scores.std() < MIN_SCORE_STD:
        raise ValueError(f"Score variance too low ({scores.std():.4f}). Constant timeseries cannot be correlated.")
    return times, scores
```

**Input shape:** CSV rows × 2 columns → arrays of shape (N,)
**Output shapes:** times: (N,) int64, scores: (N,) float64

---

### compute_gains(times, scores) -> tuple[np.ndarray, np.ndarray]

```python
def compute_gains(
    times: np.ndarray,   # shape (N,) int64
    scores: np.ndarray,  # shape (N,) float64
) -> tuple[np.ndarray, np.ndarray]:
    """
    Compute month-over-month gain rates.

    Returns:
        gain_times: np.ndarray shape (N-1,) int64  — time points for each gain
        gains:      np.ndarray shape (N-1,) float64 — score[t] - score[t-1]

    Edge case: N=1 → returns empty arrays (caller should check len(gains) >= 2)
    """
    gains = np.diff(scores)         # shape (N-1,)
    gain_times = times[1:]          # shape (N-1,)
    return gain_times, gains
```

**Shape invariant:** `len(gain_times) == len(gains) == len(scores) - 1`

---

### split_inflection(gains, inflection_idx=None) -> tuple[np.ndarray, np.ndarray]

```python
def split_inflection(
    gains: np.ndarray,               # shape (N-1,) float64
    inflection_idx: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Split gain series into pre- and post-inflection segments.

    Args:
        gains: month-over-month gain array shape (N-1,)
        inflection_idx: split index. Defaults to len(gains) // 2 (midpoint heuristic).
            Note: logistic curve peak from H-E1 could be used here if exposed,
            but midpoint is sufficient for PoC — H-E1 showed growth+inflection+plateau.

    Returns:
        pre_gains:  gains[:inflection_idx]   shape (inflection_idx,)
        post_gains: gains[inflection_idx:]   shape (N-1-inflection_idx,)

    Edge cases:
        - inflection_idx=0 → pre_gains is empty; pre_post_ratio = np.nan
        - inflection_idx >= len(gains) → post_gains is empty; pre_post_ratio = np.inf
    """
    if inflection_idx is None:
        inflection_idx = len(gains) // 2
    inflection_idx = max(0, min(inflection_idx, len(gains)))
    pre_gains  = gains[:inflection_idx]
    post_gains = gains[inflection_idx:]
    return pre_gains, post_gains
```

---

## Subtask L-E4-1: Spearman Correlation Implementation

### test_temporal_signal() — full specification

```python
def test_temporal_signal(
    times:      np.ndarray,   # shape (N,)  int64  — months since release
    scores:     np.ndarray,   # shape (N,)  float64 — monthly_max series
    gains:      np.ndarray,   # shape (N-1,) float64 — np.diff(scores)
    gain_times: np.ndarray,   # shape (N-1,) int64  — times[1:]
) -> dict:
    """
    Core H-M1 temporal signal detection.

    Returns dict:
        rho_monotonic:   float  — Spearman ρ(times, scores). Target > 0.8.
        rho_decel:       float  — Spearman ρ(gain_times, gains). Target < -0.3.
        pre_post_ratio:  float  — mean(pre_gains) / mean(post_gains). Expected > 1.0.
                                  np.inf if post_gain_mean <= 0.
                                  np.nan if pre_gains or post_gains is empty.
        n_months:        int    — len(scores)
        n_gains:         int    — len(gains)
        pass:            bool   — rho_monotonic > RHO_MONO_THRESHOLD AND rho_decel < RHO_DECEL_THRESHOLD
    """
    from scipy import stats

    # Test 1: Monotonicity — ρ(time, score)
    rho_mono, _ = stats.spearmanr(times, scores)
    # scipy.stats.spearmanr handles ties via average rank method; no special handling needed.

    # Test 2: Deceleration — ρ(gain_time, gain_rate)
    if len(gains) < 2:
        rho_decel = float("nan")
    else:
        rho_decel, _ = stats.spearmanr(gain_times, gains)

    # Test 3: Pre/post inflection ratio
    pre_gains, post_gains = split_inflection(gains)
    if len(pre_gains) == 0 or len(post_gains) == 0:
        pre_post_ratio = float("nan")
    else:
        pre_mean  = float(np.mean(pre_gains))
        post_mean = float(np.mean(post_gains))
        if post_mean <= 0:
            pre_post_ratio = float("inf")
        else:
            pre_post_ratio = pre_mean / post_mean

    return {
        "rho_monotonic":  float(rho_mono),
        "rho_decel":      float(rho_decel),
        "pre_post_ratio": pre_post_ratio,
        "n_months":       len(scores),
        "n_gains":        len(gains),
        "pass":           (float(rho_mono) > RHO_MONO_THRESHOLD and float(rho_decel) < RHO_DECEL_THRESHOLD),
    }
```

**Input validation (caller responsibility — done in load_timeseries):**
- NaN values: not expected from H-E1 clean output; if present, spearmanr propagates NaN → result NaN
- All-same scores: caught by MIN_SCORE_STD assertion in load_timeseries
- Single observation: caught by MIN_OBS assertion

**Why Spearman not Pearson:** Spearman is rank-based — robust to non-normality, ceiling effects, and the S-curve shape. Pearson would underestimate monotonicity for logistic-shaped trajectories. Phase 2B explicitly specifies Spearman.

---

## Subtask L-E4-2: Pre/Post Inflection Algorithm

**Inflection point strategy (PoC):**

```python
# Midpoint heuristic — sufficient for PoC
# H-E1 confirmed growth + inflection + plateau phases present.
# The midpoint of the monthly timeseries approximates the inflection region.
inflection_idx = len(gains) // 2

# If H-E1 exposes logistic fit parameters (t0 from curve_fit), use:
# inflection_idx = np.searchsorted(gain_times, t0)
# But this requires inter-hypothesis API coupling — avoid for now.
```

**Edge case handling:**

| Case | Condition | Handling |
|------|-----------|---------|
| post_mean = 0 | Gains plateau exactly at zero | pre_post_ratio = np.inf (gains completely stopped) |
| post_mean < 0 | Scores decrease post-inflection | pre_post_ratio = np.inf (treated as maximum deceleration) |
| pre_gains empty | inflection_idx = 0 | pre_post_ratio = np.nan (report, do not crash) |
| post_gains empty | inflection_idx >= N-1 | pre_post_ratio = np.inf |
| pre_post_ratio > 1.0 | Normal case | Pre-inflection faster than post: confirms deceleration |

---

## Subtask L-E6-1: Gate Metrics Bar Chart

```python
def plot_gate_metrics(
    benchmark_results: dict[str, dict],  # {"glue": {...}, "superglue": {...}}
    out_dir: str,
) -> None:
    """
    Grouped bar chart: rho_monotonic and rho_decel for GLUE vs SuperGLUE.
    Threshold lines at 0.8 (monotonicity) and -0.3 (deceleration).
    Saved to: {out_dir}/gate_metrics.png
    """
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    benchmarks = list(benchmark_results.keys())  # ["glue", "superglue"]
    colors = {"glue": "#2196F3", "superglue": "#FF9800"}  # blue, orange

    metrics = ["rho_monotonic", "rho_decel"]
    x = np.arange(len(metrics))
    width = 0.3

    fig, ax = plt.subplots(figsize=(8, 5))

    for i, bm in enumerate(benchmarks):
        vals = [benchmark_results[bm]["rho_monotonic"], benchmark_results[bm]["rho_decel"]]
        offset = (i - 0.5) * width
        bars = ax.bar(x + offset, vals, width, label=bm.upper(), color=colors[bm], alpha=0.85)
        # Annotate value on each bar
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, val + 0.02 * np.sign(val),
                    f"{val:.3f}", ha="center", va="bottom" if val >= 0 else "top", fontsize=9)

    # Threshold lines
    ax.axhline(RHO_MONO_THRESHOLD,  color="green", linestyle="--", linewidth=1.5,
               label=f"Mono threshold ({RHO_MONO_THRESHOLD})")
    ax.axhline(RHO_DECEL_THRESHOLD, color="red",   linestyle="--", linewidth=1.5,
               label=f"Decel threshold ({RHO_DECEL_THRESHOLD})")
    ax.axhline(0, color="black", linewidth=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(["ρ(time, score)\n[Monotonicity]", "ρ(time, gain_rate)\n[Deceleration]"])
    ax.set_ylabel("Spearman ρ")
    ax.set_ylim(-1.1, 1.1)
    ax.set_title("H-M1 Gate Metrics: Temporal Signal Detection")
    ax.legend()
    fig.tight_layout()

    Path(out_dir).mkdir(parents=True, exist_ok=True)
    fig.savefig(f"{out_dir}/gate_metrics.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
```

---

## Subtask L-E6-2: Score Trajectory + Gain Rate Plots

```python
def plot_score_trajectory(
    all_data: dict[str, tuple[np.ndarray, np.ndarray]],  # {"glue": (times, scores), ...}
    out_dir: str,
) -> None:
    """
    Overlaid line plot of monthly_max scores for all benchmarks on shared axes.
    Saved to: {out_dir}/score_trajectory.png
    """
    import matplotlib.pyplot as plt
    colors = {"glue": "#2196F3", "superglue": "#FF9800"}
    fig, ax = plt.subplots(figsize=(10, 5))
    for bm, (times, scores) in all_data.items():
        ax.plot(times, scores, marker="o", markersize=3, linewidth=1.5,
                color=colors.get(bm, "gray"), label=bm.upper())
    ax.set_xlabel("Months Since Benchmark Release")
    ax.set_ylabel("Normalized Composite Score [0, 1]")
    ax.set_title("H-M1: Score-Over-Time Trajectory (GLUE + SuperGLUE)")
    ax.legend()
    fig.tight_layout()
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    fig.savefig(f"{out_dir}/score_trajectory.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_gain_rate(
    all_data: dict[str, tuple[np.ndarray, np.ndarray]],  # {"glue": (gain_times, gains), ...}
    out_dir: str,
    window: int = 3,  # rolling mean window for trend line
) -> None:
    """
    Scatter plot of month-over-month gains vs time with rolling mean trend.
    Saved to: {out_dir}/gain_rate.png

    Trend line: pandas.Series(gains).rolling(window, min_periods=1).mean()
    (LOWESS alternative: scipy.stats.mstats.idealfourths — avoided for simplicity)
    """
    import matplotlib.pyplot as plt
    import pandas as pd
    colors = {"glue": "#2196F3", "superglue": "#FF9800"}
    fig, ax = plt.subplots(figsize=(10, 4))
    for bm, (gain_times, gains) in all_data.items():
        color = colors.get(bm, "gray")
        ax.scatter(gain_times, gains, s=20, alpha=0.6, color=color, label=f"{bm.upper()} gains")
        trend = pd.Series(gains).rolling(window, min_periods=1).mean().to_numpy()
        ax.plot(gain_times, trend, linewidth=2, color=color, linestyle="-", label=f"{bm.upper()} trend")
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_xlabel("Months Since Benchmark Release")
    ax.set_ylabel("Month-Over-Month Score Gain")
    ax.set_title("H-M1: Gain Rate Over Time (Deceleration Test)")
    ax.legend()
    fig.tight_layout()
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    fig.savefig(f"{out_dir}/gain_rate.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_pre_post_inflection(
    all_data: dict[str, tuple[np.ndarray, np.ndarray]],  # {"glue": (pre_gains, post_gains), ...}
    out_dir: str,
) -> None:
    """
    Box plot comparing gain distributions pre vs post inflection per benchmark.
    Saved to: {out_dir}/pre_post_inflection.png
    """
    import matplotlib.pyplot as plt
    benchmarks = list(all_data.keys())
    fig, axes = plt.subplots(1, len(benchmarks), figsize=(5 * len(benchmarks), 4), sharey=True)
    if len(benchmarks) == 1:
        axes = [axes]
    for ax, bm in zip(axes, benchmarks):
        pre_gains, post_gains = all_data[bm]
        ax.boxplot([pre_gains, post_gains], labels=["Pre-inflection", "Post-inflection"],
                   patch_artist=True,
                   boxprops=dict(facecolor="#BBDEFB"),
                   medianprops=dict(color="navy", linewidth=2))
        ax.axhline(0, color="red", linewidth=0.8, linestyle="--")
        ax.set_title(bm.upper())
        ax.set_ylabel("Score Gain per Month")
    fig.suptitle("H-M1: Gain Rate Pre vs Post Inflection", fontsize=13)
    fig.tight_layout()
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    fig.savefig(f"{out_dir}/pre_post_inflection.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
```

---

## Results Reporting

```python
def print_results_table(benchmark_results: dict[str, dict]) -> None:
    header = f"{'Benchmark':<12} {'ρ_mono':>8} {'ρ_decel':>9} {'pre/post':>10} {'Pass?':>7}"
    print("\n" + "=" * len(header))
    print("H-M1 Results: Temporal Signal Detection")
    print("=" * len(header))
    print(header)
    print("-" * len(header))
    for bm, r in benchmark_results.items():
        ratio_str = f"{r['pre_post_ratio']:.2f}" if np.isfinite(r['pre_post_ratio']) else "inf"
        print(f"{bm.upper():<12} {r['rho_monotonic']:>8.3f} {r['rho_decel']:>9.3f} "
              f"{ratio_str:>10} {'PASS' if r['pass'] else 'FAIL':>7}")
    print("=" * len(header))


def save_results_json(benchmark_results: dict[str, dict], out_path: str) -> None:
    import json, math
    def _json_safe(v):
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            return str(v)
        return v
    payload = {
        bm: {k: _json_safe(v) for k, v in r.items()}
        for bm, r in benchmark_results.items()
    }
    payload["overall_pass"] = all(r["pass"] for r in benchmark_results.values())
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)
```

---

## Self-Check / Test

```python
if __name__ == "__main__":
    # Synthetic monotonic + decelerating series
    t = np.arange(30)
    # Logistic-ish: fast early, slow late
    s = 1 / (1 + np.exp(-0.3 * (t - 15))) * 0.8 + 0.1
    gt, g = compute_gains(t, s)
    r = test_temporal_signal(t, s, g, gt)
    assert r["rho_monotonic"] > 0.8,  f"Expected rho_mono > 0.8, got {r['rho_monotonic']:.3f}"
    assert r["rho_decel"] < -0.3,     f"Expected rho_decel < -0.3, got {r['rho_decel']:.3f}"
    assert r["pre_post_ratio"] > 1.0, f"Expected pre_post_ratio > 1.0, got {r['pre_post_ratio']:.3f}"
    assert r["pass"] is True
    print("Self-check PASSED")
```
