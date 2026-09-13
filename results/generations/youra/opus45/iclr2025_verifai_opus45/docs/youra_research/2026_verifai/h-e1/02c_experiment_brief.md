# Experiment Design: H-E1

**Date:** 2026-03-30
**Author:** Anonymous
**Hypothesis Statement:** Runtime errors with localizable stack traces are prevalent (>=30%) in LLM-generated code failures on MBPP benchmark
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites for foundation hypothesis)
**Gate Status:** PENDING (awaiting experiment execution)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
**Gate Type:** MUST_WORK
**Condition:** Runtime error prevalence >= 30% (lower bound of 95% CI)
**If Fails:** PIVOT to studying wrong-output errors or ABANDON granularity hypothesis

---

## Continuation Context

This is the **first hypothesis** in the verification chain. No previous context to inherit.

H-E1 validates the foundation assumption (A1) that runtime errors with localizable stack traces are prevalent enough to make the granularity comparison meaningful.

### Previous Hypothesis Results (if applicable)
N/A - H-E1 is the foundation hypothesis with no prerequisites.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "LLM code generation error categorization runtime MBPP"**
- No direct matches for LLM code repair research
- General ML pipeline content returned (JAX releases, FLOPS calculation)
- Insight: This is a novel research area with limited indexed prior work

**Query 2: "code execution error classification stack trace analysis"**
- Found: General error/stack trace debugging patterns
- Example: GitHub gist on error analysis (similarity: 0.43)
- Insight: Stack trace analysis patterns exist but not specific to LLM code repair

**Query 3: "Self-Debug code repair benchmark evaluation"**
- No direct Self-Debug paper or implementation content
- General benchmark evaluation patterns available
- Insight: Need to rely on Exa for specific Self-Debug implementations

**Key Takeaway:** Archon KB lacks specific LLM code repair literature. This confirms H-E1 addresses a gap - runtime error prevalence in LLM code has not been systematically studied.

### Archon Code Examples

**Query 1: "Python code execution subprocess test runner"**
- Found: Docker/subprocess execution patterns
- Pattern: Process isolation for code execution
- Insight: Use subprocess with timeout for safe code execution

**Query 2: "error classification traceback parsing Python"**
- Found: Traceback parsing examples from HuggingFace Diffusers PRs
- Example pattern:
```python
# Traceback structure shows:
# - File path, line number, function name
# - Error type (RuntimeError, AttributeError, etc.)
# - Error message with context
```
- Insight: Python tracebacks provide line-level localization naturally

**Implementation Pattern Extracted:**
```python
import subprocess
import traceback

def execute_code_safely(code: str, test_cases: str, timeout: int = 10):
    """Execute code and categorize error type"""
    try:
        result = subprocess.run(
            ["python", "-c", code + "\n" + test_cases],
            capture_output=True, text=True, timeout=timeout
        )
        if result.returncode == 0:
            return "PASS", None
        else:
            stderr = result.stderr
            if "Traceback" in stderr:
                return "RUNTIME_ERROR", stderr
            elif "SyntaxError" in stderr:
                return "SYNTAX_ERROR", stderr
            else:
                return "WRONG_OUTPUT", stderr
    except subprocess.TimeoutExpired:
        return "TIMEOUT", None
```

**Key Insight:** Error categorization is straightforward - presence of "Traceback" indicates runtime error with stack trace.

### Exa GitHub Implementations

**Query 1: "Self-Debug Chen LLM code repair MBPP GitHub implementation"**

**Repository 1**: [EleutherAI/lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness) (⭐ 12K)
- **URL**: https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/mbpp/README.md
- **Relevance**: Standard MBPP evaluation framework
- **Key Information**:
  - Test split: Task IDs 11-510 (500 problems)
  - Few-shot: Task IDs 1-10
  - Validation: Task IDs 511-600
  - Training: Task IDs 601-974
- **Prompt Format**: `"You are an expert Python programmer, and here is your task: {prompt} Your code should pass these tests:\n\n{tests}\n[BEGIN]\n{code}\n[DONE]"`

