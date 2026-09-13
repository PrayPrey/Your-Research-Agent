# Product Requirements Document: h-m1 Friction Features Lower Entry Cost

**Date:** 2026-08-19  
**Hypothesis ID:** h-m1  
**Type:** MECHANISM  
**Tier:** 1  
**Prerequisites:** h-e1 (VALIDATED)

---

## 1. Executive Summary

**Objective:** Validate mechanism hypothesis that friction-reduction features (API upload, templates, automation) causally reduce metadata entry cost for dataset creators.

**Approach:** Within-platform controlled comparison — measure metadata completeness difference between API-programmatic vs manual-web-form uploads on HuggingFace Datasets Hub.

**Success Criteria:** API uploads show higher completeness than manual uploads (directional confirmation, p<0.05) + effect size ≥10 percentage points.

**Deliverables:**
1. Upload method classification pipeline (heuristic-based detector)
2. Metadata completeness scoring pipeline (6-field presence detection, reuses h-e1 rules)
3. Statistical validation pipeline (t-test, pilot validation)
4. Analysis report with gate decision (PASS/FAIL)

**Timeline:** 2 weeks

**Budget:** Tier 1 — 150k tokens

---

## 2. System Overview

### 2.1 System Architecture

```
[HuggingFace API] → [Dataset Discovery] → [Upload Method Classifier] → [Metadata Parser] → [Statistical Analyzer] → [Validation Report]
                          ↓                        ↓                           ↓
                    dataset_ids.csv      upload_classified.csv         completeness_scores.csv
```

### 2.2 Core Components

| Component | Purpose | Technology |
|-----------|---------|-----------|
| **Dataset Discovery** | Query HuggingFace API for ~5,000 dataset IDs, filter to candidates with README and pre-2026-08-19 creation | `huggingface_hub` API |
| **Upload Method Classifier** | Classify datasets as API-programmatic or manual-web-form based on commit history, file structure, README patterns | Rule-based heuristics (Python) |
| **Metadata Parser** | Extract 6 target fields (dependencies, version, data_source_url, preprocessing_code, license, collection_date) from README content | Regex + keyword matching (reuse h-e1 rules) |
| **Completeness Scorer** | Calculate mean presence rate × 100 for 6 fields per dataset | Python (pandas) |
| **Statistical Analyzer** | Compare mean completeness (API vs manual) via independent samples t-test | `scipy.stats.ttest_ind` |
| **Pilot Validator** | Manual review of 100-sample subset (50 API, 50 manual) to verify classification + parsing accuracy | CSV export for manual annotation |

### 2.3 Data Flow

**Input:** HuggingFace API (dataset metadata, README content, commit history)

**Processing Pipeline:**
1. **Discovery:** Fetch ~5,000 dataset IDs → Filter to ~3,000 candidates (has README + created before 2026-08-19)
2. **Classification:** For each candidate, analyze commit history + file structure → Label as API/manual
3. **Stratified Sampling:** Select ~1,000 API uploads + ~1,000 manual uploads (stratified random)
4. **Metadata Extraction:** For each sampled dataset, fetch README → Parse 6 fields → Calculate completeness score
5. **Pilot Validation:** Export 100-sample subset → Manual review → Verify classification accuracy >85%, parsing accuracy >90%
6. **Statistical Test:** Independent samples t-test (API vs manual mean completeness) → p-value + effect size
7. **Gate Decision:** IF direction confirmed (μ_API > μ_manual) AND p<0.05 AND pilot validation passed → PASS; ELSE → FAIL

**Output:**
- `data/h-m1/hf_dataset_ids.csv` (discovery results)
- `data/h-m1/upload_classified.csv` (classification results: dataset_id, upload_method, classification_confidence)
- `data/h-m1/completeness_scores.csv` (final dataset: dataset_id, upload_method, completeness_score, field_presence_vector)
- `data/h-m1/validation_pilot_100.csv` (manual validation sample)
- `docs/youra_research/h-m1/04_validation.md` (final report: statistics, gate decision, pilot results)

---

## 3. Functional Requirements

### FR-1: Dataset Discovery
**Description:** Query HuggingFace API to discover candidate datasets for analysis.

**Acceptance Criteria:**
- Query returns ≥5,000 dataset IDs from HuggingFace Datasets Hub
- Filter: datasets with README.md present
- Filter: creation date before 2026-08-19
- Output: CSV with columns `dataset_id, creation_date, has_readme`
- Target: ≥3,000 candidates after filtering

**Priority:** P0 (blocking)

---

### FR-2: Upload Method Classification
**Description:** Classify datasets as API-programmatic or manual-web-form uploads using heuristic rules.

