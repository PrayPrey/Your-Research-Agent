# Logic: H-M1 (Contamination Injection Mechanism)

Applied: LoRA fine-tuning contamination injection pattern (PEFT, reused from H-E1)
Applied: Item-level accuracy tracking for mechanism validation (contaminated vs clean split)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual H-E1 code (direct file read; Serena MCP unavailable, used as documented fallback)
**Analyzed Path**: `h-e1/code/data.py`, `h-e1/code/model.py`
**Relevant Symbols**: `load_mmlu`, `sample_contamination_subset`, `format_mmlu_prompt`, `load_base_model`, `build_lora_config`, `get_answer_token_ids`, `format_training_example`, `inject_contamination`

**Critical deviations found vs spec assumptions:**
- `load_mmlu() -> tuple[Dataset, Dataset]` returns `(test, aux_train)`. H-M1 must contaminate from **test set** (PRD FR-1.2), so H-E1's `sample_contamination_subset(aux_train, ...)` samples from the wrong split — H-M1 needs its own `sample_contamination_ids` operating on `test_set`.
- `inject_contamination(base_model, tokenizer, contamination_items, lora_cfg, epochs=3, lr=2e-4, batch_size=4, grad_accum=8, output_dir=...)` has **no `seed` parameter** and default `lr=2e-4` (not 2e-5). H-M1 must call `set_seed(seed)` before invoking, and pass `lr=2e-5` explicitly.
- `build_lora_config(rank=16, alpha=32, dropout=0.05)` hardcodes `target_modules=["q_proj","v_proj"]` (2 modules). H-M1 needs 4 modules per FR-2.2 — cannot reuse as-is, needs a variant.
- `inject_contamination` returns unmodified `peft_model` (no training) when `len(contamination_items)==0` — handles the 0% level correctly for free.

---

## M-3: Contamination Injection Orchestration [Complexity: 15, Budget: 4]

**Applied**: Standard PyTorch + PEFT LoRA fine-tuning loop (reused H-E1 pattern)

### API Signatures

```python
# h-m1/code/data.py
def sample_contamination_ids(test_set: Dataset, frac: float, seed: int) -> set[int]:
    """Deterministic index sample from TEST set (not aux_train). random.seed(seed) then random.sample."""

def build_training_dataset(test_set: Dataset, contaminated_ids: set[int]) -> Dataset:
    """test_set.select(sorted(contaminated_ids)) -> Dataset with same columns as test_set."""

# h-m1/code/model.py
def build_lora_config_m1(rank: int = 16, alpha: int = 32, dropout: float = 0.05) -> LoraConfig:
    """Same as H-E1 build_lora_config but target_modules=[q_proj,v_proj,k_proj,o_proj] per FR-2.2."""

def inject_contamination_seeded(
    base_model, tokenizer, contamination_items: Dataset,
    lora_cfg: LoraConfig, seed: int,
    epochs: int = 3, lr: float = 2e-5, batch_size: int = 4, grad_accum: int = 8,
    output_dir: str = "./lora_output",
) -> "PeftModel":
    """set_seed(seed) then delegates to h_e1.code.model.inject_contamination(..., lr=lr)."""
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, 512] | max_length=512, padding="max_length" (H-E1 convention) |
| labels | [B, 512] | copy of input_ids (causal LM) |

### Pseudo-code

```
def inject_contamination_seeded(base_model, tokenizer, contamination_items, lora_cfg, seed, **kw):
    from transformers import set_seed
    set_seed(seed)
    return h_e1_inject_contamination(base_model, tokenizer, contamination_items, lora_cfg, **kw)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M3-1 | sample_contamination_ids | Deterministic set[int] selection from test_set, per (level, seed) |
| L-M3-2 | build_training_dataset | Subset test_set by contaminated_ids |
| L-M3-3 | build_lora_config_m1 | 4-module LoRA config extending H-E1 default |
| L-M3-4 | inject_contamination_seeded | Wrap H-E1 inject_contamination with set_seed + explicit lr=2e-5 |

---

## M-4: Full Test-Set Evaluation [Complexity: 12, Budget: 2]

**Applied**: Answer-token logit extraction pattern (reused H-E1 `get_answer_token_ids`)

### API Signatures

