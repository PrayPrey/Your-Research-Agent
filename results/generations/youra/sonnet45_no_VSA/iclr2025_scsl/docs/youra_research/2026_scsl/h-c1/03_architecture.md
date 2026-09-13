# Architecture: h-c1

**Hypothesis ID:** h-c1  
**Date:** 2026-07-11  
**Type:** CONDITION (Positive Control - PoC)  
**Architecture Pattern Applied:** PyTorch modular experiment design  

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation from scratch  
**Analyzed Path:** N/A  
**Findings:** No existing h-c1 code to analyze. Clean PoC implementation based on PyTorch best practices.

---

## System Overview

**Purpose:** Validate that rotation ±15° augmentation does NOT cause differential degradation on asymmetric digits (positive control for H-E1).

**Architecture Style:** Modular PyTorch experiment with separate baseline/rotation training pipelines.

**Data Flow:**
```
MNIST Download → Transform (baseline OR rotation) → DataLoader 
→ Training Loop → Model Checkpoints → Evaluation → Metrics + Figures
```

**Component Interaction:**
- DataModule: Provides train/test loaders for both conditions
- ModelModule: Standard CNN (shared architecture)
- TrainingModule: Train loop with early stopping
- EvaluationModule: Per-class accuracy + differential effect calculation
- VisualizationModule: Generate 4 required figures

**Execution Model:** Sequential runs (baseline first, then rotation). Two separate trained models.

---

## Module Design

### 1. DataModule (`src/data.py`)

**Dependencies:** torchvision, torch.utils.data

```python
def get_mnist_loaders(
    condition: str,  # "baseline" or "rotation"
    batch_size: int = 64,
    data_dir: str = "./data",
    val_split: float = 0.1,
    seed: int = 42
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """Returns train, val, test loaders for specified condition."""
    ...

def get_transforms(condition: str) -> transforms.Compose:
    """Returns transform pipeline for baseline or rotation."""
    ...
```

### 2. ModelModule (`src/model.py`)

**Dependencies:** torch.nn

```python
class StandardCNN(nn.Module):
    def __init__(self):
        """PyTorch Official MNIST CNN architecture."""
        ...
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Returns log probabilities (shape: batch_size x 10)."""
        ...
```

### 3. TrainingModule (`src/train.py`)

**Dependencies:** ModelModule, DataModule, torch.optim

```python
def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    config: dict,
    device: str
) -> dict:
    """Train model with early stopping. Returns training history."""
    ...

def save_checkpoint(model: nn.Module, path: str, metadata: dict) -> None:
    """Save model weights and metadata."""
    ...
```

### 4. EvaluationModule (`src/evaluate.py`)

**Dependencies:** ModelModule, DataModule

```python
def evaluate_model(
    model: nn.Module,
    test_loader: DataLoader,
    device: str
) -> dict:
    """Compute per-class accuracy and group metrics."""
    ...

def compute_differential_effect(
    per_class_acc: dict
) -> dict:
    """Calculate (asymmetric - symmetric) accuracy gap."""
    ...

def check_success(
    baseline_metrics: dict,
    rotation_metrics: dict
) -> dict:
    """Determine PASS/FAIL for positive control."""
    ...
```

### 5. VisualizationModule (`src/visualize.py`)

**Dependencies:** matplotlib, EvaluationModule

```python
def plot_gate_metrics(
    baseline_metrics: dict,
    rotation_metrics: dict,
    save_path: str
) -> None:
    """Figure 1: Gate metrics comparison (mandatory)."""
    ...

def plot_per_class_accuracy(
    baseline_metrics: dict,
    rotation_metrics: dict,
    save_path: str
) -> None:
    """Figure 2: Per-class accuracy bars."""
    ...

def plot_accuracy_gap(
    baseline_metrics: dict,
    rotation_metrics: dict,
    save_path: str
) -> None:
    """Figure 3: Differential effect comparison."""
    ...

def plot_training_curves(
    baseline_history: dict,
    rotation_history: dict,
    save_path: str
) -> None:
    """Figure 4: Train/val loss over epochs."""
    ...
```

### 6. ConfigModule (`src/config.py`)

**Dependencies:** None

```python
@dataclass
class TrainingConfig:
    batch_size: int = 64
    epochs: int = 30
    lr: float = 0.001
    patience: int = 5
    seed: int = 42
    device: str = "cuda" if torch.cuda.is_available() else "cpu"

@dataclass
class ExperimentConfig:
    data_dir: str = "./data"
    checkpoint_dir: str = "./checkpoints"
    log_dir: str = "./logs"
    results_dir: str = "./results"
    figures_dir: str = "./figures"
```

### 7. Main Orchestrator (`run_experiment.py`)

**Dependencies:** All modules

