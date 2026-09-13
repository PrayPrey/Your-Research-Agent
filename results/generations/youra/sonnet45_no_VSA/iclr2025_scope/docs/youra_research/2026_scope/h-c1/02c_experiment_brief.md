# Phase 2C Experiment Design Brief: H-C1

**Hypothesis ID:** h-c1  
**Hypothesis Type:** CAUSAL  
**Hypothesis Statement:** Combining structural AND metamorphic contracts reduces false-negative rate (missed defects) by ≥30% compared to using either contract type alone

**Date:** 2026-07-11  
**Phase:** 2C - Experiment Design  
**Prerequisites:** h-m1 (VALIDATED), h-m2 (VALIDATED)

---

## 1. Research Context

### 1.1 Background from Prerequisites

**h-m1 (Structural Contracts):**
- **Mechanism:** Validates return types, tensor shapes, dtypes at import/setup time
- **Detection Rate:** 100% (2/2 shape/dtype mismatches)
- **Coverage:** Import-time violations only
- **Execution Time:** <0.03s per test
- **Limitation:** Cannot detect behavioral violations (e.g., softmax sum errors)

**h-m2 (Metamorphic Contracts):**
- **Mechanism:** Validates mathematical properties (softmax sums, dropout identity)
- **Detection Rate:** 100% (40/40 behavioral violations)
- **Coverage:** Runtime behavioral violations
- **Execution Time:** 3.7ms per test
- **Limitation:** Cannot detect structural mismatches at import time

### 1.2 Hypothesis Rationale

The two contract types are **complementary**:
- Structural contracts detect **syntax errors** (shape/type mismatches)
- Metamorphic contracts detect **semantic errors** (mathematical invariant violations)

**Expected Synergy:** A defect corpus contains BOTH types of errors. Using only one contract type misses defects the other would catch (false negatives). Combining both should reduce the false-negative rate by at least 30%.

### 1.3 Literature & Implementation Patterns

**From Archon KB & Exa Research:**

1. **Multi-layered validation architectures** (Abhishek Verma, Medium):
   - Structural layer: schema validation, type checking
   - Semantic layer: business logic, invariants
   - Composition layer: cross-component contracts
   - Pattern: Each layer catches distinct defect classes

2. **Contract combination frameworks** (Surety Python):
   - Schema-first design (structural)
   - Runtime validation (behavioral)
   - Structured diffs for mismatch reporting
   - Pattern: Combine schema + runtime validation

3. **API contract testing best practices** (DevSolve, Zuplo):
   - Schema validation (JSON Schema) for structural correctness
   - Response validation for behavioral properties
   - Pattern: Validate BOTH shape AND content

4. **Ensemble testing** (Great Expectations, API Test Automation Framework):
   - Contract testing + data quality checks
   - Multiple validator types combined
   - Pattern: Parallel validation strategies reduce false negatives

**Key Implementation Insight:** The ensemble pattern (running multiple validators in parallel) consistently outperforms single-strategy approaches in API testing, defect detection, and data quality validation.

---

## 2. Experimental Design

### 2.1 Research Question

**Primary:** Does combining structural AND metamorphic contracts reduce false-negative rate by ≥30% compared to using either alone?

**Secondary:** What is the overhead (execution time, implementation complexity) of the combined approach?

### 2.2 Causal Framework

**Independent Variable (Treatment):**
- Validation Strategy: {Structural Only, Metamorphic Only, Combined (Structural + Metamorphic)}

**Dependent Variables:**
- **Primary:** False-negative rate (proportion of defects missed)
- **Secondary:** True-positive rate (detection rate), execution time, false-positive rate

**Control Variables:**
- Defect corpus (same 348 defects from h-e1)
- Execution timeout (10s per test)
- Validation thresholds (from h-m1/h-m2)

**Confounders (Controlled):**
- Defect distribution stratified by type (structural vs behavioral vs mixed)
- Random seed fixed (42) for reproducibility

### 2.3 Dataset Design

