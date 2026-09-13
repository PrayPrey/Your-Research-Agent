# Experiment Brief: Multi-Layer Validation Detection (h-m2)

**Hypothesis ID:** h-m2  
**Type:** MECHANISM  
**Level:** 1.5 (Detailed specification)  
**Date:** 2026-08-20  
**Phase:** 2C - Experiment Design

---

## 1. Hypothesis Statement

Under contract-based validation with three layers (schema + pattern + composition), if all layers execute at phase boundaries, then constraint violations missed by schema-only are detected because pattern matching catches semantic violations and compositional contracts catch cross-phase dependencies.

**Prerequisites:** h-m1 (VALIDATED - contracts force explicit checking)

**Gate Type:** SHOULD_WORK

**Success Criteria:**
- Primary: Three-layer detection > schema-only detection by ≥40 percentage points
- Secondary: Pattern layer catches ≥80% of semantic violations (C1/C2)

---

## 2. Research Objective

Validate that multi-layer validation architecture (schema → pattern → contract) detects constraint violations through complementary mechanisms, with each layer catching violations the previous layer misses.

**Key Question:** Does three-layer validation achieve higher detection rates than single-layer schema validation alone?

**Causal Chain Position:** Step 2 of 3 (h-m1 → **h-m2** → h-m3)

---

## 3. Dataset Specification

### 3.1 Dataset Selection

**Type:** custom  
**Name:** Adversarial Test Suite for Phase Boundary Validation  
**Source:** Generated test cases with known ground-truth constraint violations

**Rationale:**
- Real hypotheses have unknown ground-truth violations (cannot measure detection rate)
- Controlled test cases enable precise measurement of each layer's detection capability
- Adversarial construction ensures test cases target specific validation layer gaps

### 3.2 Dataset Structure

**Total Size:** 30 test cases

**Distribution:**
- Valid cases: 5 (baseline - should pass all layers)
- Schema violations: 10 (structural errors - should fail at schema layer)
- Pattern violations: 10 (semantic keyword violations - should fail at pattern layer)
- Compositional violations: 5 (cross-field constraints - should fail at contract layer)

**Test Case Format:**
```yaml
id: tc-{nn}
name: {descriptive name}
violation_type: {schema|pattern|contract|none}
constraint_violated: {C1|C2|C3|C4|none}
phase2a_output:
  research_question: {string}
  dataset_type: {standard|custom|programmatic-api}
  dataset_name: {string}
  evaluation_method: {string}
  # ... other Phase 2A output fields
expected_detection:
  schema: {true|false}
  pattern: {true|false}
  contract: {true|false}
```

### 3.3 Constraint Coverage

**C1 - No Synthetic Data:** 3 pattern violation cases
- Keywords: "synthetic", "simulated", "generated" in `dataset_name`
- Expected: schema=pass, pattern=fail

**C2 - No Human Evaluation:** 3 pattern violation cases
- Keywords: "human", "manual", "annotator" in `evaluation_method`
- Expected: schema=pass, pattern=fail

**C3 - Standard Dataset Membership:** 2 contract violation cases
- Cross-field: `dataset_type=="standard"` but `dataset_name ∉ STANDARD_DATASETS`
- Expected: schema=pass, pattern=pass, contract=fail

**C4 - No New Benchmarks:** 3 contract violation cases
- State-based: `evaluation_method` mentions benchmark not in `EXISTING_BENCHMARKS`
- Expected: schema=pass, pattern=pass, contract=fail

### 3.4 Data Preparation

**Existing Infrastructure:**
- `tests/phase_boundary_validation/generate_test_cases.py` — Test case generator (already implemented)
- `tests/phase_boundary_validation/test_cases.yaml` — 20 existing test cases

**Required Updates:**
1. Extend test suite from 20 to 30 cases (add 10 schema violations)
2. Balance distribution: 10 schema, 10 pattern, 5 contract, 5 valid
3. Ensure each constraint (C1-C4) has ≥2 test cases

