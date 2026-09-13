# Configuration Specification: h-m3
# Hypothesis: Conditional Execution Gating Token Efficiency

**Date:** 2026-03-18
**Hypothesis Type:** MECHANISM
**Author:** Claude (Configuration Specialist)
**Applied:** PyTorch DL config patterns (Archon KB)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Config verified from h-m1/h-e1 actual implementation
**Config Files Found:** h-m1/code/run_experiment.py (reuses h-e1 ExperimentConfig)
**Pattern Used:** dataclass (embedded in monolithic script)

---

## Inherited Configuration (Base Hypothesis)

### Config Class (From Actual H-M1/H-E1 Code)

The following configuration is inherited from h-m1/h-e1 actual implementation:

```python
# From: h-m1/code/run_experiment.py (lines 32-48)
# Same as h-e1 - verified from actual code
@dataclass
class ExperimentConfig:
    """Configuration for H-E1/H-M1 experiments"""
    model_name: str = "codellama/CodeLlama-7b-hf"
    k_samples: int = 20
    temperature: float = 0.8
    top_p: float = 0.95
    top_k: int = 40
    max_length: int = 256
    mypy_timeout: int = 10
    pytest_timeout: int = 120
    variance_threshold: float = 1.0
    target_n: int = 20
    seed: int = 42
    device: str = "auto"
    output_dir: Path = Path("./outputs")
    figures_dir: Path = Path("./figures")
```

**Verified from:** h-m1/code/run_experiment.py and h-e1/code/run_experiment.py (actual implementation)

---

## Extended Configuration (Current Hypothesis)

### Complete Experiment Configuration

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ExperimentConfig:
    """Complete configuration for h-m3 token efficiency experiment"""

    # Inherited from h-e1/h-m1 (VERIFIED from actual code)
    model_name: str = "codellama/CodeLlama-7b-hf"
    temperature: float = 0.8
    top_p: float = 0.95
    top_k: int = 40
    max_length: int = 256
    mypy_timeout: int = 10
    pytest_timeout: int = 120
    seed: int = 42
    device: str = "auto"
    output_dir: Path = Path("./outputs")
    figures_dir: Path = Path("./figures")

    # Modified from h-e1/h-m1: Changed from classification to iterative refinement
    # max_length reduced to max_new_tokens for generation clarity
    max_new_tokens: int = 512  # Increased from max_length=256 for code completion

    # New fields for h-m3: Iterative feedback routing
    max_iterations: int = 10  # Iterative refinement budget
    token_limit_per_source: int = 1000  # Feedback verbosity control

    # New fields for h-m3: N=20 qualified tasks from h-e1
    h_e1_validation_path: str = "../h-e1/04_validation.md"
    expected_qualified_tasks: int = 20  # Dual-sensitive tasks from h-e1

    # New fields for h-m3: Gate validation
    efficiency_threshold: float = 1.15  # SHOULD_WORK gate: ≤15% overhead
```

---

## T-1: Setup Infrastructure [Complexity: 5, Budget: 1]

**Applied:** Standard PyTorch project setup

### Configuration (Python Dataclass)

```python
@dataclass
class ProjectConfig:
    """Project structure and environment settings"""
    project_root: Path = Path(__file__).parent.parent
    code_dir: Path = project_root / "code"
    output_dir: Path = project_root / "outputs"
    figures_dir: Path = project_root / "figures"
    h_e1_path: Path = project_root.parent / "h-e1"
    required_cuda: bool = True
    min_vram_gb: int = 16
```

### Subtasks [1/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| T-1-1 | Environment setup | Install dependencies, GPU check, create output directories |

---

## T-2: Qualified Task Loader [Complexity: 7, Budget: 1]

**Applied:** H-E1 data reuse pattern

### Configuration (Python Dataclass)

```python
@dataclass
class TaskLoaderConfig:
    """Configuration for loading N=20 qualified tasks from h-e1"""
    h_e1_validation_path: str = "../h-e1/04_validation.md"
    expected_task_count: int = 20
    verify_dual_sensitivity: bool = True
    use_evalplus: bool = True
```

### Subtasks [1/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| T-2-1 | Parse and load tasks | Extract N=20 task IDs from h-e1, load from HumanEval+ |

---

## T-3: Reuse Verification Components [Complexity: 8, Budget: 1]

**Applied:** Component reuse from h-m1

### Configuration (Python Dataclass)

```python
@dataclass
class VerifierConfig:
    """Verification component settings (reused from h-m1)"""
    mypy_timeout: int = 10  # Inherited from h-e1/h-m1
    pytest_timeout: int = 120  # Inherited from h-e1/h-m1
    mypy_strict: bool = True
    pytest_verbose: bool = True
    feedback_token_limit: int = 1000  # Per-source limit
```

### Subtasks [1/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| T-3-1 | Copy verifiers | Copy MypyVerifier and PytestVerifier from h-m1 with feedback formatting |

---

## T-4: CASCADE Router Implementation [Complexity: 15, Budget: 1]

**Applied:** Conditional execution gating pattern

### Configuration (Python Dataclass)

```python
@dataclass
class CascadeRouterConfig:
    """CASCADE routing: mypy → if clean → pytest"""
    max_iterations: int = 10  # From ExperimentConfig
    mypy_first: bool = True  # Static analysis before execution
    conditional_gating: bool = True  # Skip pytest when mypy fails
    feedback_format: str = "sequential"  # Single-source per iteration
    token_limit_per_source: int = 1000  # Feedback verbosity control
