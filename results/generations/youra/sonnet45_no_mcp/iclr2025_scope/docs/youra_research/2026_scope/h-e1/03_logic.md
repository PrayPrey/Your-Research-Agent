# Logic Design: h-e1

**Date:** 2026-04-19
**Hypothesis:** EXISTENCE - LoRA Rank Pareto Frontier
**Type:** PoC (Proof-of-Concept)
**Author:** Logic Agent

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field project - designing new APIs
**Analyzed Path:** N/A
**Relevant Symbols:** None - new implementation

---

## Applied Knowledge (Archon KB)

**Applied:** PyTorch LoRA adapter pattern (standard low-rank decomposition)
**Applied:** Multi-task training loop pattern (task iteration with separate optimizers)
**Applied:** Pareto frontier evaluation pattern (hypervolume computation)

---

## Core APIs

### A-1: LoRA Adapter Module [Complexity: 2, Budget: Foundation]

**Applied:** Standard LoRA decomposition (A @ B) with scaling

#### API Signatures

```python
class LoRALayer(nn.Module):
    """Low-rank adapter layer for efficient fine-tuning."""
    
    def __init__(
        self,
        in_features: int,
        out_features: int,
        rank: int = 4,
        alpha: float = 16.0,
        dropout: float = 0.1
    ):
        """Initialize LoRA layer.
        
        Args:
            in_features: Input dimension
            out_features: Output dimension
            rank: LoRA rank (4, 8, 16, 32)
            alpha: Scaling factor
            dropout: Dropout probability
        """
        ...
    
    def forward(self, x: Tensor) -> Tensor:
        """Apply LoRA transformation. x: [B, S, in_features] -> [B, S, out_features]"""
        ...


class MultiRankLoRAAdapter:
    """Manages multiple LoRA adapters with different ranks."""
    
    def __init__(
        self,
        base_model: nn.Module,
        ranks: List[int] = [4, 8, 16, 32],
        target_modules: List[str] = ["q_proj", "v_proj"]
    ):
        """Initialize multi-rank adapter manager.
        
        Args:
            base_model: Pretrained model (LLaMA-2-7B)
            ranks: List of ranks to train
            target_modules: Module names to apply LoRA
        """
        ...
    
    def create_adapter(self, rank: int, task_name: str) -> nn.Module:
        """Create LoRA adapter for specific rank and task.
        
        Returns: Model with LoRA adapter attached
        """
        ...
    
    def get_trainable_params(self, model: nn.Module) -> int:
        """Count trainable parameters. Returns: param count"""
        ...
```

#### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| x | [B, S, D] | Input features (batch, seq, hidden_dim=4096) |
| lora_A | [D, r] | Down-projection matrix |
| lora_B | [r, D] | Up-projection matrix |
| out | [B, S, D] | Output = base(x) + (x @ A @ B) * scale |

#### Pseudo-code

```
forward(x):
    1. base_output = frozen_layer(x)  # [B, S, D]
    2. lora_output = (x @ lora_A @ lora_B) * (alpha / rank)  # [B, S, D]
    3. return base_output + lora_output
```

---

### A-2: Multi-Task Training Pipeline [Complexity: 3, Budget: Core]

**Applied:** Task iteration pattern with per-task optimizer state

#### API Signatures

```python
class MultiTaskTrainer:
    """Train LoRA adapters across multiple tasks and ranks."""
    
    def __init__(
        self,
        adapter_manager: MultiRankLoRAAdapter,
        tasks: List[str],
        ranks: List[int] = [4, 8, 16, 32],
        lr: float = 3e-4,
        batch_size: int = 16
    ):
        """Initialize multi-task trainer.
        
        Args:
            adapter_manager: LoRA adapter factory
            tasks: List of task names (17 tasks)
            ranks: Ranks to train per task
            lr: Learning rate
            batch_size: Batch size per GPU
        """
        ...
    
    def train_task_rank(
        self,
        task_name: str,
        rank: int,
        train_loader: DataLoader,
        val_loader: DataLoader,
        epochs: int = 3
    ) -> Dict[str, float]:
        """Train single (task, rank) combination.
        
        Returns: {'accuracy': float, 'loss': float, 'best_epoch': int}
        """
        ...
    
    def train_all(self) -> Dict[str, Dict[int, Dict[str, float]]]:
        """Train all tasks × all ranks (17 × 4 = 68 runs).
        
        Returns: Nested dict {task: {rank: {metric: value}}}
        """
        ...
    
    def save_checkpoint(
        self,
        model: nn.Module,
        task: str,
        rank: int,
        checkpoint_dir: str
    ) -> None:
        """Save adapter weights."""
        ...
```

