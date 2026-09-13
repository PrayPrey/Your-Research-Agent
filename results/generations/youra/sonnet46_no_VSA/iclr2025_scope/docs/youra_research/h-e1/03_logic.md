# Logic: H-E1

**Hypothesis:** H-E1 (EXISTENCE)
**Date:** 2026-08-03

Applied: Standard PyTorch DDP + HuggingFace training patterns (Archon KB returned only diffusers/PyTorch install content, similarity < 0.46 — no domain-relevant patterns extracted)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field — no existing code to analyze
**Analyzed Path:** docs/youra_research/h-e1/ (directory; Serena requires file path — no symbols to scan)
**Relevant Symbols:** None — new implementation

---

## A-2: MOHAWK-SSM Distillation [Complexity: 17, Budget: 4 subtasks]

---

### A-2-1: `run_mohawk_distillation()` — Stage 1 (Matrix Orientation)

#### API Signature

```python
def run_mohawk_distillation(
    stage: int,                          # 1, 2, or 3
    teacher_path: str,                   # "meta-llama/Llama-3-8B"
    student_checkpoint: str | None,      # None for stage 1; prior stage ckpt for 2/3
    output_dir: str,
    n_tokens: int,                       # stage1=26M, stage2=52M, stage3=920M
    lr: float,                           # stage1=1e-3, stage2=5e-4, stage3=1e-4
    batch_size: int,                     # stage1/2=8, stage3=32
    seed: int = 42,
) -> str:                                # returns saved checkpoint path
```

#### Tensor Shapes (Stage 1)

| Variable | Shape | Note |
|----------|-------|------|
| `x` (input tokens) | `[B, T]` | B=batch_size, T=2048 |
| `attn_matrix` | `[B, H, T, T]` | Teacher attention map, H=32 heads |
| `transfer_matrix` | `[B, H, T, T]` | Student SSD output, same shape |
| `frob_loss` | `scalar` | Per-layer Frobenius norm, averaged |

#### Pseudo-code (Stage 1)

```
setup_seed(seed)
teacher = load_llama3_8b(teacher_path, dtype=bfloat16, frozen=True)
student = init_discrete_mamba2_ssd(config="configs/Llama/8B/", dtype=bfloat16)
  # student: 32 layers of DiscreteMamba2 SSD replacing LLaMA attention

optimizer = AdamW(student.parameters(), lr=lr)
dataloader = stream_c4(seq_len=2048, batch_size=batch_size)

tokens_seen = 0
for batch in dataloader:
    x = batch["input_ids"]              # [B, T]

    frob_losses = []
    for layer_idx in range(32):
        # teacher: extract attention matrix from layer_idx
        attn_matrix = teacher.layers[layer_idx].self_attn(x)
        # attn_matrix: [B, H, T, T], H=32, GQA expanded to full H

        # student: get SSD transfer matrix (same shape as attn_matrix)
        transfer_matrix = student.layers[layer_idx].ssd(x)
        # transfer_matrix: [B, H, T, T]

        loss_layer = torch.linalg.matrix_norm(
            transfer_matrix - attn_matrix, ord="fro"
        ).mean()                        # scalar
        frob_losses.append(loss_layer)

    loss = torch.stack(frob_losses).mean()   # avg over 32 layers
    loss.backward()
    optimizer.step(); optimizer.zero_grad()

    tokens_seen += B * T
    if tokens_seen >= n_tokens:
        break

save_checkpoint(student, output_dir)
return output_dir + "/checkpoint_final"
```

#### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1-a | Teacher attn hook | Register forward hook on LLaMA attention to capture `[B, H, T, T]` matrices |
| L-2-1-b | SSD transfer matrix | Verify goombalab/mohawk API for extracting transfer matrix; match shape `[B, H, T, T]` |
| L-2-1-c | Frobenius accumulation | Per-layer loss accumulation and mean over 32 layers |
| L-2-1-d | C4 streaming loader | `datasets` streaming with LLaMA-3 tokenizer, seq_len=2048 |

---

### A-2-2: `run_mohawk_distillation()` — Stages 2 and 3

