# Experiment Design: H-M2

**Date:** 2026-08-19
**Author:** PrayPrey
**Hypothesis Statement:** Test suites detect behavioral errors (wrong output, runtime exceptions, edge cases) not caught by static analysis alone.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> MECHANISM Template - Tests orthogonality: execution finds what static misses.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M1 PASS: 98.6% structural coverage)
**Gate Status:** SHOULD_WORK (>40% behavioral detection in static-clean code)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (COMPLETED, PASS)

### Gate Condition
Test failures occur in >40% of problems where pylint+mypy report zero errors. This validates that execution provides a unique signal orthogonal to static analysis.

---

## Continuation Context

H-M1 established that static analysis (pylint+mypy) reliably detects structural errors (98.6% coverage). H-M2 complements this by showing execution detects different errors.

### Previous Hypothesis Results
- **H-E1 (PASS):** Jaccard similarity = 0.0, confirming error classes are orthogonal
- **H-M1 (PASS):** 98.6% structural coverage, 73/74 failing problems had static errors
- **Key Finding:** Static-clean code may still fail tests (behavioral errors)

---

## Implementation Research Summary

### Knowledge Base Findings

**Self-Refine Framework (2303.17651):**
- Iterative refinement with LLM-generated feedback
- ~20% improvement on code generation tasks
- Execution feedback via test results drives refinement

**EvalPlus Benchmark:**
- HumanEval+: 164 problems, 80x more tests than HumanEval
- MBPP+: 399 problems, 35x more tests than MBPP
- Extended tests catch behavioral edge cases originals miss

### Code Examples

**EvalPlus Evaluation Pattern:**
```python
from evalplus.data import get_human_eval_plus, get_mbpp_plus
from evalplus.evaluate import evaluate_functional_correctness

# Load test cases
problems = get_human_eval_plus()

# Run tests, get pass/fail per problem
results = evaluate_functional_correctness(
    sample_file="generated_code.jsonl",
    k=[1],
    n_workers=4,
    timeout=3.0
)
```

### Implementation Priority Assessment

**Primary Approach:** Use evalplus library directly
- Official benchmark implementation
- Handles sandbox execution safely
- Returns structured pass/fail data

**Fallback:** Manual test execution with subprocess
- If evalplus unavailable

---

## Experiment Specification

### Dataset

| Attribute | Value |
|-----------|-------|
| **Name** | HumanEval+ + MBPP+ |
| **Source** | evalplus (neuralmagic/evalplus) |
| **Size** | 563 problems (164 + 399) |
| **Splits** | Full test sets (no sampling) |
| **Format** | JSONL with task_id, prompt, tests |

**Loading Information:**
- Method: pip install evalplus
- Identifier: evalplus==0.2.0
- Code:
```python
from evalplus.data import get_human_eval_plus, get_mbpp_plus

humaneval_problems = get_human_eval_plus()  # 164 problems
mbpp_problems = get_mbpp_plus()  # 399 problems
```

### Models

#### Baseline Model

This experiment reuses LLM-generated code from H-E1/H-M1 analysis. No new model inference required.

**Source:** Code samples from H-E1 generation (563 problems)

#### Proposed Model

**Architecture:** Analysis pipeline (no model training)

**Core Mechanism Implementation:**

