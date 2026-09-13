# Architecture Design: h-m1 Friction Features Lower Entry Cost

**Date:** 2026-08-19  
**Hypothesis ID:** h-m1  
**Type:** MECHANISM  
**Tier:** 1

---

## 1. System Overview

### 1.1 High-Level Architecture

```
┌─────────────────────┐
│  HuggingFace API    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Collection Pipeline                      │
│  ┌─────────────┐   ┌──────────────┐   ┌─────────────────────┐  │
│  │   Dataset   │──▶│   Upload     │──▶│  Stratified         │  │
│  │  Discovery  │   │   Method     │   │  Sampling           │  │
│  │             │   │  Classifier  │   │  (1k API + 1k Man)  │  │
│  └─────────────┘   └──────────────┘   └─────────────────────┘  │
└───────────────────────────────────┬─────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Metadata Extraction Pipeline                  │
│  ┌─────────────┐   ┌──────────────┐   ┌─────────────────────┐  │
│  │   README    │──▶│   Field      │──▶│  Completeness       │  │
│  │   Fetcher   │   │   Parser     │   │  Scorer             │  │
│  │             │   │  (6 fields)  │   │  (mean × 100)       │  │
│  └─────────────┘   └──────────────┘   └─────────────────────┘  │
└───────────────────────────────────┬─────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Validation & Analysis Pipeline                │
│  ┌─────────────┐   ┌──────────────┐   ┌─────────────────────┐  │
│  │   Pilot     │──▶│  Statistical │──▶│  Gate Decision      │  │
│  │ Validation  │   │   Analyzer   │   │  Engine             │  │
│  │ (100 sample)│   │   (t-test)   │   │  (PASS/FAIL)        │  │
│  └─────────────┘   └──────────────┘   └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow

**Phase 1: Dataset Discovery**
- Input: HuggingFace API query (5,000 dataset IDs)
- Filter: has_readme=True, created_before=2026-08-19
- Output: `data/h-m1/hf_dataset_ids.csv` (~3,000 candidates)

**Phase 2: Upload Method Classification**
- Input: Dataset IDs + metadata (commit history, file structure, README patterns)
- Processing: Heuristic classifier (4 signal types)
- Output: `data/h-m1/upload_classified.csv` (binary labels: API/manual)

**Phase 3: Stratified Sampling**
- Input: Classified datasets
- Processing: Random sampling (seed=42), 1,000 per group
- Output: Sample IDs for extraction

**Phase 4: Metadata Extraction**
- Input: Sample IDs (2,000 datasets)
- Processing: README fetch + 6-field parser (h-e1 rules)
- Output: `data/h-m1/completeness_scores.csv` (dataset_id, upload_method, score, field_vector)

**Phase 5: Pilot Validation**
- Input: 100-sample subset (50 API + 50 manual)
- Processing: Manual review (classification + parsing accuracy)
- Output: `data/h-m1/validation_pilot_100.csv` (ground truth labels, accuracy metrics)

**Phase 6: Statistical Analysis**
- Input: Completeness scores (2,000 datasets)
- Processing: t-test, effect size calculation
- Output: p-value, Cohen's d, mean difference

**Phase 7: Gate Decision**
- Input: Statistical results + pilot validation metrics
- Processing: Threshold checks (direction, p<0.05, validation >85%/>90%)
- Output: `docs/youra_research/h-m1/04_validation.md` (PASS/FAIL report)

---

## 2. Component Specifications

### 2.1 Dataset Discovery Module

**Purpose:** Query HuggingFace API for candidate datasets

**Technology Stack:**
- `huggingface_hub` Python library (API client)
- `datasets.list_datasets()` for dataset enumeration
- `HfApi().dataset_info()` for metadata retrieval

**Input:** None (API query)

**Output:** CSV with columns:
- `dataset_id` (str): HuggingFace dataset identifier (e.g., "squad", "glue")
- `creation_date` (datetime): Dataset creation timestamp
- `has_readme` (bool): README.md presence flag

**Processing Logic:**
1. Query all public datasets via `list_datasets()`
2. For each dataset, fetch metadata (`dataset_info()`)
3. Filter: `has_readme == True AND creation_date < 2026-08-19`
4. Save filtered list to CSV

**Error Handling:**
- API rate limit exceeded: Exponential backoff (1s, 2s, 4s, max 60s)
- Dataset metadata unavailable: Skip dataset, log warning
- Network timeout: Retry up to 3 times

**Performance:**
- Expected API calls: ~5,000 (dataset enumeration) + 3,000 (metadata fetch) = 8,000 calls
- Rate limit: ~1,000 requests/hour → ~8 hours runtime
- Optimization: Batch requests where possible, cache metadata locally

---

### 2.2 Upload Method Classifier

**Purpose:** Classify datasets as API-programmatic or manual-web-form uploads

**Technology Stack:**
- `huggingface_hub.HfApi().list_repo_commits()` for commit history
- `huggingface_hub.HfApi().list_repo_files()` for file structure
- Python regex for README pattern matching

**Input:** Dataset ID

**Output:** Classification record with:
- `dataset_id` (str)
- `upload_method` (str): "API", "MANUAL", or "AMBIGUOUS"
- `classification_confidence` (int): Count of matching signals (0-7)
- `matched_signals` (list[str]): Signal names that matched

**Heuristic Signals (7 total):**

1. **Commit user-agent (API signal):**
   - Pattern: `huggingface_hub` in commit metadata user-agent field
   - Weight: Strong indicator (most reliable)

2. **Commit message pattern (API signal):**
   - Pattern: Generic messages like "Upload dataset", "Update dataset" (vs custom prose)
   - Weight: Medium indicator

3. **File structure (API signal):**
   - Pattern: Presence of `dataset_info.json` in root directory
   - Weight: Strong indicator

4. **README YAML frontmatter (API signal):**
   - Pattern: Auto-generated `dataset_info` block with standardized formatting
   - Weight: Medium indicator

5. **README prose style (Manual signal):**
   - Pattern: Custom narrative text, non-template structure
   - Weight: Medium indicator

6. **Drag-and-drop file pattern (Manual signal):**
   - Pattern: File upload timestamps clustered (multiple files added in <5 min window)
   - Weight: Weak indicator

7. **Metadata UI tags (Manual signal):**
   - Pattern: YAML tags field with specific formatting patterns from web UI
   - Weight: Medium indicator

**Classification Logic:**
```python
api_signals = count([commit_agent, commit_msg, file_structure, yaml_frontmatter])
manual_signals = count([prose_style, dragdrop_pattern, ui_tags])

