# Logic: H-M3 (Objective x Length F1 Retention, 2x3 Factorial)

Applied: standard PyTorch MSE distillation + AdamW/cosine training loop (no direct KB match — real MOHAWK/CAB training has no prior implementation in this pipeline).

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m2/code/ exists)
**Status**: Serena has no active project registered for this cwd (same limitation H-M2 hit). Used direct `Read` on `h-m2/code/model.py` and `config.py` to verify actual signatures.
**Analyzed Path**: `docs/youra_research/h-m2/code/`
**Relevant Symbols**: `load_teacher(config) -> (model, tokenizer)`, `load_student(config, variant, teacher=None) -> model`, `get_student_dim(model) -> int`, `CABUnavailableError`
**Finding**: H-M2's `load_student` returns the identical `state-spaces/mamba-1.4b-hf` proxy for both `"mohawk"` and `"cab"` — no real distillation training exists to import. H-M3 implements real MOHAWK matrix-loss and CAB token-loss training from scratch (per architecture doc). Only style/pattern reuse: `AnalysisConfig`-style dataclass, `load_teacher` signature shape, `get_student_dim` fallback logic.

Budget note: 7 subtasks allocated to C-2, C-4, C-6 only (per task instruction). C-1/C-3/C-5/C-7/C-8/C-9/C-10 signatures are in `03_architecture.md`; not re-specified here.

---

## C-2: MOHAWK + CAB Loss Implementation [Complexity: 10, Budget: 3 subtasks]

**Applied**: `F.mse_loss` matrix/token distillation, small MLP bridge (standard PyTorch)

### API Signatures

```python
# losses.py
import torch
from torch import nn, Tensor
import torch.nn.functional as F
from typing import Tuple

class AttentionBridge(nn.Module):
    def __init__(self, d_model: int, hidden_dim: int = None):
        """MLP bridge: teacher Q/K -> student B/C target space."""
        super().__init__()
        hidden_dim = hidden_dim or d_model * 2
        self.q_to_b = nn.Sequential(nn.Linear(d_model, hidden_dim), nn.GELU(), nn.Linear(hidden_dim, d_model))
        self.k_to_c = nn.Sequential(nn.Linear(d_model, hidden_dim), nn.GELU(), nn.Linear(hidden_dim, d_model))

    def forward(self, q: Tensor, k: Tensor) -> Tuple[Tensor, Tensor]:
        """q,k: [B, N, D] -> (b_target, c_target): [B, N, D]"""
        return self.q_to_b(q), self.k_to_c(k)


def mohawk_matrix_loss(teacher_attn: Tensor, student_mixer_matrix: Tensor) -> Tensor:
    """teacher_attn, student_mixer_matrix: [B, H, N, N] -> scalar."""
    return F.mse_loss(student_mixer_matrix, teacher_attn)


def cab_token_loss(
    teacher_q: Tensor, teacher_k: Tensor,
    student_b: Tensor, student_c: Tensor,
    bridge: AttentionBridge,
) -> Tensor:
    """teacher_q/k, student_b/c: [B, N, D] -> scalar (sum of two MSE terms)."""
    b_target, c_target = bridge(teacher_q, teacher_k)
    return F.mse_loss(student_b, b_target) + F.mse_loss(student_c, c_target)


def extract_teacher_attn(teacher_layer_output, num_heads: int) -> Tensor:
    """Recompute softmax(QK^T/sqrt(d)) from teacher attention module. -> [B, H, N, N]"""
    ...

def extract_student_mixer(student_layer_output) -> Tensor:
    """Pull Mamba-2 SSM mixer matrix M from student layer forward hook. -> [B, H, N, N]"""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| teacher_attn | [B, H, N, N] | softmax(QK^T/sqrt(d)), H=teacher heads |
| student_mixer_matrix | [B, H, N, N] | Mamba-2 M matrix, same N (post length-matched forward) |
| teacher_q, teacher_k | [B, N, D] | D=2048 (teacher hidden dim) |
| student_b, student_c | [B, N, D] | D=2048 (post any dim-matching linear if student dim differs) |
| bridge output | [B, N, D] | q_to_b(q), k_to_c(k) |

### Pseudo-code (matrix-vs-token loss dispatch)

```
compute_loss(objective, teacher_out, student_out, bridge=None):
    if objective == "mohawk":
        t_attn = extract_teacher_attn(teacher_out, num_heads)
        s_mix = extract_student_mixer(student_out)
        return mohawk_matrix_loss(t_attn, s_mix)
    if objective == "cab":
        t_q, t_k = teacher_out.q, teacher_out.k
        s_b, s_c = student_out.b, student_out.c
        return cab_token_loss(t_q, t_k, s_b, s_c, bridge)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | `AttentionBridge` module | q_to_b/k_to_c MLPs, forward returns (b_target, c_target) |
