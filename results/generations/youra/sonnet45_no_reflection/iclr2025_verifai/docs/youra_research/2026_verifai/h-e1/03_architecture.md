# System Architecture: H-E1 Basin Entry Heterogeneity Validation

**Date:** 2026-05-12
**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Author:** Architecture Agent
**Phase:** Phase 3 - Architecture Design

---

## Applied Patterns

Applied: Generic DL training patterns (Archon KB - diffusion model architectures)

---

## Codebase Analysis (Serena)

**Project Type**: Green-field
**Status**: New implementation from scratch
**Analyzed Path**: N/A
**Findings**: No existing codebase - implementing baseline NeuroSAT + G4SATBench integration from scratch

---

## Architecture Overview

**Hypothesis Goal**: Validate that baseline NeuroSAT generates heterogeneous violation patterns (d/n range > 0.20, entropy H > 2.0) sufficient for basin recovery stratification.

**Implementation Strategy**: Minimal PoC architecture for EXISTENCE validation.
- Single model: NeuroSAT baseline
- Single dataset: G4SATBench 3-SAT easy
- Single config: Hardcoded hyperparameters
- Metrics focus: d/n and entropy distribution analysis

---

## Module Structure

### DataModule (`data/sat_dataset.py`)

**Dependencies**: torch, torch_geometric

```python
class G4SATDataset(Dataset):
    def __init__(self, root: str, split: str, difficulty: str = 'easy'): ...
    def __getitem__(self, idx: int) -> Data: ...
    def __len__(self) -> int: ...

def collate_sat_batch(batch: List[Data]) -> Batch: ...

class SATDataLoader:
    def __init__(self, root: str, batch_size: int = 128): ...
    def get_train_loader(self) -> DataLoader: ...
    def get_val_loader(self) -> DataLoader: ...
    def get_test_loader(self) -> DataLoader: ...
```

### ModelModule (`models/neurosat.py`)

**Dependencies**: torch.nn, torch_geometric

```python
class MLP(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int, num_layers: int = 3): ...
    def forward(self, x: Tensor) -> Tensor: ...

class NeuroSAT(nn.Module):
    def __init__(self, hidden_size: int = 128, num_rounds: int = 32): ...
    def forward(self, graph: Data, l_init: Tensor, c_init: Tensor) -> Tuple[Tensor, Tensor]: ...
    def decode_assignment(self, l_embeddings: Tensor) -> Tensor: ...
```

### MetricsModule (`metrics/heterogeneity.py`)

**Dependencies**: numpy, scipy

```python
def compute_hamming_distance(assignment: ndarray, ground_truth: ndarray) -> float: ...

def compute_violation_entropy(assignment: ndarray, clauses: List) -> float: ...

def compute_heterogeneity_metrics(assignments: List[ndarray], ground_truths: List[ndarray]) -> dict: ...

class HeterogeneityAnalyzer:
    def __init__(self): ...
    def collect_solutions(self, model: nn.Module, dataloader: DataLoader) -> Tuple[List, List]: ...
    def analyze_distribution(self, assignments: List, ground_truths: List) -> dict: ...
    def check_gate_criteria(self, metrics: dict) -> bool: ...
```

### VisualizationModule (`visualization/plots.py`)

**Dependencies**: matplotlib, numpy

```python
def plot_gate_comparison(metrics: dict, save_path: str): ...

def plot_dn_distribution(dn_values: List[float], save_path: str): ...

def plot_entropy_distribution(entropy_values: List[float], save_path: str): ...

def plot_dn_vs_entropy_scatter(dn_values: List[float], entropy_values: List[float], save_path: str): ...

def plot_quartile_boxplot(dn_values: List[float], entropy_values: List[float], save_path: str): ...

def generate_all_figures(metrics: dict, output_dir: str): ...
```

### TrainModule (`train.py`)

**Dependencies**: All above modules

```python
def train_epoch(model: nn.Module, dataloader: DataLoader, optimizer: Optimizer, device: str) -> float: ...

def validate_epoch(model: nn.Module, dataloader: DataLoader, device: str) -> float: ...

def unsupervised_loss(l_embeddings: Tensor, c_embeddings: Tensor, is_sat: Tensor) -> Tensor: ...

class Trainer:
    def __init__(self, model: nn.Module, train_loader: DataLoader, val_loader: DataLoader, config: dict): ...
    def train(self, epochs: int) -> dict: ...
    def save_checkpoint(self, path: str): ...
    def load_checkpoint(self, path: str): ...
```

### ExperimentModule (`run_experiment.py`)

**Dependencies**: All modules, argparse

```python
def setup_experiment(args: Namespace) -> Tuple: ...

def run_training(model: nn.Module, data_loader: SATDataLoader, config: dict) -> str: ...

def run_evaluation(model: nn.Module, test_loader: DataLoader, output_dir: str) -> dict: ...

def main(args: Namespace): ...
```

---

## File Organization

```
h-e1/
├── code/
│   ├── data/
│   │   ├── __init__.py
│   │   └── sat_dataset.py          # G4SATBench dataset wrapper
│   ├── models/
│   │   ├── __init__.py
│   │   ├── mlp.py                  # MLP helper
│   │   └── neurosat.py             # NeuroSAT architecture
│   ├── metrics/
│   │   ├── __init__.py
│   │   └── heterogeneity.py        # d/n and entropy computation
│   ├── visualization/
│   │   ├── __init__.py
│   │   └── plots.py                # Figure generation
│   ├── train.py                    # Training loop
│   ├── run_experiment.py           # Main entry point
│   └── requirements.txt
├── figures/                         # Generated visualizations
├── checkpoints/                     # Model checkpoints
└── results/
    ├── training_log.csv
    └── heterogeneity_metrics.json
```

