# Logic: h-m1

**Hypothesis:** Attention entropy at optimal LoRA rank correlates with model size (Pearson r > 0.6, p < 0.05)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no `code/` folder for h-m1, no base_hypothesis_folder in inputs
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-5: Training Loop [Complexity: 14, Budget: 4]

**Applied**: HF PEFT LoRA fine-tuning loop (AdamW + linear warmup/cosine decay)

### API Signatures

```python
def train_qa(
    model: PeftModel,
    train_loader: DataLoader,
    val_loader: DataLoader,
    cfg: TrainConfig,
    seed: int = SEED,
    patience: int = 2,
) -> tuple[PeftModel, dict]:
    """Trains LoRA adapter. Returns (model, {'train_loss': [...], 'val_f1': [...]})"""
    ...

def make_optimizer_and_scheduler(
    model: PeftModel, cfg: TrainConfig, num_training_steps: int
) -> tuple[torch.optim.Optimizer, torch.optim.lr_scheduler.LambdaLR]: ...

def train_step(
    model: PeftModel, batch: dict[str, Tensor], grad_accum: int
) -> float:
    """Single forward+backward. batch['input_ids']: [B, L]. Returns loss.item()."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, L] | B=4, L<=512 |
| start_positions, end_positions | [B] | QA span labels |
| logits (start/end) | [B, L] | from QA head |

### Pseudo-code

```
1. optimizer, scheduler = make_optimizer_and_scheduler(model, cfg, steps=len(train_loader)*cfg.epochs/grad_accum)
2. best_f1, no_improve = -inf, 0
3. for epoch in range(cfg.epochs):
4.     model.train()
5.     for i, batch in enumerate(train_loader):
6.         loss = train_step(model, batch, cfg.grad_accum) / cfg.grad_accum
7.         loss.backward()
8.         if (i+1) % cfg.grad_accum == 0:
9.             optimizer.step(); scheduler.step(); optimizer.zero_grad()
10.    val_f1 = evaluate_qa(model, tokenizer, val_loader.dataset)
11.    if val_f1 > best_f1: best_f1, no_improve = val_f1, 0; save checkpoint
12.    else: no_improve += 1
13.    if no_improve >= patience: break  # early stop on plateau
14. return model, history
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Optimizer/scheduler + train_step | AdamW, warmup+cosine LambdaLR, grad-accum backward |
| L-5-2 | Epoch loop + early stopping | Checkpoint on best val F1, patience-based break |

---

## A-7: Attention Entropy Computation [Complexity: 10, Budget: 2]

**Applied**: Masked Shannon entropy over multi-head attention weights

### API Signatures

```python
def compute_attention_entropy(
    model: PeftModel,
    input_ids: Tensor,        # [B, L]
    attention_mask: Tensor,   # [B, L]
) -> float:
    """Forward with output_attentions=True. Mean Shannon entropy, masked+renormalized, avg over layers/heads/positions."""
    ...

def _entropy_from_attn(
    attn: Tensor,              # [B, H, L, L] single layer attention probs
    attention_mask: Tensor,    # [B, L]
) -> Tensor:                   # [B] per-sample entropy for this layer
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| attentions | tuple(num_layers) of [B, H, L, L] | model(..., output_attentions=True).attentions |
| mask_2d | [B, 1, 1, L] | broadcast mask over key dim |
| p (renormalized) | [B, H, L, L] | rows sum to 1 over valid keys only |
| entropy per pos | [B, H, L] | -sum(p*log(p), dim=-1) |

### Pseudo-code

```
1. with torch.no_grad(): out = model(input_ids, attention_mask=attention_mask, output_attentions=True)
2. entropies = []
3. for layer_attn in out.attentions:               # [B, H, L, L]
4.     masked = layer_attn * attention_mask[:, None, None, :]      # zero out pad keys
5.     masked = masked / masked.sum(dim=-1, keepdim=True).clamp_min(1e-9)  # renormalize rows
6.     ent = -(masked * (masked.clamp_min(1e-9)).log()).sum(dim=-1)  # [B, H, L]
7.     valid_query = attention_mask[:, None, :].expand_as(ent)        # mask query positions too
8.     ent = (ent * valid_query).sum() / valid_query.sum()
9.     entropies.append(ent)
10. return torch.stack(entropies).mean().item()
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Forward hook + per-layer masked entropy | output_attentions=True forward, mask+renormalize, per-layer Shannon entropy |
| L-7-2 | Aggregate over layers/heads/positions | Reduce to single scalar float, masked mean over valid query positions |

---

## A-8: Full Sweep Orchestration [Complexity: 12, Budget: 2]

**Applied**: Grid-search orchestration with JSON result persistence

### API Signatures

```python
def run_experiment() -> dict:
    """Sweeps MODEL_SIZES x RANKS (4x6=24). Returns results dict, saves JSON + figures."""
    ...

def run_single_combo(
    size: str, rank: int, train_ds: Dataset, val_ds: Dataset, tokenizer
) -> dict:
    """Trains+evals one (model,rank) combo. Returns {'f1': float, 'entropy': float}."""
    ...

def main() -> None: ...
```

### Tensor Shapes

N/A (orchestration layer; delegates tensor ops to train.py/entropy.py)

### Pseudo-code

```
1. results = {size: {} for size in MODEL_SIZES}
2. train_ds, val_ds = load_squad_v2(); tokenizer shared per model family
3. for size in MODEL_SIZES:
4.     base_model, tokenizer = load_base_model(size)   # cached across ranks
5.     train_tok = tokenize_qa(train_ds, tokenizer); val_tok = tokenize_qa(val_ds, tokenizer)
6.     for rank in RANKS:
7.         lora_model = create_lora_model(base_model, rank)
8.         lora_model, _ = train_qa(lora_model, make_dataloader(train_tok,...), make_dataloader(val_tok,...), TrainConfig())
9.         f1 = evaluate_qa(lora_model, tokenizer, val_tok)
10.        sample_batch = next(iter(make_dataloader(val_tok, batch_size=8, shuffle=False)))
11.        entropy = compute_attention_entropy(lora_model, sample_batch['input_ids'], sample_batch['attention_mask'])
12.        results[size][rank] = {'f1': f1, 'entropy': entropy}
13.        del lora_model; torch.cuda.empty_cache()
14. optimal = {size: find_optimal_rank([results[size][r]['f1'] for r in RANKS], RANKS) for size in MODEL_SIZES}
15. correlation = compute_correlation(results, MODEL_PARAMS)  # uses entropy at optimal rank per model
16. save results + correlation to outputs/results.json
17. plot_gate_metrics(...); plot_rank_f1_curves(...); plot_entropy_heatmap(...); plot_optimal_rank_bar(...)
18. return {'results': results, 'optimal': optimal, 'correlation': correlation}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | Grid loop (4x6) with per-combo train/eval/entropy | Model caching across ranks, GPU memory cleanup between ranks |
| L-8-2 | Result aggregation + JSON save + figure calls | Optimal-rank selection, correlation call, results.json write, invoke visualize.py |

---

## Self-Validation

- [x] No ASCII diagrams
- [x] Only "Applied: X" lines, no KB search logs
- [x] Docstrings <= 2 lines
- [x] Tensor shapes in comments/tables
- [x] Subtask count: 6/6 used (A-5: 2, A-7: 2, A-8: 2)
- [x] Codebase Analysis (Serena) section included, green-field noted
