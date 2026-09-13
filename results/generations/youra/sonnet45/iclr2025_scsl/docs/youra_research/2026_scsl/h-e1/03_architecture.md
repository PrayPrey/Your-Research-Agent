# Architecture Specification: h-e1 — Clusterability Diagnostic

**Date:** 2026-03-19
**Author:** Phase 3 Architecture Agent
**Hypothesis:** h-e1 (EXISTENCE)
**Applied Patterns:** PyTorch DL experiment architecture, SSL training pattern

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase
**Status:** Archived implementation found
**Analyzed Path:** `docs/youra_research/20260318_scsl/_archive/20260319T212428_reflection_recovery/h-e1/src/`
**Findings:** Previous h-e1 implementation exists with WaterbirdsDataset infrastructure. Reusable data loader pattern confirmed.

---

## Project Context

**Hypothesis Type:** EXISTENCE (PoC)
**Gate:** MUST_WORK (AMI ≈0 → FAIL)
**Epic Range:** 4-5 tasks (minimal PoC)
**Validation:** Standard SimCLR creates separable spurious clusters (AMI ≥0.4) predicting fairness intervention efficacy (≥2pp WGA gain)

---

## File Structure

```
h-e1/
├── code/
│   ├── data/
│   │   ├── __init__.py
│   │   └── dataset.py           # WaterbirdsDataset
│   ├── models/
│   │   ├── __init__.py
│   │   ├── simclr.py            # SimCLR encoder + projection
│   │   └── linear_probe.py      # Linear classifier
│   ├── training/
│   │   ├── __init__.py
│   │   ├── ssl_trainer.py       # SimCLR training loop
│   │   └── probe_trainer.py     # Linear probe + cluster retraining
│   ├── evaluation/
│   │   ├── __init__.py
│   │   └── metrics.py           # AMI, WGA, ΔWGA, AUROC
│   ├── config.py                # Single config (no grid)
│   └── run_experiment.py        # Main orchestration
├── checkpoints/                 # Model checkpoints
├── results/                     # Metrics, plots
└── logs/                        # Training logs
```

---

## Module Interfaces

### 1. DataModule (`code/data/dataset.py`)

**Dependencies:** None (PyTorch, torchvision)

```python
class WaterbirdsDataset(Dataset):
    def __init__(self, root_dir: str, split: str, transform=None): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> Tuple[Tensor, int, int]: ...

def get_dataloaders(root_dir: str, batch_size: int, num_workers: int) -> Dict[str, DataLoader]: ...
def get_ssl_transforms() -> transforms.Compose: ...
def get_eval_transforms() -> transforms.Compose: ...
```

---

### 2. SimCLR Model (`code/models/simclr.py`)

**Dependencies:** DataModule

```python
class SimCLR(nn.Module):
    def __init__(self, encoder_name: str = 'resnet50', projection_dim: int = 128): ...
    def forward(self, x: Tensor) -> Tuple[Tensor, Tensor]: ...
    def get_encoder(self) -> nn.Module: ...

def nt_xent_loss(z_i: Tensor, z_j: Tensor, temperature: float = 0.5) -> Tensor: ...
```

---

### 3. Linear Probe (`code/models/linear_probe.py`)

**Dependencies:** SimCLR

```python
class LinearProbe(nn.Module):
    def __init__(self, input_dim: int = 2048, num_classes: int = 2): ...
    def forward(self, x: Tensor) -> Tensor: ...

def cluster_balanced_loss(logits: Tensor, targets: Tensor, cluster_ids: Tensor, cluster_weights: Tensor) -> Tensor: ...
```

---

### 4. SSL Trainer (`code/training/ssl_trainer.py`)

**Dependencies:** SimCLR, DataModule

```python
class SimCLRTrainer:
    def __init__(self, model: SimCLR, dataloaders: Dict, config: Dict, device: str): ...
    def train_epoch(self) -> float: ...
    def train(self, num_epochs: int) -> None: ...
    def save_checkpoint(self, epoch: int, path: str) -> None: ...
```

---

### 5. Probe Trainer (`code/training/probe_trainer.py`)

**Dependencies:** LinearProbe, DataModule

```python
class ProbeTrainer:
    def __init__(self, linear: LinearProbe, embeddings: Tensor, labels: Tensor, config: Dict, device: str): ...
    def train(self, num_epochs: int, cluster_labels: Optional[Tensor] = None) -> None: ...
    def evaluate(self, test_embeddings: Tensor, test_labels: Tensor, test_groups: Tensor) -> Dict[str, float]: ...

def extract_embeddings(encoder: nn.Module, dataloader: DataLoader, device: str) -> Tuple[Tensor, Tensor, Tensor]: ...
def grid_search_linear(embeddings: Tensor, labels: Tensor, groups: Tensor, config: Dict, device: str) -> Tuple[Dict, LinearProbe]: ...
```

