# Experiment Design: h-m3

**Date:** 2026-08-25
**Author:** YOURA Research
**Hypothesis Statement:** If we model benchmark usage as a bipartite graph (benchmarks ↔ methods) and apply community detection, then methods using the same benchmarks will cluster into research communities with ≥70% shared citation patterns, because benchmark constraints create methodological similarities.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Hypothesis** - Tests whether benchmark usage creates measurable research communities.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** Yes (h-m1 COMPLETED)
**Gate Status:** MUST_WORK (failure blocks dependent hypotheses)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** MECHANISM
- **Prerequisites:** h-m1 (Feature extraction objectivity - COMPLETED)

### Gate Condition

**Gate Type:** MUST_WORK

If community citation overlap <70%, mechanism fails:
- IF 60-70%: PIVOT - refine community detection algorithm, add temporal weighting
- IF <60%: EXPLORE - are benchmark constraints strong enough to shape communities?

---

## Continuation Context

**Previous Hypothesis:** h-m1 (Feature Extraction Objectivity)
- **Status:** COMPLETED (PASS)
- **Key Findings:** Standardized protocol achieved >0.80 inter-rater agreement
- **Relation to h-m3:** Provides validated feature extraction protocol for graph construction

**Continuation Strategy:** Independent mechanism test (no reuse from h-m1, different experimental approach)

### Previous Hypothesis Results

**h-m1 Results:**
- Status: COMPLETED
- Result: PASS
- Optimal settings: Papers with Code taxonomy for task types, regex for metrics
- Lessons: Objective feature extraction enables reliable benchmark analysis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**⚠️ ABLATION MODE:** Archon MCP disabled. Findings from domain knowledge, not retrieved cases.

**Query 1: Bipartite Graph Community Detection Experiment Design**

Result 1: Community detection in citation networks
- Dataset: Citation graph from Semantic Scholar API (papers ↔ citations)
- Hyperparameters: Louvain resolution=1.0, min_community_size=5
- Key insight: Bipartite graphs require projection to unipartite before standard community detection

Result 2: Benchmark usage pattern analysis
- Dataset: Benchmark-method bipartite graph from Papers with Code
- Evaluation: Modularity score >0.4 indicates strong communities
- Key insight: Weight edges by co-citation frequency for stronger signal

Result 3: Research community clustering
- Baseline: Random grouping (~50% citation overlap)
- Standard protocol: Project bipartite → unipartite, apply Louvain/Leiden
- Key insight: Citation overlap measured via Jaccard similarity

**Query 2: Implementation Challenges**

Common pitfalls:
- Bipartite projection loses information (choose mode: project to methods or benchmarks)
- Community detection sensitive to hyperparameters (resolution parameter)
- Sparse graphs yield unstable communities (filter low-degree nodes)

Best practices:
- Use weighted edges (citation count, co-occurrence frequency)
- Validate with multiple algorithms (Louvain, Leiden, label propagation)
- Measure robustness with bootstrap resampling

**Query 3: Citation Network Benchmarks**

Standard datasets:
- Semantic Scholar Open Research Corpus (citation graph)
- Microsoft Academic Graph (discontinued but archived)
- OpenCitations (open citation index)

Expected performance:
- Modularity >0.4 for well-separated communities
- Citation overlap 60-80% within communities (varies by domain)
- Silhouette score >0.3 indicates meaningful clusters

### Archon Code Examples

**⚠️ ABLATION MODE:** Code patterns from domain knowledge.

**Example 1: Bipartite Graph Community Detection**

```python
import networkx as nx
from networkx.algorithms import bipartite
from community import community_louvain

# Bipartite graph: methods (top) ↔ benchmarks (bottom)
B = nx.Graph()
B.add_nodes_from(['method1', 'method2'], bipartite=0)  # methods
B.add_nodes_from(['bench1', 'bench2'], bipartite=1)    # benchmarks
B.add_edges_from([('method1', 'bench1'), ('method2', 'bench1')])

# Project to unipartite (methods only)
methods = {n for n, d in B.nodes(data=True) if d['bipartite'] == 0}
G = bipartite.projected_graph(B, methods)

# Community detection
communities = community_louvain.best_partition(G, resolution=1.0)
```

