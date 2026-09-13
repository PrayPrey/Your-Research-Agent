# Experiment Design: h-m3

**Date:** 2026-08-10
**Author:** Anonymous
**Hypothesis Statement:** Under implicit evaluation standards, if authors cite prior work, then they use same benchmarks as cited papers, because comparability requires shared evaluation.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing citation-benchmark correlation mechanism.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1, H-M1, H-M2 all PASSED)
**Gate Status:** SHOULD_WORK (failure = document limitation, proceed)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** MECHANISM
- **Prerequisites:** h-m2 (PASSED)

### Gate Condition
- Citing pairs have higher dataset overlap than random (p < 0.01)
- Effect size (Cohen's d) > 0.3

---

## Continuation Context

Building on H-M2 which showed high HHI predicts standard benchmark adoption (β=56.75, p<0.001). H-M3 tests the mechanism: do papers follow citations for benchmark choice?

### Previous Hypothesis Results (if applicable)
- H-M2: β(prior_HHI) = 56.75, p = 1.51e-11
- Standard adoption rate = 20%
- Effect persists with venue controls

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct matches for citation-benchmark overlap analysis. Found:
- OpenReview discussion on dataset similarity metrics (page_id: e5f89bb6)
- Paint-by-Example repo with benchmark comparisons

**Key insight:** No existing implementation for citation-to-benchmark correlation analysis in KB. This is novel analysis requiring custom implementation.

### Archon Code Examples

Found BibTeX/citation formatting examples but no citation network analysis code. Need to implement from scratch using:
- Semantic Scholar API for citation data
- PWC data (from H-E1 cache) for benchmark tags
- Standard Jaccard similarity computation

### Exa GitHub Implementations

**Highly relevant findings:**

1. **semantic-scholar-skills** (github.com/zongmin-yu/semantic-scholar-skills)
   - Python library for S2 API with citation analysis
   - `/trace-citations` workflow maps citation neighborhoods
   - MIT license, 20 stars

2. **paper_network_builder** (github.com/hsianktin/paper_network_builder)
   - Builds citation networks from Semantic Scholar API
   - Uses NetworkX for graph operations
   - Exports to GEXF for analysis

3. **citation-compass** (github.com/dagny099/citation-compass)
   - Neo4j-based citation network analysis
   - Community detection and centrality metrics
   - TransE embeddings for citation prediction

4. **unpacd** (github.com/lukaszbrzozowski/unpacd)
   - Unified interface for citation networks (Cora, CiteSeer, DBLP, ogbn-arxiv)
   - Pre-computed degree tensors, lazy loading
   - Good for benchmarking community detection

5. **AAbasinejad/Network_Analysis**
   - DBLP citation network with Jaccard similarity
   - Direct implementation of `jaccard_similarity(lst1, lst2)` between publication sets

### 🎯 Implementation Priority Assessment

**CRITICAL: This is statistical analysis, not paper reproduction. Use standard APIs and libraries.**

**Analysis type:** Citation network + benchmark overlap correlation (novel analysis)

**Recommended Implementation Path:**
- Primary: Semantic Scholar API + PWC cache + scipy.stats
- Fallback: OpenAlex API if S2 rate-limited
- Justification: S2 provides citation data; PWC already cached from H-E1; scipy has Mann-Whitney U and permutation tests

### Code Analysis (Serena MCP)

*Skipped* - No existing codebase to analyze. This is new statistical analysis code.

---

## Experiment Specification

### Dataset

**Primary Dataset: Combined PWC + Semantic Scholar Citation Data**

| Component | Specification |
|-----------|---------------|
| **Name** | PWC-S2-Citations-NeurIPS-ICML-ICLR-2018-2024 |
| **Type** | programmatic-api (real data via API) |
| **Source 1** | PWC cache from H-E1 (HuggingFace `pwc-archive/papers-with-abstracts`) |
| **Source 2** | Semantic Scholar API (citations endpoint) |
| **Scope** | NeurIPS, ICML, ICLR papers 2018-2024 |
| **Expected Size** | ~12,000 papers, ~50,000+ citation pairs |
| **Split** | Full dataset (no train/val/test - statistical analysis) |

**Data Fields Required:**
- Paper ID (S2 corpus ID)
- Venue, Year
- Dataset tags (from PWC)
- Citing papers list (from S2)
- Cited papers list (from S2)

**Loading Information** (for Phase 4 download):
- Method: API + Cache
- Identifier: PWC cache + S2 API key
- Code:
```python
from datasets import load_dataset
import requests

pwc_cache = load_dataset("pwc-archive/papers-with-abstracts")

S2_API_KEY = os.environ.get("S2_API_KEY")
S2_BASE = "https://api.semanticscholar.org/graph/v1"

def get_citations(paper_id):
    url = f"{S2_BASE}/paper/{paper_id}/citations"
    headers = {"x-api-key": S2_API_KEY}
    return requests.get(url, headers=headers, params={"fields": "paperId,title"}).json()
```

### Models

#### Baseline Model

**Type:** Random Pair Comparison (Null Hypothesis)

For each venue-year, sample random paper pairs (not citation-linked) and compute their dataset overlap. This establishes the expected overlap under no citation relationship.

| Parameter | Value |
|-----------|-------|
| Sampling | Random pairs within venue-year |
| N per venue-year | Match citation pair count |
| Overlap metric | Jaccard similarity of dataset tags |

**Loading Information** (for Phase 4 download):
- Method: N/A (statistical baseline)
- Identifier: N/A
- Code:
```python
import random

def sample_random_pairs(papers, n_pairs):
    pairs = []
    paper_list = list(papers)
    for _ in range(n_pairs):
        p1, p2 = random.sample(paper_list, 2)
        pairs.append((p1, p2))
    return pairs
```

#### Proposed Model

**Architecture:** Citation-Linked Pair Analysis

For each citing-cited pair within venue scope, compute Jaccard similarity of their dataset tags. Compare distribution to random baseline.

**Core Mechanism Implementation:**

```python
def jaccard_similarity(set1: set, set2: set) -> float:
    if not set1 and not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0

def compute_citation_dataset_overlap(papers_df, citations_df):
    citing_overlaps = []
    random_overlaps = []
    
    for venue_year in papers_df['venue_year'].unique():
        vy_papers = papers_df[papers_df['venue_year'] == venue_year]
        vy_citations = citations_df[
            (citations_df['citing_id'].isin(vy_papers['paper_id'])) &
            (citations_df['cited_id'].isin(vy_papers['paper_id']))
        ]
        
        for _, row in vy_citations.iterrows():
            citing_datasets = set(vy_papers.loc[row['citing_id'], 'datasets'])
            cited_datasets = set(vy_papers.loc[row['cited_id'], 'datasets'])
            citing_overlaps.append(jaccard_similarity(citing_datasets, cited_datasets))
        
        n_citation_pairs = len(vy_citations)
        random_pairs = sample_random_pairs(vy_papers['paper_id'], n_citation_pairs)
        for p1, p2 in random_pairs:
            d1 = set(vy_papers.loc[p1, 'datasets'])
            d2 = set(vy_papers.loc[p2, 'datasets'])
            random_overlaps.append(jaccard_similarity(d1, d2))
    
    return citing_overlaps, random_overlaps

def run_statistical_test(citing_overlaps, random_overlaps):
    from scipy import stats
    
    stat, p_value = stats.mannwhitneyu(
        citing_overlaps, random_overlaps, 
        alternative='greater'
    )
    
    mean_citing = np.mean(citing_overlaps)
    mean_random = np.mean(random_overlaps)
    pooled_std = np.sqrt((np.var(citing_overlaps) + np.var(random_overlaps)) / 2)
    cohens_d = (mean_citing - mean_random) / pooled_std if pooled_std > 0 else 0
    
    return {
        'mann_whitney_stat': stat,
        'p_value': p_value,
        'mean_citing_overlap': mean_citing,
        'mean_random_overlap': mean_random,
        'cohens_d': cohens_d,
        'n_citing_pairs': len(citing_overlaps),
        'n_random_pairs': len(random_overlaps)
    }
```

### Training Protocol

**N/A** - This is statistical analysis, not model training.

| Step | Description |
|------|-------------|
| 1 | Load PWC cache (papers + dataset tags) |
| 2 | Filter to NeurIPS/ICML/ICLR 2018-2024 |
| 3 | Query S2 API for intra-venue citations |
| 4 | Build citation pairs within venue-years |
| 5 | Compute Jaccard overlap for citing pairs |
| 6 | Sample matched random pairs |
| 7 | Compute Jaccard overlap for random pairs |
| 8 | Run Mann-Whitney U test |
| 9 | Compute Cohen's d effect size |

### Evaluation

| Metric | Threshold | Description |
|--------|-----------|-------------|
| Mann-Whitney U p-value | < 0.01 | Citing pairs > random pairs (primary gate) |
| Cohen's d | > 0.3 | Medium effect size (secondary gate) |
| Mean overlap (citing) | Report | Average Jaccard for citation-linked pairs |
| Mean overlap (random) | Report | Average Jaccard for random pairs |
| N citing pairs | ≥ 1000 | Sufficient sample size |

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical-hypothesis-test
- Library: scipy.stats, numpy
- Code:
```python
from scipy.stats import mannwhitneyu
import numpy as np

def evaluate_gate(citing_overlaps, random_overlaps):
    stat, p = mannwhitneyu(citing_overlaps, random_overlaps, alternative='greater')
    
    mean_c, mean_r = np.mean(citing_overlaps), np.mean(random_overlaps)
    pooled_std = np.sqrt((np.var(citing_overlaps) + np.var(random_overlaps)) / 2)
    d = (mean_c - mean_r) / pooled_std if pooled_std > 0 else 0
    
    gate_passed = (p < 0.01) and (d > 0.3)
    return gate_passed, {'p': p, 'd': d, 'mean_citing': mean_c, 'mean_random': mean_r}
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing mean Jaccard overlap for citing vs random pairs with error bars and p-value annotation

#### Additional Figures (LLM Autonomous)

1. **Overlap Distribution Histogram**: Side-by-side histograms of Jaccard scores for citing vs random pairs
2. **Venue-Year Breakdown**: Heatmap of effect sizes per venue-year
3. **Citation Depth Analysis**: Overlap by citation distance (direct cite vs 2-hop)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Citing pairs dataset overlap > random pairs overlap (p < 0.01)
3. Cohen's d > 0.3 (medium effect)

**Gate Type:** SHOULD_WORK
- If PASS: H-M3 confirms citation drives benchmark homogeneity
- If FAIL: Document as limitation, proceed to H-M4

---

## Appendix: Reference Implementations

### A1. Jaccard Similarity (from AAbasinejad/Network_Analysis)
```python
def jaccard_similarity(lst1, lst2):
    s1, s2 = set(lst1), set(lst2)
    return len(s1 & s2) / len(s1 | s2) if (s1 | s2) else 0
```

### A2. Semantic Scholar API Citation Fetch
```python
import requests

def get_paper_citations(paper_id, api_key, limit=100):
    url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations"
    headers = {"x-api-key": api_key}
    params = {"fields": "paperId,title,year,venue", "limit": limit}
    resp = requests.get(url, headers=headers, params=params)
    return resp.json().get("data", [])
```

### A3. PWC Dataset Tag Extraction (from H-E1)
```python
from datasets import load_dataset

def load_pwc_papers():
    ds = load_dataset("pwc-archive/papers-with-abstracts", split="train")
    return ds.to_pandas()
```

### A4. Mann-Whitney U Test with Effect Size
```python
from scipy.stats import mannwhitneyu
import numpy as np

def compare_distributions(group1, group2):
    stat, p = mannwhitneyu(group1, group2, alternative='greater')
    d = (np.mean(group1) - np.mean(group2)) / np.sqrt((np.var(group1) + np.var(group2)) / 2)
    return {'U': stat, 'p': p, 'cohens_d': d}
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-10

### Workflow History for This Hypothesis
- 2026-08-10: h-m3 set to IN_PROGRESS (Phase 2C start)
- 2026-08-10: MCP research completed (Archon + Exa)
- 2026-08-10: Experiment specification synthesized

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
