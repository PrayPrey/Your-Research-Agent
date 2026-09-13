# Configuration: h-m2 Combined Scoring Function

**Date:** 2026-08-25
**Hypothesis:** h-m2 (MECHANISM)
**Budget:** 2 subtasks

**Applied:** Standard MECHANISM config pattern, extends h-m1 dataclass structure

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Config classes verified from h-m1 base code
**Config Files Found:** `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_verifai/docs/youra_research/h-m1/code/config.py`
**Pattern Used:** dataclass (nested structure with ExperimentConfig)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

The following configs are inherited from h-m1:

```python
# From: h-m1/code/config.py (ACTUAL CODE)
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
class OutputConfig:
    figures_dir: str = "figures"
    results_file: str = "outputs/ablation_results.json"
    log_file: str = "outputs/mechanism_log.txt"
```

**Verified from:** h-m1/code/config.py (actual implementation)

---

## Extended Configuration (Current Hypothesis)

### Full Config Schema

```python
"""Configuration for h-m2 combined scoring mechanism."""

from dataclasses import dataclass, field
from typing import Literal
import yaml


# Inherited from h-m1 (unchanged)
@dataclass
class DatasetConfig:
    name: str = "openai_humaneval"
    split: str = "test"
    poc_subset_size: int = 3
    full_size: int = 164  # HumanEval-164
    ablation_size: int = 20  # New: stratified subset for α/β testing


@dataclass
class ModelConfig:
    name: str = "meta-llama/CodeLlama-7b-hf"
    device: Literal["auto", "cuda", "cpu"] = "auto"
    dtype: Literal["float16", "float32"] = "float16"


@dataclass
class BeamSearchConfig:
    k: int = 5
    max_new_tokens: int = 512  # Increased from h-m1's 256
    temperature: float = 0.8  # Changed from h-m1's 1.0


# New for h-m2: Scoring weights
@dataclass
class ScoringConfig:
    alpha_default: float = 0.7  # Log-likelihood weight
    beta_default: float = 0.3  # Syntax validity weight
    weight_pairs: list[tuple[float, float]] = field(default_factory=lambda: [
        (0.5, 0.5),
        (0.6, 0.4),
        (0.7, 0.3),
        (0.8, 0.2)
    ])


# New for h-m2: AST validation gates
@dataclass
class GateConfig:
    ast_latency_mean_ms: float = 50.0
    ast_latency_p95_ms: float = 100.0
    ranking_correctness_min: float = 0.8  # 80% of steps
    syntax_error_rate_max: float = 0.64  # Must beat greedy baseline


@dataclass
class OutputConfig:
    figures_dir: str = "figures"
    results_file: str = "outputs/h-m2_results.json"
    log_file: str = "outputs/h-m2_log.txt"
    # New output files
    ast_latency_file: str = "results/ast_latency_stats.json"
    beam_ranking_file: str = "results/beam_ranking_logs.csv"
    ablation_file: str = "results/ablation_results.json"
    baseline_file: str = "results/baseline_comparison.json"


@dataclass
class ExperimentConfig:
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    beam_search: BeamSearchConfig = field(default_factory=BeamSearchConfig)
    scoring: ScoringConfig = field(default_factory=ScoringConfig)  # New
    gate: GateConfig = field(default_factory=GateConfig)  # New
    output: OutputConfig = field(default_factory=OutputConfig)
    random_seed: int = 42

    @classmethod
    def from_yaml(cls, path: str):
        with open(path, 'r') as f:
            config_dict = yaml.safe_load(f)

        return cls(
            dataset=DatasetConfig(**config_dict.get('dataset', {})),
            model=ModelConfig(**config_dict.get('model', {})),
            beam_search=BeamSearchConfig(**config_dict.get('beam_search', {})),
            scoring=ScoringConfig(**config_dict.get('scoring', {})),
            gate=GateConfig(**config_dict.get('gate', {})),
            output=OutputConfig(**config_dict.get('output', {})),
            random_seed=config_dict.get('random_seed', 42)
        )
```

### Optional: YAML Config File

```yaml
# config.yaml (optional, can use dataclass defaults)
dataset:
  name: "openai_humaneval"
  split: "test"
  poc_subset_size: 3
  full_size: 164
  ablation_size: 20

model:
  name: "meta-llama/CodeLlama-7b-hf"
  device: "auto"
  dtype: "float16"

beam_search:
  k: 5
  max_new_tokens: 512
  temperature: 0.8

scoring:
  alpha_default: 0.7
  beta_default: 0.3
  weight_pairs:
    - [0.5, 0.5]
    - [0.6, 0.4]
    - [0.7, 0.3]
    - [0.8, 0.2]

gate:
  ast_latency_mean_ms: 50.0
  ast_latency_p95_ms: 100.0
  ranking_correctness_min: 0.8
  syntax_error_rate_max: 0.64

output:
  figures_dir: "figures"
  results_file: "outputs/h-m2_results.json"
  log_file: "outputs/h-m2_log.txt"
  ast_latency_file: "results/ast_latency_stats.json"
  beam_ranking_file: "results/beam_ranking_logs.csv"
  ablation_file: "results/ablation_results.json"
  baseline_file: "results/baseline_comparison.json"

random_seed: 42
```

---

## Subtask Breakdown [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1 | Extend h-m1 config schema | Add ScoringConfig and GateConfig dataclasses |
| C-2 | Create config.yaml template | YAML file with default values for experiments |

---

## Changes from h-m1

### Modified Fields
- `BeamSearchConfig.max_new_tokens`: 256 → 512 (longer code generation)
- `BeamSearchConfig.temperature`: 1.0 → 0.8 (from PRD specifications)

### New Fields
- `DatasetConfig.full_size`: 164 (HumanEval-164 size)
- `DatasetConfig.ablation_size`: 20 (ablation subset)
- `ScoringConfig`: Entire class (α/β weights)
- `GateConfig`: Entire class (success criteria thresholds)
- `OutputConfig`: 4 new result file paths

### Removed Fields
- `AblationConfig` (h-m1 k-value ablation not needed)
- `MechanismGateConfig` (replaced by GateConfig)

---

## Usage in Code

```python
# Load from defaults
config = ExperimentConfig()
print(config.scoring.alpha_default)  # 0.7

# Load from YAML
config = ExperimentConfig.from_yaml("config.yaml")

# Access nested configs
alpha, beta = config.scoring.alpha_default, config.scoring.beta_default
final_score = alpha * log_likelihood + beta * validity_score

# Check gates
if mean_latency > config.gate.ast_latency_mean_ms:
    print("FAILED: AST latency gate")
```

---

**Document Status:** Ready for Phase 4 Implementation
