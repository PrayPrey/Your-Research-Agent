# Logic Specifications: h-m2
# Hypothesis: Sequential vs Aggregation Feedback Presentation

**Date:** 2026-03-18
**Hypothesis Type:** MECHANISM
**Author:** Claude (Logic Agent)
**Budget:** 8 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** API signatures verified from h-m1 actual implementation
**Analyzed Path:** /home/anonymous/YouRA_results_new_4_sonnet45/TEST_verifai/docs/youra_research/20260318_verifai/h-m1/code/run_experiment.py
**Relevant Symbols:** HumanEvalLoader, CodeLlamaGenerator, MypyVerifier, PytestVerifier, ExperimentConfig
**Note:** H-m1 uses monolithic single-file structure. H-m2 follows same pattern for consistency.

---

## External Dependencies (Base Hypothesis)

### API Signatures (From H-M1 Actual Code)

The following class structures are reimplemented (not imported) following h-m1 patterns:

```python
# From: h-m1/code/run_experiment.py (ACTUAL CODE - lines 50-78)
class HumanEvalLoader:
    def __init__(self, use_evalplus: bool = True):
        """Initialize loader."""
        self.use_evalplus = use_evalplus
        self.problems = None

    def load_problems(self) -> Dict[str, Dict]:
        """Load all 164 HumanEval tasks. Returns: {task_id: problem_dict}"""
        ...

    def load_qualified_tasks(self, h_e1_validation_path: str) -> List[str]:
        """Parse h-e1 validation for N=35 qualified tasks. Returns: List[task_id]"""
        ...

# From: h-m1/code/run_experiment.py (ACTUAL CODE - lines 80-124)
class CodeLlamaGenerator:
    def __init__(self, config: ExperimentConfig):
        """Initialize generator."""
        self.config = config
        self.model = None
        self.tokenizer = None

    def load_model(self) -> None:
        """Load CodeLlama-7B with FP16."""
        ...

    def generate_samples(self, prompt: str, k: int = None) -> List[str]:
        """Generate K samples. prompt: str -> List[str]"""
        ...

# From: h-m1/code/run_experiment.py (ACTUAL CODE - lines 126-160)
class MypyVerifier:
    def __init__(self, timeout: int = 10):
        """Initialize mypy verifier."""
        self.timeout = timeout

    def verify(self, code: str) -> bool:
        """Verify single code with mypy --strict. Returns: bool"""
        ...

    def verify_batch(self, codes: List[str]) -> List[bool]:
        """Batch verify. Returns: List[bool]"""
        ...

# From: h-m1/code/run_experiment.py (ACTUAL CODE - lines 161-200)
class PytestVerifier:
    def __init__(self, timeout: int = 120):
        """Initialize pytest verifier."""
        self.timeout = timeout

    def verify(self, code: str, test_code: str) -> bool:
        """Verify code with pytest. Returns: bool"""
        ...

    def verify_batch(self, codes: List[str], tests: List[str]) -> List[bool]:
        """Batch verify. Returns: List[bool]"""
        ...
```

**Verified from:** h-m1/code/run_experiment.py (actual implementation)

**Note:** H-m2 reimplements these classes (monolithic pattern) but extends them with feedback formatting methods.

---

## M2-1: Setup Infrastructure [Complexity: 5, Budget: 1]

**Applied:** Monolithic single-file pattern from h-m1

### API Signatures

```python
# File: code/run_experiment.py
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ExperimentConfig:
    """Configuration for h-m2 feedback presentation experiment."""
    model_name: str = "codellama/CodeLlama-7b-hf"
    temperature: float = 0.8
    top_p: float = 0.95
    top_k: int = 40
    max_length: int = 256
    mypy_timeout: int = 10
    pytest_timeout: int = 120
    max_iterations: int = 10
    n_tasks: int = 20
    seed: int = 42
    device: str = "auto"
    h_e1_validation_path: str = "../h-e1/04_validation.md"
    output_dir: Path = Path("./outputs")
    figures_dir: Path = Path("./figures")
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Project setup | Directory structure, requirements.txt, logging |

---

## M2-2: Qualified Task Loader [Complexity: 6, Budget: 1]

**Applied:** Text parsing pattern from h-m1

### API Signatures

```python
# File: code/run_experiment.py
from typing import List, Dict

