# Experiment Brief: H-E1 Friction Measurement Feasibility

**Hypothesis ID:** h-e1  
**Hypothesis Type:** EXISTENCE  
**Gate:** MUST_WORK  
**Date Generated:** 2026-08-19  

---

## 1. Hypothesis Statement

Platform friction-reduction features (automated extraction, pre-filled templates, validation feedback, API access) are objectively measurable from public documentation, and 10,000+ dataset metadata records are extractable from OpenML, HuggingFace, and UCI repositories within 2-week timeframe without rate limiting.

**Rationale:** Foundation hypothesis validating methodology feasibility. Proves that friction scoring (0-4 binary features) can be objectively assigned and that 10k+ dataset sample is extractable within 2-week timeframe without rate limiting barriers.

---

## 2. Research Context

### 2.1 Prior Work Integration

**Referenced Studies:**
- Yang 2024: Analyzed 7,433 HuggingFace datasets for completion heterogeneity (single platform, no cross-platform friction measurement)
- Batzner 2026: Automated converters enabled 22,235+ model evaluation entries (demonstrates friction-reduction scalability, different domain)
- Strecker 2026: Metadata conflict taxonomy across 8 repositories (qualitative, not quantitative presence rates)

**Gap Addressed:** No prior study has quantitatively measured platform friction-reduction features across multiple ML repositories (OpenML, HF, UCI) at 10,000+ scale with objective binary criteria.

### 2.2 Implementation Landscape (from Exa Search)

**Identified Code Examples:**
1. `stephlabou/comparative-machine-learning-metadata`: Cross-platform metadata extraction from OpenML, UCI, HuggingFace, Kaggle (demonstrates feasibility pattern)
2. `openml-python`: Official API client with `datasets.list_datasets()`, `datasets.get_dataset()` methods
3. `datasets` (HuggingFace): Hub API with Croissant metadata support, dataset card parsing
4. BeautifulSoup web scraping: Standard pattern for UCI (no public API as of project timepoint)

**Key Technical Patterns:**
- OpenML metadata fields: `collection_date`, `licence`, `url`, `original_data_url`, `paper_url`, `creator`, `contributor`, `version`
- HuggingFace dataset cards: YAML frontmatter with `license`, `dataset_info.version`, source URLs, code snippets
- Binary field presence validation: Content length thresholds + keyword matching (e.g., preprocessing_code >50 chars + language keywords)

### 2.3 Archon Knowledge Base Search

**Status:** Archon MCP tools unavailable during this session (server connection timeout).  
**Mitigation:** Proceeded with Exa search results and verification plan specifications. Future iterations should retry Archon search for past experiment cases on metadata extraction, API rate limiting, and parsing rule validation.

---

## 3. Dataset Preparation

### 3.1 Dataset Type

**Type:** programmatic-api (real data from OpenML, HuggingFace, UCI repositories)

**Justification:** 
- Avoids synthetic data failure pattern (h-e1 requires real platform metadata)
- Enables objective measurement of actual platform friction features
- Provides authentic API rate limiting testing (not simulatable)

### 3.2 Dataset Specifications

**Platform 1: OpenML**
- **Source:** OpenML API via `openml-python` library
- **Access Method:** `openml.datasets.list_datasets(status="active", output_format="dataframe")`
- **Pilot Sample Size:** 100 datasets
- **Target Fields:** 
  - `collection_date` (optional)
  - `licence` (required)
  - `url` (required)
  - `original_data_url` (optional)
  - `paper_url` (optional)
  - `version` (required)
- **Expected Friction Score:** 2 (API access + partial automation, no pre-filled templates/validation)

**Platform 2: HuggingFace**
- **Source:** HuggingFace Hub API via `datasets` library + `huggingface_hub`
- **Access Method:** `datasets.list_datasets()` + dataset card YAML parsing
- **Pilot Sample Size:** 100 datasets
- **Target Fields:**
  - `license` (from YAML frontmatter)
  - `dataset_info.version` (from YAML)
  - `source_url` / `homepage` (from YAML or README)
  - `preprocessing_code` (code snippets in dataset card or linked files)
  - `collection_date` (if documented in card)
  - `dependencies` (from dataset loading script or card)
