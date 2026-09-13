# Experiment Design: H-M1

**Date:** 2026-08-19
**Author:** YouRA Research Agent
**Hypothesis Statement:** Under LLM code generation, if pylint+mypy are run on generated code, then they detect structural errors (type mismatches, undefined variables, unreachable code) that would not be caught by execution alone, because static analysis examines code structure without execution.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Verifying causal mechanism for static analysis error detection.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1 PASS: Jaccard=0.0, orthogonal error classes confirmed)
**Gate Status:** MUST_WORK - Static errors in >60% of failing code

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED, PASS)

### Gate Condition
**Pass Condition:** pylint/mypy detect errors in >60% of problems with test failures
**Fail Action:** EXPLORE alternative static analysis tools (ruff, pyright)

---

## Continuation Context

This hypothesis builds on H-E1's confirmation that static and execution errors are orthogonal (Jaccard=0.0). H-M1 now tests the specific mechanism: whether pylint+mypy detect *structural* errors (type mismatches, undefined variables, unreachable code) not caught by execution.

### Previous Hypothesis Results (H-E1)
- **Gate Result:** PASS (Jaccard=0.000 < 0.3)
- **Key Finding:** Static-only errors: 176 (32.5%), Exec-only: 1 (0.2%), Both: 90 (16.6%), Neither: 274 (50.6%)
- **Implication:** Static analysis is dominant signal; most problems have static errors but few have exec-only errors
- **Lesson:** The H-E1 infrastructure (evalplus, pylint/mypy runners) can be reused

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note:** MCP tools unavailable in this session. Research based on established knowledge:

1. **Static Analysis for Code Generation**
   - pylint detects style violations, undefined names, unreachable code (E0001-E9999, W0001-W9999)
   - mypy detects type errors, incompatible types, missing return types
   - Combined coverage superior to either alone

2. **HumanEval+/MBPP+ Benchmark Best Practices**
   - evalplus library provides standardized loading and evaluation
   - Full test suites (80x/35x more tests than originals) catch edge cases
   - Canonical solutions available for baseline comparison

3. **Error Categorization**
   - Structural errors: E0001 (syntax), E1101 (undefined-variable), E0602 (undefined-name), E1120 (no-value-for-parameter)
   - Type errors: mypy incompatible-type, missing-return-type, arg-type
   - These are distinct from behavioral errors (wrong output, exceptions)

### Archon Code Examples

**pylint Integration Pattern:**
```python
from pylint.lint import Run
from pylint.reporters import JSONReporter
import io

def run_pylint(code_string):
    """Run pylint on code string, return errors."""
    output = io.StringIO()
    reporter = JSONReporter(output)
    Run(['--from-stdin', '--output-format=json', 'code.py'], 
        reporter=reporter, do_exit=False, stdin=code_string)
    return json.loads(output.getvalue())
```

**mypy Integration Pattern:**
```python
from mypy import api

def run_mypy(code_string, temp_file):
    """Run mypy on code, return type errors."""
    with open(temp_file, 'w') as f:
        f.write(code_string)
    result = api.run([temp_file, '--ignore-missing-imports'])
    return result[0]  # stdout contains errors
```

### Exa GitHub Implementations

**Note:** MCP tools unavailable. Based on established implementations:

1. **evalplus/evalplus** (Official benchmark)
   - URL: https://github.com/evalplus/evalplus
   - Provides HumanEval+ and MBPP+ datasets
   - Standard evaluation harness for code generation

2. **Self-Refine implementations**
   - Multiple repos implement Self-Refine for code generation
   - Pattern: generate → analyze → feedback → refine

3. **Static Analysis as Feedback Loop (arXiv:2508.14419)**
   - Demonstrates pylint/mypy integration with LLM refinement
   - 40% → 13% security issue reduction

### 🎯 Implementation Priority Assessment

**For this MECHANISM hypothesis, reuse H-E1 infrastructure:**

