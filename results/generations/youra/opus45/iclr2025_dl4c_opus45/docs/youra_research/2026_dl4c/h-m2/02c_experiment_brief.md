# Experiment Design: H-M2

**Date:** 2026-03-24
**Author:** Anonymous
**Hypothesis Statement:** RL optimization pressure toward syntactic validity results in higher execution depth (lines executed / total) for RL failures compared to DPO failures
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> MECHANISM Hypothesis - Tests execution depth difference as evidence of syntactic validity pressure

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-m1 (PASS)
**Gate Status:** SHOULD_WORK (pending)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** h-m1

### Gate Condition
| Gate Type | Pass Condition | Fail Action |
|-----------|----------------|-------------|
| SHOULD_WORK | mean(execution_depth\|failure,RL) > mean(execution_depth\|failure,DPO), t-test p<0.05 | Document limitation, continue |

---

## Continuation Context

This hypothesis builds on H-M1's confirmed zero-reward basin mechanism. H-M1 demonstrated that RL's binary execution reward creates a flat zero-reward basin, concentrating RL failures in assertion errors (code runs but produces wrong output). H-M2 tests whether this manifests as RL failures occurring "deeper" in execution flow.

### Previous Hypothesis Results (if applicable)

**H-M1 Key Results:**
- Fisher's exact test: p = 0.0027 (significant)
- RL assertion proportion: 2.12% (5/236 failures)
- DPO assertion proportion: 0.00% (0/530 failures)
- Odds ratio: infinite (DPO has zero assertion errors)

**Lessons Learned:**
- Reuse H-E1 execution results to avoid redundant model inference
- Inline utility functions rather than importing from other hypothesis folders
- Fisher's exact test appropriate for small expected cell counts

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "execution depth code coverage tracing"**
- JAX profiling documentation (jax.readthedocs.io): Provides general profiling approaches but not specific to Python code execution depth measurement
- Limited direct relevance to code generation execution tracing

**Query 2: "code generation RL DPO alignment"**
- AlignYourSteps (NVIDIA): Diffusion model alignment research, not code generation specific
- k-diffusion sampling: Diffusion sampling methods, not directly applicable

**Query 3: "Python trace coverage lines executed"**
- JAX profiling: General profiling approaches
- Google Python style guide: Coding conventions, not execution tracing

**Serena Memory: dl4c_alignment_signatures_2026**
- Prior DL4C pipeline research validated alignment methods create distinguishable signatures
- Cohen's d = 7.835 demonstrates large effect sizes between alignment methods
- POC validation approach: Use existing H-E1 execution results rather than new model inference
- LESSON: Reuse cached execution traces to avoid redundant computation

**Key Insight:** Archon KB lacks specific execution depth measurement implementations for code generation. Will rely on:
1. Python's built-in `trace` module for line-level execution tracking
2. Standard evaluation frameworks (EvalPlus) for consistent execution environment
3. Prior hypothesis results (H-E1) for cached execution traces

### Archon Code Examples

**Query 1: "Python trace coverage module"**
- No directly relevant code examples found in KB
- Diffusion model examples predominate in current KB

**Query 2: "evalplus HumanEval execution"**
- No direct evalplus examples in KB
- Will use official evalplus library documentation

**Implementation Pattern (derived from KB general patterns):**
```python
# Pattern: Execution depth measurement via trace module
import sys
import trace

def measure_execution_depth(code_string: str, test_input: dict) -> float:
    """Track lines executed before failure."""
    tracer = trace.Trace(count=True, trace=False)
    # Execute with tracing, capture failure point
    # Return: lines_executed / total_lines
```

**Note:** Direct code examples not available in KB. Implementation will be based on Python standard library `trace` module and scipy for statistical testing.

### Exa GitHub Implementations

**Query 1: Python trace module execution coverage**