- **Expected Friction Score:** 3 (API access + templates + partial validation, no full automated extraction)

**Platform 3: UCI Machine Learning Repository**
- **Source:** Web scraping via `archive.ics.uci.edu/ml/datasets`
- **Access Method:** BeautifulSoup HTML parsing with rate limiting (1 request/second)
- **Pilot Sample Size:** 50 datasets (lower due to scraping complexity)
- **Target Fields:**
  - `license` (parsed from HTML if present)
  - `version` / `date` (from dataset page metadata)
  - `data_source` (methodology text or external links)
  - `preprocessing_methodology` (text descriptions in "Data Set Information")
  - `dependencies` (software requirements if listed)
  - `collection_date` (from dataset donation date or metadata)
- **Expected Friction Score:** 0 (manual web forms only, no API/automation/templates/validation as of project timepoint)

### 3.3 Data Collection Protocol

**Pilot Phase (Week 1):**
1. Implement API clients:
   - OpenML: `openml.datasets.list_datasets()` → filter active → sample 100
   - HuggingFace: `datasets.list_datasets()` → sample 100 → fetch dataset cards
2. Implement UCI scraper:
   - Target: `archive.ics.uci.edu/ml/datasets.php` dataset listing
   - Parse dataset detail pages with BeautifulSoup
   - Rate limiting: 1 request/second (3600 datasets/hour theoretical max)
   - Sample 50 datasets for pilot
3. Apply parsing rules (see Section 3.4)
4. Record success/failure for each extraction attempt

**Full-Scale Extrapolation (if pilot succeeds):**
- OpenML: ~7,000 datasets (list_datasets returns ~7k active as of 2026)
- HuggingFace: ~2,500 datasets (stratified sample from 50k+ available)
- UCI: ~500 datasets (full repository size as of timepoint)
- **Total:** 10,000 datasets
- **Timeline:** 2 weeks (batch API requests for OpenML/HF, parallel scraping for UCI with rate limits)

### 3.4 Parsing Rules (Binary Presence Detection)

**Rule Set:**
1. **preprocessing_code:**
   - Present: Field length >50 characters AND (contains language keywords {`import`, `function`, `def`, `library`, `require`} OR file extension {`.py`, `.R`, `.ipynb`, `.jl`})
   - Absent: Otherwise

2. **data_source_url:**
   - Present: Valid URL pattern detected (regex: `http(s)?://[^\s]+`) AND length >10 chars
   - Absent: Otherwise

3. **collection_date:**
   - Present: Date format detected (ISO 8601 `YYYY-MM-DD`, `MM/DD/YYYY`, or year-only `YYYY` with context)
   - Absent: Otherwise

4. **license:**
   - Present: Non-empty string AND length >5 characters (excludes placeholder "N/A", "Unknown")
   - Absent: Otherwise or if placeholder detected

5. **version:**
   - Present: Semantic version pattern (`X.Y.Z`) OR non-empty string with version indicator (`v1`, `version 2`)
   - Absent: Otherwise

6. **dependencies:**
   - Present: List/array with >0 elements OR text field length >20 characters with library/package names
   - Absent: Otherwise

**Validation Protocol:**
- Manual review of 100-dataset stratified subset (40 OpenML, 40 HF, 20 UCI)
- Compare automated parsing results to human-annotated ground truth
- Calculate accuracy: (correct presence/absence classifications) / (6 fields × 100 datasets) × 100
- **Target:** >90% agreement

---

## 4. Baseline Experiments

**Note:** h-e1 is an EXISTENCE hypothesis (feasibility validation). No baseline comparison is performed. This hypothesis establishes prerequisites for later mechanism hypotheses (h-m1, h-m2, h-m3) which will compare against Yang 2024, Strecker 2026, and Batzner 2026 baselines.

---

## 5. Experiment Design

### 5.1 Experiment 1: Friction Score Assignment

**Objective:** Validate that friction-reduction features are objectively measurable from platform documentation.