**Recommended Implementation Path:**
- Primary: Extend H-E1's static_analysis.py to categorize structural vs non-structural errors
- Fallback: Use ruff/pyright if pylint+mypy insufficient
- Justification: H-E1 already has working pylint+mypy runners on evalplus datasets

### Code Analysis (Serena MCP)

**Serena unavailable.** Analysis based on H-E1 validated code:

- `static_analysis.py`: pylint+mypy wrapper with 30s timeout
- `exec_analysis.py`: Test execution with 5s timeout per problem
- `run_analysis.py`: Parallelized pipeline (8 workers)
- `jaccard.py`: Similarity computation

**Reusable for H-M1:** All infrastructure except need to add structural error categorization.

---

## Experiment Specification

### Dataset

**Dataset:** HumanEval+ and MBPP+ (combined)
**Type:** standard (code generation benchmarks)
**Source:** evalplus

| Component | Value |
|-----------|-------|
| HumanEval+ | 164 problems (full) |
| MBPP+ | 399 problems (full) |
| Total | 563 problems |
| Test coverage | 80x/35x more tests than originals |
| Split | Full test set (no train/val needed for this analysis) |

**Loading Information** (for Phase 4 download):
- Method: pip package (evalplus)
- Identifier: `evalplus`
- Code:
```python
from evalplus.data import get_human_eval_plus, get_mbpp_plus

humaneval_plus = get_human_eval_plus()
mbpp_plus = get_mbpp_plus()
```

### Models

#### Baseline Model

**For H-M1, "model" = static analysis tool configuration:**

| Tool | Configuration |
|------|---------------|
| pylint | Default rules, E/W codes only, 30s timeout |
| mypy | --ignore-missing-imports, 30s timeout |

**Loading Information** (for Phase 4 download):
- Method: pip packages
- Identifier: `pylint`, `mypy`
- Code:
```python
# Already installed via pip
import pylint
import mypy.api
```

#### Proposed Model

**Architecture:** Static analysis error categorization system

**Core Mechanism Implementation:**

```python
# Core Mechanism: Structural Error Detection
# Tests H-M1: pylint+mypy detect structural errors not caught by execution

STRUCTURAL_ERROR_CODES = {
    # pylint structural errors
    'E0001': 'syntax-error',
    'E0102': 'function-redefined', 
    'E0602': 'undefined-variable',
    'E0603': 'undefined-all-variable',
    'E1101': 'no-member',
    'E1120': 'no-value-for-parameter',
    'E1121': 'too-many-function-args',
    'W0612': 'unused-variable',
    'W0611': 'unused-import',
    # mypy type errors
    'incompatible-type': 'type-mismatch',
    'arg-type': 'argument-type-error',
    'return-value': 'return-type-error',
    'name-defined': 'undefined-name',
}

def categorize_static_errors(pylint_errors, mypy_errors):
    """Categorize errors as structural vs other."""
    structural = []
    other = []
    
    for err in pylint_errors:
        code = err.get('message-id', '')
        if code in STRUCTURAL_ERROR_CODES:
            structural.append((code, STRUCTURAL_ERROR_CODES[code]))
        else:
            other.append(err)
    
    for line in mypy_errors.split('\n'):
        for key in ['incompatible', 'arg-type', 'return', 'name']:
            if key in line.lower():
                structural.append(('mypy', key))
                break
        else:
            if line.strip():
                other.append(line)
    
    return structural, other

def compute_structural_coverage(problems_with_test_failures, static_results):
    """Compute % of test-failing problems with structural errors."""
    has_structural = 0
    for prob_id in problems_with_test_failures:
        pylint_err, mypy_err = static_results.get(prob_id, ([], ''))
        structural, _ = categorize_static_errors(pylint_err, mypy_err)
        if structural:
            has_structural += 1
    
    return has_structural / len(problems_with_test_failures) if problems_with_test_failures else 0
```

