# Config: H-M5 (MECHANISM Validation)

**Applied**: no relevant KB pattern found (searched "experiment config patterns" — top hit similarity 0.43, unrelated PyTorch/InvokeAI repos); using standard dataclass config, consistent with H-M4/H-E1 project convention.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — `h-m5/code/` and `h-m4/code/` do not exist (no base hypothesis code to reuse; H-M5 only reads H-E1's output CSV, not its code). Serena skipped per Scenario 3.
**Config Files Found**: None - new config
**Pattern Used**: dataclass

This is a **statistical analysis** pipeline (panel regression + Granger causality), not ML training. No epochs/batch_size/optimizer — config covers data paths, lag structure, and gate thresholds only.

---

## A-1/A-2: Data Loading + Lag Construction [Complexity: 3+5, Budget: 8]

**Applied**: Standard dataclass, single fixed config (no tuning needed for a fixed 21-obs panel).

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class DataConfig:
    e1_data_path: str = "docs/youra_research/h-e1/data/venue_year_metrics.csv"
    venue_col: str = "venue"
    year_col: str = "year"
    value_cols: tuple = ("hhi", "entropy", "paper_count")
    primary_lag: int = 1
    robustness_lag: int = 2
    seed: int = 42  # unused (no randomness in OLS/FE), kept for NFR-2 reproducibility log
```

### Subtasks [3/3 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | `load_panel_data` | Read CSV, set MultiIndex(venue, year), sort_index |
| C-2-1 | `add_lags` | Groupby(venue).shift(lag) for hhi/entropy, diff() for delta cols |
| C-2-2 | `prepare_analysis_df` | add_lags + dropna, for lag=1 and lag=2 |

---

## A-3/A-4/A-5: Models (Baseline, Primary FE, Robustness) [Complexity: 4+7+6, Budget: 17]

**Applied**: Standard econometrics defaults (linearmodels PanelOLS clustered SE).

### Configuration (Python Dataclass)

```python
@dataclass
class ModelConfig:
    baseline_formula_hhi_col: str = "hhi_lag1"
    baseline_covariates: tuple = ("paper_count",)
    fe_entity_effects: bool = True
    fe_time_effects: bool = True
    fe_cov_type: str = "clustered"
    fe_cluster_entity: bool = True
    robustness_lag2_col: str = "hhi_lag2"
    ci_level: float = 0.95
```

### Subtasks [6/6 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-3-1 | `fit_baseline` | Pooled OLS, entropy ~ hhi_lag1 + paper_count |
| C-4-1 | `fit_panel_fe` (build) | PanelOLS spec, entity+time effects |
| C-4-2 | `fit_panel_fe` (extract) | beta/p/CI/R² from clustered SE result |
| C-5-1 | `run_robustness_suite` lag2 | fit_panel_fe with hhi_lag2 |
| C-5-2 | `run_robustness_suite` entity-only | fit_panel_fe(time_effects=False) |
| C-5-3 | `fit_delta_spec` | Pooled OLS on delta_entropy ~ delta_hhi_lag1 |

---

## A-6: Granger Causality [Complexity: 7, Budget: 7]

**Applied**: statsmodels `grangercausalitytests` defaults, ssr_ftest.

### Configuration (Python Dataclass)

```python
@dataclass
class GrangerConfig:
    maxlag: int = 2
    min_obs: int = 4  # per-venue min rows required to run test
    test_stat: str = "ssr_ftest"
    sig_threshold: float = 0.05
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-6-1 | `granger_per_venue` | Per-venue loop, extract ssr_ftest p-value per lag |
| C-6-2 | `run_bidirectional_granger` | Both directions (hhi→entropy, entropy→hhi), aggregate significance counts |

---

## A-7: Gate Check + Results Export [Complexity: 3, Budget: 3]

**Applied**: Direct thresholds from PRD Success Criteria (no tuning — fixed statistical gate).

### Configuration (Python Dataclass)

```python
@dataclass
class GateConfig:
    beta_max: float = 0.0          # beta < 0 required
    p_value_max: float = 0.05      # p < 0.05 required (primary)
    granger_p_max: float = 0.05    # secondary: hhi->entropy p<0.05 at >=1 lag
    granger_reverse_p_min: float = 0.05  # secondary: entropy->hhi p>0.05 (no reverse)
    results_path: str = "docs/youra_research/h-m5/results/h_m5_results.json"
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-7-1 | `gate_check` + JSON export | beta<0 AND p<0.05 primary gate; log Granger secondary; save results dict |

---

## A-8: Visualization [Complexity: 8, Budget: 8]

**Applied**: matplotlib/seaborn defaults, one fixed color per venue (categorical palette).

### Configuration (Python Dataclass)

```python
@dataclass
class VizConfig:
    figures_dir: str = "docs/youra_research/h-m5/figures/"
    figsize_default: tuple = (8, 6)
    figsize_heatmap: tuple = (10, 5)
    dpi: int = 150
    venue_palette: str = "Set2"  # seaborn categorical palette, 3 venues
    sig_line_color: str = "red"
    ci_alpha: float = 0.3
```

### Subtasks [5/5 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-8-1 | `plot_gate_metrics` | Beta + 95% CI errorbar, zero/sig reference lines |
| C-8-2 | `plot_hhi_entropy_scatter` | Scatter + regression line, colored by venue |
| C-8-3 | `plot_time_series` | Dual y-axis HHI/entropy per venue |
| C-8-4 | `plot_granger_heatmap` | 2-subplot p-value heatmap (both directions) |
| C-8-5 | `plot_residual_diagnostics` | QQ plot + residuals vs fitted |

---

## A-9: Pipeline Integration [Complexity: 4, Budget: 4]

**Applied**: Single entrypoint `main()`, no CLI args (fixed statistical pipeline, NFR-3 <30s).

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-9-1 | Wire `main()` | Call load→prepare→models→granger→gate→visualize→export in order |
| C-9-2 | Runtime verification | Confirm end-to-end run <30s (NFR-3) |

---

## Full Config Assembly (for analyze.py)

```python
DATA = DataConfig()
MODEL = ModelConfig()
GRANGER = GrangerConfig()
GATE = GateConfig()
VIZ = VizConfig()
```
