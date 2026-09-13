# System Architecture: H-E1 Benchmark Data Validation

**Date:** 2026-07-12  
**Hypothesis:** h-e1 - Papers with Code benchmark database contains ≥100 classification benchmarks (2019-2024) with ≥5 independent reproduction attempts each  
**Type:** EXISTENCE (PoC Validation)  
**Phase:** 3 - Architecture Design

**Applied Patterns:** REST API data collection, statistical validation pipeline, modular analysis structure

---

## Codebase Analysis (Serena)

**Project Type:** Green-field  
**Status:** New implementation from scratch  
**Analyzed Path:** N/A  
**Findings:** No existing codebase. This is an original observational study validating data availability through Papers with Code API collection and statistical analysis.

---

## Architecture Overview

**Type:** Data validation pipeline (API collection → filtering → statistical analysis → visualization)  
**Infrastructure:** Minimal (single execution, no training loops)  
**Core Components:** 4 modules (data collection, validation, analysis, reporting)

---

## Module Structure

### DataCollector (`code/data/collector.py`)

**Dependencies:** requests, pandas

```python
class PapersWithCodeCollector:
    def __init__(self, base_url: str, rate_limit: float = 1.0): ...
    def fetch_benchmarks(self, task: str, start_year: int, end_year: int) -> pd.DataFrame: ...
    def fetch_results_count(self, benchmark_id: str) -> int: ...
    def collect_with_retry(self, url: str, params: dict, retries: int = 3) -> dict: ...
```

---

### BenchmarkValidator (`code/validation/validator.py`)

**Dependencies:** pandas, DataCollector

```python
class BenchmarkValidator:
    def __init__(self, min_count: int = 100, min_results: int = 5): ...
    def filter_by_criteria(self, df: pd.DataFrame) -> pd.DataFrame: ...
    def validate_hypothesis(self, df: pd.DataFrame) -> dict: ...
    def check_primary_gate(self, count: int) -> bool: ...
```

---

### StatisticalAnalyzer (`code/analysis/statistics.py`)

**Dependencies:** scipy.stats, numpy, pandas

```python
class StatisticalAnalyzer:
    def __init__(self, effect_size: float = 0.57, alpha: float = 0.05, power: float = 0.80): ...
    def calculate_required_n(self) -> int: ...
    def check_power_sufficiency(self, actual_n: int) -> dict: ...
    def analyze_domain_coverage(self, df: pd.DataFrame) -> dict: ...
    def analyze_reproduction_depth(self, df: pd.DataFrame) -> dict: ...
```

---

### ReportGenerator (`code/reporting/generator.py`)

**Dependencies:** matplotlib, seaborn, pandas

```python
class ReportGenerator:
    def __init__(self, output_dir: str): ...
    def generate_gate_metric_chart(self, threshold: int, actual: int, passes: bool) -> str: ...
    def generate_reproduction_histogram(self, df: pd.DataFrame) -> str: ...
    def generate_domain_pie_chart(self, domain_counts: dict) -> str: ...
    def generate_timeline_chart(self, df: pd.DataFrame) -> str: ...
    def generate_power_chart(self, required_n: int, actual_n: int) -> str: ...
    def generate_validation_report(self, results: dict) -> str: ...
```

---

### Main Execution (`code/main.py`)

**Dependencies:** All modules above

```python
def run_validation_pipeline(config: dict) -> dict: ...
def save_results(results: dict, output_path: str) -> None: ...
def main(): ...
```

---

### Configuration (`code/config.py`)

**Dependencies:** None

```python
class ValidationConfig:
    API_BASE_URL: str = "https://paperswithcode.com/api/v1/"
    TASK_FILTER: str = "classification"
    START_YEAR: int = 2019
    END_YEAR: int = 2024
    MIN_BENCHMARKS: int = 100
    MIN_RESULTS_PER_BENCHMARK: int = 5
    EFFECT_SIZE: float = 0.57
    ALPHA: float = 0.05
    POWER: float = 0.80
    RATE_LIMIT: float = 1.0
```

---

## File Organization

```
h-e1/
├── code/
│   ├── main.py                    # Pipeline orchestration
│   ├── config.py                  # Configuration constants
│   ├── data/
│   │   └── collector.py           # API data collection
│   ├── validation/
│   │   └── validator.py           # Filtering and hypothesis validation
│   ├── analysis/
│   │   └── statistics.py          # Power analysis and coverage
│   └── reporting/
│       └── generator.py           # Visualization and report generation
├── data/
│   ├── raw/                       # Raw JSON responses
│   └── processed/                 # Filtered CSV outputs
├── figures/                       # Generated visualizations
├── logs/                          # Error and execution logs
└── 04_validation.md               # Final validation report
```

