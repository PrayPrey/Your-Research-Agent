# Architecture Specification: h-m-integrated — 3-Step Mechanism Validation

**Date:** 2026-03-20
**Author:** Phase 3 Architecture Agent
**Hypothesis:** h-m-integrated (MECHANISM)
**Applied Patterns:** PyTorch DL experiment, SSL training with learning-speed resampling

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Patterns found from base code
**Analyzed Path:** `docs/youra_research/20260318_scsl/h-e1/code/`
**Findings:** h-e1 provides WaterbirdsDataset, SimCLR baseline, AMI/WGA metrics, linear probe infrastructure. New implementation adds LA-SSL sampler and mechanism validation components.

---

## Project Context

**Hypothesis Type:** MECHANISM
**Gate:** MUST_WORK (M1+M2 must pass, M3 can fail gracefully)
**Epic Range:** 8 tasks (mechanism with 3 causal steps)
**Validation:** InfoNCE creates clusters (M1: AMI ≥0.4) → Clusterability predicts efficacy (M2: AMI→ΔWGA correlation) → LA-SSL disperses clusters (M3: AMI reduction ≥30%, ΔAUC <0.05)

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| WaterbirdsDataset | `from h_e1.code.data.dataset import WaterbirdsDataset` | `h-e1/code/data/dataset.py` |
| SimCLR | `from h_e1.code.models.simclr import SimCLR, nt_xent_loss` | `h-e1/code/models/simclr.py` |
| LinearProbe | `from h_e1.code.models.linear_probe import LinearProbe` | `h-e1/code/models/linear_probe.py` |
| Metrics | `from h_e1.code.evaluation.metrics import compute_ami, compute_wga` | `h-e1/code/evaluation/metrics.py` |

**Verified from:** `h-e1/code/` (actual implementation)

---

## File Structure

```
h-m-integrated/
├── code/
│   ├── data/
│   │   └── __init__.py           # Re-export h-e1 dataset
│   ├── models/
│   │   ├── __init__.py
│   │   └── lassl_sampler.py      # LA-SSL learning-speed sampler
│   ├── training/
│   │   ├── __init__.py
│   │   └── lassl_trainer.py      # LA-SSL training loop
│   ├── evaluation/
│   │   ├── __init__.py
│   │   └── mechanism_validator.py # M1/M2/M3 gate checks
│   ├── config.py                  # Training configs
│   ├── run_simclr.py              # Standard SimCLR baseline
│   ├── run_lassl.py               # LA-SSL training
│   └── run_validation.py          # Mechanism validation suite
├── checkpoints/                   # SimCLR + LA-SSL checkpoints
├── results/                       # Metrics, AMI evolution, correlations
└── figures/                       # Visualizations
```

---

## Module Interfaces

### 1. LA-SSL Sampler (`code/models/lassl_sampler.py`)

**Dependencies:** None (PyTorch)

```python
class LASSLSampler(torch.utils.data.Sampler):
    def __init__(self, dataset_size: int, alpha: float = 0.5, window_size: int = 10): ...
    def update_losses(self, sample_indices: torch.Tensor, losses: torch.Tensor) -> None: ...
    def compute_sampling_probs(self) -> torch.Tensor: ...
    def __iter__(self) -> Iterator[int]: ...
    def __len__(self) -> int: ...
```

---

### 2. LA-SSL Trainer (`code/training/lassl_trainer.py`)

**Dependencies:** LASSLSampler, h-e1 SimCLR

```python
class LASSLTrainer:
    def __init__(self, model: SimCLR, dataloaders: Dict, sampler: LASSLSampler, config: Dict, device: str): ...
    def train_epoch(self) -> float: ...
    def train(self, num_epochs: int) -> None: ...
    def save_checkpoint(self, epoch: int, path: str) -> None: ...
```

---

### 3. Mechanism Validator (`code/evaluation/mechanism_validator.py`)

**Dependencies:** h-e1 metrics, matplotlib

```python
def validate_m1(embeddings: np.ndarray, groups: np.ndarray, threshold: float = 0.4) -> Dict[str, Any]: ...
def validate_m2(ami_values: List[float], delta_wga_values: List[float], threshold_ami: float = 0.4, threshold_wga: float = 2.0) -> Dict[str, Any]: ...
def validate_m3(ami_simclr: float, ami_lassl: float, auc_simclr: float, auc_lassl: float, reduction_threshold: float = 0.3, auc_threshold: float = 0.05) -> Dict[str, Any]: ...
def compute_ami_evolution(checkpoints: List[str], dataloader: DataLoader, device: str) -> List[Tuple[int, float]]: ...
def generate_mechanism_report(m1_result: Dict, m2_result: Dict, m3_result: Dict, output_path: str) -> None: ...
```

---

### 4. Configuration (`code/config.py`)

**Dependencies:** None

```python
SIMCLR_CONFIG: Dict = {
    'encoder': 'resnet50',
    'projection_dim': 128,
    'temperature': 0.5,
    'batch_size': 128,
    'lr': 0.001,
    'weight_decay': 1e-4,
    'epochs': 100,
    'checkpoint_freq': 10,
    'seeds': [0, 1, 2],
}

LASSL_CONFIG: Dict = {
    **SIMCLR_CONFIG,
    'sampler_alpha': 0.5,
    'sampler_window': 10,
}

LINEAR_CONFIG: Dict = {
    'lr_grid': [0.01, 0.001, 0.0001],
    'wd_grid': [1e-4, 1e-5, 1e-6],
    'epochs': 20,
    'batch_size': 32,
}

DATA_CONFIG: Dict = {
    'root_dir': '.data_cache/datasets/waterbird_complete95_forest2water2',
    'num_workers': 4,
}
```