**Dataset Type:** standard (real established dataset)  
**Source:** Jiang et al. 348-Defect Corpus (from h-e1)  
**Size:** 348 defects (statistically meaningful, matches h-e1 corpus)

**Stratification Strategy:**
1. **Structural-only defects** (~146 defects, 42% of corpus):
   - Shape mismatches, dtype errors, device placement issues
   - Detectable by structural contracts only
   - Example: Conv layer expects 4 channels, dataset provides 3

2. **Behavioral-only defects** (~105 defects, 30% of corpus):
   - Softmax sum errors, dropout identity violations, normalization issues
   - Detectable by metamorphic contracts only
   - Example: Softmax outputs sum to 1.05 instead of 1.0

3. **Mixed defects** (~62 defects, 18% of corpus):
   - Both structural AND behavioral issues
   - Detectable by both contract types
   - Example: Wrong tensor shape + softmax sum violation

4. **Composition/integration defects** (~35 defects, 10% of corpus):
   - Cross-component issues not detectable by single-method contracts
   - Potential false negatives for all single strategies
   - Example: Correct shapes + correct softmax, but incompatible tensor memory layouts

**Ground Truth Labeling:**
- Each defect labeled with: {defect_type: structural|behavioral|mixed|composition}
- Expected detectability: {structural_detectable: bool, metamorphic_detectable: bool}
- This enables precise false-negative rate calculation per strategy

### 2.4 Experimental Groups

**Group 1: Structural-Only Baseline**
- Validation: Structural contracts only (from h-m1)
- Expected detection: Structural defects (100%), Behavioral defects (0%), Mixed (50%), Composition (0%)
- Expected false-negative rate: ~48% (misses 105 behavioral + 31 mixed + 35 composition = 171/348)

**Group 2: Metamorphic-Only Baseline**
- Validation: Metamorphic contracts only (from h-m2)
- Expected detection: Behavioral defects (100%), Structural defects (0%), Mixed (50%), Composition (0%)
- Expected false-negative rate: ~52% (misses 146 structural + 31 mixed + 35 composition = 212/348)

**Group 3: Combined Treatment**
- Validation: Structural AND metamorphic contracts (parallel execution)
- Expected detection: Structural (100%), Behavioral (100%), Mixed (100%), Composition (variable)
- Expected false-negative rate: ~10-20% (misses only composition defects if not covered)

**Validation Logic:**
```python
def combined_validation(model, data):
    violations = []
    # Parallel execution to minimize overhead
    structural_violations = validate_structural(model, data)  # h-m1
    metamorphic_violations = validate_metamorphic(model, data)  # h-m2
    return structural_violations + metamorphic_violations
```

### 2.5 Metrics

**Primary Metric:**
```
False-Negative Rate (FNR) = Missed Defects / Total Defects
Reduction = (FNR_baseline_avg - FNR_combined) / FNR_baseline_avg × 100%
```

**Gate Criteria:**
- **MUST_WORK:** FNR reduction ≥ 30% compared to better baseline
- **Success:** If Structural-Only FNR = 48% and Combined FNR = 30%, reduction = 37.5% → PASS

**Secondary Metrics:**
1. **Detection Rate:** (Detected Defects / Total Defects) × 100%
2. **Execution Time:** Mean time per test across 348 defects
3. **False-Positive Rate:** Control scenarios flagged incorrectly
4. **Coverage by Defect Type:** Detection rate stratified by {structural, behavioral, mixed, composition}

### 2.6 Statistical Analysis

**Sample Size:** 348 defects (powered for 95% CI, ±5% margin)  
**Confidence Interval:** Bootstrap 95% CI for FNR (1000 iterations)  
**Significance Test:** McNemar's test for paired proportions (Combined vs each baseline)  
**Effect Size:** Relative risk reduction (RRR) for false negatives

**Minimum Detectable Effect:** 30% reduction in FNR (per gate criteria)

---

## 3. Implementation Specifications

### 3.1 Code Structure