**Method:**
1. Review public documentation for each platform (OpenML docs, HuggingFace docs, UCI website)
2. Evaluate presence/absence of 4 friction-reduction features:
   - **Feature 1 - Automated Field Extraction:** Platform provides API or tool to auto-populate metadata fields from data files (binary: yes/no)
   - **Feature 2 - Pre-filled Templates:** Platform provides templates with example values or auto-populated fields (binary: yes/no)
   - **Feature 3 - Validation Feedback:** Platform provides real-time validation errors or warnings during metadata entry (binary: yes/no)
   - **Feature 4 - Programmatic API Access:** Platform allows metadata submission via API (not just web forms) (binary: yes/no)
3. Assign binary score (0/1) per feature per platform
4. Calculate composite friction score: sum of 4 binary scores (range 0-4)
5. Document objective criteria for each binary assignment

**Expected Outcomes:**
- HuggingFace: Score 3 (API=1, Templates=1, Validation=1, Auto-extraction=0)
- OpenML: Score 2 (API=1, Templates=0, Validation=0, Auto-extraction=1)
- UCI: Score 0 (API=0, Templates=0, Validation=0, Auto-extraction=0)

**Success Criteria:**
- Primary: Friction scores successfully assigned for all 3 platforms with documented objective binary criteria
- Secondary: Inter-rater reliability >90% (if multiple reviewers assess documentation)

**Failure Response:**
- IF scoring subjective (inter-rater agreement <80%): PIVOT to simpler feature detection (API presence only, score 0-1)

---

### 5.2 Experiment 2: Pilot Metadata Extraction

**Objective:** Validate that 10,000+ dataset metadata records are extractable within 2-week timeframe without rate limiting barriers.

**Method:**
1. **Implementation:**
   - OpenML client: `import openml; datasets = openml.datasets.list_datasets(status="active", output_format="dataframe"); sample_ids = datasets.sample(100)['did']; records = [openml.datasets.get_dataset(did) for did in sample_ids]`
   - HuggingFace client: `from datasets import list_datasets; from huggingface_hub import DatasetCard; datasets_list = list(list_datasets())[:100]; cards = [DatasetCard.load(d.id) for d in datasets_list]`
   - UCI scraper: BeautifulSoup parser targeting `archive.ics.uci.edu/ml/datasets/<dataset-name>.html` with rate limiting (1 req/sec)

2. **Execution:**
   - Run pilot extraction: 100 OpenML + 100 HF + 50 UCI = 250 total datasets
   - Record per-platform metrics:
     - Success count (valid metadata returned)
     - Failure count (API error, timeout, missing fields, parsing error)
     - Extraction time (seconds per dataset)
   - Calculate success rate: (success count) / (total attempts) × 100
   - Calculate throughput: (successful extractions) / (total time in hours)

3. **Extrapolation to Full Scale:**
   - Estimate time for 10k extraction: (10,000 datasets) / (pilot throughput records/hour)
   - Validate <2-week feasibility: estimated time <336 hours (14 days × 24 hours)
   - Account for rate limits: UCI scraping limited to 3600 requests/hour, plan parallel execution

**Expected Outcomes:**
- OpenML success rate: >95% (mature API, reliable)
- HuggingFace success rate: >90% (some datasets may lack cards)
- UCI success rate: >70% (web scraping variability, HTML structure changes)
- Overall throughput: >500 records/hour (with parallel execution)
- Extrapolated time for 10k: ~20 hours (well within 2-week window)

**Success Criteria:**
- Primary: Pilot extraction achieves >80% success rate for OpenML/HF, >70% for UCI
- Secondary: Throughput analysis confirms 10k+ extraction feasible within 2-week window (<336 hours estimated)

**Failure Response:**
- IF OpenML/HF success rate <80%: INVESTIGATE API errors, retry logic, PIVOT to smaller sample if persistent failures
- IF UCI success rate <50%: EXPLORE alternative repositories (Kaggle, Papers With Code) OR ABANDON UCI (2-platform comparison)
- IF throughput projects >336 hours: OPTIMIZE parallel execution, REDUCE sample size to 7-8k, or EXTEND timeline to 3 weeks

---

### 5.3 Experiment 3: Parsing Rule Validation

**Objective:** Validate binary field presence detection accuracy via manual review.

**Method:**
1. **Sample Selection:**
   - Stratified random sample from pilot extraction: 100 datasets total
     - 40 from OpenML (proportional to pilot size)
     - 40 from HuggingFace (proportional to pilot size)
     - 20 from UCI (proportional to pilot size)