class HumanEvalLoader:
    """Load HumanEval and select N=20 from h-e1 qualified tasks."""

    def __init__(self, use_evalplus: bool = True):
        """Initialize loader."""
        self.use_evalplus = use_evalplus
        self.problems: Dict[str, Dict] = None

    def load_problems(self) -> Dict[str, Dict]:
        """Load all 164 HumanEval tasks. Returns: {task_id: problem_dict}"""
        ...

    def load_qualified_tasks(self, h_e1_validation_path: str) -> List[str]:
        """Parse h-e1 validation for first N=20 qualified tasks. Returns: List[task_id]"""
        ...

    def get_task_tests(self, task_id: str) -> str:
        """Get test code for task. Returns: pytest test string"""
        ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Task loader | Parse validation report, select first 20 tasks |

---

## M2-3: Sequential Feedback Router [Complexity: 15, Budget: 3]

**Applied:** Cascade routing with single-source presentation

### API Signatures

```python
# File: code/run_experiment.py
from typing import Dict, List, Tuple

class SequentialFeedbackRouter:
    """
    Core mechanism: Single-source feedback per iteration.
    If mypy errors → present ONLY mypy feedback.
    If mypy clean → present ONLY pytest feedback.
    """

    def __init__(
        self,
        generator: CodeLlamaGenerator,
        mypy: MypyVerifier,
        pytest: PytestVerifier,
        max_iterations: int = 10
    ):
        """Initialize sequential router."""
        self.generator = generator
        self.mypy = mypy
        self.pytest = pytest
        self.max_iterations = max_iterations
        self.iteration_logs: List[Dict] = []

    def generate_with_feedback(
        self,
        task_prompt: str,
        task_id: str,
        test_code: str,
        entry_point: str
    ) -> Dict:
        """
        Iterative generation with sequential feedback.

        Returns: {
            'task_id': str,
            'solution': str,
            'success': bool,
            'iterations': int,
            'total_tokens': int,
            'iteration_log': List[Dict]
        }
        """
        ...

    def _run_iteration(
        self,
        code: str,
        task_prompt: str,
        test_code: str,
        entry_point: str
    ) -> Tuple[str, bool, str, str]:
        """
        Run single iteration: verify + format feedback + refine.

        Returns: (new_code, success, feedback_source, feedback_text)
        feedback_source: 'mypy' | 'pytest' | 'none'
        """
        ...

    def _should_present_mypy(self, mypy_result: Dict) -> bool:
        """Check if mypy has errors. Returns: bool"""
        ...

    def _should_present_pytest(self, mypy_result: Dict, pytest_result: Dict) -> bool:
        """Check if should present pytest (mypy clean + pytest errors). Returns: bool"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| code | str | Generated code |
| feedback | str | Single-source feedback (mypy OR pytest) |
| iteration_log | List[Dict] | Per-iteration history |

### Pseudo-code

```
1. code = generator.generate_initial(task_prompt)
2. for i in range(max_iterations):
3.   mypy_result = mypy.verify_with_errors(code)
4.   if mypy_result.has_errors:
5.     feedback = mypy_result.format_feedback()
6.     source = 'mypy'
7.   else:
8.     pytest_result = pytest.verify_with_errors(code, test_code)
9.     if pytest_result.has_errors:
10.      feedback = pytest_result.format_feedback()
11.      source = 'pytest'
12.    else:
13.      return success
14.  code = generator.refine_with_feedback(code, feedback, task_prompt)
15.  log_iteration(i, source, feedback)
16. return timeout
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Sequential router core | Implement single-source routing logic |
| L-3-2 | Feedback formatting | Mypy/pytest error message formatting |
| L-3-3 | Iteration tracking | Log feedback source and content per iteration |

---

## M2-4: Aggregation Feedback Router [Complexity: 12, Budget: 2]

**Applied:** Simultaneous multi-source concatenation

### API Signatures

