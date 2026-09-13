# Logic Specification: H-M3

**Date:** 2026-08-28
**Hypothesis:** H-M3 - Task-Conditioned SSM Training
**Type:** MECHANISM (full spec, not PoC)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - designing new APIs. H-M1/H-M2 exist only as prior hypothesis documents (no `code/` artifacts to verify signatures against); state-spaces/mamba is an external dependency, not an in-repo base.
**Analyzed Path:** N/A
**Relevant Symbols:** None - new implementation

---

## A-1: TaskConditionedSSMBlock [Complexity: High, Budget: 4]

**Applied:** Low-rank adapter modulation (PEFT-style) + selective SSM (Mamba)

### API Signatures

```python
class TaskConditionedSSMBlock(nn.Module):
    def __init__(
        self,
        d_model: int = 768,
        d_state: int = 16,
        d_conv: int = 4,
        expand: int = 2,
        rank: int = 32,
        n_tasks: int = 8,
    ):
        """Mamba block with task-conditioned Delta/B/C modulation."""
        ...

    def forward(self, x: Tensor, task_ids: Tensor) -> Tensor:
        """x: [B, L, D] , task_ids: [B] -> [B, L, D]"""
        ...

    def forward_with_modulation(
        self,
        x: Tensor,
        delta_mod: Tensor,
        bc_mod: Tensor,
    ) -> Tensor:
        """x: [B, L, D], delta_mod: [B, D_inner], bc_mod: [B, 2*d_state] -> [B, L, D]"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| x | [B, L, D] | D = d_model = 768 |
| D_inner | scalar | expand * D = 1536 |
| task_emb | [B, rank] | rank = 32 |
| delta_mod | [B, D_inner] | added pre-softplus to dt |
| bc_mod | [B, 2*d_state] | split into B_mod, C_mod, each [B, d_state] |
| xz | [B, L, 2*D_inner] | in_proj output |
| x_conv | [B, D_inner, L] | after conv1d + activation |
| delta, B_ssm, C_ssm | [B, L, D_inner], [B, L, d_state], [B, L, d_state] | from x_proj/dt_proj |
| h (state) | [B, D_inner, d_state] | recurrent SSM state |
| y | [B, L, D_inner] | scan output |
| out | [B, L, D] | out_proj output |

### Pseudo-code

```
# forward()
1. task_emb = task_embedding(task_ids)                      # [B, rank]
2. delta_mod = delta_up(delta_down(task_emb))                # [B, D_inner]
3. bc_mod = bc_up(bc_down(task_emb))                          # [B, 2*d_state]
4. return forward_with_modulation(x, delta_mod, bc_mod)

# forward_with_modulation(x, delta_mod, bc_mod)
1. xz = in_proj(x)                                            # [B, L, 2*D_inner]
2. x_in, z = split(xz, dim=-1)                                # each [B, L, D_inner]
3. x_conv = activation(conv1d(x_in.transpose(1,2))[..., :L])  # [B, D_inner, L]
4. x_conv = x_conv.transpose(1, 2)                            # [B, L, D_inner]
5. delta_raw, B_raw, C_raw = split(x_proj(x_conv), [D_inner, d_state, d_state], dim=-1)
6. B_mod, C_mod = split(bc_mod, d_state, dim=-1)              # each [B, d_state]
7. delta = softplus(dt_proj(delta_raw) + delta_mod.unsqueeze(1))   # broadcast over L -> [B, L, D_inner]
8. B_ssm = B_raw + B_mod.unsqueeze(1)                         # [B, L, d_state]
9. C_ssm = C_raw + C_mod.unsqueeze(1)                         # [B, L, d_state]
10. h = zeros(B, D_inner, d_state)
11. for t in range(L):                                        # selective scan (sequential; use parallel scan kernel in production)
        dA_t = exp(delta[:, t] .unsqueeze(-1) * A)             # [B, D_inner, d_state]
        dB_t = delta[:, t].unsqueeze(-1) * B_ssm[:, t].unsqueeze(1)  # [B, D_inner, d_state]
        h = h * dA_t + dB_t * x_conv[:, t].unsqueeze(-1)
        y[:, t] = einsum('bdn,bn->bd', h, C_ssm[:, t])