if api_signals >= 2 and manual_signals == 0:
    return "API"
elif manual_signals >= 2 and api_signals == 0:
    return "MANUAL"
else:
    return "AMBIGUOUS"
```

**Confidence Scoring:**
- Confidence = api_signals + manual_signals (range 0-7)
- Ambiguous cases: Confidence < 2 OR (api_signals > 0 AND manual_signals > 0)

**Error Handling:**
- Commit history unavailable: Flag as AMBIGUOUS
- File listing fails: Skip file structure signal, rely on other signals
- README parsing error: Skip README signals, rely on commit/file signals

---

### 2.3 Metadata Parser

**Purpose:** Extract 6 target fields from README content (reuses h-e1 validated rules)

**Technology Stack:**
- Python `re` module (regex)
- Custom keyword matching functions
- `huggingface_hub.HfApi().dataset_info()` for README fetch

**Input:** Dataset ID

**Output:** Field presence vector with:
- `dataset_id` (str)
- `dependencies` (int): 0 or 1
- `version` (int): 0 or 1
- `data_source_url` (int): 0 or 1
- `preprocessing_code` (int): 0 or 1
- `license` (int): 0 or 1
- `collection_date` (int): 0 or 1

**Parsing Rules (inherited from h-e1):**

| Field | Regex Pattern | Presence Threshold |
|-------|--------------|-------------------|
| `dependencies` | `(requirements\.txt\|pip install\|conda install\|[a-z_-]+[>=<]=\d+)` | Match found |
| `version` | `v?\d+\.\d+(\.\d+)?\|version:\s*\d+\|\d{4}-\d{2}-\d{2}` | Match found |
| `data_source_url` | `https?://[^\s]+` (exclude github.com, huggingface.co) | Match found |
| `preprocessing_code` | Code block >50 chars with keywords (def, import, library) OR file extensions (.py, .R, .ipynb) | Match found |
| `license` | `(MIT\|Apache\|GPL\|CC-BY\|CC0\|BSD)` (case-insensitive) | Match found |
| `collection_date` | `\d{4}-\d{2}-\d{2}\|(Jan\|Feb\|...\|Dec)\s+\d{4}\|collected (on\|in)` | Match found |

**Processing Logic:**
1. Fetch README content via `dataset_info(dataset_id).card_data`
2. For each field, apply regex pattern to full README text
3. Binary scoring: 1 if pattern matches, 0 otherwise
4. Return 6-element vector (0/1 per field)

