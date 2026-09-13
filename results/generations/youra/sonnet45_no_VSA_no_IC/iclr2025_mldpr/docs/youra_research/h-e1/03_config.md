# Configuration Schema: H-E1 Friction Measurement System

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE (Proof of Concept)  
**Config Format:** Hardcoded dict (Python)

---

## Configuration Schema

```python
"""Configuration for h-e1: Platform Friction Measurement Feasibility"""

CONFIG = {
    # Sample Sizes (Pilot Phase)
    "pilot": {
        "openml": 100,
        "huggingface": 100,
        "uci": 50,
        "total": 250
    },
    
    # Validation Sample
    "validation": {
        "openml": 40,
        "huggingface": 40,
        "uci": 20,
        "total": 100
    },
    
    # API Configuration
    "api": {
        "timeout": 30,
        "retry_max": 3,
        "retry_backoff": [1, 2, 4]
    },
    
    # Rate Limiting
    "rate_limit": {
        "uci": 1.0,  # 1 second between requests
        "openml": 0.0,  # No enforced rate limit
        "huggingface": 0.0
    },
    
    # Parsing Rules - Thresholds
    "parsing": {
        "preprocessing_code_min_length": 50,
        "data_source_url_min_length": 10,
        "license_min_length": 5,
        "dependencies_min_length": 20,
        
        # Keyword Lists
        "code_keywords": ["import", "function", "def", "library", "require", "use", "from"],
        "code_extensions": [".py", ".R", ".ipynb", ".jl", ".m", ".java"],
        "license_placeholders": ["N/A", "Unknown", "TODO", "None", "null"],
        
        # Regex Patterns
        "url_pattern": r"http(s)?://[^\s]+",
        "date_iso": r"\d{4}-\d{2}-\d{2}",
        "date_slash": r"\d{1,2}/\d{1,2}/\d{4}",
        "date_year": r"\b(19|20)\d{2}\b",
        "version_semver": r"\d+\.\d+(\.\d+)?",
        "version_indicator": r"(v|version|Ver\.?)\s*\d+"
    },
    
    # Success Rate Thresholds (MUST_WORK gate)
    "thresholds": {
        "openml_success": 0.80,
        "huggingface_success": 0.80,
        "uci_success": 0.70,
        "parsing_accuracy": 0.90,
        "per_field_accuracy": 0.75,
        "max_hours_10k": 336
    },
    
    # Paths
    "paths": {
        "data": "data",
        "pilot": "data/pilot_extraction.json",
        "validation": "data/validation_sample.json",
        "ground_truth": "data/manual_annotations.csv",
        "logs": "logs",
        "results": "results"
    },
    
    # Reproducibility
    "seed": 42
}
```

---

## Field-Specific Validation Rules

### 1. preprocessing_code

**Rule:**
```python
def is_preprocessing_code_present(value):
    if not value or len(value) <= CONFIG["parsing"]["preprocessing_code_min_length"]:
        return False
    
    has_keywords = any(kw in value.lower() for kw in CONFIG["parsing"]["code_keywords"])
    has_extension = any(ext in value for ext in CONFIG["parsing"]["code_extensions"])
    
    return has_keywords or has_extension
```

**Rationale:** Length >50 chars filters placeholder text. Keyword/extension check confirms code content.

---

### 2. data_source_url

**Rule:**
```python
import re

def is_data_source_url_present(value):
    if not value or len(value) <= CONFIG["parsing"]["data_source_url_min_length"]:
        return False
    
    return bool(re.search(CONFIG["parsing"]["url_pattern"], value))
```

**Rationale:** URL regex validates format. Length >10 excludes broken fragments.

---

### 3. collection_date

**Rule:**
```python
import re

def is_collection_date_present(value):
    if not value:
        return False
    
    patterns = [
        CONFIG["parsing"]["date_iso"],
        CONFIG["parsing"]["date_slash"],
        CONFIG["parsing"]["date_year"]
    ]
    
    return any(re.search(p, str(value)) for p in patterns)
```

