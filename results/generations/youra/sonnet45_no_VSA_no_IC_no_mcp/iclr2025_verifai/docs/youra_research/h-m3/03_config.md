# Configuration: h-m3 Invalid Beam Pruning

**Date:** 2026-08-25
**Hypothesis:** h-m3 (MECHANISM)
**Budget:** 0 subtasks

**Applied:** Standard MECHANISM config pattern, extends h-m2 dataclass structure

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Config classes verified from h-m2 base code
**Config Files Found:** `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_verifai/docs/youra_research/h-m2/code/config.py`
**Pattern Used:** dataclass (nested structure with ExperimentConfig)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: h-m2/code/config.py (ACTUAL CODE)
@dataclass
class DatasetConfig:
    name: str = "openai_humaneval"
    split: str = "test"
    poc_subset_size: int = 3
    full_size: int = 164
    ablation_size: int = 20

@dataclass
class ModelConfig:
    name: str = "meta-llama/CodeLlama-7b-hf"
    device: Literal["auto", "cuda", "cpu"] = "auto"
    dtype: Literal["float16", "float32"] = "float16"

@dataclass
class BeamSearchConfig:
    k: int = 3
    max_new_tokens: int = 64
    temperature: float = 0.8

@dataclass
class ScoringConfig:
    alpha_default: float = 0.7
    beta_default: float = 0.3
    weight_pairs: list = field(default_factory=lambda: [
        (0.5, 0.5),
        (0.6, 0.4),
        (0.7, 0.3),
        (0.8, 0.2)
    ])

@dataclass
class GateConfig:
    ast_latency_mean_ms: float = 50.0
    ast_latency_p95_ms: float = 100.0
    ranking_correctness_min: float = 0.8
    syntax_error_rate_max: float = 0.64

@dataclass
class OutputConfig:
    figures_dir: str = "figures"
    results_file: str = "outputs/h-m2_results.json"
    log_file: str = "outputs/h-m2_log.txt"
    ast_latency_file: str = "results/ast_latency_stats.json"
    beam_ranking_file: str = "results/beam_ranking_logs.csv"
    ablation_file: str = "results/ablation_results.json"
    baseline_file: str = "results/baseline_comparison.json"
```

**Verified from:** h-m2/code/config.py (actual implementation)

---

## Extended Configuration (Current Hypothesis)

### Full Config Schema

```python
"""Configuration for h-m3 invalid beam pruning tracking."""

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class DatasetConfig:
    name: str = "openai_humaneval"
    split: str = "test"
    full_size: int = 164

@dataclass
class ModelConfig:
    name: str = "meta-llama/CodeLlama-7b-hf"
    device: Literal["auto", "cuda", "cpu"] = "auto"
    dtype: Literal["float16", "float32"] = "float16"

@dataclass
class BeamSearchConfig:
    k: int = 5
    max_new_tokens: int = 512
    temperature: float = 0.8

@dataclass
class ScoringConfig:
    alpha: float = 0.7
    beta: float = 0.3

@dataclass
class BaselineConfig:
    alpha: float = 1.0
    beta: float = 0.0

@dataclass
class GateConfig:
    reduction_rate_mean: float = 0.50
    final_valid_proportion: float = 0.60
    final_valid_problems_pct: float = 0.70

@dataclass
class OutputConfig:
    results_dir: str = "results"
    figures_dir: str = "figures"
    beam_validity_logs: str = "results/beam_validity_logs.csv"
    reduction_rates: str = "results/reduction_rates.json"
    final_validity: str = "results/final_validity.json"
    temporal_dynamics: str = "results/temporal_dynamics.json"
    baseline_comparison: str = "results/baseline_comparison.json"

@dataclass
class ExperimentConfig:
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    beam_search: BeamSearchConfig = field(default_factory=BeamSearchConfig)
    scoring: ScoringConfig = field(default_factory=ScoringConfig)
    baseline: BaselineConfig = field(default_factory=BaselineConfig)
    gate: GateConfig = field(default_factory=GateConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    random_seed: int = 42
```

---

## Changes from h-m2

### Simplified Fields
- `ScoringConfig.alpha_default` → `ScoringConfig.alpha` (single value, not ablation)
- `ScoringConfig.beta_default` → `ScoringConfig.beta` (single value)
- Removed `ScoringConfig.weight_pairs` (h-m3 uses fixed α=0.7, β=0.3)

### New Config Classes
- `BaselineConfig`: Pure log-likelihood (α=1.0, β=0.0) for control experiment

### New Gate Thresholds
- `GateConfig.reduction_rate_mean`: 0.50 (50% reduction from start to end)
- `GateConfig.final_valid_proportion`: 0.60 (60% of final beams valid)
- `GateConfig.final_valid_problems_pct`: 0.70 (70% of problems have ≥3 valid beams)

### New Output Files
- `beam_validity_logs.csv`: Per-step validity tracking
- `reduction_rates.json`: Invalid beam reduction per problem
- `final_validity.json`: Final beam validity distribution
- `temporal_dynamics.json`: Early/middle/late phase statistics
- `baseline_comparison.json`: Pure vs combined scoring

### Removed Fields
- `DatasetConfig.poc_subset_size` (not needed for h-m3)
- `DatasetConfig.ablation_size` (not needed for h-m3)
- h-m2 gate thresholds (different validation criteria)

---

## Usage in Code

```python
# Load from defaults
config = ExperimentConfig()
print(config.scoring.alpha)  # 0.7

# Access nested configs
alpha = config.scoring.alpha
beta = config.scoring.beta
final_score = alpha * log_likelihood + beta * validity_score

# Baseline comparison
baseline_alpha = config.baseline.alpha  # 1.0
baseline_beta = config.baseline.beta    # 0.0

# Check gates
if mean_reduction < config.gate.reduction_rate_mean:
    print("FAILED: Reduction rate gate")
```

---

**Document Status:** Ready for Phase 4 Implementation
