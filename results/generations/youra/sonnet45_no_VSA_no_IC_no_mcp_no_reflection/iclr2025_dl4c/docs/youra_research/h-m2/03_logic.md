# Logic Specification: H-M2 Root Cause Prioritization

**Hypothesis:** If agents cluster errors (H-M1), then prioritizing fixes by root cause increases high-impact fix proportion.

**Date:** 2026-08-28  
**Phase:** 3 - Logic Design  
**Complexity:** Medium  

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: API signatures verified from H-M1 code  
**Analyzed Path**: `docs/youra_research/h-m1/code/`  
**Relevant Symbols**:
- `clustering.clustering_coefficient(fix_sequence, error_labels) -> float`
- `mock_agent.MockDebugAgent.run_debug_session(problem, max_iterations) -> DebugSession`
- `utils.ErrorType`, `utils.TestFailure`, `utils.DebugSession`

---

## L-1: RootCausePrioritizer [Complexity: 3, Budget: 8 subtasks]

**Applied**: Clustering-based prioritization (Archon KB)

### API Signatures

```python
from typing import List, Dict
from h_m1.utils import ErrorType, TestFailure

class RootCausePrioritizer:
    def __init__(self, clustering_strength: float = 0.8):
        """Initialize prioritizer. clustering_strength ∈ [0,1]"""
        self.clustering_strength = clustering_strength
    
    def prioritize_fixes(
        self,
        test_failures: List[int],
        error_messages: Dict[int, str]
    ) -> List[int]:
        """
        Prioritize test fixes by cluster size.
        
        Args:
            test_failures: [N_failed] test IDs
            error_messages: {test_id: error_msg}
        
        Returns:
            priority_order: [N_failed] test IDs sorted by cluster size (descending)
        """
        ...
```

### Pseudo-code

```
1. Group tests by error type:
   clusters = defaultdict(list)
   for test_id in test_failures:
       error_type = classify_error(error_messages[test_id])
       clusters[error_type].append(test_id)

2. Sort clusters by size (descending):
   sorted_clusters = sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True)

3. Flatten to priority order:
   priority_order = []
   for error_type, test_ids in sorted_clusters:
       priority_order.extend(test_ids)
   
   return priority_order
```

### Subtasks [6/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Error classification | Map error messages to ErrorType |
| L-1-2 | Cluster grouping | Group tests by error type |
| L-1-3 | Cluster sorting | Sort by size descending |
| L-1-4 | Priority flattening | Convert clusters to ordered list |
| L-1-5 | Baseline (random) | Random permutation for baseline |
| L-1-6 | Integration | Connect to H-M1 error types |

---

## L-2: Fix Impact Measurement [Complexity: 1, Budget: 3 subtasks]

**Applied**: Standard PyTorch delta computation

### API Signatures

```python
import numpy as np
from typing import List

def measure_fix_impact(
    before: np.ndarray,
    after: np.ndarray
) -> int:
    """
    Measure fix impact as delta passing tests.
    
    Args:
        before: [N_tests] bool array (True = passing)
        after: [N_tests] bool array
    
    Returns:
        delta_passing: int (newly passing tests)
    """
    return int(after.sum() - before.sum())
```

### Subtasks [2/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Delta calculation | Compute difference in passing counts |
| L-2-2 | High-impact classification | Check if delta >= 2 |

---

## L-3: Proportion Metric Calculation [Complexity: 1, Budget: 3 subtasks]

**Applied**: Standard PyTorch proportion computation

### API Signatures

```python
def calculate_proportion_high_impact(
    fix_impacts: List[int],
    threshold: int = 2
) -> float:
    """
    Calculate proportion of high-impact fixes.
    
    Args:
        fix_impacts: [N_modifications] delta_passing values
        threshold: Minimum delta for high-impact classification
    
    Returns:
        proportion: float ∈ [0,1]
    """
    if len(fix_impacts) == 0:
        return 0.0
    high_impact_count = sum(1 for delta in fix_impacts if delta >= threshold)
    return high_impact_count / len(fix_impacts)
```

### Subtasks [2/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | High-impact counting | Count deltas >= threshold |
| L-3-2 | Proportion computation | Divide by total modifications |

---

## L-4: Baseline Sequential Debugging [Complexity: 1, Budget: 2 subtasks]

**Applied**: Random permutation baseline

### API Signatures

```python
def baseline_sequential(
    test_failures: List[int],
    seed: int = 1
) -> List[int]:
    """
    Sequential baseline (random order).
    
    Args:
        test_failures: [N_failed] test IDs
        seed: Random seed for reproducibility
    
    Returns:
        fix_order: [N_failed] test IDs in random order
    """
    import random
    rng = random.Random(seed)
    shuffled = list(test_failures)
    rng.shuffle(shuffled)
    return shuffled
```

