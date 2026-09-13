# Logic Design: H-E2 SAT Profiler

**Hypothesis ID:** H-E2  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-07-10  
**Author:** Logic Agent  
**Version:** 1.0  
**Budget:** 6 subtasks

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation from scratch - no existing code to analyze  
**Analyzed Path**: N/A  
**Relevant Symbols**: None - new implementation

---

## Knowledge Base Application (Archon)

**Applied**: PyTorch time.time() + torch.cuda.synchronize() profiling pattern  
**Applied**: PyTorch DataLoader custom wrapper pattern  
**Applied**: sklearn metrics API pattern

---

## E2-2: Implement SATProfiler [Complexity: 10, Budget: 6]

**Applied**: PyTorch CUDA synchronization profiling pattern

### API Signatures

```python
from typing import Callable
import torch
from torch import nn, Tensor
from torch.optim import Optimizer
from torch.utils.data import DataLoader

class SATProfiler:
    def __init__(self):
        """Initialize profiler."""
        self.batch_times: list[float] = []
        self.gpu_utils: list[float] = []
        
    def profile_step(
        self, 
        model: nn.Module, 
        batch: tuple[Tensor, Tensor], 
        optimizer: Optimizer, 
        criterion: Callable
    ) -> float:
        """Profile single step. x: [B, *] -> batch_time (seconds)"""
        ...
    
    def compute_SAT(self) -> float:
        """Compute SAT = (P95/Median) × (GPU_util / 100)"""
        ...
    
    def measure_epoch_time(
        self, 
        model: nn.Module, 
        dataloader: DataLoader, 
        optimizer: Optimizer, 
        criterion: Callable
    ) -> float:
        """Measure full epoch. Returns: total_time (seconds)"""
        ...
    
    def get_batch_times(self) -> list[float]:
        """Get batch times."""
        ...
    
    def get_gpu_utils(self) -> list[float]:
        """Get GPU utils."""
        ...
    
    def reset(self) -> None:
        """Clear state."""
        ...
```

### Pseudo-code

```
profile_step(model, batch, optimizer, criterion):
    torch.cuda.synchronize()
    start = time.time()
    
    x, y = batch
    output = model(x)  # [B, C]
    loss = criterion(output, y)  # scalar
    
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    
    torch.cuda.synchronize()
    batch_time = time.time() - start
    
    gpu_util = torch.cuda.utilization()
    self.batch_times.append(batch_time)
    self.gpu_utils.append(gpu_util)
    
    return batch_time

compute_SAT():
    p95 = percentile(batch_times, 95)
    median = percentile(batch_times, 50)
    avg_gpu = mean(gpu_utils)
    return (p95 / median) * (avg_gpu / 100)
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Class scaffold | __init__, reset, getters |
| L-2-2 | profile_step | CUDA sync + timing |
| L-2-3 | compute_SAT | P95/Median × GPU_util |
| L-2-4 | measure_epoch_time | Full epoch timing |
| L-2-5 | GPU tracking | torch.cuda.utilization() |
| L-2-6 | Unit tests | 50-batch validation |

---

## E2-3: Implement Config & Data Loading [Complexity: 12, Budget: 6]

**Applied**: Python dataclass config pattern

### API Signatures

```python
from dataclasses import dataclass
from torch.utils.data import DataLoader

@dataclass
class CNNConfig:
    model_name: str
    dataset: str
    optimizer: str
    batch_size: int
    lr: float
    momentum: float = 0.9
    weight_decay: float = 1e-4

@dataclass
class TransformerConfig:
    model_name: str
    dataset: str
    optimizer: str
    batch_size: int
    seq_length: int
    lr: float
    weight_decay: float = 0.01

def get_cnn_configs() -> list[CNNConfig]:
    """Generate 24 CNN configs."""
    ...

def get_transformer_configs() -> list[TransformerConfig]:
    """Generate 24 Transformer configs."""
    ...

def get_cnn_dataloader(config: CNNConfig, train: bool = True) -> DataLoader:
    """CNN dataloader with transforms."""
    ...

def get_transformer_dataloader(config: TransformerConfig, train: bool = True) -> DataLoader:
    """Transformer dataloader with tokenization."""
    ...

