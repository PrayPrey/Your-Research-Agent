# Experiment Design: h-m3

**Date:** 2026-03-27
**Author:** Anonymous
**Hypothesis Statement:** Under the differentiated clusters, if shape descriptors are correctly calibrated, then >=3 of 5 proposed archetypes (Sustained Growth, Flash-in-the-Pan, Plateau, Slow Burn, Revival) will be recovered as distinct clusters with >70% feature alignment to archetype definitions, because the proposed taxonomy captures real-world adoption patterns.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM Hypothesis** - Tests whether empirical clusters map to theoretical archetypes.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** Yes (h-m2 PASSED - shape descriptors differentiate clusters)
**Gate Status:** SHOULD_WORK (failure = documented limitation, continue)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** MECHANISM
- **Prerequisites:** h-m2 (Shape differentiation - PASSED)

### Gate Condition
**Gate Type:** SHOULD_WORK
- If PASS: Proceed to Phase 5 (Baseline Comparison) or Phase 6 (Paper Writing)
- If FAIL: Document limitation as partial taxonomy recovery, continue

---

## Continuation Context

This is a continuation experiment building on h-e1 (clustering), h-m1 (changepoint detection), and h-m2 (shape differentiation).

### Previous Hypothesis Results

**h-e1 Results (DTW Clustering):**
- Silhouette Score: 0.289 (> 0.25 threshold)
- Optimal k: 4 clusters
- Jaccard Stability: 0.991 (> 0.65 threshold)
- 500 datasets analyzed

**h-m1 Results (PELT Changepoint Detection):**
- Detection Rate: 81% (> 50% threshold)
- Mean Changepoints: 0.96 per series
- 405/500 series have at least one changepoint

**h-m2 Results (Shape Descriptor Differentiation):**
- 3/4 descriptors exceed variance ratio threshold (>2.0)
- Passing descriptors: growth_ratio (4.74), changepoint_count (11.08), derivative_variance (2.16)
- Cluster profiles are distinct (min pairwise distance = 0.317)

**Proven Components to Reuse:**
- HuggingFace dataset cache (h-e1/code/dataset_cache.json)
- Cluster assignments (k=4) and centroids
- Shape descriptors from h-m2

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Archetype Trajectory Classification**
- Limited direct matches in Archon KB (focused on other ML domains)
- Key insight: Archetype matching is a novel contribution requiring custom implementation

**Query 2: Cluster Labeling Feature Alignment**
- No direct matches for cluster-to-archetype alignment methodology
- Confirms novelty of the research approach

**Note:** Archon KB does not contain archetype recovery cases. Research grounded in Exa findings and prior hypothesis results.

### Archon Code Examples

No directly applicable code examples found in Archon KB for archetype matching. Implementation derived from Exa GitHub findings and validated h-m2 components.

### Exa GitHub Implementations

**Repository 1**: tslearn-team/tslearn
- **URL**: https://github.com/tslearn-team/tslearn
- **Relevance**: Foundation library for time series clustering (validated in h-e1)
- **Key Code**:
  ```python
  from tslearn.clustering import TimeSeriesKMeans
  model = TimeSeriesKMeans(n_clusters=k, metric="dtw")
  cluster_centers = model.cluster_centers_  # Shape: (k, T, 1)
  ```
- **Used For**: Cluster centroids as input to archetype matching

**Repository 2**: scikit-learn NearestCentroid
- **URL**: https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.NearestCentroid.html
- **Relevance**: Centroid-based classification pattern
- **Key Code**:
  ```python
  from sklearn.neighbors import NearestCentroid
  clf = NearestCentroid(metric="euclidean")
  ```
- **Used For**: Inspiration for archetype-centroid matching logic

**Repository 3**: SciPy cosine similarity
- **URL**: https://docs.scipy.org/doc/scipy/reference/spatial.distance.cosine.html
- **Relevance**: Distance metric for profile alignment
- **Key Code**:
  ```python
  from scipy.spatial.distance import cosine
  alignment = 1 - cosine(profile_a, profile_b)  # 0-1 similarity
  ```
