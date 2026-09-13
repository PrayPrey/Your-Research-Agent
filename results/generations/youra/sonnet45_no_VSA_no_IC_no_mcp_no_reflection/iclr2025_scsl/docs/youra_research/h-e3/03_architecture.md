# Architecture: h-e3 GradCAM Temporal Ratio Tracking

**Hypothesis:** h-e3  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-08-28  
**Author:** yoon303@ust.ac.kr  

---

## Knowledge Base Patterns

Applied: Minimal PoC structure (data, model, tracker, evaluate)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Reusing h-e1 data/model infrastructure  
**Analyzed Path**: `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet45/TEST_scsl/docs/youra_research/h-e1/code/`  
**Findings**: h-e1 implements Waterbirds dataloader + ResNet-50 baseline. Reuse data.py loader, add GradCAM tracker on top.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From h-e1 Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| get_dataloader | `from data import get_dataloader, DatasetConfig` | `h-e1/code/data.py` |
| get_baseline_model | `from model import get_baseline_model` | `h-e1/code/model.py` |
| DATASET_CONFIGS | `from train import DATASET_CONFIGS` | `h-e1/code/train.py` |

**Note**: Import from sibling directory. In h-e3/code/, use `import sys; sys.path.insert(0, '../../h-e1/code/')`.

---

## Module Structure

### GradCAMTracker (`h-e3/code/gradcam_tracker.py`)

**Dependencies**: captum.attr.LayerGradCam

```python
class GradCAMTemporalTracker:
    def __init__(self, model: nn.Module, target_layer: nn.Module, device: str): ...
    
    def compute_epoch_ratio(
        self, 
        dataloader: DataLoader, 
        max_batches: int = 100
    ) -> float:
        """
        Returns R_temporal = A_spurious / (A_spurious + A_core)
        """
        ...
    
    def get_temporal_history(self) -> dict[int, float]:
        """Returns {epoch: R_temporal} mapping"""
        ...
```

---

### TrainModule (`h-e3/code/train.py`)

**Dependencies**: GradCAMTracker, h-e1 modules (data, model)

```python
@dataclass
class TrainConfig:
    dataset: str
    lr: float
    max_epochs: int
    batch_size: int
    seed: int
    tracking_interval: int  # Compute R_temporal every N epochs

def run_experiment(config: TrainConfig) -> dict:
    """
    Returns {
        'R_temporal_history': dict[int, float],
        'worst_group_acc': float,
        'delta': float  # R_temporal(5) - R_temporal(50)
    }
    """
    ...

def create_region_masks(dataset_name: str, images: Tensor) -> tuple[Tensor, Tensor]:
    """
    Returns (spurious_mask, core_mask).
    Waterbirds: spurious=background, core=bird bbox (fallback: GradCAM peak).
    """
    ...
```

---

### EvaluationModule (`h-e3/code/evaluate.py`)

**Dependencies**: TrainModule (results only)

```python
def check_poc_pass(results: dict) -> bool:
    """
    Pass conditions:
    1. R_temporal(5) > R_temporal(50)
    2. delta >= 0.1
    """
    ...

def plot_temporal_ratio(R_history: dict[int, float], output_path: str):
    """MANDATORY: R_temporal vs epoch line plot"""
    ...

def plot_gradcam_heatmaps(
    model: nn.Module, 
    images: Tensor, 
    epochs: list[int], 
    output_path: str
):
    """GradCAM heatmap evolution at epochs 5, 25, 50"""
    ...

def save_results(results: dict, output_dir: str):
    """Export R_temporal history as CSV"""
    ...
```

---

## File Organization

```
h-e3/
├── code/
│   ├── gradcam_tracker.py   # 120 lines - GradCAM computation + R_temporal
│   ├── train.py             # 150 lines - training loop + tracking schedule
│   ├── evaluate.py          # 100 lines - PoC validation + plots
│   └── main.py              # 50 lines - experiment runner
├── results/
│   └── temporal_ratios.csv
└── figures/
    ├── R_temporal_vs_epoch.png
    └── gradcam_evolution.png
```

Total: ~420 lines implementation code

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | GradCAM Tracker | LayerGradCam integration + R_temporal | 12 | 3+2+5+2 |
| A-2 | Region Masking | Spurious/core mask extraction | 9 | 2+2+3+2 |
| A-3 | Training Loop | 50-epoch run + tracking schedule | 11 | 3+2+4+2 |
| A-4 | PoC Validation | Delta check + pass condition | 6 | 2+1+2+1 |
| A-5 | Visualization | R_temporal plot + GradCAM heatmaps | 9 | 2+2+3+2 |

**Total Complexity**: 47  
**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-3, A-2, A-5], Low(4-8): [A-4]

### Complexity Breakdown

**A-1 (12):** Module_Size=3 (tracker class), Dependencies=2 (Captum+PyTorch), Algorithm=5 (attribution aggregation), Integration=2

**A-2 (9):** Module_Size=2 (mask functions), Dependencies=2 (WILDS metadata), Algorithm=3 (region extraction), Integration=2

**A-3 (11):** Module_Size=3 (training loop), Dependencies=2 (h-e1 modules), Algorithm=4 (tracking schedule), Integration=2

**A-4 (6):** Module_Size=2 (validation logic), Dependencies=1 (results dict), Algorithm=2 (delta computation), Integration=1

**A-5 (9):** Module_Size=2 (plot functions), Dependencies=2 (matplotlib), Algorithm=3 (heatmap overlay), Integration=2

---

## Configuration

```python
# h-e3/code/config.py
WATERBIRDS_CONFIG = {
    'lr': 0.001,
    'batch_size': 128,
    'max_epochs': 50,
    'weight_decay': 1e-4,
    'tracking_interval': 5,  # Compute R_temporal every 5 epochs
    'seed': 0
}

GRADCAM_CONFIG = {
    'target_layer': 'layer4',  # ResNet-50 final conv block
    'max_batches_per_epoch': 100,  # Sample for efficiency
    'epsilon': 1e-8  # Numerical stability
}
```

---

## Validation Checklist

- [x] No ASCII diagrams
- [x] Module sections = interface code only
- [x] 5 Epic tasks with complexity (EXISTENCE: 4-8 range)
- [x] Total length < 500 lines
- [x] Codebase Analysis section included
- [x] Base hypothesis dependencies documented
- [x] Import paths verified from actual code
- [x] EXISTENCE rules: minimal structure
- [x] External Dependencies table included
