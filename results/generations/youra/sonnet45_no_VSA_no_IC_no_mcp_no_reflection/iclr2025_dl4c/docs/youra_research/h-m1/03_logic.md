# Logic Design: h-m1 Error Clustering Analyzer

**Date:** 2026-08-28  
**Hypothesis:** h-m1 (Error clustering in debug sessions)  
**Project Type:** Green-field  
**Phase:** 3 (Logic Design)

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New API design - no existing codebase  
**Analyzed Path**: N/A  
**Relevant Symbols**: None - new implementation

---

## Core API Signatures

### Main Evaluation Loop

```python
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class ErrorType(Enum):
    SYNTAX = "syntax"
    RUNTIME = "runtime"
    LOGIC = "logic"
    EDGE_CASE = "edge_case"

@dataclass
class TestFailure:
    test_id: int
    iteration: int
    error_msg: str
    input_data: str
    expected: str
    actual: str
    error_type: Optional[ErrorType] = None

@dataclass
class DebugSession:
    problem_id: str
    iterations: List[Dict]  # [{"passing": int, "failing": List[int]}]
    fix_sequence: List[int]  # Test IDs in fix order
    failures: List[TestFailure]

def run_evaluation(
    problem_ids: List[str],
    model: str = "gpt-4-turbo-2024-04-09",
    max_iterations: int = 10,
    seed: int = 1
) -> List[DebugSession]:
    """Run full evaluation pipeline. Returns sessions for all problems."""
    ...

def run_debug_session(
    problem: Dict,
    model: str,
    max_iterations: int = 10,
    timeout: float = 5.0
) -> DebugSession:
    """Single problem debug loop. Returns fix sequence and failures."""
    ...
```

### Clustering Analysis

```python
def clustering_coefficient(
    fix_sequence: List[int],
    error_labels: Dict[int, ErrorType]
) -> float:
    """
    Compute clustering coefficient.
    
    Args:
        fix_sequence: Test IDs in order fixed [t1, t2, t3, ...]
        error_labels: {test_id: ErrorType}
    
    Returns:
        observed_consecutive_same / expected_random
    """
    ...

def permutation_test(
    fix_sequence: List[int],
    error_labels: Dict[int, ErrorType],
    n_permutations: int = 1000,
    seed: int = 1
) -> Tuple[float, float]:
    """
    Test significance vs random.
    
    Returns:
        (clustering_coeff_observed, p_value)
    """
    ...

def cohens_kappa(
    annotations: List[Dict[int, ErrorType]]  # One dict per annotator
) -> float:
    """Compute inter-annotator agreement. Returns kappa score."""
    ...
```

### Error Annotation

```python
def annotate_errors(
    failures: List[TestFailure],
    num_annotators: int = 2
) -> Dict[int, ErrorType]:
    """
    Multi-annotator workflow with conflict resolution.
    
    Args:
        failures: Test failures to annotate
        num_annotators: Number of independent annotators
    
    Returns:
        Consensus labels {test_id: ErrorType}
    """
    ...

def resolve_conflicts(
    annotations: List[Dict[int, ErrorType]]
) -> Dict[int, ErrorType]:
    """Majority vote or flag for 3rd annotator. Returns consensus."""
    ...
```

### Problem Curation

```python
def fetch_problems(
    min_rating: int = 1200,
    max_rating: int = 1800,
    min_solves: int = 1000,
    min_tests: int = 15,
    count: int = 50
) -> List[Dict]:
    """Fetch Codeforces problems. Returns problem metadata."""
    ...

def execute_tests(
    code: str,
    test_cases: List[Tuple[str, str]],
    timeout: float = 5.0
) -> List[bool]:
    """Run code on test cases. Returns [pass/fail per test]."""
    ...
```

---

## Pseudo-code: Clustering Coefficient

```
Input: fix_sequence = [t1, t2, t3, ...], error_labels = {t1: SYNTAX, t2: SYNTAX, t3: RUNTIME, ...}

1. Extract error type sequence:
   types = [error_labels[tid] for tid in fix_sequence]  # [SYNTAX, SYNTAX, RUNTIME, ...]

2. Count consecutive same-type pairs:
   consecutive_same = 0
   for i in range(len(types) - 1):
       if types[i] == types[i+1]:
           consecutive_same += 1

3. Compute observed rate:
   observed = consecutive_same / (len(types) - 1)

4. Compute expected random rate:
   type_counts = Counter(types)
   expected = sum(count * (count - 1) for count in type_counts.values()) / (len(types) * (len(types) - 1))

5. Clustering coefficient:
   return observed / expected if expected > 0 else 0.0

Edge cases:
- len(fix_sequence) < 2 → return 0.0
- All same type → observed = 1.0, expected = 1.0 → coefficient = 1.0
- expected = 0 (single error type in population) → return 0.0
```

---

## Pseudo-code: Permutation Test

