# Config: H-E1 (SSI Contamination Detection — EXISTENCE PoC)

Applied: Single fixed dataclass config (EXISTENCE PoC — no grid, no ablations)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None
**Pattern Used**: dataclass

---

## Config (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class Config:
    # Model
    model_id: str = "mistralai/Mistral-7B-v0.1"
    dtype: str = "bfloat16"      # NFR-1: BF16 inference
    device_map: str = "auto"

    # LoRA
    lora_rank: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: tuple = ("q_proj", "v_proj")

    # Training (contamination injection fine-tune)
    lr: float = 2e-4
    batch_size: int = 4
    grad_accum: int = 8
    epochs: int = 3

    # Data / contamination
    contamination_levels: tuple = (0.0, 0.10, 0.50)  # clean, low, high
    k_paraphrases: int = 20
    n_eval_items: int = 200      # PoC subset, not full 14,042 (NFR-4: <48h)

    # Reproducibility
    seed: int = 42

    # Gate targets (evaluation, not tuned)
    auc_target: float = 0.7
    cohens_d_target: float = 0.5
```

No hyperparameter grid — PoC uses one fixed config to test existence, per FR-5 (ablations deferred post-gate).

---

## E-1: Data Pipeline [Complexity: 10]

**Applied**: HuggingFace `datasets` load pattern; rule-based paraphrase (single method per architecture, no T5/GPT-4 split)

### Configuration
Uses `Config.contamination_levels`, `Config.k_paraphrases`, `Config.seed`. No task-specific config class needed — reuses global `Config`.

### Subtasks [2/5 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | MMLU loaders | `load_mmlu()`, `sample_contamination_subset()` — HF dataset + level-based sampling |
| C-1-2 | Paraphrase + prompt | `generate_paraphrases()` (rule-based synonym swap, k=20), `format_mmlu_prompt()` |

---

## E-3: SSI Computation [Complexity: 9]

**Applied**: Confidence-variance behavioral probe (novel — SSI = 1/(var+eps))

### Configuration
```python
SSI_EPSILON: float = 1e-8   # variance floor to avoid div-by-zero
```
Uses `Config.k_paraphrases`. No separate dataclass required.

### Subtasks [2/5 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-3-1 | Confidence extraction | `extract_confidence()` — softmax over answer-token logits (A/B/C/D) |
| C-3-2 | SSI batch scoring | `compute_ssi()`, `compute_ssi_batch()` — variance across paraphrase confidences |

---

## E-5: Evaluation + Visualization [Complexity: 9]

**Applied**: Standard sklearn AUC/ROC pattern; scipy Cohen's d

### Configuration
Uses `Config.auc_target` (0.7), `Config.cohens_d_target` (0.5). No separate dataclass — plot functions take raw score lists directly.

### Subtasks [1/5 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-5-1 | Metrics + plots | `evaluate_ssi_discrimination()` (AUC, Cohen's d) + 5 required plots (gate, distribution, ROC, contamination-level, variance histogram) |

---

## Subtask Budget Summary

| Task | Subtasks Used |
|------|----------------|
| E-1 | 2 |
| E-3 | 2 |
| E-5 | 1 |
| **Total** | **5 / 5** |

E-2, E-4 not in this config pass — E-2 fully covered by LoRA/training fields above; E-4 is orchestration-only, no new config needed.
