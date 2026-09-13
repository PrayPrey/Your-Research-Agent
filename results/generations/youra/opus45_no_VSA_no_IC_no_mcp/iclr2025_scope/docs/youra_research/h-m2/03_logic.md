# Logic: H-M2 (TC-SSM)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: API signatures verified from base code
**Analyzed Path**: `docs/youra_research/h-m1/code/models/task_embedding.py`
**Relevant Symbols**: `TaskEmbeddingEncoder.__init__(hidden_dim: int, embedding_dim: int, num_tasks: int = 8)`, `forward(hidden_states: Tensor[B,seq,hidden_dim]) -> Tensor[B,embedding_dim]` (mean-pooled). No custom checkpoint-loader method exists — use standard `load_state_dict` + `torch.load`.

---

## External Dependencies (Base Hypothesis)

```python
# From: docs/youra_research/h-m1/code/models/task_embedding.py (ACTUAL CODE)
class TaskEmbeddingEncoder(nn.Module):
    def __init__(self, hidden_dim: int, embedding_dim: int, num_tasks: int = 8): ...
    def forward(self, hidden_states: Tensor) -> Tensor:
        """[B, seq, hidden_dim] -> [B, embedding_dim] (mean pool)"""
        ...
```
Load frozen: `encoder = TaskEmbeddingEncoder(...); encoder.load_state_dict(torch.load(ckpt_path)); encoder.eval(); encoder.requires_grad_(False)`.

---

## A-4: TaskConditionedMamba [Complexity: 14, Budget: 14]

**Applied**: LoRA-style low-rank modulation (Hu et al. 2021)

### API Signatures

```python
class LowRankProjection(nn.Module):
    def __init__(self, task_emb_dim: int, target_dim: int, rank: int = 32):
        """down: Linear(task_emb_dim, rank, bias=False), up: Linear(rank, target_dim, bias=False), up.weight zero-init."""
        ...

    def forward(self, task_embedding: Tensor) -> Tensor:
        # task_embedding: [B, task_emb_dim] -> [B, target_dim]
        ...


class TaskConditionedMamba(nn.Module):
    def __init__(
        self,
        d_model: int,
        d_state: int,
        task_emb_dim: int,
        rank: int = 32,
        variant: Literal["all_matrices", "delta_only"] = "all_matrices",
    ):
        ...

    def forward(self, x: Tensor, task_embedding: Tensor) -> Tensor:
        # x: [B, L, d_model], task_embedding: [B, task_emb_dim] -> [B, L, d_model]
        ...

    def get_state(self, x: Tensor, task_embedding: Tensor) -> Tensor:
        # returns final SSM hidden state for variance analysis: [B, d_model, d_state]
        ...

    def _modulate(self, base: Tensor, mod_proj: Optional[LowRankProjection], task_embedding: Tensor) -> Tensor:
        # base: [B, L, D], mod_proj may be None (variant=="delta_only" skips B/C)
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| x | [B, L, d_model] | d_model=1024 |
| task_embedding | [B, task_emb_dim] | from H-M1, frozen |
| delta, delta_mod | [B, L, d_model], [B, d_model] | mod broadcasts over L |
| B_mat, C_mat, B_mod, C_mod | [B, L, d_state], [B, d_state] | d_state=16 |
| state (get_state) | [B, d_model, d_state] | final recurrent state |

### Pseudo-code

```
forward(x, task_embedding):
    delta = delta_proj(x)                       # [B,L,d_model]
    B_mat = B_proj(x)                            # [B,L,d_state]
    C_mat = C_proj(x)                            # [B,L,d_state]

    delta = delta + delta_task_mod(task_embedding).unsqueeze(1)
    if variant == "all_matrices":
        B_mat = B_mat + B_task_mod(task_embedding).unsqueeze(1)
        C_mat = C_mat + C_task_mod(task_embedding).unsqueeze(1)
    # else (delta_only): B_mat, C_mat unmodified

    delta = softplus(delta)                      # ensure positive discretization step
    y = selective_scan(x, delta, A, B_mat, C_mat)  # mamba_ssm selective_scan_fn, [B,L,d_model]
    return y

get_state(x, task_embedding):
    # same as forward but return last recurrent state instead of output
    # h_t = exp(delta_t * A) * h_{t-1} + delta_t * B_t * x_t ; return h_L
```

### Subtasks [14/14 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | LowRankProjection | down/up linear + zero-init up |
| L-4-2 | Base Δ/B/C projections | linear layers matching mamba dims |
| L-4-3 | Modulation + variant switch | additive broadcast, delta_only skip |
| L-4-4 | selective_scan integration + get_state | call mamba_ssm scan, expose state |

---

## A-6: FLOPs/Overhead Measurement [Complexity: 10, Budget: 10]

**Applied**: Standard PyTorch (torch.profiler + wall-clock timing)

### API Signatures

```python
def count_flops(model: nn.Module, input_shape: tuple, task_emb_shape: Optional[tuple] = None) -> float:
    """Returns total CPU/CUDA time (proxy for FLOPs) via torch.profiler."""
    ...

def measure_overhead(
    vanilla_model: nn.Module,
    tc_model: nn.Module,
    inputs: Tensor,
    task_embeddings: Tensor,
    n_warmup: int = 10,
    n_iters: int = 100,
) -> float:
    # returns tc_time / vanilla_time
    ...

def per_matrix_breakdown(tc_model: "TaskConditionedMamba", inputs: Tensor, task_embeddings: Tensor) -> dict:
    # {"delta": time_s, "B": time_s, "C": time_s, "base_ssm": time_s}
    ...
