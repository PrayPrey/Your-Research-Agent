# Logic Design: H-E1 Basin Entry Heterogeneity Validation

**Date:** 2026-05-12
**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Author:** Logic Agent
**Phase:** Phase 3 - Logic Design

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project - designing new APIs
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## Overview

Copy-paste ready API signatures with tensor shapes for implementing baseline NeuroSAT on G4SATBench 3-SAT dataset to validate heterogeneity in violation patterns.

**Applied**: Standard PyTorch + PyTorch Geometric patterns

---

## A-1: Setup Dataset Infrastructure [Complexity: 8, Budget: 8]

**Applied**: PyTorch Geometric Data collate patterns

### API Signatures

```python
from typing import List, Tuple
from torch.utils.data import Dataset, DataLoader
from torch_geometric.data import Data, Batch
import torch

class G4SATDataset(Dataset):
    def __init__(self, root: str, split: str = 'train', difficulty: str = 'easy'):
        """Load G4SATBench 3-SAT dataset."""
        pass
        
    def __len__(self) -> int:
        return len(self.file_list)
    
    def __getitem__(self, idx: int) -> Data:
        """Return: Data(x_literal=[L, 128], x_clause=[C, 128], edge_index=[2, E], is_sat=bool)"""
        pass

def collate_sat_batch(batch: List[Data]) -> Batch:
    """Custom collate for variable-size SAT instances."""
    pass

class SATDataLoader:
    def __init__(self, root: str, batch_size: int = 128, num_workers: int = 4):
        """DataLoader wrapper for train/val/test splits."""
        pass
        
    def get_train_loader(self) -> DataLoader:
        """Returns training DataLoader with augmentation."""
        pass
    
    def get_val_loader(self) -> DataLoader:
        """Returns validation DataLoader."""
        pass
    
    def get_test_loader(self) -> DataLoader:
        """Returns test DataLoader."""
        pass
```

### Tensor Shapes

| Variable | Shape | Description |
|----------|-------|-------------|
| x_literal | [L, 128] | Literal node features (L = 2 × num_variables) |
| x_clause | [C, 128] | Clause node features |
| edge_index | [2, E] | Bipartite edges (clause → literal incidence) |
| batch_literal | [L_batch] | Batch assignment for literals |
| batch_clause | [C_batch] | Batch assignment for clauses |

### Pseudo-code

```
1. Parse DIMACS CNF file → extract clauses
2. Build literal nodes: [1, -1, 2, -2, ..., n, -n]
3. Build clause nodes: one per clause
4. Build edges: clause_i → literal_j if literal_j in clause_i
5. Initialize features: random embeddings [L, 128], [C, 128]
6. Return Data(x_literal, x_clause, edge_index, is_sat)
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | DIMACS parser | Parse CNF files to clause list |
| L-1-2 | Graph construction | Build literal-clause bipartite graph |
| L-1-3 | Feature initialization | Random embeddings for literals/clauses |
| L-1-4 | Dataset class | Implement __getitem__, __len__ |
| L-1-5 | Collate function | Custom batch collation for PyG |
| L-1-6 | DataLoader wrapper | Train/val/test loader factory |
| L-1-7 | Augmentation | Variable/clause permutation, negation flips |
| L-1-8 | Integration test | Load batch, verify shapes |

---

## A-2: Implement NeuroSAT Model [Complexity: 12, Budget: 12]

**Applied**: PyTorch GNN message passing patterns

### API Signatures

```python
import torch
import torch.nn as nn
from torch import Tensor
from torch_geometric.data import Batch

class MLP(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int, num_layers: int = 3):
        """Multi-layer perceptron for message functions."""
        super().__init__()
        # Build layers: input → [hidden] * (num_layers-1) → output
        
    def forward(self, x: Tensor) -> Tensor:
        """x: [*, D_in] -> [*, D_out]"""
        return self.net(x)