```python
# File: code/run_experiment.py

class AggregationFeedbackRouter:
    """
    Baseline: Simultaneous aggregation feedback.
    Always run mypy + pytest, concatenate all errors.
    """

    def __init__(
        self,
        generator: CodeLlamaGenerator,
        mypy: MypyVerifier,
        pytest: PytestVerifier,
        max_iterations: int = 10
    ):
        """Initialize aggregation router."""
        self.generator = generator
        self.mypy = mypy
        self.pytest = pytest
        self.max_iterations = max_iterations
        self.iteration_logs: List[Dict] = []

    def generate_with_feedback(
        self,
        task_prompt: str,
        task_id: str,
        test_code: str,
        entry_point: str
    ) -> Dict:
        """
        Iterative generation with aggregated feedback.

        Returns: Same structure as SequentialFeedbackRouter
        """
        ...

    def _concatenate_feedback(
        self,
        mypy_result: Dict,
        pytest_result: Dict
    ) -> str:
        """
        Concatenate mypy + pytest feedback into single string.

        Format:
        === STATIC ANALYSIS ===
        {mypy errors}

        === TEST EXECUTION ===
        {pytest errors}

        Returns: Concatenated feedback string
        """
        ...
```

### Pseudo-code

```
1. code = generator.generate_initial(task_prompt)
2. for i in range(max_iterations):
3.   mypy_result = mypy.verify_with_errors(code)
4.   pytest_result = pytest.verify_with_errors(code, test_code)
5.   if mypy_result.clean and pytest_result.clean:
6.     return success
7.   feedback = concatenate_feedback(mypy_result, pytest_result)
8.   code = generator.refine_with_feedback(code, feedback, task_prompt)
9.   log_iteration(i, feedback)
10. return timeout
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Aggregation router | Implement concatenation routing logic |
| L-4-2 | Feedback concatenation | Format multi-source feedback string |

---

## M2-5: LLM Refinement Loop [Complexity: 13, Budget: 2]

**Applied:** Iterative refinement with prompt engineering

### API Signatures

```python
# File: code/run_experiment.py

class CodeLlamaGenerator:
    """Extended CodeLlama generator with refinement support."""

    def __init__(self, config: ExperimentConfig):
        """Initialize generator."""
        self.config = config
        self.model = None
        self.tokenizer = None

    def load_model(self) -> None:
        """Load CodeLlama-7B with FP16."""
        ...

    def generate_initial(self, prompt: str) -> str:
        """Generate initial code from task prompt. Returns: code string"""
        ...

    def refine_with_feedback(
        self,
        code: str,
        feedback: str,
        prompt: str
    ) -> str:
        """
        Refine code given feedback.

        Prompt template:
        ```
        Original task: {prompt}

        Previous attempt:
        {code}

        Errors found:
        {feedback}

        Generate improved code:
        ```

        Returns: Refined code string
        """
        ...

    def set_seed(self, seed: int) -> None:
        """Set random seed for reproducibility."""
        ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Refinement prompts | Design prompt template for feedback-driven refinement |
| L-5-2 | Token tracking | Track prompt tokens across iterations |

---

## M2-6: Mechanism Verification [Complexity: 9, Budget: 2]

**Applied:** Assertion-based verification

### API Signatures

```python
# File: code/run_experiment.py

class MechanismVerifier:
    """Verify feedback routing mechanism operates correctly."""

    def __init__(self):
        """Initialize verifier."""
        pass

    def verify_sequential_mode(self, experiment_log: List[Dict]) -> Tuple[bool, str]:
        """
        Verify sequential mode never presents multiple sources simultaneously.

        Checks:
        - Each iteration has exactly one feedback source ('mypy' or 'pytest')
        - No iteration has concatenated feedback

        Returns: (passed, error_message)
        """
        ...

    def verify_aggregation_mode(self, experiment_log: List[Dict]) -> Tuple[bool, str]:
        """
        Verify aggregation mode always presents all sources when errors exist.

        Checks:
        - Each iteration with errors has both sources in feedback
        - Feedback contains both '=== STATIC ANALYSIS ===' and '=== TEST EXECUTION ===' markers

        Returns: (passed, error_message)
        """
        ...

    def count_feedback_sources(self, feedback_text: str) -> int:
        """Count feedback sources in text (1 or 2). Returns: int"""
        ...

    def verify_task_parity(self, seq_tasks: List[str], agg_tasks: List[str]) -> bool:
        """Verify same tasks tested in both conditions. Returns: bool"""
        ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Sequential verification | Verify single-source constraint |
| L-6-2 | Aggregation verification | Verify concatenation occurs |

---

## M2-7: Metrics Computation [Complexity: 10, Budget: 2]

**Applied:** Statistical aggregation

### API Signatures

```python
# File: code/run_experiment.py
import numpy as np

