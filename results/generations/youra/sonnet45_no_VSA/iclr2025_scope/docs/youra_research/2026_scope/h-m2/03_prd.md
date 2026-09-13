# Product Requirements Document: Metamorphic Contract Validation System

---

## Document Metadata

**Project:** YouRA Research - Hypothesis h-m2
**Hypothesis:** Metamorphic contracts (softmax sums, dropout identity, mathematical properties) can detect behavioral violations without full inference
**Author:** Anonymous
**Date:** 2026-07-11
**Version:** 1.0
**Status:** Draft

---

## Executive Summary

### Purpose
Implement and validate a metamorphic contract validation system that detects mathematical invariant violations in deep learning APIs (softmax sums, dropout identity) using lightweight probe-based testing without requiring full model inference.

### Business Value
- **Research Impact:** Validates mechanism hypothesis (h-m2) - second step in causal chain for API contract-based ML reproducibility
- **Detection Capability:** Target ≥70% detection rate for metamorphic property violations
- **Performance:** Maintains execution time ≤10 seconds for lightweight validation
- **Foundation:** Builds on h-m1 structural contracts, extends to behavioral properties

### Success Criteria
- **Primary:** Metamorphic violation detection rate ≥70%
- **Secondary:** Execution time ≤10s, false positive rate <5%
- **Gate Type:** SHOULD_WORK (failure documented as limitation, workflow continues)

---

## Problem Statement

### Background
ML reengineering workflows face behavioral API violations that structural contracts (h-m1) cannot detect. Mathematical invariants (softmax normalization sums to 1.0, dropout identity in eval mode) are version-stable properties that can be validated via lightweight probes without full inference.

### Current State (Baseline)
- **No-Contract Baseline:** Standard PyTorch API usage with implicit trust in library behavior
- **Detection Rate:** 0% (no validation mechanism)
- **Real-World Examples:** PyTorch #90842 (softmax sum violations), #124464 (dropout eval mode bug)

### Desired State
Metamorphic contract validation system that:
1. Detects softmax sum violations (property: `sum(softmax(x, dim)) ≈ 1.0`)
2. Detects dropout identity violations (property: `dropout(x, eval_mode=True) = x`)
3. Uses lightweight probe inputs (<10s execution time)
4. Integrates with decorator pattern from h-m1

### Gap Analysis
**H-M1 (Structural)** → Validates shapes, dtypes, non-null outputs at import time  
**H-M2 (Metamorphic)** → Extends to mathematical properties without full inference  
**Gap:** Behavioral invariants require runtime probes, not static inspection

---

## Functional Requirements

### FR-1: Test Suite Generation (Programmatic API)
**Priority:** P0 (Must Have)  
**Description:** Generate controlled test cases for metamorphic property validation

**Requirements:**
- FR-1.1: Generate 3 test scenarios minimum (1 control + 2 defect types)
- FR-1.2: Programmatic generation via PyTorch API (not synthetic simulation)
- FR-1.3: Test cases include:
  - Control: Valid operations where properties hold
  - Defect Type 1: Softmax sum violation (perturbed output where sum ≠ 1.0)
  - Defect Type 2: Dropout identity violation (dropout applied in eval mode)
- FR-1.4: 10-20 samples per scenario (~50 total metamorphic property checks)

**Acceptance Criteria:**
- All 3 scenarios executable via pytest/unittest
- Deterministic test cases with known ground truth
- Test suite completes in <10s total execution time

**Source:** Phase 2C Section "Dataset" (Test Suite Design)

---

### FR-2: Baseline Model (No-Contract)
**Priority:** P0 (Must Have)  
**Description:** Implement reference baseline without metamorphic validation

**Requirements:**
- FR-2.1: Plain PyTorch operations (softmax, dropout) without contract decoration
- FR-2.2: No metamorphic property checking
- FR-2.3: Represents current practice: implicit trust in API behavior
- FR-2.4: Expected detection rate: 0% (no validation mechanism)

**Acceptance Criteria:**
- Baseline implementation runs all test cases
- Zero overhead (no validation logic)
- Undetected violations: 0/N for both softmax and dropout defects

**Source:** Phase 2C Section "Baseline Model"

---

### FR-3: Proposed Model (Metamorphic Contracts)
**Priority:** P0 (Must Have)  
**Description:** Implement metamorphic property validation using decorator pattern

**Requirements:**
- FR-3.1: **Softmax Sum Validation**
  - Property: `sum(softmax(x, dim)) ≈ 1.0`
  - Method: `validate_softmax(func, probe_input, dim=-1, rtol=1e-5, atol=1e-7)`
  - Returns: Boolean (property holds or violated)
  
