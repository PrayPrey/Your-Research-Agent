# Config: H-M3 (MECHANISM)

**Applied**: no directly relevant Archon KB pattern found (KB returned unrelated diffusion/torch-inductor/JAX docs for "DL config patterns"); using standard single-source dataclass config pattern per architecture's `config.py`.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1, H-E1 reused; verified in `03_architecture.md`)
**Status**: Config values already sourced from architecture's `config.py` spec, which itself verified H-M1 pipeline signatures via Serena. No additional field-name risk for this file — H-M3 config.py is new (green-field), not inherited from a base config class.
**Config Files Found**: None — new config module (`h-m3/code/config.py`)
**Pattern Used**: Single dataclass (`ExperimentConfig`) mirroring architecture's flat-constants layout

---

## A-1: ExperimentConfig, ModelConfig, CalibrationConfig, EvalConfig [Complexity: 1, Budget: 1]

**Applied**: flat dataclass with grouped fields (avoids config-class sprawl for a single-script pipeline)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field

@dataclass
class ExperimentConfig:
    seed: int = 42
    benchmarks: tuple = ("trivia_qa", "natural_questions", "squad",
                          "pop_qa", "halueval_qa", "fever")
    cluster_1: tuple = ("trivia_qa", "natural_questions", "squad")
    cluster_2: tuple = ("pop_qa", "halueval_qa", "fever")
    within_cluster_pairs: tuple = (
        ("trivia_qa", "natural_questions"), ("trivia_qa", "squad"),
        ("natural_questions", "squad"),
        ("pop_qa", "halueval_qa"), ("pop_qa", "fever"),
        ("halueval_qa", "fever"),
    )
    sample_size: int = 1000
    outputs_dir: str = "h-m3/outputs"
    figures_dir: str = "h-m3/figures"

@dataclass
class ModelConfig:
    gen_model: str = "meta-llama/Llama-2-7b-hf"
    nli_model: str = "microsoft/deberta-v3-large"
    n_generations: int = 10
    temperature: float = 1.0

@dataclass
class CalibrationConfig:
    calib_split: float = 0.7      # 700/300 per FR-2
    target_fpr: float = 0.1       # FR-4 default target

@dataclass
class EvalConfig:
    degradation_threshold: float = 0.08   # PRD success criteria PRIMARY
    ci_upper_threshold: float = 0.12      # PRD success criteria SECONDARY
    all_pairs_threshold: float = 0.15     # PRD success criteria TERTIARY
    n_bootstrap: int = 1000
    bootstrap_ci: float = 0.95
```

### YAML Equivalent (reference only, code uses dataclass defaults directly)

```yaml
experiment:
  seed: 42
  sample_size: 1000
model:
  gen_model: meta-llama/Llama-2-7b-hf
  nli_model: microsoft/deberta-v3-large
  n_generations: 10
  temperature: 1.0
calibration:
  calib_split: 0.7
  target_fpr: 0.1
eval:
  degradation_threshold: 0.08
  ci_upper_threshold: 0.12
  n_bootstrap: 1000
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Core config dataclasses | ExperimentConfig, ModelConfig, CalibrationConfig, EvalConfig with defaults above |

---

## A-2: AblationConfig (FPR sweep, split sweep) [Complexity: 1, Budget: 1]

**Applied**: parametrized sweep lists per PRD Section 9 (AB-1, AB-2) — no tuning, fixed sweep values from experiment brief.

### Configuration (Python Dataclass)

```python
@dataclass
class AblationConfig:
    fpr_sweep: tuple = (0.05, 0.10, 0.15, 0.20)          # AB-1
    calib_split_sweep: tuple = (0.5, 0.6, 0.7, 0.8)       # AB-2 (50/50..80/20)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-2-1 | Ablation sweep config | AblationConfig with fpr_sweep and calib_split_sweep tuples, consumed by M3-9 |
