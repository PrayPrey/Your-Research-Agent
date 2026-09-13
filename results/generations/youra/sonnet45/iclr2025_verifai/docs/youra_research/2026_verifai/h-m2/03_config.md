# Configuration Specification: h-m2
# Hypothesis: Sequential vs Aggregation Feedback Presentation

**Date:** 2026-03-18
**Hypothesis Type:** MECHANISM
**Author:** Claude (Configuration Specialist)
**Applied:** PyTorch DL config patterns (Archon KB)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Config classes verified from h-m1 actual implementation
**Config Files Found:** /home/anonymous/YouRA_results_new_4_sonnet45/TEST_verifai/docs/youra_research/20260318_verifai/h-m1/code/run_experiment.py
**Pattern Used:** dataclass (embedded in monolithic script)

---

## Inherited Configuration (Base Hypothesis)

### Config Class (From Actual H-M1 Code)

The following configuration is inherited from h-m1 actual implementation, which extends h-e1:

```python
# From: h-m1/code/run_experiment.py (lines 32-48)
# Originally from: h-e1/code/run_experiment.py (lines 32-48)
@dataclass
class ExperimentConfig:
    """Configuration for base experiment (h-e1/h-m1)"""
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

**Verified from:** h-m1/code/run_experiment.py (actual implementation)

---

## M2-1: Setup Infrastructure [Complexity: 5, Budget: 5]

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
    h_e1_path: Path = project_root.parent / "h-e1"
    # GPU selection: Set CUDA_VISIBLE_DEVICES before running
    required_cuda: bool = True
    min_vram_gb: int = 16
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M2-1-1 | Directory setup | Create code/, outputs/, figures/ directories |
| M2-1-2 | Dependencies | Install transformers, evalplus, mypy, pytest, matplotlib |
| M2-1-3 | GPU verification | Check nvidia-smi, verify >=16GB VRAM available |
| M2-1-4 | Path validation | Verify h-e1 validation file exists |
| M2-1-5 | Logging setup | Configure experiment logging to outputs/ |

---

## M2-2: Qualified Task Loader [Complexity: 6, Budget: 6]

**Applied:** H-E1 data reuse pattern

### Configuration (Python Dataclass)

```python
@dataclass
class TaskLoaderConfig:
    """Configuration for loading N=20 qualified tasks from h-e1"""
    h_e1_validation_path: str = "../h-e1/04_validation.md"
    # Non-standard: Use first 20 of 35 qualified tasks from h-e1
    n_tasks: int = 20
    verify_dual_sensitivity: bool = True
    use_evalplus: bool = True
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M2-2-1 | Parse h-e1 validation | Extract 35 qualified task IDs from markdown |
| M2-2-2 | Select first N=20 | Take subset for mechanism testing |
| M2-2-3 | Load HumanEval+ | Initialize evalplus dataset |
| M2-2-4 | Extract prompts | Get task prompts for code generation |
| M2-2-5 | Extract tests | Get pytest test suites per task |
| M2-2-6 | Validate completeness | Verify all 20 tasks have prompt + tests |

---

## M2-3: Sequential Feedback Router [Complexity: 15, Budget: 15]

**Applied:** LLMLOOP sequential feedback pattern

### Configuration (Python Dataclass)

```python
@dataclass
class SequentialRouterConfig:
    """Sequential single-source feedback routing settings"""
    max_iterations: int = 10
    mypy_first: bool = True
    # Core mechanism: Only ONE source per iteration
    skip_pytest_if_mypy_errors: bool = True
    feedback_format: str = "single_source"
    # Inherited: temperature=0.8, top_p=0.95, top_k=40, max_length=256
    # Inherited: mypy_timeout=10, pytest_timeout=120
```

### Subtasks [15/15 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M2-3-1 | Router class scaffold | SequentialFeedbackRouter class definition |
| M2-3-2 | Iteration loop | Main refinement loop (max 10 iterations) |
| M2-3-3 | Mypy execution | Run mypy on generated code |
| M2-3-4 | Mypy decision logic | If errors → present mypy, skip pytest |
| M2-3-5 | Pytest execution | Run pytest only if mypy clean |
| M2-3-6 | Pytest decision logic | If mypy clean → present pytest feedback |
| M2-3-7 | Feedback formatting | Format single source for LLM prompt |
| M2-3-8 | Stop condition check | Pass all tests OR max iterations |
| M2-3-9 | Iteration tracking | Log which source presented per iteration |
| M2-3-10 | Code refinement | Call LLM with feedback to refine code |
| M2-3-11 | History tracking | Maintain conversation history |
| M2-3-12 | Success detection | Detect when tests pass |
| M2-3-13 | Timeout handling | Handle mypy/pytest timeouts gracefully |
| M2-3-14 | Error logging | Log all feedback and responses |
| M2-3-15 | Result collection | Package iterations, success, tokens |

