# Product Requirements Document: Combined Contract Validation Framework

**Hypothesis ID:** h-c1  
**Document Type:** PRD (Product Requirements Document)  
**Date:** 2026-07-11  
**Phase:** 3 - Implementation Planning  
**Complexity Tier:** LIGHT

---

## 1. Executive Summary

### 1.1 Purpose
Build an ensemble contract validation framework that combines structural and metamorphic contracts to reduce false-negative rate (missed defects) by ≥30% compared to using either contract type alone.

### 1.2 Success Criteria
- **Primary:** FNR reduction ≥30% vs. better baseline (MUST_WORK gate)
- **Secondary:** Execution time <10s per test, FPR <5%, detection rate >70%

### 1.3 Dependencies
- **h-m1:** Structural contract validator (VALIDATED)
- **h-m2:** Metamorphic contract validator (VALIDATED)
- **h-e1:** 348-defect corpus (VALIDATED)

---

## 2. User Stories

### 2.1 Primary User: API Testing Engineer
**As an** API testing engineer  
**I want to** validate API contracts using both structural and behavioral checks  
**So that** I can catch both syntax errors (shape/type mismatches) and semantic errors (invariant violations) in a single pass

**Acceptance Criteria:**
- Single validation call returns violations from both contract types
- Execution completes within 10s per test
- No duplicate violation reporting for mixed defects

### 2.2 Secondary User: Research Experimenter
**As a** research experimenter  
**I want to** compare FNR across three validation strategies  
**So that** I can quantify the reduction in missed defects when combining contract types

**Acceptance Criteria:**
- Experiment runs on full 348-defect corpus
- Results include FNR, detection rate, execution time per strategy
- Statistical significance computed via McNemar test

---

## 3. Functional Requirements

### 3.1 Ensemble Validator (Priority: HIGH)

**FR-1.1: Combined Validation Interface**
```python
def validate_combined(model, data, config):
    """
    Runs structural AND metamorphic contracts in parallel.
    
    Args:
        model: PyTorch model to validate
        data: Input tensor for validation
        config: Validation thresholds (from h-m1, h-m2)
    
    Returns:
        violations: List[Dict] with keys {type, message, timestamp}
    """
```

**FR-1.2: Parallel Execution**
- Use ThreadPoolExecutor with 2-4 workers
- Execute structural and metamorphic validators concurrently
- Aggregate violations without duplication

**FR-1.3: Violation Deduplication**
- If structural AND metamorphic both flag same defect (mixed type), report once
- Include violation source: {source: "structural" | "metamorphic" | "both"}

### 3.2 Defect Corpus Loader (Priority: HIGH)

**FR-2.1: Stratified Loading**
```python
def load_corpus(stratify_by="defect_type"):
    """
    Loads Jiang et al. 348-defect corpus with stratification.
    
    Returns:
        defects: List[Dict] with keys:
            - defect_id: str
            - defect_type: "structural" | "behavioral" | "mixed" | "composition"
            - code: str (defect snippet)
            - structural_detectable: bool
            - metamorphic_detectable: bool
    """
```

**FR-2.2: Ground Truth Labels**
- Each defect labeled with expected detectability per contract type
- Enables FNR calculation: `FNR = (defects_detectable_but_missed) / (total_detectable)`

### 3.3 Experiment Runner (Priority: HIGH)

**FR-3.1: Three-Strategy Comparison**
```python
def run_experiment(corpus, strategies=["structural", "metamorphic", "combined"]):
    """
    Runs validation experiment for all three strategies.
    
    Returns:
        results: Dict[str, Dict] with keys:
            - fnr: float
            - detection_rate: float
            - execution_time_mean: float
            - per_defect_results: List[Dict]
    """
```

**FR-3.2: Per-Defect Recording**
- Record for each defect: {defect_id, strategy, detected: bool, execution_time: float}
- Save to `data/results.csv`

### 3.4 Statistical Analysis (Priority: MEDIUM)

**FR-4.1: FNR Calculation**
```python
def calculate_fnr(detected, ground_truth):
    """
    FNR = (defects_expected_but_missed) / (total_expected_detectable)
    
    Returns:
        fnr: float
        fnr_ci: Tuple[float, float] (95% bootstrap CI)
    """
```

**FR-4.2: McNemar Test**
- Compare Combined vs Structural-Only (paired test)
- Compare Combined vs Metamorphic-Only (paired test)
- Report p-value and significance (α=0.05)

### 3.5 Visualization (Priority: LOW)

