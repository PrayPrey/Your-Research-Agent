# Architecture: H-M1
# JointLoRA-KV — Task CE Loss Joint Training of LoRA Adapters and Locret Retaining Heads

**Applied**: PEFT LoRA joint training pattern (HuggingFace PEFT + separate AdamW param groups)
**Applied**: Locret retaining head CIS pattern (fc1/fc2 per layer, sigmoid activation, warm init)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1 extends H-E1)
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/20260520_scope/h-e1/code/`
**Findings**: H-E1 uses inference-only extraction (no training loop). `RetainingHead` (fc1/fc2) and `LocretExtractor` with forward pre-hooks are proven patterns. `ExperimentConfig` uses `hypothesis_folder="."` relative output path. Imports use flat `from config import ExperimentConfig` (no package structure — scripts run from `code/` directory). H-M1 requires adding training loop, joint optimizer, GLUE classification head, KV eviction logic, and LongBench eval on top of these proven patterns.

---

## File Organization

- `h-m1/code/config.py` — experiment config (all hyperparameters)
- `h-m1/code/data_loader.py` — GLUE + LongBench dataset loading and tokenization
- `h-m1/code/model.py` — JointLoRAKV, B1LoRAFrozenLocret, B2LoRAKvpress model wrappers
- `h-m1/code/locret_heads.py` — RetainingHead module + load/inject utilities (extends H-E1 pattern)
- `h-m1/code/trainer.py` — JointLoRAKVTrainer with soft budget masking + B1 trainer
- `h-m1/code/evaluate.py` — GLUE eval, LongBench eval, mechanism verification
- `h-m1/code/visualize.py` — 5 required figures
- `h-m1/code/run_experiment.py` — orchestration entry point (seeds, tasks, baselines)
- `h-m1/results/` — JSON result files per seed per task
- `h-m1/figures/` — generated figures

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| RetainingHead | `from locret_heads import RetainingHead` (new, extends H-E1 pattern) | `h-e1/code/locret_extractor.py` (reference) |
| ExperimentConfig pattern | flat imports, run from `code/` directory | `h-e1/code/config.py` |
| LoRA load pattern | `PeftModel.from_pretrained` / `get_peft_model` | `h-e1/code/lora_extractor.py` |
| Locret load pattern | `hf_hub_download` + `state_dict[f"model.layers.{i}.self_attn.fc1.weight"]` | `h-e1/code/locret_extractor.py` |

**Verified from**: `docs/youra_research/20260520_scope/h-e1/code/` (actual implementation)
**Note**: H-M1 does NOT import from H-E1 directly. It reimplements the proven patterns with training support. Import paths are flat (no package), scripts run from `h-m1/code/` directory.

---

## Module Structure

### Config (`code/config.py`)

**Dependencies**: none

```python
from dataclasses import dataclass, field
from typing import List
import os

@dataclass
class ExperimentConfig:
    # Model
    base_model: str = "meta-llama/Meta-Llama-3.1-8B-Instruct"
    locret_checkpoint: str = "hyx21/Locret-llama-3.1-8B-instruct"
    attn_impl: str = "eager"
    dtype: str = "float16"

    # LoRA
    lora_r: int = 16
    lora_alpha: int = 32
    lora_target_modules: List[str] = field(default_factory=lambda: ["q_proj", "k_proj", "v_proj"])
    lora_dropout: float = 0.1

    # GQA
    num_query_heads: int = 32
    num_kv_heads: int = 8
    num_layers: int = 32
    head_dim: int = 128
    kv_repeat: int = 4

    # Training
    lora_lr: float = 1e-4
    locret_lr: float = 5e-4
    weight_decay: float = 0.01
    adam_betas: tuple = (0.9, 0.999)
    adam_eps: float = 1e-8
    warmup_ratio: float = 0.06
    max_grad_norm: float = 1.0
    per_device_batch_size: int = 8
    grad_accum_steps: int = 4
    epochs_mnli: int = 3
    epochs_sst2: int = 5
    epochs_qnli: int = 5
    seeds: List[int] = field(default_factory=lambda: [42, 123, 456])

    # KV budget
    budget_ratio: float = 0.5

    # GLUE tasks
    glue_tasks: List[str] = field(default_factory=lambda: ["mnli", "sst2", "qnli"])
    max_seq_len: int = 512

    # LongBench tasks
    longbench_tasks: List[str] = field(
        default_factory=lambda: ["narrativeqa", "qasper", "multifieldqa_en"]
    )
    longbench_max_len: int = 15360

    # Budget sensitivity
    budget_ratios_sweep: List[float] = field(default_factory=lambda: [0.3, 0.5, 0.7])

    # Output
    hypothesis_folder: str = "."
    results_dir: str = "results"
    figures_dir: str = "figures"

    def get_epochs(self, task: str) -> int: ...
    def get_results_path(self, tag: str) -> str: ...
    def get_figures_dir(self) -> str: ...
