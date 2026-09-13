# Architecture: H-M2 — JointLoRA-KV Joint Training

**Hypothesis:** Joint end-to-end training of LoRA adapter and Locret retaining head parameters in single backward pass via task CE loss
**Type:** MECHANISM (FULL tier)
**Gate:** MUST_WORK — stable convergence AND LongBench-QA F1 ≥ B3 at budget_ratio=0.5
**Date:** 2026-05-20

---

## Applied Patterns

Applied: PEFT dual-parameter-group AdamW (diffusers SDXL dual-LoRA pattern)
Applied: LoRA parameter isolation via `requires_grad` name filter (HuggingFace PEFT conceptual guide)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No local codebase — green-field implementation
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. Locret retaining head architecture sourced from huangyuxiang03/Locret official repo (Phase 2C Exa research). LoRA injection pattern from HuggingFace PEFT. Joint backward feasibility confirmed from awslabs/keys_values.

---

## File Structure

```
h-m2/code/
  config.py          # Dataclasses + YAML loading
  data.py            # DataManager (GLUE + LongBench)
  model.py           # JointLoRAKVModel + Locret head registration
  stability.py       # StabilityMonitor
  trainer.py         # JointLoRAKVTrainer + BaselineB3Trainer
  evaluator.py       # LongBenchEvaluator + GLUEEvaluator
  figures.py         # Visualization generation
  run_experiment.py  # ExperimentRunner orchestrator
h-m2/figures/        # Output figures
h-m2/checkpoints/    # Per-seed checkpoints
h-m2/results/        # JSON results per seed
```

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies**: None (stdlib dataclasses + PyYAML)

```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class LoRAConfig:
    r: int = 16
    lora_alpha: int = 32
    target_modules: List[str] = field(default_factory=lambda: ["q_proj", "k_proj", "v_proj"])
    lora_dropout: float = 0.05
    bias: str = "none"

@dataclass
class LocretConfig:
    hidden_dim: int = 1024
    num_output_scores: int = 8
    budget_ratio: float = 0.5
    warm_init_from: Optional[str] = "hyx21/Locret-llama-3.1-8B-instruct"

@dataclass
class TrainingConfig:
    lora_lr: float = 1e-4
    locret_lr: float = 5e-4
    weight_decay: float = 0.01
    betas: tuple = (0.9, 0.999)
    eps: float = 1e-8
    batch_size: int = 8
    grad_accum_steps: int = 4
    num_epochs: int = 3
    warmup_ratio: float = 0.1
    max_grad_norm: float = 1.0
    seeds: List[int] = field(default_factory=lambda: [42, 123, 456])
    max_length: int = 512

@dataclass
class ExperimentConfig:
    model_name: str = "meta-llama/Meta-Llama-3.1-8B"
    lora: LoRAConfig = field(default_factory=LoRAConfig)
    locret: LocretConfig = field(default_factory=LocretConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    output_dir: str = "h-m2"

def load_config(path: str) -> ExperimentConfig: ...
def save_config(cfg: ExperimentConfig, path: str) -> None: ...
```

---

### DataManager (`code/data.py`)

**Dependencies**: config.py

```python
from torch.utils.data import Dataset, DataLoader
from transformers import PreTrainedTokenizer
from typing import Dict, List, Tuple

class GLUEDataset(Dataset):
    def __init__(self, task_name: str, split: str, tokenizer: PreTrainedTokenizer, max_length: int): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> Dict: ...

class LongBenchDataset(Dataset):
    def __init__(self, task_name: str, split: str = "test"): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> Dict: ...

class DataManager:
    GLUE_TASKS: List[str] = ["mnli", "sst2", "qnli"]
    LONGBENCH_TASKS: List[str] = ["narrativeqa", "qasper", "multifieldqa_en"]

    def __init__(self, tokenizer: PreTrainedTokenizer, training_config): ...

    def get_glue_train_loader(self) -> DataLoader: ...
    def get_glue_val_loaders(self) -> Dict[str, DataLoader]: ...
    def get_longbench_test_loaders(self) -> Dict[str, DataLoader]: ...
```

---

### JointLoRAKVModel (`code/model.py`)

**Dependencies**: config.py

