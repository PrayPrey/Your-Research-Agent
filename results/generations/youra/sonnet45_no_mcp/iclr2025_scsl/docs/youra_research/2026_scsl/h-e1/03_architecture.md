# System Architecture: h-e1 Curvature Subspace Alignment

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE (PoC)  
**Gate:** MUST_WORK  
**Date:** 2026-04-24  
**Architect:** Architecture Agent  

---

## Codebase Analysis (Serena)

**Project Type**: Green-field  
**Status**: New implementation from scratch  
**Analyzed Path**: N/A  
**Findings**: Foundation hypothesis with no existing code to analyze. Standard PyTorch + ResNet-50 implementation using established libraries (torchvision, pytorch-hessian-eigenthings).

---

## Knowledge Base Patterns Applied

Applied: Minimal PoC Pattern (EXISTENCE hypothesis)  
Applied: PyTorch Training Loop Pattern  
Applied: Hessian Eigendecomposition Pattern  

---

## System Overview

**Purpose**: Validate that ERM and Group-DRO training produce geometrically distinct solutions measurable via Marchenko-Pastur-defined curvature subspace alignment A(w).

**Core Components**:
- Data loading (Waterbirds dataset)
- Training modules (ERM and Group-DRO)
- Hessian analysis (eigendecomposition + MP fitting)
- Alignment computation (minority gradient projection)
- Evaluation and visualization

**Infrastructure Tier**: LIGHT (hardcoded configs, CSV logging, smoke test only)

---

## Module Structure

### 1. Data Module (`data.py`)

**Dependencies**: None

```python
class WaterbirdsDataset:
    def __init__(self, root_dir: str, split: str, transform: transforms.Compose): ...
    def __getitem__(self, idx: int) -> Tuple[Tensor, int, int]: ...
    def __len__(self) -> int: ...

def get_dataloaders(data_dir: str, batch_size: int = 128) -> Dict[str, DataLoader]:
    """Returns train, val, test loaders with group labels."""
    ...

def get_minority_loader(data_dir: str, batch_size: int = 32) -> DataLoader:
    """Returns loader for minority groups (landbird-water, waterbird-land)."""
    ...
```

---

### 2. Model Module (`model.py`)

**Dependencies**: None

```python
def get_resnet50(num_classes: int = 2, pretrained: bool = True) -> nn.Module:
    """Load ResNet-50 with modified final layer."""
    ...

class GroupDROLoss(nn.Module):
    def __init__(self, num_groups: int = 4): ...
    def forward(self, outputs: Tensor, labels: Tensor, groups: Tensor) -> Tensor: ...
```

---

### 3. Training Module (`train.py`)

**Dependencies**: Data Module, Model Module

```python
class Trainer:
    def __init__(self, model: nn.Module, mode: str, device: str = 'cuda'): ...
    def train_epoch(self, train_loader: DataLoader, optimizer: Optimizer) -> float: ...
    def validate(self, val_loader: DataLoader) -> Dict[str, float]: ...
    def train(self, train_loader: DataLoader, val_loader: DataLoader, 
              epochs: int = 100, patience: int = 10) -> Dict[str, Any]: ...
```

---

### 4. Hessian Analysis Module (`hessian_analysis.py`)

**Dependencies**: Model Module

```python
def compute_hessian_spectrum(model: nn.Module, data_loader: DataLoader, 
                             num_eigenthings: int = 100) -> Tuple[np.ndarray, np.ndarray]:
    """Compute Hessian eigenvalues and eigenvectors."""
    ...

def fit_marchenko_pastur(eigenvalues: np.ndarray) -> Tuple[float, float, float]:
    """Fit MP distribution, return (bulk_edge, sigma_sq, gamma)."""
    ...

def compute_minority_gradient(model: nn.Module, minority_loader: DataLoader) -> Tensor:
    """Compute average gradient on minority groups."""
    ...

def compute_alignment(g_minority: Tensor, eigenvectors: np.ndarray, 
                      eigenvalues: np.ndarray, bulk_edge: float) -> float:
    """Compute A(w) = ||P_S_out g_minority||² / ||g_minority||²."""
    ...
```

