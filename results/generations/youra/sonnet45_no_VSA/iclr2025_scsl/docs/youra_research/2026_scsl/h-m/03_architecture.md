# Architecture Design: h-m
# Mechanism Testing: Dose-Response Validation with Statistical Inference

**Date:** 2026-07-11
**Hypothesis:** h-m (MECHANISM)
**Author:** Architecture Agent (Phase 3)

Applied: Standard DL experiment pattern (multi-seed + statistical testing)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: h-e1 validated code found - EXTENDS existing implementation
**Analyzed Path**: docs/youra_research/h-e1/code/
**Findings**: h-e1 implements 5-condition single-seed experiment. h-m extends with multi-seed infrastructure (5 seeds) and statistical testing (Spearman correlation).

---

## System Overview

**Architecture Type**: MECHANISM (extends EXISTENCE)
**Extension Strategy**: Add multi-seed orchestration + statistical analysis to h-e1 codebase
**Core Addition**: Dose-response correlation testing

This extends h-e1's directional evidence (n=1) to statistical validation (n=5 seeds) with Spearman rank correlation.

---

## Module Definitions

### 1. Configuration Module (`config.py`)

**Dependencies**: torch, h-e1.config

**Extension from h-e1**:

```python
# ADDED: Multi-seed configuration
EXPERIMENT_CONFIG = {
    "seeds": [42, 123, 456, 789, 1011],  # NEW: 5 seeds for statistical testing
    "conditions": ["baseline", "flip30", "flip50", "flip90", "rotation"],  # from h-e1
    "symmetric_digits": [0, 1, 8],  # from h-e1
    "asymmetric_digits": [2, 3, 5, 6, 7, 9],  # from h-e1
    "rotation_degrees": 15,  # from h-e1
}

# ADDED: Statistical testing configuration
STATS_CONFIG = {
    "correlation_method": "spearman",
    "alpha": 0.05,
    "flip_probabilities": [0.0, 0.3, 0.5, 0.9],  # for dose-response
}

# MODIFIED: Output paths for per-seed results
OUTPUT_CONFIG = {
    "output_dir": "docs/youra_research/h-m",
    "figures_dir": "docs/youra_research/h-m/figures",
    "results_file": "per_seed_results.csv",  # NEW: CSV instead of JSON
    "stats_file": "dose_response_stats.json",  # NEW: Statistical test results
    "logs_dir": "training_logs",  # NEW: Per-seed logs
    "checkpoints_dir": "model_checkpoints",  # NEW: Per-seed checkpoints
}
```

### 2. Data Module (`data.py`)

**Dependencies**: torchvision, h-e1.data

**Reused from h-e1 with seed control**:

```python
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import torch

def get_dataloaders(condition: str, batch_size: int, seed: int) -> tuple[DataLoader, DataLoader]:
    """
    Get dataloaders with seed-controlled sampling.
    
    Args:
        condition: "baseline" | "flip30" | "flip50" | "flip90" | "rotation"
        batch_size: Batch size
        seed: Random seed for reproducibility
    
    Returns:
        (train_loader, test_loader)
    """
    ...

def set_seed(seed: int):
    """Set all random seeds for reproducibility."""
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    import numpy as np
    import random
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True
    ...
```

### 3. Model Module (`model.py`)

**Dependencies**: torch.nn, h-e1.model

**100% Reused from h-e1**:

```python
class MNISTNet(nn.Module):
    """Identical to h-e1 - no architecture changes."""
    def __init__(self): ...
    def forward(self, x: torch.Tensor) -> torch.Tensor: ...
```

### 4. Training Module (`train.py`)

**Dependencies**: Model, Data, torch.optim, h-e1.train

**Extended from h-e1 with seed parameter**:

```python
def train_condition(condition: str, epochs: int, seed: int) -> dict:
    """
    Train model for single (condition, seed) pair.
    
    Args:
        condition: Augmentation condition
        epochs: Number of epochs
        seed: Random seed
    
    Returns:
        dict: {model, train_losses, test_accs, final_checkpoint_path}
    """
    ...

def save_checkpoint(model, condition: str, seed: int, output_dir: str):
    """Save trained model checkpoint."""
    ...

def train_epoch(model, train_loader, optimizer, device) -> float:
    """Reused from h-e1."""
    ...

def test_epoch(model, test_loader, device) -> float:
    """Reused from h-e1."""
    ...
```

### 5. Evaluation Module (`evaluate.py`)

**Dependencies**: torch, numpy, h-e1.evaluate

**Reused from h-e1**:

```python
def compute_per_class_accuracy(model, test_loader, device) -> dict:
    """
    Compute per-class accuracy (from h-e1).
    
    Returns:
        dict: {per_class, symmetric_mean, asymmetric_mean, overall_acc}
    """
    ...

def group_by_symmetry(per_class_acc: dict) -> dict:
    """From h-e1."""
    ...
```

