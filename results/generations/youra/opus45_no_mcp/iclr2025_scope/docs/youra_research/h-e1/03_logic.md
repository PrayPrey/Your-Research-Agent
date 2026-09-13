# Logic: H-E1

**Type:** EXISTENCE (PoC) — minimal logic only

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** No existing code, no base_hypothesis_folder. Designing new APIs from scratch.
**Analyzed Path:** N/A
**Relevant Symbols:** None

---

## A-3: MambaWithLoRA [Complexity: 12, Budget: 5]

**Applied:** Standard PyTorch nn.Module + mamba-ssm block stacking (from mamba-ssm package, `Mamba` block per layer)

### API Signatures

```python
from mamba_ssm import Mamba  # pip: mamba-ssm

class MambaWithLoRA(nn.Module):
    def __init__(self, d_model: int = 4096, d_state: int = 64,
                 n_layers: int = 32, d_conv: int = 4, expand: int = 2,
                 vocab_size: int = 32000):
        """Stack of n_layers Mamba blocks + embedding + LM head."""
        ...

    def forward(self, input_ids: "Tensor") -> "Tensor":
        """input_ids: [B, L] -> logits: [B, L, vocab_size]"""
        ...

def load_proposed_model(lora_config: dict) -> "PeftModel":
    """Instantiate MambaWithLoRA, wrap with peft.get_peft_model(model, LoraConfig(**lora_config))"""
    ...

def verify_mechanism_active(model: "MambaWithLoRA", sample_input: "Tensor") -> bool:
    """sample_input: [1, L] int64. Asserts each Mamba layer has A_log, D params; checks forward output shape."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, L] | token ids |
| embed | [B, L, d_model] | after embedding |
| layer_out (per Mamba block) | [B, L, d_model] | residual stream unchanged shape |
| logits | [B, L, vocab_size] | LM head output |

### Pseudo-code

```
1. x = embedding(input_ids)                  # [B, L, d_model]
2. for layer in self.layers:                 # n_layers Mamba blocks
       x = layer(x) + x                      # residual, [B, L, d_model]
3. x = final_norm(x)
4. logits = lm_head(x)                       # [B, L, vocab_size]
```

`verify_mechanism_active`:
```
1. for layer in model.layers (or base_model.layers if PeftModel):
       assert hasattr(layer.mixer, "A_log") and hasattr(layer.mixer, "D")
2. out = model(sample_input)
3. assert out.shape[:2] == sample_input.shape  # [B, L] match
4. return True
```

### Subtasks [3/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | MambaWithLoRA module | Embedding + Mamba block stack + LM head |
| L-3-2 | load_proposed_model | Instantiate + peft.get_peft_model wrap on in_proj/out_proj |
| L-3-3 | verify_mechanism_active | Assert A_log/D present, check output shape |

---

## A-4: Training loop [Complexity: 10, Budget: 5]

**Applied:** Standard PyTorch AdamW + HF `get_cosine_schedule_with_warmup` pattern, grad accumulation loop

### API Signatures

```python
from torch.optim import AdamW
from transformers import get_cosine_schedule_with_warmup

def train_one_benchmark(model, tokenizer, dataset: "Dataset",
                         train_config: dict) -> dict:
    """Fine-tunes model on dataset. Returns {'loss_curve': List[float], 'checkpoint_path': str}"""
    ...

def run_all_training(model_fn: Callable[[dict], "PeftModel"],
                      lora_config: dict, tag: str) -> dict:
    """tag in {'transformer','mamba'}. Loops BENCHMARKS, calls train_one_benchmark per benchmark.
    Returns {benchmark_name: {'loss_curve':[...], 'checkpoint_path': str}}"""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| batch['input_ids'] | [batch_size, L] | tokenized causal LM batch |
| loss | scalar | cross-entropy, next-token |

### Pseudo-code

```
train_one_benchmark(model, tokenizer, dataset, train_config):
1. loader = DataLoader(dataset, batch_size=train_config['batch_size'], shuffle=True)
2. optimizer = AdamW(model.parameters(), lr=train_config['lr'],
                      weight_decay=train_config['weight_decay'], betas=train_config['betas'])
3. total_steps = len(loader) * train_config['epochs'] // train_config['grad_accum']
4. scheduler = get_cosine_schedule_with_warmup(optimizer, train_config['warmup_steps'], total_steps)
5. loss_curve = []
6. set_seed(train_config['seed'])
7. for epoch in range(train_config['epochs']):
       for i, batch in enumerate(loader):
           out = model(**batch)                    # labels=input_ids -> out.loss
           loss = out.loss / train_config['grad_accum']
           loss.backward()
           if (i+1) % train_config['grad_accum'] == 0:
               optimizer.step(); scheduler.step(); optimizer.zero_grad()
           loss_curve.append(loss.item() * train_config['grad_accum'])
8. checkpoint_path = save model.state_dict() / peft adapter to disk
9. return {'loss_curve': loss_curve, 'checkpoint_path': checkpoint_path}

run_all_training(model_fn, lora_config, tag):
1. results = {}
2. for name, cfg in BENCHMARKS.items():
       ds = format_for_causal_lm(load_benchmark(name), tokenizer)
       model = model_fn(lora_config)
       results[name] = train_one_benchmark(model, tokenizer, ds, TRAIN_CONFIG)
3. return results
```

### Subtasks [1/5 used cumulatively → 4 total]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | train_one_benchmark + run_all_training | AdamW + cosine warmup, grad accum loop, checkpoint save |

---

## A-5: Evaluation suite [Complexity: 8, Budget: 5]

**Applied:** HF `evaluate` library metrics (exact_match, f1, accuracy) + scipy `spearmanr`

### API Signatures

```python
from scipy.stats import spearmanr

def evaluate_benchmark(model, tokenizer, dataset: "Dataset", metric_name: str) -> float:
    """Generates predictions, computes metric_name in {'exact_match','f1','accuracy'}. Returns score in [0,1]."""
    ...

def compute_deltas(transformer_scores: dict, mamba_scores: dict) -> dict:
    """Per-benchmark: mamba_scores[k] - transformer_scores[k]. Returns {benchmark: delta}"""
    ...

def spearman_correlation(deltas: dict, densities: dict) -> float:
    """Aligns by benchmark key, returns spearmanr(delta_values, density_values).correlation"""
    ...

def check_gate_conditions(deltas: dict, correlation: float) -> dict:
    """Returns {'gsm8k_pass': bool, 'nq_pass': bool, 'correlation_pass': bool, 'overall_pass': bool}
    Thresholds: gsm8k delta >= -0.05, nq delta <= -0.15, correlation > 0.5"""
    ...
```

### Pseudo-code

```
evaluate_benchmark:
1. preds = [model.generate(tokenizer(x)) for x in dataset]
2. score = evaluate.load(metric_name).compute(predictions=preds, references=dataset['answer'])
3. return score[metric_name]  # scalar in [0,1]

check_gate_conditions:
1. gsm8k_pass = deltas['gsm8k'] >= -0.05
2. nq_pass = deltas['nq'] <= -0.15
3. correlation_pass = correlation > 0.5
4. overall_pass = gsm8k_pass and nq_pass and correlation_pass
5. return {'gsm8k_pass':..., 'nq_pass':..., 'correlation_pass':..., 'overall_pass':...}
```

### Subtasks [1/5 used → 5 total]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | evaluate_benchmark + compute_deltas + spearman_correlation + check_gate_conditions | Metric computation, delta calc, correlation, gate check (single grouped subtask) |

---

## Budget Summary

Total subtasks used: 5/5 (L-3-1, L-3-2, L-3-3, L-4-1, L-5-1)
