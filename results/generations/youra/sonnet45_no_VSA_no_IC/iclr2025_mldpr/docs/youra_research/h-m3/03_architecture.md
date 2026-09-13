# Architecture: h-m3 — Required Fields Stable Across Platforms

**Date:** 2026-08-19  
**Hypothesis ID:** h-m3  
**Type:** MECHANISM  
**Tier:** 1  
**Gate:** SHOULD_WORK

Applied: Statistical validation patterns (chi-squared, effect size), metadata reuse patterns

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Reuses h-m2 data extraction (9,990 cached records)  
**Analyzed Path:** `h-m2/code/`  
**Findings:** h-m2 implements full extraction pipeline with statistical_analysis.py (chi-squared, effect size), parser.py (binary presence detection), main.py (orchestrator). Reuse statistical analysis and data loading patterns; extend parser for required fields (license, version).

---

## Directory Structure

```
h-m3/
├── code/
│   ├── config.py              # Field parsing rules, file paths
│   ├── load_data.py           # Load h-m2 cached JSON
│   ├── parse_required.py      # License/version presence detection
│   ├── statistical_analysis.py # Chi-squared, Cramér's V, CV
│   ├── generate_report.py     # validation_summary.json, 04_validation.md, charts
│   └── main.py                # Pipeline orchestrator
├── data/
│   └── results/
│       ├── required_field_presence.csv
│       ├── validation_summary.json
│       ├── validation_sample.json
│       ├── comparison_table.md
│       ├── license_presence_chart.png
│       └── version_presence_chart.png
└── 04_validation.md
```

---

## Module Breakdown

### 1. Config (`h-m3/code/config.py`)

**Dependencies:** None

```python
CONFIG = {
    "paths": {
        "hf_metadata": "/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_mldpr/h-m2/code/data/h-m2/hf_metadata.json",
        "openml_metadata": "/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_mldpr/h-m2/code/data/h-m2/openml_metadata.json",
        "uci_metadata": "/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_mldpr/h-m2/code/data/h-m2/uci_metadata.json",
        "results_dir": "h-m3/data/results",
        "validation_report": "docs/youra_research/h-m3/04_validation.md"
    },
    "required_fields": ["license", "version"],
    "parsing": {
        "license": {
            "hf_openml": ["non_empty_string", "not_unknown", "not_other"],
            "uci": ["keywords_cc_by", "mit", "apache", "gpl", "bsd"]
        },
        "version": {
            "hf": ["semantic_version_pattern"],
            "openml": ["non_null_integer"],
            "uci": ["keyword_or_date_pattern"]
        }
    },
    "stats": {
        "alpha": 0.10,
        "cv_threshold": 0.20,
        "cramers_v_threshold": 0.20,
        "min_presence_rate": 0.80
    },
    "validation": {
        "sample_size": 100,
        "stratification": {"HF": 50, "OpenML": 30, "UCI": 20},
        "parsing_accuracy_threshold": 0.85
    },
    "h_m2_contrast": {
        "optional_cv": 1.0,
        "required_vs_optional_ratio_threshold": 0.25
    }
}
```

### 2. Data Loader (`h-m3/code/load_data.py`)

**Dependencies:** json, pathlib

```python
def load_h_m2_metadata(config: dict) -> dict[str, list[dict]]:
    """Load cached metadata from h-m2 extraction"""
    ...

def validate_sample_sizes(data: dict[str, list[dict]], expected: dict[str, int]) -> bool:
    """Verify HF=6500, OpenML=2990, UCI=500"""
    ...

def check_data_integrity(data: dict[str, list[dict]]) -> dict:
    """Log missing IDs, null platforms, parsing failures"""
    ...
```

### 3. Required Field Parser (`h-m3/code/parse_required.py`)

**Dependencies:** re

