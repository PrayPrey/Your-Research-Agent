# Config: H-M4 Saturation Detection

Applied: EXISTENCE single-config pattern (no grid, no ablations)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config constants verified from H-M3 actual code
**Config Files Found**: `docs/youra_research/h-m3/code/run.py` (module-level constants)
**Pattern Used**: hardcoded dict / module-level constants (matching H-M3 style)

---

## Inherited Configuration (Base Hypothesis)

From `docs/youra_research/h-m3/code/run.py` (actual implementation):

```python
# Verified field names and values from H-M3 actual code

# Curve fit
p0 = [0.92, 0.15, 12.0]                   # K, r, t0
bounds = ([0.5, 0.01, -24], [1.05, 3.0, 72])
MAXFEV = 10000

# Bootstrap (fallback)
BOOTSTRAP_N = 500
BOOTSTRAP_SEED = 42                        # np.random.default_rng(42)
BOOTSTRAP_MAXFEV = 5000

# Plausibility thresholds (H-M3, for reference only)
K_LO, K_HI = 0.85, 1.0
T0_LO, T0_HI = 6, 48
CI_T0_MAX = 12.0

# Benchmark origin months
BENCHMARK_RELEASE_MONTH = {"glue": 0, "superglue": 0}
```

---

## A-1 / A-2 / A-3 / A-4: Core Detection Config

```python
# Ground truth saturation dates (YYYY-MM)
GROUND_TRUTH = {"glue": "2019-09", "superglue": "2021-06"}

# Benchmark launch dates (YYYY-MM)  — used to build calendar_month column
LAUNCH_DATES = {"glue": "2018-04", "superglue": "2019-05"}

# Dual-criterion saturation thresholds
THRESHOLD_K    = 0.99   # score must exceed K * THRESHOLD_K
THRESHOLD_RATE = 0.05   # monthly_gain must fall below this value

# Error acceptance gate
ERROR_THRESHOLD_MONTHS = 3  # |detected - ground_truth| <= 3 months to pass
```

---

## A-5: Sensitivity & Prospective Config

```python
# Sensitivity grid (3x3)
SENSITIVITY_K_GRID    = [0.95, 0.99, 1.00]
SENSITIVITY_RATE_GRID = [0.02, 0.05, 0.10]

# Prospective forecast lookback window
PROSPECTIVE_LOOKBACK = 6  # months of data before sat_month_idx used for re-fit
```

---

## A-6 / A-7: Output Config

```python
# Paths (relative to code/run.py location)
OUTPUT_DIR  = "outputs"        # JSON + CSV
FIGURES_DIR = "../figures"     # 5 PNGs

# Figure filenames
FIGURE_NAMES = {
    "sat_error_bar":            "sat_error_bar.png",
    "saturation_timeline":      "saturation_timeline.png",
    "dual_criterion_glue":      "dual_criterion_glue.png",
    "dual_criterion_superglue": "dual_criterion_superglue.png",
    "prospective_forecast":     "prospective_forecast.png",
    "sensitivity_heatmap":      "sensitivity_heatmap.png",
}

# results.json top-level keys
RESULTS_KEYS = [
    "hypothesis_id",   # "h-m4"
    "gate_pass",
    "glue",
    "superglue",
    "sensitivity",
    "prospective",
    "status",
]

# Matplotlib style (applies to all 5 figures)
PLOT_DPI     = 120
PLOT_STYLE   = "seaborn-v0_8-whitegrid"
PLOT_PALETTE = {"glue": "royalblue", "superglue": "darkorange"}
FIGSIZE_WIDE = (13, 5)   # 2-panel figures
FIGSIZE_SQ   = (10, 4)   # timeline / single-panel figures
FIGSIZE_HEAT = (8, 5)    # sensitivity heatmap
```

---

## Subtasks

### C-6-1: Figure Output Path Specs [Budget: 1]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Figure path naming | All figures saved to `h-m4/figures/` using `FIGURE_NAMES` dict above; `dual_criterion` produces one PNG per benchmark (2 files); `fig.savefig(fig_dir / FIGURE_NAMES[key], dpi=PLOT_DPI)` pattern |

### C-6-2: Matplotlib/Seaborn Style Config [Budget: 1]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-2 | Plot style constants | Use `plt.style.use(PLOT_STYLE)` at script top; `PLOT_PALETTE` for benchmark colors; `FIGSIZE_*` constants for each figure type; `dpi=PLOT_DPI` on all `savefig` calls; annotate saturation dates with `ax.axvline` + `ax.annotate` matching H-M3 style |
