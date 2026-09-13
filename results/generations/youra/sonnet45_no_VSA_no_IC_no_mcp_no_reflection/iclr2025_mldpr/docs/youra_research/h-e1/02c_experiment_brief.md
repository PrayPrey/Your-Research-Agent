# Experiment Brief: h-e1 - Data Availability and Expert Consensus Existence

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE  
**Gate:** MUST_WORK  
**Date:** 2026-08-28  

---

## 1. Hypothesis Statement

**Full Statement:**  
Top-5 leaderboard score standard deviation <0.5% sustained for 6 months is measurable on historical benchmarks (ImageNet 2015-2020, GLUE 2018-2022)

**Verification Restatement (from 02b_verification_plan.md H-E1):**  
Papers With Code leaderboard data (2018-2024) exists with submission timestamps, AND expert consensus survey achieves ≥30 high-confidence (≥4/5) responses per benchmark.

**Rationale:**  
Foundation hypothesis validating data infrastructure exists before attempting saturation detection (h-m1, h-m2, h-m3). Without PWC data or expert consensus, primary validation (P1) collapses.

---

## 2. Experimental Design

### 2.1 Variables

| Type | Variable | Description |
|------|----------|-------------|
| **Independent** | Data source | PWC API snapshots 2018-2024 for ImageNet, GLUE, SQuAD |
| **Dependent** | Data completeness | Submission count with valid timestamps per benchmark |
| **Dependent** | Expert response count | High-confidence (≥4/5) responses per benchmark |
| **Controlled** | Benchmark selection | ImageNet, GLUE, SQuAD (vision + NLP coverage) |
| **Controlled** | Survey distribution | Stratified sampling (vision/NLP, junior/senior) |

### 2.2 Dataset Specification

**Primary Dataset: Papers With Code Leaderboard Snapshots**

| Field | Value |
|-------|-------|
| **Name** | Papers With Code Leaderboards |
| **Type** | programmatic-api |
| **Source** | PWC public API + manual scraping for missing timestamps |
| **Access** | https://paperswithcode.com/api/v1/ |
| **Benchmarks** | ImageNet (vision), GLUE (NLP), SQuAD (NLP) |
| **Time Range** | 2018-01-01 to 2024-12-31 |
| **Required Fields** | submission_date, model_name, score, benchmark_name |
| **Sample Size** | ≥100 timestamped submissions per benchmark (target: 300+ for statistical power) |
| **Cache Path** | `data/pwc_leaderboards/` |
| **Verified** | false (to be verified in Phase 4) |

**API Endpoints:**
```
GET /benchmarks/                           # List all benchmarks
GET /benchmarks/{benchmark-slug}/          # Get benchmark details
GET /papers/                               # List papers with benchmark results
GET /sota/?benchmark={benchmark-id}        # Get SOTA results for benchmark
```

**Key Implementation Notes:**
- PWC API does NOT directly expose submission timestamps in `/sota/` endpoint
- Workaround: Cross-reference paper publication dates from `/papers/` endpoint with benchmark results
- Fallback: Manual scraping of leaderboard pages using BeautifulSoup + Selenium for timestamped data
- Rate limiting: 100 requests/minute (implemented via `time.sleep(0.6)`)

**Secondary Dataset: Expert Consensus Survey**

| Field | Value |
|-------|-------|
| **Name** | ML Expert Saturation Consensus Survey |
| **Type** | custom |
| **Source** | Qualtrics survey distributed via ML mailing lists + Twitter |
| **Distribution Channels** | NeurIPS/ICML email lists, ML Twitter community, LinkedIn ML groups |
| **Target Sample** | 50+ ML researchers (stratified: 50% vision / 50% NLP, 40% junior / 60% senior) |
| **Required Fields** | benchmark_name, saturation_year, confidence_rating (1-5), domain (vision/NLP), experience_level |
| **Minimum Viable** | ≥30 high-confidence (≥4/5) responses per benchmark |
| **Cache Path** | `data/expert_survey/` |
| **Verified** | false (to be collected in Phase 4) |

**Survey Questions:**
1. "When did ImageNet classification reach saturation (diminishing returns)?" [Year picker 2012-2024]
2. "How confident are you in this assessment?" [1-5 Likert scale]
3. Repeat for GLUE, SQuAD
4. Demographics: domain (vision/NLP), experience (years in ML research)