```python
def run_condition(
    condition: str,
    config: ExperimentConfig,
    train_config: TrainingConfig
) -> Tuple[nn.Module, dict, dict]:
    """Run full pipeline for one condition (baseline or rotation)."""
    ...

def main():
    """Execute baseline and rotation experiments, compare results."""
    ...
```

---

## Directory Structure

```
h-c1/
├── src/
│   ├── __init__.py
│   ├── data.py           # MNIST loading, transforms
│   ├── model.py          # Standard CNN architecture
│   ├── train.py          # Training loop, early stopping
│   ├── evaluate.py       # Metrics computation
│   ├── visualize.py      # Figure generation
│   └── config.py         # Configuration dataclasses
├── checkpoints/
│   ├── baseline_model.pt
│   └── rotation_model.pt
├── logs/
│   ├── baseline_training.json
│   └── rotation_training.json
├── results/
│   └── evaluation_metrics.json
├── figures/
│   ├── gate_metrics.png
│   ├── per_class_accuracy.png
│   ├── accuracy_gap.png
│   └── training_curves.png
├── data/                 # Auto-created by torchvision
│   └── MNIST/
├── run_experiment.py     # Main entry point
├── requirements.txt
└── README.md
```

---

## Integration Points

### 1. DataModule → TrainingModule
- `get_mnist_loaders()` returns train/val/test loaders
- TrainingModule consumes loaders in `train_model()`

### 2. TrainingModule → Checkpoints
- `train_model()` monitors val accuracy
- Best model saved via `save_checkpoint()` to `checkpoints/{condition}_model.pt`
- Training history logged to `logs/{condition}_training.json`

### 3. Checkpoints → EvaluationModule
- `evaluate_model()` loads checkpoint from disk
- Runs inference on test set
- Computes per-class accuracy

### 4. EvaluationModule → VisualizationModule
- Metrics dict passed to all plot functions
- `plot_*()` functions save to `figures/`

### 5. Main Orchestrator Flow
```python
# Baseline condition
baseline_loaders = get_mnist_loaders(condition="baseline")
baseline_model = StandardCNN()
baseline_history = train_model(baseline_model, baseline_loaders[0], baseline_loaders[1], ...)
save_checkpoint(baseline_model, "checkpoints/baseline_model.pt", ...)
baseline_metrics = evaluate_model(baseline_model, baseline_loaders[2], ...)

# Rotation condition (same pattern)
rotation_loaders = get_mnist_loaders(condition="rotation")
...

# Comparison
success_check = check_success(baseline_metrics, rotation_metrics)
plot_gate_metrics(baseline_metrics, rotation_metrics, "figures/gate_metrics.png")
...
```

---

## Error Handling Strategy

### Device Management
```python
device = "cuda" if torch.cuda.is_available() else "cpu"
if device == "cpu":
    logging.warning("CUDA not available, using CPU (slower)")
```

### Data Loading
```python
try:
    train_loader = get_mnist_loaders(...)
except Exception as e:
    logging.error(f"Data loading failed: {e}")
    raise RuntimeError("Cannot proceed without data") from e
```

### Training Divergence
```python
if torch.isnan(loss):
    logging.error(f"NaN loss detected at epoch {epoch}")
    raise ValueError("Training diverged - check learning rate")
```

### Early Stopping Trigger
```python
if epochs_without_improvement >= patience:
    logging.info(f"Early stopping triggered at epoch {epoch}")
    break
```

### File I/O
```python
os.makedirs(checkpoint_dir, exist_ok=True)
try:
    torch.save(state_dict, path)
except Exception as e:
    logging.error(f"Checkpoint save failed: {e}")
    # Continue training (non-fatal)
```

---

## Logging & Monitoring

### Console Logging
```python
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# tqdm for epoch progress
from tqdm import tqdm
for epoch in tqdm(range(epochs), desc="Training"):
    ...
```

### Training Logs (JSON)
```json
{
  "condition": "baseline",
  "epochs": [
    {"epoch": 1, "train_loss": 0.234, "val_loss": 0.198, "val_acc": 0.965},
    {"epoch": 2, "train_loss": 0.145, "val_loss": 0.123, "val_acc": 0.981}
  ],
  "best_epoch": 15,
  "best_val_acc": 0.992
}
```

### Checkpoint Strategy
- Save checkpoint when `val_acc > best_val_acc`
- Overwrite previous best checkpoint (space-efficient)
- Include metadata: epoch, val_acc, config

