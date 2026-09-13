# Product Requirements Document: Early Detection Cost Reduction (h-m3)

**Hypothesis:** Early detection of constraint violations at phase boundaries prevents expensive downstream failures at Phase 4/5 implementation stages.

**Date:** 2026-08-20  
**Version:** 1.0  
**Type:** MECHANISM  
**Gate:** MUST_WORK  
**Tier:** 0 (validation experiment)

---

## 1. Overview

### 1.1 Problem Statement

h-m2 demonstrated that three-layer validation detects 88% of constraint violations versus 40% for schema-only validation at phase boundaries. However, the **causal impact** of early detection on downstream Phase 4/5 implementation failures remains untested. If constraint violations escape boundary detection, they propagate through the pipeline and fail at expensive later stages (Phase 4 coding, Phase 5 baseline adaptation).

This experiment measures whether early boundary detection (Phase 2→3→4) prevents downstream failures by ≥80%, validating the hypothesis that contract-based validation provides ROI beyond detection accuracy.

### 1.2 Success Criteria

**Primary (MUST_WORK gate):**
- Failure reduction ≥80%: `(Failure_Rate_SchemaOnly - Failure_Rate_Contract) / Failure_Rate_SchemaOnly × 100% ≥ 80%`

**Secondary:**
- Contract boundary detection ≥90%
- Zero false positives on valid hypotheses (n=80)
- All failures trace to injected violations (no infrastructure attribution errors)

**Gate decision:**
- ≥80% reduction + ≥90% detection → **PASS**
- 40-79% reduction → **PIVOT** (refine contracts)
- <20% reduction → **ROUTE_TO_0** (hypothesis false)

---

## 2. Functional Requirements

### 2.1 Placeholder Hypothesis Corpus Generation

**FR-1.1 Corpus Structure**
- Generate 100 placeholder hypotheses in `tests/placeholder_hypotheses/corpus_100.json`
- Each entry contains:
  - `hypothesis_id`: Unique identifier (h-test-001 to h-test-100)
  - `statement`: Hypothesis text (placeholder)
  - `phase2_output`: Verification plan structure (minimal Phase 2 fields)
  - `injected_violation`: Ground truth violation metadata

**FR-1.2 Violation Composition**
- 80 valid hypotheses (no violations)
- 20 hypotheses with injected violations:
  - 5 C1 violations (synthetic dataset requirement)
  - 5 C2 violations (human evaluation requirement)
  - 5 C3 violations (non-standard dataset reference)
  - 5 C4 violations (new benchmark creation)

**FR-1.3 Violation Injection**
Violations embedded in Phase 2 output structure:
- **C1:** `phase2_output.dataset.type = "synthetic"`
- **C2:** `phase2_output.evaluation.requires_human = true`
- **C3:** `phase2_output.dataset.name = "custom-imagenet-variant"` (not in standard registry)
- **C4:** `phase2_output.experiment.creates_benchmark = true`

**FR-1.4 Ground Truth Labels**
Each violation includes:
- `constraint`: One of [C1, C2, C3, C4, none]
- `location`: Where injected [phase2, phase3]
- `ground_truth`: Expected outcome [violates, valid]

### 2.2 Pipeline Execution Harness

**FR-2.1 Condition A: Schema-only Validation**
- Execute Phase 2→3→4→5 pipeline with schema validation only
- Apply validation at boundaries:
  - Phase 2→3: Validate hypothesis structure schema
  - Phase 3→4: Validate PRD/Architecture schema
  - Phase 4→5: Validate code artifact schema
- Log all validation results to `results/h_m3/condition_a_log.json`

**FR-2.2 Condition B: Contract-based Validation**
- Execute same pipeline with three-layer validation (schema + pattern + contract)
- Apply h-m2 validated contract validators at same boundaries
- Log all validation results to `results/h_m3/condition_b_log.json`

**FR-2.3 Pipeline Stages**
Simulated pipeline execution:
- **Phase 2:** Read `phase2_output` from corpus entry
- **Phase 3:** Generate PRD/Architecture (minimal placeholder structure)
- **Phase 4:** Generate code artifacts (placeholder implementation)
- **Phase 5:** Execute baseline comparison (placeholder baseline adapter)

