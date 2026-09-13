# Architecture Specification: h-m2

**Hypothesis:** CNNs show larger temporal gaps than Vision Transformers (Δ_ResNet > Δ_ViT by ≥2 epochs) due to architectural inductive bias differences

**Type:** EXISTENCE (PoC) - Minimal architecture for "does it work?" validation

**Date:** 2026-08-29

**Applied:** PyTorch training patterns, timm model loading, gradient-based convergence detection from h-e1

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (h-e1)
**Status:** Reusing convergence detection and ablation training patterns
**Analyzed Path:** `docs/youra_research/h-e1/code/`
**Findings:** AblationTrainer with gradient norm tracking exists - pattern extensible to new architectures

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| AblationTrainer | `sys.path.append('../h-e1/code'); from model import AblationTrainer` | `h-e1/code/model.py` |
| Convergence Detection | Reimplement locally (gradient norm logic) | `h-e1/code/model.py:63-87` |

**Verified from:** `docs/youra_research/h-e1/code/` (actual implementation)

---

## Module Design

### 1. DataModule (`data.py`)

**Dependencies:** torch, wilds, torchvision

```python
class DatasetConfig:
    def __init__(self, name: str, batch_size: int): ...

def get_waterbirds_loader(split: str, batch_size: int) -> DataLoader:
    """Load Waterbirds from WILDS package."""
    ...

def get_celeba_loader(split: str, batch_size: int) -> DataLoader:
    """Load CelebA from WILDS package."""
    ...
```

---

### 2. ModelModule (`model.py`)

**Dependencies:** timm, torch.nn

```python
def create_resnet50(num_classes: int = 2) -> nn.Module:
    """ResNet-50 from timm, from-scratch training."""
    ...

def create_vit_base(num_classes: int = 2) -> nn.Module:
    """ViT-B/16 from timm, from-scratch training."""
    ...

class ConvergenceTracker:
    """Track gradient norms and detect convergence (from h-e1 pattern)."""
    def __init__(self, window: int = 3, threshold: float = 0.1): ...
    def update(self, grad_norm: float) -> bool: ...
    def get_convergence_epoch(self) -> int: ...
```

---

### 3. TrainModule (`train.py`)

**Dependencies:** model, data, torch.optim

```python
class AblationExperiment:
    """Train spurious-only and core-only variants for one architecture."""
    def __init__(self, arch: str, dataset: str, seed: int, device: str): ...
    def train_spurious_only(self, max_epochs: int) -> int: ...
    def train_core_only(self, max_epochs: int) -> int: ...
    def compute_temporal_gap(self) -> float: ...

def run_seed_experiment(arch: str, dataset: str, seed: int) -> dict:
    """Run single seed: returns E_spurious, E_core, delta."""
    ...
```

---

### 4. MainScript (`main.py`)

**Dependencies:** train, evaluate

```python
def run_poc():
    """Run PoC: 1 architecture, 1 seed, check Δ > 0."""
    ...

def run_full_experiment():
    """Run full: 2 architectures × 10 seeds × 2 datasets."""
    ...

if __name__ == '__main__':
    run_poc()  # Start with PoC validation
```

---

### 5. EvaluationModule (`evaluate.py`)

**Dependencies:** scipy.stats, numpy

```python
def compute_temporal_gap_stats(results: list) -> dict:
    """Compute mean/std of delta across seeds."""
    ...

def test_architectural_difference(resnet_deltas: list, vit_deltas: list) -> dict:
    """Independent t-test: Δ_ResNet > Δ_ViT."""
    ...

def plot_convergence_curves(grad_norms: dict, save_path: str): ...
def plot_temporal_gap_comparison(results: dict, save_path: str): ...
```

---

## File Structure

```
h-m2/
├── code/
│   ├── data.py          # Waterbirds/CelebA loading
│   ├── model.py         # ResNet-50/ViT-B/16 + ConvergenceTracker
│   ├── train.py         # AblationExperiment runner
│   ├── evaluate.py      # Statistical tests + plots
│   └── main.py          # Orchestration (PoC then full)
├── figures/             # Generated plots
└── results/             # Convergence logs per seed
```

---

## Epic Tasks (EXISTENCE Level)

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Pipeline | Load Waterbirds/CelebA from WILDS, spurious/core masks | 8 | dataset(3)+masks(3)+validation(2) |
| A-2 | Model Setup | Create ResNet-50/ViT-B/16 from timm, convergence tracker | 7 | timm_integration(3)+tracker(2)+test(2) |
| A-3 | Ablation Training | Train spurious/core variants with gradient tracking | 9 | loop(3)+masking(3)+convergence(3) |
| A-4 | PoC Validation | Run ResNet PoC (1 seed), verify Δ > 0 | 6 | single_run(3)+logging(2)+check(1) |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3], Low(4-8): [A-1, A-2, A-4]

**Total Complexity:** 30 (focused on minimal PoC first)

---

## Training Configuration

### Architecture-Specific Hyperparameters

**ResNet-50:**
- Optimizer: SGD (momentum=0.9, weight_decay=1e-4)
- Learning rate: 0.001
- Scheduler: CosineAnnealingLR (T_max=50)
- Batch size: 256

**ViT-B/16:**
- Optimizer: SGD (momentum=0.9, weight_decay=0.05)
- Learning rate: 0.0003
- Scheduler: CosineAnnealingLR (T_max=50)
- Batch size: 512

**Convergence Detection (from h-e1):**
- Criterion: grad_norm < 10% of peak_norm for 3 consecutive epochs
- Tracked separately: spurious-only and core-only variants
- Output: E_spurious, E_core → Δ = E_core - E_spurious

---

## Evaluation Metrics

**Primary:**
- Temporal gap Δ = E_core - E_spurious (epochs)
- Statistical test: Independent t-test on (Δ_ResNet, Δ_ViT) across 10 seeds
- Success: p < 0.05 AND (Δ_ResNet - Δ_ViT) ≥ 2 epochs

**Secondary:**
- Worst-group accuracy (Waterbirds/CelebA groups)
- Overall test accuracy

---

## PoC Success Criteria

1. Code runs without error
2. ResNet Δ > 0 (temporal gap exists)
3. ViT Δ > 0 (temporal gap exists)
4. Convergence detection triggers within 50 epochs

**Gate Threshold:** Δ_ResNet - Δ_ViT ≥ 2 epochs (statistical validation in full run)

---

## Implementation Notes

**Reused from h-e1:**
- Gradient norm convergence detection logic
- SGD optimizer setup with momentum 0.9
- Ablation training pattern (spurious-only/core-only)

**New for h-m2:**
- timm library integration (ResNet-50, ViT-B/16)
- Architecture-specific hyperparameters (batch size, LR)
- WILDS package for Waterbirds/CelebA loading
- Comparative statistical test (ResNet vs ViT)

---

**Next Phase:** Phase 4 - Code Implementation
