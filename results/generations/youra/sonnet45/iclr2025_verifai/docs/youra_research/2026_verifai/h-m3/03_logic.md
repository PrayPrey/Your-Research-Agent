# Logic Specification: h-m3
# Hypothesis: Conditional Execution Gating Token Efficiency

**Date:** 2026-03-18
**Hypothesis Type:** MECHANISM
**Author:** Claude (Logic Agent)
**Budget:** 10 subtasks allocated

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** API signatures verified from h-m1 actual code
**Analyzed Path:** docs/youra_research/20260318_verifai/h-m1/code/run_experiment.py
**Relevant Symbols:** HumanEvalLoader, CodeLlamaGenerator, MypyVerifier, PytestVerifier (lines 50-199)
**Note:** H-m1 uses monolithic single-file structure. Will copy-paste and adapt base classes for h-m3 feedback routing logic.

---

## A-1: Setup Infrastructure [Complexity: 5, Budget: 5]

**Applied:** Standard project setup pattern

### API Signatures

```python
@dataclass
class ExperimentConfig:
    """H-m3 experiment configuration"""
    model_name: str = "codellama/CodeLlama-7b-hf"
    temperature: float = 0.7
    top_p: float = 0.95
    max_new_tokens: int = 512
    max_iterations: int = 10
    token_limit_per_source: int = 1000
    mypy_timeout: int = 10
    pytest_timeout: int = 120
    efficiency_threshold: float = 1.15
    seed: int = 42
    device: str = "auto"
    h_e1_validation_path: str = "../h-e1/04_validation.md"
    output_dir: Path = Path("./outputs")
    figures_dir: Path = Path("./figures")
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | ExperimentConfig dataclass | Configuration parameters |
| L-1-2 | Logging setup | File + stdout handlers |
| L-1-3 | GPU configuration | CUDA_VISIBLE_DEVICES check |
| L-1-4 | Directory creation | outputs/, figures/ |
| L-1-5 | Seed initialization | torch, numpy, random |

---

## A-2: Qualified Task Loader [Complexity: 7, Budget: 7]

**Applied:** Standard data loading pattern

### API Signatures

```python
class HumanEvalLoader:
    """Load HumanEval+ dataset and filter to h-e1 qualified tasks"""

    def __init__(self, use_evalplus: bool = True):
        """Initialize loader. use_evalplus: [bool] prefer evalplus over human-eval"""
        self.use_evalplus = use_evalplus
        self.problems = None

    def load_problems(self) -> Dict[str, Dict]:
        """Load all 164 tasks. Returns: {task_id: problem_dict}"""
        ...

    def load_qualified_task_ids(self, h_e1_validation_path: str) -> List[str]:
        """Parse N=20 dual-sensitive task IDs from h-e1 validation.

        Args:
            h_e1_validation_path: str - Path to ../h-e1/04_validation.md

        Returns:
            List[str] - 20 task IDs (format: "HumanEval/XXX")
        """
        ...
```

### Pseudo-code

```
1. Parse h-e1 validation markdown for "Qualified Task IDs" section
2. Extract task_id list (N=20)
3. Load all problems from evalplus
4. Filter to qualified subset: {tid: problems[tid] for tid in qualified}
5. Assert len(qualified) == 20
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Markdown parser | Extract task IDs from h-e1 validation |
| L-2-2 | Evalplus loader | Load HumanEval+ dataset |
| L-2-3 | Task filter | Filter to N=20 qualified |
| L-2-4 | Problem structure | Extract prompt, entry_point, tests |
| L-2-5 | Validation | Assert N=20, all fields present |
| L-2-6 | Error handling | Fallback to human-eval if evalplus fails |
| L-2-7 | Logging | Task loading progress |

---

## A-3: Reuse Verification Components [Complexity: 8, Budget: 8]

**Applied:** Copy-paste from h-m1 with feedback formatting extensions

### API Signatures