**Verification:**
- Manual review: Each test case has correct `expected_detection` ground truth
- Coverage check: All 4 constraints represented
- Balance check: No single violation type dominates (10/10/5/5 distribution)

---

## 4. Baseline Experiments

### 4.1 Baseline Method

**Name:** Schema-Only Validation  
**Implementation:** Pydantic `BaseModel` with typed fields only

**Included:**
- Type checking (`str`, `int`, `List[str]`)
- Literal enums (`Literal["standard", "custom", "programmatic-api"]`)
- Field constraints (`min_length`, `min_items`)

**Excluded:**
- `@field_validator` decorators (pattern layer)
- `@model_validator` decorators (contract layer)
- Any semantic or cross-field checks

**Expected Behavior:**
- Detects: Missing fields, wrong types, literal enum violations, length constraints
- Misses: Keyword patterns (C1/C2), cross-field logic (C3), state-based checks (C4)

**Rationale:** Isolates schema layer to measure what typed structure alone can detect.

### 4.2 Baseline Measurement

**Metric:** Detection rate = (violations detected) / (total violations) × 100%

**Expected Performance:**
- Schema violations (10 cases): 100% detected (by definition)
- Pattern violations (10 cases): 0% detected (schema cannot check keywords)
- Contract violations (5 cases): 0% detected (schema cannot check cross-field logic)
- **Overall:** 10/25 = 40% detection rate

**Justification:** h-m1 validated schema coverage = 0% for feasibility constraints (C1-C4). Schema layer only catches structural violations, not semantic/compositional ones.

---

## 5. Proposed Method

### 5.1 Three-Layer Validation Architecture

**Layer 1: Schema Validation** (Pydantic `BaseModel`)
- Type checking, required fields, literal enums
- Same as baseline

**Layer 2: Pattern Validation** (`@field_validator`)
- Keyword blacklists for C1 (synthetic data)
- Keyword blacklists for C2 (human evaluation)
- Regex pattern matching on field values

**Layer 3: Contract Validation** (`@ensure` postconditions)
- Cross-field constraints for C3 (standard dataset membership)
- State-based validation for C4 (benchmark whitelist)
- Compositional logic across multiple fields

**Execution Order:** Schema → Pattern → Contract (fail-fast: stop at first violation)

### 5.2 Implementation

**Existing Infrastructure:**
- `src/validation/schemas.py` — Schema layer (Pydantic models)
- `src/validation/patterns.py` — Pattern layer (field validators for C1/C2)
- `src/validation/contracts.py` — Contract layer (icontract decorators for C3/C4)
- `src/validation/constants.py` — `STANDARD_DATASETS`, `EXISTING_BENCHMARKS` whitelists

**Test Harness:**
```python
def run_three_layer_validation(test_case: dict) -> dict:
    """Run test case through all three validation layers."""
    results = {"schema": False, "pattern": False, "contract": False}
    
    try:
        # Layer 1: Schema
        from src.validation.schemas import Phase2AOutput
        Phase2AOutput(**test_case["phase2a_output"])
        results["schema"] = True
        
        # Layer 2: Pattern (inherits schema + adds validators)
        from src.validation.patterns import Phase2AOutputWithPatterns
        Phase2AOutputWithPatterns(**test_case["phase2a_output"])
        results["pattern"] = True
        
        # Layer 3: Contract (inherits pattern + adds contracts)
        from src.validation.contracts import Phase2AOutputWithContracts
        obj = Phase2AOutputWithContracts(**test_case["phase2a_output"])
        obj._validate_contracts()  # Explicit contract check
        results["contract"] = True
        
    except Exception as e:
        # Violation caught at some layer
        pass
    
    return results
```

### 5.3 Expected Performance

**Layer-by-Layer Detection:**
- Schema violations (10): Caught at Layer 1
- Pattern violations (10): Pass Layer 1, caught at Layer 2
- Contract violations (5): Pass Layers 1-2, caught at Layer 3
- Valid cases (5): Pass all layers

**Cumulative Detection Rate:**
- After Layer 1: 10/25 = 40%
- After Layer 2: 20/25 = 80%
- After Layer 3: 25/25 = 100%

