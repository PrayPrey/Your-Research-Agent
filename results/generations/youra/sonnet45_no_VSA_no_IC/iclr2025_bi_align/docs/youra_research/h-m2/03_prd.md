# Product Requirements Document: Multi-Layer Validation Detection (h-m2)

**Document Type:** PRD  
**Hypothesis ID:** h-m2  
**Phase:** 3 - Implementation Planning  
**Date:** 2026-08-20  
**Status:** APPROVED

---

## 1. Executive Summary

### 1.1 Objective
Validate that three-layer validation (schema + pattern + contract) detects constraint violations missed by schema-only validation, achieving ≥40 percentage point detection gap.

### 1.2 Success Criteria
- **Primary:** Three-layer detection rate - schema-only detection rate ≥ 40pp
- **Secondary:** Pattern layer ≥80% detection on semantic violations (C1/C2)

### 1.3 Scope
- Extend test suite from 20 to 30 adversarial cases
- Implement experiment runner for both validation conditions
- Measure detection rates per layer and per constraint
- No model training, no external dependencies

---

## 2. Requirements

### 2.1 Functional Requirements

#### FR1: Test Suite Extension
- **FR1.1:** Extend `test_cases.yaml` from 20 to 30 cases
- **FR1.2:** Distribution: 10 schema, 10 pattern, 5 contract, 5 valid
- **FR1.3:** Coverage: All 4 constraints (C1-C4) with ≥2 test cases each
- **FR1.4:** Ground-truth labels: `expected_detection` for each layer

#### FR2: Validation Runners
- **FR2.1:** Schema-only runner (baseline condition)
  - Pydantic `BaseModel` only
  - No `@field_validator` or `@model_validator`
  - Record: `{detected: boolean, layer: null}`

- **FR2.2:** Three-layer runner (proposed condition)
  - Layer 1: Schema validation
  - Layer 2: Pattern validation (`@field_validator`)
  - Layer 3: Contract validation (`@ensure`)
  - Fail-fast: stop at first violation
  - Record: `{detected: boolean, layer: "schema"|"pattern"|"contract"}`

#### FR3: Metrics Calculation
- **FR3.1:** Detection rate = violations detected / total violations × 100%
- **FR3.2:** Detection gap = three_layer_rate - schema_only_rate
- **FR3.3:** Per-layer rates: schema/pattern/contract
- **FR3.4:** Per-constraint rates: C1/C2/C3/C4
- **FR3.5:** False positive rate: rejected valid / total valid × 100%

#### FR4: Results Report
- **FR4.1:** Detection rate table (baseline vs proposed)
- **FR4.2:** Layer-specific analysis
- **FR4.3:** Constraint-specific analysis
- **FR4.4:** Gate verdict (PASS/PARTIAL/FAIL)

### 2.2 Non-Functional Requirements

#### NFR1: Correctness
- Ground-truth labels verified by manual review
- Spot-check: 5 sample cases for layer-by-layer behavior

#### NFR2: Reproducibility
- Deterministic test suite (no randomness)
- Version-controlled test cases (YAML format)

#### NFR3: Simplicity
- Reuse existing validation infrastructure from h-m1
- No new validation logic needed
- ~100 LOC experiment runner

---

## 3. Architecture

### 3.1 Components

```
experiments/
├── h_m2_multilayer_validation.py  # Main experiment runner
└── utils/
    └── h_m2_validator.py          # Per-layer detection tracker

tests/
└── h_m2/
    └── test_cases_h_m2.yaml       # 30-case adversarial suite

src/validation/  # (existing, no changes)
├── schemas.py                     # Schema layer
├── patterns.py                    # Pattern layer (C1/C2)
├── contracts.py                   # Contract layer (C3/C4)
└── constants.py                   # STANDARD_DATASETS, EXISTING_BENCHMARKS
```

### 3.2 Data Flow

```
test_cases_h_m2.yaml
        ↓
    [Load 30 cases]
        ↓
    ┌───────────────────┐
    │ Baseline Runner   │ → Schema-only → Detection rate (expected: 40%)
    └───────────────────┘
        ↓
    ┌───────────────────┐
    │ Three-Layer Runner│ → Schema → Pattern → Contract → Detection rate (expected: 100%)
    └───────────────────┘
        ↓
    [Calculate gap]
        ↓
    04_validation.md
```

### 3.3 Validation Layers (existing infrastructure)

**Layer 1: Schema** (`schemas.py`)
- Type checking: `str`, `int`, `List[str]`
- Literal enums: `Literal["standard", "custom", "programmatic-api"]`
- Field constraints: `min_length`, `min_items`

**Layer 2: Pattern** (`patterns.py`)
- `@field_validator("dataset_name")` → C1 keyword blacklist
- `@field_validator("evaluation_method")` → C2 keyword blacklist
- Forbidden keywords: synthetic, simulated, generated, human, manual

