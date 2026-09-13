---
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
date: "2026-08-25"
author: Anonymous
---

# Logic: H-E1 — ECE Measurement Pipeline

Applied: Guo-2017-ECE-equal-width-binning
Applied: lm-evaluation-harness-MC-logit-extraction

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None — new implementation

---

## A-3: Logit Extraction [Complexity: 14, Budget: 4 subtasks]

### L-3-1: extract_answer_token_ids [Budget: 1]

**File**: `evaluation/logit_extractor.py`

```python
def extract_answer_token_ids(
    tokenizer: AutoTokenizer,
    choices: list[str],
    warn_on_multitoken: bool = True
) -> list[int]:
    """Tokenize choices, return first token ID each. Warns if multi-token."""
```

**Pseudo-code**:
```
token_ids = []
for choice in choices:
    # Encode WITHOUT special tokens (no BOS/EOS) — critical for chat models
    ids = tokenizer.encode(choice, add_special_tokens=False)
    if len(ids) > 1 and warn_on_multitoken:
        warnings.warn(f"Choice '{choice}' tokenizes to {len(ids)} tokens; using first.")
    token_ids.append(ids[0])
return token_ids
```

**Edge cases**:
- Chat template: call `encode()` directly, not `apply_chat_template` — avoids injected tokens
- BOS auto-prepend: `add_special_tokens=False` prevents BOS contamination
- Empty choice: raise `ValueError(f"Empty choice string at index {i}")`
- Unknown token: tokenizer returns `[unk_token_id]` — acceptable, no special handling needed

---

### L-3-2: extract_mc_logits [Budget: 1]

**File**: `evaluation/logit_extractor.py`

```python
def extract_mc_logits(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    context: str,
    answer_choices: list[str],
    device: str
) -> tuple[np.ndarray, int, float]:  # (probs [n_choices], pred_label, confidence)
    """Last-position logit extraction; softmax over answer token IDs."""
```

**Tensor shapes**:

| Step | Shape | Note |
|------|-------|------|
| input_ids | `(1, seq_len)` | Tokenized context |
| logits (model out) | `(1, seq_len, vocab_size)` | Full logits tensor |
| last_logits | `(vocab_size,)` | `logits[0, -1, :]` |
| answer_logits | `(n_choices,)` | Index by answer_token_ids |
| probs | `(n_choices,)` | softmax(answer_logits) |

**Pseudo-code**:
```
inputs = tokenizer(context, return_tensors="pt").to(device)
with torch.no_grad():
    out = model(**inputs)                         # logits: (1, seq_len, vocab_size)
last_logits = out.logits[0, -1, :]               # (vocab_size,)
answer_logits = last_logits[answer_token_ids]    # (n_choices,) — index by list
probs = F.softmax(answer_logits.float(), dim=0).cpu().numpy()  # cast bfloat16→float32 before softmax
pred_label = int(np.argmax(probs))
confidence = float(probs[pred_label])
return probs, pred_label, confidence
```

**Edge cases**:
- bfloat16 → float32 cast before softmax prevents numerical underflow
- `answer_token_ids` passed as `torch.tensor(answer_token_ids)` for efficient indexing
- Detach not needed inside `torch.no_grad()` block

---

### L-3-3: extract_cell [Budget: 1]

**File**: `evaluation/logit_extractor.py`

```python
def extract_cell(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    dataset: Dataset,
    task: str,
    model_id: str,
    batch_size: int = 8,
) -> CellResult:  # CellResult(confidences, pred_labels, true_labels, prob_sums)
    """Extract logits for all examples in one (model, task, split) cell."""
```

**Pseudo-code**:
```
answer_token_ids = extract_answer_token_ids(tokenizer, TASK_CHOICES[task])
confidences, pred_labels, true_labels, prob_sums = [], [], [], []

for example in tqdm(dataset):
    context, choices = format_mc_prompt(example, task, model_id)
    try:
        probs, pred, conf = extract_mc_logits(model, tokenizer, context, choices, device)
    except RuntimeError as e:
        if "out of memory" in str(e).lower():
            torch.cuda.empty_cache()
            # retry once — single example always fits
            probs, pred, conf = extract_mc_logits(model, tokenizer, context, choices, device)
        else:
            raise
    confidences.append(conf)
    pred_labels.append(pred)
    true_labels.append(int(example["label"]))
    prob_sums.append(float(probs.sum()))

return CellResult(
    confidences=np.array(confidences),
    pred_labels=np.array(pred_labels),
    true_labels=np.array(true_labels),
    prob_sums=np.array(prob_sums),
)
```

**Notes**:
- `batch_size` param kept for signature compatibility; single-example loop is safer for OOM recovery
- OOM retry: single example after `empty_cache()` is the minimal recovery — no half-batch logic needed
- `TASK_CHOICES` is a module-level dict mapping task name → list of choice strings (e.g. `["A", "B"]` for binary)