**Error Handling:**
- README unavailable: Return all zeros (0,0,0,0,0,0)
- Regex timeout (>1s): Skip field, score as 0
- Malformed README encoding: Attempt UTF-8 decode, fallback to ASCII

---

### 2.4 Completeness Scorer

**Purpose:** Calculate mean field presence as percentage (0-100%)

**Technology Stack:**
- Python `numpy` for mean calculation

**Input:** Field presence vector (6 elements, 0/1 per field)

**Output:** Completeness score (float, 0-100)

**Formula:**
```
completeness_score = (sum(field_presence_vector) / 6) × 100
```

**Example:**
- Vector: [1, 1, 0, 1, 0, 0] → Score: (3/6) × 100 = 50.0%
- Vector: [1, 1, 1, 1, 1, 1] → Score: (6/6) × 100 = 100.0%

---

### 2.5 Statistical Analyzer

**Purpose:** Compare mean completeness scores (API vs manual) via t-test

**Technology Stack:**
- `scipy.stats.ttest_ind` (independent samples t-test)
- `scipy.stats.shapiro` (normality test)
- `scipy.stats.levene` (equal variance test)
- `numpy` for effect size calculation

**Input:** Two arrays of completeness scores
- `api_scores` (array, n~1000)
- `manual_scores` (array, n~1000)

**Output:** Statistical results dict:
- `p_value` (float): Two-tailed t-test p-value
- `cohen_d` (float): Standardized effect size
- `mean_diff_pp` (float): Absolute percentage point difference
- `ci_lower`, `ci_upper` (float): 95% confidence interval for mean difference
- `normality_api`, `normality_manual` (bool): Shapiro-Wilk test results (p>0.05)
- `equal_variance` (bool): Levene test result (p>0.05)
- `test_used` (str): "ttest_ind", "welch_ttest", or "mann_whitney"

**Processing Logic:**
1. **Normality check:**
   - Run Shapiro-Wilk on both groups
   - IF both p>0.05: Assume normal distribution
   - ELSE: Flag non-normal, fallback to Mann-Whitney U

2. **Equal variance check (if normal):**
   - Run Levene's test
   - IF p>0.05: Use standard t-test
   - ELSE: Use Welch's t-test (unequal variance)

3. **Primary test:**
   - IF normal + equal variance: `scipy.stats.ttest_ind(equal_var=True)`
   - IF normal + unequal variance: `scipy.stats.ttest_ind(equal_var=False)` (Welch)
   - IF non-normal: `scipy.stats.mannwhitneyu(alternative='two-sided')`

4. **Effect size calculation:**
   - Cohen's d: `(mean_api - mean_manual) / pooled_std`
   - Pooled std: `sqrt(((n1-1)*std1^2 + (n2-1)*std2^2) / (n1+n2-2))`
   - Mean difference (pp): `mean_api - mean_manual`

5. **Confidence interval:**
   - 95% CI for mean difference via `scipy.stats.ttest_ind` output

**Error Handling:**
- Insufficient data (n<10 per group): Raise error, require minimum sample
- Extreme outliers (>3 SD from mean): Flag in report, do not remove
- Divide-by-zero (pooled_std=0): Return d=0, flag data quality issue

---

### 2.6 Pilot Validator

**Purpose:** Manual review of 100-sample subset to verify classification + parsing accuracy

**Technology Stack:**
- CSV export for manual annotation
- Python scripts for accuracy calculation

**Input:** 
- Stratified random sample (50 API + 50 manual from final 2,000 sample)
- Automated labels (upload_method, 6 field presence flags)

**Output:** Validation metrics dict:
- `classification_accuracy` (float): % agreement for upload method labels
- `parsing_accuracy` (float): % agreement across all 600 field labels (100 datasets × 6 fields)
- `classification_errors` (list): Dataset IDs with misclassified upload method
- `parsing_errors` (list): (dataset_id, field_name) tuples with incorrect field labels

**Manual Review Process:**
1. **Export pilot sample:** Generate `validation_pilot_100.csv` with columns:
   - `dataset_id`, `upload_method_automated`, `dependencies_automated`, ..., `collection_date_automated`
   - Empty columns: `upload_method_ground_truth`, `dependencies_ground_truth`, ..., `collection_date_ground_truth`

2. **Manual annotation:**
   - Reviewer inspects dataset (commit history, README) via HuggingFace web UI
   - Fill ground truth columns (upload method: API/MANUAL, fields: 0/1)