```

### Pseudo-code (timing protocol)

```
measure_overhead(vanilla, tc, x, task_emb):
    for _ in range(n_warmup): vanilla(x); tc(x, task_emb)
    sync()
    t0 = perf_counter()
    for _ in range(n_iters): vanilla(x)
    sync(); vanilla_time = perf_counter() - t0

    sync()
    t0 = perf_counter()
    for _ in range(n_iters): tc(x, task_emb)
    sync(); tc_time = perf_counter() - t0

    return tc_time / vanilla_time

per_matrix_breakdown(tc_model, x, task_emb):
    # monkeypatch or hook each *_task_mod submodule with torch.profiler.record_function
    # aggregate per-tag CPU time from prof.key_averages()
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | count_flops | profiler wrapper, CPU/CUDA activities |
| L-6-2 | measure_overhead | warmup + timed loop + ratio |
| L-6-3 | per_matrix_breakdown | record_function tags per Δ/B/C mod |

---

## A-7: State Variance Analysis [Complexity: 8, Budget: 8]

**Applied**: scipy.stats.f_oneway (ANOVA)

### API Signatures

```python
def measure_state_variance(
    tc_model: "TaskConditionedMamba",
    inputs: Tensor,
    task_embeddings_list: list[Tensor],
) -> dict:
    """Returns {'state_variances': list[float], 'f_statistic': float, 'p_value': float, 'significant': bool}"""
    ...
```

### Pseudo-code

```
measure_state_variance(tc_model, x, task_embs):
    states = []
    for task_emb in task_embs:
        with no_grad():
            state = tc_model.get_state(x, task_emb)   # [B, d_model, d_state]
        states.append(state.flatten().cpu().numpy())
    f_stat, p_value = scipy.stats.f_oneway(*states)
    return {
        "state_variances": [s.var() for s in states],
        "f_statistic": f_stat, "p_value": p_value,
        "significant": p_value < 0.05,
    }
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | State collection loop | call get_state per task embedding |
| L-7-2 | ANOVA + result dict | f_oneway + significance flag |

---

## A-8: Rank Ablation Framework [Complexity: 9, Budget: 9]

**Applied**: Standard PyTorch grid sweep

### API Signatures

```python
def run_rank_ablation(
    ranks: list[int] = [16, 32, 64],
    d_model: int = 1024,
    d_state: int = 16,
    task_emb_dim: int = 128,
) -> dict:
    # returns {rank: {"overhead": float, "state_variance": dict}}
    ...

def run_matrix_ablation(
    variants: list[str] = ["delta_only", "all_matrices"],
    rank: int = 32,
) -> dict:
    # returns {variant: {"overhead": float}}
    ...
```

### Pseudo-code

```
run_rank_ablation(ranks, ...):
    results = {}
    for r in ranks:
        tc_model = TaskConditionedMamba(d_model, d_state, task_emb_dim, rank=r)
        vanilla = VanillaMambaWrapper(d_model, d_state)
        overhead = measure_overhead(vanilla, tc_model, x, task_emb)
        variance = measure_state_variance(tc_model, x, task_emb_list)
        results[r] = {"overhead": overhead, "state_variance": variance}
    return results

run_matrix_ablation(variants, rank):
    for v in variants:
        tc_model = TaskConditionedMamba(..., rank=rank, variant=v)
        results[v] = {"overhead": measure_overhead(vanilla, tc_model, x, task_emb)}
```

### Subtasks [9/9 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | run_rank_ablation | sweep rank=16/32/64, reuse fixed x/task_emb |
| L-8-2 | run_matrix_ablation | sweep delta_only vs all_matrices |
| L-8-3 | Result aggregation | dict merge for visualize.py consumption |

---

## Data Flow

```
BoolQ/RTE/WiC samples --tokenize--> hidden_states [B,seq,hidden_dim]
  --> TaskEmbeddingEncoder.forward (frozen) --> task_embedding [B,task_emb_dim]

x [B,L,d_model] + task_embedding
  --> TaskConditionedMamba.forward --> y [B,L,d_model]
  --> TaskConditionedMamba.get_state --> state [B,d_model,d_state]

(vanilla_model, tc_model, x, task_embedding)
  --> measure_overhead --> overhead_ratio (float)
  --> per_matrix_breakdown --> {delta,B,C,base_ssm times}

(tc_model, x, [task_embedding_per_task])
  --> measure_state_variance --> {variances, f_stat, p_value, significant}

run_rank_ablation / run_matrix_ablation --> results dict --> visualize.py --> figures
```

---

## Edge Cases and Error Handling

- **rank >= min(task_emb_dim, target_dim)**: log warning ("low-rank projection degenerates to full-rank"); do not error, still run.
- **variant == "delta_only"**: `B_task_mod`/`C_task_mod` must be `None`; `_modulate` must skip gracefully (no AttributeError).
- **task_embeddings_list with < 2 tasks**: `f_oneway` requires >=2 groups — raise `ValueError("need >=2 task embeddings for ANOVA")` before calling scipy.
- **CUDA unavailable**: `measure_overhead`/`get_state` must guard `torch.cuda.synchronize()` calls with `if torch.cuda.is_available()`.
- **Frozen encoder accidentally in train mode**: assert `not task_embedding_encoder.training` before use in `run_experiment.py`.
- **Mismatched d_state/d_model between vanilla and TC-SSM**: `measure_overhead` should assert both models share `d_model`/`d_state` config before timing (else ratio meaningless).
- **Empty/short seq_len (L=1)**: mean-pool in `get_state`/`forward` still valid; selective_scan handles L=1 trivially — no special-case needed.
