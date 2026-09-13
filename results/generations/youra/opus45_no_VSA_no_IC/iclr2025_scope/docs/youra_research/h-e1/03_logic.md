# Logic: h-e1 (LoRA Scaling Law, EXISTENCE/PoC)

Applied: PEFT LoraConfig + get_peft_model pattern (HF peft docs)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no code to analyze (archived `h-e1/code/` is unrelated prior hypothesis, per architecture doc)
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-2: Model + LoRA Factory [Complexity: 6, Budget: 2]

**Applied**: PEFT LoraConfig pattern

### API Signatures

```python
from transformers import PreTrainedModel, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model, PeftModel

def load_base_model(model_id: str) -> PreTrainedModel:
    """AutoModelForCausalLM.from_pretrained(model_id), fp16, gradient_checkpointing_enable()."""
    ...

def apply_lora(model: PreTrainedModel, rank: int, alpha: int, dropout: float = 0.05) -> PeftModel:
    """LoraConfig(r=rank, lora_alpha=alpha, target_modules=["query_key_value"],
    lora_dropout=dropout, task_type="CAUSAL_LM") -> get_peft_model(model, config)."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, L] | L=384 (max_length) |
| qkv_weight (base) | [3H, H] | H=hidden_size, frozen |
| lora_A | [rank, H] | trainable |
| lora_B | [3H, rank] | trainable |
| logits | [B, L, V] | V=vocab_size |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A2-1 | load_base_model | fp16 load + gradient checkpointing for 12B OOM avoidance |
| L-A2-2 | apply_lora | LoraConfig w/ alpha=2*rank (rsLoRA), query_key_value target |

---

## A-3: Train/Eval Single Run [Complexity: 10, Budget: 2]

**Applied**: HF Trainer-style manual loop (per-run control needed for checkpoint/resume)

### API Signatures

```python
from torch.optim import AdamW
from transformers import get_linear_schedule_with_warmup

def train_one_run(model_id: str, rank: int, seed: int, cfg: TrainConfig) -> float:
    """Trains LoRA adapter, returns SQuAD-v2 F1 on full validation set."""
    ...

def compute_squad_f1(predictions: list[dict], references: list[dict]) -> float:
    """predictions: [{"id": str, "prediction_text": str, "no_answer_probability": float}]
    references: [{"id": str, "answers": {"text": list[str], "answer_start": list[int]}}]
    Uses evaluate.load("squad_v2"); returns metric["f1"]."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids, attention_mask | [B, L] | B=8, L=384 |
| start_logits, end_logits | [B, L] | span prediction heads |
| loss | scalar | CE(start) + CE(end) / 2 |

### Pseudo-code (training loop)

```
1. set_seed(seed)
2. model = apply_lora(load_base_model(model_id), rank, alpha=2*rank)
3. optimizer = AdamW(model.parameters(), lr=cfg.lr)
4. scheduler = get_linear_schedule_with_warmup(optimizer, cfg.warmup_steps, total_steps)
5. for epoch in range(cfg.epochs):
     for step, batch in enumerate(train_loader):
       outputs = model(**batch)  # loss = start_CE + end_CE
       (outputs.loss / cfg.grad_accum).backward()
       if (step+1) % cfg.grad_accum == 0:
         clip_grad_norm_(model.parameters(), 1.0)
         optimizer.step(); scheduler.step(); optimizer.zero_grad()
     save_checkpoint(model, epoch)  # for NFR-2 recovery
6. predictions = run_inference(model, val_loader)  # decode start/end -> answer spans
7. f1 = compute_squad_f1(predictions, references)
8. return f1
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A3-1 | train_one_run | seed+LoRA setup, AdamW+warmup loop, per-epoch checkpoint |
| L-A3-2 | compute_squad_f1 | span decode -> `evaluate.load("squad_v2")` F1 |

---

## A-6: Scaling Law Fit (reference, low complexity — no subtask budget needed)

### API Signatures

```python
import numpy as np
from scipy import stats

def fit_scaling_law(optimal_ranks: pd.DataFrame, n_bootstrap: int = 1000) -> dict:
    """optimal_ranks columns: [model, N, r_opt].
    OLS: log(r_opt) = alpha*log(N) + log(c).
    Returns {"alpha": float, "alpha_ci_low": float, "alpha_ci_high": float, "c": float, "r2": float}."""
    ...
```

### Pseudo-code

```
1. x, y = log(optimal_ranks.N), log(optimal_ranks.r_opt)   # [12], [12]
2. slope, intercept, r, _, _ = stats.linregress(x, y)
3. alpha, c, r2 = slope, exp(intercept), r**2
4. boot_alphas = []
5. for _ in range(n_bootstrap):
     idx = np.random.choice(len(x), len(x), replace=True)
     s, *_ = stats.linregress(x[idx], y[idx])
     boot_alphas.append(s)
6. ci_low, ci_high = np.percentile(boot_alphas, [2.5, 97.5])
7. return {"alpha": alpha, "alpha_ci_low": ci_low, "alpha_ci_high": ci_high, "c": c, "r2": r2}
```

---

## F1 Computation Detail (SQuAD-v2)

Standard token-overlap F1 with no-answer handling, delegated to `evaluate` lib — no custom implementation needed (rung 5: already-installed dependency).

```python
import evaluate
squad_v2 = evaluate.load("squad_v2")
result = squad_v2.compute(predictions=predictions, references=references)
f1 = result["f1"]
```

skipped: custom SQuAD F1/EM implementation — `evaluate.load("squad_v2")` already covers official scoring incl. no-answer threshold.