**Layer 3: Contract** (`contracts.py`)
- `@ensure` postcondition for C3 (standard dataset membership)
- `_validate_no_new_benchmarks()` for C4 (benchmark whitelist)
- Cross-field logic, state-based checks

---

## 4. Implementation Plan

### 4.1 Task Breakdown

**Tier 0 (Proof-of-Concept)**
- Estimated effort: 2-3 hours
- Risk: LOW (reuse h-m1 infrastructure)

**Epic Tasks:**

1. **EPIC-1: Test Suite Extension**
   - Extend `generate_test_cases.py` to produce 30 cases
   - Generate `test_cases_h_m2.yaml` with 10/10/5/5 distribution
   - Manual review: verify ground-truth `expected_detection` labels

2. **EPIC-2: Experiment Implementation**
   - Write `h_m2_multilayer_validation.py` main runner
   - Implement baseline condition (schema-only)
   - Implement three-layer condition (schema → pattern → contract)

3. **EPIC-3: Metrics and Reporting**
   - Calculate detection rates (baseline, three-layer, gap)
   - Per-layer analysis (schema/pattern/contract)
   - Per-constraint analysis (C1/C2/C3/C4)
   - Generate `04_validation.md` with gate verdict

**Validation Tasks:**

4. **VAL-1: Spot-Check Validation**
   - Run 5 sample cases manually
   - Verify layer-by-layer behavior matches expectations

5. **VAL-2: Coverage Check**
   - Verify all 4 constraints (C1-C4) represented
   - Verify 10/10/5/5 distribution

6. **VAL-3: False Positive Check**
   - Run 5 valid cases through three-layer validation
   - Ensure all pass (0% false positive rate)

### 4.2 Dependencies

**External:**
- h-m1 validation infrastructure (VALIDATED)

**Internal:**
- `src/validation/{schemas,patterns,contracts,constants}.py` (existing)
- `tests/phase_boundary_validation/generate_test_cases.py` (existing)

### 4.3 Deliverables

1. `tests/h_m2/test_cases_h_m2.yaml` (30 adversarial cases)
2. `experiments/h_m2_multilayer_validation.py` (experiment runner)
3. `experiments/utils/h_m2_validator.py` (detection tracker)
4. `docs/youra_research/h-m2/04_validation.md` (results report)

---

## 5. Risks and Mitigation

### 5.1 Technical Risks

**R1: Pattern layer detection <80%**
- Likelihood: LOW
- Impact: MEDIUM (secondary criterion fails)
- Mitigation: Synonym expansion for C1/C2 keywords if needed

**R2: Test suite imbalanced**
- Likelihood: MEDIUM
- Impact: HIGH (inflates detection rate)
- Mitigation: Adversarial review — "what edge case fools this layer?"

### 5.2 Experimental Risks

**R3: Ground-truth labels incorrect**
- Likelihood: LOW
- Impact: CRITICAL
- Mitigation: Independent verification, human spot-check

**R4: False positives on valid cases**
- Likelihood: LOW
- Impact: MEDIUM
- Mitigation: Validate 5 valid cases before full experiment

---

## 6. Success Metrics

### 6.1 Primary Metric
- **Detection Gap:** (three_layer_rate - schema_only_rate) ≥ 40pp
- **Target:** 60pp (100% - 40%)

### 6.2 Secondary Metrics
- Pattern layer ≥80% on C1/C2 violations
- Contract layer 100% on C3/C4 violations
- False positive rate = 0%

### 6.3 Gate Verdicts
- **PASS:** Primary + all secondary met
- **PARTIAL PASS:** Primary met, secondary ≥60%
- **FAIL:** Primary not met (<40pp gap)

---

## 7. Timeline

**Total Duration:** 1 day (8 hours)

- Test suite extension: 2 hours
- Experiment implementation: 3 hours
- Execution and analysis: 2 hours
- Documentation: 1 hour

---

## 8. Appendices

### 8.1 Test Case Example

```yaml
id: tc-16
name: Unknown standard dataset (C3 violation)
violation_type: contract
constraint_violated: C3
phase2a_output:
  research_question: "Can cross-field validation catch mismatches?"
  dataset_type: standard
  dataset_name: UnknownDataset123  # Not in STANDARD_DATASETS
  evaluation_method: automated
expected_detection:
  schema: true      # Structural validation passes
  pattern: true     # No keyword violations
  contract: false   # Cross-field logic fails
```

### 8.2 Constraint Definitions

- **C1 - No Synthetic Data:** Keywords in `dataset_name` (pattern layer)
- **C2 - No Human Evaluation:** Keywords in `evaluation_method` (pattern layer)
- **C3 - Standard Dataset Membership:** `dataset_type == "standard"` → `dataset_name ∈ STANDARD_DATASETS` (contract layer)
- **C4 - No New Benchmarks:** `evaluation_method` mentions benchmark → must be in `EXISTING_BENCHMARKS` (contract layer)

---

**Document Status:** Complete  
**Ready for Architecture Design:** Yes  
**Next Phase:** Architecture Agent (parallel with Logic/Config agents)
