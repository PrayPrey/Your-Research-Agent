# H-M4 Configuration: Task-Dependent Transformation Emergence

## Codebase Analysis (Serena)

**Project Type**: existing_codebase (sibling hypotheses h-m1/h-m2/h-m3 present)
**Status**: existing patterns found
**Config Files Found**: `docs/youra_research/h-m3/code/config.py`, `docs/youra_research/h-m1/code/config.py`
**Pattern Used**: hardcoded dict (not dataclass) — H-M4 follows this convention for consistency

**Applied**: Standard PyTorch/HF defaults + h-m3 config pattern (dict-based, per-benchmark density field)

---

## A-1: Cross-Architecture Config [Complexity: 2, Budget: 2]

Single fixed config, one correlation test across 2 architectures x 4 datasets. No hyperparameter grid (this is a correlational analysis, not a tuning study).

### Configuration (Hardcoded Dict)

```python
"""Configuration for H-M4: Task-Dependent Transformation Emergence"""
import os

MODEL_CONFIG = dict(
    d_model=512,
    n_layers=4,
    n_heads=8,          # Transformer only
    d_state=16,          # Mamba only
)

LORA_CONFIG = dict(
    r=16,
    lora_alpha=32,
    lora_dropout=0.0,
    target_modules=["in_proj"],  # Mamba SSM proj; Transformer uses q_proj/v_proj
)

TRAIN_CONFIG = dict(
    optimizer="AdamW",
    lr=1e-4,
    batch_size=4,
    max_epochs=5,
    weight_decay=0.01,
    gradient_clip=1.0,
    seed=42,
)

BENCHMARKS = {
    "gsm8k": dict(split="test", retrieval_density=0.1),
    "mmlu": dict(split="test", retrieval_density=0.5),
    "hotpotqa": dict(split="validation", retrieval_density=0.7),
    "nq": dict(split="validation", retrieval_density=0.9),
}

ARCHITECTURES = ["transformer", "mamba"]

GATE_THRESHOLD = dict(
    min_spearman_rho=0.7,
    max_p_value=0.01,
)

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
H_M4_DIR = os.path.dirname(CODE_DIR)
CHECKPOINTS_DIR = os.path.join(H_M4_DIR, "checkpoints")
FIGURES_DIR = os.path.join(H_M4_DIR, "figures")
```

**Non-standard**: `retrieval_density` values are fixed per-dataset labels (not measured at runtime) — sourced from PRD task allocation.

### Subtasks [1/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | config.py | Write single config module above, importable by train/evaluate scripts |

---

## Environment Variables

None required — all paths resolved relative to `CODE_DIR`; no secrets/API keys needed (local models, local datasets assumed pre-downloaded as in h-m3).

## Hyperparameter Rationale

- `lr=1e-4`, `batch_size=4`, `max_epochs=5`, `weight_decay=0.01`, `gradient_clip=1.0`: unchanged from h-m3, proven stable for LoRA fine-tuning at this scale — reuse avoids re-tuning for a PoC-scale correlational study.
- `lora_rank=16`, `lora_alpha=32`: standard LoRA defaults (alpha = 2x rank), consistent with h-m3.
- `retrieval_density` values (0.1/0.5/0.7/0.9): fixed dataset-level labels spanning low-to-high retrieval reliance, needed to compute the Spearman correlation — not tunable.
- `min_spearman_rho=0.7`, `max_p_value=0.01`: directly from hypothesis gate criteria, not derived.
- Single seed (42): correlation test over 4 datasets x 2 architectures = 8 points; PoC does not require multi-seed variance estimation.