### 2.3 Baseline Methods

No baselines required for EXISTENCE hypothesis (binary verification).

### 2.4 Evaluation Metrics

**Primary Metrics:**

1. **PWC Data Completeness Rate**
   - Formula: `(timestamped_submissions / total_submissions) * 100`
   - Success Threshold: ≥80% of submissions have valid timestamps
   - Minimum Sample: ≥100 timestamped submissions per benchmark

2. **Expert Response Rate**
   - Formula: `(high_confidence_responses / total_responses) * 100`
   - Success Threshold: ≥30 high-confidence (≥4/5) responses per benchmark
   - Completion Rate Target: >40% survey completion

**Secondary Metrics:**

3. **Response Distribution Balance**
   - Vision vs NLP: 40-60% split acceptable
   - Junior vs Senior: 30-70% split acceptable

4. **Timestamp Coverage**
   - Temporal range: At least 4 years of data per benchmark (2018-2022 minimum)
   - Density: ≥10 submissions per year on average

**Failure Indicators:**
- PWC API returns <100 submissions with timestamps for any benchmark
- Expert survey yields <30 high-confidence responses for any benchmark
- Timestamp data missing for critical periods (e.g., 2017-2020 for ImageNet)

---

## 3. Implementation Specifications

### 3.1 Data Preparation

**Task 1: PWC API Client**
- **Component:** `PWCLeaderboardScraper` class
- **Implementation:**
  - Async HTTP client using `aiohttp` for rate-limited API requests
  - Retry logic with exponential backoff (3 attempts, 1s/2s/4s delays)
  - JSON parsing + validation (pydantic models)
  - Timestamp extraction from paper metadata
- **Dependencies:** `aiohttp`, `pydantic`, `pandas`
- **Output:** `data/pwc_leaderboards/{benchmark}_raw.jsonl`
- **Estimated Complexity:** MODERATE (API pagination + timestamp parsing)

**Task 2: Manual Scraping Fallback**
- **Component:** `PWCLeaderboardWebScraper` class (BeautifulSoup + Selenium)
- **Trigger:** If API timestamp coverage <50%
- **Implementation:**
  - Selenium WebDriver for JavaScript-rendered pages
  - BeautifulSoup for HTML parsing
  - XPath selectors for submission dates
- **Dependencies:** `selenium`, `beautifulsoup4`, `webdriver-manager`
- **Output:** `data/pwc_leaderboards/{benchmark}_scraped.jsonl`
- **Estimated Complexity:** HIGH (dynamic content + anti-scraping measures)

**Task 3: Expert Survey Distribution**
- **Component:** Qualtrics survey setup + distribution protocol
- **Implementation:**
  - Survey design with branching logic (domain-specific questions)
  - Email template for distribution
  - Response tracking dashboard
- **Dependencies:** Qualtrics account, mailing list access
- **Output:** `data/expert_survey/responses.csv`
- **Estimated Complexity:** LOW (survey platform handles logic)

**Task 4: Data Validation**
- **Component:** `DataValidator` class
- **Implementation:**
  - Check timestamp format consistency (ISO 8601)
  - Verify benchmark coverage (all 3 benchmarks present)
  - Count high-confidence survey responses
  - Generate validation report
- **Dependencies:** `jsonschema`, `pandas`
- **Output:** `data/validation_report.json`
- **Estimated Complexity:** LOW (schema validation)

### 3.2 Baseline Experiment (None Required)

**Not applicable** for EXISTENCE hypothesis.

### 3.3 Experimental Pipeline

**Step 1: PWC Data Collection (Estimated: 2 hours)**
```python
# Pseudocode
scraper = PWCLeaderboardScraper(rate_limit=100)
for benchmark in ["imagenet", "glue", "squad"]:
    raw_data = await scraper.fetch_benchmark_sota(benchmark, start="2018-01-01", end="2024-12-31")
    submissions = scraper.extract_timestamped_submissions(raw_data)
    save_jsonl(f"data/pwc_leaderboards/{benchmark}_raw.jsonl", submissions)
```

