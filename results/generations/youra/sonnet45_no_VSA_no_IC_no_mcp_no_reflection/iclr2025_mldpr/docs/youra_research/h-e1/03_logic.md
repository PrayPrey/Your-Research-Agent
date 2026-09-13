# Logic Design Document: h-e1 Data Availability Verification

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE  
**Date:** 2026-08-28  
**Subtask Budget:** 3 tasks

---

## Codebase Analysis (Serena)

**Status:** Green-field implementation (no existing codebase to analyze)

**Existing APIs:** None (FOUNDATION hypothesis)

**Recommended Patterns:**
- Async HTTP client pattern for rate-limited APIs
- Dataclass-based validation models (pydantic)
- Retry decorator pattern for resilience

---

## Applied Patterns

Applied: **Async HTTP Client Pattern** (Archon KB: rate-limited API scraping with backoff)  
Applied: **Data Validation Pattern** (Archon KB: schema-based completeness checks)

---

## API Signatures

### pwc_scraper.py

#### PWCLeaderboardScraper
```python
from typing import List, Dict, Optional
from pydantic import BaseModel
import aiohttp

class LeaderboardSubmission(BaseModel):
    benchmark_name: str
    model_name: str
    score: float
    submission_date: str  # ISO 8601
    paper_id: Optional[str] = None

class PWCLeaderboardScraper:
    def __init__(self, rate_limit: int = 100):
        """
        Args:
            rate_limit: Max requests per minute (default: 100)
        """
        self.rate_limit = rate_limit
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def fetch_benchmark_sota(
        self,
        benchmark: str,
        start_date: str,
        end_date: str
    ) -> List[Dict]:
        """
        Fetch SOTA results for a benchmark with date filtering.
        
        Args:
            benchmark: Benchmark slug (e.g., 'imagenet', 'glue', 'squad')
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
        
        Returns:
            List of raw API response dicts
        
        Raises:
            aiohttp.ClientError: On API failure after retries
        """
        pass
    
    def extract_timestamped_submissions(
        self,
        raw_data: List[Dict]
    ) -> List[LeaderboardSubmission]:
        """
        Extract submissions with valid timestamps from raw API data.
        
        Args:
            raw_data: Raw API responses
        
        Returns:
            Validated LeaderboardSubmission objects
        """
        pass
    
    async def _rate_limited_request(
        self,
        url: str,
        retries: int = 3
    ) -> Dict:
        """
        Execute rate-limited HTTP GET with exponential backoff.
        
        Args:
            url: API endpoint URL
            retries: Max retry attempts (default: 3)
        
        Returns:
            Parsed JSON response
        
        Raises:
            aiohttp.ClientError: After exhausting retries
        """
        pass
```

**Subtask 1: Timestamp Extraction Logic**
- **Complexity:** 6 (moderate)
- **Scope:** Implement `extract_timestamped_submissions()` method
- **Details:**
  - Parse paper publication dates from `/papers/` endpoint
  - Cross-reference with benchmark results from `/sota/`
  - Handle missing timestamps gracefully (skip submission)
  - Validate ISO 8601 format with `datetime.fromisoformat()`

**Tensor Shapes:** N/A (data collection, no tensors)

---

### web_scraper.py

#### PWCLeaderboardWebScraper
```python
from selenium import webdriver
from bs4 import BeautifulSoup
from typing import List

class PWCLeaderboardWebScraper:
    def __init__(self):
        self.driver: webdriver.Chrome = None
    
    def scrape_leaderboard_page(
        self,
        benchmark: str
    ) -> List[LeaderboardSubmission]:
        """
        Scrape leaderboard HTML page for timestamped submissions.
        
        Args:
            benchmark: Benchmark slug
        
        Returns:
            List of LeaderboardSubmission objects
        
        Raises:
            selenium.common.exceptions.WebDriverException: On scraping failure
        """
        pass
    
    def _extract_submission_dates(
        self,
        soup: BeautifulSoup
    ) -> List[str]:
        """
        Extract submission dates using XPath selectors.
        
        Args:
            soup: BeautifulSoup parsed HTML
        
        Returns:
            List of date strings (ISO 8601)
        """
        pass
```

**Subtask 2: Web Scraping Flow Control**
- **Complexity:** 8 (high)
- **Scope:** Implement fallback trigger logic and Selenium integration
- **Details:**
  - Check API timestamp coverage: `(timestamped / total) >= 0.5`
  - If coverage <50%, launch `PWCLeaderboardWebScraper`
  - XPath selector: `//div[@class='paper-card']//span[@class='date']`
  - Merge API + scraped data (deduplicate by `model_name` + `benchmark`)

**Tensor Shapes:** N/A

---

### data_validator.py