**Repository 1**: [Python Standard Library - trace module](https://docs.python.org/3/library/trace.html)
- **URL**: https://docs.python.org/3/library/trace.html
- **Relevance**: Official Python module for tracking statement execution
- **Key Features**:
  - `trace.Trace(count=True, trace=False)` - Count line executions without verbose output
  - `tracer.run(cmd)` - Execute code with tracing
  - `tracer.results()` - Get CoverageResults object
- **Key Code**:
  ```python
  import trace

  tracer = trace.Trace(
      trace=False,   # Don't display line-by-line trace
      count=True,    # Count how many times each line was executed
  )
  tracer.run("target_function()")
  res = tracer.results()
  res.write_results(show_missing=True)
  ```
- **Alternative**: `sys.settrace()` for custom trace functions with frame-level control

**Repository 2**: [coverage.py](https://coverage.readthedocs.org/en/latest/howitworks.html)
- **URL**: https://coverage.readthedocs.org/
- **Relevance**: Popular third-party coverage tool with C-optimized trace function
- **Key Insight**: Uses `sys.settrace` internally but optimized for performance
- **Warning**: Adds overhead; for our use case, simpler trace module is sufficient

**Query 2: EvalPlus HumanEval execution harness**

**Repository 1**: [evalplus/evalplus](https://github.com/evalplus/evalplus) (⭐ 1700+)
- **URL**: https://github.com/evalplus/evalplus
- **Relevance**: Official evaluation framework for HumanEval+ and MBPP+
- **Key Features**:
  - HumanEval+: 80x more tests than original HumanEval
  - MBPP+: 35x more tests than original MBPP
  - Safe code execution within Docker
- **Installation**: `pip install evalplus`
- **Key Code**:
  ```python
  # Load dataset
  from evalplus.data import get_human_eval_plus, get_mbpp_plus

  # Evaluate samples
  evalplus.evaluate --model "model_name" --dataset humaneval
  ```
- **Note**: Provides execution harness but does NOT track execution depth by default

**Repository 2**: [CodeEval-Pro](https://github.com/CodeEval-Pro/CodeEval-Pro)
- **URL**: https://github.com/CodeEval-Pro/CodeEval-Pro
- **Relevance**: Extended evaluation with execution error statistics
- **Key Feature**: `--run_code` flag provides execution error statistics in log files
- **Insight**: Error categorization available but not execution depth

**Serena Analysis Needed**: false (Code patterns are clear; standard library trace module is well-documented)

### Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is an ANALYSIS hypothesis (no model training). Implementation priority:

1. **Python trace module** (HIGHEST): Standard library, well-documented, directly measures lines executed
2. **EvalPlus harness**: Reuse H-E1 cached execution results for error traces
3. **scipy.stats.ttest_ind**: Standard statistical test for comparing means

**Recommended Implementation Path:**
- Primary: Python `trace` module with custom wrapper to compute execution_depth = lines_executed / total_lines
- Fallback: `sys.settrace()` with custom frame counter if trace module has limitations
- Justification: Standard library approach is reliable, portable, and requires no external dependencies. H-E1 already has execution traces we can reuse to avoid redundant model inference.

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. The Python `trace` module is a well-documented standard library component, and EvalPlus has straightforward APIs. No complex architecture patterns requiring semantic analysis.

**Key Implementation Approach (derived from research):**
1. Use Python's `trace.Trace(count=True, trace=False)` for line counting
2. Wrap code execution in tracer context
3. Parse trace results to compute `lines_executed / total_lines`
4. Apply to H-E1 cached failure cases for both RL and DPO models
5. Compare means with `scipy.stats.ttest_ind()`

---

## Experiment Specification

### Dataset

**Name:** HumanEval+ and MBPP+ (standard code generation benchmarks)
**Type:** standard (NOT synthetic - real code benchmark)
**Source:** evalplus library (https://github.com/evalplus/evalplus)

**Statistics:**
- HumanEval+: 164 problems, 80x more tests than original HumanEval
- MBPP+: 378 problems, 35x more tests than original MBPP
- Total: 542 problems

**Data Reuse Strategy:**
- **CRITICAL:** Reuse H-E1 cached execution results from `h-e1/code/outputs/`
- No new model inference required - only additional analysis of existing traces
- This ensures controlled comparison and avoids redundant computation

**Loading Information** (for Phase 4 download):
- Method: evalplus library + H-E1 cache
- Identifier: `evalplus/humaneval`, `evalplus/mbpp`
- Code:
```python
# Load from H-E1 cached results (primary)
import json
h_e1_results_path = "../h-e1/code/outputs/experiment_results.json"
with open(h_e1_results_path) as f:
    cached_results = json.load(f)

# If fresh data needed (fallback)
from evalplus.data import get_human_eval_plus, get_mbpp_plus
problems_humaneval = get_human_eval_plus()
problems_mbpp = get_mbpp_plus()
```

### Models

#### Baseline Model

**Architecture:** CodeRL-770M (RL-aligned) vs CodeLlama-7B-DPO (DPO-aligned)
**Type:** Pretrained code generation models with different alignment methods

**Model Details:**
| Model | Parameters | Alignment Method | Source |
|-------|------------|------------------|--------|
| CodeRL-770M | 770M | Execution-based RL (binary pass/fail) | salesforce/CodeRL |
| CodeLlama-7B-DPO | 7B | Preference-based DPO | community DPO fine-tunes |

**Data Reuse Strategy:**
- **CRITICAL:** H-M2 is an ANALYSIS hypothesis - no model inference needed
- Reuse H-E1 generated code samples and execution traces
- Only additional analysis (execution depth measurement) is performed

**Loading Information** (for Phase 4 download):
- Method: Load from H-E1 cached outputs (NO new model inference)
- Identifier: N/A (analysis only, no model loading)
- Code:
```python
# Load H-E1 results which contain generated code and error traces
# Models are NOT loaded - this is post-hoc analysis
h_e1_rl_failures = [r for r in cached_results['rl'] if not r['passed']]
h_e1_dpo_failures = [r for r in cached_results['dpo'] if not r['passed']]
```

#### Proposed Model

**Architecture:** Analysis pipeline (no model modification)
**Purpose:** Measure execution depth from existing H-E1 failure cases

**Core Mechanism Implementation:**

```python
# Core Mechanism: Execution Depth Measurement
# Based on: Python trace module (standard library)
# Hypothesis: RL failures execute "deeper" (more lines) than DPO failures

import sys
import trace
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class ExecutionDepthResult:
    """Result of execution depth measurement for a single code sample."""
    total_lines: int
    executed_lines: int
    execution_depth: float  # executed_lines / total_lines
    error_type: str  # syntax, runtime, assertion
    alignment_method: str  # rl, dpo

def measure_execution_depth(code_string: str, test_code: str) -> ExecutionDepthResult:
    """
    Measure how many lines execute before failure.

    Args:
        code_string: Generated code (from H-E1 cache)
        test_code: Test harness code

    Returns:
        ExecutionDepthResult with depth metric
    """
    # Count total executable lines (excluding blanks, comments)
    total_lines = count_executable_lines(code_string)

    # Set up trace with line counting
    tracer = trace.Trace(count=True, trace=False)

    # Execute with tracing (wrapped in try-except)
    try:
        tracer.runfunc(exec, code_string + "\n" + test_code)
        executed_lines = total_lines  # All lines executed if no error
        error_type = "none"
    except SyntaxError:
        executed_lines = 0  # Syntax error = 0 execution depth
        error_type = "syntax"
    except Exception as e:
        # Get executed line count from trace results
        results = tracer.results()
        executed_lines = sum(results.counts.values())
        error_type = classify_runtime_error(e)

    return ExecutionDepthResult(
        total_lines=total_lines,
        executed_lines=executed_lines,
        execution_depth=executed_lines / max(total_lines, 1),
        error_type=error_type,
        alignment_method="unknown"  # Set by caller
    )

# Integration: Apply to all H-E1 failure cases, compare RL vs DPO means
```

### Training Protocol

**Protocol Type:** ANALYSIS (No training required)

This is a post-hoc analysis experiment that measures execution depth on existing H-E1 failure samples:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Mode** | Analysis only | No model training or inference |
| **Data Source** | H-E1 cached results | Reuse for controlled comparison |
| **Samples** | All H-E1 failures | RL: ~236 failures, DPO: ~530 failures |
| **Seed** | N/A | Deterministic analysis |

**Execution Pipeline:**
1. Load H-E1 cached failure cases
2. For each failure: measure execution_depth = lines_executed / total_lines
3. Group by alignment method (RL vs DPO)
4. Compute statistics and t-test

### Evaluation

**Primary Metric:** Execution Depth = lines_executed / total_lines

**Statistical Test:** Independent samples t-test (scipy.stats.ttest_ind)

**Success Criteria (SHOULD_WORK gate):**
- **Primary:** mean(execution_depth | failure, RL) > mean(execution_depth | failure, DPO)
- **Statistical:** t-test p < 0.05 (one-sided, greater)
- **Direction:** RL failures must execute deeper than DPO failures

**Expected Results (from hypothesis):**
- RL failures should have higher execution depth (code runs further before failing)
- DPO failures should have lower execution depth (fail earlier, more syntax/runtime errors)
- Effect direction matches H-M1 finding: RL concentrates failures in assertion errors

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical_comparison
- Library: scipy.stats
- Code:
```python
from scipy import stats

# Independent samples t-test (one-sided)
t_stat, p_value_two = stats.ttest_ind(rl_depths, dpo_depths)
p_value_one = p_value_two / 2 if t_stat > 0 else 1 - p_value_two / 2

# Effect size (Cohen's d)
pooled_std = np.sqrt(((len(rl_depths)-1)*np.var(rl_depths) +
                      (len(dpo_depths)-1)*np.var(dpo_depths)) /
                     (len(rl_depths) + len(dpo_depths) - 2))
cohens_d = (np.mean(rl_depths) - np.mean(dpo_depths)) / pooled_std
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart showing:
  - Mean execution depth: RL vs DPO
  - Error bars (95% CI)
  - p-value annotation

#### Additional Figures (LLM Autonomous)

1. **Execution Depth Distribution**: Violin/box plot comparing RL and DPO depth distributions
2. **Depth by Error Type**: Grouped bar chart showing depth by error category (syntax/runtime/assertion)
3. **Cumulative Distribution**: CDF plot showing how depths are distributed for each alignment method
4. **Scatter Plot**: Execution depth vs total lines, colored by alignment method

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. mean(execution_depth | failure, RL) > mean(execution_depth | failure, DPO)
3. t-test p < 0.05

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1**: JAX Profiling Documentation
- **Type**: Knowledge base article
- **Query Used**: "execution depth code coverage tracing"
- **Relevance**: General profiling approaches (limited direct relevance)
- **Key Insights**:
  - Profiling APIs exist but not specific to Python line tracing
- **Used For**: Background context only

**Source 2**: DL4C Alignment Signatures Synthesis (Serena Memory)
- **Type**: Past case / Pipeline memory
- **Query Used**: Serena memory read: `global/phase45/dl4c_alignment_signatures_2026`
- **Relevance**: Prior DL4C pipeline validated alignment signature detection
- **Key Insights**:
  - POC validation with simulated data is acceptable for demonstrating method works
  - Cohen's d = 7.835 demonstrates large effect sizes are detectable
  - Reuse cached execution traces to avoid redundant computation
- **Used For**: Data reuse strategy, POC validation approach

### Archon Code Examples

**Code Source 1**: No directly relevant code examples found
- **Query Used**: "Python trace coverage module"
- **Note**: Archon KB primarily contains diffusion model examples
- **Used For**: N/A - relied on Exa/standard library instead

### B. GitHub Implementations (Exa)

**Repository 1**: Python Standard Library - trace module
- **URL**: https://docs.python.org/3/library/trace.html
- **Query Used**: "Python trace module execution coverage lines executed"
- **Relevance**: Official Python module for tracking statement execution
- **Key Code** (annotated):
  ```python
  import trace

  tracer = trace.Trace(
      trace=False,   # Don't display line-by-line trace
      count=True,    # Count how many times each line was executed
  )
  tracer.run("target_function()")
  res = tracer.results()
  res.write_results(show_missing=True)
  ```
- **Configuration Extracted**: count=True, trace=False for silent counting
- **Used For**: Core mechanism pseudo-code (execution depth measurement)

**Repository 2**: EvalPlus (evalplus/evalplus)
- **URL**: https://github.com/evalplus/evalplus
- **Stars**: 1700+
- **Query Used**: "evalplus HumanEval code execution harness Python error trace"
- **Relevance**: Official evaluation framework for HumanEval+/MBPP+
- **Key Features**:
  - HumanEval+: 80x more tests than original
  - MBPP+: 35x more tests than original
  - Safe code execution within Docker
- **Used For**: Dataset specification, evaluation harness reference

**Repository 3**: Coverage.py Documentation
- **URL**: https://coverage.readthedocs.org/en/latest/howitworks.html
- **Query Used**: "Python trace module execution coverage"
- **Relevance**: Explains how coverage tools work internally
- **Key Insights**:
  - Uses sys.settrace internally
  - C-optimized trace function for performance
  - Our use case is simpler (post-hoc analysis of small code snippets)
- **Used For**: Understanding trace mechanisms, fallback option

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear

The Python `trace` module and EvalPlus library are well-documented standard tools that don't require semantic code analysis.

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report - H-M1
- **File**: `h-m1/04_validation.md`
- **Reused Components**:
  - Dataset: HumanEval+ and MBPP+ - Same benchmark suite
  - Data: H-E1 cached failure results (236 RL failures, 530 DPO failures)
  - Error classification: ICSE 2025 taxonomy (syntax/runtime/assertion)
- **Why Reused**: Enables controlled experiment - only analysis method changes, not data

**Key H-M1 Results Referenced**:
- Fisher's exact test: p = 0.0027
- RL assertion proportion: 2.12% (5/236)
- DPO assertion proportion: 0.00% (0/530)

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Phase 2A/2B | 02b_context.md "Experimental Setup" |
| Dataset details | Exa GitHub | EvalPlus repository (B.2) |
| Data reuse strategy | Serena Memory | DL4C synthesis (A.2) |
| Execution depth mechanism | Exa/Standard Lib | Python trace module (B.1) |
| Pseudo-code | Exa + trace docs | B.1 + Python docs |
| Statistical test | Standard practice | scipy.stats.ttest_ind |
| Success criteria | Phase 2B | 02b_verification_plan.md |
| Previous results | Previous hypothesis | H-M1/04_validation.md (D.1) |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-24

### Workflow History for This Hypothesis
- 2026-03-24: H-M2 set to IN_PROGRESS (hypothesis loop)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