class NeuroSAT(nn.Module):
    def __init__(self, hidden_size: int = 128, num_rounds: int = 32):
        """NeuroSAT message-passing GNN."""
        super().__init__()
        self.hidden_size = hidden_size
        self.num_rounds = num_rounds
        
        # Message MLPs
        self.l_msg_mlp = MLP(hidden_size, hidden_size, hidden_size, num_layers=3)
        self.c_msg_mlp = MLP(hidden_size, hidden_size, hidden_size, num_layers=3)
        
        # LSTM state updates
        self.l_update = nn.LSTM(hidden_size * 2, hidden_size, batch_first=True)
        self.c_update = nn.LSTM(hidden_size, hidden_size, batch_first=True)
        
        # Satisfiability decoder
        self.sat_decoder = nn.Sequential(
            nn.Linear(hidden_size, 1),
            nn.Sigmoid()
        )
        
    def forward(self, batch: Batch) -> Tuple[Tensor, Tensor]:
        """Message-passing forward pass.
        Args: batch with x_literal=[L, H], x_clause=[C, H], edge_index=[2, E]
        Returns: l_final=[L, H], c_final=[C, H]
        """
        pass
    
    def decode_assignment(self, l_embeddings: Tensor, num_vars: int) -> Tensor:
        """Decode variable assignment from literal embeddings.
        Args: l_embeddings=[L, H] where L=2n
        Returns: assignment=[n] boolean
        """
        pass
    
    def predict_sat(self, l_embeddings: Tensor, batch_literal: Tensor) -> Tensor:
        """Predict satisfiability from literal embeddings.
        Args: l_embeddings=[L, H], batch_literal=[L]
        Returns: p_sat=[B] probability per instance
        """
        pass
```

### Tensor Shapes

| Variable | Shape | Description |
|----------|-------|-------------|
| x_literal | [L, 128] | Literal embeddings (L = 2n) |
| x_clause | [C, 128] | Clause embeddings |
| edge_index | [2, E] | Bipartite edges |
| l_msg | [L, 128] | Literal → clause messages |
| c_msg | [C, 128] | Clause → literal messages |
| l_final | [L, 128] | Final literal embeddings |
| assignment | [n] | Boolean variable assignment |

### Pseudo-code

```
1. Initialize: l_state = x_literal, c_state = x_clause
2. For t in range(num_rounds):
   a. l_msg = l_msg_mlp(l_state)
   b. c_agg = scatter_mean(l_msg, edge_index, dim_size=num_clauses)
   c. c_state, c_hidden = c_update(c_agg.unsqueeze(1), c_hidden)
   d. c_msg = c_msg_mlp(c_state.squeeze(1))
   e. l_agg = scatter_mean(c_msg[edge_index[0]], edge_index[1])
   f. l_flip = flip_literal_pairs(l_state)  # [L, H]
   g. l_input = cat([l_agg, l_flip], dim=-1)  # [L, 2H]
   h. l_state, l_hidden = l_update(l_input.unsqueeze(1), l_hidden)
3. Return l_state.squeeze(1), c_state.squeeze(1)
```

### Subtasks [12/12 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | MLP module | 3-layer MLP with ReLU |
| L-2-2 | Message computation | l_msg_mlp, c_msg_mlp |
| L-2-3 | Scatter aggregation | scatter_mean for message passing |
| L-2-4 | LSTM update | l_update, c_update cells |
| L-2-5 | Message loop | num_rounds iterations |
| L-2-6 | Literal flip | Swap positive/negative literal embeddings |
| L-2-7 | Assignment decoder | Compare l[i] vs l[-i] scores |
| L-2-8 | SAT predictor | sigmoid(linear(mean(l_embeddings))) |
| L-2-9 | Forward pass | Full message-passing implementation |
| L-2-10 | Edge indexing | Handle PyG edge_index format |
| L-2-11 | Batch support | Handle batched graphs with batch indices |
| L-2-12 | Smoke test | Forward pass on dummy data |

---

## A-3: Build Training Pipeline [Complexity: 10, Budget: 10]

**Applied**: PyTorch training loop patterns

### API Signatures

```python
from torch.optim import Optimizer, Adam
from torch.optim.lr_scheduler import ReduceLROnPlateau
import torch.nn.functional as F

