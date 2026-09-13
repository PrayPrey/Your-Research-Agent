# Logic Design: H-E1 Papers With Code KB Extraction

**Date:** 2026-08-25  
**Hypothesis:** H-E1 (EXISTENCE)  
**Author:** Logic Agent  
**Type:** PoC - Deterministic extraction only  

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation - designing new APIs  
**Analyzed Path:** N/A  
**Relevant Symbols:** None - new implementation  

---

## Applied Patterns (Archon KB)

**Applied:** REST API pagination pattern  
**Applied:** Exponential backoff for rate limiting  
**Applied:** Local cache-first strategy  

---

## Core API Signatures

### 1. PWC API Client Wrapper

```python
from paperswithcode import PapersWithCodeClient
from typing import List, Dict, Optional
import yaml
import time

class PWCExtractor:
    def __init__(self, cache_dir: str = "/data/pwc_cache/"):
        """Initialize extractor. cache_dir: [str] -> None"""
        self.client = PapersWithCodeClient()
        self.cache_dir = cache_dir
        self.triples: List[Dict[str, str]] = []  # [(D,B,M) dicts]
    
    def extract_triples(self, max_datasets: Optional[int] = None) -> List[Dict[str, str]]:
        """Extract (D,B,M) triples. Returns: N × {dataset, benchmark, metric}"""
        ...
    
    def save_kb(self, output_file: str = "kb.yaml") -> None:
        """Save KB to YAML. triples: List[Dict] -> file"""
        ...
```

### 2. Coverage Evaluator

```python
class CoverageEvaluator:
    def __init__(self, ground_truth: List[str]):
        """Initialize evaluator. ground_truth: [50 dataset names]"""
        self.ground_truth = ground_truth
    
    def compute_coverage(self, extracted_kb: List[Dict[str, str]]) -> float:
        """Coverage = (# found) / 50. Returns: float [0,1]"""
        ...
    
    def compute_completeness(self, extracted_kb: List[Dict[str, str]]) -> float:
        """Completeness = (# complete triples) / total. Returns: float [0,1]"""
        ...
    
    def get_missing_datasets(self, extracted_kb: List[Dict[str, str]]) -> List[str]:
        """Return list of ground-truth datasets not found."""
        ...
```

### 3. Baseline Generator

```python
def random_baseline(ground_truth: List[str], seed: int = 42) -> float:
    """Random 50% baseline. Returns: coverage ~0.50"""
    import random
    random.seed(seed)
    found = random.sample(ground_truth, k=len(ground_truth) // 2)
    return len(found) / len(ground_truth)
```

---

## Data Structures

| Variable | Type | Shape/Size | Description |
|----------|------|------------|-------------|
| triples | List[Dict] | N × {D,B,M} | Extracted KB triples |
| ground_truth | List[str] | 50 | Well-known dataset names |
| coverage | float | scalar | Percentage [0,1] |
| completeness | float | scalar | Metadata quality [0,1] |

---

## Algorithm 1: Triple Extraction

```python
def extract_triples(self, max_datasets=None):
    datasets = self.client.dataset_list()  # Paginated response
    count = 0
    
    for dataset in self._paginate(datasets):
        if max_datasets and count >= max_datasets:
            break
        
        dataset_name = dataset.name
        
        # Get benchmarks for this dataset
        benchmarks = self._retry_api_call(
            lambda: self.client.dataset_benchmarks(dataset.id)
        )
        
        for benchmark in benchmarks.results:
            benchmark_name = benchmark.name
            
            # Extract metrics from evaluations
            evaluations = getattr(benchmark, 'evaluations', [])
            for eval in evaluations:
                metric_obj = getattr(eval, 'metric', None)
                if metric_obj:
                    metric_name = metric_obj.name
                    # Skip if any field missing
                    if dataset_name and benchmark_name and metric_name:
                        self.triples.append({
                            'dataset': dataset_name,
                            'benchmark': benchmark_name,
                            'metric': metric_name
                        })
        count += 1
    
    return self.triples
```

**Edge cases:**
- Missing metric object: skip triple
- API timeout: retry with exponential backoff
- Pagination end: check `next_page` field

---

## Algorithm 2: API Pagination Handler

```python
def _paginate(self, initial_response):
    """Yield all pages from API response."""
    current = initial_response
    while current:
        yield from current.results
        if hasattr(current, 'next_page') and current.next_page:
            current = self._retry_api_call(
                lambda: self.client._get(current.next_page)
            )
        else:
            break
```

---

## Algorithm 3: Exponential Backoff

```python
def _retry_api_call(self, api_call, max_retries=3):
    """Retry with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return api_call()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt  # 1s, 2s, 4s
            time.sleep(wait_time)
```

---

## Algorithm 4: Coverage Computation

```python
def compute_coverage(self, extracted_kb):
    # Extract unique dataset names from KB
    extracted_datasets = set([triple['dataset'] for triple in extracted_kb])
    
    # Exact string match (case-sensitive)
    found = [d for d in self.ground_truth if d in extracted_datasets]
    
    return len(found) / len(self.ground_truth)
```

