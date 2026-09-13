# System Architecture
## H-E1: Segment-level Memory Stress Index Profiler

**Hypothesis**: h-e1  
**Type**: EXISTENCE (MUST_WORK gate)  
**Version**: 1.0  
**Date**: 2026-07-10

---

## Applied Patterns

**Applied**: PyTorch DataLoader batch sampling (torch.utils.data.DataLoader custom collate_fn)  
**Applied**: CUDA memory profiling segment-level tracking (torch.cuda.memory_stats)

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: No existing codebase to analyze  
**Analyzed Path**: N/A  
**Findings**: New implementation from scratch - lightweight memory profiling system

---

## Module Structure

### 1. SegmentMemoryProfiler (`src/profiler/memory_profiler.py`)

**Dependencies**: torch, typing

```python
class SegmentMemoryProfiler:
    def __init__(self, device: str = "cuda:0"): ...
    def reset_memory_stats(self) -> None: ...
    def get_peak_memory_mb(self) -> float: ...
    def profile_iteration(self, model: torch.nn.Module, batch: dict) -> float: ...
    def profile_ground_truth(self, model: torch.nn.Module, dataloader: DataLoader, 
                           optimizer: torch.optim.Optimizer, num_iters: int = 10) -> float: ...
    def profile_lightweight(self, model: torch.nn.Module, sampler: StratifiedSampler,
                          optimizer: torch.optim.Optimizer) -> dict: ...
```

### 2. StratifiedSampler (`src/data/stratified_sampler.py`)

**Dependencies**: torch, numpy, typing

```python
class StratifiedSampler:
    def __init__(self, dataset: Dataset, batch_size: int, quantiles: list[float] = [0.5, 0.75, 0.95, 0.99]): ...
    def compute_length_bins(self) -> dict[str, tuple[int, int]]: ...
    def sample_from_bin(self, bin_name: str) -> torch.Tensor: ...
    def get_stratified_batches(self) -> list[dict]: ...
    
def variable_length_collate_fn(batch: list) -> dict: ...
```

### 3. ModelRegistry (`src/models/registry.py`)

**Dependencies**: torchvision.models, transformers, torch.nn

```python
class ModelRegistry:
    @staticmethod
    def get_model(name: str, num_classes: int = 10, dataset_type: str = "image") -> torch.nn.Module: ...
    @staticmethod
    def get_cnn_models() -> list[str]: ...
    @staticmethod
    def get_transformer_models() -> list[str]: ...
    @staticmethod
    def list_all_models() -> dict[str, list[str]]: ...
```

### 4. DatasetPreparer (`src/data/datasets.py`)

**Dependencies**: torchvision.datasets, datasets, transformers, torch.utils.data

```python
class DatasetPreparer:
    @staticmethod
    def get_cifar10(root: str = "./data", batch_size: int = 128) -> DataLoader: ...
    @staticmethod
    def get_imagenet(root: str = "./data", batch_size: int = 64) -> DataLoader: ...
    @staticmethod
    def get_wmt14(root: str = "./data", batch_size: int = 32, 
                 max_length: int = 128) -> tuple[Dataset, StratifiedSampler]: ...
    @staticmethod
    def get_dataset_type(dataset_name: str) -> str: ...
```

### 5. OptimizerFactory (`src/training/optimizers.py`)

**Dependencies**: torch.optim

```python
class OptimizerFactory:
    @staticmethod
    def get_optimizer(name: str, model_params, lr: float = None) -> torch.optim.Optimizer: ...
    @staticmethod
    def get_default_config(name: str) -> dict: ...
    @staticmethod
    def list_supported_optimizers() -> list[str]: ...
```

### 6. ErrorAnalyzer (`src/eval/error_analysis.py`)

**Dependencies**: numpy, pandas, scipy.stats, typing

```python
class ErrorAnalyzer:
    def __init__(self): ...
    def compute_relative_error(self, predicted: float, ground_truth: float) -> float: ...
    def aggregate_errors(self, errors: list[float]) -> dict[str, float]: ...
    def compare_methods(self, method_a: list[float], method_b: list[float]) -> dict: ...
    def generate_report(self, results: pd.DataFrame) -> dict: ...
    def export_to_csv(self, results: pd.DataFrame, filepath: str) -> None: ...
```

