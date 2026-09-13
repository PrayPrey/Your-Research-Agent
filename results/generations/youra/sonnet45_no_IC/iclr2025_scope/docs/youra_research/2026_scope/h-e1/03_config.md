# Configuration Document: H-E1 Benchmark Data Collection

**Date:** 2026-07-13
**Hypothesis:** H-E1 (EXISTENCE)
**Type:** Data Collection Infrastructure
**Tier:** LIGHT (Minimal Infrastructure)

Applied: Standard Python Data Collection Pattern

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** New data collection implementation - no existing codebase
**Config Files Found:** None - archived projects are unrelated (different hypothesis contexts)
**Pattern Used:** Hardcoded dict (LIGHT tier requirement)

---

## E1-5: Manual Data Extraction [Complexity: 9, Budget: 2]

Applied: Hardcoded dict pattern for data source configuration

### Configuration (Python Dict)

```python
# Manual extraction configuration for Champneys and Zhou papers
MANUAL_EXTRACTION_CONFIG = {
    # Paper data files (manual CSV extraction)
    'paper_files': [
        'data/champneys.csv',
        'data/zhou.csv'
    ],
    
    # Required schema fields for validation
    'required_fields': [
        'benchmark_id',
        'dataset_name',
        'domain',
        'sample_size',
        'dimensionality',
        'num_classes',
        'method_rankings'
    ],
    
    # Data type constraints
    'field_types': {
        'sample_size': int,
        'dimensionality': int,
        'num_classes': int,
        'method_rankings': dict
    },
    
    # Collection thresholds
    'min_methods_per_benchmark': 3,
    'expected_champneys_count': 5,
    'expected_zhou_count': 9,
    
    # Method family mapping
    'method_families': ['Linear', 'Polynomial', 'RNN', 'Augmentation'],
    
    # Domain classifications
    'valid_domains': ['vision', 'time-series', 'tabular', 'graph']
}
```

### Data Source Parameters

```python
# Data source endpoints and repository URLs
DATA_SOURCES = {
    'ogb_datasets': [
        'ogbn-arxiv', 'ogbn-products', 'ogbn-proteins', 'ogbn-papers100M',
        'ogbg-molhiv', 'ogbg-molpcba', 'ogbg-ppa', 'ogbg-code2',
        'ogbl-collab', 'ogbl-ddi', 'ogbl-citation2', 'ogbl-wikikg2',
        'ogbn-mag'
    ],
    
    'github_repos': [
        'https://github.com/FedML-AI/FedML',
        'https://github.com/TalwalkarLab/leaf',
        'https://github.com/TsingZ0/PFL-Non-IID'  # pFL-Bench
    ],
    
    'pwc_api_endpoint': 'https://paperswithcode.com/api/v1/',
    'pwc_domains': ['vision', 'nlp', 'graph', 'time-series'],
    
    'manual_papers': [
        {'name': 'Champneys NLSI', 'file': 'data/champneys.csv', 'domain': 'time-series'},
        {'name': 'Zhou Medical FL', 'file': 'data/zhou.csv', 'domain': 'tabular'}
    ]
}
```

### Schema Validation Rules

```python
# Schema validation configuration
VALIDATION_CONFIG = {
    # Required field presence checks
    'required_fields': [
        'benchmark_id',
        'dataset_name',
        'domain',
        'sample_size',
        'dimensionality',
        'num_classes',
        'method_rankings',
        'source_paper',
        'year'
    ],
    
    # Type constraints
    'type_constraints': {
        'benchmark_id': str,
        'dataset_name': str,
        'domain': str,
        'sample_size': int,
        'dimensionality': int,
        'num_classes': int,
        'method_rankings': dict,
        'source_paper': str,
        'year': int
    },
    
    # Range constraints
    'range_constraints': {
        'sample_size': (10, 10_000_000),
        'dimensionality': (1, 100_000),
        'num_classes': (2, 10_000),
        'year': (2015, 2026)
    },
    
    # Domain whitelist
    'valid_domains': ['vision', 'time-series', 'tabular', 'graph'],
    
    # Method family whitelist
    'valid_families': ['Linear', 'Polynomial', 'RNN', 'Augmentation'],
    
    # Completeness thresholds
    'min_methods_per_benchmark': 3,
    'required_method_fields': ['family', 'accuracy', 'ranking_percentile']
}
```

### Collection Thresholds

