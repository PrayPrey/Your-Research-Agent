# Product Requirements Document: h-m3

**Date:** 2026-08-25
**Author:** YOURA Research
**Hypothesis ID:** h-m3
**Type:** MECHANISM

---

## Hypothesis Statement

If we model benchmark usage as a bipartite graph (benchmarks ↔ methods) and apply community detection, then methods using the same benchmarks will cluster into research communities with ≥70% shared citation patterns, because benchmark constraints create methodological similarities.

## Success Criteria

**PRIMARY (Gate Criterion):**
- Citation overlap ≥0.70 within detected communities

**SECONDARY:**
- Modularity >0.4 (indicates well-separated communities)
- Proposed > Random baseline

**FAILURE CONDITIONS:**
- Citation overlap 60-70%: PIVOT (refine algorithm, add temporal weighting)
- Citation overlap <60%: FAIL (mechanism doesn't hold)

---

## Product Overview

### What We're Building

A bipartite graph community detection system that:
1. Constructs benchmark-method graph from Papers with Code + Semantic Scholar APIs
2. Projects bipartite graph to unipartite (methods-only)
3. Applies Louvain community detection
4. Measures citation overlap within communities

### Why

Tests whether benchmark usage creates measurable research communities (MECHANISM hypothesis). If methods using same benchmarks cluster with ≥70% citation overlap, benchmark constraints shape methodological choices.

### Core Deliverables

1. **Graph construction module**: Bipartite graph from API data
2. **Community detection module**: Louvain algorithm on projected graph
3. **Evaluation module**: Citation overlap + modularity metrics
4. **Visualization module**: 4 figures (bar chart, histogram, heatmap, network graph)
5. **Validation report**: Metrics vs success criteria

---

## Data Requirements

### Dataset Acquisition

**Source 1: Papers with Code API**
- **URL:** `https://paperswithcode.com/api/v1/`
- **What to collect:** Benchmark-method links (papers using specific benchmarks)
- **Filters:** Publication year 2015-2024, DL domain
- **Expected volume:** ~100-200 methods, ~50-100 benchmarks

**Source 2: Semantic Scholar API**
- **URL:** `https://api.semanticscholar.org/v1/`
- **What to collect:** Citation data for each method (cited paper IDs)
- **Rate limit:** 100 req/sec (free tier)
- **Expected volume:** ~1000-2000 citation edges

### Preprocessing Steps

1. Filter papers by year (2015-2024)
2. Extract benchmark citations using h-e1 classifier (validation vs baseline mentions)
3. Filter low-degree nodes (<3 connections)
4. Weight edges by citation frequency (co-citation strength)
5. Remove isolated nodes and small components (<5 nodes)

### Data Validation

- Verify bipartite graph has two node sets (methods, benchmarks)
- Verify no isolated nodes after filtering
- Verify edge weights are positive integers
- Cache processed graph to disk for reproducibility

**Cache Locations:**
- `docs/youra_research/h-m3/data/bipartite_graph.gpickle`
- `docs/youra_research/h-m3/data/citation_dict.json`

---

## Model Requirements

### Baseline Model

**Type:** Random Community Assignment

**Purpose:** Null hypothesis baseline (~50% citation overlap from random grouping)

**Implementation:**
```python
import random

def random_partition(nodes, num_communities=5):
    random.seed(42)
    partition = {}
    for node in nodes:
        partition[node] = random.randint(0, num_communities - 1)
    return partition
```

**Parameters:**
- `num_communities`: Match Louvain output (for fair comparison)
- `random_seed`: 42 (reproducibility)

### Proposed Model

**Type:** Louvain Community Detection on Projected Bipartite Graph

**Core Algorithm:**
1. Project bipartite graph to unipartite (methods-only, weighted by shared benchmarks)
2. Apply Louvain algorithm with modularity optimization
3. Compute citation overlap within communities

**Hyperparameters:**
- `resolution`: 1.0 (Louvain modularity parameter)
- `random_seed`: 42 (reproducibility)
- `min_community_size`: 5 methods (filter small clusters)

**Libraries:**
- `networkx` (bipartite projection)
- `python-louvain` (community detection)

**Model Cache:**
- `docs/youra_research/h-m3/models/communities.json` (partition output)

---

## Evaluation Requirements

### Metrics

**Primary Metric: Citation Overlap**
- **Definition:** Average pairwise Jaccard similarity within communities
- **Computation:** For each community, compute pairwise Jaccard over all method pairs, then average across communities
- **Success threshold:** ≥0.70

**Secondary Metric: Modularity**
- **Definition:** Graph partition quality (from Louvain output)
- **Computation:** `community_louvain.modularity(partition, graph)`
- **Success threshold:** >0.4

### Comparison

- **Baseline:** Random partition (~0.50 citation overlap expected)
- **Proposed:** Louvain (≥0.70 target)
- **Sanity check:** Proposed > Baseline

### Validation Logic

```python
# PoC success: Code runs + proposed > baseline
poc_pass = (code_runs_without_error 
            and proposed_citation_overlap > baseline_citation_overlap)

# Hypothesis validation: Citation overlap ≥0.70
hypothesis_pass = (proposed_citation_overlap >= 0.70 
                   and modularity > 0.4)

# Gate decision
if hypothesis_pass:
    gate_result = "PASS"
elif 0.60 <= proposed_citation_overlap < 0.70:
    gate_result = "PIVOT"  # Refine algorithm
else:
    gate_result = "FAIL"   # Mechanism doesn't hold
```

---

## Visualization Requirements

### Mandatory Figure

**Figure 1: Gate Metrics Comparison (Bar Chart)**
- X-axis: Metrics (Citation Overlap, Modularity)
- Y-axis: Value (0-1)
- Bars: Target (0.70, 0.40) vs Actual (from experiment)
- Save to: `figures/gate_metrics.png`

### Additional Figures (LLM Autonomous)

**Figure 2: Community Size Distribution (Histogram)**
- X-axis: Community size (number of methods)
- Y-axis: Frequency
- Purpose: Check balanced vs skewed partitions
- Save to: `figures/community_sizes.png`

**Figure 3: Citation Overlap Heatmap**
- Rows/Cols: Methods sorted by community
- Color: Jaccard similarity (0-1)
- Purpose: Visualize intra-community (high) vs inter-community (low) overlap
- Save to: `figures/citation_heatmap.png`

**Figure 4: Network Graph Visualization**
- Nodes: Methods (color-coded by community)
- Edges: Shared benchmark connections (weighted)
- Layout: Force-directed (Fruchterman-Reingold)
- Purpose: Qualitative inspection of community structure
- Save to: `figures/network_graph.png`

All figures saved to: `docs/youra_research/h-m3/figures/`

---

## Code Requirements

### Module Structure

```
experiments/h_m3/
├── data_loader.py          # API calls, graph construction
├── community_detector.py   # Louvain + baseline algorithms
├── evaluator.py            # Citation overlap + modularity metrics
├── visualizer.py           # 4 figures
└── main.py                 # Orchestration + validation report
```

### Key Functions

**data_loader.py:**
```python
def fetch_benchmark_methods(benchmark_name: str) -> List[str]:
    """Get papers using a benchmark from Papers with Code API."""
    pass

def fetch_citations(paper_id: str) -> Set[str]:
    """Get citations from Semantic Scholar API."""
    pass

def build_bipartite_graph() -> nx.Graph:
    """Construct bipartite graph (benchmarks ↔ methods)."""
    pass
```

**community_detector.py:**
```python
class BipartiteCommunityDetector:
    def __init__(self, resolution=1.0, random_seed=42):
        pass
    
    def detect_communities(self, bipartite_graph, citation_dict):
        """Apply Louvain to projected graph, return communities + metrics."""
        pass
```

**evaluator.py:**
```python
def compute_citation_overlap(communities, citation_dict) -> float:
    """Average pairwise Jaccard within communities."""
    pass

def compute_modularity(communities, graph) -> float:
    """Graph partition quality."""
    pass
```

**visualizer.py:**
```python
def plot_gate_metrics(target, actual, save_path):
    """Bar chart: target vs actual metrics."""
    pass

def plot_community_sizes(communities, save_path):
    """Histogram: community size distribution."""
    pass

def plot_citation_heatmap(communities, citation_dict, save_path):
    """Heatmap: pairwise Jaccard similarity."""
    pass

def plot_network_graph(graph, communities, save_path):
    """Force-directed graph with community colors."""
    pass
```

### Dependencies

```
networkx>=3.0
python-louvain>=0.16
requests>=2.31
matplotlib>=3.7
seaborn>=0.12
numpy>=1.24
```

---

## Acceptance Criteria

### PoC Success (Phase 4 Validation)

1. Code runs without error
2. `proposed_citation_overlap > baseline_citation_overlap`

### Hypothesis Validation (Gate Decision)

1. Citation overlap ≥0.70 (PRIMARY)
2. Modularity >0.4 (SECONDARY)
3. All 4 figures generated and saved

### Failure Response

- **IF 0.60 ≤ overlap < 0.70:** PIVOT
  - Try Leiden algorithm (alternative to Louvain)
  - Weight edges by citation count (not just co-occurrence)
  - Add temporal weighting (recent papers weighted higher)
  
- **IF overlap < 0.60:** FAIL
  - Mechanism doesn't hold
  - Benchmark constraints insufficient to create communities
  - Document failure in validation report

---

## Technical Constraints

1. **API Rate Limits:**
   - Semantic Scholar: 100 req/sec (add 10ms delay between calls)
   - Papers with Code: No documented limit (respect robots.txt)

2. **Graph Size:**
   - Target: ~100-200 methods, ~50-100 benchmarks
   - Filter low-degree nodes (<3 connections) for stability

3. **Reproducibility:**
   - All random seeds set to 42
   - Cache all API responses to disk
   - Log all hyperparameters

4. **Execution Time:**
   - Target: <10 minutes on consumer laptop
   - Louvain is O(n log n), should handle 200 nodes easily

---

## Deliverables Checklist

- [ ] Bipartite graph constructed from APIs
- [ ] Louvain community detection implemented
- [ ] Baseline (random partition) implemented
- [ ] Citation overlap metric computed
- [ ] Modularity metric computed
- [ ] 4 figures generated
- [ ] Validation report written (04_validation.md)
- [ ] PoC success verified (proposed > baseline)
- [ ] Gate decision made (PASS/PIVOT/FAIL)

---

## Open Questions for Phase 4

1. Should we validate with multiple community detection algorithms (Louvain + Leiden)?
2. How to handle isolated benchmarks with no citations?
3. Should we weight edges by citation count or binary (used/not used)?

**Decision:** Phase 4 Coder should use binary edges (simplicity), validate with Louvain only (Phase 2C spec). Leiden is PIVOT fallback if citation overlap 60-70%.

---

*Next Phase: Phase 3 - Architecture, Logic, and Configuration design*
