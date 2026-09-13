# Logic: H-M2 (Representation Invariance Mechanism)

Applied: Mean-pooled last-hidden-state extraction + cosine similarity (standard sentence-embedding pattern)
Applied: LoRA fine-tuning contamination injection, reused from H-M1

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1) + green-field (new paraphrase/representation modules)
**Status**: API signatures for training/data reused verbatim from H-M1's `03_logic.md` (verified actual code); representation-extraction and paraphrase-augmentation modules are new — no prior implementation exists.
**Analyzed Path**: `h-m1/code/data.py`, `h-m1/code/model.py` (via H-M1 `03_logic.md`, which itself verified against `h-e1/code/`)
**Relevant Symbols reused**: `load_mmlu`, `format_mmlu_prompt`, `load_base_model`, `build_lora_config_m1`, `sample_contamination_ids`, `build_training_dataset`, `inject_contamination_seeded`

**Deviations to watch**:
- `inject_contamination_seeded(base_model, tokenizer, contamination_items, lora_cfg, seed, epochs=3, lr=2e-5, ...)` has no native support for multi-sample-per-item (paraphrase) datasets — H-M2's `create_augmented_dataset` must pre-expand items into a flat `Dataset` before calling it.
- `load_mmlu()` returns `(test_set, aux_train)`; contamination sampling must use `test_set` per H-M1 convention.

---

## M2-1: Paraphrase Generation & Augmented Dataset [Complexity: 8, Budget: 3]

**Applied**: Standard PyTorch + HF T5 generation pattern

### API Signatures

```python
# h-m2/code/paraphrase.py
def generate_paraphrases(
    item_text: str, k: int = 5, methods: list[str] = ["t5", "gpt4", "rule"]
) -> list[str]:
    """Generate k paraphrases via mixed methods (40% t5, 40% gpt4, 20% rule). Returns k strings."""

def build_paraphrase_bank(
    test_set: Dataset, item_ids: set[int], k: int = 5, seed: int = 42
) -> dict[int, list[str]]:
    """Deterministic paraphrase generation for given item_ids. Returns {item_id: [k paraphrase strings]}."""
```

```python
# h-m2/code/data.py
class ParaphraseAugmentedTrainer:
    def __init__(self, model, contamination_pct: float, paraphrases_per_item: int = 3):
        """LoRA config: r=16, alpha=32, dropout=0.05, target_modules=[q_proj,v_proj,k_proj,o_proj] (reuse build_lora_config_m1)."""
        ...

    def create_augmented_dataset(
        self, test_set: Dataset, paraphrase_bank: dict[int, list[str]], seed: int = 42
    ) -> tuple[Dataset, set[int]]:
        """Flatten original + paraphrases_per_item paraphrases into one Dataset (text column) for training."""
        ...

    def train(self, train_dataset: Dataset, seed: int, epochs: int = 3, lr: float = 2e-5) -> "PeftModel":
        """Delegates to inject_contamination_seeded with flattened train_dataset."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| train_dataset (verbatim) | 1,404 rows | 1 row/item |
| train_dataset (paraphrase) | 5,616 rows | 1,404 × (1 original + 3 paraphrases) |

### Pseudo-code

```
def create_augmented_dataset(self, test_set, paraphrase_bank, seed):
    ids = sample_contamination_ids(test_set, self.contamination_pct, seed)
    rows = []
    for idx in sorted(ids):
        rows.append(format_mmlu_prompt(test_set[idx]))  # original
        for p in paraphrase_bank[idx][:self.paraphrases_per_item]:
            rows.append(p)
    return Dataset.from_dict({"text": rows}), ids
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M2-1-1 | generate_paraphrases | Mixed T5/GPT-4/rule-based generation, k per item |
| L-M2-1-2 | build_paraphrase_bank | Deterministic bank of K=5 paraphrases for eval item pool |
| L-M2-1-3 | ParaphraseAugmentedTrainer | Flatten items+paraphrases, train via inject_contamination_seeded |

---

## M2-2: Representation Extraction & Similarity [Complexity: 10, Budget: 3]

**Applied**: Attention-masked mean pooling + cosine similarity (sentence-transformers pattern)

### API Signatures