def unsupervised_loss(p_sat: Tensor, is_sat: Tensor) -> Tensor:
    """NeuroSAT unsupervised loss.
    Args: p_sat=[B] probabilities, is_sat=[B] labels
    Returns: loss scalar
    """
    pass

def train_epoch(model: nn.Module, dataloader: DataLoader, optimizer: Optimizer, device: str) -> float:
    """Train one epoch. Returns: avg_loss"""
    pass

def validate_epoch(model: nn.Module, dataloader: DataLoader, device: str) -> float:
    """Validate one epoch. Returns: avg_loss"""
    pass

class Trainer:
    def __init__(self, model: nn.Module, train_loader: DataLoader, val_loader: DataLoader, config: dict):
        """Training orchestrator."""
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.config = config
        
        self.optimizer = Adam(
            model.parameters(), 
            lr=config['lr'], 
            weight_decay=config['weight_decay']
        )
        self.scheduler = ReduceLROnPlateau(
            self.optimizer, 
            mode='min', 
            factor=0.5, 
            patience=10
        )
        self.best_val_loss = float('inf')
        self.patience_counter = 0
        
    def train(self, epochs: int) -> dict:
        """Train for epochs with early stopping. Returns: history dict"""
        pass
    
    def save_checkpoint(self, path: str):
        """Save model, optimizer, scheduler state."""
        pass
    
    def load_checkpoint(self, path: str):
        """Load checkpoint."""
        pass
```

### Pseudo-code

```
1. unsupervised_loss:
   a. loss = -is_sat * log(p_sat) - (1-is_sat) * log(1-p_sat)
   b. Return mean(loss)

2. train_epoch:
   a. For batch in dataloader:
      - l_emb, c_emb = model(batch)
      - p_sat = model.predict_sat(l_emb, batch.batch_literal)
      - loss = unsupervised_loss(p_sat, batch.is_sat)
      - loss.backward(); optimizer.step()
   b. Return avg_loss

3. Trainer.train:
   a. For epoch in range(epochs):
      - train_loss = train_epoch(...)
      - val_loss = validate_epoch(...)
      - scheduler.step(val_loss)
      - If val_loss < best: save checkpoint, reset patience
      - Else: patience_counter++
      - If patience_counter > patience: break
   b. Return history
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Unsupervised loss | -log(p_sat) formulation |
| L-3-2 | Train epoch loop | Iterate batches, forward, backward |
| L-3-3 | Validate epoch loop | No gradient, compute val loss |
| L-3-4 | Optimizer setup | Adam with lr, weight_decay |
| L-3-5 | LR scheduler | ReduceLROnPlateau |
| L-3-6 | Early stopping | Track best val_loss, patience |
| L-3-7 | Checkpoint save | torch.save model state |
| L-3-8 | Checkpoint load | torch.load and restore |
| L-3-9 | Training history | Log losses to dict/CSV |
| L-3-10 | Device handling | .to(device) for model and data |

---

## A-4: Implement Heterogeneity Metrics [Complexity: 9, Budget: 9]

**Applied**: Standard NumPy/SciPy patterns

### API Signatures

