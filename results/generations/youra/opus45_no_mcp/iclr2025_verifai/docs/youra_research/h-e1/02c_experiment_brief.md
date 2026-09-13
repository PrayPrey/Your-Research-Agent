# Experiment Design: H-E1

**Date:** 2026-08-19
**Author:** Anonymous
**Hypothesis Statement:** Errors detected by static analysis (pylint/mypy) are categorically different from errors detected by execution (test failures).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** N/A (no prerequisites)
**Gate Status:** MUST_WORK - Jaccard similarity < 0.3

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
- **Type:** MUST_WORK
- **Pass Condition:** Jaccard similarity < 0.3 between static and execution error sets
- **Fail Action:** STOP - feedback types likely redundant

---

## Continuation Context

First hypothesis in verification chain. No previous context.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Archon MCP unavailable in this environment. Research conducted via web search.*

**Key Findings:**
- EvalPlus framework provides rigorous evaluation by automatically expanding code test suites
- HumanEval+ extends tests by 80x, MBPP+ by 35x for more comprehensive assessment
- Static analysis methods do not execute programs, examining code structure algorithmically
- Execution feedback includes runtime errors and test run results from actual code execution

### Archon Code Examples

*Archon MCP unavailable. Code patterns from web research:*

**Self-Refine Pattern (github.com/madaan/self-refine):**
- LLM generates initial output
- Iteratively provides feedback on own output
- Revises based on feedback
- ~20% improvement across diverse tasks

### Exa GitHub Implementations

**Official Implementations Found:**
1. **EvalPlus**: https://evalplus.github.io/ - Official benchmark with HumanEval+ and MBPP+
2. **Self-Refine**: https://github.com/madaan/self-refine - Official iterative refinement implementation
3. **LLM Self-Correction Papers**: https://github.com/ryokamoi/llm-self-correction-papers - Comprehensive paper list

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is an EXISTENCE hypothesis testing error class orthogonality. No prior implementation exists for this specific comparison - this is the novel contribution.

**Recommended Implementation Path:**
- Primary: Custom error classification pipeline using evalplus + pylint/mypy
- Fallback: Subset analysis (100 problems) if full 563 too slow
- Justification: No existing implementation compares static vs execution error classes with Jaccard similarity

### Code Analysis (Serena MCP)

*Serena MCP unavailable. Manual analysis:*

**Required Components:**
1. evalplus library for HumanEval+/MBPP+ loading and test execution
2. pylint + mypy for static analysis
3. Jaccard similarity computation between error sets
4. Error categorization logic (structural vs behavioral)

---

## Experiment Specification

### Dataset

| Attribute | Value |
|-----------|-------|
| **Name** | HumanEval+ and MBPP+ |
| **Type** | standard |
| **Source** | evalplus (neuralmagic/evalplus) |
| **Size** | 563 problems (164 HumanEval+ + 399 MBPP+) |
| **Splits** | Full test set (no train/val needed for this analysis) |
| **Preprocessing** | None - use raw problem definitions |

**Loading Information** (for Phase 4 download):
- Method: pip install + API
- Identifier: evalplus
- Code:
```python
from evalplus.data import get_human_eval_plus, get_mbpp_plus

humaneval_problems = get_human_eval_plus()  # 164 problems
mbpp_problems = get_mbpp_plus()  # 399 problems
all_problems = {**humaneval_problems, **mbpp_problems}  # 563 total
```

### Models

#### Baseline Model

| Attribute | Value |
|-----------|-------|
| **Name** | CodeLlama-7B-Instruct or GPT-3.5-Turbo |
| **Type** | Code Generation LLM |
| **Source** | HuggingFace or OpenAI API |
| **Purpose** | Generate initial code solutions for error analysis |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers or OpenAI API
- Identifier: codellama/CodeLlama-7b-Instruct-hf or gpt-3.5-turbo
- Code:
```python
# Option A: HuggingFace
from transformers import AutoTokenizer, AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained("codellama/CodeLlama-7b-Instruct-hf")
tokenizer = AutoTokenizer.from_pretrained("codellama/CodeLlama-7b-Instruct-hf")

# Option B: OpenAI API
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(model="gpt-3.5-turbo", messages=[...])
```

#### Proposed Model

**Architecture:** N/A - This is an error classification analysis, not model comparison

**Core Mechanism Implementation:**

