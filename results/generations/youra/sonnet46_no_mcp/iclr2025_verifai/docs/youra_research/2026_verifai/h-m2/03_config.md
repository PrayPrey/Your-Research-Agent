# Configuration: h-m2

**Hypothesis:** h-m2 — Mechanistic Complementarity of mypy/ast Repair vs. SynCode
**Date:** 2026-05-10

Applied: iterative-feedback-repair-loop (Olausson 2023 / SELF-REFINE)
Applied: Jaccard-complement C_score independence null model

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1 code analyzed)
**Status**: Config classes verified from base code — actual field names confirmed from `h-m1/code/config.py`
**Config Files Found**: `docs/youra_research/20260508_verifai/h-m1/code/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual h-m1 Code)

```python
# From: h-m1/code/config.py (ACTUAL CODE — verified field names)
@dataclass
class ModelConfig:
    model_name: str = "codellama/CodeLlama-7b-hf"
    device_map: str = "auto"
    torch_dtype: str = "float16"

@dataclass
class GenerationConfig:
    temperature: float = 0.8
    max_new_tokens: int = 512
    n_samples: int = 20
    top_p: float = 0.95
    do_sample: bool = True

@dataclass
class BootstrapConfig:
    n_bootstrap: int = 10000
    alpha: float = 0.05

@dataclass
class FMDConfig:
    mypy_timeout: int = 30
    evalplus_timeout: int = 10
    category_priority: List[str] = ["syntax", "type", "functional", "success"]
    mypy_flags: List[str] = ["--ignore-missing-imports"]
    cleanup_temp_files: bool = True

@dataclass
class ExperimentConfig:
    hypothesis_id: str = "h-m1"
    n_problems: int = 164
    model: ModelConfig = ...
    generation: GenerationConfig = ...
    bootstrap: BootstrapConfig = ...
    thresholds: ThresholdConfig = ...
    fmd: FMDConfig = ...
    output: OutputConfig = ...
```

**Verified from**: `docs/youra_research/20260508_verifai/h-m1/code/config.py` (actual implementation)

---

## A-3: FMD Classification Config [Complexity: 11, Budget: 2 subtasks]

**Applied**: Standard mypy.api flags from h-m1 + extended strata for h-m2

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class H2FMDConfig:
    # Inherited from h-m1 FMDConfig (verified field names)
    mypy_timeout: int = 30
    evalplus_timeout: int = 10
    cleanup_temp_files: bool = True

    # h-m2 extended: additional mypy flag for cleaner output
    mypy_flags: List[str] = field(
        default_factory=lambda: ["--ignore-missing-imports", "--no-error-summary"]
    )

    # h-m2 FMD strata — maps h-m1 "type" category to "type_structural"
    strata: List[str] = field(
        default_factory=lambda: [
            "syntax",
            "type_structural",
            "constraint_logical",
            "functional_only",
            "pass"
        ]
    )

    # Minimum type_structural stratum size for C_score computation to proceed
    min_type_structural_problems: int = 10

    # Cross-validate sequential vs parallel FMD on N samples (Assumption A5 check)
    cross_validate_n: int = 10

    # Run FMD in parallel (order-independent signals)
    parallel_mode: bool = True
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | FMD stratum mapping | Map h-m1 "type" category to h-m2 "type_structural"; define 5-stratum labels |
| C-3-2 | Parallel/sequential validation | cross_validate_n=10 config for Assumption A5 sequential vs parallel cross-check |

---

## A-2: Baseline Pool Generation Config [Complexity: 10, Budget: 2 subtasks]

**Applied**: Standard PyTorch/HuggingFace generation defaults from h-e1/h-m1

```python
@dataclass
class H2BaselinePoolConfig:
    # Full 164-problem pool (h-m2 expands h-e1/h-m1 subsets)
    n_problems: int = 164
    n_samples_per_problem: int = 20

    # Seed formula for reproducible, controlled comparison with h-e1/h-m1
    # Non-standard: formula ensures unique seed per (problem, sample) pair
    seed_formula: str = "problem_idx * 100 + sample_idx"

    # Generation params (from h-m1 GenerationConfig — verified field names)
    generation_temperature: float = 0.8
    max_new_tokens: int = 512
    top_p: float = 0.95
    do_sample: bool = True

    # Checkpoint/resume every N problems
    checkpoint_interval: int = 10

    # Reuse existing pools to avoid regeneration
    reuse_h_e1_pool: bool = True
    h_e1_pool_path: str = ""       # abs path to h-e1/data/baseline_pool.jsonl
    h_m1_syncode_pool_path: str = ""  # abs path to h-m1/data/syncode_pool.jsonl
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Pool extension config | n_problems=164, seed_formula, reuse flags with paths |
| C-2-2 | Checkpoint/resume config | checkpoint_interval=10, progress file paths |

---

## A-11: Integration and End-to-End Test Config [Complexity: 11, Budget: 2 subtasks]

