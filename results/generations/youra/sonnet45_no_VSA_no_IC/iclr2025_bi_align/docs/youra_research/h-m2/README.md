# Hypothesis h-m2: Multi-Layer Validation Detection

**Type:** MECHANISM  
**Gate:** SHOULD_WORK  
**Status:** Phase 2C Complete  
**Created:** 2026-08-20

---

## Hypothesis Statement

Under contract-based validation with three layers (schema + pattern + composition), if all layers execute at phase boundaries, then constraint violations missed by schema-only are detected because pattern matching catches semantic violations and compositional contracts catch cross-phase dependencies.

---

## Success Criteria

**Primary:** Three-layer detection > schema-only detection by ≥40 percentage points  
**Secondary:** Pattern layer catches ≥80% of semantic violations (C1/C2)  
**Gate:** SHOULD_WORK (if fails → document limitation, proceed to h-m3)

---

## Folder Structure

```
h-m2/
├── README.md                      # This file
├── hypothesis.yaml                # Hypothesis metadata and configuration
├── experiment_spec.yaml           # Detailed experiment specification
├── 02c_experiment_brief.md        # Phase 2C: Experiment design (Level 1.5)
├── 03_prd.md                      # Phase 3: PRD (to be generated)
├── 03_architecture.md             # Phase 3: Architecture (to be generated)
├── 03_logic.md                    # Phase 3: Logic design (to be generated)
├── 03_config.md                   # Phase 3: Configuration (to be generated)
└── 04_validation.md               # Phase 4.5: Validation results (to be generated)
```

---

## Files

### Phase 2C Outputs (COMPLETE)

- **02c_experiment_brief.md** (23K)
  - Full experiment design
  - Three-layer validation architecture
  - Dataset specification (30 adversarial test cases)
  - Constraint coverage (C1-C4 with layer mapping)
  - Implementation plan (1 day, Tier 0)
  - Success criteria and risk mitigation

- **experiment_spec.yaml** (7K)
  - Structured experiment configuration
  - Variables, dataset, metrics
  - Procedure (5 steps)
  - Layer-specific expectations

- **hypothesis.yaml** (2K)
  - Hypothesis metadata
  - Gate configuration (SHOULD_WORK)
  - Phase progress tracking
  - Success criteria thresholds

---

## Experiment Overview

**Objective:** Validate that multi-layer validation architecture detects violations through complementary mechanisms.

**Approach:** Controlled test suite comparison (schema-only vs three-layer)

**Dataset:** 30 adversarial test cases with known ground-truth violations

**Baseline:** Schema-only (Pydantic BaseModel) — Expected 40% (10/25)

**Proposed:** Three-layer (schema + pattern + contract) — Expected 100% (25/25)

**Expected Gap:** 60 percentage points (exceeds ≥40pp threshold)

---

## Validation Architecture

```
THREE-LAYER VALIDATION

Layer 1: SCHEMA (Pydantic BaseModel)
├─ Type checking (str, int, List[str])
├─ Required fields
├─ Literal enums
└─ Field constraints (min_length, min_items)

Catches: Structural violations (10/10)
Misses: Semantic patterns (0/10), Compositional logic (0/5)

Layer 2: PATTERN (@field_validator)
├─ Keyword blacklists for C1 (synthetic data)
├─ Keyword blacklists for C2 (human evaluation)
└─ Regex pattern matching on field values

Catches: Semantic violations (10/10)
Misses: Cross-field constraints (0/5)

Layer 3: CONTRACT (@ensure postconditions)
├─ Cross-field constraints for C3 (standard dataset membership)
├─ State-based validation for C4 (benchmark whitelist)
└─ Compositional logic across multiple fields

Catches: Compositional violations (5/5)
```

---

## Test Suite

**Distribution:**
- Valid cases: 5 (baseline - should pass all layers)
- Schema violations: 10 (structural errors)
- Pattern violations: 10 (semantic keyword violations)
- Compositional violations: 5 (cross-field constraints)

**Constraints Tested:**
- C1: No synthetic data (3 pattern cases)
- C2: No human evaluation (3 pattern cases)
- C3: Standard dataset membership (2 contract cases)
- C4: No new benchmarks (3 contract cases)

**Storage:** `tests/phase_boundary_validation/test_cases_h_m2.yaml`

**Existing Infrastructure:**
- `tests/phase_boundary_validation/generate_test_cases.py` (20 existing cases)
- Extend to 30 cases with balanced distribution

---

## Implementation Plan

**Tier:** 0 (Proof-of-Concept)  
**Duration:** 1 day (8 hours)

