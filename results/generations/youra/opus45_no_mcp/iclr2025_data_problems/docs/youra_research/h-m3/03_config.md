# Configuration: H-M3

**Type:** MECHANISM (inference-only) | **Format:** Python Dataclass (flat, matches H-M2 pattern)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-M2)
**Status:** Config class verified from actual code at `docs/youra_research/h-m2/code/config.py`
**Config Files Found:** `h-m2/code/config.py` (single flat `@dataclass Config`, no YAML)
**Pattern Used:** Flat dataclass (not nested Model/Data/Analysis classes) — H-M2 uses one `Config` class with all fields together. H-M3 follows same flat pattern for consistency.

**Critical field-name corrections from spec vs actual code:**
- Spec said "fp16" — actual H-M2 code uses `dtype: str = "bfloat16"`. H-M3 inherits `bfloat16`.
- Spec said "checkpoint paths" — actual H-M2 has no explicit checkpoint path field (checkpoints saved via training loop, not config). H-M3 adds explicit `checkpoint_verbatim` / `checkpoint_paraphrase` fields since it's the consumer.

---

## A-1: H-M3 Analysis Config [Complexity: 2, Budget: 2]

**Applied:** Standard PyTorch/HF inference defaults + H-M2 inherited fields

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass


@dataclass
class Config:
    # Inherited from H-M2 (verified from h-m2/code/config.py)
    model_id: str = "mistralai/Mistral-7B-v0.1"
    dtype: str = "bfloat16"
    device_map: str = "auto"
    k_paraphrases_bank: int = 5  # K=5 paraphrases per item
    seeds: tuple = (42, 123, 456)

    # H-M3 checkpoint paths (new — H-M2 config had no explicit path field)
    checkpoint_verbatim: str = "h-m2/checkpoints/checkpoint-verbatim"
    checkpoint_paraphrase: str = "h-m2/checkpoints/checkpoint-paraphrase"

    # Data
    dataset_id: str = "cais/mmlu"
    dataset_config: str = "all"
    dataset_split: str = "test"
    n_eval_items: int = 14042  # full MMLU test set (not H-M2's 1000-item subset)
    batch_size: int = 1  # per-item precision (brief: batch=1 for analysis)

    # Analysis thresholds
    mps_high_low_split: str = "median"  # split items into high/low MPS groups at median
    r_threshold: float = -0.4  # gate: Pearson r < -0.4
    effect_size_threshold: float = 0.3  # gate: Cohen's d > 0.3 between groups
    p_value_threshold: float = 0.05

    # Output
    results_path: str = "h-m3/results.json"
    figures_dir: str = "h-m3/figures/"
```

### Subtasks [1/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Config dataclass | Single flat `Config` as above, saved to `h-m3/code/config.py` |

---

## Inherited Configuration (Base Hypothesis: H-M2)

```python
# From: docs/youra_research/h-m2/code/config.py (ACTUAL CODE, verified)
@dataclass
class Config:
    model_id: str = "mistralai/Mistral-7B-v0.1"
    dtype: str = "bfloat16"
    device_map: str = "auto"
    lora_rank: int = 16
    lora_alpha: int = 32
    lora_target_modules: tuple = ("q_proj", "v_proj", "k_proj", "o_proj")
    k_paraphrases_bank: int = 5
    seeds: tuple = (42, 123, 456)
```

H-M3 does not subclass this — it is inference-only and reuses only `model_id`, `dtype`, `device_map`, `k_paraphrases_bank`, `seeds` by copying values into its own flat `Config` (see A-1), plus new checkpoint/analysis/output fields. No LoRA training fields (`lora_*`, `lr`, `epochs_*`) carried over since no training occurs.

**Verified from:** `docs/youra_research/h-m2/code/config.py`