### Evaluation Results (JSON)
```json
{
  "baseline": {
    "overall_acc": 0.992,
    "per_class": {0: 0.995, 1: 0.998, ..., 9: 0.989},
    "symmetric_acc": 0.994,
    "asymmetric_acc": 0.991,
    "differential_effect": -0.003
  },
  "rotation": {
    "overall_acc": 0.993,
    "per_class": {...},
    "symmetric_acc": 0.992,
    "asymmetric_acc": 0.993,
    "differential_effect": 0.001
  },
  "success_check": {
    "passed": true,
    "reason": "abs(rotation_diff) <= abs(baseline_diff)"
  }
}
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup Project Structure | Create directories, requirements.txt, config module | 4 | Module(1) + Deps(1) + Config(2) |
| A-2 | Implement DataModule | MNIST loading, baseline/rotation transforms, DataLoaders | 8 | Dataset(2) + Transforms(2) + Splits(2) + Integration(2) |
| A-3 | Implement ModelModule | Standard CNN architecture (PyTorch Official pattern) | 6 | Architecture(3) + Forward(2) + Testing(1) |
| A-4 | Implement TrainingModule | Train loop, early stopping, checkpoint saving | 14 | Loop(4) + EarlyStopping(3) + Checkpoints(3) + Logging(4) |
| A-5 | Implement EvaluationModule | Per-class accuracy, differential effect, success check | 12 | Inference(3) + Metrics(4) + DiffEffect(3) + SuccessCheck(2) |
| A-6 | Implement VisualizationModule | Generate 4 required figures (gate metrics, per-class, gap, curves) | 10 | Figure1(3) + Figure2(2) + Figure3(2) + Figure4(3) |
| A-7 | Implement Main Orchestrator | Run baseline + rotation, compare, save results | 9 | Pipeline(4) + Comparison(3) + Output(2) |
| A-8 | Run Experiments & Validate | Execute both conditions, verify success check, generate validation report | 11 | Baseline(3) + Rotation(3) + Validation(3) + Report(2) |

**Distribution:**  
- VeryHigh (18-20): []
- High (14-17): [A-4]
- Medium (9-13): [A-2, A-5, A-6, A-7, A-8]
- Low (4-8): [A-1, A-3]

**Total Complexity:** 74 (appropriate for PoC positive control)

**Estimated Duration:** 6-8 hours (including experiment runtime)

---

## Key Design Decisions

### 1. Separate Runs vs Single Run
**Decision:** Run baseline and rotation as separate experiments (not in same training run)  
**Rationale:** Cleaner isolation, independent checkpoint management, easier debugging

### 2. Fixed Seed (No Multiple Seeds)
**Decision:** Single seed (42) for PoC  
**Rationale:** CONDITION hypothesis (positive control), not main effect. Multiple seeds reserved for H-E1.

### 3. Early Stopping on Validation Accuracy
**Decision:** Patience 5 epochs, monitor val_acc (not val_loss)  
**Rationale:** Accuracy is the metric of interest, prevents overfitting

### 4. No Learning Rate Scheduler
**Decision:** Fixed lr=0.001 for 30 epochs  
**Rationale:** MNIST converges quickly, scheduler adds complexity without benefit (researched repos confirm)

---

## Validation Checkpoints

**Pre-Experiment:**
- [ ] MNIST dataset downloads successfully
- [ ] Transforms apply correctly (visual inspection of augmented images)
- [ ] Model forward pass produces correct output shape

**During Experiment:**
- [ ] Baseline model converges within 30 epochs
- [ ] Rotation model converges within 30 epochs
- [ ] No NaN losses detected
- [ ] Checkpoints saved successfully

**Post-Experiment:**
- [ ] Baseline achieves ~99% test accuracy
- [ ] Rotation achieves ≥99% test accuracy
- [ ] Differential effect computed for both conditions
- [ ] Success check determines PASS/FAIL
- [ ] All 4 figures generated
- [ ] Validation report (04_validation.md) written

---

## Risk Mitigation

### R1: Baseline Underperforms (<99%)
**Mitigation:** Verify normalization parameters (0.1307, 0.3081), check architecture matches PyTorch Official

### R2: Rotation Underperforms
**Mitigation:** Verify RandomRotation applied only during training (not test), visual inspection of augmented images

### R3: Rotation Creates Differential Effect (FAIL)
**Mitigation:** Re-run with different seed, consider alternative positive control (translation, brightness)

### R4: GPU Out of Memory
**Mitigation:** Auto-fallback to CPU, reduce batch size if needed (64 → 32)

---

## Dependencies

**Core:**
- torch >= 2.0
- torchvision >= 0.15
- numpy >= 1.24

**Metrics & Visualization:**
- matplotlib >= 3.5
- tqdm >= 4.65

**Utils:**
- pyyaml >= 6.0 (optional, for config files)

**Install:**
```bash
pip install torch torchvision numpy matplotlib tqdm
```

---

**Next Phase:** Phase 4 - Implementation (Coding)  
**Status:** ARCHITECTURE COMPLETE
