# Architecture: H-M-MITIGATE
## Spatial Gradient Regularization for Spurious Mitigation

**Hypothesis ID:** h-m-mitigate  
**Type:** MECHANISM (SHOULD_WORK gate)  
**Prerequisites:** h-m-integrated (COMPLETED)  
**Generated:** 2026-08-20  

**Applied KB Patterns:** PyTorch trainer pattern, GradCAM integration

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** patterns found from base code  
**Analyzed Path:** h-m-integrated/code/  
**Findings:** Reused training loop pattern from train_single.py, config structure from config.py

---

## 1. System Overview

**Goal:** Mitigate spurious correlations via spatial gradient regularization on GradCAM-identified regions.

**Components:**
- MNIST+Color dataset loader (toy validation)
- Waterbirds dataset loader (reused from h-m-integrated)
- Spatial regularization trainer (ERM + gradient penalty)
- GradCAM-based spurious region detector
- Baseline trainers (ERM, GroupDRO wrapper)

**Data Flow:**
```
Dataset → Model → GradCAM → Spurious Mask → Gradient Variance → Regularization Loss
```

---

## 2. Module Structure

### 2.1 MNIST+Color Loader (`data/mnist_color.py`)

**Dependencies:** torchvision, PIL, numpy

```python
class MNISTColorDataset(Dataset):
    def __init__(self, root: str, train: bool, correlation: float = 0.9, transform=None): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> Tuple[Tensor, Tensor, Tensor]: ...
    
def create_mnist_color_metadata(
    correlation: float,
    seed: int
) -> pd.DataFrame: ...
```

### 2.2 Waterbirds Loader (`data/waterbirds.py`)

**Dependencies:** h-m-integrated (WaterbirdsDataset)

```python
from h_m_integrated.waterbirds_dataset import WaterbirdsDataset

def get_waterbirds_loaders(
    data_root: str,
    batch_size: int,
    num_workers: int
) -> Tuple[DataLoader, DataLoader, DataLoader]: ...
```

### 2.3 GradCAM Module (`models/gradcam.py`)

**Dependencies:** pytorch-grad-cam

```python
class GradCAMWrapper:
    def __init__(self, model: nn.Module, target_layer: str): ...
    def compute_cam(self, input: Tensor, target_class: int) -> Tensor: ...
    def compute_difference_map(
        self,
        majority_samples: Tensor,
        minority_samples: Tensor
    ) -> Tensor: ...
```

### 2.4 Spatial Regularization Trainer (`trainers/spatial_reg_trainer.py`)

**Dependencies:** torch, GradCAMWrapper

```python
class SpatialRegTrainer:
    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        config: dict
    ): ...
    
    def compute_spurious_mask(self, batch: Tensor, labels: Tensor) -> Tensor: ...
    def compute_regularization_loss(self, gradients: Tensor, mask: Tensor) -> Tensor: ...
    def train_epoch(self) -> dict: ...
    def validate(self) -> dict: ...
    def fit(self) -> dict: ...
```

### 2.5 ERM Trainer (`trainers/erm_trainer.py`)

**Dependencies:** torch

```python
class ERMTrainer:
    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        config: dict
    ): ...
    
    def train_epoch(self) -> dict: ...
    def validate(self) -> dict: ...
    def fit(self) -> dict: ...
```

### 2.6 GroupDRO Wrapper (`trainers/groupdro_trainer.py`)

**Dependencies:** torch, subprocess (external repo)

```python
class GroupDROTrainer:
    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        config: dict
    ): ...
    
    def fit(self) -> dict: ...
```

### 2.7 Metrics Utilities (`utils/metrics.py`)

**Dependencies:** numpy, sklearn

```python
def compute_worst_group_accuracy(
    predictions: np.ndarray,
    labels: np.ndarray,
    groups: np.ndarray
) -> float: ...

def bootstrap_test(
    wga_baseline: np.ndarray,
    wga_proposed: np.ndarray,
    n_resamples: int = 1000
) -> dict: ...
```

### 2.8 Visualization (`utils/visualization.py`)

**Dependencies:** matplotlib, pytorch-grad-cam

```python
def plot_gradcam_comparison(
    images: List[Tensor],
    cam_before: List[Tensor],
    cam_after: List[Tensor],
    save_path: str
): ...

def plot_wga_comparison(
    results_dict: dict,
    save_path: str
): ...
```

### 2.9 Config (`config.py`)

**Dependencies:** dataclasses

```python
@dataclass
class MNISTConfig:
    lr: float = 0.01
    batch_size: int = 128
    epochs: int = 50
    lambda_init: float = 0.01
    percentile_threshold: int = 75

@dataclass
class WaterbirdsConfig:
    lr: float = 0.001
    batch_size: int = 128
    epochs: int = 300
    lambda_init: float = 0.01
    percentile_threshold: int = 75
```

---

## 3. External Dependencies (h-m-integrated)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| WaterbirdsDataset | `from h_m_integrated.waterbirds_dataset import WaterbirdsDataset` | `h-m-integrated/waterbirds_dataset.py` |
| set_seed | `from h_m_integrated.gaia_utils import set_seed` | `h-m-integrated/gaia_utils.py` |
| create_resnet50 | `from h_m_integrated.gaia_utils import create_resnet50` | `h-m-integrated/gaia_utils.py` |
| get_train_transforms | `from h_m_integrated.gaia_utils import get_train_transforms` | `h-m-integrated/gaia_utils.py` |
| get_eval_transforms | `from h_m_integrated.gaia_utils import get_eval_transforms` | `h-m-integrated/gaia_utils.py` |
| GroupTracker | `from h_m_integrated.gaia_utils import GroupTracker` | `h-m-integrated/gaia_utils.py` |

