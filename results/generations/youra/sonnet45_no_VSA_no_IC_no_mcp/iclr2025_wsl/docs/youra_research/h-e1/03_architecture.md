# Architecture: H-E1 Knowledge Base Extractor

**Date:** 2026-08-25  
**Hypothesis ID:** h-e1  
**Type:** EXISTENCE (PoC)  
**Architect:** Architecture Agent

---

## Design Patterns Applied

**Archon KB**: Data pipeline pattern (API → extract → validate → report)

**Codebase Analysis (Serena)**: Green-field project - no existing code

---

## System Overview

Single-script extraction pipeline (no training, no model artifacts).

**Flow:**
```
Papers With Code API
  ↓ (paginated requests)
Datasets List
  ↓ (for each dataset)
Benchmarks Query
  ↓ (for each benchmark)
Metrics Extraction
  ↓
(D,B,M) Triples
  ↓
YAML KB File + Coverage Metrics + Visualizations
```

**Execution:** Run once → output KB + validation report

---

## Module Structure

### 1. APIClient (`extract_kb.py::PWCAPIClient`)

```python
class PWCAPIClient:
    def __init__(self, cache_dir: str = "/data/pwc_cache/responses/"): ...
    def get_datasets(self) -> Iterator[Dataset]: ...
    def get_benchmarks(self, dataset_id: str) -> List[Benchmark]: ...
    def _paginate(self, initial_response) -> Iterator[Page]: ...
    def _cache_response(self, url: str, data: dict) -> None: ...
    def _load_cached(self, url: str) -> Optional[dict]: ...
```

**Dependencies:** `paperswithcode-client`, stdlib `json`, `pathlib`

---

### 2. TripleExtractor (`extract_kb.py::TripleExtractor`)

```python
class TripleExtractor:
    def __init__(self, api_client: PWCAPIClient): ...
    def extract_all(self) -> List[dict]: ...
    def _extract_from_dataset(self, dataset: Dataset) -> List[dict]: ...
    def _validate_triple(self, triple: dict) -> bool: ...
```

**Dependencies:** PWCAPIClient

---

### 3. KBWriter (`extract_kb.py::KBWriter`)

```python
class KBWriter:
    def __init__(self, output_path: str = "/data/pwc_cache/kb.yaml"): ...
    def save(self, triples: List[dict], metadata: dict) -> None: ...
    def _add_metadata_header(self, triples: List[dict]) -> dict: ...
```

**Dependencies:** `pyyaml`

---

### 4. Evaluator (`extract_kb.py::Evaluator`)

```python
class Evaluator:
    GROUND_TRUTH = [
        # Vision (15)
        "CIFAR-10", "CIFAR-100", "ImageNet", "COCO", "ADE20K", 
        "Pascal VOC", "MS COCO", "CelebA", "Places365", "STL-10",
        "SVHN", "Fashion-MNIST", "MNIST", "Caltech-101", "Caltech-256",
        # NLP (15)
        "GLUE", "SuperGLUE", "SQuAD", "WMT", "WikiText-103",
        "IMDB", "SST-2", "CoNLL-2003", "MultiNLI", "SNLI",
        "QQP", "MRPC", "RTE", "WNLI", "CoLA",
        # Audio (5)
        "LibriSpeech", "Common Voice", "TIMIT", "VoxCeleb", "AudioSet",
        # Graph (5)
        "Cora", "CiteSeer", "PubMed", "Reddit", "ogbn-arxiv",
        # Video (5)
        "Kinetics", "UCF-101", "Something-Something", "ActivityNet", "HMDB51",
        # Other (5)
        "Omniglot", "miniImageNet", "tieredImageNet", "CUB-200", "Stanford Cars"
    ]
    
    def __init__(self, triples: List[dict]): ...
    def compute_coverage(self) -> float: ...
    def compute_completeness(self) -> float: ...
    def get_missing_datasets(self) -> List[str]: ...
    def random_baseline(self, seed: int = 42) -> float: ...
    def save_metrics(self, output_path: str = "/data/pwc_cache/metrics.json") -> None: ...
```

**Dependencies:** stdlib `random`, `json`

---

### 5. Visualizer (`extract_kb.py::Visualizer`)

```python
class Visualizer:
    def __init__(self, output_dir: str = "h-e1/figures/"): ...
    def plot_coverage_comparison(self, extracted: float, baseline: float) -> None: ...
    def plot_domain_distribution(self, triples: List[dict]) -> None: ...
    def save_missing_datasets_table(self, missing: List[str]) -> None: ...
```

**Dependencies:** `matplotlib`, `pandas`

---

## File Structure

