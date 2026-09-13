# System Architecture: H-E1 Benchmark Data Collection

**Date:** 2026-07-13
**Hypothesis:** H-E1 (EXISTENCE)
**Type:** Data Collection Infrastructure
**Tier:** LIGHT (Minimal Infrastructure)

Applied: Standard Python Data Collection Pattern

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** New implementation from scratch
**Analyzed Path:** N/A
**Findings:** First hypothesis - no existing codebase to analyze

---

## System Overview

EXISTENCE hypothesis validating benchmark data availability through collection from 7 benchmark suites:
- OGB (15 graph datasets)
- FedML/LEAF/pFL-Bench (19 federated learning benchmarks)
- Champneys/Zhou papers (14 specialized benchmarks)
- Papers with Code (10+ leaderboards)

Target: ≥50 benchmarks with complete method rankings across ≥3 domains.

---

## Module Structure

### 1. Data Collection Module (`code/collectors/`)

#### OGBCollector (`collectors/ogb_collector.py`)

**Dependencies:** ogb library, pandas

```python
class OGBCollector:
    def __init__(self, dataset_names: List[str]): ...
    def collect(self) -> List[Dict]: ...
    def _extract_metadata(self, dataset: Any) -> Dict: ...
    def _extract_rankings(self, dataset_name: str) -> Dict: ...
```

#### GitHubCollector (`collectors/github_collector.py`)

**Dependencies:** requests, beautifulsoup4, pandas

```python
class GitHubCollector:
    def __init__(self, repo_urls: List[str]): ...
    def collect(self) -> List[Dict]: ...
    def _parse_readme(self, repo_url: str) -> List[Dict]: ...
    def _extract_results_table(self, html: str) -> pd.DataFrame: ...
```

#### PapersWithCodeCollector (`collectors/pwc_collector.py`)

**Dependencies:** requests

```python
class PapersWithCodeCollector:
    def __init__(self, domain_filters: List[str]): ...
    def collect(self) -> List[Dict]: ...
    def _query_api(self, domain: str) -> Dict: ...
    def _parse_leaderboard(self, leaderboard_data: Dict) -> Dict: ...
```

#### ManualCollector (`collectors/manual_collector.py`)

**Dependencies:** pandas

```python
class ManualCollector:
    def __init__(self, paper_data_files: List[str]): ...
    def collect(self) -> List[Dict]: ...
    def _load_csv(self, filepath: str) -> List[Dict]: ...
```

---

### 2. Data Processing Module (`code/processing/`)

#### SchemaStandardizer (`processing/standardizer.py`)

**Dependencies:** None (stdlib only)

```python
class SchemaStandardizer:
    REQUIRED_FIELDS = ['benchmark_id', 'dataset_name', 'domain', 'sample_size', 'dimensionality', 'num_classes', 'method_rankings']
    
    def standardize(self, raw_data: List[Dict], source: str) -> List[Dict]: ...
    def _validate_schema(self, record: Dict) -> bool: ...
    def _transform_ogb_format(self, record: Dict) -> Dict: ...
    def _transform_github_format(self, record: Dict) -> Dict: ...
    def _transform_pwc_format(self, record: Dict) -> Dict: ...
```

#### DataValidator (`processing/validator.py`)

**Dependencies:** pandas

```python
class DataValidator:
    def validate_collection(self, benchmarks: List[Dict]) -> Tuple[bool, Dict]: ...
    def _check_total_count(self, benchmarks: List[Dict]) -> int: ...
    def _check_domain_diversity(self, benchmarks: List[Dict]) -> int: ...
    def _check_completeness(self, benchmarks: List[Dict]) -> float: ...
    def generate_report(self, metrics: Dict) -> str: ...
```

---

### 3. Orchestration Module (`code/`)

#### CollectionOrchestrator (`collect_benchmarks.py`)

**Dependencies:** All collectors, standardizer, validator

```python
class CollectionOrchestrator:
    def __init__(self, config: Dict): ...
    def run(self) -> Tuple[List[Dict], Dict]: ...
    def _collect_from_sources(self) -> List[Dict]: ...
    def _standardize_data(self, raw_data: List[Dict]) -> List[Dict]: ...
    def _validate_data(self, benchmarks: List[Dict]) -> Tuple[bool, Dict]: ...
    def _save_results(self, benchmarks: List[Dict], metrics: Dict): ...

def main():
    config = {
        'ogb_datasets': ['ogbn-arxiv', 'ogbn-products', 'ogbn-proteins', ...],
        'github_repos': ['FedML-AI/FedML', 'TalwalkarLab/leaf', ...],
        'pwc_domains': ['vision', 'nlp', 'graph'],
        'manual_files': ['data/champneys.csv', 'data/zhou.csv']
    }
    orchestrator = CollectionOrchestrator(config)
    benchmarks, metrics = orchestrator.run()
    print(f"Success: {metrics['success']}")
```

