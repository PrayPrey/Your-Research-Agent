# Config: H-M1 (Contamination Injection Mechanism)

Applied: LoRA fine-tuning config extension pattern (PEFT dataclass, reused from H-E1)
Applied: Multi-seed reproducibility config pattern (DL config patterns hyperparameters)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from base code (direct file read, `h-e1/code/config.py`)
**Config Files Found**: `h-e1/code/config.py` (actual `Config` dataclass)
**Pattern Used**: dataclass (single flat `Config`, matches H-E1 convention)

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-e1/code/config.py (ACTUAL CODE)
@dataclass
class Config:
    model_id: str = "mistralai/Mistral-7B-v0.1"
    dtype: str = "bfloat16"
    device_map: str = "auto"

    lora_rank: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: tuple = ("q_proj", "v_proj")

    lr: float = 2e-4
    batch_size: int = 4
    grad_accum: int = 8
    epochs: int = 3

    seed: int = 42
```

**Verified from**: `h-e1/code/config.py`. Note: H-E1's `lr` default is `2e-4`, but PRD FR-2.4 and architecture both specify `lr=2e-5` for H-M1 (matches H-E1's *actual validated run*, per 02c brief). Use `2e-5` below.

---

## M-8: Experiment Orchestration [Complexity: 10, Budget: 2 subtasks]

**Applied**: Multi-seed reproducibility config pattern

### Configuration (Python Dataclass)

```python
@dataclass
class Config:
    model_id: str = "mistralai/Mistral-7B-v0.1"
    dtype: str = "bfloat16"
    device_map: str = "auto"

    lora_rank: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: tuple = ("q_proj", "v_proj", "k_proj", "o_proj")

    lr: float = 2e-5  # H-E1 validated run value (overrides base default 2e-4)
    batch_size: int = 4
    grad_accum: int = 8
    epochs: int = 3

    contamination_levels: tuple = (0.0, 0.05, 0.10, 0.20, 0.50)
    seeds: tuple = (42, 123, 456)
    n_test_items: int = 14042

    effect_size_target: float = 0.05  # FR-5 primary gate threshold
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-M8-1 | Config + seed/level loop scaffold | Define `Config` dataclass; wire nested loop over `seeds` x `contamination_levels` in `run_experiment` |
| C-M8-2 | Results persistence + logging | Serialize per-run results to `results/mechanism_results.json`; structured run logging |

---

## M-6: Mechanism Verification [Complexity: 9, Budget: 2 subtasks]

**Applied**: Threshold-based mechanism verification pattern (contamination studies, Sainz et al. 2023)

### Configuration (Python Dataclass)

```python
@dataclass
class MechanismThresholds:
    effect_size_target: float = 0.05   # FR-5.1 gate: cont_acc - clean_acc > 0.05
    monotonic_check: bool = True       # FR-5.2: effect_size strictly increasing across levels
    log_prefix: str = "[MECHANISM CHECK]"  # FR-5.3
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-M6-1 | mechanism_active + effect_size check | Per level/seed: `cont_acc > clean_acc`, log via `log_prefix`, compare to `effect_size_target` |
| C-M6-2 | Monotonic trend + cross-seed aggregation | Verify effect_size(5%)<...<effect_size(50%); mean/std across `seeds` |

---

## Non-Budgeted Modules (Reference Only — No Subtasks Allocated)

M-1 through M-5, M-7 reuse the `Config` fields above but are out of this task's budget. Use the single `Config` dataclass everywhere; no additional config classes needed.
