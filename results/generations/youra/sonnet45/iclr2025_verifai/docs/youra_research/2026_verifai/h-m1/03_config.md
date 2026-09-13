# Configuration Specification: h-m1
# Hypothesis: Static Analysis Cascade Routing Mechanism

**Date:** 2026-03-18
**Hypothesis Type:** MECHANISM
**Author:** Claude (Configuration Specialist)
**Applied:** PyTorch DL config patterns (Archon KB)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Config classes verified from h-e1 actual implementation
**Config Files Found:** /home/anonymous/YouRA_results_new_4_sonnet45/TEST_verifai/docs/youra_research/20260318_verifai/h-e1/code/run_experiment.py
**Pattern Used:** dataclass (embedded in monolithic script)

---

## Inherited Configuration (Base Hypothesis)

### Config Class (From Actual H-E1 Code)

The following configuration is inherited from h-e1 actual implementation:

```python
# From: h-e1/code/run_experiment.py (lines 32-48)
@dataclass
class ExperimentConfig:
    """Configuration for H-E1 experiment"""
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

**Verified from:** h-e1/code/run_experiment.py (actual implementation)

---

## M-1: Setup Infrastructure [Complexity: 5, Budget: 2]

**Applied:** Standard PyTorch project setup

### Configuration (Python Dataclass)

```python
from pathlib import Path

@dataclass
class ProjectConfig:
    """Project structure and environment settings"""
    project_root: Path = Path(__file__).parent.parent
    code_dir: Path = project_root / "code"
    output_dir: Path = project_root / "outputs"
    figures_dir: Path = project_root / "figures"
    h_e1_path: Path = project_root.parent / "20260318_verifai" / "h-e1"
    # GPU selection: Set CUDA_VISIBLE_DEVICES before running
    required_cuda: bool = True
    min_vram_gb: int = 16
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-1-1 | Environment setup | Install dependencies, GPU check, create directories |
| M-1-2 | Path validation | Verify h-e1 paths exist, create output directories |

---

## M-2: Qualified Task Loader [Complexity: 7, Budget: 2]

**Applied:** H-E1 data reuse pattern

### Configuration (Python Dataclass)

```python
@dataclass
class TaskLoaderConfig:
    """Configuration for loading N=35 qualified tasks from h-e1"""
    h_e1_validation_path: str = "../20260318_verifai/h-e1/04_validation.md"
    expected_task_count: int = 35
    verify_dual_sensitivity: bool = True
    use_evalplus: bool = True
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-2-1 | Parse h-e1 validation | Extract N=35 task IDs from validation markdown |
| M-2-2 | Load task metadata | Load prompts, entry points, tests from HumanEval+ |

---

## M-3: Cascade Feedback Router [Complexity: 14, Budget: 2]

**Applied:** LLMLOOP sequential feedback pattern

### Configuration (Python Dataclass)

```python
@dataclass
class CascadeRouterConfig:
    """Core cascade routing mechanism settings"""
    max_retries: int = 5
    mypy_first: bool = True  # Static analysis before execution
    skip_pytest_on_mypy_fail: bool = True  # Conditional gating
    feedback_format: str = "sequential"  # Single-source per iteration
    # Inherited from h-e1: temperature, top_p, top_k, max_length
    # Inherited from h-e1: mypy_timeout=10, pytest_timeout=120
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-3-1 | Cascade loop implementation | Mypy-first sequential routing with conditional gating |
| M-3-2 | Feedback formatting | Convert mypy/pytest errors to LLM prompts |

---

## M-4: Aggregation Baseline [Complexity: 10, Budget: 2]

**Applied:** LLMLOOP aggregation feedback pattern

### Configuration (Python Dataclass)

```python
@dataclass
class AggregationRouterConfig:
    """Baseline aggregation routing settings"""
    max_retries: int = 5
    run_both_always: bool = True  # Both mypy AND pytest every iteration
    feedback_format: str = "aggregated"  # Concatenate both sources
    # Inherited from h-e1: temperature, top_p, top_k, max_length
    # Inherited from h-e1: mypy_timeout=10, pytest_timeout=120
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-4-1 | Aggregation loop implementation | Both-source feedback every iteration |
| M-4-2 | Feedback concatenation | Combine mypy + pytest errors in single prompt |

---

## M-5: Mypy Integration [Complexity: 8, Budget: 2]

**Applied:** LLMLOOP static analysis integration

### Configuration (Python Dataclass)

```python
@dataclass
class MypyConfig:
    """Static analysis verification settings"""
    strict_mode: bool = True  # --strict flag
    timeout: int = 10  # seconds (inherited from h-e1)
    capture_error_types: bool = True  # Parse error codes
    json_output: bool = False  # Use text parsing for simplicity
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-5-1 | Mypy wrapper | Subprocess runner with timeout and error parsing |
| M-5-2 | Error type extraction | Parse error codes (type-arg, arg-type, etc.) |

