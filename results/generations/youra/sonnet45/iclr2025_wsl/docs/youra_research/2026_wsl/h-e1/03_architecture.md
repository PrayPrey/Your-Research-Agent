# System Architecture: h-e1 CAWE Implementation

**Hypothesis:** h-e1 (EXISTENCE)
**Date:** 2026-03-19
**Type:** PoC (Proof of Concept)
**Applied:** Minimal EXISTENCE pattern

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** New implementation from scratch
**Analyzed Path:** N/A
**Findings:** No existing codebase. First hypothesis in research pipeline with no prerequisites.

---

## System Overview

Minimal PoC architecture to validate EXISTENCE hypothesis: architecture-agnostic weight encoder (CAWE) achieves Spearman ρ > 0.7 for generalization gap prediction across heterogeneous model zoo (CNNs, Transformers, MLPs).

**Core Components:**
- Data loader (heterogeneous model zoo)
- Baseline model (flat-weight MLP)
- Proposed model (CAWE: tokenizers + NFT backbone + regression head)
- Training loop (single script)
- Evaluation script (Spearman ρ + bootstrap CI)

---

## Module Architecture

### DataLoader (`cawe/data/loader.py`)

**Dependencies:** torch, timm, torchvision

```python
class ModelZooDataset(torch.utils.data.Dataset):
    def __init__(self, data_dir: str, split: str = 'train'): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> Tuple[Dict[str, torch.Tensor], str, float]: ...
    # Returns: (state_dict, arch_family, generalization_gap)

def load_model_zoo(data_dir: str, batch_size: int = 32) -> Tuple[DataLoader, DataLoader, DataLoader]:
    # Returns: train_loader, val_loader, test_loader
    ...
```

### Baseline Model (`cawe/baselines/flat_mlp.py`)

**Dependencies:** torch.nn

```python
class FlatWeightMLP(nn.Module):
    def __init__(self, input_dim: int): ...
    def forward(self, weights: torch.Tensor) -> torch.Tensor: ...
    # Input: Flattened weight vector
    # Output: Generalization gap prediction (scalar)
```

### CAWE Tokenizers (`cawe/tokenizers/tokenizers.py`)

**Dependencies:** torch.nn

```python
class CNNTokenizer(nn.Module):
    def __init__(self, token_dim: int = 128): ...
    def forward(self, state_dict: Dict[str, torch.Tensor]) -> torch.Tensor: ...
    # Returns: (num_layers, token_dim)

class TransformerTokenizer(nn.Module):
    def __init__(self, token_dim: int = 128): ...
    def forward(self, state_dict: Dict[str, torch.Tensor]) -> torch.Tensor: ...
    # Returns: (num_layers, token_dim)

class MLPTokenizer(nn.Module):
    def __init__(self, token_dim: int = 128): ...
    def forward(self, state_dict: Dict[str, torch.Tensor]) -> torch.Tensor: ...
    # Returns: (num_layers, token_dim)
```

### CAWE Model (`cawe/models/cawe.py`)

**Dependencies:** tokenizers, nfn (external library)

```python
class CAWE(nn.Module):
    def __init__(self, token_dim: int = 128, nft_channels: int = 64): ...
    def forward(self, weights: Dict[str, torch.Tensor], arch_family: str) -> torch.Tensor: ...
    # arch_family: 'cnn' | 'transformer' | 'mlp'
    # Returns: Generalization gap prediction (scalar)
```

### Training Script (`scripts/train.py`)

**Dependencies:** DataLoader, FlatWeightMLP, CAWE, torch.optim

```python
def train_epoch(model, loader, optimizer, criterion) -> float: ...
def validate(model, loader) -> float:
    # Returns: Spearman ρ on validation set
    ...
def main():
    # Training loop with early stopping
    ...
```

### Evaluation Script (`scripts/evaluate.py`)

**Dependencies:** CAWE, FlatWeightMLP, scipy.stats

```python
def compute_spearman_with_ci(y_true: np.ndarray, y_pred: np.ndarray, n_bootstrap: int = 1000) -> Tuple[float, float, float]:
    # Returns: (rho, ci_lower, ci_upper)
    ...

def evaluate_per_architecture(model, test_loader) -> Dict[str, float]:
    # Returns: {'cnn': rho_cnn, 'transformer': rho_transformer, 'mlp': rho_mlp}
    ...

def main():
    # Load models, compute metrics, save results
    ...
```

### Visualization Script (`scripts/visualize.py`)

**Dependencies:** matplotlib, seaborn, sklearn.manifold

