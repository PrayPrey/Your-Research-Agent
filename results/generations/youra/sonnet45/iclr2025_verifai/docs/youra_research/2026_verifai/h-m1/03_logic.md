# Logic Specifications: h-m1
# Hypothesis: Static Analysis Cascade Routing Mechanism

**Date:** 2026-03-18
**Hypothesis Type:** MECHANISM
**Author:** Claude (Logic Agent)
**Budget:** 8 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Extends h-e1 implementation - verified actual API signatures from base code
**Analyzed Path:** /home/anonymous/YouRA_results_new_4_sonnet45/TEST_verifai/docs/youra_research/20260318_verifai/h-e1/code/run_experiment.py
**Relevant Symbols:** HumanEvalLoader, CodeLlamaGenerator, MypyVerifier, PytestVerifier, DualSensitivityClassifier, ExperimentConfig
**Note:** Serena MCP unavailable (project not active), used direct file analysis. H-e1 uses monolithic single-file structure with all classes in run_experiment.py.

---

## M-1: Setup Infrastructure [Complexity: 5, Budget: 1]

**Applied:** Monolithic single-file pattern from h-e1

### API Signatures

```python
# File: code/run_experiment.py
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ExperimentConfig:
    """Configuration for h-m1 cascade routing experiment."""
    model_name: str = "codellama/CodeLlama-7b-hf"
    k_samples: int = 20
    temperature: float = 0.8
    top_p: float = 0.95
    top_k: int = 40
    max_length: int = 256
    mypy_timeout: int = 10
    pytest_timeout: int = 120
    max_retries: int = 5
    target_detection_rate: float = 30.0
    seed: int = 42
    device: str = "auto"
    h_e1_validation_path: str = "../h-e1/04_validation.md"
    output_dir: Path = Path("./outputs")
    figures_dir: Path = Path("./figures")
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Project setup | Create directory structure, requirements.txt, logging config |

---

## M-2: Qualified Task Loader [Complexity: 7, Budget: 1]

**Applied:** Text parsing pattern for validation reports

### API Signatures

```python
# File: code/run_experiment.py
from typing import List, Dict

class HumanEvalLoader:
    """Load HumanEval tasks and parse h-e1 qualified task list."""

    def __init__(self, use_evalplus: bool = True):
        """Initialize loader. use_evalplus: [bool]"""
        self.use_evalplus = use_evalplus
        self.problems: Dict[str, Dict] = None

    def load_problems(self) -> Dict[str, Dict]:
        """Load all 164 HumanEval tasks. Returns: {task_id: {prompt, entry_point, test}}"""
        ...

    def load_qualified_tasks(self, h_e1_validation_path: str) -> List[str]:
        """
        Parse h-e1 validation report for N=35 qualified task IDs.

        Args:
            h_e1_validation_path: Path to h-e1/04_validation.md

        Returns:
            List of qualified task IDs (expected N=35)
        """
        ...
```

### Pseudo-code

```
1. Read h-e1/04_validation.md
2. Parse "qualified_task_ids" section or results.json
3. Extract task IDs (e.g., "HumanEval/0", "HumanEval/1", ...)
4. Verify N >= 35
5. Return list of task IDs
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Validation parser | Parse markdown or JSON for qualified task IDs |

---

## M-3: Cascade Feedback Router [Complexity: 14, Budget: 3]

**Applied:** Iterative refinement with sequential single-source feedback

### API Signatures