- FR-3.2: **Dropout Identity Validation**
  - Property: `dropout(x, eval_mode=True) = x` (identity function)
  - Method: `validate_dropout_identity(module, probe_input, eval_mode=True)`
  - Returns: Boolean (property holds or violated)

- FR-3.3: **Integration Pattern**
  - Decorator-based application (follows h-m1 pattern)
  - Lightweight probe inputs (small tensors: 4x10 for softmax, 100-element for dropout)
  - Numerical tolerance handling (rtol=1e-5, atol=1e-7)

**Acceptance Criteria:**
- Softmax validation detects sum violations within numerical tolerance
- Dropout validation detects identity violations in eval mode
- Execution overhead <30ms per test case (within 10s budget)
- Integration via `@validate_metamorphic` decorator

**Source:** Phase 2C Section "Proposed Model - Core Mechanism Implementation"

---

### FR-4: Evaluation Metrics
**Priority:** P0 (Must Have)  
**Description:** Implement detection rate calculation and secondary metrics

**Requirements:**
- FR-4.1: **Primary Metric: Metamorphic Violation Detection Rate**
  - Formula: `(detected_violations / total_violations) × 100%`
  - Breakdown: Softmax detection rate, Dropout detection rate
  - Combined: `(N_softmax + N_dropout) / (total_softmax + total_dropout)`
  
- FR-4.2: **Secondary Metrics**
  - Execution Time: Total time for all metamorphic property checks (must be ≤10s)
  - False Positive Rate: Control tests failing incorrectly (should be 0%)

- FR-4.3: **Success Criteria Validation**
  - Primary: Detection rate ≥70% for metamorphic violations
  - Secondary: Execution time ≤10s, False positive rate <5%

**Acceptance Criteria:**
- Metrics logged to console and saved to results file
- Detection rate calculated separately for softmax vs dropout
- Gate evaluation logic (SHOULD_WORK: ≥70% passes, <50% documented as limitation)

**Source:** Phase 2C Section "Evaluation"

---

### FR-5: Visualization
**Priority:** P1 (Should Have)  
**Description:** Generate figures for metamorphic testing analysis

**Requirements:**
- FR-5.1: **Gate Metrics Comparison** (Mandatory)
  - Bar chart: Target vs actual metrics
  - Metrics: Detection rate, execution time, false positive rate

- FR-5.2: **Detection Rate Breakdown**
  - Stacked bar chart showing detection by violation type (softmax, dropout)

- FR-5.3: **Execution Time Comparison**
  - Baseline vs contract-validated execution time

- FR-5.4: **Violation Severity Distribution**
  - Histogram of numerical deviation magnitudes (e.g., |sum - 1.0| for softmax)

**Acceptance Criteria:**
- All figures saved to `{hypothesis_folder}/figures/`
- Matplotlib-generated PNG files with 300 DPI
- Figure generation code integrated in experiment script

**Source:** Phase 2C Section "Visualization Requirements"

---

## Non-Functional Requirements

### NFR-1: Performance
- **Execution Time:** Total test suite execution ≤10 seconds
- **Per-Test Overhead:** <30ms per metamorphic property check
- **Probe Size:** Small tensors only (4x10 for softmax, 100-element for dropout)

### NFR-2: Reliability
- **Determinism:** Reproducible test results with fixed seeds
- **Numerical Stability:** Tolerance-based validation (rtol=1e-5, atol=1e-7)
- **False Positive Rate:** <5% on control tests

### NFR-3: Code Quality
- **Testing:** pytest-based test suite
- **Documentation:** Docstrings for all validation methods
- **Pattern Consistency:** Follows h-m1 decorator pattern

### NFR-4: Research Validity
- **PoC Focus:** Mechanism validation, not statistical rigor
- **Ground Truth:** Known defect injection for controlled validation
- **Gate Compliance:** SHOULD_WORK gate (≥70% passes, <50% limitation noted)

---

## Technical Constraints

### TC-1: Dependencies
- **PyTorch:** Latest stable version (for API compatibility)
- **Python:** 3.8+
- **Testing:** pytest framework
- **Visualization:** matplotlib

### TC-2: Data Constraints
- **Dataset Type:** Programmatic API (generated, not file-based)
- **Test Cases:** ~50 total (deterministic, no randomness)
- **No External Data:** All test inputs generated in-code

### TC-3: Implementation Constraints
- **Pattern Reuse:** Decorator pattern from h-m1
- **No Training:** Validation experiment only (no model training)
- **Probe-Based:** Lightweight inputs, no full inference

---

## Dependencies and Prerequisites