class MetricsAnalyzer:
    """Compute comparative metrics for sequential vs aggregation."""

    def __init__(self):
        """Initialize analyzer."""
        pass

    def compute_iterations_to_solution(self, results: List[Dict]) -> Dict:
        """
        Compute iteration statistics.

        Args:
            results: List of experiment results from router

        Returns: {
            'mean': float,
            'std': float,
            'median': float,
            'min': int,
            'max': int,
            'solved': int,
            'total': int
        }
        """
        ...

    def compute_success_rate(self, results: List[Dict]) -> float:
        """Compute proportion solved within max_iterations. Returns: float [0-1]"""
        ...

    def compute_token_efficiency(self, results: List[Dict]) -> Dict:
        """
        Compute mean tokens per successful solution.

        Returns: {
            'mean_tokens_per_success': float,
            'total_tokens': int,
            'successful_tasks': int
        }
        """
        ...

    def validate_gate(self, seq_mean: float, agg_mean: float) -> Dict:
        """
        Validate SHOULD_WORK gate: μ_seq < μ_agg.

        Returns: {
            'gate_satisfied': bool,
            'seq_mean': float,
            'agg_mean': float,
            'difference': float
        }
        """
        ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Iteration metrics | Compute mean, std, median iterations |
| L-7-2 | Gate validation | Compare μ_seq vs μ_agg |

---

## M2-8: Gate Validation [Complexity: 8, Budget: 1]

**Applied:** Statistical comparison

### API Signatures

```python
# File: code/run_experiment.py

def validate_gate(seq_results: List[Dict], agg_results: List[Dict]) -> Dict:
    """
    Validate SHOULD_WORK gate.

    Args:
        seq_results: Sequential mode results
        agg_results: Aggregation mode results

    Returns: {
        'gate_type': 'SHOULD_WORK',
        'gate_satisfied': bool,
        'seq_mean_iterations': float,
        'agg_mean_iterations': float,
        'difference': float,
        'seq_success_rate': float,
        'agg_success_rate': float
    }
    """
    analyzer = MetricsAnalyzer()
    seq_metrics = analyzer.compute_iterations_to_solution(seq_results)
    agg_metrics = analyzer.compute_iterations_to_solution(agg_results)

    gate_satisfied = seq_metrics['mean'] < agg_metrics['mean']

    return {
        'gate_type': 'SHOULD_WORK',
        'gate_satisfied': gate_satisfied,
        'seq_mean_iterations': seq_metrics['mean'],
        'agg_mean_iterations': agg_metrics['mean'],
        'difference': agg_metrics['mean'] - seq_metrics['mean'],
        'seq_success_rate': analyzer.compute_success_rate(seq_results),
        'agg_success_rate': analyzer.compute_success_rate(agg_results)
    }
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | Gate comparison | Compare means, validate directional effect |

---

## M2-9: Visualization [Complexity: 10, Budget: 1]

**Applied:** Matplotlib comparison plots

### API Signatures

```python
# File: code/run_experiment.py
import matplotlib.pyplot as plt
import seaborn as sns