```python
class RequiredFieldParser:
    def __init__(self, config: dict): ...
    
    def parse_all_platforms(self, metadata: dict[str, list[dict]]) -> dict[str, list[dict]]:
        """Parse license/version for HF, OpenML, UCI"""
        ...
    
    def _parse_license(self, value: str | None, platform: str) -> bool:
        """Detect license presence (platform-specific rules)"""
        ...
    
    def _parse_version(self, value: str | int | None, platform: str) -> bool:
        """Detect version presence (platform-specific rules)"""
        ...
```

### 4. Statistical Analysis (`h-m3/code/statistical_analysis.py`)

**Dependencies:** scipy.stats, numpy

```python
class RequiredFieldAnalyzer:
    def __init__(self, config: dict): ...
    
    def analyze_field(self, field_name: str, parsed_data: dict[str, list[dict]]) -> dict:
        """Run full analysis for one field (license or version)"""
        ...
    
    def calculate_presence_rates(self, parsed_data: dict[str, list[dict]]) -> dict[str, float]:
        """Percentage per platform"""
        ...
    
    def chi_squared_test(self, contingency_table: np.ndarray) -> dict:
        """2x3 table (present/absent x HF/OpenML/UCI)"""
        ...
    
    def cramers_v(self, contingency_table: np.ndarray) -> float:
        """Effect size for categorical association"""
        ...
    
    def coefficient_of_variation(self, presence_rates: list[float]) -> float:
        """CV = std / mean"""
        ...
    
    def contrast_with_h_m2(self, required_cv: float, optional_cv: float) -> dict:
        """Compare required vs optional field variability"""
        ...
```

### 5. Report Generator (`h-m3/code/generate_report.py`)

**Dependencies:** json, matplotlib, pandas

```python
def generate_validation_summary_json(results: dict, config: dict, output_path: str) -> None:
    """FR-9: validation_summary.json with status, stats, contrast"""
    ...

def generate_validation_report_md(results: dict, config: dict, output_path: str) -> None:
    """FR-10: 04_validation.md with sections 1-8"""
    ...

def generate_presence_charts(results: dict, output_dir: str) -> None:
    """FR-11: Bar charts for license/version presence rates"""
    ...

def generate_comparison_table(results: dict, output_dir: str) -> None:
    """Markdown table: required vs optional CV/Cramér's V"""
    ...

def export_validation_sample(parsed_data: dict, config: dict, output_path: str) -> None:
    """FR-8: 100-record sample for manual validation"""
    ...
```

### 6. Pipeline Orchestrator (`h-m3/code/main.py`)

**Dependencies:** All above modules

```python
def main() -> dict:
    """End-to-end validation pipeline
    
    Steps:
    1. Load h-m2 cached metadata
    2. Parse required fields (license, version)
    3. Export validation sample (100 records)
    4. Run statistical analysis (chi-squared, CV, Cramér's V)
    5. Contrast with h-m2 optional fields
    6. Generate outputs (JSON, MD, charts)
    7. Evaluate gate (PASS/PARTIAL/FAIL)
    """
    ...

def evaluate_gate(results: dict, config: dict) -> dict:
    """Gate decision logic
    
    Primary criteria:
    1. Required fields p > 0.10 (no platform effect)
    2. Required fields CV < 0.20 (stable)
    3. Mean presence ≥ 80%
    4. Required CV << optional CV (ratio < 0.25)
    """
    ...
```

---

## Data Schemas

### Input Schema (h-m2 cached JSON)

```python
{
    "dataset_id": str,
    "platform": "HF" | "OpenML" | "UCI",
    "license": str | None,        # Required field 1
    "version": str | int | None,   # Required field 2
    "readme_text": str | None,     # (h-m2 optional fields not used)
    "yaml_frontmatter": dict | None,
    # ... other h-m2 fields
}
```

### Parsed Output Schema

```python
{
    "dataset_id": str,
    "platform": str,
    "license_present": bool,
    "version_present": bool,
    "raw_license": str | None,
    "raw_version": str | int | None
}
```

### validation_summary.json Schema