### 6. Statistical Testing Module (`statistics.py`)

**Dependencies**: scipy.stats, numpy, pandas

**NEW for h-m**:

```python
from scipy.stats import spearmanr
import numpy as np
import pandas as pd

def compute_spearman_correlation(results_df: pd.DataFrame) -> dict:
    """
    Test dose-response relationship.
    
    Args:
        results_df: DataFrame with columns [condition, seed, asymmetric_acc]
    
    Returns:
        dict: {rho, p_value, significant, interpretation}
    """
    ...

def aggregate_seed_results(results_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate results across seeds.
    
    Returns:
        DataFrame with columns [condition, mean, std, sem, n]
    """
    ...

def test_rotation_control(results_df: pd.DataFrame) -> dict:
    """
    Validate rotation shows no differential effect.
    
    Returns:
        dict: {mean_diff, within_threshold, passed}
    """
    ...
```

### 7. Visualization Module (`visualize.py`)

**Dependencies**: matplotlib, seaborn, h-e1.visualize

**Extended from h-e1 with statistical annotations**:

```python
def plot_dose_response_curve(aggregated_df: pd.DataFrame, stats: dict, save_path: str):
    """
    NEW: Dose-response with error bars + Spearman annotation.
    
    X-axis: flip_probability [0.0, 0.3, 0.5, 0.9]
    Y-axis: asymmetric_accuracy (mean ± std)
    Annotation: "ρ = {rho:.3f}, p = {p_value:.4f}"
    """
    ...

def plot_per_class_heatmap(results_df: pd.DataFrame, save_path: str):
    """Reused from h-e1 with mean across seeds."""
    ...

def plot_seed_variability_boxplot(results_df: pd.DataFrame, save_path: str):
    """
    NEW: Box plots showing distribution across seeds.
    
    X-axis: conditions
    Y-axis: asymmetric_accuracy
    Boxes: 5 seed values per condition
    """
    ...

def plot_scatter_with_regression(results_df: pd.DataFrame, stats: dict, save_path: str):
    """
    NEW: Scatter plot with regression line.
    
    Points: Individual (flip_prob, asym_acc) pairs (n=20)
    Line: Linear regression with 95% CI
    """
    ...
```

### 8. Multi-Seed Orchestrator (`run_multi_seed.py`)

**Dependencies**: All modules

**NEW for h-m**:

```python
import pandas as pd
from pathlib import Path
from itertools import product

def run_all_seeds_and_conditions() -> pd.DataFrame:
    """
    Execute 5 conditions × 5 seeds = 25 training runs.
    
    Returns:
        DataFrame with columns: [condition, seed, overall_acc, asym_acc, sym_acc, class_0-9]
    """
    ...

def save_results_csv(results_df: pd.DataFrame, output_path: str):
    """Save results in CSV format for downstream analysis."""
    ...

def generate_statistical_report(results_df: pd.DataFrame) -> dict:
    """
    Compute all statistical tests.
    
    Returns:
        dict: {spearman_test, rotation_control, aggregated_stats}
    """
    ...

def main():
    """
    Main execution flow:
    1. Run 25 training runs
    2. Aggregate results
    3. Compute statistical tests
    4. Generate visualizations
    5. Save outputs
    6. Validate SHOULD_WORK gate
    """
    ...
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual h-e1 Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| MNISTNet | `from h_e1_code.model import MNISTNet` | `docs/youra_research/h-e1/code/model.py` |
| get_dataloaders | `from h_e1_code.data import get_dataloaders, get_transform` | `docs/youra_research/h-e1/code/data.py` |
| compute_per_class_accuracy | `from h_e1_code.evaluate import compute_per_class_accuracy` | `docs/youra_research/h-e1/code/evaluate.py` |
| train_epoch, test_epoch | `from h_e1_code.train import train_epoch, test_epoch` | `docs/youra_research/h-e1/code/train.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation)

**Reuse Strategy**:
- Model architecture: 100% reused (no changes)
- Data pipeline: 95% reused (add seed parameter)
- Training loop: 90% reused (add checkpoint saving)
- Evaluation: 100% reused (same metrics)
- NEW: Statistical testing module (0% from h-e1)
- NEW: Multi-seed orchestrator (0% from h-e1)

---

## File Structure

