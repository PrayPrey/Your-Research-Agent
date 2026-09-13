# Experiment Design: H-M1

**Date:** 2026-08-10
**Author:** Anonymous
**Hypothesis Statement:** Execution trace collection enables accurate token-level execution classification
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Validates causal step in FGO mechanism chain.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 (PASS)
**Gate Status:** MUST_WORK (pending)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED)

### Gate Condition
MUST_WORK: Token classification accuracy > 95% required. If fails, explore alternative trace methods (AST-based, bytecode).

---

## Continuation Context

Building on H-E1 (FGO existence validation). H-E1 proved FGO improves performance across all content types. H-M1 validates the first causal step: can we accurately identify which tokens were executed?

### Previous Hypothesis Results (if applicable)
H-E1 PASS: FGO token masking improves code generation (compile +2.15, test +2.24, combined +2.24).

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**JAX Profiling (jax.readthedocs.io):** Profiling and tracing mechanisms for performance analysis.

**Python Style Guide (google.github.io):** Standard Python execution and tracing patterns.

*Note: Limited direct matches for execution trace collection in KB. Primary implementation guidance from Exa search.*

### Archon Code Examples

No direct code examples for Python trace module found in KB. Implementation derived from Python stdlib documentation.

### Exa GitHub Implementations

**1. Python trace module (docs.python.org/3/library/trace.html)**
- `trace.Trace(count=1, trace=1)` - Core tracing class
- `sys.settrace()` - Low-level trace hook
- Line-level coverage via `tracer.run()` and `tracer.results()`

**2. Coverage.py (coveragepy/coveragepy)**
- Three measurement cores: `ctrace` (C), `pytrace` (Python), `sysmon` (Python 3.12+)
- Uses `sys.settrace` for line-level coverage
- Records `(prev, this)` line pairs for branch coverage
- `co_lines()` method for bytecode-to-line mapping

**3. TracerSET (SET-IITGN/TracerSET)**
- Step-by-step execution tracing
- Runtime stack visualization
- Source code highlighting during execution
- Token stream analysis (whole-program and execution-aligned views)

**4. PEP 626 - Precise line numbers**
- `co_lines()` method returns (start, end, line) tuples
- `f_lineno` attribute always contains expected line number
- Line events generated for all executed lines

**5. PyMOTW sys.settrace (pymotw.com/3/sys/tracing.html)**
- Event types: call, line, return, exception, c_call, c_return, c_exception
- Frame object provides `f_code`, `f_lineno`, `f_locals`
- Local trace function for line-by-line tracing

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

StepCoder (ACL 2024) is the source paper for FGO. However, trace collection is standard Python - no need for custom implementation.

**Recommended Implementation Path:**
- Primary: Python stdlib `sys.settrace()` + `trace` module
- Fallback: Coverage.py ctrace for performance-critical cases
- Justification: Standard library provides reliable line-level tracing. StepCoder's FGO uses standard Python trace mechanisms for execution coverage. No custom tracer needed.

### Code Analysis (Serena MCP)

*Skipped: No existing codebase to analyze. This is a greenfield implementation using Python stdlib.*

---

## Experiment Specification

### Dataset

**Dataset:** HumanEval + MBPP (standard code generation benchmarks)
**Type:** standard
**Source:** OpenAI (HumanEval), Google (MBPP)

**HumanEval:**
- 164 programming problems
- Test cases provided per problem
- Standard evaluation: pass@1, pass@10

**MBPP:**
- 974 problems (500 test set)
- Python programming tasks
- Multiple test cases per problem

**Hypothesis Fit:** Both datasets provide code with test cases. Tests can be executed to collect line-level traces, enabling token-level execution classification.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `openai_humaneval`, `mbpp`
- Code: `from datasets import load_dataset; humaneval = load_dataset("openai_humaneval"); mbpp = load_dataset("mbpp")`

### Models

#### Baseline Model

**Architecture:** CodeLlama-7B-Instruct
**Type:** Decoder-only transformer, instruction-tuned
**Source:** meta-llama/CodeLlama-7b-Instruct-hf
**Parameters:** 7B

**Hypothesis Fit:** Generates Python code that can be executed with test cases. Standard baseline for code generation research.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `meta-llama/CodeLlama-7b-Instruct-hf`
- Code: `from transformers import AutoModelForCausalLM; model = AutoModelForCausalLM.from_pretrained("meta-llama/CodeLlama-7b-Instruct-hf")`

#### Proposed Model

**Architecture:** Baseline + Execution Trace Collection Module

**Core Mechanism Implementation:**

```python
# Core Mechanism: Execution Trace Collector
# Based on: Python trace module, StepCoder FGO concept

import sys
from typing import Set, Dict, Tuple

class ExecutionTraceCollector:
    """
    Collects line-level execution traces during code execution.
    Maps traces to token positions for FGO masking.
    """
    def __init__(self):
        self.executed_lines: Set[int] = set()
        self.line_to_tokens: Dict[int, Tuple[int, int]] = {}
    
    def trace_function(self, frame, event, arg):
        """Trace callback for sys.settrace()"""
        if event == 'line':
            self.executed_lines.add(frame.f_lineno)
        return self.trace_function
    
    def collect_trace(self, code_str: str, test_input: str) -> Set[int]:
        """Execute code with tracing, return executed line numbers"""
        self.executed_lines.clear()
        compiled = compile(code_str, '<generated>', 'exec')
        
        sys.settrace(self.trace_function)
        try:
            exec(compiled, {'input': lambda: test_input})
        except Exception:
            pass  # Partial execution still provides trace
        finally:
            sys.settrace(None)
        
        return self.executed_lines
    
    def classify_tokens(self, tokens: list, line_map: dict) -> list:
        """Classify each token as executed (1) or not executed (0)"""
        mask = []
        for i, token in enumerate(tokens):
            line_num = line_map.get(i, -1)
            mask.append(1 if line_num in self.executed_lines else 0)
        return mask

# Integration: Applied after code generation, before PPO loss computation
# Token mask used to zero out gradients for non-executed tokens
```