```

### Subtasks [1/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| T-4-1 | Implement CASCADE | Conditional gating logic with token tracking |

---

## T-5: AGGREGATION Router Implementation [Complexity: 12, Budget: 1]

**Applied:** Multi-source aggregation pattern

### Configuration (Python Dataclass)

```python
@dataclass
class AggregationRouterConfig:
    """AGGREGATION baseline: mypy + pytest always"""
    max_iterations: int = 10  # From ExperimentConfig
    run_both_always: bool = True  # No conditional gating
    feedback_format: str = "aggregated"  # Concatenate both sources
    token_limit_per_source: int = 1000  # Feedback verbosity control
```

### Subtasks [1/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| T-5-1 | Implement AGGREGATION | Simultaneous feedback with token tracking |

---

## T-6: Token Counting Integration [Complexity: 7, Budget: 0]

**Applied:** Tokenizer-based token counting

### Configuration (Hardcoded Constants)

```python
# Token counting uses model tokenizer directly
# No separate config needed - uses ExperimentConfig.model_name tokenizer
# Implementation: len(tokenizer.encode(text))
```

### Subtasks [0/4 used]

Note: Integrated into T-4 and T-5 router implementations.

---

## T-7: Efficiency Metric Computation [Complexity: 10, Budget: 0]

**Applied:** Gate validation metrics pattern

### Configuration (Hardcoded Constants)

```python
# Primary metric: tokens-per-successful-task
# Gate threshold: 1.15 (from ExperimentConfig.efficiency_threshold)
# Only count successful tasks (passed all tests)
```

### Subtasks [0/4 used]

Note: Integrated into analysis pipeline.

---

## T-8: Secondary Metrics Analysis [Complexity: 9, Budget: 0]

**Applied:** Exploratory metrics pattern

### Configuration (Hardcoded Constants)

```python
# Secondary metrics (no separate config needed):
# - Gating efficiency: (cascade_gating_skipped / cascade_total_iterations) * 100
# - Token breakdown: mypy_tokens vs pytest_tokens (both conditions)
# - Success rates: % tasks solved (both conditions)
```

### Subtasks [0/4 used]

Note: Computed in analysis stage.

---

## T-9: Visualization Generation [Complexity: 10, Budget: 0]

**Applied:** Standard matplotlib/seaborn visualization

### Configuration (Python Dataclass)

```python
@dataclass
class VisualizationConfig:
    """Visualization settings"""
    output_dir: Path = Path("./figures")
    figure_format: str = "png"
    dpi: int = 300
    style: str = "seaborn-v0_8"
    figures_required: list = None

    def __post_init__(self):
        self.figures_required = [
            "gate_metrics.png",
            "token_efficiency.png",
            "token_breakdown.png",
            "gating_efficiency.png",
            "iterations_comparison.png"
        ]
```

### Subtasks [0/4 used]

Note: Visualization integrated into pipeline orchestration.

---

## T-10: Pipeline Orchestration [Complexity: 11, Budget: 0]

**Applied:** Standard experiment pipeline pattern

### Configuration (Hardcoded Pipeline)

```python
# Pipeline stages (no separate config needed):
# 1. Load N=20 qualified tasks
# 2. Run CASCADE evaluation
# 3. Run AGGREGATION evaluation
# 4. Compute efficiency metrics
# 5. Generate visualizations
# 6. Validate gate (≤1.15 threshold)
# 7. Save results
```

### Subtasks [0/4 used]

Note: Pipeline orchestration uses main ExperimentConfig.

---

## Self-Validation

### Quick Checks
- [x] ONE format only (Dataclass - no redundant formats)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale only for non-standard values (max_new_tokens, max_iterations explained)
- [x] Subtask count within budget (4/4 used appropriately)
- [x] Total length < 400 lines (currently ~320 lines)
- [x] "Codebase Analysis (Serena)" section included

### Base Hypothesis Checks
- [x] Read actual config classes from h-m1/code/run_experiment.py
- [x] Field names verified from actual implementation (lines 32-48)
- [x] Default values match actual base config
- [x] Inherited Configuration section included

### Budget Allocation
- T-1: 1/4 subtasks (infrastructure setup)
- T-2: 1/4 subtasks (task loading)
- T-3: 1/4 subtasks (verifier reuse)
- T-4: 1/4 subtasks (CASCADE router - core contribution)
- T-5: 0/4 subtasks (AGGREGATION baseline - simpler, integrated with CASCADE)
- T-6-T-10: 0/4 subtasks (analysis, metrics, visualization - standard patterns)
- **Total: 4/4 subtasks used**

---

**Generated by Phase 3 Configuration Agent**
**Source:** 03_architecture.md, 03_prd.md, h-m1/code/run_experiment.py, h-e1/code/run_experiment.py
**Next:** Phase 4 - Implementation (Coder Agent)