12. y = y + x_conv * D_param                                  # skip connection, D_param: [D_inner]
13. y = y * silu(z)                                            # gating
14. out = out_proj(y)                                          # [B, L, D]
15. log.debug(f"TC-SSM: Task conditioning applied, task_id={task_ids}")
16. return out
```

### Complexity
- Sequential scan: O(L * D_inner * d_state) per sample -> O(B * L * D_inner * d_state) total.
- Modulation overhead: O(B * rank * (D_inner + d_state)) — negligible vs scan (<2% per H-M2).
- Memory: O(B * D_inner * d_state) for state h (no growth with L).

### Edge Cases
- `task_ids` out of `[0, n_tasks)` range -> raises IndexError from `nn.Embedding`; validate upstream in dataloader.
- `L=1` (single-token decode step): skip loop, single scan update, used for incremental generation.
- Empty batch (`B=0`): short-circuit return `x` unchanged, skip embedding lookup (avoids div-by-zero in norm layers downstream).
- Mixed dtypes (bf16 activations, fp32 state `h`): cast `h` to fp32 internally for numerical stability, cast back to `x.dtype` at return.

---

## A-2: ConversionTrainer [Complexity: High, Budget: 4]

**Applied:** Knowledge distillation (KL + hidden MSE) with auxiliary adaptation-preserving regularizer

### API Signatures

```python
class ConversionTrainer:
    def __init__(
        self,
        student: TaskConditionedSSMBlock,
        teacher: nn.Module,          # frozen BERT-base / GPT-2-small
        kl_weight: float = 1.0,
        mse_weight: float = 0.5,
        adapt_reg_weight: float = 0.1,
        temperature: float = 2.0,
    ):
        ...

    def compute_loss(
        self,
        input_ids: Tensor,
        attention_mask: Tensor,
        task_ids: Tensor,
    ) -> dict[str, Tensor]:
        """Returns dict with keys: total, kl, mse, adapt_reg. All scalar tensors."""
        ...

    def adaptation_regularizer(
        self,
        student_hidden: Tensor,
        task_ids: Tensor,
    ) -> Tensor:
        """student_hidden: [B, L, D] -> scalar. Penalizes collapse of task-conditioned variance."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids, attention_mask | [B, L] | tokenized batch |
| teacher_logits, student_logits | [B, L, V] | V = vocab size |
| teacher_hidden, student_hidden | [B, L, D] | last hidden state |
| task_ids | [B] | |
| kl_loss, mse_loss, adapt_reg, total | scalar | |

### Pseudo-code

```
# compute_loss(input_ids, attention_mask, task_ids)
1. with torch.no_grad():
       teacher_out = teacher(input_ids, attention_mask=attention_mask, output_hidden_states=True)
       teacher_logits = teacher_out.logits                       # [B, L, V]
       teacher_hidden = teacher_out.hidden_states[-1]             # [B, L, D]
2. student_out = student(input_ids, task_ids=task_ids)            # forward through TC-SSM stack
   student_logits = student_out.logits                            # [B, L, V]
   student_hidden = student_out.hidden_states[-1]                 # [B, L, D]
3. kl = KLDiv(
        log_softmax(student_logits / T, dim=-1),
        softmax(teacher_logits / T, dim=-1),
        reduction='batchmean'
     ) * T**2
4. mse = MSELoss()(student_hidden, teacher_hidden)
5. adapt_reg = adaptation_regularizer(student_hidden, task_ids)
6. total = kl_weight*kl + mse_weight*mse + adapt_reg_weight*adapt_reg
7. return {"total": total, "kl": kl, "mse": mse, "adapt_reg": adapt_reg}

# adaptation_regularizer(student_hidden, task_ids)
# Goal: prevent conversion training from collapsing task-conditioned diversity
# (i.e. ensure different tasks still produce distinguishable representations)
1. pooled = student_hidden.mean(dim=1)                # [B, D] mean-pool over L
2. for each unique task t in task_ids:
       group_mean[t] = pooled[task_ids == t].mean(dim=0)   # [D]
3. between_task_var = var(stack(group_mean.values()), dim=0).mean()   # scalar
4. reg = -between_task_var   # negative: maximize inter-task variance (minimize its negative)
   # clamp to avoid unbounded negative loss dominating total
5. reg = clamp(reg, min=-10.0)
6. return reg
```

### Complexity
- Teacher forward: O(L^2 * D) (standard transformer attention), run under `no_grad` — no backward cost.
- Student forward: O(L * D_inner * d_state) per TC-SSM layer (linear in L, dominant advantage over teacher).
- `adaptation_regularizer`: O(B * D) grouping, negligible.

### Edge Cases
- Single task present in batch (`len(unique(task_ids)) == 1`): `between_task_var` undefined (variance of one point = 0) -> `adapt_reg=0`, skip regularizer term for that step (log warning, do not raise).
- Teacher/student vocab mismatch: assert `teacher_logits.shape[-1] == student_logits.shape[-1]` at trainer init; raise `ValueError` early if mismatched tokenizers.
- NaN in KL (zero-probability teacher tokens under low temperature): use `F.kl_div` with `log_target=False` and clamp teacher probs with `eps=1e-8` before log.
- Gradient clipping applied post `total.backward()`: `torch.nn.utils.clip_grad_norm_(student.parameters(), max_norm=1.0)` per PRD.

---

## A-3: FewShotEvaluator [Complexity: Medium, Budget: 3]

**Applied:** Standard k-shot fine-tune-then-eval protocol (PEFT/LoRA-style adaptation loop)

### API Signatures

```python
class FewShotEvaluator:
    def __init__(
        self,
        model: nn.Module,
        tasks: list[str] = ["boolq", "cb", "copa", "rte", "wic"],
        k_shots: list[int] = [8, 16],
        max_steps: int = 100,
        seeds: list[int] = [0, 1, 2],
    ):
        ...

    def run_task(self, task: str, k: int, seed: int) -> dict:
        """Returns {'accuracy': float, 'steps_to_95pct': int|None, 'per_step_acc': list[float]}"""
        ...

    def run_all(self) -> dict:
        """Returns {task: {k: {'mean_acc': float, 'std_acc': float, 'mean_steps': float}}}"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| support_set | k examples | stratified sample, k in {8,16} |
