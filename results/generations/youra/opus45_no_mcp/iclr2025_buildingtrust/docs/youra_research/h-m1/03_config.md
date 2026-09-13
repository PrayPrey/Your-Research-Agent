# Config: H-M1 CoT Reasoning Chain Detection

**Type**: MECHANISM (standard tier) — single fixed run per condition, no hyperparameter sweep.

**Applied**: Standard PyTorch/API-experiment dataclass config pattern (Archon KB unreachable in this environment — no MCP tools registered; using stdlib `@dataclass` defaults).

## Codebase Analysis (Serena)

**Project Type**: green-field (H-M1 code/ does not exist yet; H-E1 base has no code/ either)
**Status**: green-field — new config design, no Serena calls made (Serena MCP not available in this environment)
**Config Files Found**: None
**Pattern Used**: dataclass (Python)

---

## Config (`config.py`)

```python
from dataclasses import dataclass, field
from datetime import date


@dataclass
class APIConfig:
    model: str = "gpt-3.5-turbo"
    fallback_model: str = "meta-llama/Llama-2-70b-chat-hf"  # Together AI fallback
    temperature: float = 0.0
    max_tokens: int = 1024
    max_retries: int = 3
    retry_backoff_base: float = 2.0   # exponential backoff: base ** attempt seconds
    request_timeout: float = 60.0


@dataclass
class DatasetConfig:
    name: str = "truthful_qa"
    subset: str = "multiple_choice"   # mc2 target field
    split: str = "validation"         # HF truthful_qa only has 'validation' (817 rows)
    num_examples: int = 817           # full set, no subsampling


@dataclass
class DetectionConfig:
    # regex patterns for reasoning-chain detection (FR-4)
    numbered_step_pattern: str = r"(?:^|\n)\s*(?:\d+[\.\)]|Step\s+\d+:)"
    ordinal_pattern: str = r"\b(First|Second|Third|Fourth|Fifth|Finally|Lastly)\b"
    logical_connector_pattern: str = r"\b(therefore|thus|hence|because|so|consequently)\b"
    answer_pattern: str = r"(?:answer|Answer)[:\s]+\(?([A-E])\)?"
    confidence_pattern: str = r"(?:confidence|Confidence)[:\s]+(\d*\.?\d+)%?"
    case_insensitive: bool = True


@dataclass
class GateConfig:
    # PoC pass conditions (all MUST_WORK)
    min_reasoning_presence_rate: float = 0.90
    min_mean_step_count: float = 2.0
    min_rate_difference: float = 0.50  # cot_rate - baseline_rate


@dataclass
class PathConfig:
    results_dir: str = "h-m1/code/results"
    cache_path: str = "h-m1/code/.cache/responses.jsonl"
    figures_dir: str = "h-m1/figures"
    results_file: str = "h-m1/code/results/h-m1_results.json"
    metrics_file: str = "h-m1/code/results/h-m1_metrics.yaml"


@dataclass
class ExperimentConfig:
    hypothesis_id: str = "H-M1"
    date: str = str(date.today())
    conditions: list = field(default_factory=lambda: ["baseline", "cot"])
    seed: int = 42
    api: APIConfig = field(default_factory=APIConfig)
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    detection: DetectionConfig = field(default_factory=DetectionConfig)
    gate: GateConfig = field(default_factory=GateConfig)
    paths: PathConfig = field(default_factory=PathConfig)


CONFIG = ExperimentConfig()
```

Non-standard: `retry_backoff_base=2.0` used for exponential backoff (`2**attempt` sec) per NFR-2. `split="validation"` is non-standard-looking but is the only split HF `truthful_qa` provides.

---

## YAML Schema (metrics/output persistence, FR-7)

```yaml
# h-m1_metrics.yaml
hypothesis_id: H-M1
date: "2026-08-19"
conditions: [baseline, cot]
metrics:
  baseline:
    reasoning_presence_rate: 0.0
    mean_step_count: 0.0
    n: 817
  cot:
    reasoning_presence_rate: 0.0
    mean_step_count: 0.0
    n: 817
gate:
  cot_reasoning_presence_rate_pass: false   # > 0.90
  cot_mean_step_count_pass: false           # > 2.0
  rate_difference_pass: false               # cot - baseline > 0.50
  overall_pass: false
api:
  model: gpt-3.5-turbo
  temperature: 0.0
  max_tokens: 1024
```

---

## Subtasks

Config is shared infra, not a separately budgeted task — consumed by A-1 (dataset name/split), A-3 (APIConfig), A-4 (DetectionConfig regex), A-6 (GateConfig), A-7 (PathConfig, ExperimentConfig).

No additional subtasks: config values are fixed constants for this PoC, no sweep/grid.