**Primary Criterion:** 100% - 40% = **60 percentage point gap** (exceeds ≥40pp threshold)

---

## 6. Experiment Design

### 6.1 Experimental Procedure

**Step 1: Test Suite Preparation**
1. Run `tests/phase_boundary_validation/generate_test_cases.py` to create 30-case suite
2. Manual review: Verify ground-truth `expected_detection` labels
3. Save to `tests/phase_boundary_validation/test_cases_h_m2.yaml`

**Step 2: Baseline Condition**
1. Load 30 test cases
2. For each case, run schema-only validation
3. Record detection: {detected: boolean, layer: null}
4. Calculate baseline detection rate

**Step 3: Three-Layer Condition**
1. Load same 30 test cases
2. For each case, run three-layer validation
3. Record detection: {detected: boolean, layer: "schema"|"pattern"|"contract"}
4. Calculate three-layer detection rate

**Step 4: Per-Layer Analysis**
1. For each violation type (schema/pattern/contract), compute layer-specific detection
2. Verify: Pattern layer catches ≥80% of C1/C2 violations
3. Verify: Contract layer catches 100% of C3/C4 violations

**Step 5: Statistical Validation**
1. Compute detection gap: (three_layer_rate - schema_only_rate)
2. Check primary criterion: gap ≥ 40pp
3. Check secondary criterion: pattern layer ≥ 80% on C1/C2 violations

### 6.2 Metrics

**Primary Metric:** Detection Rate Gap (percentage points)
- Formula: `(three_layer_detection_rate - schema_only_detection_rate)`
- Success: ≥40 percentage points

**Secondary Metrics:**
1. **Layer-Specific Detection Rates:**
   - Schema layer: {schema violations detected} / {total schema violations}
   - Pattern layer: {pattern violations detected} / {total pattern violations}
   - Contract layer: {contract violations detected} / {total contract violations}

2. **Constraint-Specific Detection:**
   - C1 detection rate (pattern layer)
   - C2 detection rate (pattern layer)
   - C3 detection rate (contract layer)
   - C4 detection rate (contract layer)

3. **False Positive Rate:**
   - Valid cases incorrectly rejected / total valid cases
   - Target: 0% (all 5 valid cases should pass all layers)

### 6.3 Success Criteria

**Primary (MUST MEET):**
- Detection gap ≥40pp: Three-layer catches ≥40% more violations than schema-only

**Secondary (NICE TO HAVE):**
- Pattern layer ≥80% on semantic violations (C1/C2 combined)
- Contract layer 100% on compositional violations (C3/C4 combined)
- False positive rate = 0% (no valid cases rejected)

**Gate Verdict:**
- **PASS:** Primary + Secondary all met
- **PARTIAL PASS:** Primary met, Secondary ≥60% (document limitation, proceed to h-m3)
- **FAIL:** Primary not met (<40pp gap)

---

## 7. Implementation Planning

### 7.1 Required Components

**Existing (No Changes Needed):**
- `src/validation/schemas.py` — Schema layer
- `src/validation/patterns.py` — Pattern layer (C1/C2)
- `src/validation/contracts.py` — Contract layer (C3/C4)
- `src/validation/constants.py` — Constraint definitions
- `tests/phase_boundary_validation/generate_test_cases.py` — Test generator

**New Components:**
1. `tests/h_m2/test_cases_h_m2.yaml` — Extended 30-case test suite
2. `experiments/h_m2_multilayer_validation.py` — Experiment runner
3. `experiments/utils/h_m2_validator.py` — Per-layer detection tracker

### 7.2 Complexity Assessment

**Implementation Tier:** Tier 0 (Proof-of-Concept)
- No new validation logic needed (reuse h-m1 infrastructure)
- Test suite extension: +10 schema violation cases
- Experiment runner: ~100 LOC (loop over test cases, measure detection)

**Estimated Effort:** 2-3 hours
- Test suite extension: 30 min
- Experiment runner: 1 hour
- Validation and documentation: 1 hour