#### DataValidator
```python
from typing import Dict, List
from jsonschema import validate
import pandas as pd

class DataValidator:
    def __init__(self):
        self.pwc_schema = {...}  # JSON schema for PWC data
        self.survey_schema = {...}  # JSON schema for survey data
    
    def validate_pwc_data(
        self,
        data_path: str
    ) -> Dict[str, any]:
        """
        Validate PWC leaderboard data completeness.
        
        Args:
            data_path: Path to pwc_leaderboards/ directory
        
        Returns:
            {
                'timestamp_coverage': float,  # 0.0-1.0
                'submission_counts': {benchmark: count},
                'temporal_range': {benchmark: (start, end)},
                'pass': bool
            }
        """
        pass
    
    def validate_survey_data(
        self,
        responses_csv: str
    ) -> Dict[str, any]:
        """
        Validate expert survey response completeness.
        
        Args:
            responses_csv: Path to responses.csv
        
        Returns:
            {
                'high_confidence_count': {benchmark: count},
                'completion_rate': float,
                'domain_distribution': {domain: percent},
                'pass': bool
            }
        """
        pass
```

**Subtask 3: Completeness Check Logic**
- **Complexity:** 5 (low-moderate)
- **Scope:** Implement validation report generation
- **Details:**
  - Schema validation: `jsonschema.validate(data, schema)`
  - Sample count check: `len(df[df['timestamp'].notnull()]) >= 100`
  - Coverage calculation: `(non_null / total) * 100`
  - High-confidence filter: `df[df['confidence'] >= 4]`

**Tensor Shapes:** N/A

---

### main.py

#### Pipeline Orchestration
```python
import asyncio
from pwc_scraper import PWCLeaderboardScraper
from web_scraper import PWCLeaderboardWebScraper
from data_validator import DataValidator

async def main():
    """Execute h-e1 data availability verification pipeline."""
    # Step 1: PWC API scraping
    scraper = PWCLeaderboardScraper()
    for benchmark in ["imagenet", "glue", "squad"]:
        raw_data = await scraper.fetch_benchmark_sota(
            benchmark, "2018-01-01", "2024-12-31"
        )
        submissions = scraper.extract_timestamped_submissions(raw_data)
        # Save to JSONL
    
    # Step 2: Fallback scraping (conditional)
    validator = DataValidator()
    pwc_report = validator.validate_pwc_data("data/pwc_leaderboards/")
    
    if pwc_report['timestamp_coverage'] < 0.5:
        web_scraper = PWCLeaderboardWebScraper()
        for benchmark in ["imagenet", "glue", "squad"]:
            scraped = web_scraper.scrape_leaderboard_page(benchmark)
            # Merge with API data
    
    # Step 3: Survey validation (assumes manual collection)
    survey_report = validator.validate_survey_data("data/expert_survey/responses.csv")
    
    # Step 4: Success criteria check
    h_e1_pass = pwc_report['pass'] and survey_report['pass']
    print(f"H-E1 EXISTENCE: {'PASS' if h_e1_pass else 'FAIL'}")
    
    # Save validation report
    with open("data/validation_report.json", "w") as f:
        json.dump({
            'pwc_data': pwc_report,
            'expert_survey': survey_report,
            'overall_pass': h_e1_pass
        }, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
```

**Pseudo-code:** Flow control logic shown above

**Algorithms:**
- **Rate Limiting:** Token bucket algorithm (100 tokens/minute)
- **Retry Backoff:** Exponential backoff (1s, 2s, 4s delays)
- **Deduplication:** Hash-based dedup on `(model_name, benchmark)` tuple

---

## Data Flows

**PWC API → Validation:**
```
fetch_benchmark_sota() → List[Dict]
    ↓
extract_timestamped_submissions() → List[LeaderboardSubmission]
    ↓
save_jsonl() → data/pwc_leaderboards/{benchmark}_raw.jsonl
    ↓
validate_pwc_data() → Dict (report)
```

**Fallback Flow:**
```
IF timestamp_coverage < 0.5:
    scrape_leaderboard_page() → List[LeaderboardSubmission]
        ↓
    merge(api_data, scraped_data) → deduplicated List
        ↓
    save_jsonl() → data/pwc_leaderboards/{benchmark}_scraped.jsonl
```

---

## Complexity Breakdown

| Module | Subtasks | Total Complexity |
|--------|----------|------------------|
| pwc_scraper.py | 1 | 6 |
| web_scraper.py | 1 | 8 |
| data_validator.py | 1 | 5 |

**Total Subtasks:** 3  
**Avg Complexity:** 6.3  
**Budget Compliance:** PASS (allocated: 3, actual: 3)

---

## Error Handling

**API Failures:**
- Retry with exponential backoff (3 attempts)
- Log failure to `data/scraping_log.csv`
- Raise `aiohttp.ClientError` after exhausting retries

**Schema Validation Failures:**
- Log invalid records to `data/validation_errors.jsonl`
- Skip invalid submissions (do not block pipeline)
- Report error count in `validation_report.json`

**Web Scraping Failures:**
- Selenium timeout: retry once with 2x wait time
- XPath selector mismatch: log warning, return empty list
- Do not block pipeline (fallback is optional)

---

## Next Steps

**After Logic Approval:**
1. Proceed to Step 6: Overall Complexity Assessment
2. Finalize configuration schemas (03_config.md)
3. Generate task list with priority ordering

**Phase 4 Implementation:**
- Implement Subtask 1 (timestamp extraction) first
- Implement Subtask 3 (validation) in parallel with Subtask 1
- Implement Subtask 2 (web scraping) only if needed

---

**Document Status:** DRAFT  
**Next Review:** Step 6 (Complexity Assessment)
