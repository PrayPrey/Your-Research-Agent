# Config: H-E1
# Deduplication Benchmark Signature — Existence Verification

**Hypothesis:** H-E1 (EXISTENCE)
**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr

Applied: Dataclass-first Config (Python dataclasses as single source of truth, no YAML needed for simple config)
Applied: Constants Module Pattern (all magic numbers in one constants.py file)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — new config design (no MCP available; Serena skipped)
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## Configuration Dataclasses

```python
from dataclasses import dataclass, field


@dataclass
class ModelConfig:
    sizes: list[str] = field(default_factory=lambda: ["160m", "410m", "1b", "6.9b"])
    pile_step: int = 99000
    dedup_step: int = 143000
    batch_tokens: int = 2097152
    hf_prefix: str = "EleutherAI/pythia-{size}"


@dataclass
class BenchmarkConfig:
    names: list[str] = field(default_factory=lambda: ["mmlu", "hellaswag", "arc_challenge", "winogrande"])
    fewshot: dict[str, int] = field(default_factory=lambda: {
        "mmlu": 5,
        "hellaswag": 0,
        "arc_challenge": 25,
        "winogrande": 5,
    })


@dataclass
class StatConfig:
    alpha: float = 0.05
    n_tests: int = 4
    corrected_alpha: float = 0.0125   # Bonferroni: alpha / n_tests
    min_delta_for_mechanism: float = 0.001


@dataclass
class PathConfig:
    base_dir: str = "docs/youra_research/h-e1"
    results_dir: str = "docs/youra_research/h-e1/results"
    figures_dir: str = "docs/youra_research/h-e1/figures"


@dataclass
class ExperimentConfig:
    model: ModelConfig = field(default_factory=ModelConfig)
    benchmark: BenchmarkConfig = field(default_factory=BenchmarkConfig)
    stat: StatConfig = field(default_factory=StatConfig)
    paths: PathConfig = field(default_factory=PathConfig)
    dtype: str = "float16"
    batch_size: str = "auto:4"
    device: str = "auto"


CONFIG = ExperimentConfig()
```

---

## YAML Configuration (experiment_config.yaml)

```yaml
experiment:
  hypothesis_id: "h-e1"
  name: "Deduplication Benchmark Signature — Existence Check"

models:
  sizes: ["160m", "410m", "1b", "6.9b"]
  pile:
    hf_prefix: "EleutherAI/pythia-{size}"
    step: 99000
  dedup:
    hf_prefix: "EleutherAI/pythia-{size}-deduped"
    step: 143000
  batch_tokens: 2097152

benchmarks:
  tasks: [mmlu, hellaswag, arc_challenge, winogrande]
  fewshot:
    mmlu: 5
    hellaswag: 0
    arc_challenge: 25
    winogrande: 5

statistics:
  alpha: 0.05
  n_tests: 4
  corrected_alpha: 0.0125
  min_delta_for_mechanism: 0.001

hardware:
  dtype: "float16"
  batch_size: "auto:4"
  device: "auto"

paths:
  base_dir: "docs/youra_research/h-e1"
  results_dir: "docs/youra_research/h-e1/results"
  figures_dir: "docs/youra_research/h-e1/figures"
```

---

## requirements.txt

```
lm-eval>=0.4.0
transformers>=4.38.0
accelerate>=0.27.0
torch>=2.1.0
scipy>=1.11.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
statsmodels>=0.14.0
datasets>=2.16.0
```

---

## E3: Results Parsing [Complexity: 6, Budget: 1 subtask]

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-E3-1 | Implement results parser | Parse lm-eval JSON output files; extract `acc,none` field per task; handle missing keys gracefully; write `results_matrix.json` |

---

## E5: Visualization [Complexity: 6, Budget: 1 subtask]

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-E5-1 | Implement 4-panel visualization | `differential_bar` (significance stars at p<0.0125), `scaling_plot`, `paired_scatter` (diagonal reference line), `pvalue_heatmap` (Bonferroni threshold line) |