**Applied**: Standard pipeline orchestration pattern

```python
@dataclass
class H2IntegrationConfig:
    # Dry-run mode: test pipeline on small subset
    dry_run: bool = False
    dry_run_n_problems: int = 5

    # Ordered phase names for orchestration
    phases: List[str] = field(
        default_factory=lambda: [
            "phase_1_baseline_pool",
            "phase_2_fmd_classification",
            "phase_3_mypy_repair",
            "phase_4_syncode_pool",
            "phase_5_extract_transitions",
            "phase_6_c_score",
            "phase_7_z3_delta",
            "phase_8_visualization",
        ]
    )

    # Required output files checklist (validated post-run)
    required_output_files: List[str] = field(
        default_factory=lambda: [
            "baseline_pool.jsonl",
            "fmd_classification.jsonl",
            "mypy_repair_pool.jsonl",
            "syncode_pool.jsonl",
            "f_syncode_transitions.json",
            "f_mypy_transitions.json",
            "c_score_results.json",
            "z3_eligibility_delta.json",
            "metrics.json",
        ]
    )

    # GPU config — set CUDA_VISIBLE_DEVICES before launching
    cuda_visible_devices: str = "0"

    # Logging
    log_file: str = "h-m2/results/experiment.log"
    log_level: str = "INFO"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-11-1 | Dry-run config | dry_run_n_problems=5, phases list |
| C-11-2 | Output validation config | required_output_files checklist, CUDA_VISIBLE_DEVICES |

---

## A-9: Visualization Config [Complexity: 10, Budget: 1 subtask]

**Applied**: Standard matplotlib defaults; consistent with h-m1 for paper coherence

```python
@dataclass
class H2VisualizationConfig:
    figures_dir: str = "h-m2/figures/"

    # Figure filenames (6 required figures)
    gate_metrics_file: str = "gate_metrics.png"
    jaccard_heatmap_file: str = "jaccard_heatmap.png"
    fmd_distribution_file: str = "fmd_distribution.png"
    z3_eligibility_file: str = "z3_eligibility_comparison.png"
    repair_convergence_file: str = "repair_convergence.png"
    quintile_c_score_file: str = "quintile_c_score.png"

    # Display settings
    dpi: int = 150
    fig_width: float = 8.0
    fig_height: float = 6.0

    # Color scheme (consistent with h-m1 for paper coherence)
    color_syncode: str = "#2196F3"   # blue
    color_mypy: str = "#FF5722"      # orange-red
    color_baseline: str = "#9E9E9E"  # grey
    color_pass: str = "#4CAF50"      # green
    color_fail: str = "#F44336"      # red
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-9-1 | Figure config | 6 figure paths, DPI, size, color scheme |

---

## Top-Level H2ExperimentConfig

This is the primary config used by `run_experiment.py`.

