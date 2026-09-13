# Logic: H-E1 LoRA-KV Misalignment Diagnostic

**Applied**: PeftModel eager attention extraction pattern
**Applied**: GQA repeat_interleave head expansion pattern
**Applied**: Sequential model loading for VRAM management

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-4: Locret CIS Extraction [Complexity: 15, Budget: 4 subtasks]

### API Signatures

```python
# code/locret_extractor.py
import torch
from torch import Tensor
from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedModel
from typing import Optional

class LocretExtractor:
    def __init__(self, config: "ExperimentConfig"):
        """Initialize with experiment config."""
        self.config = config
        self.model: Optional[PreTrainedModel] = None

    def load_model(self) -> PreTrainedModel:
        """Load hyx21/Locret-llama-3.1-8B-instruct with official Locret pattern."""
        # L-4-1: Official Locret loading
        model = AutoModelForCausalLM.from_pretrained(
            self.config.locret_checkpoint,  # "hyx21/Locret-llama-3.1-8B-instruct"
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,  # Locret uses custom modeling code
        )
        model.eval()
        self.model = model
        return model

    def extract_cis_scores(
        self,
        model: PreTrainedModel,
        input_ids: Tensor,        # [1, L]
        attention_mask: Tensor,   # [1, L]
    ) -> list[Tensor]:
        """
        Extract CIS scores per layer via output_retaining_scores=True.
        Returns list of 32 tensors, each shape (num_kv_heads, L) = (8, L).
        """
        # L-4-2: CIS extraction with output_retaining_scores
        with torch.no_grad():
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                output_retaining_scores=True,
            )
        # outputs.retaining_scores: tuple of 32 tensors, each (1, L, num_kv_heads)
        # L-4-3: Shape validation and per-layer indexing
        all_layer_scores = []
        for layer_idx in range(self.config.num_layers):
            # retaining_scores[layer_idx]: (1, L, num_kv_heads)
            cis = outputs.retaining_scores[layer_idx]  # (1, L, 8)
            cis = cis.squeeze(0).T.contiguous()        # (8, L)
            # L-4-3: Validate shape
            assert cis.shape == (self.config.num_kv_heads, input_ids.shape[1]), \
                f"CIS shape mismatch at layer {layer_idx}: {cis.shape}"
            all_layer_scores.append(cis)
        return all_layer_scores  # list[32] of (8, L)

    def get_layer_scores(
        self,
        all_layer_scores: list[Tensor],
        layer_idx: int,
    ) -> Tensor:
        """Return (num_kv_heads, seq_len) = (8, L) for a specific layer."""
        return all_layer_scores[layer_idx]  # (8, L)

    def unload(self) -> None:
        """L-4-4: Free GPU memory after extraction."""
        if self.model is not None:
            del self.model
            self.model = None
        torch.cuda.empty_cache()
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| `input_ids` | `[1, L]` | Single example, seq len L ≤ 512 |
| `attention_mask` | `[1, L]` | 1=real token, 0=padding |
| `retaining_scores[i]` | `[1, L, 8]` | Raw Locret output per layer |
| `cis` (after squeeze+T) | `[8, L]` | num_kv_heads × seq_len |
| return value | `list[32]` of `[8, L]` | 32 layers |

### Pseudo-code (L-4-2: CIS Extraction Algorithm)

```
1. model.eval(); torch.no_grad()
2. outputs = model(input_ids, attention_mask, output_retaining_scores=True)
   # CIS = sigma([Q,K,V] @ W1) @ W2  (computed inside Locret attention layers)
3. for layer_idx in 0..31:
       raw = outputs.retaining_scores[layer_idx]  # (1, L, 8)
       cis = raw.squeeze(0).T                     # (8, L)
       validate shape == (8, L)
       store cis
4. return list of 32 (8, L) tensors
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Locret model loading | `AutoModelForCausalLM` with `trust_remote_code=True`, `torch.float16`, `device_map="auto"` |
| L-4-2 | CIS score extraction | Forward with `output_retaining_scores=True`, access `outputs.retaining_scores` |
| L-4-3 | Shape validation | `squeeze(0).T` → `(8, L)`; assert shape per layer |
| L-4-4 | Memory management | `unload()` method: del model + `torch.cuda.empty_cache()` |

---

## A-3: LoRA Attention Extraction [Complexity: 14, Budget: 3 subtasks]

### API Signatures

