# Architecture: H-E1 — Eviction-Aware LoRA Weight Divergence (EXISTENCE PoC)

**Applied**: HuggingFace PEFT LoRA pattern + H2O eviction mask construction pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field - no existing codebase to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; no base hypothesis code exists

---

## File Organization

```
outputs/h-e1/
├── llama2-7b-baseline/
├── llama2-7b-eviction-aware/
├── mistral-7b-baseline/
├── mistral-7b-eviction-aware/
├── weight_analysis_llama2.json
├── weight_analysis_mistral.json
└── gate_result.json

docs/youra_research/20260504_scope/h-e1/
├── figures/
│   ├── cosine_similarity_bar_llama2.png
│   └── cosine_similarity_bar_mistral.png
└── 03_architecture.md

code/h-e1/
├── config.py
├── data.py
├── model.py
├── train.py
├── evaluate.py
├── visualize.py
└── run_experiment.py
```

---

## Module Definitions

### Config (`code/h-e1/config.py`)

**Dependencies**: None

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class LoRAConfig:
    rank: int = 16
    alpha: int = 32
    dropout: float = 0.05
    target_modules: List[str] = field(default_factory=lambda: ["q_proj", "v_proj"])

@dataclass
class TrainingConfig:
    model_name: str = ""
    condition: str = ""          # "baseline" or "eviction-aware"
    output_dir: str = ""
    max_seq_length: int = 32768
    per_device_train_batch_size: int = 1
    gradient_accumulation_steps: int = 16
    num_train_epochs: int = 1
    learning_rate: float = 2e-4
    warmup_ratio: float = 0.03
    seed: int = 42
    kv_budget_ratio: float = 0.5
    lora: LoRAConfig = field(default_factory=LoRAConfig)

def get_all_configs() -> List[TrainingConfig]: ...
```

---

### DataModule (`code/h-e1/data.py`)

**Dependencies**: Config

```python
from torch.utils.data import Dataset
from transformers import PreTrainedTokenizer

class LongAlpacaDataset(Dataset):
    def __init__(self, tokenizer: PreTrainedTokenizer, max_seq_length: int = 32768): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> dict: ...

def build_dataloader(tokenizer: PreTrainedTokenizer, max_seq_length: int, batch_size: int): ...
```

---

### ModelModule (`code/h-e1/model.py`)

**Dependencies**: Config

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from peft import LoraConfig, get_peft_model, PeftModel
from transformers import AutoModelForCausalLM

class H2OEvictionAwareAttention(nn.Module):
    def __init__(self, base_attention: nn.Module, kv_budget_ratio: float = 0.5): ...
    def h2o_mask(self, attn_scores: torch.Tensor) -> torch.Tensor: ...
    def forward(self, hidden_states: torch.Tensor, **kwargs) -> tuple: ...

def load_base_model(model_name: str) -> AutoModelForCausalLM: ...
def inject_h2o_wrappers(model: nn.Module, kv_budget_ratio: float) -> nn.Module: ...
def apply_lora(model: nn.Module, lora_cfg: "LoRAConfig") -> PeftModel: ...
def build_model(cfg: "TrainingConfig") -> PeftModel: ...
```

---

### TrainModule (`code/h-e1/train.py`)

**Dependencies**: Config, DataModule, ModelModule

```python
from transformers import Trainer, TrainingArguments

def get_training_args(cfg: "TrainingConfig") -> TrainingArguments: ...
def run_training(cfg: "TrainingConfig") -> str: ...
    # Returns output_dir path of saved adapter
```

---

### EvaluateModule (`code/h-e1/evaluate.py`)

**Dependencies**: None (pure torch)

```python
import torch
import torch.nn.functional as F
from typing import Dict

def load_adapter_state_dict(adapter_dir: str) -> Dict[str, torch.Tensor]: ...
def compute_layer_cosine_similarity(
    baseline_sd: Dict[str, torch.Tensor],
    proposed_sd: Dict[str, torch.Tensor]
) -> Dict[str, float]: ...
def evaluate_gate(results: Dict[str, float], threshold: float = 0.95) -> dict: ...
def save_results(results: dict, path: str) -> None: ...
```

---

### VisualizeModule (`code/h-e1/visualize.py`)

**Dependencies**: EvaluateModule

```python
import matplotlib.pyplot as plt
from typing import Dict

def plot_cosine_similarity_bar(
    results: Dict[str, float],
    model_name: str,
    output_path: str,
    threshold: float = 0.95
) -> None: ...
def generate_all_figures(
    llama2_results: Dict[str, float],
    mistral_results: Dict[str, float],
    figures_dir: str
) -> None: ...
```

---

### ExperimentRunner (`code/h-e1/run_experiment.py`)

**Dependencies**: Config, TrainModule, EvaluateModule, VisualizeModule

```python
def run_model_pair(model_name: str, baseline_cfg: "TrainingConfig", eviction_cfg: "TrainingConfig") -> dict: ...
def main() -> None: ...
    # 1. Run 4 training jobs (llama2 baseline, llama2 eviction, mistral baseline, mistral eviction)
    # 2. Run weight divergence analysis per model pair
    # 3. Evaluate MUST_WORK gate
    # 4. Generate figures
    # 5. Save gate_result.json
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Config | Project structure, config.py with all TrainingConfig/LoRAConfig definitions, requirements.txt | 5 | 1+1+1+2 |
| A-2 | Data Loading | LongAlpacaDataset, tokenization at max_seq_length=32768, DataLoader with causal LM collator | 7 | 2+1+2+2 |
| A-3 | H2O Attention Wrapper | H2OEvictionAwareAttention: mask construction, logit-level injection, training-only guard | 12 | 3+2+4+3 |
| A-4 | Model Builder | load_base_model, inject_h2o_wrappers, apply_lora, build_model for both conditions | 10 | 2+3+3+2 |
| A-5 | Training Loop | HuggingFace Trainer integration, run_training for all 4 runs, adapter saving | 9 | 2+3+2+2 |
| A-6 | Evaluation & Gate | cosine similarity per layer, gate evaluation (min < 0.95), JSON output, gate_result.json | 8 | 2+1+3+2 |
| A-7 | Visualization & Runner | Bar charts with threshold line, run_experiment.py orchestration of all 4 runs + analysis | 7 | 2+2+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-4, A-5], Low(4-8): [A-1, A-2, A-6, A-7]

---

## External Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| torch | >=2.0.0 | Core tensor ops, cosine_similarity |
| transformers | >=4.36.0 | AutoModelForCausalLM, Trainer, AutoTokenizer |
| peft | >=0.7.0 | LoraConfig, get_peft_model, adapter save/load |
| datasets | >=2.16.0 | load_dataset("Yukang/LongAlpaca-12k") |
| accelerate | >=0.25.0 | Trainer backend |
| matplotlib | >=3.7.0 | Bar chart generation |
| scipy | >=1.11.0 | Optional stats |

---

## Data Flow

- `run_experiment.py` calls `run_training(cfg)` x4 → adapter checkpoints in `outputs/h-e1/`
- `evaluate.py` loads adapter state dicts → computes per-layer cosine similarity → gate JSON
- `visualize.py` reads gate results → writes PNG figures to `docs/.../figures/`

---

## Key Interface: H2O Mask Injection

Mask applied at attention **logit level** (before softmax), training-only (`if self.training`).
Evicted positions set to `-inf` so softmax zeros them out and gradient is blocked.
Wrapper injected per-layer via `inject_h2o_wrappers()` before `get_peft_model()` call.