**FR-5.1: FNR Comparison Plot**
- Bar chart: FNR by strategy with 95% CI error bars
- Horizontal line at 30% reduction threshold

**FR-5.2: Coverage by Defect Type**
- Stacked bar chart: Detection rate stratified by {structural, behavioral, mixed, composition}

---

## 4. Non-Functional Requirements

### 4.1 Performance
- **NFR-1.1:** Execution time <10s per test (99th percentile)
- **NFR-1.2:** Parallel overhead <10% vs sequential execution
- **NFR-1.3:** Total experiment runtime <2 minutes (348 defects × 3 strategies)

### 4.2 Reliability
- **NFR-2.1:** Validator idempotency (same input → same output)
- **NFR-2.2:** No state mutation (deep copy model if needed)
- **NFR-2.3:** Timeout handling (10s per test max)

### 4.3 Maintainability
- **NFR-3.1:** Reuse h-m1, h-m2 validators without modification
- **NFR-3.2:** Modular design (separate loader, validator, analyzer)
- **NFR-3.3:** Configuration-driven thresholds (no hardcoded magic numbers)

### 4.4 Reproducibility
- **NFR-4.1:** Fixed random seed (42) for bootstrap sampling
- **NFR-4.2:** Versioned corpus (checksum validation)
- **NFR-4.3:** Logged execution environment (Python/PyTorch versions)

---

## 5. Technical Specifications

### 5.1 Input Specifications

**Input 1: Defect Corpus**
- Format: CSV with columns {defect_id, defect_type, code, structural_detectable, metamorphic_detectable}
- Size: 348 rows
- Source: h-e1 validation results
- Cache path: `docs/youra_research/h-e1/data/defect_corpus.csv`

**Input 2: Validators**
- Structural validator: `h-m1/code/contracts/validator.py::validate_structural()`
- Metamorphic validator: `h-m2/code/contracts/validator.py::validate_metamorphic()`
- Reuse as-is (no modifications)

**Input 3: Configuration**
- Validation thresholds from h-m1, h-m2 (e.g., softmax sum tolerance = 1e-5)
- Timeout: 10s per test
- Parallel workers: 4

### 5.2 Output Specifications

**Output 1: Validation Results**
- File: `data/results.csv`
- Schema: `defect_id, strategy, detected, execution_time, violation_type`
- Size: 1044 rows (348 defects × 3 strategies)

**Output 2: Validation Report**
- File: `04_validation.md`
- Sections: FNR reduction, statistical tests, gate verdict, visualizations

**Output 3: Visualizations**
- `visualizations/fnr_comparison.png`
- `visualizations/coverage_by_type.png`
- `visualizations/execution_time.png`

### 5.3 Algorithm Specifications

**Ensemble Validation Algorithm:**
```
1. Deep copy model (avoid state mutation)
2. Launch parallel tasks:
   - Task A: validate_structural(model_copy, data, config)
   - Task B: validate_metamorphic(model_copy, data, config)
3. Wait for both tasks (timeout: 10s)
4. Aggregate violations:
   - If same defect in both → mark as "both"
   - Otherwise → preserve source
5. Return aggregated violations
```

**FNR Calculation Algorithm:**
```
1. For each strategy:
   - detected = set(defects detected by strategy)
   - expected = set(defects ground_truth_detectable)
   - missed = expected - detected
   - FNR = len(missed) / len(expected)
2. Bootstrap 95% CI (1000 iterations)
3. Reduction = (FNR_baseline - FNR_combined) / FNR_baseline
```

---

## 6. Data Requirements

### 6.1 Dataset: Jiang et al. 348-Defect Corpus

**Source:** h-e1 validation artifacts  
**Type:** Synthetic representative corpus  
**Size:** 348 defects

**Stratification:**
- Structural-only: ~146 defects (42%)
- Behavioral-only: ~105 defects (30%)
- Mixed: ~62 defects (18%)
- Composition: ~35 defects (10%)

**Ground Truth Labels:**
- `structural_detectable`: Expected detection by h-m1
- `metamorphic_detectable`: Expected detection by h-m2

### 6.2 Control Set

**Purpose:** False-positive rate (FPR) validation  
**Size:** 50 valid API interactions (no defects)  
**Source:** h-e1 control scenarios  
**Expected:** 0 violations for all strategies

---

## 7. Dependencies & Constraints

### 7.1 External Dependencies
- **Python 3.9+**
- **PyTorch 2.0+**
- **scipy** (for McNemar test)
- **matplotlib** (for visualizations)
- **pandas** (for CSV handling)

