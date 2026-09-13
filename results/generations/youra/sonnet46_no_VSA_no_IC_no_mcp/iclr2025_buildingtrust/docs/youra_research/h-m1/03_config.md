---
hypothesis_id: H-M1
date: "2026-08-25"
author: Anonymous
---

# Configuration: H-M1

Applied: dataclass config pattern with verified field names from h-e1/code/config.py

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config classes verified from h-e1/code/config.py actual code
**Config Files Found**: `docs/youra_research/h-e1/code/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

```python
# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE)
@dataclass
class ExperimentConfig:
    seed: int = 1
    batch_size: int = 8
    n_bins_primary: int = 15
    n_bins_secondary: int = 10
    min_examples_per_cell: int = 50
    subsample_clean: int = 200
    subsample_adv: int = 200
    prevalidation_n: int = 10
    models: List[str] = field(default_factory=lambda: ["meta-llama/Llama-2-7b-hf"])
    use_4bit_threshold_gb: float = 40.0
    max_confidence_degenerate: float = 0.999
    non_degenerate_fraction: float = 0.90
    min_confidence_uniform: float = 0.30
    prob_sum_tolerance: float = 1e-3
    ece_plausible_min: float = 0.0
    ece_plausible_max: float = 0.5
    clean_ece_min: float = 0.05
    clean_ece_max: float = 0.15
    min_models_sanity: int = 1
    gate_min_cells: int = 1
    results_dir: str = "docs/youra_research/h-e1/results"
    figures_dir: str = "docs/youra_research/h-e1/figures"
    errors_log: str = "docs/youra_research/h-e1/results/errors.log"
```

**Verified from**: `docs/youra_research/h-e1/code/config.py` (actual implementation)

---

## H-M1 Global Constants

```python
# docs/youra_research/h-m1/code/config.py

# Measured constants — do not modify
CLEAN_ECE_H_E1: float = 0.279    # H-E1 measured clean ECE
DELTA_ECE_H_E1: float = 0.071    # H-E1 overall NLI ΔECE

# Gate threshold
PRESERVE_RATE_GATE: float = 0.80

# Analysis parameters
SEED: int = 1
N_BINS: int = 15
SUBSAMPLE_CLEAN: int = 2000

# Paths
H_E1_CODE_PATH: str = "docs/youra_research/h-e1/code"
H_E1_RESULTS_DIR: str = "docs/youra_research/h-e1/results"
RESULTS_DIR: str = "docs/youra_research/h-m1/results"
FIGURES_DIR: str = "docs/youra_research/h-m1/figures"

SPLITS: list = ["advglue_mnli", "anli_r1", "anli_r2", "anli_r3", "mnli"]
```

---

## A-2: CacheLoader Config [Complexity: 9, Budget: 1 subtask]

Applied: dataclass config pattern

```python
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class CacheLoaderConfig:
    results_dir: str = "docs/youra_research/h-e1/results"
    splits: List[str] = field(default_factory=lambda: [
        "advglue_mnli", "anli_r1", "anli_r2", "anli_r3", "mnli"
    ])
    # Expected example counts per split for integrity check (FR-1.2)
    expected_counts: Dict[str, int] = field(default_factory=lambda: {
        "advglue_mnli": 1200,
        "anli_r1": 1000,
        "anli_r2": 1000,
        "anli_r3": 1000,
        "mnli": 2000,
    })
    required_fields: List[str] = field(default_factory=lambda: [
        "conf", "correct", "pred", "label"
    ])
    # Fallback: re-run H-E1 loader if cache missing
    fallback_h_e1_code_path: str = "docs/youra_research/h-e1/code"
    # Count mismatch tolerance before warning (fraction)
    count_tolerance: float = 0.05
```

YAML equivalent:
```yaml
cache_loader:
  results_dir: "docs/youra_research/h-e1/results"
  splits: [advglue_mnli, anli_r1, anli_r2, anli_r3, mnli]
  expected_counts:
    advglue_mnli: 1200
    anli_r1: 1000
    anli_r2: 1000
    anli_r3: 1000
    mnli: 2000
  required_fields: [conf, correct, pred, label]
  fallback_h_e1_code_path: "docs/youra_research/h-e1/code"
  count_tolerance: 0.05
```

Validation constraints:
- `count_tolerance` in [0.0, 0.20]
- All `required_fields` must be present or FileNotFoundError raised

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | CacheLoaderConfig | Dataclass with expected_counts, required_fields, fallback path |

---

## A-4: Stratifier Config [Complexity: 9, Budget: 1 subtask]

Applied: dataclass config pattern

```python
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class StratifierConfig:
    preserve_rate_gate: float = 0.80
    # Stratum label mapping per split
    stratum_labels: Dict[str, str] = field(default_factory=lambda: {
        "advglue_mnli": "high_pres_all",
        "anli_r1": "anli_r1_high_pres",
        "anli_r2": "anli_r2_high_pres",
        "anli_r3": "anli_r3_high_pres",
        "mnli": "clean_baseline",
    })
    # Secondary stratification: by perturbation type if metadata available
    secondary_stratification_advglue: bool = True   # word-level vs sentence-level
    secondary_stratification_anli_rounds: bool = True  # R1/R2/R3 gradient
    # All examples in high-preservation stratum by construction (FR-3.1)
    use_construction_guarantee: bool = True
