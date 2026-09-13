# Product Requirements Document (PRD): h-m3 Validation Implementation

**Date:** 2026-08-19  
**Hypothesis ID:** h-m3  
**Type:** MECHANISM  
**Tier:** 1  
**Gate:** SHOULD_WORK

---

## 1. Overview

### 1.1 Objective

Implement validation code for h-m3: test whether **required metadata fields** (enforced by platform validation) exhibit **consistent high presence rates** (~90%) across platforms regardless of friction score, contrasting with **optional fields** (h-m2 validated) which vary significantly by friction level.

This validates the hypothesis that **enforcement** and **friction reduction** are **independent mechanisms** driving metadata completeness.

### 1.2 Success Criteria

**Primary:**
1. Required fields (license, version) show **no friction effect**: Chi-squared test p > 0.10
2. Required fields **stable across platforms**: coefficient of variation (CV) < 0.20
3. **High absolute presence**: mean presence rate ≥80% for both license and version
4. **Contrast with h-m2**: required CV << optional CV (ratio < 0.25)

**Secondary:**
5. Cramér's V < 0.20 for required fields (weak platform association)
6. Parsing accuracy ≥85% (manual validation)

**Gate Decision:**
- PASS: All primary criteria met → mechanism distinction validated
- PARTIAL: 1-2 criteria met → mechanisms partially coupled
- FAIL: No criteria met → single mechanism hypothesis

### 1.3 Dependencies

**Prerequisite:**
- h-m2 VALIDATED (optional field friction effect confirmed: HF 55-66%, UCI 0-15%, p<0.0001)

**Data Dependency:**
- h-m2 cached extraction (9,990 datasets: HF 6,500, OpenML 2,990, UCI 500)
- No new API calls required (reuse h-m2 metadata records)

---

## 2. Functional Requirements

### 2.1 Data Loading & Preparation

**FR-1: Load h-m2 Cached Metadata**
- **Input:** `h-m2/data/raw/*.json` (HuggingFace, OpenML, UCI metadata)
- **Output:** Python dictionaries/DataFrames with 9,990 records
- **Validation:** Verify sample size (HF=6,500, OpenML=2,990, UCI=500)

**FR-2: Required Field Parsing**
- **Input:** Raw metadata records per platform
- **Output:** Binary presence flags (`license_present: bool, version_present: bool`)
- **Rules:**
  - **license:** Non-empty string, not "unknown"/"other" (HF/OpenML); keyword match for UCI (CC-BY/MIT/Apache/GPL/BSD)
  - **version:** Semantic version pattern `\d+\.\d+\.\d+` (HF); non-null integer (OpenML); keyword/date pattern (UCI)

**FR-3: Data Integrity Checks**
- Verify no null dataset IDs
- Verify all records have platform tag (HF/OpenML/UCI)
- Log parsing failures (record count, error types)

### 2.2 Statistical Analysis

**FR-4: Presence Rate Calculation**
- **Input:** Parsed presence flags per platform
- **Output:** Percentage present for each field per platform (6 values: 2 fields × 3 platforms)
- **Formula:** `(sum(field_present) / total_records) * 100`

**FR-5: Chi-Squared Test of Independence**
- **Input:** 2×3 contingency table per field (present/absent × HF/OpenML/UCI)
- **Output:** χ² statistic, p-value, degrees of freedom
- **Library:** `scipy.stats.chi2_contingency`
- **Success:** p > 0.10 (no significant platform effect)

