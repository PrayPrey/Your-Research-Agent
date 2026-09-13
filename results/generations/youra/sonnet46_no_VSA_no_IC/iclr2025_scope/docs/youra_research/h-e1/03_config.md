---
hypothesis_id: h-e1
phase: 03_config
date: 2026-08-22
author: yoon303@etri.re.kr
---

# Config: h-e1 — Per-Layer Attention Entropy Stability

Applied: Standard HuggingFace inference-only dataclass pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No existing codebase — new config design
**Config Files Found**: None
**Pattern Used**: dataclass

---

## A-3: Model Loading [Complexity: 6, Budget: 1 subtask]

### Configuration

```python
from dataclasses import dataclass, field
import os

@dataclass
class ModelConfig:
    model_name: str = "meta-llama/Llama-2-7b-hf"
    attn_implementation: str = "eager"   # Non-standard: flash_attention_2 blocks output_attentions=True
    torch_dtype: str = "float16"
    device_map: str = "auto"

    def __post_init__(self):
        if self.attn_implementation != "eager":
            raise ValueError(
                f"attn_implementation must be 'eager', got '{self.attn_implementation}'. "
                "flash_attention_2 does not support output_attentions=True."
            )

    @property
    def hf_token(self) -> str | None:
        return os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-A3-1 | Model loading config | ModelConfig dataclass with eager-only validation and HF_TOKEN env lookup |

---

## A-6: Integration & Gate [Complexity: 7, Budget: 1 subtask]

### Configuration

```python
from dataclasses import dataclass, field

@dataclass
class ExperimentConfig:
    n_subsets: int = 3
    subset_size: int = 100
    seqlen: int = 2048
    eps: float = 1e-9
    gate_threshold: float = 0.8
    output_dir: str = "."
    figures_dir: str = "figures/"
```

### YAML Config Schema (config.yaml)

```yaml
model:
  model_name: "meta-llama/Llama-2-7b-hf"
  attn_implementation: "eager"   # MUST be "eager" — do not change
  torch_dtype: "float16"
  device_map: "auto"

experiment:
  n_subsets: 3
  subset_size: 100
  seqlen: 2048
  eps: 1.0e-9
  gate_threshold: 0.8
  output_dir: "."
  figures_dir: "figures/"
```

### Validation Rules

| Field | Rule |
|-------|------|
| `attn_implementation` | MUST equal `"eager"` — enforced in `__post_init__` |
| `gate_threshold` | Default 0.8; GATE PASS requires `min(rho_AB, rho_AC, rho_BC) >= gate_threshold` |
| `n_subsets` | Fixed at 3 (subsets A, B, C); changing breaks Spearman pairwise logic |
| `eps` | 1e-9 prevents log(0) in Shannon entropy; do not set to 0 |

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `HF_TOKEN` | HuggingFace token for Llama-2 gated model access (primary) |
| `HUGGING_FACE_HUB_TOKEN` | Alternative HF token env var (fallback) |

At least one must be set before running. `ModelConfig.hf_token` checks both.

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-A6-1 | Experiment config | ExperimentConfig dataclass, YAML schema, validation rules, env var handling |