```python
import numpy as np
from numpy import ndarray
from scipy.stats import entropy
from typing import List, Dict, Tuple

def compute_hamming_distance(assignment: ndarray, ground_truth: ndarray) -> float:
    """Compute normalized Hamming distance d/n.
    Args: assignment=[n], ground_truth=[n]
    Returns: d_n in [0, 1]
    """
    pass

def compute_violation_entropy(assignment: ndarray, clauses: List[List[int]]) -> float:
    """Compute violation pattern entropy H.
    Args: assignment=[n], clauses=List of clause literals
    Returns: H entropy value
    """
    pass

def compute_heterogeneity_metrics(
    assignments: List[ndarray], 
    ground_truths: List[ndarray],
    clauses_list: List[List[List[int]]]
) -> Dict[str, float]:
    """Compute heterogeneity distribution metrics.
    Returns: {d_n_range, d_n_iqr, d_n_mean, d_n_std, entropy_range, entropy_mean, entropy_std, pass_criteria}
    """
    pass

class HeterogeneityAnalyzer:
    def __init__(self):
        """Analyzer for basin entry heterogeneity."""
        self.gate_threshold_dn = 0.20
        self.gate_threshold_entropy = 2.0
        
    def collect_solutions(self, model: nn.Module, dataloader: DataLoader) -> Tuple[List[ndarray], List[ndarray], List]:
        """Generate assignments from model on test set.
        Returns: (assignments, ground_truths, clauses_list)
        """
        pass
    
    def analyze_distribution(self, assignments: List[ndarray], ground_truths: List[ndarray], clauses_list: List) -> Dict:
        """Wrapper for compute_heterogeneity_metrics."""
        return compute_heterogeneity_metrics(assignments, ground_truths, clauses_list)
    
    def check_gate_criteria(self, metrics: Dict[str, float]) -> bool:
        """Check if gate thresholds met. Returns: d_n_range > 0.20 AND entropy_range > 2.0"""
        pass
```

### Pseudo-code

```
1. compute_hamming_distance:
   a. d = sum(assignment != ground_truth)
   b. Return d / len(assignment)

2. compute_violation_entropy:
   a. For each clause: check if violated
   b. Count violations per clause
   c. p_i = violations[i] / total_violations
   d. H = -sum(p_i * log(p_i))
   e. Return H

3. compute_heterogeneity_metrics:
   a. For each (assignment, ground_truth, clauses):
      - Compute d_n = compute_hamming_distance(...)
      - Compute H = compute_violation_entropy(...)
   b. Compute statistics: d_n_range, d_n_iqr, entropy_range
   c. Check gate: d_n_range > 0.20 AND entropy_range > 2.0
   d. Return metrics dict
```

### Subtasks [9/9 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Hamming distance | Compute d/n metric |
| L-4-2 | Violation entropy | Compute H metric |
| L-4-3 | Distribution stats | Range, IQR, mean, std |
| L-4-4 | Gate check | Threshold comparison |
| L-4-5 | Solution collector | Generate assignments from model |
| L-4-6 | Batch processing | Loop over test set |
| L-4-7 | Metrics aggregation | Compute summary statistics |
| L-4-8 | JSON export | Save metrics to file |
| L-4-9 | Integration test | Run on synthetic data |

---

## A-5: Create Visualization System [Complexity: 7, Budget: 7]

**Applied**: Matplotlib visualization patterns

### API Signatures

```python
import matplotlib.pyplot as plt
from typing import List

def plot_gate_comparison(metrics: Dict[str, float], save_path: str):
    """Bar chart comparing target vs actual gate metrics."""
    pass

def plot_dn_distribution(dn_values: List[float], save_path: str):
    """Histogram of d/n values with quartile markers."""
    pass

def plot_entropy_distribution(entropy_values: List[float], save_path: str):
    """Histogram of entropy H values."""
    pass

def plot_dn_vs_entropy_scatter(dn_values: List[float], entropy_values: List[float], save_path: str):
    """Scatter plot of d/n vs entropy."""
    pass

def plot_quartile_boxplot(dn_values: List[float], entropy_values: List[float], save_path: str):
    """Box plots for d/n and entropy distributions."""
    pass

def generate_all_figures(metrics: Dict[str, float], output_dir: str):
    """Generate all required figures."""
    pass
```

### Pseudo-code

