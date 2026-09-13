# Logic Design: h-e1 Execution Trace Feature Extraction

**Hypothesis:** h-e1 (EXISTENCE)  
**Date:** 2026-04-15  
**Author:** Logic Agent  
**Type:** Data Infrastructure Validation  

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** Foundation hypothesis - no existing code to analyze  
**Analyzed Path:** N/A  
**Relevant Symbols:** None - new implementation  
**Note:** Archon MCP and Serena MCP not available - using domain knowledge and best practices

---

## Design Patterns Applied

**Applied:** ETL Pipeline Pattern (Extract-Transform-Load for benchmark data)  
**Applied:** Strategy Pattern (Multiple benchmark loaders with common interface)  
**Applied:** Sandbox Pattern (Isolated code execution environment)  
**Applied:** Repository Pattern (Standardized data access across benchmarks)

---

## A-3: Feature Extraction Pipeline [Complexity: 12, Budget: 3]

**Applied:** Statistical Computing Pattern (NumPy-based percentile calculations)

### API Signatures

```python
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

class ExecutionTraceExtractor:
    """Extract execution trace features from benchmark evaluation results."""
    
    def __init__(self, benchmark_name: str):
        """
        Initialize extractor for specific benchmark.
        
        Args:
            benchmark_name: One of ["HumanEval", "MBPP", "APPS"]
        """
        self.benchmark_name = benchmark_name
        self.feature_schema = {
            'pass@1': float, 'pass@10': float, 'pass@100': float,
            'runtime_q25': float, 'runtime_q50': float, 'runtime_q75': float,
            'error_syntax': float, 'error_runtime': float, 'error_timeout': float
        }
    
    def extract_passk(
        self, 
        model_outputs: List[Dict[str, any]], 
        k_values: List[int] = [1, 10, 100]
    ) -> Dict[str, float]:
        """
        Calculate pass@k metrics using Chen et al. 2021 formula.
        
        Args:
            model_outputs: List of evaluation results per problem
                Each dict: {"problem_id": str, "n_samples": int, "n_correct": int}
            k_values: List of k values to compute [1, 10, 100]
        
        Returns:
            Dict with keys "pass@1", "pass@10", "pass@100"
        """
        ...
    
    def extract_runtime_quartiles(
        self, 
        passing_solutions: List[Dict[str, any]]
    ) -> Dict[str, float]:
        """
        Compute runtime distribution quartiles for passing solutions.
        
        Args:
            passing_solutions: List of successful executions
                Each dict: {"problem_id": str, "runtime_ms": float}
        
        Returns:
            Dict with keys "runtime_q25", "runtime_q50", "runtime_q75" (ms)
        """
        ...
    
    def categorize_errors(
        self, 
        failed_solutions: List[Dict[str, any]]
    ) -> Dict[str, float]:
        """
        Categorize error types and compute distribution percentages.
        
        Args:
            failed_solutions: List of failed executions
                Each dict: {"problem_id": str, "error_type": str}
        
        Returns:
            Dict with keys "error_syntax", "error_runtime", "error_timeout" (percentages)
        """
        ...
    
    def extract_all_features(
        self, 
        model_name: str, 
        evaluation_results: Dict[str, any]
    ) -> Dict[str, any]:
        """
        Extract complete feature vector for one model-benchmark pair.
        
        Args:
            model_name: Model identifier
            evaluation_results: {
                "outputs": List[Dict],  # model_outputs for pass@k
                "passing": List[Dict],   # passing_solutions for runtime
                "failed": List[Dict]     # failed_solutions for errors
            }
        
        Returns:
            Complete feature dict with all 9 features + metadata
        """
        ...
```

### Pseudo-code

#### L-3-1: Pass@k Calculation Algorithm

```
Input: model_outputs (list of {n_samples, n_correct} per problem), k_values
Output: {pass@1: float, pass@10: float, pass@100: float}

Algorithm (Chen et al. 2021):
1. For each k in k_values:
   a. For each problem in model_outputs:
      - n = problem.n_samples
      - c = problem.n_correct
      - If c >= k:
          prob_problem = 1.0  # guaranteed to pass
      - Else if c == 0:
          prob_problem = 0.0  # impossible to pass
      - Else:
          prob_problem = 1 - comb(n-c, k) / comb(n, k)
   b. pass@k = mean(prob_problem across all problems)
2. Return {"pass@1": val1, "pass@10": val10, "pass@100": val100}

Note: comb(n, k) = n! / (k! * (n-k)!)
Handle edge cases: n < k → prob = 0 if c == 0, else 1.0
```

#### L-3-2: Runtime Quartile Extraction Logic

