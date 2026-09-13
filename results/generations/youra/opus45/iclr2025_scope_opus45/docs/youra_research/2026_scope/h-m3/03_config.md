# Configuration: H-M3 Eigenmode Energy Redistribution via Projection-Only LoRA

**Applied**: Standard PyTorch dataclass pattern (Archon KB match - using research defaults)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from actual base code
**Config Files Found**: `h-m2/code/config.py` (read directly)
**Pattern Used**: dataclass (inherited from H-M2)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: h-m2/code/config.py (ACTUAL CODE - verified)
@dataclass
class ExperimentConfig:
    # Model
    model_id: str = "state-spaces/mamba-1.4b-hf"
    tokenizer_id: str = "state-spaces/mamba-1.4b-hf"

    # Dataset
    dataset_name: str = "wikitext"
    dataset_config: str = "wikitext-103-raw-v1"
    num_eval_sequences: int = 100
    max_seq_length: int = 256
    seed: int = 42

    # H_spec (validated from H-E1 and H-M1)
    h_spec_known: float = 256.18

    # LoRA Parameters
    lora_r: int = 16
    lora_alpha: int = 32
    lora_target_modules: List[str] = field(default_factory=lambda: ["in_proj", "x_proj"])
    lora_dropout: float = 0.1
    lora_bias: str = "none"

    # Training Parameters
    learning_rate: float = 1e-4
    weight_decay: float = 1e-4
    num_epochs: int = 1
    batch_size: int = 2
    gradient_accumulation_steps: int = 8
    warmup_steps: int = 10
    lr_scheduler_type: str = "cosine"
    num_train_sequences: int = 200

    # Gate Thresholds (H-M2 specific)
    delta_h_spec_threshold: float = 10.0
    eigenvalue_corr_threshold: float = 0.95

    # Hardware
    device: str = "cuda"
    dtype: str = "float16"

    # Output
    figures_dir: str = "figures"
    results_path: str = "results.yaml"
    checkpoint_dir: str = "checkpoints"
```

**Verified from**: `h-m2/code/config.py` (actual implementation)

---

## New Configuration Fields

H-M3 extends `ExperimentConfig` with energy analysis fields.

---

## A-9: Visualization Config [Complexity: 2, Budget: 2 subtasks]

### Configuration

```python
from dataclasses import dataclass, field
from typing import List


@dataclass
class ExperimentConfig:
    """H-M3: Eigenmode Energy Redistribution - extends H-M2 config."""

    # --- Inherited from H-M2 (field names verified from actual code) ---
    model_id: str = "state-spaces/mamba-1.4b-hf"
    tokenizer_id: str = "state-spaces/mamba-1.4b-hf"

    dataset_name: str = "wikitext"
    dataset_config: str = "wikitext-103-raw-v1"
    num_train_sequences: int = 500      # Non-standard: increased from 200 (H-M2) for energy measurement stability
    num_eval_sequences: int = 100
    max_seq_length: int = 256
    seed: int = 42

    h_spec_known: float = 256.43        # Non-standard: updated from H-M2 result (was 256.18 in spec, 256.43 measured)

    lora_r: int = 16
    lora_alpha: int = 32
    lora_target_modules: List[str] = field(
        default_factory=lambda: ["in_proj", "x_proj"]
    )
    lora_dropout: float = 0.1
    lora_bias: str = "none"

    learning_rate: float = 1e-4
    weight_decay: float = 1e-4
    num_epochs: int = 1
    batch_size: int = 2
    gradient_accumulation_steps: int = 8
    warmup_steps: int = 10
    lr_scheduler_type: str = "cosine"

    device: str = "cuda"
    dtype: str = "float16"

    figures_dir: str = "figures"
    results_path: str = "results.yaml"
    checkpoint_dir: str = "checkpoints"

    # --- NEW: H-M3 Energy Analysis ---
    slow_mode_threshold: float = 0.99           # |λ| > 0.99 defines "slow" eigenmode
    delta_e_gate_threshold: float = 0.1         # ΔE must exceed 0.1 nats to pass gate
    num_energy_probe_sequences: int = 50        # Sequences used for pre/post energy measurement
    num_layers: int = 48                        # Mamba-1.4B layer count

    # --- Visualization settings ---
    fig_dpi: int = 150
    fig_format: str = "png"
    energy_hist_bins: int = 32
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-9-1 | EnergyDistributionPlot | Pre/post eigenmode energy histogram + slow mode threshold overlay |
| C-9-2 | PerLayerEnergyPlot | 48-layer bar chart of slow_fraction pre vs post; gate metric bar chart with PASS/FAIL annotation |

---

## A-12: Validation Config [Complexity: 1, Budget: 1 subtask]

### Configuration

YAML schema for `results.yaml`:

```yaml
# results.yaml schema (written by experiment, read by validator)
gate_pass: false                    # bool: delta_e_nats > delta_e_gate_threshold
delta_e_nats: 0.0                   # float: KL-approx energy shift in nats

pre_energy:
  slow_fraction: 0.0                # float: fraction of energy in slow modes before training
  total_energy: 0.0                 # float: sum of all mode energies
  per_layer: []                     # list[float]: slow_fraction per layer (48 values)

post_energy:
  slow_fraction: 0.0
  total_energy: 0.0
  per_layer: []

perplexity:
  pre: 0.0                          # float: validation perplexity before LoRA
  post: 0.0                         # float: validation perplexity after LoRA

per_layer_metrics:
  - layer_idx: 0
    pre_slow_fraction: 0.0
    post_slow_fraction: 0.0
    delta_slow_fraction: 0.0

metadata:
  model_id: "state-spaces/mamba-1.4b-hf"
  seed: 42
  num_train_sequences: 500
  slow_mode_threshold: 0.99
  delta_e_gate_threshold: 0.1
```

### Validation dataclass

```python
@dataclass
class ValidationThresholds:
    """Gate thresholds for H-M3 validator."""
    delta_e_gate_threshold: float = 0.1     # nats; gate PASS if delta_e_nats > this
    slow_mode_threshold: float = 0.99       # |λ| cutoff for slow mode classification
    max_perplexity_degradation: float = 5.0 # sanity: post_ppl - pre_ppl must be < 5
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-12-1 | ResultsSchemaAndValidator | Write results.yaml with schema above; validator reads gate_pass and delta_e_nats |
