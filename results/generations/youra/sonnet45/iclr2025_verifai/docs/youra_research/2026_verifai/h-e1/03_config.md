# Configuration Specification: h-e1
# Hypothesis: Dual-Sensitive Task Classification System

**Date:** 2026-03-18
**Hypothesis Type:** EXISTENCE
**Author:** Claude (Configuration Specialist)
**Applied:** PyTorch config dataclass pattern

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field project - designing new config schema
**Config Files Found:** None - new config
**Pattern Used:** dataclass

---

## Configuration Format

Single dataclass-based configuration for EXISTENCE hypothesis. No hyperparameter variations needed for PoC validation.

---

## A-1: Setup Infrastructure [Complexity: 6, Budget: 6]

**Applied:** Standard project structure pattern

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ProjectConfig:
    project_root: Path = Path("./h-e1")
    output_dir: Path = Path("./h-e1/results")
    figures_dir: Path = Path("./h-e1/figures")
    checkpoint_dir: Path = Path("./h-e1/checkpoints")
    log_level: str = "INFO"
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Directory structure | Create src/, results/, figures/, checkpoints/ |
| C-1-2 | Requirements file | Pin dependencies (evalplus, transformers, torch, mypy, pytest, numpy, matplotlib) |
| C-1-3 | Config schema | Implement dataclass-based configuration |
| C-1-4 | Logger setup | Configure Python logging with INFO level |
| C-1-5 | GPU detection | Implement CUDA_VISIBLE_DEVICES validation |
| C-1-6 | README | Document setup instructions and dependencies |

---

## A-2: Dataset Loading [Complexity: 7, Budget: 7]

**Applied:** Standard HumanEval loader pattern

### Configuration (Python Dataclass)

```python
@dataclass
class DatasetConfig:
    use_evalplus: bool = True  # Use evalplus (HumanEval+), fallback to human-eval if False
    cache_dir: str = "./cache/datasets"
    num_tasks: int = 164  # All HumanEval tasks
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Evalplus integration | Load HumanEval+ with get_human_eval_plus() |
| C-2-2 | Fallback loader | Implement human-eval fallback if evalplus fails |
| C-2-3 | Task parser | Extract prompt, entry_point, test cases |
| C-2-4 | Validation | Verify all 164 tasks loaded |
| C-2-5 | Cache system | Save loaded tasks to checkpoint |
| C-2-6 | Task metadata | Store task IDs and structure |
| C-2-7 | Error handling | Graceful fallback on dataset loading errors |

---

## A-3: Code Generation [Complexity: 12, Budget: 12]

**Applied:** HuggingFace transformers standard generation config

### Configuration (Python Dataclass)

```python
@dataclass
class GenerationConfig:
    model_name: str = "codellama/CodeLlama-7b-hf"
    device: str = "auto"  # Auto-assign GPU
    precision: str = "fp16"  # torch.float16
    k_samples: int = 20  # Samples per task
    temperature: float = 0.8
    top_p: float = 0.95
    top_k: int = 40
    max_tokens: int = 256
    seed: int = 1  # Fixed for reproducibility
    batch_size: int = 1  # Sequential generation (GPU OOM mitigation)
    cache_dir: str = "./cache/models"
```

### Subtasks [12/12 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Model loader | Load CodeLlama-7B with AutoModelForCausalLM |
| C-3-2 | Tokenizer setup | Configure AutoTokenizer |
| C-3-3 | Device assignment | Implement auto GPU assignment with CUDA_VISIBLE_DEVICES |
| C-3-4 | Precision conversion | Apply torch.float16 for FP16 inference |
| C-3-5 | Generation loop | K=20 samples per task |
| C-3-6 | Sampling parameters | Apply temperature, top_p, top_k |
| C-3-7 | Seed management | Set seed for torch, numpy, random |
| C-3-8 | Output formatting | Save completions in JSONL format |
| C-3-9 | Progress tracking | Log generation progress per task |
| C-3-10 | GPU OOM handling | Retry with batch_size=1 on OOM |
| C-3-11 | Model caching | Cache model weights locally |
| C-3-12 | Checkpoint saving | Save generated samples after each task |

---

## A-4: Static Verification [Complexity: 9, Budget: 9]

**Applied:** subprocess mypy integration pattern

### Configuration (Python Dataclass)

```python
@dataclass
class MypyConfig:
    strict_mode: bool = True  # Use --strict flag
    timeout: int = 10  # Seconds per sample
    json_report: bool = True  # Use --json-report for structured output
    temp_dir: str = "/tmp/mypy_verification"
