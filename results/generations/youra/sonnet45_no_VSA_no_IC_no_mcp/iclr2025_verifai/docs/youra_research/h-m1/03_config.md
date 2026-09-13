# Configuration Specification: h-m1 Beam Search Mechanism Validation

**Date:** 2026-08-25  
**Author:** yoon303@ust.ac.kr  
**Hypothesis:** h-m1 (MECHANISM)  
**Base Hypothesis:** h-e1 (EXISTENCE)

**Applied:** Standard PyTorch/HuggingFace defaults for beam search instrumentation

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Config classes verified from h-e1 actual code  
**Config Files Found:** `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_verifai/docs/youra_research/h-e1/code/config.py`  
**Pattern Used:** dataclass with YAML loader

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From h-e1 Actual Code)

The following configs are inherited from h-e1 validated implementation:

```python
# From: h-e1/code/config.py (ACTUAL CODE - Field names verified)
from dataclasses import dataclass, field
from typing import Literal

@dataclass
class DatasetConfig:
    name: str = "openai_humaneval"
    split: str = "test"
    poc_subset_size: int = 5

@dataclass
class ModelConfig:
    name: str = "meta-llama/CodeLlama-7b-hf"
    device: Literal["auto", "cuda", "cpu"] = "auto"
    dtype: Literal["float16", "float32"] = "float16"

@dataclass
class BeamSearchConfig:
    k: int = 5
    max_new_tokens: int = 256
    temperature: float = 1.0
    do_sample: bool = False

@dataclass
class OutputConfig:
    figures_dir: str = "figures"
    results_file: str = "outputs/results.json"
    log_file: str = "outputs/poc_log.txt"
```

**Verified from:** h-e1/code/config.py (actual implementation)

---

## Extended Configuration (h-m1)

### New Config Classes

```python
@dataclass
class AblationConfig:
    k_values: list[int] = field(default_factory=lambda: [3, 5, 10])
    num_problems: int = 3

@dataclass
class MechanismGateConfig:
    beam_maintenance: float = 1.0  # 100% steps must maintain k
    diversity_ratio_min: float = 0.6  # >=60% unique for k=5
```

### Modified Base Configs

```python
@dataclass
class DatasetConfig:
    name: str = "openai_humaneval"
    split: str = "test"
    poc_subset_size: int = 3  # Changed from h-e1's 5 to 3 for ablation study
```

### Full h-m1 Config

```python
# h-m1/code/config.py
from dataclasses import dataclass, field
from typing import Literal
import yaml

@dataclass
class DatasetConfig:
    name: str = "openai_humaneval"
    split: str = "test"
    poc_subset_size: int = 3

@dataclass
class ModelConfig:
    name: str = "meta-llama/CodeLlama-7b-hf"
    device: Literal["auto", "cuda", "cpu"] = "auto"
    dtype: Literal["float16", "float32"] = "float16"

@dataclass
class BeamSearchConfig:
    k: int = 5
    max_new_tokens: int = 256
    temperature: float = 1.0
    do_sample: bool = False

@dataclass
class AblationConfig:
    k_values: list[int] = field(default_factory=lambda: [3, 5, 10])
    num_problems: int = 3

@dataclass
class MechanismGateConfig:
    beam_maintenance: float = 1.0
    diversity_ratio_min: float = 0.6

@dataclass
class OutputConfig:
    figures_dir: str = "figures"
    results_file: str = "outputs/ablation_results.json"
    log_file: str = "outputs/mechanism_log.txt"

@dataclass
class ExperimentConfig:
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    beam_search: BeamSearchConfig = field(default_factory=BeamSearchConfig)
    ablation: AblationConfig = field(default_factory=AblationConfig)
    gate: MechanismGateConfig = field(default_factory=MechanismGateConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    random_seed: int = 42

    @classmethod
    def from_yaml(cls, path: str) -> 'ExperimentConfig':
        with open(path, 'r') as f:
            config_dict = yaml.safe_load(f)

        return cls(
            dataset=DatasetConfig(**config_dict.get('dataset', {})),
            model=ModelConfig(**config_dict.get('model', {})),
            beam_search=BeamSearchConfig(**config_dict.get('beam_search', {})),
            ablation=AblationConfig(**config_dict.get('ablation', {})),
            gate=MechanismGateConfig(**config_dict.get('gate', {})),
            output=OutputConfig(**config_dict.get('output', {})),
            random_seed=config_dict.get('random_seed', 42)
        )
```

---

## YAML Config Template

```yaml
# h-m1/code/config.yaml
dataset:
  name: "openai_humaneval"
  split: "test"
  poc_subset_size: 3

model:
  name: "meta-llama/CodeLlama-7b-hf"
  device: "auto"
  dtype: "float16"

beam_search:
  k: 5
  max_new_tokens: 256
  temperature: 1.0
  do_sample: false

ablation:
  k_values: [3, 5, 10]
  num_problems: 3

gate:
  beam_maintenance: 1.0
  diversity_ratio_min: 0.6

output:
  figures_dir: "figures"
  results_file: "outputs/ablation_results.json"
  log_file: "outputs/mechanism_log.txt"

random_seed: 42
```

---

## Configuration Changes from h-e1

| Field | h-e1 Value | h-m1 Value | Rationale |
|-------|------------|------------|-----------|
| `dataset.poc_subset_size` | 5 | 3 | Ablation study needs smaller set |
| `output.results_file` | results.json | ablation_results.json | Distinguishes mechanism output |
| N/A | N/A | `AblationConfig` added | New ablation study framework |
| N/A | N/A | `MechanismGateConfig` added | Mechanism-specific gates |

---

## Task Configuration (Zero Subtasks)

No subtask breakdown required (budget: 0 subtasks). Configuration is copy-paste ready for Phase 4 implementation.

---

**Document Status:** Ready for Phase 4 Implementation
