# Product Requirements Document: h-m3

**Hypothesis:** Archetype Recovery via Shape Descriptor Alignment
**Date:** 2026-03-27
**Author:** Anonymous
**Version:** 1.0
**Status:** Draft

---

## Executive Summary

This PRD defines the requirements for implementing hypothesis h-m3: validating that empirical clusters can be mapped to theoretical archetypes (Sustained Growth, Flash-in-the-Pan, Plateau, Slow Burn, Revival) using shape descriptor alignment. This is a MECHANISM hypothesis with a SHOULD_WORK gate that determines whether our proposed lifecycle taxonomy captures real-world HuggingFace dataset adoption patterns.

**Key Objective:** Demonstrate that >=3 of 5 proposed archetypes are recovered as distinct clusters with >70% feature alignment to archetype definitions.

---

## Problem Statement

### Background
Building on the validated hypothesis chain:
- **h-e1:** DTW clustering validated (silhouette=0.289, k=4, Jaccard=0.991)
- **h-m1:** PELT changepoint detection validated (detection_rate=81%, mean_cps=0.96)
- **h-m2:** Shape descriptors differentiate clusters (3/4 descriptors exceed variance ratio >2.0)

We now have k=4 empirical clusters with validated shape descriptor profiles. The final step is mapping these clusters to human-interpretable archetypes to validate our lifecycle taxonomy.

### Problem Definition
There is no validated evidence that the empirical clusters align with theoretical lifecycle archetypes. Without archetype alignment, the clusters remain unlabeled statistical groupings rather than interpretable adoption patterns. This hypothesis completes the lifecycle taxonomy by providing semantic meaning to the clusters.

### Impact
- **If archetypes align:** Validates the complete lifecycle taxonomy; enables interpretable dataset recommendations; ready for paper writing
- **If archetypes fail to align:** Document as partial taxonomy; consider refining archetype definitions or accepting 4-cluster empirical taxonomy without theoretical mapping

---

## Functional Requirements

### FR-1: Data Loading Module

**FR-1.1: Reuse h-e1 Data Pipeline**
- Load preprocessed time series from h-e1 execution
- Reuse same 500 dataset samples for controlled comparison
- **Cache Path:** `../h-e1/code/dataset_cache.json`
- **Fallback:** Re-collect via HuggingFace Hub API

**FR-1.2: Load Cluster Assignments and Centroids**
- Load k=4 cluster assignments from h-e1
- Extract cluster centroids from TimeSeriesKMeans model
- Validate centroid shape: (k, T) where T=normalized time points

**FR-1.3: Load Shape Descriptors from h-m2**
- Reuse computed shape descriptors for each centroid
- **Descriptors:** growth_ratio, peak_timing, changepoint_count, derivative_variance
- If not cached, recompute using h-m2 ShapeDescriptorAnalyzer

### FR-2: Archetype Definition Module

**FR-2.1: Define 5 Theoretical Archetypes**
Define a priori archetype profiles based on expected adoption mechanisms:

| Archetype | growth_ratio | peak_timing | changepoint_count | derivative_variance | Mechanism |
|-----------|-------------|-------------|-------------------|---------------------|-----------|
| **Sustained Growth** | 0.8 | 0.9 | 0.2 | 0.2 | Continuous adoption, benchmark datasets |
| **Flash-in-the-Pan** | 0.3 | 0.2 | 0.8 | 0.8 | Viral spike, rapid decline |
| **Plateau** | 0.5 | 0.5 | 0.2 | 0.1 | Stable moderate adoption |
| **Slow Burn** | 0.7 | 0.8 | 0.1 | 0.2 | Gradual adoption over time |
| **Revival** | 0.4 | 0.6 | 0.6 | 0.5 | Decline then resurgence |

**FR-2.2: Archetype Profile Storage**
```python
ARCHETYPE_PROFILES = {
    "sustained_growth": {"growth_ratio": 0.8, "peak_timing": 0.9, "changepoint_count": 0.2, "derivative_variance": 0.2},
    "flash_in_pan":     {"growth_ratio": 0.3, "peak_timing": 0.2, "changepoint_count": 0.8, "derivative_variance": 0.8},
    "plateau":          {"growth_ratio": 0.5, "peak_timing": 0.5, "changepoint_count": 0.2, "derivative_variance": 0.1},
    "slow_burn":        {"growth_ratio": 0.7, "peak_timing": 0.8, "changepoint_count": 0.1, "derivative_variance": 0.2},
    "revival":          {"growth_ratio": 0.4, "peak_timing": 0.6, "changepoint_count": 0.6, "derivative_variance": 0.5}
}
```

### FR-3: Baseline Model Implementation

**FR-3.1: Random Archetype Assignment**
- Randomly assign each cluster (k=4) to one of 5 archetypes
- Expected alignment: ~20% by chance
- **Code:**
```python
import numpy as np
np.random.seed(42)
# Random baseline: assign each cluster to random archetype
random_assignments = np.random.choice(5, size=4, replace=False)
# Expected alignment: ~20% by chance
```

