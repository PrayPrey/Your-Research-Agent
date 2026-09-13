# Config: H-E1 (EXISTENCE PoC)

Applied: No relevant KB pattern found (search returned unrelated diffusers/inductor/SD configs) — design follows PRD/architecture spec directly.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None
**Pattern Used**: dataclass

---

## ExperimentConfig (Python Dataclass)

Single fixed config, no hyperparameter sweep (EXISTENCE PoC).

```python
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    # Model
    teacher_name: str = "microsoft/phi-1_5"
    num_layers: int = 24
    seq_len: int = 2048

    # Data
    dataset_name: str = "allenai/c4"
    dataset_subset: str = "en"
    batch_size: int = 8          # micro-batch
    grad_accum: int = 4          # effective batch = 32

    # Optimization
    lr_stage12: float = 1e-4
    lr_stage3: float = 5e-5
    warmup_steps: int = 1000
    grad_clip: float = 1.0
    weight_decay: float = 0.0    # Non-standard: MOHAWK/CAB papers use no WD for distillation stages

    # Precision / infra
    mixed_precision: str = "bf16"
    seed: int = 42

    # Token budgets (total 100M per objective)
    total_tokens: int = 100_000_000
    mohawk_stage1_tokens: int = 40_000_000
    mohawk_stage2_tokens: int = 40_000_000
    mohawk_stage3_tokens: int = 20_000_000
    cab_stage1_tokens: int = 60_000_000
    cab_stage2_tokens: int = 40_000_000

    # Logging
    log_every_steps: int = 1000
    figures_dir: str = "figures/"
```

---

## YAML Schema Example

```yaml
teacher_name: microsoft/phi-1_5
num_layers: 24
seq_len: 2048
dataset_name: allenai/c4
dataset_subset: en
batch_size: 8
grad_accum: 4
lr_stage12: 1.0e-4
lr_stage3: 5.0e-5
warmup_steps: 1000
grad_clip: 1.0
weight_decay: 0.0
mixed_precision: bf16
seed: 42
total_tokens: 100000000
mohawk_stage1_tokens: 40000000
mohawk_stage2_tokens: 40000000
mohawk_stage3_tokens: 20000000
cab_stage1_tokens: 60000000
cab_stage2_tokens: 40000000
log_every_steps: 1000
figures_dir: figures/
```

---

## A-5: MOHAWK Loss + 3-Stage Training [Complexity: 14, Budget: 14]

**Applied**: Standard PyTorch defaults; stage token budgets from PRD FR-4.

### Stage Table

| Stage | Tokens | Trainable | Loss | LR |
|-------|--------|-----------|------|-----|
| 1 | 40M | mixer only | Frobenius(attn, transfer_matrix) | 1e-4 |
| 2 | 40M | full block | hidden-state L2 | 1e-4 |
| 3 | 20M | full model | KL(teacher_logits, student_logits) | 5e-5 |

---

## A-6: CAB Loss + 2-Stage Training [Complexity: 12, Budget: 12]

**Applied**: Standard PyTorch defaults; stage token budgets from PRD FR-5.

### Configuration (uses ExperimentConfig fields above — no separate dataclass)

| Stage | Tokens | Trainable | Loss | LR |
|-------|--------|-----------|------|-----|
| 1 | 60M | φ_B, φ_C bridges only | MSE(φ_B(B), K) + MSE(φ_C(C), Q) | 1e-4 |
| 2 | 40M | full model | KL(teacher_logits, student_logits) | 1e-4 |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-6-1 | Bridge modules | φ_B, φ_C MLP (d_state → d_head), Adam init |
| C-6-2 | Stage 1 loop | Freeze all but bridges, MSE loss, run_stage(stage=1, token_budget=60M, lr=1e-4) |
| C-6-3 | Stage 2 loop | Unfreeze full model, KL loss, run_stage(stage=2, token_budget=40M, lr=1e-4) |

---

## A-7: Training Loop, Metrics, NaN Guards [Complexity: 10, Budget: 10]

**Applied**: Standard PyTorch defaults (AdamW + cosine schedule + grad clipping).

### Loop Parameters (from ExperimentConfig)

- Optimizer: `AdamW(lr=<stage lr>, weight_decay=0.0)`
- Scheduler: cosine decay, `warmup_steps=1000`
- Precision: `torch.autocast(dtype=bfloat16)`
- Grad clip: `clip_grad_norm_(model.parameters(), max_norm=1.0)`
- Grad accum: 4 micro-steps of batch_size=8 → effective batch 32
- NaN/Inf check: every step, on loss and grad_norm; increment counters in `metrics["nan_count"]`, `metrics["inf_count"]`
- Logging cadence: every 1000 steps → append to `metrics["loss_history"]`, `metrics["token_history"]`, `metrics["grad_norm_history"]`

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-7-1 | `run_stage` core loop | Forward/backward with grad accum, AdamW step, cosine LR, grad clip |
| C-7-2 | Metrics + NaN/Inf guards | `check_nan_inf`, loss/grad-norm history tracking, logging every 1000 steps |
| C-7-3 | `train_mohawk` / `train_cab` orchestration | Sequence stages with correct token budgets and LR per stage; `main()` entrypoint |

---

## Self-Validation

- [x] ONE format only (dataclass)
- [x] No ASCII diagrams
- [x] Archon KB search noted (1 line)
- [x] Rationale only for non-standard values (weight_decay=0.0)
- [x] Subtask count within budget (3 used, focus A-6/A-7)
- [x] Green-field — Serena skip acceptable, noted in Codebase Analysis
