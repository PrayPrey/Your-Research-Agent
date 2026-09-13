# Architecture Specification: h-m1

**Date:** 2026-08-28  
**Author:** Phase 3 Architecture Agent  
**Hypothesis:** Transformer backbones capture global weight dependencies while Equivariant GNN backbones capture local permutation-symmetric patterns  
**Type:** MECHANISM  
**Applied:** Archon KB patterns (DL experiment structure, perturbation protocol)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Patterns found from h-e1 implementation  
**Analyzed Path:** h-e1/src/  
**Findings:** Reusing TimmModelZooLoader, WeightTokenizer, Trainer from h-e1. Adding GNN model and perturbation modules.

---

## System Overview

Test whether Transformer captures global dependencies (symmetry differential <10%) while Equivariant GNN captures local permutation-symmetric patterns (differential >30%) via within-layer vs across-layer perturbation analysis.

**Data Flow:**
```
h-e1 components → [transformer | gnn] → evaluate unperturbed → apply perturbations → measure differential
```

---

## Module Structure

### 1. DataLoader (`src/data_loader.py` - REUSED FROM H-E1)

**External Dependency:** h-e1/src/data_loader.py

```python
# Import from h-e1 implementation
from h_e1.src.data_loader import TimmModelZooLoader, WeightTokenizer
```

**No changes needed** - h-e1 provides:
- `TimmModelZooLoader.load_models() -> [(name, model, family_id), ...]`
- `WeightTokenizer.tokenize(weights) -> [num_layers, max_size]`

---

### 2. Models (`src/model.py`)

**Dependencies:** torch.nn, torch_geometric.nn.EGNNConv, h-e1 WeightTransformer

```python
class WeightGNN(nn.Module):
    def __init__(self, max_layer_size: int, hidden_dim: int, num_gnn_layers: int, 
                 num_classes: int, k_neighbors: int): ...
    def construct_graph(self, batch_size: int, num_nodes: int) -> Tensor: ...
    def forward(self, layer_tokens: Tensor) -> Tensor: ...

# Reuse from h-e1
from h_e1.src.model import WeightTransformer
```

**Interfaces:**
- `WeightGNN.forward([batch, num_layers, max_size]) -> [batch, num_classes]`
- `construct_graph(batch_size, num_nodes) -> edge_index [2, num_edges]`: Fully connected graph

**Architecture:**
- Embedding: Linear(max_layer_size → hidden_dim)
- GNN: 2× EGNNConv layers (permutation-equivariant message passing)
- Pooling: Mean over nodes (permutation-invariant)
- Head: Linear(hidden_dim → num_classes)

---

### 3. Perturbations (`src/perturbations.py` - NEW)

**Dependencies:** torch

```python
def permute_within_layer(layer_tokens: Tensor, seed: int = None) -> Tensor: ...
def permute_across_layers(layer_tokens: Tensor, seed: int = None) -> Tensor: ...
def apply_perturbation(layer_tokens: Tensor, perturb_type: str, seed: int) -> Tensor: ...
```

**Interfaces:**
- `permute_within_layer([batch, T, L]) -> [batch, T, L]`: Shuffle indices within each layer
- `permute_across_layers([batch, T, L]) -> [batch, T, L]`: Shuffle indices across all layers
- `apply_perturbation(tokens, type, seed)`: Unified interface, type in {None, 'within', 'across'}

**Implementation:**
```python
def permute_within_layer(layer_tokens: Tensor, seed: int = None) -> Tensor:
    # ponytail: in-place shuffle per layer, deterministic via seed
    if seed is not None:
        torch.manual_seed(seed)
    perturbed = layer_tokens.clone()
    B, T, L = perturbed.shape
    for b in range(B):
        for t in range(T):
            idx = torch.randperm(L)
            perturbed[b, t] = perturbed[b, t, idx]
    return perturbed

def permute_across_layers(layer_tokens: Tensor, seed: int = None) -> Tensor:
    # ponytail: flatten all layers, shuffle, reshape
    if seed is not None:
        torch.manual_seed(seed)
    B, T, L = layer_tokens.shape
    perturbed = layer_tokens.clone().view(B, -1)
    for b in range(B):
        idx = torch.randperm(T * L)
        perturbed[b] = perturbed[b, idx]
    return perturbed.view(B, T, L)
```

---

### 4. Training (`src/train.py` - REUSED FROM H-E1)

**External Dependency:** h-e1/src/train.py

```python
from h_e1.src.train import Trainer, EarlyStopping
```

**No changes needed** - h-e1 provides standard training loop.

---

### 5. Evaluation (`src/evaluate.py`)

**Dependencies:** torch, h-e1 evaluate module, src.perturbations

```python
def evaluate_with_perturbations(
    model: nn.Module, 
    test_loader: DataLoader, 
    device: str, 
    seed: int
) -> dict[str, float]: ...

def compute_symmetry_differential(results: dict) -> float: ...

def plot_differential_comparison(
    transformer_results: dict, 
    gnn_results: dict, 
    save_path: str
): ...

def plot_degradation_heatmap(
    transformer_results: dict, 
    gnn_results: dict, 
    save_path: str
): ...
```

**Interfaces:**
- `evaluate_with_perturbations() -> {unperturbed_acc, within_acc, across_acc}`
- `compute_symmetry_differential(results) -> |within_acc - across_acc|`
- `plot_differential_comparison()`: Bar chart (Transformer vs GNN differential)
- `plot_degradation_heatmap()`: 2×3 heatmap (2 models × 3 perturbation types)