**Acceptance Criteria:**
- **Heuristics implemented:**
  1. **Commit history analysis:** Detect `huggingface_hub` user-agent in commit messages → API upload signal
  2. **File structure check:** Presence of `dataset_info.json` → API upload signal
  3. **README structure:** Template-based YAML frontmatter (auto-generated `dataset_info` block) → API upload signal
  4. **Manual indicators:** Custom prose README, drag-and-drop file timestamps, hand-filled metadata UI tags → Manual upload signal
- **Classification output:** Binary label (API/manual) + confidence score (number of matching signals)
- **Ambiguous cases:** If signal count tied or low confidence (<2 signals), flag as "AMBIGUOUS" for manual review
- Output: CSV with columns `dataset_id, upload_method, classification_confidence, matched_signals`

**Priority:** P0 (blocking)

**Validation Target:** >85% accuracy on 50-sample pilot (manual ground truth)

---

### FR-3: Stratified Sampling
**Description:** Select ~1,000 API uploads and ~1,000 manual uploads from classified dataset pool.

**Acceptance Criteria:**
- Stratified random sampling per upload_method group
- Random seed: 42 (reproducibility)
- Exclude AMBIGUOUS classifications from sample
- Target: exactly 1,000 API uploads + 1,000 manual uploads (2,000 total)
- IF insufficient datasets in either group: Sample all available (minimum 500 per group required to proceed)

**Priority:** P0 (blocking)

---

### FR-4: Metadata Parsing
**Description:** Extract 6 target fields from README content using h-e1 validated parsing rules.

**Acceptance Criteria:**
- **Reuse h-e1 parsing rules:**
  - `dependencies`: Regex match for `requirements.txt`, `pip install`, `conda install`, package names with version specifiers
  - `version`: Regex match for version numbers (`v?\d+\.\d+(\.\d+)?`), date-based versions (`YYYY-MM-DD`)
  - `data_source_url`: URL extraction (http/https links), exclude GitHub/HuggingFace repo URLs
  - `preprocessing_code`: Code block detection (>50 chars + language keywords OR file extensions .py/.R/.ipynb)
  - `license`: License identifier extraction (MIT, Apache, CC-BY, GPL, etc. from YAML or README text)
  - `collection_date`: Date extraction (YYYY-MM-DD, Month YYYY, date keywords like "collected on")
- **Binary presence scoring:** Each field scored 0 (absent) or 1 (present)
- **Completeness score calculation:** Mean presence across 6 fields × 100 = percentage (0-100%)
- Output: CSV with columns `dataset_id, upload_method, completeness_score, dependencies, version, data_source_url, preprocessing_code, license, collection_date`

**Priority:** P0 (blocking)

**Validation Target:** >90% parsing accuracy on 100-sample pilot (manual review)

---

### FR-5: Pilot Validation
**Description:** Manual review of 100-sample subset to verify upload method classification and parsing accuracy.

**Acceptance Criteria:**
- **Sample selection:** 50 API uploads + 50 manual uploads (stratified random from final 2,000-dataset sample)
- **Validation tasks:**
  1. **Upload method validation:** Manual inspection of commit history, README structure, file timestamps → Verify classification label correct
  2. **Parsing validation:** Manual reading of README → Verify each of 6 field presence labels correct
- **Validation output:** CSV with columns `dataset_id, upload_method_ground_truth, classification_match, [field]_ground_truth, [field]_parsing_match` (for 6 fields)
- **Metrics:**
  - Classification accuracy: % agreement between automated label and ground truth (target >85%)
  - Parsing accuracy: % agreement across all 6 fields × 100 samples = 600 field labels (target >90%)
- **Failure response:** IF classification <85% OR parsing <90%: STOP, refine heuristics/rules, re-run validation until thresholds met

**Priority:** P0 (blocking, gate condition)

---

### FR-6: Statistical Analysis
**Description:** Compare mean completeness scores between API and manual upload groups via independent samples t-test.

**Acceptance Criteria:**
- **Test:** Independent samples t-test (two-tailed for null hypothesis, one-tailed for directional interpretation)
- **Null hypothesis (H0):** μ_API = μ_manual
- **Alternative hypothesis (H1):** μ_API > μ_manual (one-tailed directional prediction)
- **Significance level:** α = 0.05
- **Effect size:** Cohen's d (standardized mean difference) + absolute percentage point difference
- **Normality check:** Shapiro-Wilk test on both groups (IF violated: use Mann-Whitney U instead of t-test)
- **Equal variance check:** Levene's test (IF violated: use Welch's t-test)
- **Outlier detection:** Identify datasets with completeness >95% or <5%, inspect for anomalies (data quality check, not removal)
- Output: Statistical report with p-value, Cohen's d, mean difference (percentage points), confidence interval