```python
# Success criteria thresholds
SUCCESS_THRESHOLDS = {
    'total_benchmarks': 50,
    'domains_above_10': 3,
    'completeness': 100.0,  # percentage
    
    # Per-source expected counts
    'expected_counts': {
        'ogb': 15,
        'fedml': 6,
        'leaf': 5,
        'pfl_bench': 8,
        'champneys': 5,
        'zhou': 9,
        'pwc': 10
    },
    
    # Quality thresholds
    'min_accuracy_range': 0.05,  # Methods must differ by >=5%
    'max_missing_metadata': 0.0  # No missing metadata allowed
}
```

### Error Handling Constants

```python
# Collection error handling configuration
ERROR_HANDLING = {
    'retry_attempts': 3,
    'timeout_seconds': 30,
    'exponential_backoff_base': 2,
    
    # Continue on failure flags
    'continue_on_api_failure': True,
    'continue_on_parse_error': True,
    'continue_on_validation_failure': False,
    
    # Logging configuration (LIGHT tier: print + file)
    'log_file': 'collection.log',
    'error_log_file': 'errors.log',
    'log_level': 'INFO'
}
```

### Hardcoded Output Paths

```python
# Output file paths (LIGHT tier: hardcoded)
OUTPUT_PATHS = {
    'benchmarks_collection': 'output/benchmarks_collection.jsonl',
    'validation_report': 'output/validation_report.txt',
    'raw_data_dir': 'data/raw/',
    'figures_dir': 'figures/',
    
    # Individual figure files
    'domain_distribution_plot': 'figures/domain_distribution.png',
    'source_breakdown_plot': 'figures/source_breakdown.png',
    'method_families_plot': 'figures/method_families.png',
    'completeness_heatmap': 'figures/completeness_heatmap.png'
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Manual extraction schema | Define CSV format and validation rules for manual paper extraction |
| C-5-2 | Data source parameters | Configure API endpoints, repository URLs, and collection thresholds |

---

## Complete Collection Configuration

```python
# Main orchestrator configuration (collect_benchmarks.py)
COLLECTION_CONFIG = {
    **DATA_SOURCES,
    **MANUAL_EXTRACTION_CONFIG,
    **VALIDATION_CONFIG,
    **SUCCESS_THRESHOLDS,
    **ERROR_HANDLING,
    **OUTPUT_PATHS
}

# Example usage in orchestrator
def main():
    from collect_benchmarks import CollectionOrchestrator
    
    orchestrator = CollectionOrchestrator(COLLECTION_CONFIG)
    benchmarks, metrics = orchestrator.run()
    
    print(f"Total collected: {metrics['total_count']}")
    print(f"Domains with >=10: {metrics['domains_above_10']}")
    print(f"Completeness: {metrics['completeness']}%")
    print(f"Success: {metrics['success']}")
```

---

## Schema Definition (Output Format)

```python
# Standardized benchmark record schema
BENCHMARK_SCHEMA = {
    "benchmark_id": "string (unique identifier, format: source_dataset_year)",
    "dataset_name": "string",
    "domain": "vision | time-series | tabular | graph",
    "sample_size": "integer (number of samples)",
    "dimensionality": "integer (feature count)",
    "num_classes": "integer (output classes)",
    "method_rankings": {
        "method_name": {
            "family": "Linear | Polynomial | RNN | Augmentation",
            "accuracy": "float (0-1)",
            "ranking_percentile": "float (0-100)"
        }
    },
    "source_paper": "string (citation)",
    "year": "integer (publication year)"
}