```python
# File: code/run_experiment.py
from typing import Dict, List, Optional

class StaticAnalysisFeedbackRouter:
    """
    Core mechanism: Cascade routing with mypy-first sequential feedback.
    Tests hypothesis that static analysis catches ≥30% of errors before execution.
    """

    def __init__(
        self,
        generator: 'CodeLlamaGenerator',
        mypy_verifier: 'MypyVerifier',
        pytest_verifier: 'PytestVerifier',
        max_retries: int = 5
    ):
        """Initialize cascade router."""
        self.generator = generator
        self.mypy_verifier = mypy_verifier
        self.pytest_verifier = pytest_verifier
        self.max_retries = max_retries

    def generate_with_feedback(
        self,
        task_prompt: str,
        task_id: str,
        test_code: str,
        entry_point: str
    ) -> Dict:
        """
        Generate code with cascade feedback loop.

        Args:
            task_prompt: HumanEval prompt
            task_id: Task identifier
            test_code: Pytest test code
            entry_point: Function name to test

        Returns:
            {
                "task_id": str,
                "code": str,  # Final generated code
                "iterations": int,  # Total iterations used
                "mypy_error_count": int,  # Times mypy caught errors
                "pytest_error_count": int,  # Times pytest caught errors
                "mypy_caught": bool,  # Whether mypy caught any error
                "pytest_caught": bool,  # Whether pytest caught any error
                "success": bool,  # Both verifiers passed
                "timeout": bool,  # Hit max_retries
                "execution_time": float  # Total time (seconds)
            }
        """
        ...

    def format_mypy_feedback(self, mypy_output: str) -> str:
        """
        Format mypy errors for LLM prompt.

        Args:
            mypy_output: Raw mypy stderr

        Returns:
            Formatted feedback string (concise, token-efficient)
        """
        ...

    def format_pytest_feedback(self, pytest_output: str) -> str:
        """
        Format pytest failures for LLM prompt.

        Args:
            pytest_output: Raw pytest output

        Returns:
            Formatted feedback string
        """
        ...
```

### Pseudo-code

```
1. Initialize: iteration = 0, code = None
2. While iteration < max_retries:
   a. Generate code:
      - If iteration == 0: use original prompt
      - Else: use prompt + previous feedback

   b. Run mypy --strict (ALWAYS FIRST):
      - If mypy fails:
          * mypy_error_count += 1
          * feedback = format_mypy_feedback(mypy_output)
          * prompt = prompt + "\n\nMypy errors:\n" + feedback
          * iteration += 1
          * CONTINUE (skip pytest)

   c. Run pytest (ONLY if mypy passed):
      - If pytest fails:
          * pytest_error_count += 1
          * feedback = format_pytest_feedback(pytest_output)
          * prompt = prompt + "\n\nTest failures:\n" + feedback
          * iteration += 1
          * CONTINUE

   d. Success: both passed → BREAK

3. Return result dictionary
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Cascade loop | Implement mypy-first sequential routing logic |
| L-3-2 | Feedback formatting | Parse and format mypy/pytest errors for prompts |
| L-3-3 | Iteration tracking | Track error counts and routing decisions |

---

## M-4: Aggregation Baseline [Complexity: 10, Budget: 2]

**Applied:** Dual-source aggregation feedback pattern

### API Signatures

```python
# File: code/run_experiment.py

class AggregationFeedbackRouter:
    """
    Baseline: Run both mypy + pytest every iteration, aggregate feedback.
    Comparison baseline for cascade routing efficiency.
    """

    def __init__(
        self,
        generator: 'CodeLlamaGenerator',
        mypy_verifier: 'MypyVerifier',
        pytest_verifier: 'PytestVerifier',
        max_retries: int = 5
    ):
        """Initialize aggregation router."""
        self.generator = generator
        self.mypy_verifier = mypy_verifier
        self.pytest_verifier = pytest_verifier
        self.max_retries = max_retries

    def generate_with_feedback(
        self,
        task_prompt: str,
        task_id: str,
        test_code: str,
        entry_point: str
    ) -> Dict:
        """
        Generate code with aggregated feedback.

        Args:
            Same as StaticAnalysisFeedbackRouter

        Returns:
            Same structure as cascade router for comparison
        """
        ...

    def format_aggregated_feedback(
        self,
        mypy_output: Optional[str],
        pytest_output: Optional[str]
    ) -> str:
        """
        Concatenate both feedback sources.

        Args:
            mypy_output: Mypy errors (if any)
            pytest_output: Pytest failures (if any)

        Returns:
            Combined feedback string
        """
        ...
