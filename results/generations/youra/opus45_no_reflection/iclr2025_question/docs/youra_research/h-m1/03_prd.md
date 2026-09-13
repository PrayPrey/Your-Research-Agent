# Product Requirements Document: H-M1

**Hypothesis:** Forward pass with hooks extracts hidden states without affecting generation
**Date:** 2026-08-18
**Author:** Anonymous
**Type:** MECHANISM (MUST_WORK Gate)

---

## 1. Executive Summary

This PRD specifies the implementation requirements for validating that PyTorch forward hooks can extract hidden states from Llama-3-8B-Instruct without altering the model's generation output. This is a MECHANISM hypothesis verifying the non-intrusiveness of the hook-based extraction approach established in H-E1.

**Success Criteria:** 100% output identity between hooked and non-hooked generation, with <10% inference overhead.

---

## 2. Problem Statement

### 2.1 Context
H-E1 validated that hidden states encode correctness signal (AUROC=0.8854). H-M1 must now verify that the extraction mechanism itself does not introduce artifacts or alterations to model behavior.

### 2.2 Core Problem
Forward hooks may theoretically modify outputs if implemented incorrectly. We need empirical verification that:
1. Hook attachment does not change model outputs
2. Hook execution does not significantly impact inference time
3. Hook cleanup properly releases resources

---

## 3. Functional Requirements

### FR-1: HiddenStateExtractor Implementation
- Implement context-managed hook attachment/detachment
- Support selective layer extraction (single or multiple layers)
- Return None from hooks (non-intrusive read pattern)
- Use `.detach().cpu()` for memory-safe tensor copying

### FR-2: Baseline Generation Pipeline
- Generate outputs from 1000 TriviaQA validation samples WITHOUT hooks
- Use greedy decoding (deterministic comparison)
- Max 128 new tokens per sample
- Store outputs for comparison

### FR-3: Hooked Generation Pipeline
- Generate outputs from same 1000 samples WITH hooks attached
- Extract hidden states at layer 19 (60% depth, same as H-E1)
- Identical decoding parameters to baseline

### FR-4: Identity Verification
- Byte-by-byte comparison of all 1000 output pairs
- Calculate identity rate (must be 100%)
- Log any mismatches with sample indices

### FR-5: Performance Measurement
- Measure total inference time with and without hooks
- Calculate overhead percentage
- Target: <10% overhead

### FR-6: Memory Profiling (Optional)
- Track peak GPU memory with hooks
- Verify CPU memory usage for stored tensors

---

## 4. Data Specification

### 4.1 Primary Dataset
- **Name:** TriviaQA (validation subset)
- **Source:** HuggingFace `trivia_qa` (rc configuration)
- **Size:** 1000 samples (subset of H-E1's 17K validation)
- **Split:** `validation[:1000]`
- **Auto-download:** Yes (HuggingFace datasets)

### 4.2 Loading Code
```python
from datasets import load_dataset
dataset = load_dataset("trivia_qa", "rc", split="validation[:1000]")
```

---

## 5. Model Specification

### 5.1 Target Model
- **Name:** Llama-3-8B-Instruct
- **Source:** `meta-llama/Meta-Llama-3-8B-Instruct`
- **Architecture:** 32 transformer layers, 4096 hidden dim
- **Loading:** float16, auto device_map

### 5.2 Loading Code
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3-8B-Instruct",
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")
```

---

## 6. Success Metrics

### 6.1 Primary Metric (GATE)
- **Output Identity Rate:** 100.0%
- **Gate Type:** MUST_WORK
- **Fail Action:** PIVOT to alternative extraction methods

### 6.2 Secondary Metrics
- **Inference Overhead:** <10%
- **Memory Overhead:** <20% GPU peak

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=2.0.0
transformers>=4.35.0
datasets>=2.14.0
accelerate>=0.24.0
```

### 7.2 Hardware Requirements
- GPU with 24GB+ VRAM (A100 or equivalent)
- CUDA 11.8+

### 7.3 External References
- PyTorch register_forward_hook documentation
- HuggingFace transformers output_capturing.py
- TransformerLens hook system (reference pattern)

---

## 8. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed (42) for all operations
- Greedy decoding (no sampling)
- Deterministic outputs

### NFR-2: Code Quality
- Type hints on all public APIs
- Docstrings with parameter descriptions
- pytest-compatible test structure

### NFR-3: Resource Management
- Proper hook cleanup in context manager `__exit__`
- No memory leaks after context exit
- GPU memory released after tensor detachment

---

## 9. Visualization Requirements

### Required Figures
1. **Gate Metrics Bar Chart:** Identity rate (100% target) + Overhead (<10% target)
2. **Inference Time Histogram:** Distribution comparison with/without hooks
3. **Memory Profile:** GPU/CPU usage over generation steps

---

## 10. Constraints

### 10.1 Scope Constraints
- Test single layer (19) initially
- 1000 samples sufficient for identity verification
- No training involved (verification only)

### 10.2 Technical Constraints
- Must use PyTorch forward hooks (not backward)
- Must return None from hook (no output modification)
- Must detach tensors before storage

---

*Generated from Phase 2C Experiment Brief: 02c_experiment_brief.md*