**FR-2.4 Failure Detection**
Track Phase 4/5 failures:
- **Phase 4 failure:** Implementation blocked due to constraint violation (cannot generate code for synthetic data, human eval)
- **Phase 5 failure:** Baseline comparison blocked (non-standard dataset, new benchmark incompatible)
- Write failure trace to `results/h_m3/phase45_failures/<hypothesis_id>.json`

### 2.3 Failure Classification

**FR-3.1 Failure Attribution**
For each Phase 4/5 failure:
- Trace failure to injected violation in corpus entry
- Classify constraint type (C1, C2, C3, C4)
- Verify failure is NOT from infrastructure bugs

**FR-3.2 Exclusion Criteria**
Do NOT count as constraint failures:
- Pipeline execution errors (file I/O, JSON parsing)
- Timeout errors
- Dependency errors
- Failures on valid hypotheses (n=80) → these are false positives

**FR-3.3 Failure Log Format**
```json
{
  "hypothesis_id": "h-test-015",
  "phase": 4,
  "constraint_violated": "C1",
  "failure_message": "Cannot generate code for synthetic dataset requirement",
  "ground_truth": "violates",
  "detected_at_boundary": false,
  "trace": {...}
}
```

### 2.4 Metrics Calculation

**FR-4.1 Failure Rate Calculation**
```
Failure_Rate_A = (Phase4_failures_A + Phase5_failures_A) / 20
Failure_Rate_B = (Phase4_failures_B + Phase5_failures_B) / 20
```

**FR-4.2 Reduction Calculation**
```
Reduction = (Failure_Rate_A - Failure_Rate_B) / Failure_Rate_A × 100%
```

**FR-4.3 Boundary Detection Rate**
```
Detection_Rate = Violations_caught_at_boundary / 20 × 100%
```

**FR-4.4 False Positive Rate**
```
FP_Rate = Valid_hypotheses_rejected / 80 × 100%
```

### 2.5 Result Analysis

**FR-5.1 Per-Constraint Breakdown**
Report metrics for each constraint type:
- C1, C2, C3, C4 detection rates
- C1, C2, C3, C4 failure rates by condition

**FR-5.2 Correlation Analysis**
- Boundary detection vs downstream failure correlation
- Identify which violations escape detection most frequently

**FR-5.3 Gate Verdict**
Apply decision matrix:
| Failure Reduction | Boundary Detection | Action |
|------------------|-------------------|--------|
| ≥80% | ≥90% | PASS |
| 40-79% | ≥90% | PIVOT |
| 40-79% | <90% | PIVOT |
| <20% | any | ROUTE_TO_0 |

---

## 3. Non-Functional Requirements

### 3.1 Performance
- Corpus generation: <5 minutes
- Per-condition pipeline execution: <30 minutes (100 hypotheses)
- Total experiment runtime: <2 hours

### 3.2 Reproducibility
- Deterministic corpus generation (fixed random seed)
- Logged execution traces for all pipeline stages
- Ground truth labels for all test cases

### 3.3 Maintainability
- Modular condition harnesses (swap validation layers via config)
- Reusable failure tracker across conditions
- Clear separation of corpus generation vs execution

---

## 4. System Architecture

### 4.1 Component Diagram

```
┌────────────────────────────────────────────────────────────┐
│ Corpus Generator                                           │
│  - generate_corpus.py                                      │
│  - Output: corpus_100.json                                 │
└────────────────┬───────────────────────────────────────────┘
                 │
                 v
┌────────────────────────────────────────────────────────────┐
│ Pipeline Runner                                            │
│  - pipeline_runner.py                                      │
│  - Executes Phase 2→3→4→5 per condition                   │
└────────────┬───────────────────────────┬───────────────────┘
             │                           │
             v                           v
┌────────────────────────┐   ┌──────────────────────────────┐
│ Condition A Harness    │   │ Condition B Harness          │
│  - condition_a.py      │   │  - condition_b.py            │
│  - Schema-only valid.  │   │  - Three-layer valid.        │
└────────────┬───────────┘   └─────────────┬────────────────┘
             │                             │
             v                             v
┌────────────────────────────────────────────────────────────┐
│ Failure Tracker                                            │
│  - failure_tracker.py                                      │
│  - Log Phase 4/5 failures                                  │
│  - Output: phase45_failures/*.json                         │
└────────────────┬───────────────────────────────────────────┘
                 │
                 v
┌────────────────────────────────────────────────────────────┐
│ Analysis Module                                            │
│  - analyze_results.py                                      │
│  - Calculate reduction metrics                             │
│  - Generate 04_validation.md                               │
└────────────────────────────────────────────────────────────┘
```