# Example record
EXAMPLE_RECORD = {
    "benchmark_id": "ogb_arxiv_2020",
    "dataset_name": "ogbn-arxiv",
    "domain": "graph",
    "sample_size": 169343,
    "dimensionality": 128,
    "num_classes": 40,
    "method_rankings": {
        "GCN": {
            "family": "Linear",
            "accuracy": 0.7189,
            "ranking_percentile": 35.2
        },
        "GraphSAINT": {
            "family": "Polynomial",
            "accuracy": 0.7207,
            "ranking_percentile": 45.8
        },
        "DAGNN": {
            "family": "Polynomial",
            "accuracy": 0.7264,
            "ranking_percentile": 78.3
        }
    },
    "source_paper": "Hu et al. OGB: Open Graph Benchmark. NeurIPS 2020",
    "year": 2020
}
```

---

## Validation Logic

```python
# Data validator implementation guide
def validate_benchmark_record(record: dict) -> tuple[bool, list[str]]:
    """Validate a single benchmark record against schema."""
    errors = []
    
    # Check required fields
    for field in VALIDATION_CONFIG['required_fields']:
        if field not in record:
            errors.append(f"Missing required field: {field}")
    
    # Check type constraints
    for field, expected_type in VALIDATION_CONFIG['type_constraints'].items():
        if field in record and not isinstance(record[field], expected_type):
            errors.append(f"Type mismatch for {field}: expected {expected_type}")
    
    # Check range constraints
    for field, (min_val, max_val) in VALIDATION_CONFIG['range_constraints'].items():
        if field in record:
            if not (min_val <= record[field] <= max_val):
                errors.append(f"{field} out of range: {record[field]} not in [{min_val}, {max_val}]")
    
    # Check domain validity
    if 'domain' in record and record['domain'] not in VALIDATION_CONFIG['valid_domains']:
        errors.append(f"Invalid domain: {record['domain']}")
    
    # Check method rankings completeness
    if 'method_rankings' in record:
        method_count = len(record['method_rankings'])
        if method_count < VALIDATION_CONFIG['min_methods_per_benchmark']:
            errors.append(f"Insufficient methods: {method_count} < {VALIDATION_CONFIG['min_methods_per_benchmark']}")
        
        for method_name, method_data in record['method_rankings'].items():
            for req_field in VALIDATION_CONFIG['required_method_fields']:
                if req_field not in method_data:
                    errors.append(f"Method {method_name} missing field: {req_field}")
    
    return len(errors) == 0, errors


def validate_collection(benchmarks: list[dict]) -> tuple[bool, dict]:
    """Validate entire collection against success criteria."""
    metrics = {
        'total_count': len(benchmarks),
        'domains_above_10': 0,
        'completeness': 0.0,
        'success': False
    }
    
    # Count domains with >=10 benchmarks
    domain_counts = {}
    for benchmark in benchmarks:
        domain = benchmark.get('domain', 'unknown')
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
    
    metrics['domains_above_10'] = sum(1 for count in domain_counts.values() if count >= 10)
    
    # Calculate completeness
    complete_benchmarks = sum(
        1 for b in benchmarks 
        if len(b.get('method_rankings', {})) >= VALIDATION_CONFIG['min_methods_per_benchmark']
    )
    metrics['completeness'] = (complete_benchmarks / len(benchmarks) * 100) if benchmarks else 0.0
    
    # Check success criteria
    metrics['success'] = (
        metrics['total_count'] >= SUCCESS_THRESHOLDS['total_benchmarks'] and
        metrics['domains_above_10'] >= SUCCESS_THRESHOLDS['domains_above_10'] and
        metrics['completeness'] == SUCCESS_THRESHOLDS['completeness']
    )
    
    return metrics['success'], metrics
```

---

## Usage Example (Phase 4 Implementation)

```python
# Main collection script: collect_benchmarks.py
from collectors.ogb_collector import OGBCollector
from collectors.github_collector import GitHubCollector
from collectors.pwc_collector import PapersWithCodeCollector
from collectors.manual_collector import ManualCollector
from processing.standardizer import SchemaStandardizer
from processing.validator import DataValidator

# Load configuration
config = COLLECTION_CONFIG

# Initialize collectors
ogb_collector = OGBCollector(config['ogb_datasets'])
github_collector = GitHubCollector(config['github_repos'])
pwc_collector = PapersWithCodeCollector(config['pwc_domains'])
manual_collector = ManualCollector([p['file'] for p in config['manual_papers']])

# Collect from all sources
raw_data = []
raw_data.extend(ogb_collector.collect())
raw_data.extend(github_collector.collect())
raw_data.extend(pwc_collector.collect())
raw_data.extend(manual_collector.collect())

# Standardize and validate
standardizer = SchemaStandardizer()
benchmarks = standardizer.standardize(raw_data)

validator = DataValidator()
success, metrics = validator.validate_collection(benchmarks)

# Save results
with open(config['benchmarks_collection'], 'w') as f:
    for benchmark in benchmarks:
        f.write(json.dumps(benchmark) + '\n')

print(f"Collection complete: {metrics}")
print(f"Success: {success}")
```

---

## Self-Validation Checklist

- [x] ONE format only (hardcoded dict, no dataclass)
- [x] No ASCII diagrams
- [x] KB search result noted ("Applied: Standard Python Data Collection Pattern")
- [x] No rationale for standard values (all are typical data collection defaults)
- [x] Subtask count within budget (2/2 used)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] Green-field project (Serena skip acceptable)
- [x] Focus on data collection parameters (no model hyperparameters)
- [x] LIGHT tier constraints observed (hardcoded config, no YAML)

---

**Document Status:** Ready for Implementation (Phase 4)
**Next Step:** Phase 4 Coder Agent - Implement data collection pipeline with these configurations