```

---

### DataLoader (`code/data_loader.py`)

**Dependencies**: Config

```python
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer
from typing import Tuple, Dict, List, Optional
from config import ExperimentConfig

class GLUEDataset(Dataset):
    def __init__(self, task: str, split: str, tokenizer, config: ExperimentConfig): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> Dict[str, object]: ...

class LongBenchDataset(Dataset):
    def __init__(self, task: str, tokenizer, config: ExperimentConfig): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> Dict[str, object]: ...

def get_glue_loaders(
    task: str,
    tokenizer,
    config: ExperimentConfig,
    seed: int,
) -> Tuple[DataLoader, DataLoader]: ...
    # Returns (train_loader, val_loader)

def get_longbench_loader(
    task: str,
    tokenizer,
    config: ExperimentConfig,
) -> DataLoader: ...

def get_num_labels(task: str) -> int: ...
    # mnli->3, sst2->2, qnli->2
```

---

### LocretHeads (`code/locret_heads.py`)

**Dependencies**: Config

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
from typing import List, Tuple
from huggingface_hub import hf_hub_download
from config import ExperimentConfig

class RetainingHead(nn.Module):
    """Per-layer Locret retaining head. CIS = sigmoid([Q;K;V] @ fc1.T) @ fc2.T"""
    def __init__(self, fc1_weight: Tensor, fc2_weight: Tensor): ...
    def forward(self, q: Tensor, k: Tensor, v: Tensor) -> Tensor: ...
        # q: (B, L, 4096), k: (B, L, 1024), v: (B, L, 1024)
        # returns: (B, L, 8) CIS scores in (0, 1)

class LocretHeadCollection(nn.Module):
    """Container for all 32 per-layer RetainingHead modules."""
    def __init__(self, heads: List[RetainingHead]): ...
    def __getitem__(self, layer_idx: int) -> RetainingHead: ...
    def parameters(self): ...

def load_locret_heads(
    checkpoint: str,
    num_layers: int,
    device: torch.device,
) -> LocretHeadCollection: ...
    # Downloads hyx21/Locret-llama-3.1-8B-instruct .bin
    # Reads state_dict[f"model.layers.{i}.self_attn.fc1.weight"]
    # Returns collection with requires_grad=True (for JointLoRA-KV)

def freeze_locret_heads(heads: LocretHeadCollection) -> None: ...
    # Sets requires_grad=False on all head parameters (for B1)
```

---

### Model (`code/model.py`)

**Dependencies**: Config, LocretHeads

```python
import torch
import torch.nn as nn
from torch import Tensor
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, TaskType, get_peft_model
from typing import Dict, Optional, Tuple
from config import ExperimentConfig
from locret_heads import LocretHeadCollection, load_locret_heads, freeze_locret_heads

class JointLoRAKVModel(nn.Module):
    """LLaMA-3.1-8B + LoRA (trainable) + Locret retaining heads (trainable).
    Used for JointLoRA-KV and B1 (with frozen heads).
    """
    def __init__(self, base_model, locret_heads: LocretHeadCollection, config: ExperimentConfig): ...
    def forward(
        self,
        input_ids: Tensor,
        attention_mask: Tensor,
        labels: Optional[Tensor] = None,
        budget_ratio: Optional[float] = None,
        training_mode: bool = True,
    ) -> Dict[str, Tensor]: ...
        # Returns dict with keys: loss, logits, cis_scores (list of per-layer tensors)
    def compute_cis(self, layer_idx: int, hidden_states: Tensor) -> Tensor: ...
        # Returns (B, L, 8) CIS scores for layer_idx
    def apply_soft_budget_mask(
        self, hidden_states: Tensor, cis_scores: Tensor, budget_ratio: float
    ) -> Tensor: ...
        # Differentiable soft masking for training (top-k approximation)
    def apply_hard_eviction(
        self, kv_cache: Tuple, cis_scores: Tensor, budget_ratio: float
    ) -> Tuple: ...
        # Hard top-k eviction for inference

class B2KvpressModel(nn.Module):
    """LLaMA-3.1-8B + LoRA (trainable) + kvpress StreamingLLM/H2O heuristic at inference."""
    def __init__(self, base_model, config: ExperimentConfig): ...
    def forward(
        self,
        input_ids: Tensor,
        attention_mask: Tensor,
        labels: Optional[Tensor] = None,
    ) -> Dict[str, Tensor]: ...
    def apply_kvpress_eviction(
        self, kv_cache: Tuple, budget_ratio: float
    ) -> Tuple: ...

def build_lora_model(
    config: ExperimentConfig,
    num_labels: int,
    task: str,
) -> Tuple[nn.Module, object]: ...
    # Returns (peft_model, tokenizer)
    # Loads meta-llama/Meta-Llama-3.1-8B-Instruct with eager attn + classification head

def build_joint_model(
    config: ExperimentConfig,
    num_labels: int,
    task: str,
    freeze_locret: bool = False,
) -> Tuple[JointLoRAKVModel, object]: ...
    # freeze_locret=True → B1; freeze_locret=False → JointLoRA-KV
```

