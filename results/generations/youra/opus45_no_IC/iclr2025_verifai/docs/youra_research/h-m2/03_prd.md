# Product Requirements Document: H-M2 Static Analysis Feedback Loop

**Date:** 2026-08-12
**Author:** Anonymous
**Hypothesis:** H-M2 - Static analysis identifies semantic patterns (security, reliability) in syntactically valid code, reducing issues after feedback

---

## 1. Executive Summary

This PRD defines requirements for implementing and validating the H-M2 hypothesis: that static analysis tools (Bandit + Pylint) can identify semantic patterns in LLM-generated code and reduce security/reliability issues through an iterative feedback loop.

**Core Mechanism:** Generate code → Run Bandit+Pylint → Extract issues → Feed back to LLM → Regenerate → Iterate until convergence or max iterations.

**Success Criteria:** Measurable reduction in security and reliability issues after feedback loop compared to initial generation.

---

## 2. Problem Statement

LLM-generated code often passes syntax checks but contains semantic issues:
- Security vulnerabilities (CWE categories detected by Bandit)
- Reliability issues (Pylint warnings/errors)

H-M1 proved syntax filtering works (40% error reduction). H-M2 tests whether static analysis catches semantic errors orthogonal to syntax errors.

---

## 3. Functional Requirements

### FR-1: Dataset Loading
- **FR-1.1:** Load SecurityEval v2.2 dataset (121 prompts, 69 CWEs)
- **FR-1.2:** Source: HuggingFace `s2e-lab/SecurityEval`
- **FR-1.3:** Filter to Python-only prompts
- **FR-1.4:** Extract prompt text and CWE category

### FR-2: Baseline Code Generation
- **FR-2.1:** Use CodeLlama-7B-Instruct model (same as H-M1 for continuity)
- **FR-2.2:** Generate code WITHOUT static analysis feedback
- **FR-2.3:** Temperature: 0.2, Max tokens: 512
- **FR-2.4:** Record initial security/reliability issue counts

### FR-3: Static Analysis Integration
- **FR-3.1:** Run Bandit for security analysis (JSON output)
- **FR-3.2:** Run Pylint for reliability analysis (JSON output)
- **FR-3.3:** Count issues by category (security vs reliability)
- **FR-3.4:** Format issues as structured feedback for LLM

### FR-4: Feedback Loop Implementation
- **FR-4.1:** Maximum iterations: 5 (PoC) or 10 (full)
- **FR-4.2:** Early termination: no issues remaining
- **FR-4.3:** Track iteration count to convergence
- **FR-4.4:** Preserve code functionality during refinement

### FR-5: Proposed Model (Feedback-Enhanced)
- **FR-5.1:** Same base model (CodeLlama-7B-Instruct)
- **FR-5.2:** Inject Bandit+Pylint feedback into prompt
- **FR-5.3:** Generate refined code based on feedback
- **FR-5.4:** Record final security/reliability issue counts

### FR-6: Evaluation Pipeline
- **FR-6.1:** Primary metric: `security_issue_reduction = (initial - final) / initial`
- **FR-6.2:** Primary metric: `reliability_issue_reduction = (initial - final) / initial`
- **FR-6.3:** Secondary: iterations to convergence
- **FR-6.4:** Statistical significance testing across full dataset

### FR-7: Visualization
- **FR-7.1:** Gate metrics comparison (bar chart: initial vs final)
- **FR-7.2:** Issue reduction over iterations (line plot)
- **FR-7.3:** CWE category distribution (bar chart)

---

## 4. Data Specification

### 4.1 Primary Dataset

| Property | Value |
|----------|-------|
| Name | SecurityEval v2.2 |
| Source | `s2e-lab/SecurityEval` (HuggingFace) |
| Size | 121 prompts |
| Coverage | 69 CWEs |
| Format | JSONL with ID, prompt, CWE |

**Loading:**
```python
from datasets import load_dataset
dataset = load_dataset("s2e-lab/SecurityEval")
```

### 4.2 Static Baselines

None required - this hypothesis measures improvement through feedback loop.

### 4.3 Preprocessing

1. Load from HuggingFace datasets
2. Filter to Python-only prompts
3. Extract prompt text and expected CWE category

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- Feedback loop should complete within 60 seconds per prompt (5 iterations)
- Full dataset evaluation: < 2 hours

### NFR-2: Reproducibility
- Fixed random seed for generation
- Deterministic temperature (0.2)
- Logged iteration history

### NFR-3: Extensibility
- Modular static analyzer interface (swap Bandit/Pylint for others)
- Configurable iteration limits

---

## 6. Success Criteria

### Gate Condition (SHOULD_WORK)
- `final_security_issues < initial_security_issues` (any measurable reduction)
- `final_reliability_issues < initial_reliability_issues` (any measurable reduction)

### Full Validation Targets (Reference: Blyth et al. 2025)
- Security issues: 40% → 13% (67% reduction)
- Reliability issues: 50% → 11% (78% reduction)

### PoC Pass Condition
1. Code runs without error
2. `final_security_issues < initial_security_issues`
3. `final_reliability_issues < initial_reliability_issues`

---

## 7. Dependencies

### 7.1 Python Packages
- `transformers` - CodeLlama model loading
- `datasets` - HuggingFace dataset loading
- `bandit` - Security analysis
- `pylint` - Reliability analysis
- `torch` - Model inference
- `matplotlib` - Visualization
- `pyyaml` - Config handling

### 7.2 External Repositories (Reference)
- `cyb3rlab/CodeEnhancer` - Two-stage validation loop reference
- `Kamel773/LLM-code-refine` - FDSP approach reference
- `s2e-lab/SecurityEval` - Dataset source

### 7.3 Hardware
- GPU: 1x A100 40GB (CodeLlama-7B inference)
- Storage: 10GB (model weights)

---

## 8. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Bandit/Pylint slow on large code | Timeout per analysis (30s max) |
| Feedback causes functionality loss | Track functional correctness (unit tests if available) |
| Low initial issue rate | Dataset designed for security vulnerabilities |

---

## 9. Appendix: Reference Implementations

### Blyth et al. 2025 - "Static Analysis as a Feedback Loop"
- Results: Security 40%→13%, Reliability 50%→11% in 10 iterations
- Key insight: Inject issue descriptions at specific code lines

### cyb3rlab/CodeEnhancer
- Components: `code_validator.py` with Pylint+Bandit loop
- Iterations: 5 (configurable)

---

*Generated from Phase 2C Experiment Brief*
*Next Phase: Architecture Design*