---

### 4. Visualization Module (`code/visualize.py`)

**Dependencies:** matplotlib, seaborn, pandas

```python
def plot_domain_distribution(benchmarks: List[Dict], output_dir: str): ...
def plot_source_breakdown(benchmarks: List[Dict], output_dir: str): ...
def plot_method_family_distribution(benchmarks: List[Dict], output_dir: str): ...
def plot_completeness_heatmap(benchmarks: List[Dict], output_dir: str): ...

def generate_all_figures(benchmarks: List[Dict], output_dir: str):
    plot_domain_distribution(benchmarks, output_dir)
    plot_source_breakdown(benchmarks, output_dir)
    plot_method_family_distribution(benchmarks, output_dir)
    plot_completeness_heatmap(benchmarks, output_dir)
```

---

## File Organization

```
h-e1/
├── code/
│   ├── collectors/
│   │   ├── __init__.py
│   │   ├── ogb_collector.py          (OGB API collection)
│   │   ├── github_collector.py       (FedML/LEAF/pFL-Bench parsing)
│   │   ├── pwc_collector.py          (Papers with Code API)
│   │   └── manual_collector.py       (Champneys/Zhou CSV loading)
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── standardizer.py           (Schema transformation)
│   │   └── validator.py              (Data validation)
│   ├── collect_benchmarks.py         (Main orchestrator)
│   ├── visualize.py                  (Figure generation)
│   └── requirements.txt              (Dependencies)
├── data/
│   ├── raw/                          (Downloaded data before standardization)
│   ├── champneys.csv                 (Manual paper extraction)
│   └── zhou.csv                      (Manual paper extraction)
├── output/
│   └── benchmarks_collection.jsonl   (Final standardized collection)
└── figures/
    ├── domain_distribution.png
    ├── source_breakdown.png
    ├── method_families.png
    └── completeness_heatmap.png
```

---

## Data Flow

1. **Collection Phase:**
   - OGBCollector → 15 graph benchmarks
   - GitHubCollector → 19 federated learning benchmarks
   - PapersWithCodeCollector → 10+ additional benchmarks
   - ManualCollector → 14 paper-extracted benchmarks

2. **Standardization Phase:**
   - SchemaStandardizer transforms all sources to unified format
   - Filter: Remove benchmarks with <3 methods

3. **Validation Phase:**
   - DataValidator checks total count (≥50)
   - Check domain diversity (≥3 domains with ≥10 each)
   - Check completeness (100% - no missing rankings)

4. **Output Phase:**
   - Save validated collection to JSONL
   - Generate validation report
   - Create 4 visualization figures

---

## Configuration (LIGHT Tier)

**Hardcoded in `collect_benchmarks.py`:**

```python
CONFIG = {
    'ogb_datasets': [
        'ogbn-arxiv', 'ogbn-products', 'ogbn-proteins', 'ogbn-papers100M',
        'ogbg-molhiv', 'ogbg-molpcba', 'ogbg-ppa', 'ogbg-code2',
        'ogbl-collab', 'ogbl-ddi', 'ogbl-citation2', 'ogbl-wikikg2',
        'ogbn-mag', 'ogbn-papers100M', 'ogbn-proteins'
    ],
    'github_repos': [
        'FedML-AI/FedML',
        'TalwalkarLab/leaf',
        'TsingZ0/PFL-Non-IID'  # pFL-Bench
    ],
    'pwc_domains': ['vision', 'nlp', 'graph', 'time-series'],
    'manual_files': [
        'data/champneys.csv',
        'data/zhou.csv'
    ],
    'min_methods_per_benchmark': 3,
    'success_thresholds': {
        'total_count': 50,
        'domains_above_10': 3,
        'completeness': 100.0
    },
    'retry_attempts': 3,
    'timeout_seconds': 30
}
```

---

## Error Handling Strategy

**LIGHT Tier Approach:** Continue on failure, log errors, generate partial results

- **API Failures:** Retry 3x, then skip source and log warning
- **Parse Errors:** Skip malformed records, log to `errors.log`
- **Validation Failures:** Report partial success with recommendations
- **Network Timeouts:** 30s timeout per API call, retry with exponential backoff

**Logging:** Print statements + `collection.log` file

```python
def safe_collect(collector, source_name):
    try:
        return collector.collect()
    except Exception as e:
        print(f"WARNING: {source_name} collection failed: {e}")
        with open('errors.log', 'a') as f:
            f.write(f"{source_name}: {e}\n")
        return []
```

---