```python
# h-m2/code/represent.py
class RepresentationInvarianceEvaluator:
    def __init__(self, model, tokenizer):
        ...

    def extract_representation(self, text: str) -> torch.Tensor:
        """Mean-pooled last hidden state, mask-excluded padding. Returns [4096]."""
        ...

    def compute_paraphrase_similarity(self, original: str, paraphrases: list[str]) -> float:
        """Mean cosine similarity between original and each paraphrase representation. Returns scalar."""
        ...

    def evaluate_invariance(self, test_items: list[str], paraphrases: list[list[str]]) -> np.ndarray:
        """Per-item MPS over N items. Returns [N] array."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| inputs["input_ids"] | [1, seq_len] | single-item batch |
| hidden_states[-1] | [1, seq_len, 4096] | last-layer hidden states |
| mask | [1, seq_len, 1] | broadcast for pooling |
| pooled | [4096] | mean-pooled representation |
| similarity | scalar | cosine similarity, float |
| MPS array | [N] | one value per evaluated item |

### Pseudo-code

**Mean pooling with attention mask:**
```
def extract_representation(self, text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        out = model(**inputs, output_hidden_states=True)
    hidden = out.hidden_states[-1]                      # [1, seq, 4096]
    mask = inputs["attention_mask"].unsqueeze(-1)        # [1, seq, 1]
    pooled = (hidden * mask).sum(dim=1) / mask.sum(dim=1)  # [1, 4096]
    return pooled.squeeze(0)                              # [4096]
```

**Cosine similarity:**
```
def compute_paraphrase_similarity(self, original, paraphrases):
    orig_rep = self.extract_representation(original)     # [4096]
    sims = [F.cosine_similarity(orig_rep, self.extract_representation(p), dim=0).item()
            for p in paraphrases]
    return np.mean(sims)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M2-2-1 | extract_representation | Mask-aware mean pooling of last hidden layer |
| L-M2-2-2 | compute_paraphrase_similarity | Per-item mean cosine similarity to K paraphrases |
| L-M2-2-3 | evaluate_invariance | Batch over N items, return MPS array |

---

## M2-3: Mechanism Verification [Complexity: 6, Budget: 2]

**Applied**: Two-sample t-test + Cohen's d (scipy.stats)

### API Signatures

```python
# h-m2/code/mechanism.py
def verify_invariance_mechanism(
    verbatim_model, paraphrase_model, tokenizer,
    test_items: list[str], paraphrases: list[list[str]]
) -> dict:
    """Compares MPS distributions across the two models. Returns metrics dict + logs [MECHANISM CHECK]."""
    ...
```

### Pseudo-code

**Statistical comparison (t-test + Cohen's d):**
```
def verify_invariance_mechanism(verbatim_model, paraphrase_model, tokenizer, test_items, paraphrases):
    ev = RepresentationInvarianceEvaluator(verbatim_model, tokenizer)
    ep = RepresentationInvarianceEvaluator(paraphrase_model, tokenizer)

    mps_v = ev.evaluate_invariance(test_items, paraphrases)   # [N]
    mps_p = ep.evaluate_invariance(test_items, paraphrases)   # [N]

    t_stat, p_value = stats.ttest_ind(mps_p, mps_v)
    effect_size = (mps_p.mean() - mps_v.mean()) / mps_v.std()  # Cohen's d
    mechanism_active = mps_p.mean() > mps_v.mean()

    print(f"[MECHANISM CHECK] Verbatim MPS: {mps_v.mean():.4f}")
    print(f"[MECHANISM CHECK] Paraphrase MPS: {mps_p.mean():.4f}")
    print(f"[MECHANISM CHECK] Difference: {mps_p.mean() - mps_v.mean():.4f}")
    print(f"[MECHANISM CHECK] p-value: {p_value:.4e}, Active: {mechanism_active}")

    return {
        "mechanism_active": bool(mechanism_active),
        "mps_verbatim": float(mps_v.mean()),
        "mps_paraphrase": float(mps_p.mean()),
        "difference": float(mps_p.mean() - mps_v.mean()),
        "effect_size": float(effect_size),
        "p_value": float(p_value),
    }
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M2-3-1 | verify_invariance_mechanism | t-test + Cohen's d over MPS arrays, mechanism_active flag |
| L-M2-3-2 | aggregate_across_seeds | Reuse H-M1 `aggregate_across_seeds` for 3-seed mean/std of effect_size |

---

## External Dependencies (Base Hypothesis: H-M1)

### API Signatures (From H-M1 `03_logic.md`, verified against actual H-E1/H-M1 code)

```python
# From: h-m1/code/data.py
def load_mmlu() -> tuple[Dataset, Dataset]:
    """Returns (test_set, aux_train_set). H-M2 uses test_set."""

def sample_contamination_ids(test_set: Dataset, frac: float, seed: int) -> set[int]:
    """Deterministic index sample from test_set."""

def format_mmlu_prompt(item: dict) -> str:
    """'Question: {q}\\n\\nA. {c0}\\n...\\nAnswer:'"""

# From: h-m1/code/model.py
def load_base_model(model_id: str = "mistralai/Mistral-7B-v0.1"):
    """Returns (model, tokenizer). bf16, device_map='auto'."""

def build_lora_config_m1(rank: int = 16, alpha: int = 32, dropout: float = 0.05) -> LoraConfig:
    """target_modules=[q_proj,v_proj,k_proj,o_proj]."""

def inject_contamination_seeded(
    base_model, tokenizer, contamination_items: Dataset, lora_cfg: LoraConfig, seed: int,
    epochs: int = 3, lr: float = 2e-5, batch_size: int = 4, grad_accum: int = 8,
    output_dir: str = "./lora_output",
) -> "PeftModel":
    """set_seed(seed) then LoRA fine-tune. H-M2 passes flattened original+paraphrase Dataset as contamination_items."""
```

**Verified from**: `h-m1/03_logic.md` (which verified against `h-e1/code/data.py`, `h-e1/code/model.py`).

**Note**: `inject_contamination_seeded` expects a `Dataset` of formatted text/QA rows — H-M2's `ParaphraseAugmentedTrainer.create_augmented_dataset` must produce compatible schema (single `text` column mirroring `format_mmlu_prompt` output) before calling it.