2. **Automated Parsing:**
   - Apply parsing rules (Section 3.4) to all 6 target fields across 100 datasets
   - Record binary presence/absence per field per dataset
   - Total classifications: 6 fields × 100 datasets = 600 binary labels

3. **Manual Ground Truth Annotation:**
   - Human reviewer inspects raw metadata for each of 100 datasets
   - Manually annotates presence/absence for 6 fields using same definitions as parsing rules
   - Records decisions in validation spreadsheet

4. **Accuracy Calculation:**
   - Compare automated parsing results to manual annotations
   - Calculate per-field accuracy: (correct classifications) / (100 datasets) × 100
   - Calculate overall accuracy: (total correct) / (600 classifications) × 100
   - Identify confusion patterns: false positives (automated says present, manual says absent) vs false negatives

**Expected Outcomes:**
- Overall parsing accuracy: >90%
- Per-field accuracy:
  - `license`: >95% (structured field, low ambiguity)
  - `version`: >90% (pattern-based, some edge cases)
  - `data_source_url`: >95% (URL pattern clear)
  - `collection_date`: >85% (date format variability)
  - `preprocessing_code`: >85% (keyword matching may miss edge cases)
  - `dependencies`: >80% (highest ambiguity, text vs list formats)

**Success Criteria:**
- Primary: Overall parsing accuracy >90% agreement with manual review
- Secondary: No single field <75% accuracy (validates rule quality across all fields)

**Failure Response:**
- IF overall accuracy <80%: REVISE parsing rules (stricter thresholds, add keyword lists, improve regex patterns)
- IF specific field <70%: SCOPE reduction (drop problematic field from analysis) OR MANUAL annotation (not scalable to 10k)
- IF false positive rate >20%: INCREASE thresholds (e.g., preprocessing_code requires >100 chars instead of >50)

---

## 6. Evaluation Metrics

### 6.1 Primary Metrics

| Metric | Definition | Target | Gate Condition |
|--------|------------|--------|----------------|
| **Friction Score Objectivity** | Binary: Friction scores successfully assigned with documented criteria (yes/no) | Yes | MUST_WORK: Yes |
| **Extraction Success Rate (OpenML/HF)** | (Successful extractions) / (Total attempts) × 100 for OpenML and HuggingFace | >80% | MUST_WORK: >80% |
| **Extraction Success Rate (UCI)** | (Successful extractions) / (Total attempts) × 100 for UCI | >70% | MUST_WORK: >70% |
| **Parsing Accuracy** | (Correct presence/absence labels) / (600 total field classifications) × 100 | >90% | MUST_WORK: >90% |
| **10k Feasibility** | Extrapolated time for 10,000-dataset extraction <336 hours (yes/no) | Yes | MUST_WORK: Yes |

### 6.2 Secondary Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| **Extraction Throughput** | (Successful records extracted) / (Total time in hours) | >500 records/hour |
| **Per-Platform Throughput** | Breakdown by OpenML, HuggingFace, UCI | OpenML >1000/hr, HF >800/hr, UCI >100/hr |
| **Per-Field Parsing Accuracy** | Accuracy for each of 6 fields individually | All fields >75% |
| **False Positive Rate** | (Automated=present, Manual=absent) / (Manual absent count) × 100 | <15% |
| **False Negative Rate** | (Automated=absent, Manual=present) / (Manual present count) × 100 | <15% |

---

## 7. Success Criteria & Gate Conditions

### 7.1 MUST_WORK Gate (h-e1)

**Pass Conditions (ALL must be met):**
1. Friction scores assigned for all 3 platforms (HF, OpenML, UCI) with objective binary criteria documented
2. Pilot extraction success rate: >80% for OpenML and HuggingFace
3. Pilot extraction success rate: >70% for UCI
4. Parsing accuracy: >90% overall agreement with manual review
5. Throughput extrapolation confirms 10k extraction feasible within 2-week window

**Fail Conditions (ANY triggers STOP):**
- Friction scoring subjective (inter-rater agreement <80%, no objective criteria)
- OpenML or HuggingFace extraction success rate <70%
- UCI extraction success rate <50% (below minimum for meaningful comparison)
- Parsing accuracy <80% (measurement unreliable)
- Throughput extrapolation >336 hours without feasible optimization