**Edge cases:**
- Empty KB: coverage = 0
- Duplicate dataset names: set() deduplicates

---

## Algorithm 5: Completeness Check

```python
def compute_completeness(self, extracted_kb):
    """Check all (D,B,M) fields populated."""
    if not extracted_kb:
        return 0.0
    
    complete_triples = [
        t for t in extracted_kb 
        if all([t.get('dataset'), t.get('benchmark'), t.get('metric')])
    ]
    
    return len(complete_triples) / len(extracted_kb)
```

---

## Main Execution Flow

```python
if __name__ == '__main__':
    # 1. Initialize
    extractor = PWCExtractor(cache_dir="/data/pwc_cache/")
    evaluator = CoverageEvaluator(ground_truth=GROUND_TRUTH_DATASETS)
    
    # 2. Extract KB
    triples = extractor.extract_triples()  # ~4000 datasets
    extractor.save_kb("kb.yaml")
    
    # 3. Evaluate
    coverage = evaluator.compute_coverage(triples)
    completeness = evaluator.compute_completeness(triples)
    missing = evaluator.get_missing_datasets(triples)
    
    # 4. Baseline comparison
    baseline_coverage = random_baseline(GROUND_TRUTH_DATASETS, seed=42)
    
    # 5. Gate check
    print(f"Coverage: {coverage:.2%} (target: >80%)")
    print(f"Completeness: {completeness:.2%} (target: >95%)")
    print(f"Baseline: {baseline_coverage:.2%}")
    print(f"Missing: {missing}")
    
    # 6. MUST_WORK gate
    assert coverage > 0.80, f"Gate failed: {coverage:.2%} < 80%"
    
    # 7. Save metrics
    import json
    with open("/data/pwc_cache/metrics.json", 'w') as f:
        json.dump({
            'coverage': coverage,
            'completeness': completeness,
            'baseline': baseline_coverage,
            'missing_count': len(missing)
        }, f, indent=2)
```

---

## Ground Truth Dataset List

```python
GROUND_TRUTH_DATASETS = [
    # Vision (15)
    'CIFAR-10', 'CIFAR-100', 'ImageNet', 'COCO', 'ADE20K', 'Pascal VOC',
    'MS COCO', 'CelebA', 'Places365', 'STL-10', 'SVHN', 'Fashion-MNIST',
    'MNIST', 'Caltech-101', 'Caltech-256',
    
    # NLP (15)
    'GLUE', 'SuperGLUE', 'SQuAD', 'WMT', 'WikiText-103', 'IMDB',
    'SST-2', 'CoNLL-2003', 'MultiNLI', 'SNLI', 'QQP', 'MRPC',
    'RTE', 'WNLI', 'CoLA',
    
    # Audio (5)
    'LibriSpeech', 'Common Voice', 'TIMIT', 'VoxCeleb', 'AudioSet',
    
    # Graph (5)
    'Cora', 'CiteSeer', 'PubMed', 'Reddit', 'ogbn-arxiv',
    
    # Video (5)
    'Kinetics', 'UCF-101', 'Something-Something', 'ActivityNet', 'HMDB51',
    
    # Other (5)
    'Omniglot', 'miniImageNet', 'tieredImageNet', 'CUB-200', 'Stanford Cars'
]  # Total: 50
```

---

## Error Handling

### API Failures

```python
class APIError(Exception):
    """Custom exception for API errors."""
    pass

try:
    response = self.client.dataset_list()
except Exception as e:
    # Log error, continue with partial results
    print(f"API error: {e}")
    # Save partial KB if >0 triples extracted
    if self.triples:
        self.save_kb("kb_partial.yaml")
    raise APIError(f"Failed after {len(self.triples)} triples")
```

### Missing Fields

```python
# In extract_triples loop:
metric_name = getattr(metric_obj, 'name', None)
if not metric_name:
    # Log warning, skip this triple
    print(f"Warning: Missing metric for {dataset_name}/{benchmark_name}")
    continue
```

### Cache Directory

```python
import os
os.makedirs(self.cache_dir, exist_ok=True)
```

---

## Performance Notes

**Expected Runtime:**
- API queries: ~5-10 min (4000 datasets, ~0.1s per request)
- Processing: <1 min
- Total: <15 min (within NFR1 requirement)

**Bottlenecks:**
- Network I/O for API calls
- Pagination overhead

**Optimizations:**
- Cache API responses locally (skip if file exists)
- Parallel requests (if rate limit allows)

---

## File Outputs

| File | Path | Format | Size |
|------|------|--------|------|
| KB | /data/pwc_cache/kb.yaml | YAML | ~500KB |
| Metrics | /data/pwc_cache/metrics.json | JSON | ~1KB |
| Validation | h-e1/04_validation.md | Markdown | ~5KB |

---

## Dependencies

```python
# requirements.txt
paperswithcode-client>=0.3.0
pyyaml>=5.4
matplotlib>=3.5
pandas>=1.3
```

---

*Total logic design: deterministic extraction with retry/cache patterns. No training required.*
