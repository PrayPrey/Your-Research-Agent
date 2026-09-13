# Product Requirements Document: h-m2 — Lower Friction Increases Voluntary Completion

**Date:** 2026-08-19  
**Hypothesis ID:** h-m2  
**Type:** MECHANISM  
**Tier:** 1  
**Prerequisites:** h-m1 (VALIDATED - API 63.9% vs Manual 51.8%, p=0.0000)

---

## 1. Executive Summary

### 1.1 Objective
Validate that lower documentation friction (via tooling/automation) increases voluntary completion rates for optional metadata fields across ML dataset platforms.

### 1.2 Hypothesis Statement
Under scope of optional metadata fields (preprocessing_code, data_source_url, collection_date) not enforced by platform validation, if dataset creators encounter lower friction when documenting (via tooling/automation), then voluntary completion rates for optional fields increase, because reduced cognitive/time cost makes documentation less burdensome and more likely to be completed.

### 1.3 Success Criteria
**Gate: SHOULD_WORK**

**Primary (required for PASS):**
1. Direction confirmed: HF optional presence > UCI optional presence for all 3 fields
2. Statistical significance: p < 0.05 for HF vs UCI chi-squared test
3. Substantial effect size: HF - UCI difference ≥30 percentage points for ≥2/3 fields

**Secondary (desirable):**
- Gradient effect: UCI < OpenML < HF (friction score order)
- Field consistency: Effect holds across all 3 optional fields
- Parsing accuracy: >85% agreement with manual review
- Semantic validity: >80% cross-platform field equivalence

---

## 2. System Architecture

### 2.1 High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                   Platform Data Sources                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ HuggingFace  │  │   OpenML     │  │     UCI      │      │
│  │ (friction=3) │  │ (friction=2) │  │ (friction=0) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
            │                  │                  │
            ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│              Platform-Specific Extractors                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │HF Extractor  │  │OpenML Extr.  │  │ UCI Scraper  │      │
