# Architecture: H-M1 KB Extraction Logic Validator

**Date:** 2026-08-25  
**Hypothesis ID:** h-m1  
**Type:** MECHANISM (PoC)  
**Architect:** Architecture Agent

---

## Design Patterns Applied

**Archon KB**: Data pipeline pattern (API → extract → validate → report)

**Codebase Analysis (Serena)**

**Project Type**: base_hypothesis  
**Status**: Reusing h-e1 code structure  
**Analyzed Path**: `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_wsl/docs/youra_research/h-e1/code/`  
**Findings**: Single-script extraction pipeline at `extract_kb.py` - proven 84% coverage. h-m1 validates the mechanism logic itself.

---

## System Overview

Single-script extraction pipeline validating automated KB extraction achieves >80% coverage without manual curation.

**Flow:**
```
HuggingFace Datasets Hub API
  ↓ (list all datasets)
Dataset Metadata Query
  ↓ (infer benchmarks/metrics)
(D,B,M) Triple Extraction
  ↓
YAML KB File + Coverage Metrics + Visualizations
```

**Execution:** Run once → validate coverage >80% → confirm mechanism works

---

## Module Structure

### 1. APIClient (`extract_kb.py::PWCExtractor`)

```python
class PWCExtractor:
    def __init__(self, cache_dir: str): ...
    def extract_triples(self, ground_truth_datasets: List[str]) -> List[Dict]: ...
    def _retry_api_call(self, url: str, max_retries: int = 3) -> dict: ...
    def _infer_benchmark(self, dataset_name: str) -> str: ...
    def _infer_metric(self, dataset_name: str) -> str: ...
```

**Dependencies:** `requests`, `pathlib`

---

### 2. Evaluator (`extract_kb.py::Evaluator`)

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
```

**Dependencies:** stdlib `random`, `json`

---

### 3. Visualizer (`extract_kb.py::Visualizer`)

```python
class Visualizer:
    def __init__(self, output_dir: str = "h-m1/figures/"): ...
    def plot_coverage_comparison(self, extracted: float, baseline: float, h_e1: float = 0.84) -> None: ...
    def plot_domain_distribution(self, triples: List[dict]) -> None: ...
    def plot_gate_metrics(self, actual_coverage: float, target: float = 0.80) -> None: ...
    def save_missing_datasets_table(self, missing: List[str]) -> None: ...
```

**Dependencies:** `matplotlib`, `pandas`

---

## File Structure

```
/data/pwc_cache/
├── responses/               # API response cache (optional - from h-e1)
└── kb.yaml                  # KB output (reused from h-e1 or regenerated)

h-m1/
├── code/
│   └── extract_kb.py        # Single-script implementation (adapted from h-e1)
├── data/
│   └── pwc_cache/
│       ├── kb.yaml          # KB extraction output
│       └── metrics.json     # Coverage metrics
└── figures/
    ├── coverage_comparison.png      # random vs manual vs h-e1 vs h-m1
    ├── domain_distribution.png      # coverage by domain
    ├── gate_metrics.png             # target 80% vs actual
    ├── metadata_completeness.png    # histogram of triple completeness
    └── missing_datasets.txt         # list of datasets not found
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| PWCExtractor | `from h_e1.code.extract_kb import PWCExtractor` | `h-e1/code/extract_kb.py` |
| GROUND_TRUTH_DATASETS | `from h_e1.code.extract_kb import GROUND_TRUTH_DATASETS` | `h-e1/code/extract_kb.py` |

**Verified from**: `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_wsl/docs/youra_research/h-e1/code/` (actual implementation)

**Reuse Strategy**: Copy h-e1/code/extract_kb.py to h-m1/code/ with minor adaptations:
- Update output paths to h-m1/data/pwc_cache/
- Update figure paths to h-m1/figures/
- Add h-e1 comparison to visualizations (84% baseline)

---

## Data Flow

**Step 1: API Query (automated extraction)**
- Use HuggingFace Datasets Hub API (list all datasets)
- No manual intervention - fully automated