```

### Pseudo-code

```
1. Initialize: iteration = 0, code = None
2. While iteration < max_retries:
   a. Generate code

   b. Run BOTH mypy AND pytest (aggregation):
      - mypy_result = run_mypy(code)
      - pytest_result = run_pytest(code, test_code)

   c. If either failed:
      - Aggregate feedback from both sources
      - prompt = prompt + "\n\nFeedback:\n" + aggregated_feedback
      - iteration += 1
      - CONTINUE

   d. Success: both passed → BREAK

3. Return result dictionary
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Aggregation loop | Implement dual-source parallel routing |
| L-4-2 | Feedback aggregation | Concatenate mypy + pytest feedback |

---

## M-5: Mypy Integration [Complexity: 8, Budget: 1]

**Applied:** Subprocess execution with timeout and error parsing

### API Signatures

```python
# File: code/run_experiment.py
import subprocess
import tempfile
from typing import Dict, List

class MypyVerifier:
    """Static analysis with mypy --strict."""

    def __init__(self, timeout: int = 10):
        """Initialize verifier. timeout: [int seconds]"""
        self.timeout = timeout

    def verify(self, code: str) -> Dict:
        """
        Verify single code sample with mypy --strict.

        Args:
            code: Python code string

        Returns:
            {
                "passed": bool,  # returncode == 0
                "output": str,  # stderr/stdout
                "errors": List[Dict],  # Parsed error objects
                "error_count": int,
                "execution_time": float
            }
        """
        ...

    def parse_errors(self, output: str) -> List[Dict]:
        """
        Parse mypy output to structured errors.

        Args:
            output: Raw mypy stderr

        Returns:
            [
                {
                    "line": int,
                    "message": str,
                    "code": str  # e.g., "arg-type", "return-value"
                },
                ...
            ]
        """
        ...
```

### Pseudo-code

```
1. Write code to temp file
2. Run: subprocess.run(["mypy", "--strict", temp_file], timeout=10)
3. Capture stdout/stderr
4. Parse errors with regex
5. Return structured result
6. Cleanup temp file
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Mypy wrapper | Subprocess execution with error parsing |

---

## M-6: Pytest Integration [Complexity: 9, Budget: 1]

**Applied:** Subprocess execution with test sandboxing

### API Signatures

```python
# File: code/run_experiment.py

class PytestVerifier:
    """Execution testing with pytest and HumanEval+ tests."""

    def __init__(self, timeout: int = 120):
        """Initialize verifier. timeout: [int seconds]"""
        self.timeout = timeout

    def verify(self, code: str, test_code: str, entry_point: str) -> Dict:
        """
        Verify code with pytest.

        Args:
            code: Python code string
            test_code: Pytest test code
            entry_point: Function name to import

        Returns:
            {
                "passed": bool,  # returncode == 0
                "output": str,  # pytest output
                "failures": List[str],  # Failure messages
                "failure_count": int,
                "execution_time": float
            }
        """
        ...

    def parse_failures(self, output: str) -> List[str]:
        """
        Extract failure messages from pytest output.

        Args:
            output: Raw pytest output

        Returns:
            List of failure descriptions
        """
        ...
```

### Pseudo-code

```
1. Create temp directory
2. Write code to solution.py
3. Write test to test_solution.py (with import from solution)
4. Run: subprocess.run(["pytest", "-v", test_file], timeout=120)
5. Parse failures from output
6. Cleanup temp directory
7. Return result
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Pytest wrapper | Subprocess execution with sandboxed test environment |

---

## M-7: Detection Rate Analysis [Complexity: 11, Budget: 1]

**Applied:** Statistical aggregation pattern

### API Signatures