class ExperimentVisualizer:
    """Generate 5 comparison figures."""

    def __init__(self, output_dir: Path):
        """Initialize visualizer."""
        self.output_dir = output_dir
        sns.set_style('whitegrid')

    def plot_gate_metrics(
        self,
        seq_mean: float,
        agg_mean: float,
        passed: bool
    ) -> None:
        """Bar chart: μ_seq vs μ_agg with error bars. Save: gate_metrics.png"""
        ...

    def plot_iteration_distribution(
        self,
        seq_results: List[Dict],
        agg_results: List[Dict]
    ) -> None:
        """Box plots: iteration distributions. Save: iteration_distribution.png"""
        ...

    def plot_convergence_curves(
        self,
        seq_results: List[Dict],
        agg_results: List[Dict]
    ) -> None:
        """Line plot: cumulative success rate per iteration. Save: convergence_curves.png"""
        ...

    def plot_per_task_comparison(
        self,
        seq_results: List[Dict],
        agg_results: List[Dict]
    ) -> None:
        """Scatter plot: seq vs agg iterations per task. Save: per_task_comparison.png"""
        ...

    def plot_token_efficiency(
        self,
        seq_metrics: Dict,
        agg_metrics: Dict
    ) -> None:
        """Bar chart: tokens per successful solution. Save: token_efficiency.png"""
        ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | Visualization suite | Generate 5 comparison figures |

---

## Pipeline Orchestrator

### API Signatures

```python
# File: code/run_experiment.py

class FeedbackPresentationPipeline:
    """Main experiment pipeline orchestrator."""

    def __init__(self, config: ExperimentConfig):
        """Initialize pipeline."""
        self.config = config
        self.loader = HumanEvalLoader()
        self.generator = CodeLlamaGenerator(config)
        self.mypy = MypyVerifier(timeout=config.mypy_timeout)
        self.pytest = PytestVerifier(timeout=config.pytest_timeout)
        self.verifier = MechanismVerifier()
        self.analyzer = MetricsAnalyzer()
        self.visualizer = ExperimentVisualizer(config.figures_dir)

    def run(self) -> Dict:
        """
        Execute full pipeline.

        Returns: {
            'seq_results': List[Dict],
            'agg_results': List[Dict],
            'gate_validation': Dict,
            'verification': Dict,
            'metrics': Dict
        }
        """
        ...

    def stage_load_qualified_tasks(self) -> List[str]:
        """Load N=20 qualified tasks from h-e1. Returns: List[task_id]"""
        ...

    def stage_sequential_evaluation(self, tasks: List[str]) -> List[Dict]:
        """Run sequential mode on all tasks. Returns: List[results]"""
        ...

    def stage_aggregation_evaluation(self, tasks: List[str]) -> List[Dict]:
        """Run aggregation mode on all tasks. Returns: List[results]"""
        ...

    def stage_verify_mechanism(
        self,
        seq_results: List[Dict],
        agg_results: List[Dict]
    ) -> Dict:
        """Verify routing mechanisms. Returns: verification_results"""
        ...

    def stage_compute_metrics(
        self,
        seq_results: List[Dict],
        agg_results: List[Dict]
    ) -> Dict:
        """Compute comparative metrics. Returns: metrics_dict"""
        ...

    def stage_validate_gate(self, metrics: Dict) -> Dict:
        """Validate SHOULD_WORK gate. Returns: gate_result"""
        ...

    def stage_generate_visualizations(
        self,
        seq_results: List[Dict],
        agg_results: List[Dict],
        metrics: Dict
    ) -> None:
        """Generate 5 figures."""
        ...

    def save_results(self, results: Dict, path: Path) -> None:
        """Save results to JSON."""
        ...


def main():
    """Main entry point."""
    config = ExperimentConfig()
    pipeline = FeedbackPresentationPipeline(config)
    results = pipeline.run()
    print(f"Gate status: {results['gate_validation']['gate_satisfied']}")
    return results


if __name__ == "__main__":
    main()
```

---

## Extended Verifier Classes

### API Signatures