**Risk:** LOW
- All validation layers already implemented and tested (h-m1)
- No model training, no API calls, no external dependencies
- Deterministic test suite (no random variation)

---

## 8. Validation Strategy

### 8.1 Correctness Checks

**Test Suite Validation:**
1. Manual review: Each test case has correct ground-truth labels
2. Coverage check: All 4 constraints (C1-C4) represented
3. Balance check: 10/10/5/5 distribution maintained

**Detection Logic Validation:**
1. Spot check: Run 5 sample cases, verify layer-by-layer behavior
2. Edge cases: Test valid cases pass all layers
3. Negative control: Schema violations caught at Layer 1 only

### 8.2 Internal Validity

**Threat:** Test cases artificially favor three-layer approach
- **Mitigation:** Adversarial construction targets realistic violations (keywords, cross-field logic)
- **Justification:** Same test cases used for both conditions (controlled comparison)

**Threat:** Ground-truth labels biased
- **Mitigation:** Manual review by independent verifier
- **Fallback:** Run detected cases through human inspection

### 8.3 External Validity

**Threat:** 30 test cases insufficient for generalization
- **Mitigation:** Test cases cover all 4 constraint types, multiple violation patterns
- **Justification:** Proof-of-concept (PoC) threshold, not production evaluation

**Threat:** Placeholder Phase 2A outputs unrealistic
- **Mitigation:** Test cases mirror real Phase 2A schema structure
- **Future work:** h-m3 validates on 100-case corpus with realistic content

---

## 9. Expected Outcomes

### 9.1 Quantitative Results

**Detection Rates:**
- Schema-only: 40% (10/25 violations)
- Three-layer: 100% (25/25 violations)
- **Gap:** 60 percentage points (exceeds 40pp threshold)

**Layer-Specific Performance:**
- Schema layer: 100% on structural violations (10/10)
- Pattern layer: 100% on keyword violations (10/10)
- Contract layer: 100% on compositional violations (5/5)

**False Positives:** 0% (all 5 valid cases pass)

### 9.2 Qualitative Insights

**Why Three Layers Succeed:**
1. **Complementary detection mechanisms:** Schema catches structure, pattern catches semantics, contracts catch composition
2. **Fail-fast architecture:** Early layers filter out simple violations, reducing load on expensive contract checks
3. **Explicit enforcement:** Each layer enforces constraints schema alone cannot express

**Why Schema-Only Fails:**
- Cannot express keyword patterns (C1/C2)
- Cannot express cross-field logic (C3)
- Cannot reference external state (C4)

### 9.3 Implications for Main Hypothesis

**h-m2 validates causal chain step 2:**
- Multi-layer validation detects violations schema-only misses ✓
- Pattern + contract layers are complementary (not redundant) ✓

**Prerequisite for h-m3:**
- Detection mechanism proven → next step tests if detection reduces downstream failures
- Expected: If h-m2 passes → h-m3 likely passes (early detection prevents late failures)

---

## 10. Risks and Mitigation

### 10.1 Technical Risks

**Risk R1:** Pattern layer detection <80%
- **Likelihood:** LOW (keyword regex is deterministic)
- **Impact:** MEDIUM (secondary criterion fails, but primary can still pass)
- **Mitigation:** Add synonym expansion for C1/C2 keywords if needed

**Risk R2:** Test suite imbalanced (too many easy cases)
- **Likelihood:** MEDIUM (manual test case generation)
- **Impact:** HIGH (inflates detection rate, false confidence)
- **Mitigation:** Adversarial review — ask "what edge case would fool this layer?"

### 10.2 Experimental Risks

**Risk R3:** Ground-truth labels incorrect
- **Likelihood:** LOW (automated generation with manual review)
- **Impact:** CRITICAL (wrong labels → wrong detection rates)
- **Mitigation:** Independent verification step, spot-check with human inspection

**Risk R4:** False positives on valid cases
- **Likelihood:** LOW (h-m1 tested valid inputs)
- **Impact:** MEDIUM (undermines trust in validation framework)
- **Mitigation:** Validate all 5 valid cases pass before running full experiment