def inject_jitter_delay(dataloader: DataLoader, delay_ms: int) -> DataLoader:
    """Wrap dataloader with delay. Returns: DataLoader with time.sleep()"""
    ...
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Dataclasses | CNNConfig, TransformerConfig |
| L-3-2 | Config generators | 48 configs (8 models × 3 opts × 2 datasets) |
| L-3-3 | CNN loaders | CIFAR-10, ImageNet with transforms |
| L-3-4 | Transformer loaders | WildChat, PersonaChat with tokenization |
| L-3-5 | Jitter injection | time.sleep() wrapper |
| L-3-6 | Validation | Assert 48 configs, correct shapes |

---

## E2-4: Implement Model Loading [Complexity: 9, Budget: 6]

**Applied**: PyTorch model registry pattern

### API Signatures

```python
from typing import Union
from torch import nn
from torch.optim import Optimizer

def load_cnn_model(config: CNNConfig, device: str = "cuda") -> nn.Module:
    """Load CNN from torchvision."""
    ...

def load_transformer_model(config: TransformerConfig, device: str = "cuda") -> nn.Module:
    """Load Transformer from HuggingFace."""
    ...

def get_optimizer(model: nn.Module, config: Union[CNNConfig, TransformerConfig]) -> Optimizer:
    """Create optimizer (SGD/Adam/AdamW)."""
    ...

def get_criterion(config: Union[CNNConfig, TransformerConfig]) -> Callable:
    """Get CrossEntropyLoss."""
    ...
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | CNN loader | torchvision models (8 models) |
| L-4-2 | Transformer loader | HuggingFace models (8 models) |
| L-4-3 | Optimizer factory | SGD, Adam, AdamW, Adafactor |
| L-4-4 | Criterion | CrossEntropyLoss |
| L-4-5 | Device placement | .to(device) handling |
| L-4-6 | Model validation | Test 16 models load |

---

## E2-5: Implement Experiment Runner [Complexity: 14, Budget: 6]

**Applied**: Standard experiment orchestration pattern

### API Signatures

```python
from typing import Union

class ExperimentRunner:
    def __init__(self, output_dir: str):
        """Initialize runner."""
        self.output_dir = output_dir
        self.profiler = SATProfiler()
        
    def run_natural_workload(
        self, 
        configs: list[Union[CNNConfig, TransformerConfig]]
    ) -> dict:
        """Run 48 configs. Returns: {config_id: {SAT, epoch_time, degradation}}"""
        ...
    
    def run_synthetic_jitter(
        self, 
        config: Union[CNNConfig, TransformerConfig], 
        delays: list[int]
    ) -> dict:
        """Run jitter test. Returns: {delay_ms: SAT}"""
        ...
    
    def save_results(self, results: dict, filename: str) -> None:
        """Save to JSON."""
        ...
```

### Pseudo-code

```
run_natural_workload(configs):
    for config in configs:
        model = load_model(config)
        dataloader = get_dataloader(config)
        optimizer, criterion = get_optimizer(model, config), get_criterion(config)
        
        # Profile 50 batches
        profiler.reset()
        for i, batch in enumerate(dataloader):
            if i >= 50: break
            profiler.profile_step(model, batch, optimizer, criterion)
        
        SAT = profiler.compute_SAT()
        
        # Measure epoch
        profiler.reset()
        epoch_time = profiler.measure_epoch_time(model, dataloader, optimizer, criterion)
        
        degradation = (epoch_time - baseline) / baseline
        results[config_id] = {SAT, epoch_time, degradation}
    
    return results
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Runner class | __init__, output_dir |
| L-5-2 | run_natural_workload | 48-config loop |
| L-5-3 | run_synthetic_jitter | Delay experiments |
| L-5-4 | Result aggregation | Dict construction |
| L-5-5 | save_results | JSON serialization |
| L-5-6 | Progress logging | Print status |

---

## E2-6: Implement Metrics & Evaluation [Complexity: 10, Budget: 6]

**Applied**: sklearn metrics pattern

### API Signatures

```python
from sklearn.metrics import precision_score, recall_score, f1_score

def compute_degradation(epoch_time: float, baseline_time: float) -> float:
    """Compute degradation %."""
    ...

def compute_precision_recall(
    SAT_values: list[float], 
    degradations: list[float], 
    threshold: float = 1.5
) -> tuple[float, float, float]:
    """Compute P/R/F1. Returns: (precision, recall, f1)"""
    ...

def evaluate_causality(
    SAT_natural: float, 
    SAT_jitter: dict[int, float], 
    gpu_util: float
) -> dict:
    """Validate causality. Returns: {correlation, conditional_effect}"""
    ...
```