│  │(API + YAML)  │  │  (API + XML) │  │(BeautifulSoup│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
            │                  │                  │
            ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│         Cross-Platform Field Normalizer                      │
│  ┌───────────────────────────────────────────────┐          │
│  │  Semantic Field Mapping                       │          │
│  │  (preprocessing_code, data_source_url,        │          │
│  │   collection_date)                            │          │
│  └───────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│            Binary Field Presence Parser                      │
│  ┌───────────────────────────────────────────────┐          │
│  │  Rule-based Detection                         │          │
│  │  (>50 chars, keywords, URL patterns, dates)   │          │
│  └───────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│          Statistical Analysis & Validation                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Chi-Squared  │  │ Effect Size  │  │  Validation  │      │
│  │    Test      │  │  Calculation │  │  (Parsing +  │      │
│  │              │  │              │  │   Semantic)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Output Artifacts                          │
│  ┌───────────────────────────────────────────────┐          │
│  │ - presence_rates.csv                          │          │
│  │ - statistical_results.json                    │          │
│  │ - validation_report.json                      │          │
│  │ - 04_validation.md                            │          │
│  └───────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Component Breakdown

| Component | Purpose | Technology | Reuse from h-m1 |
|-----------|---------|------------|-----------------|
| **HF Extractor** | Fetch HuggingFace dataset cards, parse YAML frontmatter | `huggingface_hub` API + PyYAML | ✓ (h-m1 codebase) |
| **OpenML Extractor** | Fetch OpenML dataset metadata, parse XML | `openml-python` API + lxml | ✓ (h-e1 codebase) |
| **UCI Scraper** | Web scrape UCI dataset descriptions | BeautifulSoup + requests | ✓ (h-e1 codebase) |
| **Cross-Platform Normalizer** | Map platform-specific field names to standard schema | Custom Python mapping logic | ✗ (new for h-m2) |
| **Field Presence Parser** | Detect binary presence of 3 optional fields | Regex + keyword matching | ✓ (h-m1 parsing rules, adapted) |
| **Statistical Analyzer** | Chi-squared test, effect size calculation | scipy.stats.chi2_contingency | ✗ (new for h-m2) |
| **Validator** | Parsing accuracy + semantic validation | Manual review pipeline | ✓ (h-m1 validation protocol) |

---

## 3. Functional Requirements

### 3.1 Data Extraction

**FR-1: HuggingFace Dataset Discovery**
- Query `huggingface_hub.list_datasets()` for public datasets
- Filter: datasets with README.md AND created before 2026-08-19
- Stratified random sample: 7,000 datasets
- Output: `data/h-m2/hf_metadata.json`

**FR-2: OpenML Dataset Discovery**
- Query `openml.datasets.list_datasets()` for active datasets
- Filter: status='active' AND date < 2026-08-19
- Stratified random sample: 2,500 datasets
- Output: `data/h-m2/openml_metadata.json`

**FR-3: UCI Dataset Discovery**
- Web scrape dataset list from `archive.ics.uci.edu/ml/datasets`
- Filter: datasets with accessible description page
- Near-census sample: 500 datasets (all available)
- Output: `data/h-m2/uci_metadata.json`

**FR-4: Metadata Extraction per Platform**

**HuggingFace:**
- Fetch README.md + dataset card YAML via `huggingface_hub.hf_api.dataset_info()`
- Parse YAML frontmatter for: `source`, `homepage`, `date_created`
- Extract code blocks from README.md for preprocessing_code

**OpenML:**
- Fetch dataset metadata via `openml.datasets.get_dataset()`
- Parse XML for: `processing_script`, `url`, `version_date`

**UCI:**
- Fetch HTML description page via BeautifulSoup
- Extract: methodology section, source URL, publication date via CSS selectors

### 3.2 Cross-Platform Field Normalization

**FR-5: Semantic Field Mapping**

| Standard Field | HuggingFace Source | OpenML Source | UCI Source |
|---------------|-------------------|---------------|------------|
| **preprocessing_code** | Code snippets in README.md OR dataset card YAML | `processing_script` in XML | Methodology section in HTML |
| **data_source_url** | `source` OR `homepage` in YAML | `url` field in XML | Source URL in HTML |
| **collection_date** | `date_created` in YAML OR prose timestamp | `upload_date` OR `version_date` in XML | Publication date in HTML metadata |

**FR-6: Normalization Rules**
- Map platform-specific field names to standard schema
- Handle missing fields gracefully (null if absent)
- Preserve original platform field names in metadata for audit

### 3.3 Binary Field Presence Detection

**FR-7: Parsing Rules (per field)**

| Field | Presence Criteria | Rejection Criteria |
|-------|------------------|-------------------|
| **preprocessing_code** | >50 chars AND (language keywords: import/def/function OR file extension: .py/.R/.ipynb/.sh) | Empty placeholders ("TODO", "N/A"), <50 chars |
| **data_source_url** | Valid URL pattern (http/https + domain) | Broken links, localhost URLs, placeholder URLs |
| **collection_date** | Date pattern (YYYY-MM-DD, Month YYYY, YYYY) | Placeholder dates ("TBD", "Unknown"), invalid formats |

**FR-8: Binary Scoring**
- Each field scored: 0 (absent) OR 1 (present)
- Presence rate per platform: (datasets with field) / (total datasets) × 100

### 3.4 Statistical Analysis

**FR-9: Chi-Squared Test of Independence**
- Construct 2×2 contingency table per field (HF vs UCI):
  ```
           | Present | Absent |
  ---------|---------|--------|
  HF       | a       | b      |
  UCI      | c       | d      |
  ```
- Run `scipy.stats.chi2_contingency(observed)`
- Extract: chi-squared statistic, p-value, degrees of freedom
- Significance threshold: p < 0.05 (two-tailed)

**FR-10: Effect Size Calculation**
- Difference in proportions: `HF_rate - UCI_rate`
- Effect size threshold: ≥30 percentage points
- Report per field: preprocessing_code, data_source_url, collection_date

**FR-11: Gradient Analysis (Secondary)**
- Construct 3×3 contingency table (HF, OpenML, UCI)
- Run chi-squared test on full table
- Validate friction gradient: UCI < OpenML < HF

### 3.5 Validation Protocol

**FR-12: Parsing Accuracy Validation**
- Sample 100 datasets stratified per platform (50 HF, 30 OpenML, 20 UCI)
- Manual review: human annotator marks field presence (binary: 0/1)
- Calculate agreement: (automated matches manual) / (total samples)
- Threshold: >85% agreement required

**FR-13: Cross-Platform Semantic Validation**
- Sample 50 datasets per platform with field present (150 total)
- Manual review: verify semantic equivalence (HF preprocessing_code ≈ OpenML processing_script ≈ UCI methodology)
- Calculate semantic match rate: (semantically equivalent) / (total samples)
- Threshold: >80% semantic agreement required

---

## 4. Non-Functional Requirements

### 4.1 Performance
- **NFR-1:** Total runtime ≤4 hours for 10k+ dataset extraction + parsing + statistical test
- **NFR-2:** API rate limits respected (HF: 100 req/min, OpenML: 60 req/min)
- **NFR-3:** Parallel API calls where possible (async I/O for HF, OpenML)

### 4.2 Reliability
- **NFR-4:** Retry logic for API failures (3 retries with exponential backoff)
- **NFR-5:** Graceful handling of malformed HTML/XML/YAML (log errors, skip dataset)
- **NFR-6:** Checkpointing for partial progress (resume on failure)

### 4.3 Reproducibility
- **NFR-7:** Fixed random seed for stratified sampling (seed=42)
- **NFR-8:** Versioned dependencies (requirements.txt with pinned versions)
- **NFR-9:** Timestamped data extraction (all datasets fetched on 2026-08-19)

### 4.4 Validation
- **NFR-10:** Parsing accuracy >85% (validated via manual review)
- **NFR-11:** Semantic equivalence >80% (validated via manual inspection)
- **NFR-12:** No silent failures (all errors logged and reported)

---

## 5. Data Specifications

### 5.1 Input Data

**Source Platforms:**
1. **HuggingFace Datasets Hub** (huggingface.co/datasets) — friction=3
2. **OpenML** (openml.org) — friction=2
3. **UCI ML Repository** (archive.ics.uci.edu/ml/datasets) — friction=0

**Sample Sizes:**
- HuggingFace: 7,000 datasets (70% of total sample)
- OpenML: 2,500 datasets (25% of total sample)
- UCI: 500 datasets (5% of total sample, near-census)

**Temporal Scope:** Datasets published before 2026-08-19

### 5.2 Output Data

**Directory:** `/data/h-m2/`

| File | Format | Content | Size Estimate |
|------|--------|---------|--------------|
| `hf_metadata.json` | JSON | HuggingFace extracted metadata (7k datasets) | ~50 MB |
| `openml_metadata.json` | JSON | OpenML extracted metadata (2.5k datasets) | ~15 MB |
| `uci_metadata.json` | JSON | UCI extracted metadata (500 datasets) | ~3 MB |
| `presence_rates.csv` | CSV | Optional field presence rates per platform | <1 MB |
| `statistical_results.json` | JSON | Chi-squared test results + effect sizes | <1 MB |
| `validation_report.json` | JSON | Parsing accuracy + semantic validation results | <1 MB |

### 5.3 Metadata Schema (Normalized)

```json
{
  "dataset_id": "string (platform-specific ID)",
  "platform": "string (HF | OpenML | UCI)",
  "name": "string",
  "friction_score": "int (0-4)",
  "fields": {
    "preprocessing_code": {
      "present": "bool",
      "source_field": "string (platform-specific field name)",
      "value": "string | null"
    },
    "data_source_url": {
      "present": "bool",
      "source_field": "string",
      "value": "string | null"
    },
    "collection_date": {
      "present": "bool",
      "source_field": "string",
      "value": "string | null"
    }
  },
  "extraction_timestamp": "string (ISO 8601)"
}
```

---

## 6. Technical Constraints

### 6.1 API Rate Limits
- **HuggingFace:** 100 requests/minute (no auth), 1000 requests/minute (with token)
- **OpenML:** 60 requests/minute (no strict enforcement, but throttling observed)
- **UCI:** No API (web scraping only) — respect robots.txt, 1 req/sec max

### 6.2 Dependency Versions
- Python 3.9+
- `huggingface_hub>=0.20.0`
- `openml>=0.14.0`
- `beautifulsoup4>=4.12.0`
- `scipy>=1.11.0`
- `pandas>=2.0.0`
- `numpy>=1.24.0`
- `lxml>=4.9.0`
- `requests>=2.31.0`

### 6.3 Computational Resources
- **Memory:** ~4 GB RAM (for 10k+ dataset metadata in memory)
- **Disk:** ~100 MB for output artifacts
- **CPU:** 4+ cores recommended (parallel API calls)
- **Network:** Stable internet connection (API-dependent)

---

## 7. Risk Mitigation

### 7.1 Technical Risks

| Risk ID | Description | Likelihood | Impact | Mitigation |
|---------|-------------|-----------|--------|------------|
| **R1** | Parsing misclassification (false positives/negatives) | Medium | High | Explicit parsing rules (>50 chars + keywords) + validation (>85% accuracy) |
| **R3** | Cross-platform semantic mismatch | Medium | Medium | Semantic mapping + manual inspection (>80% agreement) |
| **R4** | Insufficient statistical power | Low | Medium | 10k+ sample provides power >0.99 for 20pp+ difference |
| **R6** | Platform size imbalance (UCI small) | High | Low | Report confidence intervals per platform; acknowledge UCI as near-census |
| **R7** | Temporal confounds (platform age) | Medium | Medium | Control for dataset publication date in sensitivity analysis |

### 7.2 Operational Risks

| Risk ID | Description | Likelihood | Impact | Mitigation |
|---------|-------------|-----------|--------|------------|
| **R8** | API rate limit exceeded | High | Medium | Exponential backoff + retry logic; use HF token for higher limits |
| **R9** | Web scraping blocked (UCI) | Medium | High | Respect robots.txt; rotate User-Agent; implement delays |
| **R10** | Malformed metadata (invalid JSON/XML/YAML) | Medium | Low | Graceful error handling; log errors; skip malformed datasets |

---

## 8. Success Metrics

### 8.1 Gate Evaluation (SHOULD_WORK)

**Primary Criteria (required for PASS):**
1. ✓ **Direction confirmed:** HF optional presence > UCI optional presence for all 3 fields
2. ✓ **Statistical significance:** p < 0.05 for HF vs UCI chi-squared test
3. ✓ **Substantial effect size:** HF - UCI difference ≥30 percentage points for ≥2/3 fields

**Secondary Criteria (desirable but not required):**
- Gradient effect: UCI < OpenML < HF (friction score order)
- Field consistency: Effect holds across all 3 optional fields
- Parsing accuracy: >85% agreement with manual review
- Semantic validity: >80% cross-platform field equivalence

**Acceptance Levels:**
- **Full PASS:** All primary + all secondary criteria met
- **Partial PASS:** All primary + 50%+ secondary criteria met
- **FAIL:** Any primary criterion failed

### 8.2 Expected Results (Based on Verification Plan)

| Field | HF Rate (Expected) | OpenML Rate (Expected) | UCI Rate (Expected) | HF-UCI Diff |
|-------|-------------------|----------------------|-------------------|-------------|
| **preprocessing_code** | 55-65% | 30-40% | <15% | ≥40pp |
| **data_source_url** | 60-70% | 35-45% | <20% | ≥40pp |
| **collection_date** | 50-60% | 25-35% | <10% | ≥40pp |

---

## 9. Deliverables

### 9.1 Code Artifacts

**Directory:** `/h-m2/`

| File | Purpose | Dependencies | Reuse from h-m1 |
|------|---------|-------------|-----------------|
| `config.py` | Hyperparameters, thresholds, platform URLs | None | ✓ (adapted) |
| `hf_extractor.py` | HuggingFace metadata extraction | `huggingface_hub` | ✓ |
| `openml_extractor.py` | OpenML metadata extraction | `openml-python` | ✓ |
| `uci_extractor.py` | UCI web scraping | BeautifulSoup | ✓ |
| `field_parser.py` | Optional field presence detection | None | ✓ (adapted) |
| `cross_platform_normalizer.py` | Field mapping logic | None | ✗ (new) |
| `statistical_analysis.py` | Chi-squared test, effect size | scipy | ✗ (new) |
| `validation.py` | Parsing + semantic validation | None | ✓ (adapted) |
| `main.py` | End-to-end pipeline orchestration | All above | ✓ (adapted) |

### 9.2 Data Artifacts

**Directory:** `/data/h-m2/`

| File | Content | Format |
|------|---------|--------|
| `hf_metadata.json` | HuggingFace extracted metadata (7k datasets) | JSON |
| `openml_metadata.json` | OpenML extracted metadata (2.5k datasets) | JSON |
| `uci_metadata.json` | UCI extracted metadata (500 datasets) | JSON |
| `presence_rates.csv` | Optional field presence rates per platform | CSV |
| `statistical_results.json` | Chi-squared test results + effect sizes | JSON |
| `validation_report.json` | Parsing + semantic validation results | JSON |

### 9.3 Report Artifacts

**Directory:** `/docs/youra_research/h-m2/`

| File | Content | Format |
|------|---------|--------|
| `04_validation.md` | Validation report (gate evaluation, findings, interpretation) | Markdown |
| `figures/presence_rates_barplot.png` | Visualization: optional field presence rates per platform | PNG |
| `figures/contingency_tables.png` | Visualization: contingency tables for chi-squared tests | PNG |

---

## 10. Timeline & Effort Estimate

**Phase 4 Implementation:** 1.5-2 days

| Step | Task | Duration | Parallelizable |
|------|------|----------|----------------|
| 1 | Reuse h-e1/h-m1 extractors (HF, OpenML, UCI) | 0.5 days | No |
| 2 | Implement cross-platform normalizer | 0.5 days | No |
| 3 | Run 10k+ dataset extraction | 0.5 days | Yes (parallel API calls) |
| 4 | Apply optional field parsing rules | 0.25 days | Yes (parallel per platform) |
| 5 | Run chi-squared tests + effect size calculation | 0.25 days | No |
| 6 | Validation (parsing accuracy + semantic check) | 0.5 days | Partially (manual review bottleneck) |
| 7 | Generate 04_validation.md report + figures | 0.25 days | No |

**Total:** ~2.75 days (can be shortened to 1.5 days if validation is streamlined)

---

## 11. Acceptance Criteria

### 11.1 Code Quality
- All Python code passes `flake8` linting (no errors)
- All functions have docstrings (Google style)
- Unit tests for field parsing rules (pytest, coverage >80%)
- Integration tests for end-to-end pipeline

### 11.2 Data Quality
- No null/missing dataset_ids in output metadata files
- All presence rates in [0, 100] range
- Statistical results include p-values, chi-squared stats, effect sizes

### 11.3 Validation Quality
- Parsing accuracy >85% (manual review validation)
- Semantic equivalence >80% (manual inspection validation)
- All validation results documented in `validation_report.json`

### 11.4 Reproducibility
- Fixed random seed (seed=42) for stratified sampling
- All dependencies pinned in `requirements.txt`
- Extraction timestamp logged in all output files

---

**PRD Complete** | **Next:** Architecture Design (03_architecture.md) | **Date:** 2026-08-19
