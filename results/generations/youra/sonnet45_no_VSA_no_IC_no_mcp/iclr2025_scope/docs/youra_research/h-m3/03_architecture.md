# Architecture Specification: h-m3

**Date:** 2026-08-25
**Hypothesis ID:** h-m3
**Type:** MECHANISM
**Phase:** Phase 3 - Architecture

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase
**Status:** Patterns found from existing hypotheses
**Analyzed Path:** docs/youra_research/_archive/
**Findings:** Existing experiments use modular structure (data_loader, evaluator, visualizer, validation_reporter, run_experiment). Reusing pattern.

---

## Knowledge Base Patterns (Archon)

Applied: Bipartite graph projection + Louvain community detection pattern

---

## Overview

**Hypothesis:** If we model benchmark usage as a bipartite graph and apply community detection, then methods using the same benchmarks will cluster into research communities with ≥70% shared citation patterns.

**Approach:** 
1. Fetch benchmark-method links from Papers with Code API
2. Fetch citation data from Semantic Scholar API
3. Construct bipartite graph (benchmarks ↔ methods)
4. Project to unipartite graph (methods only, weighted by shared benchmarks)
5. Apply Louvain community detection
6. Measure citation overlap within communities vs random baseline

**Success Criteria:**
- PRIMARY: Citation overlap ≥0.70 within detected communities
- SECONDARY: Modularity >0.4

---

## Module Structure

### DataLoader (`src/data_loader.py`)

**Dependencies:** requests, networkx, json

```python
class APIDataLoader:
    def __init__(self, cache_dir: str, rate_limit_delay: float = 0.01): ...
    def fetch_benchmark_methods(self, benchmark_names: List[str]) -> Dict[str, List[str]]: ...
    def fetch_citations(self, paper_ids: List[str]) -> Dict[str, Set[str]]: ...
    def build_bipartite_graph(self, benchmark_methods: Dict) -> nx.Graph: ...
    def save_cache(self, graph: nx.Graph, citations: Dict, cache_dir: str): ...
    def load_cache(self, cache_dir: str) -> Tuple[nx.Graph, Dict]: ...
```

### CommunityDetector (`src/community_detector.py`)

**Dependencies:** networkx, community (python-louvain), random

```python
class BipartiteCommunityDetector:
    def __init__(self, resolution: float = 1.0, random_seed: int = 42, min_community_size: int = 5): ...
    def detect_communities(self, bipartite_graph: nx.Graph) -> Dict[str, int]: ...
    def baseline_random(self, nodes: List[str], num_communities: int) -> Dict[str, int]: ...
    def project_to_unipartite(self, bipartite_graph: nx.Graph) -> nx.Graph: ...
```

### Evaluator (`src/evaluator.py`)

**Dependencies:** networkx, community, numpy

```python
class CommunityEvaluator:
    def compute_citation_overlap(self, communities: Dict[str, int], citation_dict: Dict[str, Set[str]]) -> float: ...
    def compute_modularity(self, communities: Dict[str, int], graph: nx.Graph) -> float: ...
    def compute_community_stats(self, communities: Dict[str, int]) -> Dict[str, Any]: ...
    def jaccard_similarity(self, set1: Set[str], set2: Set[str]) -> float: ...
```

### Visualizer (`src/visualizer.py`)

**Dependencies:** matplotlib, seaborn, networkx

```python
class CommunityVisualizer:
    def __init__(self, output_dir: str): ...
    def plot_gate_metrics(self, target: Dict, actual: Dict, save_path: str): ...
    def plot_community_sizes(self, communities: Dict[str, int], save_path: str): ...
    def plot_citation_heatmap(self, communities: Dict, citation_dict: Dict, save_path: str): ...
    def plot_network_graph(self, graph: nx.Graph, communities: Dict, save_path: str): ...
```

### ValidationReporter (`src/validation_reporter.py`)

**Dependencies:** yaml, datetime

```python
class ValidationReporter:
    def __init__(self, output_path: str): ...
    def generate_report(self, metrics: Dict, gate_result: str) -> str: ...
    def save_report(self, report: str, metrics: Dict): ...
```

### Main Orchestrator (`run_experiment.py`)

**Dependencies:** All modules above, yaml, os

