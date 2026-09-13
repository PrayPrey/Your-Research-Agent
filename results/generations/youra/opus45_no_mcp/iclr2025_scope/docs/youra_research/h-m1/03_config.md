# Configuration: H-M1

**Type:** MECHANISM
**Applied:** Hardcoded dict pattern (matches h-e1 config.py style)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** config classes verified from base code (h-e1/code/config.py)
**Config Files Found:** `h-e1/code/config.py` (LORA_CONFIG_TRANSFORMER, LORA_CONFIG_MAMBA, BENCHMARKS, MODEL_ID_BASELINE)
**Pattern Used:** dict (module-level constants, not dataclass)

---

## M-1: Setup & Data Loading [Complexity: 6, Budget: 6]

**Applied:** Config-as-dict pattern (h-e1 precedent), fixed defaults from PRD FR requirements (no tuning — single config, not a sweep)

### Configuration

```python
# code/config.py
LANDSCAPE_CONFIG = dict(
    sam_epsilon=0.05,
    hessian_top_k=50,
    num_bins=50,
    kl_eps=1e-10,
    batch_size=16,
    grad_accum=4,
    max_length=512,
    seed=42,
)

DATASETS = {
    "gsm8k": dict(hf_id="gsm8k", subset="main", split="test[:500]"),
    "nq": dict(hf_id="natural_questions", subset=None, split="validation[:500]"),
}

GATE_THRESHOLDS = dict(
    sharpness_delta_pct_min=0.10,
    kl_divergence_min=0.1,
)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-M1-1 | LANDSCAPE_CONFIG + DATASETS | Define dict constants in config.py |
| C-M1-2 | load_landscape_eval_set wrapper | Wrap h_e1.code.data loaders for GSM8K/NQ 500-sample subsets, batch_size=16 |

---

## Inherited Configuration (Base Hypothesis)

**Verified from**: `h-e1/code/config.py` (actual implementation)

```python
# From: h-e1/code/config.py (ACTUAL CODE — field names verified)
LORA_CONFIG_TRANSFORMER = dict(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.0,
)

LORA_CONFIG_MAMBA = dict(
    r=16,
    lora_alpha=32,
    target_modules=["in_proj", "out_proj"],
    lora_dropout=0.0,
)

MODEL_ID_BASELINE = "meta-llama/Llama-2-7b-hf"
```

**Reused as-is** via `from h_e1.code.config import LORA_CONFIG_TRANSFORMER, LORA_CONFIG_MAMBA` — no modification needed for model loading (M-2 task). `MODEL_ID_BASELINE` also imported directly for Llama-2-7B load.

**Not inherited** (h-e1 `TRAIN_CONFIG`, `BENCHMARKS` full-split entries, `GATE_THRESHOLDS`) — H-M1 uses its own `LANDSCAPE_CONFIG`/`DATASETS`/`GATE_THRESHOLDS` above since this is evaluation-only (no training) with different subset sizes and gate formula (sharpness/KL vs accuracy delta).
