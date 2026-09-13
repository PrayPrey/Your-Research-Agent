# Logic: H-E1 (EXISTENCE PoC)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-2: Oracle Labeling [Complexity: 12, Budget: 2 subtasks]

**Applied**: PEFT/LoRA adapter loading pattern (huggingface/peft)

### API Signatures

```python
def load_base_and_adapters(
    base_model_name: str, adapter_ids: list[str]
) -> tuple[PreTrainedModel, dict[str, PeftModel]]:
    """Load frozen base model + PEFT-wrapped adapters, one per adapter_id."""
    ...

def compute_oracle_labels(
    samples: list[dict],
    base_model: PreTrainedModel,
    adapters: dict[str, PeftModel],
    cfg: Config,
) -> list[int]:
    """For each sample, argmin CE loss over adapters on target response. Returns adapter index per sample."""
    ...

def adapter_loss(model: PreTrainedModel, tokenizer, prompt: str, response: str) -> float:
    """Teacher-forced CE loss of response given prompt, single adapter active."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, T] | prompt+response tokens, single sample |
| logits | [1, T, V] | V = vocab size |
| loss | scalar | mean CE over response tokens only (prompt masked) |
| oracle_labels | [N] | int in [0, 8], argmin loss adapter index |

### Pseudo-code

```
for sample in samples:
    losses = []
    for adapter_id in adapter_ids:
        model.set_adapter(adapter_id)          # swap active LoRA
        loss = adapter_loss(model, tok, sample["prompt"], sample["response"])
        losses.append(loss)
    oracle_labels[i] = argmin(losses)           # best (lowest-loss) adapter
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-A2-1 | Adapter loading + loss fn | `load_base_and_adapters`, `adapter_loss` with prompt-masked CE |
| L-A2-2 | Oracle label loop | `compute_oracle_labels`: iterate samples x 9 adapters, argmin, store int labels |

---

## A-4: Linear Probe Model [Complexity: 6] — API only, no subtask budget

**Applied**: sentence-transformers + sklearn LogisticRegression canonical linear-probe pattern

```python
class AdapterSelectionProbe:
    def __init__(self, encoder_name: str, num_adapters: int, max_iter: int, solver: str, random_state: int):
        """Frozen SentenceTransformer encoder + sklearn LogisticRegression head."""
        ...

    def encode(self, texts: list[str]) -> np.ndarray:
        """texts: list[str] len N -> embeddings [N, 384]"""
        ...

    def fit(self, texts: list[str], adapter_labels: list[int]) -> None:
        """Encode then LogisticRegression.fit(X, y)."""
        ...

    def predict_proba(self, texts: list[str]) -> np.ndarray:
        """-> [N, num_adapters] softmax-like probabilities"""
        ...

    def evaluate(self, texts: list[str], adapter_labels: list[int]) -> dict:
        """-> {'top1_acc': float, 'top3_acc': float}"""
        ...
```

Top-3 via `np.argsort(-proba, axis=1)[:, :3]`, check `y_true in row`.