---

### 5. SimCLR Orchestration (`code/run_simclr.py`)

**Dependencies:** h-e1 modules, config

```python
def main():
    """Train standard SimCLR for M1 baseline."""
    ...

def extract_and_save_embeddings(model: SimCLR, dataloader: DataLoader, checkpoint_path: str, device: str) -> None: ...
```

---

### 6. LA-SSL Orchestration (`code/run_lassl.py`)

**Dependencies:** LASSLTrainer, LASSLSampler, config

```python
def main():
    """Train LA-SSL for M3 intervention."""
    ...
```

---

### 7. Validation Orchestration (`code/run_validation.py`)

**Dependencies:** MechanismValidator, h-e1 metrics

```python
def main():
    """Run M1/M2/M3 gate checks and generate report."""
    ...

def plot_ami_evolution(simclr_ami: List[Tuple], lassl_ami: List[Tuple], output_path: str) -> None: ...
def plot_ami_wga_correlation(ami_values: List[float], delta_wga_values: List[float], output_path: str) -> None: ...
def plot_embeddings_tsne(embeddings_simclr: np.ndarray, embeddings_lassl: np.ndarray, groups: np.ndarray, output_path: str) -> None: ...
def plot_group_accuracies(baseline: Dict, cluster_balanced: Dict, lassl: Dict, output_path: str) -> None: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | LA-SSL Sampler Implementation | Implement learning-speed tracking, inverse probability sampling | 11 | Module(3) + Deps(1) + Algo(4) + Integ(3) |
| M-2 | LA-SSL Training Infrastructure | Integrate sampler with SimCLR training loop, loss tracking | 9 | Module(2) + Deps(2) + Algo(2) + Integ(3) |
| M-3 | SimCLR Baseline Training | Train standard SimCLR 100 epochs, save checkpoints every 10 epochs | 8 | Module(2) + Deps(1) + Algo(2) + Integ(3) |
| M-4 | LA-SSL Training Execution | Train LA-SSL with sampler, aligned checkpoints with SimCLR | 8 | Module(2) + Deps(1) + Algo(2) + Integ(3) |
| M-5 | Embedding Extraction & Clustering | Extract embeddings from all checkpoints, compute AMI evolution | 10 | Module(2) + Deps(2) + Algo(3) + Integ(3) |
| M-6 | Linear Probe & Cluster Retraining | Grid search baseline, cluster-balanced retraining, ΔWGA | 12 | Module(3) + Deps(2) + Algo(4) + Integ(3) |
| M-7 | Mechanism Validation Suite | Implement M1/M2/M3 gate checks with statistical tests | 14 | Module(3) + Deps(2) + Algo(5) + Integ(4) |
| M-8 | Visualization & Reporting | Generate AMI evolution, correlation plots, t-SNE, report | 10 | Module(2) + Deps(2) + Algo(3) + Integ(3) |

**Distribution:** VeryHigh(18-20): [], High(14-17): [M-7], Medium(9-13): [M-1, M-5, M-6, M-8], Low(4-8): [M-2, M-3, M-4]

---

## Implementation Notes

### Critical Decisions

**LA-SSL Sampling:** Inverse probability weighting based on loss delta over 10-epoch window. Alpha=0.5 controls temperature.

**Checkpoint Alignment:** Both SimCLR and LA-SSL save checkpoints at epochs [10, 20, ..., 100] for direct comparison.

**M2 Validation:** Collect (AMI, ΔWGA) pairs across all SimCLR checkpoints. Use Pearson correlation with p-value test.

**M3 Validation:** Compare epoch-100 checkpoints. AMI reduction = (SimCLR - LA-SSL) / SimCLR. Linear separability via logistic regression AUC on subgroup classification.

### Risk Mitigation

**M1 Failure (AMI <0.4):** MUST_WORK gate violated. Verify SimCLR hyperparameters match h-e1, check temperature=0.5, ensure 100 epochs sufficient.

**M2 Failure (No correlation):** MUST_WORK gate violated. Increase checkpoint count, verify cluster-balanced retraining logic, check across seeds.

**M3 Failure (LA-SSL doesn't disperse):** Secondary failure, graceful degradation. M1+M2 sufficient for Tiers 1-2 publication.

**GPU:** Single GPU via CUDA_VISIBLE_DEVICES. Mixed precision if memory constrained.

---

## Success Criteria

### Primary (MUST_WORK Gate)

**M1:** AMI ≥0.4 on SimCLR epoch-100 embeddings

**M2:** Pearson correlation(AMI, ΔWGA) significant (p<0.05), high-AMI (≥0.4) models gain ≥2pp WGA

### Secondary (Can Fail)

**M3:** AMI reduction ≥30% AND ΔAUC <0.05

### Graceful Degradation

M1+M2 passing → Clusterability diagnostic validated, M3 mechanism unexplained but core contribution intact

---

## Validation Checklist

- [x] No ASCII diagrams
- [x] KB search pattern applied (DL experiment architecture)
- [x] Module interfaces only
- [x] 6-12 Epic tasks (MECHANISM range: 8 tasks)
- [x] Complexity scores with breakdown
- [x] Codebase Analysis section included
- [x] External Dependencies section with actual h-e1 paths
- [x] Total length <500 lines

---

**END OF ARCHITECTURE SPECIFICATION**