```python
def plot_spearman_comparison(cawe_rho, baseline_rho, cawe_ci, baseline_ci, save_path: str): ...
def plot_per_architecture_performance(rho_dict: Dict[str, float], save_path: str): ...
def plot_prediction_scatter(y_true, y_pred, save_path: str): ...
def plot_tsne_clustering(embeddings, labels, save_path: str): ...
```

---

## File Structure

```
h-e1/
├── code/
│   ├── cawe/
│   │   ├── __init__.py
│   │   ├── data/
│   │   │   ├── __init__.py
│   │   │   └── loader.py          # ModelZooDataset, load_model_zoo
│   │   ├── baselines/
│   │   │   ├── __init__.py
│   │   │   └── flat_mlp.py        # FlatWeightMLP
│   │   ├── tokenizers/
│   │   │   ├── __init__.py
│   │   │   └── tokenizers.py      # CNNTokenizer, TransformerTokenizer, MLPTokenizer
│   │   └── models/
│   │       ├── __init__.py
│   │       └── cawe.py            # CAWE
│   ├── scripts/
│   │   ├── train.py               # Training loop
│   │   ├── evaluate.py            # Evaluation + metrics
│   │   └── visualize.py           # Figure generation
│   ├── requirements.txt
│   └── README.md
├── data/
│   └── model_zoo/                 # Dataset (not version controlled)
│       ├── vit/
│       ├── cnn/
│       └── mlp/
├── checkpoints/                   # Saved models
├── results/                       # Metrics CSV
└── figures/                       # Visualization outputs
```

---

## External Dependencies

### Python Packages (requirements.txt)

```
torch>=2.0
nfn
timm
torchvision
scipy
numpy
pandas
matplotlib
seaborn
scikit-learn
```

### NFN Library Integration

**Library:** `nfn` (github.com/AllanYangZhou/nfn, NeurIPS 2023)
**Installation:** `pip install nfn`
**Usage Pattern:**

```python
from nfn import layers
from nfn.common import state_dict_to_tensors, network_spec_from_wsfeat

# Convert weights to NFN format
wsfeat = state_dict_to_tensors(model.state_dict())
network_spec = network_spec_from_wsfeat(wsfeat)

# Build NFN backbone
nfn_encoder = nn.Sequential(
    layers.NPLinear(network_spec, 128, 64, io_embed=True),
    layers.TupleOp(nn.ReLU()),
    layers.NPLinear(network_spec, 64, 128, io_embed=True)
)
```

**Note:** Original NFN library expects homogeneous model zoos. CAWE extends this with architecture-specific tokenizers to handle heterogeneous zoos.

---

## Data Flow

```
Model Zoo (750 models)
    ↓
[DataLoader]
    ↓
Architecture-Specific Tokenizer (CNN/Transformer/MLP)
    ↓
Tokenized Weights (num_layers, D=128)
    ↓
NFT Backbone (NPLinear layers)
    ↓
Encoded Features (permutation-equivariant)
    ↓
Global Average Pooling
    ↓
Regression Head
    ↓
Generalization Gap Prediction
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Dataset Assembly | Download/generate heterogeneous model zoo (750 models: 250 ViT, 250 CNN, 250 MLP) with generalization gap metadata | 11 | Module(3) + Dep(2) + Algo(3) + Integ(3) |
| A-2 | Baseline Implementation | Implement FlatWeightMLP baseline model | 6 | Module(2) + Dep(1) + Algo(1) + Integ(2) |
| A-3 | Tokenizer Implementation | Implement 3 architecture-specific tokenizers (CNN, Transformer, MLP) | 12 | Module(3) + Dep(2) + Algo(4) + Integ(3) |
| A-4 | CAWE Model Integration | Integrate tokenizers + NFT backbone + regression head into CAWE model | 14 | Module(3) + Dep(4) + Algo(3) + Integ(4) |
| A-5 | Training Pipeline | Implement training loop with early stopping and validation monitoring | 10 | Module(2) + Dep(2) + Algo(3) + Integ(3) |
| A-6 | Evaluation Pipeline | Implement Spearman ρ computation with bootstrap CI and per-architecture metrics | 9 | Module(2) + Dep(2) + Algo(3) + Integ(2) |
| A-7 | Visualization Generation | Generate 4 required figures (comparison, per-arch, scatter, t-SNE) | 8 | Module(2) + Dep(2) + Algo(2) + Integ(2) |

**Total Complexity:** 70
**Distribution:** VeryHigh(18-20): [], High(14-17): [A-4], Medium(9-13): [A-1, A-3, A-5, A-6], Low(4-8): [A-2, A-7]

**Task Dependencies:**
- A-2, A-3, A-4 depend on A-1 (dataset ready)
- A-5 depends on A-2, A-4 (models implemented)
- A-6 depends on A-5 (training complete)
- A-7 depends on A-6 (metrics computed)

---

## Configuration

**Hardcoded Constants (LIGHT tier - no config files):**

```python
# Training hyperparameters
LEARNING_RATE = 1e-4
BATCH_SIZE = 32
EPOCHS = 100
EARLY_STOPPING_PATIENCE = 10
WEIGHT_DECAY = 1e-2