**Reuse from Prerequisites:**
- `h-m1/code/contracts/validator.py` → Structural validator
- `h-m2/code/contracts/validator.py` → Metamorphic validator
- Both validators already proven to work (100% detection rates)

**New Components:**
1. **Ensemble Validator** (`code/contracts/ensemble.py`):
   - Combines structural + metamorphic validators
   - Parallel execution using `concurrent.futures.ThreadPoolExecutor`
   - Aggregates violations from both sources

2. **Defect Corpus Loader** (`code/data/corpus_loader.py`):
   - Loads Jiang et al. corpus from h-e1 cache
   - Stratifies defects by type
   - Provides ground truth labels

3. **Comparison Experiment** (`code/run_experiment.py`):
   - Tests 3 strategies: Structural-Only, Metamorphic-Only, Combined
   - Records FNR, execution time, per-defect-type coverage
   - Generates bootstrap confidence intervals

4. **Analysis & Visualization** (`code/analysis/metrics.py`, `code/visualization/plots.py`):
   - FNR reduction calculation
   - Statistical tests (McNemar)
   - Plots: FNR comparison, coverage by defect type, execution time overhead

### 3.2 Validation Protocol

**For Each Defect in Corpus:**
1. Load defect code + expected violation type
2. Run validation strategy (Structural-Only | Metamorphic-Only | Combined)
3. Record: {detected: bool, execution_time: float, violation_type: str}
4. Compare detected vs ground truth → classify as TP/FN/TN/FP

**Control Scenarios:**
- 50 valid API interactions (no defects) from h-e1 control set
- Expected result: 0 violations for all strategies (FPR check)

### 3.3 Execution Environment

**Platform:** Python 3.9+, PyTorch 2.0+  
**Hardware:** CPU-only (no GPU required for contract validation)  
**Timeout:** 10s per test (from h-e1/h-m1/h-m2 precedent)  
**Parallelization:** ThreadPoolExecutor with 4 workers for ensemble validation

---

## 4. Expected Outcomes

### 4.1 Baseline Performance (Projected)

| Strategy | FNR | Detection Rate | Execution Time |
|----------|-----|----------------|----------------|
| **Structural-Only** | ~48% | ~52% | <0.03s |
| **Metamorphic-Only** | ~52% | ~48% | <0.004s |
| **Average Baseline** | ~50% | ~50% | - |

### 4.2 Treatment Performance (Projected)

| Strategy | FNR | Detection Rate | FNR Reduction | Execution Time | Gate Status |
|----------|-----|----------------|---------------|----------------|-------------|
| **Combined** | ~10-20% | ~80-90% | **60-80%** | <0.034s | ✅ PASS (≥30%) |

**Key Prediction:** The combined approach should catch:
- 100% of structural defects (146/146)
- 100% of behavioral defects (105/105)
- 100% of mixed defects (62/62)
- Variable coverage of composition defects (0-35/35, depends on interaction complexity)

**Conservative Estimate:** Even if 0% of composition defects are caught, FNR = 35/348 = 10%, reduction = (50% - 10%) / 50% = 80%

### 4.3 Success Criteria (Gate Evaluation)

**MUST_WORK Gate:**
- **Criterion:** FNR reduction ≥ 30% compared to better baseline
- **Threshold:** If best baseline FNR = 48%, Combined FNR must be ≤ 33.6%
- **Projected:** Combined FNR = 10-20% → **PASS**

**Secondary Criteria:**
1. Execution time overhead <10s per test → Projected <0.034s → ✅
2. False-positive rate <5% → Projected 0% (reusing validated h-m1/h-m2 logic) → ✅
3. Detection rate >70% → Projected 80-90% → ✅

---

## 5. Risks & Mitigations

### 5.1 Technical Risks

**Risk 1: Execution Time Overhead**
- **Concern:** Running both validators doubles execution time
- **Projected Impact:** 0.03s + 0.004s = 0.034s (still <10s gate)
- **Mitigation:** Parallel execution via ThreadPoolExecutor reduces overhead

