# Logic: H-E1 SSI Contamination Detection (EXISTENCE PoC)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design, no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## E-2: Model + LoRA Fine-tuning [Complexity: 14, Budget: 4 subtasks]

**Applied**: LoRA fine-tuning pattern (PEFT) for contamination injection

### API Signatures

```python
# model.py
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, PeftModel, get_peft_model
from datasets import Dataset
import torch

def load_base_model(model_id: str = "mistralai/Mistral-7B-v0.1") -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Loads base model in BF16, device_map='auto'."""
    ...

def build_lora_config(rank: int = 16, alpha: int = 32) -> LoraConfig:
    """target_modules=['q_proj','v_proj'], task_type='CAUSAL_LM'."""
    ...

def inject_contamination(
    base_model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    contamination_items: Dataset,
    general_data: Dataset,
    lora_cfg: LoraConfig,
    epochs: int = 3,
    lr: float = 2e-4,
    batch_size: int = 4,
    grad_accum: int = 8,
) -> PeftModel:
    """LoRA fine-tune on general_data + contamination_items (concatenated, shuffled)."""
    ...

def get_answer_token_ids(tokenizer: AutoTokenizer) -> list[int]:
    """Returns token ids for [' A',' B',' C',' D'] (single tokens, leading space)."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, L] | Tokenized prompt batch |
| logits | [B, L, V] | Model output, V=vocab size |
| answer_logits | [B, 4] | Logits gathered at answer token ids, last position |

### Pseudo-code: inject_contamination

```
1. train_ds = concat(general_data, contamination_items).shuffle(seed)
2. tokenize train_ds -> input_ids, labels (causal LM, labels=input_ids)
3. peft_model = get_peft_model(base_model, lora_cfg)
4. for epoch in range(epochs):
     for batch in DataLoader(train_ds, batch_size, grad_accum):
       loss = peft_model(**batch).loss
       loss.backward(); optimizer.step() every grad_accum steps
5. return peft_model  # 3 separate calls -> clean(frac=0.0)/low(0.10)/high(0.50) variants
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-E2-1 | load_base_model + get_answer_token_ids | Load Mistral-7B BF16, resolve A/B/C/D token ids |
| L-E2-2 | build_lora_config | LoraConfig(rank=16, alpha=32, target_modules q/v_proj) |
| L-E2-3 | inject_contamination: data prep + training loop | Tokenize, concat general+contamination, LoRA train loop |
| L-E2-4 | inject_contamination: run x3 variants (clean/low/high) | Call with frac 0.0/0.10/0.50, return 3 PeftModel instances |

---

## Note on Scope

Only E-2 allocated for this pass (budget: 4 subtasks, High complexity per architecture doc). E-1, E-3, E-4, E-5 signatures already fully specified in `03_architecture.md` and require no further pseudo-code (simple forward passes / IO wiring) per EXISTENCE PoC brevity rules.
