# H-M1 Configuration (MECHANISM Test)

**Hypothesis**: Token entropy correlates with answer correctness on TriviaQA (Llama-2-7B-chat).

**Scope**: Full validation set (~11,313 questions), single fixed config, MUST_WORK gate.

**Applied**: Dataclass config pattern (consistent with h-e1); sampling-loop + statistical-gate config pattern for uncertainty-correctness validation.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: h-e1/code/ not found on disk — verified against h-e1/03_config.md spec (HE1Config dataclass) instead. Field names below match that spec; Phase 4 must re-verify if h-e1/code/config.py materializes with different names.
**Config Files Found**: `h-e1/03_config.md` (HE1Config dataclass, spec-only)
**Pattern Used**: dataclass (single source of truth)

---

## Inherited Configuration (Base Hypothesis h-e1)

```python
# From: h-e1/03_config.md (HE1Config spec — h-e1/code/ not materialized)
@dataclass
class HE1Config:
    model_name: str = "meta-llama/Llama-2-7b-chat-hf"
    torch_dtype: Literal["float16", "bfloat16"] = "float16"
    device_map: str = "auto"
    temperature: float = 0.7
    top_p: float = 0.9
    max_new_tokens: int = 128
    n_samples: int = 10
    do_sample: bool = True
    output_scores: bool = True
    dataset_name: str = "trivia_qa"
    dataset_config: str = "rc.nocontext"
    dataset_split: str = "validation"
    seed: int = 42
```

Inherited fields reused as-is: `model_name`, `torch_dtype`, `device_map`, `temperature`, `top_p`, `max_new_tokens`, `n_samples`, `do_sample`, `output_scores`, `dataset_name`, `dataset_config`, `dataset_split`, `seed`.

**Differs from h-e1**: `n_questions` — h-e1 used 50 (PoC subset); h-m1 uses full ~11,313 (MUST_WORK gate requires statistical power on full val set).

---

## Config Schema (Python Dataclass)

```python
import os
from dataclasses import dataclass, field
from typing import Literal

@dataclass
class HM1Config:
    # --- Model (inherited from h-e1) ---
    model_name: str = "meta-llama/Llama-2-7b-chat-hf"
    torch_dtype: Literal["float16", "bfloat16"] = "float16"
    device_map: str = "auto"
    hf_token: str = field(default_factory=lambda: os.environ.get("HF_TOKEN", ""))

    # --- Generation (inherited from h-e1) ---
    temperature: float = 0.7
    top_p: float = 0.9
    max_new_tokens: int = 128
    n_samples: int = 10        # num_responses per question
    do_sample: bool = True
    return_dict_in_generate: bool = True
    output_scores: bool = True  # required for entropy computation

    # --- Dataset ---
    dataset_name: str = "trivia_qa"
    dataset_config: str = "rc.nocontext"
    dataset_split: str = "validation"
    n_questions: int | None = None  # None = full ~11,313 (MUST_WORK requires full set)
    dataset_seed: int = 42

    # --- Correctness evaluation ---
    normalize_lowercase: bool = True
    normalize_strip: bool = True

    # --- Gate thresholds (MUST_WORK) ---
    p_value_target: float = 0.05     # t-test p < this to pass
    auroc_target: float = 0.55       # AUROC > this to pass
    require_direction: bool = True   # mean_incorrect_entropy > mean_correct_entropy

    # --- Output ---
    output_dir: str = "results/h-m1"
    results_path: str = "results/h-m1/h-m1_results.json"
    figures_dir: str = "figures/"
    checkpoint_path: str = "results/h-m1/checkpoint.json"
    checkpoint_every: int = 50   # larger interval than h-e1 (50 vs 10) — full-set run, less overhead
    log_file: str = "results/h-m1/run.log"

    # --- Hardware ---
    min_vram_gb: int = 16
    device: str = "cuda"

    # --- Reproducibility ---
    seed: int = 42
```

## Instantiation (copy-paste)

```python
CONFIG = HM1Config()
```

## Validation Rules

```python
def validate(cfg: HM1Config) -> None:
    assert cfg.hf_token, "HF_TOKEN env var must be set (gated model)"
    assert cfg.n_samples >= 2, "need >=2 samples per question for entropy averaging"
    assert cfg.output_scores, "output_scores required for entropy computation"
    assert 0 < cfg.temperature <= 2.0
    assert cfg.max_new_tokens > 0
    assert 0 < cfg.p_value_target < 1
    assert 0.5 < cfg.auroc_target < 1.0
```

## YAML Equivalent (optional, for CLI override)

```yaml
model_name: meta-llama/Llama-2-7b-chat-hf
torch_dtype: float16
temperature: 0.7
top_p: 0.9
max_new_tokens: 128
n_samples: 10
dataset_config: rc.nocontext
dataset_split: validation
n_questions: null   # full validation set
p_value_target: 0.05
auroc_target: 0.55
checkpoint_every: 50
seed: 42
```

---

## A-1: H-M1 Pipeline Config [Complexity: 1, Budget: 0]

**Applied**: Standard PyTorch/HF FP16 generation config, extended with scipy/sklearn gate-threshold fields.

### Configuration
Uses `HM1Config` above directly — single script/pipeline config, no per-module split (0 subtask budget).

### Subtasks [0/0 used]
None allocated — config consumed directly by `run_pipeline.py` per architecture spec.