---

## Data Flow

```
DIMACS CNF → G4SATDataset → Literal-Clause Graph → NeuroSAT → Literal Embeddings → Assignment Decoder → Heterogeneity Metrics → Gate Evaluation
```

---

## Configuration

**Hardcoded in `run_experiment.py`** (EXISTENCE PoC - no YAML config):

```python
CONFIG = {
    'model': {
        'hidden_size': 128,
        'num_rounds': 32,
    },
    'training': {
        'optimizer': 'Adam',
        'lr': 1e-4,
        'weight_decay': 1e-8,
        'batch_size': 128,
        'epochs': 100,
        'early_stopping_patience': 20,
        'lr_scheduler': {
            'type': 'ReduceLROnPlateau',
            'mode': 'min',
            'factor': 0.5,
            'patience': 10,
        },
        'seed': 123,
    },
    'dataset': {
        'root': './data/g4satbench',
        'difficulty': 'easy',
        'num_workers': 4,
    },
    'evaluation': {
        'num_test_samples': 10000,
        'gate_threshold_dn': 0.20,
        'gate_threshold_entropy': 2.0,
    }
}
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup Dataset Infrastructure | Install G4SATBench, implement dataset loader, collate function | 8 | Module(2) + Deps(2) + Algo(2) + Integ(2) |
| A-2 | Implement NeuroSAT Model | MLP helper, NeuroSAT architecture, assignment decoder | 12 | Module(3) + Deps(2) + Algo(4) + Integ(3) |
| A-3 | Build Training Pipeline | Training loop, unsupervised loss, validation, checkpointing | 10 | Module(2) + Deps(2) + Algo(3) + Integ(3) |
| A-4 | Implement Heterogeneity Metrics | d/n computation, entropy computation, distribution analysis | 9 | Module(2) + Deps(2) + Algo(3) + Integ(2) |
| A-5 | Create Visualization System | Gate comparison, histograms, scatter plot, box plot | 7 | Module(2) + Deps(1) + Algo(2) + Integ(2) |
| A-6 | Integration & Execution | Main script, experiment orchestration, results saving | 6 | Module(1) + Deps(1) + Algo(2) + Integ(2) |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3, A-4], Low(4-8): [A-1, A-5, A-6]

**Total Complexity**: 52 points

---

## Interface Contracts

### Data Format

**Input**: DIMACS CNF files
```
p cnf 10 42
1 -2 3 0
-1 2 -3 0
...
```

**Graph Representation**: PyTorch Geometric `Data` object
```python
Data(
    x_literal=Tensor(num_literals, 128),  # Literal node features
    x_clause=Tensor(num_clauses, 128),    # Clause node features
    edge_index=Tensor(2, num_edges),      # Bipartite edges
    is_sat=bool,                          # Satisfiability label
)
```

**Model Output**: Tuple[Tensor, Tensor]
```python
(
    l_final: Tensor(num_literals, 128),   # Final literal embeddings
    c_final: Tensor(num_clauses, 128),    # Final clause embeddings
)
```

**Metrics Output**: Dict
```python
{
    'd_n_range': float,          # max - min
    'd_n_iqr': float,            # Q3 - Q1
    'd_n_mean': float,
    'd_n_std': float,
    'entropy_range': float,
    'entropy_mean': float,
    'entropy_std': float,
    'pass_criteria': bool,       # Both gates passed
}
```

---

## Dependencies

**Core Libraries**:
- PyTorch >= 2.0
- PyTorch Geometric >= 2.3
- NumPy >= 1.24
- SciPy >= 1.10
- Matplotlib >= 3.7

**External Repository**:
- G4SATBench: https://github.com/zhaoyu-li/G4SATBench
  - Installation: `git clone` + `bash scripts/install.sh`
  - Usage: Dataset generation and loading utilities

---

## Success Criteria

**Gate Validation** (MUST_WORK):
1. d/n range > 0.20
2. Entropy range > 2.0
3. Both conditions must be satisfied

**Expected Baseline Performance**:
- Clause satisfaction: ~85% (NeuroSAT paper)
- Classification accuracy: ~85% on SR(U(10,40))

---

## Risk Mitigation

**Risk 1: Insufficient Heterogeneity**
- Fallback: Explore alternative Stage 1 architectures (GGNN, GCN)

**Risk 2: G4SATBench Installation Issues**
- Fallback: Generate synthetic 3-SAT instances with simple generator

**Risk 3: Memory Constraints (batch_size=128 on 24GB GPU)**
- Mitigation: Reduce to batch_size=64/32 with gradient accumulation

---

## Implementation Notes

**EXISTENCE PoC Simplifications**:
- Hardcoded config (no YAML)
- Print statements + CSV logging (no WandB)
- Smoke tests only (no unit test suite)
- Single seed run (seed=123)

**Next Phase**: Phase 4 - Implementation
- Implement modules in order: Data → Model → Metrics → Training → Visualization → Integration
- Run training (100 epochs, ~8 hours on single GPU)
- Generate heterogeneity metrics and figures
- Evaluate gate criteria

---

**Document Status:** READY FOR PHASE 4
**Architecture Type:** Minimal PoC (EXISTENCE hypothesis)
**Total Epic Tasks:** 6 (complexity range: 6-12)
