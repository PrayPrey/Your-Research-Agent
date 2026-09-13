# Architecture: h-e1 (EXISTENCE PoC)

**Hypothesis**: Locality inductive bias difference between DWS and NFT architectures
**Type**: EXISTENCE — minimal architecture, 3 models, mechanism verification

Applied: weight-space-classification-pipeline (MLP baseline + equivariant/attention comparison models)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No base hypothesis or existing `src/`/`code/` directory present.

---

## File Structure (Minimal — EXISTENCE)

```
h-e1/code/
  data.py         # MNIST INR loading + normalization + DataLoaders
  models.py       # FlattenedMLP, DWSModel, NFTModel
  metrics.py       # attention_entropy, layer_activation_variance, verify_mechanism
  train.py         # training loop (shared across 3 models) + eval
  visualize.py     # 4 required figures
  config.py        # single fixed config (dataclass)
  main.py          # entrypoint: train all 3 models, run eval, generate figures
```

---

## Module Definitions

### config.py

```python
@dataclass
class Config:
    data_dir: str = "data/mnist_inrs"
    batch_size: int = 64
    lr: float = 1e-3
    weight_decay: float = 1e-4
    epochs: int = 50
    seed: int = 42
    d_model: int = 128
    nhead: int = 4
    num_layers: int = 2
    device: str = "cuda"
```

### data.py

**Dependencies**: config.py

```python
class MNISTINRDataset(Dataset):
    def __init__(self, path: str): ...
    def __getitem__(self, idx: int) -> tuple[list[Tensor], int]: ...  # (weight_list_per_layer, label)
    def __len__(self) -> int: ...

def normalize_weights(weight_list: list[Tensor]) -> list[Tensor]: ...  # zero mean, unit var per layer

def get_dataloaders(cfg: Config) -> tuple[DataLoader, DataLoader]: ...

def download_mnist_inrs(data_dir: str) -> None: ...  # fetch from DWSNets Dropbox if missing
```

### models.py

**Dependencies**: config.py

```python
class FlattenedMLP(nn.Module):
    def __init__(self, input_dim: int, num_classes: int = 10): ...
    def forward(self, weight_list: list[Tensor]) -> Tensor: ...

class DWSLayer(nn.Module):
    def __init__(self, weight_shapes: list[tuple[int,int]], out_channels: int): ...
    def forward(self, weight_list: list[Tensor]) -> tuple[Tensor, list[Tensor]]: ...  # (agg, per_layer_feats)

class DWSModel(nn.Module):
    def __init__(self, weight_shapes: list[tuple[int,int]], hidden: int = 128, num_classes: int = 10): ...
    def forward(self, weight_list: list[Tensor]) -> Tensor: ...
    def get_layer_activations(self, weight_list: list[Tensor]) -> list[Tensor]: ...

class WeightTokenizer(nn.Module):
    def __init__(self, weight_shapes: list[tuple[int,int]], d_model: int): ...
    def forward(self, weight_list: list[Tensor]) -> Tensor: ...  # (B, num_tokens, d_model)

class NFTModel(nn.Module):
    def __init__(self, weight_shapes: list[tuple[int,int]], d_model: int = 128, nhead: int = 4, num_layers: int = 2, num_classes: int = 10): ...
    def forward(self, weight_list: list[Tensor]) -> Tensor: ...
    def get_attention_weights(self, weight_list: list[Tensor]) -> Tensor: ...  # (B, heads, seq, seq)
```

### metrics.py

**Dependencies**: none (pure functions on tensors)

```python
def attention_entropy(attn_weights: Tensor) -> float: ...
def layer_activation_variance(layer_outputs: list[Tensor]) -> float: ...
def verify_mechanism(model: nn.Module, sample_input: list[Tensor], model_type: str) -> bool: ...
```

### train.py

**Dependencies**: models.py, data.py, metrics.py, config.py

```python
def train_model(model: nn.Module, train_loader: DataLoader, cfg: Config) -> nn.Module: ...
def evaluate(model: nn.Module, test_loader: DataLoader) -> dict:  # {"accuracy": float}
    ...
def run_experiment(cfg: Config) -> dict: ...  # trains MLP/DWS/NFT, returns all results + mechanism checks
```

### visualize.py

**Dependencies**: metrics.py

```python
def plot_accuracy_comparison(results: dict, out_path: str) -> None: ...
def plot_attention_heatmap(attn_weights: Tensor, out_path: str) -> None: ...
def plot_layer_activation_profile(layer_acts: list[Tensor], out_path: str) -> None: ...
def plot_tsne_representations(dws_reprs: Tensor, nft_reprs: Tensor, labels: Tensor, out_path: str) -> None: ...
```

### main.py

**Dependencies**: all modules

```python
def main() -> None: ...  # load cfg -> data -> train 3 models -> evaluate -> verify_mechanism -> visualize -> save results.json
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data pipeline | Download + load MNIST INRs, normalize, DataLoaders | 10 | 3+2+3+2 |
| A-2 | FlattenedMLP baseline | Implement baseline model | 4 | 2+1+1+0 |
| A-3 | DWS model | DWSLayer + DWSModel + layer activation hook | 13 | 4+2+4+3 |
| A-4 | NFT model | WeightTokenizer + NFTModel + attention hook | 13 | 4+2+4+3 |
| A-5 | Metrics module | attention_entropy, layer_activation_variance, verify_mechanism | 6 | 2+1+2+1 |
| A-6 | Training loop | Shared train/eval loop for 3 models, AdamW+CosineLR | 8 | 2+3+2+1 |
| A-7 | Mechanism verification run | Run verify_mechanism on trained DWS/NFT, log results | 5 | 1+2+1+1 |
| A-8 | Visualization suite | 4 required figures (accuracy bar, attention heatmap, activation profile, t-SNE) | 9 | 3+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-3, A-4, A-8], Low(4-8): [A-2, A-5, A-6, A-7]

---

## Notes

- Green-field, no external module reuse — all 3 models implemented from scratch per PRD pseudo-code.
- `weight_shapes` (list of (in_c, out_c) per SIREN layer) derived from dataset metadata at load time, passed to DWS/NFT constructors.
- Single fixed config only (no ablation grid) per EXISTENCE scope.