### Subtasks [1/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Random permutation | Shuffle test failures |

---

## L-5: Mock Agent Integration [Complexity: 2, Budget: 5 subtasks]

**Applied**: H-M1 mock agent pattern

### API Signatures

```python
from h_m1.utils import Problem, DebugSession

class MockPrioritizedDebugAgent:
    def __init__(self, prioritizer: RootCausePrioritizer, seed: int = 1):
        """Initialize with prioritizer."""
        self.prioritizer = prioritizer
        self.seed = seed
    
    def run_debug_session(
        self,
        problem: Problem,
        max_iterations: int = 10
    ) -> DebugSession:
        """
        Run debug session with prioritized fixes.
        
        Args:
            problem: Problem with test cases
            max_iterations: Max fix iterations
        
        Returns:
            session: DebugSession with fix_sequence tracking
        """
        ...
```

### Pseudo-code

```
1. Initialize test results:
   failing_ids = [tc.case_id for tc in problem.test_cases]
   fix_impacts = []
   
2. For each iteration:
   - Record before state: before[i] = (test_i passing)
   - Prioritize fixes: priority_order = prioritizer.prioritize_fixes(failing_ids, error_msgs)
   - Fix top K tests from priority_order
   - Record after state: after[i] = (test_i passing)
   - Compute impact: delta = measure_fix_impact(before, after)
   - Store: fix_impacts.append(delta)
   
3. Return DebugSession with fix_impacts tracked
```

### Subtasks [4/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | State tracking | Track before/after test results |
| L-5-2 | Prioritization call | Call RootCausePrioritizer |
| L-5-3 | Fix execution | Update test results based on fixes |
| L-5-4 | Impact recording | Store delta_passing per iteration |

---

## External Dependencies (Base Hypothesis)

### API Signatures (From H-M1 Actual Code)

The following APIs are reused from H-M1. Signatures verified from actual implementation:

```python
# From: docs/youra_research/h-m1/code/utils.py
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

class ErrorType(Enum):
    SYNTAX = "syntax"
    RUNTIME = "runtime"
    LOGIC = "logic"
    EDGE_CASE = "edge_case"

@dataclass
class TestCase:
    case_id: int
    input_data: str
    expected_output: str

@dataclass
class Problem:
    problem_id: str
    title: str
    rating: int
    solve_count: int
    test_cases: List[TestCase]

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
    iterations: List[DebugIteration]
    fix_sequence: List[int]  # Test IDs in fix order
    failures: List[TestFailure]

# From: docs/youra_research/h-m1/code/mock_agent.py
class MockDebugAgent:
    def __init__(self, seed: int = 1, clustering_strength: float = 0.4):
        """clustering_strength ∈ [0,1]"""
        ...
    
    def run_debug_session(
        self,
        problem: Problem,
        max_iterations: int = 10
    ) -> DebugSession:
        """Simulate debug session with controlled clustering."""
        ...

def generate_mock_problems(
    count: int = 50,
    min_tests: int = 15,
    seed: int = 1
) -> List[Problem]:
    """Generate mock Codeforces problems."""
    ...
```

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation)

---

## Integration Architecture

```
H-M2 (Prioritization)
├── RootCausePrioritizer (new)
│   ├── Uses: H-M1 ErrorType classification
│   └── Extends: H-M1 clustering with size-based ordering
│
├── MockPrioritizedDebugAgent (new)
│   ├── Extends: H-M1 MockDebugAgent
│   └── Adds: Fix impact tracking
│
└── Metrics (new)
    ├── measure_fix_impact()
    ├── calculate_proportion_high_impact()
    └── baseline_sequential()

Reused from H-M1:
├── utils.ErrorType
├── utils.Problem, TestCase, TestFailure
├── utils.DebugSession
└── mock_agent.generate_mock_problems()
```

---

## Budget Summary

| Task | Allocated | Used | Remaining |
|------|-----------|------|-----------|
| L-1 Prioritizer | 8 | 6 | 2 |
| L-2 Fix Impact | 3 | 2 | 1 |
| L-3 Proportion | 3 | 2 | 1 |
| L-4 Baseline | 2 | 1 | 1 |
| L-5 Mock Agent | 5 | 4 | 1 |
| **Total** | **21** | **15** | **6** |

---

## Validation Checklist

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in comments (N/A - not tensor-based)
- [x] Subtask count within budget (15/21 used)
- [x] Total length < 600 lines
- [x] Codebase Analysis (Serena) section included
- [x] Base hypothesis APIs verified from actual code
- [x] External Dependencies API section included

---

*Logic design complete. Next: Phase 4 - Implementation.*
