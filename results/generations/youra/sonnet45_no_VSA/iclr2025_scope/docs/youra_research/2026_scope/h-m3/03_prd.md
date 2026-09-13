# Product Requirements Document (PRD): H-M3

**Date:** 2026-07-11
**Hypothesis ID:** h-m3
**Hypothesis Statement:** Composition-level contracts validate binding assumptions across library interactions (device placement, tensor layout consistency)
**Document Type:** Product Requirements Document (PRD)
**Phase:** Phase 3 Implementation Planning

---

## 1. Executive Summary

### 1.1 Purpose
Implement a composition-level contract validation framework that detects cross-library interaction defects (device placement, dtype mismatches, tensor layout inconsistencies) at import/setup time before execution.

### 1.2 Success Criteria
- Detection rate ≥60% for composition-level defects (SHOULD_WORK gate)
- Execution time ≤10s per test case
- False positive rate <5%
- Supports PyTorch + CUDA + Transformers library triads

### 1.3 Scope
**In Scope:**
- Composition-level contract validator (decorator-based)
- Device consistency validation across library boundaries
- Dtype consistency validation
- Tensor layout validation (strided vs sparse)
- Test suite with 10-20 real defect cases
- Evaluation metrics and visualization

**Out of Scope:**
- Runtime-only validation (must be import/setup time)
- Full distributed tensor validation (DTensor complexity)
- Training loop integration

---

## 2. Problem Statement

### 2.1 Core Problem
88% of environment defects are interface defects, 46% are API defects (Jiang et al., 2023). Many arise from cross-library interactions (PyTorch + CUDA + Transformers version triads). Current CI-only baselines do not systematically validate composition-level invariants.

### 2.2 User Impact
ML engineers spend significant time debugging cryptic device mismatch errors that occur at runtime. Early detection at environment-stage would prevent downstream failures.

### 2.3 Gap Analysis
**Current State:** Defects detected at runtime (if at all)
**Desired State:** Composition-level defects detected at import/setup time
**Gap:** No systematic validation framework for cross-library contracts

---

## 3. Stakeholders & Users

### 3.1 Primary Users
- ML Research Engineers (conducting hypothesis validation experiments)
- Phase 4 Coder Agent (consumes this PoC code)

### 3.2 Success Metrics
- Detection rate (primary): ≥60%
- Execution overhead: ≤10s
- False positive rate: <5%

---

## 4. Data Specification

### 4.1 Defect Test Suite (Primary Dataset)
**Name:** Cross-Library Defect Test Suite
**Type:** `custom` (manually curated from real PyTorch/HuggingFace issues)
**Size:** 10-20 test cases
**Categories:**
1. Device mismatch (CUDA vs CPU): 5 cases
2. Dtype mismatch (float32 vs float16): 3 cases
3. Layout mismatch (strided vs sparse): 2 cases
4. Cross-library composition: 5 cases

**Test Case Sources:**
- PyTorch Issue #166117: scaled_dot_product_attention device mismatch
- PyTorch Issue #168010: conv2d device mismatch
- PyTorch Issue #159133: torch.compile cross-device error
- HuggingFace Diffusers PR #3313: generator device mismatch

**Loading Method:** Programmatic generation from documented error patterns (no download required)

### 4.2 Control Dataset
**Purpose:** Validate false positive rate
**Size:** 5-10 valid test cases
**Content:** Correct cross-library code that should NOT trigger violations

---

## 5. Functional Requirements

### FR-1: Composition Contract Decorator
**Priority:** P0 (CRITICAL)
**Description:** Implement `@validate_composition()` decorator that validates device/dtype/layout consistency at function boundaries
**Inputs:** Function arguments (tensors)
**Outputs:** Structured error if violations detected, else pass-through
**Success Criteria:**
- Decorator detects device mismatches (e.g., tensor on CUDA, mask on CPU)
- Decorator detects dtype mismatches (e.g., float32 vs float16)
- Validation runs at import/setup time (not runtime)
- Execution overhead <30ms per validation

### FR-2: Device Consistency Validation
**Priority:** P0 (CRITICAL)
**Description:** Validate all tensors are on the same device
**Algorithm:** Extract device from each tensor, ensure all match expected device
**Validation Approach:** Based on tensorguard pattern (see Phase 2C research)
**Success Criteria:**
- Detects cross-device errors (CUDA vs CPU)
- Handles torch.device specification correctly
- Provides actionable error messages

### FR-3: Dtype Consistency Validation
**Priority:** P0 (CRITICAL)
**Description:** Validate tensor dtypes match expected types
**Algorithm:** Check tensor.dtype against spec, raise structured error if mismatch
**Success Criteria:**
- Detects dtype mismatches (float32 vs float16)
- Handles mixed precision scenarios (autocast boundaries)
- Returns clear mismatch details

### FR-4: Layout Consistency Validation
**Priority:** P1 (HIGH)
**Description:** Validate tensor layout (strided vs sparse) compatibility
**Algorithm:** Check tensor.layout property
**Success Criteria:**
- Detects strided/sparse incompatibility
- Minimal performance overhead

### FR-5: Test Suite Execution
**Priority:** P0 (CRITICAL)
**Description:** Execute defect test suite and measure detection metrics
**Test Cases:** 10-20 composition-level defect cases + 5-10 control cases
**Outputs:** Detection rate, execution time, false positive rate
**Success Criteria:**
- All test cases execute successfully
- Detection rate calculated correctly
- Execution time measured per test

### FR-6: Baseline Comparison
**Priority:** P0 (CRITICAL)
**Description:** Compare proposed mechanism against no-contract baseline
**Baseline:** Execute tests WITHOUT contract validation (defects go undetected)
**Comparison Metrics:** Detection rate (baseline ~0%, proposed ≥60%)
**Success Criteria:**
- Baseline detection rate documented
- Proposed detection rate ≥60%
- Clear comparison in results