```python
import torch
import torch.nn as nn
from torch import Tensor
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from typing import Optional, Tuple, Dict

class LocretRetainingHead(nn.Module):
    """Per-layer MLP: S̃ = σ([Q,K,V] @ W1) @ W2"""
    def __init__(self, d_model: int, d_kv: int, hidden_dim: int = 1024, num_scores: int = 8): ...
    def forward(self, q: Tensor, k: Tensor, v: Tensor) -> Tensor:
        """Returns CIS scores shape (batch, seq_len, num_scores)"""
        ...

class JointLoRAKVModel(nn.Module):
    def __init__(self, base_model_name: str, lora_config, locret_config): ...

    def register_retaining_heads(self) -> None:
        """Attach LocretRetainingHead to each attention layer; set requires_grad=True."""
        ...

    def load_locret_warm_init(self, checkpoint_path: str) -> None:
        """Load pre-trained Locret W1/W2 weights for warm initialization."""
        ...

    def get_lora_params(self) -> list:
        """Filter: [p for n,p in named_parameters() if 'lora_' in n and p.requires_grad]"""
        ...

    def get_locret_params(self) -> list:
        """Filter: [p for n,p in named_parameters() if 'retaining_head' in n and p.requires_grad]"""
        ...

    def compute_soft_kv_mask(self, cis_scores: Tensor, budget_ratio: float) -> Tensor:
        """Differentiable soft top-k approximation for training."""
        ...

    def apply_hard_kv_eviction(self, kv_cache: Tensor, cis_scores: Tensor, budget_ratio: float) -> Tensor:
        """Hard top-k eviction for inference."""
        ...

    def forward(
        self,
        input_ids: Tensor,
        attention_mask: Optional[Tensor] = None,
        labels: Optional[Tensor] = None,
        kv_budget_ratio: float = 0.5,
        training: bool = True,
    ) -> Tuple[Tensor, Optional[Tensor]]:
        """Returns (logits, cis_scores). Applies soft mask if training, hard eviction if not."""
        ...

    def save_checkpoint(self, path: str) -> None: ...
    def load_checkpoint(self, path: str) -> None: ...

def build_joint_model(config) -> JointLoRAKVModel: ...
def build_baseline_b3_model(config) -> JointLoRAKVModel:
    """Same architecture; training procedure differs (sequential stages in trainer)."""
    ...
```

---

### StabilityMonitor (`code/stability.py`)

**Dependencies**: None (stdlib + torch)

```python
import torch
from typing import List, Dict, Optional
from collections import deque

class StabilityMonitor:
    def __init__(self, seed: int, moving_avg_window: int = 100, divergence_factor: float = 2.0): ...

    def record_loss(self, step: int, loss: float) -> None: ...
    def record_grad_norms(self, step: int, lora_norm: float, locret_norm: float) -> None: ...

    def check_nan(self, loss: torch.Tensor) -> bool:
        """Returns True if NaN detected; increments nan_events counter."""
        ...

    def check_divergence(self, loss: float) -> bool:
        """Returns True if loss > divergence_factor * moving_average."""
        ...

    def get_moving_average(self) -> float: ...

    def is_stable(self) -> bool:
        """Returns nan_events == 0 AND divergence_events == 0."""
        ...

    def get_report(self) -> Dict:
        """Returns {seed, nan_events, divergence_events, final_loss, loss_history, grad_norm_history}."""
        ...

    def save_report(self, path: str) -> None:
        """Save to {seed}/stability_log.json."""
        ...
```

---

### JointLoRAKVTrainer + BaselineB3Trainer (`code/trainer.py`)

**Dependencies**: model.py, stability.py, data.py, config.py

```python
import torch
import torch.nn.functional as F
from torch.optim import AdamW
from torch.optim.lr_scheduler import LambdaLR
from typing import Dict, Optional

class JointLoRAKVTrainer:
    def __init__(self, model, data_manager, stability_monitor, training_config, seed: int): ...

    def build_optimizer(self) -> AdamW:
        """Two param groups: LoRA lr=1e-4, Locret lr=5e-4; shared AdamW."""
        ...

    def build_scheduler(self, optimizer: AdamW, total_steps: int) -> LambdaLR:
        """Linear warmup (10%) + cosine decay."""
        ...

    def train_step(self, batch: Dict, step: int) -> float:
        """Single forward+backward; CE loss only; grad clip max_norm=1.0."""
        ...

    def train_epoch(self, epoch: int) -> Dict:
        """Returns {epoch, mean_loss, nan_events, divergence_events}."""
        ...

    def train(self) -> Dict:
        """Full training loop over all epochs; returns stability_report."""
        ...

    def save_checkpoint(self, path: str) -> None: ...


class BaselineB3Trainer:
    """Sequential LoRA→Locret pipeline (2-stage training)."""

    def __init__(self, model, data_manager, training_config, seed: int): ...

    def stage1_lora_finetune(self) -> Dict:
        """Train LoRA on GLUE CE loss; Locret heads frozen."""
        ...

    def stage2_locret_finetune(self) -> Dict:
        """Freeze LoRA; train Locret heads on LM distillation loss."""
        ...

    def train(self) -> Dict:
        """Run stage1 then stage2; return combined report."""
        ...

    def save_checkpoint(self, path: str) -> None: ...
```

