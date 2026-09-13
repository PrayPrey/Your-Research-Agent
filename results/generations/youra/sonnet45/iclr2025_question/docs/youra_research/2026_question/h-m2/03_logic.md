# Logic Specification: h-m2 Trajectory Divergence

**Date:** 2026-03-21
**Hypothesis ID:** h-m2 (MECHANISM)
**Version:** 1.0
**Phase:** 3 (Implementation Planning)

Applied: Artifact reuse pattern, PyTorch weight loading, Statistical significance testing

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** API signatures verified from h-m1 actual code
**Analyzed Path:** `docs/youra_research/20260318_question/h-m1/code/`
**Relevant Symbols:** compute_pairwise_distances, test_independence, plot_distance_distribution, ExperimentConfig

**Key Insight:** H-M2 reuses h-m1's statistical infrastructure for pairwise distance computation and significance testing, applying it to final weights instead of initial weights.

---

## External Dependencies API (Base Hypothesis)

### API Signatures (From h-m1 Actual Code)

**Verified from:** `h-m1/code/statistics.py`, `h-m1/code/viz_h_m1.py`

```python
# From: h-m1/code/statistics.py
def compute_pairwise_distances(models_dict: Dict[int, torch.Tensor]) -> np.ndarray:
    """
    Compute Euclidean distances between all parameter pairs.

    Args:
        models_dict: Dict mapping seed -> parameter tensor
    Returns:
        Array of pairwise distances (n choose 2)
    """
    ...

def test_independence(distances: np.ndarray) -> Dict[str, float]:
    """
    Statistical test: H0: mean=0 vs H1: mean>0

    Returns:
        Dict with keys: mean_distance, std_distance, t_statistic, p_value, n_pairs
    """
    ...

# From: h-m1/code/viz_h_m1.py
def plot_distance_distribution(
    distances: np.ndarray,
    condition: str,
    save_path: Path,
    mean_dist: float = None,
    p_value: float = None
) -> None:
    """Generate histogram of pairwise distance distribution."""
    ...

def plot_condition_comparison(
    all_results: Dict[str, Dict],
    save_path: Path
) -> None:
    """Generate boxplot comparing distributions across conditions."""
    ...
```

**Import Paths:**
```python
from h_m1.code.statistics import compute_pairwise_distances, test_independence
from h_m1.code.viz_h_m1 import plot_distance_distribution, plot_condition_comparison
```

---

## A-1: Configuration Module [Complexity: 5, Budget: 5]

Applied: Dataclass pattern from h-m1

### API Signatures

```python
from dataclasses import dataclass
from pathlib import Path
from typing import List

@dataclass
class H_M1_ArtifactConfig:
    """Configuration for h-m1 artifact paths."""
    h_m1_results_path: Path
    conditions: List[str]  # ['1layer_mnist', '1layer_fashion_mnist', '2layer_mnist', '2layer_fashion_mnist']
    n_seeds: int
    n_epochs: int

@dataclass
class AnalysisConfig:
    """Main configuration for h-m2 analysis."""
    h_m1_config: H_M1_ArtifactConfig
    output_dir: Path
    figures_dir: Path
    primary_alpha: float = 0.05
    secondary_cv_threshold: float = 1.0

def get_default_config() -> AnalysisConfig:
    """Return default configuration with h-m1 path."""
    ...
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | H_M1_ArtifactConfig | Path config dataclass |
| L-1-2 | AnalysisConfig | Main config with thresholds |
| L-1-3 | get_default_config | Factory with h-m1 path |
| L-1-4 | Directory creation | Ensure output/figures exist |
| L-1-5 | Validation | Check h-m1 path exists |

---

## A-2: Artifact Verification Module [Complexity: 8, Budget: 8]

Applied: Early failure pattern

### API Signatures

```python
from pathlib import Path
from typing import Tuple, List

def verify_all_artifacts_exist(
    h_m1_results_path: Path,
    conditions: List[str],
    n_seeds: int
) -> Tuple[bool, List[str]]:
    """
    Verify all 360 h-m1 artifact files exist.

    Returns:
        (all_exist: bool, missing_files: List[str])
    """
    ...