3. **Accuracy calculation:**
   - Classification accuracy: `sum(upload_method_automated == upload_method_ground_truth) / 100`
   - Parsing accuracy: `sum(all_field_labels_match) / 600` (100 datasets × 6 fields)

**Error Handling:**
- Missing ground truth labels: Exclude from accuracy calculation, flag as incomplete
- Reviewer disagreement (if multiple reviewers): Use majority vote

---

### 2.7 Gate Decision Engine

**Purpose:** Evaluate success criteria and determine PASS/FAIL for MUST_WORK gate

**Input:** Statistical results + pilot validation metrics

**Output:** Gate decision dict:
- `gate_result` (str): "PASS" or "FAIL"
- `rationale` (str): Explanation of decision
- `primary_criterion_met` (bool): Direction confirmed AND p<0.05
- `validation_criteria_met` (bool): Classification >85% AND parsing >90%
- `effect_size_sufficient` (bool): Mean difference ≥10pp (secondary criterion)

**Decision Logic:**
```python
primary_met = (mean_api > mean_manual) AND (p_value < 0.05)
validation_met = (classification_accuracy > 0.85) AND (parsing_accuracy > 0.90)

if primary_met AND validation_met:
    gate_result = "PASS"
    rationale = f"Direction confirmed (μ_API={mean_api:.1f}% > μ_manual={mean_manual:.1f}%, p={p_value:.4f}), validation thresholds met (classification={classification_accuracy:.2%}, parsing={parsing_accuracy:.2%})"
elif not primary_met:
    gate_result = "FAIL"
    rationale = "Primary criterion failed: " + (
        "No difference detected (p≥0.05)" if p_value >= 0.05 else
        "Reverse direction (μ_API < μ_manual)"
    )
elif not validation_met:
    gate_result = "FAIL"
    rationale = "Validation criteria failed: " + (
        f"Classification accuracy {classification_accuracy:.2%} ≤85%" if classification_accuracy <= 0.85 else
        f"Parsing accuracy {parsing_accuracy:.2%} ≤90%"
    )
```

**Output File:** `docs/youra_research/h-m1/04_validation.md`

---

## 3. Technology Stack

### 3.1 Core Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| `huggingface_hub` | ≥0.25 | HuggingFace API client (dataset metadata, commits, files) |
| `datasets` | ≥3.0 | Dataset enumeration, README fetch |
| `pandas` | ≥2.0 | CSV I/O, data manipulation |
| `numpy` | ≥1.24 | Numerical operations, mean calculation |
| `scipy` | ≥1.10 | Statistical tests (t-test, Shapiro-Wilk, Levene, Mann-Whitney) |
| `matplotlib` | ≥3.5 | Visualization (distribution plots, effect size chart) |
| `requests` | ≥2.28 | HTTP client (fallback for API calls) |

### 3.2 Development Tools

| Tool | Purpose |
|------|---------|
| `pytest` | Unit testing (parsing rules, classification logic) |
| `black` | Code formatting |
| `mypy` | Type checking |
| `jupyter` | Exploratory analysis notebook |

---

## 4. Scalability & Performance

### 4.1 API Rate Limits

**HuggingFace API:**
- Free tier: ~1,000 requests/hour (burst up to 100/min)
- Authentication: Optional (API key increases rate limit to 10,000/hour)

**Total API Calls (h-m1 pipeline):**
- Dataset discovery: 5,000 (list datasets) + 3,000 (metadata fetch) = 8,000 calls
- Upload classification: 3,000 (commit history + file listing) = 3,000 calls
- Metadata extraction: 2,000 (README fetch) = 2,000 calls
- **Total:** ~13,000 API calls

**Estimated Runtime:**
- Free tier (1,000 req/hr): ~13 hours
- Authenticated tier (10,000 req/hr): ~1.5 hours

**Optimization Strategies:**
1. Use authenticated API key (10x speedup)
2. Cache intermediate results (discovery, classification) to disk
3. Batch file listing requests (single API call per dataset)
4. Parallelize README fetching (10 concurrent threads, respecting rate limit)

### 4.2 Data Storage

**Disk Space Requirements:**
- Dataset IDs CSV: ~100 KB (5,000 rows × 20 bytes/row)
- Upload classification CSV: ~150 KB (3,000 rows × 50 bytes/row)
- Completeness scores CSV: ~100 KB (2,000 rows × 50 bytes/row)
- Pilot validation CSV: ~5 KB (100 rows × 50 bytes/row)
- **Total:** <1 MB