**Rationale:** Supports multiple date formats (ISO 8601, MM/DD/YYYY, year-only).

---

### 4. license

**Rule:**
```python
def is_license_present(value):
    if not value or len(value) <= CONFIG["parsing"]["license_min_length"]:
        return False
    
    return value not in CONFIG["parsing"]["license_placeholders"]
```

**Rationale:** Length >5 excludes abbreviations. Placeholder list filters common non-values.

---

### 5. version

**Rule:**
```python
import re

def is_version_present(value):
    if not value:
        return False
    
    semver = re.search(CONFIG["parsing"]["version_semver"], str(value))
    indicator = re.search(CONFIG["parsing"]["version_indicator"], str(value), re.IGNORECASE)
    
    return bool(semver or indicator)
```

**Rationale:** Matches semantic versioning (1.0.0) or labeled versions (v2, Version 3).

---

### 6. dependencies

**Rule:**
```python
def is_dependencies_present(value):
    if isinstance(value, list):
        return len(value) > 0
    
    if isinstance(value, str):
        return len(value) > CONFIG["parsing"]["dependencies_min_length"]
    
    return False
```

**Rationale:** Lists with elements are present. Text >20 chars likely contains package names.

---

## Configuration Validation

```python
def validate_config():
    """Validate configuration constraints"""
    
    # Sample size consistency
    assert CONFIG["pilot"]["total"] == sum([
        CONFIG["pilot"]["openml"],
        CONFIG["pilot"]["huggingface"],
        CONFIG["pilot"]["uci"]
    ])
    
    assert CONFIG["validation"]["total"] == sum([
        CONFIG["validation"]["openml"],
        CONFIG["validation"]["huggingface"],
        CONFIG["validation"]["uci"]
    ])
    
    # Retry backoff exponential
    assert len(CONFIG["api"]["retry_backoff"]) == CONFIG["api"]["retry_max"]
    
    # Threshold ranges
    for key, value in CONFIG["thresholds"].items():
        if "success" in key or "accuracy" in key:
            assert 0 <= value <= 1, f"{key} must be in [0,1]"
    
    # Required paths exist in dict
    required = ["data", "pilot", "validation", "ground_truth", "logs", "results"]
    for p in required:
        assert p in CONFIG["paths"]
    
    return True
```

---

## Example Usage

```python
from config import CONFIG, validate_config

# Validate on load
validate_config()

# Access configuration
pilot_size = CONFIG["pilot"]["openml"]  # 100
timeout = CONFIG["api"]["timeout"]  # 30
min_accuracy = CONFIG["thresholds"]["parsing_accuracy"]  # 0.90

# Apply parsing rule
from parsing_rules import is_license_present

license_value = "MIT License"
is_present = is_license_present(license_value)  # True
```

---

## Rationale for Non-Standard Values

**pilot.uci = 50** (not 100): Web scraping slower than API access. 50 sufficient for feasibility test.

**rate_limit.uci = 1.0**: UCI documentation recommends 1 req/sec to avoid IP blocking.

**parsing.preprocessing_code_min_length = 50**: Empirically tested threshold from stephlabou/comparative-machine-learning-metadata codebase. Excludes "see documentation" placeholders.

**thresholds.uci_success = 0.70** (lower than 0.80): Web scraping brittle to HTML changes. 70% acceptable for feasibility gate.

---

## EXISTENCE Hypothesis Constraints

This is an EXISTENCE (proof-of-concept) hypothesis. Configuration reflects:

- **Single fixed config**: No hyperparameter grid.
- **Minimal tuning**: Defaults from prior work (stephlabou repo, Yang 2024).
- **One seed**: Reproducibility without multi-run overhead.
- **Minimal epochs**: 250 pilot samples sufficient to test "does it work?"

For MECHANISM hypotheses (h-m1/h-m2/h-m3), this config will be extended with ablation studies and larger sample sizes.

---

**File Locations:**

- Config code: `/h-e1/code/config.py`
- Parsing rules: `/h-e1/code/parsing_rules.py`
- Validation script: `/h-e1/code/validate_parsing.py`
