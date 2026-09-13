# Configuration: H-E1 Retrospective Corpus Collection

**Hypothesis**: h-e1 (EXISTENCE)  
**Created**: 2026-08-25  
**Config Version**: 1.0

Applied: ETL Pipeline Pattern, EXISTENCE minimal config

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New data pipeline, no existing codebase  
**Config Pattern**: Hardcoded dict (matches project pattern from h-m1)

---

## Configuration (Hardcoded Dict)

```python
# config.py - Pipeline configuration for retrospective corpus collection

CONFIG = {
    # Collection sources
    "collection": {
        "pwc_api_url": "https://paperswithcode.com/api/v1/papers",
        "pwc_tag": "ablation",
        "pwc_max_results": 50,
        
        "conferences": [
            {"venue": "NeurIPS", "years": [2020, 2021, 2022, 2023, 2024]},
            {"venue": "ICML", "years": [2020, 2021, 2022, 2023, 2024]},
            {"venue": "ICLR", "years": [2020, 2021, 2022, 2023, 2024]},
        ],
        
        "keywords": ["ablation study", "overhead", "sample size"],
        "max_retries": 3,
        "timeout_seconds": 30,
    },
    
    # Extraction patterns
    "extraction": {
        "timing_patterns": [
            r"Table\s+\d+:.*overhead.*sample.*\n(.*?\n){1,10}",
            r"(\d+)\s*samples?:\s*(\d+\.?\d*)\s*sec.*?(\d+)\s*samples?:\s*(\d+\.?\d*)\s*sec",
            r"micro-pilot.*?(\d+\.?\d*)\s*sec.*?full.*?(\d+\.?\d*)\s*sec",
            r"ablation.*?\n.*?(\d+)\s+(\d+\.?\d*).*?\n.*?(\d+)\s+(\d+\.?\d*)",
        ],
        "micro_pilot_threshold": 50,
        "full_scale_threshold": 1000,
        "sample_size_ratio_min": 10,
    },
    
    # Validation thresholds
    "validation": {
        "target_count": 30,
        "pass_threshold": 30,
        "fail_threshold": 20,
        "stratification": {
            "low_overhead_max": 20.0,
            "high_overhead_min": 80.0,
            "cv_threshold": 0.5,
        },
        "spot_check_rate": 0.2,
    },
    
    # Output paths
    "paths": {
        "corpus_output": "data/retrospective_corpus/papers_metadata.json",
        "raw_papers_dir": "data/retrospective_corpus/raw_papers",
        "checkpoints_dir": "data/retrospective_corpus/checkpoints",
        "validation_report": "data/retrospective_corpus/validation_report.md",
    },
    
    # Reproducibility
    "seed": 42,
}
```

---

## Task Breakdown (3 Subtasks Allocated)

### C-1: Collection Configuration

**Budget**: 1 subtask  
**Complexity**: Low (standard HTTP params)

| Field | Value | Notes |
|-------|-------|-------|
| `pwc_max_results` | 50 | PWC API limit |
| `conferences` | NeurIPS/ICML/ICLR 2020-2024 | 5 years × 3 venues |
| `keywords` | ablation/overhead/sample size | Filter for timing data |
| `max_retries` | 3 | Standard retry pattern |

### C-2: Extraction Configuration

**Budget**: 1 subtask  
**Complexity**: Low (regex patterns from architecture)

| Field | Value | Notes |
|-------|-------|-------|
| `timing_patterns` | 4 regex patterns | From architecture spec |
| `micro_pilot_threshold` | 50 | PRD requirement: ≤50 samples |
| `full_scale_threshold` | 1000 | PRD requirement: ≥1000 samples |
| `sample_size_ratio_min` | 10 | PRD validation: 10x difference |

### C-3: Validation Configuration

**Budget**: 1 subtask  
**Complexity**: Low (PRD thresholds)

| Field | Value | Notes |
|-------|-------|-------|
| `target_count` | 30 | PRD success criteria |
| `pass_threshold` | 30 | Gate decision: PASS |
| `fail_threshold` | 20 | Gate decision: FAIL |
| `cv_threshold` | 0.5 | Stratification balance |
| `spot_check_rate` | 0.2 | 20% manual verification |

---

## Rationale (Non-Standard Values Only)

**`sample_size_ratio_min: 10`**: Ensures micro-pilot (≤50) and full-scale (≥1000) differ meaningfully. Standard for scale validation.

**`cv_threshold: 0.5`**: PRD requirement for balanced stratification across low/mid/high overhead bins.

---

## Usage

```python
from config import CONFIG

# Collection module
def collect_all_sources():
    api_url = CONFIG["collection"]["pwc_api_url"]
    max_results = CONFIG["collection"]["pwc_max_results"]
    ...

# Extraction module
def extract_timing_table(text):
    patterns = CONFIG["extraction"]["timing_patterns"]
    for pattern in patterns:
        match = re.search(pattern, text)
        ...

# Validation module
def decide_gate(valid_count, cv):
    if valid_count >= CONFIG["validation"]["pass_threshold"]:
        return "PASS"
    elif valid_count >= CONFIG["validation"]["fail_threshold"]:
        return "PARTIAL"
    else:
        return "FAIL"
```

---

**Document Version**: 1.0  
**Created**: 2026-08-25  
**Hypothesis**: H-E1 (EXISTENCE)