### 4.2 Data Flow

1. **Corpus Generation:**
   - `generate_corpus.py` → `corpus_100.json`

2. **Condition A Execution:**
   - `condition_a.py` reads corpus → runs pipeline with schema validation → logs results to `condition_a_log.json` → failures to `phase45_failures/cond_a_*.json`

3. **Condition B Execution:**
   - `condition_b.py` reads corpus → runs pipeline with contract validation → logs results to `condition_b_log.json` → failures to `phase45_failures/cond_b_*.json`

4. **Analysis:**
   - `analyze_results.py` reads both logs + failure traces → calculates metrics → writes `04_validation.md`

---

## 5. Implementation Phases

### Phase 1: Corpus Generation (1 day)
- Implement `generate_corpus.py`
- Generate 100 placeholder hypotheses with violations
- Validate corpus structure and ground truth labels

### Phase 2: Pipeline Infrastructure (1 day)
- Implement `pipeline_runner.py` (Phase 2→3→4→5 simulation)
- Implement `failure_tracker.py`
- Validate pipeline execution on single test case

### Phase 3: Condition A (2 days)
- Implement `condition_a.py` (schema-only validation)
- Execute on full corpus (100 hypotheses)
- Log failures and boundary validation results

### Phase 4: Condition B (2 days)
- Implement `condition_b.py` (contract-based validation)
- Execute on full corpus (100 hypotheses)
- Log failures and boundary validation results

### Phase 5: Analysis (1 day)
- Implement `analyze_results.py`
- Calculate failure reduction, detection rates
- Generate `04_validation.md` with gate verdict

---

## 6. Dependencies

### 6.1 External Dependencies
- h-m2 validation framework (`src/validation/`)
- Existing Phase 2-5 pipeline infrastructure (minimal simulation)

### 6.2 Data Dependencies
- None (generates own test corpus)

### 6.3 Compute Dependencies
- Standard workstation (no GPU required)
- <2GB memory for corpus + logs

---

## 7. Risks & Mitigation

### Risk R2: Incomplete Contract Specification
**Manifestation:** Violations pass boundary validation but fail at Phase 4/5  
**Mitigation:**
- Track which violations escape detection
- If >5 violations escape (25%): PIVOT to enhanced contracts
- Mutation testing to find contract gaps

### Risk R5: Validation Overhead Cost
**Manifestation:** Contract validation cost > failure recovery cost  
**Mitigation:**
- Measure validation execution time per boundary
- Measure Phase 4/5 debugging time for failures
- Document trade-off if overhead >2× recovery cost

### Risk: False Attribution
**Manifestation:** Phase 4/5 failures from infrastructure bugs counted as constraint failures  
**Mitigation:**
- Manual review of all Phase 4/5 failures
- Strict classification protocol (FR-3.2)
- Only count failures with constraint violation trace

---

## 8. Deliverables

1. **Corpus:** `tests/placeholder_hypotheses/corpus_100.json`
2. **Execution logs:**
   - `results/h_m3/condition_a_log.json`
   - `results/h_m3/condition_b_log.json`
3. **Failure traces:** `results/h_m3/phase45_failures/` (per-hypothesis failure logs)
4. **Validation report:** `04_validation.md` with:
   - Failure reduction percentage
   - Per-constraint breakdown
   - Gate verdict (PASS/PIVOT/ROUTE_TO_0)

---

## 9. Acceptance Criteria

**Must have:**
- 100 placeholder hypotheses with correct violation composition
- Both conditions execute on full corpus
- All Phase 4/5 failures logged with constraint attribution
- Failure reduction metric calculated
- Gate verdict determined

**Should have:**
- Per-constraint breakdown metrics
- Boundary detection vs failure correlation analysis
- Validation overhead measurements

**Nice to have:**
- Mutation testing for contract gaps
- Interactive failure trace viewer

---

## 10. Future Extensions

If hypothesis passes (PASS):
- Integrate contract validation into production pipeline
- Extend to real Phase 2 outputs (beyond placeholders)
- Optimize validation performance for large-scale runs

If hypothesis pivots (PIVOT):
- Iterative contract refinement based on escaped violations
- Enhanced pattern layer for subtle constraint violations

---

**Status:** Ready for Phase 3 implementation  
**Next Step:** Architecture design (03_architecture.md)