---

### Trainer (`code/trainer.py`)

**Dependencies**: Config, Model, DataLoader

```python
import torch
from torch.optim import AdamW
from transformers import get_linear_schedule_with_warmup
from typing import Dict, List, Optional
from config import ExperimentConfig
from model import JointLoRAKVModel

class JointLoRAKVTrainer:
    """Trains JointLoRA-KV (or B1 frozen) via task CE loss with separate LRs."""
    def __init__(
        self,
        model: JointLoRAKVModel,
        train_loader,
        config: ExperimentConfig,
        task: str,
        seed: int,
        is_b1: bool = False,
    ): ...

    def build_optimizer(self) -> AdamW: ...
        # Param group 1: LoRA params, lr=lora_lr
        # Param group 2: Locret params, lr=locret_lr (skipped if is_b1=True)

    def train_epoch(self, epoch: int) -> Dict[str, float]: ...
        # Returns {loss, locret_grad_norm, step_count}
        # Logs: "JointLoRA-KV: Locret heads receiving CE gradients — step {step}, locret_grad_norm={norm:.4f}"

    def train(self) -> List[Dict[str, float]]: ...
        # Returns training history (loss per epoch, grad norm)

    def save_checkpoint(self, output_dir: str) -> None: ...
```

---

### Evaluate (`code/evaluate.py`)

**Dependencies**: Config, Model, DataLoader

```python
import torch
from typing import Dict, List, Optional, Tuple
from config import ExperimentConfig

def evaluate_glue(
    model,
    val_loader,
    task: str,
    budget_ratio: float,
    config: ExperimentConfig,
    collect_cis_samples: bool = False,
) -> Dict[str, object]: ...
    # Returns {accuracy, task, budget_ratio, cis_samples (optional), tokens_retained_ratio}
    # Uses evaluate.load("glue", task) for metric computation
    # Hard eviction at inference (budget_ratio=0.5)

def evaluate_longbench(
    model,
    loader,
    task: str,
    budget_ratio: float,
    config: ExperimentConfig,
) -> Dict[str, float]: ...
    # Returns {f1, task, budget_ratio}
    # Uses qa_f1_score from THUDM/LongBench metrics.py

def evaluate_budget_sensitivity(
    model,
    val_loader,
    task: str,
    config: ExperimentConfig,
) -> Dict[float, float]: ...
    # Returns {budget_ratio: accuracy} for ratios in config.budget_ratios_sweep

def verify_mechanism_activated(
    training_log: List[str],
    b1_results: Dict,
    joint_results: Dict,
) -> Tuple[bool, Dict]: ...
    # Checks: locret_grad_received, cis_shape_correct, eviction_active, accuracy_improved
    # Gate: joint mean_glue_acc - b1 mean_glue_acc >= 2.0
    # Returns (gate_passed, indicators_dict)

def aggregate_seed_results(
    results_per_seed: List[Dict],
) -> Dict[str, float]: ...
    # Returns {mean_accuracy, std_accuracy} per task and overall mean GLUE
```

---

### Visualize (`code/visualize.py`)

**Dependencies**: Config

```python
from typing import Dict, List
from config import ExperimentConfig

def plot_gate_metrics_comparison(
    joint_results: Dict,
    b1_results: Dict,
    b2_results: Dict,
    output_dir: str,
) -> None: ...
    # FR-8.1 (Mandatory): bar chart mean GLUE acc ± std, 3 models

def plot_training_curves(
    training_history: Dict[str, List],
    output_dir: str,
) -> None: ...
    # FR-8.2: loss per epoch, all 3 seeds

def plot_per_task_glue(
    joint_results: Dict,
    b1_results: Dict,
    b2_results: Dict,
    output_dir: str,
) -> None: ...
    # FR-8.3: MNLI/SST-2/QNLI breakdown bars

def plot_budget_sensitivity(
    joint_sensitivity: Dict[float, float],
    b1_sensitivity: Dict[float, float],
    output_dir: str,
) -> None: ...
    # FR-8.4: accuracy vs budget_ratio curve

def plot_longbench_comparison(
    joint_results: Dict,
    b1_results: Dict,
    b2_results: Dict,
    output_dir: str,
) -> None: ...
    # FR-8.5: NarrativeQA/Qasper/MultiFieldQA F1 bars
```

