# System Architecture: H-E2 SAT Profiler

**Hypothesis ID:** H-E2  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-07-10  
**Author:** Architecture Agent  
**Version:** 1.0  

---

## Knowledge Base Application

Applied: PyTorch Design Philosophy (modular components, imperative execution)

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation from scratch  
**Analyzed Path**: N/A  
**Findings**: No existing code to analyze - implementing new profiling system

---

## Module Structure

### SATProfiler (`src/profiling/profiler.py`)

**Dependencies**: None (core profiling module)

```python
class SATProfiler:
    def __init__(self): ...
    def profile_step(self, model: nn.Module, batch: tuple, optimizer: Optimizer, criterion: Callable) -> float: ...
    def compute_SAT(self) -> float: ...
    def measure_epoch_time(self, model: nn.Module, dataloader: DataLoader, optimizer: Optimizer, criterion: Callable) -> float: ...
    def get_batch_times(self) -> list[float]: ...
    def get_gpu_utils(self) -> list[float]: ...
    def reset(self) -> None: ...
```

### ConfigManager (`src/config.py`)

**Dependencies**: None

```python
@dataclass
class CNNConfig:
    model_name: str
    dataset: str
    optimizer: str
    batch_size: int
    lr: float
    momentum: float
    weight_decay: float

@dataclass
class TransformerConfig:
    model_name: str
    dataset: str
    optimizer: str
    batch_size: int
    seq_length: int
    lr: float
    weight_decay: float

def get_cnn_configs() -> list[CNNConfig]: ...
def get_transformer_configs() -> list[TransformerConfig]: ...
```

### DataLoader (`src/data/loader.py`)

**Dependencies**: ConfigManager

```python
def get_cnn_dataloader(config: CNNConfig, train: bool = True) -> DataLoader: ...
def get_transformer_dataloader(config: TransformerConfig, train: bool = True) -> DataLoader: ...
def inject_jitter_delay(dataloader: DataLoader, delay_ms: int) -> DataLoader: ...
```

### ModelLoader (`src/models/loader.py`)

**Dependencies**: ConfigManager

```python
def load_cnn_model(config: CNNConfig, device: str = "cuda") -> nn.Module: ...
def load_transformer_model(config: TransformerConfig, device: str = "cuda") -> nn.Module: ...
def get_optimizer(model: nn.Module, config: Union[CNNConfig, TransformerConfig]) -> Optimizer: ...
def get_criterion(config: Union[CNNConfig, TransformerConfig]) -> Callable: ...
```

### ExperimentRunner (`src/experiment/runner.py`)

**Dependencies**: SATProfiler, DataLoader, ModelLoader, ConfigManager

```python
class ExperimentRunner:
    def __init__(self, output_dir: str): ...
    def run_natural_workload(self, configs: list[Union[CNNConfig, TransformerConfig]]) -> dict: ...
    def run_synthetic_jitter(self, config: Union[CNNConfig, TransformerConfig], delays: list[int]) -> dict: ...
    def save_results(self, results: dict, filename: str) -> None: ...
```

### MetricsEvaluator (`src/evaluation/metrics.py`)

**Dependencies**: None

```python
def compute_degradation(epoch_time: float, baseline_time: float) -> float: ...
def compute_precision_recall(SAT_values: list[float], degradations: list[float], threshold: float = 1.5) -> tuple[float, float, float]: ...
def evaluate_causality(SAT_natural: float, SAT_jitter: dict[int, float], gpu_util: float) -> dict: ...
```

### Visualizer (`src/visualization/plotter.py`)

**Dependencies**: MetricsEvaluator

```python
def plot_sat_vs_degradation(SAT_values: list[float], degradations: list[float], output_path: str) -> None: ...
def plot_precision_recall_curve(SAT_values: list[float], degradations: list[float], output_path: str) -> None: ...
def plot_jitter_validation(jitter_results: dict, output_path: str) -> None: ...
def plot_architecture_sat_distribution(results: dict, output_path: str) -> None: ...
def plot_confusion_matrix(y_true: list[int], y_pred: list[int], output_path: str) -> None: ...
def plot_gate_metrics_comparison(metrics: dict, targets: dict, output_path: str) -> None: ...
```

