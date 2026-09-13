# Experiment Brief: h-m2 — Lower Friction Increases Voluntary Completion

**Date:** 2026-08-19  
**Hypothesis ID:** h-m2  
**Type:** MECHANISM  
**Tier:** 1  
**Prerequisites:** h-m1 (VALIDATED - API 63.9% vs Manual 51.8%, p=0.0000)

---

## 1. Hypothesis Statement

**Statement:** Under scope of optional metadata fields (preprocessing_code, data_source_url, collection_date) not enforced by platform validation, if dataset creators encounter lower friction when documenting (via tooling/automation), then voluntary completion rates for optional fields increase, because reduced cognitive/time cost makes documentation less burdensome and more likely to be completed.

**Rationale:** Second mechanism step linking friction reduction to behavioral outcome. Tests whether lower entry cost (validated in h-m1) translates to higher completion rates for valuable-but-not-required fields.

**Gate:** SHOULD_WORK  
**Success Criteria:** HF shows higher optional presence than UCI (direction confirmed); difference ≥30 percentage points (substantial effect size).

---

## 2. Experimental Design

### 2.1 Core Research Question

Do **optional metadata fields** (not enforced by platform validation) exhibit higher presence rates on **high-friction-reduction platforms** (HuggingFace friction=3) compared to **low-friction-reduction platforms** (UCI friction=0)?

### 2.2 Variables

| Type | Variable | Operationalization |
|------|----------|-------------------|
| **Independent** | Platform friction score (0-4 scale) | HF=3 (templates + validation + API), OpenML=2 (API + basic templates), UCI=0 (manual web forms only) |
| **Dependent** | Optional field presence rate (0-100%) | Percentage of datasets with field present across 3 optional fields |
| **Controlled** | Dataset stratification | Proportional sampling (~7k HF, ~2.5k OpenML, ~500 UCI based on platform size) |
| **Controlled** | Field definition consistency | Cross-platform semantic normalization (explicit mapping rules) |
| **Controlled** | Temporal snapshot | Same extraction timepoint (2026-08-19) for all platforms |

### 2.3 Causal Mechanism

```
High Friction-Reduction Platform (HF friction=3)
    ↓
Lower entry cost for dataset creators (validated in h-m1)
    ↓
Optional fields easier to complete (automation, templates, API)
    ↓
Higher voluntary completion rates (preprocessing_code, data_source_url, collection_date)
```

**Counterfactual:** Low friction platforms (UCI friction=0) → manual typing required → optional fields skipped (low completion rates).

---

## 3. Dataset Specification

### 3.1 Dataset Selection

**Type:** standard (existing public datasets across 3 platforms)  
**Sources:**
- **HuggingFace Datasets Hub** (huggingface.co/datasets) — friction=3
- **OpenML** (openml.org) — friction=2
- **UCI ML Repository** (archive.ics.uci.edu/ml/datasets) — friction=0

**Access Methods:**
- HuggingFace: `huggingface_hub` API + `datasets` library
- OpenML: `openml-python` API
- UCI: Web scraping via BeautifulSoup

### 3.2 Dataset Characteristics

| Property | Specification |
|----------|--------------|
| **Total sample size** | 10,000+ datasets (stratified by platform) |
| **Platform distribution** | HF: ~7,000 (70%), OpenML: ~2,500 (25%), UCI: ~500 (5%) |
| **Sampling strategy** | Stratified random sampling per platform (proportional to platform size) |
| **Temporal scope** | Datasets published before 2026-08-19 |
| **Target fields (optional)** | preprocessing_code, data_source_url, collection_date |

**Rationale for distribution:**
- HF has largest dataset count (100k+) → larger sample for statistical power
- OpenML intermediate (~20k datasets) → medium sample
- UCI smallest (~600 datasets) → near-census sample

### 3.3 Field Classification: Optional vs Required

