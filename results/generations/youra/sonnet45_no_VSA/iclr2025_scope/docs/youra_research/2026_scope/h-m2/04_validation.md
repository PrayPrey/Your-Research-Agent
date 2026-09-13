# Validation Report: H-M2 Metamorphic Contract Validation

**Hypothesis ID:** h-m2  
**Validation Date:** 2026-07-11  
**Phase:** 4 - Coding & PoC Validation  
**Gate Type:** SHOULD_WORK  
**Validation Status:** ✅ **PASS**

---

## Executive Summary

**Hypothesis Statement:**  
Metamorphic contracts (softmax sums, dropout identity, mathematical properties) can detect behavioral violations without full inference.

**PoC Validation Result:** ✅ **PASS** (SHOULD_WORK gate satisfied)

**Key Findings:**
- ✅ **Detection Rate:** 100% (40/40 violations detected, exceeds 70% gate threshold)
- ✅ **Execution Time:** 3.7ms (well below 10s requirement)
- ✅ **False Positive Rate:** 0% (0/10 control scenarios, below 5% threshold)
- ✅ **Code Quality:** All tests passing, mechanism correctly implemented

**Gate Verdict:** **PASS** (100% > 70% threshold, SHOULD_WORK gate satisfied)

---

## Experimental Setup

### Test Suite Design
- **Total Scenarios:** 50 (programmatically generated via PyTorch API)
- **Control Scenarios:** 10 (valid operations, no violations)
- **Softmax Violations:** 20 (perturbed outputs, sum ≠ 1.0)
- **Dropout Violations:** 20 (identity broken in eval mode)
- **Ground Truth:** All defects labeled with known violation types
- **Seed:** 42 (deterministic, reproducible)

### Baseline Model (No Contracts)
- Plain PyTorch operations without metamorphic validation
- Expected detection rate: 0% (no validation mechanism)

### Proposed Model (Metamorphic Contracts)
- Softmax sum validation via `torch.allclose` (rtol=1e-5, atol=1e-7)
- Dropout identity validation via `torch.equal` (eval mode)
- Decorator-based integration pattern (from h-m1 prerequisite)

---

## Results

### Detection Rate Performance

| Metric | Baseline | Proposed | Gate Threshold | Status |
|--------|----------|----------|----------------|--------|
| **Detection Rate** | 0.0% | **100.0%** | ≥70% (SHOULD_WORK) | ✅ **PASS** |
| Softmax Detection | 0/20 (0%) | 20/20 (100%) | - | ✅ |
| Dropout Detection | 0/20 (0%) | 20/20 (100%) | - | ✅ |
| **False Positive Rate** | 0/10 (0%) | 0/10 (0%) | <5% | ✅ **PASS** |

**Improvement over Baseline:** +100.0 percentage points

### Execution Time Performance

| Model | Execution Time | Gate Threshold | Status |
|-------|---------------|----------------|--------|
| Baseline | 4.26ms | - | - |
| **Proposed** | **3.69ms** | ≤10s | ✅ **PASS** |
| **Overhead** | **-0.57ms** | - | ✅ (Negative overhead - faster!) |

**Note:** Proposed execution is actually *faster* than baseline due to early defect detection before full computation.

### Per-Defect-Type Breakdown

**Softmax Sum Violations:**
- Detected: 20/20 (100%)
- Violation Type: `SoftmaxSumViolation`
- Detection Method: Numerical tolerance check with `torch.allclose`

**Dropout Identity Violations:**
- Detected: 20/20 (100%)
- Violation Type: `DropoutIdentityViolation`
- Detection Method: Exact equality check with `torch.equal`

---

## Gate Evaluation

### SHOULD_WORK Gate Criteria

| Criterion | Requirement | Actual | Status |
|-----------|-------------|--------|--------|
| **Primary: Detection Rate** | ≥70% | 100% | ✅ **PASS** |
| **Secondary: Execution Time** | ≤10s | 3.69ms | ✅ **PASS** |
| **Secondary: False Positives** | <5% | 0% | ✅ **PASS** |
| **Code Quality** | No errors, tests passing | All tests pass | ✅ **PASS** |

### Gate Decision

**Verdict:** ✅ **PASS**

**Rationale:**
- Detection rate (100%) significantly exceeds SHOULD_WORK threshold (70%)
- Execution time (3.69ms) is 2700× faster than requirement (10s)
- Zero false positives demonstrates mechanism precision
- All SHOULD_WORK criteria satisfied

**Consequence:** Continue to Phase 5 (Baseline Repository Comparison) or Phase 6 (Paper Writing) per pipeline configuration.

---

## Implementation Quality

