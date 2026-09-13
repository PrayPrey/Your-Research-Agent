# Experiment Brief: Early Detection Cost Reduction (h-m3)

**Hypothesis:** Early detection of constraint violations at phase boundaries prevents expensive downstream failures at Phase 4/5 implementation stages.

**Date:** 2026-08-20  
**Type:** MECHANISM  
**Gate:** MUST_WORK  
**Prerequisites:** h-m2 (completed)

---

## 1. Research Question

Does catching constraint violations early at phase boundaries (Phase 2→3→4) via contract validation reduce downstream Phase 4/5 implementation failures by ≥80% compared to schema-only validation?

### Key Variables
- **Independent:** Validation timing (early boundary detection vs late Phase 4/5 detection)
- **Dependent:** Phase 4/5 failure rate from constraint violations
- **Controlled:** Placeholder hypothesis corpus (100 test cases), violation injection rate (20%)

---

## 2. Experimental Design

### 2.1 Dataset

**Type:** custom  
**Name:** Placeholder Hypothesis Corpus (100 test cases)  
**Source:** Programmatically generated test cases with embedded constraint violations  
**Path:** `tests/placeholder_hypotheses/corpus_100.json`

**Structure:**
```json
{
  "hypothesis_id": "h-test-001",
  "statement": "...",
  "phase2_output": {...},
  "injected_violation": {
    "constraint": "C1|C2|C3|C4|none",
    "location": "phase2|phase3",
    "ground_truth": "violates|valid"
  }
}
```

**Composition:**
- 80 valid hypotheses (no violations)
- 20 hypotheses with injected violations:
  - 5 C1 violations (synthetic data)
  - 5 C2 violations (human eval)
  - 5 C3 violations (non-standard dataset)
  - 5 C4 violations (new benchmark)

**Rationale:** Controlled corpus with known ground truth violations enables precise measurement of detection vs downstream failure rates. 20% violation rate reflects realistic Phase 2 output error rate from validation plan (Section 1.6).

**No synthetic data policy compliance:** This dataset contains placeholder research hypotheses (structured text), NOT synthetic training data for ML models. Acceptable per policy.

### 2.2 Baseline Methods

**Condition A: Schema-only validation**
- Validates typed schemas at phase boundaries (Phase 2→3→4)
- Catches structural violations only
- Expected detection rate: ~40% (from h-m2 results)

**Condition B: Contract-based validation**
- Three-layer validation (schema + pattern + contract)
- Validates at same boundaries as Condition A
- Expected detection rate: ~88% (from h-m2 results)

### 2.3 Evaluation Protocol

**Pipeline Execution:**
1. Generate 100 placeholder hypotheses (80 valid + 20 with violations)
2. Run Condition A (schema-only):
   - Execute through Phase 2→3→4→5 pipeline
   - Log boundary validation results
   - Count Phase 4/5 failures from constraint violations
3. Run Condition B (contract-based):
   - Same pipeline execution
   - Log three-layer validation results
   - Count Phase 4/5 failures from constraint violations
4. Calculate failure reduction

**Phase 4/5 Failure Definition:**
- Phase 4 coding failure: Implementation cannot proceed due to constraint violation
- Phase 5 baseline comparison failure: Baseline adaptation blocked by constraint mismatch
- Examples: Synthetic dataset error, missing standard benchmark, human eval requirement

**Measurement:**
```
Failure_Rate_A = (Phase4_failures_A + Phase5_failures_A) / 20
Failure_Rate_B = (Phase4_failures_B + Phase5_failures_B) / 20
Reduction = (Failure_Rate_A - Failure_Rate_B) / Failure_Rate_A × 100%
```

---

## 3. Success Criteria

### Primary (MUST_WORK gate)
**Criterion:** Failure rate reduction ≥80%

**Rationale:** Main hypothesis prediction P1 from verification plan. Validates that early detection actually prevents downstream failures.

**Threshold justification:**
- 80% reduction = strong causal evidence
- Below 80% but above 40% → PIVOT (refine contracts)
- Below 20% → ROUTE_TO_0 (hypothesis false)

### Secondary
1. **Contract detection rate ≥90%:** Validates that contract validation catches violations at boundaries
2. **No false positives:** Valid hypotheses (n=80) must pass all validation layers
3. **Failure attribution accuracy:** All counted failures must trace to injected violations (not infrastructure bugs)

---

## 4. Implementation Notes

### 4.1 Experiment Code Structure

```
experiments/h_m3_early_detection/
├── config.py              # Experiment parameters
├── generate_corpus.py     # Create 100 placeholder hypotheses
├── pipeline_runner.py     # Execute Phase 2→3→4→5 pipeline
├── condition_a.py         # Schema-only validation harness
├── condition_b.py         # Contract-based validation harness
├── failure_tracker.py     # Log and classify Phase 4/5 failures
├── analyze_results.py     # Calculate reduction metrics
└── main.py                # Orchestration
```

### 4.2 Validation Checkpoints

**Phase 2→3 boundary:**
- Input: Phase 2 verification plan output
- Validation: hypothesis structure, constraint patterns
- Failure mode: Invalid hypothesis propagates to Phase 3

**Phase 3→4 boundary:**
- Input: Phase 3 implementation plan (PRD/Architecture)
- Validation: dataset/model specifications, Archon task consistency
- Failure mode: Infeasible implementation plan reaches Phase 4

**Phase 4→5 boundary:**
- Input: Phase 4 validated code
- Validation: executable artifacts, baseline compatibility
- Failure mode: Code runs but violates constraints for baseline comparison

### 4.3 Failure Injection Strategy