**Risk 2: Validator Interference**
- **Concern:** Structural validator modifies model state, breaking metamorphic validator
- **Projected Impact:** Low (both validators designed as stateless decorators in h-m1/h-m2)
- **Mitigation:** Deep copy model before validation, or ensure decorator idempotency

**Risk 3: Defect Corpus Mislabeling**
- **Concern:** Ground truth labels (structural vs behavioral) are incorrect
- **Projected Impact:** Medium (affects FNR calculation accuracy)
- **Mitigation:** Manual review of 10% sample (35 defects) to verify labels

### 5.2 Validity Threats

**Internal Validity:**
- **Threat:** Validators not applied consistently across strategies
- **Control:** Shared validation harness, same timeout/thresholds

**External Validity:**
- **Threat:** Results specific to PyTorch, may not generalize to TensorFlow/JAX
- **Generalization:** Corpus from h-e1 includes multi-framework defects (if available)

**Construct Validity:**
- **Threat:** FNR reduction doesn't capture real-world "missed critical bugs"
- **Control:** Weight defects by severity (if severity labels exist in corpus)

---

## 6. Timeline & Resources

### 6.1 Implementation Phases

| Phase | Tasks | Estimated Effort | Output |
|-------|-------|------------------|--------|
| **Data Preparation** | Load h-e1 corpus, stratify by type, label ground truth | 2 hours | `data/corpus_loader.py` |
| **Ensemble Validator** | Integrate h-m1 + h-m2, implement parallel execution | 3 hours | `contracts/ensemble.py` |
| **Experiment Script** | Run 3 strategies, record metrics, statistical tests | 2 hours | `run_experiment.py` |
| **Analysis** | FNR calculation, bootstrap CI, McNemar test, plots | 2 hours | `analysis/metrics.py`, `visualization/plots.py` |
| **Validation** | Run experiment, verify gate criteria, document results | 1 hour | `04_validation.md` |

**Total Estimated Effort:** ~10 hours (LIGHT tier, matches implementation_planning tier)

### 6.2 Resource Requirements

**Code Assets (Reuse):**
- h-m1 structural validator (validated, 100% detection)
- h-m2 metamorphic validator (validated, 100% detection)
- h-e1 defect corpus (348 defects, cached)

**New Code (Minimal):**
- Ensemble validator wrapper (~50 LOC)
- Comparison experiment script (~150 LOC)
- Analysis utilities (~100 LOC)

**Computational Resources:**
- CPU-only validation (no GPU)
- Estimated runtime: 348 defects × 0.034s × 3 strategies = ~35 seconds total

---

## 7. Deliverables

### 7.1 Code Artifacts

1. **`code/contracts/ensemble.py`**: Combined validator
2. **`code/data/corpus_loader.py`**: Defect corpus loader with stratification
3. **`code/run_experiment.py`**: Experiment script (3 strategies)
4. **`code/analysis/metrics.py`**: FNR calculation, statistical tests
5. **`code/visualization/plots.py`**: FNR comparison plots, coverage breakdown

### 7.2 Documentation

1. **`04_validation.md`**: Validation report with:
   - FNR reduction results
   - Statistical significance (McNemar test)
   - Coverage by defect type
   - Gate evaluation (MUST_WORK verdict)

2. **`data/results.csv`**: Per-defect results (defect_id, strategy, detected, execution_time)

3. **`visualizations/`**:
   - `fnr_comparison.png`: FNR by strategy with 95% CI
   - `coverage_by_type.png`: Detection rate stratified by defect type
   - `execution_time.png`: Overhead comparison

---

## 8. Alignment with Pipeline

### 8.1 Phase 3 Readiness

**PRD Requirements:**
- Input: Defect corpus (from h-e1, already available)
- Output: FNR reduction metric, gate verdict
- Dependencies: h-m1, h-m2 validators (both validated)

