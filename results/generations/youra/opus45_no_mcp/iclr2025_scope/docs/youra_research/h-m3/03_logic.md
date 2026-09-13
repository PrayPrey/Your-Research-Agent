# Logic: H-M3

**Applied**: SVD-based effective rank (Hu et al. 2021 LoRA) + reuse of H-M2 finetune/sharpness pipeline

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual H-M2 code (differ from 03_architecture.md spec in places)
**Analyzed Path**: `docs/youra_research/h-m2/code/`
**Relevant Symbols**: `finetune_on_task`, `load_task_loader`, `measure_task_sharpness`, `MambaWithLoRA`, `load_proposed_model`

**Discrepancies found vs h-m3/03_architecture.md spec**:
- `finetune_on_task(task_name, tokenizer, train_config=None, output_dir=None)` — `output_dir` default is `None` (resolves internally to `h-m2/checkpoints`), not `"h-m2/checkpoints"` string default. H-M3 must pass its own `output_dir="h-m3/checkpoints"` explicitly.
- `load_task_loader(name, tokenizer, max_length=512, batch_size=16, split=None, num_samples=None)` — has extra `num_samples` param not in spec; needed to build separate train/test loaders (architecture doc didn't show how train vs test split is obtained — use `split="train"` and `split="test"` overrides for `evaluate.py`).
- H-M2's `data.py` is standalone (does NOT import from `h_m1.data`) — loads HF datasets directly via its own `config.BENCHMARKS`. H-M3 reuses `h_m2.code.data.load_task_loader` directly, no h_m1 dependency needed for data.
- `MambaWithLoRA.forward` returns `type("Output",...)()` object with `.loss`/`.logits`, not a dict — `evaluate_accuracy` must use `outputs.logits`.
- PEFT wraps `base_model` where target module `in_proj` is `MambaBlockSimulated.in_proj` (a plain `nn.Linear`); after `get_peft_model`, LoRA A/B live at `model.base_model.model.layers[i].in_proj.lora_A['default'].weight` / `lora_B['default'].weight` (standard PEFT naming) — must walk `model.named_modules()` filtering for `lora_A`/`lora_B` attrs rather than assuming fixed names.

---

## External Dependencies API (From Actual Code)

```python
# From: h-m2/code/finetune.py (ACTUAL CODE)
def finetune_on_task(task_name: str, tokenizer, train_config: dict = None,
                      output_dir: str = None) -> dict:
    """Returns {'model': PeftModel, 'loss_curve': list[float], 'checkpoint_path': str}"""
    ...

# From: h-m2/code/data.py (ACTUAL CODE)
def load_task_loader(name: str, tokenizer, max_length: int = 512, batch_size: int = 16,
                      split: str = None, num_samples: int = None) -> DataLoader:
    """name in {'gsm8k','nq'}. split overrides config default (use 'train'/'test')."""
    ...

# From: h-m2/code/sharpness.py (ACTUAL CODE)
def measure_task_sharpness(model, dataloader, max_batches: int = 100,
                            sam_epsilon: float = 0.05) -> dict:
    """Returns {'mean_sharpness': float, 'per_batch': list[float]}"""
    ...

# From: h-m2/code/model.py (ACTUAL CODE)
class MambaWithLoRA(nn.Module):
    def forward(self, input_ids, attention_mask=None, labels=None):
        ...  # returns object with .loss (Optional[Tensor]), .logits [B, L, vocab_size]
```

**Verified from**: `h-m2/code/{finetune,data,sharpness,model}.py` (actual implementation, not spec)

---

## M3-4/M3-5: LoRA Matrix Extraction + Effective Rank [Complexity: 6+8, Budget: 2 subtasks]

**Applied**: SVD-based effective rank (Hu et al. 2021)

### API Signatures

```python
# code/rank.py
def extract_lora_matrices(model: "PeftModel") -> dict:
    """Walks model.named_modules(); collects lora_A/lora_B['default'].weight pairs.
    Returns {module_name: (lora_A: Tensor[r, in], lora_B: Tensor[out, r])}"""
    ...

def compute_effective_rank(lora_A: "Tensor", lora_B: "Tensor", threshold: float = 0.90) -> tuple:
    """delta_W = lora_B @ lora_A -> [out, in]; SVD; effective_rank = min k s.t. cumsum(S[:k])/sum(S)>=threshold.
    Returns (effective_rank: int, singular_values: list[float])."""
    ...

def compute_model_effective_rank(model: "PeftModel", threshold: float = 0.90) -> dict:
    """Aggregates extract_lora_matrices + compute_effective_rank across all modules.
    Returns {'effective_rank': int (max across modules), 'per_module': dict[str,int],
             'singular_values': dict[str, list[float]]}"""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| lora_A | [16, 512] | rank=16, in_proj input dim |
| lora_B | [1024, 16] | in_proj out dim = d_model*expand*2 = 1024 |
| delta_W | [1024, 512] | lora_B @ lora_A |
| singular_values | [512] | min(1024, 512) |

### Pseudo-code (compute_effective_rank)

```
1. delta_W = lora_B @ lora_A                     # [out, in]
2. U, S, Vh = torch.linalg.svd(delta_W, full_matrices=False)
3. S_norm = S / S.sum()
4. cumsum = torch.cumsum(S_norm, dim=0)
5. effective_rank = int((cumsum < threshold).sum().item()) + 1
6. return effective_rank, S.tolist()
```

```
compute_model_effective_rank:
  matrices = extract_lora_matrices(model)
  per_module = {}; sv = {}
  for name, (A, B) in matrices.items():
      rank, s = compute_effective_rank(A, B, threshold)
      per_module[name] = rank; sv[name] = s
  return {'effective_rank': max(per_module.values()), 'per_module': per_module, 'singular_values': sv}
```

### Subtasks [2/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M3-1 | extract_lora_matrices | Walk PeftModel named_modules, collect lora_A/lora_B weight pairs for in_proj |
| L-M3-2 | compute_effective_rank / compute_model_effective_rank | SVD + cumsum threshold, aggregate max across modules |

---

## M3-6: Generalization Gap [Complexity: 6, Budget: 1 subtask]

**Applied**: Standard PyTorch eval loop

### API Signatures

```python
# code/evaluate.py
def evaluate_accuracy(model: "nn.Module", dataloader: "DataLoader") -> float:
    """Token-level top-1 accuracy on non-padded positions, no_grad, model.eval()."""
    ...

def compute_generalization_gap(model: "nn.Module", tokenizer, task_name: str,
                                train_config: dict) -> dict:
    """Builds train/test loaders via h_m2.data.load_task_loader(split='train'/'test'),
    evaluates both. Returns {'train_acc': float, 'test_acc': float, 'gen_gap': float}"""
    ...
```

### Pseudo-code (evaluate_accuracy)

```
1. model.eval(); correct = 0; total = 0
2. for batch in dataloader:
       with torch.no_grad():
           out = model(input_ids=batch['input_ids'], attention_mask=batch.get('attention_mask'),
                        labels=batch['labels'])
       preds = out.logits[..., :-1, :].argmax(-1)        # [B, L-1]
       labels = batch['labels'][..., 1:]                  # [B, L-1]
       mask = labels != pad_token_id
       correct += ((preds == labels) & mask).sum().item()
       total += mask.sum().item()
3. return correct / max(total, 1)
```

### Subtasks [1/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M3-3 | evaluate_accuracy + compute_generalization_gap | Token-level accuracy, train/test loaders, gap = train-test |

---

## M3-7/M3-8: Correlation + Ablations [Complexity: 5+9, Budget: 2 subtasks]

**Applied**: scipy.stats.spearmanr

### API Signatures

```python
# code/correlate.py
def compute_spearman(sharpness_vals: list, rank_vals: list) -> dict:
    """scipy.stats.spearmanr; Returns {'rho': float, 'p_value': float, 'gate_pass': rho > GATE_THRESHOLD}"""
    ...

def compute_gap_correlation(sharpness_vals: list, gap_vals: list) -> dict:
    """Secondary Spearman corr(sharpness, gen_gap). Returns {'rho': float, 'p_value': float}"""
    ...

def run_threshold_sensitivity(models: dict, sharpness_vals: dict, thresholds: list) -> dict:
    """A-1: for each threshold, recompute effective_rank per task via compute_model_effective_rank,
    then compute_spearman. Returns {threshold: {'rho': float, 'p_value': float}}"""
    ...

def run_seed_sensitivity(seeds: list, run_fn: "Callable[[int], dict]") -> dict:
    """A-2: run_fn(seed) executes full pipeline (finetune->sharpness->rank->corr) per seed.
    Returns {'mean_rho': float, 'std_rho': float, 'per_seed': dict[int, float]}"""
    ...
```

### Pseudo-code (run_threshold_sensitivity)

```
1. results = {}
2. for threshold in thresholds:
       rank_vals = [compute_model_effective_rank(models[t], threshold)['effective_rank'] for t in tasks]
       sharp_vals = [sharpness_vals[t] for t in tasks]
       results[threshold] = compute_spearman(sharp_vals, rank_vals)
3. return results
```

### Subtasks [2/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M3-4 | compute_spearman + compute_gap_correlation | Primary gate rho + secondary gen-gap rho |
| L-M3-5 | run_threshold_sensitivity + run_seed_sensitivity | A-1 threshold sweep [0.85,0.90,0.95], A-2 seed sweep [42,123,456] |

---

## M3-10: Integration [Complexity: 10, Budget: 1 subtask]

### API Signatures

```python
# code/run_experiment.py
def main() -> dict:
    """Returns {'spearman_result': dict, 'gap_correlation': dict, 'task_metrics': dict,
                'threshold_sensitivity': dict, 'seed_sensitivity': dict, 'figures': list[str]}"""
    ...
```

### Pseudo-code

```
1. tokenizer = load_tokenizer()  # h_m2.code.model
2. task_metrics = {}
3. for task in ['gsm8k', 'nq']:
       ft = finetune_on_task(task, tokenizer, TRAIN_CONFIG, output_dir="h-m3/checkpoints")
       model = ft['model']
       loader = load_task_loader(task, tokenizer, batch_size=TRAIN_CONFIG['batch_size'])
       sharp = measure_task_sharpness(model, loader, max_batches=SHARPNESS_CONFIG['max_batches'],
                                       sam_epsilon=SHARPNESS_CONFIG['sam_epsilon'])
       rank_result = compute_model_effective_rank(model, threshold=RANK_CONFIG['default_threshold'])
       gap = compute_generalization_gap(model, tokenizer, task, TRAIN_CONFIG)
       task_metrics[task] = {**sharp, **rank_result, **gap, 'loss_curve': ft['loss_curve'], 'model': model}
4. sharpness_vals = [task_metrics[t]['mean_sharpness'] for t in tasks]
5. rank_vals = [task_metrics[t]['effective_rank'] for t in tasks]
6. gap_vals = [task_metrics[t]['gen_gap'] for t in tasks]
7. spearman_result = compute_spearman(sharpness_vals, rank_vals)
8. gap_correlation = compute_gap_correlation(sharpness_vals, gap_vals)
9. models = {t: task_metrics[t]['model'] for t in tasks}
10. sharp_map = {t: task_metrics[t]['mean_sharpness'] for t in tasks}
11. threshold_sensitivity = run_threshold_sensitivity(models, sharp_map, RANK_CONFIG['thresholds'])
12. seed_sensitivity = run_seed_sensitivity(SEEDS, run_fn=lambda seed: run_full_pipeline(seed))
13. plot_sharpness_vs_rank(task_metrics, spearman_result['rho'], "h-m3/figures/sharpness_vs_rank.png")
14. plot_singular_values({t: task_metrics[t]['singular_values'] for t in tasks}, "h-m3/figures/sv_dist.png")
15. plot_generalization_gap(task_metrics, "h-m3/figures/gen_gap.png")
16. plot_training_curves({t: task_metrics[t]['loss_curve'] for t in tasks}, "h-m3/figures/training_curves.png")
17. plot_correlation_matrix(task_metrics, "h-m3/figures/corr_matrix.png")
18. return {'spearman_result': spearman_result, 'gap_correlation': gap_correlation,
            'task_metrics': task_metrics, 'threshold_sensitivity': threshold_sensitivity,
            'seed_sensitivity': seed_sensitivity, 'figures': [...]}
```

### Subtasks [0 dedicated — orchestration only, uses APIs above]

Covered by L-M3-1..5; `main()` is pure wiring, no new subtask budget needed.

---

## visualize.py (reused pattern from H-M2 `plot_gate_comparison`)

```python
# code/visualize.py
def plot_sharpness_vs_rank(task_metrics: dict, rho: float, out_path: str) -> None:
    """Required: scatter (sharpness, effective_rank) per task, rho annotated."""
    ...

def plot_singular_values(singular_values: dict, out_path: str) -> None:
    """Per-task SVD spectrum overlay (line plot, log-y)."""
    ...

def plot_generalization_gap(task_metrics: dict, out_path: str) -> None:
    """Scatter sharpness vs gen_gap."""
    ...

def plot_training_curves(loss_curves: dict, out_path: str) -> None:
    """Per-task loss curve over epochs."""
    ...

def plot_correlation_matrix(task_metrics: dict, out_path: str) -> None:
    """Heatmap: sharpness, effective_rank, gen_gap, train_acc, test_acc pairwise corr."""
    ...
```

No dedicated subtask — reuses M2's `visualize.py` bar/histogram pattern directly, straightforward matplotlib calls.

---

## Budget Summary

| Subtask ID | Maps to Task | Used |
|------------|--------------|------|
| L-M3-1 | M3-4 | 1 |
| L-M3-2 | M3-5 | 1 |
| L-M3-3 | M3-6 | 1 |
| L-M3-4 | M3-7 | 1 |
| L-M3-5 | M3-8 | 1 |

**Total: 5/6 subtasks used** (1 reserve for integration debugging in M3-10)