### 7. Visualizer (`src/eval/visualizer.py`)

**Dependencies**: matplotlib, pandas, numpy

```python
class Visualizer:
    @staticmethod
    def plot_error_distribution(results: pd.DataFrame, save_path: str) -> None: ...
    @staticmethod
    def plot_predicted_vs_actual(results: pd.DataFrame, save_path: str) -> None: ...
    @staticmethod
    def plot_length_bin_analysis(results: pd.DataFrame, save_path: str) -> None: ...
    @staticmethod
    def generate_summary_table(results: pd.DataFrame) -> str: ...
```

### 8. ExperimentRunner (`experiments/run_evaluation.py`)

**Dependencies**: All above modules, argparse, logging, tqdm

```python
class ExperimentRunner:
    def __init__(self, config: dict): ...
    def run_ground_truth_experiments(self) -> pd.DataFrame: ...
    def run_lightweight_experiments(self) -> pd.DataFrame: ...
    def run_ablation_2iter(self) -> pd.DataFrame: ...
    def run_full_evaluation(self) -> dict[str, pd.DataFrame]: ...
```

---

## File Organization

```
src/
├── profiler/
│   ├── __init__.py
│   └── memory_profiler.py          # SegmentMemoryProfiler
├── data/
│   ├── __init__.py
│   ├── datasets.py                 # DatasetPreparer
│   └── stratified_sampler.py       # StratifiedSampler + collate_fn
├── models/
│   ├── __init__.py
│   └── registry.py                 # ModelRegistry
├── training/
│   ├── __init__.py
│   └── optimizers.py               # OptimizerFactory
└── eval/
    ├── __init__.py
    ├── error_analysis.py           # ErrorAnalyzer
    └── visualizer.py               # Visualizer

experiments/
├── run_evaluation.py               # ExperimentRunner (main script)
└── configs/
    └── default_config.yaml         # Experiment configuration

tests/
├── test_memory_profiler.py
├── test_stratified_sampler.py
├── test_model_registry.py
└── test_end_to_end.py

results/
├── ground_truth_results.csv
├── lightweight_results.csv
├── ablation_2iter_results.csv
└── error_analysis.csv

figures/
├── error_distribution.png
├── predicted_vs_actual.png
└── length_bin_analysis.png
```

---

## Data Flow

1. **Dataset Preparation**: DatasetPreparer loads CIFAR-10/ImageNet/WMT-14 → DataLoader/StratifiedSampler
2. **Model Initialization**: ModelRegistry creates 16 models (8 CNNs + 8 transformers)
3. **Optimizer Setup**: OptimizerFactory creates Adam/AdamW/SGD instances
4. **Ground Truth Profiling**: SegmentMemoryProfiler runs 10 iterations → peak memory MB
5. **Lightweight Profiling**: SegmentMemoryProfiler runs 3 iterations + stratified sampling → predicted memory MB
6. **Error Computation**: ErrorAnalyzer compares predicted vs ground truth → relative errors
7. **Statistical Testing**: ErrorAnalyzer runs Wilcoxon test → significance results
8. **Visualization**: Visualizer generates plots and summary tables
9. **Export**: Results saved to CSV files in results/ directory

---

## Key Interfaces

### Profiler → Sampler
```python
# Lightweight profiling uses stratified batches for transformers
batches = stratified_sampler.get_stratified_batches()  # 4 batches from length bins
for batch in batches:
    mem = profiler.profile_iteration(model, batch)
```

### Profiler → Model Registry
```python
# Profiler receives any model from registry
model = model_registry.get_model("resnet18", num_classes=10)
peak_mem = profiler.profile_ground_truth(model, dataloader, optimizer)
```