**Optional Fields (h-m2 focus):**
1. **preprocessing_code:** Code snippets/scripts for data preprocessing (NOT enforced by any platform)
2. **data_source_url:** URL to original data source (NOT enforced by any platform)
3. **collection_date:** Timestamp of data collection (NOT enforced by any platform)

**Required Fields (excluded from h-m2, tested in h-m3):**
- **license:** Enforced by HF/OpenML (upload blocked without license selection)
- **version:** Enforced by OpenML (required metadata field)

**Distinction:** Optional fields test voluntary completion behavior; required fields test enforcement mechanism (h-m3 control).

### 3.4 Cross-Platform Field Mapping

Platforms define fields differently. Explicit semantic mapping:

| Standard Field | HuggingFace | OpenML | UCI |
|---------------|-------------|--------|-----|
| **preprocessing_code** | Code snippets in README.md or dataset card YAML | `processing_script` in dataset description XML | Methodology section in dataset description HTML |
| **data_source_url** | `source` or `homepage` in dataset card YAML | `url` field in dataset metadata | Source URL in dataset description |
| **collection_date** | `date_created` in YAML or prose timestamp | `upload_date` or `version_date` in XML | Publication date in HTML metadata |

**Validation:** Manual inspection of 50 samples per platform (150 total) to confirm semantic equivalence (target >80% agreement).

### 3.5 Metadata Field Parsing Rules

Following h-e1 validated rules, adapted per platform:

| Field | Presence Criteria | Platform-Specific Notes |
|-------|------------------|------------------------|
| **preprocessing_code** | >50 chars + language keywords (import, def, function) OR file extension (.py, .R, .ipynb, .sh) | HF: README code blocks; OpenML: processing_script XML; UCI: methodology prose |
| **data_source_url** | Valid URL pattern (http/https + domain) | HF: YAML source field; OpenML: url XML; UCI: HTML link extraction |
| **collection_date** | Date pattern (YYYY-MM-DD, Month YYYY, YYYY) | HF: YAML date_created; OpenML: version_date XML; UCI: HTML publication date |

**Binary Presence:** Each field scored 0 (absent) or 1 (present).  
**Presence Rate per Platform:** (datasets with field) / (total datasets) × 100 = percentage.

---

## 4. Model/Algorithm Specification

### 4.1 Algorithm Type

**Binary field presence detection** via rule-based parsing (reuse h-e1/h-m1 infrastructure).

No machine learning model required — automated extraction pipeline with platform-specific parsers.

### 4.2 Implementation Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **HuggingFace extractor** | `huggingface_hub` API + YAML parser | Fetch dataset cards, parse YAML frontmatter |
| **OpenML extractor** | `openml-python` API + XML parser | Fetch dataset metadata, parse XML responses |
| **UCI extractor** | BeautifulSoup + HTML parser | Web scraping for dataset descriptions |
| **Cross-platform normalizer** | Custom mapping logic | Normalize field names across platforms |
| **Field presence parser** | Python regex + keyword matching | Detect presence of 3 optional fields |
| **Statistical test** | Chi-squared test (scipy.stats.chi2_contingency) | Compare presence rates across platforms |

### 4.3 Baseline Comparison

**Comparison Target:** h-m1 within-platform analysis (API vs manual on HuggingFace)

**h-m2 Extension:**
- h-m1 validated friction-reduction mechanism within HF (API higher than manual)
- h-m2 tests cross-platform friction effect (high-friction HF vs low-friction UCI)
- h-m2 focuses on optional fields only (voluntary completion, not enforcement)

**No external baseline method** — this is a novel cross-platform observational study.

---

## 5. Experimental Protocol

### 5.1 Data Collection Steps

**Step 1: Platform Friction Scoring (reuse h-e1 validated scores)**
- HuggingFace: friction=3 (templates + validation + API)
- OpenML: friction=2 (API + basic schema)
- UCI: friction=0 (manual web forms only)

**Step 2: Dataset Discovery per Platform**

**HuggingFace (~7,000 datasets):**
- Query `list_datasets()` API for public datasets
- Filter: datasets with README.md and created before 2026-08-19
- Stratified random sample: 7,000 datasets