```python
# code/lora_extractor.py
import torch
from torch import Tensor
from transformers import AutoModelForSequenceClassification, AutoTokenizer, PreTrainedModel, PreTrainedTokenizer
from peft import PeftModel, LoraConfig, TaskType, get_peft_model
from typing import Optional

class LoRAExtractor:
    def __init__(self, config: "ExperimentConfig"):
        """Initialize with experiment config."""
        self.config = config
        self.model: Optional[PreTrainedModel] = None
        self.tokenizer: Optional[PreTrainedTokenizer] = None

    def load_model(self) -> tuple[PreTrainedModel, PreTrainedTokenizer]:
        """
        Load LLaMA-3.1-8B + LoRA MNLI; attn_implementation='eager' mandatory.
        Falls back to LoRA fine-tune if checkpoint incompatible.
        """
        # L-3-1: Load base model with eager attention
        tokenizer = AutoTokenizer.from_pretrained(self.config.lora_base_model)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        base_model = AutoModelForSequenceClassification.from_pretrained(
            self.config.lora_base_model,  # "meta-llama/Meta-Llama-3.1-8B"
            num_labels=self.config.num_labels,  # 3
            attn_implementation="eager",        # CRITICAL: enables output_attentions
            torch_dtype=torch.float16,
            device_map="auto",
        )

        # L-3-1: Try primary checkpoint, fallback to LoRA fine-tune
        try:
            model = PeftModel.from_pretrained(
                base_model,
                self.config.lora_checkpoint,  # "yophis/DRM-Llama-3.1-8B-mnli"
            )
        except Exception:
            # Fallback: apply fresh LoRA config
            lora_config = LoraConfig(
                task_type=TaskType.SEQ_CLS,
                r=16,
                lora_alpha=32,
                target_modules=["q_proj", "k_proj", "v_proj"],
                lora_dropout=0.1,
            )
            model = get_peft_model(base_model, lora_config)
            # Note: fallback model is untrained; caller should fine-tune 3 epochs

        model.eval()
        self.model = model
        self.tokenizer = tokenizer
        return model, tokenizer

    def extract_attention_scores(
        self,
        model: PreTrainedModel,
        input_ids: Tensor,       # [1, L]
        attention_mask: Tensor,  # [1, L]
    ) -> list[Tensor]:
        """
        Forward pass with output_attentions=True.
        Returns list of 32 tensors, each (num_query_heads, L) = (32, L).
        Aggregation: sum over query axis (dim=2), squeeze batch dim.
        """
        # L-3-2: Attention extraction
        with torch.no_grad():
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                output_attentions=True,
            )
        # outputs.attentions: tuple of 32 tensors, each (1, 32, L, L)
        # L-3-3: GQA-aware aggregation
        all_layer_scores = []
        for layer_idx in range(self.config.num_layers):
            attn = outputs.attentions[layer_idx]   # (1, 32, L, L)
            # Sum over query dimension (dim=2) to get per-token importance
            per_token = attn.sum(dim=2).squeeze(0) # (32, L)
            all_layer_scores.append(per_token)
        return all_layer_scores  # list[32] of (32, L)

    def get_layer_scores(
        self,
        all_layer_scores: list[Tensor],
        layer_idx: int,
    ) -> Tensor:
        """Return (num_query_heads, seq_len) = (32, L) for a specific layer."""
        return all_layer_scores[layer_idx]  # (32, L)

    def unload(self) -> None:
        """Free GPU memory after extraction."""
        if self.model is not None:
            del self.model
            self.model = None
        torch.cuda.empty_cache()
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| `input_ids` | `[1, L]` | Batch size 1, L ≤ 512 |
| `attention_mask` | `[1, L]` | 1=real, 0=padding |
| `outputs.attentions[i]` | `[1, 32, L, L]` | Raw attention weights per layer |
| `per_token` (after sum+squeeze) | `[32, L]` | num_query_heads × seq_len |
| return value | `list[32]` of `[32, L]` | 32 layers |

### Pseudo-code (L-3-3: GQA-Aware Aggregation)

```
# LLaMA-3.1-8B: 32 query heads, 8 KV heads (GQA)
# output_attentions returns full (32, L, L) matrix (eager mode expands KV)
1. outputs = model(input_ids, attention_mask, output_attentions=True)
2. for layer_idx in 0..31:
       attn = outputs.attentions[layer_idx]   # (1, 32, L, L)
       # dim=2 is the "attending-from" query position axis
       per_token = attn.sum(dim=2)            # (1, 32, L) — sum query axis
       per_token = per_token.squeeze(0)       # (32, L)
       store per_token
3. return list of 32 (32, L) tensors
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | PeftModel loading | `AutoModelForSequenceClassification` with `attn_implementation="eager"` + `PeftModel.from_pretrained`; fallback LoRA config |
| L-3-2 | Attention extraction | Forward with `output_attentions=True`; access `outputs.attentions` tuple |
| L-3-3 | GQA aggregation | `attn.sum(dim=2).squeeze(0)` → `(32, L)`; no repeat_interleave needed here (done in correlator) |

---

## Sequential Loading Pattern (Memory Management)

```python
# run_experiment.py orchestration pattern
# Step 1: Extract LoRA attention scores
lora_extractor = LoRAExtractor(config)
model, tokenizer = lora_extractor.load_model()
lora_all_examples = []
for i, example in enumerate(dataset):
    input_ids = example["input_ids"].unsqueeze(0).to(model.device)
    attention_mask = example["attention_mask"].unsqueeze(0).to(model.device)
    scores = lora_extractor.extract_attention_scores(model, input_ids, attention_mask)
    lora_all_examples.append(scores)  # list[N] of list[32] of (32, L)
lora_extractor.unload()  # Free ~16GB VRAM before loading Locret

# Step 2: Extract Locret CIS scores
locret_extractor = LocretExtractor(config)
model = locret_extractor.load_model()
cis_all_examples = []
for i, example in enumerate(dataset):
    input_ids = example["input_ids"].unsqueeze(0).to(model.device)
    attention_mask = example["attention_mask"].unsqueeze(0).to(model.device)
    scores = locret_extractor.extract_cis_scores(model, input_ids, attention_mask)
    cis_all_examples.append(scores)  # list[N] of list[32] of (8, L)
locret_extractor.unload()
```

---

## Non-Padding Token Masking Pattern

```python
# Used in correlate.py — applied before spearmanr call
def _mask_padding(
    scores: Tensor,          # (num_heads, L)
    attention_mask: Tensor,  # (1, L) or (L,)
) -> Tensor:
    """Return scores[:, non_pad_indices] → (num_heads, T) where T = non-padding tokens."""
    mask = attention_mask.squeeze(0).bool()  # (L,)
    return scores[:, mask]                   # (num_heads, T)
```

### GQA Expansion in Correlator

```python
# correlate.py
cis_expanded = cis_scores.repeat_interleave(
    self.config.kv_repeat,  # 4 = 32 // 8
    dim=0
)  # (8, L) → (32, L)
# Then correlate lora_scores (32, L) vs cis_expanded (32, L) per head
```