```python
def main():
    # 1. Load config
    # 2. Data loading (API or cache)
    # 3. Community detection (proposed + baseline)
    # 4. Evaluation (citation overlap + modularity)
    # 5. Visualization (4 figures)
    # 6. Validation report (gate decision)
    pass
```

---

## Data Flow

1. **API Calls** → `DataLoader.fetch_benchmark_methods()` → benchmark-method dict
2. **API Calls** → `DataLoader.fetch_citations()` → citation dict
3. **Dicts** → `DataLoader.build_bipartite_graph()` → bipartite graph (cached)
4. **Bipartite graph** → `CommunityDetector.project_to_unipartite()` → unipartite graph
5. **Unipartite graph** → `CommunityDetector.detect_communities()` → partition (proposed)
6. **Nodes** → `CommunityDetector.baseline_random()` → partition (baseline)
7. **Partitions + citations** → `Evaluator.compute_citation_overlap()` → overlap metric
8. **Partition + graph** → `Evaluator.compute_modularity()` → modularity metric
9. **Metrics** → `Visualizer.plot_*()` → 4 figures
10. **Metrics** → `ValidationReporter.generate_report()` → 04_validation.md

---

## File Organization

```
experiments/h-m3/
├── src/
│   ├── data_loader.py          # API calls, graph construction, caching
│   ├── community_detector.py   # Louvain + baseline algorithms
│   ├── evaluator.py            # Citation overlap + modularity metrics
│   ├── visualizer.py           # 4 figures
│   └── validation_reporter.py  # Gate decision report
├── run_experiment.py           # Main pipeline orchestration
├── config.yaml                 # Experiment parameters
├── data/                       # Cache directory
│   ├── bipartite_graph.gpickle
│   └── citation_dict.json
├── figures/                    # Output visualizations
│   ├── gate_metrics.png
│   ├── community_sizes.png
│   ├── citation_heatmap.png
│   └── network_graph.png
└── results/
    └── metrics.yaml
```

---

## Configuration Schema

```yaml
# config.yaml

# API settings
api:
  pwc_base_url: "https://paperswithcode.com/api/v1/"
  s2_base_url: "https://api.semanticscholar.org/v1/"
  rate_limit_delay: 0.01  # 10ms delay between requests (100 req/sec)
  timeout: 30

# Dataset settings
dataset:
  benchmarks:
    - "ImageNet"
    - "COCO"
    - "SQuAD"
    - "WMT14"
  publication_year_start: 2015
  publication_year_end: 2024
  min_degree: 3  # Filter nodes with <3 connections

# Algorithm settings
algorithm:
  resolution: 1.0
  random_seed: 42
  min_community_size: 5

# Success criteria
success_criteria:
  citation_overlap_threshold: 0.70
  modularity_threshold: 0.40

# Execution settings
execution:
  cache_dir: "data/"
  figures_dir: "figures/"
  results_dir: "results/"
  use_cache: true
```

---

## Component Interactions

**Phase 1: Data Collection**
- `run_experiment.py` → `DataLoader.fetch_benchmark_methods()` → Papers with Code API
- `run_experiment.py` → `DataLoader.fetch_citations()` → Semantic Scholar API
- `DataLoader` → `save_cache()` → disk (bipartite_graph.gpickle, citation_dict.json)

**Phase 2: Graph Construction**
- `DataLoader.build_bipartite_graph()` → NetworkX bipartite graph
- Filter low-degree nodes (<3 connections)
- `CommunityDetector.project_to_unipartite()` → weighted projection (shared benchmarks)

**Phase 3: Community Detection**
- `CommunityDetector.detect_communities()` → Louvain algorithm → partition
- `CommunityDetector.baseline_random()` → random assignment → baseline partition

**Phase 4: Evaluation**
- `Evaluator.compute_citation_overlap()` → pairwise Jaccard → average per community
- `Evaluator.compute_modularity()` → graph partition quality
- Compare proposed vs baseline

**Phase 5: Visualization**
- `Visualizer.plot_gate_metrics()` → target vs actual bar chart
- `Visualizer.plot_community_sizes()` → histogram of community sizes
- `Visualizer.plot_citation_heatmap()` → intra vs inter community overlap
- `Visualizer.plot_network_graph()` → force-directed layout with community colors

**Phase 6: Validation**
- `ValidationReporter.generate_report()` → gate decision (PASS/PIVOT/FAIL)
- Save metrics.yaml and 04_validation.md