| L-2-2 | `mohawk_matrix_loss` + attn/mixer extraction hooks | teacher attn recompute, student M-matrix hook, MSE |
| L-2-3 | `cab_token_loss` + dispatch | bridge-based MSE sum, `compute_loss` objective router |

---

## C-4: Distillation Training Loop (6 conditions) [Complexity: 15, Budget: 2 subtasks]

**Applied**: AdamW + cosine schedule, gradient accumulation, periodic checkpointing (standard HF/PyTorch pattern)

### API Signatures

```python
# train.py
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR

def train_condition(
    config: ExperimentConfig,
    objective: str,          # "mohawk" | "cab"
    length: int,             # 4096 | 16384 | 32768
    teacher: nn.Module,
    tokenizer,
) -> nn.Module:
    """Fresh student (+bridge if cab); trains tokens_per_condition tokens; checkpoints every 500M tokens."""
    ...

def save_checkpoint(model: nn.Module, bridge: Optional[nn.Module], optimizer, step: int, tokens_seen: int, path: str) -> None: ...

def load_checkpoint(path: str, model: nn.Module, bridge: Optional[nn.Module], optimizer) -> int:
    """Returns tokens_seen to resume from (0 if no checkpoint found)."""
    ...

def train_all_conditions(config: ExperimentConfig) -> Dict[str, nn.Module]:
    """Loop 2 objectives x 3 lengths -> train_condition. Returns {"mohawk_4096": model, ...}."""
    ...
```

### Pseudo-code (checkpointing + smoke-mode)

