---
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
document_type: architecture
created_at: 2026-05-12
author: Phase 3 Architecture Agent
version: 1.0
---

# System Architecture: H-E1 Quotient Space Existence

**Applied Patterns**: Standard PyTorch training loop, encoder-decoder architecture, metric computation pipeline

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: New implementation from scratch
**Analyzed Path**: N/A
**Findings**: No existing codebase - implementing from foundational specifications.

---

## Module Structure

### DataModule (`src/data.py`)

**Dependencies**: torch, transformers, numpy

```python
class ModelZooDataset(torch.utils.data.Dataset):
    def __init__(self, model_list: List[str], split: str, cache_dir: str): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]: ...
    def _load_and_preprocess_weights(self, model_id: str) -> torch.Tensor: ...

def download_modelzoo_14k(cache_dir: str, architectures: List[str], size_range: Tuple[int, int]) -> Dict[str, List[str]]: ...
def create_dataloaders(train_ids: List[str], val_ids: List[str], test_ids: List[str], batch_size: int, cache_dir: str) -> Tuple[DataLoader, DataLoader, DataLoader]: ...
```

### BaselineModel (`src/models/baseline.py`)

**Dependencies**: torch.nn

```python
class DeepSetsEncoder(nn.Module):
    def __init__(self, weight_dim: int, hidden_dim: int, output_dim: int): ...
    def forward(self, weights: torch.Tensor) -> torch.Tensor: ...
    def reconstruct(self, z: torch.Tensor) -> torch.Tensor: ...

class PerElementEncoder(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int): ...
    def forward(self, x: torch.Tensor) -> torch.Tensor: ...

class PostAggregationDecoder(nn.Module):
    def __init__(self, hidden_dim: int, output_dim: int): ...
    def forward(self, x: torch.Tensor) -> torch.Tensor: ...
```

### ProposedModel (`src/models/proposed.py`)

**Dependencies**: torch.nn, baseline

```python
class SlotEquivariantEncoder(nn.Module):
    def __init__(self, weight_dim: int, K: int, hidden_dim: int, num_arch_classes: int): ...
    def forward(self, weights: torch.Tensor, arch_labels: torch.Tensor) -> torch.Tensor: ...
    def reconstruct_weights(self, z: torch.Tensor) -> torch.Tensor: ...

class ArchitectureEmbedder(nn.Module):
    def __init__(self, num_classes: int, embed_dim: int): ...
    def forward(self, arch_labels: torch.Tensor) -> torch.Tensor: ...
```

### LossModule (`src/loss.py`)

**Dependencies**: torch.nn.functional, models.proposed

```python
def reconstruction_loss(original: torch.Tensor, reconstructed: torch.Tensor) -> torch.Tensor: ...
def equivariance_loss(model: nn.Module, weights: torch.Tensor, arch_labels: torch.Tensor) -> torch.Tensor: ...
def combined_loss(model: nn.Module, weights: torch.Tensor, arch_labels: torch.Tensor, lambda_equiv: float) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]: ...
```

### TrainingModule (`src/train.py`)

**Dependencies**: torch.optim, data, models, loss

```python
class Trainer:
    def __init__(self, model: nn.Module, train_loader: DataLoader, val_loader: DataLoader, config: dict): ...
    def train_epoch(self, epoch: int) -> Dict[str, float]: ...
    def validate(self) -> Dict[str, float]: ...
    def train(self, num_epochs: int) -> Dict[str, List[float]]: ...
    def save_checkpoint(self, path: str, metrics: dict): ...
    def load_checkpoint(self, path: str): ...

def setup_optimizer(model: nn.Module, lr: float, weight_decay: float) -> torch.optim.Optimizer: ...
def setup_scheduler(optimizer: torch.optim.Optimizer, T_max: int) -> torch.optim.lr_scheduler._LRScheduler: ...
```

### EvaluationModule (`src/evaluate.py`)

**Dependencies**: torch, models, data

```python
class Evaluator:
    def __init__(self, model: nn.Module, test_loader: DataLoader): ...
    def compute_reconstruction_error(self) -> float: ...
    def compute_frozen_k_generalization(self, rnn_loader: DataLoader) -> float: ...
    def compute_kernel_robustness(self, num_permutations: int) -> float: ...
    def evaluate_all(self) -> Dict[str, float]: ...

def relative_mse(original: torch.Tensor, reconstructed: torch.Tensor) -> float: ...
def measure_output_divergence(z_original: torch.Tensor, z_permuted: torch.Tensor) -> float: ...
```

### VisualizationModule (`src/visualize.py`)

**Dependencies**: matplotlib, sklearn, numpy

```python
def plot_gate_metrics(targets: Dict[str, float], actuals: Dict[str, float], save_path: str): ...
def plot_quotient_space_tsne(embeddings: np.ndarray, arch_labels: np.ndarray, save_path: str): ...
def plot_reconstruction_error_distribution(errors: np.ndarray, save_path: str): ...
def plot_k_dimensionality_analysis(k_values: List[int], errors: List[float], save_path: str): ...
def plot_training_curves(history: Dict[str, List[float]], save_path: str): ...
```

### ConfigModule (`src/config.py`)

**Dependencies**: None

```python
class Config:
    SEED: int = 42
    BATCH_SIZE: int = 32
    NUM_EPOCHS: int = 100
    LEARNING_RATE: float = 1e-3
    WEIGHT_DECAY: float = 1e-4
    HIDDEN_DIM: int = 256
    K_VALUES: List[int] = [16, 32, 64]
    LAMBDA_EQUIV_VALUES: List[float] = [0.0, 0.25, 0.5, 0.75, 1.0]
    NUM_ARCH_CLASSES: int = 3
    ARCH_EMBED_DIM: int = 64
    CACHE_DIR: str = "./data/model_zoo"
    CHECKPOINT_DIR: str = "./checkpoints"
    FIGURES_DIR: str = "./figures"
    TARGET_RECONSTRUCTION_ERROR: float = 10.0
    TARGET_FROZEN_K_GEN: float = 10.0
    TARGET_KERNEL_ROBUSTNESS: float = 90.0
```