---

## Data Flow

1. **Collection Phase**: `DataCollector` → Raw JSON → `data/raw/`
2. **Filtering Phase**: Raw JSON → `BenchmarkValidator` → Filtered DataFrame → `data/processed/benchmarks.csv`
3. **Analysis Phase**: Filtered DataFrame → `StatisticalAnalyzer` → Metrics dict
4. **Visualization Phase**: Metrics + DataFrame → `ReportGenerator` → 5 figures → `figures/`
5. **Reporting Phase**: All results → `ReportGenerator.generate_validation_report()` → `04_validation.md`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1-1 | Data Collection Module | Implement PapersWithCodeCollector with API querying, rate limiting, and retry logic | 10 | Module(3) + Deps(2) + API(3) + Integration(2) |
| E1-2 | Validation Module | Implement BenchmarkValidator with filtering and hypothesis gate checking | 8 | Module(2) + Deps(2) + Logic(2) + Integration(2) |
| E1-3 | Statistical Analysis Module | Implement StatisticalAnalyzer with power analysis and coverage metrics | 11 | Module(3) + Deps(2) + Algorithm(4) + Integration(2) |
| E1-4 | Visualization Module | Implement ReportGenerator with 5 required figures (matplotlib/seaborn) | 12 | Module(3) + Deps(3) + Viz(4) + Integration(2) |
| E1-5 | Pipeline Integration | Implement main.py orchestration and config.py with execution logging | 7 | Module(2) + Deps(1) + Orchestration(2) + Integration(2) |
| E1-6 | Report Generation | Implement markdown report generation with embedded figures and gate decision | 6 | Module(2) + Deps(1) + Template(2) + Integration(1) |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [E1-3, E1-4], Low(4-8): [E1-1, E1-2, E1-5, E1-6]  
**Total Complexity**: 54 points across 6 tasks

---

## Validation Metrics

### Primary Metric
- **Benchmark Count**: `len(filtered_df) >= 100` (MUST_WORK gate)

### Secondary Metrics
- **Statistical Power**: `actual_n >= required_n` (Cohen's d=0.57, α=0.05, β=0.20)
- **Domain Coverage**: `len(df['task'].unique()) >= 2`
- **Reproduction Depth**: `df['result_count'].median() >= 7`

---

## Success Criteria

**PASS Conditions:**
1. `benchmark_count >= 100` (primary gate)
2. `power_sufficient == True` (secondary check)
3. Pipeline executes without errors
4. All 5 figures generated
5. 04_validation.md created with clear PASS/FAIL statement

**FAIL Conditions:**
1. `benchmark_count < 100` → ABANDON study (infeasible per Phase 2B)
2. API errors preventing data collection
3. Insufficient domain coverage (single domain only)

---

## External Dependencies

### Required Libraries
- `requests==2.31.0` (HTTP client)
- `pandas==2.1.0` (data manipulation)
- `scipy==1.11.0` (statistical analysis)
- `numpy==1.25.0` (numerical computation)
- `matplotlib==3.7.0` (visualization)
- `seaborn==0.12.0` (statistical visualization)

### External APIs
- **Papers with Code REST API**
  - Base URL: `https://paperswithcode.com/api/v1/`
  - Rate Limit: 1000 requests/hour (conservative: 1 req/sec)
  - Authentication: None required
  - Endpoints: `/benchmarks/`, `/benchmarks/{id}/results/`

---

## Risk Mitigation

### API Availability
- **Risk**: Papers with Code API downtime or quota limits
- **Mitigation**: Retry logic with exponential backoff, local caching of raw JSON

### Insufficient Data
- **Risk**: <100 benchmarks meet criteria (MUST_WORK failure)
- **Mitigation**: Early gate check after collection, clear FAIL message in report

### Execution Time
- **Risk**: API rate limiting extends execution beyond 60 minutes
- **Mitigation**: Progress logging, checkpoint saving for partial results

---

## Self-Validation Checklist

- [x] No ASCII diagrams (bullet lists only)
- [x] No KB search logs (only "Applied: X" in header)
- [x] Module sections = interface code only
- [x] 6 Epic tasks with complexity scores
- [x] Total length < 500 lines
- [x] Codebase Analysis (Serena) section included
- [x] Green-field project noted (Serena skip acceptable)
- [x] EXISTENCE template applied (4-8 tasks, minimal structure)

---

**Next Phase:** Phase 5 - Logic Design (API signatures and validation algorithms)
