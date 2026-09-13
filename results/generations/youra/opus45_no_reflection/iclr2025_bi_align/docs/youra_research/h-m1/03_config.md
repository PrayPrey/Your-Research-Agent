# Configuration: H-M1 (MECHANISM)

**Hypothesis:** L_agency integrates stably with DPO loss (training completes, loss decreases)
**Type:** MECHANISM - single training run, no ablations, no hyperparameter sweep

Applied: No relevant KB pattern found (searched "DPO training hyperparameters", "PyTorch config dataclass" — only unrelated diffusers/pytorch.org results); standard dataclass config used per architecture spec.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: Verified — H-E1 has no reusable config dataclass (uses flat `CONFIG` dict for a non-training PoC). Only reusable artifact is `collab_score.py`'s `compute_collab_score_v2()`, confirmed unbounded raw ratio (not [0,1]) — H-M1 must normalize/clip before use in loss.
**Config Files Found**: `docs/youra_research/h-e1/code/config.py` (dict pattern, not a dataclass — no field-name inheritance needed)
**Pattern Used**: dataclass (new — H-M1 is training, unlike H-E1's stats-only PoC)

---

## config.py

Single fixed training config, dataclass — MECHANISM test, single run, no sweep.

```python
from dataclasses import dataclass

@dataclass
class BiDPOConfig:
    # Experiment
    seed: int = 42

    # Model
    model_name: str = "mistralai/Mistral-7B-Instruct-v0.2"
    dtype: str = "bfloat16"
    device_map: str = "auto"

    # Data
    dataset_name: str = "Anthropic/hh-rlhf"
    max_length: int = 1024

    # BiDPO loss
    beta: float = 0.1              # DPO temperature (TRL default)
    lambda_agency: float = 0.5     # agency loss weight (mid of [0.25, 1.0] range)
    agency_clip_max: float = 5.0   # clip raw collab_score_v2 output before (1 - score)

    # Optimization
    learning_rate: float = 5e-7    # DPO standard (TRL default)
    batch_size: int = 4
    grad_accum_steps: int = 4      # effective batch = 16
    epochs: int = 1
    warmup_ratio: float = 0.1
    grad_clip_norm: float = 1.0
    lr_schedule: str = "cosine"

    # Logging / paths
    log_interval: int = 100
    output_dir: str = "outputs/"
    figures_dir: str = "outputs/figures/"
    results_path: str = "outputs/results.json"

CONFIG = BiDPOConfig()
```

### Subtasks [1/1 used — M-1]

| ID | Subtask | Description |
|----|---------|--------------|
| C-M-1-1 | Write config.py | Define `BiDPOConfig` dataclass above, instantiate `CONFIG` |
| C-M-1-2 | Copy collab_score.py | Copy verbatim from `h-e1/code/collab_score.py` into `h-m1/code/` |
| C-M-1-3 | Verify imports | Ensure `data.py`/`bidpo_loss.py` import `CONFIG` and `compute_collab_score_v2` correctly |
| C-M-1-4 | Smoke-check defaults | Assert `CONFIG.beta == 0.1`, `CONFIG.lambda_agency == 0.5` in `__main__` guard |

---

## PoC Gate Thresholds (used by run_experiment.py, not part of dataclass)

```python
GATE = {
    "max_nan_inf_allowed": 0,       # any NaN/Inf -> FAIL
    "require_loss_decrease": True,  # total_loss_final < total_loss_initial (post-warmup)
}
```

---

## Inherited Configuration (Base Hypothesis)

H-E1 used a flat `CONFIG` dict (EXISTENCE PoC, no training), not a dataclass — no field names to inherit. Only artifact reused is the function `compute_collab_score_v2(response: str) -> float` from `docs/youra_research/h-e1/code/collab_score.py`, copied verbatim (per architecture's External Dependencies section). No config values carried over; H-M1's `BiDPOConfig` is a new, independent schema.

---

## Self-Validation

- [x] ONE format only (dataclass)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Subtasks within M-1 budget (4/4)
- [x] Codebase Analysis (Serena) section included
- [x] Inherited Configuration section included (base_hypothesis scenario)
- [x] Total length < 400 lines
