# Logic Design: H-E1 Benchmark Data Collection

**Date:** 2026-07-13
**Hypothesis:** H-E1 (EXISTENCE)
**Type:** Data Collection Infrastructure
**Tier:** LIGHT (Minimal Infrastructure)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** New implementation - no existing codebase
**Analyzed Path:** N/A
**Relevant Symbols:** None - designing new data collection APIs from scratch

**Note:** This is the first hypothesis in the research pipeline. No base hypothesis or existing codebase to analyze.

---

## Applied Patterns

**Applied:** Sequential Collector Pattern with Partial Failure Handling
- Pattern: Orchestrator-based data pipeline with independent collectors
- Error Strategy: Continue-on-failure with exponential backoff retry
- Source: Standard Python data collection architecture

---

## E1-7: Orchestration Logic (Complexity: 11, Budget: 2)

**Description:** Sequential collection workflow with partial success handling.

### API Signatures

```python
from typing import Dict, List, Tuple, Any
import json
import time
from collections import Counter

class CollectionOrchestrator:
    """Orchestrates sequential data collection from multiple sources."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize orchestrator with hardcoded config.
        config: {ogb_datasets, github_repos, pwc_domains, manual_files, success_thresholds, ...}
        """
        self.config = config
        self.errors = []
        self.collectors = {}
    
    def run(self) -> Tuple[List[Dict], Dict[str, Any]]:
        """
        Execute collection pipeline. Returns: (benchmarks, metrics)
        benchmarks: List of standardized benchmark records
        metrics: {total_count, domains_above_10, completeness, success, errors}
        """
        ...
    
    def _collect_from_sources(self) -> Dict[str, List[Dict]]:
        """
        Collect from all sources with error handling.
        Returns: {source_name: [raw_records]}
        """
        ...
    
    def _safe_collect(self, collector: Any, source_name: str) -> List[Dict]:
        """
        Wrapper with retry logic. Returns: [records] or [] on failure
        """
        ...
    
    def _standardize_data(self, raw_data: Dict[str, List[Dict]]) -> List[Dict]:
        """
        Transform all sources to unified schema.
        raw_data: {source: [records]} -> [standardized_records]
        """
        ...
    
    def _validate_data(self, benchmarks: List[Dict]) -> Tuple[bool, Dict[str, Any]]:
        """
        Check success criteria. Returns: (success, metrics)
        metrics: {total_count, domains_above_10, completeness, errors}
        """
        ...
    
    def _save_results(self, benchmarks: List[Dict], metrics: Dict[str, Any]):
        """Save to JSONL and generate validation report."""
        ...


class DataValidator:
    """Validates collection against hypothesis success criteria."""
    
    def validate_collection(self, benchmarks: List[Dict]) -> Tuple[bool, Dict]:
        """Returns: (success, metrics)"""
        total = self._check_total_count(benchmarks)
        domains = self._check_domain_diversity(benchmarks)
        completeness = self._check_completeness(benchmarks)
        
        metrics = {
            'total_count': total,
            'domains_above_10': domains,
            'completeness': completeness
        }
        
        success = (total >= 50 and domains >= 3 and completeness == 100.0)
        return success, metrics
    
    def _check_total_count(self, benchmarks: List[Dict]) -> int:
        """Count total benchmarks."""
        return len(benchmarks)
    
    def _check_domain_diversity(self, benchmarks: List[Dict]) -> int:
        """Count domains with >=10 benchmarks."""
        ...
    
    def _check_completeness(self, benchmarks: List[Dict]) -> float:
        """Calculate % benchmarks with >=3 methods."""
        ...
    
    def generate_report(self, metrics: Dict) -> str:
        """Format validation report text."""
        ...


def main():
    """Entry point for data collection."""
    config = {
        'ogb_datasets': ['ogbn-arxiv', 'ogbn-products', 'ogbn-proteins', 'ogbn-papers100M',
                         'ogbg-molhiv', 'ogbg-molpcba', 'ogbg-ppa', 'ogbg-code2',
                         'ogbl-collab', 'ogbl-ddi', 'ogbl-citation2', 'ogbl-wikikg2',
                         'ogbn-mag'],
        'github_repos': ['FedML-AI/FedML', 'TalwalkarLab/leaf', 'TsingZ0/PFL-Non-IID'],
        'pwc_domains': ['vision', 'nlp', 'graph', 'time-series'],
        'manual_files': ['data/champneys.csv', 'data/zhou.csv'],
        'min_methods_per_benchmark': 3,
        'success_thresholds': {'total_count': 50, 'domains_above_10': 3, 'completeness': 100.0},
        'retry_attempts': 3,
        'timeout_seconds': 30
    }
    
    orchestrator = CollectionOrchestrator(config)
    benchmarks, metrics = orchestrator.run()
    
    print(f"\n{'='*60}")
    print(f"Collection Complete: {'PASS' if metrics['success'] else 'FAIL'}")
    print(f"Total Benchmarks: {metrics['total_count']}")
    print(f"Domains with ≥10: {metrics['domains_above_10']}")
    print(f"Completeness: {metrics['completeness']:.1f}%")
    print(f"{'='*60}\n")
```

