# Logic Design: H-M4 - Task-Dependent Transformation Emergence

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-E1, H-M2, H-M3)
**Status**: API signatures verified from actual implementation (not specs)
**Analyzed Path**: `docs/youra_research/{h-e1,h-m2,h-m3}/code/`
**Relevant Symbols**:
- `h-m2/code/model.py::MambaWithLoRA`, `load_proposed_model(vocab_size, d_model, n_layers)`
- `h-m2/code/sharpness.py::measure_task_sharpness(model, dataloader, max_batches, sam_epsilon)`
- `h-m2/code/finetune.py::finetune_on_task(task_name, tokenizer, train_config, output_dir)`
- `h-m3/code/rank.py::compute_model_effective_rank(model, threshold)`
- `h-m3/code/correlate.py::compute_spearman(sharpness_vals, rank_vals)` (pattern reused for density/delta)
- `h-e1/code/model.py::MambaWithLoRA`, `MambaBlockSimulated` (fallback when `mamba_ssm` unavailable)

**Note**: H-E1's Transformer baseline loads `Llama-2-7B` (not a from-scratch d_model=512 Transformer). H-M4 PRD (FR-2) requires a custom small Transformer — no existing `TransformerWithLoRA` class found in any prior hypothesis. **New implementation required.**

---

## External Dependencies (Base Hypothesis)

```python
# From: h-m2/code/model.py (ACTUAL CODE)
def load_proposed_model(vocab_size: int = 50304, d_model: int = 1024, n_layers: int = 8) -> MambaWithLoRA:
    """Returns unwrapped MambaWithLoRA (apply peft LoRA separately)."""
    ...

# From: h-m2/code/sharpness.py (ACTUAL CODE)
def measure_task_sharpness(model, dataloader, max_batches: int = 100, sam_epsilon: float = 0.05) -> dict:
    """Returns {'mean_sharpness': float, 'per_batch': list[float]}"""
    ...

# From: h-m2/code/finetune.py (ACTUAL CODE)
def finetune_on_task(task_name: str, tokenizer, train_config: dict = None, output_dir: str = None) -> dict:
    """Returns {'model': nn.Module, 'loss_curve': list[float], 'checkpoint_path': str}"""
    ...

# From: h-m3/code/rank.py (ACTUAL CODE)
def compute_model_effective_rank(model, threshold: float = None) -> dict:
    """Returns {'effective_rank': int, 'mean_effective_rank': float, 'per_module': dict, 'singular_values': dict}"""
    ...

# From: h-m3/code/correlate.py (ACTUAL CODE, pattern reused)
def compute_spearman(sharpness_vals: list, rank_vals: list) -> dict:
    """Returns {'rho': float, 'p_value': float, 'gate_pass': bool}"""
    ...
```

**Verified from**: `h-m2/code/`, `h-m3/code/` (actual implementation).

---

## A-1: Benchmark Data Pipeline [Complexity: 3, Budget: 3]

**Applied**: HuggingFace `datasets.load_dataset`, standard PyTorch `DataLoader` collate pattern (matches `h-m2/code/data.py::load_task_loader`).

### API Signatures

```python
# retrieval_density.py
RETRIEVAL_DENSITY: dict[str, float] = {
    "gsm8k": 0.1,
    "mmlu": 0.5,
    "hotpot_qa": 0.7,
    "natural_questions": 0.9,
}

# data.py
def load_benchmark_suite(
    tokenizer,
    max_length: int = 512,
    batch_size: int = 4,
) -> dict[str, dict]:
    """Load 4 benchmarks. Returns {task_name: {'loader': DataLoader, 'density': float, 'n_samples': int}}"""
    ...

def load_single_benchmark(task_name: str, tokenizer, max_length: int, batch_size: int) -> "DataLoader":
    """Dispatch to per-dataset loader; tokenize -> input_ids/labels/attention_mask [B, 512]"""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [4, 512] | batch=4, seq_len=512 |
| attention_mask | [4, 512] | 1=real, 0=pad |
| labels | [4, 512] | shifted internally by model loss |

### Pseudo-code

```
load_benchmark_suite(tokenizer, max_length, batch_size):
    suite = {}
    for task_name, density in RETRIEVAL_DENSITY.items():
        try:
            loader = load_single_benchmark(task_name, tokenizer, max_length, batch_size)
        except Exception as e:
            raise RuntimeError(f"Failed to load {task_name}: {e}")
        suite[task_name] = {"loader": loader, "density": density, "n_samples": len(loader.dataset)}
    total = sum(v["n_samples"] for v in suite.values())
    assert total > 0, "No samples loaded across benchmark suite"
    return suite
