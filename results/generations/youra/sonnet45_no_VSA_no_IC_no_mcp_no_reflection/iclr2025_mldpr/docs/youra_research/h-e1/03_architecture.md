# Architecture Document: h-e1 Data Availability Verification

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE  
**Date:** 2026-08-28  
**Infrastructure Tier:** LIGHT (minimal)

---

## Codebase Analysis (Serena)

**Status:** Green-field implementation (no existing codebase to analyze)

**Existing Patterns:** None (FOUNDATION hypothesis)

**Recommended Patterns:**
- Simple script-based organization (no framework overhead)
- Single-file modules for data collection components
- JSON/JSONL for data serialization

---

## Applied Patterns

Applied: **Data Collection Script Pattern** (Archon KB: standalone data gathering with validation)  
Applied: **Async HTTP Client Pattern** (Archon KB: rate-limited API scraping)

---

## System Architecture

### Module Structure

```
h-e1/
├── src/
│   ├── pwc_scraper.py         # PWC API client
│   ├── web_scraper.py         # Fallback HTML scraping
│   ├── data_validator.py      # Validation logic
│   └── main.py                # Pipeline orchestration
├── data/
│   ├── pwc_leaderboards/      # API outputs
│   └── expert_survey/         # Survey data
├── requirements.txt           # Dependencies
└── README.md                  # Usage instructions
```

### Module Descriptions

**pwc_scraper.py** (Complexity: 8)
- `PWCLeaderboardScraper` class
- Async HTTP client with rate limiting
- Timestamp extraction from paper metadata
- JSONL output generation

**web_scraper.py** (Complexity: 12)
- `PWCLeaderboardWebScraper` class
- Selenium + BeautifulSoup integration
- Fallback logic triggered by low API coverage
- XPath selectors for submission dates

**data_validator.py** (Complexity: 5)
- `DataValidator` class
- Schema validation (jsonschema)
- Completeness checks (sample counts, coverage %)
- Validation report generation

**main.py** (Complexity: 6)
- Pipeline orchestration
- API → fallback flow control
- Success criteria evaluation
- Console output formatting

### File Organization (LIGHT tier)

**Configuration:** Hardcoded constants (no YAML)
```python
# config.py
BENCHMARKS = ["imagenet", "glue", "squad"]
PWC_RATE_LIMIT = 100  # req/min
MIN_SAMPLE_SIZE = 100
MIN_EXPERT_RESPONSES = 30
```

**Logging:** Print statements + CSV progress log
```python
import csv
with open("data/scraping_log.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "benchmark", "submissions_scraped"])
```

**Testing:** Single smoke test script (test_main.py)
```python
# test_main.py
def test_pwc_api_connection():
    scraper = PWCLeaderboardScraper()
    response = scraper.fetch_benchmark_list()
    assert len(response) > 0
```

---

## Proposed Tasks (Epic Level)

### Epic 1: PWC API Data Collection
**Complexity: 8** (Module: 3, Dependencies: 2, Algorithm: 2, Integration: 1)

**Scope:**
- Implement `PWCLeaderboardScraper` with async HTTP
- Rate limiting (100 req/min)
- Timestamp extraction from paper metadata
- Output: `data/pwc_leaderboards/{benchmark}_raw.jsonl`

**Acceptance Criteria:**
- API client handles 3 benchmarks (ImageNet, GLUE, SQuAD)
- Extracts ≥100 submissions with timestamps per benchmark
- Retry logic with exponential backoff (3 attempts)

**Estimated Effort:** ~4 hours

---

### Epic 2: Fallback Web Scraping
**Complexity: 12** (Module: 4, Dependencies: 3, Algorithm: 3, Integration: 2)

**Scope:**
- Implement `PWCLeaderboardWebScraper` with Selenium + BeautifulSoup
- XPath selectors for submission dates
- Trigger logic: API coverage <50%
- Output: `data/pwc_leaderboards/{benchmark}_scraped.jsonl`

**Acceptance Criteria:**
- Web scraper extracts timestamps from HTML
- Handles JavaScript-rendered pages
- Merges API + scraped data without duplicates

**Estimated Effort:** ~6 hours

---

### Epic 3: Expert Survey Setup
**Complexity: 4** (Module: 1, Dependencies: 1, Algorithm: 1, Integration: 1)