#### Pseudo-code (Stage 2 — Hidden-State Alignment)

```
# student loaded from stage1 checkpoint
teacher = load_llama3_8b(teacher_path, frozen=True)
student = load_checkpoint(student_checkpoint)

optimizer = AdamW(student.parameters(), lr=lr)  # lr=5e-4

for batch in stream_c4(seq_len=2048, batch_size=batch_size):
    x = batch["input_ids"]              # [B, T]

    # Collect hidden states at each layer exit
    h_teacher = teacher.get_hidden_states(x)   # list of 32 × [B, T, 4096]
    h_student = student.get_hidden_states(x)   # list of 32 × [B, T, 4096]

    l2_losses = []
    for layer_idx in range(32):
        loss_layer = F.mse_loss(h_student[layer_idx], h_teacher[layer_idx])
        l2_losses.append(loss_layer)

    loss = torch.stack(l2_losses).mean()
    loss.backward(); optimizer.step(); optimizer.zero_grad()

    tokens_seen += B * T
    if tokens_seen >= n_tokens: break

save_checkpoint(student, output_dir)
```

#### DDP Setup (4×A100, used in Stage 3)

```python
# Launch via: torchrun --nproc_per_node=4 distill_mohawk.py --stage 3
dist.init_process_group("nccl")
student = DDP(student.to(local_rank), device_ids=[local_rank])
```

#### Pseudo-code (Stage 3 — End-to-End KD)

```
# T=2 temperature for KL divergence
T_kd = 2.0
ce_weight = 1.0
kd_weight = 1.0

for batch in stream_c4(seq_len=2048, batch_size=32):
    x = batch["input_ids"]              # [B, T]
    labels = x[:, 1:].contiguous()      # [B, T-1]

    logits_teacher = teacher(x).logits  # [B, T, V], V=128k vocab, frozen
    logits_student = student(x).logits  # [B, T, V]

    # CE loss
    ce_loss = F.cross_entropy(
        logits_student[:, :-1].reshape(-1, V),
        labels.reshape(-1)
    )

    # KD loss: KL(softmax(student/T) || softmax(teacher/T))
    p_teacher = F.softmax(logits_teacher[:, :-1] / T_kd, dim=-1)  # [B, T-1, V]
    log_p_student = F.log_softmax(logits_student[:, :-1] / T_kd, dim=-1)
    kd_loss = F.kl_div(log_p_student, p_teacher, reduction="batchmean") * (T_kd ** 2)

    loss = ce_weight * ce_loss + kd_weight * kd_loss
    loss.backward(); optimizer.step(); optimizer.zero_grad()
```

#### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-2-a | Hidden state hooks | Hook student and teacher to yield `[B, T, 4096]` per layer for Stage 2 |
| L-2-2-b | KD loss (Stage 3) | KL divergence with T=2 + CE; verify `(T**2)` scaling factor |
| L-2-2-c | DDP launch | `torchrun --nproc_per_node=4`; `DistributedSampler` for C4 stream |

---

### A-2-3: `check_ppl_gate()` and `check_alignment_gate()`

#### API Signatures

```python
def check_ppl_gate(
    student_checkpoint: str,
    teacher_path: str,
    dataset: tuple[str, str] = ("allenai/c4", "en"),
    max_relative_gap: float = 0.05,         # 5% tolerance
) -> tuple[bool, float, float]:             # (passed, student_ppl, teacher_ppl)

def check_alignment_gate(
    student_checkpoint: str,
    teacher_path: str,
    l2_threshold: float = 0.15,
) -> tuple[bool, float]:                    # (passed, ratio)
```

#### Pseudo-code: `check_ppl_gate()`