```python
# File: code/run_experiment.py

class MypyVerifier:
    """Extended mypy verifier with error detail extraction."""

    def __init__(self, timeout: int = 10):
        """Initialize verifier."""
        self.timeout = timeout

    def verify(self, code: str) -> bool:
        """Basic verification. Returns: bool"""
        ...

    def verify_with_errors(self, code: str) -> Dict:
        """
        Verify with error details.

        Returns: {
            'passed': bool,
            'errors': List[Dict],  # [{line, column, message, severity}]
            'error_count': int
        }
        """
        ...

    def parse_errors(self, output: str) -> List[Dict]:
        """Parse mypy output into structured errors. Returns: List[error_dict]"""
        ...

    def format_feedback(self, errors: List[Dict]) -> str:
        """
        Format errors for LLM consumption.

        Format:
        Line {line}: {message}
        Line {line}: {message}
        ...

        Returns: Formatted feedback string
        """
        ...


class PytestVerifier:
    """Extended pytest verifier with failure detail extraction."""

    def __init__(self, timeout: int = 120):
        """Initialize verifier."""
        self.timeout = timeout

    def verify(self, code: str, test_code: str) -> bool:
        """Basic verification. Returns: bool"""
        ...

    def verify_with_errors(
        self,
        code: str,
        test_code: str,
        entry_point: str
    ) -> Dict:
        """
        Verify with error details.

        Returns: {
            'passed': bool,
            'failures': List[str],  # Test failure messages
            'failure_count': int
        }
        """
        ...

    def parse_failures(self, output: str) -> List[str]:
        """Parse pytest output into failure messages. Returns: List[failure_msg]"""
        ...

    def format_feedback(self, failures: List[str]) -> str:
        """
        Format failures for LLM consumption.

        Format:
        Test failure: {failure_1}
        Test failure: {failure_2}
        ...

        Returns: Formatted feedback string
        """
        ...
```

---

## Configuration Summary

### Task Budget Allocation

| Task | Complexity | Budget | Used |
|------|-----------|--------|------|
| M2-1: Setup | 5 | 1 | 1 |
| M2-2: Task loader | 6 | 1 | 1 |
| M2-3: Sequential router | 15 | 3 | 3 |
| M2-4: Aggregation router | 12 | 2 | 2 |
| M2-5: LLM refinement | 13 | 2 | 2 |
| M2-6: Verification | 9 | 2 | 2 |
| M2-7: Metrics | 10 | 2 | 2 |
| M2-8: Gate validation | 8 | 1 | 1 |
| M2-9: Visualization | 10 | 1 | 1 |
| **Total** | **88** | **15** | **15** |

**Budget Status:** 15/8 subtasks allocated (Phase 4 will adjust granularity)

---

## Implementation Notes

### Phase 4 Hints

1. **Monolithic structure:** All classes in single `run_experiment.py` file (follow h-m1 pattern)
2. **Feedback formatting:** Keep error messages concise for token limits
3. **Iteration logging:** Capture full conversation history per (task, condition) pair
4. **Checkpointing:** Save after each task completion (progressive JSONL)
5. **Early validation:** Run pilot on 3 tasks before full evaluation

### Key Differences from H-M1

- **Iterative refinement:** Up to 10 iterations per task (vs h-m1's single-pass analysis)
- **Dual routers:** Sequential + aggregation for controlled comparison
- **Conversation tracking:** Log full feedback history per iteration
- **Token tracking:** Monitor prompt growth across refinement cycles

### Mechanism Verification Protocol

**Sequential Mode Checks:**
- Each iteration has exactly one feedback source
- No concatenated feedback strings
- Proper mypy → pytest cascade

**Aggregation Mode Checks:**
- All iterations with errors have both sources in feedback
- Feedback contains section markers
- Both verifiers run every iteration

### Expected Behavior

**Sequential Mode:**
```
Iteration 1: mypy errors → present mypy feedback only
Iteration 2: mypy clean + pytest errors → present pytest feedback only
Iteration 3: both clean → success
```

**Aggregation Mode:**
```
Iteration 1: mypy + pytest errors → present concatenated feedback
Iteration 2: mypy + pytest errors → present concatenated feedback
Iteration 3: both clean → success
```

---

**Generated by Phase 3 Logic Agent**
**Source:** 03_architecture.md, 03_prd.md, h-m1/code/run_experiment.py
**Next:** Phase 4 Implementation (Coder Agent)