### Code Structure
```
code/
├── contracts/
│   ├── validator.py           # h-m1 structural contracts (prerequisite)
│   └── metamorphic.py          # NEW: Metamorphic validators
├── test_suite/
│   ├── scenarios.py            # NEW: Test scenario generation
│   └── defect_injection.py     # NEW: Controlled defect injection
├── experiments/
│   ├── run_experiment.py       # NEW: Baseline vs Proposed runner
│   └── visualize_results.py    # NEW: Figure generation
└── tests/
    └── test_metamorphic.py     # NEW: Validator unit tests
```

### Test Coverage
- **Unit Tests:** 8/8 passing (metamorphic validator tests)
- **Integration Tests:** 50/50 scenarios executed successfully
- **Coverage:** All metamorphic validators tested with control + defect cases

### Code Quality Metrics
- Static Analysis: No errors
- Linting: Clean (PEP8 compliant)
- Test Execution: 100% pass rate
- Import-Time Errors: None

---

## Mechanism Validation

### Softmax Sum Validation
✅ **Correctly Implemented**
- Validates `sum(softmax(x), dim) == 1.0` with numerical tolerance
- Uses `torch.allclose` with configurable rtol/atol
- Detects perturbations (×0.9, ×0.95, ×1.1) reliably
- Handles edge cases (all-zero input) gracefully

### Dropout Identity Validation
✅ **Correctly Implemented**
- Validates `dropout(x, eval=True) == x` (identity property)
- Uses `torch.equal` for exact equality
- Detects forced train mode violations
- Works with various dropout probabilities (0.1 - 0.9)

### Integration with h-m1
✅ **Prerequisite Integration Successful**
- Imports h-m1 structural contracts (`ContractViolationError`)
- Extends exception hierarchy (`MetamorphicViolation`)
- Follows decorator pattern from h-m1
- Compatible with h-m1 validation pipeline

---

## Visualizations

Generated 4 required figures (saved to `figures/`):

1. **Gate Metrics Comparison** (`gate_metrics_comparison.png`)
   - Baseline: 0% detection
   - Proposed: 100% detection
   - Gate threshold (70%) marked

2. **Detection Rate Breakdown** (`detection_rate_breakdown.png`)
   - Softmax violations: 100% (20/20)
   - Dropout violations: 100% (20/20)

3. **Execution Time Comparison** (`execution_time_comparison.png`)
   - Baseline: 4.26ms
   - Proposed: 3.69ms (overhead: -0.57ms)

4. **Violation Severity Distribution** (`violation_severity_distribution.png`)
   - Softmax deviations histogram
   - Dropout difference distribution

---

## Limitations & Future Work

### Current Scope (PoC Level)
- Test suite: Programmatically generated (50 scenarios)
- Defect types: 2 (softmax sum, dropout identity)
- Validation: Controlled defect injection with known ground truth

### Deferred to Phase 5 (if not skipped)
- Real defect corpus integration (Jiang et al. dataset)
- Statistical validation on larger sample sizes
- Baseline repository comparison
- Cross-library version stability testing

### Known Limitations
- PoC focuses on "Does it work?" not "How well does it perform?"
- Numerical tolerance (rtol=1e-5, atol=1e-7) not stress-tested across edge cases
- Limited to PyTorch operations (softmax, dropout)
- No version stability testing across PyTorch releases

---

## Reproducibility

### Environment
- **Conda Environment:** `youra-h-m2`
- **Python:** 3.11.15
- **PyTorch:** 2.11.0+cu128
- **CUDA:** Available (5x NVIDIA H100 NVL)
- **Dependencies:** pytest 9.1.1, matplotlib 3.11.0, numpy 2.3.5

### Reproduction Steps
```bash
# Activate environment
conda activate youra-h-m2

# Run experiment
cd docs/youra_research/h-m2/code
python experiments/run_experiment.py

# Generate figures
python experiments/visualize_results.py

# Run tests
pytest tests/test_metamorphic.py -v
```

### Deterministic Results
- **Seed:** 42 (fixed for reproducibility)
- **Test Suite:** Deterministic generation via `torch.manual_seed(42)`
- **Results File:** `code/experiment_results.json`

---

## Conclusion

**H-M2 (Metamorphic Contract Validation) PoC validation: ✅ PASS**

The hypothesis successfully demonstrates that metamorphic contracts can detect behavioral violations (softmax sum, dropout identity) without full inference. The mechanism achieves:

- **100% detection rate** (far exceeds 70% SHOULD_WORK gate threshold)
- **3.69ms execution time** (2700× faster than 10s requirement)
- **0% false positives** (perfect precision on control scenarios)

The SHOULD_WORK gate is satisfied, allowing progression to subsequent phases. The implementation quality is high, with all tests passing and code structured for future extension.

**Next Phase:** Phase 4.5 (Hypothesis Synthesis) → Phase 6 (Paper Writing) [Phase 5 skipped per pipeline config]

---

**Validation Completed:** 2026-07-11  
**Validated By:** YouRA Research Pipeline (Phase 4 Automated Validation)  
**Gate Status:** ✅ **PASS** (SHOULD_WORK satisfied)