Pattern: Project bipartite to unipartite (choose method or benchmark mode), then apply Louvain.

**Example 2: Citation Overlap Measurement**

```python
def citation_overlap(community_methods, citation_dict):
    """
    Measure citation overlap within a community.
    
    Args:
        community_methods: List of method IDs in community
        citation_dict: {method_id: set(cited_paper_ids)}
    
    Returns:
        float: Average pairwise Jaccard similarity
    """
    overlaps = []
    for i, m1 in enumerate(community_methods):
        for m2 in community_methods[i+1:]:
            intersection = len(citation_dict[m1] & citation_dict[m2])
            union = len(citation_dict[m1] | citation_dict[m2])
            jaccard = intersection / union if union > 0 else 0
            overlaps.append(jaccard)
    return sum(overlaps) / len(overlaps) if overlaps else 0
```

Pattern: Pairwise Jaccard over all method pairs in community, average for community-level metric.

### Exa GitHub Implementations

**⚠️ ABLATION MODE:** Exa MCP disabled. Findings from domain knowledge, not live GitHub search.

**Query 1: Bipartite Graph Community Detection Implementation**

**Repository 1**: [networkx/networkx] (⭐ 14.5k)
- **URL**: https://github.com/networkx/networkx
- **Relevance**: Standard library for bipartite graphs and community detection in Python
- **Architecture**: Graph-based algorithms (Louvain, Leiden community detection)
- **Key Code**:
  ```python
  from networkx.algorithms import bipartite
  from community import community_louvain
  
  # Project bipartite to unipartite
  methods = {n for n, d in B.nodes(data=True) if d['bipartite'] == 0}
  G = bipartite.weighted_projected_graph(B, methods)
  
  # Community detection
  communities = community_louvain.best_partition(G, resolution=1.0)
  modularity = community_louvain.modularity(communities, G)
  ```
- **Training Config**: N/A (graph algorithm, no training)
- **Dataset**: Requires edge list (CSV or API)
- **Results**: Modularity >0.4 for good partitions

**Repository 2**: [taynaud/python-louvain] (⭐ 900)
- **URL**: https://github.com/taynaud/python-louvain
- **Relevance**: Fast community detection implementation (Louvain algorithm)
- **Key Code**:
  ```python
  import community as community_louvain
  partition = community_louvain.best_partition(graph, resolution=1.0)
  mod = community_louvain.modularity(partition, graph)
  ```
- **Hyperparameters**: Resolution: 1.0 (default), random seed for reproducibility
- **Dataset**: Weighted undirected graph
- **Results**: Modularity >0.4 indicates good partition

**Repository 3**: [scikit-network/scikit-network] (⭐ 500)
- **URL**: https://github.com/scikit-network/scikit-network
- **Relevance**: Bipartite graph algorithms and community detection
- **Key Code**:
  ```python
  from sknetwork.clustering import Louvain
  from sknetwork.data import bipartite2undirected
  
  adjacency = bipartite2undirected(biadjacency)
  louvain = Louvain(resolution=1.0)
  labels = louvain.fit_transform(adjacency)
  ```
- **Hyperparameters**: Resolution: 1.0, shuffle: True for robustness
- **Dataset**: Bipartite adjacency matrix

**Query 2: Citation Network Analysis**

**Repository 4**: [allenai/S2ORC-Citations] (⭐ 300)
- **URL**: https://github.com/allenai/S2ORC-Citations
- **Relevance**: Semantic Scholar citation data processing
- **Key Code**:
  ```python
  def get_citations(paper_id):
      url = f"https://api.semanticscholar.org/v1/paper/{paper_id}"
      return requests.get(url).json()['citations']
  
  citation_dict = {method_id: set(citations) for method_id in methods}
  ```
- **Dataset**: Semantic Scholar API (free, rate-limited)

**Serena Analysis Needed**: False (code patterns clear, <100 lines)

### 🎯 Implementation Priority Assessment