```
Input: fix_sequence, error_labels, n_permutations = 1000, seed = 1

1. Compute observed clustering coefficient:
   observed = clustering_coefficient(fix_sequence, error_labels)

2. Generate null distribution:
   rng = np.random.default_rng(seed)
   null_coeffs = []
   for _ in range(n_permutations):
       shuffled = rng.permutation(fix_sequence)
       null_coeff = clustering_coefficient(shuffled, error_labels)
       null_coeffs.append(null_coeff)

3. Compute p-value (two-tailed):
   p_value = (sum(abs(null_c - mean(null_coeffs)) >= abs(observed - mean(null_coeffs)) 
              for null_c in null_coeffs) + 1) / (n_permutations + 1)

4. Return (observed, p_value)

Edge cases:
- All permutations yield same coefficient → p = 1.0
- observed >> all null values → p ≈ 0.001
```

---

## Algorithm: Debugging Loop

```
Input: problem (test_cases, prompt), model, max_iterations, timeout

1. Initialize:
   code = generate_initial_solution(problem, model)
   fix_sequence = []
   failures = []
   iteration = 0

2. Loop until all pass or max_iterations:
   results = execute_tests(code, problem.test_cases, timeout)
   passing = sum(results)
   failing_ids = [i for i, r in enumerate(results) if not r]
   
   if len(failing_ids) == 0:
       break  # All tests pass
   
   # Track newly fixed tests (compare to previous iteration)
   if iteration > 0:
       newly_fixed = previous_failing - set(failing_ids)
       fix_sequence.extend(sorted(newly_fixed))
   
   # Log failures for annotation
   for tid in failing_ids:
       failures.append(TestFailure(
           test_id=tid,
           iteration=iteration,
           error_msg=get_error(results[tid]),
           input_data=test_cases[tid][0],
           expected=test_cases[tid][1],
           actual=get_output(results[tid])
       ))
   
   # Agent generates fix
   prompt = build_fix_prompt(code, failing_ids, test_cases)
   code = call_model(model, prompt, temp=0.7)
   
   previous_failing = set(failing_ids)
   iteration += 1

3. Return DebugSession(
       problem_id=problem.id,
       iterations=[...],
       fix_sequence=fix_sequence,
       failures=deduplicate_failures(failures)  # Keep first occurrence per test
   )

Edge cases:
- Timeout on test execution → mark as "execution_failed", exclude from analysis
- Agent returns invalid code → log error, retry with error message once
- No progress after 3 iterations → abort session, discard problem
```

---

## Algorithm: Error Annotation Workflow

```
Input: failures (List[TestFailure]), num_annotators

1. For each annotator in [1..num_annotators]:
   annotations[annotator] = {}
   for failure in failures:
       display(failure.error_msg, failure.input_data, failure.expected, failure.actual)
       label = get_user_input(["syntax", "runtime", "logic", "edge_case"])
       annotations[annotator][failure.test_id] = ErrorType(label)

2. Compute Cohen's kappa:
   kappa = cohens_kappa(list(annotations.values()))
   if kappa < 0.7:
       log_warning("Low agreement, consider re-annotation or guidelines review")
       # Continue but flag in report

3. Resolve conflicts:
   consensus = {}
   for test_id in failures:
       votes = [annotations[a][test_id] for a in range(num_annotators)]
       if len(set(votes)) == 1:
           consensus[test_id] = votes[0]  # Full agreement
       else:
           consensus[test_id] = majority_vote(votes)  # Or trigger 3rd annotator

4. Return consensus

Edge cases:
- No majority (2-way tie with 2 annotators) → flag for 3rd annotator or discard test
- Annotator skips test → exclude test from analysis
- Kappa < 0.7 → log warning but proceed (report will note low agreement)
```

---

## Data Structures

```python
# No tensors - this is statistical analysis, not deep learning

# Main data containers:
fix_sequence: List[int]           # [3, 7, 2, 14, ...]
error_labels: Dict[int, ErrorType]  # {3: SYNTAX, 7: SYNTAX, 2: RUNTIME, ...}
sessions: List[DebugSession]      # All problem sessions
annotations: List[Dict[int, ErrorType]]  # Per-annotator labels

# Sizes:
- 50 problems
- ~15 tests/problem → 750 total test IDs
- fix_sequence length: variable (5-50 fixes/problem depending on iterations)
- annotations: num_annotators × 750 labels
```

---

## Edge Cases & Error Handling

### Clustering Coefficient Edge Cases

1. **Empty fix sequence** (`len(fix_sequence) == 0`)
   - Return: `0.0`
   - Handle: Skip problem in analysis, log warning

2. **Single fix** (`len(fix_sequence) == 1`)
   - Return: `0.0` (no consecutive pairs)
   - Handle: Valid data point, include in analysis

3. **All same error type**
   - Observed: `1.0` (all consecutive pairs match)
   - Expected: `1.0` (only one type in population)
   - Return: `1.0`
   - Handle: Valid result, indicates agent focused on one error category

4. **Zero expected rate** (mathematically impossible if len > 1, but guard)
   - Return: `0.0`
   - Handle: Avoid division by zero