---

## 11. Timeline and Deliverables

### 11.1 Timeline

**Total Duration:** 1 day (8 hours)

**Breakdown:**
- Test suite extension: 2 hours
- Experiment implementation: 3 hours
- Execution and analysis: 2 hours
- Documentation: 1 hour

### 11.2 Deliverables

**Phase 4 Implementation:**
1. `tests/h_m2/test_cases_h_m2.yaml` — 30-case adversarial test suite
2. `experiments/h_m2_multilayer_validation.py` — Detection rate experiment
3. `experiments/utils/h_m2_validator.py` — Layer-specific detection tracker

**Phase 4 Validation:**
4. `docs/youra_research/h-m2/04_validation.md` — Results report with:
   - Detection rate table (schema-only vs three-layer)
   - Per-layer analysis (schema/pattern/contract)
   - Per-constraint analysis (C1/C2/C3/C4)
   - Gate verdict (PASS/PARTIAL/FAIL)

**Artifacts:**
5. Detection rate plots (bar chart: schema-only vs three-layer)
6. Confusion matrix (expected vs actual detection per layer)

---

## 12. Next Steps

### 12.1 Immediate Actions (Phase 3)

1. **Implementation Planning:**
   - Generate PRD with task breakdown
   - Create Archon project with implementation tasks
   - Estimate token budget (expected: Tier 0, <10k tokens)

2. **Dataset Preparation:**
   - Extend test suite to 30 cases
   - Manual review ground-truth labels
   - Validate existing validation infrastructure (h-m1 code)

### 12.2 Downstream Hypotheses

**If h-m2 PASSES:**
- Proceed to h-m3: Early detection prevents downstream failures
- Use same three-layer validation framework
- Scale test corpus to 100 placeholder hypotheses

**If h-m2 FAILS (<40pp gap):**
- EXPLORE: Diagnose which layer(s) underperforming
- Root cause: Pattern layer missing synonyms? Contract layer incomplete?
- PIVOT: Refine patterns/contracts, re-run experiment

---

## 13. Appendices

### 13.1 Constraint Definitions (from h-m1)

**C1 - No Synthetic Data:**
- Forbidden keywords: "synthetic", "simulated", "generated", "artificial"
- Field: `dataset_name`
- Enforcement: Pattern layer (`@field_validator`)

**C2 - No Human Evaluation:**
- Forbidden keywords: "human", "manual", "annotator", "rater"
- Field: `evaluation_method`
- Enforcement: Pattern layer (`@field_validator`)

**C3 - Standard Dataset Membership:**
- Logic: `IF dataset_type == "standard" THEN dataset_name ∈ STANDARD_DATASETS`
- Whitelist: `["MNIST", "CIFAR-10", "CIFAR-100", "ImageNet", "GLUE", ...]`
- Enforcement: Contract layer (`@ensure`)

**C4 - No New Benchmarks:**
- Logic: `IF "benchmark" in evaluation_method THEN mentioned_benchmark ∈ EXISTING_BENCHMARKS`
- Whitelist: `["GLUE", "SuperGLUE", "SQuAD", "ImageNet", ...]`
- Enforcement: Contract layer (method `_validate_no_new_benchmarks()`)

### 13.2 Test Case Example

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
  # ... other required fields
expected_detection:
  schema: true      # Structural validation passes
  pattern: true     # No keyword violations
  contract: false   # Cross-field logic fails
```

### 13.3 References

**Prior Work:**
- h-e1: Contract framework existence (VALIDATED)
- h-m1: Contract specification forces checking (VALIDATED)

**Implementation:**
- `src/validation/*` — Existing three-layer validation infrastructure
- `tests/phase_boundary_validation/` — Existing test suite generator

**Next Hypothesis:**
- h-m3: Early detection prevents downstream failures (dependent on h-m2)

---

**Document Status:** Complete  
**Experiment Level:** 1.5 (Detailed Specification)  
**Ready for Phase 3:** Yes  
**Next Phase:** Implementation Planning (PRD generation)