---

### L-3-4: prevalidate_cell [Budget: 1]

**File**: `evaluation/validator.py`

```python
def prevalidate_cell(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    dataset: Dataset,
    task: str,
    model_id: str,
    n: int = 10
) -> ValidationResult:  # ValidationResult(passed, indicators)
    """Run extract_cell on first n examples; check sanity before full evaluation."""
```

**Pseudo-code**:
```
subset = dataset.select(range(min(n, len(dataset))))
result = extract_cell(model, tokenizer, subset, task, model_id)

indicators = {
    "coverage_met": len(result.confidences) >= n,
    "non_degenerate": float((result.confidences < 0.999).mean()) > 0.90,
    "non_uniform": float(result.confidences.mean()) > 0.40,
    "ece_plausible": True,          # skip ECE check for n=10 (too few examples)
    "probs_sum_to_one": abs(float(result.prob_sums.mean()) - 1.0) < 1e-3,
}
passed = all(indicators.values())
return ValidationResult(passed=passed, indicators=indicators)
```

**Edge cases**:
- `ece_plausible` always True at prevalidation (n=10 insufficient for reliable ECE)
- If `extract_cell` throws, catch at call site in orchestrator — not here

---

## A-4: ECE + Validation [Complexity: 13, Budget: 2 subtasks]

### L-4-1: compute_ece [Budget: 1]

**File**: `evaluation/ece.py`

```python
def compute_ece(
    confidences: np.ndarray,  # (n_examples,)
    correct: np.ndarray,       # (n_examples,) bool or 0/1 int
    n_bins: int = 15
) -> float:
    """Guo 2017 equal-width ECE. Empty bins skipped (not NaN)."""
```

**Pseudo-code**:
```
bins = np.linspace(0, 1, n_bins + 1)   # n_bins+1 edges → n_bins intervals
ece = 0.0
n = len(confidences)

for b in range(n_bins):
    mask = (confidences > bins[b]) & (confidences <= bins[b + 1])
    # Right-edge of last bin: include == 1.0
    if b == n_bins - 1:
        mask = (confidences >= bins[b]) & (confidences <= bins[b + 1])
    if mask.sum() == 0:
        continue                        # skip empty bins — no NaN contribution
    acc_b = correct[mask].mean()
    conf_b = confidences[mask].mean()
    ece += (mask.sum() / n) * abs(acc_b - conf_b)

return float(ece)
```

**Edge cases**:
- Last bin `(0.933, 1.0]` must include 1.0 exactly (confidence=1.0 after softmax is rare but possible)
- Empty bins: `continue` — correct per Guo 2017 (no weight contribution)
- `correct` may be bool array: `.mean()` works for both bool and int

---

### L-4-2: verify_logit_extraction [Budget: 1]

**File**: `evaluation/validator.py`

```python
def verify_logit_extraction(
    cell_result: CellResult,
    ece_15: float,
) -> ValidationResult:  # ValidationResult(passed: bool, indicators: dict)
    """FR-4.3: 5-indicator post-hoc cell validation."""
```

**Pseudo-code**:
```
c = cell_result.confidences
indicators = {
    "coverage_met":      len(c) >= 200,
    "non_degenerate":    float((c < 0.999).mean()) > 0.90,
    "non_uniform":       float(c.mean()) > 0.40,
    "ece_plausible":     0.0 <= ece_15 <= 0.5,
    "probs_sum_to_one":  abs(float(cell_result.prob_sums.mean()) - 1.0) < 1e-3,
}
passed = all(indicators.values())
return ValidationResult(passed=passed, indicators=indicators)
```

**Thresholds** (from FR-4.3, not tunable):
- `non_degenerate`: `< 0.999` catches only full-confidence collapse; `> 0.90` allows up to 10% saturated examples
- `non_uniform`: `> 0.40` — uniform over 4 choices = 0.25, so 0.40 filters near-random models
- `ece_plausible`: `[0.0, 0.5]` — ECE > 0.5 indicates extraction error, not just poor calibration

---

## Subtask Summary

| ID | Subtask | File | Budget |
|----|---------|------|--------|
| L-3-1 | extract_answer_token_ids | evaluation/logit_extractor.py | 1 |
| L-3-2 | extract_mc_logits | evaluation/logit_extractor.py | 1 |
| L-3-3 | extract_cell | evaluation/logit_extractor.py | 1 |
| L-3-4 | prevalidate_cell | evaluation/validator.py | 1 |
| L-4-1 | compute_ece | evaluation/ece.py | 1 |
| L-4-2 | verify_logit_extraction | evaluation/validator.py | 1 |

**Total: 6/6 subtasks used**