```
Input: passing_solutions (list of {runtime_ms: float})
Output: {runtime_q25: float, runtime_q50: float, runtime_q75: float}

Algorithm:
1. Extract runtimes = [sol.runtime_ms for sol in passing_solutions]
2. If len(runtimes) == 0:
   - Return {q25: None, q50: None, q75: None}
3. Compute quartiles using NumPy:
   - q25 = np.percentile(runtimes, 25)
   - q50 = np.percentile(runtimes, 50)  # median
   - q75 = np.percentile(runtimes, 75)
4. Return quartile dict

Outlier Handling: Cap at 99th percentile to exclude extreme outliers
```

#### L-3-3: Error Categorization Logic

```
Input: failed_solutions (list of {error_type: str})
Output: {error_syntax: %, error_runtime: %, error_timeout: %}

Algorithm:
1. Initialize counters: {syntax: 0, runtime: 0, timeout: 0}
2. For each failure in failed_solutions:
   - error_type = failure.error_type
   - counters[error_type] += 1
3. total = sum(counters.values())
4. If total == 0:
   - Return {syntax: None, runtime: None, timeout: None}
5. Compute percentages:
   - error_syntax = (counters.syntax / total) * 100
   - error_runtime = (counters.runtime / total) * 100
   - error_timeout = (counters.timeout / total) * 100
6. Return percentage dict

Error Type Mapping:
- SyntaxError, IndentationError → "syntax"
- RuntimeError, AssertionError, ValueError, etc. → "runtime"
- TimeoutError, subprocess.TimeoutExpired → "timeout"
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Pass@k calculation | Implement Chen et al. formula with combinatorial probability |
| L-3-2 | Runtime quartile extraction | NumPy percentile computation with outlier handling |
| L-3-3 | Error categorization | Map exception types to three categories, compute distribution |

---

## A-4: Code Execution Sandbox [Complexity: 11, Budget: 3]

**Applied:** Process Isolation Pattern (subprocess with timeout)

### API Signatures

```python
from typing import Tuple, Dict, Optional
import subprocess
from enum import Enum

class ExecutionStatus(Enum):
    """Execution outcome categories."""
    SUCCESS = "success"
    SYNTAX_ERROR = "syntax"
    RUNTIME_ERROR = "runtime"
    TIMEOUT = "timeout"

class CodeExecutor:
    """Safe execution environment for code solutions."""
    
    def __init__(
        self, 
        timeout: int = 30, 
        use_sandbox: bool = True,
        max_memory_mb: int = 512
    ):
        """
        Initialize code executor with safety constraints.
        
        Args:
            timeout: Maximum execution time in seconds
            use_sandbox: Use isolated subprocess (True recommended)
            max_memory_mb: Memory limit per execution
        """
        self.timeout = timeout
        self.use_sandbox = use_sandbox
        self.max_memory_mb = max_memory_mb
    
    def execute_solution(
        self, 
        code: str, 
        test_case: Dict[str, any]
    ) -> Tuple[ExecutionStatus, Optional[float], Optional[str]]:
        """
        Execute code solution on single test case with timeout protection.
        
        Args:
            code: Python code string to execute
            test_case: {"input": str, "expected_output": str, "test_fn": Optional[str]}
        
        Returns:
            Tuple of (status, runtime_ms, error_message)
            - status: ExecutionStatus enum
            - runtime_ms: Execution time in ms (None if failed)
            - error_message: Error details (None if success)
        """
        ...
    
    def measure_runtime(
        self, 
        code: str, 
        test_case: Dict[str, any],
        n_trials: int = 3
    ) -> float:
        """
        Measure runtime with multiple trials, return median.
        
        Args:
            code: Python code to benchmark
            test_case: Test case specification
            n_trials: Number of trials for robust measurement
        
        Returns:
            Median runtime in milliseconds
        """
        ...
    
    def categorize_error(
        self, 
        error: Exception
    ) -> str:
        """
        Categorize exception into standard error types.
        
        Args:
            error: Exception object from execution
        
        Returns:
            One of ["syntax", "runtime", "timeout"]
        """
        ...
```

### Pseudo-code

#### L-4-1: Safe Execution API

```
Input: code (str), test_case (dict with input/expected_output)
Output: (ExecutionStatus, runtime_ms, error_message)

Algorithm:
1. Prepare execution environment:
   - Create temporary file with code
   - Wrap code with test case execution logic
   - Add assertion: actual_output == expected_output

2. Execute in isolated subprocess:
   - Command: ["python", "-c", wrapped_code]
   - Set timeout: self.timeout seconds
   - Capture stdout, stderr
   - Start timer

