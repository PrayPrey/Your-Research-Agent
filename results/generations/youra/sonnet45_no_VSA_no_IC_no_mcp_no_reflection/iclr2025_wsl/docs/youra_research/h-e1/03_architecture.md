# Architecture Specification: h-e1

**Date:** 2026-08-28  
**Author:** Phase 3 Architecture Agent  
**Hypothesis:** Layer-wise weight tokenization preserves structural signal for backbone comparison  
**Type:** EXISTENCE (PoC)  
**MCP Status:** Unavailable (ablation mode)

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation from scratch  
**Analyzed Path:** N/A  
**Findings:** No existing code to analyze

---

## System Overview

Validate that layer-wise weight tokenization preserves sufficient signal for architecture family classification on timm model zoo (100-200 pre-trained vision models). Success: >60% test accuracy, beating random (20-25%) and weight statistics baseline (30-40%).

**Data Flow:**
```
timm models → extract weights → tokenize layers → [transformer | baseline] → classify → evaluate
```

---

## Module Structure

### 1. DataLoader (`src/data_loader.py`)

**Dependencies:** timm, torch

```python
class TimmModelZooLoader:
    def __init__(self, families: list[str], num_models: int, cache_path: str): ...
    def load_models(self) -> list[tuple[str, nn.Module]]: ...
    def extract_weights(self, model: nn.Module) -> list[Tensor]: ...
    def split_data(self, test_size: float, val_size: float, seed: int) -> tuple: ...

class WeightTokenizer:
    def __init__(self, max_layer_size: int, normalize: bool): ...
    def tokenize(self, layer_weights: list[Tensor]) -> Tensor: ...
    def add_position_encoding(self, tokens: Tensor) -> Tensor: ...
```

**Interfaces:**
- `load_models() -> [(name, model), ...]`: Download and cache timm models
- `extract_weights(model) -> [layer_tensor, ...]`: Extract layer-wise weights
- `tokenize(weights) -> [batch, num_layers, layer_size]`: Flatten + pad layers
- `split_data() -> (train, val, test)`: Stratified split by architecture family

---

### 2. Models (`src/model.py`)

**Dependencies:** torch.nn, torch.nn.TransformerEncoder

```python
class WeightTransformer(nn.Module):
    def __init__(self, d_model: int, nhead: int, num_layers: int, 
                 max_layer_size: int, num_classes: int, dropout: float): ...
    def forward(self, layer_weights: Tensor) -> Tensor: ...

class BaselineMLP(nn.Module):
    def __init__(self, num_features: int, hidden_dim: int, num_classes: int): ...
    def forward(self, layer_stats: Tensor) -> Tensor: ...

def extract_layer_statistics(weights: list[Tensor]) -> Tensor: ...
```

**Interfaces:**
- `WeightTransformer.forward([batch, num_layers, layer_size]) -> [batch, num_classes]`
- `BaselineMLP.forward([batch, num_features]) -> [batch, num_classes]`
- `extract_layer_statistics(weights) -> [batch, 3*num_layers]`: mean/std/norm per layer

**Architecture Details:**
- Transformer: token_projection → pos_encoding → TransformerEncoder(6 layers, 8 heads) → global_pooling → MLP
- Baseline: layer_stats → MLP(256 → 128 → num_classes)

---

### 3. Training (`src/train.py`)

**Dependencies:** torch.optim, torch.nn.functional

```python
class Trainer:
    def __init__(self, model: nn.Module, optimizer: Optimizer, 
                 scheduler: LRScheduler, criterion: nn.Module, device: str): ...
    def train_epoch(self, dataloader: DataLoader) -> dict[str, float]: ...
    def validate(self, dataloader: DataLoader) -> dict[str, float]: ...
    def fit(self, train_loader: DataLoader, val_loader: DataLoader, 
            epochs: int, patience: int, checkpoint_path: str) -> dict: ...

class EarlyStopping:
    def __init__(self, patience: int, min_delta: float): ...
    def __call__(self, val_loss: float) -> bool: ...
```

**Interfaces:**
- `train_epoch(loader) -> {loss, accuracy}`: Single training epoch
- `validate(loader) -> {loss, accuracy}`: Validation pass
- `fit() -> {train_history, val_history, best_epoch}`: Full training loop with early stopping

---

### 4. Evaluation (`src/evaluate.py`)

**Dependencies:** sklearn.metrics, matplotlib

```python
def evaluate_model(model: nn.Module, test_loader: DataLoader, 
                   device: str) -> dict[str, float]: ...

def generate_confusion_matrix(y_true: ndarray, y_pred: ndarray, 
                              class_names: list[str], save_path: str): ...

def plot_training_curves(train_history: dict, val_history: dict, 
                         save_path: str): ...

def plot_gate_metrics(random_acc: float, baseline_acc: float, 
                      proposed_acc: float, threshold: float, save_path: str): ...

def visualize_attention(model: WeightTransformer, sample_input: Tensor, 
                        save_path: str): ...
```