### Permutation Test Edge Cases

1. **Insufficient variance** (all permutations → same coefficient)
   - Return: `p = 1.0`
   - Handle: Valid result, clustering not significant

2. **Perfect clustering** (observed >> all null values)
   - Return: `p ≈ 1 / (n_permutations + 1)` (minimum p-value)
   - Handle: Valid strong result

### Annotation Edge Cases

1. **Low kappa** (`kappa < 0.7`)
   - Action: Log warning, flag in report
   - Don't halt: Proceed with majority vote, note limitation

2. **Tie in majority vote** (2 annotators, 2 different labels)
   - Action: Recruit 3rd annotator OR exclude test from analysis
   - Default: Exclude test, log count

3. **Missing annotations** (annotator skips test)
   - Action: Exclude test from consensus, log count
   - If > 10% missing → halt, re-annotate

### Debug Session Edge Cases

1. **No progress** (same failing tests for 3 iterations)
   - Action: Abort session, discard problem
   - Rationale: Agent stuck, not generating useful fix sequence

2. **Test execution crash** (timeout, runtime exception)
   - Action: Mark test as "execution_failed", exclude from analysis
   - Log: Problem ID, test ID, error message

3. **Agent returns non-code** (explanation instead of code)
   - Action: Retry once with explicit prompt "return only code"
   - If fails again: Abort session, discard problem

4. **API rate limit** (Codeforces or OpenAI)
   - Action: Exponential backoff (1s, 2s, 4s), max 3 retries
   - If exhausted: Log error, pause 60s, retry

---

## Validation Checks

### Pre-analysis Filters

```python
def validate_session(session: DebugSession) -> bool:
    """Return True if session meets quality criteria."""
    return (
        len(session.fix_sequence) >= 5 and  # Min 5 fixes for meaningful clustering
        len(session.failures) >= 15 and     # Min 15 test cases
        session.iterations[-1]["passing"] > session.iterations[0]["passing"]  # Progress made
    )

def validate_annotations(annotations: List[Dict[int, ErrorType]]) -> Tuple[bool, float]:
    """Return (passes, kappa). Passes if kappa > 0.7."""
    kappa = cohens_kappa(annotations)
    return (kappa >= 0.7, kappa)
```

### Gate Evaluation Logic

```python
def evaluate_gate(sessions: List[DebugSession], error_labels: Dict[int, ErrorType]) -> Dict:
    """Compute gate metrics and return pass/fail decision."""
    
    # Aggregate all fix sequences
    all_fixes = []
    for s in sessions:
        all_fixes.extend(s.fix_sequence)
    
    # Compute agent clustering
    agent_coeff, p_value = permutation_test(all_fixes, error_labels)
    
    # Random baseline (shuffle once for comparison)
    random_fixes = np.random.permutation(all_fixes)
    random_coeff = clustering_coefficient(random_fixes, error_labels)
    
    # Gate decision
    gate_pass = (agent_coeff > 0.3) and (p_value < 0.05)
    
    return {
        "clustering_agent": agent_coeff,
        "clustering_random": random_coeff,
        "p_value": p_value,
        "gate_pass": gate_pass,
        "decision": "PASS" if gate_pass else "PIVOT"
    }
```

---

## Implementation Notes

### Libraries

Applied: Standard Python statistical libraries

- `numpy.random.permutation` for permutation test
- `sklearn.metrics.cohen_kappa_score` for inter-annotator agreement
- `collections.Counter` for type frequency counting
- `subprocess.run(timeout=...)` for test execution isolation

### Simplifications for PoC

- **Annotation UI**: Command-line input instead of web interface (add GUI when scaling to > 100 annotators)
- **Conflict resolution**: Majority vote only, no sophisticated adjudication (add ML-based suggestion when kappa data available)
- **Caching**: No result caching (add Redis if re-running same problems frequently)

### Not Included (YAGNI)

- Parallel test execution (50 problems × 10 iter = ~500 runs, serial is fine)
- Real-time progress dashboard (batch analysis, logs sufficient)
- Automated error classification (requires ground truth first, this experiment establishes it)

---

## File Structure

```
h-m1/
├── code/
│   ├── main.py                  # run_evaluation()
│   ├── debug_loop.py            # run_debug_session(), execute_tests()
│   ├── clustering.py            # clustering_coefficient(), permutation_test()
│   ├── annotation.py            # annotate_errors(), resolve_conflicts()
│   ├── codeforces.py            # fetch_problems()
│   └── utils.py                 # ErrorType, DebugSession, TestFailure
├── data/
│   ├── problems.json            # Fetched problem metadata
│   ├── sessions.json            # Debug sessions (fix sequences)
│   └── annotations.json         # Error labels (consensus)
├── figures/
│   ├── clustering_comparison.png
│   ├── error_distribution.png
│   ├── fix_sequence_heatmap.png
│   └── kappa_matrix.png
└── docs/
    └── annotation_guidelines.md  # Examples for each error type
```

---

*Next: Phase 4 Implementation (04_code.py)*