### Internal Dependencies
- **H-M1 (Structural Contracts):** COMPLETED with PASS
  - Validation: Detection rate 100%, execution time <0.03s
  - Reuse: Decorator pattern, probe-based testing approach

### External Dependencies
- **PyTorch Test Patterns:**
  - test/nn/test_dropout.py (dropout identity validation)
  - test/utils/test_softmax.py (softmax sum validation)
- **Research Implementations:**
  - ModelMeta (anonymous-tai/ModelMeta) - Metamorphic testing framework
  - TENSURE (wjddusrb03/tensure) - Algebraic property validation

### Prerequisite Validation
- Phase 2C experiment brief completed (02c_experiment_brief.md)
- H-M1 validation report available (04_validation.md)

---

## Success Metrics

### Primary Success Criteria
| Metric | Target | Measured By |
|--------|--------|-------------|
| Metamorphic Violation Detection Rate | ≥70% | `(detected / total_violations) × 100%` |
| Softmax Sum Detection | ≥70% | Softmax-specific test cases |
| Dropout Identity Detection | ≥70% | Dropout-specific test cases |

### Secondary Success Criteria
| Metric | Target | Measured By |
|--------|--------|-------------|
| Execution Time | ≤10s | Total test suite runtime |
| False Positive Rate | <5% | Control test failures / total controls |
| Code Execution | Pass | Test suite runs without errors |

### Gate Evaluation
**SHOULD_WORK Gate:**
- **Pass:** Detection rate ≥70%
- **Documented Limitation:** Detection rate <50%
- **Consequence:** Failure allows workflow continuation with limitation noted

---

## Out of Scope

### Explicitly Excluded
- ❌ Statistical validation across multiple runs (deferred to Phase 5)
- ❌ Real Jiang et al. defect corpus integration (Phase 5)
- ❌ Model training or fine-tuning (validation experiment only)
- ❌ Version stability testing across PyTorch releases (Phase 5)
- ❌ Production deployment or packaging

### Future Phases
- **Phase 5:** Full statistical validation with real defect corpus
- **Phase 5:** Version stability testing (±2 PyTorch releases)
- **Phase 6:** Paper writing with complete experimental results

---

## Risks and Mitigations

### Risk 1: Numerical Tolerance Issues
**Probability:** Medium | **Impact:** Medium  
**Description:** Floating-point precision may cause false positives/negatives  
**Mitigation:** Use tolerance-based validation (rtol=1e-5, atol=1e-7) following PyTorch test patterns

### Risk 2: Probe Representativeness
**Probability:** Low | **Impact:** Medium  
**Description:** Small probe inputs may not represent real-world violations  
**Mitigation:** PoC validation only - Phase 5 will test on real defect corpus

### Risk 3: Detection Rate Below Threshold
**Probability:** Medium | **Impact:** Low (SHOULD_WORK gate)  
**Description:** Detection rate <70% fails primary criterion  
**Mitigation:** SHOULD_WORK gate allows graceful degradation; document as limitation

---

## Appendix

### A. Reference Implementations

**Primary Sources:**
1. **ModelMeta** (anonymous-tai/ModelMeta) - ACM SIGMETRICS 2024
   - 4 structural metamorphic relations for DL framework testing
   - 31 bugs found in PyTorch/MindSpore/ONNX

2. **TENSURE** (wjddusrb03/tensure) - NDSS Fuzzing Workshop 2026
   - Constraint-based metamorphic testing
   - Algebraic properties (operand permutation, format equivalence)

3. **PyTorch Test Suite**
   - test/nn/test_dropout.py - Dropout identity validation patterns
   - test/utils/test_softmax.py - Softmax sum validation patterns

### B. Research Context

**H-M1 Results (Prerequisite):**
- Detection Rate: 100% (2/2 structural defects)
- Execution Time: <0.03s
- Pattern: Decorator-based contracts with probe validation

**Phase 2C Experiment Design:**
- File: docs/youra_research/h-m2/02c_experiment_brief.md
- Specification Level: 1.5 (Concrete + Pseudo-code)
- Research Sources: 5 Archon queries, 7 GitHub repositories

### C. Traceability Matrix

| Requirement | Source | Priority |
|-------------|--------|----------|
| FR-1: Test Suite | Phase 2C "Dataset" | P0 |
| FR-2: Baseline Model | Phase 2C "Baseline Model" | P0 |
| FR-3: Metamorphic Contracts | Phase 2C "Proposed Model" | P0 |
| FR-4: Evaluation Metrics | Phase 2C "Evaluation" | P0 |
| FR-5: Visualization | Phase 2C "Visualization Requirements" | P1 |

---

**Document Status:** Ready for Architecture Design (Step 3)  
**Next Phase:** Implementation Planning - Architecture Agent
