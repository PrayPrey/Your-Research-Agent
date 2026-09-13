# Config: H-M3 — Scenario Classification of Partial Spearman

Applied: H-M2 dataclass pattern (verified from h-m2/code/config.py)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config classes verified from base code
**Config Files Found**: `docs/youra_research/h-m2/code/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

From `h-m2/code/config.py` (actual code):

```python
# Verified field names and defaults:
@dataclass
class ExperimentConfig:          # H-M2
    data_path: str               # = "../../h-e1/code/data/llm_leaderboard_v1/llm.csv"
    bbq_path: str                # = "../../h-e1/code/data/bbq_scores/bbq_per_model.csv"
    required_cols: Tuple[str, ...]
    n_min: int                   # = 30
    n_boot: int                  # = 5000
    seed: int                    # = 42
    min_family_size: int         # = 3
    figures_dir: str             # = "../../figures"
    results_dir: str             # = "./results"
    fig_size: Tuple[float, float]# = (8.0, 5.0)
    fig_dpi: int                 # = 150
    color_significant: str       # = "#2ca02c"
    color_null: str              # = "#ff7f0e"
```

H-M3 does NOT extend this class — it reads `h_m2_results.json` and defines its own `ExperimentConfig`.

---

## Full ExperimentConfig (H-M3)

```python
from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class ExperimentConfig:
    # Paths
    h_m2_results_path: str = "../../h-m2/code/results/h_m2_results.json"
    h_m1_pairs_csv: str = "../../h-e1/code/data/llm_leaderboard_v1/llm.csv"
    results_dir: str = "./results"
    figures_dir: str = "../../figures/h-m3"

    # Scenario boundaries (pre-specified, immutable)
    scenario_a_bound: float = 0.20   # |partial_rho| < this → scenario a
    scenario_b_bound: float = 0.40   # partial_rho > this → scenario b
    scenario_c_bound: float = -0.20  # partial_rho < this → scenario c

    # Ablation boundary variants
    tight_a: float = 0.15
    tight_b: float = 0.35
    tight_c: float = -0.15
    wide_a: float = 0.25
    wide_b: float = 0.45
    wide_c: float = -0.25

    # Tier 2
    n_min_harmbench: int = 20
    fuzzy_threshold: int = 75        # rapidfuzz token_sort_ratio cutoff

    # Bootstrap (Tier 2 re-analysis only)
    n_boot: int = 5000
    seed: int = 42

    # Figures
    fig_dpi: int = 300               # non-standard: 300 for publication quality (H-M2 used 150)
    fig_size: Tuple[float, float] = (9.0, 5.0)

    # Heatmap (Fig2)
    heatmap_cmap: str = "RdBu_r"
    heatmap_vmin: float = -1.0
    heatmap_vmax: float = 1.0
    heatmap_annot_fmt: str = ".2f"
    heatmap_fig_size: Tuple[float, float] = (6.0, 5.0)

    # Output schema
    output_filename: str = "h_m3_results.json"


def load_config() -> ExperimentConfig:
    """Return ExperimentConfig with defaults."""
    return ExperimentConfig()
```

---

## A-3: DataLoader Tier 2+3 [Complexity: 8, Budget: 1]

Applied: hardcoded-dict data pattern

### Configuration

No separate config class needed — parameters live in `ExperimentConfig`:

| Field | Default | Purpose |
|-------|---------|---------|
| `h_m1_pairs_csv` | `"../../h-e1/code/data/llm_leaderboard_v1/llm.csv"` | ΔBBQ CSV path |
| `n_min_harmbench` | `20` | Skip Tier 2 if joined N < 20 |
| `fuzzy_threshold` | `75` | rapidfuzz cutoff for model name join |

HarmBench hardcoded dict requires no config — it is a fixed research artifact (arXiv:2402.04249 Table 2). Any parameterization would be misleading.

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | DataLoader config | `n_min_harmbench`, `fuzzy_threshold`, `h_m1_pairs_csv` in ExperimentConfig; HarmBench dict is hardcoded constant |

### Validation Rules

- `n_min_harmbench >= 1`
- `fuzzy_threshold` in `[0, 100]`
- `h_m1_pairs_csv` must exist at runtime (checked in `load_tier3_delta_bbq`)

---

## A-7: Ablation Studies [Complexity: 8, Budget: 1]

Applied: boundary-variant config pattern

### Configuration

Ablation parameters live in `ExperimentConfig` (no separate class needed):

```python
# Boundary variants — all in ExperimentConfig
tight_a: float = 0.15
tight_b: float = 0.35
tight_c: float = -0.15
wide_a: float = 0.25
wide_b: float = 0.45
wide_c: float = -0.25
# CI method switch: pingouin.partial_corr Fisher CI vs BCa bootstrap
# Controlled by call site in ablation_ci_method() — no config flag needed
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Ablation variant config | tight/wide boundary fields in ExperimentConfig; CI method switch is code-level (no config flag) |

### Validation Rules

- `tight_a < scenario_a_bound < wide_a`
- `tight_b < scenario_b_bound < wide_b`
- `wide_c < scenario_c_bound < tight_c` (note: negative values, inequality reverses)

---

## A-12: main.py + Serialization [Complexity: 8, Budget: 1]

Applied: output-schema config pattern

### Configuration

```python
# In ExperimentConfig:
results_dir: str = "./results"
figures_dir: str = "../../figures/h-m3"
output_filename: str = "h_m3_results.json"
```

Output JSON schema (for validation in `main.py`):

```python
REQUIRED_OUTPUT_KEYS = (
    "partial_rho", "ci_partial", "raw_rho", "ci_raw", "N",
    "scenario", "is_ambiguous", "narrative",
    "ablation_ci_method", "ablation_boundary_tight", "ablation_boundary_wide",
    "tier2", "tier3",
    "mechanism_verified", "gate_passed",
)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-12-1 | Output schema config | `results_dir`, `figures_dir`, `output_filename` in ExperimentConfig; `REQUIRED_OUTPUT_KEYS` tuple as module constant in main.py |

### Validation Rules

- `results_dir` created via `os.makedirs(results_dir, exist_ok=True)` before write
- `figures_dir` created similarly
- All `REQUIRED_OUTPUT_KEYS` present in results dict before JSON dump (raise `RuntimeError` if missing)

---

## A-9: Fig2 Heatmap [Complexity: 8, Budget: 1]

Applied: matplotlib heatmap config pattern

### Configuration

```python
# In ExperimentConfig:
heatmap_cmap: str = "RdBu_r"          # diverging colormap centered at 0
heatmap_vmin: float = -1.0
heatmap_vmax: float = 1.0
heatmap_annot_fmt: str = ".2f"
heatmap_fig_size: Tuple[float, float] = (6.0, 5.0)
fig_dpi: int = 300
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-9-1 | Heatmap plot config | `heatmap_cmap`, `heatmap_vmin/vmax`, `heatmap_annot_fmt`, `heatmap_fig_size` in ExperimentConfig; `plot_partial_corr_heatmap` returns None if Tier 2 SKIPPED |

### Validation Rules

- `heatmap_vmin < 0 < heatmap_vmax`
- `heatmap_cmap` must be valid matplotlib colormap (runtime check via `matplotlib.cm.get_cmap`)
- Function returns `None` (not raises) when Tier 2 status is SKIPPED