```
docs/youra_research/h-m/
├── code/
│   ├── config.py              # EXTENDED: Add seeds + stats config
│   ├── data.py                # EXTENDED: Add seed control
│   ├── model.py               # SYMLINK/IMPORT: Reuse h-e1
│   ├── train.py               # EXTENDED: Add checkpoint saving
│   ├── evaluate.py            # SYMLINK/IMPORT: Reuse h-e1
│   ├── statistics.py          # NEW: Spearman correlation testing
│   ├── visualize.py           # EXTENDED: Add dose-response plots
│   ├── run_multi_seed.py      # NEW: Multi-seed orchestrator
│   └── __init__.py
├── model_checkpoints/         # NEW: Per (condition, seed) models
│   ├── baseline_seed42.pth
│   ├── flip30_seed42.pth
│   └── ...
├── training_logs/             # NEW: Per-seed logs
│   ├── baseline_seed42.log
│   └── ...
├── figures/                   # EXTENDED: Additional plots
│   ├── dose_response_curve.png       # NEW
│   ├── scatter_regression.png        # NEW
│   ├── seed_variability_boxplot.png  # NEW
│   └── per_class_heatmap.png         # from h-e1
├── per_seed_results.csv       # NEW: All 25 runs
└── dose_response_stats.json   # NEW: Statistical tests
```

---

## Data Flow

1. **Configuration** → Load seeds + conditions (5 × 5 = 25 runs)
2. **Multi-Seed Loop** → For each (condition, seed):
   - Set seed
   - Get dataloaders (with seed)
   - Train model (14 epochs)
   - Evaluate (per-class accuracy)
   - Save checkpoint
3. **Aggregation** → Collect all 25 results into DataFrame
4. **Statistical Testing** → Compute Spearman correlation
5. **Visualization** → Generate 4 figures (dose-response, scatter, boxplot, heatmap)
6. **Gate Validation** → Check ρ < 0, p < 0.05

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Extend configuration | Add seeds, stats config, output paths | 6 | 2+2+1+1 (seeds+stats+paths+test) |
| M-2 | Add seed control to data | Modify get_dataloaders with seed param | 7 | 2+2+2+1 (set_seed+dataloaders+torch_seed+integration) |
| M-3 | Extend training module | Add checkpoint saving per (condition, seed) | 8 | 2+3+2+1 (save_fn+train_mod+path_handling+test) |
| M-4 | Implement statistical testing | Spearman correlation + aggregation functions | 11 | 3+3+3+2 (spearman+aggregation+rotation_test+validation) |
| M-5 | Extend visualization | Dose-response curve + scatter + boxplot | 12 | 4+4+3+1 (dose_curve+scatter+boxplot+integration) |
| M-6 | Implement multi-seed orchestrator | 25-run execution + CSV output + gate validation | 14 | 4+3+3+2+2 (loop+csv+stats_report+gate+error_handling) |
| M-7 | Run full experiment + validate gate | Execute 25 runs, verify Spearman ρ<0, p<0.05 | 15 | 5+4+3+3 (run_all+results_check+gate_validation+debug) |

**Total Complexity**: 73 points

**Distribution**:
- VeryHigh (18-20): []
- High (14-17): [M-6, M-7]
- Medium (9-13): [M-4, M-5]
- Low (4-8): [M-1, M-2, M-3]

**Rationale for 7 Tasks**:
- MECHANISM hypothesis requires statistical validation (not PoC)
- Multi-seed infrastructure is significant addition to h-e1
- Statistical testing module is new component
- Reuses ~70% of h-e1 code, adds ~30% new functionality
- Each task produces incrementally testable output

---

## Integration Points

### Reuse from h-e1

**Direct Imports** (verified from actual code):

```python
# Import h-e1 modules (add to PYTHONPATH or relative import)
import sys
sys.path.append('/workspace/TEST_scsl/docs/youra_research/h-e1/code')

from model import MNISTNet
from data import get_transform  # Reuse transform logic
from evaluate import compute_per_class_accuracy, group_by_symmetry
from train import train_epoch, test_epoch
```

**h-e1 Configuration Constants** (reused):

```python
# From h-e1/code/config.py
MODEL_CONFIG = {...}         # Unchanged
TRAINING_CONFIG = {...}      # Unchanged (except seed iteration)
DATA_CONFIG = {...}          # Unchanged
EXPERIMENT_CONFIG = {...}    # Unchanged (conditions, digit groups)
```

### New Dependencies

**Python Packages** (additions to h-e1):

```
scipy>=1.5.0      # NEW: For scipy.stats.spearmanr
pandas>=1.1.0     # NEW: For CSV results management
```

**Existing from h-e1**:
```
torch>=1.10
torchvision>=0.11
numpy>=1.20
matplotlib>=3.4
seaborn>=0.11
```

---

## SHOULD_WORK Gate Validation

**Success Criteria** (from PRD):

**Primary Gate Pass**:
- Spearman ρ < 0 (negative correlation)
- p-value < 0.05 (statistically significant)