### MainScript (`main.py`)

**Dependencies**: src.*

```python
def setup_experiment(config: Config) -> None: ...
def run_baseline_experiment(config: Config) -> Dict[str, float]: ...
def run_proposed_experiment(config: Config, lambda_equiv: float, K: int) -> Dict[str, float]: ...
def run_ablation_studies(config: Config) -> Dict[str, Dict[str, float]]: ...
def main(): ...
```

---

## File Organization

```
h-e1/
├── code/
│   ├── main.py                    # Entry point, experiment orchestration
│   ├── src/
│   │   ├── __init__.py
│   │   ├── config.py              # Hyperparameters and paths
│   │   ├── data.py                # Dataset loading and preprocessing
│   │   ├── loss.py                # Loss functions
│   │   ├── train.py               # Training loop
│   │   ├── evaluate.py            # Evaluation metrics
│   │   ├── visualize.py           # Figure generation
│   │   └── models/
│   │       ├── __init__.py
│   │       ├── baseline.py        # Deep Sets baseline
│   │       └── proposed.py        # Slot-Equivariant encoder
│   ├── requirements.txt
│   └── README.md
├── data/
│   └── model_zoo/                 # Cached HuggingFace models
├── checkpoints/                   # Model checkpoints
├── figures/                       # Generated visualizations
└── results/                       # CSV logs and metrics
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Dataset Infrastructure | Download ModelZoo-14K, implement weight extraction/preprocessing, create train/val/test splits | 14 | Module(4)+Dep(3)+Algo(4)+Integ(3) |
| A-2 | Baseline Model | Implement Deep Sets encoder (phi/rho architecture) with reconstruction decoder | 11 | Module(3)+Dep(2)+Algo(4)+Integ(2) |
| A-3 | Proposed Model | Implement Slot-Equivariant encoder with architecture embeddings and equivariance loss | 16 | Module(4)+Dep(3)+Algo(5)+Integ(4) |
| A-4 | Training Pipeline | Implement training loop with Adam optimizer, cosine annealing, early stopping, checkpointing | 12 | Module(3)+Dep(2)+Algo(4)+Integ(3) |
| A-5 | Evaluation Metrics | Implement reconstruction error, frozen-K generalization, kernel robustness measurements | 15 | Module(4)+Dep(2)+Algo(5)+Integ(4) |
| A-6 | Ablation Studies | Run experiments for K∈{16,32,64} and λ_equiv∈{0.0,0.25,0.5,0.75,1.0}, compare results | 9 | Module(2)+Dep(2)+Algo(3)+Integ(2) |
| A-7 | Visualization | Generate gate metrics chart, t-SNE, training curves, K-analysis, error distribution plots | 10 | Module(2)+Dep(2)+Algo(3)+Integ(3) |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-1, A-3, A-5], Medium(9-13): [A-2, A-4, A-6, A-7], Low(4-8): []

**Total Complexity**: 87 points across 7 tasks

---

## Data Flow

**Training Flow**:
1. ModelZooDataset loads HuggingFace models → extracts weights → normalizes → returns (weights, arch_label)
2. DataLoader batches models → (B, N, D) weight tensors + (B,) architecture labels
3. Model forward: weights + arch_labels → K-dim quotient representation z
4. Loss computation: reconstruction_loss + λ_equiv × equivariance_loss
5. Optimizer updates model parameters
6. Validation metrics logged every epoch

**Evaluation Flow**:
1. Load best checkpoint from training
2. Test set → model → compute reconstruction error (MSE / ||W||²)
3. RNN holdout → frozen model → compute frozen-K generalization error
4. Random permutations → model → measure output divergence → kernel robustness %
5. Compare against targets (10%, 10%, 90%)
6. Generate visualizations

---

## Key Design Decisions

**Weight Representation**: Models stored as flattened vectors with layer-wise normalization. Set representation handles variable architecture sizes via permutation-invariant pooling.

**Architecture Embedding**: 3-class embedding (CNN/Transformer/RNN) injected before per-element encoding to provide architecture-specific context without breaking equivariance.

**Equivariance Loss**: Random weight permutations during training enforce that quotient representations remain invariant to neuron reordering within layers.

**K Dimensionality**: Ablation over {16, 32, 64} identifies minimal sufficient quotient space dimension for <10% reconstruction error.

---

## Dependencies

**External Libraries**:
- torch>=2.0.0
- transformers>=4.30.0
- numpy>=1.24.0
- scikit-learn>=1.3.0
- matplotlib>=3.7.0
- tqdm>=4.65.0

**Compute Requirements**:
- Single GPU (≥16GB VRAM)
- 32GB RAM
- ~50GB storage for model cache

---

## Success Criteria

**Gate Conditions (MUST_WORK)**:
1. Reconstruction error <10% on test set
2. Frozen-K generalization (R_RNN) <10%
3. Kernel robustness ≥90% (D<0.01 threshold)

**Implementation Success**:
- All modules implemented and integrated
- Training converges without instability
- All evaluation metrics computed correctly
- Gate metrics comparison figure generated

---

**Document Status**: Complete
**Next Phase**: Phase 4 - Implementation
**Task File**: 03_tasks.yaml (to be generated in Phase 3 Step 9)