---

### 5. Evaluation Module (`evaluate.py`)

**Dependencies**: Model Module, Hessian Analysis Module

```python
def compute_group_accuracies(model: nn.Module, test_loader: DataLoader) -> Dict[int, float]:
    """Compute per-group accuracies (4 groups)."""
    ...

def compute_worst_group_accuracy(group_accs: Dict[int, float]) -> float: ...

def evaluate_alignment_comparison(erm_alignment: float, dro_alignment: float) -> Dict[str, Any]:
    """Compare alignments and determine PoC success."""
    ...
```

---

### 6. Visualization Module (`visualize.py`)

**Dependencies**: None

```python
def plot_alignment_comparison(erm_alignment: float, dro_alignment: float, save_path: str): ...

def plot_hessian_spectrum(eigenvalues: np.ndarray, bulk_edge: float, save_path: str): ...

def plot_training_curves(history: Dict[str, List[float]], save_path: str): ...

def plot_group_accuracy_heatmap(erm_accs: Dict, dro_accs: Dict, save_path: str): ...

def plot_worst_group_vs_alignment(metrics: Dict[str, float], save_path: str): ...
```

---

### 7. Configuration Module (`config.py`)

**Dependencies**: None

```python
# Hardcoded configuration for LIGHT tier
SEED = 42
DATA_DIR = './data/waterbird_complete95_forest2water2/'
BATCH_SIZE = 128
LEARNING_RATE = 0.001
MOMENTUM = 0.9
WEIGHT_DECAY = 1e-4
EPOCHS = 100
PATIENCE = 10
NUM_EIGENTHINGS = 100
NUM_CLASSES = 2
NUM_GROUPS = 4
```

---

### 8. Main Experiment Script (`run_experiment.py`)

**Dependencies**: All modules

```python
def main():
    # Setup
    set_seed(SEED)
    dataloaders = get_dataloaders(DATA_DIR, BATCH_SIZE)
    minority_loader = get_minority_loader(DATA_DIR)
    
    # Train ERM
    erm_model = train_erm(dataloaders)
    
    # Train DRO
    dro_model = train_dro(dataloaders)
    
    # Hessian analysis
    erm_alignment = analyze_model(erm_model, dataloaders['train'], minority_loader)
    dro_alignment = analyze_model(dro_model, dataloaders['train'], minority_loader)
    
    # Evaluation
    results = evaluate_and_visualize(erm_model, dro_model, erm_alignment, dro_alignment)
    
    # Save results
    save_results(results)
```

---

### 9. Smoke Test (`test_smoke.py`)

**Dependencies**: All modules

```python
def test_data_loading(): ...
def test_model_forward_pass(): ...
def test_training_one_epoch(): ...
def test_hessian_computation_small(): ...
def run_smoke_tests(): ...
```

---

## File Structure