### Training Protocol

**Note:** H-M1 is a MECHANISM validation experiment, NOT a training experiment.

This hypothesis validates trace collection accuracy, not model training.

**Experiment Type:** Validation (no training required)
**Procedure:**
1. Sample N code solutions from HumanEval/MBPP (generated or ground truth)
2. Execute each with test cases while collecting trace
3. Map line traces to token positions
4. Compare token classification against ground truth (manual annotation or AST analysis)
5. Compute accuracy metrics

**Seeds:** 1 (fixed for reproducibility)

### Evaluation

**Primary Metrics:**
- **Token Classification Accuracy:** % of tokens correctly classified as executed/non-executed
- **Line Coverage Accuracy:** % of lines correctly identified as executed
- **Trace Collection Overhead:** Execution time with tracing / baseline execution time

**Success Criteria (PoC):**
- Primary: Token classification accuracy > 95%
- Secondary: Trace overhead < 20× baseline execution time

**Expected Baseline Performance:**
- Python trace module: ~5-10× overhead (from coverage.py documentation)
- Line-level accuracy: Should be 100% for correctly mapped lines
- Token-level accuracy depends on line-to-token mapping quality

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification (executed vs non-executed tokens)
- Library: sklearn.metrics
- Code: `from sklearn.metrics import accuracy_score, precision_recall_fscore_support`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Token classification accuracy bar chart (target: >95%)

#### Additional Figures (LLM Autonomous)

1. **Confusion Matrix:** True/False Positive/Negative for token execution classification
2. **Overhead Distribution:** Histogram of trace collection overhead across samples
3. **Coverage Heatmap:** Visual representation of executed vs non-executed code regions
4. **Line-to-Token Mapping Accuracy:** Per-line accuracy breakdown

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Token classification accuracy > 95%
3. Trace overhead < 20× baseline

---

## Appendix: Reference Implementations

### 1. Python trace module (stdlib)
- **Source:** https://docs.python.org/3/library/trace.html
- **Usage:** `trace.Trace(count=1, trace=1)` for line counting
- **Key API:** `tracer.run(cmd)`, `tracer.results()`

### 2. sys.settrace (stdlib)
- **Source:** https://docs.python.org/3/library/sys.html#sys.settrace
- **Usage:** `sys.settrace(trace_function)` for custom tracing
- **Events:** call, line, return, exception

### 3. Coverage.py
- **Source:** https://github.com/nedbat/coveragepy
- **Key insight:** Uses `ctrace` (C implementation) for performance
- **Branch coverage:** Records (prev, this) line pairs

### 4. PEP 626 - Precise line numbers
- **Source:** https://peps.python.org/pep-0626/
- **Key API:** `code.co_lines()` for bytecode-to-line mapping
- **Frame:** `f_lineno` always contains current line number

### 5. StepCoder FGO (ACL 2024)
- **Source:** https://aclanthology.org/2024.acl-long.251/
- **Concept:** Mask non-executed tokens from gradient computation
- **Method:** Uses execution trace to identify executed lines, maps to tokens

---

## Mechanism Verification Protocol

### Pre-conditions
- `mechanism_exists`: True (Python trace module is stdlib)
- `mechanism_isolatable`: True (trace collection independent of model)
- `baseline_measurable`: True (execution time without tracing)

### Architecture Compatibility
- Python 3.7+ required (co_lines available in 3.10+)
- No model architecture constraints (operates on generated code strings)
- Compatible with any tokenizer that provides offset mapping

### Activation Indicators
- `mechanism_log_message`: "Trace collection completed: {n} lines executed"
- `tensor_shape_change`: N/A (not a neural network module)
- `metric_delta_expected`: Accuracy > 95%, Overhead < 20×

### Verification Code
```python
def verify_trace_mechanism(code: str, test_input: str) -> dict:
    collector = ExecutionTraceCollector()
    
    # Collect trace
    start = time.time()
    executed_lines = collector.collect_trace(code, test_input)
    trace_time = time.time() - start
    
    # Baseline (no trace)
    start = time.time()
    try:
        exec(compile(code, '<test>', 'exec'), {'input': lambda: test_input})
    except:
        pass
    baseline_time = time.time() - start
    
    return {
        'lines_executed': len(executed_lines),
        'overhead': trace_time / max(baseline_time, 1e-6),
        'mechanism_active': len(executed_lines) > 0
    }
```

### Success Thresholds
- `hypothesis_support_metric`: token_classification_accuracy
- `hypothesis_support_threshold`: 0.95

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-10

### Workflow History for This Hypothesis
- H-E1 completed: FGO existence validated (PASS)
- H-M1 started: Trace collection mechanism validation (IN_PROGRESS)
- Phase 2C experiment design: COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in Python stdlib documentation and StepCoder paper*
*Next Phase: Phase 3 - Implementation Planning*