**Contingency Actions:**
- IF friction scoring fails: PIVOT to simpler binary feature (API presence only, score 0-1)
- IF OpenML/HF extraction fails: INVESTIGATE errors, REDUCE sample, PIVOT to single platform
- IF UCI extraction fails: ABANDON UCI, proceed with 2-platform comparison (OpenML + HF)
- IF parsing accuracy fails: REVISE rules, SCOPE reduction (fewer fields), or MANUAL annotation
- IF throughput fails: OPTIMIZE parallelization, REDUCE sample to 7k, or EXTEND timeline to 3 weeks

---

## 8. Implementation Plan

### 8.1 Phase 1: Setup (Days 1-2)

**Tasks:**
1. Install dependencies: `pip install openml datasets huggingface_hub beautifulsoup4 requests pandas`
2. Implement OpenML client wrapper:
   ```python
   import openml
   def extract_openml_metadata(dataset_id):
       dataset = openml.datasets.get_dataset(dataset_id)
       return {
           'platform': 'openml',
           'id': dataset_id,
           'collection_date': dataset.collection_date,
           'licence': dataset.licence,
           'url': dataset.url,
           'original_data_url': dataset.original_data_url,
           'paper_url': dataset.paper_url,
           'version': dataset.version
       }
   ```
3. Implement HuggingFace client wrapper:
   ```python
   from datasets import list_datasets
   from huggingface_hub import DatasetCard
   def extract_hf_metadata(dataset_id):
       card = DatasetCard.load(dataset_id)
       card_data = card.data.to_dict() if card.data else {}
       return {
           'platform': 'huggingface',
           'id': dataset_id,
           'license': card_data.get('license'),
           'version': card_data.get('dataset_info', {}).get('version'),
           'source_url': card_data.get('source_datasets') or card_data.get('homepage'),
           'preprocessing_code': extract_code_from_card(card.text),  # helper function
           'collection_date': None,  # rarely documented
           'dependencies': card_data.get('requires')
       }
   ```
4. Implement UCI scraper:
   ```python
   import requests
   from bs4 import BeautifulSoup
   import time
   def extract_uci_metadata(dataset_name):
       url = f"https://archive.ics.uci.edu/ml/datasets/{dataset_name}"
       response = requests.get(url)
       soup = BeautifulSoup(response.content, 'html.parser')
       time.sleep(1)  # rate limiting
       return {
           'platform': 'uci',
           'name': dataset_name,
           'license': parse_license_from_html(soup),  # helper function
           'version': parse_version_from_html(soup),
           'data_source': parse_data_source(soup),
           'preprocessing_methodology': parse_methodology(soup),
           'dependencies': parse_dependencies(soup),
           'collection_date': parse_collection_date(soup)
       }
   ```
5. Implement parsing rules module (6 functions, one per field)

**Deliverables:**
- Working API clients for OpenML, HuggingFace
- Working UCI web scraper with rate limiting
- Parsing rules module with unit tests

---

### 8.2 Phase 2: Friction Score Assignment (Day 3)

**Tasks:**
1. Review documentation:
   - OpenML: https://openml.github.io/openml-python/main/
   - HuggingFace: https://huggingface.co/docs/datasets/ and https://huggingface.co/docs/hub/datasets-cards
   - UCI: https://archive.ics.uci.edu/
2. Evaluate 4 friction features per platform (see Experiment 1 method)
3. Document binary criteria for each feature assignment
4. Calculate composite friction scores
5. Create friction scoring report (markdown table)

**Deliverables:**
- Friction scoring report with objective criteria (Markdown file)
- Expected friction scores validated or adjusted based on documentation review

---

### 8.3 Phase 3: Pilot Extraction (Days 4-7)

**Tasks:**
1. **Day 4:** OpenML pilot (100 datasets)
   - Sample 100 random active dataset IDs
   - Execute extraction with error handling
   - Record success/failure, timing per dataset
2. **Day 5:** HuggingFace pilot (100 datasets)
   - Sample 100 dataset IDs from list_datasets()
   - Extract dataset cards and parse metadata
   - Record success/failure, timing per dataset