```
h-e1/
├── code/
│   ├── data.py                    # Dataset and dataloaders
│   ├── model.py                   # ResNet-50 + Group-DRO loss
│   ├── train.py                   # Training loops
│   ├── hessian_analysis.py        # Hessian + MP + alignment
│   ├── evaluate.py                # Metrics computation
│   ├── visualize.py               # Figure generation
│   ├── config.py                  # Hardcoded hyperparameters
│   ├── run_experiment.py          # Main execution script
│   ├── test_smoke.py              # Smoke tests
│   └── requirements.txt           # Dependencies
├── data/                          # Waterbirds dataset (downloaded)
├── checkpoints/                   # Model checkpoints
│   ├── erm_best.pth
│   └── dro_best.pth
├── results/                       # Logs and metrics
│   ├── training_log_erm.csv
│   ├── training_log_dro.csv
│   ├── alignment_results.csv
│   └── hessian_stats.csv
└── figures/                       # Visualizations
    ├── fig1_alignment_comparison.png
    ├── fig2_hessian_spectrum_erm.png
    ├── fig3_hessian_spectrum_dro.png
    ├── fig4_training_curves.png
    └── fig5_group_accuracy_heatmap.png
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Environment Setup | Create conda env, install dependencies, download Waterbirds dataset | 5 | 1+1+2+1 |
| A-2 | Data Module | Implement WaterbirdsDataset class and dataloaders with group labels | 8 | 2+2+2+2 |
| A-3 | Model Training | Implement ERM and Group-DRO training loops with checkpointing | 12 | 3+3+3+3 |
| A-4 | Hessian Analysis | Implement Hessian computation, MP fitting, and alignment metric A(w) | 14 | 4+3+4+3 |
| A-5 | Evaluation Pipeline | Implement metrics computation (worst-group accuracy, per-group accuracy) | 8 | 2+2+2+2 |
| A-6 | Visualization | Generate 5 required figures (alignment, spectrum, training curves, heatmap) | 10 | 2+2+3+3 |
| A-7 | Integration Testing | Run full experiment pipeline, verify results, smoke tests | 9 | 2+3+2+2 |

**Total Complexity**: 66  
**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4], Medium(9-13): [A-3, A-6, A-7], Low(4-8): [A-1, A-2, A-5]

**Complexity Scoring**:
- A-1: Module(1) + Deps(1) + Algo(2) + Integration(1) = 5
- A-2: Module(2) + Deps(2) + Algo(2) + Integration(2) = 8
- A-3: Module(3) + Deps(3) + Algo(3) + Integration(3) = 12
- A-4: Module(4) + Deps(3) + Algo(4) + Integration(3) = 14
- A-5: Module(2) + Deps(2) + Algo(2) + Integration(2) = 8
- A-6: Module(2) + Deps(2) + Algo(3) + Integration(3) = 10
- A-7: Module(2) + Deps(3) + Algo(2) + Integration(2) = 9

---

## Task Breakdown Details

### A-1: Environment Setup (Complexity: 5)

**Subtasks**:
1. Create conda environment with Python 3.8
2. Install PyTorch, torchvision with CUDA support
3. Install pytorch-hessian-eigenthings, numpy, scipy, matplotlib
4. Clone group_DRO repository and download Waterbirds dataset
5. Verify dataset structure and GPU availability

**Deliverables**:
- Working conda environment
- Waterbirds dataset in `./data/waterbird_complete95_forest2water2/`
- `requirements.txt` file

---

### A-2: Data Module (Complexity: 8)

**Subtasks**:
1. Implement `WaterbirdsDataset` class with group label support
2. Implement preprocessing transforms (resize, normalize, augmentation)
3. Create `get_dataloaders()` for train/val/test splits
4. Create `get_minority_loader()` for minority groups (groups 1, 2)
5. Verify group distribution and label correctness

**Deliverables**:
- `data.py` module
- Unit tests for data loading

---

### A-3: Model Training (Complexity: 12)

**Subtasks**:
1. Implement `get_resnet50()` with pretrained weights
2. Implement `GroupDROLoss` class with worst-group optimization
3. Implement `Trainer` class with ERM and DRO modes
4. Add early stopping on worst-group accuracy
5. Add checkpointing (save best model)
6. Add CSV logging for training metrics
7. Train both ERM and DRO models to convergence

**Deliverables**:
- `model.py` module
- `train.py` module
- ERM checkpoint (`checkpoints/erm_best.pth`)
- DRO checkpoint (`checkpoints/dro_best.pth`)
- Training logs (`results/training_log_erm.csv`, `results/training_log_dro.csv`)

---

### A-4: Hessian Analysis (Complexity: 14)

**Subtasks**:
1. Implement `compute_hessian_spectrum()` using pytorch-hessian-eigenthings
2. Implement `fit_marchenko_pastur()` with scipy optimization
3. Verify MP fit quality (visual inspection of spectrum vs distribution)
4. Implement `compute_minority_gradient()` on minority groups
5. Implement `compute_alignment()` with outlier subspace projection
6. Compute alignment for both ERM and DRO models
7. Save Hessian statistics to CSV

**Deliverables**:
- `hessian_analysis.py` module
- Hessian eigenvalues/eigenvectors (saved to disk)
- Alignment metrics (`results/alignment_results.csv`)
- Hessian statistics (`results/hessian_stats.csv`)

---

### A-5: Evaluation Pipeline (Complexity: 8)

**Subtasks**:
1. Implement `compute_group_accuracies()` for 4 groups
2. Implement `compute_worst_group_accuracy()`
3. Implement `evaluate_alignment_comparison()` with PoC success check
4. Compute metrics for ERM and DRO models on test set
5. Save final results to CSV

**Deliverables**:
- `evaluate.py` module
- Final evaluation metrics (accuracy, worst-group, alignment)
- PoC success determination (A_w_ERM > A_w_DRO?)

---

### A-6: Visualization (Complexity: 10)

**Subtasks**:
1. Implement `plot_alignment_comparison()` (bar chart)
2. Implement `plot_hessian_spectrum()` with MP bulk edge overlay
3. Implement `plot_training_curves()` (loss, accuracy over epochs)
4. Implement `plot_group_accuracy_heatmap()` (4 groups × 2 methods)
5. Implement `plot_worst_group_vs_alignment()` (scatter plot)
6. Generate all 5 figures and save to `figures/` directory

**Deliverables**:
- `visualize.py` module
- 5 figures in `figures/` directory

---

### A-7: Integration Testing (Complexity: 9)

**Subtasks**:
1. Implement smoke tests (1 epoch on 100 samples)
2. Run full experiment pipeline end-to-end
3. Verify all outputs generated correctly
4. Validate alignment comparison (A_w_ERM vs A_w_DRO)
5. Document any issues or deviations from expected results

**Deliverables**:
- `test_smoke.py` module
- Complete experiment run confirmation
- All artifacts verified (checkpoints, logs, figures, metrics)

---

## Key Design Decisions

**Minimal Infrastructure**: LIGHT tier requires hardcoded configs (no YAML), CSV logging (no TensorBoard), and basic smoke tests only.

**Single-File Modules**: Each module is self-contained in a single file for PoC simplicity.

**External Dependencies**: Uses established libraries (pytorch-hessian-eigenthings) rather than custom Hessian implementations.

**Group Label Handling**: Waterbirds dataset provides ground-truth group labels, enabling both Group-DRO training and minority gradient computation.

---

## Dependencies

**External Libraries**:
```
python>=3.8
torch>=1.10.0
torchvision>=0.11.0
numpy>=1.21.0
scipy>=1.7.0
matplotlib>=3.4.0
pytorch-hessian-eigenthings
```

**Dataset**: Waterbirds from https://github.com/kohpangwei/group_DRO

**Hardware**: Single GPU with ≥12GB VRAM

---

## Success Criteria

**PoC Pass Conditions**:
1. Code executes without errors
2. Both ERM and DRO models converge (validation accuracy plateau)
3. Hessian computation completes successfully
4. Marchenko-Pastur bulk edge estimation stable
5. **A(w)_ERM > A(w)_DRO** (direction confirmed)

**PoC Fail Conditions**:
- A(w)_ERM ≤ A(w)_DRO (no geometric signature exists)
- Hessian computation fails or OOM errors
- MP fitting fails (no clear bulk edge)

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Hessian OOM | Use training subset (2000 samples); reduce num_eigenthings to 50 |
| MP fit poor quality | Visual inspection; use middle 60% of eigenvalues for fitting |
| Long training time | Use ImageNet pretrained weights; early stopping |
| Dataset download issues | Clone group_DRO repo; follow official data preparation scripts |

---

*Architecture designed for Phase 4 Implementation | h-e1 EXISTENCE Hypothesis | LIGHT Infrastructure Tier*
