---
hypothesis_id: h-m2
hypothesis_type: MECHANISM
phase: Phase 3
date: 2026-03-21
applied_patterns: ["Statistical analysis pipeline", "Artifact reuse pattern", "Multi-condition testing"]
---

# Architecture: H-M2 Trajectory Divergence

**Hypothesis:** Different initial weight configurations lead to different optimization trajectories and final model states.

**Gate Type:** MUST_WORK

**Success Criteria:**
- Primary: Mean pairwise final weight distance > 0 with p < 0.05 for ALL 4 conditions
- Secondary: CV of final epoch loss ≥ 1% for ≥2/4 conditions

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Analyzed h-m1 code structure for statistical analysis patterns
**Analyzed Path:** `docs/youra_research/20260318_question/h-m1/code/`
**Findings:** Reusable statistical infrastructure (pairwise distance, t-test, visualization). H-M2 extends pattern to analyze training artifacts instead of initialization.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From h-m1 Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| compute_pairwise_distances | `from h_m1.code.statistics import compute_pairwise_distances` | `h-m1/code/statistics.py` |
| test_independence | `from h_m1.code.statistics import test_independence` | `h-m1/code/statistics.py` |
| plot_distance_distribution | `from h_m1.code.viz_h_m1 import plot_distance_distribution` | `h-m1/code/viz_h_m1.py` |

**Verified from:** `h-m1/code/` (actual implementation)

**Note:** H-M2 reuses h-m1 statistical infrastructure for pairwise distance and significance testing. New modules added for artifact loading and loss trajectory analysis.

---

## System Architecture

### File Structure

```
h-m2/
└── code/
    ├── config.py             # Experiment configuration
    ├── artifact_loader.py    # Load h-m1 weights/losses
    ├── trajectory_analyzer.py # Loss CV, divergence metrics
    ├── visualize.py          # 4-panel gate metrics figure
    └── run_analysis.py       # Main entry point
```

---

## Module Specifications

### 1. Configuration (`code/config.py`)

**Dependencies:** None

```python
from dataclasses import dataclass
from pathlib import Path
from typing import List

@dataclass
class H_M1_ArtifactConfig:
    h_m1_results_path: Path
    conditions: List[str]
    n_seeds: int
    n_epochs: int

@dataclass
class AnalysisConfig:
    h_m1_config: H_M1_ArtifactConfig
    output_dir: Path
    primary_alpha: float
    secondary_cv_threshold: float

def get_default_config() -> AnalysisConfig: ...
```

---

### 2. Artifact Loader (`code/artifact_loader.py`)

**Dependencies:** torch, numpy, pathlib

```python
import torch
import numpy as np
from pathlib import Path
from typing import Dict, Tuple

def load_initial_weights(
    h_m1_results_path: Path,
    condition: str,
    n_seeds: int
) -> Dict[int, torch.Tensor]: ...

def load_final_weights(
    h_m1_results_path: Path,
    condition: str,
    n_seeds: int
) -> Dict[int, torch.Tensor]: ...

def load_loss_trajectories(
    h_m1_results_path: Path,
    condition: str,
    n_seeds: int
) -> np.ndarray: ...

def verify_all_artifacts_exist(
    h_m1_results_path: Path,
    conditions: List[str],
    n_seeds: int
) -> Tuple[bool, List[str]]: ...
```

---

### 3. Trajectory Analyzer (`code/trajectory_analyzer.py`)

**Dependencies:** numpy

```python
import numpy as np
from typing import Dict

def calculate_loss_cv(loss_trajectories: np.ndarray) -> float: ...

def analyze_trajectory_divergence(
    loss_trajectories: np.ndarray
) -> Dict[str, float]: ...

def compute_epoch_wise_cv(
    loss_trajectories: np.ndarray
) -> np.ndarray: ...
```

---

### 4. Visualization (`code/visualize.py`)

**Dependencies:** matplotlib, numpy

```python
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict

def plot_gate_metrics_comparison(
    all_results: Dict[str, Dict],
    save_path: Path
) -> None: ...

def plot_distance_distribution_panel(
    ax: plt.Axes,
    distances: np.ndarray,
    mean_dist: float,
    p_value: float,
    condition: str
) -> None: ...

def plot_loss_trajectory_fan(
    ax: plt.Axes,
    loss_trajectories: np.ndarray,
    cv_final: float,
    condition: str
) -> None: ...
```

---

### 5. Analysis Runner (`code/run_analysis.py`)

**Dependencies:** artifact_loader, trajectory_analyzer, visualize, config, h_m1.code.statistics

