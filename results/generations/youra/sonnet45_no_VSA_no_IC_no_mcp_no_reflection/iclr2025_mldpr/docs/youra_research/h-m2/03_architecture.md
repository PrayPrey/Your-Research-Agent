# Architecture Document: h-m2 Temporal Lead Time Validation

**Hypothesis ID:** h-m2
**Type:** MECHANISM
**Date:** 2026-08-28
**Infrastructure Tier:** LIGHT

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Extends h-m1 saturation detection with temporal validation
**Analyzed Path:** docs/youra_research/h-m1/code/
**Findings:** Reuses h-m1 convergence results (convergence_results.json), adds citation-based adoption detection

---

## Applied Patterns

Applied: **API Integration Pattern** (rate-limited external data fetch)
Applied: **Temporal Alignment Analysis** (offset computation between event dates)

---

## System Architecture

### Module Structure

```
h-m2/
├── code/
│   ├── citation_fetcher.py         # Semantic Scholar API client
│   ├── adoption_detector.py        # Rolling avg threshold detection
│   ├── lead_time_analyzer.py       # Temporal offset computation
│   ├── statistical_validator.py    # McNemar test, permutation baseline
│   ├── visualizer.py               # Timeline + histogram plots
│   └── main_experiment.py          # Pipeline orchestration
├── data/
│   ├── citations/                  # Cached API responses
│   └── shift_adoption_dates.json   # Detected adoption dates
├── figures/                        # Generated plots
└── results/
    ├── lead_times.json             # Per-pair lead times
    └── statistical_validation.json # p-values
```

---

## Module Definitions

### CitationFetcher (`code/citation_fetcher.py`)

**Dependencies:** requests, json, pathlib

```python
class CitationFetcher:
    def __init__(self, cache_dir: Path, rate_limit: tuple = (100, 300)): ...
    def fetch_citations(self, paper_id: str) -> pd.DataFrame: ...
    def _api_call(self, url: str) -> dict: ...
    def _rate_limit_sleep(self) -> None: ...
```

### AdoptionDetector (`code/adoption_detector.py`)

**Dependencies:** pandas, numpy

```python
class AdoptionDetector:
    def __init__(self, threshold: int = 50, window: int = 3): ...
    def detect_adoption_date(self, citation_timeseries: pd.DataFrame) -> str: ...
    def smooth_citations(self, df: pd.DataFrame) -> pd.Series: ...
```

### LeadTimeAnalyzer (`code/lead_time_analyzer.py`)

**Dependencies:** pandas, json

```python
class LeadTimeAnalyzer:
    def load_saturation_dates(self, h1_results_path: Path) -> dict: ...
    def compute_lead_times(self, saturation_dates: dict, adoption_dates: dict, pairs: list) -> list: ...
    def compute_metrics(self, lead_times: list) -> dict: ...
```

### StatisticalValidator (`code/statistical_validator.py`)

**Dependencies:** scipy.stats, numpy

```python
class StatisticalValidator:
    def mcnemar_test(self, lead_times: list) -> dict: ...
    def permutation_baseline(self, saturation_dates: dict, adoption_dates: dict, n_iter: int = 1000) -> dict: ...
```

### Visualizer (`code/visualizer.py`)

**Dependencies:** matplotlib

```python
class TemporalVisualizer:
    def __init__(self, output_dir: Path): ...
    def plot_timeline(self, lead_times: list) -> None: ...
    def plot_lead_time_distribution(self, lead_times: list, threshold: int = 6) -> None: ...
    def plot_citation_curves(self, citation_data: dict) -> None: ...
```

### MainExperiment (`code/main_experiment.py`)

**Dependencies:** All above modules