**Interfaces:**
- `evaluate_model() -> {accuracy, precision, recall, f1}`: Test set metrics
- `generate_confusion_matrix()`: Per-family accuracy visualization
- `plot_training_curves()`: Train/val loss and accuracy over epochs
- `plot_gate_metrics()`: Bar chart comparing baselines vs proposed
- `visualize_attention()`: Transformer attention heatmap over layers

---

### 5. Configuration (`src/config.py`)

**Dependencies:** dataclasses, yaml

```python
@dataclass
class DataConfig:
    source: str
    families: list[str]
    num_models: int
    train_split: float
    val_split: float
    test_split: float
    cache_path: str
    max_layer_size: int

@dataclass
class ModelConfig:
    type: str
    d_model: int
    nhead: int
    num_layers: int
    dim_feedforward: int
    dropout: float
    num_classes: int

@dataclass
class TrainingConfig:
    optimizer: str
    lr: float
    weight_decay: float
    batch_size: int
    epochs: int
    early_stopping_patience: int
    gradient_clip_max_norm: float
    scheduler_T_max: int
    scheduler_eta_min: float

@dataclass
class ExperimentConfig:
    data: DataConfig
    model: ModelConfig
    training: TrainingConfig
    random_seed: int
    device: str
    output_dir: str

def load_config(path: str) -> ExperimentConfig: ...
def save_config(config: ExperimentConfig, path: str): ...
```

---

### 6. Main Entry Point (`src/main.py`)

**Dependencies:** all modules

```python
def run_baseline(config: ExperimentConfig, train_data, val_data, test_data) -> float: ...
def run_proposed(config: ExperimentConfig, train_data, val_data, test_data) -> float: ...
def main(config_path: str): ...
```

**Interfaces:**
- `run_baseline() -> test_accuracy`: Train and evaluate baseline MLP
- `run_proposed() -> test_accuracy`: Train and evaluate weight transformer
- `main()`: End-to-end pipeline (load data → train both models → compare → generate figures)

---

## File Structure

```
h-e1/
├── src/
│   ├── data_loader.py       # TimmModelZooLoader, WeightTokenizer
│   ├── model.py             # WeightTransformer, BaselineMLP
│   ├── train.py             # Trainer, EarlyStopping
│   ├── evaluate.py          # Metrics, confusion matrix, plots
│   ├── config.py            # Config dataclasses, YAML loader
│   └── main.py              # Entry point
├── config.yaml              # Hyperparameters
├── data/                    # Cached model weights
└── figures/                 # Generated plots
```

---

## Dependency Graph

```
External:
- torch (nn, optim, TransformerEncoder)
- timm (model zoo)
- sklearn (metrics, train_test_split)
- matplotlib (plots)
- pyyaml (config)

Internal:
data_loader ← model
data_loader ← train
model ← train
model ← evaluate
train ← main
evaluate ← main
config ← main
```

---

## Implementation Notes

### PoC Simplifications

**Minimal structure for "does it work?" validation:**
- Single config file (no hyperparameter search)
- Fixed architecture (no ablation modules)
- Classification only (architecture family, not regression)
- Basic attention visualization (first layer only)

**EXISTENCE architecture omits:**
- Hyperparameter sweep logic
- Advanced tokenization strategies (just flatten + pad)
- Multiple backbone variants (just transformer + baseline)
- Per-layer ablation studies

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

model:
  type: transformer
  d_model: 256
  nhead: 8
  num_layers: 6
  dim_feedforward: 1024
  dropout: 0.1
  num_classes: 4

training:
  optimizer: AdamW
  lr: 1e-4
  weight_decay: 1e-5
  batch_size: 32
  epochs: 50
  early_stopping_patience: 10
  gradient_clip_max_norm: 1.0
  scheduler_T_max: 50
  scheduler_eta_min: 1e-6

random_seed: 42
device: cuda
output_dir: ./h-e1/
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1-1 | Data pipeline | Load timm models, tokenize weights, stratified split | 8 | 2(load)+2(tokenize)+2(split)+2(cache) |
| E1-2 | Baseline model | Layer statistics extraction + MLP classifier | 5 | 2(stats)+2(MLP)+1(train) |
| E1-3 | Transformer model | Token projection + TransformerEncoder + pooling + head | 9 | 3(projection)+3(transformer)+2(head)+1(pooling) |
| E1-4 | Training loop | AdamW + CosineAnnealingLR + early stopping + logging | 7 | 2(optimizer)+2(scheduler)+2(early_stop)+1(log) |
| E1-5 | Evaluation | Test metrics + confusion matrix + training curves + gate plot | 6 | 2(metrics)+2(confusion)+1(curves)+1(gate) |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [E1-3], Low(4-8): [E1-1, E1-2, E1-4, E1-5]

**Total Complexity:** 35 (5 tasks)

---

*Architecture Status: FINAL*  
*Next Phase: Phase 4 - Implementation (Coder-Validator loop)*
