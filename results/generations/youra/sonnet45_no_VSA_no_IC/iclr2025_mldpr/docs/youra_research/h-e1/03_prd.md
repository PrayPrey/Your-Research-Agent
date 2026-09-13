# Product Requirements Document: H-E1 Friction Measurement Feasibility System

**Hypothesis ID:** h-e1  
**Product Version:** 1.0  
**Date:** 2026-08-19  
**PRD Owner:** Phase 3 Implementation Planning  

---

## 1. Executive Summary

### 1.1 Purpose

Build a metadata extraction and friction scoring system to validate that:
1. Platform friction-reduction features are objectively measurable from public documentation
2. 10,000+ dataset metadata records are extractable from OpenML, HuggingFace, and UCI repositories within 2-week timeframe without rate limiting barriers

### 1.2 Success Criteria

**MUST_WORK Gate (ALL required):**
- Friction scores assigned for 3 platforms with documented objective binary criteria
- Pilot extraction success rate: >80% (OpenML/HF), >70% (UCI)
- Parsing accuracy: >90% agreement with manual validation
- Throughput analysis confirms 10k extraction feasible within 336 hours

**Failure triggers immediate STOP.**

### 1.3 Scope

**In-Scope:**
- Friction scoring system (4 binary features × 3 platforms)
- API clients for OpenML and HuggingFace
- Web scraper for UCI repository
- Parsing rules for 6 metadata fields
- Pilot extraction (250 datasets: 100 OpenML, 100 HF, 50 UCI)
- Manual validation (100-dataset stratified sample)
- Throughput extrapolation analysis

**Out-of-Scope:**
- Full-scale 10k extraction (validated but not executed in h-e1)
- Statistical analysis of friction-completion correlations (h-m1/h-m2/h-m3)
- Baseline comparisons (Yang 2024, Strecker 2026, Batzner 2026)

---

## 2. Functional Requirements

### 2.1 Friction Scoring Module

**FR-1.1: Documentation Review Interface**
- Input: URLs to platform documentation (OpenML, HuggingFace, UCI)
- Output: Binary presence matrix (4 features × 3 platforms)
- Features to evaluate:
  1. Automated Field Extraction (API/tool auto-populates metadata from data files)
  2. Pre-filled Templates (templates with example values or auto-populated fields)
  3. Validation Feedback (real-time validation errors/warnings during metadata entry)
  4. Programmatic API Access (metadata submission via API, not just web forms)

**FR-1.2: Objective Criteria Documentation**
- For each binary assignment (0/1), system must store:
  - Evidence source (URL, section, screenshot reference)
  - Decision rationale (why scored 0 or 1)
  - Reviewer ID (for inter-rater reliability)
- Format: Structured markdown table

**FR-1.3: Composite Score Calculation**
- Formula: `friction_score = sum(4 binary features)`
- Range: 0-4 (integer)
- Expected scores:
  - HuggingFace: 3 (API=1, Templates=1, Validation=1, Auto-extraction=0)
  - OpenML: 2 (API=1, Templates=0, Validation=0, Auto-extraction=1)
  - UCI: 0 (all features absent)

---

### 2.2 Metadata Extraction Module

**FR-2.1: OpenML API Client**
- Library: `openml-python >=0.14.0`
- Methods:
  - `list_datasets(status="active", output_format="dataframe")` → dataset listing
  - `get_dataset(did)` → full metadata for dataset ID
- Target fields:
  - `collection_date` (optional)
  - `licence` (required)
  - `url` (required)
  - `original_data_url` (optional)
  - `paper_url` (optional)
  - `version` (required)
- Error handling: Retry logic (3 attempts with exponential backoff), timeout 30s per request
- Logging: Record success/failure per dataset ID

**FR-2.2: HuggingFace API Client**
- Libraries: `datasets >=2.0.0`, `huggingface_hub >=0.16.0`
- Methods:
  - `list_datasets()` → dataset listing
  - `DatasetCard.load(dataset_id)` → dataset card YAML + README