3. **Day 6-7:** UCI pilot (50 datasets)
   - Identify 50 dataset names from main listing page
   - Scrape dataset detail pages with rate limiting
   - Record success/failure, timing per dataset
4. Aggregate pilot metrics:
   - Per-platform success rates
   - Per-platform throughput (records/hour)
   - Error taxonomy (API errors, parsing failures, missing fields)

**Deliverables:**
- Pilot extraction dataset (250 records in JSON or CSV)
- Pilot metrics report (success rates, throughput, error analysis)

---

### 8.4 Phase 4: Parsing Rule Validation (Days 8-10)

**Tasks:**
1. **Day 8:** Sample selection and automated parsing
   - Stratified random sample: 40 OpenML, 40 HF, 20 UCI
   - Apply parsing rules to 6 fields × 100 datasets = 600 labels
   - Export automated labels to validation spreadsheet
2. **Day 9:** Manual annotation
   - Human reviewer inspects raw metadata for 100 datasets
   - Manually annotates presence/absence for 6 fields
   - Records annotations in validation spreadsheet (alongside automated labels)
3. **Day 10:** Accuracy calculation and analysis
   - Compare automated vs manual labels
   - Calculate overall accuracy, per-field accuracy
   - Analyze false positives and false negatives
   - Identify parsing rule refinements needed

**Deliverables:**
- Validation spreadsheet (100 datasets × 6 fields, automated + manual labels)
- Parsing accuracy report (overall, per-field, confusion matrix)

---

### 8.5 Phase 5: Throughput Extrapolation & Gate Evaluation (Days 11-12)

**Tasks:**
1. Calculate throughput per platform from pilot data
2. Estimate time for full-scale extraction (10,000 datasets):
   - OpenML: 7,000 datasets / (OpenML throughput)
   - HuggingFace: 2,500 datasets / (HF throughput)
   - UCI: 500 datasets / (UCI throughput)
   - Total time = max(platform times) assuming parallel execution
3. Validate <336 hour threshold (2 weeks)
4. Document optimization strategies if needed (parallelization, batch requests)
5. Evaluate MUST_WORK gate:
   - Check all 5 pass conditions (Section 7.1)
   - Document gate decision (PASS/FAIL)
   - If FAIL, document contingency actions taken

**Deliverables:**
- Throughput extrapolation report (with optimization plan if needed)
- Gate evaluation report (PASS/FAIL with justification)

---

### 8.6 Phase 6: Documentation & Handoff to Phase 3 (Days 13-14)

**Tasks:**
1. Compile final experiment report:
   - Executive summary (gate result, key findings)
   - Friction score assignments (with criteria)
   - Pilot extraction results (success rates, throughput)
   - Parsing validation results (accuracy, refinements)
   - Full-scale feasibility analysis
   - Recommendations for h-m1/h-m2/h-m3 experiments
2. Archive code and data:
   - API client code (versioned)
   - Pilot extraction dataset (250 records)
   - Validation dataset (100 records with manual annotations)
   - Parsing rules module (refined version)
3. Prepare inputs for Phase 3 (Implementation Planning):
   - Validated extraction methodology
   - Friction scores for 3 platforms
   - Parsing accuracy baseline

**Deliverables:**
- Final h-e1 experiment report (Markdown)
- Code repository (GitHub or local archive)
- Data artifacts (pilot dataset, validation dataset)

---

## 9. Risk Assessment & Mitigation

### 9.1 High-Risk Items

| Risk ID | Description | Probability | Impact | Mitigation |
|---------|-------------|-------------|--------|------------|
| **R1** | Parsing misclassification (empty placeholders marked as "present") | Medium | High | Explicit parsing rules (>50 chars + keywords), 100-sample manual validation, target >90% accuracy |
| **R2** | UCI web scraping failures (HTML structure changes, rate limiting) | Medium | Medium | Lower success rate threshold (>70%), fallback to 2-platform comparison if <50% |
| **R3** | API rate limiting blocks 10k extraction | Low | High | Pilot throughput testing, batch requests, parallel execution, retry logic with exponential backoff |

### 9.2 Mitigation Strategies (Detailed)

