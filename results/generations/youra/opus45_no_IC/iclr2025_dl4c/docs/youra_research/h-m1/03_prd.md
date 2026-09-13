# Product Requirements Document: H-M1

**Hypothesis:** Execution trace collection enables accurate token-level execution classification
**Type:** MECHANISM
**Date:** 2026-08-10
**Author:** Anonymous

---

## 1. Executive Summary

This PRD defines the implementation requirements for validating hypothesis H-M1: that Python's execution trace collection mechanism can accurately classify tokens as executed or non-executed with >95% accuracy. This is a foundational MECHANISM validation for the FGO (Fine-Grained Optimization) pipeline, building on the confirmed H-E1 existence proof.

**Key Deliverable:** A trace collection module that maps line-level execution traces to token-level classifications, enabling FGO masking for code generation RL.

---

## 2. Problem Statement

### 2.1 Background
FGO (Fine-Grained Optimization) requires knowing which tokens in generated code were actually executed during test case evaluation. This enables selective gradient updates only for executed code paths, improving learning signal quality.

### 2.2 Challenge
Converting line-level Python trace output to token-level classification requires:
1. Reliable line-level trace collection via `sys.settrace()`
2. Accurate mapping from source lines to token positions
3. Handling of edge cases (multi-line statements, comments, etc.)

### 2.3 Success Criteria
- Token classification accuracy > 95%
- Trace collection overhead < 20× baseline execution time

---

## 3. Functional Requirements

### FR-1: Execution Trace Collection
**Priority:** P0 (Critical)
**Description:** Implement `ExecutionTraceCollector` class using Python's `sys.settrace()` API.

**Acceptance Criteria:**
- Captures all executed line numbers during code execution
- Handles exceptions gracefully (partial trace on error)
- Supports sandboxed execution environment

### FR-2: Line-to-Token Mapping
**Priority:** P0 (Critical)
**Description:** Map source code lines to token positions using tokenizer offset mapping.

**Acceptance Criteria:**
- Correctly maps line numbers to token index ranges
- Handles multi-line statements (continuation, block statements)
- Handles comments and whitespace correctly

### FR-3: Token Classification
**Priority:** P0 (Critical)
**Description:** Generate binary mask classifying each token as executed (1) or non-executed (0).

**Acceptance Criteria:**
- Output mask has same length as token sequence
- Classification matches ground truth with >95% accuracy

### FR-4: Ground Truth Generation
**Priority:** P1 (High)
**Description:** Generate ground truth token classifications for validation.

**Methods:**
1. AST-based analysis (identify executable vs non-executable nodes)
2. Manual annotation on sample subset
3. Coverage.py cross-validation

### FR-5: Overhead Measurement
**Priority:** P1 (High)
**Description:** Measure execution time overhead from trace collection.

**Acceptance Criteria:**
- Overhead measurement on 100+ samples
- Report mean, median, and 95th percentile overhead
- Target: < 20× baseline execution time

---

## 4. Data Specification

### 4.1 Primary Datasets

**HumanEval**
- Source: OpenAI
- Size: 164 problems
- Format: Python function completion tasks
- Test cases: Provided per problem
- Loading: `from datasets import load_dataset; humaneval = load_dataset("openai_humaneval")`

**MBPP**
- Source: Google
- Size: 974 problems (500 test set)
- Format: Python programming tasks
- Test cases: Multiple per problem
- Loading: `from datasets import load_dataset; mbpp = load_dataset("mbpp")`

### 4.2 Evaluation Sample Size
- Full test sets: HumanEval (164) + MBPP test (500) = 664 problems
- Minimum 500 samples for statistical validity
- Use complete standard splits, no arbitrary subsets

---

## 5. Models

### 5.1 Baseline Model
**CodeLlama-7B-Instruct**
- Source: meta-llama/CodeLlama-7b-Instruct-hf
- Purpose: Generate Python code for trace collection validation
- Loading: `AutoModelForCausalLM.from_pretrained("meta-llama/CodeLlama-7b-Instruct-hf")`

### 5.2 Proposed Module
**ExecutionTraceCollector**
- Core mechanism being validated (not a neural network)
- Uses Python stdlib `sys.settrace()` and `trace` module
- No model training required

---

## 6. Evaluation Metrics

### 6.1 Primary Metrics
| Metric | Target | Method |
|--------|--------|--------|
| Token Classification Accuracy | > 95% | Compare mask to ground truth |
| Line Coverage Accuracy | 100% | Verify all executed lines captured |

### 6.2 Secondary Metrics
| Metric | Target | Method |
|--------|--------|--------|
| Trace Overhead | < 20× | time_with_trace / time_without_trace |
| Precision | > 90% | True positive rate for executed tokens |
| Recall | > 95% | Coverage of actually executed tokens |

---

## 7. Dependencies

### 7.1 Python Packages
```
transformers>=4.35.0
datasets>=2.14.0
torch>=2.0.0
scikit-learn>=1.3.0
pyyaml>=6.0
matplotlib>=3.7.0
```

### 7.2 External References
- Python trace module: https://docs.python.org/3/library/trace.html
- sys.settrace: https://docs.python.org/3/library/sys.html#sys.settrace
- Coverage.py: https://github.com/nedbat/coveragepy (reference implementation)
- StepCoder (ACL 2024): https://aclanthology.org/2024.acl-long.251/

---

## 8. Non-Functional Requirements

### NFR-1: Performance
- Trace collection completes within 20× baseline time
- Memory overhead < 2× baseline

### NFR-2: Reliability
- Handle all Python exception types gracefully
- Provide partial traces for code that crashes

### NFR-3: Reproducibility
- Fixed random seed: 42
- Deterministic trace collection
- Results reproducible across runs

---

## 9. Success Criteria (Gate Conditions)

**MUST_WORK Gate:**
- Token classification accuracy > 95%
- Trace overhead < 20×

**Pass Action:** Proceed to H-M2 (token masking validation)
**Fail Action:** Explore alternative trace methods (AST-based, bytecode analysis)

---

## 10. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Multi-line statement mapping errors | Medium | Use AST for complex cases |
| Trace overhead too high | Medium | Consider ctrace (C implementation) |
| Edge cases in tokenizer mapping | Low | Comprehensive test suite |

---

*Document generated for Phase 3 Implementation Planning*
*Next: Architecture Design*