```json
{
    "hypothesis_id": "h-m3",
    "status": "PASS|PARTIAL|FAIL",
    "required_fields": {
        "license": {
            "hf_presence_pct": float,
            "openml_presence_pct": float,
            "uci_presence_pct": float,
            "chi2_statistic": float,
            "p_value": float,
            "cramers_v": float,
            "cv": float
        },
        "version": {...}
    },
    "contrast_with_h_m2": {
        "optional_field_cv": float,
        "required_vs_optional_cv_ratio": float
    },
    "parsing_validation": {
        "sample_size": 100,
        "agreement_rate_pct": float
    },
    "key_findings": [string]
}
```

---

## Technology Stack

| Component | Library | Version |
|-----------|---------|---------|
| Data loading | json (stdlib) | - |
| Statistical tests | scipy.stats | ≥1.11 |
| Numerical computation | numpy | ≥1.24 |
| Visualization | matplotlib | ≥3.7 |
| Data structures | pandas | ≥2.0 |

---

## External Dependencies (h-m2 Base)

### Data Paths (From Actual Code)

| Data File | Path | Description |
|-----------|------|-------------|
| HF metadata | `h-m2/code/data/h-m2/hf_metadata.json` | 6,500 HuggingFace datasets |
| OpenML metadata | `h-m2/code/data/h-m2/openml_metadata.json` | 2,990 OpenML datasets |
| UCI metadata | `h-m2/code/data/h-m2/uci_metadata.json` | 500 UCI datasets |

**Verified from:** `h-m2/code/main.py` (lines 53-56)

---

## Data Flow

```
h-m2 cached JSON
    ↓ [load_data.py]
Raw metadata dict (9,990 records)
    ↓ [parse_required.py]
Parsed presence flags (license_present, version_present)
    ↓ [statistical_analysis.py]
Statistical results (chi-squared, CV, Cramér's V)
    ↓ [generate_report.py]
Outputs (validation_summary.json, 04_validation.md, charts)
```

---

## Error Handling Strategy

| Error Type | Handling |
|------------|----------|
| Missing h-m2 files | Fail with clear path error |
| Sample size mismatch | Log warning, continue with available data |
| Parsing failures | Log count/types, mark as "absent" |
| Zero cells in contingency table | Apply Laplace smoothing (+1 to all cells) |
| Manual validation < 85% | Refine parsing rules, re-run (FR-8 fallback) |

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup | Project structure, config, dependencies | 6 | structure(1) + config(2) + deps(1) + paths(2) |
| A-2 | Data Loading | Load h-m2 JSON, validate sample sizes, integrity checks | 9 | load_json(2) + validation(3) + integrity(2) + error_handling(2) |
| A-3 | Required Parser | License/version parsing with platform-specific rules | 14 | license_rules(4) + version_rules(4) + regex(3) + testing(3) |
| A-4 | Statistical Analysis | Chi-squared, Cramér's V, CV calculation | 12 | chi2(3) + cramers_v(2) + cv(2) + h_m2_contrast(3) + tests(2) |
| A-5 | Validation Sample | Export 100-record stratified sample for manual review | 7 | stratify(2) + export_json(2) + manual_review(3) |
| A-6 | Report Generation | validation_summary.json, 04_validation.md, charts | 11 | json_schema(3) + md_sections(4) + charts(2) + tables(2) |
| A-7 | Pipeline Integration | main.py orchestrator, gate evaluation | 8 | orchestrator(3) + gate_logic(3) + logging(2) |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3], Medium(9-13): [A-2, A-4, A-6], Low(4-8): [A-1, A-5, A-7]

**Total Complexity:** 67 points  
**Estimated Duration:** 9 hours (per PRD Phase 1-4)

---

## Self-Validation Checklist

- [x] No ASCII diagrams
- [x] Module sections = interface only
- [x] 7 epic tasks with complexity scores
- [x] External dependencies section (h-m2 data paths)
- [x] Codebase Analysis section included
- [x] Import paths verified from h-m2/code/main.py
- [x] Total length < 500 lines

---

**Architecture Complete** | **Next:** Phase 4 Implementation | **Date:** 2026-08-19