3. Handle execution outcomes:
   a. If syntax error (before execution starts):
      - Return (SYNTAX_ERROR, None, error_msg)
   
   b. If timeout expires:
      - Kill subprocess
      - Return (TIMEOUT, None, "Execution exceeded Xs")
   
   c. If runtime exception:
      - Parse stderr for exception type
      - Return (RUNTIME_ERROR, None, exception_msg)
   
   d. If assertion fails:
      - Return (RUNTIME_ERROR, None, "Output mismatch")
   
   e. If success:
      - Stop timer, compute runtime_ms
      - Return (SUCCESS, runtime_ms, None)

4. Cleanup temporary files
```

#### L-4-2: Timeout Handling Mechanism

```
Input: subprocess handle, timeout (seconds)
Output: Controlled termination or result

Mechanism (using subprocess.run):
1. Launch subprocess with timeout parameter:
   result = subprocess.run(
       cmd,
       timeout=timeout,
       capture_output=True,
       text=True
   )

2. Exception handling:
   try:
       result = subprocess.run(...)
   except subprocess.TimeoutExpired:
       - Log timeout event
       - Kill process forcefully if still alive
       - Return TIMEOUT status

3. Graceful degradation:
   - If timeout too aggressive: log warning
   - If process hangs: force terminate after timeout + 5s grace period

Resource Limits (Linux):
- Use resource.setrlimit() for memory cap
- Disable network access (optional)
- Restrict file I/O (optional)
```

#### L-4-3: Error Capture and Classification

```
Input: Exception object or stderr output
Output: Error category ("syntax", "runtime", "timeout")

Classification Rules:
1. Syntax Errors:
   - Exception types: SyntaxError, IndentationError, NameError (at parse time)
   - Pattern match in stderr: "SyntaxError:", "IndentationError:"

2. Runtime Errors:
   - Exception types: AssertionError, ValueError, TypeError, AttributeError, 
                      KeyError, IndexError, ZeroDivisionError, etc.
   - Pattern match in stderr: "Traceback", "Error:", except syntax/timeout

3. Timeout Errors:
   - Exception type: subprocess.TimeoutExpired
   - Pattern match: "timed out", "timeout expired"

Algorithm:
1. If isinstance(error, subprocess.TimeoutExpired):
   - Return "timeout"

2. error_msg = str(error) or stderr
3. If "SyntaxError" in error_msg or "IndentationError" in error_msg:
   - Return "syntax"

4. Else:
   - Return "runtime"  # Default for all execution failures

Edge Cases:
- NameError at import time → "syntax"
- NameError during execution → "runtime"
- Use AST parsing to distinguish parse-time vs runtime errors
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Safe execution API | Subprocess-based isolated execution with resource limits |
| L-4-2 | Timeout handling | subprocess.run with timeout, graceful termination |
| L-4-3 | Error capture and classification | Parse stderr/exceptions into three categories |

---

## Data Structures

### Feature Vector Schema

```python
# Complete feature vector for one model-benchmark pair
FeatureVector = {
    "model": str,              # "CodeLlama-7B"
    "benchmark": str,          # "HumanEval" | "MBPP" | "APPS"
    "pass@1": float,           # 0.0 - 100.0
    "pass@10": float,          # 0.0 - 100.0
    "pass@100": float,         # 0.0 - 100.0
    "runtime_q25": float,      # milliseconds, None if unavailable
    "runtime_q50": float,      # milliseconds (median)
    "runtime_q75": float,      # milliseconds
    "error_syntax": float,     # percentage (0.0 - 100.0)
    "error_runtime": float,    # percentage
    "error_timeout": float     # percentage
}

# Evaluation results input format
EvaluationResults = {
    "outputs": List[{
        "problem_id": str,
        "n_samples": int,      # Number of generated solutions
        "n_correct": int       # Number passing all tests
    }],
    "passing": List[{
        "problem_id": str,
        "solution_id": int,
        "runtime_ms": float
    }],
    "failed": List[{
        "problem_id": str,
        "solution_id": int,
        "error_type": str      # "syntax" | "runtime" | "timeout"
    }]
}
```

### Test Case Format

```python
# Benchmark test case specification
TestCase = {
    "problem_id": str,         # "HumanEval/0"
    "input": str,              # Function input or args
    "expected_output": any,    # Expected return value
    "test_fn": Optional[str]   # Custom test function if assertion logic complex
}

# Execution result
ExecutionResult = {
    "problem_id": str,
    "solution_id": int,
    "status": ExecutionStatus,  # SUCCESS | SYNTAX_ERROR | RUNTIME_ERROR | TIMEOUT
    "runtime_ms": Optional[float],
    "error_message": Optional[str],
    "stdout": str,
    "stderr": str
}
```

---

## Integration Points

### A-3 ↔ A-4 Integration

