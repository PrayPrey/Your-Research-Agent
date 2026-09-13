# Configuration Design: H-C1 — Sign-Flip Canonicalization Uniqueness Audit

**Hypothesis:** H-C1  
**Type:** CONDITION  
**Date:** 2026-08-27  
**Config Budget:** 1 subtask  

---

Applied: dataclass-config pattern (standard DL experiment config)  
Applied: fixed-seed-reproducibility pattern  
Applied: minimal-config-for-audit pattern (no hyperparameters to tune)  

---

## Configuration Philosophy

H-C1 is a pure algorithmic audit — no training, no learned hyperparameters. Configuration is minimal: sampling parameters, paths, and threshold constants. All values are fixed from the experiment spec.

---

## Configuration Schema (YAML)

```yaml
# config.yaml — H-C1 Experiment Configuration
experiment:
  hypothesis_id: "h-c1"
  description: "Sign-flip canonicalization uniqueness audit"
  seed: 1

dataset:
  hf_id: "MarcBrun/model-zoos"
  split: "train"
  n_sample: 500
  local_cache: "./data/"

model_zoo:
  architecture: "M2-MLP"
  hidden_dim: 64
  input_dim: 784
  output_dim: 10
  # W1: (hidden_dim, input_dim) = (64, 784)
  # W2: (output_dim, hidden_dim) = (10, 64)

canonicalization:
  method: "sign-flip"
  tie_breaking: "positive"   # default +1 for exact ties
  scope: "M2"               # M=2 MLPs only

audit:
  check_idempotency: true
  characterize_degenerate: true   # compute stats if degen > 0

thresholds:
  fraction_unique_pass: 0.99    # gate P1 pass threshold
  fraction_unique_scope: 0.95   # below this → SCOPE BOUNDARY
  fraction_idempotent_pass: 1.0 # must be exact

output:
  results_dir: "results/"
  figures_dir: "docs/youra_research/h-c1/figures/"
  results_file: "results/audit_results.json"
```

---

## Python Dataclass

```python
from dataclasses import dataclass, field

@dataclass
class ExperimentConfig:
    hypothesis_id: str = "h-c1"
    seed: int = 1

@dataclass
class DatasetConfig:
    hf_id: str = "MarcBrun/model-zoos"
    split: str = "train"
    n_sample: int = 500
    local_cache: str = "./data/"

@dataclass
class ModelZooConfig:
    architecture: str = "M2-MLP"
    hidden_dim: int = 64
    input_dim: int = 784
    output_dim: int = 10

@dataclass
class CanonicalizationConfig:
    method: str = "sign-flip"
    tie_breaking: str = "positive"  # "+1 default for ties"
    scope: str = "M2"

@dataclass
class AuditConfig:
    check_idempotency: bool = True
    characterize_degenerate: bool = True

@dataclass
class ThresholdConfig:
    fraction_unique_pass: float = 0.99
    fraction_unique_scope: float = 0.95
    fraction_idempotent_pass: float = 1.0

@dataclass
class OutputConfig:
    results_dir: str = "results/"
    figures_dir: str = "docs/youra_research/h-c1/figures/"
    results_file: str = "results/audit_results.json"

@dataclass
class HC1Config:
    experiment: ExperimentConfig = field(default_factory=ExperimentConfig)
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    model_zoo: ModelZooConfig = field(default_factory=ModelZooConfig)
    canonicalization: CanonicalizationConfig = field(default_factory=CanonicalizationConfig)
    audit: AuditConfig = field(default_factory=AuditConfig)
    thresholds: ThresholdConfig = field(default_factory=ThresholdConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
```

---

## Subtask C-6-1: Entry Point Config Integration

**Description:** Wire `HC1Config` dataclass into `run_experiment.py`. Load from `config.yaml` (if present) or use defaults. Pass config object through to all modules.

**Rationale:** Centralizes all magic numbers (n_sample=500, seed=1, threshold=0.99) in one place so Phase 4 coder does not scatter them across files.

**Implementation pattern:**
```python
# run_experiment.py
import yaml
from dataclasses import asdict
from config import HC1Config

def load_config(path="config.yaml") -> HC1Config:
    if Path(path).exists():
        with open(path) as f:
            d = yaml.safe_load(f)
        # Simple override from YAML (no deep merge needed for this experiment)
        ...
    return HC1Config()
```

---

## Inherited Configuration (from H-M3)

| Parameter | H-M3 value | H-C1 value | Change |
|-----------|------------|------------|--------|
| n_sample | 500 | 500 | Same |
| seed | 1 | 1 | Same (for reproducibility) |
| hf_id | `MarcBrun/model-zoos` | Same | No change |
| hidden_dim | 64 | 64 | Same |
| input_dim | 784 | 784 | Same |
| output_dim | 10 | 10 | Same |
| tie_breaking | +1 | +1 | Same |

**New in H-C1 (not in H-M3):**
- `fraction_unique_pass: 0.99` — gate threshold (H-C1 specific)
- `fraction_unique_scope: 0.95` — scope boundary threshold (H-C1 specific)
- `fraction_idempotent_pass: 1.0` — idempotency requirement (H-C1 specific)
- `characterize_degenerate: true` — degeneracy stats (H-C1 specific)

---

## Notes

- `ponytail: no hyperparameter sweep config needed — this is a fixed algorithmic audit`
- All thresholds (0.99, 0.95, 1.0) come directly from 02b_verification_plan.md — do not change without updating the gate spec
