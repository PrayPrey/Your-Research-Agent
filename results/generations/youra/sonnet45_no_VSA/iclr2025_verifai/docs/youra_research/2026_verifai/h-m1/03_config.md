# Configuration Document: H-M1 Information Gradient Validation

**Date:** 2026-07-11  
**Hypothesis:** H-M1 - Proof discharge rate scales monotonically with feedback richness  
**Type:** MECHANISM (Ablation Study)  
**Phase:** Phase 3 Implementation Planning  

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Config classes verified from base code (h-e1)  
**Config Files Found**: h-e1/code/src/*.py  
**Pattern Used**: Python dataclass (inheriting from h-e1 patterns)  

**Verified Fields from Base Code**:
- `IterativeRefinementLoop`: max_iterations, no_improvement_threshold
- `SpecificationGenerator`: model, api_key
- `FramaCVerifier`: timeout_per_obligation, provers
- `StructuredFeedback`: witness, structure, dependency (3 dimensions)

---

## Configuration Overview

**Applied**: Ablation experiment pattern with controlled variables (from Archon KB)

This ablation study extends h-e1 configuration with 4 feedback conditions controlling information richness. All other variables (LLM model, random seed, verifier settings) remain fixed across conditions.

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

The following configs are inherited from base hypothesis:

```python
# From: h-e1/code/src/refinement_loop.py (ACTUAL CODE)
class IterativeRefinementLoop:
    max_iterations: int = 10
    no_improvement_threshold: int = 3

# From: h-e1/code/src/llm_client.py (ACTUAL CODE)
class SpecificationGenerator:
    model: str = "claude-opus-4-5"
    # Uses Anthropic API key from environment

# From: h-e1/code/src/verifier.py (ACTUAL CODE)
class FramaCVerifier:
    timeout_per_obligation: int = 10  # seconds
    provers: List[str] = ["alt-ergo", "z3"]

# From: h-e1/code/src/feedback_parser.py (ACTUAL CODE)
@dataclass
class StructuredFeedback:
    witness: WitnessInstantiation
    structure: LogicalStructure
    dependency: DependencyPreservation
    natural_language: str
```

**Verified from**: `/workspace/TEST_verifai/docs/youra_research/h-e1/code/` (actual implementation)

---

## M-1: Feedback Ablator [Complexity: 9, Budget: 3]

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
from enum import Enum

class FeedbackCondition(Enum):
    FULL_STRUCTURED = "FullStructured"
    OBLIGATION_SLICE = "ObligationSlice"
    TAG_ONLY = "TagOnly"
    RAW_ERROR = "RawError"

@dataclass
class AblatorConfig:
    condition: FeedbackCondition
    preserve_natural_language: bool = True
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-1-1 | Condition Logic | Implement 4 ablation filters (3 complexity) |
| M-1-2 | Feedback Filtering | Filter StructuredFeedback dimensions (3 complexity) |
| M-1-3 | Integration Tests | Test all 4 conditions with mock data (3 complexity) |

---

## M-2: Ablation Experiment [Complexity: 12, Budget: 3]

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class AblationExperimentConfig:
    conditions: List[FeedbackCondition] = field(
        default_factory=lambda: [
            FeedbackCondition.FULL_STRUCTURED,
            FeedbackCondition.OBLIGATION_SLICE,
            FeedbackCondition.TAG_ONLY,
            FeedbackCondition.RAW_ERROR
        ]
    )
    
    # Control variables (MUST be same across all conditions)
    same_random_seed: int = 42
    same_compute_budget: bool = True
    same_verifier_config: bool = True
    
    # Checkpointing
    checkpoint_every_n_trials: int = 10
    checkpoint_dir: str = "docs/youra_research/h-m1/checkpoints"
    
    # Results storage
    results_dir: str = "docs/youra_research/h-m1/results/trials"
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-2-1 | Trial Runner | Execute program × condition trials (4 complexity) |
| M-2-2 | Result Aggregation | Aggregate per-condition statistics (4 complexity) |
| M-2-3 | Checkpointing | Save/resume trial-level checkpoints (4 complexity) |

---

## M-3: Statistical Analysis [Complexity: 16, Budget: 3]

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class StatisticalConfig:
    significance_level: float = 0.05
    
    # Monotonic test
    monotonic_ordering: List[FeedbackCondition] = field(
        default_factory=lambda: [
            FeedbackCondition.FULL_STRUCTURED,
            FeedbackCondition.OBLIGATION_SLICE,
            FeedbackCondition.TAG_ONLY,
            FeedbackCondition.RAW_ERROR
        ]
    )
    
    # Gap test threshold (percentage points)
    gap_threshold_pp: float = 10.0
    warn_threshold_pp: float = 5.0  # Warning zone
    
    # Regression (ordinal encoding: 1=Raw, 2=Tag, 3=Obl, 4=Full)
    regression_type: str = "linear_monotonic"
    
    # Compute fairness
    max_compute_delta_percent: float = 20.0  # Max 20% difference
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-3-1 | Monotonic & Gap Tests | Test ordering and adjacent gaps (7 complexity) |
| M-3-2 | Regression Analysis | Linear regression with significance test (6 complexity) |
| M-3-3 | Gate Logic | Combine all tests into gate decision (3 complexity) |

---

## M-4: Ablation Visualizer [Complexity: 11, Budget: 3]

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class VisualizationConfig:
    output_dir: str = "docs/youra_research/h-m1/figures"
    dpi: int = 300
    format: str = "png"
    
    # Color scheme (per condition)
    color_map: dict = field(default_factory=lambda: {
        FeedbackCondition.FULL_STRUCTURED: "#2ecc71",
        FeedbackCondition.OBLIGATION_SLICE: "#3498db",
        FeedbackCondition.TAG_ONLY: "#f39c12",
        FeedbackCondition.RAW_ERROR: "#e74c3c"
    })
    
    # Confidence interval
    confidence_level: float = 0.95
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-4-1 | Ordering & Heatmap Plots | Line plot + per-program heatmap (6 complexity) |
| M-4-2 | Regression Plot | Scatter with fitted line and CI bands (3 complexity) |
| M-4-3 | Budget Analysis Plot | Compute fairness visualization (2 complexity) |

---

## M-5: Results Documentor [Complexity: 8, Budget: 3]

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class DocumentationConfig:
    hypothesis_folder: str = "docs/youra_research/h-m1"
    validation_report_filename: str = "04_validation.md"
    verification_state_file: str = "../../verification_state.yaml"
    
    # Report sections (all required)
    include_sections: List[str] = field(default_factory=lambda: [
        "experiment_configuration",
        "per_condition_statistics",
        "monotonic_ordering_test",
        "adjacent_gap_test",
        "regression_analysis",
        "compute_fairness_check",
        "gate_decision"
    ])
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-5-1 | Report Template | Generate 04_validation.md structure (3 complexity) |
| M-5-2 | State Update | Update verification_state.yaml (2 complexity) |
| M-5-3 | Figure Integration | Embed all plots in report (3 complexity) |

---

## M-6: Dataset Expansion [Complexity: 7, Budget: 3]

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class DatasetConfig:
    # Dataset source
    repository_url: str = "https://github.com/fraunhoferfokus/acsl-by-example"
    cache_dir: str = ".cache/datasets/acsl-by-example"
    
    # Selection criteria
    num_programs: int = 30  # Minimum for statistical power
    selection_strategy: str = "diverse"
    
    # Program filters
    min_lines: int = 10
    max_lines: int = 100
    min_proof_obligations: int = 5
    max_proof_obligations: int = 20
    
    # Preprocessing
    strip_acsl_annotations: bool = True
    preserve_comments: bool = False
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-6-1 | Repository Clone & Selection | Clone repo and select 30 programs (4 complexity) |
| M-6-2 | Validation & Preprocessing | Strip ACSL, validate with Frama-C (2 complexity) |
| M-6-3 | Gold Standard Storage | Save original annotations for comparison (1 complexity) |

---

## M-7: Integration Runner [Complexity: 13, Budget: 3]

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class AblationRunnerConfig:
    # Experiment metadata
    experiment_name: str = "h-m1-information-gradient"
    hypothesis_type: str = "MECHANISM"
    gate_type: str = "MUST_WORK"
    
    # Paths
    config_path: Path = Path("docs/youra_research/h-m1/config/ablation_config.yaml")
    output_dir: Path = Path("docs/youra_research/h-m1")
    
    # Component configs (composed)
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    ablation: AblationExperimentConfig = field(default_factory=AblationExperimentConfig)
    statistics: StatisticalConfig = field(default_factory=StatisticalConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    documentation: DocumentationConfig = field(default_factory=DocumentationConfig)
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "docs/youra_research/h-m1/logs/experiment.log"
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-7-1 | Orchestration | End-to-end pipeline (dataset → stats → docs) (4 complexity) |
| M-7-2 | Error Handling | Graceful recovery, retry logic, logging (4 complexity) |
| M-7-3 | Results Pipeline | Collect all outputs, generate final report (5 complexity) |

---

## Configuration Rationale

### Non-Standard Values

**num_programs: 30** (vs 10 in h-e1)
- Ablation study requires higher N for statistical power across 4 conditions
- Minimum for valid regression analysis (30 programs × 4 conditions = 120 trials)

**gap_threshold_pp: 10.0** (percentage points)
- Based on hypothesis requirement: adjacent conditions must differ by ≥10pp
- Stricter than typical 5pp threshold to demonstrate strong gradient

**checkpoint_every_n_trials: 10** (vs every iteration in h-e1)
- Trial-level granularity (not iteration-level) for ablation recovery
- 10 trials = ~2.5 programs, reasonable checkpoint frequency

---

## Environment Variables

Required for experiment execution:

```bash
# Anthropic API key (inherited from h-e1)
export ANTHROPIC_API_KEY="sk-ant-..."

# Optional: OpenRouter fallback
# export OPENROUTER_API_KEY="sk-or-..."

# Logging
export LOG_LEVEL="INFO"

# Cache directories
export HF_HOME=".cache/huggingface"
```

---

## Cost Estimates

### LLM API Costs

Based on h-e1 actual costs ($0.036/program):

| Item | Unit Cost | Quantity | Total |
|------|-----------|----------|-------|
| 30 programs × 4 conditions | $0.036/program-condition | 120 | $4.32 |
| Safety margin (1.5x) | | | $6.48 |

**Total Estimated Cost:** $6.48 USD

### Compute Budget

- **Verifier execution:** Free (Frama-C/WP)
- **Storage:** ~500MB (checkpoints + results)
- **Runtime:** 6-8 hours (120 trials × 4 min avg)

---

## Resource Budgets

### Time Budget

| Phase | Estimated Time | Notes |
|-------|----------------|-------|
| Dataset expansion (30 programs) | 30 min | One-time setup |
| Per-trial synthesis (avg) | 4 min | Same as h-e1 |
| Total experiment runtime | 8 hours | 120 trials × 4 min |

### Storage Budget

| Component | Size | Notes |
|-----------|------|-------|
| Checkpoints | 200MB | Trial-level saves |
| Results (JSON) | 50MB | Per-trial + aggregates |
| Figures | 10MB | 4 plots at 300 DPI |
| Logs | 100MB | Iteration logs |
| **Total** | **360MB** | |

---

## Self-Validation

### Quick Checks
- [x] ONE format only (Python dataclass)
- [x] No ASCII diagrams
- [x] No KB search logs (noted "Applied: Ablation experiment pattern")
- [x] Rationale only for non-standard values (3 items)
- [x] Subtask count within budget (3 per task)
- [x] Total length < 400 lines
- [x] "Codebase Analysis (Serena)" section included

### Base Hypothesis Checks
- [x] Read actual config classes from h-e1/code/
- [x] Field names verified from actual implementation
- [x] Default values match actual base config
- [x] Inherited Configuration section included

---

## Summary

This configuration provides **copy-paste ready** ablation setup for H-M1:

1. **Inherits h-e1 configs** (IterativeRefinementLoop, SpecificationGenerator, FramaCVerifier)
2. **Adds ablation-specific configs** (4 feedback conditions, statistical tests)
3. **Per-task dataclasses** for all 7 Epic tasks
4. **Cost estimate**: $6.48 (4 conditions × 30 programs)
5. **Resource estimate**: 8 hours runtime, 360MB storage

**Phase 4 Coder**: Use dataclass configs as-is. All values are research-validated or inherited from h-e1.

**Key Difference from h-e1**: This is a MECHANISM hypothesis testing information gradient, not an EXISTENCE PoC. No hyperparameter tuning, but needs rigorous statistical analysis across 4 controlled conditions.

**Reproducibility**: Same random seed (42), same LLM model, same verifier settings across all conditions. Only variable is feedback richness.
