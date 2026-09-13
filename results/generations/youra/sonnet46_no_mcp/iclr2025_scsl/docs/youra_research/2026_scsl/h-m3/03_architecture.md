# Architecture: H-M3
# Transition Epoch t* Reproducibility Analysis

**Hypothesis ID:** H-M3
**Type:** MECHANISM (Post-hoc Statistical Analysis)
**Date:** 2026-05-04

Applied: threshold-based-transition-detection (H-E1 analyze.py pattern)
Applied: dataclass-config (H-E1 config.py pattern)
Applied: flat-module-layout (H-E1 code structure pattern)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/20260504_scsl/h-e1/code/`
**Findings**: H-E1 uses flat module layout with relative imports (`from config import ...`). `find_t_star` and gap area logic already exist in `h-e1/code/analyze.py`. Results output pattern: JSON to `results_dir`. H-M3 mirrors this layout and extends t* analysis with cross-seed variance and bootstrap CI.

---

## File Structure

```
h-m3/code/
    analyze_t_star.py          # main entry point / orchestrator
    data_loader.py             # H-E1 array loading + fallback checkpoint regeneration
    analyzer.py                # TransitionEpochAnalyzer
    statistical_validator.py   # bootstrap CI, gate checks, mechanism verification
    visualizer.py              # matplotlib figures
    results_exporter.py        # JSON/CSV/stdout
    config.py                  # ExperimentConfig dataclass
    configs/
        waterbirds.yaml        # default config
```

---

## Module Definitions

### ExperimentConfig (`config.py`)

**Dependencies**: stdlib only

```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class AnalysisConfig:
    threshold: float = 0.02
    n_consecutive: int = 3
    checkpoint_interval: int = 2
    n_bootstrap: int = 10000
    bootstrap_seed: int = 42
    std_gate_threshold: float = 10.0
    seeds: List[int] = field(default_factory=lambda: [42, 43, 44])

@dataclass
class PathConfig:
    h_e1_results_dir: str = "../../h-e1/results"
    h_e1_checkpoint_dir: str = "../../h-e1/checkpoints"
    waterbirds_root: str = ".data_cache/datasets/waterbirds"
    results_dir: str = "./results"
    figures_dir: str = "./figures"

@dataclass
class ExperimentConfig:
    analysis: AnalysisConfig
    paths: PathConfig

def load_config(config_path: str) -> ExperimentConfig: ...
```

---

### DataLoader (`data_loader.py`)

**Dependencies**: config, numpy, torch (fallback only)

```python
import numpy as np
from typing import Dict, Optional
from config import ExperimentConfig

class DeltaCurveLoader:
    def __init__(self, cfg: ExperimentConfig): ...

    def load(self) -> Dict[int, np.ndarray]:
        """Load delta(t) arrays for all seeds.
        Primary: load from h-e1/results/delta_t_seed{N}.npy or h-e1_results.json.
        Fallback: regenerate from H-E1 checkpoints via probe evaluation.
        Returns: {seed: array of shape (n_checkpoints,)}
        """
        ...

    def _load_from_npy(self, seed: int) -> Optional[np.ndarray]: ...

    def _load_from_json(self) -> Optional[Dict[int, np.ndarray]]:
        """Parse h-e1/results/h-e1_results.json per_seed delta_curve fields."""
        ...

    def _regenerate_from_checkpoints(self, seed: int) -> np.ndarray:
        """Fallback: load ResNet-50 checkpoints, extract features, run probes."""
        ...

    def validate(self, curves: Dict[int, np.ndarray]) -> None:
        """Assert n_checkpoints >= 15, n_seeds >= 3; log shapes."""
        ...
```

---

### TransitionEpochAnalyzer (`analyzer.py`)

**Dependencies**: config, numpy

```python
import numpy as np
from typing import Dict, List, Optional
from config import ExperimentConfig

class TransitionEpochAnalyzer:
    def __init__(self, cfg: ExperimentConfig): ...

    def find_t_star(self, delta_curve: np.ndarray,
                    threshold: Optional[float] = None,
                    n_consecutive: Optional[int] = None) -> Optional[int]:
        """Return first epoch (int) where delta < threshold for n_consecutive
        consecutive checkpoints. Returns None if not found.
        Epoch = checkpoint_index * checkpoint_interval."""
        ...

    def find_t_star_adaptive(self, delta_curve: np.ndarray) -> Optional[int]:
        """Retry with threshold = 0.5 * min(delta_curve) if primary returns None."""
        ...

    def compute_gap_area(self, delta_curve: np.ndarray) -> float:
        """sum(max(delta(t), 0)) across all checkpoints."""
        ...

    def analyze_across_seeds(self, delta_curves: Dict[int, np.ndarray]) -> dict:
        """Run find_t_star and compute_gap_area for each seed.
        Returns: {t_star_per_seed, mean_t_star, std_t_star, gap_areas,
                  mean_gap_area, valid_seed_count, used_adaptive_threshold}
        """
        ...
```

---

### StatisticalValidator (`statistical_validator.py`)

**Dependencies**: analyzer, config, numpy, scipy

```python
import numpy as np
from typing import Dict, List, Optional, Tuple
from config import ExperimentConfig