### 7.2 Internal Dependencies
- **h-m1 validator** (structural contracts, VALIDATED)
- **h-m2 validator** (metamorphic contracts, VALIDATED)
- **h-e1 corpus** (348 defects, cached)

### 7.3 Constraints
- CPU-only execution (no GPU required)
- 10s timeout per test (hard limit)
- No network access (offline validation)

---

## 8. Risk Mitigation

### 8.1 Technical Risks

**Risk 1: Validator Interference**
- **Probability:** Low
- **Impact:** High (incorrect FNR calculation)
- **Mitigation:** Deep copy model before validation, verify idempotency via unit tests

**Risk 2: Defect Corpus Mislabeling**
- **Probability:** Medium
- **Impact:** High (invalid ground truth)
- **Mitigation:** Manual review of 10% sample (35 defects), cross-check with h-e1 validation logs

**Risk 3: Execution Timeout**
- **Probability:** Low
- **Impact:** Medium (incomplete results)
- **Mitigation:** ThreadPoolExecutor with timeout, record TIMEOUT as separate category

### 8.2 Validity Threats

**Internal Validity:**
- Control same timeout/thresholds across strategies
- Use same random seed for bootstrap sampling

**External Validity:**
- Document corpus source (Jiang et al., PyTorch)
- Note generalization limits (single framework, synthetic corpus)

---

## 9. Implementation Phases

### Phase 1: Data Preparation (2 hours)
- Load h-e1 corpus
- Stratify by defect_type
- Validate ground truth labels

### Phase 2: Ensemble Validator (3 hours)
- Implement parallel execution wrapper
- Integrate h-m1 + h-m2 validators
- Deduplication logic

### Phase 3: Experiment Script (2 hours)
- Three-strategy runner
- Per-defect recording
- Timeout handling

### Phase 4: Analysis (2 hours)
- FNR calculation + bootstrap CI
- McNemar test
- Visualizations

### Phase 5: Validation (1 hour)
- Run full experiment
- Verify gate criteria
- Document 04_validation.md

**Total Estimated Effort:** ~10 hours (LIGHT tier)

---

## 10. Acceptance Testing

### 10.1 Unit Tests
- `test_ensemble_validator()`: Verify parallel execution, deduplication
- `test_corpus_loader()`: Verify stratification, ground truth labels
- `test_fnr_calculation()`: Verify FNR formula, bootstrap CI

### 10.2 Integration Tests
- `test_experiment_runner()`: Run on 10-defect subset, verify result schema
- `test_timeout_handling()`: Inject slow validator, verify timeout

### 10.3 Validation Tests
- `test_control_set()`: FPR = 0% on 50 valid scenarios
- `test_gate_criteria()`: FNR reduction ≥30% on full corpus

---

## 11. Documentation Requirements

### 11.1 Code Documentation
- Docstrings for all public functions
- Inline comments for non-obvious logic (e.g., deduplication)

### 11.2 Validation Report (04_validation.md)
- Executive summary (gate verdict)
- FNR reduction results with 95% CI
- McNemar test p-values
- Coverage breakdown by defect type
- Execution time analysis
- Visualizations

### 11.3 Data Artifacts
- `data/results.csv`: Per-defect results
- `data/corpus_stratified.csv`: Stratified corpus with labels

---

## 12. Open Questions

1. **Q1:** Should severity weighting be applied if corpus includes severity labels?
   - **Answer:** Out of scope for h-c1, document as future work

2. **Q2:** Should composition defects be analyzed separately (expected FN)?
   - **Answer:** Yes, report coverage by defect type in 04_validation.md

3. **Q3:** Should TensorFlow/JAX compatibility be tested?
   - **Answer:** No, PyTorch-only for h-c1 (external validity threat)

---

## 13. Appendices

### Appendix A: Glossary
- **FNR (False-Negative Rate):** Proportion of defects missed by validator
- **FPR (False-Positive Rate):** Proportion of valid scenarios flagged as defects
- **MUST_WORK Gate:** Hypothesis validation criterion requiring ≥30% FNR reduction
- **Ensemble Validation:** Running multiple validators in parallel

### Appendix B: References
- h-m1 validation report: `docs/youra_research/h-m1/04_validation.md`
- h-m2 validation report: `docs/youra_research/h-m2/04_validation.md`
- h-e1 corpus: `docs/youra_research/h-e1/data/defect_corpus.csv`
- Experiment brief: `docs/youra_research/h-c1/02c_experiment_brief.md`

---

**End of PRD**