```python
def analyze_behavioral_errors(code_samples: list, problems: list) -> dict:
    """
    Core H-M2 mechanism: identify behavioral errors in static-clean code.
    
    Returns:
        {
            'total_static_clean': int,       # Problems with zero pylint/mypy errors
            'behavioral_failures': int,       # Of those, how many fail tests
            'behavioral_rate': float,         # behavioral_failures / total_static_clean
            'failure_categories': dict,       # {category: count}
        }
    """
    results = {
        'total_static_clean': 0,
        'behavioral_failures': 0,
        'failure_categories': defaultdict(int)
    }
    
    for idx, (code, problem) in enumerate(zip(code_samples, problems)):
        # Step 1: Run static analysis
        static_errors = run_static_analysis(code)  # pylint + mypy
        
        if len(static_errors) == 0:
            # Code has no static errors
            results['total_static_clean'] += 1
            
            # Step 2: Run tests
            test_result = run_evalplus_tests(code, problem['task_id'])
            
            if not test_result['passed']:
                # Behavioral error found
                results['behavioral_failures'] += 1
                
                # Categorize failure
                category = categorize_failure(test_result)
                results['failure_categories'][category] += 1
    
    results['behavioral_rate'] = (
        results['behavioral_failures'] / results['total_static_clean']
        if results['total_static_clean'] > 0 else 0.0
    )
    
    return results


def categorize_failure(test_result: dict) -> str:
    """Categorize test failure type."""
    error_msg = test_result.get('error', '')
    
    if 'AssertionError' in error_msg or 'Expected' in error_msg:
        return 'wrong_output'
    elif any(exc in error_msg for exc in ['TypeError', 'ValueError', 'IndexError']):
        return 'runtime_exception'
    elif 'timeout' in error_msg.lower():
        return 'timeout'
    else:
        return 'edge_case'


def run_static_analysis(code: str) -> list:
    """Run pylint + mypy, return list of errors."""
    errors = []
    
    # pylint
    pylint_result = subprocess.run(
        ['python', '-m', 'pylint', '--errors-only', '-'],
        input=code, capture_output=True, text=True
    )
    if pylint_result.returncode != 0:
        errors.extend(parse_pylint_errors(pylint_result.stdout))
    
    # mypy
    mypy_result = subprocess.run(
        ['python', '-m', 'mypy', '--no-error-summary', '-'],
        input=code, capture_output=True, text=True
    )
    if 'error:' in mypy_result.stdout:
        errors.extend(parse_mypy_errors(mypy_result.stdout))
    
    return errors
```

### Training Protocol

**Not Applicable** - This is an analysis experiment, not model training.

**Execution Protocol:**
1. Load code samples from H-E1/H-M1 generation
2. Run static analysis on all 563 samples
3. Identify samples with zero static errors
4. Run evalplus tests on static-clean samples
5. Categorize and count behavioral failures
6. Compute behavioral rate (target: >40%)

### Evaluation

| Metric | Definition | Target |
|--------|------------|--------|
| **Behavioral Rate** | test_failures / static_clean_problems | >40% |
| **Total Static-Clean** | Problems with zero pylint+mypy errors | Report |
| **Category Distribution** | wrong_output, exception, edge_case counts | Report |

**Metrics Loading Information:**
- Task Type: Code Analysis
- Library: Custom (uses evalplus for execution)
- Code:
```python
def compute_gate_metrics(results: dict) -> dict:
    """Compute H-M2 gate metrics."""
    behavioral_rate = results['behavioral_rate']
    passed = behavioral_rate > 0.40
    
    return {
        'behavioral_rate': behavioral_rate,
        'gate_threshold': 0.40,
        'passed': passed,
        'message': f"Behavioral rate {behavioral_rate:.1%} {'>' if passed else '<='} 40%"
    }
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Behavioral rate vs 40% threshold bar chart

#### Additional Figures (LLM Autonomous)
1. **Failure Category Pie Chart**: Distribution of wrong_output, exception, edge_case
2. **Per-Benchmark Breakdown**: HumanEval+ vs MBPP+ behavioral rates
3. **Venn Diagram**: Static errors vs Test failures overlap (validates H-E1)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. behavioral_rate > 0.40 (gate metric)

**Expected Outcome:**
Based on H-E1 (Jaccard=0.0, 48.9% non-overlapping), we expect significant behavioral errors in static-clean code.

---

## Appendix: Reference Implementations

### EvalPlus Repository
- URL: https://github.com/evalplus/evalplus
- Usage: Standard benchmark evaluation
- Installation: `pip install evalplus`

### Self-Refine Framework
- Paper: arXiv:2303.17651
- Relevance: Execution feedback mechanism

### H-M1 Implementation
- Location: h-m1/code/
- Relevance: Reuse static analysis logic

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19T06:20:00Z

### Workflow History for This Hypothesis
- 2026-08-19: H-M2 set to IN_PROGRESS (Phase 2C start)
- Predecessor: H-M1 PASS (98.6% structural coverage)

---

*MCP Tools: Not available in this session (no-mcp mode)*
*Specifications derived from verification plan and H-M1 validation*
*Next Phase: Phase 3 - Implementation Planning*