**Breakdown:**
- Test suite extension: 2 hours
- Experiment implementation: 3 hours
- Execution and analysis: 2 hours
- Documentation: 1 hour

**Risk:** LOW (all validation layers already implemented in h-m1)

**Existing Components:**
- `src/validation/schemas.py` — Schema layer
- `src/validation/patterns.py` — Pattern layer (C1/C2)
- `src/validation/contracts.py` — Contract layer (C3/C4)
- `src/validation/constants.py` — STANDARD_DATASETS, EXISTING_BENCHMARKS

**New Components:**
- `tests/h_m2/test_cases_h_m2.yaml` — Extended 30-case test suite
- `experiments/h_m2_multilayer_validation.py` — Experiment runner
- `experiments/utils/h_m2_validator.py` — Per-layer detection tracker

---

## Metrics

**Primary:**
- Detection Rate Gap = (three_layer_rate - schema_only_rate)
  - Success: ≥40 percentage points
  - Expected: 60pp (100% - 40%)

**Secondary:**
- Layer-Specific Detection:
  - Schema layer: schema violations detected / total schema violations
  - Pattern layer: pattern violations detected / total pattern violations
  - Contract layer: contract violations detected / total contract violations

- Constraint-Specific Detection:
  - C1 detection rate (pattern layer)
  - C2 detection rate (pattern layer)
  - C3 detection rate (contract layer)
  - C4 detection rate (contract layer)

- False Positive Rate:
  - Valid cases incorrectly rejected / total valid cases
  - Target: 0% (all 5 valid cases should pass)

---

## Expected Results

**Baseline (Schema-Only):**
| Violation Type | Detected | Total | Rate |
|----------------|----------|-------|------|
| Schema | 10 | 10 | 100% |
| Pattern | 0 | 10 | 0% |
| Contract | 0 | 5 | 0% |
| **Overall** | **10** | **25** | **40%** |

**Proposed (Three-Layer):**
| Violation Type | Detected | Total | Rate | Layer |
|----------------|----------|-------|------|-------|
| Schema | 10 | 10 | 100% | Layer 1 |
| Pattern | 10 | 10 | 100% | Layer 2 |
| Contract | 5 | 5 | 100% | Layer 3 |
| **Overall** | **25** | **25** | **100%** | **All** |

**Detection Gap:** 60 percentage points ✅ (exceeds ≥40pp threshold)

---

## Connection to Main Hypothesis

**Main Hypothesis:** Contract-based validation reduces downstream failures by >80%

**h-m2 Tests:** Causal mechanism step 2 — "Do multiple layers detect complementary violations?"

**Causal Chain:**
1. **h-e1:** Contract framework exists ✅ (VALIDATED)
2. **h-m1:** Contracts force explicit checking ✅ (VALIDATED)
3. **h-m2 (this experiment):** Multi-layer detection catches schema-missed violations → (in progress)
4. **h-m3:** Early detection prevents downstream failures → (next)

**IF h-m2 passes:**
- Establishes validation layers are complementary (not redundant)
- Pattern layer catches semantic violations schema cannot
- Contract layer catches compositional violations neither can
- Prerequisite for h-m3 (early detection prevents downstream failures)

**IF h-m2 partial passes (primary met, secondary <80%):**
- Document limitation (e.g., pattern layer needs synonym expansion)
- Still proceed to h-m3 (detection mechanism proven, just needs refinement)

---

## Next Steps

**Phase 3: Implementation Planning**
1. Generate PRD (Product Requirements Document)
2. Generate Architecture specification
3. Generate Logic/Config specifications
4. Initialize Archon project with implementation tasks

**Phase 4: Coding**
1. Extend test suite to 30 cases (add 10 schema violations)
2. Implement experiment runner (loop over test cases, measure detection)
3. Implement per-layer detection tracker
4. Run validation experiment

**Phase 4.5: Validation**
1. Execute baseline condition (schema-only)
2. Execute three-layer condition
3. Compute detection gap
4. Verify success criteria
5. Write validation report → `04_validation.md`

---

## References

- Phase 2B Verification Plan: `../02b_verification_plan.md`
- Phase 2C Experiment Brief: `02c_experiment_brief.md`
- Experiment Specification: `experiment_spec.yaml`
- Hypothesis Metadata: `hypothesis.yaml`
- h-e1 validation: `../h-e1/04_validation.md` (contract framework exists)
- h-m1 validation: `../h-m1/04_validation.md` (contracts force checking)
- Existing validation infrastructure: `src/validation/` (schemas, patterns, contracts)

---

**Last Updated:** 2026-08-20  
**Phase:** 2C Complete  
**Ready for Phase 3:** YES