#### Pseudo-code

```
train_all():
    results = {}
    for task in tasks:  # 17 tasks
        results[task] = {}
        for rank in [4, 8, 16, 32]:
            1. model = adapter_manager.create_adapter(rank, task)
            2. optimizer = AdamW(model.parameters(), lr=3e-4)
            3. scheduler = CosineAnnealingLR(optimizer)
            4. for epoch in range(epochs):
                   train_loss = train_epoch(model, train_loader)
                   val_acc = validate(model, val_loader)
            5. results[task][rank] = {'accuracy': val_acc, ...}
            6. save_checkpoint(model, task, rank)
    return results
```

---

### A-3: Efficiency Metrics Computation [Complexity: 2, Budget: Evaluation]

**Applied:** FLOPs counting pattern (fvcore), parameter counting

#### API Signatures

```python
class EfficiencyMetrics:
    """Compute FLOPs and parameter counts for LoRA adapters."""
    
    def __init__(self, base_model: nn.Module):
        """Initialize metrics calculator."""
        ...
    
    def count_flops(
        self,
        model: nn.Module,
        input_shape: Tuple[int, int, int] = (1, 512, 4096)
    ) -> int:
        """Count FLOPs for forward pass.
        
        Args:
            model: Model with LoRA adapter
            input_shape: (batch, seq_len, hidden_dim)
        
        Returns: Total FLOPs (int)
        """
        ...
    
    def count_parameters(self, model: nn.Module) -> int:
        """Count trainable parameters.
        
        Returns: Number of trainable params
        """
        ...
    
    def compute_all_metrics(
        self,
        model: nn.Module,
        accuracy: float
    ) -> Dict[str, float]:
        """Compute all metrics for a model.
        
        Returns: {'accuracy': float, 'flops': int, 'params': int}
        """
        ...
```

#### Pseudo-code

```
count_flops(model, input_shape):
    1. dummy_input = torch.randn(input_shape)  # [B, S, D]
    2. flops = FlopCountAnalysis(model, dummy_input).total()
    3. return flops

count_parameters(model):
    1. return sum(p.numel() for p in model.parameters() if p.requires_grad)
```

---

### A-4: Oracle Gap Evaluator [Complexity: 3, Budget: Core Metric]

**Applied:** Pareto hypervolume computation (pymoo library)

#### API Signatures

```python
class OracleGapEvaluator:
    """Compute oracle gap between per-task optimal and fixed-rank baselines."""
    
    def __init__(self, ref_point: List[float] = [0.0, 1e12]):
        """Initialize evaluator.
        
        Args:
            ref_point: Reference point for hypervolume [min_acc, max_flops]
        """
        ...
    
    def compute_hypervolume(
        self,
        points: np.ndarray
    ) -> float:
        """Compute hypervolume for Pareto front.
        
        Args:
            points: Array of shape [N, 2] with (accuracy, -flops)
        
        Returns: Hypervolume value
        """
        ...
    
    def compute_oracle_gap(
        self,
        results: Dict[str, Dict[int, Dict[str, float]]]
    ) -> Dict[str, float]:
        """Compute oracle gap from training results.
        
        Args:
            results: {task: {rank: {'accuracy': val, 'flops': val}}}
        
        Returns: {
            'oracle_hv': float,
            'best_fixed_hv': float,
            'oracle_gap': float,
            'oracle_gap_pct': float,
            'best_fixed_rank': int
        }
        """
        ...
    
    def select_per_task_oracle(
        self,
        task_results: Dict[int, Dict[str, float]]
    ) -> Tuple[int, float, int]:
        """Select best rank for a single task.
        
        Args:
            task_results: {rank: {'accuracy': val, 'flops': val}}
        
        Returns: (best_rank, best_accuracy, best_flops)
        """
        ...
```

#### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| points | [N, 2] | Pareto points (accuracy, -flops) |
| ref_point | [2] | Reference for hypervolume |

#### Pseudo-code

```
compute_oracle_gap(results):
    # Step 1: Compute per-task oracle hypervolume
    oracle_points = []
    for task in results:
        best_rank, acc, flops = select_per_task_oracle(results[task])
        oracle_points.append([acc, -flops])
    oracle_hv = compute_hypervolume(oracle_points)
    
    # Step 2: Compute fixed-rank baseline hypervolumes
    fixed_hvs = {}
    for rank in [4, 8, 16, 32]:
        fixed_points = [[results[task][rank]['accuracy'], 
                        -results[task][rank]['flops']] 
                       for task in results]
        fixed_hvs[rank] = compute_hypervolume(fixed_points)
    
    # Step 3: Compute oracle gap
    best_fixed_rank = max(fixed_hvs, key=fixed_hvs.get)
    best_fixed_hv = fixed_hvs[best_fixed_rank]
    oracle_gap = oracle_hv - best_fixed_hv
    oracle_gap_pct = (oracle_gap / best_fixed_hv) * 100
    
    return {
        'oracle_hv': oracle_hv,
        'best_fixed_hv': best_fixed_hv,
        'oracle_gap': oracle_gap,
        'oracle_gap_pct': oracle_gap_pct,
        'best_fixed_rank': best_fixed_rank
    }

select_per_task_oracle(task_results):
    # Select rank with highest accuracy (or best accuracy/flops trade-off)
    best_rank = max(task_results, key=lambda r: task_results[r]['accuracy'])
    return best_rank, task_results[best_rank]['accuracy'], task_results[best_rank]['flops']
```

---

### A-5: Data Pipeline [Complexity: 2, Budget: Foundation]

**Applied:** HuggingFace datasets loading pattern

#### API Signatures

```python
class MultiDomainDataLoader:
    """Load and preprocess GLUE + XTREME tasks."""
    
    def __init__(
        self,
        tokenizer: AutoTokenizer,
        max_length: int = 512,
        batch_size: int = 16
    ):
        """Initialize data loader.
        
        Args:
            tokenizer: LLaMA-2 tokenizer
            max_length: Max sequence length
            batch_size: Batch size
        """
        ...
    
    def load_glue_tasks(self) -> Dict[str, Tuple[DataLoader, DataLoader]]:
        """Load all 9 GLUE tasks.
        
        Returns: {task_name: (train_loader, val_loader)}
        """
        ...
    
    def load_xtreme_tasks(self) -> Dict[str, Tuple[DataLoader, DataLoader]]:
        """Load XTREME tasks (XNLI + PAWS-X, 4 languages each).
        
        Returns: {task_name: (train_loader, val_loader)}
        """
        ...
    
    def get_all_tasks(self) -> Dict[str, Tuple[DataLoader, DataLoader]]:
        """Get all 17 tasks.
        
        Returns: Combined GLUE + XTREME (17 tasks total)
        """
        ...
    
    def preprocess_batch(
        self,
        batch: Dict[str, Any],
        task_type: str = "classification"
    ) -> Dict[str, Tensor]:
        """Tokenize and prepare batch.
        
        Returns: {'input_ids': [B, S], 'attention_mask': [B, S], 'labels': [B]}
        """
        ...
```

#### Pseudo-code

```
load_glue_tasks():
    glue_tasks = ["cola", "sst2", "mrpc", "qqp", "stsb", "mnli", "qnli", "rte", "wnli"]
    loaders = {}
    for task in glue_tasks:
        1. dataset = load_dataset("glue", task)
        2. train_ds = dataset["train"].map(tokenize_function)
        3. val_ds = dataset["validation"].map(tokenize_function)
        4. train_loader = DataLoader(train_ds, batch_size=16, shuffle=True)
        5. val_loader = DataLoader(val_ds, batch_size=16)
        6. loaders[task] = (train_loader, val_loader)
    return loaders
```