# Model hyperparameters
TOKEN_DIM = 128
NFT_CHANNELS = 64
DROPOUT = 0.1

# Dataset split
TRAIN_SIZE = 600  # 200/200/200 per family
VAL_SIZE = 0  # Use early stopping on validation split from train
TEST_SIZE = 150  # 50/50/50 per family

# Reproducibility
RANDOM_SEED = 42

# Bootstrap
N_BOOTSTRAP = 1000
```

---

## Success Criteria

### PoC Pass (MUST_WORK Gate)
1. Code runs without error
2. CAWE Spearman ρ > Baseline Spearman ρ

### Hypothesis Validation (Primary)
1. CAWE Spearman ρ > 0.7 on test set
2. 95% CI lower bound > 0.7

### Secondary Metrics
1. Per-architecture ρ > 0.65 (CNN, Transformer, MLP)
2. Δρ = ρ_CAWE - ρ_baseline > 0.15

### Failure Response
- If ρ < 0.7 → MUST_WORK gate fails → ABANDON h-e1 → ROUTE_TO_PHASE_0

---

## Implementation Notes

### NFT Backbone Adaptation

The NFN library (`nfn`) is designed for homogeneous model zoos. CAWE extends this by:
1. Pre-processing heterogeneous weights with architecture-specific tokenizers
2. Projecting to shared D=128 token space
3. Using NFT layers (NPLinear) to process tokenized representations
4. Maintaining permutation-equivariance across all architectures

### Model Zoo Assembly Strategy

**ViT Models (250):**
- Source: HuggingFace `timm` library
- Method: `timm.create_model('vit_base_patch16_224', pretrained=True)` and variants
- Generalization gap: Fine-tune on CIFAR-10/ImageNet, compute train_acc - test_acc

**CNN Models (250):**
- Source: `torchvision.models`
- Method: `torchvision.models.resnet50(pretrained=True)` and variants
- Generalization gap: Same as ViT

**MLP Models (250):**
- Source: Zenodo 5645138 (Unterthiner MNIST MLPs) or generate locally
- Method: Download pre-computed weights or train MNIST MLPs with varying architectures
- Generalization gap: Provided in dataset or compute from training logs

**Stratification:**
- Train: 200 CNN + 200 Transformer + 200 MLP = 600
- Test: 50 CNN + 50 Transformer + 50 MLP = 150
- Random seed: 42 for reproducibility

### Tokenization Strategy

**CNN Tokenizer:**
- Extract convolutional layer weights: `state_dict['layer*.conv*.weight']`
- Flatten kernel tensors: `[out_ch, in_ch, kh, kw] → [out_ch, in_ch*kh*kw]`
- Project to D=128: `nn.Linear(in_ch*kh*kw, 128)`
- Output: (num_conv_layers, 128)

**Transformer Tokenizer:**
- Extract Q/K/V matrices: `state_dict['*attn.qkv.weight']`
- Project to D=128: `nn.Linear(qkv_dim, 128)`
- Output: (num_attn_layers, 128)

**MLP Tokenizer:**
- Extract FC layer weights: `state_dict['fc*.weight']`
- Project to D=128: `nn.Linear(fc_dim, 128)`
- Output: (num_fc_layers, 128)

All tokenizers output fixed-length token sequences for NFT backbone processing.

---

## Resource Requirements

**GPU:**
- Single GPU (user sets `CUDA_VISIBLE_DEVICES`)
- Estimated memory: < 16GB (model zoo + CAWE model)

**Disk:**
- Model zoo: ~2GB
- Checkpoints: ~500MB
- Results: ~10MB

**Training Time:**
- Estimated: < 2 hours for 100 epochs (600 models, batch_size=32)

---

*Generated by Phase 3 Architecture Design*
*Next: Phase 4 Implementation*