**FR-3.2: Baseline Metrics**
- Compute alignment scores under random assignment
- Establish statistical baseline for comparison
- Used to demonstrate shape descriptors provide meaningful alignment

### FR-4: Proposed Model Implementation

**FR-4.1: Profile Normalization**
```python
def normalize_profile(self, profile):
    """Normalize descriptor values to 0-1 range for comparison."""
    # Use min-max normalization based on observed ranges from h-m2
    ranges = {
        "growth_ratio": (0.3, 0.6),
        "peak_timing": (0, 0.03),
        "changepoint_count": (0, 5),
        "derivative_variance": (0.1, 0.4)
    }
    normalized = {}
    for k, v in profile.items():
        min_v, max_v = ranges.get(k, (0, 1))
        normalized[k] = (v - min_v) / (max_v - min_v) if max_v > min_v else 0.5
        normalized[k] = np.clip(normalized[k], 0, 1)
    return normalized
```

**FR-4.2: Alignment Score Computation**
```python
from scipy.spatial.distance import cosine

def compute_alignment(self, cluster_profile, archetype_name):
    """Compute alignment score (0-1) between cluster and archetype."""
    archetype = self.archetypes[archetype_name]
    norm_profile = self.normalize_profile(cluster_profile)
    cluster_vec = np.array([norm_profile[k] for k in archetype.keys()])
    archetype_vec = np.array(list(archetype.values()))
    return 1 - cosine(cluster_vec, archetype_vec)
```

