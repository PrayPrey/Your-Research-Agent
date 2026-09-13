# Logic Design: h-m3

**Date:** 2026-08-25
**Author:** YOURA Research
**Hypothesis ID:** h-m3
**Type:** MECHANISM

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field - new graph analysis implementation
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## Core Logic Overview

**Algorithm**: Bipartite graph community detection via Louvain algorithm
**Primary Task**: Detect research communities from benchmark usage patterns
**Success Criterion**: Citation overlap ≥0.70 within communities

**Key Components**:
1. Bipartite graph construction (benchmarks ↔ methods)
2. Graph projection (bipartite → unipartite methods graph)
3. Louvain community detection (resolution=1.0)
4. Citation overlap computation (pairwise Jaccard)
5. Random baseline for comparison

**Applied**: NetworkX bipartite projection + python-louvain community detection

---

## L-1: BipartiteCommunityDetector [Complexity: 3, Budget: 20]

### API Signatures

```python
from typing import Dict, Set, Tuple
import networkx as nx

class BipartiteCommunityDetector:
    """Detect communities from benchmark-method bipartite graph."""
    
    def __init__(self, resolution: float = 1.0, random_seed: int = 42, min_community_size: int = 5):
        """
        Args:
            resolution: Louvain modularity parameter
            random_seed: Reproducibility seed
            min_community_size: Filter communities smaller than this
        """
        self.resolution = resolution
        self.random_seed = random_seed
        self.min_community_size = min_community_size
    
    def detect_communities(
        self, 
        bipartite_graph: nx.Graph, 
        citation_dict: Dict[str, Set[str]]
    ) -> Tuple[Dict[str, int], Dict[str, float]]:
        """
        Detect communities and compute metrics.
        
        Args:
            bipartite_graph: NetworkX bipartite graph with 'bipartite' node attribute
                             bipartite=0 for methods, bipartite=1 for benchmarks
            citation_dict: {method_id: set(cited_paper_ids)}
        
        Returns:
            communities: {method_id: community_label}
            metrics: {modularity: float, citation_overlap: float}
        """
        pass
    
    def random_baseline(
        self,
        method_ids: list,
        num_communities: int,
        citation_dict: Dict[str, Set[str]]
    ) -> Tuple[Dict[str, int], float]:
        """
        Random partition baseline.
        
        Args:
            method_ids: List of method node IDs
            num_communities: Number of communities (match Louvain output)
            citation_dict: Citation data for overlap computation
        
        Returns:
            partition: {method_id: random_label}
            citation_overlap: Random baseline overlap score
        """
        pass
```

### Pseudo-code

```
detect_communities(bipartite_graph, citation_dict):
    1. Extract method nodes (bipartite=0)
    2. Project to weighted unipartite graph:
       - Edge weight = number of shared benchmarks
       - G = bipartite.weighted_projected_graph(B, methods)
    3. Apply Louvain:
       - partition = community_louvain.best_partition(G, resolution, random_state)
    4. Filter small communities:
       - Remove communities with < min_community_size methods
       - Reassign orphaned nodes to nearest community
    5. Compute modularity:
       - modularity = community_louvain.modularity(partition, G)
    6. Compute citation overlap:
       - overlap = _compute_citation_overlap(partition, citation_dict)
    7. Return partition, {modularity, citation_overlap}

random_baseline(method_ids, num_communities, citation_dict):
    1. random.seed(random_seed)
    2. partition = {mid: random.randint(0, num_communities-1) for mid in method_ids}
    3. overlap = _compute_citation_overlap(partition, citation_dict)
    4. Return partition, overlap
```

### Subtasks [15/20 used]

| ID | Subtask | Description | Budget |
|----|---------|-------------|--------|
| L-1-1 | Graph projection | Bipartite to weighted unipartite | 3 |
| L-1-2 | Louvain detection | Apply community_louvain.best_partition | 2 |
| L-1-3 | Community filtering | Remove small communities | 3 |
| L-1-4 | Modularity computation | Graph partition quality metric | 2 |
| L-1-5 | Citation overlap | Average pairwise Jaccard within communities | 5 |

---

## L-2: Citation Overlap Computation [Complexity: 2, Budget: 10]

### API Signatures