---

## M-6: Pytest Integration [Complexity: 9, Budget: 2]

**Applied:** LLMLOOP execution testing integration

### Configuration (Python Dataclass)

```python
@dataclass
class PytestConfig:
    """Execution testing settings"""
    timeout: int = 120  # seconds (inherited from h-e1)
    use_evalplus_tests: bool = True  # 80+ tests per task
    verbose: bool = True  # Capture failure details
    capture_output: bool = True  # Redirect stdout/stderr
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-6-1 | Pytest wrapper | Subprocess runner with HumanEval+ tests |
| M-6-2 | Failure parsing | Extract failure messages for feedback |

---

## M-7: Detection Rate Analysis [Complexity: 11, Budget: 2]

**Applied:** Gate validation metrics pattern

### Configuration (Python Dataclass)

```python
@dataclass
class AnalysisConfig:
    """Error detection rate analysis settings"""
    target_detection_rate: float = 30.0  # MUST_WORK gate threshold
    gate_metric: str = "mypy_error_rate"
    calculate_per_task: bool = True
    # Detection rate = (mypy error iterations) / (total iterations)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-7-1 | Metrics computation | Calculate detection rates per task and overall |
| M-7-2 | Gate validation | Compare against 30% threshold, generate report |

---

## M-8: Visualization [Complexity: 9, Budget: 2]

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
    figures_required: list = None  # Set in __post_init__

    def __post_init__(self):
        self.figures_required = [
            "gate_metrics.png",
            "error_breakdown.png",
            "iteration_comparison.png",
            "execution_cost.png",
            "task_heatmap.png"
        ]
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-8-1 | Gate + breakdown plots | Figure 1-2: gate metrics, error distribution |
| M-8-2 | Comparison + heatmap | Figure 3-5: cascade vs aggregation, cost, heatmap |

---

## Extended Configuration (Current Hypothesis)

### Complete Experiment Configuration

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ExperimentConfig:
    """Complete configuration for h-m1 cascade routing experiment"""

    # Inherited from h-e1 (VERIFIED from actual code)
    model_name: str = "codellama/CodeLlama-7b-hf"
    k_samples: int = 20
    temperature: float = 0.8
    top_p: float = 0.95
    top_k: int = 40
    max_length: int = 256
    mypy_timeout: int = 10
    pytest_timeout: int = 120
    variance_threshold: float = 1.0
    seed: int = 42
    device: str = "auto"
    output_dir: Path = Path("./outputs")
    figures_dir: Path = Path("./figures")

    # New fields for h-m1
    h_e1_validation_path: str = "../20260318_verifai/h-e1/04_validation.md"
    expected_qualified_tasks: int = 35
    max_retries: int = 5
    target_detection_rate: float = 30.0
    use_cascade_routing: bool = True
    use_aggregation_baseline: bool = True

    # Routing strategies
    cascade_mypy_first: bool = True
    cascade_skip_pytest_on_mypy_fail: bool = True
    aggregation_run_both_always: bool = True
```

---

## Self-Validation

### Quick Checks
- [x] ONE format only (Dataclass - no hardcoded dict)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale only for non-standard values (none needed - all standard)
- [x] Subtask count within budget (all tasks: 2/2)
- [x] Total length < 400 lines (currently ~280 lines)
- [x] "Codebase Analysis (Serena)" section included

### Base Hypothesis Checks
- [x] Read actual config classes from h-e1/code/run_experiment.py
- [x] Field names verified from actual implementation (lines 32-48)
- [x] Default values match actual base config
- [x] Inherited Configuration section included

---

**Generated by Phase 3 Configuration Agent**
**Source:** 03_architecture.md, 03_prd.md, h-e1/code/run_experiment.py
**Next:** Phase 4 - Implementation (Coder Agent)