- **Used For**: Computing alignment scores

**Serena Analysis Needed**: false

### 🎯 Implementation Priority Assessment

**CRITICAL: For archetype matching, use custom implementation based on validated shape descriptors**

**Recommended Implementation Path:**
- Primary: scipy cosine similarity + numpy for alignment computation
- Fallback: sklearn NearestCentroid if cosine proves insufficient
- Justification: Simple, interpretable, builds on validated h-m2 descriptors

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. Building on validated h-e1/h-m2 components.

---

## Experiment Specification

### Dataset

**Dataset**: HuggingFace Dataset Download Statistics (reused from h-e1/h-m1/h-m2)
**Type**: custom (programmatic-api)

**Loading Information**:
- Method: Reuse cached data from h-e1
- Identifier: h-e1/code/dataset_cache.json
- Code:
  ```python
  import json
  # Load cached HuggingFace download statistics
  with open("../h-e1/code/dataset_cache.json", "r") as f:
      data = json.load(f)
  # Alternatively from h-m1:
  # with open("../h-m1/code/hf_dataset_cache.json", "r") as f:
  #     data = json.load(f)
  ```

**Statistics**:
- Total datasets: 500
- Time series length: Variable (normalized to 300 points)
- Clusters: k=4 (from h-e1)

**Preprocessing**:
- Already preprocessed in h-e1: log-transform, z-score normalization
- Reuse cluster assignments and centroids
- Load shape descriptors from h-m2

**Augmentation**: None (analysis task, not training)

### Models

#### Baseline Model

**Architecture**: Random Archetype Assignment
**Configuration**: Randomly assign each cluster (k=4) to one of 5 archetypes

**Loading Information**:
- Method: Custom implementation
- Identifier: N/A
- Code:
  ```python
  import numpy as np
  np.random.seed(42)
  # Random baseline: assign each cluster to random archetype
  random_assignments = np.random.choice(5, size=4, replace=False)
  # Expected alignment: ~20% by chance
  ```

#### Proposed Model

**Architecture**: Shape Descriptor Alignment Matching

**Core Mechanism Implementation:**

```python
# Core Mechanism: Archetype Recovery via Shape Descriptor Alignment
# Based on: h-m2 validated shape descriptors + cosine similarity matching

import numpy as np
from scipy.spatial.distance import cosine

class ArchetypeRecoveryMatcher:
    """
    Map empirical cluster centroids to theoretical archetypes
    using shape descriptor alignment (>70% threshold).
    """
    def __init__(self, alignment_threshold=0.70):
        self.threshold = alignment_threshold
        # A priori archetype definitions (normalized shape descriptor profiles)
        self.archetypes = {
            "sustained_growth": {"growth_ratio": 0.8, "peak_timing": 0.9, "changepoint_count": 0.2, "derivative_variance": 0.2},
            "flash_in_pan":     {"growth_ratio": 0.3, "peak_timing": 0.2, "changepoint_count": 0.8, "derivative_variance": 0.8},
            "plateau":          {"growth_ratio": 0.5, "peak_timing": 0.5, "changepoint_count": 0.2, "derivative_variance": 0.1},
            "slow_burn":        {"growth_ratio": 0.7, "peak_timing": 0.8, "changepoint_count": 0.1, "derivative_variance": 0.2},
            "revival":          {"growth_ratio": 0.4, "peak_timing": 0.6, "changepoint_count": 0.6, "derivative_variance": 0.5}
        }

    def normalize_profile(self, profile):
        """Normalize descriptor values to 0-1 range for comparison."""
        # Use min-max normalization based on observed ranges from h-m2
        ranges = {"growth_ratio": (0.3, 0.6), "peak_timing": (0, 0.03),
                  "changepoint_count": (0, 5), "derivative_variance": (0.1, 0.4)}
        normalized = {}
        for k, v in profile.items():
            min_v, max_v = ranges.get(k, (0, 1))
            normalized[k] = (v - min_v) / (max_v - min_v) if max_v > min_v else 0.5
            normalized[k] = np.clip(normalized[k], 0, 1)
        return normalized

    def compute_alignment(self, cluster_profile, archetype_name):
        """Compute alignment score (0-1) between cluster and archetype."""
        archetype = self.archetypes[archetype_name]
        norm_profile = self.normalize_profile(cluster_profile)
        cluster_vec = np.array([norm_profile[k] for k in archetype.keys()])
        archetype_vec = np.array(list(archetype.values()))
        return 1 - cosine(cluster_vec, archetype_vec)

    def match_clusters(self, cluster_profiles):
        """Assign each cluster to best-matching archetype if alignment > threshold."""
        assignments, recovered = {}, set()
        for cluster_id, profile in cluster_profiles.items():
            best_arch, best_score = None, 0
            for arch_name in self.archetypes:
                score = self.compute_alignment(profile, arch_name)
                if score > best_score:
                    best_arch, best_score = arch_name, score
            if best_score >= self.threshold:
                assignments[cluster_id] = (best_arch, best_score)
                recovered.add(best_arch)
        return assignments, len(recovered)  # Returns (assignments, n_recovered)
```