```python
def compute_citation_overlap(
    partition: Dict[str, int],
    citation_dict: Dict[str, Set[str]]
) -> float:
    """
    Compute average pairwise Jaccard similarity within communities.
    
    Args:
        partition: {method_id: community_label}
        citation_dict: {method_id: set(cited_paper_ids)}
    
    Returns:
        float: Average citation overlap (0-1), 0.70+ is success
    """
    pass

def pairwise_jaccard(citations1: Set[str], citations2: Set[str]) -> float:
    """
    Jaccard similarity between two citation sets.
    
    Args:
        citations1, citations2: Sets of cited paper IDs
    
    Returns:
        float: |intersection| / |union|, 0 if union empty
    """
    pass
```

### Pseudo-code

```
compute_citation_overlap(partition, citation_dict):
    1. Group methods by community:
       - community_groups = defaultdict(list)
       - for method, label in partition: community_groups[label].append(method)
    
    2. For each community:
       - If len(methods) < 2: skip (no pairs)
       - overlaps = []
       - For each pair (m1, m2) in methods:
           * jaccard = pairwise_jaccard(citation_dict[m1], citation_dict[m2])
           * overlaps.append(jaccard)
       - community_overlap = mean(overlaps)
    
    3. Return mean(all_community_overlaps)

pairwise_jaccard(citations1, citations2):
    1. intersection = len(citations1 & citations2)
    2. union = len(citations1 | citations2)
    3. Return intersection / union if union > 0 else 0.0
```

### Tensor Shapes (Data Structures)

| Variable | Type | Shape/Structure | Note |
|----------|------|-----------------|------|
| partition | Dict | {str: int} | method_id → community_label |
| citation_dict | Dict | {str: Set[str]} | method_id → cited_paper_ids |
| community_groups | Dict | {int: List[str]} | community_label → [method_ids] |
| overlaps | List | [N_pairs] | Jaccard scores for all pairs |

### Subtasks [8/10 used]

| ID | Subtask | Description | Budget |
|----|---------|-------------|--------|
| L-2-1 | Group by community | Organize methods into communities | 2 |
| L-2-2 | Pairwise Jaccard | Compute similarity for all pairs | 4 |
| L-2-3 | Average across communities | Aggregate community scores | 2 |

---

## L-3: Graph Construction [Complexity: 2, Budget: 8]

### API Signatures

```python
def build_bipartite_graph(
    benchmark_methods: Dict[str, list],
    filter_degree: int = 3
) -> nx.Graph:
    """
    Construct bipartite graph from benchmark-method mappings.
    
    Args:
        benchmark_methods: {benchmark_id: [method_ids]}
        filter_degree: Remove nodes with degree < this value
    
    Returns:
        nx.Graph: Bipartite graph with 'bipartite' node attribute
                  Nodes: methods (bipartite=0) + benchmarks (bipartite=1)
    """
    pass

def validate_bipartite(G: nx.Graph) -> bool:
    """
    Verify graph is bipartite with no isolated nodes.
    
    Args:
        G: NetworkX graph to validate
    
    Returns:
        bool: True if valid bipartite graph
    
    Raises:
        ValueError: If graph is invalid (not bipartite, has isolated nodes)
    """
    pass
```

### Pseudo-code

```
build_bipartite_graph(benchmark_methods, filter_degree):
    1. G = nx.Graph()
    2. Extract unique method_ids and benchmark_ids
    3. Add nodes:
       - G.add_nodes_from(method_ids, bipartite=0)
       - G.add_nodes_from(benchmark_ids, bipartite=1)
    4. Add edges:
       - For benchmark, methods in benchmark_methods:
           * For method in methods: G.add_edge(method, benchmark)
    5. Filter low-degree nodes:
       - Remove nodes with degree < filter_degree
       - Remove isolated nodes
    6. Validate bipartite structure
    7. Return G

validate_bipartite(G):
    1. Check bipartite: nx.is_bipartite(G)
    2. Check no isolated nodes: all(G.degree(n) > 0 for n in G.nodes())
    3. Verify two node sets exist with 'bipartite' attribute
    4. Return True or raise ValueError
```

### Subtasks [6/8 used]

| ID | Subtask | Description | Budget |
|----|---------|-------------|--------|
| L-3-1 | Node/edge construction | Build NetworkX graph structure | 2 |
| L-3-2 | Degree filtering | Remove low-degree nodes | 2 |
| L-3-3 | Validation | Check bipartite invariants | 2 |

---

## L-4: Modularity Computation [Complexity: 1, Budget: 2]

### API Signatures