---

### A-6: Visualization Pipeline [Complexity: 2, Budget: Analysis]

**Applied:** Matplotlib Pareto front plotting pattern

#### API Signatures

```python
class ExperimentVisualizer:
    """Generate visualization for oracle gap analysis."""
    
    def __init__(self, output_dir: str):
        """Initialize visualizer.
        
        Args:
            output_dir: Directory to save figures
        """
        ...
    
    def plot_pareto_fronts(
        self,
        results: Dict[str, Dict[int, Dict[str, float]]],
        oracle_selections: Dict[str, int]
    ) -> None:
        """Plot per-task Pareto fronts (4×4 grid, 17 subplots).
        
        Saves to: {output_dir}/pareto_fronts.png
        """
        ...
    
    def plot_oracle_vs_fixed(
        self,
        oracle_hv: float,
        fixed_hvs: Dict[int, float],
        oracle_gap_pct: float
    ) -> None:
        """Plot bar chart comparing oracle vs fixed-rank baselines.
        
        Saves to: {output_dir}/oracle_comparison.png
        """
        ...
    
    def plot_rank_selection_heatmap(
        self,
        results: Dict[str, Dict[int, Dict[str, float]]],
        oracle_selections: Dict[str, int]
    ) -> None:
        """Plot heatmap of accuracy across tasks and ranks.
        
        Saves to: {output_dir}/rank_heatmap.png
        """
        ...
    
    def plot_gate_metrics(
        self,
        target_gap: float,
        actual_gap: float
    ) -> None:
        """Plot gate metrics comparison (mandatory figure).
        
        Saves to: {output_dir}/gate_metrics.png
        """
        ...
```

#### Pseudo-code

```
plot_pareto_fronts(results, oracle_selections):
    1. fig, axes = plt.subplots(4, 5, figsize=(20, 16))  # 17 tasks + 3 empty
    2. for idx, task in enumerate(results.keys()):
           ax = axes[idx // 5, idx % 5]
           for rank in [4, 8, 16, 32]:
               acc = results[task][rank]['accuracy']
               flops = results[task][rank]['flops']
               color = 'red' if rank == oracle_selections[task] else 'blue'
               ax.scatter(flops, acc, label=f'r={rank}', color=color)
           ax.set_xlabel('FLOPs (log)')
           ax.set_ylabel('Accuracy')
           ax.set_title(task)
    3. plt.savefig(f'{output_dir}/pareto_fronts.png')
```

---

## Main Experiment Pipeline

**Applied:** Sequential experiment execution pattern

### API Signatures

```python
def run_experiment(
    model_name: str = "meta-llama/Llama-2-7b-hf",
    output_dir: str = "./outputs/h-e1",
    device: str = "cuda:0"
) -> Dict[str, Any]:
    """Run full h-e1 experiment.
    
    Args:
        model_name: HuggingFace model identifier
        output_dir: Output directory for checkpoints and figures
        device: Device to run on
    
    Returns: {
        'results': Dict[task, Dict[rank, metrics]],
        'oracle_gap': float,
        'oracle_gap_pct': float,
        'gate_passed': bool
    }
    """
    ...
```

### Pseudo-code

