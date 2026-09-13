# Configuration: H-M1 — SSM Eigenvalue Memory Horizon Empirical Validation

Applied: Standard inference-only PoC config pattern (Archon KB unavailable, using research defaults)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending H-E1)
**Status**: Config classes verified from base code
**Config Files Found**: `docs/youra_research/20260327_scope/h-e1/code/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: docs/youra_research/20260327_scope/h-e1/code/config.py (ACTUAL CODE)
@dataclass
class ExperimentConfig:
    # Model
    model_id: str = "state-spaces/mamba-1.4b"
    model_370m_id: str = "state-spaces/mamba-370m"
    tokenizer_id: str = "EleutherAI/gpt-neox-20b"

    # Measurement
    num_samples: int = 1000
    seq_length: int = 512
    seed: int = 42

    # Gate condition
    cv_threshold: float = 0.3

    # Compute
    device: str = "cuda"
    dtype: str = "float32"

    # Output
    figures_dir: str = "figures"
    results_path: str = "results.yaml"
```

**Verified from**: `docs/youra_research/20260327_scope/h-e1/code/config.py` (actual implementation)

**Key differences vs H-E1**: H-E1 uses `tokenizer_id = "EleutherAI/gpt-neox-20b"` (not the mamba-hf tokenizer). H-M1 uses `"state-spaces/mamba-1.4b-hf"` per PRD FR-2. H-E1 uses `num_samples`/`seq_length`; H-M1 uses `num_eval_sequences`/`max_seq_length` to match architecture spec.

---

## A-1: Setup Project Structure [Complexity: 5, Budget: 4 subtasks]

Applied: Standard inference-only PoC config pattern

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List


@dataclass
class ExperimentConfig:
    # Model
    model_id: str = "state-spaces/mamba-1.4b"
    tokenizer_id: str = "state-spaces/mamba-1.4b-hf"

    # Dataset
    dataset_name: str = "wikitext"
    dataset_config: str = "wikitext-103-raw-v1"
    num_eval_sequences: int = 1000
    max_seq_length: int = 1024
    seed: int = 42

    # H_spec (validated from H-E1)
    h_spec_known: float = 256.18
    context_length_multipliers: tuple = (0.1, 0.25, 0.5, 1.0, 2.0, 4.0)

    # Gate
    degradation_ratio_threshold: float = 1.1
    baseline_ppl_expected: float = 16.3
    # Non-standard: ±20% tolerance per PRD FR-6 (wider than typical 5-10%)
    baseline_ppl_tolerance: float = 0.2

    # Hardware
    device: str = "cuda"
    dtype: str = "float32"

    # Output
    figures_dir: str = "figures"
    results_path: str = "results.yaml"
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Create file skeleton | Create `code/` directory with empty `config.py`, `model.py`, `evaluate.py`, `run_experiment.py`, `figures/` |
| C-1-2 | Implement ExperimentConfig | Write dataclass above into `config.py` |
| C-1-3 | Verify imports | Confirm all dependency imports resolve (torch, mamba_ssm, datasets, transformers) |
| C-1-4 | Smoke test config | Instantiate ExperimentConfig(), verify defaults print correctly |

---

## A-7: Visualization [Complexity: 9, Budget: 1 subtask]

Applied: Standard matplotlib figure config pattern

### Configuration (Python Dataclass)

```python
# Visualization settings — hardcoded dict (no separate class needed)
VIZ_CONFIG = {
    # Figure sizing
    "fig_width": 10,
    "fig_height": 6,
    "dpi": 150,

    # PPL vs context length curve
    "h_spec_line_color": "red",
    "h_spec_line_style": "--",
    "ppl_curve_color": "steelblue",
    "ppl_curve_marker": "o",

    # Gate metrics bar chart
    "bar_threshold_color": "orange",
    "bar_ratio_color": "steelblue",

    # Output format
    "save_format": "png",
    "figure_names": {
        "ppl_curve": "ppl_vs_context_length.png",
        "gate_metrics": "gate_metrics_bar.png",
        "per_layer_eigenvalues": "per_layer_eigenvalues.png",   # optional
        "decay_rate_profile": "decay_rate_profile.png",         # optional
    },
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Implement generate_figures | Write `generate_figures()` in `evaluate.py`: (1) PPL vs context curve with vertical H_spec line, (2) gate metrics bar chart showing ratio vs threshold 1.1; optionally (3) per-layer eigenvalue distribution, (4) decay rate profile |