### Main (`src/main.py`)

**Dependencies**: All modules

```python
def main():
    # Setup
    # Run natural workload experiments (48 configs)
    # Run synthetic jitter experiments
    # Evaluate metrics
    # Generate visualizations
    # Save results
    ...
```

---

## File Organization

```
docs/youra_research/h-e2/
├── code/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── main.py
│   │   ├── profiling/
│   │   │   ├── __init__.py
│   │   │   └── profiler.py
│   │   ├── data/
│   │   │   ├── __init__.py
│   │   │   └── loader.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── loader.py
│   │   ├── experiment/
│   │   │   ├── __init__.py
│   │   │   └── runner.py
│   │   ├── evaluation/
│   │   │   ├── __init__.py
│   │   │   └── metrics.py
│   │   └── visualization/
│   │       ├── __init__.py
│   │       └── plotter.py
│   ├── requirements.txt
│   └── README.md
├── data/
│   ├── cifar10/
│   ├── imagenet/
│   ├── wildchat/
│   └── personachat/
├── results/
│   ├── profiling_results.json
│   └── metrics_summary.json
└── figures/
    ├── sat_vs_degradation.png
    ├── precision_recall_curve.png
    ├── jitter_validation.png
    ├── architecture_sat_dist.png
    ├── confusion_matrix.png
    └── gate_metrics_comparison.png
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E2-1 | Setup Infrastructure | Project structure, requirements.txt, data directories | 6 | Module(2) + Deps(1) + Algo(1) + Integ(2) |
| E2-2 | Implement SATProfiler | Core profiling class with batch timing and GPU util measurement | 10 | Module(3) + Deps(2) + Algo(3) + Integ(2) |
| E2-3 | Implement Config & Data Loading | Config management for 48 configs, dataset loaders, jitter injection | 12 | Module(3) + Deps(3) + Algo(3) + Integ(3) |
| E2-4 | Implement Model Loading | Load 16 models (CNNs + Transformers), optimizers, criteria | 9 | Module(3) + Deps(2) + Algo(2) + Integ(2) |
| E2-5 | Implement Experiment Runner | Natural workload + synthetic jitter experiments | 14 | Module(4) + Deps(3) + Algo(4) + Integ(3) |
| E2-6 | Implement Metrics & Evaluation | Precision/Recall/F1, degradation computation, causality analysis | 10 | Module(3) + Deps(2) + Algo(3) + Integ(2) |
| E2-7 | Implement Visualization | 6 required plots (SAT scatter, P-R curve, jitter, dist, confusion, gate) | 11 | Module(3) + Deps(2) + Algo(3) + Integ(3) |
| E2-8 | Integration & Testing | Main script, end-to-end execution, result validation | 8 | Module(2) + Deps(2) + Algo(2) + Integ(2) |

**Distribution**: VeryHigh(18-20): [], High(14-17): [E2-5], Medium(9-13): [E2-2, E2-3, E2-4, E2-6, E2-7], Low(4-8): [E2-1, E2-8]

**Total Complexity**: 80 (8 tasks, avg 10 per task)

---

## Dependencies

### External Libraries
```
torch>=2.0.0
torchvision>=0.15.0
transformers>=4.30.0
datasets>=2.14.0
numpy>=1.24.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

### Hardware Requirements
- NVIDIA GPU with CUDA 11.8+
- 16GB GPU memory minimum
- 100GB disk space

---

## Key Design Decisions

1. **Minimal PoC Architecture**: Single profiler class, flat config structure (no complex experiment management)
2. **Profiling Strategy**: torch.cuda.synchronize() + time.time() (fallback to torch.profiler if needed)
3. **Config Management**: Dataclass-based configs for type safety and clarity
4. **Jitter Injection**: Custom DataLoader wrapper with time.sleep() for causality validation

---

## Validation Checkpoints

1. **Module Interface Check**: All modules import successfully
2. **Profiler Activation**: batch_times list length = 50 after profiling
3. **Causality Check**: SAT_jitter > SAT_natural for all delay levels
4. **Metrics Gate**: Precision ≥0.80 AND Recall ≥0.70

---

**Document Status**: Complete  
**Next Phase**: Logic Design (03_logic.md)