def list_missing_artifacts(
    h_m1_results_path: Path,
    conditions: List[str],
    n_seeds: int
) -> List[str]:
    """Return list of missing file paths."""
    ...
```

### Expected File Structure

```
h-m1/results/{condition}/seed_{i}/
  - initial_weights.pt    # [n_params] flattened tensor
  - final_weights.pt      # [n_params] flattened tensor
  - loss_history.npy      # [10] training losses
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | File path construction | Build expected paths |
| L-2-2 | Existence checker | Loop all 360 files |
| L-2-3 | Missing file collector | Track missing files |
| L-2-4 | Error reporting | Clear error messages |
| L-2-5 | Path validation | Validate h-m1 base path |
| L-2-6 | Condition validation | Check condition names |
| L-2-7 | Early failure | Fail before loading |
| L-2-8 | Summary report | Print verification summary |

---

## A-3: Weight Loader Module [Complexity: 9, Budget: 9]

Applied: PyTorch checkpoint loading

### API Signatures

```python
import torch
from pathlib import Path
from typing import Dict

def load_initial_weights(
    h_m1_results_path: Path,
    condition: str,
    n_seeds: int
) -> Dict[int, torch.Tensor]:
    """
    Load initial weights for all seeds.

    Returns:
        Dict mapping seed -> parameter tensor [n_params]
    """
    ...

def load_final_weights(
    h_m1_results_path: Path,
    condition: str,
    n_seeds: int
) -> Dict[int, torch.Tensor]:
    """
    Load final weights for all seeds.

    Returns:
        Dict mapping seed -> parameter tensor [n_params]
    """
    ...
```

### Tensor Shapes

| Model | n_params | Details |
|-------|----------|---------|
| 1layer | 196K | fc1[128,784], fc2[10,128] + biases |
| 2layer | 400K | fc1[256,784], fc2[128,256], fc3[10,128] + biases |

### Subtasks [9/9 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | load_initial_weights | Initial weight loader |
| L-3-2 | load_final_weights | Final weight loader |
| L-3-3 | Path construction | Build file paths |
| L-3-4 | torch.load wrapper | Load .pt files |
| L-3-5 | Dict construction | Map seed -> tensor |
| L-3-6 | Shape validation | Verify tensor shapes |
| L-3-7 | Device mapping | Load to CPU |
| L-3-8 | Error handling | Handle missing files |
| L-3-9 | Type checking | Ensure tensor type |

---

## A-4: Loss Loader Module [Complexity: 7, Budget: 7]

Applied: NumPy array loading

### API Signatures

```python
import numpy as np
from pathlib import Path

def load_loss_trajectories(
    h_m1_results_path: Path,
    condition: str,
    n_seeds: int
) -> np.ndarray:
    """
    Load loss trajectories for all seeds.

    Returns:
        Array [n_seeds=30, n_epochs=10]
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Description |
|----------|-------|-------------|
| loss_trajectories | [30, 10] | 30 seeds × 10 epochs |
| final_losses | [30] | Extracted epoch 9 losses |

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | load_loss_trajectories | Main loader |
| L-4-2 | Path construction | Build .npy paths |
| L-4-3 | np.load wrapper | Load loss files |
| L-4-4 | Array stacking | Stack to [30, 10] |
| L-4-5 | Shape validation | Verify [10] per seed |
| L-4-6 | Error handling | Handle missing files |
| L-4-7 | Type checking | Ensure np.ndarray |

---

## A-5: CV Calculator Module [Complexity: 6, Budget: 6]

Applied: Statistical CV formula

### API Signatures

```python
import numpy as np

def calculate_loss_cv(loss_trajectories: np.ndarray) -> float:
    """
    Compute coefficient of variation for final epoch losses.

    Args:
        loss_trajectories: [30, 10] array
    Returns:
        CV as percentage
    """
    ...

def compute_epoch_wise_cv(loss_trajectories: np.ndarray) -> np.ndarray:
    """
    Compute CV for each epoch.

    Returns:
        Array [10] of CV values
    """
    ...