**Memory Requirements:**
- Discovery: <10 MB (5,000 dataset metadata records)
- Classification: <5 MB (3,000 datasets × file listings)
- Extraction: <2 MB (2,000 README files, max 5 KB each = 10 MB peak)
- Analysis: <1 MB (2,000 float scores)
- **Peak memory:** ~20 MB (comfortably fits in 512 MB RAM)

### 4.3 Parallelization

**Parallelizable Components:**
1. Dataset discovery: Batch API calls (10 parallel threads)
2. Upload classification: Process datasets independently (10 parallel threads)
3. Metadata extraction: Fetch READMEs in parallel (10 parallel threads)

**Sequential Components:**
1. Stratified sampling (requires full classification results)
2. Statistical analysis (requires full extraction results)
3. Gate decision (requires all prior results)

**Concurrency Strategy:**
- Use `concurrent.futures.ThreadPoolExecutor` with max_workers=10
- Respect API rate limit: Semaphore with 10 permits (10 parallel requests)
- Exponential backoff for rate limit errors

---

## 5. Error Handling & Fault Tolerance

### 5.1 API Error Handling

| Error Type | HTTP Code | Recovery Strategy |
|------------|----------|------------------|
| Rate limit exceeded | 429 | Exponential backoff (1s, 2s, 4s, ..., max 60s), retry up to 5 times |
| Dataset not found | 404 | Skip dataset, log warning, continue |
| Server error | 500, 502, 503 | Retry up to 3 times with 5s delay |
| Network timeout | - | Retry up to 3 times with exponential backoff |
| Authentication error | 401 | Fail fast, require valid API key |

### 5.2 Data Quality Checks

**Discovery Phase:**
- Check: Dataset has README.md
- Failure: Skip dataset (cannot parse metadata without README)

**Classification Phase:**
- Check: At least 1 signal matches (confidence ≥1)
- Failure: Flag as AMBIGUOUS, exclude from stratified sample

**Extraction Phase:**
- Check: README content non-empty
- Failure: Assign all-zero field vector (0,0,0,0,0,0), completeness=0%

**Pilot Validation:**
- Check: Manual reviewer fills all ground truth labels
- Failure: Exclude incomplete reviews from accuracy calculation

### 5.3 Checkpoint & Resume

**Checkpoint Strategy:**
- Save intermediate results after each phase (discovery → classification → extraction)
- CSV files serve as natural checkpoints (idempotent re-runs)

**Resume Logic:**
- Before each phase, check if output CSV exists
- IF exists AND not stale (timestamp <24h old): Skip phase, load from file
- ELSE: Re-run phase, overwrite CSV

**Staleness Detection:**
- Discovery: Re-run if dataset count changes by >5% (HuggingFace adds/removes datasets)
- Classification: Re-run if input dataset IDs change
- Extraction: Re-run if classification results change

---

## 6. Security & Privacy

### 6.1 Data Privacy

**Public Data Only:**
- All datasets analyzed are public (HuggingFace public repositories)
- No private dataset access, no authentication credentials exposed

**No PII Collection:**
- Dataset metadata (README, commit history) may contain author names/emails
- Do NOT store author identifiers in output CSVs (only dataset_id)

### 6.2 API Key Management

**Best Practices:**
- Store API key in environment variable `HUGGINGFACE_API_KEY`
- Never hardcode API key in source code
- Never commit API key to version control
- Use `.env` file with `.gitignore` exclusion

---

## 7. Testing Strategy

### 7.1 Unit Tests

**Upload Method Classifier:**
- Test: Known API upload (has `huggingface_hub` commit) → "API" label
- Test: Known manual upload (custom README prose) → "MANUAL" label
- Test: Ambiguous case (mixed signals) → "AMBIGUOUS" label

**Metadata Parser:**
- Test: README with all 6 fields present → [1,1,1,1,1,1]
- Test: README with no fields → [0,0,0,0,0,0]
- Test: README with 3 fields (dependencies, version, license) → [1,1,0,0,1,0]

**Completeness Scorer:**
- Test: [1,1,1,1,1,1] → 100.0%
- Test: [0,0,0,0,0,0] → 0.0%
- Test: [1,1,0,1,0,0] → 50.0%

### 7.2 Integration Tests

**End-to-End Pipeline:**
- Test: Run full pipeline on 10-dataset sample (manually labeled ground truth)
- Verify: Upload method classification matches manual labels
- Verify: Field presence matches manual README review
- Verify: Completeness scores within ±5% of manual calculation