```python
# CodeExecutor (A-4) produces ExecutionResults
# ExecutionTraceExtractor (A-3) consumes them

# Example flow:
executor = CodeExecutor(timeout=30)
extractor = ExecutionTraceExtractor("HumanEval")

# A-4: Execute solutions
execution_results = []
for solution in model_solutions:
    status, runtime, error = executor.execute_solution(solution.code, test_case)
    execution_results.append({
        "status": status,
        "runtime_ms": runtime,
        "error_type": executor.categorize_error(error) if error else None
    })

# A-3: Extract features from execution results
passing = [r for r in execution_results if r["status"] == ExecutionStatus.SUCCESS]
failed = [r for r in execution_results if r["status"] != ExecutionStatus.SUCCESS]

features = extractor.extract_all_features(
    model_name="CodeLlama-7B",
    evaluation_results={
        "outputs": compute_passk_inputs(execution_results),
        "passing": passing,
        "failed": failed
    }
)
```

### External Dependencies Usage

```python
# NumPy for statistical computations (A-3)
import numpy as np
quartiles = np.percentile(runtimes, [25, 50, 75])

# SciPy for combinatorics (A-3, pass@k calculation)
from scipy.special import comb
probability = 1 - comb(n - c, k) / comb(n, k)

# Subprocess for isolation (A-4)
import subprocess
result = subprocess.run(
    ["python", "-c", code],
    timeout=30,
    capture_output=True,
    text=True
)

# Resource limits (A-4, optional)
import resource
resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
```

---

## Validation Logic

### Feature Completeness Calculation

```python
def calculate_completeness(feature_df: pd.DataFrame) -> float:
    """
    Calculate percentage of complete model-benchmark pairs.
    
    Args:
        feature_df: DataFrame with columns from FeatureVector schema
    
    Returns:
        Completeness percentage (0.0 - 100.0)
    """
    required_features = [
        'pass@1', 'pass@10', 'pass@100',
        'runtime_q25', 'runtime_q50', 'runtime_q75',
        'error_syntax', 'error_runtime', 'error_timeout'
    ]
    
    total_pairs = len(feature_df)
    complete_pairs = 0
    
    for _, row in feature_df.iterrows():
        if all(pd.notna(row[feat]) for feat in required_features):
            complete_pairs += 1
    
    return (complete_pairs / total_pairs) * 100 if total_pairs > 0 else 0.0
```

### Gate Condition Check

```python
def validate_gate_condition(completeness_rate: float, threshold: float = 95.0) -> bool:
    """
    Validate EXISTENCE hypothesis gate condition.
    
    Args:
        completeness_rate: Calculated completeness percentage
        threshold: Minimum required completeness (default 95%)
    
    Returns:
        True if gate passed, False otherwise
    """
    return completeness_rate >= threshold
```

---

## Complexity Justification

### A-3: Feature Extraction Pipeline (Complexity 12)
- **Module_Size (3):** ~150 lines (4 methods, statistical logic)
- **Dependencies (2):** NumPy, SciPy, Pandas
- **Algorithm (4):** Pass@k combinatorics, percentile computation, error categorization
- **Integration (3):** Consumes A-4 outputs, feeds validation/visualization

### A-4: Code Execution Sandbox (Complexity 11)
- **Module_Size (3):** ~120 lines (3 methods, subprocess handling)
- **Dependencies (3):** subprocess, resource, tempfile, enum
- **Algorithm (2):** Timeout mechanism, error classification
- **Integration (3):** Provides execution data to A-3, critical for runtime/error features

---

## Error Handling Strategy

### Graceful Degradation

```python
# Missing features → None (not zero)
if len(passing_solutions) == 0:
    runtime_features = {
        "runtime_q25": None,
        "runtime_q50": None,
        "runtime_q75": None
    }

# Log missing data reasons
missing_data_log = {
    "model": "GPT-4",
    "benchmark": "APPS",
    "missing_features": ["runtime_q25", "runtime_q50", "runtime_q75"],
    "reason": "No open-source implementation for re-execution"
}
```

### Execution Failures

```python
# Retry logic for transient failures
MAX_RETRIES = 3
for attempt in range(MAX_RETRIES):
    try:
        status, runtime, error = executor.execute_solution(code, test_case)
        break
    except OSError as e:  # System-level failures
        if attempt == MAX_RETRIES - 1:
            status = ExecutionStatus.RUNTIME_ERROR
            error = f"System error after {MAX_RETRIES} retries: {e}"
        time.sleep(1)
```

---

## Budget Summary

**Total Subtasks Allocated: 6**

| Epic | Subtasks Used | Remaining |
|------|---------------|-----------|
| A-3  | 3             | 0         |
| A-4  | 3             | 0         |

**All subtasks within budget.** ✓

---

**Document Status:** Final Logic Design for Phase 4 Implementation  
**Next Phase:** Phase 4 - Implementation (Coding)  
**Validation:** All API signatures copy-paste ready, algorithms specified, budget respected