---

### 6. Metrics Module (`code/evaluation/metrics.py`)

**Dependencies:** ProbeTrainer

```python
def compute_ami(embeddings: np.ndarray, groups: np.ndarray, n_clusters: int = 4) -> Tuple[float, np.ndarray]: ...
def compute_wga(preds: np.ndarray, labels: np.ndarray, groups: np.ndarray) -> float: ...
def compute_group_accuracies(preds: np.ndarray, labels: np.ndarray, groups: np.ndarray) -> Dict[int, float]: ...
def compute_linear_auroc(embeddings: np.ndarray, groups: np.ndarray) -> float: ...
def compute_diagnostic_auroc(ami_values: List[float], delta_wga_values: List[float], threshold: float = 1.0) -> float: ...
```

---

### 7. Config (`code/config.py`)

**Dependencies:** None

```python
SSL_CONFIG: Dict = {
    'encoder': 'resnet50',
    'projection_dim': 128,
    'temperature': 0.5,
    'batch_size': 256,
    'lr': 0.3,
    'weight_decay': 1e-6,
    'epochs': 200,
}

LINEAR_CONFIG: Dict = {
    'lr_grid': [0.01, 0.001, 0.0001],
    'wd_grid': [1e-4, 1e-5, 1e-6],
    'seeds': [0, 1, 2, 3, 4],
    'epochs': 20,
    'batch_size': 32,
}

DATA_CONFIG: Dict = {
    'root_dir': '.data_cache/datasets/waterbirds/',
    'num_workers': 4,
}
```

---

### 8. Main Orchestration (`code/run_experiment.py`)

**Dependencies:** All modules

```python
def main():
    # Phase 1: SSL pretraining
    # Phase 2: Embedding extraction + AMI
    # Phase 3: Linear ERM baseline
    # Phase 4: Cluster-balanced retraining
    # Phase 5: Stratified analysis
    # Phase 6: Report generation
    ...

def download_waterbirds(cache_dir: str) -> None: ...
def save_results(metrics: Dict, output_path: str) -> None: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Infrastructure | Download Waterbirds, implement WaterbirdsDataset, verify splits | 8 | Module(2) + Deps(1) + Algo(2) + Integ(3) |
| A-2 | SimCLR Implementation | ResNet-50 encoder, projection head, NT-Xent loss | 14 | Module(4) + Deps(2) + Algo(4) + Integ(4) |
| A-3 | SSL Training | Train SimCLR 200 epochs, save checkpoint, freeze encoder | 10 | Module(2) + Deps(2) + Algo(3) + Integ(3) |
| A-4 | Clustering & Linear Probe | Extract embeddings, k-means AMI, linear ERM grid search | 12 | Module(3) + Deps(2) + Algo(4) + Integ(3) |
| A-5 | Cluster Retraining & Validation | Cluster-balanced loss, ΔWGA, stratified analysis, report | 11 | Module(3) + Deps(2) + Algo(3) + Integ(3) |

**Distribution:** VeryHigh(18-20): [], High(14-17): [A-2], Medium(9-13): [A-3, A-4, A-5], Low(4-8): [A-1]

---

## Implementation Notes

### Critical Decisions

**SimCLR Training:** Train from scratch (pretrained=False) for fair SSL evaluation.

**K-means:** sklearn.cluster.KMeans with n_clusters=4, random_state=42.

**Grid Search:** 3 LR × 3 WD × 5 seeds = 45 configs for baseline robustness.

**Cluster Weighting:** Inverse frequency weighting (1 / cluster_count).

### Risk Mitigation

**AMI ≈0 Early Detection:** Compute AMI at epochs 50, 100, 150, 200. If all <0.2, STOP early.

**Training Stability:** Gradient clipping (max_norm=1.0), checkpoint every 50 epochs.

**Compute:** Mixed precision (torch.cuda.amp) if needed for speed.

---

## Success Criteria

**Primary (Gate):**
- High-AMI (≥0.4): mean ΔWGA ≥2pp, 95% CI excludes zero
- Low-AMI (<0.3): mean ΔWGA <0.5pp

**Secondary:**
- AMI-Linear dissociation: r < 0.9
- AMI diagnostic AUROC: >0.80

**Failure:** AMI ≈0 → PIVOT to density-based clustering (DBSCAN/HDBSCAN)

---

## Validation Checklist

- [x] No ASCII diagrams
- [x] KB search pattern applied (SSL training)
- [x] Module interfaces only (no implementations)
- [x] 4-5 Epic tasks (EXISTENCE range)
- [x] Complexity scores with breakdown
- [x] Codebase Analysis section included
- [x] Total length <500 lines

---

**END OF ARCHITECTURE SPECIFICATION**
