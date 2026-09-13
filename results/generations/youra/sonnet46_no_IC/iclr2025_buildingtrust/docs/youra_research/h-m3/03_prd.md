# Product Requirements Document: H-M3
## RLHF Causal Chain Produces 2-Cluster Trustworthiness Correlation Structure

**Hypothesis ID:** H-M3  
**Type:** MECHANISM (Step 3 of 3-step RLHF causal chain)  
**Gate:** SHOULD_WORK  
**PRD Version:** 1.0  
**Date:** 2026-08-04  
**Author:** Anonymous  
**stepsCompleted:** [prd-step-1, prd-step-2, prd-step-3, prd-step-4, prd-step-5]

---

## 1. Executive Summary

H-M3 tests whether the RLHF-driven co-movement of safety+ethics (positive ρ, confirmed by H-M1) combined with the safety-robustness anti-correlation (negative ρ, directionally confirmed by H-M2) produces a 2-cluster solution when applying Ward-linkage hierarchical clustering to the 6×6 ρ_partial matrix from H-E1. The predicted clusters are: RLHF-sensitive {safety, machine_ethics} vs RLHF-insensitive {adversarial robustness, privacy}, with {truthfulness, fairness} ambiguous.

H-M3 requires no neural model training. Implementation consists of: (1) loading the pre-computed 6×6 ρ_partial matrix from H-E1, (2) converting to distance matrix (d=1−ρ), (3) running scipy Ward-linkage hierarchical clustering (bypassing sklearn's Ward+precomputed limitation via sklearn issue #27655), (4) computing silhouette score, (5) evaluating cluster membership alignment against pre-specified predictions, and (6) optionally replicating on HELM leaderboard data.

**Gate condition (SHOULD_WORK):** Failure does not stop the pipeline. Silhouette < 0.3 → EXPLORE (report without cluster interpretation); membership misalignment → EXPLORE (report actual cluster composition).

---

## 2. Problem Statement

### 2.1 Research Question

Does the RLHF causal chain from H-M1 and H-M2 produce a measurable 2-cluster structure in trustworthiness dimensions? Specifically:
- Does Ward-linkage hierarchical clustering of the 6×6 ρ_partial matrix yield silhouette score > 0.3 for k=2?
- Does the resulting cluster membership match the predicted RLHF-sensitive {safety, machine_ethics} vs RLHF-insensitive {robustness, privacy} grouping in ≥4/6 dimensions?

### 2.2 Mechanism Under Test

The hypothesis posits that RLHF alignment creates a structural divide in trustworthiness dimensions:
- **RLHF-sensitive cluster:** Dimensions co-optimized by RLHF preference learning (safety, machine_ethics) → high positive ρ among themselves
- **RLHF-insensitive cluster:** Dimensions not directly targeted by RLHF (adversarial robustness, privacy in terms of isolation from RLHF signal) → near-zero or negative ρ with RLHF-sensitive cluster
- **Ambiguous dimensions:** {truthfulness, fairness} — high ρ with both safety and privacy in H-E1, unclear RLHF sensitivity

This structural divide should be detectable as a clear 2-cluster Ward linkage solution.

### 2.3 Theoretical Grounding

- H-E1 (PASS): Average-linkage silhouette=0.614 for k=2 — strong cluster structure already present
- H-M1 (PASS): ρ_partial(safety, machine_ethics)=0.841 — RLHF co-optimizes both dimensions
- H-M2 (PARTIAL_PASS): Robustness directionally isolated from positive ρ cluster; scale-only ρ(safety,robustness)=−0.771
- H-E1 pre-analysis: {truthfulness, safety, fairness, privacy, machine_ethics} form positive ρ cluster (ρ>0.53 for all pairs); robustness isolated (ρ≈−0.19 to +0.22 with all others)
- Sun et al. 2024 TrustLLM (ICML): Notes over-calibration and dimension correlation structure

### 2.4 Prior Results Context

From H-E1 (prerequisite, PASS):
- 6×6 ρ_partial matrix fully pre-computed: h-e1/experiment_results_phase3.json
- Dimension order: [truthfulness, safety, fairness, robustness, privacy, machine_ethics]
- Average-linkage silhouette=0.614 (k=2) — Ward expected to be similar or higher
- Strongest pairs: ρ(safety,privacy)=0.971, ρ(truthfulness,fairness)=0.935, ρ(safety,machine_ethics)=0.841
- Robustness most isolated: ρ(robustness, others)∈[−0.188, +0.221]

---

## 3. Scope

### 3.1 In Scope

- Load pre-computed 6×6 ρ_partial matrix from h-e1/experiment_results_phase3.json
- scipy Ward-linkage hierarchical clustering on distance matrix (d=1−ρ_partial)
- Silhouette score computation with precomputed distance matrix
- Cluster membership alignment against predicted RLHF-sensitive/insensitive groupings
- Robustness checks: k=3 comparison, alternative linkages (average, complete), alternative distance (sqrt(1−ρ²))
- Visualization: dendrogram, heatmap with cluster annotations, silhouette comparison, 2D MDS projection
- Optional: HELM replication (Ward clustering on HELM 30-model × 7-metric ρ_partial matrix)
- Generate figures to `h-m3/figures/`
- Save results to `h-m3/experiment_results_h_m3.json`

### 3.2 Out of Scope

- Neural model training or fine-tuning
- New TrustLLM benchmark data collection (ρ_partial matrix already cached)
- Multi-GPU computation (pure CPU scipy analysis, <5 seconds)
- Individual model score analysis (only aggregate ρ_partial matrix used)

---

## 4. Data Specification

### 4.1 Primary Dataset: TrustLLM 6×6 ρ_partial Matrix (Derived from H-E1)

| Attribute | Value |
|-----------|-------|
| Name | TrustLLM Partial Spearman Correlation Matrix (6×6, derived) |
| Type | Derived (pre-computed in H-E1 from 16-model × 6-dimension scores) |
| Source | h-e1/experiment_results_phase3.json (field: `rho_partial`) |
| Cache Path | h-e1/experiment_results_phase3.json |
| Verified | true (reused from H-E1, validated by H-M1 and H-M2) |
| Download Required | NO — already cached from H-E1 |
| Matrix Size | 6×6 (symmetric, all values pre-computed) |
| Dimensions | [truthfulness, safety, fairness, robustness, privacy, machine_ethics] |
| Underlying Models | 16 LLMs from TrustLLM evaluation (Sun et al., ICML 2024) |

**Key pre-confirmed ρ values from H-E1:**

| Dim Pair | ρ_partial | Status |
|----------|-----------|--------|
| truthfulness–fairness | 0.935 | Significant (p<0.0033) |
| safety–privacy | 0.971 | Significant (p<0.0033) |
| safety–machine_ethics | 0.841 | Significant (p<0.0033) |
| fairness–privacy | 0.894 | Significant (p<0.0033) |
| fairness–machine_ethics | 0.782 | Significant (p<0.0033) |
| privacy–machine_ethics | 0.859 | Significant (p<0.0033) |
| safety–robustness | -0.188 | Not significant (p=0.519) |
| robustness–truthfulness | +0.221 | Not significant |
| robustness–fairness | +0.097 | Not significant |
| robustness–privacy | -0.106 | Not significant |
| robustness–machine_ethics | -0.068 | Not significant |

**Loading code:**
```python
import json, numpy as np

DIMS = ["truthfulness", "safety", "fairness", "robustness", "privacy", "machine_ethics"]

with open("../h-e1/experiment_results_phase3.json") as f:
    h_e1_results = json.load(f)

# rho_partial: 6×6 numpy array
rho_partial = np.array(h_e1_results["rho_partial"])  # shape (6,6)
```

### 4.2 Optional Dataset: HELM Leaderboard (Replication Check)

| Attribute | Value |
|-----------|-------|
| Name | HELM Leaderboard (30-model × 7-metric) |
| Type | Standard (published leaderboard, CRFM Stanford) |
| Source | https://crfm.stanford.edu/helm/latest/ |
| Metric Mapping | safety→toxicity, fairness→stereotypes/bias, robustness→robustness |
| Purpose | Replicate sign pattern (safety-ethics positive, safety-robustness negative) in independent dataset |
| If Unavailable | Skip; note as limitation; primary gate unaffected |

---

## 5. Functional Requirements

### FR-1: Data Loading and Validation

**Priority:** Critical  
**Source:** Phase 2C §Dataset

- FR-1.1: Load h-e1/experiment_results_phase3.json and validate JSON structure
- FR-1.2: Extract rho_partial as 6×6 numpy array; validate shape is (6,6)
- FR-1.3: Validate matrix is symmetric (|rho[i,j] − rho[j,i]| < 1e-6 for all pairs)
- FR-1.4: Validate diagonal is 1.0 (self-correlation)
- FR-1.5: Validate all off-diagonal values in [−1, 1]
- FR-1.6: Confirm dimension order: [truthfulness, safety, fairness, robustness, privacy, machine_ethics]

### FR-2: Distance Matrix Construction

**Priority:** Critical  
**Source:** Phase 2C §Training Protocol Step 1

- FR-2.1: Construct distance matrix: `dist_matrix = np.clip(1 - rho_partial, 0, 2)`
- FR-2.2: Set diagonal to 0: `np.fill_diagonal(dist_matrix, 0)`
- FR-2.3: Validate dist_matrix is non-negative and symmetric
- FR-2.4: Convert to condensed form: `condensed = squareform(dist_matrix)` for scipy linkage input

### FR-3: Ward-Linkage Hierarchical Clustering (Primary)

**Priority:** Critical  
**Source:** Phase 2C §Models §Proposed Model, sklearn issue #27655 workaround

- FR-3.1: Run scipy Ward linkage on condensed distance matrix:
  ```python
  from scipy.cluster.hierarchy import linkage, fcluster
  from scipy.spatial.distance import squareform
  Z = linkage(condensed, method='ward')
  ```
- FR-3.2: Cut dendrogram at k=2 clusters: `labels = fcluster(Z, t=2, criterion='maxclust') - 1`
- FR-3.3: Compute silhouette score with precomputed distance:
  ```python
  from sklearn.metrics import silhouette_score
  sil_ward = silhouette_score(dist_matrix, labels, metric='precomputed')
  ```
- FR-3.4: Evaluate primary gate: `sil_ward > 0.3`
- FR-3.5: Store cluster assignments as dict: `{dim: cluster_label for dim in DIMS}`
- FR-3.6: **MUST NOT** use `sklearn.cluster.AgglomerativeClustering(linkage='ward', metric='precomputed')` — Ward+precomputed not supported (sklearn #27655)

### FR-4: Cluster Membership Alignment (Secondary Gate)

**Priority:** Critical  
**Source:** Phase 2C §Training Protocol Step 6, §Evaluation

Pre-specified predictions (MUST be defined BEFORE running analysis):
```python
PREDICTED_RLHF_SENSITIVE = {"safety", "machine_ethics"}      # positive ρ, RLHF co-optimized
PREDICTED_RLHF_INSENSITIVE = {"robustness", "privacy"}       # isolated/negative ρ with safety
# {truthfulness, fairness} = ambiguous (NOT pre-specified)
```

- FR-4.1: Try both label assignments (0=sensitive or 1=sensitive); take best alignment:
  ```python
  def compute_membership_alignment(cluster_membership):
      best = 0
      for sensitive_label in [0, 1]:
          count = 0
          for dim, label in cluster_membership.items():
              if dim in PREDICTED_RLHF_SENSITIVE and label == sensitive_label:
                  count += 1
              elif dim in PREDICTED_RLHF_INSENSITIVE and label != sensitive_label:
                  count += 1
          best = max(best, count)
      return best  # range: 0–4 (only 4 pre-specified dims)
  ```
- FR-4.2: Evaluate secondary gate: `membership_alignment >= 4` (≥4/6 dimensions; effectively ≥4/4 pre-specified)
- FR-4.3: Report full cluster composition and alignment score
- FR-4.4: Note placement of ambiguous dims {truthfulness, fairness} as exploratory finding

### FR-5: Robustness Checks

**Priority:** High  
**Source:** Phase 2C §Training Protocol §Robustness Checks

- FR-5.1: k=3 clustering: compute silhouette for k=3; confirm k=2 is optimal (sil_k2 > sil_k3)
- FR-5.2: Average-linkage comparison: run sklearn AgglomerativeClustering(linkage='average', metric='precomputed'); compare silhouette with Ward result; note H-E1 baseline=0.614
- FR-5.3: Complete-linkage comparison: run sklearn AgglomerativeClustering(linkage='complete', metric='precomputed')
- FR-5.4: Alternative distance metric: `dist_alt = np.sqrt(1 - rho_partial**2)`; re-run Ward on this; report silhouette
- FR-5.5: Dendrogram: generate scipy dendrogram plot; annotate predicted cluster membership

### FR-6: Visualization

**Priority:** High  
**Source:** Phase 2C §Visualization Requirements

All figures saved to `h-m3/figures/`.

- FR-6.1: **Gate Metrics Bar Chart** (mandatory): silhouette_ward vs 0.3 threshold; membership_alignment vs 4/6 threshold
- FR-6.2: **Dendrogram**: scipy dendrogram of Ward linkage on 6 TrustLLM dimensions; color leaves by predicted cluster membership (green=RLHF-sensitive, red=RLHF-insensitive, gray=ambiguous); annotate 2-cluster cut line
- FR-6.3: **ρ_partial Heatmap with Cluster Annotations**: 6×6 heatmap, reordered by Ward cluster assignment; diverging colormap (red=positive, blue=negative); annotate cluster boundaries
- FR-6.4: **Silhouette Comparison Bar Chart**: Ward vs average (H-E1) vs complete linkage silhouette scores for k=2
- FR-6.5: **2D MDS Projection**: 2D MDS of distance matrix; color points by Ward cluster assignment; annotate predicted membership labels

### FR-7: Optional HELM Replication

**Priority:** Medium  
**Source:** Phase 2C §Training Protocol §HELM Optional Replication

- FR-7.1: Attempt to load HELM leaderboard data from public API or local cache
- FR-7.2: If available: map HELM metrics to TrustLLM dimensions; compute ρ_partial matrix; run Ward clustering
- FR-7.3: Report whether sign pattern (safety-ethics positive, safety-robustness negative) replicates
- FR-7.4: If unavailable: skip; note as limitation; gate evaluation unaffected

### FR-8: Results Persistence

**Priority:** Critical  
**Source:** Phase 2C §State Information, Phase 4 integration

- FR-8.1: Save all results to `h-m3/experiment_results_h_m3.json`:
  ```json
  {
    "hypothesis_id": "h-m3",
    "silhouette_ward": <float>,
    "primary_gate_pass": <bool>,
    "cluster_membership": {"truthfulness": <int>, "safety": <int>, ...},
    "membership_alignment": <int>,
    "secondary_gate_pass": <bool>,
    "overall_gate": "PASS|PARTIAL_PASS|FAIL",
    "silhouette_average": <float>,
    "silhouette_complete": <float>,
    "silhouette_k3": <float>,
    "silhouette_alt_distance": <float>,
    "cluster_labels": <list>,
    "figure_paths": [...]
  }
  ```
- FR-8.2: Print gate verification messages consistent with prior hypothesis output format
- FR-8.3: Write gate result regardless of pass/fail (SHOULD_WORK — pipeline continues)

---

## 6. Non-Functional Requirements

### NFR-1: Performance
- Runtime < 10 seconds for primary analysis (6×6 matrix, pure numpy/scipy)
- MDS visualization may take up to 30 seconds (acceptable)

### NFR-2: Reproducibility
- Seed: 1 (applied to MDS if randomized)
- Ward linkage is deterministic — no seed needed for clustering itself
- Environment: youra-h-m2 conda (reuse: Python 3.10, scipy 1.11.0, sklearn, numpy, matplotlib)

### NFR-3: Continuity with H-E1/H-M1/H-M2
- Must read rho_partial from h-e1/experiment_results_phase3.json (do NOT recompute)
- Dimension ordering must match H-E1: [truthfulness, safety, fairness, robustness, privacy, machine_ethics]
- scipy Ward implementation must use squareform+linkage pattern (sklearn Ward+precomputed forbidden)

### NFR-4: SHOULD_WORK Gate Compliance
- Code must NOT terminate on gate failure
- Failure result must be saved and reported (publishable finding either way)
- Pipeline continuation checkpoint must be written regardless of gate result

---

## 7. Dependencies

### 7.1 Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| scipy | 1.11.0 | linkage, fcluster, squareform, dendrogram |
| scikit-learn | latest | silhouette_score (precomputed), AgglomerativeClustering (alternative linkages), MDS |
| numpy | latest | Array operations, distance matrix |
| matplotlib | latest | Figures (dendrogram, heatmap, bar charts) |
| seaborn | latest | Heatmap |
| json | stdlib | Data loading |

**Environment:** Reuse `youra-h-m2` conda environment (all packages already installed)

### 7.2 External Repositories

| Repository | Purpose | Access |
|------------|---------|--------|
| HowieHwong/TrustLLM | Primary data source (already cached in H-E1) | h-e1/experiment_results_phase3.json |
| scikit-learn/scikit-learn | AgglomerativeClustering (alternative linkages), silhouette_score | Already installed |
| scipy | Ward linkage with precomputed distances (workaround for sklearn #27655) | Already installed |

### 7.3 Prerequisite Files

| File | Source | Required |
|------|--------|---------|
| h-e1/experiment_results_phase3.json | H-E1 Phase 4 output | YES — primary data (6×6 rho_partial) |
| h-m1/04_validation.md | H-M1 Phase 4 output | Reference only (confirms safety-ethics correlation) |
| h-m2/04_validation.md | H-M2 Phase 4 output | Reference only (confirms robustness isolation direction) |

---

## 8. Success Criteria

### 8.1 Primary Gate (SHOULD_WORK)

| Metric | Threshold | Expected |
|--------|-----------|---------|
| silhouette_ward (k=2, Ward linkage) | > 0.3 | ~0.55–0.70 (based on H-E1 average-linkage=0.614) |

### 8.2 Secondary Gate

| Metric | Threshold | Expected |
|--------|-----------|---------|
| membership_alignment | ≥ 4/6 dimensions | safety, machine_ethics in same cluster; robustness in different cluster; privacy ambiguous (ρ=0.971 with safety may place it in RLHF-sensitive cluster) |

### 8.3 Outcome Classification

| Result | Condition | Action |
|--------|-----------|--------|
| PASS | Primary (sil>0.3) AND Secondary (align≥4) | Report 2-cluster RLHF mechanism confirmation |
| PARTIAL_PASS | Only primary satisfies | Report cluster exists but membership ambiguous |
| PARTIAL_PASS | Only secondary satisfies | Report membership aligns but silhouette low |
| FAIL/EXPLORE | Both fail | Report null; SHOULD_WORK = pipeline continues |

### 8.4 PoC Pass Condition

1. Code runs without error
2. silhouette_ward value computed and compared to 0.3 threshold
3. membership_alignment computed and compared to 4/6 threshold
4. Results saved to experiment_results_h_m3.json
5. All mandatory figures generated (FR-6.1 at minimum)

---

## 9. Ablation Variants

### Ablation A1: Alternative Linkage Methods
- Average-linkage (H-E1 baseline, silhouette=0.614): confirm Ward produces comparable or better separation
- Complete-linkage: compare; Ward typically gives tighter, more equal-sized clusters

### Ablation A2: k=3 Sensitivity
- Run Ward clustering at k=3; check if silhouette improves (would suggest 3-cluster is more natural)
- Expected: k=2 should win or be comparable (hypothesis predicts binary RLHF-sensitive/insensitive structure)

### Ablation A3: Alternative Distance Metric
- Use d=sqrt(1−ρ²) instead of d=1−ρ; re-run Ward clustering
- Compare cluster assignments and silhouette; report robustness of membership to distance choice

### Ablation A4: HELM Cross-Dataset Replication (Optional)
- Replicate ward clustering on HELM 30-model × 7-metric data
- Report whether safety-ethics positive / safety-robustness negative pattern holds
- If HELM unavailable: skip as limitation

---

## 10. Implementation Notes

### 10.1 Code Structure

```
h-m3/
├── code/
│   ├── run_h_m3.py          # Main analysis script
│   └── visualize.py         # Figure generation
├── figures/
│   ├── gate_metrics.png         # FR-6.1
│   ├── dendrogram.png           # FR-6.2
│   ├── rho_heatmap_clustered.png # FR-6.3
│   ├── silhouette_comparison.png # FR-6.4
│   └── mds_projection.png       # FR-6.5
└── experiment_results_h_m3.json
```

### 10.2 Critical Implementation Decision: scipy vs sklearn Ward

**FORBIDDEN:** `sklearn.cluster.AgglomerativeClustering(linkage='ward', metric='precomputed')` — throws ValueError (Ward does not support precomputed, sklearn #27655, still open as of 2024)

**REQUIRED:** Use scipy Ward pipeline:
```python
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform

condensed = squareform(dist_matrix)    # (6*5/2=15,) condensed distance vector
Z = linkage(condensed, method='ward')  # Ward linkage on condensed distances
labels = fcluster(Z, t=2, criterion='maxclust') - 1  # 0-indexed cluster labels
```

### 10.3 SHOULD_WORK Gate Behavior

This is the **culminating test** of the 3-step RLHF causal chain. Code must:
- Never raise exception on gate failure
- Always write results JSON regardless of outcome
- Write clear EXPLORE message if primary gate fails: "silhouette_ward = {value:.4f} — below 0.3 threshold; no clear 2-cluster structure"
- Note: H-E1 average-linkage silhouette=0.614 makes primary gate failure unlikely, but membership alignment is genuinely uncertain (privacy may cluster with RLHF-sensitive group due to ρ(safety,privacy)=0.971)

### 10.4 Membership Alignment Uncertainty

Pre-analysis note: The predicted cluster {robustness, privacy} may not hold because:
- ρ(safety, privacy)=0.971 is the strongest pair — privacy will almost certainly cluster with safety
- Predicted: {robustness, privacy} = RLHF-insensitive; Actual likely: {robustness} isolated, {privacy} with safety cluster
- If privacy clusters with RLHF-sensitive: membership_alignment may be 3/4 → secondary gate FAIL
- This is pre-specified uncertainty; report actual outcome without post-hoc rationalization