- Target fields:
  - `license` (from YAML frontmatter)
  - `dataset_info.version` (from YAML)
  - `source_url` / `homepage` (from YAML or README)
  - `preprocessing_code` (code snippets in card or linked files)
  - `collection_date` (if documented in card)
  - `dependencies` (from loading script or card)
- Error handling: Retry logic (3 attempts), timeout 30s, handle missing dataset cards gracefully
- Logging: Record success/failure per dataset ID

**FR-2.3: UCI Web Scraper**
- Libraries: `beautifulsoup4 >=4.12.0`, `requests >=2.31.0`
- Target: `archive.ics.uci.edu/ml/datasets/<dataset-name>.html`
- Rate limiting: 1 request/second (enforced with `time.sleep(1)`)
- Target fields:
  - `license` (parsed from HTML if present)
  - `version` / `date` (from dataset page metadata)
  - `data_source` (methodology text or external links)
  - `preprocessing_methodology` (text in "Data Set Information" section)
  - `dependencies` (software requirements if listed)
  - `collection_date` (from donation date or metadata)
- Error handling: Retry logic (3 attempts), timeout 30s, handle HTML structure changes gracefully
- Logging: Record success/failure per dataset name, log HTML parsing errors

**FR-2.4: Unified Data Schema**
- Output format: JSON or CSV with standardized field names
- Required fields per record:
  - `platform` (openml | huggingface | uci)
  - `dataset_id` (platform-specific identifier)
  - `extraction_timestamp` (ISO 8601)
  - `extraction_status` (success | failure)
  - `error_message` (if failure)
  - 6 target metadata fields (values or null)

---

### 2.3 Parsing Rules Module

**FR-3.1: Binary Presence Detection**
- Input: Raw metadata field value (string, list, or null)
- Output: Binary label (present=1, absent=0)
- Rules (see Section 3.4 of experiment brief):
  1. `preprocessing_code`: length >50 chars AND (language keywords OR code file extension)
  2. `data_source_url`: valid URL pattern AND length >10 chars
  3. `collection_date`: date format detected (ISO 8601, MM/DD/YYYY, YYYY)
  4. `license`: non-empty string AND length >5 chars (exclude placeholders "N/A", "Unknown")
  5. `version`: semantic version pattern OR version indicator (`v1`, `version 2`)
  6. `dependencies`: list with >0 elements OR text >20 chars with library/package names

**FR-3.2: Rule Configuration**
- Parameters must be configurable without code changes:
  - Length thresholds (e.g., 50 chars for preprocessing_code)
  - Keyword lists (e.g., `['import', 'function', 'def', 'library', 'require']`)
  - Regex patterns (URL, date, version)
  - Placeholder strings to exclude
- Format: YAML or JSON config file

**FR-3.3: Batch Processing**
- Apply parsing rules to all 6 fields across N datasets
- Output: Binary presence matrix (6 fields × N datasets)
- Performance: Process 100 datasets in <10 seconds

---

### 2.4 Validation Module

**FR-4.1: Manual Annotation Interface**
- Input: Stratified random sample (100 datasets: 40 OpenML, 40 HF, 20 UCI)
- Output: Ground truth binary labels (6 fields × 100 datasets = 600 labels)
- Interface: Spreadsheet or simple web form showing:
  - Raw metadata field value
  - Automated parsing result (present/absent)
  - Manual annotation field (checkbox or binary dropdown)
  - Notes field (for edge cases)

**FR-4.2: Accuracy Calculation**
- Metrics:
  - Overall accuracy: `(correct classifications) / 600 × 100`
  - Per-field accuracy: `(correct per field) / 100 × 100`
  - Confusion matrix: true positives, false positives, true negatives, false negatives
- Target: Overall >90%, all fields >75%

**FR-4.3: Inter-Rater Reliability (if multiple reviewers)**
- Calculate Cohen's kappa or percentage agreement
- Target: >90% agreement between reviewers

