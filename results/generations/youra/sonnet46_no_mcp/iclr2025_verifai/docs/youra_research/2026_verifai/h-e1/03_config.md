# Configuration: h-e1 (EXISTENCE PoC)

**Hypothesis:** h-e1 — Formal Repair Tool Operationality
**Type:** EXISTENCE (PoC)
**Date:** 2026-05-09

Applied: PoC minimal pipeline pattern
Applied: Python code generation evaluation pipeline

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## Configuration (Python Dataclasses)

```python
# h-e1/code/config.py
from dataclasses import dataclass, field
from typing import List


@dataclass
class ModelConfig:
    model_name: str = "codellama/CodeLlama-7b-hf"
    device_map: str = "auto"
    torch_dtype: str = "float16"


@dataclass
class GenerationConfig:
    temperature: float = 0.8
    max_new_tokens: int = 256
    n_samples: int = 20
    seeds: List[int] = field(default_factory=lambda: list(range(20)))


@dataclass
class SynCodeConfig:
    grammar: str = "python"
    mode: str = "grammar_mask"
    # Inherits temperature, max_new_tokens, n_samples from GenerationConfig


@dataclass
class Z3Config:
    timeout_ms: int = 2000
    theory: str = "LIA"


@dataclass
class MypyConfig:
    flags: List[str] = field(default_factory=lambda: ["--ignore-missing-imports"])
    # Non-standard: 50 samples (not 10 from FR-5) for statistical validity
    sample_size: int = 50


@dataclass
class ThresholdConfig:
    delta_ast_min: float = 0.0   # strict > 0
    z3_eligibility_min: float = 0.15
    mypy_structured_rate_min: float = 0.90


@dataclass
class OutputConfig:
    data_dir: str = "h-e1/data/"
    results_dir: str = "h-e1/results/"
    figures_dir: str = "h-e1/figures/"
    baseline_pool_file: str = "baseline_pool.jsonl"
    syncode_pool_file: str = "syncode_pool.jsonl"
    z3_eligibility_file: str = "z3_eligibility.json"
    mypy_results_file: str = "mypy_results.json"
    metrics_file: str = "metrics.json"


@dataclass
class ExperimentConfig:
    hypothesis_id: str = "h-e1"
    seed: int = 1
    output_dir: str = "h-e1/"
    model: ModelConfig = field(default_factory=ModelConfig)
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    syncode: SynCodeConfig = field(default_factory=SynCodeConfig)
    z3: Z3Config = field(default_factory=Z3Config)
    mypy: MypyConfig = field(default_factory=MypyConfig)
    thresholds: ThresholdConfig = field(default_factory=ThresholdConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    humaneval_size: int = 164
    mbpp_size: int = 374
```

---

## Equivalent YAML Schema

```yaml
# h-e1/config.yaml
experiment:
  hypothesis_id: "h-e1"
  seed: 1
  output_dir: "h-e1/"
  humaneval_size: 164
  mbpp_size: 374

model:
  model_name: "codellama/CodeLlama-7b-hf"
  device_map: "auto"
  torch_dtype: "float16"

generation:
  temperature: 0.8
  max_new_tokens: 256
  n_samples: 20
  seeds: [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]

syncode:
  grammar: "python"
  mode: "grammar_mask"

z3:
  timeout_ms: 2000
  theory: "LIA"

mypy:
  flags: ["--ignore-missing-imports"]
  sample_size: 50

thresholds:
  delta_ast_min: 0.0
  z3_eligibility_min: 0.15
  mypy_structured_rate_min: 0.90

output:
  data_dir: "h-e1/data/"
  results_dir: "h-e1/results/"
  figures_dir: "h-e1/figures/"
  baseline_pool_file: "baseline_pool.jsonl"
  syncode_pool_file: "syncode_pool.jsonl"
  z3_eligibility_file: "z3_eligibility.json"
  mypy_results_file: "mypy_results.json"
  metrics_file: "metrics.json"
```

---

## Hyperparameter Justification

| Parameter | Value | Valid Range | Source | Sensitivity |
|-----------|-------|-------------|--------|-------------|
| `temperature` | 0.8 | 0.6–1.0 | SynCode paper [Ugare 2024], CodeLlama-7B standard | Lower → less diversity; higher → more syntax errors |
| `max_new_tokens` | 256 | 128–512 | SynCode paper default; HumanEval solutions fit in 256 tokens | Lower may truncate; higher increases latency |
| `n_samples` | 20 | 10–50 | SynCode frozen pool protocol | Fewer → higher variance in ast.parse rate estimates |
| `z3.timeout_ms` | 2000 | 500–10000 | Z3 documentation standard; de Moura & Bjørner 2008 | Lower → more `unknown` returns; higher → path explosion risk |
| `mypy.sample_size` | 50 | 10–164 | Non-standard: increased from FR-5's 10 for statistical validity | Must be ≤ 164 (HumanEval size); <10 → unreliable rate |
| `thresholds.z3_eligibility_min` | 0.15 | — | Phase 2B assumption A2; 02b_verification_plan.md | Below 0.15 → Z3 tool not operationally useful |
| `thresholds.mypy_structured_rate_min` | 0.90 | — | mypy.api stability assumption | mypy.api.run() expected ~95–100% on valid Python files |
| `seed` | 1 | any int | Reproducibility convention | Master seed for non-generation randomness |
| `seeds` | [0..19] | fixed pool | SynCode frozen pool protocol | Must be identical for baseline and syncode pools (controlled comparison) |

---

## Environment Requirements

```
Python >= 3.9
CUDA: single GPU (set CUDA_VISIBLE_DEVICES before running)

Key packages:
  transformers >= 4.35.0
  accelerate >= 0.24.0
  torch >= 2.0.0
  syncode                    # pip install syncode OR git clone uiuc-focal-lab/syncode
  z3-solver >= 4.12.0
  mypy >= 1.0.0
  evalplus >= 0.3.0
  matplotlib >= 3.7.0
  seaborn >= 0.12.0

Install:
  pip install syncode z3-solver mypy evalplus transformers accelerate matplotlib seaborn

GPU setup (required before running):
  export CUDA_VISIBLE_DEVICES=<single_empty_gpu_id>

OS: Linux (recommended); macOS supported for CPU-only runs
```

---

## Reproducibility Specifications

- **Master seed**: `seed=1` passed to `torch.manual_seed`, `random.seed`, `numpy.seed` at startup
- **Pool seeds**: `seeds=[0..19]` — fixed list, used identically for both baseline and syncode generation; ensures controlled comparison
- **Frozen pool design**: Pools serialized to JSONL on disk before any downstream analysis; re-runs load from disk
- **Determinism guarantees**: `transformers.set_seed(seed)` before each sample generation; SynCode LogitsProcessor is deterministic given same input tokens
- **Verification**: Re-run `run_experiment.py` with `--load_pools` flag to skip regeneration and recompute metrics from saved JSONL; metrics must match within float precision

---

## Subtasks

Budget: 0 subtasks (LIGHT tier — architecture-level config only)