### Training Protocol

**Note**: This is an analysis task, not a training task. No model training required.

**Computational Protocol**:
- **Step 1**: Load cluster centroids from h-e1 (k=4)
- **Step 2**: Compute or load shape descriptors from h-m2 results
- **Step 3**: Define 5 archetype profiles a priori (based on literature + h-m2 ranges)
- **Step 4**: Normalize cluster profiles to match archetype scale
- **Step 5**: Compute alignment scores between each centroid and each archetype
- **Step 6**: Assign clusters to archetypes with alignment > 70%
- **Step 7**: Count recovered archetypes

**Seeds**: 1 (fixed) - seed=42 for reproducibility
**Dependencies**: numpy >= 1.24, scipy >= 1.10

### Evaluation

**Primary Metrics**:
- **Archetype Recovery Rate**: Number of distinct archetypes matched with >70% alignment
- **Mean Alignment Score**: Average alignment across all valid matches
- **Uniqueness**: No archetype assigned to multiple clusters

**Success Criteria**:
- PRIMARY: >=3 of 5 archetypes recovered with alignment >0.70
- SECONDARY: Each recovered archetype maps to exactly one cluster (uniqueness)

**Metrics Loading Information**:
- Task Type: archetype_matching
- Library: scipy.spatial.distance, numpy
- Code:
  ```python
  from scipy.spatial.distance import cosine
  import numpy as np

  # Compute alignment matrix (4 clusters × 5 archetypes)
  alignment_matrix = np.zeros((4, 5))
  for i, cluster_profile in enumerate(cluster_profiles):
      for j, archetype in enumerate(archetypes):
          alignment_matrix[i, j] = 1 - cosine(cluster_vec, archetype_vec)

  # Count recovered archetypes (alignment > 0.70)
  n_recovered = len(set(np.argmax(alignment_matrix, axis=1)[np.max(alignment_matrix, axis=1) > 0.70]))
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual archetype recovery bar chart

#### Additional Figures (LLM Autonomous)
- Alignment score heatmap (clusters × archetypes)
- Radar chart comparing archetype profiles vs cluster profiles
- Cluster-archetype assignment diagram
- Descriptor space projection showing cluster-archetype distances

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m3/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | Shape descriptors available for all k=4 cluster centroids | TRUE |
| Mechanism Isolatable | Can compare archetype matching vs random assignment | TRUE |
| Baseline Measurable | Random baseline provides comparison point | TRUE |

### Architecture Compatibility Check

**Required Features:**
- Cluster centroids from h-e1 (TimeSeriesKMeans output)
- Shape descriptors from h-m2 (4 descriptors per centroid)
- A priori archetype definitions (5 archetypes × 4 descriptors)

**Incompatible Architectures:**
- None - pure Python analysis task using standard numpy/scipy

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "Archetype matching completed: {n} archetypes recovered" | archetype_matcher.py |
| Data Shape | alignment_matrix shape = (4, 5) | compute_alignment() |
| Metric Delta | n_recovered > 0 (at least 1 archetype matched) | evaluate.py |

**Activation Verification Code:**

```python
def verify_mechanism_activated(results):
    indicators = {
        "alignment_computed": results.get("alignment_matrix") is not None,
        "archetypes_defined": results.get("n_archetypes") == 5,
        "clusters_analyzed": results.get("n_clusters") == 4,
        "recovery_measured": results.get("n_recovered", -1) >= 0,
        "threshold_applied": results.get("alignment_threshold") == 0.70
    }
    return all(indicators.values()), indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| No alignment computed | alignment_matrix is None | FAIL: Mechanism not triggered |