## Testing Strategy (LIGHT Tier)

**Smoke Tests Only:**

```python
# test_smoke.py
def test_ogb_collection():
    collector = OGBCollector(['ogbn-arxiv'])
    results = collector.collect()
    assert len(results) == 1
    assert results[0]['dataset_name'] == 'ogbn-arxiv'

def test_standardization():
    raw = [{'dataset': 'test', 'metrics': {'acc': 0.9}}]
    standardizer = SchemaStandardizer()
    results = standardizer.standardize(raw, 'test')
    assert 'benchmark_id' in results[0]

def test_validation():
    benchmarks = [{'domain': 'graph', 'method_rankings': {'m1': {}, 'm2': {}, 'm3': {}}}] * 50
    validator = DataValidator()
    success, metrics = validator.validate_collection(benchmarks)
    assert success == False  # Only 1 domain, need 3 with ≥10
```

Run: `python test_smoke.py` (no pytest framework needed)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1-1 | Setup Project Structure | Create folders, requirements.txt, README | 5 | Size(1) + Deps(1) + Algo(1) + Integ(2) |
| E1-2 | Implement OGB Collection | OGBCollector with API access and ranking extraction | 8 | Size(2) + Deps(2) + Algo(2) + Integ(2) |
| E1-3 | Implement GitHub Collection | GitHubCollector for FedML/LEAF/pFL-Bench parsing | 10 | Size(3) + Deps(2) + Algo(3) + Integ(2) |
| E1-4 | Implement Papers with Code Collection | PapersWithCodeCollector with API integration | 7 | Size(2) + Deps(1) + Algo(2) + Integ(2) |
| E1-5 | Manual Data Extraction | Extract Champneys/Zhou results to CSV, implement ManualCollector | 9 | Size(2) + Deps(1) + Algo(4) + Integ(2) |
| E1-6 | Data Standardization | SchemaStandardizer with source-specific transformations | 8 | Size(2) + Deps(2) + Algo(2) + Integ(2) |
| E1-7 | Validation and Orchestration | DataValidator, CollectionOrchestrator, main workflow | 11 | Size(3) + Deps(3) + Algo(2) + Integ(3) |
| E1-8 | Visualization Generation | 4 required plots with matplotlib/seaborn | 6 | Size(2) + Deps(1) + Algo(1) + Integ(2) |

**Total Complexity:** 64
**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [E1-3, E1-5, E1-7], Low(4-8): [E1-1, E1-2, E1-4, E1-6, E1-8]

---

## Dependencies

**External Libraries:**
```
ogb>=1.3.0
requests>=2.28.0
pandas>=1.5.0
beautifulsoup4>=4.11.0
matplotlib>=3.6.0
seaborn>=0.12.0
```

**Data Sources:**
- OGB API (online)
- GitHub repositories (online, cacheable)
- Papers with Code API (online)
- Manual CSV files (local)

**No Internal Dependencies:** Standalone data collection module

---

## Success Criteria

**Quantitative Metrics:**
1. Total benchmarks collected ≥ 50
2. Domains with ≥10 benchmarks ≥ 3
3. Data completeness = 100%

**Validation Logic:**
```python
success = (
    metrics['total_count'] >= 50 and
    metrics['domains_above_10'] >= 3 and
    metrics['completeness'] == 100.0
)
```

**Output:**
- `benchmarks_collection.jsonl` - Validated collection
- `validation_report.txt` - Pass/Fail decision
- 4 figure files in `figures/`

**Gate Decision:**
- PASS (≥50): Proceed to H-M1 (meta-classifier training)
- PARTIAL (40-49): Explore additional sources
- FAIL (<40): ABANDON meta-method selector hypothesis chain

---

## Implementation Notes

**Recommended Development Order:**
1. E1-1: Setup (folders, requirements.txt)
2. E1-2: OGB collection (most reliable API)
3. E1-6: Standardization (needed for incremental testing)
4. E1-3: GitHub collection (second largest source)
5. E1-7: Validation (check if target met before manual work)
6. E1-4: Papers with Code (if needed to reach 50)
7. E1-5: Manual extraction (only if still short of 50)
8. E1-8: Visualization (after validation passes)

**Key Design Constraints:**
- LIGHT tier: No YAML configs, no WandB, no pytest
- Runtime: <2 hours total collection time
- Parallelization: Optional (sequential is acceptable)
- Error tolerance: Continue on source failure, log errors

**Phase 4 Execution:**
```bash
cd h-e1/code
pip install -r requirements.txt
python collect_benchmarks.py
python visualize.py
```

---

**Document Status:** Ready for Implementation (Phase 4)
**Next Step:** Phase 4 Coder Agent - Implement data collection pipeline
