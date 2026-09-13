# Configuration Schema: h-m2

**Date:** 2026-08-19  
**Hypothesis ID:** h-m2  
**Type:** MECHANISM  

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase (h-e1 base)  
**Status:** Config pattern verified from h-e1/code/config.py  
**Config Files Found:** h-e1/code/config.py  
**Pattern Used:** Hardcoded dict (reused for consistency)

---

## Configuration (Python Dict)

```python
"""Configuration for h-m2: Lower friction increases voluntary completion"""

CONFIG = {
    # Data Collection (Stratified sampling per platform)
    "data": {
        "hf_sample_size": 7000,
        "openml_sample_size": 2500,
        "uci_sample_size": 500,
        "temporal_cutoff": "2026-08-19",  # Datasets published before this date
        "validation_parsing_sample": 100,  # Stratified: 50 HF, 30 OpenML, 20 UCI
        "validation_semantic_sample": 150,  # 50 per platform (with field present)
    },

    # Platform URLs
    "api": {
        "retry_max": 3,
        "retry_backoff": [1, 2, 4],
        "timeout": 30,
        "hf_endpoint": "https://huggingface.co/api/datasets",
        "openml_endpoint": "https://www.openml.org/api/v1",
        "uci_base_url": "https://archive.ics.uci.edu/datasets",
        # Rate limits (requests per minute)
        "hf_rate_limit": 100,  # 1000 with token, but conservative default
        "openml_rate_limit": 60,
        "uci_rate_limit": 60,  # 1 req/sec, conservative
    },

    # Field Parsing Rules (Binary presence detection)
    "parsing": {
        "preprocessing_code": {
            "min_chars": 50,
            "keywords": ["import", "def", "function", "library", "package"],
            "file_extensions": [".py", ".R", ".ipynb", ".sh"],
        },
        "data_source_url": {
            "url_pattern": r"https?://[^\s]+",
            "reject_patterns": ["localhost", "example.com", "TODO", "N/A"],
        },
        "collection_date": {
            "date_patterns": [
                r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
                r"[A-Z][a-z]+ \d{4}",  # Month YYYY
                r"\d{4}",              # YYYY
            ],
            "reject_patterns": ["TBD", "Unknown", "N/A"],
        },
    },

    # Cross-Platform Field Mapping (Semantic normalization)
    "field_mapping": {
        "preprocessing_code": {
            "hf": ["README.md code blocks", "dataset card YAML"],
            "openml": ["processing_script"],
            "uci": ["methodology section"],
        },
        "data_source_url": {
            "hf": ["source", "homepage"],
            "openml": ["url"],
            "uci": ["source URL in HTML"],
        },
        "collection_date": {
            "hf": ["date_created", "prose timestamp"],
            "openml": ["upload_date", "version_date"],
            "uci": ["publication date"],
        },
    },

    # Statistical Tests
    "stats": {
        "alpha": 0.05,
        "effect_size_threshold": 30,  # Percentage points (HF - UCI)
        "test_type": "chi2_contingency",  # scipy.stats.chi2_contingency
        "min_expected_frequency": 5,  # For chi-squared validity
    },

    # File Paths
    "paths": {
        "data_dir": "data/h-m2",
        "figures_dir": "docs/youra_research/h-m2/figures",
        "results_dir": "results/h-m2",
        "hf_metadata": "data/h-m2/hf_metadata.json",
        "openml_metadata": "data/h-m2/openml_metadata.json",
        "uci_metadata": "data/h-m2/uci_metadata.json",
        "presence_rates": "data/h-m2/presence_rates.csv",
        "statistical_results": "data/h-m2/statistical_results.json",
        "validation_report": "data/h-m2/validation_report.json",
    },

    # Reproducibility
    "experiment": {
        "seed": 42,
        "deterministic": True,
        "cache_enabled": True,
        "verbose": True,
        "checkpoint_enabled": True,  # Resume on failure
    },

    # Validation Thresholds
    "validation": {
        "parsing_accuracy_threshold": 0.85,  # >85% agreement with manual review
        "semantic_equivalence_threshold": 0.80,  # >80% cross-platform semantic match
    },
}
```

---

## Default Values Rationale

**Sample Sizes:**
- HF: 7,000 (70% of total) — largest platform, proportional sampling
- OpenML: 2,500 (25% of total) — intermediate platform
- UCI: 500 (5% of total) — near-census (UCI has ~600 datasets total)

**Field Parsing Thresholds:**
- `min_chars: 50` — reused from h-e1, eliminates empty placeholders
- Keywords: Standard programming language markers (cross-language)
- URL pattern: Standard HTTP/HTTPS validation
- Date patterns: Common ISO + prose formats

**Statistical Parameters:**
- `alpha: 0.05` — standard significance level
- `effect_size_threshold: 30` — substantial difference (30 percentage points)
- Chi-squared test: Appropriate for categorical frequency data (present/absent)

**Rate Limits:**
- HF: 100 req/min (conservative, 1000 available with token)
- OpenML: 60 req/min (observed throttling)
- UCI: 60 req/min (1 req/sec to respect robots.txt)

**Validation:**
- Parsing accuracy: >85% (reused from h-e1/h-m1 validation protocol)
- Semantic equivalence: >80% (new threshold for cross-platform field mapping)

---

## Environment-Specific Overrides

**Development (Fast Iteration):**
```python
DEV_CONFIG = CONFIG.copy()
DEV_CONFIG["data"].update({
    "hf_sample_size": 100,
    "openml_sample_size": 50,
    "uci_sample_size": 50,
})
DEV_CONFIG["experiment"]["cache_enabled"] = False
```

**Production (Full Run):**
```python
PROD_CONFIG = CONFIG.copy()
PROD_CONFIG["api"]["hf_rate_limit"] = 1000  # With HF token
```

---

## Validation Rules

**Pre-Execution Checks:**
1. Total sample size: `hf_sample_size + openml_sample_size + uci_sample_size >= 10000`
2. UCI sample size: `uci_sample_size <= 600` (near-census limit)
3. Validation samples: `validation_parsing_sample >= 100` AND `validation_semantic_sample >= 150`
4. Rate limits: All > 0
5. Effect size threshold: `>= 20` (minimum detectable difference)

**Post-Execution Checks:**
1. Parsing accuracy: `>= validation.parsing_accuracy_threshold`
2. Semantic equivalence: `>= validation.semantic_equivalence_threshold`
3. Chi-squared validity: All expected frequencies >= 5
4. Missing data: `< 5%` per platform

---

## Configuration Files

**Single source of truth:** `h-m2/code/config.py`

**Usage:**
```python
from config import CONFIG

# Access platform URLs
hf_url = CONFIG["api"]["hf_endpoint"]

# Access parsing thresholds
min_chars = CONFIG["parsing"]["preprocessing_code"]["min_chars"]

# Access sample sizes
hf_sample = CONFIG["data"]["hf_sample_size"]
```

**No external config files (YAML/JSON) — hardcoded dict for simplicity and type safety.**

---

**Configuration Complete** | **Path:** `/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_mldpr/docs/youra_research/h-m2/03_config.md`