```
1. plot_gate_comparison:
   a. x = ['d/n range', 'entropy range']
   b. target = [0.20, 2.0]
   c. actual = [metrics['d_n_range'], metrics['entropy_range']]
   d. Bar chart with target (red) and actual (blue)

2. generate_all_figures:
   a. Call all plot functions
   b. Save to output_dir/*.png
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Gate comparison plot | Bar chart with target/actual |
| L-5-2 | d/n histogram | Distribution with quartiles |
| L-5-3 | Entropy histogram | Distribution with statistics |
| L-5-4 | Scatter plot | d/n vs entropy correlation |
| L-5-5 | Box plot | Quartile visualization |
| L-5-6 | Figure orchestrator | generate_all_figures wrapper |
| L-5-7 | Save utilities | PNG export with DPI |

---

## A-6: Integration & Execution [Complexity: 6, Budget: 6]

**Applied**: Standard argparse + orchestration patterns

### API Signatures

```python
import argparse
from argparse import Namespace

def setup_experiment(args: Namespace) -> Tuple[nn.Module, SATDataLoader, dict]:
    """Initialize model, data, config from args.
    Returns: (model, data_loader, config)
    """
    pass

def run_training(model: nn.Module, data_loader: SATDataLoader, config: dict) -> str:
    """Run training pipeline. Returns: checkpoint_path"""
    pass

def run_evaluation(model: nn.Module, test_loader: DataLoader, output_dir: str) -> Dict[str, float]:
    """Run evaluation and generate metrics. Returns: metrics dict"""
    pass

def main(args: Namespace):
    """Main experiment orchestrator."""
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='H-E1 NeuroSAT Experiment')
    parser.add_argument('--data_root', type=str, default='./data/g4satbench')
    parser.add_argument('--output_dir', type=str, default='./outputs')
    parser.add_argument('--seed', type=int, default=123)
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--batch_size', type=int, default=128)
    parser.add_argument('--lr', type=float, default=1e-4)
    parser.add_argument('--weight_decay', type=float, default=1e-8)
    parser.add_argument('--hidden_size', type=int, default=128)
    parser.add_argument('--num_rounds', type=int, default=32)
    parser.add_argument('--device', type=str, default='cuda')
    
    args = parser.parse_args()
    main(args)
```

### Pseudo-code

```
1. setup_experiment:
   a. Set random seed
   b. Create SATDataLoader(args.data_root, args.batch_size)
   c. Create NeuroSAT(args.hidden_size, args.num_rounds)
   d. Build config dict from args
   e. Return model, data_loader, config

2. main:
   a. model, data_loader, config = setup_experiment(args)
   b. checkpoint_path = run_training(model, data_loader, config)
   c. model.load_checkpoint(checkpoint_path)
   d. metrics = run_evaluation(model, data_loader.get_test_loader(), args.output_dir)
   e. Print gate results
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Argparse setup | CLI argument parser |
| L-6-2 | setup_experiment | Initialize all components |
| L-6-3 | run_training | Training orchestration |
| L-6-4 | run_evaluation | Evaluation orchestration |
| L-6-5 | main workflow | Connect all stages |
| L-6-6 | End-to-end test | Smoke test with small dataset |

---

## Configuration Specifications

```python
DEFAULT_CONFIG = {
    'model': {'hidden_size': 128, 'num_rounds': 32},
    'training': {
        'optimizer': 'Adam',
        'lr': 1e-4,
        'weight_decay': 1e-8,
        'batch_size': 128,
        'epochs': 100,
        'early_stopping_patience': 20,
        'lr_scheduler': {'type': 'ReduceLROnPlateau', 'mode': 'min', 'factor': 0.5, 'patience': 10},
        'seed': 123,
    },
    'dataset': {'root': './data/g4satbench', 'difficulty': 'easy', 'num_workers': 4},
    'evaluation': {'num_test_samples': 10000, 'gate_threshold_dn': 0.20, 'gate_threshold_entropy': 2.0}
}
```

---

## Self-Validation Checklist

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in code comments
- [x] Subtask count within budget (52/52 total)
- [x] Total length < 600 lines
- [x] "Codebase Analysis (Serena)" section included
- [x] Green-field project noted

---

**Document Status:** READY FOR PHASE 4
**Total Budget Used:** 52/52 subtasks
**Next Phase:** Phase 4 - Implementation