```python
from dataclasses import dataclass, field
from typing import List


@dataclass
class ModelConfig:
    model_name: str = "codellama/CodeLlama-7b-hf"
    device_map: str = "auto"
    torch_dtype: str = "float16"


@dataclass
class MypyRepairConfig:
    max_rounds: int = 3
    repair_temperature: float = 0.2        # Non-standard: lower T for repair to stay close to error-corrected prompt (Madaan 2023)
    max_new_tokens: int = 512
    mypy_flags: List[str] = field(
        default_factory=lambda: ["--ignore-missing-imports", "--no-error-summary"]
    )
    mypy_timeout: int = 30
    mechanism_activated_threshold: float = 0.10  # Non-standard: min fraction of samples requiring repair


@dataclass
class CScoreConfig:
    n_bootstrap: int = 10000
    alpha: float = 0.0167              # Non-standard: Bonferroni correction 0.05/3 (3 pairwise comparisons)
    seed: int = 42
    min_stratum_size: int = 10


@dataclass
class Z3DeltaConfig:
    z3_timeout_seconds: int = 60
    arith_density_threshold: float = 0.1  # heuristic for z3_eligible flag


@dataclass
class H2FMDConfig:
    mypy_timeout: int = 30
    evalplus_timeout: int = 10
    cleanup_temp_files: bool = True
    mypy_flags: List[str] = field(
        default_factory=lambda: ["--ignore-missing-imports", "--no-error-summary"]
    )
    strata: List[str] = field(
        default_factory=lambda: [
            "syntax", "type_structural", "constraint_logical", "functional_only", "pass"
        ]
    )
    min_type_structural_problems: int = 10
    cross_validate_n: int = 10
    parallel_mode: bool = True


@dataclass
class H2BaselinePoolConfig:
    n_problems: int = 164
    n_samples_per_problem: int = 20
    seed_formula: str = "problem_idx * 100 + sample_idx"
    generation_temperature: float = 0.8
    max_new_tokens: int = 512
    top_p: float = 0.95
    do_sample: bool = True
    checkpoint_interval: int = 10
    reuse_h_e1_pool: bool = True
    h_e1_pool_path: str = ""
    h_m1_syncode_pool_path: str = ""


@dataclass
class H2IntegrationConfig:
    dry_run: bool = False
    dry_run_n_problems: int = 5
    phases: List[str] = field(
        default_factory=lambda: [
            "phase_1_baseline_pool",
            "phase_2_fmd_classification",
            "phase_3_mypy_repair",
            "phase_4_syncode_pool",
            "phase_5_extract_transitions",
            "phase_6_c_score",
            "phase_7_z3_delta",
            "phase_8_visualization",
        ]
    )
    required_output_files: List[str] = field(
        default_factory=lambda: [
            "baseline_pool.jsonl",
            "fmd_classification.jsonl",
            "mypy_repair_pool.jsonl",
            "syncode_pool.jsonl",
            "f_syncode_transitions.json",
            "f_mypy_transitions.json",
            "c_score_results.json",
            "z3_eligibility_delta.json",
            "metrics.json",
        ]
    )
    cuda_visible_devices: str = "0"
    log_file: str = "h-m2/results/experiment.log"
    log_level: str = "INFO"


@dataclass
class H2VisualizationConfig:
    figures_dir: str = "h-m2/figures/"
    gate_metrics_file: str = "gate_metrics.png"
    jaccard_heatmap_file: str = "jaccard_heatmap.png"
    fmd_distribution_file: str = "fmd_distribution.png"
    z3_eligibility_file: str = "z3_eligibility_comparison.png"
    repair_convergence_file: str = "repair_convergence.png"
    quintile_c_score_file: str = "quintile_c_score.png"
    dpi: int = 150
    fig_width: float = 8.0
    fig_height: float = 6.0
    color_syncode: str = "#2196F3"
    color_mypy: str = "#FF5722"
    color_baseline: str = "#9E9E9E"
    color_pass: str = "#4CAF50"
    color_fail: str = "#F44336"


@dataclass
class H2OutputConfig:
    data_dir: str = "h-m2/data/"
    results_dir: str = "h-m2/results/"
    figures_dir: str = "h-m2/figures/"
    baseline_pool_file: str = "baseline_pool.jsonl"
    syncode_pool_file: str = "syncode_pool.jsonl"
    mypy_repair_pool_file: str = "mypy_repair_pool.jsonl"
    fmd_classification_file: str = "fmd_classification.jsonl"
    f_syncode_transitions_file: str = "f_syncode_transitions.json"
    f_mypy_transitions_file: str = "f_mypy_transitions.json"
    c_score_results_file: str = "c_score_results.json"
    z3_eligibility_delta_file: str = "z3_eligibility_delta.json"
    metrics_file: str = "metrics.json"
    progress_baseline_file: str = "progress_baseline.json"
    progress_syncode_file: str = "progress_syncode.json"
    progress_repair_file: str = "progress_repair.json"


@dataclass
class H2ExperimentConfig:
    hypothesis_id: str = "h-m2"
    n_problems: int = 164
    n_samples: int = 20
    h_m1_code_dir: str = ""       # abs path to h-m1/code/ (for sys.path.insert)
    h_e1_baseline_pool: str = ""  # abs path to h-e1/data/baseline_pool.jsonl
    h_m1_syncode_pool: str = ""   # abs path to h-m1/data/syncode_pool.jsonl
    model: ModelConfig = field(default_factory=ModelConfig)
    repair: MypyRepairConfig = field(default_factory=MypyRepairConfig)
    c_score: CScoreConfig = field(default_factory=CScoreConfig)
    z3: Z3DeltaConfig = field(default_factory=Z3DeltaConfig)
    fmd: H2FMDConfig = field(default_factory=H2FMDConfig)
    baseline_pool: H2BaselinePoolConfig = field(default_factory=H2BaselinePoolConfig)
    integration: H2IntegrationConfig = field(default_factory=H2IntegrationConfig)
    visualization: H2VisualizationConfig = field(default_factory=H2VisualizationConfig)
    output: H2OutputConfig = field(default_factory=H2OutputConfig)
```

---

## Subtask Summary

| ID | Task | Subtask | Description |
|----|------|---------|-------------|
| C-3-1 | A-3 | FMD stratum mapping | 5-stratum labels, type→type_structural mapping |
| C-3-2 | A-3 | Parallel/sequential validation | cross_validate_n=10, parallel_mode flag |
| C-2-1 | A-2 | Pool extension config | n_problems=164, seed_formula, reuse flags |
| C-2-2 | A-2 | Checkpoint/resume config | checkpoint_interval=10, progress paths |
| C-11-1 | A-11 | Dry-run config | dry_run_n_problems=5, phases list |
| C-11-2 | A-11 | Output validation config | required_output_files, CUDA_VISIBLE_DEVICES |
| C-9-1 | A-9 | Figure config | 6 figure paths, DPI, size, color scheme |

**Total subtasks used: 7/7**
