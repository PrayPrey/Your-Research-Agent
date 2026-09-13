# Product Requirements Document: h-e1 Data Availability Verification

**Version:** 1.0  
**Date:** 2026-08-28  
**Hypothesis ID:** h-e1  
**Type:** EXISTENCE  
**Gate:** MUST_WORK  

---

## Executive Summary

**Objective:** Verify that historical benchmark leaderboard data (Papers With Code 2018-2024) and expert consensus on saturation exist with sufficient completeness to support downstream saturation detection experiments.

**Success Criteria:**
- ≥100 timestamped submissions per benchmark (ImageNet, GLUE, SQuAD)
- ≥30 high-confidence expert responses per benchmark
- 80% timestamp coverage in PWC data

**Scope:** Data collection and validation only (no model training).

---

## Problem Statement

### Background
Downstream hypotheses (h-m1, h-m2, h-m3) require two data sources:
1. Historical leaderboard scores with timestamps (to measure score convergence)
2. Expert consensus on saturation dates (to validate detection methods)

### Problem
Unknown whether PWC API provides sufficient historical data and whether ML community has consensus on saturation timing.

### Impact
If data unavailable → entire research pipeline blocked → requires pivot to citation-based methods.

---

## Functional Requirements

### FR-1: PWC Leaderboard Data Collection
**Description:** Collect timestamped submissions for 3 benchmarks from Papers With Code API.

**Acceptance Criteria:**
- API client handles rate limiting (100 req/min)
- Extracts: benchmark_name, submission_date, model_name, score
- Outputs JSONL files: `data/pwc_leaderboards/{benchmark}_raw.jsonl`
- Covers 2018-2024 time range

**Dependencies:** `aiohttp`, `pydantic`, `pandas`

### FR-2: Fallback Web Scraping
**Description:** If API timestamp coverage <50%, scrape PWC leaderboard HTML pages.

**Acceptance Criteria:**
- Uses Selenium + BeautifulSoup
- Extracts same fields as FR-1
- Outputs: `data/pwc_leaderboards/{benchmark}_scraped.jsonl`
- Implements retry logic for failed requests

**Dependencies:** `selenium`, `beautifulsoup4`, `webdriver-manager`

**Trigger Condition:** `(timestamped_submissions / total_submissions) < 0.5`

### FR-3: Expert Consensus Survey
**Description:** Distribute Qualtrics survey to ML researchers asking for saturation year estimates.

**Acceptance Criteria:**
- Survey includes 3 benchmarks (ImageNet, GLUE, SQuAD)
- Collects: saturation_year, confidence (1-5), domain, experience_level
- Distributed via NeurIPS/ICML lists, Twitter, LinkedIn
- Target: 50+ responses

**Dependencies:** Qualtrics account, mailing list access

### FR-4: Data Validation
**Description:** Validate completeness of PWC data and expert survey responses.

**Acceptance Criteria:**
- Checks: timestamp format (ISO 8601), benchmark coverage, sample counts
- Counts high-confidence (≥4/5) survey responses per benchmark
- Generates: `data/validation_report.json`
- Reports pass/fail for each criterion

**Dependencies:** `jsonschema`

### FR-5: Success Criteria Check
**Description:** Determine h-e1 PASS/FAIL based on validation report.

**Logic:**
```python
pwc_pass = all(count >= 100 for benchmark, count in pwc_sample_sizes.items())
survey_pass = all(count >= 30 for benchmark, count in high_confidence_counts.items())
h_e1_pass = pwc_pass AND survey_pass
```

**Outputs:** Console message "H-E1 EXISTENCE: PASS" or "H-E1 EXISTENCE: FAIL"

---

## Non-Functional Requirements

### NFR-1: Performance
- PWC API data collection: <2 hours for all 3 benchmarks
- Fallback scraping: <4 hours if triggered
- Data validation: <1 hour

