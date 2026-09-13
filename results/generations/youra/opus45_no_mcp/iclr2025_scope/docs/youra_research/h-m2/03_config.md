# Config: H-M2

**Format:** Hardcoded dict (matches H-M1 codebase convention)
**Applied:** flat-dict-config-module pattern (Archon KB: DL config patterns hyperparameters)

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** config classes verified from base code
**Config Files Found:** `h-m1/code/config.py`
**Pattern Used:** dict (module-level constants, no dataclass wrapping)

---

## M2-1: Setup & Config [Complexity: 3, Budget: 3]

**Applied:** flat-dict-config pattern (consistent with H-M1 `config.py`)

### Configuration (`h-m2/code/config.py`)

```python
"""Configuration for H-M2: Task-Specific Sharpness Comparison"""

LORA_CONFIG = dict(
    r=16,
    lora_alpha=32,
    target_modules=["in_proj", "out_proj"],
    lora_dropout=0.0,
)

TRAIN_CONFIG = dict(
    lr=2e-4,
    epochs=3,
    batch_size=16,
    warmup_pct=0.06,
    max_length=512,
    seed=42,
)

SHARPNESS_CONFIG = dict(
    sam_epsilon=0.05,
    max_batches=100,
)

BENCHMARKS = {
    "gsm8k": dict(
        hf_id="openai/gsm8k",
        subset="main",
        split="test",
        num_samples=1319,
        density=0.1,
    ),
    "nq": dict(
        hf_id="google-research-datasets/natural_questions",
        subset=None,
        split="validation",
        num_samples=3610,
        density=0.9,
    ),
}

GATE_THRESHOLD = 0.8

MODEL_ID = "state-spaces/mamba-2.8b-hf"
```

**Non-standard:** `hf_id` values match H-M1's verified dataset IDs (`openai/gsm8k`, `google-research-datasets/natural_questions`), not the shorter placeholders in architecture doc, for cross-hypothesis consistency.

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M2-1-1 | Write config.py | All 5 dicts/constants above, single file |

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-m1/code/config.py (ACTUAL CODE, verified)
LORA_CONFIG_MAMBA = dict(
    r=16,
    lora_alpha=32,
    target_modules=["in_proj", "out_proj"],
    lora_dropout=0.0,
)

LANDSCAPE_CONFIG = dict(
    sam_epsilon=0.05,
    hessian_top_k=50,
    num_bins=50,
    kl_eps=1e-10,
    batch_size=16,
    grad_accum=4,
    max_length=512,
    seed=42,
    eval_samples=500,
)
```

H-M2's `LORA_CONFIG` and `SHARPNESS_CONFIG.sam_epsilon` mirror `LORA_CONFIG_MAMBA` and `LANDSCAPE_CONFIG.sam_epsilon` exactly — reuse via `h_m1.code.landscape.measure_sharpness_sam(epsilon=SHARPNESS_CONFIG["sam_epsilon"], ...)`, no re-implementation needed.

**Verified from:** `h-m1/code/config.py` (actual implementation)

---

## Remaining Budget

3 subtasks unused (4 allocated, 1 used for M2-1). No further config-only tasks — data/finetune/sharpness/gate modules consume `config.py` constants directly, no additional schema work required (Logic Agent's scope).