**OpenML (~2,500 datasets):**
- Query `openml.datasets.list_datasets()` for active datasets
- Filter: datasets with status='active' and date < 2026-08-19
- Stratified random sample: 2,500 datasets

**UCI (~500 datasets):**
- Web scrape dataset list from archive.ics.uci.edu/ml/datasets
- Filter: datasets with description page accessible
- Near-census sample: 500 datasets (all available)

**Step 3: Metadata Extraction per Platform**

**HuggingFace:**
- Fetch README.md + dataset card YAML via `huggingface_hub.hf_api.dataset_info()`
- Parse YAML frontmatter for `source`, `homepage`, `date_created`
- Extract code blocks from README.md for preprocessing_code

**OpenML:**
- Fetch dataset metadata via `openml.datasets.get_dataset()`
- Parse XML for `processing_script`, `url`, `version_date`

**UCI:**
- Fetch HTML description page via BeautifulSoup
- Extract methodology section, source URL, publication date via CSS selectors

**Step 4: Field Presence Detection**
- Apply binary parsing rules per field per platform
- Calculate presence rate per optional field per platform:
  - `preprocessing_code_rate = (datasets with preprocessing_code) / (total datasets) × 100`
  - `data_source_url_rate = (datasets with data_source_url) / (total datasets) × 100`
  - `collection_date_rate = (datasets with collection_date) / (total datasets) × 100`

**Step 5: Statistical Comparison**
- Construct 3×3 contingency table:
  ```
                  | preprocessing_code | data_source_url | collection_date |
  ----------------|--------------------|-----------------|-----------------
  HuggingFace     | count_present      | count_present   | count_present   |
  OpenML          | count_present      | count_present   | count_present   |
  UCI             | count_present      | count_present   | count_present   |
  ```
- Run chi-squared test per field: `scipy.stats.chi2_contingency(observed)`
- Primary comparison: HF vs UCI (highest vs lowest friction)
- Secondary comparison: OpenML intermediate (friction=2)

### 5.2 Success Metrics

**Primary (Gate: SHOULD_WORK):**
1. **Direction confirmed:** HF optional presence rate > UCI optional presence rate for all 3 fields
2. **Effect size substantial:** HF - UCI difference ≥30 percentage points for at least 2/3 fields
3. **Statistical significance:** p < 0.05 for chi-squared test (HF vs UCI comparison)

**Secondary:**
1. **Gradient effect:** OpenML presence rate intermediate (UCI < OpenML < HF)
2. **Field consistency:** Effect holds across all 3 optional fields (not just 1)

### 5.3 Validation Protocol

**Parsing Accuracy Validation (reuse h-e1 protocol):**
- Sample 100 datasets stratified per platform (50 HF, 30 OpenML, 20 UCI)
- Manual review: human annotator marks field presence (binary: 0/1)
- Calculate agreement: (automated matches manual) / (total samples)
- Threshold: >85% agreement required (same as h-m1)

**Cross-Platform Semantic Validation:**
- Sample 50 datasets per platform with field present (150 total)
- Manual review: verify semantic equivalence (HF preprocessing_code ≈ OpenML processing_script ≈ UCI methodology)
- Calculate semantic match rate: (semantically equivalent) / (total samples)
- Threshold: >80% semantic agreement required

### 5.4 Execution Environment

**Runtime:** ~2-4 hours (10k+ dataset extraction + parsing + statistical test)

**Dependencies:**
- Python 3.9+
- `huggingface_hub>=0.20.0`
- `openml>=0.14.0`
- `beautifulsoup4>=4.12.0`
- `scipy>=1.11.0`
- `pandas>=2.0.0`
- `numpy>=1.24.0`

**Output Artifacts:**
- `data/h-m2/hf_metadata.json` — HuggingFace extracted metadata
- `data/h-m2/openml_metadata.json` — OpenML extracted metadata
- `data/h-m2/uci_metadata.json` — UCI extracted metadata
- `data/h-m2/presence_rates.csv` — Optional field presence rates per platform
- `data/h-m2/statistical_results.json` — Chi-squared test results
- `data/h-m2/validation_report.json` — Parsing accuracy + semantic validation results

