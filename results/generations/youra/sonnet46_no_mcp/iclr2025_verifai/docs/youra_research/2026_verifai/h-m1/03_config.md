# Configuration: h-m1 — Distinct Failure Channel: SynCode Eliminates Syntactic Invalidity

**Type:** MECHANISM (INCREMENTAL — extends h-e1)
**Applied:** standard-dl-experiment-config-dataclass-pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config classes verified from base code (h-e1/code/config.py — actual file read)
**Config Files Found**: `docs/youra_research/20260508_verifai/h-e1/code/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual h-e1 Code)

```python
# From: h-e1/code/config.py (VERIFIED from actual implementation)
@dataclass
class ModelConfig:
    model_name: str = "codellama/CodeLlama-7b-hf"
    device_map: str = "auto"
    torch_dtype: str = "float16"

@dataclass
class GenerationConfig:
    temperature: float = 0.8
    max_new_tokens: int = 256      # ← h-e1 actual; h-m1 CHANGES to 512
    n_samples: int = 20
    seeds: List[int] = field(default_factory=lambda: list(range(20)))  # ← h-m1 REPLACES with seed scheme

# h-e1 also defined: SynCodeConfig, Z3Config, MypyConfig — NOT reused in h-m1
# h-e1 ThresholdConfig fields: delta_ast_min, z3_eligibility_min, mypy_structured_rate_min — h-m1 uses different fields
# h-e1 OutputConfig fields: data_dir, results_dir, figures_dir + h-e1 specific files
```

**Key Divergences from h-e1 (verified from actual code):**

| Field | h-e1 Actual | h-m1 Value | Reason |
|-------|-------------|------------|--------|
| `max_new_tokens` | 256 | 512 | Experiment brief specifies 512 |
| `seeds` (GenerationConfig) | `list(range(20))` | REMOVED; replaced by seed scheme | `seed = problem_idx × 100 + sample_idx` |
| `n_problems` | `humaneval_size: int = 164` (ExperimentConfig) | `n_problems: int = 164` | Renamed; full HumanEval |
| ThresholdConfig fields | `z3_eligibility_min`, `mypy_structured_rate_min` | `ci_lower_min`, `constraint_active_rate_min` | h-m1 tests different signals |
| `hypothesis_id` | `"h-e1"` | `"h-m1"` | Updated |

**Verified from**: `docs/youra_research/20260508_verifai/h-e1/code/config.py` (actual implementation)

---

## h-m1 Configuration Dataclasses

```python
from dataclasses import dataclass, field
from typing import List


@dataclass
class ModelConfig:
    """Inherited from h-e1; unchanged."""
    model_name: str = "codellama/CodeLlama-7b-hf"
    device_map: str = "auto"
    torch_dtype: str = "float16"


@dataclass
class GenerationConfig:
    """Extended from h-e1: max_new_tokens increased; seeds field removed (scheme-based)."""
    temperature: float = 0.8
    max_new_tokens: int = 512       # Non-standard: increased from h-e1's 256 per experiment brief
    n_samples: int = 20
    top_p: float = 0.95
    do_sample: bool = True
    # Seed scheme: seed = problem_idx * 100 + sample_idx (NOT stored here; computed at generation)


@dataclass
class BootstrapConfig:
    """New in h-m1: statistical test configuration."""
    n_bootstrap: int = 10000        # Standard for bootstrap CI (Chen et al. 2021)
    alpha: float = 0.05             # 95% CI


@dataclass
class ThresholdConfig:
    """Replaced h-e1 ThresholdConfig: different fields for MECHANISM gate."""
    delta_ast_min: float = 0.0
    ci_lower_min: float = 0.0      # Bootstrap CI lower bound must exceed 0
    constraint_active_rate_min: float = 0.3  # Pre-check threshold for mechanism verification


@dataclass
class OutputConfig:
    """Updated from h-e1: h-m1 paths + h-e1 pool reference."""
    data_dir: str = "h-m1/data/"
    results_dir: str = "h-m1/results/"
    figures_dir: str = "h-m1/figures/"
    baseline_pool_file: str = "baseline_pool.jsonl"
    syncode_pool_file: str = "syncode_pool.jsonl"
    progress_file: str = "progress.json"
    h_e1_baseline_pool: str = "h-e1/data/baseline_pool.jsonl"
    ast_failure_rates_file: str = "ast_failure_rates.json"
    bootstrap_ci_file: str = "bootstrap_ci.json"
    fmd_results_file: str = "fmd_results.json"
    transitions_file: str = "F_SynCode_success_transitions.json"
    mechanism_verification_file: str = "mechanism_verification.json"
    metrics_file: str = "metrics.json"


@dataclass
class FMDConfig:
    """A-6: FMD Classifier settings."""
    mypy_timeout: int = 30          # Non-standard: seconds for mypy.api.run() per completion
    evalplus_timeout: int = 10      # Non-standard: seconds for EvalPlus functional evaluation per sample
    # FMD category priority (exclusive ordering): syntax > type > functional > success
    category_priority: List[str] = field(
        default_factory=lambda: ["syntax", "type", "functional", "success"]
    )
    mypy_flags: List[str] = field(
        default_factory=lambda: ["--ignore-missing-imports"]
    )
    cleanup_temp_files: bool = True  # Remove temp .py files after mypy inspection


