# H-E1 Configuration (EXISTENCE Test)

**Hypothesis**: Given multiple sampled responses + token logits from Llama-2-7B-chat on QA, entropy and semantic consistency can be computed per response.

**PoC scope**: single fixed config, no tuning, no grid, 1 seed. Just prove the pipeline runs and produces both metrics.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design (no existing config/code files found in repo)
**Config Files Found**: None
**Pattern Used**: dataclass (single source of truth, no dict duplication)

---

## Config Schema

```python
import os
from dataclasses import dataclass, field
from typing import Literal

@dataclass
class HE1Config:
    # --- Model ---
    model_name: str = "meta-llama/Llama-2-7b-chat-hf"
    torch_dtype: Literal["float16", "bfloat16"] = "float16"  # 7B fits ~14GB in FP16
    device_map: str = "auto"
    hf_token: str = field(default_factory=lambda: os.environ.get("HF_TOKEN", ""))

    # --- Generation ---
    temperature: float = 0.7   # standard for diverse-but-coherent sampling (semantic consistency needs variance)
    top_p: float = 0.9
    max_new_tokens: int = 128  # sufficient for short-form QA answers
    n_samples: int = 10        # min samples for stable consistency metric (per SelfCheckGPT precedent)
    do_sample: bool = True
    return_dict_in_generate: bool = True
    output_scores: bool = True  # required to access token logits for entropy

    # --- Dataset ---
    dataset_name: str = "trivia_qa"
    dataset_config: str = "rc.nocontext"
    dataset_split: str = "validation"
    n_questions: int = 50       # PoC subset only, enough to see effect exists
    dataset_seed: int = 42

    # --- Embedding (semantic consistency) ---
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_device: str = "cuda"

    # --- Output ---
    output_dir: str = "results/h-e1"
    checkpoint_every: int = 10  # save every 10 questions (cheap resume, PoC scale)
    log_file: str = "results/h-e1/run.log"

    # --- Hardware ---
    min_vram_gb: int = 16       # 7B FP16 (~14GB) + MiniLM + activations headroom
    device: str = "cuda"

    # --- Reproducibility ---
    seed: int = 42
```

## Instantiation (copy-paste)

```python
CONFIG = HE1Config()
```

## Environment Variable Mappings

| Env Var | Field | Required |
|---------|-------|----------|
| `HF_TOKEN` | `hf_token` | Yes (gated Llama-2 weights) |
| `CUDA_VISIBLE_DEVICES` | (external, not a field) | No |

## Validation Rules

```python
def validate(cfg: HE1Config) -> None:
    assert cfg.hf_token, "HF_TOKEN env var must be set (gated model)"
    assert cfg.n_samples >= 2, "need >=2 samples for semantic consistency"
    assert cfg.output_scores, "output_scores required for entropy computation"
    assert 0 < cfg.temperature <= 2.0
    assert cfg.max_new_tokens > 0
```

## YAML Equivalent (optional, for CLI override)

```yaml
model_name: meta-llama/Llama-2-7b-chat-hf
torch_dtype: float16
temperature: 0.7
max_new_tokens: 128
n_samples: 10
dataset_config: rc.nocontext
dataset_split: validation
n_questions: 50
embedding_model: sentence-transformers/all-MiniLM-L6-v2
seed: 42
```

---

## A-1: H-E1 Pipeline Config [Complexity: 1, Budget: 1]

**Applied**: Standard PyTorch/HF defaults for FP16 generation + sentence-transformers embedding

### Configuration
Uses `HE1Config` above directly — no per-module split needed at PoC scale (single script/pipeline).

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Load config | Instantiate `HE1Config()`, call `validate()` before run |
