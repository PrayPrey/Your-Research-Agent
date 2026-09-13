# Config: H-M2 - Projection-Only LoRA Eigenvalue Preservation

**Applied**: PEFT LoRA dataclass config pattern (Archon KB: HuggingFace PEFT docs)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from H-M1 actual code
**Config Files Found**: `h-m1/code/config.py` (read directly)
**Pattern Used**: dataclass (extending H-M1 ExperimentConfig)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: h-m1/code/config.py (VERIFIED from actual implementation)
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
    context_length_multipliers: Tuple[float, ...] = (0.1, 0.25, 0.5, 1.0, 2.0, 4.0)

    # Gate (MUST_WORK)
    degradation_ratio_threshold: float = 1.1
    baseline_ppl_expected: float = 16.3
    baseline_ppl_tolerance: float = 0.2

    # Hardware
    device: str = "cuda"
    dtype: str = "float32"

    # Output
    figures_dir: str = "figures"
    results_path: str = "results.yaml"
```

**Verified from**: `h-m1/code/config.py` (actual implementation)

---

## A-1: ExperimentConfig [Complexity: 2, Budget: 1]

**Applied**: PEFT LoRA dataclass pattern

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class ExperimentConfig:
    """Configuration for H-M2: Projection-only LoRA eigenvalue preservation."""

    # --- Inherited from H-M1 (field names verified from actual code) ---
    model_id: str = "state-spaces/mamba-1.4b-hf"
    tokenizer_id: str = "state-spaces/mamba-1.4b-hf"
    dataset_name: str = "wikitext"
    dataset_config: str = "wikitext-103-raw-v1"
    num_eval_sequences: int = 1000
    max_seq_length: int = 1024
    seed: int = 42
    h_spec_known: float = 256.18  # From H-M1 validated result
    device: str = "cuda"
    dtype: str = "float16"        # Non-standard: float16 for 1.4B model memory efficiency
    figures_dir: str = "figures"
    results_path: str = "results.yaml"

    # --- LoRA Parameters ---
    lora_r: int = 16
    lora_alpha: int = 32
    lora_target_modules: List[str] = field(
        default_factory=lambda: ["in_proj", "out_proj"]  # Projections only, NOT A_log
    )
    lora_dropout: float = 0.1
    lora_bias: str = "none"

    # --- Training Parameters ---
    learning_rate: float = 1e-4
    weight_decay: float = 1e-4
    epochs: int = 3
    batch_size: int = 8
    gradient_accumulation_steps: int = 4   # Non-standard: effective batch = 32
    warmup_steps: int = 100
    lr_scheduler_type: str = "cosine"

    # --- Gate Thresholds (MUST_WORK) ---
    delta_h_spec_threshold: float = 10.0   # |ΔH_spec| must be < 10%
    eigenvalue_corr_threshold: float = 0.95

    # --- Eval ---
    num_train_sequences: int = 5000        # Non-standard: small subset for PoC speed
```

### results.yaml Schema

```yaml
hypothesis: H-M2
status: PASS | FAIL
gate: MUST_WORK

metrics:
  h_spec_pre: 256.18          # float - H_spec before LoRA fine-tuning
  h_spec_post: ~              # float - H_spec after LoRA fine-tuning
  delta_h_spec_percent: ~     # float - |ΔH_spec| percentage
  eigenvalue_correlation: ~   # float - Pearson correlation pre/post eigenvalues
  a_log_frozen: ~             # bool - True if A_log unchanged
  val_perplexity_pre: ~       # float - WikiText-103 PPL before fine-tuning
  val_perplexity_post: ~      # float - WikiText-103 PPL after fine-tuning

gate_result:
  delta_h_spec_pass: ~        # bool - delta_h_spec_percent < 10.0
  eigenvalue_corr_pass: ~     # bool - eigenvalue_correlation > 0.95
  overall_pass: ~             # bool - all gate conditions met

lora_config:
  r: 16
  alpha: 32
  target_modules: ["in_proj", "out_proj"]
  dropout: 0.1

figures:
  - figures/gate_metrics.png
  - figures/eigenvalue_distribution.png
  - figures/per_layer_h_spec_change.png
  - figures/a_log_diff_heatmap.png
  - figures/eigenvalue_scatter.png
  - figures/training_loss.png
```

### Visualization Configuration

```python
VIZ_CONFIG = {
    "figure_size": (10, 6),
    "dpi": 150,
    "style": "seaborn-v0_8-whitegrid",
    "gate_bar_colors": {"actual": "steelblue", "threshold": "red"},
    "save_format": "png",
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | ExperimentConfig | Dataclass with LoRA params, training params, gate thresholds, results schema |