```python
def compute_modularity(partition: Dict[str, int], graph: nx.Graph) -> float:
    """
    Graph partition quality metric.
    
    Args:
        partition: {node_id: community_label}
        graph: Unipartite graph (projected from bipartite)
    
    Returns:
        float: Modularity score, >0.4 indicates well-separated communities
    """
    pass
```

### Pseudo-code

```
compute_modularity(partition, graph):
    1. Return community_louvain.modularity(partition, graph)
```

**Applied**: python-louvain built-in modularity function

### Subtasks [2/2 used]

| ID | Subtask | Description | Budget |
|----|---------|-------------|--------|
| L-4-1 | Call library function | Wrapper around community_louvain.modularity | 2 |

---

## L-5: Data Structures and Edge Weighting [Complexity: 1, Budget: 5]

### Graph Representation

**Bipartite Graph (Input)**:
```python
# Nodes:
# - Methods: {id: paper_id, bipartite: 0}
# - Benchmarks: {id: benchmark_name, bipartite: 1}
# Edges:
# - (method, benchmark) if method uses benchmark
```

**Projected Graph (After Projection)**:
```python
# Nodes: methods only
# Edges: (method_i, method_j, weight)
# - weight = number of shared benchmarks between method_i and method_j
# - Computed automatically by bipartite.weighted_projected_graph()
```

### Edge Weighting Strategy

**Applied**: NetworkX weighted projection (shared neighbor count)

```
Edge weight = |shared_benchmarks(method_i, method_j)|
```

Example:
```
method_A uses [bench1, bench2, bench3]
method_B uses [bench2, bench3, bench4]
→ edge_weight(A, B) = 2 (shared: bench2, bench3)
```

### Citation Data Structure

```python
citation_dict: Dict[str, Set[str]]
# {
#   "method_id_1": {"cited_paper_1", "cited_paper_2", ...},
#   "method_id_2": {"cited_paper_3", "cited_paper_1", ...},
#   ...
# }
```

### Community Partition Structure

```python
partition: Dict[str, int]
# {
#   "method_id_1": 0,  # community 0
#   "method_id_2": 0,  # community 0
#   "method_id_3": 1,  # community 1
#   ...
# }
```

### Subtasks [3/5 used]

| ID | Subtask | Description | Budget |
|----|---------|-------------|--------|
| L-5-1 | Data structure definitions | Type annotations and schemas | 2 |
| L-5-2 | Edge weight documentation | Explain weighting strategy | 1 |

---

## Algorithm Parameters

| Parameter | Value | Source | Rationale |
|-----------|-------|--------|-----------|
| resolution | 1.0 | python-louvain default | Standard modularity optimization |
| random_seed | 42 | Standard practice | Reproducibility |
| min_community_size | 5 | Domain knowledge | Stable statistics for overlap |
| filter_degree | 3 | Best practice | Remove noise, ensure connectivity |

---

## Success Validation Logic

```python
def validate_results(proposed_overlap, baseline_overlap, modularity):
    """
    Determine gate decision.
    
    Returns:
        str: "PASS", "PIVOT", or "FAIL"
    """
    # PoC success: code runs + proposed > baseline
    poc_pass = proposed_overlap > baseline_overlap
    
    # Hypothesis validation
    if proposed_overlap >= 0.70 and modularity > 0.4:
        return "PASS"
    elif 0.60 <= proposed_overlap < 0.70:
        return "PIVOT"  # Refine algorithm (try Leiden, temporal weighting)
    else:
        return "FAIL"   # Mechanism doesn't hold
```

---

## Implementation Notes

**Libraries Required**:
```python
networkx>=3.0         # Bipartite graphs
python-louvain>=0.16  # Community detection
```

**Performance**:
- Target graph size: 100-200 methods, 50-100 benchmarks
- Expected runtime: <1 minute (Louvain is O(n log n))
- Memory: <100MB for graph structures

**Caching Strategy**:
- Cache bipartite graph to `data/bipartite_graph.gpickle`
- Cache citation_dict to `data/citation_dict.json`
- Cache community partition to `models/communities.json`

---

## Total Budget Usage

| Task | Allocated | Used | Remaining |
|------|-----------|------|-----------|
| L-1: BipartiteCommunityDetector | 20 | 15 | 5 |
| L-2: Citation Overlap | 10 | 8 | 2 |
| L-3: Graph Construction | 8 | 6 | 2 |
| L-4: Modularity | 2 | 2 | 0 |
| L-5: Data Structures | 5 | 3 | 2 |
| **Total** | **45** | **34** | **11** |

---

*Next Phase: Phase 4 - Implementation*
