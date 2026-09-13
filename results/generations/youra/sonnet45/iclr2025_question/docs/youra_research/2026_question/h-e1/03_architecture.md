# System Architecture: h-e1 Variance Measurement

**Date:** 2026-03-21
**Hypothesis ID:** h-e1 (EXISTENCE)
**Version:** 3.0
**Phase:** 3 (Implementation Planning)

Applied: PyTorch modular experiment pattern

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase
**Status:** Existing patterns found from previous implementation
**Analyzed Path:** `/home/anonymous/YouRA_results_new_4_sonnet45/TEST_question/code/`
**Findings:** Existing codebase has modular structure (config, data, model, train, evaluate, visualize, run_experiment). New implementation will follow established pattern with dual-dataset/dual-architecture extensions.

---

## Project Context

**Hypothesis Type:** EXISTENCE (PoC)
**Goal:** Validate measurable variance (σ² ≥ 0.3%) across random seeds for 4 conditions (2 datasets × 2 architectures)
**Total Experiments:** 120 runs (30 seeds × 4 conditions)
**Gate:** MUST_WORK (failure abandons entire verification plan)

---

## Architecture Overview

### Design Philosophy
- Minimal structure for EXISTENCE validation
- Single codebase for all 4 conditions
- Deterministic execution priority
- Sequential experiment orchestration (no parallelization)

### Module Structure
```
code/
├── config.py          # Experiment configuration
├── data.py            # Dataset loading (MNIST + Fashion-MNIST)
├── model.py           # MLP architectures (1-layer + 2-layer)
├── train.py           # Training logic with determinism
├── evaluate.py        # Metrics calculation
├── visualize.py       # Figure generation
└── run_experiment.py  # Orchestrator (120 experiments)

results/
├── experiment_logs.csv
├── variance_summary.json
└── gate_result.json

figures/
├── gate_metrics_comparison.png  (mandatory)
├── variance_by_condition.png
├── accuracy_distributions.png
├── cv_comparison.png
└── accuracy_ranges.png
```

---

## Module Specifications

### ConfigModule (`code/config.py`)

**Dependencies:** None

```python
@dataclass
class ExperimentConfig:
    # Dataset selection
    datasets: List[str] = field(default_factory=lambda: ["mnist", "fashion_mnist"])

    # Model architectures
    architectures: List[str] = field(default_factory=lambda: ["1layer", "2layer"])

    # Training parameters
    seeds: List[int] = field(default_factory=lambda: list(range(30)))
    epochs: int = 10
    lr: float = 0.01
    momentum: float = 0.9
    batch_size: int = 64

    # Determinism settings
    cudnn_deterministic: bool = True
    cudnn_benchmark: bool = False

    # Paths
    data_root: str = "./data"
    results_dir: str = "./results"
    figures_dir: str = "./figures"

    def get_conditions(self) -> List[Tuple[str, str]]: ...
```

### DataModule (`code/data.py`)

**Dependencies:** ConfigModule

```python
def load_dataset(
    dataset_name: str,
    data_root: str,
    batch_size: int,
    seed: int
) -> Tuple[DataLoader, DataLoader]:
    """Load MNIST or Fashion-MNIST with deterministic shuffling."""
    ...

def get_transforms(dataset_name: str) -> transforms.Compose:
    """Get dataset-specific normalization transforms."""
    ...

def create_seeded_dataloader(
    dataset: Dataset,
    batch_size: int,
    shuffle: bool,
    seed: int
) -> DataLoader:
    """Create DataLoader with generator for reproducibility."""
    ...
```

### ModelModule (`code/model.py`)

**Dependencies:** None

```python
class SimpleMLP1Layer(nn.Module):
    def __init__(self, input_size: int = 784, hidden_size: int = 128, output_size: int = 10): ...
    def forward(self, x: Tensor) -> Tensor: ...

class SimpleMLP2Layer(nn.Module):
    def __init__(self, input_size: int = 784, hidden1: int = 256, hidden2: int = 128, output_size: int = 10): ...
    def forward(self, x: Tensor) -> Tensor: ...

def create_model(architecture: str) -> nn.Module:
    """Factory function for model creation."""
    ...
```

### TrainModule (`code/train.py`)

**Dependencies:** ModelModule, DataModule

```python
def set_seed_deterministic(seed: int) -> None:
    """Set all random seeds for reproducibility."""
    ...

def train_epoch(
    model: nn.Module,
    train_loader: DataLoader,
    optimizer: Optimizer,
    criterion: nn.Module,
    device: str
) -> float:
    """Train for one epoch, return average loss."""
    ...

def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    epochs: int,
    lr: float,
    momentum: float,
    device: str
) -> None:
    """Full training loop for 10 epochs."""
    ...
```