class StatisticalValidator:
    def __init__(self, cfg: ExperimentConfig): ...

    def bootstrap_std_ci(self, t_star_values: List[float],
                         n_resamples: int = 10000) -> Tuple[float, float]:
        """95% bootstrap CI for std(t*). Returns (ci_low, ci_high)."""
        ...

    def bootstrap_mean_ci(self, values: List[float],
                          n_resamples: int = 10000) -> Tuple[float, float]:
        """95% bootstrap CI for mean (used for gap area). Returns (ci_low, ci_high)."""
        ...

    def evaluate_gate(self, analysis_results: dict) -> dict:
        """Evaluate MUST_WORK gate: std(t*) < 10 across >= 3 seeds.
        Returns: {gate_passed, decision, std_t_star, ci_95_std,
                  partial_pass, insufficient_data, criteria}
        """
        ...

    def verify_mechanism_activated(self, results: dict) -> Tuple[bool, dict]:
        """Check all 4 indicators: all_seeds_found_t_star, std_below_threshold,
        gap_area_positive, curves_loaded. Returns (all_pass, indicators_dict)."""
        ...

    def run_full_validation(self, analysis_results: dict) -> dict:
        """Combine gate evaluation + mechanism verification + CI computation.
        Returns unified validation dict for results export."""
        ...
```

---

### Visualizer (`visualizer.py`)

**Dependencies**: config, numpy, matplotlib, seaborn

```python
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List
from config import ExperimentConfig

class Visualizer:
    def __init__(self, cfg: ExperimentConfig): ...

    def plot_gate_metrics(self, std_t_star: float,
                          t_star_per_seed: Dict[int, float],
                          gate_threshold: float = 10.0) -> str:
        """Bar chart of std(t*) vs threshold with seed scatter. Returns saved path."""
        ...

    def plot_delta_timeline(self, delta_curves: Dict[int, np.ndarray],
                            t_star_per_seed: Dict[int, float],
                            checkpoint_interval: int = 2) -> str:
        """All seeds on same axes with vertical lines at t*. Returns saved path."""
        ...

    def plot_gap_area_boxplot(self, gap_areas: List[float],
                              ci_low: float, ci_high: float) -> str:
        """Box plot of gap area per seed with 95% bootstrap CI band. Returns path."""
        ...

    def plot_cross_dataset(self, waterbirds_std: float,
                           celeba_std: float) -> str:
        """Side-by-side bar chart if CelebA available. Returns path."""
        ...

    def save_all(self, delta_curves: Dict[int, np.ndarray],
                 analysis_results: dict, validation_results: dict) -> List[str]:
        """Run all applicable plots, return list of saved figure paths."""
        ...
```

---

### ResultsExporter (`results_exporter.py`)

**Dependencies**: config, numpy, json, csv

```python
import json
import csv
from typing import Dict, List
import numpy as np
from config import ExperimentConfig

class ResultsExporter:
    def __init__(self, cfg: ExperimentConfig): ...

    def save_json(self, analysis_results: dict, validation_results: dict,
                  figure_paths: List[str]) -> str:
        """Save full results to results/h-m3_results.json. Returns path."""
        ...

    def save_csv(self, delta_curves: Dict[int, np.ndarray],
                 checkpoint_interval: int = 2) -> str:
        """Save per-seed delta(t) curves as CSV for reproducibility. Returns path."""
        ...

    def print_summary(self, analysis_results: dict,
                      validation_results: dict) -> None:
        """Print PASS/FAIL/PARTIAL-PASS gate summary to stdout."""
        ...
```

---

### Main Entry Point (`analyze_t_star.py`)

**Dependencies**: all modules

```python
import argparse
from config import load_config
from data_loader import DeltaCurveLoader
from analyzer import TransitionEpochAnalyzer
from statistical_validator import StatisticalValidator
from visualizer import Visualizer
from results_exporter import ResultsExporter

def main(config_path: str) -> dict:
    """Orchestrate: load -> analyze -> validate -> visualize -> export."""
    ...

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/waterbirds.yaml")
    args = parser.parse_args()
    main(args.config)
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual H-E1 Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| find_t_star (reference) | N/A — reimplemented in analyzer.py | `h-e1/code/analyze.py:67` |
| H-E1 JSON results | File load: `h-e1/results/h-e1_results.json` | `h-e1/code/analyze.py:188` |
| ExperimentConfig pattern | Adapted, not imported | `h-e1/code/config.py` |

**Verified from**: `h-e1/code/` (actual implementation)

**H-E1 JSON schema** (per_seed fields used by DataLoader._load_from_json):
- `per_seed[i].seed`, `.delta_curve`, `.epochs`, `.gap_area`, `.t_star`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | File structure, config.py, configs/waterbirds.yaml, requirements | 5 | 1+1+2+1 |
| A-2 | Data Loader | DeltaCurveLoader: primary JSON/npy load + fallback checkpoint regen | 14 | 3+3+4+4 |
| A-3 | TransitionEpochAnalyzer | find_t_star, adaptive threshold, compute_gap_area, analyze_across_seeds | 12 | 3+2+4+3 |
| A-4 | StatisticalValidator | bootstrap CI (std + mean), gate evaluation, mechanism verification | 14 | 3+3+5+3 |
| A-5 | Visualizer | 4 plot types (gate metrics, delta timeline, boxplot, cross-dataset) | 11 | 3+2+4+2 |
| A-6 | ResultsExporter | JSON save, CSV save, stdout summary | 7 | 2+2+2+1 |
| A-7 | Orchestrator | analyze_t_star.py main(), argparse, end-to-end flow | 8 | 2+3+2+1 |
| A-8 | Integration Test | Run full pipeline on H-E1 JSON outputs; verify gate PASS | 9 | 2+3+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-2, A-4], Medium(9-13): [A-3, A-5, A-8], Low(4-8): [A-1, A-6, A-7]

---

*Architecture for H-M3 — post-hoc statistical analysis, no new model training*
*Generated: 2026-05-04*