---

### 2.5 Throughput Analysis Module

**FR-5.1: Metrics Collection**
- Per extraction attempt, record:
  - `dataset_id`
  - `platform`
  - `start_time` (timestamp)
  - `end_time` (timestamp)
  - `duration_seconds` (end - start)
  - `status` (success | failure)

**FR-5.2: Throughput Calculation**
- Per-platform throughput: `(successful extractions) / (total time in hours)`
- Overall throughput: Weighted average or parallel execution model
- Extrapolation to 10k:
  - OpenML: `7000 / (OpenML throughput)` hours
  - HuggingFace: `2500 / (HF throughput)` hours
  - UCI: `500 / (UCI throughput)` hours
  - Total time = max(platform times) assuming parallel execution

**FR-5.3: Feasibility Report**
- Output: Markdown report with:
  - Pilot throughput per platform
  - Extrapolated time for 10k extraction
  - Feasibility verdict (within 336 hours: yes/no)
  - Optimization recommendations (if needed)

---

## 3. Non-Functional Requirements

### 3.1 Performance

**NFR-1: Extraction Speed**
- OpenML: Target >1000 records/hour
- HuggingFace: Target >800 records/hour
- UCI: Target >100 records/hour (web scraping constraint)

**NFR-2: Parsing Speed**
- Process 100 datasets in <10 seconds (all 6 parsing rules)

**NFR-3: Validation Throughput**
- Manual annotation: <1 minute per dataset (100 datasets in <2 hours)

### 3.2 Reliability

**NFR-4: Error Handling**
- Retry logic: 3 attempts with exponential backoff (1s, 2s, 4s)
- Timeout: 30 seconds per API request or web scrape
- Graceful degradation: Missing fields recorded as null, not failure

**NFR-5: Rate Limiting Compliance**
- UCI: Enforce 1 request/second (no faster)
- OpenML/HuggingFace: Respect HTTP 429 responses (implement backoff)

### 3.3 Data Quality

**NFR-6: Parsing Accuracy**
- Target: >90% overall agreement with manual validation
- Minimum per-field accuracy: >75%

**NFR-7: Success Rate**
- OpenML/HuggingFace: >80% successful extractions
- UCI: >70% successful extractions

### 3.4 Maintainability

**NFR-8: Configuration Externalization**
- All parsing thresholds, keywords, and regex patterns in config file (YAML/JSON)
- No hardcoded magic numbers in parsing logic

**NFR-9: Logging**
- Structured logging (JSON format)
- Log levels: DEBUG (raw metadata), INFO (success/failure), ERROR (exceptions)
- Log file per platform + aggregated log

**NFR-10: Code Modularity**
- Separate modules:
  - `extractors/` (openml.py, huggingface.py, uci.py)
  - `parsers/` (parsing_rules.py, config loader)
  - `validators/` (manual_annotation.py, accuracy_calculator.py)
  - `analysis/` (throughput.py, gate_evaluator.py)

---

## 4. Technical Constraints

### 4.1 Platform Dependencies

**TC-1: OpenML API**
- Dependency: `openml-python >=0.14.0`
- Constraint: Public API, no authentication required (read-only access)
- Known limitation: API may have undocumented rate limits (monitor 429 responses)

**TC-2: HuggingFace API**
- Dependencies: `datasets >=2.0.0`, `huggingface_hub >=0.16.0`
- Constraint: Public API, optional authentication for higher rate limits
- Known limitation: Not all datasets have dataset cards (expect ~10% missing)

**TC-3: UCI Repository**
- Dependencies: `beautifulsoup4 >=4.12.0`, `requests >=2.31.0`
- Constraint: No public API, web scraping only
- Known limitation: HTML structure may change without notice (brittle)

### 4.2 Data Constraints

**TC-4: Pilot Sample Size**
- OpenML: 100 datasets (sampled from ~7,000 active)
- HuggingFace: 100 datasets (sampled from ~50,000 available)
- UCI: 50 datasets (sampled from ~500 total)
- Total: 250 datasets for pilot

