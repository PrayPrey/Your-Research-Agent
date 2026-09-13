# Logic: H-M2

**Applied**: SAM sharpness measurement pattern (reused from H-M1); LoRA fine-tune loop pattern (adapted from H-E1)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from base code (h-m1, h-e1)
**Analyzed Path**: `docs/youra_research/h-m1/code/`, `docs/youra_research/h-e1/code/`
**Relevant Symbols**: `measure_sharpness_sam`, `compute_loss`, `load_landscape_eval_set`, `load_benchmark`, `format_for_causal_lm`, `MambaWithLoRA`, `load_proposed_model`, `train_one_benchmark`

**Discrepancies found vs spec (03_architecture.md)**:
- `measure_sharpness_sam(model, dataloader, epsilon=None, max_batches=8) -> float` — returns a **scalar float**, not a dict. Architecture spec implied dict; wrapper must build the dict.
- `load_proposed_model(lora_config: dict = None)` returns a raw `MambaWithLoRA` with **no LoRA applied** (no `get_peft_model` call in h-m1). H-M2 must apply `peft.get_peft_model` itself in `finetune.py`.
- `MambaWithLoRA` is a plain `nn.Module`, no `save_pretrained`. Use `torch.save(model.state_dict(), path)` for checkpoints, not `model.save_pretrained` (h-e1's `train_one_benchmark` assumed a HF-style model incompatible with `MambaWithLoRA`).
- `load_benchmark(name) -> DatasetDict` (raw), separate from `load_landscape_eval_set(name, tokenizer, max_length, num_samples) -> DataLoader` (tokenized + batched, batch_size from `LANDSCAPE_CONFIG`). H-M2 needs its own batch_size=16 and its own `BENCHMARKS` (gsm8k+nq), so wrap `load_benchmark` + `format_for_causal_lm` directly rather than reusing `load_landscape_eval_set` (which hardcodes h-m1's config).

---

## External Dependencies (Base Hypothesis)

```python
# From: h-m1/code/landscape.py (ACTUAL CODE)
def measure_sharpness_sam(model: nn.Module, dataloader: DataLoader,
                           epsilon: float = None, max_batches: int = 8) -> float:
    """SAM sharpness = L(w+eps*grad/||grad||) - L(w). Restores params. Returns scalar."""
    ...

def compute_loss(model: nn.Module, dataloader: DataLoader,
                  max_batches: int = None, device=None) -> float: ...

# From: h-m1/code/data.py (ACTUAL CODE)
def load_benchmark(name: str) -> "DatasetDict": ...

def format_for_causal_lm(dataset, tokenizer, max_length: int = 512) -> "Dataset":
    """Adds labels=input_ids.copy(); tokenizes 'question' or 'text' field."""
    ...

# From: h-m1/code/model.py (ACTUAL CODE)
class MambaWithLoRA(nn.Module):
    def __init__(self, d_model=4096, d_state=64, n_layers=32, d_conv=4,
                 expand=2, vocab_size=32000): ...
    def forward(self, input_ids: Tensor, attention_mask: Optional[Tensor] = None,
                labels: Optional[Tensor] = None): ...  # returns obj with .loss, .logits

def load_proposed_model(lora_config: dict = None) -> MambaWithLoRA:
    """Returns MambaWithLoRA(d_model=2048, d_state=32, n_layers=16, vocab_size=32000). No LoRA applied."""
    ...
```

**Verified from**: `h-m1/code/landscape.py`, `h-m1/code/data.py`, `h-m1/code/model.py` (actual implementation, not spec)

---

## M2-2/M2-3/M2-4: Data + Finetune [Complexity: 6+8+4, Budget: 3 subtasks]

**Applied**: PEFT LoRA wrapping over plain `nn.Module` (target_modules must exist as named submodules — `MambaBlockSimulated.in_proj`/`out_proj` qualify)

### API Signatures

```python
# code/data.py
def load_task_loader(name: str, tokenizer, max_length: int = 512,
                      batch_size: int = 16, split: Optional[str] = None) -> DataLoader:
    """Wraps h_m1.data.load_benchmark + format_for_causal_lm.
    name in {'gsm8k','nq'}. Uses BENCHMARKS[name]['split'] if split=None."""
    ...

# code/finetune.py
def finetune_on_task(task_name: str, tokenizer, train_config: dict = None,
                      output_dir: str = "h-m2/checkpoints") -> dict:
    """LoRA-finetunes load_proposed_model() on task_name for train_config['epochs'].
    Returns {'model': nn.Module, 'loss_curve': list[float], 'checkpoint_path': str}"""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [16, 512] | batch_size=16, max_length=512 |
| labels | [16, 512] | shifted internally in forward |
| logits | [16, 512, 32000] | vocab_size |
| loss | scalar | CrossEntropy |

### Pseudo-code (finetune_on_task)

```
1. cfg = train_config or TRAIN_CONFIG
2. base = load_proposed_model()                          # h_m1.model, no LoRA
3. peft_cfg = LoraConfig(r=LORA_CONFIG['r'], lora_alpha=LORA_CONFIG['lora_alpha'],
                          target_modules=LORA_CONFIG['target_modules'], task_type=None)
4. model = get_peft_model(base, peft_cfg)                # applies LoRA per PRD FR-2.2
5. loader = load_task_loader(task_name, tokenizer, batch_size=cfg['batch_size'])
6. optimizer = AdamW(model.parameters(), lr=cfg['lr'])
7. for epoch in range(cfg['epochs']):
       for batch in loader:
           out = model(**batch); out.loss.backward()
           optimizer.step(); optimizer.zero_grad()
8. torch.save(model.state_dict(), f"{output_dir}/{task_name}_checkpoint.pt")
9. return {'model': model, 'loss_curve': ..., 'checkpoint_path': ...}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M2-1 | load_task_loader | GSM8K/NQ wrapper over h_m1.data, batch=16 |
| L-M2-2 | finetune_on_task | peft LoRA wrap + train loop, state_dict checkpoint |
| L-M2-3 | Checkpoint I/O | Save/load state_dict per task (gsm8k, nq independent) |

---

## M2-5/M2-6: Sharpness + Comparison [Complexity: 7+3, Budget: 2 subtasks]

**Applied**: Standard PyTorch (direct reuse of h_m1.measure_sharpness_sam)

### API Signatures

```python
# code/sharpness.py
def measure_task_sharpness(model: nn.Module, dataloader: DataLoader,
                            max_batches: int = 100, sam_epsilon: float = 0.05) -> dict:
    """Calls h_m1.landscape.measure_sharpness_sam once per max_batches-batch;
    also runs per-batch loop for distribution.
    Returns {'mean_sharpness': float, 'per_batch': list[float]}"""
    ...

def compare_task_sharpness(seq_result: dict, ret_result: dict) -> dict:
    """Returns {'sequential_sharpness': float, 'retrieval_sharpness': float, 'ratio': float}"""
    ...
```

### Pseudo-code (measure_task_sharpness)

```
1. per_batch = []
2. for i, batch in enumerate(dataloader):
       if i >= max_batches: break
       single_loader = DataLoader([batch], batch_size=1)  # or reuse batch directly
       s = measure_sharpness_sam(model, single_loader, epsilon=sam_epsilon, max_batches=1)
       per_batch.append(s)
3. mean_sharpness = mean(per_batch)
4. return {'mean_sharpness': mean_sharpness, 'per_batch': per_batch}
```

```
compare_task_sharpness:
  ratio = seq_result['mean_sharpness'] / ret_result['mean_sharpness']
  return {'sequential_sharpness': seq_result['mean_sharpness'],
          'retrieval_sharpness': ret_result['mean_sharpness'], 'ratio': ratio}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M2-4 | measure_task_sharpness | Per-batch SAM sharpness loop via h_m1.landscape, 100 batches |
| L-M2-5 | compare_task_sharpness | ratio = seq/ret dict combiner |

---

## M2-7: Gate + Mechanism Verification [Complexity: 5, Budget: 1 subtask]

**Applied**: Standard PyTorch

### API Signatures

```python
# code/gate.py
def evaluate_gate(compare_result: dict, threshold: float = 0.8) -> dict:
    """ratio = compare_result['ratio']; pass_gate = ratio < threshold.
    Returns {'ratio', 'pass', 'sequential_sharpness', 'retrieval_sharpness'}"""
    ...

def verify_mechanism(compare_result: dict) -> Tuple[bool, str]:
    """Checks: both sharpness values computed (not None/nan),
    |seq - ret| > 0.01 (tasks differentiated), 0 < ratio < 10 (sane range).
    Returns (passed: bool, message: str)"""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M2-6 | evaluate_gate + verify_mechanism | Ratio/threshold check + sanity checks per PRD FR-4 |

---

## M2-8: Visualization [Complexity: 5, Budget: no dedicated subtask — reuses gate/sharpness outputs]

### API Signatures

```python
# code/visualize.py
def plot_gate_comparison(seq_sharpness: float, ret_sharpness: float,
                          threshold: float, out_path: str) -> None:
    """Bar chart GSM8K vs NQ sharpness, horizontal line at threshold * ret_sharpness."""
    ...

def plot_sharpness_distribution(seq_per_batch: List[float], ret_per_batch: List[float],
                                 out_path: str) -> None:
    """Overlaid histograms of per-batch sharpness for both tasks."""
    ...
```

---

## M2-9: run_experiment Orchestration [Complexity: 9, Budget: covered by subtasks above]

### API Signatures

```python
# code/run_experiment.py
def main() -> dict:
    """Returns {'gate_result': dict, 'mechanism_check': tuple, 'figures': list[str]}"""
    ...
```

### Pseudo-code

```
1. tokenizer = AutoTokenizer.from_pretrained("state-spaces/mamba-2.8b-hf")
2. seq_out = finetune_on_task("gsm8k", tokenizer, TRAIN_CONFIG)
3. ret_out = finetune_on_task("nq", tokenizer, TRAIN_CONFIG)
4. seq_loader = load_task_loader("gsm8k", tokenizer)
5. ret_loader = load_task_loader("nq", tokenizer)
6. seq_sharp = measure_task_sharpness(seq_out['model'], seq_loader, max_batches=100)
7. ret_sharp = measure_task_sharpness(ret_out['model'], ret_loader, max_batches=100)
8. cmp = compare_task_sharpness(seq_sharp, ret_sharp)
9. gate = evaluate_gate(cmp, threshold=GATE_THRESHOLD)
10. mech = verify_mechanism(cmp)
11. plot_gate_comparison(cmp['sequential_sharpness'], cmp['retrieval_sharpness'],
                          GATE_THRESHOLD, "h-m2/figures/gate_comparison.png")
12. plot_sharpness_distribution(seq_sharp['per_batch'], ret_sharp['per_batch'],
                                 "h-m2/figures/sharpness_dist.png")
13. return {'gate_result': gate, 'mechanism_check': mech, 'figures': [...]}
```

---

## Budget Summary

| Subtask ID | Maps to Task | Used |
|------------|--------------|------|
| L-M2-1 | M2-2 | 1 |
| L-M2-2 | M2-3, M2-4 | 1 |
| L-M2-3 | M2-3, M2-4 | 1 |
| L-M2-4 | M2-5 | 1 |
| L-M2-5 | M2-6 | 1 |
| L-M2-6 | M2-7 | 1 |

**Total: 6/6 subtasks used**