```python
# H-E1: Error Class Orthogonality Analysis
# Goal: Compute Jaccard similarity between static and execution error sets

import subprocess
from typing import Set, Dict, Tuple
from evalplus.data import get_human_eval_plus, get_mbpp_plus
from evalplus.evaluate import evaluate_functional_correctness

def run_static_analysis(code: str) -> Set[str]:
    """Run pylint + mypy, return set of error codes."""
    errors = set()
    
    # pylint analysis
    result = subprocess.run(
        ["pylint", "--output-format=json", "-"],
        input=code, capture_output=True, text=True
    )
    for item in json.loads(result.stdout or "[]"):
        errors.add(f"pylint:{item['message-id']}")
    
    # mypy analysis
    result = subprocess.run(
        ["mypy", "--no-error-summary", "-"],
        input=code, capture_output=True, text=True
    )
    for line in result.stdout.splitlines():
        if "error:" in line:
            errors.add(f"mypy:{line.split('error:')[1].strip()[:50]}")
    
    return errors

def run_execution_tests(problem_id: str, code: str) -> Set[str]:
    """Run evalplus tests, return set of failure types."""
    failures = set()
    # Use evalplus execution framework
    results = evaluate_functional_correctness(problem_id, code)
    for test_id, outcome in results.items():
        if outcome != "passed":
            failures.add(f"exec:{outcome}")  # wrong_answer, runtime_error, timeout
    return failures

def compute_jaccard(set_a: Set, set_b: Set) -> float:
    """Jaccard similarity: |A ∩ B| / |A ∪ B|"""
    if not set_a and not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0

def analyze_error_orthogonality(problems: Dict) -> Dict:
    """Main analysis: compute Jaccard across all problems."""
    results = {"jaccard_scores": [], "static_only": 0, "exec_only": 0, "both": 0}
    
    for problem_id, problem in problems.items():
        code = generate_code(problem)  # LLM generates solution
        
        static_errors = run_static_analysis(code)
        exec_errors = run_execution_tests(problem_id, code)
        
        jaccard = compute_jaccard(static_errors, exec_errors)
        results["jaccard_scores"].append(jaccard)
        
        # Track overlap categories
        if static_errors and not exec_errors:
            results["static_only"] += 1
        elif exec_errors and not static_errors:
            results["exec_only"] += 1
        elif static_errors and exec_errors:
            results["both"] += 1
    
    results["mean_jaccard"] = sum(results["jaccard_scores"]) / len(results["jaccard_scores"])
    results["non_overlapping_pct"] = (results["static_only"] + results["exec_only"]) / len(problems)
    
    return results
```

### Training Protocol

**N/A - This is an analysis experiment, not a training experiment.**

| Attribute | Value |
|-----------|-------|
| **Type** | Error Classification Analysis |
| **Training Required** | No |
| **Inference Runs** | 563 (one per problem) |
| **Static Analysis Runs** | 563 |
| **Execution Test Runs** | 563 |

### Evaluation

| Metric | Description | Success Threshold |
|--------|-------------|-------------------|
| **Mean Jaccard Similarity** | Average overlap between static and execution error sets | < 0.3 (GATE) |
| **Non-Overlapping %** | Problems with errors from only one source | > 70% |
| **Static-Only Count** | Problems with pylint/mypy errors but passing tests | Report |
| **Exec-Only Count** | Problems with test failures but no static errors | Report |

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Error Classification / Set Similarity
- Library: scikit-learn (jaccard_score) or custom implementation
- Code:
```python
from sklearn.metrics import jaccard_score
# Or use custom implementation above

def evaluate_gate(results: Dict) -> Tuple[bool, str]:
    """Check if MUST_WORK gate passes."""
    mean_jaccard = results["mean_jaccard"]
    non_overlapping = results["non_overlapping_pct"]
    
    gate_passed = mean_jaccard < 0.3
    message = f"Jaccard={mean_jaccard:.3f} ({'PASS' if gate_passed else 'FAIL'})"
    
    if non_overlapping >= 0.7:
        message += f", Non-overlapping={non_overlapping:.1%} (PASS)"
    
    return gate_passed, message
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing Jaccard threshold (0.3) vs actual mean Jaccard

#### Additional Figures (LLM Autonomous)

1. **Error Distribution Histogram**: Distribution of Jaccard scores across 563 problems
2. **Venn Diagram**: Overlap between static and execution error sets
3. **Error Category Breakdown**: Stacked bar showing static-only, exec-only, both categories
4. **Per-Benchmark Comparison**: HumanEval+ vs MBPP+ Jaccard distributions

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error on all 563 problems
2. Mean Jaccard similarity < 0.3 (GATE CONDITION)
3. Non-overlapping percentage > 70% (secondary)

**Direction-Based Success (PoC):**
- No statistical tests required for EXISTENCE hypothesis
- Simple threshold check: Jaccard < 0.3

---

## Appendix: Reference Implementations

### A. EvalPlus Framework
- **URL**: https://evalplus.github.io/
- **GitHub**: https://github.com/evalplus/evalplus
- **Usage**: Dataset loading, test execution framework
- **Relevance**: Primary source for HumanEval+/MBPP+ problems and evaluation

### B. Self-Refine
- **URL**: https://github.com/madaan/self-refine
- **Paper**: "Self-Refine: Iterative Refinement with Self-Feedback" (NeurIPS 2023)
- **Usage**: Reference for feedback-based refinement (used in H-M3, H-M4)
- **Relevance**: Background for overall research direction

### C. Static Analysis Tools
- **pylint**: https://pylint.org/ - Python linting with error codes
- **mypy**: https://mypy-lang.org/ - Static type checking
- **Usage**: Static error detection component

### D. Jaccard Similarity
- **Reference**: Standard set similarity metric
- **Formula**: J(A,B) = |A ∩ B| / |A ∪ B|
- **Threshold**: < 0.3 indicates low overlap (error classes are distinct)

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- 2026-08-19: Phase 2C Experiment Design started (IN_PROGRESS)
- 2026-08-19: Research completed (WebSearch - Archon/Exa unavailable)
- 2026-08-19: Experiment specification synthesized

---

*Research Tools Used: WebSearch (Archon/Exa MCP unavailable)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