```

### Subtasks [2/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A1-1 | dataset dispatch | gsm8k/mmlu/hotpot_qa/nq loaders -> tokenized DataLoader |
| L-A1-2 | density mapping | Static dict, task_name -> retrieval_density |

---

## A-2: Transformer Baseline (New) [Complexity: 4, Budget: 4]

**Applied**: Standard `nn.TransformerEncoder` causal LM, mirrors `h-m2/code/model.py::MambaWithLoRA` interface (embedding -> layers -> norm -> lm_head, same `Output` object with `.loss`/`.logits`) for drop-in symmetry with Mamba.

### API Signatures

```python
# transformer_model.py
class TransformerWithLoRA(nn.Module):
    def __init__(
        self,
        d_model: int = 512,
        n_heads: int = 8,
        n_layers: int = 4,
        vocab_size: int = 50304,
        max_seq_len: int = 512,
    ):
        """Causal decoder-only Transformer, same I/O contract as h-m2 MambaWithLoRA."""
        ...

    def forward(
        self,
        input_ids: "Tensor",       # [B, L]
        attention_mask: "Tensor" = None,  # [B, L]
        labels: "Tensor" = None,   # [B, L]
    ) -> "Output":  # .loss: Tensor|None, .logits: [B, L, V]
        ...


def load_baseline_model(vocab_size: int = 50304, d_model: int = 512, n_layers: int = 4) -> TransformerWithLoRA:
    """Mirrors h-m2 load_proposed_model() signature for symmetry. No LoRA applied yet."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| x (embed) | [B, L, 512] | B=4, L=512 |
| attn causal mask | [L, L] | `nn.Transformer.generate_square_subsequent_mask` |
| logits | [B, L, vocab_size] | |

### Pseudo-code

```
TransformerWithLoRA.forward(input_ids, attention_mask, labels):
    x = embedding(input_ids) + pos_embedding[:, :L]          # [B, L, 512]
    causal_mask = generate_square_subsequent_mask(L)          # [L, L]
    key_padding_mask = (attention_mask == 0) if attention_mask is not None else None
    x = transformer_encoder(x, mask=causal_mask, src_key_padding_mask=key_padding_mask)
    logits = lm_head(final_norm(x))                           # [B, L, V]
    loss = None
    if labels is not None:
        loss = cross_entropy(logits[:, :-1].reshape(-1, V), labels[:, 1:].reshape(-1))
    return Output(loss=loss, logits=logits)
```

### Subtasks [2/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A2-1 | TransformerWithLoRA class | encoder stack, causal mask, lm_head |
| L-A2-2 | load_baseline_model | init wrapper matching h-m2 pattern |

---

## A-3: Training & Evaluation [Complexity: 4, Budget: 5]

**Applied**: Reuse `finetune_on_task` pattern from `h-m2/code/finetune.py` (AdamW + LinearLR warmup/decay), generalized to accept either model loader.

### API Signatures

```python
# train_eval.py
def train_and_evaluate(
    model_type: str,           # "transformer" | "mamba"
    task_name: str,
    tokenizer,
    loader: "DataLoader",
    train_config: dict = None,
) -> dict:
    """
    LoRA-finetune model_type on task_name, then compute accuracy + sharpness + rank.
    Returns {
        'accuracy': float, 'sharpness': float, 'effective_rank': int,
        'loss_curve': list[float], 'checkpoint_path': str,
    }
    """
    ...

def compute_accuracy(model, eval_loader, task_name: str) -> float:
    """Exact-match (gsm8k/hotpot_qa/nq) or MCQ accuracy (mmlu). Returns [0, 1]."""
    ...
```

### Pseudo-code

```
train_and_evaluate(model_type, task_name, tokenizer, loader, train_config):
    build_fn = load_baseline_model if model_type == "transformer" else load_proposed_model  # h-m2 reuse
    lora_targets = ["q_proj","v_proj"] if model_type == "transformer" else ["in_proj"]

    result = finetune_on_task(task_name, tokenizer, train_config)   # reuse h-m2/finetune.py, model swapped internally
    model = result["model"]

    accuracy = compute_accuracy(model, loader, task_name)
    sharp = measure_task_sharpness(model, loader, max_batches=100, sam_epsilon=0.05)   # reuse h-m2/sharpness.py
    rank = compute_model_effective_rank(model, threshold=0.90)                          # reuse h-m3/rank.py

    return {
        "accuracy": accuracy,
        "sharpness": sharp["mean_sharpness"],
        "effective_rank": rank["effective_rank"],
        "loss_curve": result["loss_curve"],
        "checkpoint_path": result["checkpoint_path"],
    }
```

**Error handling**: wrap `finetune_on_task` in try/except; on OOM, retry once with `batch_size //= 2`; on persistent failure, log task/model_type and return `accuracy=None` (excluded from correlation, not silently zeroed).

### Subtasks [2/5 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A3-1 | train_and_evaluate | orchestrates finetune + accuracy + sharpness + rank |
| L-A3-2 | compute_accuracy | task-specific exact-match / MCQ scoring |

---

## A-4: Efficiency Delta & Correlation [Complexity: 3, Budget: 3]

**Applied**: `scipy.stats.spearmanr`, identical pattern to `h-m3/code/correlate.py::compute_spearman`.

### API Signatures

```python
# analysis.py
def compute_efficiency_delta(transformer_metrics: dict, mamba_metrics: dict) -> dict:
    """
    Per task: delta = mamba[metric] - transformer[metric] for accuracy/sharpness/effective_rank.
    Returns {task_name: {'accuracy_delta': float, 'sharpness_delta': float, 'rank_delta': float}}
    """
    ...

def analyze_correlation(densities: list[float], deltas: list[float]) -> dict:
    """
    Spearman rho between retrieval density and accuracy_delta.
    Returns {'rho': float, 'p_value': float, 'gate_pass': bool, 'monotonic': bool}
    """
    ...
```

### Pseudo-code

```
compute_efficiency_delta(transformer_metrics, mamba_metrics):
    deltas = {}
    for task in transformer_metrics:
        t, m = transformer_metrics[task], mamba_metrics[task]
        if t["accuracy"] is None or m["accuracy"] is None:
            continue  # skip failed runs
        deltas[task] = {
            "accuracy_delta": m["accuracy"] - t["accuracy"],
            "sharpness_delta": m["sharpness"] - t["sharpness"],
            "rank_delta": m["effective_rank"] - t["effective_rank"],
        }
    return deltas

analyze_correlation(densities, deltas):
    if len(densities) < 2:
        return {"rho": 0.0, "p_value": 1.0, "gate_pass": False, "monotonic": False}
    rho, p_value = spearmanr(densities, deltas)
    rho = 0.0 if isnan(rho) else float(rho)
    sorted_idx = argsort(densities)
    monotonic = is_sorted(deltas[sorted_idx]) or is_sorted(deltas[sorted_idx][::-1])
    return {
        "rho": rho, "p_value": float(p_value),
        "gate_pass": abs(rho) > 0.7 and p_value < 0.01,
        "monotonic": monotonic,
    }
```

### Subtasks [2/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A4-1 | compute_efficiency_delta | mamba - transformer per-task metric deltas |
| L-A4-2 | analyze_correlation | spearmanr + gate + monotonicity check |

---

## A-5: Main Orchestrator [Complexity: 3, Budget: 4]

**Applied**: Standard experiment-runner pattern (matches `h-m3/code/run_experiment.py`).

### API Signatures

```python
# run_experiment.py
def run_h_m4_experiment(config: dict) -> dict:
    """
    Full pipeline: load data -> train/eval both archs on 4 tasks -> deltas -> correlation -> figures.
    Returns {
        'transformer_metrics': dict, 'mamba_metrics': dict,
        'deltas': dict, 'correlation': dict, 'gate_pass': bool,
    }
    """
    ...
```

### Pseudo-code

```
run_h_m4_experiment(config):
    tokenizer = load_tokenizer()
    suite = load_benchmark_suite(tokenizer, max_length=512, batch_size=4)

    transformer_metrics, mamba_metrics = {}, {}
    for task_name, info in suite.items():
        try:
            transformer_metrics[task_name] = train_and_evaluate("transformer", task_name, tokenizer, info["loader"])
            mamba_metrics[task_name] = train_and_evaluate("mamba", task_name, tokenizer, info["loader"])
        except Exception as e:
            log.error(f"Task {task_name} failed: {e}")
            continue  # exclude task from correlation, keep pipeline alive

    deltas = compute_efficiency_delta(transformer_metrics, mamba_metrics)
    densities = [RETRIEVAL_DENSITY[t] for t in deltas]
    accuracy_deltas = [deltas[t]["accuracy_delta"] for t in deltas]

    correlation = analyze_correlation(densities, accuracy_deltas)

    generate_scatter_plot(densities, accuracy_deltas, correlation["rho"])  # h-m4/figures/
    save_results_json(transformer_metrics, mamba_metrics, deltas, correlation)

    return {
        "transformer_metrics": transformer_metrics,
        "mamba_metrics": mamba_metrics,
        "deltas": deltas,
        "correlation": correlation,
        "gate_pass": correlation["gate_pass"],
    }
```

**Error handling strategy**:
- Dataset load failure -> raise immediately (fatal, no partial suite).
- Per-task train/eval failure -> catch, log, exclude task from correlation (need >=2 remaining tasks or abort with clear message).
- Correlation with <2 valid tasks -> return `gate_pass=False`, `rho=0.0`, log warning (not a crash).
- All checkpoints saved to `h-m4/checkpoints/{model_type}_{task}_checkpoint.pt` before any metric computation, so partial reruns are resumable.

### Subtasks [1/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A5-1 | run_h_m4_experiment | orchestrates full 8-run pipeline + gate check |

---

## Summary

| Task | Subtasks Used | Reuse Source |
|------|----------------|--------------|
| A-1 Data Pipeline | 2/3 | New (pattern from h-m2/data.py) |
| A-2 Transformer Baseline | 2/4 | New (interface mirrors h-m2 MambaWithLoRA) |
| A-3 Train & Eval | 2/5 | h-m2 finetune.py, sharpness.py; h-m3 rank.py |
| A-4 Delta & Correlation | 2/3 | h-m3 correlate.py pattern |
| A-5 Orchestrator | 1/4 | h-m3 run_experiment.py pattern |
</content>