**Step 2: Fallback Scraping (if needed) (Estimated: 4 hours)**
```python
if timestamp_coverage < 0.5:
    web_scraper = PWCLeaderboardWebScraper()
    for benchmark in ["imagenet", "glue", "squad"]:
        scraped_data = web_scraper.scrape_leaderboard_page(benchmark)
        save_jsonl(f"data/pwc_leaderboards/{benchmark}_scraped.jsonl", scraped_data)
```

**Step 3: Survey Distribution (Estimated: 1 hour setup + 1 week collection)**
```python
survey = QualtricsSurvey("ML_Saturation_Consensus")
survey.distribute(channels=["neurips_list", "icml_list", "twitter_ml"])
survey.monitor_responses(target=50, min_confidence=4)
```

**Step 4: Data Validation (Estimated: 1 hour)**
```python
validator = DataValidator()
pwc_report = validator.validate_pwc_data("data/pwc_leaderboards/")
survey_report = validator.validate_survey_data("data/expert_survey/responses.csv")
combined_report = {
    "pwc_completeness": pwc_report["timestamp_coverage"],
    "pwc_sample_size": pwc_report["submission_counts"],
    "survey_high_confidence": survey_report["high_confidence_count"],
    "survey_completion_rate": survey_report["completion_rate"]
}
save_json("data/validation_report.json", combined_report)
```

**Step 5: Success Criteria Check (Estimated: 0.5 hours)**
```python
def check_existence_criteria(report):
    pwc_pass = all(count >= 100 for count in report["pwc_sample_size"].values())
    survey_pass = all(count >= 30 for count in report["survey_high_confidence"].values())
    return pwc_pass and survey_pass

success = check_existence_criteria(combined_report)
print(f"H-E1 EXISTENCE: {'PASS' if success else 'FAIL'}")
```

### 3.4 Environment Setup

**Compute Requirements:**
- **Hardware:** Standard laptop (no GPU required)
- **Memory:** 8GB RAM
- **Storage:** 500MB (leaderboard data + survey responses)
- **Runtime:** ~8 hours (excluding 1-week survey collection)

**Software Dependencies:**
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

**Directory Structure:**
```
data/
├── pwc_leaderboards/
│   ├── imagenet_raw.jsonl
│   ├── glue_raw.jsonl
│   ├── squad_raw.jsonl
│   ├── imagenet_scraped.jsonl  # fallback
│   └── ...
├── expert_survey/
│   └── responses.csv
└── validation_report.json

src/
├── pwc_scraper.py          # PWCLeaderboardScraper
├── web_scraper.py          # PWCLeaderboardWebScraper (fallback)
├── data_validator.py       # DataValidator
└── main.py                 # Pipeline orchestration
```

---

## 4. Success Criteria

### 4.1 Primary Success Criteria

**PWC Data Availability:**
- ✅ ≥100 timestamped submissions per benchmark (ImageNet, GLUE, SQuAD)
- ✅ Timestamp coverage ≥80% (timestamped_submissions / total_submissions)
- ✅ Temporal range ≥4 years per benchmark (2018-2022 minimum)

**Expert Consensus Availability:**
- ✅ ≥30 high-confidence (≥4/5) responses per benchmark
- ✅ Survey completion rate >40%
- ✅ Response distribution balanced (vision/NLP: 40-60%, junior/senior: 30-70%)

**Combined Success:**
- Both PWC AND expert criteria met → **h-e1 PASS** → proceed to h-m1
- Either criterion fails → **h-e1 FAIL** → trigger failure response

### 4.2 Failure Response (from 02b_verification_plan.md)

**IF PWC data incomplete (<100 submissions or <80% timestamp coverage):**
- PIVOT to citation-based validation (SOTA mention decay in published papers)
- Alternative dataset: ArXiv papers citing benchmarks (Semantic Scholar API)
- Alternative metric: Citation velocity decay as saturation proxy

**IF expert consensus weak (<30 high-confidence responses or <50% agreement):**
- PIVOT to citation fallback per A1 assumption
- Use paper citation patterns as ground truth (citation surge = pre-saturation, decay = post-saturation)

**Failure Decision Tree:**
```
IF pwc_pass AND survey_pass:
    PROCEED to h-m1 (score convergence detection)
ELIF pwc_pass AND NOT survey_pass:
    PIVOT to citation-based expert consensus (Semantic Scholar API)
    RETRY h-e1 with citation data
ELIF NOT pwc_pass AND survey_pass:
    PIVOT to citation-based saturation detection
    REDESIGN h-m1, h-m2 to use citation velocity instead of PWC scores
ELSE:
    ABORT h-e1
    ESCALATE to user for alternative hypothesis formulation
```