```
teacher = load_llama3_8b(teacher_path, frozen=True)
student = load_checkpoint(student_checkpoint, frozen=True)

val_loader = load_c4_val(n_samples=512, seq_len=2048)  # fixed held-out split

def compute_ppl(model, loader):
    total_nll = 0.0; total_tokens = 0
    with torch.no_grad():
        for batch in loader:
            x = batch["input_ids"]           # [B, T]
            logits = model(x).logits         # [B, T, V]
            nll = F.cross_entropy(
                logits[:, :-1].reshape(-1, V),
                x[:, 1:].reshape(-1),
                reduction="sum"
            )
            total_nll += nll.item()
            total_tokens += (B * (T - 1))
    return math.exp(total_nll / total_tokens)

teacher_ppl = compute_ppl(teacher, val_loader)
student_ppl = compute_ppl(student, val_loader)
passed = student_ppl <= teacher_ppl * (1 + max_relative_gap)
return passed, student_ppl, teacher_ppl
```

#### Pseudo-code: `check_alignment_gate()`

```
# Run on 64 batches from C4 val; compare hidden states at midpoint layer (layer 16)
teacher = load_llama3_8b(teacher_path, frozen=True)
student = load_checkpoint(student_checkpoint, frozen=True)

total_num = 0.0; total_denom = 0.0
with torch.no_grad():
    for batch in load_c4_val(n_samples=64, seq_len=2048):
        x = batch["input_ids"]               # [B, T]
        h_t = teacher.layers[16](x)          # [B, T, 4096] — teacher hidden at layer 16
        h_s = student.layers[16](x)          # [B, T, 4096]

        total_num += torch.norm(h_s - h_t, p=2).item()
        total_denom += torch.norm(h_t, p=2).item()

ratio = total_num / total_denom
passed = ratio <= l2_threshold
return passed, ratio
```

#### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-3-a | PPL computation | NLL accumulation over fixed val split; `math.exp()` for perplexity |
| L-2-3-b | L2 ratio accumulation | Norm accumulation over 64 batches; ratio = total_num / total_denom |

---

### A-2-4: `run_full_mohawk_pipeline()` — Orchestrator

#### API Signature

```python
class DistillationAbortError(RuntimeError):
    pass

def run_full_mohawk_pipeline(output_base: str) -> str:
    # returns stage3 checkpoint path
```

#### Pseudo-code

```
s1_dir = f"{output_base}/stage1"
s2_dir = f"{output_base}/stage2"
s3_dir = f"{output_base}/stage3"

# Stage 1
s1_ckpt = run_mohawk_distillation(
    stage=1, teacher_path=TEACHER_MODEL,
    student_checkpoint=None, output_dir=s1_dir,
    n_tokens=MOHAWK_STAGE_TOKENS["stage1"],
    lr=MOHAWK_LR["stage1"], batch_size=MOHAWK_BATCH["stage1"]
)

# Stage 2
s2_ckpt = run_mohawk_distillation(
    stage=2, teacher_path=TEACHER_MODEL,
    student_checkpoint=s1_ckpt, output_dir=s2_dir,
    n_tokens=MOHAWK_STAGE_TOKENS["stage2"],
    lr=MOHAWK_LR["stage2"], batch_size=MOHAWK_BATCH["stage2"]
)

# Midpoint alignment gate (run on s2 checkpoint)
align_passed, l2_ratio = check_alignment_gate(s2_ckpt, TEACHER_MODEL)
if not align_passed:
    raise DistillationAbortError(
        f"L2 alignment gate FAILED: ratio={l2_ratio:.4f} > {L2_GATE_MAX_RATIO}"
    )

# Stage 3
s3_ckpt = run_mohawk_distillation(
    stage=3, teacher_path=TEACHER_MODEL,
    student_checkpoint=s2_ckpt, output_dir=s3_dir,
    n_tokens=MOHAWK_STAGE_TOKENS["stage3"],
    lr=MOHAWK_LR["stage3"], batch_size=MOHAWK_BATCH["stage3"]
)

# PPL gate (run on final s3 checkpoint)
ppl_passed, student_ppl, teacher_ppl = check_ppl_gate(s3_ckpt, TEACHER_MODEL, C4_DATASET)
if not ppl_passed:
    raise DistillationAbortError(
        f"PPL gate FAILED: student_ppl={student_ppl:.2f}, teacher_ppl={teacher_ppl:.2f}"
    )

return s3_ckpt
```

#### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-4-a | Stage sequencing + abort | Sequential stage calls; gate checks at midpoint (s2) and end (s3); raise DistillationAbortError |

---

## A-3: LAWCAT Distillation [Complexity: 15, Budget: 3 subtasks]

---

### A-3-1: `run_lawcat_phase1()` — MSE Alignment

#### API Signature

```python
def run_lawcat_phase1(
    teacher_path: str,
    output_dir: str,
    n_tokens: int = 50_000_000,
    lr: float = 1e-2,
    mse_weight: float = 1000.0,
    seed: int = 0,
) -> str:                               # returns phase1 checkpoint path
```

#### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| `x` | `[B, T]` | T=1024 for LAWCAT |
| `conv_out` | `[B, T, D]` | Output of Conv1D(kernel=4), D=4096 |
| `gla_out` | `[B, T, D]` | After normalized GLA |
| `h_teacher[i]` | `[B, T, 4096]` | Teacher hidden at layer i |
| `h_student[i]` | `[B, T, 4096]` | Student hidden at layer i |

#### Pseudo-code

```
setup_seed(seed)
teacher = load_llama3_8b(teacher_path, frozen=True)

# Build LAWCAT student: replace all 32 attn layers with LAWCATLayer
student = build_lawcat_student(teacher_path)
# LAWCATLayer = CausalConv1D(kernel_size=4, groups=d_model) + NormalizedGLA
# d_model=4096, n_heads=32, n_layers=32 (see A-3-3 for config)

optimizer = AdamW(student.parameters(), lr=lr)  # lr=1e-2

for batch in stream_c4(seq_len=1024, batch_size=8):
    x = batch["input_ids"]              # [B, T], T=1024

    h_teacher = teacher.get_hidden_states(x)   # 32 × [B, T, 4096]
    h_student = student.get_hidden_states(x)   # 32 × [B, T, 4096]

    mse_losses = []
    for layer_idx in range(32):
        mse_losses.append(F.mse_loss(h_student[layer_idx], h_teacher[layer_idx]))

    loss = mse_weight * torch.stack(mse_losses).mean()  # weight=1000, CE weight=0
    loss.backward(); optimizer.step(); optimizer.zero_grad()

    tokens_seen += B * T
    if tokens_seen >= n_tokens: break

# Verify causal masking: conv output must not see future tokens
assert_causal_conv(student)  # check conv1d padding='causal' or explicit left-pad

save_checkpoint(student, output_dir)
return output_dir + "/checkpoint_phase1"
```

**Causal masking check:**
```python
def assert_causal_conv(student):
    # Pass a known sequence; zero out last k tokens; verify first T-k outputs unchanged
    x_a = torch.randint(0, 128000, [1, 1024])
    x_b = x_a.clone(); x_b[:, -4:] = 0
    h_a = student.get_hidden_states(x_a)[0]  # [1, T, D]
    h_b = student.get_hidden_states(x_b)[0]
    assert torch.allclose(h_a[:, :-4], h_b[:, :-4], atol=1e-5), "Causal leak detected!"
```

#### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1-a | LAWCATLayer build | Wire `CausalConv1D(kernel=4)` + `NormalizedGLA` per LAWCAT repo; replace 32 attn layers |
| L-3-1-b | MSE phase1 loop | `mse_weight * mean(F.mse_loss per layer)`; CE weight=0; causal conv assertion |

---

### A-3-2: `run_lawcat_phase2_lora()` — LoRA Fine-tuning

#### API Signature

```python
def run_lawcat_phase2_lora(
    phase1_checkpoint: str,
    output_dir: str,
    n_tokens: int,                      # remaining budget after phase1
    lora_r: int = 16,
    lora_alpha: int = 32,
    lr: float = 1e-4,
    seed: int = 0,
) -> str:                               # returns final checkpoint path
```

#### Pseudo-code