**Secondary Validation**:
- Degradation gradient: flip30 < flip50 < flip90 (asymmetric accuracy)
- Rotation control: |rotation - baseline| < 1.0% (asymmetric accuracy)

**Implementation** (in run_multi_seed.py):

```python
def validate_gate_criteria(stats: dict, aggregated_df: pd.DataFrame) -> dict:
    """
    Check SHOULD_WORK gate criteria.
    
    Returns:
        dict: {passed, failures, action, details}
    """
    spearman = stats['spearman_test']
    rotation = stats['rotation_control']
    
    checks = {
        'spearman_negative': spearman['rho'] < 0,
        'spearman_significant': spearman['p_value'] < 0.05,
        'gradient_observed': (
            aggregated_df[aggregated_df.condition == 'flip30']['mean'].values[0] >
            aggregated_df[aggregated_df.condition == 'flip50']['mean'].values[0] >
            aggregated_df[aggregated_df.condition == 'flip90']['mean'].values[0]
        ),
        'rotation_control_passed': rotation['within_threshold']
    }
    
    primary_passed = checks['spearman_negative'] and checks['spearman_significant']
    
    return {
        'passed': primary_passed,
        'checks': checks,
        'action': 'PROCEED' if primary_passed else 'DOCUMENT_LIMITATION',
        'gate_type': 'SHOULD_WORK',
        'details': {
            'rho': spearman['rho'],
            'p_value': spearman['p_value'],
            'interpretation': spearman['interpretation']
        }
    }
```

---

## Design Decisions

**Why extend h-e1 instead of fresh implementation?**
- Controlled comparison requires identical model/hyperparameters
- h-e1 validated baseline (99.14% accuracy) provides quality assurance
- Only variable is statistical validation (n=1 → n=5)

**Why CSV output instead of JSON?**
- 25 runs × 12 metrics = 300 data points
- CSV enables easy pandas analysis for statistical tests
- JSON for summary statistics only

**Why 5 seeds instead of 10?**
- Power analysis (from PRD): n=5 sufficient for |ρ| ≥ 0.7 with power=0.95
- h-e1 preliminary evidence suggests ρ ≈ -0.85
- Balance between statistical power and computational cost

**Why separate statistics.py module?**
- Spearman correlation is new capability (not in h-e1)
- Encapsulates statistical testing logic separately from ML code
- Enables future extension (e.g., bootstrap confidence intervals)

---

## Output Artifacts

**Phase 4.5 Synthesis Inputs**:

1. `per_seed_results.csv` - All 25 runs with per-class accuracy
2. `dose_response_stats.json` - Spearman ρ, p-value, aggregated statistics
3. `figures/dose_response_curve.png` - Primary evidence of monotonic relationship
4. `figures/scatter_regression.png` - Statistical visualization
5. `figures/seed_variability_boxplot.png` - Variance across seeds
6. `model_checkpoints/` - All 25 trained models
7. `gate_decision.json` - SHOULD_WORK gate validation

**Gate Decision File** (generated by run_multi_seed.py):

```json
{
  "hypothesis": "h-m",
  "gate_type": "SHOULD_WORK",
  "primary_passed": true,
  "action": "PROCEED",
  "spearman_test": {
    "rho": -0.87,
    "p_value": 0.0023,
    "significant": true,
    "interpretation": "Strong negative monotonic relationship"
  },
  "secondary_validation": {
    "gradient_observed": true,
    "rotation_control_passed": true
  },
  "recommendation": "Mechanism confirmed - dose-response relationship established"
}
```

---

## Risk Mitigation

**High Risk**: Insufficient statistical power (n=5)
- **Mitigation**: h-e1 showed strong effect (4.12% at p=0.9), expect ρ ≈ -0.85
- **Detection**: If 0.05 < p < 0.10, increase to n=10 seeds and re-run
- **Fallback**: Document as "suggestive but inconclusive" (SHOULD_WORK allows continuation)

**Medium Risk**: Non-monotonic relationship (e.g., U-shaped at p=0.9)
- **Mitigation**: Spearman test detects monotonic violation
- **Detection**: Compare Spearman ρ on full range [0.0-0.9] vs subset [0.0-0.5]
- **Fallback**: Report monotonic relationship in subset, document non-linearity

**Low Risk**: Seed variance too high (obscures dose-response)
- **Mitigation**: h-e1 showed consistent degradation with single seed
- **Detection**: High std in aggregated_df (>2% per condition)
- **Fallback**: Visualize per-seed trajectories, increase to n=10 if needed

---

*Architecture extends validated h-e1 with multi-seed statistical testing*
*Total estimated implementation: 6-8 hours (building on h-e1 foundation)*
*Next Phase: Logic Design (execution flow specifications)*