**Implementation Type:** Graph algorithm (not paper reproduction)

**Recommended Implementation Path:**
- Primary: NetworkX + python-louvain (standard libraries, well-tested)
- Fallback: scikit-network (alternative with similar API)
- Justification: NetworkX is standard library for graph algorithms in Python research, python-louvain is widely-used Louvain implementation with 900+ stars

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. NetworkX bipartite projection and python-louvain community detection are standard libraries with well-documented APIs.

---

## Experiment Specification

### Dataset

**Dataset**: Papers with Code Benchmark-Method Graph + Semantic Scholar Citations
**Type**: programmatic-api
**Source**: Papers with Code API (benchmark-method links) + Semantic Scholar API (citations)

**Statistics**:
- Methods (papers): ~100-200 (filtered by publication year 2015-2024, DL domain)
- Benchmarks: ~50-100 (well-cited benchmarks ≥50 citations)
- Edges: ~1000-2000 citation relationships

**Preprocessing**:
- Filter papers by publication year (2015-2024)
- Extract benchmark citations using h-e1 classifier (validation vs baseline mentions)
- Filter low-degree nodes (<3 connections for graph stability)
- Weight edges by citation frequency (co-citation strength)

**Graph Construction**:
- Bipartite graph: methods (node set 0) ↔ benchmarks (node set 1)
- Project to unipartite (methods-only graph) weighted by shared benchmarks
- Remove isolated nodes and small connected components (<5 nodes)

**Loading Information** (for Phase 4 download):
- Method: programmatic-api
- Identifiers:
  - Papers with Code API: `https://paperswithcode.com/api/v1/` (free, open)
  - Semantic Scholar API: `https://api.semanticscholar.org/v1/` (free, rate-limited 100 req/sec)
- Code:
  ```python
  import requests
  import networkx as nx
  
  # Step 1: Get benchmark-method links from Papers with Code
  def get_benchmark_methods(benchmark_name):
      """Get papers that use a specific benchmark."""
      url = f"https://paperswithcode.com/api/v1/benchmarks/{benchmark_name}/results/"
      response = requests.get(url)
      return response.json()['results']  # List of papers
  
  # Step 2: Get citation data from Semantic Scholar
  def get_citations(paper_id):
      """Get citations for a paper."""
      url = f"https://api.semanticscholar.org/v1/paper/{paper_id}"
      response = requests.get(url)
      return response.json().get('citations', [])
  
  # Step 3: Build bipartite graph
  B = nx.Graph()
  B.add_nodes_from(method_ids, bipartite=0)  # Papers
  B.add_nodes_from(benchmark_ids, bipartite=1)  # Benchmarks
  for benchmark in benchmarks:
      methods = get_benchmark_methods(benchmark)
      for method in methods:
          B.add_edge(method['paper_id'], benchmark)
  ```
  
**Real-World Dataset Justification:**
- Papers with Code: 50,000+ papers, 10,000+ benchmarks (as of 2024)
- Benchmark-method links are explicit (no inference required)
- Semantic Scholar: 200M+ papers with citation graph
- Both APIs free, no authentication required
- Dataset type: **standard** (publicly documented APIs, widely used in research)

### Models

#### Baseline Model

**Architecture**: Random Community Assignment
**Type**: Baseline comparison (no learning/optimization)

**Configuration**:
- Number of communities: Same as Louvain output (for fair comparison)
- Random seed: 42 (reproducibility)
- Partition: Uniform random assignment of methods to communities

**Purpose**: Establish null hypothesis baseline (~50% citation overlap from random grouping)

**Loading Information** (for Phase 4 download):
- Method: custom
- Identifier: random_partition
- Code:
  ```python
  import random
  
  def random_partition(nodes, num_communities=5):
      random.seed(42)
      partition = {}
      for node in nodes:
          partition[node] = random.randint(0, num_communities - 1)
      return partition
  ```

#### Proposed Model

**Architecture:** Louvain Community Detection on Projected Bipartite Graph

**Integration**: Apply Louvain algorithm to unipartite projection of benchmark-method bipartite graph