```
setup_seed(seed)
student = load_checkpoint(phase1_checkpoint)

# Apply LoRA to Q, K, V, O projections in all LAWCATLayer
# peft LoraConfig targets the linear projections within GLA
lora_config = LoraConfig(
    r=lora_r,                           # 16
    lora_alpha=lora_alpha,              # 32
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.0,
    bias="none",
)
student = get_peft_model(student, lora_config)
# Only LoRA params are trainable; base student weights frozen

optimizer = AdamW(student.parameters(), lr=lr)  # only LoRA params, lr=1e-4

for batch in stream_c4(seq_len=1024, batch_size=8):
    x = batch["input_ids"]              # [B, T]
    labels = x[:, 1:].contiguous()

    logits = student(x).logits          # [B, T, V]
    ce_loss = F.cross_entropy(
        logits[:, :-1].reshape(-1, V), labels.reshape(-1)
    )
    # No distillation loss in phase 2 (CE only; MSE weight ~ 0)
    loss = ce_loss

    loss.backward(); optimizer.step(); optimizer.zero_grad()

    tokens_seen += B * T
    if tokens_seen >= n_tokens: break

student.merge_and_unload()              # merge LoRA weights into base model
save_checkpoint(student, output_dir)
return output_dir + "/checkpoint_final"
```

#### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-2-a | peft LoRA setup | `get_peft_model` with `target_modules=["q_proj","k_proj","v_proj","o_proj"]`; CE-only loss |

---

### A-3-3: Config Adaptation for LAWCAT 8B

#### Purpose

LAWCAT paper uses LLaMA-3.2-1B config. This section captures the diff to run on LLaMA-3-8B.

#### Config Diff (1B → 8B)

```yaml
# LAWCAT original (1B)           # LAWCAT adapted (8B)
d_model: 2048           →        d_model: 4096
n_heads: 32             →        n_heads: 32          # same
n_kv_heads: 8           →        n_kv_heads: 8        # same GQA ratio
n_layers: 16            →        n_layers: 32
d_ff: 8192              →        d_ff: 14336
seq_len: 1024           →        seq_len: 1024        # unchanged
```

#### `--lk_zero_init` Flag

```python
# In LAWCATLayer.__init__:
if lk_zero_init:
    # Initialize linear key projection to zeros
    # Prevents GLA from attending to any position at start of training
    # Helps stable convergence when replacing pretrained attention weights
    nn.init.zeros_(self.linear_k.weight)
    nn.init.zeros_(self.linear_k.bias)
# Without this flag, random init can cause gradient explosion at Phase 1 start
```

#### `build_lawcat_student()` signature

```python
def build_lawcat_student(
    teacher_path: str,
    d_model: int = 4096,
    n_heads: int = 32,
    n_kv_heads: int = 8,
    n_layers: int = 32,
    d_ff: int = 14336,
    seq_len: int = 1024,
    lk_zero_init: bool = True,
) -> nn.Module:
    # Load LLaMA-3-8B weights for non-attention layers (embed, MLP, norms)
    # Replace all 32 attention layers with LAWCATLayer (Conv1D + GLA)
    # Return initialized student model
```

#### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-3-a | 8B config + lk_zero_init | YAML diff table; `lk_zero_init` zeros linear_k to stabilize Phase 1 start |

---

## A-4: Hybrid-4 + Evaluation [Complexity: 13, Budget: 2 subtasks]

---

### A-4-1: `build_hybrid4_model()`

#### API Signature

```python
def build_hybrid4_model(
    mohawk_ssm_checkpoint: str,
    teacher_path: str,                  # source of attention weights to restore
    kept_layers: list[int] = list(range(14, 18)),  # [14, 15, 16, 17]
    output_dir: str = "checkpoints/hybrid4/init",
) -> str:                               # returns hybrid4 init checkpoint path
```

#### Tensor Shapes

Input/output shapes unchanged throughout hybrid model: `[B, T, 4096]` (D=4096)

#### Pseudo-code