---

## Error Handling

### API Failures

**Papers with Code API errors:**
- HTTP 404 (benchmark not found): Log warning, skip benchmark
- HTTP 429 (rate limit): Sleep 1 second, retry 3 times
- Connection timeout: Retry with exponential backoff (max 3 attempts)

**Semantic Scholar API errors:**
- HTTP 404 (paper not found): Skip paper, log warning
- HTTP 429 (rate limit): Enforce 10ms delay between requests
- Empty citation list: Store empty set (valid case)

### Graph Construction Errors

**Empty graph after filtering:**
- Log error, increase min_degree threshold
- Fallback: Use unfiltered graph with warning

**Isolated nodes:**
- Remove before projection (standard practice)
- Log count of removed nodes

**Single-component check:**
- If multiple components, use largest component
- Log component sizes

### Community Detection Errors

**Louvain fails to converge:**
- Increase resolution parameter
- Fallback to Leiden algorithm (PIVOT mode)

**Single community output:**
- Log error, decrease resolution
- Skip overlap computation (undefined)

### Evaluation Errors

**Empty citation sets:**
- Jaccard = 0.0 (standard definition)
- Log warning if >50% of pairs have empty citations

**Modularity computation fails:**
- Check graph connectivity
- Log error, set modularity = 0.0

---

## Integration Points

### Input Data Sources

1. **Papers with Code API** (`/api/v1/benchmarks/{name}/results/`)
   - Returns: List of papers using benchmark
   - Fields: paper_id, title, authors, publication_date
   - Rate limit: None documented (respect 100 req/sec)

2. **Semantic Scholar API** (`/v1/paper/{id}`)
   - Returns: Paper metadata + citations
   - Fields: citations (list of paper IDs)
   - Rate limit: 100 req/sec (free tier)

### Output Artifacts

1. **Cache files** (reproducibility)
   - `data/bipartite_graph.gpickle` - NetworkX graph object
   - `data/citation_dict.json` - {paper_id: [cited_ids]}

2. **Figures** (validation)
   - `figures/gate_metrics.png` - Target vs actual metrics
   - `figures/community_sizes.png` - Distribution histogram
   - `figures/citation_heatmap.png` - Overlap matrix
   - `figures/network_graph.png` - Graph visualization

3. **Validation report** (gate decision)
   - `results/metrics.yaml` - Numeric results
   - `04_validation.md` - Gate decision document

### External Dependencies

```
networkx>=3.0
python-louvain>=0.16
requests>=2.31
matplotlib>=3.7
seaborn>=0.12
numpy>=1.24
pyyaml>=6.0
```

---

## Reproducibility Guarantees

1. **Random seed = 42**
   - Louvain algorithm
   - Random baseline partition
   - Force-directed graph layout

2. **Caching**
   - All API responses cached to disk
   - Cache keyed by benchmark list + date range
   - Cache check before API calls

3. **Deterministic algorithms**
   - NetworkX bipartite projection (deterministic for same graph)
   - Louvain with fixed seed (deterministic)
   - Jaccard computation (deterministic)

4. **Logging**
   - Log all hyperparameters to metrics.yaml
   - Log API call count and cache hits
   - Log graph statistics (nodes, edges, components)

---

## Performance Constraints

**Execution time target:** <10 minutes

**Bottlenecks:**
1. API calls (rate-limited to 100 req/sec)
   - ~200 papers × 10ms = 2 seconds
   - ~200 citation requests × 10ms = 2 seconds
   - Total API time: ~5 minutes (conservative)

2. Community detection (Louvain O(n log n))
   - 200 nodes → <1 second

3. Citation overlap computation (O(n² × citation_set_size))
   - 200 nodes, 5 communities → ~5 × 40² pairs = 8000 comparisons
   - ~1 second

**Expected total:** 6-8 minutes