```python
# File: code/run_experiment.py
from typing import List, Dict
import numpy as np

class ErrorDetectionAnalyzer:
    """Calculate mypy error detection rate and validate MUST_WORK gate."""

    def __init__(self, threshold: float = 30.0):
        """Initialize analyzer. threshold: [30.0] minimum detection rate (%)"""
        self.threshold = threshold

    def calculate_detection_rate(self, cascade_results: List[Dict]) -> Dict:
        """
        Calculate overall mypy error detection rate.

        Args:
            cascade_results: List of cascade router results (one per task)

        Returns:
            {
                "overall_detection_rate": float,  # Percentage (0-100)
                "per_task_rates": List[float],  # Per-task detection rates
                "total_iterations": int,
                "total_mypy_errors": int,
                "total_pytest_errors": int,
                "mypy_only_count": int,  # Tasks with mypy errors only
                "pytest_only_count": int,  # Tasks with pytest errors only
                "both_clean_count": int,  # Tasks with no errors
                "gate_satisfied": bool  # >= threshold
            }
        """
        ...

    def compute_per_task_rates(self, results: List[Dict]) -> List[float]:
        """
        Compute detection rate per task.

        Args:
            results: Cascade results

        Returns:
            List of per-task detection rates (%)
        """
        ...

    def validate_gate(self, overall_rate: float) -> bool:
        """Check if overall_rate >= threshold."""
        return overall_rate >= self.threshold
```

### Pseudo-code

```
1. Aggregate across all N=35 tasks:
   - total_iterations = sum(r["iterations"] for r in results)
   - total_mypy_errors = sum(r["mypy_error_count"] for r in results)
   - total_pytest_errors = sum(r["pytest_error_count"] for r in results)

2. Calculate overall detection rate:
   - detection_rate = (total_mypy_errors / total_iterations) * 100

3. Compute per-task rates:
   - For each task: (mypy_error_count / iterations) * 100

4. Validate gate:
   - gate_satisfied = (detection_rate >= 30.0)

5. Return metrics dictionary
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Metrics calculation | Implement detection rate computation and gate validation |

---

## M-8: Visualization [Complexity: 9, Budget: 0]

**Applied:** Matplotlib standard plotting patterns

### API Signatures

```python
# File: code/run_experiment.py
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

class ExperimentVisualizer:
    """Generate experiment figures for h-m1."""

    def __init__(self, output_dir: Path):
        """Initialize visualizer. output_dir: Path to save figures"""
        self.output_dir = output_dir

    def plot_gate_metrics(
        self,
        target: float,
        actual: float,
        passed: bool
    ) -> None:
        """
        Figure 1: Bar chart comparing target vs actual detection rate.
        Save to: output_dir/gate_metrics.png
        """
        ...

    def plot_error_detection_breakdown(self, results: List[Dict]) -> None:
        """
        Figure 2: Stacked bar chart of error type distribution.
        Categories: [Mypy-only, Pytest-only, Both clean, Both failed]
        Save to: output_dir/error_breakdown.png
        """
        ...

    def plot_iteration_comparison(
        self,
        cascade_results: List[Dict],
        aggregation_results: List[Dict]
    ) -> None:
        """
        Figure 3: Box plot comparing iterations-to-solution.
        Groups: [Cascade, Aggregation]
        Save to: output_dir/iteration_comparison.png
        """
        ...

    def plot_execution_cost(
        self,
        cascade_results: List[Dict],
        aggregation_results: List[Dict]
    ) -> None:
        """
        Figure 4: Grouped bar chart of total execution time.
        X-axis: [Cascade, Aggregation]
        Y-axis: Total time (mypy + pytest)
        Save to: output_dir/execution_cost.png
        """
        ...

    def plot_task_heatmap(self, results: List[Dict]) -> None:
        """
        Figure 5: Binary heatmap of dual-sensitivity patterns.
        Rows: N=35 tasks
        Columns: [mypy_caught, pytest_caught]
        Save to: output_dir/task_heatmap.png
        """
        ...
```

### Subtasks [0/0 used]

No subtasks allocated (complexity absorbed into other tasks).

---

## Pipeline Orchestrator

**Applied:** Standard experiment pipeline pattern

### API Signatures

```python
# File: code/run_experiment.py