---

## 6. Analysis Plan

### 6.1 Statistical Test Specification

**Primary Test: Chi-Squared Test of Independence**

**Null Hypothesis (H0):** No significant difference in optional field presence rates between HF (friction=3) and UCI (friction=0).

**Alternative Hypothesis (H1):** HF shows significantly higher optional field presence rates than UCI.

**Test Procedure:**
1. Construct 2×2 contingency table per field (HF vs UCI):
   ```
             | Present | Absent |
   ----------|---------|--------|
   HF        | a       | b      |
   UCI       | c       | d      |
   ```
2. Run `scipy.stats.chi2_contingency(observed)`
3. Extract chi-squared statistic, p-value, degrees of freedom
4. Calculate effect size: difference in proportions (HF_rate - UCI_rate)

**Significance Threshold:** p < 0.05 (two-tailed)

**Effect Size Threshold:** ≥30 percentage points (HF - UCI)

**Secondary Test: Gradient Analysis (3-platform comparison)**
- Run chi-squared test on full 3×3 contingency table (HF, OpenML, UCI)
- If significant, confirms friction gradient effect (not just HF vs UCI binary)

### 6.2 Expected Results

**Based on verification plan predictions (Section 2.2 of 02b):**

| Field | HF Rate (Expected) | OpenML Rate (Expected) | UCI Rate (Expected) | HF-UCI Diff |
|-------|-------------------|----------------------|-------------------|-------------|
| **preprocessing_code** | 55-65% | 30-40% | <15% | ≥40pp |
| **data_source_url** | 60-70% | 35-45% | <20% | ≥40pp |
| **collection_date** | 50-60% | 25-35% | <10% | ≥40pp |

**Interpretation:**
- If HF ≥55% and UCI <15% across all 3 fields → **Gate PASS** (direction + effect size confirmed)
- If HF 40-50% and UCI 20-30% → **Partial support** (direction confirmed but smaller effect size)
- If HF <40% or UCI >40% → **Gate FAIL** (no friction effect detected)

### 6.3 Failure Response

**Scenario 1: No cross-platform difference (p > 0.05 or HF ≈ UCI)**
- **Action:** ABANDON cross-platform friction claim
- **Fallback:** Report h-m1 within-platform effect only (API vs manual on HF)
- **Interpretation:** Platform confounds dominate (age, community size), not friction features

**Scenario 2: Direction reversed (UCI > HF)**
- **Action:** STOP verification, reassess hypothesis
- **Interpretation:** Enforcement mechanism dominates (UCI may enforce optional fields differently)

**Scenario 3: Small effect size (10-20pp difference, p < 0.05)**
- **Action:** Document partial support
- **Interpretation:** Friction effect exists but weaker than predicted (h-m3 may still hold)

---

## 7. Risk Analysis

### 7.1 Key Risks (from verification plan Section 3)

| Risk ID | Description | Mitigation | Impact on h-m2 |
|---------|-------------|------------|----------------|
| **R1: Parsing Misclassification** | Binary presence detection misclassifies empty placeholders as "present" or misses valid entries | Explicit parsing rules (>50 chars + keywords) + 100-sample validation (target >85% accuracy) | **High** — unreliable presence rates invalidate comparison |
| **R3: Normalization Semantic Loss** | Cross-platform fields semantically different (HF preprocessing_code ≠ UCI methodology) | Semantic mapping documentation + 50-sample inspection per platform (target >80% agreement) | **Medium** — reduces comparison validity, doesn't invalidate |
| **R4: Insufficient Statistical Power** | True effect size <20pp, sample lacks power to detect | 10k+ sample provides power >0.99 for 20pp+ difference (per verification plan Section 1.5 A4) | **Low** — large sample mitigates |

### 7.2 Novel Risks for h-m2