**Scope:**
- Design Qualtrics survey (3 benchmarks, confidence scale)
- Email distribution template
- Response tracking dashboard

**Acceptance Criteria:**
- Survey includes saturation year + confidence questions
- Distributed to ≥50 researchers
- CSV export: `data/expert_survey/responses.csv`

**Estimated Effort:** ~2 hours (+ 1 week collection)

---

### Epic 4: Data Validation
**Complexity: 5** (Module: 2, Dependencies: 1, Algorithm: 1, Integration: 1)

**Scope:**
- Implement `DataValidator` class
- Schema validation (timestamp format, required fields)
- Completeness checks (sample size, coverage %)
- Output: `data/validation_report.json`

**Acceptance Criteria:**
- Validates PWC data (≥100 submissions, ≥80% coverage)
- Validates survey data (≥30 high-confidence responses)
- Generates JSON report with pass/fail flags

**Estimated Effort:** ~2 hours

---

### Epic 5: Pipeline Orchestration
**Complexity: 6** (Module: 2, Dependencies: 2, Algorithm: 1, Integration: 1)

**Scope:**
- Implement `main.py` orchestration script
- API → fallback flow control
- Success criteria evaluation
- Console output formatting

**Acceptance Criteria:**
- Executes: API scraping → fallback (if needed) → validation
- Prints "H-E1 EXISTENCE: PASS/FAIL"
- Logs progress to CSV

**Estimated Effort:** ~3 hours

---

### Epic 6: Environment Setup
**Complexity: 3** (Module: 1, Dependencies: 1, Algorithm: 0, Integration: 1)

**Scope:**
- Create `requirements.txt`
- Write `README.md` with usage instructions
- Set up directory structure (`data/`, `src/`)

**Acceptance Criteria:**
- Dependencies installable via `pip install -r requirements.txt`
- README includes: setup steps, usage, data paths
- Directory structure created (mkdir -p)

**Estimated Effort:** ~1 hour

---

## Task Complexity Summary

| Epic | Complexity | Category |
|------|------------|----------|
| Epic 1: PWC API Collection | 8 | MODERATE |
| Epic 2: Fallback Scraping | 12 | HIGH |
| Epic 3: Survey Setup | 4 | LOW |
| Epic 4: Validation | 5 | LOW |
| Epic 5: Orchestration | 6 | MODERATE |
| Epic 6: Environment | 3 | LOW |

**Total Epic Tasks:** 6  
**Avg Complexity:** 6.3  
**Budget Compliance:** PASS (LIGHT tier: 4-8 tasks, actual: 6)

---

## External Dependencies

**Python Packages:**
```
aiohttp==3.9.1        # Async HTTP for PWC API
pydantic==2.5.0       # Data validation
pandas==2.1.4         # Data manipulation
selenium==4.16.0      # Web scraping
beautifulsoup4==4.12.2 # HTML parsing
webdriver-manager==4.0.1  # ChromeDriver auto-install
jsonschema==4.20.0    # Schema validation
numpy==1.26.2         # Array operations
```

**External Services:**
- Papers With Code API (https://paperswithcode.com/api/v1/)
- Qualtrics (survey platform)
- Chrome/ChromeDriver (for Selenium)

---

## Integration Points

**Data Flow:**
```
PWC API → pwc_scraper.py → data/pwc_leaderboards/*.jsonl
                            ↓
                      data_validator.py → validation_report.json
                            ↑
Expert Survey → responses.csv → data/expert_survey/
```

**Failure Handling:**
```
API scraping → Check coverage
                ↓
           coverage <50%?
                ↓
           Yes → web_scraper.py (fallback)
                ↓
           Merge → validation
```

---

## Next Steps

**After Architecture Approval:**
1. Proceed to Step 4: Complexity Analysis
2. Generate detailed subtasks from Epic tasks
3. Allocate subtask budget based on LIGHT tier constraints

**Phase 4 Implementation:**
- Start with Epic 6 (environment setup)
- Parallel: Epic 1 (API) + Epic 3 (survey)
- Conditional: Epic 2 (fallback if needed)
- Final: Epic 4 (validation) + Epic 5 (orchestration)

---

**Document Status:** DRAFT  
**Next Review:** Step 4 (Budget Allocation)