**Architecture Requirements:**
- Ensemble validation pattern (parallel execution)
- Modular validators (reuse h-m1/h-m2)
- Statistical analysis pipeline

**Complexity Tier:** LIGHT (minimal new code, reuse existing validators)

### 8.2 Success Metrics Mapping

| Hypothesis Gate | Experiment Metric | Threshold | Validation Method |
|-----------------|-------------------|-----------|-------------------|
| MUST_WORK (≥30% FNR reduction) | (FNR_baseline - FNR_combined) / FNR_baseline | ≥0.30 | McNemar test p<0.05 |
| Execution time <10s | Mean execution time per test | <10s | Direct measurement |
| FPR <5% | False positives / Control scenarios | <0.05 | Control set (n=50) |

---

## 9. Archon Knowledge Base Integration

### 9.1 Past Cases Referenced

1. **Multi-layered API validation** (Abhishek Verma):
   - Structural + semantic + composition layers
   - Ensemble pattern reduces false negatives
   - Relevant to: combining h-m1 + h-m2 strategies

2. **Contract testing frameworks** (Surety, apiwatch):
   - Schema validation (structural) + runtime checks (behavioral)
   - Parallel execution for performance
   - Relevant to: implementation pattern for ensemble.py

3. **Defect detection ensemble methods** (Great Expectations):
   - Multiple validators catch distinct error classes
   - Statistical aggregation of results
   - Relevant to: FNR reduction justification

### 9.2 Implementation Patterns Applied

1. **Decorator composition** (from h-m1/h-m2):
   - Stack `@validate_structural` and `@validate_metamorphic`
   - Non-interfering stateless decorators

2. **Parallel validation** (from Exa code examples):
   - ThreadPoolExecutor for concurrent checks
   - Reduces overhead from sequential execution

3. **Stratified evaluation** (from h-e1):
   - Defect corpus stratified by type
   - Per-stratum coverage metrics

---

## 10. Notes for Phase 3

### 10.1 Implementation Priorities

**High Priority:**
1. Ensure ensemble validator doesn't double-count mixed defects
2. Verify ground truth labels for defect stratification
3. Implement McNemar test for statistical rigor

**Medium Priority:**
1. Optimize parallel execution (ThreadPoolExecutor tuning)
2. Add severity weighting if corpus includes severity labels

**Low Priority:**
1. Extend to TensorFlow/JAX (out of scope for h-c1, future work)

### 10.2 Known Limitations

1. **Composition defects:** May not be caught by either contract type alone  
   → Expected residual FNR ~10% even with combined approach

2. **Oracle problem:** Ground truth labels assume perfect defect classification  
   → Mitigate with 10% manual review sample

3. **Generalization:** Results specific to Jiang et al. corpus, PyTorch APIs  
   → Document as threat to external validity

---

## Appendix A: Defect Corpus Schema

```python
# Expected structure from h-e1 corpus
defect_record = {
    "defect_id": "jiang_001",
    "defect_type": "structural" | "behavioral" | "mixed" | "composition",
    "code": "...",  # Defect-inducing code snippet
    "expected_violation": "shape_mismatch" | "softmax_sum_error" | ...,
    "structural_detectable": bool,  # Can h-m1 catch this?
    "metamorphic_detectable": bool,  # Can h-m2 catch this?
    "severity": "critical" | "major" | "minor",  # If available
}
```

---

## Appendix B: Statistical Power Analysis

**Hypothesis Test:** McNemar test for paired proportions  
**Null Hypothesis:** FNR_combined = FNR_baseline_best  
**Alternative:** FNR_combined < FNR_baseline_best (one-tailed)

**Power Calculation:**
- Sample size: n = 348 defects
- Expected effect: 30% reduction (0.48 → 0.34)
- Significance level: α = 0.05
- Power: 1-β > 0.95 (adequate for n=348)

**Interpretation:** With 348 defects, the experiment has >95% power to detect a 30% reduction in FNR at p<0.05.

---

**End of Experiment Design Brief**
