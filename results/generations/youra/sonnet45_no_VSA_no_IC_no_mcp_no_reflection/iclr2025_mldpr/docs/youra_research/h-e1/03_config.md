# Configuration Design Document: h-e1 Data Availability Verification

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE  
**Date:** 2026-08-28  
**Subtask Budget:** 1 task  
**Infrastructure Tier:** LIGHT (minimal)

---

## Applied Patterns

Applied: **Hardcoded Config Pattern** (Archon KB: LIGHT tier uses constants, not YAML)

---

## Configuration Schema

### config.py (Hardcoded Constants)

```python
"""
Configuration for h-e1 data availability verification.
LIGHT tier: No YAML files, hardcoded constants for simplicity.
"""

# PWC API Configuration
PWC_API_BASE_URL = "https://paperswithcode.com/api/v1"
PWC_RATE_LIMIT = 100  # requests per minute
PWC_RETRY_ATTEMPTS = 3
PWC_RETRY_DELAYS = [1.0, 2.0, 4.0]  # seconds (exponential backoff)

# Benchmark Configuration
BENCHMARKS = ["imagenet", "glue", "squad"]
DATE_RANGE_START = "2018-01-01"
DATE_RANGE_END = "2024-12-31"

# Data Paths
DATA_ROOT = "data/"
PWC_OUTPUT_DIR = "data/pwc_leaderboards/"
SURVEY_OUTPUT_DIR = "data/expert_survey/"
VALIDATION_REPORT_PATH = "data/validation_report.json"
SCRAPING_LOG_PATH = "data/scraping_log.csv"

# Success Criteria Thresholds
MIN_SAMPLE_SIZE = 100  # per benchmark
MIN_TIMESTAMP_COVERAGE = 0.80  # 80%
MIN_TEMPORAL_RANGE_YEARS = 4  # minimum years of data
MIN_EXPERT_RESPONSES = 30  # high-confidence responses per benchmark
MIN_SURVEY_COMPLETION_RATE = 0.40  # 40%

# Web Scraping Configuration (Fallback)
FALLBACK_TRIGGER_THRESHOLD = 0.50  # API coverage below 50% triggers web scraping
SELENIUM_TIMEOUT = 10  # seconds
CHROME_HEADLESS = True

# XPath Selectors (Web Scraping)
XPATH_SELECTORS = {
    "submission_date": "//div[@class='paper-card']//span[@class='date']",
    "model_name": "//div[@class='paper-card']//h3[@class='model-name']",
    "score": "//div[@class='paper-card']//span[@class='metric-value']"
}

# Logging
LOG_LEVEL = "INFO"  # print() statements for LIGHT tier
LOG_FORMAT = "{timestamp},{benchmark},{submissions_scraped}"

# Survey Distribution (Manual Process)
SURVEY_CHANNELS = [
    "neurips_list",
    "icml_list",
    "twitter_ml",
    "linkedin_ml_groups"
]
SURVEY_TARGET_SAMPLE = 50
SURVEY_STRATIFICATION = {
    "domain": {"vision": 0.5, "nlp": 0.5},
    "experience": {"junior": 0.4, "senior": 0.6}
}
```

---

## Dataclasses (Minimal for LIGHT tier)

### PWC API Models (pydantic)

```python
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

class LeaderboardSubmission(BaseModel):
    """Validated PWC leaderboard submission."""
    benchmark_name: str
    model_name: str
    score: float
    submission_date: str  # ISO 8601
    paper_id: Optional[str] = None
    
    @field_validator('submission_date')
    def validate_date_format(cls, v):
        """Ensure ISO 8601 format."""
        try:
            datetime.fromisoformat(v)
        except ValueError:
            raise ValueError(f"Invalid date format: {v}, expected ISO 8601")
        return v

class ValidationReport(BaseModel):
    """Combined validation report for h-e1."""
    hypothesis_id: str = "h-e1"
    timestamp: str  # ISO 8601
    pwc_data: dict
    expert_survey: dict
    success_criteria: dict
```

---

## Hyperparameters (None for EXISTENCE)

**Not applicable** for data collection task. No model training, no hyperparameters.

---

## Environment Variables

**None required.** All configuration is hardcoded in `config.py` (LIGHT tier design).

---

## Logging Configuration (LIGHT Tier)

### Print-Based Logging
```python
# main.py
import csv
from datetime import datetime

def log_progress(benchmark: str, submissions_scraped: int):
    """Log scraping progress to CSV."""
    with open("data/scraping_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            benchmark,
            submissions_scraped
        ])
    print(f"[{datetime.now()}] Scraped {submissions_scraped} submissions for {benchmark}")
```

**No structured logging** (no WandB, no logging framework). Simple print + CSV.

---

## Directory Structure Setup

```python
# setup.py (create folders on first run)
import os

def create_directory_structure():
    """Create data directories if they don't exist."""
    directories = [
        "data",
        "data/pwc_leaderboards",
        "data/expert_survey"
    ]
    for dir_path in directories:
        os.makedirs(dir_path, exist_ok=True)
    print("✓ Directory structure created")

if __name__ == "__main__":
    create_directory_structure()
```

---

## Subtask: XPath Selector Configuration

**Complexity:** 3 (low)  
**Scope:** Define and test XPath selectors for web scraping fallback

**Implementation:**
```python
# xpath_config.py
XPATH_SELECTORS = {
    "imagenet": {
        "submission_date": "//div[@class='sota-row']//td[@data-date]",
        "model_name": "//div[@class='sota-row']//td[@class='model-col']//a",
        "score": "//div[@class='sota-row']//td[@class='metric-col']"
    },
    "glue": {
        "submission_date": "//tr[@class='leaderboard-entry']//td[1]",
        "model_name": "//tr[@class='leaderboard-entry']//td[2]//a",
        "score": "//tr[@class='leaderboard-entry']//td[3]"
    },
    "squad": {
        "submission_date": "//div[@class='submission']//span[@data-timestamp]",
        "model_name": "//div[@class='submission']//h4",
        "score": "//div[@class='submission']//span[@class='score']"
    }
}

def get_selectors(benchmark: str) -> dict:
    """Get XPath selectors for a specific benchmark."""
    if benchmark not in XPATH_SELECTORS:
        raise ValueError(f"Unknown benchmark: {benchmark}")
    return XPATH_SELECTORS[benchmark]
```

**Testing:** Manual verification on live PWC pages (curl + verify XPath matches).

---

## Configuration Summary

| Tier | Config Method | Logging | Testing |
|------|---------------|---------|---------|
| LIGHT | Hardcoded (config.py) | print + CSV | Smoke test |

**No YAML files** (per LIGHT tier specification)  
**No dataclasses** for configuration (pydantic used only for data validation)  
**No environment variables** (all values in code)

---

## Next Steps

**After Config Approval:**
1. Proceed to Step 6: Overall Complexity Assessment
2. Verify all configuration values with Phase 2C experiment brief
3. Generate final task list with configuration tasks included

**Phase 4 Implementation:**
- Create `config.py` first (Epic 6: Environment Setup)
- Use constants from `config.py` in all modules
- Update XPath selectors if PWC HTML structure changes

---

**Document Status:** DRAFT  
**Next Review:** Step 6 (Complexity Assessment)