```

### Pseudo-code

```python
def calculate_loss_cv(loss_trajectories):
    final_losses = loss_trajectories[:, -1]  # [30]
    cv = (np.std(final_losses) / np.mean(final_losses)) * 100
    return float(cv)
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | calculate_loss_cv | Final epoch CV |
| L-5-2 | compute_epoch_wise_cv | Per-epoch CV |
| L-5-3 | Extract final losses | Index [:, -1] |
| L-5-4 | CV computation | std/mean × 100 |
| L-5-5 | Validation | Check non-zero mean |
| L-5-6 | Type conversion | Return float |

---

## A-6: Distance & Significance Module [Complexity: 8, Budget: 8]

Applied: Reuse h-m1 statistical functions

### API Signatures

```python
from typing import Dict
import numpy as np
import torch

def analyze_weight_divergence(
    final_weights_dict: Dict[int, torch.Tensor]
) -> Dict[str, float]:
    """
    Compute pairwise distances and significance test.

    Uses h-m1 functions: compute_pairwise_distances, test_independence

    Returns:
        Dict with keys: mean_distance, std_distance, t_statistic, p_value, n_pairs, distances
    """
    ...
```

### Pseudo-code

```python
def analyze_weight_divergence(final_weights_dict):
    # Reuse h-m1 function
    distances = compute_pairwise_distances(final_weights_dict)  # [435]

    # Reuse h-m1 function
    stats = test_independence(distances)

    # Add raw distances for visualization
    stats['distances'] = distances
    return stats
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | analyze_weight_divergence | Main orchestrator |
| L-6-2 | Import h-m1 functions | From h_m1.code.statistics |
| L-6-3 | Call compute_pairwise_distances | Reuse h-m1 |
| L-6-4 | Call test_independence | Reuse h-m1 |
| L-6-5 | Add distances to result | For visualization |
| L-6-6 | Validate output | Check all keys present |
| L-6-7 | Type conversion | Ensure float types |
| L-6-8 | Error handling | Wrap h-m1 calls |

---

## A-7: Multi-Condition Orchestrator [Complexity: 10, Budget: 10]

Applied: Loop-based multi-condition pattern

### API Signatures

```python
from typing import Dict
from pathlib import Path

def run_single_condition_analysis(
    condition: str,
    config: AnalysisConfig
) -> Dict[str, float]:
    """
    Run analysis for one condition.

    Returns:
        Dict with keys: mean_initial_distance, mean_final_distance,
                       final_distance_p_value, final_distance_t_stat,
                       cv_final_loss_percent, test1_passed, test2_passed,
                       n_seeds, n_params
    """
    ...

def run_all_conditions(config: AnalysisConfig) -> Dict[str, Dict[str, float]]:
    """
    Run analysis for all 4 conditions.

    Returns:
        Dict mapping condition -> results dict
    """
    ...
```

### Pseudo-code

```python
def run_single_condition_analysis(condition, config):
    # Load artifacts
    final_weights = load_final_weights(config.h_m1_config.h_m1_results_path, condition, 30)
    loss_trajectories = load_loss_trajectories(config.h_m1_config.h_m1_results_path, condition, 30)

    # Compute metrics
    weight_stats = analyze_weight_divergence(final_weights)
    cv = calculate_loss_cv(loss_trajectories)

    # Test pass/fail
    test1_passed = weight_stats['p_value'] < 0.05 and weight_stats['mean_distance'] > 0
    test2_passed = cv >= 1.0

    return {
        'mean_final_distance': weight_stats['mean_distance'],
        'final_distance_p_value': weight_stats['p_value'],
        'final_distance_t_stat': weight_stats['t_statistic'],
        'cv_final_loss_percent': cv,
        'test1_passed': test1_passed,
        'test2_passed': test2_passed,
        'distances': weight_stats['distances'],
        'loss_trajectories': loss_trajectories,
        'n_seeds': 30
    }