```python
import sys
import json
import numpy as np
from pathlib import Path
from typing import Dict

def run_single_condition_analysis(
    condition: str,
    config: AnalysisConfig
) -> Dict[str, float]: ...

def run_all_conditions(config: AnalysisConfig) -> Dict[str, Dict[str, float]]: ...

def validate_gate(results: Dict[str, Dict[str, float]]) -> Tuple[bool, str]: ...

def save_results(
    results: Dict[str, Dict[str, float]],
    gate_status: Dict[str, bool],
    output_dir: Path
) -> None: ...

def generate_validation_report(
    results: Dict[str, Dict[str, float]],
    gate_passed: bool,
    output_dir: Path
) -> None: ...

def main() -> None: ...
```

---

## Data Flow

```
H-M1 Artifacts (360 files)
  → verify_all_artifacts_exist()
  → For each condition:
    → load_initial_weights() → Dict[seed, params]
    → load_final_weights() → Dict[seed, params]
    → load_loss_trajectories() → (30, 10) array
    → compute_pairwise_distances(final_weights) → (435,) distances
    → test_independence(distances) → {mean, p_value}
    → calculate_loss_cv(trajectories) → cv_percent
    → Store metrics
  → validate_gate(all_results) → PASS/FAIL
  → plot_gate_metrics_comparison() → figure
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Environment Setup | Config, h-m1 path setup | 5 | 2+1+1+1 |
| A-2 | Artifact Verification | File existence checker with error reporting | 8 | 2+2+2+2 |
| A-3 | Weight Loader | Load initial/final weights from h-m1 | 9 | 3+2+2+2 |
| A-4 | Loss Loader | Load loss trajectories from h-m1 | 7 | 2+2+2+1 |
| A-5 | CV Calculator | Coefficient of variation for trajectories | 6 | 2+1+2+1 |
| A-6 | Distance & Significance | Reuse h-m1 stats, apply to final weights | 8 | 2+2+3+1 |
| A-7 | Multi-Condition Orchestrator | Run all 4 conditions, aggregate | 10 | 3+3+2+2 |
| A-8 | Gate Validation | Primary/secondary criteria checking | 7 | 2+1+3+1 |
| A-9 | 4-Panel Visualization | Distance histograms + trajectory fans | 12 | 3+2+5+2 |
| A-10 | Results Logging | JSON output, validation report | 6 | 2+1+2+1 |
| A-11 | Integration Testing | End-to-end artifact flow test | 8 | 2+2+2+2 |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-7, A-9], Low(4-8): [A-1, A-2, A-4, A-5, A-6, A-8, A-10, A-11]

**Total Complexity:** 86 (11 tasks)

---

## Complexity Scoring Details

### A-1: Environment Setup (5)
- Module_Size: 2 (config dataclasses, path setup)
- Dependencies: 1 (pathlib only)
- Algorithm: 1 (simple config)
- Integration: 1 (standalone)

### A-2: Artifact Verification (8)
- Module_Size: 2 (file existence checks)
- Dependencies: 2 (pathlib, typing)
- Algorithm: 2 (nested file path construction)
- Integration: 2 (validates entire pipeline input)

### A-3: Weight Loader (9)
- Module_Size: 3 (initial + final loaders, error handling)
- Dependencies: 2 (torch, pathlib)
- Algorithm: 2 (dict construction from files)
- Integration: 2 (reads external h-m1 artifacts)

### A-4: Loss Loader (7)
- Module_Size: 2 (numpy array loading)
- Dependencies: 2 (numpy, pathlib)
- Algorithm: 2 (array stacking)
- Integration: 1 (file I/O)

### A-5: CV Calculator (6)
- Module_Size: 2 (CV formula, epoch-wise)
- Dependencies: 1 (numpy)
- Algorithm: 2 (std/mean calculation)
- Integration: 1 (pure function)

### A-6: Distance & Significance (8)
- Module_Size: 2 (import h-m1 functions, adapt)
- Dependencies: 2 (h_m1.code.statistics, scipy)
- Algorithm: 3 (t-test on final weights)
- Integration: 1 (reuse existing code)

### A-7: Multi-Condition Orchestrator (10)
- Module_Size: 3 (4 condition loops, result aggregation)
- Dependencies: 3 (loader, analyzer, stats)
- Algorithm: 2 (nested iteration)
- Integration: 2 (coordinates all modules)

### A-8: Gate Validation (7)
- Module_Size: 2 (primary/secondary logic)
- Dependencies: 1 (typing)
- Algorithm: 3 (multi-criterion evaluation)
- Integration: 1 (reads results dict)

### A-9: 4-Panel Visualization (12)
- Module_Size: 3 (2 plot types × 4 conditions)
- Dependencies: 2 (matplotlib, numpy)
- Algorithm: 5 (subplot layout, histogram, trajectory fan, annotations)
- Integration: 2 (reads results + trajectories)

### A-10: Results Logging (6)
- Module_Size: 2 (JSON serialization, report)
- Dependencies: 1 (json)
- Algorithm: 2 (format results, gate summary)
- Integration: 1 (file output)

### A-11: Integration Testing (8)
- Module_Size: 2 (test suite, end-to-end)
- Dependencies: 2 (pytest, all modules)
- Algorithm: 2 (mock artifacts, validation)
- Integration: 2 (full pipeline)

---

## Implementation Notes

### Artifact Loading (FR-1)

```python
def load_final_weights(h_m1_results_path: Path, condition: str, n_seeds: int) -> Dict[int, torch.Tensor]:
    """Load final weights from h-m1 experiment."""
    weights_dict = {}
    for seed in range(n_seeds):
        weight_path = h_m1_results_path / condition / f"seed_{seed}" / "final_weights.pt"
        if not weight_path.exists():
            raise FileNotFoundError(f"Missing: {weight_path}")
        weights_dict[seed] = torch.load(weight_path, map_location='cpu')
    return weights_dict