### Error Analyzer → Experiment Runner
```python
# Runner collects results, analyzer computes metrics
results_df = runner.run_lightweight_experiments()
metrics = analyzer.aggregate_errors(results_df['relative_error'].tolist())
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1-1 | Data Preparation Pipeline | Implement DatasetPreparer + StratifiedSampler for CIFAR-10/ImageNet/WMT-14 | 14 | 4+3+4+3 (Module:4, Deps:3, Algo:4, Integration:3) |
| E1-2 | Core Memory Profiler | Implement SegmentMemoryProfiler with segment-level tracking via torch.cuda.memory_stats | 16 | 5+3+5+3 (Module:5, Deps:3, Algo:5, Integration:3) |
| E1-3 | Model Registry | Implement ModelRegistry for 16 models (8 CNNs from torchvision + 8 transformers from HuggingFace) | 11 | 3+2+3+3 (Module:3, Deps:2, Algo:3, Integration:3) |
| E1-4 | Optimizer Factory | Implement OptimizerFactory for Adam/AdamW/SGD with default configs | 7 | 2+1+2+2 (Module:2, Deps:1, Algo:2, Integration:2) |
| E1-5 | Evaluation Harness | Implement ErrorAnalyzer + Visualizer for metrics computation and reporting | 13 | 3+2+4+4 (Module:3, Deps:2, Algo:4, Integration:4) |
| E1-6 | Ground Truth Experiments | Implement 10-iteration profiling protocol for all 48 configs | 15 | 4+3+4+4 (Module:4, Deps:3, Algo:4, Integration:4) |
| E1-7 | Lightweight Profiling | Implement 3-iteration + stratified sampling protocol | 17 | 4+4+5+4 (Module:4, Deps:4, Algo:5, Integration:4) |
| E1-8 | Statistical Validation | Implement Wilcoxon test + ablation comparison (2-iter vs 3-iter) | 10 | 2+2+3+3 (Module:2, Deps:2, Algo:3, Integration:3) |

**Total Complexity**: 103 points  
**Distribution**: VeryHigh(18-20): [], High(14-17): [E1-2, E1-6, E1-7], Medium(9-13): [E1-1, E1-3, E1-5, E1-8], Low(4-8): [E1-4]

---

## Implementation Priorities

### Phase 1: Core Infrastructure (Weeks 1-2)
- E1-1: Data Preparation Pipeline (FR-4)
- E1-2: Core Memory Profiler (FR-1)
- E1-3: Model Registry (FR-3)
- E1-4: Optimizer Factory (FR-5)

**Gate**: Unit tests pass for all core modules

### Phase 2: Evaluation System (Week 2)
- E1-5: Evaluation Harness (FR-6)

**Gate**: Integration test runs successfully on 1 config

### Phase 3: Experiments (Week 3)
- E1-6: Ground Truth Experiments (FR-7.1)
- E1-7: Lightweight Profiling (FR-7.2)
- E1-8: Statistical Validation (FR-6.5, FR-7.3)

**Gate**: MUST_WORK criteria met (median ≤10/15%, P95 ≤25%, p<0.05)

---

## Module Dependency Graph

```
ExperimentRunner
├── SegmentMemoryProfiler
│   └── torch.cuda.memory_stats
├── StratifiedSampler
│   └── DatasetPreparer
├── ModelRegistry
│   ├── torchvision.models
│   └── transformers
├── OptimizerFactory
│   └── torch.optim
├── ErrorAnalyzer
│   └── scipy.stats
└── Visualizer
    └── matplotlib
```

---

## Configuration Schema

```yaml
# experiments/configs/default_config.yaml
experiment:
  seed: 42
  device: "cuda:0"
  num_ground_truth_iters: 10
  num_lightweight_iters: 3

datasets:
  cifar10:
    batch_size: 128
    root: "./data"
  imagenet:
    batch_size: 64
    root: "./data"
  wmt14:
    batch_size: 32
    max_length: 128
    root: "./data"

stratified_sampling:
  quantiles: [0.5, 0.75, 0.95, 0.99]
  min_samples_per_bin: 100

