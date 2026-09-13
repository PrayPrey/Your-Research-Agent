# Configuration: H-E1 ECE Measurability Validation

**Type:** EXISTENCE (PoC) — single fixed config, no sweeps, 1 seed.

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - new config design (no existing code, no base hypothesis)
**Config Files Found:** None
**Pattern Used:** dataclass (Python)

**Applied:** Standard PyTorch/API-experiment config defaults (no KB pattern needed for PoC).

---

## Config (Python Dataclass)

```python
import os
from dataclasses import dataclass, field
from typing import Literal

@dataclass
class ModelConfig:
    model_name: str = "gpt-3.5-turbo-0125"
    temperature: float = 0.0          # deterministic per NFR-1
    max_tokens: int = 512

@dataclass
class DatasetConfig:
    dataset_name: str = "truthful_qa"
    subset: str = "multiple_choice"   # mc1 task used from this config
    split: str = "validation"         # 817 items, full set for PoC

@dataclass
class ExperimentConfig:
    conditions: list[str] = field(default_factory=lambda: [
        "baseline", "cot_only", "confidence_only", "cot_confidence", "token_padding"
    ])
    n_bins: int = 15                  # ECE bins, Guo et al. 2017
    seed: int = 42
    confidence_regex: str = r"Confidence:\s*(\d+)%"
    answer_regex: str = r"Answer:\s*([A-Z])"
    extraction_rate_threshold: float = 0.95

@dataclass
class APIConfig:
    api_key_env: str = "OPENAI_API_KEY"
    requests_per_minute: int = 500    # tier-1 default; lower if rate-limited
    max_retries: int = 5
    retry_backoff_base: float = 2.0   # exponential: base ** attempt seconds
    retry_on_status: tuple[int, ...] = (429, 500, 502, 503, 529)
    cache_enabled: bool = True
    cache_path: str = "cache/h-e1_responses.jsonl"

@dataclass
class OutputConfig:
    results_dir: str = "results"
    results_path: str = "results/results.json"
    figures_dir: str = "figures"
    reliability_fig_pattern: str = "figures/reliability_{condition}.png"
    ece_comparison_fig: str = "figures/ece_comparison.png"
    extraction_rate_fig: str = "figures/extraction_rate.png"

@dataclass
class Config:
    model: ModelConfig = field(default_factory=ModelConfig)
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    experiment: ExperimentConfig = field(default_factory=ExperimentConfig)
    api: APIConfig = field(default_factory=APIConfig)
    output: OutputConfig = field(default_factory=OutputConfig)

    def __post_init__(self):
        # Environment variable overrides
        self.model.model_name = os.getenv("HE1_MODEL_NAME", self.model.model_name)
        rpm = os.getenv("HE1_RPM")
        if rpm:
            self.api.requests_per_minute = int(rpm)

CONFIG = Config()
```

---

## YAML Equivalent (reference only — dataclass is source of truth)

```yaml
model:
  model_name: gpt-3.5-turbo-0125
  temperature: 0.0
  max_tokens: 512

dataset:
  dataset_name: truthful_qa
  subset: multiple_choice
  split: validation

experiment:
  conditions: [baseline, cot_only, confidence_only, cot_confidence, token_padding]
  n_bins: 15
  seed: 42
  confidence_regex: 'Confidence:\s*(\d+)%'
  answer_regex: 'Answer:\s*([A-Z])'
  extraction_rate_threshold: 0.95

api:
  api_key_env: OPENAI_API_KEY
  requests_per_minute: 500
  max_retries: 5
  retry_backoff_base: 2.0
  retry_on_status: [429, 500, 502, 503, 529]
  cache_enabled: true
  cache_path: cache/h-e1_responses.jsonl

output:
  results_dir: results
  results_path: results/results.json
  figures_dir: figures
  reliability_fig_pattern: 'figures/reliability_{condition}.png'
  ece_comparison_fig: figures/ece_comparison.png
  extraction_rate_fig: figures/extraction_rate.png
```

---

## Validation Rules

- `model.temperature == 0.0` (required for NFR-1 reproducibility)
- `experiment.n_bins > 0` and `n_bins <= 100`
- `experiment.conditions` must be non-empty and match keys in the `PROMPTS` dict (5 fixed conditions)
- `api.requests_per_minute > 0`
- `OPENAI_API_KEY` must be set in environment (raise `EnvironmentError` if missing at startup)
- `output.results_dir` / `output.figures_dir` created via `os.makedirs(exist_ok=True)` before writing

---

## Environment Variable Overrides

| Variable | Overrides | Default |
|----------|-----------|---------|
| `OPENAI_API_KEY` | API auth (required) | — |
| `HE1_MODEL_NAME` | `model.model_name` | `gpt-3.5-turbo-0125` |
| `HE1_RPM` | `api.requests_per_minute` | `500` |

---

## Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-E1-1 | Define config module | Implement dataclasses above in `config.py` |
| C-E1-2 | Env var + validation | `__post_init__` overrides + startup validation checks |
| C-E1-3 | Wire into experiment script | Import `CONFIG` singleton in main experiment runner |
