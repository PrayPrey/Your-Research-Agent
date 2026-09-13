# Hypothesis h-m1: Contract Specification Forces Constraint Checking

**Type:** MECHANISM  
**Gate:** MUST_WORK  
**Status:** Phase 2C Complete  
**Created:** 2026-08-20

---

## Hypothesis Statement

Under research pipeline phase transitions with typed schemas, if explicit contracts (preconditions/postconditions/invariants) are specified at each boundary, then feasibility constraints are explicitly checked because Design by Contract formal methods force constraint validation that schema-only approaches leave implicit.

---

## Success Criteria

**Primary:** Contracts check 100% of 4 constraints, schema checks <50%  
**Gate:** MUST_WORK (if fails → PIVOT to more semantic constraints)

---

## Folder Structure

```
h-m1/
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

- **02c_experiment_brief.md** (21K)
  - Full experiment design
  - Technical architecture (schema-only vs contract-based)
  - Dataset specification (5 validation test cases)
  - Constraint coverage matrix (C1-C4)
  - Implementation plan (4 days, Tier 1)
  - Success criteria and risk mitigation

- **experiment_spec.yaml** (7K)
  - Structured experiment configuration
  - Variables, dataset, metrics
  - Procedure (5 steps)
  - File structure and dependencies

- **hypothesis.yaml** (2K)
  - Hypothesis metadata
  - Gate configuration
  - Phase progress tracking
  - Success criteria thresholds

---

## Experiment Overview

**Objective:** Demonstrate that contracts force explicit checking of constraints schema-only validation cannot express.

**Approach:** Comparative analysis (schema vs contracts)

**Dataset:** 5 validation test cases (TC-M1-01 through TC-M1-05)

**Baseline:** Pydantic schema-only (Field() + Literal[]) — Expected 0-25% coverage

**Proposed:** icontract @require/@ensure decorators — Expected 100% coverage

**Expected Gap:** ≥75 percentage points

---

## Validation Comparison

```
SCHEMA-ONLY (Pydantic BaseModel)
├─ Type checking
├─ Required fields
├─ Field constraints (min_length)
└─ Literal enums

CANNOT EXPRESS:
✗ Keyword blacklists (C1, C2)
✗ Cross-field constraints (C3)
✗ State-based validation (C4)

CONTRACT-BASED (icontract)
├─ All schema checks
├─ @require(lambda: "synthetic" not in dataset_name.lower())  # C1
├─ @require(lambda: "human" not in eval_method.lower())       # C2
├─ @ensure(lambda: dataset_type != "standard" or ...)         # C3
└─ @require(lambda: benchmark in EXISTING_BENCHMARKS)         # C4
```

---

## Test Suite

**Test Case Distribution:**
- TC-M1-01: C1 Synthetic Data Detection (VIOLATION)
- TC-M1-02: C2 Human Evaluation Detection (VIOLATION)
- TC-M1-03: C3 Cross-Field Constraint (VIOLATION)
- TC-M1-04: C4 State-Based Validation (VIOLATION)
- TC-M1-05: Valid Input (NO VIOLATION)

**Constraints Tested:**
- C1: No synthetic data (keyword pattern in dataset_name)
- C2: No human evaluation (keyword blacklist)
- C3: Standard dataset membership (cross-field IF-THEN)
- C4: No new benchmarks (state-based list check)

**Storage:** `tests/h_m1/test_cases.yaml`

---

## Implementation Plan

**Tier:** 1 (Low Complexity)  
**Duration:** 4 days

**Breakdown:**
- Day 1: Implement schema-only baseline, document gaps
- Day 2: Implement contract-based validation with icontract
- Day 3: Create test suite and run coverage experiment
- Day 4: Analyze results, verify success criteria, document findings

**Libraries:**
- Pydantic >=2.0 (schema validation baseline)
- icontract >=2.0 (contract-based validation)
- pytest >=7.0 (test framework)

---

## Metrics

**Primary:**
- Constraint Coverage = (Constraints Checked / Total Constraints) × 100%
  - Contract Coverage: Expected 100% (4/4)
  - Schema Coverage: Expected 0-25% (0-1/4)

**Secondary:**
- Expressiveness Gap = Contract Coverage - Schema Coverage
  - Expected: ≥75 percentage points
- Execution Behavior: Do violations halt execution?
- Implementation Complexity: Contract LOC < 50

---

## Expected Results

| Constraint | Schema Can Express? | Contract Can Express? |
|------------|--------------------|-----------------------|
| C1: No synthetic | ❌ | ✅ @require keyword check |
| C2: No human eval | ❌ | ✅ @require keyword blacklist |
| C3: Standard dataset | ❌ | ✅ @ensure cross-field |
| C4: No new benchmarks | ❌ | ✅ @require state-based |

**Coverage:**
- Schema-Only: 0/4 (0%)
- Contract-Based: 4/4 (100%)
- Gap: 100 percentage points

**Success:** Contract coverage ≥100% AND Schema coverage <50%

---

## Connection to Main Hypothesis

**Main Hypothesis:** Contract-based validation reduces downstream failures by >80%

**h-m1 Tests:** Causal mechanism step 1 — "Do contracts force checking?"

**Causal Chain:**
1. **h-m1 (this experiment):** Contracts force explicit constraint checking → ✅
2. **h-m2:** Multi-layer validation catches violations → (next)
3. **h-m3:** Early detection prevents downstream failures → (next)

**IF h-m1 passes:**
- Establishes contracts CAN express constraints schema cannot
- Prerequisite for h-m2 (multi-layer detection rates)
- Does NOT prove contracts reduce failures (that's h-m3)

---

## Next Steps

**Phase 3: Implementation Planning**
1. Generate PRD (Product Requirements Document)
2. Generate Architecture specification
3. Generate Logic/Config specifications
4. Generate PRP (Project Requirements Plan)
5. Initialize Archon tasks

**Phase 4: Coding**
1. Implement schema-only baseline (schemas.py)
2. Implement contract-based validation (contracts.py)
3. Create test suite (test_cases.yaml)
4. Run coverage experiment (run_coverage_test.py)

**Phase 4.5: Validation**
1. Run test suite
2. Count constraint coverage (schema vs contract)
3. Verify success criteria
4. Write validation report → `04_validation.md`

---

## References

- Phase 2B Verification Plan: `../02b_verification_plan.md`
- Phase 2C Experiment Brief: `02c_experiment_brief.md`
- Experiment Specification: `experiment_spec.yaml`
- Hypothesis Metadata: `hypothesis.yaml`
- h-e1 validation: `../h-e1/04_validation.md` (contract framework validated)

---

**Last Updated:** 2026-08-20  
**Phase:** 2C Complete  
**Ready for Phase 3:** YES