---

## 5. Expected Outcomes

### 5.1 Quantitative Outcomes

**PWC Data:**
- Expected: 200-500 timestamped submissions per benchmark (based on PWC archive depth)
- Timestamp coverage: 70-90% (API limitations may require fallback scraping)
- Temporal density: 15-50 submissions/year per benchmark

**Expert Survey:**
- Expected: 40-60 total responses (60-80% from senior researchers)
- High-confidence responses: 35-45 per benchmark (assuming strong consensus on ImageNet saturation ~2017-2020)
- Completion rate: 50-70% (standard for academic surveys)

### 5.2 Qualitative Outcomes

**Data Quality:**
- PWC timestamps may have granularity issues (monthly vs daily)
- Expert consensus likely stronger for ImageNet (established saturation narrative) vs GLUE/SQuAD (ongoing debates)
- Survey responses may cluster around paradigm shift dates (GPT-3 2020, ViT 2021) rather than true saturation dates

**Insights:**
- If h-e1 PASS: Confirms data infrastructure ready for causal mechanism tests (h-m1, h-m2, h-m3)
- If h-e1 FAIL on PWC: Reveals limitations of public leaderboard archives, may require proprietary data sources
- If h-e1 FAIL on survey: Reveals lack of community consensus on saturation, may require objective citation metrics instead

---

## 6. Validation Protocol

### 6.1 Verification Steps (from 02b_verification_plan.md H-E1)

1. **Query PWC API** for ImageNet/GLUE/SQuAD leaderboards, extract submission timestamps (2018-2024)
2. **Count submissions** with valid timestamps per benchmark, verify ≥100 entries/benchmark
3. **Distribute expert survey** (50+ ML researchers, stratified vision/NLP, junior/senior)
4. **Filter responses** ≥4/5 confidence, count per benchmark, verify ≥30 responses/benchmark

### 6.2 Validation Checklist

**Data Validation:**
- [ ] PWC API responds with 200 status for all 3 benchmarks
- [ ] JSON parsing successful (no schema errors)
- [ ] Timestamp fields present and parseable (ISO 8601 or epoch)
- [ ] ≥100 timestamped submissions per benchmark
- [ ] Temporal coverage spans ≥4 years (2018-2022 minimum)

**Survey Validation:**
- [ ] Survey distributed to ≥50 researchers
- [ ] Completion rate >40%
- [ ] ≥30 high-confidence (≥4/5) responses per benchmark
- [ ] Response distribution balanced (domain, experience)

**Combined Validation:**
- [ ] `validation_report.json` generated successfully
- [ ] Success criteria check returns PASS or FAIL
- [ ] Failure response protocol documented (if FAIL)

### 6.3 Output Artifacts

**Required Files:**
```
data/pwc_leaderboards/imagenet_raw.jsonl       # PWC API data
data/pwc_leaderboards/glue_raw.jsonl
data/pwc_leaderboards/squad_raw.jsonl
data/expert_survey/responses.csv               # Survey responses
data/validation_report.json                    # Validation summary
```

**Validation Report Schema:**
```json
{
  "hypothesis_id": "h-e1",
  "timestamp": "2026-08-28T12:00:00Z",
  "pwc_data": {
    "imagenet": {
      "total_submissions": 450,
      "timestamped_submissions": 380,
      "timestamp_coverage": 0.84,
      "temporal_range": "2018-01-15 to 2024-11-30"
    },
    "glue": {...},
    "squad": {...}
  },
  "expert_survey": {
    "total_responses": 62,
    "completion_rate": 0.62,
    "high_confidence_responses": {
      "imagenet": 45,
      "glue": 38,
      "squad": 41
    },
    "domain_distribution": {"vision": 0.52, "nlp": 0.48},
    "experience_distribution": {"junior": 0.35, "senior": 0.65}
  },
  "success_criteria": {
    "pwc_pass": true,
    "survey_pass": true,
    "overall_pass": true
  },
  "failure_response": null
}
```

---

## 7. Implementation Resources

### 7.1 Papers With Code API Documentation