**Verified from:** h-m-integrated/code/ (actual implementation)

---

## 4. File Organization

```
h-m-mitigate/
├── code/
│   ├── data/
│   │   ├── mnist_color.py
│   │   └── waterbirds.py
│   ├── models/
│   │   ├── resnet.py
│   │   └── gradcam.py
│   ├── trainers/
│   │   ├── base_trainer.py
│   │   ├── erm_trainer.py
│   │   ├── spatial_reg_trainer.py
│   │   └── groupdro_trainer.py
│   ├── utils/
│   │   ├── metrics.py
│   │   ├── visualization.py
│   │   └── logging.py
│   ├── config.py
│   └── run_experiment.py
├── configs/
│   ├── mnist_color.yaml
│   └── waterbirds.yaml
├── scripts/
│   ├── train_mnist.sh
│   └── train_waterbirds.sh
└── outputs/
    ├── mnist/
    └── waterbirds/
```

---

## 5. Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | MNIST+Color Dataset | Implement programmatic color spurious correlation | 7 | 3(loader)+2(metadata)+1(tests)+1(viz) |
| M-2 | GradCAM Integration | pytorch-grad-cam wrapper + difference maps | 8 | 3(wrapper)+3(diff_map)+2(tests) |
| M-3 | Spatial Reg Trainer | Core regularization loop + adaptive λ | 12 | 4(reg_loss)+3(mask)+3(adaptive)+2(tests) |
| M-4 | ERM Baseline | Standard training loop for MNIST + Waterbirds | 6 | 2(trainer)+2(metrics)+2(integration) |
| M-5 | GroupDRO Integration | Wrapper for official repo | 7 | 3(wrapper)+2(conversion)+2(tests) |
| M-6 | Evaluation Pipeline | WGA metrics + bootstrap + visualization | 9 | 3(metrics)+3(bootstrap)+2(viz)+1(tests) |
| M-7 | MNIST Experiments | 4 conditions × 5 seeds = 20 runs | 8 | 3(orchestration)+2(logging)+2(ablation)+1(analysis) |
| M-8 | Waterbirds Experiments | 3 methods × 5 seeds = 15 runs | 11 | 4(orchestration)+3(hyperparam)+2(logging)+2(analysis) |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M-3, M-6, M-8], Low(4-8): [M-1, M-2, M-4, M-5, M-7]

**Total Complexity:** 68

---

## 6. Interface Contracts

### 6.1 Trainer API
```python
# All trainers follow same interface
trainer.train_epoch() -> dict  # {loss, wga, avg_acc}
trainer.validate() -> dict
trainer.fit() -> dict  # best metrics
```

### 6.2 GradCAM API
```python
# Input: batch (B, C, H, W), labels (B,)
# Output: difference map (H, W) in [0, 1]
# Constraint: majority/minority identified via group annotations
```

### 6.3 Metrics API
```python
# Input: predictions (N,), labels (N,), groups (N,)
# Output: {wga: float, avg_acc: float, group_accs: List[float]}
# Constraint: 4 groups for both datasets
```

---

## 7. Computational Requirements

### 7.1 MNIST+Color
- GPU: 1× (≥8GB VRAM)
- Time: ~2 hours (20 runs × 50 epochs)
- Storage: ~500MB

### 7.2 Waterbirds
- GPU: 1× (≥16GB VRAM)
- Time: ~10 hours (15 runs × 300 epochs)
- Storage: ~5GB

### 7.3 Total Budget
- GPU hours: ~12 hours
- Storage: ~6GB

---

## 8. Key Design Decisions

### 8.1 Why MNIST+Color First?
- **Rationale:** Toy validation gates real-world experiments
- **Fallback:** If MNIST fails → abandon mitigation claim

### 8.2 Why Spatial Over Global Regularization?
- **Rationale:** Ablation study validates spatial targeting matters
- **Trade-off:** Higher GradCAM overhead (mitigated by batch subsampling)

### 8.3 Why Adaptive λ Scaling?
- **Rationale:** Fixed penalty insufficient across datasets
- **Trade-off:** Hyperparameter search over λ_init still needed

---

## 9. Validation Checkpoints

### 9.1 MNIST+Color Gates
- WGA improvement ≥10% over baseline → PASS
- Color-only accuracy ≥baseline+10% → mechanism validated
- Digit-only accuracy ≤baseline-5% → spatial targeting confirmed

### 9.2 Waterbirds Gates
- WGA ≥GroupDRO+5% → SHOULD_WORK
- Average accuracy drop ≤2% → no catastrophic overfitting
- Bootstrap p<0.05 → statistical significance

---

## 10. Risk Mitigation

### 10.1 GradCAM Overhead >2×
- **Mitigation:** Compute on 32 samples/batch max
- **Fallback:** Update every 10 batches instead of every batch

### 10.2 MNIST Fails
- **Action:** ABANDON mitigation, reframe as negative result
- **Impact:** Detection-only positioning (Tier 3)

### 10.3 Waterbirds Fails
- **Action:** PIVOT to detection-only
- **Impact:** Position regularization as future work

---

## 11. Success Criteria

**Primary:**
1. MNIST WGA ≥ baseline+10% (MUST_WORK gate)
2. Waterbirds WGA ≥ GroupDRO+5% (SHOULD_WORK gate)
3. Average accuracy drop ≤2%

**Secondary:**
1. GradCAM attention shift ≥20%
2. Bootstrap p<0.05

**Gate Logic:** (MNIST PASS AND Waterbirds PASS) → SUCCESS

---

## 12. Document Metadata

- **Generated:** 2026-08-20
- **Phase:** 3 (Architecture)
- **Status:** READY FOR IMPLEMENTATION
- **Next Action:** Phase 4 (Coding)
