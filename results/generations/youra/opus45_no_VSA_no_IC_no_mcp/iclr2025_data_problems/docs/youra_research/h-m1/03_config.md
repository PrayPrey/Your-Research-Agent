# Configuration: H-M1 Noise-Dilution Mechanism

**Applied**: CCNet/RedPajama perplexity-filter config pattern (reused from H-E1); dataclass sweep-config pattern

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from base code (`h-e1/code/config/config.py`, read directly — Serena MCP unavailable, used Read tool as fallback)
**Config Files Found**: `docs/youra_research/h-e1/code/config/config.py`
**Pattern Used**: dict (MODEL/TRAIN/DATA/EVAL_CONFIG) + dataclass (`CurationConfig`)

---

## Inherited Configuration (Base Hypothesis)

Reused **as-is** from H-E1 (`from config.config import MODEL_CONFIG, TRAIN_CONFIG, DATA_CONFIG, EVAL_CONFIG`), no changes:

```python
# From: h-e1/code/config/config.py (ACTUAL CODE — verified field names)
MODEL_CONFIG = {
    "vocab_size": 50257,
    "n_positions": 1024,
    "n_embd": 768,
    "n_layer": 12,
    "n_head": 12,
}

TRAIN_CONFIG = {
    "total_tokens": 10_000_000_000,
    "batch_size": 512,
    "seq_len": 1024,
    "max_steps": 19073,
    "optimizer": "adamw",
    "adam_beta1": 0.9,
    "adam_beta2": 0.95,
    "weight_decay": 0.1,
    "grad_clip": 1.0,
    "lr_peak": 6e-4,
    "lr_min": 6e-5,
    "lr_schedule": "cosine",
    "warmup_steps": 2000,
    "precision": "bf16",
    "seed": 42,
}

DATA_CONFIG = {
    "dataset": "togethercomputer/RedPajama-Data-v2",
    "subset": "default",
    "split": "train",
    "streaming": True,
    "quality_field": "ccnet_perplexity",
    "val_holdout_fraction": 0.001,
}

EVAL_CONFIG = {
    "library": "lm-evaluation-harness",
    "tasks": ["hellaswag", "arc_easy", "piqa", "winogrande"],
    "metrics": {
        "hellaswag": "acc_norm",
        "arc_easy": "acc",
        "piqa": "acc",
        "winogrande": "acc",
    },
    "batch_size": 32,
    "ensemble_method": "pc1",
}
```

`CurationConfig` dataclass shape (fields `config_id`, `perplexity_pct`, `dedup`) is also inherited — H-M1 fixes `dedup="none"` for every entry (no dedup dimension in this experiment).

**Verified from**: `docs/youra_research/h-e1/code/config/config.py` (actual implementation).

---

## A-1: Config Definitions [Complexity: 3, Budget: 0]

**Applied**: Dataclass sweep-config pattern (reused from H-E1 `SWEEP_CONFIGS`)

### Configuration (Python Dataclass + dict)

```python
from dataclasses import dataclass
from typing import Optional
from h_e1.code.config.config import MODEL_CONFIG, TRAIN_CONFIG, DATA_CONFIG, EVAL_CONFIG

@dataclass
class CurationConfig:
    config_id: str
    perplexity_pct: Optional[int]
    dedup: str = "none"          # fixed — no dedup sweep in H-M1

M1_CONFIGS: list[CurationConfig] = [
    CurationConfig("M1-C0", None),
    CurationConfig("M1-C1", 20),
    CurationConfig("M1-C2", 40),
    CurationConfig("M1-C3", 50),
    CurationConfig("M1-C4", 60),
    CurationConfig("M1-C5", 80),
    CurationConfig("M1-C6", 90),
]

LOSS_THRESHOLD: float = 3.5
CHECKPOINT_TOKENS: list[int] = [1_000_000_000, 5_000_000_000, 10_000_000_000]
LOG_INTERVAL: int = 100          # steps, per FR-2.5 / NFR-4
```

No subtasks — budget is 0, single flat config module (mirrors H-E1 `config.py` structure exactly).

---

## Convergence Analysis Constants (used by `convergence.py`, A-5)

```python
BOOTSTRAP_N: int = 10_000        # bootstrap resamples for p-value/Cohen's d
BOOTSTRAP_PAIR: tuple[str, str] = ("M1-C3", "M1-C0")  # p50 vs p0, per Success Criteria #4
```

---

## Self-Validation

- [x] ONE format: dict (inherited MODEL/TRAIN/DATA/EVAL_CONFIG) + dataclass (`CurationConfig`) — same shape as H-E1, no new format introduced
- [x] Field names verified from actual H-E1 code (not spec)
- [x] `dedup` fixed to `"none"` per architecture note
- [x] 0 subtasks (within budget)
- [x] Codebase Analysis (Serena) section included