**R6: Platform Size Imbalance**
- **Description:** UCI has only ~600 total datasets (near-census sample); HF has 100k+ (stratified sample)
- **Impact:** Statistical power imbalanced; UCI outliers have larger effect
- **Mitigation:** Report confidence intervals per platform; acknowledge UCI as near-census (not sample)

**R7: Temporal Confounds**
- **Description:** Platforms evolved at different rates (HF launched 2020, UCI legacy since 2000s)
- **Impact:** Friction effect confounded with platform age, dataset vintage
- **Mitigation:** Control for dataset publication date in sensitivity analysis; report as limitation

---

## 8. Deliverables

### 8.1 Code Artifacts

**Directory:** `/h-m2/`

**Files:**
- `config.py` — Hyperparameters, thresholds, platform URLs
- `hf_extractor.py` — HuggingFace metadata extraction (reuse h-e1/h-m1)
- `openml_extractor.py` — OpenML metadata extraction (reuse h-e1)
- `uci_extractor.py` — UCI web scraping (reuse h-e1)
- `field_parser.py` — Optional field presence detection
- `cross_platform_normalizer.py` — Field mapping logic
- `statistical_analysis.py` — Chi-squared test, effect size calculation
- `validation.py` — Parsing accuracy + semantic validation
- `main.py` — End-to-end pipeline orchestration

### 8.2 Data Artifacts

**Directory:** `/data/h-m2/`

**Files:**
- `hf_metadata.json` — HuggingFace extracted metadata (7k datasets)
- `openml_metadata.json` — OpenML extracted metadata (2.5k datasets)
- `uci_metadata.json` — UCI extracted metadata (500 datasets)
- `presence_rates.csv` — Optional field presence rates per platform
- `statistical_results.json` — Chi-squared test results
- `validation_report.json` — Parsing + semantic validation results

### 8.3 Report Artifacts

**Directory:** `/docs/youra_research/h-m2/`

**Files:**
- `04_validation.md` — Validation report (gate evaluation, findings, interpretation)
- `figures/presence_rates_barplot.png` — Visualization of optional field presence rates per platform
- `figures/contingency_tables.png` — Contingency tables for chi-squared tests

---

## 9. Timeline

**Phase 4 Implementation:** 1-2 days

| Step | Task | Duration |
|------|------|----------|
| 1 | Reuse h-e1/h-m1 extractors (HF, OpenML, UCI) | 0.5 days |
| 2 | Implement cross-platform normalizer | 0.5 days |
| 3 | Run 10k+ dataset extraction | 0.5 days (parallel API calls) |
| 4 | Apply optional field parsing rules | 0.25 days |
| 5 | Run chi-squared tests | 0.25 days |
| 6 | Validation (parsing accuracy + semantic check) | 0.5 days (manual review) |
| 7 | Generate 04_validation.md report | 0.25 days |

**Total:** ~2.75 days (can be shortened to 1.5 days if validation is streamlined)

---

## 10. Success Criteria Summary

**Gate: SHOULD_WORK (not MUST_WORK — allows partial failure)**

**Primary Criteria (required for PASS):**
1. ✓ Direction confirmed: HF optional presence > UCI optional presence for all 3 fields
2. ✓ Statistical significance: p < 0.05 for HF vs UCI chi-squared test
3. ✓ Substantial effect size: HF - UCI difference ≥30 percentage points for ≥2/3 fields

**Secondary Criteria (desirable but not required):**
- Gradient effect: UCI < OpenML < HF (friction score order)
- Field consistency: Effect holds across all 3 optional fields
- Parsing accuracy: >85% agreement with manual review
- Semantic validity: >80% cross-platform field equivalence

**Acceptance Levels:**
- **Full PASS:** All primary + all secondary criteria met
- **Partial PASS:** All primary + 50%+ secondary criteria met
- **FAIL:** Any primary criterion failed

---

**Phase 2C Complete** | **Next:** Phase 3 Implementation Planning | **Date:** 2026-08-19