**Official API Docs:**
- https://paperswithcode.com/api/v1/docs/
- Endpoints: `/benchmarks/`, `/papers/`, `/sota/`
- Rate limit: 100 requests/minute
- Authentication: None required (public API)

**Known Limitations:**
- Timestamp granularity: Monthly for older submissions, daily for recent
- Missing fields: Some submissions lack paper metadata
- Leaderboard completeness: Not all historical submissions archived

### 7.2 Alternative Data Sources (Fallback)

**If PWC API insufficient:**
1. **ArXiv + Semantic Scholar** for citation-based validation
2. **GitHub repositories** with benchmark result tables (e.g., `pytorch/vision` model zoo)
3. **Manual scraping** of PWC leaderboard HTML pages

### 7.3 Expert Survey Distribution Channels

**Primary Channels:**
- NeurIPS/ICML/CVPR mailing lists (requires conference committee approval)
- ML Twitter community (ML influencers with >10k followers)
- LinkedIn ML groups (Deep Learning, Computer Vision, NLP)

**Secondary Channels:**
- Reddit r/MachineLearning (survey post)
- Discord ML communities (Weights & Biases, Hugging Face)
- Direct outreach to benchmark authors (ImageNet, GLUE, SQuAD creators)

**Incentives:**
- Early access to saturation detection tool (if built in Phase 5)
- Co-authorship on resulting paper (for detailed responses)
- $10 Amazon gift card raffle (1 winner per 10 responses)

---

## 8. Risk Mitigation

### 8.1 Data Collection Risks

**Risk 1: PWC API rate limiting**
- **Mitigation:** Implement exponential backoff, spread requests over 2-3 days
- **Fallback:** Manual scraping with BeautifulSoup + Selenium

**Risk 2: Survey low response rate (<40%)**
- **Mitigation:** Multi-channel distribution, incentives, follow-up reminders
- **Fallback:** Lower threshold to ≥20 high-confidence responses (adjust success criteria)

**Risk 3: Timestamp data incomplete (coverage <50%)**
- **Mitigation:** Combine API + web scraping for comprehensive coverage
- **Fallback:** Pivot to citation-based validation (per failure response protocol)

### 8.2 Implementation Risks

**Risk 4: Web scraping blocked by anti-bot measures**
- **Mitigation:** Selenium with human-like delays, rotating user agents
- **Fallback:** Manual data entry for critical benchmarks (ImageNet priority)

**Risk 5: Survey response bias (senior researchers over-represented)**
- **Mitigation:** Stratified sampling, targeted outreach to junior researchers
- **Fallback:** Weight responses by experience level in analysis

---

## 9. Timeline

| Phase | Task | Duration | Dependencies |
|-------|------|----------|--------------|
| **Setup** | Environment setup, API testing | 1 hour | None |
| **Data Collection** | PWC API scraping (all benchmarks) | 2 hours | Setup |
| **Fallback** | Manual web scraping (if needed) | 4 hours | Data Collection |
| **Survey** | Survey distribution + monitoring | 1 week | Setup |
| **Validation** | Data validation + report generation | 1 hour | Data Collection, Survey |
| **Analysis** | Success criteria check + failure response | 0.5 hours | Validation |

**Total Duration:** 8.5 hours (excluding 1-week survey collection time)

**Critical Path:** Survey collection (1 week wait time) is bottleneck. PWC scraping can proceed in parallel.

---

## 10. Next Steps (Phase 3: Implementation Planning)

**Upon h-e1 PASS:**
1. Proceed to h-m1 (Score Convergence Detection) experiment design
2. Use validated PWC data for rolling window std(top-5) analysis
3. Use expert consensus dates as ground truth for alignment validation

**Upon h-e1 FAIL:**
1. Execute failure response protocol (citation-based pivot)
2. Redesign h-m1, h-m2, h-m3 for citation velocity metrics
3. Update verification_state.yaml with pivot decision

**Implementation Planning Inputs (Phase 3):**
- Validated dataset paths (`data/pwc_leaderboards/*.jsonl`)
- Sample size statistics (for power analysis in h-m1, h-m2)
- Expert consensus dates (ground truth for temporal alignment in h-m3)

---

**Document Status:** DRAFT  
**Next Review:** Phase 3 Implementation Planning  
**Approval Required:** User confirmation before Phase 4 execution