Violations inserted at Phase 2 output (verification plan stage):
- **C1 (synthetic data):** `dataset.type = "synthetic"` in verification plan
- **C2 (human eval):** `evaluation.requires_human = true` in verification plan
- **C3 (non-standard dataset):** `dataset.name = "custom-imagenet-variant"` (not in standard registry)
- **C4 (new benchmark):** `experiment.creates_benchmark = true` in verification plan

Each violation class gets 5 test cases with varying severity/obviousness to test detection robustness.

---

## 5. Expected Outcomes

### 5.1 Predicted Results

| Metric | Condition A (Schema) | Condition B (Contract) |
|--------|---------------------|------------------------|
| Boundary detection rate | 40% (8/20) | 88% (18/20) |
| Phase 4/5 failure rate | 60% (12/20) | 10% (2/20) |
| Failure reduction | - | 83.3% |

**Reasoning:**
- h-m2 showed 88% vs 40% detection gap
- Violations NOT caught at boundary propagate to Phase 4/5
- Schema-only misses 12 violations → 12 Phase 4/5 failures
- Contract-based misses 2 violations → 2 Phase 4/5 failures
- Reduction: (12-2)/12 = 83.3% (exceeds 80% threshold)

### 5.2 Alternative Outcomes

**Outcome 1: Partial success (40-79% reduction)**
- Some violations caught early but still significant Phase 4/5 failures
- **Action:** PIVOT - analyze which constraint types still fail, refine contracts

**Outcome 2: Failure (<20% reduction)**
- Early detection does not prevent downstream failures
- **Possible causes:**
  - Contract specification incomplete (Risk R2)
  - Violations mutate during phase transitions
  - Phase 4/5 failures from sources other than constraint violations
- **Action:** ROUTE_TO_0 - hypothesis false, early detection insufficient

**Outcome 3: Over-performance (>95% reduction)**
- Nearly all violations caught early
- **Interpretation:** Strong causal evidence, contracts highly effective

---

## 6. Risk Mitigation

### Risk R2: Incomplete Contract Specification
**Manifestation:** Violations pass boundary validation but fail at Phase 4/5

**Detection:**
- Track which specific violations escape detection
- Analyze contract coverage per constraint type

**Mitigation:**
- Mutation testing: adversarially modify violations to find contract gaps
- Iterative contract refinement based on escaped violations
- If >5 violations escape: PIVOT to enhanced contract layer

### Risk R5: Validation Overhead Cost
**Manifestation:** Contract validation cost > failure recovery cost

**Detection:**
- Measure validation execution time per boundary
- Measure Phase 4/5 debugging time for failures

**Mitigation:**
- Profile validation hot paths
- If overhead >2× failure recovery cost: document as limitation
- Trade-off analysis: early detection time vs late-stage debugging time

### Risk: False Attribution
**Manifestation:** Phase 4/5 failures from infrastructure bugs counted as constraint failures

**Detection:**
- Manual review of all Phase 4/5 failures
- Verify each failure traces to an injected violation

**Mitigation:**
- Strict failure classification protocol
- Only count failures that directly reference constraint violations
- Document and exclude infrastructure failures from metrics

---

## 7. Timeline & Resources

**Duration:** 1 week

**Phases:**
1. Corpus generation (1 day)
2. Condition A execution (2 days)
3. Condition B execution (2 days)
4. Failure analysis and metrics (1 day)
5. Report generation (1 day)

**Computational Resources:**
- Minimal (placeholder hypotheses, no model training)
- Pipeline execution on standard workstation
- No GPU required

**Dependencies:**
- Existing validation framework (`src/validation/`)
- h-m2 three-layer validation code
- Phase 2-5 pipeline infrastructure

---

## 8. Deliverables

1. **Corpus:** `tests/placeholder_hypotheses/corpus_100.json`
2. **Execution logs:**
   - `results/h_m3/condition_a_log.json`
   - `results/h_m3/condition_b_log.json`
3. **Failure traces:** `results/h_m3/phase45_failures/` (one file per failure)
4. **Analysis report:** `04_validation.md` with:
   - Failure reduction percentage
   - Per-constraint breakdown
   - Boundary detection vs downstream failure correlation
   - Gate verdict (PASS/PIVOT/ROUTE_TO_0)

---

## 9. Gate Decision Matrix

| Failure Reduction | Boundary Detection | Action |
|------------------|-------------------|--------|
| ≥80% | ≥90% | **PASS** - hypothesis validated |
| 40-79% | ≥90% | **PIVOT** - refine contracts, some violations still escape |
| 40-79% | <90% | **PIVOT** - improve detection at boundaries first |
| <20% | any | **ROUTE_TO_0** - early detection insufficient |

**Next Phase:** If PASS → Phase 5 baseline comparison (deferred to main hypothesis level per verification plan)

---

## 10. References

### Research Evidence
1. **Fail-fast principle:** Fowler (IEEE Software) - assertions reduce debugging cost by catching errors at source
2. **Phased validation:** Caskey Engineering - batch validation within phases, gate between phases
3. **Early detection cost:** Jenkins/Harness documentation - early pipeline failures prevent downstream resource waste
4. **Contract validation:** C++26, Boost.Contract, .NET Code Contracts - precondition/postcondition enforcement

### Codebase Evidence
1. **h-m2 results:** Three-layer validation achieves 88% detection vs 40% schema-only (48pp gap)
2. **Validation framework:** `src/validation/` implements schema, pattern, contract layers
3. **Phase boundary definitions:** `.claude/hooks/run_phase*.py` define transition points

### Dataset Precedent
1. **Placeholder approach:** Verification plan Section 1.5 Assumption A4 - minimal fidelity placeholders satisfy interface contracts
2. **Controlled corpus:** Similar to mutation testing in software engineering - inject known defects to measure detection

---

**Status:** Complete  
**Next Step:** Phase 3 implementation planning