def run_all_conditions(config):
    results = {}
    for condition in config.h_m1_config.conditions:
        results[condition] = run_single_condition_analysis(condition, config)
    return results
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | run_single_condition_analysis | Per-condition orchestrator |
| L-7-2 | run_all_conditions | Loop over 4 conditions |
| L-7-3 | Load artifacts | Call loaders |
| L-7-4 | Compute distances | Call weight divergence |
| L-7-5 | Compute CV | Call loss CV |
| L-7-6 | Test pass/fail logic | Evaluate criteria |
| L-7-7 | Result aggregation | Build results dict |
| L-7-8 | Error propagation | Handle failures |
| L-7-9 | Progress logging | Print condition status |
| L-7-10 | Validation | Check all metrics present |

---

## A-8: Gate Validation Module [Complexity: 7, Budget: 7]

Applied: Multi-criterion validation pattern

### API Signatures

```python
from typing import Dict, Tuple

def validate_gate(results: Dict[str, Dict[str, float]]) -> Tuple[bool, str]:
    """
    Determine MUST_WORK gate pass/fail.

    Primary: ALL 4 conditions p < 0.05 and mean_distance > 0
    Secondary: ≥2/4 conditions CV ≥ 1%

    Returns:
        (gate_passed: bool, summary: str)
    """
    ...

def generate_gate_summary(
    test1_count: int,
    test2_count: int,
    gate_passed: bool
) -> str:
    """Generate human-readable gate summary."""
    ...
```

### Pseudo-code

```python
def validate_gate(results):
    # Primary criterion: ALL 4 conditions
    test1_count = sum(r['test1_passed'] for r in results.values())
    primary_pass = (test1_count == 4)

    # Secondary criterion: ≥2/4 conditions
    test2_count = sum(r['test2_passed'] for r in results.values())
    secondary_pass = (test2_count >= 2)

    # MUST_WORK requires primary only
    gate_passed = primary_pass

    summary = f"Primary: {test1_count}/4, Secondary: {test2_count}/4"
    return gate_passed, summary
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | validate_gate | Main validator |
| L-8-2 | Primary criterion check | All 4 p < 0.05 |
| L-8-3 | Secondary criterion check | ≥2/4 CV ≥ 1% |
| L-8-4 | Gate decision | Primary only for MUST_WORK |
| L-8-5 | generate_gate_summary | Human-readable output |
| L-8-6 | Logging | Print gate status |
| L-8-7 | Return formatting | Tuple[bool, str] |

---

## A-9: Visualization Module [Complexity: 12, Budget: 12]

Applied: Multi-panel matplotlib layout

### API Signatures

```python
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict

def plot_gate_metrics_comparison(
    all_results: Dict[str, Dict],
    save_path: Path
) -> None:
    """
    Generate 2×4 grid figure.
    Top row: Final weight distance distributions
    Bottom row: Loss trajectory fans
    """
    ...

def plot_distance_distribution_panel(
    ax: plt.Axes,
    distances: np.ndarray,
    mean_dist: float,
    p_value: float,
    condition: str
) -> None:
    """Plot histogram on given axes."""
    ...

def plot_loss_trajectory_fan(
    ax: plt.Axes,
    loss_trajectories: np.ndarray,
    cv_final: float,
    condition: str
) -> None:
    """Plot all 30 loss curves on given axes."""
    ...
```

### Pseudo-code

```python
def plot_gate_metrics_comparison(all_results, save_path):
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    conditions = ['1layer_mnist', '1layer_fashion_mnist', '2layer_mnist', '2layer_fashion_mnist']

    for i, condition in enumerate(conditions):
        # Top row: distance histograms
        plot_distance_distribution_panel(
            axes[0, i],
            all_results[condition]['distances'],
            all_results[condition]['mean_final_distance'],
            all_results[condition]['final_distance_p_value'],
            condition
        )

        # Bottom row: trajectory fans
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