### EvaluateModule (`code/evaluate.py`)

**Dependencies:** ModelModule

```python
def evaluate_model(
    model: nn.Module,
    test_loader: DataLoader,
    device: str
) -> float:
    """Compute test accuracy (%)."""
    ...

def compute_variance_metrics(
    test_accuracies: List[float]
) -> Dict[str, float]:
    """Calculate variance, std, CV%, confidence intervals."""
    ...

def check_gate_condition(
    variance_summary: Dict[str, Dict[str, float]],
    threshold: float = 0.3
) -> Dict[str, Any]:
    """Validate MUST_WORK gate (≥2 conditions above threshold)."""
    ...
```

### VisualizeModule (`code/visualize.py`)

**Dependencies:** EvaluateModule

```python
def plot_gate_metrics_comparison(
    variance_summary: Dict[str, Dict[str, float]],
    threshold: float,
    save_path: str
) -> None:
    """Bar chart: target vs actual variance."""
    ...

def plot_variance_by_condition(
    variance_summary: Dict[str, Dict[str, float]],
    save_path: str
) -> None:
    """Bar chart: variance for all 4 conditions."""
    ...

def plot_accuracy_distributions(
    results_df: pd.DataFrame,
    save_path: str
) -> None:
    """2×2 histogram grid for test accuracies."""
    ...

def plot_cv_comparison(
    variance_summary: Dict[str, Dict[str, float]],
    save_path: str
) -> None:
    """Bar chart: coefficient of variation."""
    ...

def plot_accuracy_ranges(
    variance_summary: Dict[str, Dict[str, float]],
    save_path: str
) -> None:
    """Box plots with min/max/mean."""
    ...
```

### OrchestratorModule (`code/run_experiment.py`)

**Dependencies:** All modules

```python
def run_single_experiment(
    dataset_name: str,
    architecture: str,
    seed: int,
    config: ExperimentConfig,
    device: str
) -> Dict[str, Any]:
    """Execute one training run with deterministic seed."""
    ...

def run_all_experiments(
    config: ExperimentConfig
) -> pd.DataFrame:
    """Run 120 experiments (4 conditions × 30 seeds)."""
    ...

def generate_variance_summary(
    results_df: pd.DataFrame
) -> Dict[str, Dict[str, float]]:
    """Aggregate variance metrics per condition."""
    ...

def save_results(
    results_df: pd.DataFrame,
    variance_summary: Dict,
    gate_result: Dict,
    config: ExperimentConfig
) -> None:
    """Save experiment logs, variance summary, gate result."""
    ...

def main() -> None:
    """Entry point: orchestrate full experiment workflow."""
    ...
```

---

## Data Flow

```
1. Config Loading → ExperimentConfig
2. For each (dataset, architecture, seed):
   a. set_seed_deterministic(seed)
   b. load_dataset(dataset, seed) → train_loader, test_loader
   c. create_model(architecture) → model
   d. train_model(model, train_loader, epochs=10)
   e. evaluate_model(model, test_loader) → test_accuracy
   f. Save to experiment_logs.csv
3. Aggregate results → variance_summary.json
4. Check gate condition → gate_result.json
5. Generate 5 figures → figures/
```

---

## Implementation Details

### Determinism Protocol

```python
def set_seed_deterministic(seed: int) -> None:
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
```

### Dataset Loading

```python
# MNIST normalization
transforms.Normalize((0.1307,), (0.3081,))

# Fashion-MNIST normalization
transforms.Normalize((0.5,), (0.5,))

# Deterministic DataLoader
g = torch.Generator()
g.manual_seed(seed)
DataLoader(dataset, batch_size=64, shuffle=True, generator=g, num_workers=0)
```

### Model Architectures

**1-Layer MLP:** 784 → 128 (ReLU) → 10 (~196K params)
**2-Layer MLP:** 784 → 256 (ReLU) → 128 (ReLU) → 10 (~400K params)

### Variance Metrics

