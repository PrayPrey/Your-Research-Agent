# Architecture: H-E1 Benchmark Fingerprint Detection

**Type:** EXISTENCE (PoC) | **Epic Tasks:** 5

Applied: standard feature-extraction + linear-probe pattern (frozen backbone, sklearn probe)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch

## File Structure (Minimal - EXISTENCE)

```
src/
├── data.py          # dataset loaders + transforms (6 datasets)
├── model.py          # ResNet-50 wrapper w/ feature hook
├── train.py           # finetune loop + feature extraction + probe + stats
└── config.py           # single fixed config (all hyperparams)
```

## Modules

### config.py

```python
@dataclass
class Config:
    benchmarks: list[str]           # 5 fine-tune datasets
    probe_dataset: str = "nabirds"
    seeds: list[int] = (0, 1, 2)
    epochs: int = 30
    lr: float = 0.01
    batch_size: int = 32
    weight_decay: float = 1e-4
    momentum: float = 0.9
    feature_dim: int = 2048
    data_root: str = "./data"
    ckpt_dir: str = "./models/finetuned"
    feature_dir: str = "./features"
    results_path: str = "./results/h_e1_results.json"
```

### data.py (`src/data.py`)

**Dependencies**: config.py

```python
def get_transforms(train: bool) -> transforms.Compose: ...
def build_dataset(name: str, root: str, train: bool) -> Dataset: ...
    # name in {cub, dogs, flowers, cars, aircraft, nabirds}
def build_dataloader(name: str, root: str, train: bool, batch_size: int) -> DataLoader: ...
```

### model.py (`src/model.py`)

**Dependencies**: torchvision

```python
class FeatureResNet50(nn.Module):
    def __init__(self, num_classes: int, pretrained: bool = True): ...
    def forward(self, x: Tensor) -> Tensor: ...          # classification logits
    def extract_features(self, x: Tensor) -> Tensor: ... # 2048-d avgpool output
```

### train.py (`src/train.py`)

**Dependencies**: data.py, model.py, config.py, sklearn

```python
def finetune_one(benchmark: str, seed: int, cfg: Config) -> str: ...        # returns ckpt path
def run_all_finetuning(cfg: Config) -> list[str]: ...                       # 15 models

def extract_all_features(ckpt_paths: list[str], cfg: Config) -> tuple[np.ndarray, np.ndarray]: ...
    # returns (features [15*24000, 2048], labels [benchmark_idx per model])

def train_linear_probe(features: np.ndarray, labels: np.ndarray, cfg: Config) -> dict: ...
    # sklearn LogisticRegression, 70/15/15 split by model, 3-fold CV, bootstrap CI, t-test, Cohen's d

def run_baselines(cfg: Config) -> dict: ...
    # random-init features, shuffled labels, same-domain probe

def main(cfg: Config) -> None: ...   # orchestrates full pipeline, writes results_path
```

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; no base_hypothesis folder provided

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data pipeline | Loaders+transforms for 6 datasets (torchvision + custom CUB/Dogs/Cars) | 10 | 3+2+2+3 |
| A-2 | Model wrapper | ResNet-50 w/ classifier head + feature-extraction hook | 6 | 2+1+2+1 |
| A-3 | Finetuning loop | Train 15 models (5 benchmarks x 3 seeds), SGD+cosine, checkpoint save | 12 | 3+3+3+3 |
| A-4 | Feature extraction | Run 15 models over NABirds test set, batch to disk, label by benchmark | 9 | 2+2+2+3 |
| A-5 | Linear probe + stats | LogisticRegression, 3-fold CV, bootstrap CI, t-test, Cohen's d, confusion matrix | 11 | 3+2+4+2 |
| A-6 | Baselines | Random-init features, shuffled labels, same-domain probe | 7 | 2+2+2+1 |
| A-7 | Results/report | Aggregate JSON output, confusion matrix figure, validation report | 5 | 1+1+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-3, A-4, A-5], Low(4-8): [A-2, A-6, A-7]