### 7.3 Validation Tests

**Pilot Validation:**
- Test: Run pilot validation on h-e1 validation dataset (100 datasets with ground truth)
- Verify: Classification accuracy ≥85%
- Verify: Parsing accuracy ≥90%

---

## 8. Monitoring & Observability

### 8.1 Logging

**Log Levels:**
- INFO: Phase completion (discovery done, classification done, etc.)
- WARNING: Skipped datasets (404 errors, missing README)
- ERROR: API failures, network timeouts

**Log Format:**
```
[2026-08-19 10:30:00] INFO: Discovery phase complete. 3,120 candidates found (filtered from 5,000 initial).
[2026-08-19 10:45:00] WARNING: Dataset 'xyz/abc' skipped (404 Not Found).
[2026-08-19 11:00:00] ERROR: API rate limit exceeded. Retrying in 10s...
```

### 8.2 Progress Tracking

**Console Output:**
- Discovery: "Fetching dataset 1,234 / 5,000..."
- Classification: "Classified 567 / 3,000 datasets (189 API, 378 manual, 0 ambiguous)"
- Extraction: "Extracted 123 / 2,000 datasets. Mean completeness so far: 62.3%"

---

## 9. Deployment & Execution

### 9.1 Execution Environment

**Requirements:**
- Python 3.9+
- 512 MB RAM (peak usage ~20 MB)
- 10 MB disk space
- Internet connection (HuggingFace API access)
- Optional: HuggingFace API key (10x rate limit increase)

### 9.2 Execution Command

**Single-Command Pipeline:**
```bash
python scripts/h-m1/run_pipeline.py \
  --api-key $HUGGINGFACE_API_KEY \
  --output-dir data/h-m1 \
  --seed 42
```

**Phase-by-Phase Execution (manual checkpoints):**
```bash
# Phase 1: Discovery
python scripts/h-m1/01_discover_datasets.py --output data/h-m1/hf_dataset_ids.csv

# Phase 2: Classification
python scripts/h-m1/02_classify_upload_method.py \
  --input data/h-m1/hf_dataset_ids.csv \
  --output data/h-m1/upload_classified.csv

# Phase 3: Stratified Sampling
python scripts/h-m1/03_stratified_sample.py \
  --input data/h-m1/upload_classified.csv \
  --output data/h-m1/sampled_ids.txt \
  --n-per-group 1000 --seed 42

# Phase 4: Metadata Extraction
python scripts/h-m1/04_extract_metadata.py \
  --input data/h-m1/sampled_ids.txt \
  --output data/h-m1/completeness_scores.csv

# Phase 5: Pilot Validation (manual step — export for human review)
python scripts/h-m1/05_export_pilot_sample.py \
  --input data/h-m1/completeness_scores.csv \
  --output data/h-m1/validation_pilot_100.csv \
  --n 100 --seed 42

# Phase 6: Statistical Analysis (after manual validation complete)
python scripts/h-m1/06_statistical_analysis.py \
  --input data/h-m1/completeness_scores.csv \
  --pilot data/h-m1/validation_pilot_100.csv \
  --output docs/youra_research/h-m1/04_validation.md
```

---

## 10. Summary

**Architecture Highlights:**
- **Modular pipeline:** 6 independent phases (discovery → classification → sampling → extraction → validation → analysis)
- **Scalable design:** Parallelized API calls (10 concurrent threads), respects rate limits, checkpointed execution
- **Robust error handling:** Retry logic, fallback tests (Welch's t-test, Mann-Whitney), ambiguity flagging
- **Reproducible:** Fixed random seed (42), versioned dependencies, idempotent pipeline

**Key Design Decisions:**
1. **Heuristic classifier over ML model:** Upload method signals are discrete and interpretable (commit patterns, file structure). Heuristic rules provide transparency + fast execution without training data.
2. **Reuse h-e1 parsing rules:** Validated 90%+ accuracy on HuggingFace datasets. No need to reinvent.
3. **Pilot validation before full analysis:** 100-sample manual review catches classification/parsing errors early, prevents garbage-in-garbage-out statistical results.
4. **Stratified sampling:** Ensures balanced comparison (1,000 API vs 1,000 manual), avoids class imbalance bias.
5. **Checkpoint-based execution:** CSV files serve as natural checkpoints. Pipeline can resume from any phase if interrupted.

**Next Steps:** Logic specification (03_logic.md), Configuration (03_config.md), Task breakdown (03_tasks.yaml)