**Priority:** P0 (blocking)

**Success Thresholds:**
- **Primary (MUST_WORK):** Direction confirmed (μ_API > μ_manual) AND p < 0.05
- **Secondary:** Absolute difference ≥10 percentage points

---

### FR-7: Validation Report
**Description:** Generate final validation report documenting results, gate decision, and next steps.

**Acceptance Criteria:**
- **Report structure:**
  1. **Hypothesis statement:** Restate h-m1 mechanism claim
  2. **Data summary:** Sample sizes (API vs manual), mean completeness scores, distribution statistics
  3. **Statistical results:** t-test p-value, Cohen's d, mean difference (pp), confidence interval
  4. **Pilot validation results:** Classification accuracy, parsing accuracy, error analysis
  5. **Gate decision:** PASS/FAIL with rationale
  6. **Key findings:** Interpretation of results (strong/moderate/weak support, null result, reverse direction)
  7. **Next steps:** IF PASS → proceed to h-m2; IF FAIL → stop verification plan, document limitation
- **Output file:** `docs/youra_research/h-m1/04_validation.md`

**Priority:** P0 (blocking)

---

## 4. Non-Functional Requirements

### NFR-1: Reproducibility
**Description:** All analysis steps must be reproducible with fixed random seed and versioned dependencies.

**Acceptance Criteria:**
- Random seed = 42 for all sampling operations
- Python dependencies versioned in `requirements.txt` (datasets, huggingface_hub, pandas, scipy, matplotlib)
- All scripts executable with single command: `python scripts/h-m1/run_pipeline.py`
- Data artifacts saved with timestamps and version metadata

---

### NFR-2: Performance
**Description:** Pipeline must complete within 2-week timeline with HuggingFace API rate limits.

**Acceptance Criteria:**
- Dataset discovery: ≤2 days (5,000 API calls @ ~1,000 requests/hour rate limit)
- Classification + extraction: ≤5 days (2,000 datasets × 5 API calls each = 10,000 calls @ ~10 hours runtime)
- Pilot validation: ≤2 days (5 hours upload method + 20 hours parsing validation, can parallelize)
- Statistical analysis: <1 hour (lightweight computation)
- Total: ≤10 working days (2 weeks)

---

### NFR-3: Code Quality
**Description:** Code must be readable, modular, and documented for handoff to Phase 6 paper writing.

**Acceptance Criteria:**
- Each component (discovery, classification, parsing, analysis) in separate script
- Docstrings for all functions (input/output specification)
- Inline comments for heuristic rules (rationale for each classification signal)
- Notebook for exploratory analysis (`notebooks/h-m1_analysis.ipynb`)

---

## 5. Gate Decision Logic

**MUST_WORK gate passes IF ALL conditions met:**
1. **Primary criterion:** Direction confirmed (μ_API > μ_manual) AND p < 0.05
2. **Validation criterion:** Upload method classification accuracy >85% (pilot)
3. **Validation criterion:** Parsing accuracy >90% (pilot)

**MUST_WORK gate fails IF ANY condition met:**
1. No difference detected (p ≥ 0.05)
2. Reverse direction (μ_API < μ_manual)
3. Classification accuracy ≤85%
4. Parsing accuracy ≤90%

**FAIL response:**
- STOP verification plan (h-m2, h-m3 blocked)
- Document limitation in 04_validation.md
- Reassess causal mechanism claim (consider alternative friction proxies, e.g., user surveys)

**PASS response:**
- Proceed to h-m2 (cross-platform comparison)
- Document effect size (strong/moderate/weak support) for Phase 6 paper writing

---

## 6. Implementation Risks & Mitigations

| Risk ID | Risk | Severity | Likelihood | Mitigation |
|---------|------|----------|-----------|------------|
| **R1** | Upload method classification unreliable (heuristics misclassify datasets) | High | Medium | 100-sample pilot validation, refine heuristics based on pilot errors, add manual review for ambiguous cases (AMBIGUOUS flag) |
| **R2** | Platform-level confounds despite within-platform comparison (API users are power-users with inherently higher quality datasets) | Medium | Medium | Acknowledge limitation in validation report, frame results as "friction feature availability" proxy not pure causal effect |
| **R3** | Small effect size (<10pp) undetectable despite large sample | Medium | Low | n=2,000 provides power >0.95 for detecting 10pp difference; accept smaller effects as weaker evidence |
| **R4** | Parsing rule failures inherited from h-e1 | Low | Low | h-e1 validation passed (>90% accuracy), reuse same rules; IF pilot validation <90%: Refine rules, reduce field set to high-confidence subset |
| **R5** | Insufficient datasets in API or manual group after classification | Low | Medium | IF <500 per group: PIVOT to reduced sample size (minimum n=500 per group for power >0.80); IF <500 in either group: FAIL, report data availability limitation |