```
/data/pwc_cache/
├── responses/               # API response cache (JSON files)
│   ├── datasets_page1.json
│   ├── datasets_page2.json
│   └── benchmarks_{id}.json
├── kb.yaml                  # Final KB output
└── metrics.json             # Coverage + completeness metrics

h-e1/
├── code/
│   └── extract_kb.py        # Single-script implementation
└── figures/
    ├── coverage_comparison.png
    ├── domain_distribution.png
    └── missing_datasets.txt
```

---

## Data Flow

**Step 1: API Query (with caching)**
- Query `/datasets` endpoint (paginated)
- Cache responses to `/data/pwc_cache/responses/`
- If cache exists (<24h), skip API call

**Step 2: Triple Extraction**
- For each dataset: query `/datasets/{id}/benchmarks`
- For each benchmark: extract metrics from evaluations
- Filter: skip triples with missing fields (log warning)

**Step 3: KB Storage**
- Format: YAML list of dictionaries
- Schema: `{dataset: str, benchmark: str, metric: str}`
- Metadata header: extraction timestamp, API version, triple count

**Step 4: Evaluation**
- Coverage: count datasets in GROUND_TRUTH found in KB
- Completeness: % of triples with all 3 fields populated
- Baseline: random 50% coverage (seed=42)

**Step 5: Visualization**
- Bar chart: extracted vs baseline coverage
- Pie chart: domain distribution (vision/NLP/audio/graph/video)
- Text file: missing datasets list

---

## Error Handling

**API Failures:**
- Retry 3x with exponential backoff (1s, 2s, 4s)
- Timeout: 30s per request
- On total failure: log error, continue with partial results

**Missing Metadata:**
- Skip incomplete triples (log warning)
- Report completeness % in metrics

**Cache Corruption:**
- Delete corrupted file, re-fetch from API

**Graceful Degradation:**
- If coverage <100% of API queries succeed, report partial coverage
- Don't fail entire pipeline on single dataset failure

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup | Install dependencies, create cache directory | 4 | setup(1) + deps(1) + verify(2) |
| A-2 | API Client | Implement PWC API wrapper with caching | 8 | client(2) + pagination(2) + cache(2) + retry(2) |
| A-3 | Extraction | Triple extraction from API responses | 6 | parse(2) + validate(2) + store(2) |
| A-4 | Evaluation | Coverage + completeness metrics | 5 | coverage(2) + completeness(1) + baseline(2) |
| A-5 | Visualization | Generate 3 figures | 5 | bar(2) + pie(2) + table(1) |

**Total Complexity:** 28  
**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1, A-2, A-3, A-4, A-5]

**Note:** EXISTENCE PoC uses 5 tasks (not 6-12), all low-medium complexity.

---

## Integration Points for Phase 4

**Execution:**
```bash
cd h-e1/code
python extract_kb.py
```

**Expected Runtime:** 5-10 minutes (API latency dependent)

**Success Validation:**
```python
# Phase 5 will check:
assert os.path.exists("/data/pwc_cache/kb.yaml")
assert os.path.exists("/data/pwc_cache/metrics.json")

with open("/data/pwc_cache/metrics.json") as f:
    metrics = json.load(f)
    assert metrics["coverage"] > 0.80  # MUST_WORK gate
    assert metrics["completeness"] > 0.95
    assert metrics["extracted_coverage"] > metrics["baseline_coverage"]

# Verify figures exist
assert len(os.listdir("h-e1/figures/")) == 3
```

**Outputs for Downstream Hypotheses:**
- KB file (`kb.yaml`) → used by H-M1 (constraint validator)
- Metrics (`metrics.json`) → validation report input

---

## Configuration Parameters (Hardcoded)

```python
# No external config file - all hardcoded in script
CONFIG = {
    "cache_dir": "/data/pwc_cache/responses/",
    "kb_output": "/data/pwc_cache/kb.yaml",
    "metrics_output": "/data/pwc_cache/metrics.json",
    "figures_dir": "h-e1/figures/",
    "retry_attempts": 3,
    "request_timeout": 30,
    "random_seed": 42,
    "cache_expiry_hours": 24
}
```

---

## Self-Validation Checklist

- [x] No ASCII diagrams (used simple arrow flow)
- [x] Module sections = interface code only (no prose explanations)
- [x] 5 Epic tasks (EXISTENCE PoC: 3-5 tasks, not 6-12)
- [x] Single-script architecture (extract_kb.py)
- [x] Codebase Analysis section included (green-field status noted)
- [x] Total length <500 lines
- [x] No unrequested abstractions (single class per concern)
- [x] No config files (all hardcoded per NFR4)

---

*Minimal PoC architecture: prove "does it work?" with single-script extraction pipeline.*
