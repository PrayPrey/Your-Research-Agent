# Configuration: h-m4 Final Valid Output Selection

**Date:** 2026-08-25
**Hypothesis:** h-m4 (MECHANISM)
**Budget:** 10 tasks allocated

**Applied:** MECHANISM config pattern, extends h-m3 dataclass structure

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Config classes verified from h-m3 base code
**Config Files Found:** `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_verifai/docs/youra_research/h-m3/code/` (not yet implemented)
**Pattern Used:** dataclass (nested structure with ExperimentConfig)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From h-m3 Spec)

```python
# From: h-m3/03_config.md (spec - no actual code yet)
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
```

**Verified from:** h-m3/03_config.md specification

---

## Extended Configuration (Current Hypothesis)

### Full Config Schema

```python
"""Configuration for h-m4 final valid output selection."""

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
class GreedyConfig:
    num_beams: int = 1
    max_new_tokens: int = 512
    temperature: float = 0.8


@dataclass
class ScoringConfig:
    alpha: float = 0.7
    beta: float = 0.3


@dataclass
class SelectionConfig:
    strategy: Literal["argmax", "validity_first", "random_valid"] = "argmax"


@dataclass
class GateConfig:
    syntax_validity_rate_min: float = 0.60
    beam_better_than_greedy: bool = True
    selection_accuracy_min: float = 0.90


@dataclass
class OutputConfig:
    results_dir: str = "results"
    figures_dir: str = "figures"
    final_outputs: str = "results/final_outputs.json"
    greedy_baseline: str = "results/greedy_baseline.json"
    error_comparison: str = "results/error_comparison.json"
    selection_quality: str = "results/selection_quality.json"
    strategy_comparison: str = "results/strategy_comparison.json"


@dataclass
class ExperimentConfig:
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    beam_search: BeamSearchConfig = field(default_factory=BeamSearchConfig)
    greedy: GreedyConfig = field(default_factory=GreedyConfig)
    scoring: ScoringConfig = field(default_factory=ScoringConfig)
    selection: SelectionConfig = field(default_factory=SelectionConfig)
    gate: GateConfig = field(default_factory=GateConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    random_seed: int = 42
```

---

## Changes from h-m3

### New Config Classes
- `GreedyConfig`: Greedy sampling baseline (num_beams=1)
- `SelectionConfig`: Final beam selection strategy (argmax default)

### New Gate Thresholds
- `GateConfig.syntax_validity_rate_min`: 0.60 (60% final outputs valid)
- `GateConfig.beam_better_than_greedy`: True (beam error < greedy error)
- `GateConfig.selection_accuracy_min`: 0.90 (90% accuracy when ≥3 valid beams)

### New Output Files
- `final_outputs.json`: Selected beam outputs with validity labels
- `greedy_baseline.json`: Greedy sampling results
- `error_comparison.json`: Beam vs greedy syntax error rates
- `selection_quality.json`: Selection accuracy by beam availability
- `strategy_comparison.json`: Argmax vs alternative strategies

### Removed Fields from h-m3
- `BaselineConfig` (h-m3 used α=1.0/β=0.0, h-m4 uses greedy sampling)
- h-m3 gate thresholds (different validation criteria)
- h-m3 temporal tracking outputs (not needed for h-m4)

---

## Usage in Code

```python
# Load from defaults
config = ExperimentConfig()

# Beam search final selection
alpha = config.scoring.alpha  # 0.7
beta = config.scoring.beta    # 0.3
final_score = alpha * log_likelihood + beta * validity_score
selected_beam = beams[np.argmax(final_scores)]

# Greedy baseline
greedy_outputs = model.generate(
    **inputs,
    num_beams=config.greedy.num_beams,  # 1
    max_new_tokens=config.greedy.max_new_tokens,  # 512
    temperature=config.greedy.temperature  # 0.8
)

# Gate validation
if syntax_validity_rate < config.gate.syntax_validity_rate_min:
    print("FAILED: Syntax validity gate (ABANDON)")

if beam_error_rate >= greedy_error_rate:
    print("FAILED: Baseline comparison gate (ABANDON)")
```

---

**Document Status:** Ready for Phase 4 Implementation