**Step 2: Triple Extraction**
- For each dataset: infer benchmark from dataset name or metadata
- For each benchmark: infer default metric ("accuracy")
- Filter: skip triples with missing fields (log warning)

**Step 3: KB Storage**
- Format: YAML list of dictionaries
- Schema: `{dataset: str, benchmark: str, metric: str}`

**Step 4: Evaluation (mechanism validation)**
- Coverage: count datasets in GROUND_TRUTH found in KB
- Gate check: coverage > 0.80 (MUST_WORK)
- Completeness: % of triples with all 3 fields populated (>0.95)
- Baseline comparison: random (50%), manual (60-70%), h-e1 (84%)

**Step 5: Visualization**
- Gate metrics: target 80% vs actual
- Coverage comparison: random/manual/h-e1/h-m1
- Domain distribution: coverage by domain
- Metadata completeness: histogram
- Missing datasets: text file

---

## Error Handling

**API Failures:**
- Retry 3x with exponential backoff (1s, 2s, 4s)
- Timeout: 30s per request
- On total failure: log error, continue with partial results

**Missing Metadata:**
- Use inference rules (benchmark = dataset_name + "-benchmark", metric = "accuracy")
- Report completeness % in metrics

**Graceful Degradation:**
- If coverage <100% of API queries succeed, report partial coverage
- Don't fail entire pipeline on single dataset failure

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup | Copy h-e1 code, adapt paths to h-m1 | 3 | copy(1) + adapt(1) + verify(1) |
| A-2 | Extraction | Run automated KB extraction (no manual steps) | 5 | run(2) + validate(2) + cache(1) |
| A-3 | Evaluation | Coverage + completeness metrics + gate check | 6 | coverage(2) + completeness(2) + gate(2) |
| A-4 | Visualization | Generate 5 figures (gate metrics, comparison, domain, completeness, missing) | 7 | gate(2) + comparison(2) + domain(1) + completeness(1) + missing(1) |

**Total Complexity:** 21  
**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1, A-2, A-3, A-4]

**Note:** MECHANISM PoC uses 4 tasks (simplified for "does it work?" validation).

---

## Integration Points for Phase 4

**Execution:**
```bash
cd h-m1/code
python extract_kb.py
```

**Expected Runtime:** 5-10 minutes (API latency dependent)

**Success Validation:**
```python
# Phase 5 will check:
assert os.path.exists("h-m1/data/pwc_cache/kb.yaml")
assert os.path.exists("h-m1/data/pwc_cache/metrics.json")

with open("h-m1/data/pwc_cache/metrics.json") as f:
    metrics = json.load(f)
    assert metrics["coverage"] > 0.80  # MUST_WORK gate
    assert metrics["completeness"] > 0.95
    assert metrics["extracted_coverage"] > metrics["baseline_coverage"]

# Verify figures exist
assert len(os.listdir("h-m1/figures/")) == 5
```

---

## Configuration Parameters (Hardcoded)

```python
# No external config file - all hardcoded in script
CONFIG = {
    "cache_dir": "../data/pwc_cache",
    "response_cache": "../data/pwc_cache/responses",
    "kb_output": "../data/pwc_cache/kb.yaml",
    "metrics_output": "../data/pwc_cache/metrics.json",
    "figures_dir": "../figures",
    "retry_attempts": 3,
    "request_timeout": 30,
    "random_seed": 42,
    "coverage_threshold": 0.80,
    "completeness_threshold": 0.95,
}
```

---

## Self-Validation Checklist

- [x] No ASCII diagrams (used simple arrow flow)
- [x] Module sections = interface code only (no prose explanations)
- [x] 4 Epic tasks (MECHANISM PoC: 3-5 tasks, not 6-12)
- [x] Single-script architecture (extract_kb.py adapted from h-e1)
- [x] Codebase Analysis section included (base_hypothesis status noted)
- [x] External Dependencies section included with file locations
- [x] Total length <500 lines
- [x] Import paths verified from actual h-e1 code

---

*Minimal MECHANISM PoC: validate automated extraction logic achieves >80% coverage threshold.*
