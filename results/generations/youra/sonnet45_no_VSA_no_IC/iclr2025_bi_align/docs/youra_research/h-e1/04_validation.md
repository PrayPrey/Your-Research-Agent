# Validation Results: h-e1 Contract Validation

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE  
**Date:** 2026-08-20  
**Phase:** 4 - Validation

---

## Executive Summary

Contract-based validation framework successfully demonstrated **200% improvement** over schema-only validation in detecting feasibility constraint violations at phase boundaries.

**Gate Result:** **PASS** (MUST_WORK gate satisfied)

---

## Violation Detection Rates

| Layer | Detection Rate | Detected |
|-------|----------------|----------|
| Schema Only | 33.33% | 5/15 violations |
| Schema + Pattern | 66.67% | 10/15 violations |
| Full Contract | 100.00% | 15/15 violations |

**Improvement:** 200.0% (contract vs schema-only)

**Execution Overhead:** 0.01 ms (well below 100ms threshold)

---

## Layer-wise Breakdown

### Layer 1: Schema (Pydantic BaseModel)

**Detected:** 5/15 violations (33%)

**Coverage:**
- Type errors
- Missing required fields
- Field constraint violations (min_length, min_items)

**Missed:**
- Constraint keyword patterns (C1: synthetic data, C2: human evaluation)
- Cross-field constraints (C3: standard dataset membership)
- State-based constraints (C4: benchmark existence)

### Layer 2: Pattern (field_validator)

**Detected:** 10/15 violations (67%)

**Coverage:**
- All schema-layer violations
- C1: Synthetic data keywords in dataset_name
- C2: Human evaluation keywords in evaluation_method

**Missed:**
- C3: Cross-field constraint (dataset_type="standard" → dataset_name must be in STANDARD_DATASETS)
- C4: Benchmark name validation

### Layer 3: Contract (icontract)

**Detected:** 15/15 violations (100%)

**Coverage:**
- All schema + pattern violations
- C3: Cross-field invariants via @ensure decorators
- C4: State-based validation via custom methods
- Compositional constraints (hypotheses count ≥ 1)

---

## Example Violations

### Caught by Schema Only

**tc-06: Missing research_question**
```python
# Missing required field
ValidationError: Field required [type=missing]
```

**tc-08: Empty hypotheses list**
```python
hypotheses: []  # Violates min_length=1
ValidationError: List should have at least 1 item [type=too_short]
```

### Caught by Pattern (Missed by Schema)

**tc-11: Synthetic keyword in dataset_name**
```python
dataset_name: "synthetic_data"
# Caught by field_validator
ValueError: C1 violation: synthetic data forbidden
```

**tc-13: Human keyword in evaluation_method**
```python
evaluation_method: "human annotators"
# Caught by field_validator
ValueError: C2 violation: human evaluation forbidden
```

### Caught by Contract Only (Missed by Schema+Pattern)

**tc-16: Unknown standard dataset**
```python
dataset_type: "standard"
dataset_name: "UnknownDataset123"
# Caught by @ensure postcondition
ViolationError: C3 violation: unknown standard dataset
```

**tc-18: New benchmark name**
```python
evaluation_method: "new benchmark XYZ"
# Caught by _validate_no_new_benchmarks()
ViolationError: C4 violation: new benchmark not allowed
```

---

## Gate Evaluation (MUST_WORK)

**Primary Criterion:**
✓ **PASS**: Improvement 200.0% ≥ 50% threshold

**Secondary Criteria:**
✓ False positive rate: 0% < 10% threshold  
✓ Execution overhead: 0.01ms < 100ms threshold  
✓ Contract LOC: 25 LOC < 50 LOC threshold

---

## Key Findings

1. **Three-layer validation is implementable** using Pydantic + icontract
2. **Contract layer detects compositional failures** that schema/pattern layers cannot express
3. **200% improvement** over schema-only validation demonstrates feasibility constraint enforcement
4. **Minimal overhead** (0.01ms) makes it suitable for production pipelines
5. **Compact specification** (25 LOC for contract layer) meets maintainability requirements

---

## Implementation Files

**Validation Framework:**
- `src/validation/schemas.py` — Layer 1: Pydantic BaseModel
- `src/validation/patterns.py` — Layer 2: field_validator decorators
- `src/validation/contracts.py` — Layer 3: icontract @ensure decorators
- `src/validation/constants.py` — Constraint definitions

**Test Suite:**
- `tests/phase_boundary_validation/test_cases.yaml` — 20 adversarial cases
- `tests/phase_boundary_validation/generate_test_cases.py` — Test generator

**Experiment:**
- `experiments/h_e1_contract_validation.py` — Validation executor

---

## Conclusion

**Hypothesis h-e1 VALIDATED:** Contract-based validation framework with three layers (schema + pattern + composition) successfully detects constraint violations at phase boundaries that schema-only validation misses.

**Gate:** PASS  
**Improvement:** 200%  
**Next Phase:** Phase 5 — Baseline Comparison (if required by workflow)
