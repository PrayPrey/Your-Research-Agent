# Product Requirements Document: H-M1

**Hypothesis:** Grammar-constrained decoding reduces compilation errors by >50% compared to baseline through prefix automata enforcement

**Date:** 2026-08-12
**Author:** Anonymous
**Version:** 1.0

---

## 1. Executive Summary

This PRD specifies the implementation requirements for validating hypothesis H-M1, which tests whether grammar-constrained decoding using SynCode can reduce Python compilation errors in LLM-generated code by more than 50% compared to unconstrained generation.

**Key Deliverables:**
- Baseline code generator using CodeLlama-7B with standard decoding
- Grammar-constrained generator using SynCode with Python CFG enforcement
- Evaluation pipeline comparing compilation error rates
- Statistical analysis and visualization

---

## 2. Problem Statement

LLM-generated code frequently contains syntax errors that prevent compilation. Grammar-constrained decoding enforces syntactic validity during generation by restricting token predictions to those allowed by a context-free grammar.

**Research Question:** Does SynCode's DFA-based grammar constraint mechanism reduce compilation errors by >50%?

**Success Criteria:** `constrained_error_rate < baseline_error_rate` (directional for PoC)

---

## 3. Functional Requirements

### FR-1: Baseline Code Generator
- Load CodeLlama-7B from HuggingFace
- Generate n=10 samples per HumanEval problem
- Use temperature=0.2, max_tokens=512
- Standard autoregressive decoding (no constraints)

### FR-2: Grammar-Constrained Generator
- Initialize SynCode with CodeLlama-7B
- Use mode='grammar_strict' with Python grammar
- Generate n=10 samples per HumanEval problem
- Same temperature and sampling parameters as baseline

### FR-3: Dataset Loading
- Load HumanEval from `openai/openai_humaneval`
- Extract prompts (function signature + docstring)
- 164 problems total (test split only)

### FR-4: Compilation Error Evaluation
- Check syntax validity using `ast.parse()`
- Calculate error rate per condition
- Compare baseline vs constrained rates

### FR-5: Visualization
- Bar chart comparing error rates
- Statistical summary table

---

## 4. Data Specification

### 4.1 Primary Dataset

| Field | Value |
|-------|-------|
| Name | HumanEval |
| Source | openai/openai_humaneval |
| Size | 164 problems |
| Split | test only |
| Format | Function signature + docstring + unit tests |
| Auto-download | Yes (HuggingFace datasets) |

**Loading Code:**
```python
from datasets import load_dataset
dataset = load_dataset("openai/openai_humaneval", split="test")
```

### 4.2 Generated Samples

| Condition | Samples/Problem | Total Samples |
|-----------|-----------------|---------------|
| Baseline | 10 | 1,640 |
| Constrained | 10 | 1,640 |
| **Total** | 20 | **3,280** |

---

## 5. Model Specification

### 5.1 Baseline Model

| Field | Value |
|-------|-------|
| Architecture | CodeLlama-7B |
| Parameters | 7B |
| Source | meta-llama/CodeLlama-7b-hf |
| Dtype | bfloat16 |
| Device | CUDA (auto) |

### 5.2 Proposed Model

| Field | Value |
|-------|-------|
| Base | CodeLlama-7B |
| Constraint | SynCode grammar_strict mode |
| Grammar | Python CFG |
| Library | syncode |

---

## 6. Evaluation Metrics

### 6.1 Primary Metric

| Metric | Formula | Target |
|--------|---------|--------|
| Compilation Error Rate | errors / total_samples | Lower is better |

### 6.2 Gate Condition

```
PASS if: constrained_error_rate < baseline_error_rate
```

---

## 7. Dependencies

### 7.1 Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| torch | >=2.0 | Deep learning framework |
| transformers | >=4.35 | Model loading |
| syncode | latest | Grammar-constrained decoding |
| datasets | >=2.14 | HumanEval loading |
| matplotlib | >=3.7 | Visualization |
| pyyaml | >=6.0 | Config management |

### 7.2 Hardware Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| GPU VRAM | 16GB | 24GB |
| RAM | 32GB | 64GB |
| Storage | 50GB | 100GB |

---

## 8. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seed (seed=1)
- Deterministic generation where possible
- All hyperparameters documented

### NFR-2: Performance
- Generation should complete within 4 hours
- Memory-efficient model loading (quantization optional)

### NFR-3: Logging
- Log generation progress
- Save intermediate results
- Error handling with informative messages

---

## 9. Success Criteria

| Criterion | Threshold | Priority |
|-----------|-----------|----------|
| Code runs without error | 100% | MUST |
| constrained_error_rate < baseline_error_rate | directional | MUST |
| Figures generated | 1+ | SHOULD |
| Results reproducible | seed=1 | SHOULD |

---

## 10. Out of Scope

- Pass@k functional correctness (future work)
- Multiple model sizes (only 7B)
- Other languages (only Python)
- Training/fine-tuning (inference only)

---

*Generated for Phase 3 Implementation Planning*
*Source: 02c_experiment_brief.md*