```

### Subtasks [9/9 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Tempfile handler | Write code to temporary .py files |
| C-4-2 | Mypy executor | Run mypy --strict via subprocess |
| C-4-3 | JSON parser | Parse mypy JSON output |
| C-4-4 | Timeout handler | Apply 10-second timeout per sample |
| C-4-5 | Pass/fail classifier | Convert mypy returncode to boolean |
| C-4-6 | Batch processor | Process all 3,280 samples |
| C-4-7 | Error logging | Log mypy crashes and syntax errors |
| C-4-8 | Cleanup handler | Remove temporary files |
| C-4-9 | Checkpoint saving | Save mypy results to JSON |

---

## A-5: Execution Verification [Complexity: 10, Budget: 10]

**Applied:** subprocess pytest integration pattern

### Configuration (Python Dataclass)

```python
@dataclass
class PytestConfig:
    timeout: int = 120  # Seconds per sample (3s × 40 tests)
    json_report: bool = True  # Use --json-report
    fail_fast: bool = True  # Use -x flag (stop on first failure)
    temp_dir: str = "/tmp/pytest_verification"
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Test file generator | Combine code + HumanEval+ tests |
| C-5-2 | Pytest executor | Run pytest via subprocess |
| C-5-3 | JSON parser | Parse pytest JSON report |
| C-5-4 | Timeout handler | Apply 120-second timeout per sample |
| C-5-5 | Pass/fail classifier | Convert pytest returncode to boolean |
| C-5-6 | Test isolation | Ensure no cross-contamination between samples |
| C-5-7 | Batch processor | Process all 3,280 samples |
| C-5-8 | Error logging | Log pytest exceptions and timeouts |
| C-5-9 | Cleanup handler | Remove temporary test files |
| C-5-10 | Checkpoint saving | Save pytest results to JSON |

---

## A-6: Classification Logic [Complexity: 8, Budget: 8]

**Applied:** Numpy-based variance computation pattern

### Configuration (Python Dataclass)

```python
@dataclass
class ClassificationConfig:
    k_samples: int = 20  # Samples per task
    variance_threshold: float = 1.0  # SD threshold for qualification
    relaxed_threshold: float = 0.2  # Risk mitigation threshold
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Pattern counter | Count mypy_fail_pytest_pass and mypy_pass_pytest_fail |
| C-6-2 | Dual-sensitivity check | Verify both patterns ≥1 |
| C-6-3 | Variance computation | Compute SD across K=20 samples using numpy |
| C-6-4 | Qualification filter | Apply dual_sensitive AND variance ≤ threshold |
| C-6-5 | Batch classifier | Classify all 164 tasks |
| C-6-6 | Result aggregator | Collect classification results |
| C-6-7 | Statistics calculator | Compute mean, median, min, max variance |
| C-6-8 | JSON export | Save classification results |

---

## A-7: Gate Validation [Complexity: 6, Budget: 6]

**Applied:** MUST_WORK gate pattern with risk mitigation

### Configuration (Python Dataclass)

```python
@dataclass
class GateConfig:
    min_qualifying_tasks: int = 20  # MUST_WORK threshold
    relaxed_threshold: float = 0.2  # R1 mitigation threshold
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Counter | Count qualifying tasks (N) |
| C-7-2 | Gate checker | Check N ≥ 20 |
| C-7-3 | R1 mitigation | Apply relaxed threshold if N < 20 |
| C-7-4 | Status reporter | Generate PASS/FAIL report |
| C-7-5 | Validation output | Write gate results to 04_validation.md |
| C-7-6 | Error messages | Generate clear failure messages |

---

## A-8: Visualization [Complexity: 7, Budget: 7]

**Applied:** Matplotlib standard plotting pattern

### Configuration (Python Dataclass)