**TC-5: Validation Sample Size**
- 100 datasets for manual annotation (40 OpenML, 40 HF, 20 UCI)
- Stratified random sampling from pilot extraction

### 4.3 Timeline Constraints

**TC-6: Phase Durations**
- Phase 1 (Setup): Days 1-2
- Phase 2 (Friction Scoring): Day 3
- Phase 3 (Pilot Extraction): Days 4-7
- Phase 4 (Parsing Validation): Days 8-10
- Phase 5 (Throughput Analysis): Days 11-12
- Phase 6 (Documentation): Days 13-14
- **Total: 14 days (2 weeks)**

**TC-7: Human Effort Budget**
- Total: ~11 person-days (within 14-day timeline)

---

## 5. User Stories

### 5.1 Friction Scoring

**US-1: As a researcher, I want to assign objective friction scores to ML platforms so that I can quantitatively compare friction-reduction features.**

**Acceptance Criteria:**
- Friction scores assigned for OpenML, HuggingFace, UCI
- Each binary feature assignment has documented evidence and rationale
- Inter-rater reliability >90% (if multiple reviewers)

---

### 5.2 Metadata Extraction

**US-2: As a data engineer, I want to extract metadata from 250 datasets across 3 platforms so that I can validate extraction feasibility.**

**Acceptance Criteria:**
- 100 OpenML datasets extracted with >80% success rate
- 100 HuggingFace datasets extracted with >80% success rate
- 50 UCI datasets extracted with >70% success rate
- All extractions logged with timestamps and error messages

---

### 5.3 Parsing Validation

**US-3: As a data scientist, I want to validate parsing accuracy against manual annotations so that I can trust automated field detection.**

**Acceptance Criteria:**
- 100-dataset stratified sample manually annotated (6 fields each)
- Overall parsing accuracy >90%
- Per-field accuracy report generated
- Confusion matrix showing false positives and false negatives

---

### 5.4 Throughput Analysis

**US-4: As a project manager, I want to know if 10,000 datasets are extractable within 2 weeks so that I can approve full-scale data collection.**

**Acceptance Criteria:**
- Pilot throughput calculated per platform
- Extrapolated time for 10k datasets estimated
- Feasibility report states yes/no for 336-hour threshold
- Optimization plan provided if throughput insufficient

---

## 6. Data Flow

```
[Platform Documentation] → [Friction Scoring Module] → [Friction Score Report (markdown)]

[OpenML API] → [OpenML Client] → [Raw Metadata JSON]
[HuggingFace API] → [HF Client] → [Raw Metadata JSON]
[UCI Website] → [UCI Scraper] → [Raw Metadata JSON]

[Raw Metadata JSON] → [Parsing Rules Module] → [Binary Presence Matrix (CSV)]

[Binary Presence Matrix (subset)] → [Manual Annotation Interface] → [Ground Truth Labels (CSV)]

[Binary Presence Matrix + Ground Truth] → [Validation Module] → [Accuracy Report (markdown)]

[Extraction Logs] → [Throughput Analysis Module] → [Feasibility Report (markdown)]

[All Reports] → [Gate Evaluator] → [PASS/FAIL Decision]
```

---

## 7. Deliverables

| Deliverable | Format | Timeline | Owner |
|-------------|--------|----------|-------|
| Friction Scoring Report | Markdown table | Day 3 | Researcher |
| OpenML API Client | Python module | Days 1-2 | Data Engineer |
| HuggingFace API Client | Python module | Days 1-2 | Data Engineer |
| UCI Web Scraper | Python module | Days 1-2 | Data Engineer |
| Parsing Rules Module | Python module + config YAML | Days 1-2 | Data Engineer |
| Pilot Extraction Dataset | JSON/CSV (250 records) | Days 4-7 | Data Engineer |
| Pilot Metrics Report | Markdown | Day 7 | Data Engineer |
| Validation Dataset | CSV (100 records × 6 fields) | Days 8-10 | Data Scientist |
| Parsing Accuracy Report | Markdown | Day 10 | Data Scientist |
| Throughput Extrapolation Report | Markdown | Days 11-12 | Data Scientist |
| Gate Evaluation Report | Markdown (PASS/FAIL) | Day 12 | Project Manager |
| Final h-e1 Experiment Report | Markdown (comprehensive) | Days 13-14 | Researcher |