```python
variance = np.var(test_accuracies, ddof=1)  # Sample variance
std_dev = np.std(test_accuracies, ddof=1)
mean_acc = np.mean(test_accuracies)
cv_percent = (std_dev / mean_acc) * 100
ci_lower, ci_upper = bootstrap_ci(test_accuracies)  # 95% CI
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Configuration Setup | Config dataclasses for 4 conditions, paths, hyperparameters | 6 | Module(2)+Dep(1)+Algo(1)+Int(2) |
| A-2 | Data Loading | MNIST/Fashion-MNIST loaders with deterministic generators | 9 | Module(3)+Dep(2)+Algo(2)+Int(2) |
| A-3 | Model Implementation | 1-layer and 2-layer MLP classes | 7 | Module(3)+Dep(1)+Algo(2)+Int(1) |
| A-4 | Training Logic | Deterministic training loop with SGD optimizer | 11 | Module(3)+Dep(3)+Algo(3)+Int(2) |
| A-5 | Evaluation & Metrics | Test accuracy calculation and variance statistics | 10 | Module(3)+Dep(2)+Algo(3)+Int(2) |
| A-6 | Experiment Orchestration | 120-run sequential executor with logging | 14 | Module(4)+Dep(4)+Algo(3)+Int(3) |
| A-7 | Visualization | 5 required figures (gate metrics, variance, distributions, CV, ranges) | 12 | Module(3)+Dep(3)+Algo(3)+Int(3) |
| A-8 | Gate Validation | Check MUST_WORK condition and save gate_result.json | 8 | Module(2)+Dep(2)+Algo(2)+Int(2) |

**Distribution:**
- VeryHigh(18-20): []
- High(14-17): [A-6]
- Medium(9-13): [A-2, A-4, A-5, A-7]
- Low(4-8): [A-1, A-3, A-8]

**Total Complexity:** 77 points across 8 tasks

---

## File Specifications

### results/experiment_logs.csv
```csv
condition,dataset,architecture,seed,test_accuracy,train_time,timestamp
mnist_1layer,mnist,1layer,0,97.45,8.23,2026-03-21T10:00:00
...
```

### results/variance_summary.json
```json
{
  "mnist_1layer": {
    "mean_accuracy": 97.5,
    "variance": 0.42,
    "std_dev": 0.65,
    "cv_percent": 0.67,
    "min_accuracy": 96.8,
    "max_accuracy": 98.2,
    "ci_lower": 0.35,
    "ci_upper": 0.51
  },
  ...
}
```

### results/gate_result.json
```json
{
  "gate_type": "MUST_WORK",
  "threshold": 0.3,
  "conditions_passed": 3,
  "gate_result": "PASS",
  "details": {
    "mnist_1layer": {"variance": 0.42, "passed": true},
    ...
  }
}
```

---

## Validation Criteria

**Code Correctness:**
- All 120 experiments complete without errors
- Identical seed produces identical accuracy (tolerance ≤ 0.01%)

**Gate Validation:**
- σ² ≥ 0.3% for ≥2 out of 4 conditions → PASS
- Otherwise → FAIL (abandon verification plan)

**Performance:**
- Each experiment completes in <30 seconds
- Total runtime <60 minutes (120 experiments)

**Outputs:**
- 3 JSON/CSV files in results/
- 5 PNG figures in figures/
- All required metrics present

---

## Risk Mitigation

**R-1: Gate Failure Risk**
- Mitigation: Dual-dataset (MNIST + Fashion-MNIST) and dual-architecture (1L + 2L) provide 4 independent chances
- Expectation: Fashion-MNIST has higher variance than MNIST, 2L has higher variance than 1L

**R-2: Non-Determinism**
- Mitigation: Comprehensive seed setting, CUDA workspace config, num_workers=0
- Validation: Re-run seed=0 for all 4 conditions, verify accuracy match

**R-3: Performance Baseline Mismatch**
- Expected ranges: MNIST 97-98%, Fashion-MNIST 85-90%
- Mitigation: Use proven hyperparameters (lr=0.01, momentum=0.9, epochs=10)

---

## Dependencies

**Python Libraries:**
- torch >= 1.10.0
- torchvision >= 0.11.0
- numpy >= 1.21.0
- scipy >= 1.7.0
- matplotlib >= 3.4.0
- pandas >= 1.3.0

**System:**
- Python >= 3.8
- CUDA >= 10.2 (optional)
- Single GPU with 2GB memory (recommended)

**Environment:**
- CUDA_VISIBLE_DEVICES: Set to empty GPU
- CUBLAS_WORKSPACE_CONFIG: `:4096:8`

---

**Architecture Complexity:** LOW (EXISTENCE PoC)
**Total Epic Tasks:** 8
**Expected Implementation Time:** Phase 4 (1-2 days for 120 experiments)
**Next Phase:** Phase 4 (Coding and Experimentation)
