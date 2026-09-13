# Architecture: H-E1 — Spurious Direction Recovery via K-Means Clustering

**Hypothesis**: H-E1 (EXISTENCE / PoC)
**Tier**: LIGHT
**Applied**: Standard DL Experiment Pipeline

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing codebase to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. DFR repo (PolinaKirichenko/deep_feature_reweighting) patterns used as reference for data loading and training — not as imported code.

---

## File Organization

```
h-e1/code/
├── data/
│   ├── __init__.py
│   └── datasets.py          # WaterBirdsDataset, CelebADataset, GroupDataset
├── models/
│   ├── __init__.py
│   └── resnet.py            # ERM ResNet-50 wrapper + feature extractor
├── configs/
│   ├── waterbirds.yaml      # Dataset-specific hyperparameters
│   └── celeba.yaml
├── train.py                 # ERM training with epoch-5 checkpoint saving
├── extract.py               # Penultimate-layer embedding extraction
├── cluster.py               # K-means probe + AMI/purity metrics
├── visualize.py             # t-SNE, bar charts, AMI-vs-epoch figures
├── evaluate.py              # Gate check + results report
└── run_experiment.sh        # End-to-end orchestration script
```

---

## Modules

### GroupDataset (`data/datasets.py`)

**Dependencies**: torch, torchvision, numpy, pandas, PIL

```python
class GroupDataset(torch.utils.data.Dataset):
    def __init__(self, data_dir: str, split: str, transform=None): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> tuple[Tensor, int, int]: ...
    # Returns: (image, class_label, group_label)

class WaterBirdsDataset(GroupDataset):
    def __init__(self, data_dir: str, split: str, augment: bool = False): ...
    # Reads metadata.csv; groups: 0=landbird-land, 1=landbird-water,
    #                                2=waterbird-land, 3=waterbird-water

class CelebADataset(GroupDataset):
    def __init__(self, data_dir: str, split: str, augment: bool = False): ...
    # Reads metadata.csv; groups: 0=non-blond-female, 1=blond-female,
    #                                2=non-blond-male, 3=blond-male

def get_dataloader(dataset: GroupDataset, batch_size: int,
                   shuffle: bool = False, num_workers: int = 4
                   ) -> torch.utils.data.DataLoader: ...

def get_transforms(augment: bool, dataset_name: str) -> transforms.Compose: ...
```

---

### ERMModel (`models/resnet.py`)

**Dependencies**: torch, torchvision

```python
class ERMModel(nn.Module):
    def __init__(self, num_classes: int = 2, pretrained: bool = True): ...
    def forward(self, x: Tensor) -> Tensor: ...           # logits (B, num_classes)
    def get_feature_extractor(self) -> nn.Sequential: ... # drops model.fc
    # feature_extractor output: (B, 2048) after avg_pool squeeze

def load_checkpoint(model: ERMModel, ckpt_path: str) -> ERMModel: ...
def save_checkpoint(model: ERMModel, epoch: int, output_dir: str) -> str: ...
```

---

### ERM Trainer (`train.py`)

**Dependencies**: ERMModel, GroupDataset, configs/

```python
def train_one_epoch(model: ERMModel, loader: DataLoader,
                    optimizer: Optimizer, criterion: nn.Module,
                    device: torch.device) -> dict[str, float]: ...
    # Returns: {"loss": float, "acc": float}

def train(config_path: str, dataset_name: str, output_dir: str,
          stop_after_epoch: int = 5) -> str: ...
    # Returns path to epoch-5 checkpoint
    # Saves checkpoint at each epoch; early-stops after stop_after_epoch
    # Prints per-epoch: loss, accuracy

def main(): ...  # CLI entry: --config, --dataset, --output_dir, --stop_epoch
```

---

### Embedding Extractor (`extract.py`)

**Dependencies**: ERMModel, GroupDataset

```python
def extract_embeddings(model: ERMModel, loader: DataLoader,
                       device: torch.device
                       ) -> tuple[np.ndarray, np.ndarray, np.ndarray]: ...
    # Returns: (embeddings (N,2048), class_labels (N,), group_labels (N,))
    # Asserts embeddings.shape[1] == 2048

def run_extraction(ckpt_path: str, dataset_name: str, data_dir: str,
                   output_dir: str, batch_size: int = 256) -> dict[str, str]: ...
    # Saves: embeddings.npy, labels.npy, group_ids.npy
    # Returns dict of saved file paths

def main(): ...  # CLI: --ckpt, --dataset, --data_dir, --output_dir
```

---

### K-Means Probe (`cluster.py`)

**Dependencies**: numpy, sklearn

```python
def run_kmeans(embeddings: np.ndarray, k: int = 2,
               n_init: int = 10, seed: int = 42) -> np.ndarray: ...
    # Returns cluster_assignments (N,)

def compute_ami(group_ids: np.ndarray,
                cluster_assignments: np.ndarray) -> float: ...

def compute_worst_cluster_purity(group_ids: np.ndarray,
                                  cluster_assignments: np.ndarray,
                                  k: int = 2) -> float: ...

def compute_random_baseline(group_ids: np.ndarray,
                             k: int = 2, seed: int = 0
                             ) -> tuple[float, float]: ...
    # Returns: (ami_random, purity_random)

def verify_mechanism(embeddings: np.ndarray,
                     cluster_assignments: np.ndarray,
                     group_ids: np.ndarray,
                     k: int = 2) -> tuple[bool, dict]: ...
    # Checks: shape==2048, cluster_size>10, ami_above_chance

def probe(embeddings_path: str, group_ids_path: str,
          k: int = 2) -> dict[str, float]: ...
    # Returns: {"ami": float, "worst_purity": float, "ami_random": float,
    #           "purity_random": float, "mechanism_ok": bool}

def main(): ...  # CLI: --embeddings, --group_ids, --k, --output
```