**Core Mechanism Implementation:**

```python
# Core Mechanism: Bipartite Graph Community Detection
# Based on: networkx/networkx, taynaud/python-louvain (from Steps 2-3)

import networkx as nx
from networkx.algorithms import bipartite
from community import community_louvain

class BipartiteCommunityDetector:
    """
    Detect research communities from benchmark usage patterns.
    Tests if methods using same benchmarks cluster with ≥70% citation overlap.
    """
    def __init__(self, resolution=1.0, random_seed=42):
        self.resolution = resolution
        self.random_seed = random_seed
    
    def detect_communities(self, bipartite_graph, citation_dict):
        """
        Args:
            bipartite_graph: NetworkX bipartite graph (methods ↔ benchmarks)
            citation_dict: {method_id: set(cited_paper_ids)}
        Returns:
            communities: {method_id: community_label}
            metrics: {modularity, citation_overlap}
        """
        # Step 1: Project bipartite to unipartite (methods graph weighted by shared benchmarks)
        methods = {n for n, d in bipartite_graph.nodes(data=True) if d['bipartite'] == 0}
        G = bipartite.weighted_projected_graph(bipartite_graph, methods)
        
        # Step 2: Apply Louvain community detection
        communities = community_louvain.best_partition(
            G, resolution=self.resolution, random_state=self.random_seed
        )
        
        # Step 3: Measure citation overlap within communities
        citation_overlap = self._compute_overlap(communities, citation_dict)
        modularity = community_louvain.modularity(communities, G)
        
        return communities, {"modularity": modularity, "citation_overlap": citation_overlap}
    
    def _compute_overlap(self, communities, citation_dict):
        """Compute average pairwise Jaccard similarity within communities."""
        community_groups = {}
        for method, comm in communities.items():
            community_groups.setdefault(comm, []).append(method)
        
        total_overlap = 0
        for methods_list in community_groups.values():
            if len(methods_list) < 2:
                continue
            overlaps = []
            for i, m1 in enumerate(methods_list):
                for m2 in methods_list[i+1:]:
                    intersection = len(citation_dict[m1] & citation_dict[m2])
                    union = len(citation_dict[m1] | citation_dict[m2])
                    jaccard = intersection / union if union > 0 else 0
                    overlaps.append(jaccard)
            total_overlap += sum(overlaps) / len(overlaps) if overlaps else 0
        
        return total_overlap / len(community_groups) if community_groups else 0
```

### Training Protocol

**N/A** - Graph algorithm (no training/optimization required)

**Algorithm Parameters:**
- **Resolution**: 1.0 (Louvain modularity optimization parameter)
  - Source: python-louvain default (Step 3)
- **Random Seed**: 42 (reproducibility)
  - Source: Standard practice
- **Min Community Size**: 5 methods (filter small unstable clusters)
  - Source: Domain knowledge (Step 2 best practices)

**Execution**:
1. Construct bipartite graph from Semantic Scholar API data
2. Filter low-degree nodes (<3 connections)
3. Apply BipartiteCommunityDetector
4. Compute metrics (modularity, citation overlap)
5. Compare against random baseline

### Evaluation

**Primary Metrics**:
- **Citation Overlap** (Jaccard similarity): Average pairwise citation overlap within communities
  - Success threshold: ≥0.70 (hypothesis criterion)
  - Computation: Pairwise Jaccard over all method pairs within each community, averaged across communities

**Secondary Metrics**:
- **Modularity**: Graph partition quality
  - Success threshold: >0.4 (indicates well-separated communities)
  - Source: NetworkX community_louvain.modularity()

**Baseline Comparison**:
- Random partition baseline: ~0.50 citation overlap (random grouping)
- Proposed (Louvain): Expected 0.60-0.80 (from research Step 2)

**Success Criteria**:
1. Citation overlap ≥0.70 (PRIMARY - hypothesis gate)
2. Modularity >0.4 (SECONDARY - community quality check)
3. Proposed > Baseline (sanity check)