```
train_condition(config, objective, length, teacher, tokenizer):
    student = load_student_base(config)                     # fresh Mamba copy
    bridge = AttentionBridge(d_model) if objective == "cab" else None
    params = list(student.parameters()) + (list(bridge.parameters()) if bridge else [])
    opt = AdamW(params, lr=config.lr, weight_decay=config.weight_decay)
    total_tokens = config.tokens_per_condition if not smoke else 1_000_000  # --smoke override
    sched = CosineAnnealingLR(opt, T_max=total_tokens // (config.batch_size * length))

    ckpt_dir = f"{config.checkpoint_dir}/{objective}_{length}"
    tokens_seen = load_checkpoint(f"{ckpt_dir}/latest.pt", student, bridge, opt)  # resume support
    next_ckpt_at = ((tokens_seen // 500_000_000) + 1) * 500_000_000

    stream = get_c4_stream(config, tokenizer, length)
    for step, batch in enumerate(stream):
        try:
            with torch.no_grad():
                teacher_out = teacher(batch["input_ids"], output_attentions=True, output_hidden_states=True)
            student_out = student(batch["input_ids"], output_hidden_states=True)
            loss = compute_loss(objective, teacher_out, student_out, bridge) / config.grad_accum
            loss.backward()
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache(); opt.zero_grad(); continue  # OOM-safe skip

        if (step + 1) % config.grad_accum == 0:
            torch.nn.utils.clip_grad_norm_(params, 1.0)
            opt.step(); sched.step(); opt.zero_grad()

        tokens_seen += batch["input_ids"].numel()
        if tokens_seen >= next_ckpt_at:
            save_checkpoint(student, bridge, opt, step, tokens_seen, f"{ckpt_dir}/step_{tokens_seen}.pt")
            save_checkpoint(student, bridge, opt, step, tokens_seen, f"{ckpt_dir}/latest.pt")
            next_ckpt_at += 500_000_000
        if tokens_seen >= total_tokens:
            break
    return student

train_all_conditions(config):
    teacher, tokenizer = load_teacher(config)
    models = {}
    for objective in config.objectives:
        for length in config.lengths:
            models[f"{objective}_{length}"] = train_condition(config, objective, length, teacher, tokenizer)
    return models
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | `train_condition` core loop | fresh student/bridge, AdamW+cosine, grad accum, OOM-safe skip, smoke-mode token cap |
| L-4-2 | Checkpointing + `train_all_conditions` orchestration | `save_checkpoint`/`load_checkpoint` every 500M tokens, resume, 2x3 condition loop |

---

## C-6: Generation + F1 Evaluation [Complexity: 9, Budget: 2 subtasks]

**Applied**: greedy/short-sample generation + LongBench token-F1 (standard eval pattern)

### API Signatures

```python
# generate.py
def generate_response(model: nn.Module, tokenizer, prompt: str, max_new_tokens: int = 128) -> str:
    """model.generate(**tokenizer(prompt), max_new_tokens=..., do_sample=False) -> decoded str."""
    ...

# metrics.py
def qa_f1_score(prediction: str, ground_truth: str) -> float:
    """Token-overlap F1 (LongBench eval.py normalize_answer + bag-of-words F1)."""
    ...

def evaluate_condition(
    model: nn.Module, tokenizer,
    samples_by_length: Dict[int, List[dict]],
    length: int,
) -> Dict[str, List[float]]:
    """Generate+score all samples at this length. Returns {task_name: [f1, ...]}."""
    ...

def f1_retention(student_f1: float, teacher_f1: float) -> float:
    """(student_f1 / teacher_f1) * 100."""
    return (student_f1 / teacher_f1) * 100
```

### Pseudo-code (evaluate_condition)

```
evaluate_condition(model, tokenizer, samples_by_length, length):
    scores = defaultdict(list)
    for sample in samples_by_length[length]:
        pred = generate_response(model, tokenizer, sample["prompt"])
        f1 = max(qa_f1_score(pred, gt) for gt in sample["answers"])  # multi-ref max, LongBench convention
        scores[sample["task"]].append(f1)
    return dict(scores)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | `generate_response` + `qa_f1_score` | greedy generation, LongBench normalize+bag-of-words F1 |
| L-6-2 | `evaluate_condition` + `f1_retention` | per-task/per-length aggregation loop, multi-ref max-F1, retention ratio |

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

```python
# From: h-m2/code/model.py (ACTUAL CODE)
def load_teacher(config) -> Tuple[nn.Module, AutoTokenizer]:
    """AutoModelForCausalLM.from_pretrained(teacher_name, dtype=fp16, device_map='auto'); .eval()"""
    ...

def get_student_dim(model: nn.Module) -> int:
    """model.config.hidden_size, fallback model.config.d_model, else 2048."""
    ...
```

**Verified from**: `docs/youra_research/h-m2/code/model.py`, `config.py` (actual implementation via Read — Serena inactive for this cwd)

**No direct training-code import**: H-M2's `load_student` used an identical Mamba proxy for both `mohawk`/`cab` variants — real MOHAWK matrix-loss and CAB token-loss training (C-2, C-4) has no prior implementation to reuse. Only `load_teacher` signature shape and `get_student_dim` fallback logic carry over into `model.py`.