---

### Visualizer (`visualize.py`)

**Dependencies**: numpy, matplotlib, seaborn, sklearn (TSNE)

```python
def plot_gate_metrics(results: dict, output_path: str) -> None: ...
    # Bar chart: AMI + worst_purity per dataset vs threshold lines

def plot_tsne(embeddings: np.ndarray, labels: np.ndarray,
              color_by: str, title: str, output_path: str) -> None: ...
    # color_by: "class" | "group" | "cluster"

def plot_cluster_composition(group_ids: np.ndarray,
                              cluster_assignments: np.ndarray,
                              dataset_name: str, output_path: str) -> None: ...
    # Stacked bar chart per cluster

def plot_ami_vs_epoch(epoch_ami_dict: dict[int, float],
                      dataset_name: str, output_path: str) -> None: ...
    # Epochs 1, 3, 5, 7, 10 on x-axis

def generate_all_figures(results: dict, embeddings_dir: str,
                         figures_dir: str) -> None: ...
```

---

### Gate Evaluator (`evaluate.py`)

**Dependencies**: cluster.py, visualize.py, yaml, json

```python
def check_gate(results: dict) -> tuple[bool, dict]: ...
    # Returns (gate_pass: bool, per_dataset_pass: dict)
    # gate_pass = True iff BOTH datasets pass AMI>=0.5 AND purity>=0.75

def format_results_table(results: dict) -> str: ...
    # ASCII table: dataset | AMI | purity | AMI_pass | purity_pass

def save_results(results: dict, gate_pass: bool,
                 output_dir: str) -> None: ...
    # Saves results.yaml and results.json

def main(): ...
    # CLI: --wb_probe, --celeba_probe, --output_dir, --figures_dir
    # Runs visualize.generate_all_figures, prints table, saves results
```

---

## Epic Tasks

| ID | Task | Description | Files Affected | Complexity | Breakdown |
|----|------|-------------|----------------|------------|-----------|
| A-1 | Data Pipeline | WaterBirdsDataset + CelebADataset with group labels, transforms, dataloader utils | `data/datasets.py`, `configs/*.yaml` | 10 | Size:3 + Deps:2 + Algo:2 + Int:3 |
| A-2 | Model + ERM Training | ERMModel wrapper, SGD training loop, epoch-5 checkpoint save/load, early stop | `models/resnet.py`, `train.py` | 12 | Size:3 + Deps:3 + Algo:2 + Int:4 |
| A-3 | Embedding Extraction | Penultimate-layer (2048-dim) extraction, batch inference, .npy save, shape assert | `extract.py` | 9 | Size:2 + Deps:3 + Algo:2 + Int:2 |
| A-4 | K-Means Clustering Probe | k-means(k=2), AMI, worst-cluster purity, random baseline, mechanism verification | `cluster.py` | 11 | Size:3 + Deps:2 + Algo:4 + Int:2 |
| A-5 | Visualization | t-SNE (class/group/cluster), gate bar chart, cluster composition, AMI-vs-epoch curve | `visualize.py` | 10 | Size:3 + Deps:2 + Algo:3 + Int:2 |
| A-6 | Gate Evaluation + Results | Gate check (AMI>=0.5, purity>=0.75), results YAML/JSON, summary table, orchestration | `evaluate.py`, `run_experiment.sh` | 9 | Size:2 + Deps:3 + Algo:2 + Int:2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-2, A-3, A-4, A-5, A-6], Low(4-8): []

---

## Configuration Schema (`configs/waterbirds.yaml`)

```yaml
dataset:
  name: waterbirds
  data_dir: ./data/waterbirds
  num_classes: 2
  num_groups: 4

training:
  seed: 1
  epochs: 100
  stop_after_epoch: 5
  batch_size: 32
  lr: 1.0e-3
  weight_decay: 1.0e-3
  momentum: 0.9
  augment: true

clustering:
  k: 2
  n_init: 10
  seed: 42
  ami_threshold: 0.5
  purity_threshold: 0.75

output:
  checkpoint_dir: ./checkpoints/waterbirds
  embeddings_dir: ./embeddings/waterbirds
  figures_dir: ./figures
  results_dir: ./results
```

`configs/celeba.yaml` mirrors the above with: `batch_size: 128`, `weight_decay: 1.0e-4`, `stop_after_epoch: 5`, `epochs: 50`.

---

## Module Dependency Graph

- `train.py` → `models/resnet.py`, `data/datasets.py`, `configs/`
- `extract.py` → `models/resnet.py`, `data/datasets.py`
- `cluster.py` → numpy, sklearn (no internal deps)
- `visualize.py` → numpy, matplotlib, sklearn.manifold.TSNE
- `evaluate.py` → `cluster.py`, `visualize.py`
- `run_experiment.sh` → invokes `train.py`, `extract.py`, `cluster.py`, `evaluate.py` sequentially

---

## Key Interface Contracts

- `GroupDataset.__getitem__` MUST return `(image: Tensor, y: int, g: int)` — all downstream modules depend on this triple
- `extract_embeddings` MUST assert `embeddings.shape[1] == 2048` before saving
- `probe()` in `cluster.py` is the single integration point consumed by `evaluate.py`
- Embeddings saved as `.npy` float32; reusable without re-training
- All random seeds fixed: training seed=1, k-means seed=42
