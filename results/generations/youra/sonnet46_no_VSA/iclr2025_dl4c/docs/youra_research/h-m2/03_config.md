# Config: H-M2
# Spearman Correlation — Embedding Alignment vs Pass@1 Rank

Applied: Standard Python dataclass pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — new config design (H-M2 is pure statistical analysis, no base hypothesis code)
**Config Files Found**: None — new config
**Pattern Used**: dataclass

---

## C-6-1: Statistical Config [Complexity: 5, Budget: 1]

**Applied**: Standard scipy permutation test defaults

### Configuration

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class StatTestConfig:
    n_resamples: int = 10000
    random_state: int = 42
    significance_threshold: float = 0.05
    alternative: str = "greater"          # one-sided ρ > 0
    bootstrap_n: int = 1000
    min_rank_variation: int = 2           # min unique values in pass@1 for valid test
    ci_percentiles: List[float] = field(default_factory=lambda: [2.5, 97.5])
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1-1 | StatTestConfig | Dataclass for permutation test + bootstrap CI parameters |

---

## C-6-2: Visualization + Path + Experiment Config [Complexity: 5, Budget: 1]

**Applied**: Standard matplotlib/seaborn defaults

### Configuration

```python
@dataclass
class PathConfig:
    # Input paths (relative to project root)
    h_e1_results: str = "docs/youra_research/h-e1/experiment_results.json"
    h_e2_csv: str = "docs/youra_research/h-e2/results/all_results.csv"
    h_c1_json: str = "docs/youra_research/h-c1/results/pass_at_1_7b.json"  # optional

    # Output dirs
    results_dir: str = "docs/youra_research/h-m2/results"
    figures_dir: str = "docs/youra_research/h-m2/figures"
    null_dist_dir: str = "docs/youra_research/h-m2/results/null_distributions"


@dataclass
class VizConfig:
    dpi: int = 150
    # Figure sizes (width, height) in inches
    fig1_size: tuple = (10, 5)   # rho bar chart
    fig2_size: tuple = (14, 8)   # scatter panels (2×4 grid)
    fig3_size: tuple = (8, 5)    # null distribution histogram
    fig4_size: tuple = (8, 6)    # rank heatmap
    fig5_size: tuple = (6, 6)    # dual-encoder scatter

    # Source condition colors (CRITICAL: index order matches CONDITIONS list)
    # Index 0: humaneval_only (HE), 1: mbpp_only (MB), 2: leetcode_only (LC), 3: equal_mix (EQ)
    condition_colors: List[str] = field(default_factory=lambda: [
        "#1f77b4",  # HE — blue
        "#ff7f0e",  # MB — orange
        "#2ca02c",  # LC — green
        "#d62728",  # EQ — red
    ])
    significance_marker: str = "*"   # plotted when p < significance_threshold
    significance_fontsize: int = 14


@dataclass
class ExperimentConfig:
    # CRITICAL: index order must match H-E1 sim_matrices row order and H-E2 CSV condition values
    # Index 0: humaneval_only (HE), 1: mbpp_only (MB), 2: leetcode_only (LC), 3: equal_mix (EQ)
    source_conditions: List[str] = field(default_factory=lambda: [
        "humaneval_only",
        "mbpp_only",
        "leetcode_only",
        "equal_mix",
    ])

    # H-E1 source keys (map 1:1 to source_conditions by index)
    h_e1_source_keys: List[str] = field(default_factory=lambda: [
        "humaneval_train",
        "mbpp_train",
        "leetcode",
        "equal_mix",
    ])

    # CRITICAL: index 0 = humaneval_plus (has data), index 1 = mbpp_plus (CANNOT_TEST)
    benchmarks: List[str] = field(default_factory=lambda: [
        "humaneval_plus",
        "mbpp_plus",
    ])

    # H-E2 CSV benchmark label (maps to benchmarks list by index)
    h_e2_benchmark_keys: List[str] = field(default_factory=lambda: [
        "humaneval",    # index 0 — data available
        "mbpp_plus",    # index 1 — CANNOT_TEST (no rows in H-E2 CSV)
    ])

    encoders: List[str] = field(default_factory=lambda: ["codebert", "minilm"])

    model_sizes: List[str] = field(default_factory=lambda: ["1b"])  # "7b" added if H-C1 present

    stat: StatTestConfig = field(default_factory=StatTestConfig)
    viz: VizConfig = field(default_factory=VizConfig)
    paths: PathConfig = field(default_factory=PathConfig)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-2-1 | VizConfig + PathConfig + ExperimentConfig | All remaining config dataclasses |

---

## Usage (copy-paste for run_experiment.py)

```python
from dataclasses import dataclass, field
from typing import List

# -- paste all dataclass definitions above --

CFG = ExperimentConfig()

# Access examples:
# CFG.stat.n_resamples       → 10000
# CFG.stat.random_state      → 42
# CFG.paths.h_e1_results     → "docs/youra_research/h-e1/experiment_results.json"
# CFG.viz.condition_colors[0] → "#1f77b4"  (HE blue)
# CFG.source_conditions[0]   → "humaneval_only"
# CFG.benchmarks[1]          → "mbpp_plus"  (CANNOT_TEST)
```