**Risk R1: Parsing Misclassification**
- **Prevention:** 
  - Strict parsing rules: e.g., `preprocessing_code` requires >50 chars AND language keywords (not just length)
  - Placeholder detection: exclude common placeholders ("N/A", "Unknown", "TODO")
- **Detection:** 100-sample manual validation with accuracy target >90%
- **Response:** 
  - IF accuracy 80-90%: Refine rules (increase thresholds, expand keyword lists)
  - IF accuracy <80%: Major rule revision OR scope reduction (drop problematic fields)

**Risk R2: UCI Web Scraping Failures**
- **Prevention:**
  - Robust HTML parsing (handle missing elements gracefully)
  - Rate limiting: 1 request/second (avoids IP blocking)
  - Error handling: retry logic for transient failures
- **Detection:** Track success rate during pilot (target >70%)
- **Response:**
  - IF success 50-70%: Accept lower quality, document limitations
  - IF success <50%: Abandon UCI, proceed with OpenML + HuggingFace only (still 9,500 datasets for 10k target)

**Risk R3: API Rate Limiting**
- **Prevention:**
  - Pilot throughput testing validates no hard rate limits encountered
  - Batch API requests where supported (OpenML allows bulk queries)
  - Parallel execution (multiple threads/processes for independent extractions)
- **Detection:** Monitor API response codes (429 = rate limit) during pilot
- **Response:**
  - IF rate limits detected: Implement exponential backoff, reduce parallelism, extend timeline to 3 weeks

---

## 10. Expected Outcomes & Next Steps

### 10.1 Expected Outcomes (if PASS)

1. **Friction Scores Validated:**
   - HuggingFace: 3 (API + templates + validation)
   - OpenML: 2 (API + automation)
   - UCI: 0 (manual web forms only)

2. **Extraction Feasibility Confirmed:**
   - 10,000+ datasets extractable within 2-week window
   - Success rates: OpenML >90%, HF >85%, UCI >70%
   - Throughput >500 records/hour

3. **Parsing Rules Validated:**
   - Overall accuracy >90%
   - All 6 fields >75% accuracy
   - Refinements documented for full-scale deployment

4. **Methodology Ready for h-m1/h-m2/h-m3:**
   - Friction scoring protocol established
   - API clients and parsing rules production-ready
   - Full-scale extraction plan validated

### 10.2 Next Steps (Phase 3: Implementation Planning)

**Prerequisites from h-e1:**
- Validated API clients (OpenML, HuggingFace, UCI)
- Parsing rules with >90% accuracy
- Friction scores assigned (HF=3, OpenML=2, UCI=0)

**Phase 3 Inputs:**
- h-e1 final report (friction scores, extraction feasibility, parsing accuracy)
- Code artifacts (API clients, parsing rules module)
- Pilot dataset (250 records for testing h-m1/h-m2/h-m3 experiments)

**Phase 3 Deliverables (for h-m1/h-m2/h-m3):**
- PRD (Product Requirements Document) for full-scale metadata extraction pipeline
- Architecture document (data flow, parallel execution, error handling)
- Epic-level task breakdown (Archon project initialization)
- Complexity tier assessment (Tier 1-3)

### 10.3 Decision Tree

```
h-e1 Experiment Execution
    │
    ├─ Friction Score Assignment (Exp 1)
    │   ├─ PASS (scores assigned with objective criteria) → Continue
    │   └─ FAIL (subjective scoring) → PIVOT to API-only feature (score 0-1)
    │
    ├─ Pilot Extraction (Exp 2)
    │   ├─ OpenML/HF success >80% AND UCI >70% → Continue
    │   ├─ OpenML/HF success >80% AND UCI <50% → ABANDON UCI, continue with 2 platforms
    │   └─ OpenML/HF success <70% → STOP, methodology infeasible
    │
    ├─ Parsing Validation (Exp 3)
    │   ├─ Accuracy >90% → Continue
    │   ├─ Accuracy 80-90% → REFINE rules, re-validate
    │   └─ Accuracy <80% → SCOPE reduction (fewer fields) OR STOP
    │
    ├─ Throughput Extrapolation
    │   ├─ <336 hours → PASS
    │   ├─ 336-500 hours → OPTIMIZE (parallelization), re-estimate
    │   └─ >500 hours → REDUCE sample to 7k OR EXTEND timeline to 3 weeks
    │
    └─ MUST_WORK Gate Evaluation
        ├─ ALL criteria met → PASS → Proceed to h-m1 (Phase 3)
        └─ ANY criterion fails → FAIL → Document contingency, STOP or PIVOT
```