| query_set | full val split | e.g. BoolQ val = 3270 |
| logits | [B, n_classes] | n_classes task-dependent (2 for BoolQ/RTE/WiC, 3 for CB, 2 for COPA) |

### Pseudo-code

```
# run_task(task, k, seed)
1. set_seed(seed)
2. support = stratified_sample(train_split[task], k=k, seed=seed)
3. query = val_split[task]                                     # full val set
4. adapted_model = deepcopy(model)                              # fresh copy per (task, k, seed)
5. optimizer = AdamW(adapted_model.parameters(), lr=2e-5, betas=(0.9,0.999), weight_decay=0.01)
6. scheduler = linear_warmup_decay(optimizer, warmup_ratio=0.1, total_steps=max_steps)
7. ceiling_acc = None   # computed after full run or via known ref; use best acc observed as proxy ceiling
8. per_step_acc = []
9. for step in range(max_steps):
       batch = sample_batch(support, batch_size=8, cycle=True)  # cycles since k may be < batch_size
       loss = cross_entropy(adapted_model(batch, task_ids=task_to_id[task]).logits, batch.labels)
       loss.backward()
       clip_grad_norm_(adapted_model.parameters(), 1.0)
       optimizer.step(); scheduler.step(); optimizer.zero_grad()
       if step % 5 == 0 or step == max_steps - 1:
           acc = evaluate(adapted_model, query, task_ids=task_to_id[task])
           per_step_acc.append((step, acc))
10. final_acc = per_step_acc[-1][1]
11. ceiling = max(a for _, a in per_step_acc)
12. steps_to_95pct = next((s for s, a in per_step_acc if a >= 0.95 * ceiling), None)
13. return {"accuracy": final_acc, "steps_to_95pct": steps_to_95pct, "per_step_acc": per_step_acc}

# run_all()
1. results = {}
2. for task in tasks:
       for k in k_shots:
           runs = [run_task(task, k, seed) for seed in seeds]
           results[task][k] = {
               "mean_acc": mean([r["accuracy"] for r in runs]),
               "std_acc": std([r["accuracy"] for r in runs]),
               "mean_steps": mean([r["steps_to_95pct"] or max_steps for r in runs]),
           }
3. return results
```

### Complexity
- Per (task, k, seed): O(max_steps * batch_size * forward_cost) + O(eval_interval * |val_set| * forward_cost).
- Total: O(|tasks| * |k_shots| * |seeds| * max_steps) = 5 * 2 * 3 * 100 = 3000 adaptation steps total.

### Edge Cases
- `k < batch_size` (k=8, batch_size=8 boundary; k could be < 8 for edge configs): sample with replacement (`cycle=True`) to fill batch.
- CB task has 3 classes vs binary tasks: `n_classes` read from task metadata, classifier head sized dynamically per task (or per-task head swap).
- `steps_to_95pct` never reached within `max_steps`: return `None`, downstream aggregation treats as `max_steps` (penalize, per `run_all` mean_steps computation above).
- Task-to-id mapping for unseen task at eval time: raise `KeyError` early with explicit message rather than silent embedding index 0 fallback.
- Val set > 500 samples: no subsampling per PRD (statistically meaningful); if val set < 500 (e.g., COPA val=100), use full set and flag low-N in report.

---

## External Dependencies (External Library, not in-repo)

```python
# From: transformers.MambaForCausalLM (HuggingFace) - reference only, not modified
# TC-SSM replaces MambaBlock internals per-layer; in_proj/x_proj/dt_proj/out_proj
# names below match state-spaces/mamba official naming convention.
class MambaBlock(nn.Module):
    def __init__(self, d_model: int, d_state: int = 16, d_conv: int = 4, expand: int = 2):
        self.in_proj = nn.Linear(d_model, expand * d_model * 2)
        self.conv1d = nn.Conv1d(expand * d_model, expand * d_model, d_conv, groups=expand*d_model, padding=d_conv-1)
        self.x_proj = nn.Linear(expand * d_model, d_state * 2 + expand * d_model)  # dt, B, C
        self.dt_proj = nn.Linear(expand * d_model, expand * d_model)
        self.out_proj = nn.Linear(expand * d_model, d_model)
```

**Verified from:** state-spaces/mamba public repo (WebFetch, no local `code/` present — MCP/Serena unavailable per 02c brief). Names to be re-verified against actual installed `mamba-ssm` package version at Phase 4 implementation time.

---

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs (Applied: X only)
- [x] Docstrings <= 2 lines
- [x] Tensor shapes in comments/tables
- [x] Subtask/complexity budgets noted per task
- [x] Total length < 600 lines
- [x] Codebase Analysis (Serena) section included
