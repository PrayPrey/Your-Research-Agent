# Configuration: H-M3 — Contamination-Accuracy Correlation Analysis

**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr

Applied: dataclass-based experiment config pattern
Applied: JSON serialization with 4-decimal precision pattern
Applied: path-relative result file organization pattern

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field — no existing config classes to verify
**Config Files Found:** None - new config design
**Pattern Used:** dataclass

---

## A-1: Data Loading Config [Complexity: 1, Budget: 1 subtask]

### C-1-1: DataConfig

```python
from dataclasses import dataclass, field
from typing import List

BENCHMARKS: List[str] = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]
MODEL_SIZES: List[str] = ["160m", "410m", "1b", "6.9b"]

BASE = "docs/youra_research"

@dataclass
class DataConfig:
    acc_diff_path: str = f"{BASE}/h-e1/results/accuracy_differentials.json"
    cont_est_path: str = f"{BASE}/h-m1/results/contamination_estimates.json"
    mink_diff_path: str = f"{BASE}/h-m2/results/mink_differentials.json"
    benchmarks: List[str] = field(default_factory=lambda: list(BENCHMARKS))
    model_sizes: List[str] = field(default_factory=lambda: list(MODEL_SIZES))
    allow_missing_mink: bool = True   # H-M2 failed gate; skip if absent
```

YAML schema:
```yaml
data:
  acc_diff_path: docs/youra_research/h-e1/results/accuracy_differentials.json
  cont_est_path: docs/youra_research/h-m1/results/contamination_estimates.json
  mink_diff_path: docs/youra_research/h-m2/results/mink_differentials.json
  benchmarks: [mmlu, hellaswag, arc_challenge, winogrande]
  model_sizes: [160m, 410m, 1b, 6.9b]
  allow_missing_mink: true
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | DataConfig | Path fields + constants + mink optional flag |

---

## A-5: Results & Report Config [Complexity: 2, Budget: 2 subtasks]

### C-5-1: ResultsConfig

```python
@dataclass
class ResultsConfig:
    results_dir: str = "docs/youra_research/h-m3/results"
    correlation_results: str = "correlation_results.json"
    ablation_results: str = "ablation_results.json"
    per_benchmark_summary: str = "per_benchmark_summary.json"
    gate_verdict: str = "gate_verdict.json"
    report: str = "report.md"
    float_precision: int = 4  # decimal places for JSON output

    def path(self, filename: str) -> str:
        import os
        return os.path.join(self.results_dir, filename)
```

YAML schema:
```yaml
results:
  results_dir: docs/youra_research/h-m3/results
  correlation_results: correlation_results.json
  ablation_results: ablation_results.json
  per_benchmark_summary: per_benchmark_summary.json
  gate_verdict: gate_verdict.json
  report: report.md
  float_precision: 4
```

### C-5-2: GateConfig

```python
@dataclass
class GateConfig:
    pearson_r_threshold: float = 0.5
    p_threshold: float = 0.05
    spearman_threshold: float = 0.5
    directional_min: int = 3    # non-standard: ≥3/4 benchmarks must match direction
    explore_threshold: float = 0.3  # EXPLORE verdict if r in [0.3, 0.5)
```

YAML schema:
```yaml
gate:
  pearson_r_threshold: 0.5
  p_threshold: 0.05
  spearman_threshold: 0.5
  directional_min: 3
  explore_threshold: 0.3
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | ResultsConfig | Output paths + float precision + path helper |
| C-5-2 | GateConfig | Pass/explore/fail thresholds |

---

## A-6: Main Pipeline Config [Complexity: 2, Budget: 2 subtasks]

### C-6-1: ExperimentConfig (master)

```python
@dataclass
class ExperimentConfig:
    data: DataConfig = field(default_factory=DataConfig)
    results: ResultsConfig = field(default_factory=ResultsConfig)
    gate: GateConfig = field(default_factory=GateConfig)
    seed: int = 42
    n_resamples: int = 1000
    figure_dpi: int = 150
    figure_format: str = "png"
    figure_dir: str = "docs/youra_research/h-m3/figures"
```

YAML schema (all fields):
```yaml
seed: 42
n_resamples: 1000
figure_dpi: 150
figure_format: png
figure_dir: docs/youra_research/h-m3/figures
data:
  acc_diff_path: docs/youra_research/h-e1/results/accuracy_differentials.json
  cont_est_path: docs/youra_research/h-m1/results/contamination_estimates.json
  mink_diff_path: docs/youra_research/h-m2/results/mink_differentials.json
  benchmarks: [mmlu, hellaswag, arc_challenge, winogrande]
  model_sizes: [160m, 410m, 1b, 6.9b]
  allow_missing_mink: true
results:
  results_dir: docs/youra_research/h-m3/results
  correlation_results: correlation_results.json
  ablation_results: ablation_results.json
  per_benchmark_summary: per_benchmark_summary.json
  gate_verdict: gate_verdict.json
  report: report.md
  float_precision: 4
gate:
  pearson_r_threshold: 0.5
  p_threshold: 0.05
  spearman_threshold: 0.5
  directional_min: 3
  explore_threshold: 0.3
```

### C-6-2: Bootstrap and Figure Config

Inline in ExperimentConfig above. Loader utility:

```python
def load_config(yaml_path: str | None = None) -> ExperimentConfig:
    if yaml_path is None:
        return ExperimentConfig()
    import yaml
    from dataclasses import replace
    with open(yaml_path) as f:
        d = yaml.safe_load(f)
    data = DataConfig(**d.pop("data", {}))
    results = ResultsConfig(**d.pop("results", {}))
    gate = GateConfig(**d.pop("gate", {}))
    return ExperimentConfig(data=data, results=results, gate=gate, **d)
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | ExperimentConfig | Master dataclass composing all sub-configs |
| C-6-2 | Bootstrap/Figure config + loader | n_resamples, seed, dpi, format, figure_dir, YAML loader |