---

## 8. Risk Mitigation

| Risk ID | Description | Mitigation | Fallback |
|---------|-------------|------------|----------|
| **R1** | Parsing misclassification (placeholders marked as "present") | Strict parsing rules (>50 chars + keywords), manual validation target >90% | Refine rules if 80-90% accuracy; major revision if <80% |
| **R2** | UCI scraping failures (HTML structure changes) | Robust parsing (handle missing elements), rate limiting (1 req/sec), target >70% success | Accept 50-70% success; abandon UCI if <50% |
| **R3** | API rate limiting blocks 10k extraction | Pilot throughput testing, batch requests, parallel execution, exponential backoff | Reduce parallelism, extend timeline to 3 weeks if rate limits detected |

---

## 9. Success Metrics (MUST_WORK Gate)

| Metric | Target | Gate Condition |
|--------|--------|----------------|
| Friction Score Objectivity | Binary (yes/no) | **MUST be yes** |
| Extraction Success Rate (OpenML/HF) | >80% | **MUST exceed 80%** |
| Extraction Success Rate (UCI) | >70% | **MUST exceed 70%** |
| Parsing Accuracy | >90% | **MUST exceed 90%** |
| 10k Feasibility | <336 hours | **MUST be <336 hours** |

**If ANY metric fails gate condition → IMMEDIATE STOP (hypothesis h-e1 fails MUST_WORK gate)**

---

## 10. Open Questions

**OQ-1:** Should we implement parallel processing for OpenML/HF extraction in pilot phase, or only in throughput optimization?
- **Decision needed by:** Day 4 (before pilot extraction)
- **Impact:** Throughput estimates, code complexity

**OQ-2:** If UCI success rate falls between 50-70%, do we proceed with degraded data quality or abandon UCI entirely?
- **Decision needed by:** Day 7 (after pilot extraction)
- **Impact:** Platform comparison validity

**OQ-3:** If parsing accuracy is 85-90% (below target but above minimum), do we refine rules or accept the accuracy?
- **Decision needed by:** Day 10 (after validation)
- **Impact:** Timeline (re-validation adds 2-3 days)

---

## 11. Appendix: Field Definitions

### 11.1 Target Metadata Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `preprocessing_code` | string/code | No | Code snippets or scripts for data preprocessing |
| `data_source_url` | URL | No | Original data source URL |
| `collection_date` | date | No | Date when dataset was collected |
| `license` | string | Yes | License type (e.g., "MIT", "CC-BY-4.0") |
| `version` | string | Yes | Dataset version identifier |
| `dependencies` | list/string | No | Software dependencies or libraries required |

### 11.2 Friction-Reduction Features

| Feature | Definition | Example (Present) | Example (Absent) |
|---------|------------|-------------------|------------------|
| Automated Field Extraction | Platform provides API/tool to auto-populate metadata from data files | OpenML's auto-extraction from ARFF files | Manual entry only |
| Pre-filled Templates | Platform provides templates with example values or auto-populated fields | HuggingFace dataset card templates | Blank forms |
| Validation Feedback | Real-time validation errors/warnings during metadata entry | HuggingFace YAML syntax validation | No validation |
| Programmatic API Access | Metadata submission via API (not just web forms) | OpenML Python API, HF Hub API | Web form only (UCI) |

---

**End of PRD**

**Next Steps:** Architecture design (03_architecture.md), Logic design (03_logic.md), Configuration design (03_config.md)