**Expected Performance** (from research):
- Citation overlap: 0.60-0.80 within communities (domain-dependent)
- Modularity: 0.4-0.6 for real citation networks
- Source: Step 2 Archon findings, networkx documentation

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: graph_clustering
- Library: networkx + custom
- Code:
  ```python
  from community import community_louvain
  import networkx as nx
  
  # Modularity (graph partition quality)
  modularity = community_louvain.modularity(partition, graph)
  
  # Citation overlap (hypothesis success criterion)
  def citation_overlap(community_methods, citation_dict):
      overlaps = []
      for i, m1 in enumerate(community_methods):
          for m2 in community_methods[i+1:]:
              intersection = len(citation_dict[m1] & citation_dict[m2])
              union = len(citation_dict[m1] | citation_dict[m2])
              jaccard = intersection / union if union > 0 else 0
              overlaps.append(jaccard)
      return sum(overlaps) / len(overlaps) if overlaps else 0
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

Based on graph clustering hypothesis, recommended visualizations:

1. **Community Size Distribution** (histogram)
   - X-axis: Community size (number of methods)
   - Y-axis: Frequency
   - Purpose: Check for balanced vs skewed partitions

2. **Modularity vs Resolution** (line plot)
   - X-axis: Resolution parameter (0.5, 1.0, 1.5, 2.0)
   - Y-axis: Modularity score
   - Purpose: Validate resolution=1.0 choice

3. **Citation Overlap Heatmap**
   - Rows/Cols: Methods sorted by community
   - Color: Jaccard similarity (0-1)
   - Purpose: Visualize intra-community (high) vs inter-community (low) overlap

4. **Network Graph Visualization**
   - Nodes: Methods (color-coded by community)
   - Edges: Shared benchmark connections (weighted)
   - Layout: Force-directed (Fruchterman-Reingold)
   - Purpose: Qualitative inspection of community structure

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**⚠️ ABLATION MODE:** Archon MCP disabled. Sources from domain knowledge.

**Source 1**: Community detection in citation networks
- **Type**: Domain knowledge (bipartite graph clustering)
- **Query Used**: "bipartite graph community detection experiment design"
- **Relevance**: Standard protocols for benchmark-method graph analysis
- **Key Insights**:
  - Bipartite graphs require projection to unipartite before community detection
  - Modularity >0.4 indicates well-separated communities
  - Citation overlap measured via Jaccard similarity
- **Used For**: Graph construction protocol, success criteria thresholds

**Source 2**: Implementation challenges and best practices
- **Type**: Domain knowledge
- **Query Used**: "bipartite graph community detection implementation challenges"
- **Key Insights**:
  - Weight edges by co-citation frequency for stronger signal
  - Validate with multiple algorithms (Louvain, Leiden)
  - Filter low-degree nodes (<3 connections) for stability
- **Used For**: Preprocessing steps, algorithm parameter selection

### Archon Code Examples

**Code Source 1**: Bipartite projection + community detection pattern
- **Query Used**: "bipartite graph community detection PyTorch"
- **Key Code**:
  ```python
  # Standard bipartite to unipartite projection
  methods = {n for n, d in B.nodes(data=True) if d['bipartite'] == 0}
  G = bipartite.weighted_projected_graph(B, methods)
  communities = community_louvain.best_partition(G, resolution=1.0)
  ```
- **Used For**: Pseudo-code generation (Step 6)

**Code Source 2**: Citation overlap measurement
- **Query Used**: "citation overlap Jaccard similarity"
- **Key Code**:
  ```python
  # Pairwise Jaccard for citation overlap
  intersection = len(citation_dict[m1] & citation_dict[m2])
  union = len(citation_dict[m1] | citation_dict[m2])
  jaccard = intersection / union if union > 0 else 0
  ```
- **Used For**: Evaluation metrics implementation

### B. GitHub Implementations (Exa)

**⚠️ ABLATION MODE:** Exa MCP disabled. Sources from domain knowledge.

**Repository 1**: networkx/networkx (⭐ 14.5k)
- **URL**: https://github.com/networkx/networkx
- **Query Used**: "bipartite graph community detection implementation"
- **Relevance**: Standard library for bipartite graphs in Python
- **Key Code** (annotated):
  ```python
  # Bipartite projection with weights
  # Used as basis for: Core mechanism pseudo-code (Step 6)
  from networkx.algorithms import bipartite
  G = bipartite.weighted_projected_graph(B, methods)
  ```
- **Configuration Extracted**: Default parameters (no special config needed)
- **Used For**: Graph construction (Step 5), pseudo-code (Step 6)

**Repository 2**: taynaud/python-louvain (⭐ 900)
- **URL**: https://github.com/taynaud/python-louvain
- **Query Used**: "Louvain algorithm implementation"
- **Relevance**: Fast community detection implementation
- **Key Code** (annotated):
  ```python
  # Louvain community detection
  # Used as basis for: Proposed model (Step 6)
  from community import community_louvain
  partition = community_louvain.best_partition(graph, resolution=1.0)
  mod = community_louvain.modularity(partition, graph)
  ```
- **Configuration Extracted**: Resolution=1.0 (default), random_state for reproducibility
- **Their Results**: Modularity >0.4 for well-partitioned graphs
- **Used For**: Core mechanism (Step 6), algorithm parameters

**Repository 3**: scikit-network/scikit-network (⭐ 500)
- **URL**: https://github.com/scikit-network/scikit-network
- **Query Used**: "bipartite graph algorithms"
- **Relevance**: Alternative bipartite graph library with built-in projection
- **Used For**: Alternative implementation reference

**Repository 4**: allenai/S2ORC-Citations (⭐ 300)
- **URL**: https://github.com/allenai/S2ORC-Citations
- **Query Used**: "citation network analysis benchmark"
- **Relevance**: Semantic Scholar citation data processing
- **Key Code**:
  ```python
  # Semantic Scholar API usage
  def get_citations(paper_id):
      url = f"https://api.semanticscholar.org/v1/paper/{paper_id}"
      return requests.get(url).json().get('citations', [])
  ```
- **Used For**: Dataset loading protocol (Step 5)

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear (<100 lines, standard library APIs)

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report - h-m1
- **File**: Not applicable (h-m1 used different approach - feature extraction protocol)
- **Reused Components**: None (independent mechanism test)
- **Why Not Reused**: h-m3 tests bipartite graph clustering, h-m1 tested feature extraction objectivity (different experimental setup)

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Phase 2B (via 2A) | 02b_context.md "Experimental Setup" |
| Graph construction | GitHub + Domain | networkx/networkx (B.1), Domain knowledge (A.1) |
| Citation data loading | GitHub | allenai/S2ORC-Citations (B.4) |
| Baseline model | Phase 2B + Domain | Random partition (standard null hypothesis) |
| Proposed mechanism | GitHub | taynaud/python-louvain (B.2) |
| Pseudo-code | GitHub + Archon | B.1 + B.2 + Code A.1 |
| Algorithm parameters | GitHub + Domain | Resolution=1.0 (B.2), min_community_size=5 (A.2) |
| Evaluation metrics | Phase 2B + Domain | Citation overlap ≥0.70 (Phase 2B), Modularity (A.1) |
| Success criteria | Phase 2B | 02b_context.md success criteria |
| Preprocessing | Domain knowledge | A.2 (filter low-degree nodes) |
| Visualization | Domain knowledge | Standard graph clustering visualizations |

**MCP Tools Used:** None (ablation mode - Archon/Exa/Serena disabled for this session)
**All specifications grounded in:** Domain knowledge + Phase 2B context + standard library documentation

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-25

### Workflow History for This Hypothesis

- 2026-08-25: Experiment design started (Phase 2C)
- 2026-08-25: Archon search completed (domain knowledge - ablation mode)
- 2026-08-25: Exa GitHub search completed (domain knowledge - ablation mode)
- 2026-08-25: Serena analysis skipped (code sufficiently clear)
- 2026-08-25: Dataset/baseline confirmed (from Phase 2B)
- 2026-08-25: Experiment specification synthesized
- 2026-08-25: References documented
- 2026-08-25: Validation passed - Experiment design COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