---

### LongBenchEvaluator + GLUEEvaluator (`code/evaluator.py`)

**Dependencies**: model.py, data.py, config.py

```python
from typing import Dict, List
import torch

class LongBenchEvaluator:
    TASKS: List[str] = ["narrativeqa", "qasper", "multifieldqa_en"]

    def __init__(self, model, data_manager, budget_ratio: float = 0.5): ...

    def evaluate_task(self, task_name: str) -> float:
        """Run inference with hard KV eviction; compute qa_f1_score."""
        ...

    def evaluate_all(self) -> Dict[str, float]:
        """Returns {task_name: f1, ..., 'mean_f1': float}."""
        ...

    @staticmethod
    def qa_f1_score(prediction: str, ground_truth: str) -> float:
        """From THUDM/LongBench metrics.py."""
        ...


class GLUEEvaluator:
    TASKS: List[str] = ["mnli", "sst2", "qnli"]

    def __init__(self, model, data_manager): ...

    def evaluate_task(self, task_name: str) -> float:
        """Compute accuracy on validation split."""
        ...

    def evaluate_all(self) -> Dict[str, float]:
        """Returns {task_name: accuracy, ..., 'mean_accuracy': float}."""
        ...
```

---

### Figures (`code/figures.py`)

**Dependencies**: None (matplotlib + numpy)

```python
from typing import Dict, List

def plot_longbench_comparison(
    joint_results: Dict[str, float],
    b3_results: Dict[str, float],
    save_path: str = "h-m2/figures/longbench_comparison.png",
) -> None:
    """Mandatory: bar chart JointLoRA-KV vs B3 F1 per task + mean."""
    ...

def plot_training_loss_curves(
    loss_histories: Dict[int, List[float]],
    save_path: str = "h-m2/figures/training_loss_curves.png",
) -> None:
    """Per-step loss curves for seeds 42, 123, 456."""
    ...

def plot_loss_distribution(
    epoch_end_losses: Dict[int, List[float]],
    save_path: str = "h-m2/figures/loss_distribution.png",
) -> None:
    """Box plot of loss distribution per seed at epoch end."""
    ...

def plot_per_task_f1(
    joint_results: Dict[str, float],
    b3_results: Dict[str, float],
    save_path: str = "h-m2/figures/per_task_f1.png",
) -> None: ...

def plot_gradient_norms(
    lora_norms: Dict[int, List[float]],
    locret_norms: Dict[int, List[float]],
    save_path: str = "h-m2/figures/gradient_norms.png",
) -> None: ...
```

---

### ExperimentRunner (`code/run_experiment.py`)

**Dependencies**: config.py, data.py, model.py, trainer.py, evaluator.py, stability.py, figures.py

```python
import json
from typing import Dict, List
from config import ExperimentConfig

class ExperimentRunner:
    def __init__(self, config: ExperimentConfig): ...

    def run_seed(self, seed: int, model_type: str) -> Dict:
        """Train + evaluate one model (joint or b3) for one seed.
        model_type: 'joint' | 'b3'
        Returns {seed, longbench_results, glue_results, stability_report}."""
        ...

    def run_all(self) -> Dict:
        """3 seeds × 2 models; aggregates results; checks gate criteria."""
        ...

    def aggregate_results(self, all_results: List[Dict]) -> Dict:
        """Compute mean ± std across seeds per model type."""
        ...

    def check_gate(self, aggregated: Dict) -> Dict:
        """Returns {stability_passed, accuracy_passed, gate_satisfied}.
        stability_passed: all seeds nan_events==0 AND divergence_events==0.
        accuracy_passed: joint mean F1 >= b3 mean F1."""
        ...

    def save_results(self, aggregated: Dict, path: str) -> None: ...
    def generate_figures(self, aggregated: Dict) -> None: ...


def main() -> None:
    """Entry point: load config, run experiment, print gate result."""
    ...
```