class CascadeRoutingPipeline:
    """Orchestrate h-m1 cascade routing experiment."""

    def __init__(self, config: ExperimentConfig):
        """Initialize pipeline with config."""
        self.config = config
        self.loader = None
        self.generator = None
        self.mypy_verifier = None
        self.pytest_verifier = None
        self.cascade_router = None
        self.aggregation_router = None
        self.analyzer = None
        self.visualizer = None

    def run(self) -> Dict:
        """
        Execute full pipeline.

        Returns:
            {
                "gate_satisfied": bool,
                "detection_rate": float,
                "cascade_results": List[Dict],
                "aggregation_results": List[Dict],
                "metrics": Dict
            }
        """
        ...

    def stage_load_qualified_tasks(self) -> List[str]:
        """Stage 1: Load N=35 qualified tasks from h-e1. Returns: [task_id, ...]"""
        ...

    def stage_cascade_evaluation(self, tasks: List[str]) -> List[Dict]:
        """Stage 2: Run cascade routing on all tasks. Returns: cascade results"""
        ...

    def stage_aggregation_baseline(self, tasks: List[str]) -> List[Dict]:
        """Stage 3: Run aggregation baseline. Returns: aggregation results"""
        ...

    def stage_analyze_detection_rate(self, cascade_results: List[Dict]) -> Dict:
        """Stage 4: Calculate detection rate and metrics. Returns: metrics dict"""
        ...

    def stage_generate_visualizations(
        self,
        cascade_results: List[Dict],
        aggregation_results: List[Dict],
        metrics: Dict
    ) -> None:
        """Stage 5: Generate all 5 figures."""
        ...

    def stage_validate_gate(self, metrics: Dict) -> Dict:
        """Stage 6: Validate MUST_WORK gate (≥30%). Returns: gate result"""
        ...

    def save_results(self, results: Dict, path: Path) -> None:
        """Save experiment results to JSON."""
        ...

def main():
    """Entry point for h-m1 experiment."""
    config = ExperimentConfig()
    pipeline = CascadeRoutingPipeline(config)
    results = pipeline.run()

    print(f"\n{'='*80}")
    print(f"H-M1 EXPERIMENT COMPLETE")
    print(f"{'='*80}")
    print(f"Detection Rate: {results['detection_rate']:.1f}%")
    print(f"Target: ≥{config.target_detection_rate}%")
    print(f"Gate: {'PASS' if results['gate_satisfied'] else 'FAIL'}")
    print(f"{'='*80}\n")

    return results
```

### Pseudo-code

```
1. Initialize all components:
   - HumanEvalLoader
   - CodeLlamaGenerator (load model)
   - MypyVerifier
   - PytestVerifier
   - StaticAnalysisFeedbackRouter
   - AggregationFeedbackRouter
   - ErrorDetectionAnalyzer
   - ExperimentVisualizer

2. Stage 1: Load qualified tasks
   - qualified_tasks = loader.load_qualified_tasks(h_e1_path)
   - Verify len(qualified_tasks) == 35

3. Stage 2: Cascade evaluation
   - For each task in qualified_tasks:
       * result = cascade_router.generate_with_feedback(task)
       * Save result to cascade_results

4. Stage 3: Aggregation baseline
   - For each task in qualified_tasks:
       * result = aggregation_router.generate_with_feedback(task)
       * Save result to aggregation_results

5. Stage 4: Analyze detection rate
   - metrics = analyzer.calculate_detection_rate(cascade_results)

6. Stage 5: Generate visualizations
   - visualizer.plot_gate_metrics(...)
   - visualizer.plot_error_detection_breakdown(...)
   - visualizer.plot_iteration_comparison(...)
   - visualizer.plot_execution_cost(...)
   - visualizer.plot_task_heatmap(...)

7. Stage 6: Validate gate
   - gate_result = analyzer.validate_gate(metrics["overall_detection_rate"])

8. Save all results to outputs/
9. Return final results
```

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

The following classes are reimplemented (not imported) from h-e1, but follow the same patterns:

```python
# From: h-e1/code/run_experiment.py (ACTUAL CODE - lines 50-78)
class HumanEvalLoader:
    def __init__(self, use_evalplus: bool = True):
        """use_evalplus: [bool] - matches h-e1 implementation"""
        ...

    def load_problems(self) -> Dict[str, Dict]:
        """Returns: {task_id: {prompt, entry_point, test}} - matches h-e1"""
        ...