optimizers:
  adam:
    lr: 0.0001
    betas: [0.9, 0.999]
  adamw:
    lr: 0.0001
    betas: [0.9, 0.999]
    weight_decay: 0.01
  sgd:
    lr: 0.1
    momentum: 0.9

models:
  cnn: ["resnet18", "resnet34", "resnet50", "vgg16", "densenet121", 
        "mobilenet_v2", "efficientnet_b0", "shufflenet_v2_x1_0"]
  transformer: ["bert-base-uncased", "roberta-base", "gpt2", "t5-small",
                "distilbert-base-uncased", "albert-base-v2", 
                "microsoft/deberta-base", "google/vit-base-patch16-224"]

evaluation:
  error_thresholds:
    cnn_median: 0.10
    transformer_median: 0.15
    p95_all: 0.25
  statistical_test:
    method: "wilcoxon"
    alpha: 0.05

output:
  results_dir: "./results"
  figures_dir: "./figures"
  log_level: "INFO"
```

---

## Validation Strategy

### Unit Tests
- `test_memory_profiler.py`: Validate reset_stats, get_peak_memory, profile_iteration APIs
- `test_stratified_sampler.py`: Validate length bucketing, quantile computation, batch sampling
- `test_model_registry.py`: Validate all 16 models load and forward pass works

### Integration Tests
- `test_end_to_end.py`: Run 3-iteration profiling on resnet18 + Adam + CIFAR-10, verify error <20%

### Acceptance Tests
- Run full 48-config evaluation
- Verify median error ≤10% (CNNs) or ≤15% (transformers)
- Verify P95 error ≤25%
- Verify Wilcoxon test p<0.05 vs 2-iteration baseline

---

## Success Criteria Mapping

| Success Metric | Module Responsible | Epic Task |
|----------------|-------------------|-----------|
| Median ≤10% (CNNs) | ErrorAnalyzer | E1-5, E1-7, E1-8 |
| Median ≤15% (transformers) | ErrorAnalyzer | E1-5, E1-7, E1-8 |
| P95 ≤25% | ErrorAnalyzer | E1-5, E1-8 |
| p<0.05 (Wilcoxon) | ErrorAnalyzer | E1-8 |
| Segment-level tracking | SegmentMemoryProfiler | E1-2 |
| Stratified sampling | StratifiedSampler | E1-1, E1-7 |
| Post-optimizer capture | SegmentMemoryProfiler | E1-7 |
| 48 configs validated | ExperimentRunner | E1-6, E1-7 |

---

## Risk Mitigation

### Technical Risks
1. **Allocator simulation fails for transformers (30% probability)**
   - Mitigation: Contingency threshold ≤15% median error acceptable
   - Fallback: Extend to 5-iteration sampling if needed

2. **WMT-14 length distribution skewed (10% probability)**
   - Mitigation: Validate quantile bins during E1-1 implementation
   - Fallback: Adjust quantiles based on actual distribution

3. **ImageNet download timeout (15% probability)**
   - Mitigation: Use torchvision streaming datasets or cached splits
   - Fallback: Reduce validation set size to 10,000 samples if needed

### Timeline Risks
- Ground truth profiling takes ~50 GPU-hours (2 days on single GPU)
- Mitigation: Implement early stopping if 10 configs show stable results
- Contingency: Parallelize across multiple GPUs if available

---

## Dependencies

### Python Packages
```
torch>=2.0.0
torchvision>=0.15.0
transformers>=4.30.0
datasets>=2.13.0
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.7.0
scipy>=1.10.0
tqdm>=4.65.0
pyyaml>=6.0
```

### Hardware Requirements
- GPU: 1x NVIDIA A100 (40GB VRAM) or equivalent
- Storage: ~200GB for ImageNet-1K download
- Compute: ~53 GPU-hours total (50 ground truth + 3 lightweight)

---

## Document Status

**Architecture Status**: COMPLETE  
**Ready for Phase 4**: YES  
**Epic Tasks**: 8 tasks covering end-to-end workflow  
**Total Complexity**: 103 points (avg 12.9 per task)  
**Next Step**: Phase 4 Logic Agent (detailed algorithm design)