---

## Module Dependencies

```
config.py
  ↑
data.py ─────────────────────────────┐
  ↑                                  │
model.py ← stability.py             │
  ↑            ↑                    │
trainer.py ────┘                    │
  ↑                                  │
evaluator.py ←──────────────────────┘
  ↑
figures.py
  ↑
run_experiment.py (orchestrator)
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config + Data Pipeline | config.py dataclasses + DataManager for GLUE/LongBench loading, tokenization, DataLoaders | 9 | 2+2+3+2 |
| A-2 | Locret Retaining Head + Model Registration | LocretRetainingHead MLP, per-layer registration on LLaMA-3.1-8B, warm init from checkpoint, GQA expand | 14 | 3+3+4+4 |
| A-3 | JointLoRAKVModel Forward Pass | PEFT LoRA injection, soft KV mask (differentiable top-k), hard eviction, unified forward returning (logits, cis_scores) | 16 | 4+3+5+4 |
| A-4 | StabilityMonitor | Moving average window, NaN detection, divergence detection (2× spike), per-step grad norm logging, JSON report | 10 | 2+2+3+3 |
| A-5 | JointLoRAKVTrainer | Dual-param-group AdamW, linear warmup + cosine schedule, grad clip, single CE backward, step-level stability checks | 15 | 3+4+4+4 |
| A-6 | BaselineB3Trainer | Stage-1 LoRA CE fine-tune, Stage-2 freeze LoRA + Locret LM distillation loss (Locret official script adapted) | 14 | 3+3+4+4 |
| A-7 | LongBenchEvaluator | Hard KV eviction at inference, generation loop, qa_f1_score from THUDM/LongBench metrics.py, 3-task mean | 13 | 3+3+4+3 |
| A-8 | GLUEEvaluator | Accuracy eval on MNLI/SST-2/QNLI validation splits, HuggingFace evaluate integration | 8 | 2+2+2+2 |
| A-9 | ExperimentRunner + Gate Logic | Orchestrate 3 seeds × 2 models, aggregate mean±std, stability gate check, accuracy gate check, checkpoint management | 12 | 2+3+4+3 |
| A-10 | Figures Generation | 5 mandatory figures: bar comparison, loss curves, box plot, per-task F1, gradient norms | 8 | 2+1+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-2, A-3, A-5, A-6], Medium(9-13): [A-4, A-7, A-9], Low(4-8): [A-1, A-8, A-10]

---

## Key Interfaces Between Modules

| Caller | Callee | Interface |
|--------|--------|-----------|
| trainer.py | model.py | `model.forward(input_ids, labels, kv_budget_ratio, training=True)` |
| trainer.py | stability.py | `monitor.check_nan(loss)`, `monitor.check_divergence(loss.item())`, `monitor.record_grad_norms(step, ...)` |
| evaluator.py | model.py | `model.forward(..., training=False)` with hard KV eviction |
| run_experiment.py | trainer.py | `trainer.train()` → stability_report |
| run_experiment.py | evaluator.py | `evaluator.evaluate_all()` → {task: f1, mean_f1} |
| run_experiment.py | figures.py | `plot_*(aggregated_results)` |

---

## Critical Implementation Notes

1. **Parameter disjointness**: LoRA params filtered via `"lora_" in name`, Locret params via `"retaining_head" in name`. No overlap possible since PEFT injects A/B with `lora_` prefix and retaining heads are registered under `retaining_head` namespace.

2. **GQA compatibility**: LLaMA-3.1-8B uses 8 KV heads vs 32 query heads. CIS score input requires `k.repeat_interleave(4, dim=1)` and `v.repeat_interleave(4, dim=1)` before concat with Q.

3. **Soft-to-hard transition**: During training, `compute_soft_kv_mask` uses sigmoid-based differentiable approximation (not argmax). At inference, `apply_hard_kv_eviction` switches to exact `torch.topk`. The `training` flag in `forward()` controls this branch.

4. **Stability halt**: If `monitor.check_nan(loss)` returns True in `train_step`, trainer logs event and raises `StabilityError` — halts seed run, reports failure, does not continue training.

5. **B3 Stage-2 loss**: LM distillation objective from Locret official repo (`locret/train/train.py`) — next-token prediction loss on long-context QA data, NOT CE classification loss.