```
run_experiment():
    # Step 1: Setup
    1. tokenizer = AutoTokenizer.from_pretrained(model_name)
    2. base_model = AutoModelForSequenceClassification.from_pretrained(model_name)
    3. data_loader = MultiDomainDataLoader(tokenizer)
    4. tasks = data_loader.get_all_tasks()  # 17 tasks
    
    # Step 2: Train all adapters (17 tasks × 4 ranks)
    5. adapter_manager = MultiRankLoRAAdapter(base_model, ranks=[4, 8, 16, 32])
    6. trainer = MultiTaskTrainer(adapter_manager, tasks)
    7. results = trainer.train_all()  # 68 training runs
    
    # Step 3: Compute efficiency metrics
    8. metrics_calc = EfficiencyMetrics(base_model)
    9. for task in results:
           for rank in results[task]:
               model = load_checkpoint(task, rank)
               results[task][rank]['flops'] = metrics_calc.count_flops(model)
               results[task][rank]['params'] = metrics_calc.count_parameters(model)
    
    # Step 4: Compute oracle gap
    10. evaluator = OracleGapEvaluator()
    11. oracle_results = evaluator.compute_oracle_gap(results)
    12. oracle_gap_pct = oracle_results['oracle_gap_pct']
    
    # Step 5: Visualization
    13. visualizer = ExperimentVisualizer(output_dir)
    14. visualizer.plot_pareto_fronts(results, oracle_results['oracle_selections'])
    15. visualizer.plot_oracle_vs_fixed(oracle_results['oracle_hv'], 
                                         oracle_results['fixed_hvs'],
                                         oracle_gap_pct)
    16. visualizer.plot_gate_metrics(target_gap=10.0, actual_gap=oracle_gap_pct)
    
    # Step 6: Gate check
    17. gate_passed = oracle_gap_pct >= 10.0
    18. return {
            'results': results,
            'oracle_gap': oracle_results['oracle_gap'],
            'oracle_gap_pct': oracle_gap_pct,
            'gate_passed': gate_passed
        }
```

---

## Subtask Budget Allocation

| ID | Subtask | Complexity | Description |
|----|---------|------------|-------------|
| L-1 | LoRA Layer | 2 | Low-rank adapter implementation |
| L-2 | Multi-Rank Manager | 2 | Adapter creation across ranks |
| L-3 | Training Loop | 3 | Multi-task × multi-rank training |
| L-4 | FLOPs Counter | 2 | Efficiency metrics computation |
| L-5 | Oracle Gap Calculator | 3 | Hypervolume & gap computation |
| L-6 | Data Pipeline | 2 | GLUE + XTREME loading |
| L-7 | Visualization | 2 | Pareto plots & heatmaps |
| L-8 | Main Pipeline | 2 | Experiment orchestration |

**Total Complexity:** 18 subtasks
**Budget Status:** Within PoC scope (EXISTENCE hypothesis)

---

## External Dependencies

### PyTorch Ecosystem
```python
import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader
```

### HuggingFace Libraries
```python
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    TrainingArguments,
    Trainer
)
from datasets import load_dataset
from evaluate import load as load_metric
```

### Efficiency & Metrics
```python
from fvcore.nn import FlopCountAnalysis  # FLOPs counting
from pymoo.indicators.hv import HV  # Hypervolume computation
import numpy as np
```

### Visualization
```python
import matplotlib.pyplot as plt
import seaborn as sns
```

---

## PoC Success Criteria

**Pass Conditions:**
1. Code runs without error (all 68 training runs complete)
2. Oracle gap G_o ≥ 10% (oracle_gap_pct >= 10.0)

**No Statistical Tests Required:** EXISTENCE hypothesis only validates direction

---

## Notes for Phase 4 Coder

1. **Training Time:** 17 tasks × 4 ranks × ~2 hours = ~140 hours total
   - Consider parallelization if multiple GPUs available
   - Implement checkpoint resumption for interrupted runs

2. **Memory:** LLaMA-2-7B + LoRA fits on single A100 40GB
   - Use fp16 training (`torch_dtype=torch.float16`)
   - Gradient checkpointing if memory issues

3. **HuggingFace PEFT:** Use `peft` library for LoRA implementation
   - Avoid manual matrix implementation (PEFT is production-tested)

4. **Hypervolume:** Use `pymoo.indicators.hv.HV` for computation
   - Normalize accuracy to [0, 1] range
   - Use negative FLOPs for minimization objective

5. **Visualization:** All 5 figures must be generated and saved to `{hypothesis_folder}/figures/`

6. **Gate Check:** Print clear PASS/FAIL message based on oracle_gap_pct >= 10.0

---

*Generated by Logic Agent*
*Date: 2026-04-19*
*Hypothesis: h-e1 (EXISTENCE)*
*Total API Count: 6 core modules + 1 main pipeline*