### Data Flow

```
1. Initialize collectors (OGB, GitHub, PapersWithCode, Manual)
2. For each collector:
   a. Try: collector.collect() with timeout
   b. Retry up to 3x on failure with exponential backoff
   c. Log errors, continue to next collector
3. Aggregate raw_data: {source_name: [records]}
4. Standardize: SchemaStandardizer.standardize(raw_data[source], source)
5. Filter: Remove benchmarks with <3 methods
6. Validate: Check total≥50, domains≥3, completeness=100%
7. Save: benchmarks_collection.jsonl + validation_report.txt
```

### Pseudo-code

```
run():
    raw_data = _collect_from_sources()  # {source: [records]}
    standardized = _standardize_data(raw_data)  # [unified_records]
    success, metrics = _validate_data(standardized)
    _save_results(standardized, metrics)
    return standardized, metrics

_collect_from_sources():
    results = {}
    collectors = {
        'ogb': OGBCollector(config['ogb_datasets']),
        'github': GitHubCollector(config['github_repos']),
        'pwc': PapersWithCodeCollector(config['pwc_domains']),
        'manual': ManualCollector(config['manual_files'])
    }
    
    for source_name, collector in collectors.items():
        records = _safe_collect(collector, source_name)
        results[source_name] = records
        print(f"✓ {source_name}: {len(records)} records collected")
    
    return results

_safe_collect(collector, source_name):
    for attempt in range(config['retry_attempts']):
        try:
            with timeout(config['timeout_seconds']):
                return collector.collect()
        except Timeout:
            if attempt < config['retry_attempts'] - 1:
                sleep_time = 2 ** attempt  # 1s, 2s, 4s
                print(f"  Timeout, retrying in {sleep_time}s...")
                time.sleep(sleep_time)
            else:
                error_msg = f"{source_name} timeout after {config['retry_attempts']} attempts"
                print(f"✗ {error_msg}")
                errors.append({source_name: error_msg})
                return []
        except Exception as e:
            error_msg = f"{source_name} failed: {str(e)}"
            print(f"✗ {error_msg}")
            errors.append({source_name: error_msg})
            return []
    
    return []

_standardize_data(raw_data):
    standardizer = SchemaStandardizer()
    all_benchmarks = []
    
    for source, records in raw_data.items():
        print(f"Standardizing {len(records)} records from {source}...")
        standardized = standardizer.standardize(records, source)
        all_benchmarks.extend(standardized)
    
    # Filter: minimum 3 methods per benchmark
    filtered = [b for b in all_benchmarks if len(b.get('method_rankings', {})) >= 3]
    excluded = len(all_benchmarks) - len(filtered)
    if excluded > 0:
        print(f"Excluded {excluded} benchmarks with <3 methods")
    
    return filtered

_validate_data(benchmarks):
    validator = DataValidator()
    success, metrics = validator.validate_collection(benchmarks)
    metrics['errors'] = errors
    return success, metrics

_save_results(benchmarks, metrics):
    # Save JSONL
    output_path = 'output/benchmarks_collection.jsonl'
    with open(output_path, 'w') as f:
        for b in benchmarks:
            f.write(json.dumps(b) + '\n')
    print(f"Saved {len(benchmarks)} benchmarks to {output_path}")
    
    # Save validation report
    validator = DataValidator()
    report = validator.generate_report(metrics)
    report_path = 'output/validation_report.txt'
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"Saved validation report to {report_path}")
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Sequential Collection | Implement collector initialization and sequential execution with partial failure |
| L-7-2 | Error Handling & Validation | Retry logic with exponential backoff, validation checks |

---

## E1-3: GitHub Parsing Logic (Complexity: 10, Budget: 2)

**Description:** Parse HTML/README tables from FedML, LEAF, pFL-Bench repositories.

### API Signatures

```python
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