```

### Loss CV Calculation (FR-4)

```python
def calculate_loss_cv(loss_trajectories: np.ndarray) -> float:
    """
    Compute coefficient of variation for final epoch losses.

    Args:
        loss_trajectories: (30, 10) array of losses

    Returns:
        CV as percentage
    """
    final_losses = loss_trajectories[:, -1]
    cv = (np.std(final_losses) / np.mean(final_losses)) * 100
    return float(cv)
```

### Gate Validation (FR-6)

```python
def validate_gate(results: Dict[str, Dict[str, float]]) -> Tuple[bool, str]:
    """Determine MUST_WORK gate pass/fail."""
    # Primary: ALL 4 conditions p < 0.05
    test1_count = sum(
        r['final_distance_p_value'] < 0.05 and r['mean_final_distance'] > 0
        for r in results.values()
    )
    primary_pass = (test1_count == 4)

    # Secondary: ≥2/4 conditions CV ≥ 1%
    test2_count = sum(r['cv_final_loss_percent'] >= 1.0 for r in results.values())
    secondary_pass = (test2_count >= 2)

    gate_passed = primary_pass  # MUST_WORK only requires primary
    summary = f"Primary: {test1_count}/4 conditions, Secondary: {test2_count}/4 conditions"

    return gate_passed, summary
```

### 4-Panel Figure (FR-7)

```python
def plot_gate_metrics_comparison(all_results: Dict, save_path: Path) -> None:
    """Generate 2×2 grid: distance distributions + trajectory fans."""
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    conditions = ['1layer_mnist', '1layer_fashion_mnist', '2layer_mnist', '2layer_fashion_mnist']

    for i, condition in enumerate(conditions):
        # Top row: Final weight distance distribution
        plot_distance_distribution_panel(
            axes[0, i],
            all_results[condition]['distances'],
            all_results[condition]['mean_final_distance'],
            all_results[condition]['final_distance_p_value'],
            condition
        )

        # Bottom row: Loss trajectory fan
        plot_loss_trajectory_fan(
            axes[1, i],
            all_results[condition]['loss_trajectories'],
            all_results[condition]['cv_final_loss_percent'],
            condition
        )

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
```

---

## Success Criteria Mapping

| Criterion | Module | Metric |
|-----------|--------|--------|
| Mean final distance > 0 | artifact_loader + h_m1.statistics | mean_final_distance |
| p < 0.05 (all 4 conditions) | h_m1.statistics | final_distance_p_value |
| CV ≥ 1% (≥2/4 conditions) | trajectory_analyzer | cv_final_loss_percent |
| All artifacts loaded | artifact_loader | verify_all_artifacts_exist |
| Gate validation | run_analysis | validate_gate |

---

## Risk Mitigation

### R1: H-M1 Artifacts Incomplete
- **Mitigation:** Early file existence check before any analysis
- **Module:** artifact_loader.py (verify_all_artifacts_exist)

### R2: Import Path Issues (h-m1 modules)
- **Mitigation:** Add h-m1 code directory to sys.path
- **Module:** run_analysis.py (path setup)

### R3: Numerical Precision (Float64)
- **Mitigation:** Use float64 for distance arrays
- **Module:** h_m1.code.statistics (reused)

### R4: Memory (360 files)
- **Mitigation:** Load per-condition, not all at once
- **Module:** run_analysis.py (single_condition loop)

---

*Generated by Phase 3 Architecture Agent*
*Applied: Statistical analysis pipeline, Artifact reuse pattern*
*Next: Phase 4 Implementation (Epic Task Execution)*