### NFR-2: Reliability
- API retry logic: 3 attempts with exponential backoff (1s, 2s, 4s)
- Graceful degradation: API fails → trigger web scraping

### NFR-3: Data Quality
- Timestamp coverage ≥80% (prefer API, supplement with scraping)
- Survey completion rate >40%
- Response distribution balanced (vision/NLP: 40-60%, junior/senior: 30-70%)

### NFR-4: Resource Constraints
- Compute: Standard laptop (no GPU)
- Memory: 8GB RAM
- Storage: 500MB

---

## Data Requirements

### Primary Datasets

**Dataset 1: Papers With Code Leaderboards**
- **Source:** PWC API (https://paperswithcode.com/api/v1/)
- **Benchmarks:** ImageNet, GLUE, SQuAD
- **Time Range:** 2018-01-01 to 2024-12-31
- **Fields:** submission_date, model_name, score, benchmark_name
- **Expected Size:** 200-500 submissions/benchmark
- **Cache:** `data/pwc_leaderboards/`

**Dataset 2: Expert Consensus Survey**
- **Source:** Qualtrics survey
- **Target Sample:** 50+ ML researchers
- **Fields:** benchmark_name, saturation_year, confidence_rating, domain, experience_level
- **Expected Size:** 40-60 responses
- **Cache:** `data/expert_survey/responses.csv`

---

## Success Criteria

### Primary Criteria
1. **PWC Data:** ≥100 timestamped submissions/benchmark, ≥80% coverage, ≥4-year range
2. **Expert Survey:** ≥30 high-confidence responses/benchmark, >40% completion rate
3. **Combined:** Both criteria met → h-e1 PASS

### Failure Response
**If PWC incomplete:** Pivot to citation-based validation (ArXiv + Semantic Scholar)  
**If survey weak:** Use citation velocity as expert consensus proxy  
**If both fail:** ABORT, escalate for alternative hypothesis

---

## Technical Constraints

### Dependencies
```
python==3.10
aiohttp==3.9.1
pydantic==2.5.0
pandas==2.1.4
selenium==4.16.0
beautifulsoup4==4.12.2
webdriver-manager==4.0.1
jsonschema==4.20.0
numpy==1.26.2
```

### API Constraints
- **Rate Limit:** 100 requests/minute (PWC API)
- **Authentication:** None (public API)
- **Timestamp Granularity:** Monthly (older), daily (recent)

### Risks
1. PWC API rate limiting → Mitigation: exponential backoff
2. Low survey response (<40%) → Mitigation: multi-channel distribution, incentives
3. Web scraping blocked → Mitigation: Selenium with human-like delays

---

## Validation Protocol

### Validation Checklist
- [ ] PWC API responds (200 status) for all benchmarks
- [ ] ≥100 timestamped submissions/benchmark
- [ ] Temporal coverage ≥4 years
- [ ] Survey distributed to ≥50 researchers
- [ ] ≥30 high-confidence responses/benchmark
- [ ] `validation_report.json` generated

### Output Artifacts
```
data/pwc_leaderboards/imagenet_raw.jsonl
data/pwc_leaderboards/glue_raw.jsonl
data/pwc_leaderboards/squad_raw.jsonl
data/expert_survey/responses.csv
data/validation_report.json
```

---

## Timeline

| Phase | Duration |
|-------|----------|
| Environment setup | 1 hour |
| PWC API scraping | 2 hours |
| Fallback scraping (if needed) | 4 hours |
| Survey distribution + collection | 1 week |
| Data validation | 1 hour |
| Success criteria check | 0.5 hours |

**Total:** 8.5 hours (excluding 1-week survey wait)

---

## Next Steps

**If h-e1 PASS:** Proceed to h-m1 (Score Convergence Detection)  
**If h-e1 FAIL:** Execute failure response protocol (citation-based pivot)

---

**Approval Status:** DRAFT  
**Approvers:** User (before Phase 4)