### Subtasks [12/12 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | plot_gate_metrics_comparison | Main orchestrator |
| L-9-2 | Figure layout | 2×4 subplot grid |
| L-9-3 | plot_distance_distribution_panel | Histogram plotter |
| L-9-4 | plot_loss_trajectory_fan | Trajectory plotter |
| L-9-5 | Histogram styling | Bins, colors, labels |
| L-9-6 | Mean line annotation | Vertical line at mean |
| L-9-7 | P-value annotation | Text box on plot |
| L-9-8 | Trajectory plotting | 30 lines, alpha=0.5 |
| L-9-9 | CV annotation | Text on trajectory plot |
| L-9-10 | Axis labels | x/y labels, titles |
| L-9-11 | File saving | DPI=300, tight layout |
| L-9-12 | Error handling | Handle missing data |

---

## A-10: Results Logging Module [Complexity: 6, Budget: 6]

Applied: JSON serialization pattern

### API Signatures

```python
import json
from pathlib import Path
from typing import Dict

def save_results(
    results: Dict[str, Dict[str, float]],
    gate_status: Dict[str, bool],
    output_dir: Path
) -> None:
    """Save analysis results to JSON."""
    ...

def generate_validation_report(
    results: Dict[str, Dict[str, float]],
    gate_passed: bool,
    output_dir: Path
) -> None:
    """Generate human-readable markdown report."""
    ...
```

### Output Files

| File | Format | Content |
|------|--------|---------|
| analysis_results.json | JSON | All metrics per condition |
| gate_validation.json | JSON | Gate pass/fail, summary |
| validation_report.md | Markdown | Human-readable summary |

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-10-1 | save_results | JSON serializer |
| L-10-2 | generate_validation_report | Markdown generator |
| L-10-3 | Convert np arrays | To lists for JSON |
| L-10-4 | Format floats | 4 decimal places |
| L-10-5 | File I/O | Write JSON/markdown |
| L-10-6 | Error handling | Handle write failures |

---

## A-11: Integration Testing Module [Complexity: 8, Budget: 8]

Applied: End-to-end validation pattern

### API Signatures

```python
import pytest
from pathlib import Path

def test_artifact_loading_integration(tmp_path: Path) -> None:
    """Test end-to-end artifact loading with mock files."""
    ...

def test_single_condition_analysis(tmp_path: Path) -> None:
    """Test full analysis pipeline for one condition."""
    ...

def test_gate_validation_pass() -> None:
    """Test gate validation with passing metrics."""
    ...

def test_gate_validation_fail() -> None:
    """Test gate validation with failing metrics."""
    ...
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-11-1 | test_artifact_loading_integration | End-to-end load test |
| L-11-2 | test_single_condition_analysis | Pipeline test |
| L-11-3 | test_gate_validation_pass | Pass case |
| L-11-4 | test_gate_validation_fail | Fail case |
| L-11-5 | Mock artifact creation | Create test files |
| L-11-6 | Assertion checks | Verify all metrics |
| L-11-7 | Cleanup | Remove test artifacts |
| L-11-8 | Error case testing | Missing files |

---

## Implementation Priority

1. A-1: Configuration (setup)
2. A-2: Artifact verification (early failure)
3. A-3: Weight loader
4. A-4: Loss loader
5. A-5: CV calculator
6. A-6: Distance & significance (reuse h-m1)
7. A-7: Multi-condition orchestrator
8. A-8: Gate validation
9. A-10: Results logging
10. A-9: Visualization (non-blocking)
11. A-11: Integration testing (validation)

---

## Critical Implementation Notes

### Import Path Setup

```python
import sys
from pathlib import Path

# Add h-m1 code to Python path
h_m1_code_path = Path(__file__).parent.parent / 'h-m1' / 'code'
sys.path.insert(0, str(h_m1_code_path))

# Now can import
from h_m1.code.statistics import compute_pairwise_distances, test_independence
from h_m1.code.viz_h_m1 import plot_distance_distribution
```

### Numerical Precision

All distance arrays and statistical calculations use `float64` to prevent underflow in t-tests.

### Early Failure

File verification (A-2) runs BEFORE any artifact loading to prevent wasted computation on incomplete h-m1 results.

---

*Generated by Phase 3 Logic Agent*
*APIs verified from h-m1 actual implementation*
*Budget: 5 subtasks target → 86 total used (11 tasks)*