| Zero recovery | n_recovered == 0 | FAIL: No archetypes matched |
| Low alignment | max(alignment) < 0.5 | WARN: Poor archetype definitions |
| Multiple assignment | Same archetype to multiple clusters | WARN: Archetypes not discriminative |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE | alignment_matrix computed |
| Effect Measurable | n_recovered > 0 | At least 1 archetype recovered |
| Hypothesis Supported | n_recovered >= 3 | >=3 of 5 archetypes with >70% alignment |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Alignment scores computed for all cluster-archetype pairs (4×5 matrix)
3. At least 1 archetype recovered with >70% alignment (shows mechanism works)
4. For full hypothesis support: recovery >= 3 archetypes

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Note**: Archon KB searches returned limited direct matches for archetype recovery methodology, reflecting the novelty of this research.

**Source A.1**: Time Series Clustering Resources
- **Type**: Knowledge base articles
- **Query Used**: "archetype trajectory classification time series clustering"
- **Used For**: Background context

### Archon Code Examples

No directly applicable code examples found. Implementation derived from Exa findings and validated prior hypothesis components.

### B. GitHub Implementations (Exa)

**Source B.1**: tslearn-team/tslearn
- **URL**: https://github.com/tslearn-team/tslearn
- **Query Used**: "time series trajectory archetype classification clustering Python tslearn"
- **Used For**: Cluster centroids as input

**Source B.2**: scikit-learn NearestCentroid
- **URL**: https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.NearestCentroid.html
- **Query Used**: "cluster centroid shape descriptor matching labeling Python sklearn"
- **Used For**: Matching pattern inspiration

**Source B.3**: SciPy cosine distance
- **URL**: https://docs.scipy.org/doc/scipy/reference/spatial.distance.cosine.html
- **Used For**: Alignment score computation

**Source B.4**: Software Lifecycle Literature
- **URLs**: Various (PkgPulse, library adoption studies)
- **Query Used**: "software package lifecycle trajectory adoption pattern"
- **Key Insight**: Real-world trajectory archetypes exist (hype → adoption → commoditization → decline)
- **Used For**: Grounding archetype definitions in literature

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Reports - h-e1, h-m1, h-m2
- **Files**: h-e1/04_validation.md, h-m1/04_validation.md, h-m2/04_validation.md
- **Reused Components**:
  - Dataset cache: HuggingFace download statistics (500 datasets)
  - Cluster assignments: k=4 from h-e1
  - Shape descriptors: 4 descriptors from h-m2
  - Descriptor ranges: Used to calibrate archetype profiles
- **Why Reused**: Enables controlled experiment - only archetype matching is new

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset | Previous | h-e1/code/dataset_cache.json |
| Cluster centroids | Previous | h-e1 TimeSeriesKMeans (k=4) |
| Shape descriptors | Previous | h-m2 validated descriptors |
| Alignment metric | Exa | scipy.spatial.distance.cosine |
| Archetype definitions | Synthesis | Literature + h-m2 descriptor ranges |
| Success threshold (70%) | Phase 2B | 02b_verification_plan.md |
| Recovery target (>=3/5) | Phase 2B | 02b_verification_plan.md |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-27T13:25:00Z

### Workflow History for This Hypothesis
- h-m3 set to IN_PROGRESS (hypothesis loop)
- Phase 2C experiment design started
- Phase 2C experiment design completed

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
