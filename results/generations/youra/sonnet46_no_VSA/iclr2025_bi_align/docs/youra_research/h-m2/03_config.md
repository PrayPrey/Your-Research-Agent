# H-M2 Configuration Design

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis extension
**Status**: Config classes verified from H-M1 actual code (`h-m1/code/config.py`)
**Config Files Found**: `h-m1/code/config.py` — `AnalysisConfig` dataclass + `load_config()`
**Pattern Used**: dataclass + optional YAML override via `load_config(yaml_path=None)`

Applied: Standard Python dataclass config pattern, consistent with H-M1

---

## Inherited Configuration (Base Hypothesis H-M1)

Verified from `h-m1/code/config.py` (actual code, not specs):

```python
# H-M1 AnalysisConfig — actual field names and defaults
@dataclass
class AnalysisConfig:
    data_path: str = "../../h-e1/code/data/llm_leaderboard_v1/llm.csv"
    required_cols: Tuple[str, ...] = ("model_name", "TruthfulQA_MC2", "bbq_accuracy", "MMLU")
    r2_threshold: float = 0.05
    n_min: int = 30
    figures_dir: str = "../figures"
    results_dir: str = "./results"
    seed: int = 42
    fig_bar_size: Tuple[float, float] = (7.0, 5.0)
    fig_scatter_size: Tuple[float, float] = (6.0, 5.0)
    fig_heatmap_size: Tuple[float, float] = (5.0, 4.5)
    fig_dpi: int = 150
    color_pass: str = "#2ca02c"
    color_fail: str = "#d62728"
    color_scatter: str = "#1f77b4"
    color_threshold: str = "#ff7f0e"
```

**H-M2 changes from H-M1:**
- Class renamed `AnalysisConfig` → `ExperimentConfig`
- `required_cols`: `"bbq_accuracy"` → `"BBQ_accuracy"` (column name corrected to match dataset)
- `figures_dir`: `"../figures"` → `"../../figures"` (H-M2 lives one level deeper)
- Removed: `r2_threshold`, `fig_bar_size`, `fig_scatter_size`, `fig_heatmap_size`, `color_fail`, `color_scatter`, `color_threshold` (not needed for bootstrap/family analysis)
- Added: `n_boot`, `min_family_size`, `fig_size`, `color_significant`, `color_null`

---

## YAML Config Schema

```yaml
# h-m2/code/config.yaml
# All fields optional — omitted fields use dataclass defaults

data:
  data_path: "../../h-e1/code/data/llm_leaderboard_v1/llm.csv"  # str; path to LLM leaderboard CSV
  required_cols:                                                   # list[str]; columns that must exist
    - "model_name"
    - "TruthfulQA_MC2"
    - "BBQ_accuracy"
    - "MMLU"
  n_min: 30                                                        # int, >= 10; minimum total rows to proceed

bootstrap:
  n_boot: 5000     # int, >= 1000; bootstrap resamples (5000 = SE < 0.7% at p=0.05)
  seed: 42         # int; global RNG seed for full reproducibility
  min_family_size: 3  # int, >= 2; minimum models per family to include family in analysis

output:
  figures_dir: "../../figures"   # str; directory for saved figures
  results_dir: "./results"       # str; directory for saved CSV/JSON results

figures:
  fig_size: [8.0, 5.0]           # [width, height] in inches
  fig_dpi: 150                   # int; output DPI (150 = publication-quality screen)
  color_significant: "#2ca02c"   # str; hex color for statistically significant results
  color_null: "#ff7f0e"          # str; hex color for null/non-significant results
```

---

## Python Dataclass (Implementation-Ready)

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple


@dataclass
class ExperimentConfig:
    # --- Data ---
    data_path: str = "../../h-e1/code/data/llm_leaderboard_v1/llm.csv"
    required_cols: Tuple[str, ...] = (
        "model_name", "TruthfulQA_MC2", "BBQ_accuracy", "MMLU"
    )
    n_min: int = 30  # minimum dataset rows; below this analysis is underpowered

    # --- Bootstrap ---
    n_boot: int = 5000        # resamples; 5000 keeps SE(p-value) < 0.7% at alpha=0.05
    seed: int = 42            # global RNG seed
    min_family_size: int = 3  # families with fewer models excluded (unstable bootstrap CI)

    # --- Output ---
    figures_dir: str = "../../figures"
    results_dir: str = "./results"

    # --- Visualization ---
    fig_size: Tuple[float, float] = (8.0, 5.0)
    fig_dpi: int = 150
    color_significant: str = "#2ca02c"  # matplotlib default green
    color_null: str = "#ff7f0e"         # matplotlib default orange


def load_config(yaml_path: str = None) -> ExperimentConfig:
    """Return ExperimentConfig from defaults, optionally overridden by YAML."""
    if yaml_path is None:
        return ExperimentConfig()
    import yaml
    with open(yaml_path) as f:
        raw = yaml.safe_load(f) or {}
    d = raw.get("data", {})
    b = raw.get("bootstrap", {})
    o = raw.get("output", {})
    fig = raw.get("figures", {})
    fig_size_raw = fig.get("fig_size", list(ExperimentConfig.fig_size))
    return ExperimentConfig(
        data_path=d.get("data_path", ExperimentConfig.data_path),
        required_cols=tuple(d.get("required_cols", ExperimentConfig.required_cols)),
        n_min=d.get("n_min", ExperimentConfig.n_min),
        n_boot=b.get("n_boot", ExperimentConfig.n_boot),
        seed=b.get("seed", ExperimentConfig.seed),
        min_family_size=b.get("min_family_size", ExperimentConfig.min_family_size),
        figures_dir=o.get("figures_dir", ExperimentConfig.figures_dir),
        results_dir=o.get("results_dir", ExperimentConfig.results_dir),
        fig_size=tuple(fig_size_raw),
        fig_dpi=fig.get("fig_dpi", ExperimentConfig.fig_dpi),
        color_significant=fig.get("color_significant", ExperimentConfig.color_significant),
        color_null=fig.get("color_null", ExperimentConfig.color_null),
    )
```

---

## Hyperparameter Justification

| Parameter | Value | Reason |
|-----------|-------|--------|
| `n_boot` | 5000 | Standard for publication-level bootstrap CIs; Efron & Tibshirani (1993) recommend >= 1000, 5000 gives SE(p) < 0.7% at alpha=0.05 |
| `seed` | 42 | Inherited from H-M1; arbitrary but fixed for reproducibility |
| `min_family_size` | 3 | Bootstrap CI for a group of 2 is degenerate (only 1 permutation); 3 is the practical minimum for meaningful resampling |
| `n_min` | 30 | Inherited from H-M1; standard minimum for parametric approximations; ensures family subsetting still leaves viable data |

---

## Environment Requirements

```
scipy>=1.10.0
pingouin>=0.5.0
pandas>=1.5.0
numpy>=1.23.0
matplotlib>=3.6.0
seaborn>=0.12.0
pyyaml>=6.0
```

Minimum Python: 3.9 (for `tuple` type hints without `from __future__ import annotations`)

---

## Experiment Reproducibility Checklist

- [ ] `seed=42` passed to `numpy.random.default_rng(cfg.seed)` before any bootstrap sampling
- [ ] `n_boot=5000` used consistently — do not vary mid-run
- [ ] `required_cols` validated at load time; raise `ValueError` if any column missing
- [ ] `results_dir` created with `Path(cfg.results_dir).mkdir(parents=True, exist_ok=True)` before writing
- [ ] All results (p-values, CIs, effect sizes) saved to `results_dir` as CSV/JSON alongside figures
- [ ] Config instance serialized to `results_dir/config_used.json` for audit trail
- [ ] Environment pinned via `pip freeze > requirements_used.txt` at run time

---

## Subtasks

Budget: 0 subtasks. Config implementation is integrated into A-1.