class GitHubCollector:
    """Collect benchmark data from GitHub repository README files."""
    
    def __init__(self, repo_urls: List[str]):
        """
        Initialize with GitHub repo URLs.
        repo_urls: ['owner/repo', 'owner/repo']
        """
        self.repo_urls = repo_urls
        self.base_url = "https://raw.githubusercontent.com"
    
    def collect(self) -> List[Dict]:
        """
        Collect from all repos. Returns: [raw_benchmark_records]
        """
        ...
    
    def _parse_readme(self, repo_url: str) -> List[Dict]:
        """
        Parse single repo README. Returns: [benchmarks]
        repo_url: 'owner/repo' -> extract tables from README.md
        """
        ...
    
    def _extract_results_table(self, html: str) -> Optional[pd.DataFrame]:
        """
        Extract first results table from HTML/markdown.
        html: Raw README content -> DataFrame or None
        """
        ...
    
    def _identify_table_format(self, df: pd.DataFrame, repo_name: str) -> str:
        """
        Detect table format (FedML vs LEAF vs pFL-Bench).
        Returns: 'fedml' | 'leaf' | 'pflbench'
        """
        ...
    
    def _parse_fedml_format(self, df: pd.DataFrame) -> List[Dict]:
        """
        Parse FedML table format. Returns: [benchmark_records]
        Columns: Dataset | Method | Accuracy | ...
        """
        ...
    
    def _parse_leaf_format(self, df: pd.DataFrame) -> List[Dict]:
        """
        Parse LEAF table format. Returns: [benchmark_records]
        Columns: Benchmark | Baseline | FedAvg | FedProx | ...
        """
        ...
    
    def _parse_pflbench_format(self, df: pd.DataFrame) -> List[Dict]:
        """
        Parse pFL-Bench table format. Returns: [benchmark_records]
        Columns: Task | Model | Acc (%) | F1 | ...
        """
        ...
```

### Data Structures

```python
# Input: GitHub repo URL
repo_url = "FedML-AI/FedML"

# Intermediate: Raw README HTML
html_content = """
<table>
<tr><th>Dataset</th><th>Method</th><th>Accuracy</th></tr>
<tr><td>FEMNIST</td><td>FedAvg</td><td>0.82</td></tr>
...
</table>
"""

# Output: Parsed benchmark record
{
    'dataset_name': 'FEMNIST',
    'domain': 'vision',
    'sample_size': 805263,
    'dimensionality': 784,
    'num_classes': 62,
    'method_rankings': {
        'FedAvg': {'family': 'Linear', 'accuracy': 0.82, 'ranking_percentile': 50.0},
        'FedProx': {'family': 'Linear', 'accuracy': 0.85, 'ranking_percentile': 75.0},
        'FedOpt': {'family': 'Linear', 'accuracy': 0.88, 'ranking_percentile': 100.0}
    },
    'source_paper': 'FedML-AI/FedML',
    'year': 2021
}
```

### Pseudo-code

```
collect():
    all_benchmarks = []
    for repo_url in repo_urls:
        try:
            benchmarks = _parse_readme(repo_url)
            all_benchmarks.extend(benchmarks)
            print(f"Collected {len(benchmarks)} from {repo_url}")
        except Exception as e:
            print(f"Failed to parse {repo_url}: {e}")
    return all_benchmarks

_parse_readme(repo_url):
    # Download README
    url = f"{base_url}/{repo_url}/main/README.md"
    response = requests.get(url, timeout=30)
    html = response.text
    
    # Extract table
    df = _extract_results_table(html)
    if df is None:
        print(f"No results table found in {repo_url}")
        return []
    
    # Identify format
    repo_name = repo_url.split('/')[1]
    format_type = _identify_table_format(df, repo_name)
    
    # Parse based on format
    if format_type == 'fedml':
        return _parse_fedml_format(df)
    elif format_type == 'leaf':
        return _parse_leaf_format(df)
    elif format_type == 'pflbench':
        return _parse_pflbench_format(df)
    else:
        print(f"Unknown table format for {repo_url}")
        return []

