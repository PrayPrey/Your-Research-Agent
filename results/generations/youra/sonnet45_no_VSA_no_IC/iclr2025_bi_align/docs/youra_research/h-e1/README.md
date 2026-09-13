# Hypothesis h-e1: Contract-Based Phase Transition Validation

**Type:** EXISTENCE  
**Gate:** MUST_WORK  
**Status:** Phase 2C Complete  
**Created:** 2026-08-20

---

## Hypothesis Statement

Under research workflows with sequential multi-phase structure and typed interfaces, if contract-based validation (schema + pattern + composition layers) is implemented at phase boundaries, then constraint violations can be detected before Phase 4/5 execution because contracts enforce preconditions/postconditions/invariants that schema-only validation cannot check.

---

## Success Criteria

**Primary:** Contract-based detection rate >50% better than schema-only  
**Gate:** MUST_WORK (if fails → ABORT)

---

## Folder Structure

```
h-e1/
├── README.md                      # This file
├── hypothesis.yaml                # Hypothesis metadata and configuration
├── experiment_spec.yaml           # Detailed experiment specification
├── 02c_experiment_brief.md        # Phase 2C: Experiment design (Level 1.5)
├── prd/                          # Phase 3: PRD (to be generated)
├── architecture/                 # Phase 3: Architecture docs (to be generated)
├── prp/                          # Phase 3: Project Requirements Plan (to be generated)
├── code/                         # Phase 4: Implementation (to be generated)
└── validation/                   # Phase 4.5: Validation results (to be generated)
```

---

## Files

### Phase 2C Outputs (COMPLETE)

- **02c_experiment_brief.md** (17K)
  - Full experiment design
  - Technical architecture (3 validation layers)
  - Dataset specification (20 adversarial test cases)
  - Baseline experiments (schema-only, schema+pattern)
  - Implementation plan (12 hours, Tier 1)
  - Success criteria and risk mitigation

- **experiment_spec.yaml** (6K)
  - Structured experiment configuration
  - Variables, dataset, metrics
  - Procedure (8 steps)
  - File structure and dependencies

- **hypothesis.yaml** (2K)
  - Hypothesis metadata
  - Gate configuration
  - Phase progress tracking
  - Success criteria thresholds

---

## Experiment Overview

**Objective:** Prove that three-layer contract validation can be implemented and detects violations schema-only validation misses.

**Approach:** PoC with controlled adversarial test suite

**Dataset:** 20 test cases (5 valid, 15 violations across 3 types)

**Baseline:** Pydantic schema-only validation (30% detection rate)

**Proposed:** Schema + Pattern + Contract validation (95% detection rate)

**Expected Improvement:** +217% (2.17×)

---

## Validation Architecture

```
INPUT (Phase 2A Output)
  ↓
Layer 1: SCHEMA VALIDATION (Pydantic BaseModel)
  ├─ Type checking
  ├─ Required fields
  └─ Field types
  ↓
Layer 2: PATTERN VALIDATION (Pydantic field_validator)
  ├─ C1: No synthetic data (regex blacklist)
  ├─ C2: No human evaluation (keyword blacklist)
  ├─ C3: Real standard datasets
  └─ C4: No new benchmarks
  ↓
Layer 3: CONTRACT VALIDATION (contractme)
  ├─ @precondition: Input constraints
  ├─ @postcondition: Output guarantees
  └─ Compositional invariants (cross-field)
  ↓
OUTPUT (Phase 2B Input)
```

---

## Test Suite

**Test Case Distribution:**
- 5 valid cases (no violations)
- 5 schema violations (type errors, missing fields)
- 5 pattern violations (constraint keywords)
- 5 contract violations (compositional failures)

**Constraints Tested:**
- C1: No synthetic data
- C2: No human evaluation
- C3: Real standard datasets only
- C4: No new benchmarks

**Storage:** `tests/phase_boundary_validation/test_cases.yaml`

---

## Implementation Plan

**Tier:** 1 (Low Complexity)  
**Duration:** 1.5 days (12 hours)

**Breakdown:**
- Environment setup: 15 min
- Test case generation: 2 hours
- Schema layer: 1 hour
- Pattern layer: 2 hours
- Contract layer: 3 hours
- Baseline experiments: 1 hour
- Contract experiments: 1 hour
- Analysis: 2 hours

**Libraries:**
- Pydantic v2.8.0 (schema + pattern validation)
- contractme v2.2.0 (contract validation)
- pytest (test framework)

---

## Metrics

**Primary:**
- Detection Rate Improvement = (Contract_DR - SchemaOnly_DR) / SchemaOnly_DR × 100%
- Success Threshold: ≥50%

**Secondary:**
- False Positive Rate < 10%
- Execution Overhead < 100ms
- Contract LOC < 50 per boundary

**Tertiary:**
- Layer-wise detection breakdown
- Constraint-specific patterns

---

## Expected Results

| Approach | Detection Rate | Improvement |
|----------|---------------|-------------|
| Schema-Only | 30% (6/20) | Baseline |
| Schema + Pattern | 60% (12/20) | +100% |
| Full Contracts | 95% (19/20) | +217% |

**Success:** ≥50% improvement → Contract detects ≥9/20 (schema detects ≤6/20)

---

## Next Steps

**Phase 3: Implementation Planning**
1. Generate PRD (Product Requirements Document)
2. Generate Architecture specification
3. Generate PRP (Project Requirements Plan)
4. Initialize Archon tasks

**Phase 4: Coding**
1. Implement validation layers
2. Generate test suite
3. Write baseline experiments
4. Write contract experiments

**Phase 4.5: Validation**
1. Run test suite
2. Compute detection rates
3. Calculate improvement
4. Write validation report → `04_validation.md`

---

## References

- Phase 2B Verification Plan: `../02b_verification_plan.md`
- Phase 2C Experiment Brief: `02c_experiment_brief.md`
- Experiment Specification: `experiment_spec.yaml`
- Hypothesis Metadata: `hypothesis.yaml`

---

**Last Updated:** 2026-08-20  
**Phase:** 2C Complete  
**Ready for Phase 3:** YES