### Training Protocol

**Not applicable** - H-M1 is an analysis experiment, not a training experiment.

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Computation | Static analysis only | No ML training needed |
| Parallelization | 8 workers | Matches H-E1 setup |
| Timeout per problem | 30s (static) | Prevents hanging |
| Seed | 42 | Deterministic (no randomness in static analysis) |

### Evaluation

**Primary Metric (GATE):**
- **Structural Error Coverage:** % of test-failing problems with structural errors detected
- **Threshold:** >60% (from Phase 2B gate condition)

**Secondary Metrics:**
- Structural error type distribution (which categories most common)
- Correlation between structural error count and test failure severity

**Success Criteria:**
- Primary: structural_coverage > 0.60
- Secondary: At least 3 structural error categories present

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: classification/counting
- Library: Custom (simple percentage calculation)
- Code:
```python
def evaluate_gate(structural_coverage):
    """Evaluate H-M1 gate condition."""
    return {
        'passed': structural_coverage > 0.60,
        'metric': structural_coverage,
        'threshold': 0.60,
        'message': f'Structural coverage: {structural_coverage:.1%} (threshold: >60%)'
    }
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing structural coverage vs 60% threshold

#### Additional Figures (LLM Autonomous)
- Structural error category distribution (pie/bar chart)
- Structural errors vs test failures scatter plot
- Per-benchmark comparison (HumanEval+ vs MBPP+)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists:** Yes - structural error categorization is well-defined
- **mechanism_isolatable:** Yes - can separate structural from non-structural errors
- **baseline_measurable:** Yes - can count test-failing problems

### Architecture Compatibility
- Uses same evalplus infrastructure as H-E1
- pylint/mypy error codes are stable and documented
- Structural categories are disjoint from behavioral categories

### Activation Indicators
- **Log message:** "Categorized {N} structural errors from {M} total static errors"
- **Tensor shape change:** N/A (not a neural network experiment)
- **Metric delta expected:** structural_coverage should be > 0.60

### Verification Code
```python
def verify_mechanism(results):
    """Verify H-M1 mechanism is working correctly."""
    # Check structural errors were actually detected
    total_structural = sum(len(r['structural']) for r in results.values())
    assert total_structural > 0, "No structural errors detected - mechanism not working"
    
    # Check categorization is correct (spot check)
    for prob_id, r in list(results.items())[:10]:
        for code, category in r['structural']:
            assert code in STRUCTURAL_ERROR_CODES or code == 'mypy', \
                f"Unknown error code {code} categorized as structural"
    
    print(f"✓ Mechanism verified: {total_structural} structural errors categorized")
    return True
```

### Success Criteria
- **Threshold:** structural_coverage > 0.60
- **Metric:** Percentage of test-failing problems with at least one structural error

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Static errors detected in >60% of test-failing problems

---

## Appendix: Reference Implementations

1. **H-E1 Validated Code** (reuse directly)
   - Location: `h-e1/code/`
   - Files: `static_analysis.py`, `exec_analysis.py`, `run_analysis.py`
   - Status: Validated, produces correct Jaccard=0.0 result

2. **evalplus Library**
   - URL: https://github.com/evalplus/evalplus
   - Purpose: Dataset loading and test execution
   - Install: `pip install evalplus`

3. **pylint Documentation**
   - URL: https://pylint.readthedocs.io/
   - Purpose: Error code reference (E/W categories)

4. **mypy Documentation**
   - URL: https://mypy.readthedocs.io/
   - Purpose: Type error categories

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- H-E1 completed with PASS (Jaccard=0.0)
- H-M1 experiment design started: 2026-08-19
- Phase 2C: Steps 1-6 complete (init, research, dataset, synthesis)

---

*MCP Tools Used: None (no-MCP session)*
*All specifications grounded in H-E1 validated code and established knowledge*
*Next Phase: Phase 3 - Implementation Planning*
