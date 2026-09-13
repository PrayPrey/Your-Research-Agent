---
title: "Architecture: h-e1 — Mamba-130m LoRA GLUE Fine-tuning"
hypothesis_id: h-e1
type: EXISTENCE
date: "2026-08-31"
author: yoon303@ust.ac.kr
---

Applied: MambaPEFT projection-layer LoRA pattern (in_proj/out_proj/x_proj, conv1d exclusion, last-token pooling classification head)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field — no existing codebase
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No src/ directory exists.

---

## File Organization

```
h-e1/
  code/
    model.py       # MambaForSequenceClassification + verify_lora_activated
    train.py       # training loop + zero-shot eval, CLI --task arg
    config.py      # single fixed config dataclass
    evaluate.py    # GLUE metric computation + visualization
    run_all.py     # orchestrates 4 tasks, writes results.json
  results/
    results.json
  figures/
```

---

## Modules

### Config (`code/config.py`)

**Dependencies**: none

```python
from dataclasses import dataclass, field
from typing import tuple

@dataclass
class ExperimentConfig:
    model_name: str = "state-spaces/mamba-130m-hf"
    tasks: tuple = ("sst2", "mnli", "qnli", "qqp")
    lora_r: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    target_modules: tuple = ("in_proj", "out_proj", "x_proj")
    max_length: int = 128
    batch_size: int = 32
    epochs: int = 3
    lr: float = 3e-4
    weight_decay: float = 0.01
    warmup_ratio: float = 0.06
    seed: int = 42
    results_dir: str = "h-e1/results"
    figures_dir: str = "h-e1/figures"
```

---

### Model (`code/model.py`)

**Dependencies**: Config

```python
import torch.nn as nn
from transformers import AutoModelForCausalLM
from peft import LoraConfig, get_peft_model
from config import ExperimentConfig

class MambaForSequenceClassification(nn.Module):
    def __init__(self, cfg: ExperimentConfig, num_labels: int): ...
    # backbone: AutoModelForCausalLM (optionally wrapped with PEFT)
    # classifier: nn.Linear(d_model, num_labels)
    def forward(self, input_ids, labels=None) -> dict: ...
    # hidden_states[-1][:, -1, :] -> classifier -> CrossEntropyLoss if labels

def build_lora_model(cfg: ExperimentConfig, num_labels: int) -> MambaForSequenceClassification: ...
    # applies LoraConfig(target_modules=cfg.target_modules, r=cfg.lora_r, ...)
    # MUST assert "conv1d" not in cfg.target_modules

def build_zero_shot_model(cfg: ExperimentConfig, num_labels: int) -> MambaForSequenceClassification: ...
    # same arch, no LoRA, frozen backbone

def verify_lora_activated(model, results_lora: dict, results_zeroshot: dict) -> tuple[bool, dict]: ...
    # checks: lora_A/lora_B keys in state_dict, nonzero weights, sst2 accuracy delta
```

---

### Train (`code/train.py`)

**Dependencies**: Config, Model

```python
from config import ExperimentConfig
import torch

TASK_LABEL_COUNTS = {"sst2": 2, "mnli": 3, "qnli": 2, "qqp": 2}
TASK_TEXT_FIELDS = {"sst2": ("sentence",), "mnli": ("premise","hypothesis"), ...}

def get_dataloaders(task: str, tokenizer, cfg: ExperimentConfig) -> tuple: ...
    # load_dataset("glue", task), tokenize (max_length=128, truncation=True)
    # returns train_loader, val_loader

def train_one_task(task: str, cfg: ExperimentConfig) -> tuple[nn.Module, dict]: ...
    # builds LoRA model via build_lora_model()
    # AdamW + linear_schedule_with_warmup
    # 3-epoch loop with val eval each epoch
    # returns trained model, final val metrics

def eval_model(model, val_loader, task: str, device) -> dict: ...
    # returns {task: metric_value} using compute_glue_metric()

def eval_zero_shot(task: str, cfg: ExperimentConfig) -> dict: ...
    # builds zero-shot model, evals val split

# CLI: python train.py --task sst2
```

---

### Evaluate (`code/evaluate.py`)

**Dependencies**: Config

```python
import evaluate as hf_evaluate
import matplotlib.pyplot as plt
from config import ExperimentConfig

def compute_glue_metric(task: str, preds, labels) -> dict: ...
    # hf_evaluate.load("glue", task).compute(predictions=preds, references=labels)

def compute_glue_avg(results: dict) -> float: ...
    # mean of results["sst2"], results["mnli"], results["qnli"], results["qqp"]

def plot_results(results: dict, cfg: ExperimentConfig) -> None: ...
    # bar chart: zero-shot vs LoRA per task, horizontal line at 0.70
    # 4-subplot loss curves if loss_history provided
    # saves to cfg.figures_dir/comparison.png, cfg.figures_dir/loss_curves.png
```

---

### Run All (`code/run_all.py`)

**Dependencies**: Config, Train, Evaluate, Model

```python
import json
from config import ExperimentConfig
from train import train_one_task, eval_zero_shot
from evaluate import compute_glue_avg, plot_results
from model import verify_lora_activated

def run_experiment(cfg: ExperimentConfig) -> dict: ...
    # for task in cfg.tasks:
    #   zero_shot[task] = eval_zero_shot(task, cfg)
    #   model, lora_results[task] = train_one_task(task, cfg)
    # gate = lora_results["sst2"]["sst2"] > 0.70
    # verify_lora_activated on SST-2 model
    # writes results.json, calls plot_results

# entrypoint: python run_all.py
```

---

## Proposed Epic Tasks

| ID | Task | Description | Files | Complexity | Breakdown |
|----|------|-------------|-------|------------|-----------|
| E1 | Environment + Config | Project dirs, requirements.txt, ExperimentConfig dataclass with all fixed hyperparams | config.py, requirements.txt | 5 | 1+1+1+2 |
| E2 | Model Implementation | MambaForSequenceClassification (last-token pooling), build_lora_model with conv1d guard, build_zero_shot_model | model.py | 12 | 3+3+3+3 |
| E3 | Data Loading | GLUE dataset loading for 4 tasks, tokenization, DataLoader construction per task | train.py (data) | 9 | 2+3+2+2 |
| E4 | Training Loop | Per-task AdamW + linear warmup schedule, 3-epoch loop, val eval per epoch, loss history collection | train.py (train) | 13 | 3+3+4+3 |
| E5 | Zero-shot Evaluation | Eval Mamba-130m without LoRA on 4 GLUE val splits, return per-task metrics | train.py (eval_zero_shot) | 7 | 2+2+2+1 |
| E6 | Metrics + Gate Logic | GLUE metric computation via hf evaluate, glue_avg, verify_lora_activated, gate pass/fail | evaluate.py, model.py | 10 | 2+2+3+3 |
| E7 | Visualization | Bar chart with 70% gate line, 4-subplot loss curves, save to figures_dir | evaluate.py (plot_results) | 7 | 2+1+2+2 |
| E8 | Orchestration + Results | run_all.py: loop tasks, collect results, write results.json with gate_passed field | run_all.py | 8 | 2+3+1+2 |

**Distribution**: High(10-13): [E2, E4, E6], Medium(7-9): [E3, E5, E7, E8], Low(4-6): [E1]