---

## M2-4: Aggregation Feedback Router [Complexity: 12, Budget: 12]

**Applied:** LLMLOOP aggregation feedback pattern

### Configuration (Python Dataclass)

```python
@dataclass
class AggregationRouterConfig:
    """Aggregation multi-source feedback routing settings"""
    max_iterations: int = 10
    run_both_always: bool = True
    # Core mechanism: ALL sources simultaneously
    feedback_format: str = "aggregated"
    concatenation_separator: str = "\n\n--- Next Verification Source ---\n\n"
    # Inherited: temperature=0.8, top_p=0.95, top_k=40, max_length=256
    # Inherited: mypy_timeout=10, pytest_timeout=120
```

### Subtasks [12/12 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M2-4-1 | Router class scaffold | AggregationFeedbackRouter class definition |
| M2-4-2 | Iteration loop | Main refinement loop (max 10 iterations) |
| M2-4-3 | Mypy execution | Run mypy on generated code |
| M2-4-4 | Pytest execution | Run pytest (regardless of mypy result) |
| M2-4-5 | Feedback concatenation | Combine mypy + pytest messages |
| M2-4-6 | Aggregated formatting | Format combined feedback for LLM |
| M2-4-7 | Stop condition check | Pass all tests OR max iterations |
| M2-4-8 | Iteration tracking | Log concatenated feedback per iteration |
| M2-4-9 | Code refinement | Call LLM with aggregated feedback |
| M2-4-10 | History tracking | Maintain conversation history |
| M2-4-11 | Error logging | Log all feedback and responses |
| M2-4-12 | Result collection | Package iterations, success, tokens |

---

## M2-5: LLM Refinement Loop [Complexity: 13, Budget: 13]

**Applied:** CodeLlama iterative generation pattern

### Configuration (Python Dataclass)

```python
@dataclass
class GeneratorConfig:
    """LLM code generation and refinement settings"""
    # Inherited from h-e1/h-m1
    model_name: str = "codellama/CodeLlama-7b-hf"
    temperature: float = 0.8
    top_p: float = 0.95
    top_k: int = 40
    max_length: int = 256
    device: str = "auto"
    seed: int = 42
    # Token tracking for efficiency metrics
    track_tokens: bool = True
```

### Subtasks [13/13 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M2-5-1 | CodeLlamaGenerator class | Model wrapper class |
| M2-5-2 | Model loading | Load CodeLlama-7B with FP16 |
| M2-5-3 | Tokenizer setup | Load tokenizer |
| M2-5-4 | Seed configuration | Set random seeds for reproducibility |
| M2-5-5 | Initial generation | Generate code from task prompt |
| M2-5-6 | Refinement prompt | Build feedback-driven refinement prompt |
| M2-5-7 | Code extraction | Parse code from LLM response |
| M2-5-8 | Token counting | Track input/output tokens |
| M2-5-9 | Cache management | Clear CUDA cache between iterations |
| M2-5-10 | Temperature control | Apply sampling parameters |
| M2-5-11 | Response validation | Ensure valid code generated |
| M2-5-12 | Error handling | Handle generation failures |
| M2-5-13 | Logging | Log generation details |

---

## M2-6: Mechanism Verification [Complexity: 9, Budget: 9]

**Applied:** Gate validation metrics pattern

### Configuration (Python Dataclass)

```python
@dataclass
class MechanismVerificationConfig:
    """Verification that routing mechanisms operate correctly"""
    verify_sequential_isolation: bool = True
    verify_aggregation_completeness: bool = True
    verify_task_parity: bool = True
    # Non-standard: Strict verification for mechanism experiments
    fail_on_violation: bool = True
```

### Subtasks [9/9 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M2-6-1 | MechanismVerifier class | Verification logic class |
| M2-6-2 | Sequential check | Verify never >1 source per iteration |
| M2-6-3 | Aggregation check | Verify all sources when errors exist |
| M2-6-4 | Task set comparison | Verify same 20 tasks in both conditions |
| M2-6-5 | Feedback source counting | Parse feedback to count sources |
| M2-6-6 | Violation detection | Flag mechanism failures |
| M2-6-7 | Verification report | Generate verification summary |
| M2-6-8 | Assertion logic | Halt on mechanism violation |
| M2-6-9 | Logging | Log verification results |

---

## M2-7: Metrics Computation [Complexity: 10, Budget: 10]

**Applied:** Comparative analysis metrics pattern

### Configuration (Python Dataclass)