---

## 11. Deliverables Summary

| Deliverable | Description | Timeline |
|-------------|-------------|----------|
| **Friction Scoring Report** | Objective binary criteria for 4 features × 3 platforms, composite scores | Day 3 |
| **API Clients & Scraper** | Working code for OpenML, HuggingFace, UCI extraction | Days 1-2 |
| **Parsing Rules Module** | 6 field parsing functions with unit tests | Days 1-2 |
| **Pilot Dataset** | 250 metadata records (100 OpenML, 100 HF, 50 UCI) | Days 4-7 |
| **Pilot Metrics Report** | Success rates, throughput, error analysis | Day 7 |
| **Validation Dataset** | 100 records × 6 fields with automated + manual labels | Days 8-10 |
| **Parsing Accuracy Report** | Overall accuracy, per-field accuracy, confusion analysis | Day 10 |
| **Throughput Extrapolation Report** | 10k feasibility analysis with optimization plan | Days 11-12 |
| **Gate Evaluation Report** | MUST_WORK gate decision (PASS/FAIL) with justification | Day 12 |
| **Final h-e1 Experiment Report** | Comprehensive results, recommendations for h-m1/h-m2/h-m3 | Days 13-14 |

---

## 12. Resource Requirements

### 12.1 Computational Resources

- **Hardware:** Standard laptop/desktop (no GPU required)
- **Storage:** ~100 MB for pilot dataset (250 records × 6 fields with raw metadata)
- **Network:** Stable internet for API requests and web scraping

### 12.2 Software Dependencies

```
openml>=0.14.0
datasets>=2.0.0
huggingface_hub>=0.16.0
beautifulsoup4>=4.12.0
requests>=2.31.0
pandas>=2.0.0
```

### 12.3 Human Effort

- **Friction scoring:** 1 day (documentation review, criteria definition)
- **Code implementation:** 2 days (API clients, scraper, parsing rules)
- **Pilot extraction monitoring:** 4 days (supervise runs, debug errors)
- **Manual validation:** 1 day (100 datasets × 6 fields annotation)
- **Analysis & reporting:** 3 days (metrics calculation, gate evaluation, final report)
- **Total:** ~11 days (within 2-week budget)

### 12.4 External Dependencies

- **OpenML API:** Public, no authentication required for read access
- **HuggingFace Hub API:** Public, optional authentication for higher rate limits
- **UCI Repository:** Public web access, no authentication

---

## 13. Alignment with Verification Plan

**From 02b_verification_plan.md Section 2.2 (H-E1):**

| Verification Protocol Step | Implementation in Experiment Brief |
|----------------------------|-------------------------------------|
| 1. Review platform documentation and assign friction scores | Experiment 1 (Days 3) |
| 2. Implement API clients and web scraper | Phase 1 Setup (Days 1-2) |
| 3. Execute 100-sample pilot extraction per platform | Experiment 2 (Days 4-7) |
| 4. Validate parsing rules for 6 target fields | Experiment 3 (Days 8-10) |
| 5. Confirm 10k+ extraction feasible within 2-week timeframe | Phase 5 Throughput Extrapolation (Days 11-12) |

**Success Criteria Mapping:**
- Primary: Friction scores assigned → Experiment 1
- Secondary: Pilot extraction >80% success (OpenML/HF), >70% (UCI) → Experiment 2

**Gate Alignment:**
- MUST_WORK gate in verification plan → Section 7.1 gate conditions in this brief
- All 5 pass conditions from verification plan implemented in gate evaluation

---

**End of Experiment Brief**

**Prepared for:** Phase 3 Implementation Planning  
**Next Phase:** Generate PRD, Architecture, Epic-level tasks (Archon project)  
**Hypothesis Chain:** h-e1 (foundation) → h-m1 → h-m2 → h-m3 (mechanisms)
