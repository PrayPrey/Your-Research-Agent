# Logic: H-E1 (EXISTENCE PoC)

Budget: 4 subtasks. Focus: A-3 (Phi-Mamba student mixer), A-5 (MOHAWK 3-stage training).

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

**Applied**: No relevant KB pattern found (Archon search for "Mamba-2 mixer transfer matrix API" returned unrelated CUDA docs) — design follows architecture spec + goombalab/phi-mamba conventions directly.

---

## A-3: Phi-Mamba Student + Mamba-2 Mixer [Complexity: 16, Budget: 16]

**Applied**: Standard PyTorch (Mamba-2 SSD scan, vendored minimal impl)

### API Signatures

```python
class Mamba2Mixer(nn.Module):
    def __init__(self, d_model: int, d_state: int = 64, n_heads: int = 32, d_head: int = 64, chunk_size: int = 256):
        """Mamba-2 SSD mixer. d_model = n_heads * d_head."""
        ...

    def forward(self, x: Tensor, return_mixer_matrix: bool = False,
                return_bc: bool = False) -> dict:
        """x: [B, L, D] -> {"hidden_states": [B, L, D],
        "transfer_matrix"?: [B, H, L, L], "B"?: [B, L, H, N], "C"?: [B, L, H, N]}"""
        ...

class PhiMambaLayer(nn.Module):
    def __init__(self, hidden_size: int, num_heads: int, d_state: int):
        """hidden_size = num_heads * d_head. Wraps Mamba2Mixer + norm + MLP."""
        ...

    def forward(self, hidden_states: Tensor, return_mixer_matrix: bool = False,
                return_bc: bool = False) -> dict:
        """hidden_states: [B, L, D] -> dict (see Mamba2Mixer.forward)"""
        ...

class PhiMambaStudent(nn.Module):
    def __init__(self, config: ExperimentConfig):
        """Stacks config.num_layers PhiMambaLayer blocks + embedding + lm_head."""
        ...

    def forward(self, input_ids: Tensor, layer_idx: Optional[int] = None,
                return_mixer_matrix: bool = False, return_bc: bool = False) -> dict:
        """input_ids: [B, L] -> {"logits": [B, L, V], "hidden_states": list[[B,L,D]],
        "layer_out"?: dict from PhiMambaLayer.forward at layer_idx}"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| x / hidden_states | [B, L, D] | D = num_heads * d_head |
| transfer_matrix | [B, H, L, L] | Materialized SSM transfer matrix (lower-triangular), compared to teacher attention |
| B (SSM input gate) | [B, L, H, N] | N = d_state |
| C (SSM output gate) | [B, L, H, N] | N = d_state |

### Pseudo-code (transfer_matrix construction — non-trivial)

```
1. compute per-token SSM params: A [B,L,H], B [B,L,H,N], C [B,L,H,N], dt [B,L,H]
2. discretize: dA = exp(dt * A)                       # [B,L,H]
3. cumulative decay: dA_cumsum[i,j] = prod(dA[j+1:i+1])  for j <= i  # [B,H,L,L] lower-tri
4. transfer_matrix[b,h,i,j] = C[b,i,h] @ B[b,j,h] * dA_cumsum[b,h,i,j]  if j<=i else 0
5. hidden_states = transfer_matrix @ x_proj  (chunked scan in practice, materialized only if return_mixer_matrix)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | Mamba2Mixer core scan | SSD chunked scan, produces hidden_states [B,L,D] |
| L-3-2 | transfer_matrix materialization | return_mixer_matrix=True path, [B,H,L,L] |
| L-3-3 | B/C extraction + PhiMambaLayer wrap | return_bc=True path, norm/MLP wrapper |
| L-3-4 | PhiMambaStudent stacking | embed, 24-layer stack, layer_idx dict passthrough |

---

## A-5: MOHAWK Loss + 3-Stage Training [Complexity: 14, Budget: 14]

**Applied**: Standard PyTorch (staged distillation loop)

### API Signatures

```python
def mohawk_loss(teacher_out: "TeacherOutput", student_layer_out: dict, stage: int) -> Tensor:
    """stage1: Frobenius(attn, transfer_matrix). stage2: += L2(hidden_states).
    stage3: KL(student_logits, teacher_logits). Returns scalar."""
    ...

def train_mohawk(framework: "UnifiedDistillationFramework", dataloader: Iterator[dict],
                  config: ExperimentConfig) -> dict:
    """Runs stages 1-3 sequentially. Returns metrics dict."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| teacher_out.attentions[l] | [B, H, L, L] | Per-layer attention matrix |
| student_layer_out["transfer_matrix"] | [B, H, L, L] | Compared via Frobenius norm |
| hidden_states (stage 2) | [B, L, D] | L2 loss vs teacher hidden_states |
| logits (stage 3) | [B, L, V] | KL(softmax(student), softmax(teacher)) |

### Pseudo-code (3-stage loop)

```
for stage, (token_budget, lr) in [(1, (40M, 1e-4)), (2, (40M, 1e-4)), (3, (20M, 5e-5))]:
    freeze_params(stage)  # stage1: mixer only; stage2: full block; stage3: full model
    opt = AdamW(trainable_params(stage), lr=lr)
    sched = cosine_warmup(opt, warmup_steps=1000)
    tokens_seen = 0
    while tokens_seen < token_budget:
        batch = next(dataloader)                        # input_ids [B, L]
        teacher_out = teacher.forward(batch["input_ids"])
        student_out = student.forward(batch["input_ids"], layer_idx=cur_layer,
                                       return_mixer_matrix=(stage==1))
        loss = mohawk_loss(teacher_out, student_out["layer_out"], stage)
        loss.backward()
        grad_norm = clip_grad_norm_(trainable_params(stage), config.grad_clip)
        check_nan_inf(loss, grad_norm, metrics)
        opt.step(); sched.step(); opt.zero_grad()
        tokens_seen += batch["input_ids"].numel()
        log_every_1000_steps(loss, grad_norm, metrics)
return metrics
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | mohawk_loss stage1 (Frobenius) | ||attn - transfer_matrix||_F |
| L-5-2 | mohawk_loss stage2 (hidden L2) | Adds hidden-state L2 term, unfreezes full block |
| L-5-3 | mohawk_loss stage3 (KL) | KL(student_logits, teacher_logits), unfreezes full model |
| L-5-4 | train_mohawk orchestration | Stage loop, freeze/unfreeze, optimizer/sched per stage, metrics wiring |

---

## Notes for Remaining Tasks (Out of Budget — Follow Architecture Spec Directly)

- A-4 (CAB bridges): `Bridge(nn.Module)` per architecture — simple 2-layer MLP `d_state -> d_head`, MSE loss. No new API design needed beyond `03_architecture.md`.
- A-6 (CAB loss + 2-stage): mirrors A-5 pattern (bridge stage MSE, then KL stage) at `stage in {1,2}` — reuse `cab_loss` signature from architecture.
- A-7/A-8: infra/plotting, signatures already fully specified in architecture (`check_nan_inf`, `plot_loss_curves`, `check_gate_criteria`) — no additional logic needed.