**FR-6: Effect Size (Cramér's V)**
- **Input:** Contingency tables (license, version)
- **Output:** Cramér's V per field (0-1 scale)
- **Library:** `scipy.stats.contingency.association`
- **Success:** V < 0.20 (weak association)

**FR-7: Variance Comparison**
- **Input:** Presence rates per field
- **Output:** Coefficient of variation (CV) = std / mean
- **Comparison:** Required field CV vs h-m2 optional field CV
- **Success:** required CV < 0.20, optional CV > 1.0, ratio < 0.25

### 2.3 Validation

**FR-8: Parsing Accuracy Validation**
- **Input:** Stratified random sample (100 records: 50 HF, 30 OpenML, 20 UCI)
- **Output:** Manual review agreement rate (%)
- **Target:** ≥85% agreement
- **Process:** Export JSON sample → manual review → calculate accuracy
- **Fallback:** If <85%, refine parsing rules and re-validate

### 2.4 Result Output

**FR-9: Validation Summary JSON**
- **Schema:**
  ```json
  {
    "hypothesis_id": "h-m3",
    "status": "VALIDATED|PARTIAL|FAIL",
    "required_fields": {
      "license": {
        "hf_presence_pct": float,
        "openml_presence_pct": float,
        "uci_presence_pct": float,
        "chi2_statistic": float,
        "p_value": float,
        "cramers_v": float,
        "cv": float
      },
      "version": {...}
    },
    "contrast_with_h-m2": {
      "optional_field_cv": float,
      "required_vs_optional_cv_ratio": float
    },
    "parsing_validation": {
      "sample_size": 100,
      "agreement_rate_pct": float
    },
    "key_findings": [string]
  }
  ```

**FR-10: Validation Report (04_validation.md)**
- **Sections:**
  1. Hypothesis recap (statement, gate, success criteria)
  2. Experimental setup (dataset, fields, platforms)
  3. Results summary (presence rates table, statistical tests table)
  4. Contrast with h-m2 (required vs optional comparison)
  5. Validation decision (PASS/PARTIAL/FAIL with rationale)
  6. Key findings (numbered list)
  7. Limitations (parsing accuracy, platform-specific formats)
  8. Implications (repository design, two-lever model)

**FR-11: Comparison Visualizations**
- Bar chart: presence rates per field per platform (2 charts: license, version)
- Comparison table: required vs optional CV/Cramér's V
- Output format: PNG/SVG, saved to `h-m3/data/results/`

---

## 3. Non-Functional Requirements

### 3.1 Performance

**NFR-1: Execution Time**
- Total runtime ≤30 minutes (data reuse, no API calls)
- Statistical tests: <5 seconds per field

**NFR-2: Memory Usage**
- Peak memory <2GB (9,990 records fit in memory)

### 3.2 Reliability

**NFR-3: Reproducibility**
- Fixed random seed for validation sampling (seed=42)
- Deterministic parsing (no stochastic components)

**NFR-4: Error Handling**
- Missing files → clear error message with expected path
- Parsing failures → log warning, continue with valid records
- Contingency table validation → check for zero cells (add Laplace smoothing if needed)

### 3.3 Maintainability

**NFR-5: Code Organization**
- Modular functions: load_data(), parse_fields(), run_chi2_test(), generate_report()
- Type hints for all functions
- Docstrings with examples

**NFR-6: Configuration**
- Parsing rules in config dict (easy to refine if validation fails)
- File paths in constants (easy to update for different runs)

---

## 4. Data Specification

### 4.1 Input Data

**Source:** h-m2 extraction (already completed)

**Files:**
- `h-m2/data/raw/huggingface_metadata.json` (6,500 records)
- `h-m2/data/raw/openml_metadata.json` (2,990 records)
- `h-m2/data/raw/uci_metadata.json` (500 records)

**Schema (per record):**
```python
{
  "id": str,  # unique dataset identifier
  "platform": str,  # "HF" | "OpenML" | "UCI"
  "license": str | None,  # license field (format varies by platform)
  "version": str | int | None,  # version field (format varies by platform)
  # ... other fields from h-m2 extraction
}
```

### 4.2 Output Data

**Files:**
- `h-m3/data/results/required_field_presence.csv` (presence rates per platform)
- `h-m3/data/results/validation_summary.json` (statistical test results)
- `h-m3/data/results/validation_sample.json` (100-record manual review sample)
- `h-m3/data/results/comparison_table.md` (required vs optional contrast)
- `h-m3/data/results/license_presence_chart.png` (bar chart)
- `h-m3/data/results/version_presence_chart.png` (bar chart)
- `h-m3/04_validation.md` (full validation report)

---

## 5. Implementation Phases

### Phase 1: Data Preparation (2 hours)
1. Load h-m2 cached metadata (FR-1)
2. Implement required field parsing rules (FR-2)
3. Run data integrity checks (FR-3)
4. Generate parsing validation sample (FR-8)

### Phase 2: Manual Validation (3 hours)
5. Export 100-sample JSON for manual review (FR-8)
6. Human reviewer checks parsing accuracy
7. Calculate agreement rate (FR-8)
8. Refine parsing rules if <85% (FR-8)

### Phase 3: Statistical Analysis (2 hours)
9. Calculate presence rates per platform (FR-4)
10. Run chi-squared tests (FR-5)
11. Calculate Cramér's V (FR-6)
12. Calculate CV and compare with h-m2 (FR-7)

### Phase 4: Result Synthesis (2 hours)
13. Generate validation summary JSON (FR-9)
14. Create comparison visualizations (FR-11)
15. Write validation report (FR-10)
16. Update verification_state.yaml (h-m3.validation.status)

**Total Duration:** 9 hours (1 day)

---

## 6. Acceptance Criteria

### 6.1 Code Quality

- All functions have type hints and docstrings
- Parsing rules validated (≥85% manual agreement)
- Statistical tests pass sanity checks (p-values in [0,1], CV non-negative)

### 6.2 Output Completeness

- All output files generated (FR-9, FR-10, FR-11)
- validation_summary.json validates against schema
- 04_validation.md includes all required sections

### 6.3 Gate Decision

- Validation status (PASS/PARTIAL/FAIL) clearly stated
- Rationale for decision documented
- Key findings list all critical results (presence rates, p-values, CV, contrast)

---

## 7. Risk Mitigation

**R1: Parsing Misclassification**
- **Risk:** Platform-specific formats lead to incorrect presence detection
- **Mitigation:** Manual validation (100 samples, target ≥85% agreement)
- **Fallback:** Refine parsing rules and re-validate

**R2: UCI Enforcement Ambiguity**
- **Risk:** UCI doesn't enforce license/version, but creators may include anyway (social norm)
- **Mitigation:** Document UCI results separately; high UCI presence (>80%) still consistent with hypothesis (enforcement by professional expectation)

**R3: Zero Cells in Contingency Table**
- **Risk:** If UCI has 0% presence for a field, chi-squared test may fail
- **Mitigation:** Add Laplace smoothing (+1 to all cells) if zero cells detected

**R4: Small UCI Sample (n=500)**
- **Risk:** UCI results less stable due to smaller sample size
- **Mitigation:** Report confidence intervals for UCI rates; emphasize HF/OpenML comparison as primary test

---

## 8. Testing Strategy

### 8.1 Unit Tests

**Test 1: Parsing Rules**
- Input: Synthetic metadata records (known license/version values)
- Expected: Correct presence flags (True/False)
- Coverage: All platform-specific formats

**Test 2: Statistical Functions**
- Input: Mock contingency tables (known distributions)
- Expected: Correct p-values, Cramér's V, CV
- Coverage: Edge cases (zero cells, uniform distribution)

### 8.2 Integration Tests

**Test 3: End-to-End Pipeline**
- Input: h-m2 cached metadata (real data)
- Expected: validation_summary.json with valid schema
- Check: All output files generated, no runtime errors

**Test 4: Validation Report Generation**
- Input: Mock validation summary JSON
- Expected: 04_validation.md with all sections populated
- Check: Markdown syntax valid, tables formatted correctly

---

## 9. Documentation

### 9.1 Code Documentation

- README in `h-m3/` with setup instructions
- Inline comments for complex parsing logic
- Docstrings for all public functions

### 9.2 User Documentation

- 04_validation.md (FR-10) serves as primary documentation
- Interpretation guide: how to read chi-squared results, what CV means
- Decision tree: PASS/PARTIAL/FAIL criteria

---

## 10. Deliverables

**Code:**
- `h-m3/code/load_data.py` (FR-1)
- `h-m3/code/parse_fields.py` (FR-2)
- `h-m3/code/statistical_analysis.py` (FR-4, FR-5, FR-6, FR-7)
- `h-m3/code/generate_report.py` (FR-9, FR-10, FR-11)
- `h-m3/code/main.py` (orchestrator)

**Data:**
- `h-m3/data/results/*.csv|json|png|md` (FR-9, FR-10, FR-11)
- `h-m3/data/results/validation_sample.json` (FR-8)

**Documentation:**
- `h-m3/04_validation.md` (FR-10)
- `h-m3/README.md` (setup/usage)

**State:**
- Updated `verification_state.yaml` (h-m3.validation.status = COMPLETED)

---

**PRD Complete** | **Next:** Architecture Design | **Date:** 2026-08-19
