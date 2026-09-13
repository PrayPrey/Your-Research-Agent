---
name: "Configuration: h-e1 Three-Tier Contamination Detection System"
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
date: 2026-05-11
phase: Phase 3 - Configuration
source: 03_architecture.md, 03_prd.md
budget_used: 3/3 subtasks
---

# Configuration Schema: h-e1

**Applied**: Standard PyTorch training config pattern (dataclass-based)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: New config design - no existing codebase
**Config Files Found**: None
**Pattern Used**: Python dataclass (single format)

---

## E-2: Base Model & Training Infrastructure [Complexity: 11, Budget: 2]

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class TrainingConfig:
    # Model
    model_name: str = "meta-llama/Llama-2-7b-hf"
    max_seq_length: int = 512
    
    # Training
    learning_rate: float = 2e-5
    weight_decay: float = 0.01
    epochs: int = 3
    batch_size: int = 64
    per_device_batch_size: int = 4
    gradient_accumulation_steps: int = 16
    warmup_ratio: float = 0.1
    fp16: bool = True
    
    # Experiment control
    contamination_rates: List[float] = field(default_factory=lambda: [0.0, 0.01, 0.05])
    n_runs: int = 20
    seed_start: int = 0
    
    # Paths
    checkpoint_dir: str = "./checkpoints"
    log_dir: str = "./logs"
    results_dir: str = "./results"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Training loop | AdamW optimizer, gradient accumulation, FP16 precision |
| C-2-2 | Checkpoint management | Per-epoch saves, seed control, training logs |

---

## E-7: Evaluation & Visualization [Complexity: 12, Budget: 1]

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class Tier1Config:
    benchmark_release_date: str = "2021-11-01"
    lsh_bands: int = 20
    lsh_rows: int = 5
    minhash_permutations: int = 128

@dataclass
class Tier2Config:
    n_invariant_probes: int = 1000
    n_neighbor_probes: int = 1000
    n_broken_probes: int = 1000
    # Non-standard: 2σ threshold from clean baseline calibration
    detection_threshold_sigma: float = 2.0

@dataclass
class Tier3Config:
    gradient_overlap_threshold: float = 0.10
    hessian_concentration_threshold: float = 1.5
    cka_alignment_threshold: float = 0.15
    efficiency_zscore_threshold: float = 2.5
    # Non-standard: ≥2 of 4 metrics must exceed thresholds
    min_metrics_required: int = 2
    hessian_top_k: int = 10

@dataclass
class EvaluationConfig:
    tier1: Tier1Config = field(default_factory=Tier1Config)
    tier2: Tier2Config = field(default_factory=Tier2Config)
    tier3: Tier3Config = field(default_factory=Tier3Config)
    
    # Detection logic
    detection_mode: str = "OR"  # Tier1 OR Tier2 OR Tier3
    
    # Success criteria
    target_detection_power: float = 0.80
    max_false_positive_rate: float = 0.05
    min_tiers_active: int = 2
    
    # Visualization
    figures_dir: str = "./figures"
    generate_mandatory_gate_figure: bool = True
    generate_heatmap: bool = True
    generate_roc_curve: bool = True
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Metrics & visualization | Detection power, FPR, per-tier rates, gate figure generation |

---

## Complete Configuration (src/config.py)

```python
from dataclasses import dataclass, field, asdict
from typing import List
import json

@dataclass
class Tier1Config:
    benchmark_release_date: str = "2021-11-01"
    lsh_bands: int = 20
    lsh_rows: int = 5
    minhash_permutations: int = 128

@dataclass
class Tier2Config:
    n_invariant_probes: int = 1000
    n_neighbor_probes: int = 1000
    n_broken_probes: int = 1000
    detection_threshold_sigma: float = 2.0

@dataclass
class Tier3Config:
    gradient_overlap_threshold: float = 0.10
    hessian_concentration_threshold: float = 1.5
    cka_alignment_threshold: float = 0.15
    efficiency_zscore_threshold: float = 2.5
    min_metrics_required: int = 2
    hessian_top_k: int = 10

@dataclass
class TrainingConfig:
    model_name: str = "meta-llama/Llama-2-7b-hf"
    max_seq_length: int = 512
    learning_rate: float = 2e-5
    weight_decay: float = 0.01
    epochs: int = 3
    batch_size: int = 64
    per_device_batch_size: int = 4
    gradient_accumulation_steps: int = 16
    warmup_ratio: float = 0.1
    fp16: bool = True
    contamination_rates: List[float] = field(default_factory=lambda: [0.0, 0.01, 0.05])
    n_runs: int = 20
    seed_start: int = 0
    checkpoint_dir: str = "./checkpoints"
    log_dir: str = "./logs"
    results_dir: str = "./results"

@dataclass
class EvaluationConfig:
    tier1: Tier1Config = field(default_factory=Tier1Config)
    tier2: Tier2Config = field(default_factory=Tier2Config)
    tier3: Tier3Config = field(default_factory=Tier3Config)
    detection_mode: str = "OR"
    target_detection_power: float = 0.80
    max_false_positive_rate: float = 0.05
    min_tiers_active: int = 2
    figures_dir: str = "./figures"
    generate_mandatory_gate_figure: bool = True
    generate_heatmap: bool = True
    generate_roc_curve: bool = True

@dataclass
class ExperimentConfig:
    training: TrainingConfig = field(default_factory=TrainingConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    
    def to_dict(self):
        return asdict(self)
    
    def save_json(self, path: str):
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
```

---

## Usage Example

```python
from src.config import ExperimentConfig

# Load default config
config = ExperimentConfig()

# Override specific values
config.training.epochs = 5
config.evaluation.tier3.min_metrics_required = 3

# Save config
config.save_json("experiment_config.json")

# Access nested configs
lr = config.training.learning_rate
threshold = config.evaluation.tier3.gradient_overlap_threshold
```

---

## Budget Summary

| Task | Complexity | Subtasks Allocated | Subtasks Used |
|------|------------|-------------------|---------------|
| E-2 Training | 11 | 2 | 2 |
| E-7 Evaluation | 12 | 1 | 1 |
| **Total** | **23** | **3** | **3/3** |

---

*Generated by Phase 3 Configuration | Hypothesis: h-e1 (EXISTENCE) | Budget: 3/3 subtasks used*