```python
# h-m1/code/evaluate.py
def evaluate_full_test_set(
    model, tokenizer, test_set: Dataset, answer_token_ids: list[int]
) -> list[dict]:
    """Runs inference on all 14,042 items. Returns [{"id": int, "correct": bool, "pred": str}, ...]"""

def compute_item_accuracy(eval_results: list[dict], contaminated_ids: set[int]) -> dict:
    """Returns {"contaminated_accuracy": float, "clean_accuracy": float, "effect_size": float}"""
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| logits | [4] | logits at answer_token_ids positions (A/B/C/D), per item |
| eval_results | list[14042] | one dict per test item |

### Pseudo-code

```
def evaluate_full_test_set(model, tokenizer, test_set, answer_token_ids):
    results = []
    for idx, item in enumerate(test_set):
        prompt = format_mmlu_prompt(item)  # H-E1 reused
        out = model(**tokenizer(prompt, return_tensors="pt"))
        last_logits = out.logits[0, -1, :]           # [vocab]
        answer_logits = last_logits[answer_token_ids]  # [4]
        pred_idx = answer_logits.argmax().item()
        correct = (pred_idx == item["answer"])
        results.append({"id": idx, "correct": correct, "pred": chr(ord('A')+pred_idx)})
    return results

def compute_item_accuracy(eval_results, contaminated_ids):
    cont = [r["correct"] for r in eval_results if r["id"] in contaminated_ids]
    clean = [r["correct"] for r in eval_results if r["id"] not in contaminated_ids]
    cont_acc = mean(cont) if cont else 0.0
    clean_acc = mean(clean)
    return {"contaminated_accuracy": cont_acc, "clean_accuracy": clean_acc,
            "effect_size": cont_acc - clean_acc}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M4-1 | evaluate_full_test_set | Batch-free loop over all 14,042 items, extract A/B/C/D logits, record correctness |
| L-M4-2 | compute_item_accuracy | Split by contaminated_ids, compute contaminated/clean accuracy + effect_size |

---

## Mechanism Verification (mechanism.py — not separately budgeted, PRD FR-5)

```python
def verify_contamination_mechanism(cont_acc: float, clean_acc: float) -> dict:
    """mechanism_active = cont_acc > clean_acc. Logs '[MECHANISM CHECK] ...' per PRD FR-5.3."""
    mechanism_active = cont_acc > clean_acc
    effect_size = cont_acc - clean_acc
    print(f"[MECHANISM CHECK] Contaminated: {cont_acc:.3f}, Clean: {clean_acc:.3f}")
    print(f"[MECHANISM CHECK] Effect: {effect_size:.3f}, Active: {mechanism_active}")
    return {"mechanism_active": mechanism_active, "effect_size": effect_size}

def verify_monotonic_trend(effect_sizes_by_level: dict[float, float]) -> bool:
    """effect_size(5%) < effect_size(10%) < effect_size(20%) < effect_size(50%). Excludes 0% level."""
    levels = sorted(k for k in effect_sizes_by_level if k > 0)
    values = [effect_sizes_by_level[l] for l in levels]
    return all(values[i] < values[i+1] for i in range(len(values)-1))

def aggregate_across_seeds(results_per_seed: list[dict]) -> dict:
    """Mean/std of effect_size across 3 seeds, per contamination level. Returns {level: {"mean": f, "std": f}}"""
```

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual H-E1 Code)

```python
# From: h-e1/code/data.py (ACTUAL CODE)
def load_mmlu() -> tuple[Dataset, Dataset]:
    """Returns (test_set, aux_train_set). H-M1 uses test_set for contamination (NOT aux_train)."""

def format_mmlu_prompt(item: dict) -> str:
    """'Question: {q}\\n\\nA. {c0}\\n...\\nAnswer:' — used for both eval and training format."""

# From: h-e1/code/model.py (ACTUAL CODE)
def load_base_model(model_id: str = "mistralai/Mistral-7B-v0.1"):
    """Returns (model, tokenizer). bf16, device_map='auto'."""

def build_lora_config(rank: int = 16, alpha: int = 32, dropout: float = 0.05) -> LoraConfig:
    """target_modules=['q_proj','v_proj'] hardcoded — H-M1 needs its own build_lora_config_m1 for 4 modules."""

def get_answer_token_ids(tokenizer) -> list[int]:
    """Returns token ids for [' A',' B',' C',' D']. Reused as-is."""

def format_training_example(item: dict) -> str:
    """'Question: {q}\\n\\n...Answer: {letter}' — includes answer, used by inject_contamination internally."""

def inject_contamination(
    base_model, tokenizer, contamination_items: Dataset, lora_cfg: LoraConfig,
    epochs: int = 3, lr: float = 2e-4, batch_size: int = 4, grad_accum: int = 8,
    output_dir: str = "./lora_output",
):
    """NO seed param (H-M1 must call set_seed() before). Default lr=2e-4 (H-M1 must pass lr=2e-5 explicitly
    per PRD FR-2.4). Returns unfit peft_model when len(contamination_items)==0 (handles 0% level)."""
```

**Verified from**: `h-e1/code/data.py`, `h-e1/code/model.py` (actual implementation, read directly).