_extract_results_table(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Try HTML table first
    tables = soup.find_all('table')
    if tables:
        # Find first table with result keywords
        for table in tables:
            text = table.get_text().lower()
            if any(kw in text for kw in ['accuracy', 'method', 'dataset', 'benchmark']):
                return pd.read_html(str(table))[0]
    
    # Fallback: regex for markdown tables
    # Pattern: | Col1 | Col2 | ...
    #          |------|------|
    #          | val1 | val2 | ...
    pattern = r'\|([^\n]+)\|\n\|[-:\| ]+\|\n((?:\|[^\n]+\|\n?)+)'
    match = re.search(pattern, html)
    if match:
        header = [h.strip() for h in match.group(1).split('|') if h.strip()]
        rows = []
        for line in match.group(2).strip().split('\n'):
            if '|' in line:
                row = [c.strip() for c in line.split('|')[1:-1]]
                if len(row) == len(header):
                    rows.append(row)
        if rows:
            return pd.DataFrame(rows, columns=header)
    
    return None

_identify_table_format(df, repo_name):
    columns = [c.lower() for c in df.columns]
    
    # FedML: Has 'method' and 'accuracy' columns
    if 'method' in columns and 'accuracy' in columns:
        return 'fedml'
    
    # LEAF: Has method names as columns (FedAvg, FedProx, etc.)
    fed_methods = ['fedavg', 'fedprox', 'fedopt']
    if any(m in columns for m in fed_methods):
        return 'leaf'
    
    # pFL-Bench: Has 'task' or 'model' columns
    if 'task' in columns or 'model' in columns:
        return 'pflbench'
    
    # Use repo name as hint
    if 'fedml' in repo_name.lower():
        return 'fedml'
    elif 'leaf' in repo_name.lower():
        return 'leaf'
    elif 'pfl' in repo_name.lower():
        return 'pflbench'
    
    return 'unknown'

_parse_fedml_format(df):
    benchmarks = {}
    
    for _, row in df.iterrows():
        dataset = row['Dataset']
        method = row['Method']
        accuracy = float(row['Accuracy'])
        
        if dataset not in benchmarks:
            benchmarks[dataset] = {
                'dataset_name': dataset,
                'domain': _infer_domain(dataset),
                'method_rankings': {}
            }
        
        benchmarks[dataset]['method_rankings'][method] = {
            'family': _classify_method_family(method),
            'accuracy': accuracy
        }
    
    # Calculate ranking percentiles
    for b in benchmarks.values():
        methods = b['method_rankings']
        sorted_methods = sorted(methods.items(), key=lambda x: x[1]['accuracy'])
        for i, (method, data) in enumerate(sorted_methods):
            percentile = (i + 1) / len(sorted_methods) * 100
            methods[method]['ranking_percentile'] = percentile
    
    return list(benchmarks.values())

_parse_leaf_format(df):
    # LEAF format: rows are benchmarks, columns are methods
    benchmarks = []
    
    for _, row in df.iterrows():
        dataset = row['Benchmark']
        method_rankings = {}
        
        for col in df.columns:
            if col == 'Benchmark':
                continue
            method = col
            try:
                accuracy = float(row[col])
                method_rankings[method] = {
                    'family': _classify_method_family(method),
                    'accuracy': accuracy
                }
            except (ValueError, TypeError):
                continue  # Skip non-numeric values
        
        if method_rankings:  # Only add if we extracted at least one method
            benchmarks.append({
                'dataset_name': dataset,
                'domain': _infer_domain(dataset),
                'method_rankings': method_rankings
            })
    
    return benchmarks

_parse_pflbench_format(df):
    # pFL-Bench format: similar to FedML
    benchmarks = {}
    
    for _, row in df.iterrows():
        dataset = row.get('Task', row.get('Dataset'))
        method = row.get('Model', row.get('Method'))
        accuracy = float(row.get('Acc (%)', row.get('Accuracy', 0))) / 100
        
        if dataset not in benchmarks:
            benchmarks[dataset] = {
                'dataset_name': dataset,
                'domain': _infer_domain(dataset),
                'method_rankings': {}
            }
        
        benchmarks[dataset]['method_rankings'][method] = {
            'family': _classify_method_family(method),
            'accuracy': accuracy
        }
    
    return list(benchmarks.values())
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | HTML/Markdown Parsing | Implement table extraction from README files |
| L-3-2 | Format Detection & Transformation | Detect repo-specific formats and parse accordingly |

---

## Supporting APIs (Standard Implementations)

### SchemaStandardizer

```python
class SchemaStandardizer:
    """Transform raw data to unified schema."""
    
    REQUIRED_FIELDS = ['benchmark_id', 'dataset_name', 'domain', 'sample_size', 
                       'dimensionality', 'num_classes', 'method_rankings']
    
    def standardize(self, raw_data: List[Dict], source: str) -> List[Dict]:
        """Apply source-specific transformation."""
        if source == 'ogb':
            return [self._transform_ogb_format(r) for r in raw_data]
        elif source == 'github':
            return [self._transform_github_format(r) for r in raw_data]
        elif source == 'pwc':
            return [self._transform_pwc_format(r) for r in raw_data]
        elif source == 'manual':
            return [self._transform_manual_format(r) for r in raw_data]
        else:
            return []
    
    def _validate_schema(self, record: Dict) -> bool:
        """Check all required fields present."""
        return all(field in record for field in self.REQUIRED_FIELDS)
```

### OGBCollector (Standard API Access)

```python
class OGBCollector:
    """Collect from OGB library."""
    
    def __init__(self, dataset_names: List[str]):
        self.dataset_names = dataset_names
    
    def collect(self) -> List[Dict]:
        """Query OGB API for each dataset."""
        from ogb.nodeproppred import PygNodePropPredDataset
        benchmarks = []
        
        for name in self.dataset_names:
            try:
                dataset = PygNodePropPredDataset(name=name)
                metadata = self._extract_metadata(dataset)
                rankings = self._extract_rankings(name)
                
                benchmarks.append({
                    'dataset_name': name,
                    'domain': 'graph',
                    **metadata,
                    'method_rankings': rankings
                })
            except Exception as e:
                print(f"Failed to collect {name}: {e}")
        
        return benchmarks
```

---

## Error Handling Strategy

### Retry Logic

```python
def with_retry(func, max_attempts=3, timeout=30):
    """Retry wrapper with exponential backoff."""
    import time
    
    for attempt in range(max_attempts):
        try:
            return func()
        except requests.Timeout:
            if attempt == max_attempts - 1:
                raise
            sleep_time = 2 ** attempt
            print(f"Timeout, retrying in {sleep_time}s...")
            time.sleep(sleep_time)
        except Exception as e:
            print(f"Error: {e}")
            if attempt == max_attempts - 1:
                return None
            time.sleep(2 ** attempt)
    return None
```

### Partial Failure Handling

```python
# In CollectionOrchestrator._collect_from_sources():
results = {}
for source_name, collector in collectors.items():
    try:
        records = _safe_collect(collector, source_name)
        results[source_name] = records
        print(f"✓ {source_name}: {len(records)} records collected")
    except Exception as e:
        print(f"✗ {source_name} failed: {e}")
        results[source_name] = []
        errors.append({source_name: str(e)})

# Continue with partial data
return results
```

---

## Data Schema

### Standardized Benchmark Record

```python
{
    "benchmark_id": "ogb_arxiv_001",           # Unique identifier
    "dataset_name": "ogbn-arxiv",              # Dataset name
    "domain": "graph",                         # vision|time-series|tabular|graph
    "sample_size": 169343,                     # Number of samples
    "dimensionality": 128,                     # Feature dimension
    "num_classes": 40,                         # Number of classes
    "method_rankings": {
        "GCN": {
            "family": "Linear",                # Method family
            "accuracy": 0.72,                  # Performance metric
            "ranking_percentile": 33.3         # 0-100 ranking
        },
        "GAT": {
            "family": "Polynomial",
            "accuracy": 0.74,
            "ranking_percentile": 66.7
        },
        "SAGE": {
            "family": "Linear",
            "accuracy": 0.76,
            "ranking_percentile": 100.0
        }
    },
    "source_paper": "OGB: Open Graph Benchmark",
    "year": 2020
}
```

---

## Validation Criteria

### Success Conditions

```python
success = (
    metrics['total_count'] >= 50 and
    metrics['domains_above_10'] >= 3 and
    metrics['completeness'] == 100.0
)
```

### Gate Decision Logic

```python
if metrics['total_count'] >= 50:
    print("PASS - Proceed to H-M1 (meta-classifier training)")
elif 40 <= metrics['total_count'] < 50:
    print("PARTIAL - Explore additional sources")
else:
    print("FAIL - ABANDON meta-method selector hypothesis")
```

---

## Implementation Notes

### Execution Order

1. Install dependencies: `pip install -r requirements.txt`
2. Run collection: `python code/collect_benchmarks.py`
3. Check validation: `cat output/validation_report.txt`
4. Generate figures: `python code/visualize.py`

### LIGHT Tier Constraints

- **Configuration:** Hardcoded in `main()` function (no YAML)
- **Logging:** `print()` statements + `errors.log` file (no WandB)
- **Testing:** Smoke test only (verify 1-2 collectors work)
- **No GPU required:** Pure data collection, no training

### Expected Runtime

- OGB collection: 5-10 minutes
- GitHub parsing: 2-5 minutes per repo
- Total: <30 minutes for 50+ benchmarks

---

**Document Status:** Ready for Implementation (Phase 4)
**Next Phase:** Phase 4 Coder - Implement collection pipeline
**Output File:** `/workspace/TEST_scope/docs/youra_research/h-e1/03_logic.md`
