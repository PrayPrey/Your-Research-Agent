# Config: H-M3

**Format:** Hardcoded dict (matches H-M1/H-M2 codebase convention)
**Applied:** flat-dict-config-module pattern (Archon KB: DL config patterns hyperparameters)

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** config classes verified from base code (H-M2 `config.py`), extended per architecture doc
**Config Files Found:** `h-m2/code/config.py`, `h-m1/code/config.py`
**Pattern Used:** dict (module-level constants, no dataclass wrapping)

---

## M3-1: Setup & Config [Complexity: 3, Budget: 1]

**Applied:** flat-dict-config pattern (consistent with H-M1/H-M2 `config.py`)

### Configuration (`h-m3/code/config.py`)

```python
"""Configuration for H-M3: LoRA Adaptation Efficiency vs Landscape Geometry"""

LORA_CONFIG = dict(
    r=16,
    lora_alpha=32,
    target_modules=["in_proj"],
)

TRAIN_CONFIG = dict(
    lr=1e-4,
    epochs=5,
    batch_size=4,
    patience=2,
    weight_decay=0.01,
    grad_clip=1.0,
    seed=42,
)

SHARPNESS_CONFIG = dict(
    sam_epsilon=0.05,
    max_batches=50,
)

RANK_CONFIG = dict(
    thresholds=[0.85, 0.90, 0.95],
    default_threshold=0.90,
)

BENCHMARKS = {
    "gsm8k": dict(
        hf_id="gsm8k",
        subset="main",
        split="test",
        num_samples=1319,
    ),
    "nq": dict(
        hf_id="natural_questions",
        subset=None,
        split="validation",
        num_samples=3610,
    ),
}

SEEDS = [42, 123, 456]

GATE_THRESHOLD = 0.5  # Spearman rho
```

**Non-standard:** `LORA_CONFIG.target_modules=["in_proj"]` only (not `["in_proj","out_proj"]` like H-M2) — per PRD FR-2, scoped narrower for this hypothesis's rank-extraction focus. `TRAIN_CONFIG` lr/epochs/batch_size differ from H-M2 (1e-4 vs 2e-4, 5 vs 3 epochs, batch 4 vs 16) per PRD FR-3 convergence/VRAM constraints. `GATE_THRESHOLD=0.5` (Spearman rho) replaces H-M2's `0.8` (sharpness ratio) — different metric per PRD Section 6.

### Subtasks [1/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M3-1-1 | Write config.py | All 7 dicts/constants above, single file |

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-m2/code/config.py (ACTUAL CODE, verified)
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
    "gsm8k": dict(hf_id="openai/gsm8k", subset="main", split="test", num_samples=1319, density=0.1),
    "nq": dict(hf_id="google-research-datasets/natural_questions", subset=None, split="validation", num_samples=3610, density=0.9),
}
```

Reused directly (imported, not redefined) via `from h_m2.code.config import LORA_CONFIG, TRAIN_CONFIG, BENCHMARKS` where H-M3 modules call H-M2 functions (`finetune_on_task`, `load_task_loader`, `measure_task_sharpness`) — those functions expect H-M2's config shape internally. H-M3's own `config.py` (above) holds the **overriding** values (narrower `target_modules`, different `lr`/`epochs`/`batch_size`, `hf_id` without org prefix) passed explicitly into those reused functions per architecture doc's External Dependencies table.

**Verified from:** `h-m2/03_architecture.md` (External Dependencies), `h-m2/code/config.py`

---

## Remaining Budget

3 subtasks unused (4 allocated, 1 used for M3-1). No further config-only work — `rank.py`, `evaluate.py`, `correlate.py`, `visualize.py`, `run_experiment.py` consume `config.py` constants directly (Logic Agent's scope).