---

### 6. Configuration (`src/config.py`)

**Dependencies:** dataclasses, yaml

```python
@dataclass
class ModelConfig:
    transformer: dict  # d_model, nhead, num_layers, ...
    gnn: dict          # hidden_dim, num_gnn_layers, k_neighbors

@dataclass
class PerturbationConfig:
    seed: int
    perturbation_types: list[str]  # ['within', 'across']

@dataclass
class ExperimentConfig:
    data: DataConfig      # from h-e1
    models: ModelConfig
    training: TrainingConfig  # from h-e1
    perturbation: PerturbationConfig
    gate_thresholds: dict  # gnn_differential_min, transformer_differential_max
```

---

### 7. Main Entry Point (`src/main.py`)

**Dependencies:** all modules, h-e1 components

```python
def train_model(model_type: str, config: ExperimentConfig, 
                train_data, val_data) -> nn.Module: ...

def evaluate_model_with_perturbations(
    model: nn.Module, 
    test_data, 
    config: ExperimentConfig
) -> dict: ...

def check_gate(transformer_results: dict, gnn_results: dict, 
               thresholds: dict) -> bool: ...

def main(config_path: str): ...
```

**Interfaces:**
- `train_model(type, config, train, val) -> trained_model`: Reuse h-e1 Trainer
- `evaluate_model_with_perturbations() -> {unperturbed_acc, within_acc, across_acc, differential}`
- `check_gate() -> bool`: PASS if gnn_diff >30% AND transformer_diff <10%
- `main()`: Train both models → evaluate with perturbations → compare differentials → generate figures → check gate

---

## File Structure

```
h-m1/
├── src/
│   ├── model.py             # WeightGNN (new)
│   ├── perturbations.py     # Perturbation functions (new)
│   ├── evaluate.py          # Perturbation evaluation + plots (new)
│   ├── config.py            # Extended config with GNN + perturbation (new)
│   └── main.py              # Entry point (new)
├── config.yaml              # Hyperparameters
└── figures/                 # Generated plots
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| TimmModelZooLoader | `from h_e1.src.data_loader import TimmModelZooLoader` | h-e1/src/data_loader.py |
| WeightTokenizer | `from h_e1.src.data_loader import WeightTokenizer` | h-e1/src/data_loader.py |
| WeightTransformer | `from h_e1.src.model import WeightTransformer` | h-e1/src/model.py |
| Trainer | `from h_e1.src.train import Trainer` | h-e1/src/train.py |
| EarlyStopping | `from h_e1.src.train import EarlyStopping` | h-e1/src/train.py |

**Verified from:** h-e1/src/ (actual implementation)

---

## Dependency Graph

```
External Libraries:
- torch (nn, optim)
- torch_geometric (EGNNConv)
- timm (via h-e1)

External Modules (h-e1):
- data_loader (TimmModelZooLoader, WeightTokenizer)
- model (WeightTransformer)
- train (Trainer, EarlyStopping)

Internal (h-m1):
model (WeightGNN) ← main
perturbations ← evaluate
evaluate ← main
config ← main
```

---

## Configuration Schema

```yaml
data:
  source: timm
  families: [resnet, vit, efficientnet, convnext]
  num_models: 100
  train_split: 0.7
  val_split: 0.15
  test_split: 0.15
  cache_path: ./data/model_zoo_cache/
  max_layer_size: 4096

models:
  transformer:
    d_model: 256
    nhead: 8
    num_layers: 6
    dim_feedforward: 1024
    dropout: 0.1
    num_classes: 4
  gnn:
    hidden_dim: 128
    num_gnn_layers: 2
    k_neighbors: 5  # unused (fully connected)
    num_classes: 4

training:
  optimizer: AdamW
  lr: 1e-3
  weight_decay: 1e-4
  batch_size: 32
  epochs: 50
  early_stopping_patience: 10

perturbation:
  seed: 42
  perturbation_types: ['within', 'across']

gate_thresholds:
  gnn_differential_min: 0.30
  transformer_differential_max: 0.10

random_seed: 42
device: cuda
output_dir: ./h-m1/
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M1-1 | GNN model | WeightGNN with EGNNConv + graph construction | 11 | 3(embed)+4(gnn)+2(graph)+2(head) |
| M1-2 | Perturbations | Within-layer and across-layer permutation functions | 6 | 3(within)+3(across) |
| M1-3 | Training pipeline | Train Transformer + GNN with h-e1 components | 7 | 2(transformer)+2(gnn)+2(checkpoint)+1(reuse) |
| M1-4 | Perturbation evaluation | Evaluate both models on 3 perturbation types | 9 | 3(unperturbed)+3(within)+3(across) |
| M1-5 | Differential analysis | Compute symmetry differential + gate check | 5 | 3(compute)+2(gate) |
| M1-6 | Visualization | Differential comparison + degradation heatmap | 8 | 4(bar_chart)+4(heatmap) |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M1-1, M1-4], Low(4-8): [M1-2, M1-3, M1-5, M1-6]

**Total Complexity:** 46 (6 tasks)

---

*Architecture Status: FINAL*  
*Next Phase: Phase 4 - Implementation (Coder-Validator loop)*