```python
def run_temporal_validation(h1_results_path: Path, output_dir: Path, papers: dict) -> dict: ...
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| h-m1 Results | Direct JSON read | `h-m1/results/convergence_results.json` |

**Verified from:** docs/youra_research/h-m1/code/ (actual implementation)

**h-m1 Results Schema:**
```json
{
  "results": {
    "imagenet": {"convergence_date": "2015-08", "final_std": 0.00341},
    "glue": {"convergence_date": "2018-03", "final_std": 0.00254},
    "squad": {"convergence_date": "2018-05", "final_std": 0.00198}
  }
}
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M2-1 | Citation Data Fetching | Semantic Scholar API integration with rate limiting | 8 | 2+2+2+2 (API client + rate limiter + caching + error handling) |
| M2-2 | Adoption Date Detection | Rolling average threshold detection algorithm | 7 | 2+2+2+1 (smoothing + threshold logic + sustained window check + edge cases) |
| M2-3 | Lead Time Computation | Load h-m1 dates, compute temporal offsets | 6 | 2+1+2+1 (JSON parsing + offset calc + pairing logic + storage) |
| M2-4 | Statistical Validation | McNemar test + permutation baseline | 9 | 2+3+2+2 (McNemar impl + permutation loop + p-value computation + reporting) |
| M2-5 | Timeline Visualization | Saturation vs adoption timeline plot | 7 | 2+2+2+1 (matplotlib setup + timeline arrows + threshold shading + save) |
| M2-6 | Distribution Visualization | Lead time histogram with 6-month threshold | 6 | 2+2+1+1 (histogram binning + threshold line + labels + save) |
| M2-7 | Citation Curves Plot | Monthly citation time series for 3 papers | 5 | 1+2+1+1 (data prep + multi-line plot + legend + save) |
| M2-8 | Pipeline Orchestration | Main experiment loop, gate evaluation | 8 | 2+2+2+2 (fetch loop + detection loop + validation + gate logic) |

**Total Epic Tasks:** 8
**Complexity Distribution:** 
- Low (4-8): M2-1, M2-2, M2-3, M2-5, M2-6, M2-7, M2-8
- Medium (9-13): M2-4
- High (14-17): None
- VeryHigh (18-20): None

**Avg Complexity:** 7.0

---

## Integration Points

### Data Flow
```
h-m1/results/convergence_results.json → saturation_dates
    ↓
Semantic Scholar API → citation_fetcher.py → data/citations/*.json
    ↓
adoption_detector.py → shift_adoption_dates.json
    ↓
lead_time_analyzer.py → lead_times.json
    ↓
statistical_validator.py → statistical_validation.json
    ↓
visualizer.py → figures/
    ↓
main_experiment.py → gate evaluation
```

### Success Criteria Flow
```
lead_times.json
    ↓
Criteria: Precede fraction ≥0.6
    ↓
Criteria: Mean lead >6 months
    ↓
Criteria: p<0.05 (statistical significance)
    ↓
Gate Metrics → PASS/FAIL
```

---

## Configuration

**Hardcoded Constants (LIGHT tier):**
```python
# config.py
PAPERS = {
    'gpt3': '2020.01109',  # Semantic Scholar paper IDs
    'vit': '2010.11929',
    'llama': '2302.13971'
}

BENCHMARKS = ["imagenet", "glue", "squad"]

BENCHMARK_SHIFT_PAIRS = [
    ('imagenet', 'vit'),
    ('glue', 'gpt3'),
    ('squad', 'gpt3')
]

ADOPTION_THRESHOLD = 50  # citations/month
ADOPTION_WINDOW = 3  # months sustained
LEAD_TIME_THRESHOLD = 6  # months
SIGNIFICANCE_LEVEL = 0.05
PERMUTATION_ITERATIONS = 1000
RATE_LIMIT = (100, 300)  # requests per 5 minutes
```

---

## Environment

**Python Packages:**
```
pandas>=1.3.0
numpy>=1.21.0
scipy>=1.7.0
matplotlib>=3.4.0
requests>=2.26.0
```

**Python Version:** 3.8+

**External APIs:**
- Semantic Scholar API (free tier, 100 req/5min)
- Network access required

---

## Next Steps

**Phase 4 Implementation Order:**
1. M2-1: Citation data fetching (prerequisite for adoption detection)
2. M2-2: Adoption date detection (core mechanism)
3. M2-3: Lead time computation (depends on h-m1 results + adoption dates)
4. M2-4: Statistical validation (depends on lead times)
5. M2-7: Citation curves (validation plot)
6. M2-5, M2-6: Timeline and distribution visualizations
7. M2-8: Pipeline orchestration

**Document Status:** READY FOR PHASE 4