# From: h-e1/code/run_experiment.py (ACTUAL CODE - lines 80-124)
class CodeLlamaGenerator:
    def __init__(self, config: ExperimentConfig):
        """config: [ExperimentConfig] - matches h-e1 pattern"""
        ...

    def load_model(self) -> None:
        """Load model - matches h-e1 implementation"""
        ...

    def generate_samples(self, prompt: str, k: int = None) -> List[str]:
        """
        prompt: [str], k: [int] - matches h-e1 signature
        Returns: [K × str] completions
        """
        ...

# From: h-e1/code/run_experiment.py (ACTUAL CODE - lines 126-159)
class MypyVerifier:
    def __init__(self, timeout: int = 10):
        """timeout: [int] - matches h-e1"""
        ...

    def verify(self, code: str) -> bool:
        """
        code: [str] → bool (h-e1 returns bool, h-m1 extends to Dict)
        H-M1 extends return type to Dict for detailed error info
        """
        ...

# From: h-e1/code/run_experiment.py (ACTUAL CODE - lines 161-199)
class PytestVerifier:
    def __init__(self, timeout: int = 120):
        """timeout: [int] - matches h-e1"""
        ...

    def verify(self, code: str, test_code: str) -> bool:
        """
        code: [str], test_code: [str] → bool (h-e1 signature)
        H-M1 extends return type to Dict for detailed failure info
        """
        ...
```

**Verified from**: h-e1/code/run_experiment.py (actual implementation, NOT spec!)

**Key Differences in h-m1:**
- MypyVerifier.verify() returns Dict instead of bool (extended for error details)
- PytestVerifier.verify() returns Dict instead of bool (extended for failure details)
- Added StaticAnalysisFeedbackRouter and AggregationFeedbackRouter (new in h-m1)
- Added ErrorDetectionAnalyzer (new in h-m1)

---

## Task Allocation Summary

| Task | Budget | Used | Remaining |
|------|--------|------|-----------|
| M-1 | 1 | 1 | 0 |
| M-2 | 1 | 1 | 0 |
| M-3 | 3 | 3 | 0 |
| M-4 | 2 | 2 | 0 |
| M-5 | 1 | 1 | 0 |
| M-6 | 1 | 1 | 0 |
| M-7 | 1 | 1 | 0 |
| M-8 | 0 | 0 | 0 |
| **Total** | **8** | **8** | **0** |

---

## Implementation Notes

### Type Hints
All APIs use Python 3.10+ type hints (`typing` module).

### Error Handling
- **Subprocess timeouts:** Catch `subprocess.TimeoutExpired`, log and continue
- **Model loading:** Retry up to 3 times with 15s delay
- **File I/O:** Use `with` statements and Path.unlink(missing_ok=True)

### Configuration
All hyperparameters in ExperimentConfig dataclass:
- Model settings (name, device, precision)
- Generation parameters (K=20, temperature=0.8, top_p=0.95, top_k=40)
- Verification timeouts (mypy=10s, pytest=120s)
- Gate threshold (30.0%)
- Max retries for feedback loops (5)

### Checkpointing
Save intermediate results to outputs/:
- cascade_results.jsonl - Progressive results from cascade router
- aggregation_results.jsonl - Progressive results from aggregation router
- detection_metrics.json - Final analysis metrics
- experiment.log - Execution log

### Logging
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('experiment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
```

---

## Dependencies

### External Packages
```txt
evalplus>=0.2.0
human-eval>=1.0.0
transformers>=4.30.0
torch>=2.0.0
mypy>=1.5.0
pytest>=7.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

### System Requirements
- Python 3.10+
- CUDA 11.0+
- GPU: ≥16GB VRAM (same as h-e1)
- RAM: ≥32GB

---

**Generated by Phase 3 Logic Agent**
**Source:** 03_architecture.md, 03_prd.md, h-e1/code/run_experiment.py (actual code)
**Next:** Phase 4 - Implementation (Coder Agent)
