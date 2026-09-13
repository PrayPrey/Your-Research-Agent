# Config: H-M1 — MMLU Scale Covariate Pre-Test

**Applied**: dataclass config pattern (mirrored from H-E1 AuditConfig)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-E1)
**Status**: config classes verified from base code
**Config Files Found**: `docs/youra_research/h-e1/code/config.py`
**Pattern Used**: dataclass + optional yaml loader

---

## Inherited Configuration (Base Hypothesis)

```python
# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE)
@dataclass
class AuditConfig:
    llm_lb_cache: str = "./data/llm_leaderboard_v1/llm.csv"
    n_complete_min: int = 30
    figures_dir: str = "./docs/youra_research/h-e1/figures"
    seed: int = 42
```

**Verified from**: `docs/youra_research/h-e1/code/config.py` (actual implementation)

---

## A-5: Visualization Config [Complexity: 9, Budget: 1 subtask]

**Applied**: dataclass config pattern

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class AnalysisConfig:
    # --- Data ---
    data_path: str = "../../h-e1/code/data/llm_leaderboard_v1/llm.csv"
    required_cols: Tuple[str, ...] = (
        "model_name", "TruthfulQA_MC2", "BBQ_accuracy", "MMLU"
    )

    # --- Gate ---
    r2_threshold: float = 0.05
    n_min: int = 30

    # --- Output ---
    figures_dir: str = "../figures"
    results_dir: str = "./results"
    seed: int = 42

    # --- Figure sizes (width, height) in inches ---
    fig_bar_size: Tuple[float, float] = (7.0, 5.0)
    fig_scatter_size: Tuple[float, float] = (6.0, 5.0)
    fig_heatmap_size: Tuple[float, float] = (5.0, 4.5)
    fig_dpi: int = 150

    # --- Color scheme ---
    color_pass: str = "#2ca02c"    # green — bar above threshold
    color_fail: str = "#d62728"    # red   — bar below threshold
    color_scatter: str = "#1f77b4" # blue  — scatter points
    color_threshold: str = "#ff7f0e"  # orange — threshold line


def load_config(yaml_path: str = None) -> AnalysisConfig:
    if yaml_path is None:
        return AnalysisConfig()
    import yaml
    with open(yaml_path) as f:
        raw = yaml.safe_load(f)
    d = raw.get("data", {})
    g = raw.get("gate", {})
    o = raw.get("output", {})
    fig = raw.get("figures", {})
    return AnalysisConfig(
        data_path=d.get("data_path", AnalysisConfig.data_path),
        r2_threshold=g.get("r2_threshold", AnalysisConfig.r2_threshold),
        n_min=g.get("n_min", AnalysisConfig.n_min),
        figures_dir=o.get("figures_dir", AnalysisConfig.figures_dir),
        results_dir=o.get("results_dir", AnalysisConfig.results_dir),
        seed=raw.get("seed", AnalysisConfig.seed),
        fig_dpi=fig.get("dpi", AnalysisConfig.fig_dpi),
    )
```

### Path Resolution (from `code/` subdirectory)

| Config field | Resolved path (relative to `code/`) |
|---|---|
| `data_path` | `../../h-e1/code/data/llm_leaderboard_v1/llm.csv` |
| `figures_dir` | `../figures` → `docs/youra_research/h-m1/figures/` |
| `results_dir` | `./results` → `docs/youra_research/h-m1/code/results/` |

### Figure Filenames

| Figure | Filename |
|---|---|
| R² bar chart | `h_m1_r2_bar.png` |
| Scatter MMLU × TruthfulQA | `h_m1_scatter_mmlu_truthqa.png` |
| Scatter MMLU × BBQ | `h_m1_scatter_mmlu_bbq.png` |
| Correlation heatmap | `h_m1_heatmap.png` |

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Figure config | AnalysisConfig fields for 4 figure sizes, DPI, color scheme |

---

## requirements.txt

```
scipy>=1.10.0
pingouin>=0.5.0
pandas>=1.5.0
numpy>=1.23.0
matplotlib>=3.6.0
seaborn>=0.12.0
```