@dataclass
class ExperimentConfig:
    """Top-level h-m1 experiment configuration."""
    hypothesis_id: str = "h-m1"
    n_problems: int = 164
    model: ModelConfig = field(default_factory=ModelConfig)
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    bootstrap: BootstrapConfig = field(default_factory=BootstrapConfig)
    thresholds: ThresholdConfig = field(default_factory=ThresholdConfig)
    fmd: FMDConfig = field(default_factory=FMDConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
```

---

## YAML Configuration Template (`h-m1/config.yaml`)

```yaml
# h-m1 experiment configuration
hypothesis_id: "h-m1"
n_problems: 164

model:
  model_name: "codellama/CodeLlama-7b-hf"
  device_map: "auto"
  torch_dtype: "float16"

generation:
  temperature: 0.8          # Inherited from h-e1; standard for code generation diversity
  max_new_tokens: 512       # Increased from h-e1's 256
  n_samples: 20
  top_p: 0.95
  do_sample: true
  # Seed scheme (applied at generation time, not stored here):
  # seed = problem_idx * 100 + sample_idx

bootstrap:
  n_bootstrap: 10000        # Standard: 10,000 iterations for bootstrap CI
  alpha: 0.05               # 95% CI

thresholds:
  delta_ast_min: 0.0        # Gate: delta_ast must exceed 0
  ci_lower_min: 0.0         # Gate: bootstrap CI lower bound must exceed 0
  constraint_active_rate_min: 0.3  # Pre-check: mechanism must be active in >= 30% samples

fmd:
  mypy_timeout: 30          # Seconds; prevents hang on pathological completions
  evalplus_timeout: 10      # Seconds; per-sample functional evaluation cap
  category_priority:        # Exclusive ordering — first match wins
    - syntax
    - type
    - functional
    - success
  mypy_flags:
    - "--ignore-missing-imports"
  cleanup_temp_files: true

output:
  data_dir: "h-m1/data/"
  results_dir: "h-m1/results/"
  figures_dir: "h-m1/figures/"
  baseline_pool_file: "baseline_pool.jsonl"
  syncode_pool_file: "syncode_pool.jsonl"
  progress_file: "progress.json"
  h_e1_baseline_pool: "h-e1/data/baseline_pool.jsonl"
  ast_failure_rates_file: "ast_failure_rates.json"
  bootstrap_ci_file: "bootstrap_ci.json"
  fmd_results_file: "fmd_results.json"
  transitions_file: "F_SynCode_success_transitions.json"
  mechanism_verification_file: "mechanism_verification.json"
  metrics_file: "metrics.json"
```

---

## Valid Ranges for Key Hyperparameters

| Parameter | Default | Valid Range | Notes |
|-----------|---------|-------------|-------|
| `temperature` | 0.8 | [0.0, 2.0] | 0.0 = greedy; 0.8 standard for diverse pool |
| `max_new_tokens` | 512 | [64, 2048] | Must fit model context; 512 per experiment brief |
| `n_samples` | 20 | [10, 200] | Statistical power requires ≥ 10 per problem |
| `n_problems` | 164 | [1, 164] | Full HumanEval; reduce for debug runs |
| `n_bootstrap` | 10000 | [1000, 100000] | < 1000 unstable; > 10000 diminishing returns |
| `alpha` | 0.05 | (0.0, 1.0) | Standard 95% CI |
| `mypy_timeout` | 30 | [5, 120] | Seconds; pathological completions can hang |
| `evalplus_timeout` | 10 | [5, 60] | Seconds; per-sample cap |
| `constraint_active_rate_min` | 0.3 | [0.0, 1.0] | Pre-check fails if below threshold |

---

## A-6: FMD Classifier Configuration [Complexity: 13, Budget: 2 subtasks]

Applied: timeout-guard-pattern for mypy.api.run() calls

### Configuration

```python
@dataclass
class FMDConfig:
    mypy_timeout: int = 30          # Non-standard: guard against mypy hang on malformed code
    evalplus_timeout: int = 10      # Non-standard: cap per-sample functional test execution
    category_priority: List[str] = field(
        default_factory=lambda: ["syntax", "type", "functional", "success"]
    )
    mypy_flags: List[str] = field(
        default_factory=lambda: ["--ignore-missing-imports"]
    )
    cleanup_temp_files: bool = True
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | FMD Classification Logic | `classify_completion()` priority ordering (syntax→type→functional→success); mypy.api.run() with timeout wrapper; temp file write/cleanup for mypy |
| C-6-2 | FMD Distribution & Syntax Shift | `classify_pool()` → `compute_distribution()` → `compute_syntax_shift()`; output serialization to `fmd_results.json` |