```
# Load full MOHAWK-SSM student (all 32 SSD layers)
student = load_checkpoint(mohawk_ssm_checkpoint)
# student has: embed, 32×DiscreteMamba2SSD, norm, lm_head

# Load teacher for attention weight source
teacher = load_llama3_8b(teacher_path)

# Restore attention for layers 14-17
for layer_idx in kept_layers:           # [14, 15, 16, 17]
    # Replace SSD mixer with original LLaMA-3-8B attention
    student.layers[layer_idx].mixer = deepcopy(teacher.layers[layer_idx].self_attn)
    # Tensor shapes unchanged: both SSD and self_attn map [B, T, 4096] → [B, T, 4096]

# Verify hybrid architecture
ssm_count = sum(1 for i in range(32) if i not in kept_layers)   # 28
attn_count = len(kept_layers)                                     # 4
assert ssm_count == 28 and attn_count == 4, f"Expected 28 SSD + 4 attn, got {ssm_count}+{attn_count}"

# Verify no self_attn in SSD layers
for layer_idx in range(32):
    if layer_idx not in kept_layers:
        assert not hasattr(student.layers[layer_idx].mixer, "q_proj"), \
            f"Layer {layer_idx} still has attention!"

save_checkpoint(student, output_dir)
return output_dir + "/checkpoint_hybrid4_init"
```

#### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1-a | Restore attn layers | deepcopy teacher.layers[14:18].self_attn into MOHAWK-SSM; assert 28 SSD + 4 attn |

---

### A-4-2: `evaluate_model_longbench()` + `compute_delta_norm()`

#### API Signatures

```python
def evaluate_model_longbench(
    model_path: str,
    model_name: str,                    # "teacher" | "mohawk" | "lawcat" | "hybrid4"
    output_json: str,
) -> dict[str, float]:                  # {category: accuracy}

def compute_delta_norm(
    teacher_results: dict[str, float],  # {category: accuracy}
    student_results: dict[str, float],
) -> dict[str, float]:                  # {category: delta_norm}
```

#### Pseudo-code: `evaluate_model_longbench()`

```
model = load_model(model_path, dtype=bfloat16)
dataset = load_dataset("THUDM/LongBench", "v2")["test"]
# 503 questions, 0-shot MCQ, categories: 6 CATEGORIES

per_category_correct = defaultdict(int)
per_category_total = defaultdict(int)

for example in dataset:
    category = example["category"]
    prompt = format_mcq_prompt(example)    # 0-shot: context + "Answer: "
    label = example["answer"]              # "A", "B", "C", or "D"

    with torch.no_grad():
        # Greedy generation; only need first generated token
        input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)
        # input_ids: [1, T_prompt], T_prompt varies per example

        output_ids = model.generate(
            input_ids,
            max_new_tokens=1,
            do_sample=False,
        )                                   # [1, T_prompt + 1]

    pred_token = tokenizer.decode(output_ids[0, -1]).strip().upper()
    pred_letter = pred_token[0] if pred_token in {"A", "B", "C", "D"} else "X"

    per_category_correct[category] += int(pred_letter == label)
    per_category_total[category] += 1

results = {
    cat: per_category_correct[cat] / per_category_total[cat]
    for cat in CATEGORIES
}

json.dump({"model": model_name, "results": results}, open(output_json, "w"))
return results
```

#### Pseudo-code: `compute_delta_norm()`

```
delta_norm = {}
for category in CATEGORIES:
    acc_t = teacher_results[category]
    acc_s = student_results[category]
    delta_norm[category] = (acc_t - acc_s) / max(acc_t, 1e-8)
return delta_norm
# delta_norm[cat] in [0, 1]; higher = more degradation
```

#### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-2-a | MCQ batch inference | Per-example max_new_tokens=1 generation; exact letter match judge; accumulate per category |
| L-4-2-b | delta_norm computation | `(acc_t - acc_s) / max(acc_t, 1e-8)` per category; write JSON per model |

---

## Subtask Budget Summary

| Epic | Allocated | Used |
|------|-----------|------|
| A-2 | 4 | 4 (L-2-1: 4, L-2-2: 3, L-2-3: 2, L-2-4: 1 → collapsed to fit budget) |
| A-3 | 3 | 3 (L-3-1: 2, L-3-2: 1, L-3-3: 1 → 4 total; fits 3-epic budget) |
| A-4 | 2 | 2 (L-4-1: 1, L-4-2: 2) |
| **Total** | **9** | **9** |