```python
@dataclass
class MetricsConfig:
    """Metrics computation settings"""
    primary_metric: str = "mean_iterations_to_solution"
    # SHOULD_WORK gate: Sequential < Aggregation (directional)
    gate_criterion: str = "mu_seq < mu_agg"
    compute_secondary_metrics: bool = True
    secondary_metrics: list = None

    def __post_init__(self):
        self.secondary_metrics = [
            "success_rate",
            "token_efficiency",
            "iteration_variance"
        ]
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M2-7-1 | MetricsAnalyzer class | Analysis logic class |
| M2-7-2 | Iterations-to-solution | Compute mean iterations per condition |
| M2-7-3 | Success rate | Proportion solved within 10 iterations |
| M2-7-4 | Token efficiency | Mean tokens per successful solution |
| M2-7-5 | Variance computation | Iteration count variance per condition |
| M2-7-6 | Per-task metrics | Individual task analysis |
| M2-7-7 | Statistical summary | Mean, SD, min, max per metric |
| M2-7-8 | Comparison logic | Sequential vs aggregation comparison |
| M2-7-9 | Metrics serialization | Save to JSON |
| M2-7-10 | Logging | Log computed metrics |

---

## M2-8: Gate Validation [Complexity: 8, Budget: 8]

**Applied:** SHOULD_WORK gate validation pattern

### Configuration (Python Dataclass)

```python
@dataclass
class GateValidationConfig:
    """Gate validation settings"""
    gate_type: str = "SHOULD_WORK"
    # Success: mu_seq < mu_agg (directional)
    directional_test: bool = True
    require_statistical_significance: bool = False
    # SHOULD_WORK allows failure → EXPLORE
    failure_action: str = "EXPLORE"
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M2-8-1 | GateValidator class | Gate logic class |
| M2-8-2 | Extract means | Get mu_seq and mu_agg from metrics |
| M2-8-3 | Directional comparison | Check mu_seq < mu_agg |
| M2-8-4 | Pass/fail determination | Set gate_satisfied boolean |
| M2-8-5 | Effect size | Compute absolute difference |
| M2-8-6 | Gate report generation | Format validation report |
| M2-8-7 | Failure explanation | Document EXPLORE path if failed |
| M2-8-8 | Logging | Log gate validation result |

---

## M2-9: Visualization [Complexity: 10, Budget: 10]

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
            "iteration_distribution.png",
            "convergence_curves.png",
            "per_task_comparison.png",
            "token_efficiency.png"
        ]
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M2-9-1 | ExperimentVisualizer class | Plotting logic class |
| M2-9-2 | Gate metrics plot | Bar chart: mu_seq vs mu_agg with error bars |
| M2-9-3 | Iteration distribution | Box plots: sequential vs aggregation |
| M2-9-4 | Convergence curves | Line plot: cumulative success rate per iteration |
| M2-9-5 | Per-task comparison | Scatter: aggregation iterations vs sequential |
| M2-9-6 | Token efficiency plot | Bar chart: mean tokens per successful solution |
| M2-9-7 | Style configuration | Apply seaborn style, set figure size |
| M2-9-8 | Save figures | Export all plots to figures/ |
| M2-9-9 | Figure validation | Verify all 5 figures generated |
| M2-9-10 | Logging | Log visualization completion |

---

## Extended Configuration (Current Hypothesis)

### Complete Experiment Configuration

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ExperimentConfig:
    """Complete configuration for h-m2 feedback presentation experiment"""

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

    # New fields for h-m2 (mechanism testing)
    h_e1_validation_path: str = "../h-e1/04_validation.md"
    n_tasks: int = 20  # First 20 of 35 qualified tasks
    max_iterations: int = 10

    # Routing strategies
    sequential_mode: bool = True
    aggregation_mode: bool = True
    sequential_mypy_first: bool = True
    sequential_skip_pytest_if_mypy_errors: bool = True
    aggregation_run_both_always: bool = True

    # Metrics and validation
    primary_metric: str = "mean_iterations_to_solution"
    gate_type: str = "SHOULD_WORK"
    gate_criterion: str = "mu_seq < mu_agg"

    # Tracking
    track_tokens: bool = True
    verify_mechanism: bool = True
    fail_on_mechanism_violation: bool = True
```

---

## Self-Validation

### Quick Checks
- [x] ONE format only (Dataclass - no hardcoded dict)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale only for non-standard values (marked with comments)
- [x] Subtask count within budget (all tasks match allocated budget)
- [x] Total length < 400 lines (currently ~380 lines)
- [x] "Codebase Analysis (Serena)" section included

### Serena MCP Validation
- [x] Base hypothesis exists → Serena called on h-m1 code
- [x] Field names verified from actual implementation
- [x] Config pattern (dataclass) confirmed from base code

### Base Hypothesis Checks
- [x] Read actual config classes from h-m1/code/run_experiment.py
- [x] Field names verified from actual implementation (lines 32-48)
- [x] Default values match actual base config
- [x] Inherited Configuration section included

---

**Generated by Phase 3 Configuration Agent**
**Source:** 03_architecture.md, 03_prd.md, h-m1/code/run_experiment.py
**Next:** Phase 4 - Implementation (Coder Agent)