### FR-7: Evaluation Metrics Calculation
**Priority:** P0 (CRITICAL)
**Description:** Compute detection rate, execution overhead, false positive rate
**Formulas:**
- Detection rate = (defects detected / total defects) × 100%
- Avg execution time = sum(exec_time) / test_count
- False positive rate = (false positives / control tests) × 100%
**Success Criteria:**
- All metrics calculated correctly
- Results saved to validation report

### FR-8: Visualization Generation
**Priority:** P1 (HIGH)
**Description:** Generate required figures for validation report
**Mandatory Figure:** Detection rate bar chart (baseline vs proposed) with 60% threshold line
**Optional Figures:**
- Defect category breakdown (stacked bar chart)
- Execution time distribution (histogram)
- False positive analysis (bar chart)
**Output Path:** `{hypothesis_folder}/figures/`
**Success Criteria:**
- At least 1 mandatory figure generated
- Figures saved as PNG/SVG
- Clear labels and legends

---

## 6. Non-Functional Requirements

### NFR-1: Performance
- Validation overhead: <30ms per test case
- Total test suite execution: ≤10s (hard requirement from hypothesis)

### NFR-2: Compatibility
- PyTorch ≥1.12.0
- Python ≥3.8
- CUDA optional (CPU fallback supported)

### NFR-3: Code Quality
- Type hints for all functions
- Docstrings for public APIs
- Clear error messages with actionable guidance

### NFR-4: Testability
- Each validator function independently testable
- Clear separation: validator logic vs test harness

---

## 7. Dependencies & Prerequisites

### 7.1 Python Packages
**Core:**
- `torch>=1.12.0` (PyTorch framework)
- `numpy>=1.21.0` (numerical operations)

**Testing:**
- `pytest>=7.0.0` (test framework)
- `matplotlib>=3.5.0` (visualization)

**Optional:**
- `transformers>=4.20.0` (for cross-library tests)

### 7.2 External References
**Implementation Patterns (from Phase 2C research):**
1. PyTorch DTensor validation framework (pattern extraction only, not full replication)
2. tensorguard (decorator API pattern)
3. gpucheck (parametric testing pattern)

**No external repositories required** - patterns adapted to PoC implementation.

### 7.3 Prerequisites from Hypothesis h-m1
**Status:** VALIDATED ✓ (100% detection rate)
**Reusable Components:**
- `@validate_at_import` decorator pattern
- Import-time validation trigger via `__init__`
- Custom exception hierarchy (ShapeViolation, DeviceViolation, DtypeViolation)
- Probe-based validation (1-sample batch)

**Adaptation for h-m3:**
- Extend from single-tensor structural checks → multi-tensor composition checks
- Add device/dtype cross-parameter validation
- Support library boundary scenarios

---

## 8. Success Criteria (Detailed)

### 8.1 Gate Criteria (SHOULD_WORK)
| Metric | Threshold | Priority |
|--------|-----------|----------|
| Detection Rate | ≥60% | MUST |
| Execution Time | ≤10s total | MUST |
| False Positive Rate | <5% | SHOULD |

### 8.2 Pass Condition
- Detection rate ≥60% AND execution time ≤10s → **PASS**
- Detection rate 40-59% → **PARTIAL** (document limitation)
- Detection rate <40% → **FAIL** (mechanism insufficient)

### 8.3 Deliverables
1. `code/composition_validator.py` - Core validation framework
2. `code/test_cases.py` - Defect test suite
3. `code/run_experiment.py` - Test harness
4. `code/evaluate.py` - Metrics calculation
5. `04_validation.md` - Validation report with results
6. `figures/*.png` - Visualization outputs

---

## 9. Out of Scope (Explicit)

**NOT Implementing:**
- Full DTensor distributed validation (too complex for PoC)
- Production-ready zero-overhead mode (environment variable bypass)
- Automatic contract generation from type hints
- Runtime-only validation (contradicts import-time hypothesis)
- Integration with existing CI/CD pipelines
- Multi-GPU placement validation

---

## 10. Risks & Mitigation

### Risk 1: Network constraints prevent dataset download
**Likelihood:** Low (using programmatic test generation, not downloads)
**Impact:** Low (can use synthetic data)
**Mitigation:** Generate test cases from documented error patterns

### Risk 2: Detection rate <60% (gate failure)
**Likelihood:** Medium (composition-level validation is harder than structural)
**Impact:** High (hypothesis fails SHOULD_WORK gate)
**Mitigation:** Focus on highest-impact defect categories (device mismatch first)

### Risk 3: Execution overhead >10s
**Likelihood:** Low (validation is lightweight)
**Impact:** High (violates PoC constraint)
**Mitigation:** Profile validation overhead, optimize hot paths

---

## 11. Timeline & Phases

**Phase 3 (Current):** Implementation Planning - Complete
**Phase 4 (Next):** Coding & Validation
- Task A-0: Environment setup (install dependencies)
- Tasks A-1 to A-6: Epic implementation tasks
- Subtasks: API implementation, test case generation
- Duration: ~1-2 hours (PoC scale)

---

## 12. Appendix

### 12.1 Reference Documents
- Phase 2C Experiment Brief: `02c_experiment_brief.md`
- Prerequisite Hypothesis: h-m1 (`docs/youra_research/h-m1/`)

### 12.2 Terminology
- **Composition-level contract:** Validation across multiple library boundaries
- **Environment-stage:** Import/setup time (before training loop)
- **SHOULD_WORK gate:** ≥60% success threshold (failure documented, workflow continues)

---

**Document Status:** COMPLETE
**Next Step:** Phase 3 Step 3 - Architecture Design