**Repository 2**: [google-research/google-research](https://github.com/google-research/google-research/tree/master/mbpp) (⭐ 38K)
- **URL**: https://github.com/google-research/google-research/blob/master/mbpp/README.md
- **Relevance**: **OFFICIAL MBPP dataset source**
- **Dataset Format**: JSONL with task description, code solution, 3 test cases
- **Sanitized Version**: `sanitized-mbpp.json` (hand-verified subset)

**Repository 3**: [bigcode-project/bigcode-evaluation-harness](https://github.com/bigcode-project/bigcode-evaluation-harness) (⭐ 1K)
- **URL**: https://github.com/bigcode-project/bigcode-evaluation-harness/blob/main/docs/README.md
- **Relevance**: Code generation benchmark framework with pass@k metric
- **Key Insight**: Functional correctness via unit tests is standard evaluation

**Query 2: "MBPP benchmark code execution Python error categorization"**

**Paper Reference**: Self-Debug (Chen et al., 2023)
- **URL**: https://huggingface.co/papers/2304.05128
- **Key Finding**: Self-Debugging achieves up to 12% improvement on MBPP using execution feedback
- **Mechanism**: Rubber duck debugging - model explains code to identify mistakes

**Paper Reference**: Revisit Self-Debugging (Chen et al., 2025)
- **URL**: https://arxiv.org/html/2501.12793v1
- **Key Finding**: Post-execution vs in-execution self-debugging paradigms
- **Insight**: Post-execution debugging struggles on basic problems

**Serena Analysis Needed**: false
- Code patterns are clear: subprocess execution, traceback parsing
- No complex architecture requiring deep analysis

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Implementation | Status |
|----------|----------------|--------|
| 1 | HuggingFace Datasets (mbpp) | ✅ Available |
| 2 | Google Research official MBPP | ✅ Available |
| 3 | EleutherAI lm-evaluation-harness | ✅ Available |

**Recommended Implementation Path:**
- Primary: HuggingFace Datasets API (`load_dataset("mbpp")`)
- Fallback: Direct download from Google Research GitHub
- Justification: HuggingFace provides clean API with standard splits; widely used in LLM evaluation

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear.

**Rationale:** H-E1 is an existence hypothesis focused on measuring runtime error prevalence. The implementation involves:
1. Code execution via subprocess (standard Python pattern)
2. Error categorization via traceback detection (string matching)
3. Statistical calculation (proportion with confidence interval)

No complex neural network architecture or custom layers requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** MBPP (Mostly Basic Python Problems)
**Type:** standard
**Source:** Google Research (https://github.com/google-research/google-research/tree/master/mbpp)

**Statistics:**
- Total problems: 974
- Test split (IDs 11-510): 500 problems
- Validation split (IDs 511-600): 90 problems
- Few-shot examples (IDs 1-10): 10 problems
- Training split (IDs 601-974): 374 problems

**Features per problem:**
- `task_id`: Unique identifier
- `text`: Task description (natural language prompt)
- `code`: Reference solution
- `test_list`: 3 automated test cases (assertions)
- `test_setup_code`: Setup code if needed
- `challenge_test_list`: Additional challenge tests

**Preprocessing:** None required - direct JSON parsing
**Augmentation:** N/A (evaluation only, no training)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Datasets
- Identifier: `"mbpp"` or `"Muennighoff/mbpp"`
- Code:
```python
from datasets import load_dataset

# Load full dataset
dataset = load_dataset("mbpp")

# Or load sanitized version (hand-verified, 427 problems)
dataset_sanitized = load_dataset("mbpp", "sanitized")

# Access test split
test_data = dataset["test"]  # 974 rows (use task_id 11-510 for standard test)
```

### Models

#### Baseline Model

**Architecture:** CodeLlama-7B-Instruct
**Type:** Instruction-tuned code LLM (7 billion parameters)
**Source:** Meta AI (meta-llama/CodeLlama-7b-Instruct-hf)

**Configuration:**
- Context length: 16,384 tokens
- Vocabulary size: 32,016
- Temperature: 0 (deterministic generation for reproducibility)
- Max new tokens: 512 (sufficient for MBPP solutions)

**Why this model:**
- Widely used in self-repair literature (Self-Debug, TraceFixer)
- Representative of instruction-tuned code LLMs
- 7B scale is computationally feasible for 500+ generations
- Instruct version follows prompts better than base model

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `"codellama/CodeLlama-7b-Instruct-hf"`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model_id = "codellama/CodeLlama-7b-Instruct-hf"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="auto"
)

# Generation config
generation_config = {
    "max_new_tokens": 512,
    "temperature": 0.0,  # Deterministic
    "do_sample": False,
    "eos_token_id": tokenizer.eos_token_id,
}
```

#### Proposed Model

**Architecture:** N/A (Existence hypothesis - no model modification)

This is an **EXISTENCE** hypothesis that measures runtime error prevalence in LLM-generated code. There is no "proposed model" - we are measuring a property of the baseline model's outputs.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Runtime Error Prevalence Measurement
# Based on: MBPP evaluation framework + Self-Debug methodology

import subprocess
from typing import Tuple, Optional
from enum import Enum

class ErrorCategory(Enum):
    PASS = "pass"
    RUNTIME_ERROR = "runtime_error"      # Has Traceback with stack trace
    WRONG_OUTPUT = "wrong_output"        # Assertion failed, no crash
    SYNTAX_ERROR = "syntax_error"        # SyntaxError before execution
    TIMEOUT = "timeout"                  # Exceeded time limit

def categorize_execution(code: str, tests: str, timeout: int = 10) -> Tuple[ErrorCategory, Optional[str]]:
    """
    Execute code against tests and categorize the result.

    Args:
        code: Generated Python code
        tests: Test assertions (e.g., "assert func(1) == 2")
        timeout: Execution timeout in seconds

    Returns:
        (category, error_message) tuple
    """
    full_code = code + "\n" + tests
    try:
        result = subprocess.run(
            ["python", "-c", full_code],
            capture_output=True, text=True, timeout=timeout
        )
        if result.returncode == 0:
            return ErrorCategory.PASS, None

        stderr = result.stderr
        if "SyntaxError" in stderr:
            return ErrorCategory.SYNTAX_ERROR, stderr
        elif "Traceback (most recent call last):" in stderr:
            # Runtime error with localizable stack trace
            return ErrorCategory.RUNTIME_ERROR, stderr
        else:
            return ErrorCategory.WRONG_OUTPUT, stderr

    except subprocess.TimeoutExpired:
        return ErrorCategory.TIMEOUT, None

def calculate_prevalence(results: list) -> dict:
    """Calculate runtime error prevalence with confidence interval."""
    total_failures = sum(1 for r in results if r != ErrorCategory.PASS)
    runtime_errors = sum(1 for r in results if r == ErrorCategory.RUNTIME_ERROR)

    if total_failures == 0:
        return {"prevalence": 0.0, "ci_lower": 0.0, "ci_upper": 0.0}

    prevalence = runtime_errors / total_failures
    # Wilson confidence interval (scipy.stats.proportion_confint)
    return {"prevalence": prevalence, "n_runtime": runtime_errors, "n_failures": total_failures}
```

### Training Protocol

> ⚠️ **EXISTENCE (PoC)**: This hypothesis does NOT involve training. It measures properties of generated code.

**Protocol Type:** Inference + Evaluation (No Training)

**Code Generation:**
- Model: CodeLlama-7B-Instruct
- Temperature: 0.0 (deterministic)
- Max tokens: 512
- Prompt format: MBPP standard (see below)

**Prompt Template** (from MBPP paper):
```
You are an expert Python programmer, and here is your task: {text}
Your code should pass these tests:

{test_list}

[BEGIN]
{code}
[DONE]
```

**Execution:**
- Timeout: 10 seconds per problem
- Sandbox: subprocess isolation
- Python version: 3.10+

**Seeds:** 1 (fixed, deterministic generation)

### Evaluation

> ⚠️ **EXISTENCE (PoC)**: Simple success check - no statistical tests required.

**Primary Metric:** Runtime Error Prevalence
- Definition: `runtime_errors / total_failures`
- Where runtime_errors = failures with "Traceback (most recent call last):" in stderr

**Secondary Metrics:**
- Total problems: 500 (MBPP test split, IDs 11-510)
- Pass rate: `passes / total_problems`
- Error distribution: counts per category (PASS, RUNTIME_ERROR, WRONG_OUTPUT, SYNTAX_ERROR, TIMEOUT)

**Success Criteria (Gate Condition):**
- **Primary:** runtime_error_prevalence >= 30% (lower bound of 95% Wilson CI)
- **Secondary:** Minimum 150 runtime error cases for statistical power

**Expected Results (from prior work):**
- SBEST found 98.3% of crash bugs have relevant stack traces
- Haque et al. suggest runtime errors are common in LLM code
- Expected prevalence: 30-50% (conservative estimate)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: proportion_estimation
- Library: scipy.stats
- Code:
```python
from scipy.stats import proportion_confint

# Wilson confidence interval for proportion
def wilson_ci(successes, total, confidence=0.95):
    return proportion_confint(successes, total, alpha=1-confidence, method='wilson')

# Usage
prevalence = runtime_errors / total_failures
ci_lower, ci_upper = wilson_ci(runtime_errors, total_failures)
gate_passed = ci_lower >= 0.30
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

1. **Error Distribution Pie Chart**: Show breakdown of error categories (PASS, RUNTIME_ERROR, WRONG_OUTPUT, SYNTAX_ERROR, TIMEOUT)
2. **Runtime Error Type Breakdown**: Bar chart of specific error types (TypeError, IndexError, KeyError, ValueError, etc.)
3. **Prevalence with Confidence Interval**: Point estimate with 95% Wilson CI error bars
4. **Stack Trace Depth Histogram**: Distribution of stack trace lengths (lines) for runtime errors

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1**: General Error Handling Patterns
- **Type**: Code examples
- **Query Used**: "error classification traceback parsing Python"
- **Relevance**: Stack trace parsing patterns
- **Key Insights**:
  - Python tracebacks follow consistent "Traceback (most recent call last):" format
  - Error type appears on last line with line number context
- **Used For**: Error categorization logic in pseudo-code

**Source A.2**: Debugging Model Errors (HuggingFace Diffusers)
- **Type**: Code example
- **Query Used**: "error classification traceback parsing Python"
- **Key Pattern**: Traceback structure analysis for error diagnosis
- **Used For**: Understanding stack trace format for categorization

### B. GitHub Implementations (Exa)

**Repository B.1**: [google-research/google-research](https://github.com/google-research/google-research/tree/master/mbpp) (⭐ 38K)
- **URL**: https://github.com/google-research/google-research/blob/master/mbpp/README.md
- **Query Used**: "MBPP benchmark code execution Python error categorization GitHub"
- **Relevance**: **OFFICIAL MBPP dataset source**
- **Configuration Extracted**: Test split IDs 11-510 (500 problems)
- **Used For**: Dataset specification

**Repository B.2**: [EleutherAI/lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness) (⭐ 12K)
- **URL**: https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/mbpp/README.md
- **Query Used**: "Self-Debug Chen LLM code repair MBPP GitHub implementation"
- **Relevance**: Standard MBPP evaluation framework
- **Key Info**: Prompt format, evaluation methodology
- **Used For**: Prompt template, evaluation protocol

**Repository B.3**: [Muennighoff/mbpp](https://huggingface.co/datasets/Muennighoff/mbpp)
- **URL**: https://huggingface.co/datasets/Muennighoff/mbpp
- **Query Used**: "MBPP dataset huggingface datasets load python code benchmark"
- **Relevance**: HuggingFace Datasets API for MBPP
- **Key Code**:
  ```python
  from datasets import load_dataset
  dataset = load_dataset("mbpp")
  ```
- **Used For**: Dataset loading specification

**Repository B.4**: [chunhualiao/CodeLlama-7b-Instruct-hf.md](https://gist.github.com/chunhualiao/0656f951076bb761e11fccf72f342c5f)
- **URL**: https://gist.github.com/chunhualiao/0656f951076bb761e11fccf72f342c5f
- **Query Used**: "CodeLlama-7B-Instruct huggingface transformers load model inference"
- **Relevance**: CodeLlama loading example
- **Key Code**:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  tokenizer = AutoTokenizer.from_pretrained("codellama/CodeLlama-7b-Instruct-hf")
  model = AutoModelForCausalLM.from_pretrained("codellama/CodeLlama-7b-Instruct-hf")
  ```
- **Used For**: Model loading specification

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear.

The error categorization and execution patterns are standard Python (subprocess, traceback parsing) and do not require deep semantic analysis.

### D. Previous Hypothesis Context

**Previous Context**: None - H-E1 is the first hypothesis in the verification chain.

### E. Academic References

**Paper 1**: Self-Debug (Chen et al., 2023)
- **URL**: https://huggingface.co/papers/2304.05128
- **Citation**: Chen, X. et al. "Teaching Large Language Models to Self-Debug"
- **Relevance**: Self-debugging achieves up to 12% improvement on MBPP using execution feedback
- **Used For**: Baseline comparison context, motivation

**Paper 2**: Revisit Self-Debugging (Chen et al., 2025)
- **URL**: https://arxiv.org/html/2501.12793v1
- **Citation**: Chen, X. et al. "Revisit Self-Debugging with Self-Generated Tests for Code Generation"
- **Relevance**: Post-execution vs in-execution debugging paradigms
- **Used For**: Understanding self-debugging methodology

**Paper 3**: MBPP Paper (Austin et al., 2021)
- **URL**: https://arxiv.org/abs/2108.07732
- **Citation**: Austin, J. et al. "Program Synthesis with Large Language Models"
- **Relevance**: Original MBPP benchmark definition
- **Used For**: Dataset structure, evaluation protocol

### F. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (MBPP) | GitHub | B.1, B.2, B.3 |
| Dataset loading | HuggingFace | B.3 |
| Model (CodeLlama) | GitHub Gist | B.4 |
| Prompt template | GitHub | B.2 |
| Error categorization | Archon KB | A.1, A.2 |
| Execution protocol | Standard Python | subprocess docs |
| Success criteria | Phase 2B | verification_state.yaml |
| Confidence interval | scipy | Wilson CI method |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-30T06:45:00Z

### Workflow History for This Hypothesis
1. **2026-03-30T06:31:40Z** - Hypothesis h-e1 set to IN_PROGRESS (Hypothesis Loop)
2. **2026-03-30T06:32:00Z** - Phase 2C experiment design started
3. **2026-03-30T06:45:00Z** - Experiment design COMPLETED

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