```python
@dataclass
class VisualizationConfig:
    output_dir: str = "./h-e1/figures"
    dpi: int = 300
    figsize: tuple = (10, 6)
    format: str = "png"
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | Gate metrics plot | Bar chart: target vs actual N |
| C-8-2 | Classification distribution | Bar chart: dual-sensitive vs not |
| C-8-3 | Variance histogram | Histogram with SD=1.0 threshold line |
| C-8-4 | Pattern scatter plot | Mypy vs pytest failure patterns |
| C-8-5 | Color mapping | Green/red for pass/fail |
| C-8-6 | Figure saving | Save all 4 figures as PNG (300 DPI) |
| C-8-7 | Filename convention | fig1_gate_metrics.png, fig2_classification.png, etc. |

---

## Master Configuration File

**File:** `h-e1/code/config.py`

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple

@dataclass
class ProjectConfig:
    project_root: Path = Path("./h-e1")
    output_dir: Path = Path("./h-e1/results")
    figures_dir: Path = Path("./h-e1/figures")
    checkpoint_dir: Path = Path("./h-e1/checkpoints")
    log_level: str = "INFO"

@dataclass
class DatasetConfig:
    use_evalplus: bool = True
    cache_dir: str = "./cache/datasets"
    num_tasks: int = 164

@dataclass
class GenerationConfig:
    model_name: str = "codellama/CodeLlama-7b-hf"
    device: str = "auto"
    precision: str = "fp16"
    k_samples: int = 20
    temperature: float = 0.8
    top_p: float = 0.95
    top_k: int = 40
    max_tokens: int = 256
    seed: int = 1
    batch_size: int = 1
    cache_dir: str = "./cache/models"

@dataclass
class MypyConfig:
    strict_mode: bool = True
    timeout: int = 10
    json_report: bool = True
    temp_dir: str = "/tmp/mypy_verification"

@dataclass
class PytestConfig:
    timeout: int = 120
    json_report: bool = True
    fail_fast: bool = True
    temp_dir: str = "/tmp/pytest_verification"

@dataclass
class ClassificationConfig:
    k_samples: int = 20
    variance_threshold: float = 1.0
    relaxed_threshold: float = 0.2

@dataclass
class GateConfig:
    min_qualifying_tasks: int = 20
    relaxed_threshold: float = 0.2

@dataclass
class VisualizationConfig:
    output_dir: str = "./h-e1/figures"
    dpi: int = 300
    figsize: Tuple[int, int] = (10, 6)
    format: str = "png"

@dataclass
class ExperimentConfig:
    """Master configuration for h-e1 experiment."""
    project: ProjectConfig = field(default_factory=ProjectConfig)
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    mypy: MypyConfig = field(default_factory=MypyConfig)
    pytest: PytestConfig = field(default_factory=PytestConfig)
    classification: ClassificationConfig = field(default_factory=ClassificationConfig)
    gate: GateConfig = field(default_factory=GateConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)

# Instantiate default config
DEFAULT_CONFIG = ExperimentConfig()
```

---

## Configuration Usage

**Phase 4 Implementation Example:**

```python
from config import DEFAULT_CONFIG

# Access nested configs
config = DEFAULT_CONFIG

# Use in modules
loader = HumanEvalLoader(use_evalplus=config.dataset.use_evalplus)
generator = CodeLlamaGenerator(
    model_name=config.generation.model_name,
    device=config.generation.device
)
classifier = DualSensitivityClassifier(
    k_samples=config.classification.k_samples,
    variance_threshold=config.classification.variance_threshold
)
```

---

## Validation Checklist

- [x] ONE format only (Dataclass)
- [x] No ASCII diagrams
- [x] KB search logs condensed (1 line)
- [x] Rationale only for non-standard values
- [x] Subtask counts within budget
- [x] Total length < 400 lines
- [x] Codebase Analysis (Serena) section included
- [x] EXISTENCE hypothesis: single fixed config (no hyperparameter grid)
- [x] All default values from research (PRD specifications)
- [x] Configuration is copy-paste ready for Phase 4

---

**Generated by Phase 3 Configuration Agent**
**Source:** 03_architecture.md, 03_prd.md
**Next:** Phase 4 - Implementation (Coder Agent)
