# Architecture: h-e2 Gradient Variance & Forgetting Analysis

**Hypothesis:** h-e2  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-08-28  
**Author:** yoon303@ust.ac.kr  

---

## Knowledge Base Patterns

Applied: Minimal PoC extension (reuse h-e1 + add trackers)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Extends h-e1 validated infrastructure  
**Analyzed Path**: /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet45/TEST_scsl/docs/youra_research/h-e1/code/  
**Findings**: Reuse h-e1 data/model/train modules. Add variance + forgetting trackers only.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From h-e1 Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| DataModule | `from h_e1.data import get_dataloader, apply_spurious_mask, apply_core_mask` | `h-e1/code/data.py` |
| BaseModel | `from h_e1.model import get_baseline_model` | `h-e1/code/model.py` |

**Verified from**: h-e1/code/ (actual implementation)

---

## Module Structure

### GradientVarianceTracker (`h-e2/code/trackers.py`)

**Dependencies**: None (stdlib only)

```python
class GradientVarianceTracker:
    def __init__(self, window_size: int = 3): ...
    
    def log_gradients(self, model: nn.Module): 
        """Store per-param gradient norms"""
        ...
    
    def compute_variance(self) -> float:
        """Rolling variance over last window_size epochs"""
        ...
```

---

### ForgettingTracker (`h-e2/code/trackers.py`)

**Dependencies**: None (stdlib only)

```python
class ForgettingTracker:
    def __init__(self, num_samples: int): ...
    
    def log_predictions(self, sample_indices: Tensor, predictions: Tensor, epoch: int):
        """Store per-sample predictions per epoch"""
        ...
    
    def compute_forgetting_events(self) -> float:
        """Count prediction flips (correct→incorrect)"""
        ...
```

---

### TrainModule (`h-e2/code/train.py`)

**Dependencies**: h-e1 data/model, GradientVarianceTracker, ForgettingTracker

```python
def run_single_experiment_with_tracking(config: TrainConfig) -> dict:
    """
    Extend h-e1 training loop with variance + forgetting tracking.
    
    Returns {
        'E_spurious': int,
        'E_core': int,
        'variance_ratio': float,  # V_spurious / V_core
        'forgetting_spurious': float,
        'forgetting_core': float
    }
    """
    ...
```

---

### StatisticalTests (`h-e2/code/stats.py`)

**Dependencies**: None (scipy only)

```python
def variance_ratio_test(var_spurious: list, var_core: list) -> dict:
    """F-test. Returns {'f_stat': float, 'p_value': float}"""
    ...

def forgetting_paired_test(forgetting_s: list, forgetting_c: list) -> dict:
    """Paired t-test. Returns {'t_stat': float, 'p_value': float}"""
    ...
```

---

### EvaluationModule (`h-e2/code/evaluate.py`)

**Dependencies**: StatisticalTests

```python
def check_poc_pass(results: dict) -> bool:
    """
    V_spurious/V_core < 0.7 AND Forgetting_spurious < Forgetting_core
    (direction only, no stats for PoC)
    """
    ...

def plot_gate_metrics(results: dict, output_path: str):
    """MANDATORY: Bar chart variance_ratio + forgetting rates"""
    ...

def plot_rolling_variance(results: dict, output_path: str):
    """Line plot V_spurious(t), V_core(t) over 30 epochs"""
    ...
```

---

## File Organization

```
h-e2/
├── code/
│   ├── trackers.py       # 100 lines - variance + forgetting
│   ├── train.py          # 80 lines - extend h-e1 loop
│   ├── stats.py          # 50 lines - F-test + t-test
│   └── evaluate.py       # 100 lines - gate check + plots
├── results/
│   ├── variance_ratios.csv
│   └── forgetting_rates.csv
└── figures/
    ├── gate_metrics.png
    └── rolling_variance.png
```

Total: ~330 lines new code (reuse h-e1 for data/model)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| B-1 | Gradient Tracker | Rolling window variance | 8 | 2+1+3+2 |
| B-2 | Forgetting Tracker | Per-sample prediction log | 9 | 2+1+4+2 |
| B-3 | Extended Training | Integrate trackers into h-e1 loop | 11 | 3+3+3+2 |
| B-4 | Statistical Tests | F-test + paired t-test | 7 | 2+2+2+1 |
| B-5 | PoC Gate Check | Directional validation | 5 | 1+1+2+1 |
| B-6 | Visualization | 2 plots (gate metrics + variance) | 8 | 2+1+3+2 |

**Total Complexity**: 48  
**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [B-2, B-3], Low(4-8): [B-1, B-4, B-5, B-6]

### Complexity Breakdown

**B-1 (8):** Module_Size=2 (simple tracker), Dependencies=1 (none), Algorithm=3 (rolling window), Integration=2

**B-2 (9):** Module_Size=2 (dict tracking), Dependencies=1 (none), Algorithm=4 (flip detection), Integration=2

**B-3 (11):** Module_Size=3 (extend h-e1), Dependencies=3 (h-e1+trackers), Algorithm=3 (hook gradients), Integration=2

**B-4 (7):** Module_Size=2 (2 test functions), Dependencies=2 (scipy), Algorithm=2 (standard tests), Integration=1

**B-5 (5):** Module_Size=1 (threshold check), Dependencies=1 (results only), Algorithm=2 (comparison), Integration=1

**B-6 (8):** Module_Size=2 (2 plots), Dependencies=1 (matplotlib), Algorithm=3 (time series), Integration=2

---

## Configuration

```python
# h-e2/code/config.py
WINDOW_SIZE = 3  # epochs for variance
CHECKPOINT_EPOCHS = [10, 20, 30]  # when to compute variance
VARIANCE_THRESHOLD = 0.7  # V_s/V_c gate
P_VALUE_THRESHOLD = 0.05
NUM_SEEDS = 1  # PoC only (10 for full validation)
```

---

## Validation Checklist

- [x] No ASCII diagrams
- [x] Module sections = interface code only
- [x] 6 Epic tasks with complexity
- [x] Total length < 500 lines
- [x] Codebase Analysis section included
- [x] External Dependencies table (h-e1 modules)
- [x] EXISTENCE rules: 4-8 tasks (actual: 6)
- [x] Minimal extension (reuse h-e1 infrastructure)