---

### RunExperiment (`code/run_experiment.py`)

**Dependencies**: Config, DataLoader, Model, Trainer, Evaluate, Visualize

```python
from config import ExperimentConfig
from typing import Optional

def set_seed(seed: int) -> None: ...
    # torch.manual_seed + numpy.random.seed + random.seed

def run_joint_training(
    config: ExperimentConfig,
    task: str,
    seed: int,
) -> Dict: ...
    # Trains JointLoRA-KV, returns training history + val results

def run_b1_training(
    config: ExperimentConfig,
    task: str,
    seed: int,
) -> Dict: ...
    # Trains B1 (LoRA only, frozen Locret), returns val results

def run_b2_inference(
    config: ExperimentConfig,
    task: str,
    seed: int,
) -> Dict: ...
    # B2: LoRA inference with kvpress heuristic eviction

def run_longbench_eval(
    config: ExperimentConfig,
    seed: int,
    model_tag: str,
) -> Dict: ...

def main() -> None: ...
    # Entry point: iterates seeds x tasks, calls run_* functions
    # Saves results to JSON, calls visualize, calls verify_mechanism_activated
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup + Config | File structure, config.py, deps verification, CUDA setup | 5 | 1+1+1+2 |
| A-2 | Data Loading | GLUEDataset + LongBenchDataset, tokenization, DataLoader factories | 8 | 2+1+2+3 |
| A-3 | LocretHeads Module | RetainingHead nn.Module, LocretHeadCollection, load from .bin checkpoint | 10 | 3+2+3+2 |
| A-4 | Model Wrappers | JointLoRAKVModel (soft budget + hard eviction), B2KvpressModel, build_* factories | 16 | 4+4+4+4 |
| A-5 | Joint Trainer | JointLoRAKVTrainer, separate param groups, grad norm logging, LR schedule | 14 | 3+3+4+4 |
| A-6 | GLUE Evaluation | evaluate_glue with hard eviction, evaluate.load metric, tokens_retained_ratio | 12 | 3+3+3+3 |
| A-7 | LongBench Evaluation | evaluate_longbench, qa_f1_score integration, generation with eviction | 12 | 3+3+3+3 |
| A-8 | Mechanism Verification | verify_mechanism_activated, CIS shape checks, grad norm checks, gate logic | 9 | 2+2+3+2 |
| A-9 | Budget Sensitivity | evaluate_budget_sensitivity sweep (0.3/0.5/0.7), result aggregation | 8 | 2+2+2+2 |
| A-10 | Visualization | 5 figures: gate comparison, training curves, per-task GLUE, budget sensitivity, LongBench | 9 | 2+1+3+3 |
| A-11 | Orchestration + Seeds | run_experiment.py, 3 seeds × 3 GLUE tasks × 3 models, result serialization | 11 | 2+3+3+3 |
| A-12 | End-to-End Validation | Run full pipeline, verify gate condition, check all figures generated, fix failures | 13 | 3+3+3+4 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4, A-5], Medium(9-13): [A-3, A-6, A-7, A-8, A-11, A-12], Low(4-8): [A-1, A-2, A-9, A-10]

---

## Key Interface Notes for Phase 4

- All scripts run from `h-m1/code/` directory; use flat imports (`from config import ...`)
- `JointLoRAKVModel` handles BOTH training mode (soft budget, differentiable) and inference mode (hard top-k eviction)
- `build_joint_model(freeze_locret=False)` → JointLoRA-KV; `build_joint_model(freeze_locret=True)` → B1
- Locret state dict keys verified from H-E1: `model.layers.{i}.self_attn.fc1.weight` / `fc2.weight`
- GQA expansion: `repeat_interleave(4)` for 8 KV heads → 32 query heads (proven in H-E1)
- `attn_implementation="eager"` required on base model load (blocks flash-attn, enables Q/K/V access)
- Loss computation in float32; model loaded in float16
- Output paths relative to `hypothesis_folder="."` (scripts run from `h-m1/code/` with `hypothesis_folder=".."`)