**Optimizations:**
- Use cache on repeat runs (<1 minute without API calls)
- Batch API requests where possible
- Compute overlap only within communities (not all pairs)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Collection | API integration + caching | 9 | Module(3) + Dep(2) + Algo(2) + Int(2) |
| A-2 | Graph Construction | Bipartite graph building + projection | 8 | Module(2) + Dep(2) + Algo(2) + Int(2) |
| A-3 | Community Detection | Louvain + baseline implementation | 10 | Module(2) + Dep(3) + Algo(3) + Int(2) |
| A-4 | Evaluation Metrics | Citation overlap + modularity | 8 | Module(2) + Dep(2) + Algo(2) + Int(2) |
| A-5 | Visualization | 4 figures generation | 7 | Module(2) + Dep(1) + Algo(2) + Int(2) |
| A-6 | Validation Report | Gate decision logic + report | 6 | Module(1) + Dep(1) + Algo(2) + Int(2) |

**Distribution:** 
- VeryHigh(18-20): []
- High(14-17): []
- Medium(9-13): [A-1, A-3]
- Low(4-8): [A-2, A-4, A-5, A-6]

**Total Complexity:** 48 (6 tasks)

---

## Task Breakdown Details

### A-1: Data Collection (Complexity: 9)

**Subtasks:**
1. Implement Papers with Code API client (2 points)
   - HTTP requests with retry logic
   - Benchmark query endpoint
   - Response parsing

2. Implement Semantic Scholar API client (2 points)
   - Rate limiting (10ms delay)
   - Citation extraction
   - Error handling (404, 429)

3. Caching system (3 points)
   - Save/load bipartite graph (gpickle)
   - Save/load citation dict (JSON)
   - Cache invalidation logic

4. Integration testing (2 points)
   - Mock API responses
   - Cache hit/miss verification
   - Error recovery

### A-2: Graph Construction (Complexity: 8)

**Subtasks:**
1. Bipartite graph builder (2 points)
   - Add nodes with bipartite attribute
   - Add edges from benchmark-method links
   - Filter by publication year

2. Graph filtering (2 points)
   - Remove low-degree nodes (<3)
   - Remove isolated nodes
   - Extract largest component

3. Unipartite projection (2 points)
   - NetworkX weighted projection
   - Verify projection weights
   - Save projected graph

4. Graph validation (2 points)
   - Check bipartite property
   - Verify edge weights
   - Log graph statistics

### A-3: Community Detection (Complexity: 10)

**Subtasks:**
1. Louvain implementation (3 points)
   - python-louvain integration
   - Resolution parameter tuning
   - Seed setting for reproducibility

2. Baseline random partition (2 points)
   - Random assignment with seed
   - Match number of communities
   - Verify uniform distribution

3. Community filtering (2 points)
   - Remove small communities (<5 nodes)
   - Merge or discard outliers
   - Log community sizes

4. Algorithm comparison (3 points)
   - Run both proposed and baseline
   - Verify partition validity
   - Store both results

### A-4: Evaluation Metrics (Complexity: 8)

**Subtasks:**
1. Citation overlap computation (3 points)
   - Pairwise Jaccard within communities
   - Average across communities
   - Handle empty citation sets

2. Modularity computation (2 points)
   - python-louvain modularity function
   - Verify against manual calculation
   - Log modularity per community

3. Community statistics (2 points)
   - Size distribution
   - Density per community
   - Inter vs intra community edges

4. Comparison logic (1 point)
   - Proposed vs baseline
   - Statistical significance (if applicable)
   - Gate decision threshold check

### A-5: Visualization (Complexity: 7)

**Subtasks:**
1. Gate metrics bar chart (2 points)
   - Target vs actual bars
   - Threshold lines
   - Color coding (pass/fail)

2. Community size histogram (2 points)
   - Size distribution
   - Bin selection
   - Overlay mean/median

3. Citation heatmap (2 points)
   - Pairwise Jaccard matrix
   - Sort by community
   - Color scale (0-1)

4. Network graph visualization (1 point)
   - Force-directed layout
   - Community colors
   - Edge weights

### A-6: Validation Report (Complexity: 6)

**Subtasks:**
1. Metrics aggregation (1 point)
   - Collect all metrics
   - Format for report
   - Save to YAML

2. Gate decision logic (2 points)
   - Check ≥0.70 citation overlap
   - Check >0.4 modularity
   - Determine PASS/PIVOT/FAIL

3. Report generation (2 points)
   - Markdown template
   - Insert metrics
   - Include figures

4. Save artifacts (1 point)
   - Save metrics.yaml
   - Save 04_validation.md
   - Archive results

---

*Next Phase: Phase 4 - Implementation*
