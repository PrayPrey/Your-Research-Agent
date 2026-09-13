# Product Requirements Document: H-E1

**Hypothesis:** EVAF mechanism can be implemented and produces filtered AI feedback with measurable accept rate between 20-60%
**Type:** EXISTENCE (PoC)
**Date:** 2026-08-18
**Author:** Anonymous

---

## 1. Executive Summary

This PRD defines requirements for implementing and validating the EVAF (Execution-Verified AI Feedback) mechanism. The goal is to prove the core concept works: AI-generated code fixes can be filtered through execution gating, achieving an accept rate between 20-60%.

**Success Criteria:** Accept rate of AI suggestions passing execution verification is 20-60%.

---

## 2. Problem Statement

Current AI code generation produces incorrect suggestions ~40-60% of the time. Without verification, training on these suggestions introduces noise. EVAF proposes execution-based gating: only AI suggestions that pass unit tests are accepted for training signal.

**Gate Condition:** Accept rate must be 20-60%
- <10%: EVAF degenerates (AI nearly always wrong)
- >90%: Gating unnecessary (AI nearly always correct)

---

## 3. Functional Requirements

### FR-1: Baseline Code Generation
- Load CodeT5-770M model from `Salesforce/codet5-large`
- Generate code solutions for HumanEval problems
- Expected baseline pass@1: ~15.5%

### FR-2: AI Feedback Generation
- Load CodeLlama-7b-Instruct for critique generation
- Given failing code + problem description, generate fix suggestions
- Temperature: 0.2, max_tokens: 512

### FR-3: Execution Gating Pipeline
- Extract code from AI response
- Run extracted code against unit tests (3.0s timeout per test)
- Accept if all tests pass, reject otherwise

### FR-4: Metrics Computation
- Compute accept rate: (accepted suggestions) / (total suggestions)
- Compute coverage: (problems with actionable suggestions) / (total failing problems)
- Track rejection reason distribution

### FR-5: Visualization
- Gate metrics bar chart with 20-60% target zone
- Accept rate distribution histogram
- Rejection reason breakdown pie chart

---

## 4. Data Specification

### 4.1 Primary Dataset

| Attribute | Value |
|-----------|-------|
| **Name** | HumanEval |
| **Source** | openai_humaneval (HuggingFace) |
| **Size** | 164 problems |
| **Split** | Full test set (all 164 problems) |
| **Auto-download** | Yes (via HuggingFace datasets) |

**Loading:**
```python
from datasets import load_dataset
dataset = load_dataset("openai_humaneval", split="test")
```

### 4.2 Preprocessing
1. Extract function signature, docstring, canonical solution
2. Generate baseline solutions using CodeT5-770M
3. Filter to problems where baseline fails (~80-120 problems expected)

---

## 5. Model Specification

### 5.1 Baseline Model: CodeT5-770M

| Attribute | Value |
|-----------|-------|
| **Model ID** | Salesforce/codet5-large |
| **Parameters** | 770M |
| **Architecture** | Encoder-Decoder Transformer |
| **HumanEval pass@1** | 15.5% (reference) |

### 5.2 AI Feedback Generator: CodeLlama-7b-Instruct

| Attribute | Value |
|-----------|-------|
| **Model ID** | codellama/CodeLlama-7b-Instruct-hf |
| **Parameters** | 7B |
| **Architecture** | Decoder-only Transformer |
| **Precision** | float16 |

---

## 6. Evaluation Specification

### 6.1 Primary Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| **Accept Rate** | accepted / total | 20-60% |
| **Coverage** | actionable / failing | >80% |

### 6.2 Gate Decision Rules

| Accept Rate | Decision |
|-------------|----------|
| 20-60% | PASS - Proceed to H-M1 |
| <10% | FAIL - EVAF not viable |
| >90% | FAIL - Gating unnecessary |

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
transformers>=4.30.0
datasets>=2.14.0
accelerate>=0.21.0
matplotlib>=3.7.0
pyyaml>=6.0
tqdm>=4.65.0
```

### 7.2 Hardware Requirements
- GPU: 1x A100 40GB (or 2x V100 32GB)
- For CodeLlama-7B: ~14GB VRAM in fp16

### 7.3 External References
- RLTF: https://github.com/Zyq-scut/RLTF
- bigcode-evaluation-harness: https://github.com/bigcode-project/bigcode-evaluation-harness

---

## 8. Non-Functional Requirements

### NFR-1: Performance
- Process full HumanEval (164 problems) in <4 hours
- Unit test timeout: 3.0 seconds per test

### NFR-2: Reproducibility
- Deterministic generation (temperature 0.2)
- Fixed random seed for consistency
- All results logged with timestamps

### NFR-3: Safety
- Sandboxed test execution (no network, no filesystem writes)
- Resource limits on spawned processes

---

## 9. Success Criteria Summary

| Criterion | Requirement | Priority |
|-----------|-------------|----------|
| Accept rate 20-60% | MUST | P0 |
| Coverage >80% | SHOULD | P1 |
| Full HumanEval run | MUST | P0 |
| Figures generated | MUST | P0 |

---

*Generated from Phase 2C Experiment Brief*
*Next: Architecture Design (03_architecture.md)*