---

## 7. Dependencies & Assumptions

### 7.1 External Dependencies
- **HuggingFace API:** Free tier access, rate-limited to ~1,000 requests/hour
- **Python libraries:** datasets (≥3.0), huggingface_hub (≥0.25), pandas (≥2.0), scipy (≥1.10), matplotlib (≥3.5)
- **h-e1 validation dataset:** IF available, reduces pilot validation manual effort by ~15 hours (reuse same 100 datasets for parsing validation)

### 7.2 Key Assumptions
| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| **A1** | Upload method is detectable from commit history + file structure patterns | GEO Uploader 2026 paper demonstrates programmatic upload pattern detection; HuggingFace commit messages include API user-agent strings | IF heuristics <85% accurate: Add manual review, reduce sample size, or PIVOT to user surveys |
| **A2** | API upload is a valid proxy for "friction reduction" (automation/tooling usage) | HuggingFace docs show `push_to_hub()` enables batch metadata population, templates, automated validation; manual web form requires field-by-field entry | IF API users manually fill fields anyway: Mechanism claim weakened, acknowledge limitation |
| **A3** | Within-platform comparison controls for platform-level confounds | Same community, same timepoint, same documentation; only upload method varies | IF API users systematically different (power-users): Selection bias acknowledged, results interpreted as "friction feature availability" not pure causality |
| **A4** | h-e1 parsing rules transfer to HuggingFace-only dataset | h-e1 validated HuggingFace extraction (90%+ success), same platform, same fields | IF parsing fails: Reuse h-e1 validation data, stricter rules |

---

## 8. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Dataset discovery** | ≥3,000 candidates | Count of datasets with README + created before 2026-08-19 |
| **Classification sample size** | 1,000 API + 1,000 manual | Count of datasets per upload_method group after stratified sampling |
| **Upload method classification accuracy** | >85% | % agreement with manual ground truth on 50-sample pilot |
| **Parsing accuracy** | >90% | % agreement across 6 fields × 100 samples = 600 field labels |
| **Statistical significance** | p < 0.05 | Independent samples t-test p-value |
| **Directional prediction** | μ_API > μ_manual | Mean completeness API group > mean completeness manual group |
| **Effect size** | ≥10 percentage points | Absolute difference in mean completeness scores |
| **Gate decision** | PASS | All primary + validation criteria met |

---

## 9. Deliverables

| Deliverable | Description | Output Path |
|------------|-------------|-------------|
| **Dataset IDs** | Discovery results (5,000 candidates → 3,000+ filtered) | `data/h-m1/hf_dataset_ids.csv` |
| **Upload classification** | Classification results (dataset_id, upload_method, confidence) | `data/h-m1/upload_classified.csv` |
| **Completeness scores** | Final analysis dataset (2,000 rows: dataset_id, upload_method, completeness_score, 6 field presence flags) | `data/h-m1/completeness_scores.csv` |
| **Pilot validation sample** | 100-sample subset for manual review | `data/h-m1/validation_pilot_100.csv` |
| **Validation report** | Final results, statistics, gate decision | `docs/youra_research/h-m1/04_validation.md` |
| **Analysis notebook** | Exploratory data analysis, visualizations | `notebooks/h-m1_analysis.ipynb` |
| **Scripts** | Runnable pipeline (discovery, classification, parsing, analysis) | `scripts/h-m1/run_pipeline.py` |

---

## 10. Out of Scope

- **Cross-platform comparison** (covered by h-m2, h-m3)
- **User surveys for self-reported friction** (potential future work if h-m1 fails)
- **Temporal trend analysis** (upload method friction changes over time)
- **Fine-grained friction feature decomposition** (isolating template vs API vs validation effects)
- **Causal intervention study** (randomized controlled trial with platform cooperation)

---

## 11. Approval & Sign-off

**Phase 2C Experiment Brief:** COMPLETED (02c_experiment_brief.md)  
**Phase 3 PRD:** COMPLETED (this document)  
**Next Steps:** Architecture design (03_architecture.md), Logic specification (03_logic.md), Configuration (03_config.md)

**Gate Dependency:** h-e1 VALIDATED (prerequisite satisfied)

**Status:** READY FOR IMPLEMENTATION PLANNING