```

YAML equivalent:
```yaml
stratifier:
  preserve_rate_gate: 0.80
  stratum_labels:
    advglue_mnli: high_pres_all
    anli_r1: anli_r1_high_pres
    anli_r2: anli_r2_high_pres
    anli_r3: anli_r3_high_pres
    mnli: clean_baseline
  secondary_stratification_advglue: true
  secondary_stratification_anli_rounds: true
  use_construction_guarantee: true
```

Validation constraints:
- `preserve_rate_gate` in [0.0, 1.0]

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | StratifierConfig | Dataclass with gate threshold, stratum labels, secondary flags |

---

## A-8: Visualizer Config [Complexity: 12, Budget: 1 subtask]

Applied: dataclass config pattern

```python
from dataclasses import dataclass, field
from typing import Tuple, Dict

@dataclass
class VisualizerConfig:
    figures_dir: str = "docs/youra_research/h-m1/figures"
    dpi: int = 150
    # Figure sizes (width, height) in inches
    bar_chart_figsize: Tuple[float, float] = (8.0, 5.0)
    line_chart_figsize: Tuple[float, float] = (6.0, 4.0)
    reliability_figsize: Tuple[float, float] = (10.0, 6.0)
    # Color scheme
    color_clean: str = "#4C72B0"    # blue for clean baseline
    color_adv: str = "#DD8452"      # orange for adversarial
    color_threshold: str = "#C44E52"  # red for gate threshold lines
    color_anli: Dict[str, str] = field(default_factory=lambda: {
        "anli_r1": "#55A868",
        "anli_r2": "#8172B2",
        "anli_r3": "#937860",
    })
    # Output filenames
    preservation_rate_filename: str = "preservation_rate_by_benchmark.png"
    stratum_ece_filename: str = "stratum_ece_comparison.png"
    anli_gradient_filename: str = "anli_round_gradient.png"
    reliability_diagram_filename: str = "reliability_diagrams.png"
```

YAML equivalent:
```yaml
visualizer:
  figures_dir: "docs/youra_research/h-m1/figures"
  dpi: 150
  bar_chart_figsize: [8.0, 5.0]
  line_chart_figsize: [6.0, 4.0]
  reliability_figsize: [10.0, 6.0]
  color_clean: "#4C72B0"
  color_adv: "#DD8452"
  color_threshold: "#C44E52"
  color_anli:
    anli_r1: "#55A868"
    anli_r2: "#8172B2"
    anli_r3: "#937860"
  preservation_rate_filename: preservation_rate_by_benchmark.png
  stratum_ece_filename: stratum_ece_comparison.png
  anli_gradient_filename: anli_round_gradient.png
  reliability_diagram_filename: reliability_diagrams.png
```

Validation constraints:
- `dpi` in [72, 300]

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | VisualizerConfig | Dataclass with figure sizes, DPI, color schemes, output paths |

---

## H-M1 ExperimentConfig [Budget: 1 subtask]

```python
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class H_M1_ExperimentConfig:
    # --- Inherited from H-E1 (verified field names) ---
    seed: int = 1
    n_bins_primary: int = 15       # primary ECE bin count; ablation: [10, 15, 20]

    # --- H-M1 constants (measured, do not modify) ---
    clean_ece_h_e1: float = 0.279
    delta_ece_h_e1: float = 0.071
    delta_ece_consistency_tol: float = 0.05  # |ΔECE_high_pres - 0.071| < 0.05

    # --- Gate thresholds ---
    preserve_rate_gate: float = 0.80

    # --- Analysis parameters ---
    subsample_clean: int = 2000    # Non-standard: H-E1 used 200; H-M1 uses full 2000 for clean baseline
    n_bins_ablation: List[int] = field(default_factory=lambda: [10, 15, 20])
    splits: List[str] = field(default_factory=lambda: [
        "advglue_mnli", "anli_r1", "anli_r2", "anli_r3", "mnli"
    ])

    # --- Paths ---
    h_e1_code_path: str = "docs/youra_research/h-e1/code"
    h_e1_results_dir: str = "docs/youra_research/h-e1/results"
    results_dir: str = "docs/youra_research/h-m1/results"
    figures_dir: str = "docs/youra_research/h-m1/figures"

    # --- Sub-configs ---
    cache_loader: CacheLoaderConfig = field(default_factory=CacheLoaderConfig)
    stratifier: StratifierConfig = field(default_factory=StratifierConfig)
    visualizer: VisualizerConfig = field(default_factory=VisualizerConfig)
```

Ablation overrides (copy-paste ready):
```python
# Bin count ablation
cfg_10bins = H_M1_ExperimentConfig(n_bins_primary=10)
cfg_20bins = H_M1_ExperimentConfig(n_bins_primary=20)
```

Validation constraints:
- `n_bins_primary` in [10, 15, 20]
- `preserve_rate_gate` in [0.0, 1.0]
- `subsample_clean` >= 1000

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-HM1-1 | H_M1_ExperimentConfig | Top-level dataclass composing all sub-configs, verified H-E1 field names |
