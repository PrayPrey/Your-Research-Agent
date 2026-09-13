# H-M2 Config: Annotator Conflation Analysis

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1)
**Status**: config classes verified from h-m1/code/config.py
**Config Files Found**: `docs/youra_research/h-m1/code/config.py` (`M1Config` dataclass)
**Pattern Used**: dataclass

H-M2 reads H-M1 results as input. `models` list must match H-M1's actual HF
model ids, not short aliases — verified from code above.

---

## A-1: Config Module [Complexity: 1, Budget: 1]

**Applied**: Standard PyTorch/analysis-script dataclass pattern (same style as h-m1)

### Python Dataclass

```python
from dataclasses import dataclass, field
from typing import List


@dataclass
class ThresholdConfig:
    high_confidence_threshold: float = 0.7
    threshold_range: List[float] = field(default_factory=lambda: [0.5, 0.6, 0.7, 0.8, 0.9])


@dataclass
class GateConfig:
    pass_rate_diff_threshold: float = 0.15
    pass_conflation_threshold: float = 0.85
    fail_rate_diff_threshold: float = 0.3
    fail_conflation_threshold: float = 0.7


@dataclass
class PathConfig:
    h_m1_results: str = "h-m1/code/outputs/results.json"
    output_dir: str = "h-m2/code/outputs"
    figures_dir: str = "h-m2/figures"


@dataclass
class FeatureMarkers:
    USER_MARKERS: List[str] = field(default_factory=lambda: [
        "you think", "your opinion", "do you believe"
    ])
    CONTEXT_MARKERS: List[str] = field(default_factory=lambda: [
        "given that", "considering", "in this situation"
    ])
    HEDGE_MARKERS: List[str] = field(default_factory=lambda: [
        "might", "could", "possibly"
    ])


@dataclass
class ModelConfig:
    # Non-standard: full HF ids, verified from h-m1/code/config.py M1Config.models
    models: List[str] = field(default_factory=lambda: [
        "meta-llama/Llama-2-7b-chat-hf",
        "meta-llama/Llama-2-13b-chat-hf",
        "mistralai/Mistral-7B-Instruct-v0.2",
    ])


@dataclass
class M2Config:
    thresholds: ThresholdConfig = field(default_factory=ThresholdConfig)
    gates: GateConfig = field(default_factory=GateConfig)
    paths: PathConfig = field(default_factory=PathConfig)
    markers: FeatureMarkers = field(default_factory=FeatureMarkers)
    model_cfg: ModelConfig = field(default_factory=ModelConfig)
    seed: int = 42


CONFIG = M2Config()
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | config.py | Write dataclasses above to `h-m2/code/config.py` |

---

## Example config file (YAML, optional override)

```yaml
thresholds:
  high_confidence_threshold: 0.7
  threshold_range: [0.5, 0.6, 0.7, 0.8, 0.9]

gates:
  pass_rate_diff_threshold: 0.15
  pass_conflation_threshold: 0.85
  fail_rate_diff_threshold: 0.3
  fail_conflation_threshold: 0.7

paths:
  h_m1_results: h-m1/code/outputs/results.json
  output_dir: h-m2/code/outputs
  figures_dir: h-m2/figures

markers:
  USER_MARKERS: ["you think", "your opinion", "do you believe"]
  CONTEXT_MARKERS: ["given that", "considering", "in this situation"]
  HEDGE_MARKERS: ["might", "could", "possibly"]

model_cfg:
  models:
    - meta-llama/Llama-2-7b-chat-hf
    - meta-llama/Llama-2-13b-chat-hf
    - mistralai/Mistral-7B-Instruct-v0.2

seed: 42
```

YAML loading is optional — this is a pure-analysis task over existing H-M1
outputs, no training loop, so the dataclass defaults above are sufficient on
their own. Load YAML only if per-run overrides are actually needed.