```python
class MypyVerifier:
    """Static verification with mypy --strict + feedback formatting"""

    def __init__(self, timeout: int = 10):
        """Initialize verifier. timeout: [int] seconds"""
        self.timeout = timeout

    def verify(self, code: str) -> Dict[str, any]:
        """Run mypy --strict on code.

        Args:
            code: str - Python code to verify

        Returns:
            {
                "success": bool,
                "stderr": str,
                "returncode": int
            }
        """
        ...

    def format_feedback(self, stderr: str) -> str:
        """Format mypy errors for LLM feedback (≤1000 tokens).

        Args:
            stderr: str - Raw mypy output

        Returns:
            str - Formatted feedback (truncated if needed)
        """
        ...

class PytestVerifier:
    """Execution verification with pytest + feedback formatting"""

    def __init__(self, timeout: int = 120):
        """Initialize verifier. timeout: [int] seconds"""
        self.timeout = timeout

    def verify(self, code: str, test_code: str, entry_point: str) -> Dict[str, any]:
        """Run pytest on code with test cases.

        Args:
            code: str - Python solution code
            test_code: str - Test cases
            entry_point: str - Function name to test

        Returns:
            {
                "success": bool,
                "stdout": str,
                "stderr": str,
                "returncode": int
            }
        """
        ...

    def format_feedback(self, output: str) -> str:
        """Format pytest output for LLM feedback (≤1000 tokens).

        Args:
            output: str - Raw pytest stdout/stderr

        Returns:
            str - Formatted feedback (truncated if needed)
        """
        ...
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | MypyVerifier.verify | Copy from h-m1, return dict |
| L-3-2 | MypyVerifier.format_feedback | Truncate to 1000 token limit |
| L-3-3 | PytestVerifier.verify | Copy from h-m1, return dict |
| L-3-4 | PytestVerifier.format_feedback | Truncate to 1000 token limit |
| L-3-5 | Tempfile handling | Clean up after verification |
| L-3-6 | Timeout handling | Subprocess timeout logic |
| L-3-7 | Error handling | Catch subprocess exceptions |
| L-3-8 | Logging | Verification status logs |

---

## A-4: CASCADE Router Implementation [Complexity: 15, Budget: 15]

**Applied:** Conditional gating pattern with token tracking

### API Signatures

```python
class CascadeRouter:
    """Conditional feedback routing: mypy → (if clean) → pytest"""

    def __init__(self, generator: CodeLlamaGenerator, max_iterations: int = 10):
        """Initialize router.

        Args:
            generator: CodeLlamaGenerator - Code generation model
            max_iterations: int - Max feedback iterations
        """
        self.generator = generator
        self.max_iterations = max_iterations
        self.mypy_verifier = MypyVerifier(timeout=10)
        self.pytest_verifier = PytestVerifier(timeout=120)
        self.token_limit_per_source = 1000

    def solve_task(self, task_prompt: str, test_code: str, entry_point: str) -> Dict:
        """Solve task with conditional gating.

        Args:
            task_prompt: str - HumanEval problem prompt
            test_code: str - Test cases
            entry_point: str - Function name

        Returns:
            {
                "code": str,
                "iterations": int,
                "total_tokens": int,
                "mypy_tokens": int,
                "pytest_tokens": int,
                "gating_skipped_count": int,
                "success": bool
            }
        """
        ...

    def _iteration_step(self, prompt: str, test_code: str, entry_point: str) -> Tuple[str, str, int, bool]:
        """Single iteration: generate → mypy → (if clean) → pytest.

        Returns:
            (code, feedback, tokens_used, success)
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| prompt | [B=1, seq_len] | Input prompt tokens |
| generated | [B=1, max_new_tokens] | Generated code tokens |

### Pseudo-code

```
1. iteration = 0, prompt = task_prompt, total_tokens = 0, gating_skipped = 0
2. WHILE iteration < max_iterations:
   3. code = generator.generate(prompt)  # LLM generation
   4. mypy_result = mypy_verifier.verify(code)
   5. mypy_feedback = format_feedback(mypy_result["stderr"])
   6. mypy_tokens = count_tokens(mypy_feedback)
   7. total_tokens += mypy_tokens

   8. IF mypy_result["success"]:  # Gate OPEN
      9. pytest_result = pytest_verifier.verify(code, test_code, entry_point)
      10. pytest_feedback = format_feedback(pytest_result["stdout"])
      11. pytest_tokens = count_tokens(pytest_feedback)
      12. total_tokens += pytest_tokens
      13. IF pytest_result["success"]:
          14. RETURN success
      15. prompt = prompt + "\n\nTests failed:\n" + pytest_feedback
   16. ELSE:  # Gate CLOSED
      17. gating_skipped += 1
      18. prompt = prompt + "\n\nMypy errors:\n" + mypy_feedback

   19. iteration += 1
20. RETURN failure
```

### Subtasks [15/15 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Router initialization | Generator + verifiers setup |
| L-4-2 | Iteration loop | Max iterations control |
| L-4-3 | Code generation | Call generator.generate() |
| L-4-4 | Mypy verification | Always run mypy first |
| L-4-5 | Mypy feedback formatting | Truncate to token limit |
| L-4-6 | Token counting | Count mypy feedback tokens |
| L-4-7 | Conditional gate logic | Check mypy success |
| L-4-8 | Pytest verification | Run if gate open |
| L-4-9 | Pytest feedback formatting | Truncate to token limit |
| L-4-10 | Token counting | Count pytest feedback tokens |
| L-4-11 | Gating counter | Track skipped executions |
| L-4-12 | Success detection | Both mypy + pytest pass |
| L-4-13 | Prompt construction | Append feedback to prompt |
| L-4-14 | Result aggregation | Package metrics dict |
| L-4-15 | Logging | Per-iteration status |

---

## A-5: AGGREGATION Router Implementation [Complexity: 12, Budget: 12]

**Applied:** Simultaneous multi-source feedback pattern

### API Signatures

```python
class AggregationRouter:
    """Baseline: simultaneous mypy + pytest feedback"""

    def __init__(self, generator: CodeLlamaGenerator, max_iterations: int = 10):
        """Initialize router.

        Args:
            generator: CodeLlamaGenerator - Code generation model
            max_iterations: int - Max feedback iterations
        """
        self.generator = generator
        self.max_iterations = max_iterations
        self.mypy_verifier = MypyVerifier(timeout=10)
        self.pytest_verifier = PytestVerifier(timeout=120)
        self.token_limit_per_source = 1000

    def solve_task(self, task_prompt: str, test_code: str, entry_point: str) -> Dict:
        """Solve task with simultaneous feedback.

        Args:
            task_prompt: str - HumanEval problem prompt
            test_code: str - Test cases
            entry_point: str - Function name

        Returns:
            {
                "code": str,
                "iterations": int,
                "total_tokens": int,
                "mypy_tokens": int,
                "pytest_tokens": int,
                "success": bool
            }
        """
        ...

    def _iteration_step(self, prompt: str, test_code: str, entry_point: str) -> Tuple[str, str, int, bool]:
        """Single iteration: generate → mypy + pytest → concatenate.

        Returns:
            (code, combined_feedback, tokens_used, success)
        """
        ...
```

### Pseudo-code

```
1. iteration = 0, prompt = task_prompt, total_tokens = 0
2. WHILE iteration < max_iterations:
   3. code = generator.generate(prompt)

   4. mypy_result = mypy_verifier.verify(code)  # Always run
   5. pytest_result = pytest_verifier.verify(code, test_code, entry_point)  # Always run

   6. mypy_feedback = format_feedback(mypy_result["stderr"])
   7. pytest_feedback = format_feedback(pytest_result["stdout"])

   8. mypy_tokens = count_tokens(mypy_feedback)
   9. pytest_tokens = count_tokens(pytest_feedback)
   10. total_tokens += (mypy_tokens + pytest_tokens)

   11. IF mypy_result["success"] AND pytest_result["success"]:
       12. RETURN success

   13. combined_feedback = mypy_feedback + "\n\n" + pytest_feedback
   14. prompt = prompt + "\n\nFeedback:\n" + combined_feedback
   15. iteration += 1
16. RETURN failure
```

### Subtasks [12/12 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Router initialization | Generator + verifiers setup |
| L-5-2 | Iteration loop | Max iterations control |
| L-5-3 | Code generation | Call generator.generate() |
| L-5-4 | Mypy verification | Always run mypy |
| L-5-5 | Pytest verification | Always run pytest |
| L-5-6 | Mypy feedback formatting | Truncate to token limit |
| L-5-7 | Pytest feedback formatting | Truncate to token limit |
| L-5-8 | Token counting | Count both sources separately |
| L-5-9 | Success detection | Both must pass |
| L-5-10 | Feedback concatenation | Combine mypy + pytest |
| L-5-11 | Prompt construction | Append combined feedback |
| L-5-12 | Result aggregation | Package metrics dict |

---

## A-6: Token Counting Integration [Complexity: 7, Budget: 7]

**Applied:** Tokenizer-based counting pattern

### API Signatures

```python
class CodeLlamaGenerator:
    """Code generation with token counting"""

    def __init__(self, config: ExperimentConfig):
        """Initialize generator. config: [ExperimentConfig] model config"""
        self.config = config
        self.model = None
        self.tokenizer = None

    def load_model(self) -> None:
        """Load CodeLlama-7B with FP16 and device_map='auto'"""
        ...

    def generate(self, prompt: str) -> str:
        """Generate code from prompt.

        Args:
            prompt: str - Task description + feedback history

        Returns:
            str - Generated code completion
        """
        ...

    def count_tokens(self, text: str) -> int:
        """Count tokens in text.

        Args:
            text: str - Text to count

        Returns:
            int - Number of tokens
        """
        return len(self.tokenizer.encode(text))
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Tokenizer initialization | Load CodeLlama tokenizer |
| L-6-2 | count_tokens method | Encode + len() |
| L-6-3 | Integration in CASCADE | Call count_tokens for mypy/pytest |
| L-6-4 | Integration in AGGREGATION | Call count_tokens for both |
| L-6-5 | Token limit enforcement | Truncate feedback to 1000 |
| L-6-6 | Unit test | Validate counting accuracy |
| L-6-7 | Logging | Token counts per iteration |

---

## A-7: Efficiency Metric Computation [Complexity: 10, Budget: 10]

**Applied:** Statistical aggregation pattern

### API Signatures

```python
class TokenEfficiencyAnalyzer:
    """Compute token efficiency metrics"""

    def __init__(self, threshold: float = 1.15):
        """Initialize analyzer. threshold: [float] efficiency ratio gate (≤1.15)"""
        self.threshold = threshold

    def compute_tokens_per_task(self, results: List[Dict]) -> Dict:
        """Compute primary metric: tokens per successful task.

        Args:
            results: List[Dict] - Task results from router

        Returns:
            {
                "tokens_per_task": float,
                "successful_tasks": int,
                "total_tokens": int,
                "mean_iterations": float
            }
        """
        ...

    def compute_efficiency_ratio(self, cascade_metrics: Dict, aggregation_metrics: Dict) -> float:
        """Compute CASCADE / AGGREGATION ratio.

        Returns:
            float - Efficiency ratio (≤1.15 passes gate)
        """
        return cascade_metrics["tokens_per_task"] / aggregation_metrics["tokens_per_task"]

    def validate_gate(self, ratio: float) -> bool:
        """Check if ratio ≤ threshold. Returns: [bool] gate passed"""
        return ratio <= self.threshold
```

### Pseudo-code

```
1. Filter results to successful only: successful = [r for r in results if r["success"]]
2. IF no successful tasks: RETURN inf
3. total_tokens = sum(r["total_tokens"] for r in successful)
4. tokens_per_task = total_tokens / len(successful)
5. mean_iterations = sum(r["iterations"] for r in successful) / len(successful)
6. RETURN metrics dict
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Filter successful | success=True only |
| L-7-2 | Total token sum | Aggregate across tasks |
| L-7-3 | Tokens per task | Divide by successful count |
| L-7-4 | Mean iterations | Average convergence |
| L-7-5 | Efficiency ratio | CASCADE / AGGREGATION |
| L-7-6 | Gate validation | Check ≤1.15 threshold |
| L-7-7 | Edge case handling | Zero successful tasks |
| L-7-8 | Metrics packaging | Return structured dict |
| L-7-9 | Logging | Metric computation logs |
| L-7-10 | Unit test | Validate calculations |

---

## A-8: Secondary Metrics Analysis [Complexity: 9, Budget: 9]

**Applied:** Exploratory analysis pattern

### API Signatures

```python
class TokenEfficiencyAnalyzer:
    """Extended with secondary metrics"""

    def compute_secondary_metrics(self, cascade_results: List, aggregation_results: List) -> Dict:
        """Compute exploratory metrics.

        Returns:
            {
                "gating_efficiency_pct": float,  # % iterations skipped
                "cascade_token_breakdown": {"mypy": int, "pytest": int},
                "aggregation_token_breakdown": {"mypy": int, "pytest": int},
                "success_rates": {"cascade": float, "aggregation": float}
            }
        """
        ...
```

### Pseudo-code

```
1. gating_skipped = sum(r["gating_skipped_count"] for r in cascade_results)
2. total_iterations = sum(r["iterations"] for r in cascade_results)
3. gating_efficiency = (gating_skipped / total_iterations) * 100

4. cascade_mypy = sum(r["mypy_tokens"] for r in cascade_results)
5. cascade_pytest = sum(r["pytest_tokens"] for r in cascade_results)

6. aggregation_mypy = sum(r["mypy_tokens"] for r in aggregation_results)
7. aggregation_pytest = sum(r["pytest_tokens"] for r in aggregation_results)

8. cascade_success_rate = sum(r["success"] for r in cascade_results) / len(cascade_results)
9. aggregation_success_rate = sum(r["success"] for r in aggregation_results) / len(aggregation_results)

10. RETURN metrics dict
```

### Subtasks [9/9 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | Gating efficiency | % pytest skipped in CASCADE |
| L-8-2 | Token breakdown | Mypy vs pytest contribution |
| L-8-3 | Success rate | % tasks solved per condition |
| L-8-4 | CASCADE analysis | Aggregate CASCADE metrics |
| L-8-5 | AGGREGATION analysis | Aggregate AGGREGATION metrics |
| L-8-6 | Comparison | CASCADE vs AGGREGATION breakdown |
| L-8-7 | Metrics packaging | Structure output dict |
| L-8-8 | Logging | Secondary metrics logs |
| L-8-9 | Validation | Check metric consistency |

---

## A-9: Visualization Generation [Complexity: 10, Budget: 10]

**Applied:** Matplotlib plotting pattern

### API Signatures

```python
class ExperimentVisualizer:
    """Generate experiment figures"""

    def __init__(self, output_dir: Path):
        """Initialize visualizer. output_dir: [Path] figures directory"""
        self.output_dir = output_dir

    def plot_gate_metrics(self, target: float, actual: float, passed: bool) -> None:
        """Gate validation figure (threshold vs actual ratio)"""
        ...

    def plot_token_efficiency_comparison(self, cascade_metrics: Dict, aggregation_metrics: Dict) -> None:
        """Bar chart: CASCADE vs AGGREGATION tokens-per-task"""
        ...

    def plot_token_breakdown(self, cascade_results: List, aggregation_results: List) -> None:
        """Stacked bar: mypy vs pytest token contribution"""
        ...

    def plot_gating_efficiency(self, cascade_results: List) -> None:
        """Histogram: % execution skipped in CASCADE"""
        ...

    def plot_iterations_comparison(self, cascade_results: List, aggregation_results: List) -> None:
        """Box plot: convergence iterations both conditions"""
        ...
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | Gate metrics figure | Threshold vs actual ratio |
| L-9-2 | Token efficiency figure | CASCADE vs AGGREGATION bar |
| L-9-3 | Token breakdown figure | Mypy vs pytest stacked bar |
| L-9-4 | Gating efficiency figure | % skipped histogram |
| L-9-5 | Iterations figure | Convergence box plot |
| L-9-6 | Matplotlib setup | Seaborn style, figure size |
| L-9-7 | Color scheme | Consistent colors across plots |
| L-9-8 | Axis labels | Clear annotations |
| L-9-9 | Save figures | PNG @ 300 DPI |
| L-9-10 | Logging | Figure generation logs |

---

## A-10: Pipeline Orchestration [Complexity: 11, Budget: 11]

**Applied:** Stage-based pipeline pattern

### API Signatures

```python
class TokenEfficiencyPipeline:
    """Main experiment pipeline orchestrator"""

    def __init__(self, config: ExperimentConfig):
        """Initialize pipeline. config: [ExperimentConfig] experiment config"""
        self.config = config
        self.loader = None
        self.generator = None
        self.cascade_router = None
        self.aggregation_router = None
        self.analyzer = None
        self.visualizer = None

    def run(self) -> Dict:
        """Execute full pipeline.

        Returns:
            {
                "cascade_results": List[Dict],
                "aggregation_results": List[Dict],
                "metrics": Dict,
                "gate_satisfied": bool
            }
        """
        ...

    def stage_load_qualified_tasks(self) -> Dict[str, Dict]:
        """Stage 1: Load N=20 dual-sensitive tasks"""
        ...

    def stage_cascade_evaluation(self, tasks: Dict) -> List[Dict]:
        """Stage 2: Evaluate with CASCADE router"""
        ...

    def stage_aggregation_evaluation(self, tasks: Dict) -> List[Dict]:
        """Stage 3: Evaluate with AGGREGATION router"""
        ...

    def stage_analyze_efficiency(self, cascade_results: List, aggregation_results: List) -> Dict:
        """Stage 4: Compute token efficiency metrics"""
        ...

    def stage_generate_visualizations(self, cascade_results: List, aggregation_results: List, metrics: Dict) -> None:
        """Stage 5: Generate 5 figures"""
        ...

    def stage_validate_gate(self, metrics: Dict) -> Dict:
        """Stage 6: Validate ≤1.15 gate"""
        ...

    def save_results(self, results: Dict, path: Path) -> None:
        """Save results to JSON"""
        ...

def main():
    """Entry point"""
    config = ExperimentConfig()
    pipeline = TokenEfficiencyPipeline(config)
    results = pipeline.run()
    print(f"Gate status: {results['gate_satisfied']}")
```

### Pseudo-code

```
1. Initialize all components (loader, generator, routers, analyzer, visualizer)
2. Load N=20 qualified tasks from h-e1
3. FOR each task:
   4. result_cascade = cascade_router.solve_task(task)
   5. result_aggregation = aggregation_router.solve_task(task)
   6. Save intermediate checkpoint every 5 tasks
7. Compute primary metrics (tokens-per-task, efficiency ratio)
8. Compute secondary metrics (gating efficiency, token breakdown)
9. Generate 5 figures
10. Validate gate (ratio ≤ 1.15)
11. Save final results to JSON
12. RETURN results
```

### Subtasks [11/11 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-10-1 | Component initialization | All classes setup |
| L-10-2 | Stage 1 | Load qualified tasks |
| L-10-3 | Stage 2 | CASCADE evaluation loop |
| L-10-4 | Stage 3 | AGGREGATION evaluation loop |
| L-10-5 | Stage 4 | Metric computation |
| L-10-6 | Stage 5 | Visualization generation |
| L-10-7 | Stage 6 | Gate validation |
| L-10-8 | Checkpoint saving | Progressive results save |
| L-10-9 | Error handling | Stage failure recovery |
| L-10-10 | Logging | Pipeline progress logs |
| L-10-11 | Results packaging | Final output dict |

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

The following base classes from h-m1 will be COPIED and ADAPTED (not imported):

```python
# From: h-m1/code/run_experiment.py (ACTUAL CODE - lines 50-199)

class HumanEvalLoader:
    def __init__(self, use_evalplus: bool = True):
        """Initialize loader"""
        self.use_evalplus = use_evalplus
        self.problems = None

    def load_problems(self) -> Dict[str, Dict]:
        """Load all 164 HumanEval tasks. Returns: {task_id: problem_dict}"""
        # From evalplus.data import get_human_eval_plus (line 62)
        # Returns dict with keys: prompt, entry_point, test, canonical_solution
        ...

class CodeLlamaGenerator:
    def __init__(self, config: ExperimentConfig):
        """Initialize generator"""
        self.config = config
        self.model = None
        self.tokenizer = None

    def load_model(self):
        """Load model with FP16 and auto device mapping (lines 92-98)"""
        # AutoTokenizer.from_pretrained(model_name)
        # AutoModelForCausalLM.from_pretrained(torch_dtype=float16, device_map="auto")
        ...

    def generate_samples(self, prompt: str, k: int = None) -> List[str]:
        """Generate K samples (lines 100-124)"""
        # model.generate(max_length, temperature, top_p, top_k, do_sample=True)
        # Note: H-m1 uses k samples, h-m3 needs single generation per iteration
        ...

class MypyVerifier:
    def __init__(self, timeout: int = 10):
        """Initialize verifier"""
        self.timeout = timeout

    def verify(self, code: str) -> bool:
        """Verify code with mypy --strict (lines 132-155)"""
        # Creates temp file, runs subprocess ['mypy', '--strict', temp_path]
        # Returns: (returncode == 0)
        # Note: H-m3 needs stderr capture for feedback
        ...

class PytestVerifier:
    def __init__(self, timeout: int = 120):
        """Initialize verifier"""
        self.timeout = timeout

    def verify(self, code: str, test_code: str) -> bool:
        """Verify code with pytest (lines 167-195)"""
        # Creates temp dir, writes solution.py and test_solution.py
        # Runs subprocess ['pytest', test_file, '-v', '--tb=short']
        # Returns: (returncode == 0)
        # Note: H-m3 needs stdout capture for feedback
        ...
```

**Verified from:** h-m1/code/run_experiment.py (actual implementation)

**Adaptation Notes for H-M3:**
1. **HumanEvalLoader:** Add `load_qualified_task_ids()` method (NEW)
2. **CodeLlamaGenerator:** Change `generate_samples()` to `generate()` for single output (MODIFIED)
3. **CodeLlamaGenerator:** Add `count_tokens()` method (NEW)
4. **MypyVerifier:** Change return from bool to Dict with stderr (MODIFIED)
5. **MypyVerifier:** Add `format_feedback()` method (NEW)
6. **PytestVerifier:** Change return from bool to Dict with stdout (MODIFIED)
7. **PytestVerifier:** Add `format_feedback()` method (NEW)
8. **PytestVerifier:** Add `entry_point` parameter to verify() (MODIFIED)

---

## Budget Summary

| Task | Complexity | Subtasks Allocated | Subtasks Used |
|------|------------|-------------------|---------------|
| A-1: Setup | 5 | 5 | 5 |
| A-2: Task Loader | 7 | 7 | 7 |
| A-3: Verification | 8 | 8 | 8 |
| A-4: CASCADE Router | 15 | 15 | 15 |
| A-5: AGGREGATION Router | 12 | 12 | 12 |
| A-6: Token Counting | 7 | 7 | 7 |
| A-7: Efficiency Metrics | 10 | 10 | 10 |
| A-8: Secondary Metrics | 9 | 9 | 9 |
| A-9: Visualization | 10 | 10 | 10 |
| A-10: Pipeline | 11 | 11 | 11 |
| **Total** | **94** | **94** | **94** |

**Budget Status:** 94/94 subtasks used (100% utilization, within 10× base budget of 10)

---

## Implementation Notes

### Key Differences from H-M1
1. **Iterative feedback:** Up to 10 iterations per task (vs h-m1's single-pass K=20 samples)
2. **Token tracking:** Primary metric (vs h-m1's classification)
3. **Dual routers:** CASCADE vs AGGREGATION comparison (NEW)
4. **Feedback formatting:** Truncate to 1000 token limit (NEW)
5. **Conditional gating:** Skip pytest when mypy fails (NEW in CASCADE)

### Critical Implementation Details

**Token Counting:**
```python
def count_tokens(self, text: str) -> int:
    return len(self.tokenizer.encode(text))
```

**Feedback Truncation:**
```python
def format_feedback(self, raw_output: str) -> str:
    tokens = self.tokenizer.encode(raw_output)
    if len(tokens) > 1000:
        tokens = tokens[:1000]
    return self.tokenizer.decode(tokens)
```

**Gate Logic (CASCADE only):**
```python
if mypy_result["success"]:  # Gate OPEN
    pytest_result = pytest_verifier.verify(code, test_code, entry_point)
    # Run pytest only when mypy clean
else:  # Gate CLOSED
    gating_skipped += 1
    # Skip pytest, give only mypy feedback
```

### Success Criteria Recap
- **Primary Gate:** `cascade_tokens_per_task / aggregation_tokens_per_task ≤ 1.15`
- **Secondary:** Gating efficiency ≥60%, success rates similar between conditions
- **SHOULD_WORK:** Failure documented, workflow continues to h-c1

---

**Generated by Phase 3 Logic Agent**
**Source:** 03_architecture.md, 03_prd.md, h-m1/code/run_experiment.py
**Next:** Phase 4 - Implementation (Coder Agent)
**Token Budget:** 94 subtasks allocated and fully utilized