**FR-4.3: ArchetypeRecoveryMatcher Class**
```python
import numpy as np
from scipy.spatial.distance import cosine

class ArchetypeRecoveryMatcher:
    """
    Map empirical cluster centroids to theoretical archetypes
    using shape descriptor alignment (>70% threshold).
    """
    def __init__(self, alignment_threshold=0.70):
        self.threshold = alignment_threshold
        self.archetypes = ARCHETYPE_PROFILES  # From FR-2.2

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

**FR-4.4: Alignment Matrix Construction**
- Compute full alignment matrix: shape (4 clusters, 5 archetypes)
- Each cell contains cosine similarity between cluster profile and archetype
- Used for visualization and analysis

### FR-5: Evaluation Module

**FR-5.1: Primary Metrics**
| Metric | Target | Required |
|--------|--------|----------|
| Archetype Recovery Rate | >=3 of 5 archetypes matched | Yes (SHOULD_WORK gate) |
| Mean Alignment Score | >0.70 across matched archetypes | Yes |
| Uniqueness | No archetype assigned to multiple clusters | Yes |

**FR-5.2: Secondary Metrics**
| Metric | Purpose |
|--------|---------|
| Alignment Matrix Max per Row | Best archetype match per cluster |
| Alignment Distribution | Histogram of all alignment scores |
| Unmatched Archetypes | Which archetypes have no matching cluster |

**FR-5.3: Mechanism Activation Verification**
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

### FR-6: Visualization Requirements

**FR-6.1: Required Figure (Mandatory)**
- **Gate Metrics Bar Chart:** Target (3) vs actual archetype recovery with pass/fail indicator

**FR-6.2: Additional Figures (Autonomous)**
1. **Alignment Heatmap:** 4x5 matrix showing cluster-archetype alignment scores
2. **Radar Chart:** Archetype profiles vs cluster profiles overlay
3. **Cluster-Archetype Assignment Diagram:** Visual mapping of clusters to archetypes
4. **Descriptor Space Projection:** 2D visualization showing cluster-archetype distances

**FR-6.3: Figure Output**
- Save all figures to `h-m3/figures/` directory
- Use PNG format with 300 DPI
- Include descriptive titles and axis labels

### FR-7: Results Persistence

**FR-7.1: Validation Report**
- Save results to `h-m3/04_validation.md`
- Include all metric values with pass/fail status
- Record execution timestamp and parameters

**FR-7.2: Artifacts**
- Save alignment matrix (4 x 5)
- Save cluster-archetype assignments
- Save archetype profiles for reproducibility

---

## Non-Functional Requirements

### NFR-1: Performance
- Complete full pipeline in < 2 minutes on single CPU
- Handle k=4 clusters × 5 archetypes efficiently
- No GPU required (pure analysis task)

### NFR-2: Reproducibility
- Fixed random seed (42) for baseline
- Log all hyperparameters (alignment_threshold, normalization ranges)
- Document library versions (scipy, numpy)

### NFR-3: Code Quality
- Type hints for all functions
- Docstrings with parameter descriptions
- Modular design with clear separation of concerns

### NFR-4: Error Handling
- Handle edge cases: all clusters below threshold, identical profiles
- Graceful degradation for partial matches
- Validate input shapes and types

---

## Technical Specifications

### Dependencies
```
numpy>=1.24.0
scipy>=1.10.0
matplotlib>=3.5.0
seaborn>=0.12.0
```

### Hardware Requirements
- Single CPU
- Minimum 2GB RAM
- No GPU required

### Algorithm Reference
- **Cosine Similarity:** scipy.spatial.distance.cosine
- **Alignment Threshold:** 0.70 (from Phase 2C specification)
- **Archetype Definitions:** Literature-based + h-m2 observed ranges

---

## Success Criteria

### Gate Condition: SHOULD_WORK

**Pass Criteria:**
1. >=3 of 5 archetypes recovered with alignment > 0.70
2. Mean alignment across matched archetypes > 0.70
3. No archetype assigned to multiple clusters (uniqueness)

**Secondary Validation:**
4. Shape-based matching outperforms random assignment baseline
5. Archetype assignments are interpretable (align with known adoption patterns)

**Consequence of Failure:**
- DOCUMENT: Partial taxonomy recovery noted
- PROCEED: To paper writing with 4-cluster empirical taxonomy
- CONSIDER: Refining archetype definitions

### Mechanism Verification
- Alignment scores successfully computed for all cluster-archetype pairs
- At least 1 archetype recovered (mechanism activation)
- For full hypothesis support: recovery >= 3 archetypes

---

## Data Flow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  h-m2 Shape     │────▶│  Profile         │────▶│  Alignment      │
│  Descriptors    │     │  Normalization   │     │  Matrix (4×5)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                          │
┌─────────────────┐                                       │
│  Archetype      │───────────────────────────────────────┘
│  Definitions    │
└─────────────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Validation     │◀────│  Archetype       │◀────│  Threshold      │
│  Report         │     │  Recovery Count  │     │  Matching       │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

---

## Acceptance Criteria

### AC-1: Data Loading
- [ ] Successfully loads h-e1 cluster centroids
- [ ] Successfully loads h-m2 shape descriptors
- [ ] Validates k=4 clusters with 4 descriptors each

### AC-2: Archetype Definition
- [ ] 5 archetypes defined with 4 descriptors each
- [ ] Archetype profiles based on literature + observed ranges
- [ ] Profiles stored in reproducible format

### AC-3: Alignment Computation
- [ ] Normalization applied consistently
- [ ] Cosine similarity computed for all 20 pairs (4×5)
- [ ] Alignment matrix validated

### AC-4: Baseline Comparison
- [ ] Random assignment baseline implemented
- [ ] Shape-based matching outperforms baseline
- [ ] Statistical significance assessed

### AC-5: Visualization
- [ ] Gate metrics bar chart generated
- [ ] Alignment heatmap generated
- [ ] All saved to h-m3/figures/

### AC-6: Gate Validation
- [ ] Pass/Fail determination based on recovery criteria
- [ ] Results written to 04_validation.md
- [ ] Gate result recorded in verification_state.yaml

---

## Traceability

| Requirement | Source |
|-------------|--------|
| k=4 centroids | h-e1 validated clustering |
| Shape descriptors | h-m2 validated differentiation |
| Alignment threshold (70%) | Phase 2C hypothesis specification |
| Recovery target (>=3/5) | Phase 2C hypothesis specification |
| 5 archetypes | Phase 2B verification plan |
| Cosine similarity | Phase 2C Exa research (scipy) |

---

## Appendix

### A. Phase 2C Reference
- Source: `h-m3/02c_experiment_brief.md`
- Contains: Full experiment specification with pseudo-code

### B. Hypothesis Chain
```
h-e1 (EXISTENCE) ──▶ h-m1 (MECHANISM) ──▶ h-m2 (MECHANISM) ──▶ h-m3 (MECHANISM)
     │                    │                    │                    │
  VALIDATED           VALIDATED            VALIDATED           SHOULD_WORK
   (PASS)              (PASS)              (PASS)              (current)
```

### C. Prerequisite Results

**h-e1 (DTW Clustering):**
- Gate: MUST_WORK - **PASS**
- Silhouette Score: 0.289 (> 0.25 threshold)
- Optimal k: 4 (in [3, 8] range)
- Jaccard Stability: 0.991 (> 0.65 threshold)

**h-m1 (PELT Changepoint Detection):**
- Gate: MUST_WORK - **PASS**
- Detection Rate: 81% (> 50% threshold)
- Mean Changepoints: 0.96 per series
- 405/500 series have at least one changepoint

**h-m2 (Shape Descriptor Differentiation):**
- Gate: SHOULD_WORK - **PASS**
- Passing Descriptors: 3/4 (growth_ratio, changepoint_count, derivative_variance)
- Variance Ratios: 4.74, 11.08, 2.16 (all > 2.0)
- Min Pairwise Distance: 0.317 (distinct profiles)

---

*Generated by Phase 3 Implementation Planning*
*Source: Phase 2C Experiment Brief (h-m3/02c_experiment_brief.md)*