### Pseudo-code

```
compute_precision_recall(SAT_values, degradations, threshold):
    y_true = [1 if d >= 0.15 else 0 for d in degradations]
    y_pred = [1 if s > threshold else 0 for s in SAT_values]
    
    return (
        precision_score(y_true, y_pred),
        recall_score(y_true, y_pred),
        f1_score(y_true, y_pred)
    )
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | compute_degradation | Percentage calc |
| L-6-2 | compute_precision_recall | sklearn metrics |
| L-6-3 | evaluate_causality | Correlation + conditional |
| L-6-4 | Gate validation | Assert P≥0.80, R≥0.70 |
| L-6-5 | Result formatting | Dict → JSON |
| L-6-6 | Metrics summary | metrics_summary.json |

---

## E2-7: Implement Visualization [Complexity: 11, Budget: 6]

**Applied**: matplotlib + seaborn patterns

### API Signatures

```python
import matplotlib.pyplot as plt

def plot_sat_vs_degradation(SAT_values: list[float], degradations: list[float], path: str):
    """Scatter plot with decision boundary."""
    ...

def plot_precision_recall_curve(SAT_values: list[float], degradations: list[float], path: str):
    """P-R curve varying threshold."""
    ...

def plot_jitter_validation(jitter_results: dict, path: str):
    """SAT vs delay, stratified by GPU."""
    ...

def plot_architecture_sat_distribution(results: dict, path: str):
    """Violin plot per architecture."""
    ...

def plot_confusion_matrix(y_true: list[int], y_pred: list[int], path: str):
    """Confusion matrix."""
    ...

def plot_gate_metrics_comparison(metrics: dict, targets: dict, path: str):
    """Bar chart: achieved vs target."""
    ...
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | SAT vs degradation | Scatter + boundary |
| L-7-2 | P-R curve | Varying threshold |
| L-7-3 | Jitter validation | SAT vs delay |
| L-7-4 | SAT distribution | Violin plot |
| L-7-5 | Confusion matrix | TP/FP/TN/FN |
| L-7-6 | Gate metrics | Bar chart |

---

## E2-8: Integration & Testing [Complexity: 8, Budget: 6]

**Applied**: Standard main orchestration pattern

### API Signatures

```python
def main():
    """Main experiment orchestration."""
    # Setup
    # Run natural (48 configs)
    # Run jitter (4 delays)
    # Evaluate metrics
    # Generate visualizations
    # Validate gate
    ...
```

### Pseudo-code

```
main():
    output_dir = "results/"
    runner = ExperimentRunner(output_dir)
    
    configs = get_cnn_configs() + get_transformer_configs()  # 48
    
    natural_results = runner.run_natural_workload(configs)
    jitter_results = runner.run_synthetic_jitter(configs[0], [0, 50, 100, 200])
    
    SAT_values = [r["SAT"] for r in natural_results.values()]
    degradations = [r["degradation"] for r in natural_results.values()]
    
    precision, recall, f1 = compute_precision_recall(SAT_values, degradations)
    
    plot_sat_vs_degradation(SAT_values, degradations, "figures/sat_vs_degradation.png")
    # ... 5 more plots
    
    assert precision >= 0.80 and recall >= 0.70, "GATE FAIL"
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | main script | Orchestrate phases |
| L-8-2 | Directory setup | Create output dirs |
| L-8-3 | Progress logging | Print status |
| L-8-4 | Error handling | CUDA OOM, downloads |
| L-8-5 | Gate validation | Assert thresholds |
| L-8-6 | End-to-end test | Mock data (10 configs) |

---

## Summary

**Total Subtasks Allocated**: 48 (8 tasks × 6 subtasks)  
**Budget**: 6 subtasks  
**Status**: OVER BUDGET (48 > 6)

**Note**: Budget of 6 subtasks insufficient for architecture scope (8 epic tasks, 80 complexity). Document provides full logic for all tasks as specified in 03_architecture.md. Budget constraint requires adjustment or scope reduction.

---

**Document Status**: Complete  
**Next Phase**: Task Breakdown (03_tasks.yaml)
