# Experiment Design: h-m3

**Date:** 2026-08-04
**Author:** Anonymous
**Hypothesis Statement:** Under the TrustLLM 16-model setting, if the RLHF-driven co-movement of safety+ethics (positive ρ) combines with the safety-robustness anti-correlation (negative ρ) from Steps 1+2, then hierarchical clustering (Ward linkage) of the 6×6 ρ_partial matrix will produce a 2-cluster solution with silhouette score > 0.3 AND cluster membership matching the predicted RLHF-sensitive {safety, ethics} vs RLHF-insensitive {adversarial robustness, calibration/privacy} grouping in ≥4/6 dimensions.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** h-m2 COMPLETED (PARTIAL_PASS, SHOULD_WORK — pipeline continues)
**Gate Status:** SHOULD_WORK (non-blocking; pipeline continues regardless of outcome)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** MECHANISM (Step 3 of 3-step RLHF causal chain)
- **Prerequisites:** h-m1 (PASS), h-m2 (PARTIAL_PASS)

### Gate Condition

**Primary:** Silhouette score > 0.3 for k=2 Ward-linkage hierarchical clustering of 6×6 ρ_partial matrix

**Secondary:** ≥4/6 dimensions correctly assigned to predicted clusters:
- Predicted RLHF-sensitive cluster: {safety, machine_ethics}
- Predicted RLHF-insensitive cluster: {robustness, privacy}
- Ambiguous (pre-specified): {truthfulness, fairness}

**Note:** This is SHOULD_WORK — primary gate fail → EXPLORE (report without cluster interpretation); secondary fail → EXPLORE (report actual cluster membership).

---

## Continuation Context

### Previous Hypothesis Results

**H-E1 (PASS):**
- 8/15 partial Spearman pairs significant (|ρ|>0.5, p<0.0033 Bonferroni)
- Silhouette=0.614 (k=2, average-linkage) — strong cluster structure already confirmed
- ρ_partial matrix: dimension order = [truthfulness, safety, fairness, robustness, privacy, machine_ethics]
- Key values: ρ(safety,privacy)=0.971, ρ(truthfulness,fairness)=0.935, ρ(safety,fairness)=0.859
- Robustness uncorrelated with all others: ρ(robustness,safety)=-0.188, ρ(robustness,privacy)=-0.106
- Results file: h-e1/experiment_results_phase3.json

**H-M1 (PASS):**
- ρ_partial(safety, machine_ethics)=0.841 > 0.5 — RLHF co-optimizes safety+ethics CONFIRMED
- 3/3 LLaMA-2 pairs: Δ_safety>0 AND Δ_ethics>0 simultaneously

**H-M2 (PARTIAL_PASS):**
- ρ_partial(safety, robustness)=-0.1882 (not significant at Bonferroni threshold)
- 3/3 LLaMA-2 pairs: Δ_robustness≤0 — directional support
- Scale-only ablation: ρ=-0.771 (p=0.0008) — strong negative controlling scale alone
- Key implication for H-M3: robustness sits isolated from all positive-ρ cluster

**Critical Pre-Analysis from H-E1 matrix:**
The ρ_partial matrix structure already strongly suggests 2-cluster solution:
- Cluster A (high positive ρ): {truthfulness, safety, fairness, privacy, machine_ethics} — all pairs ρ > 0.53
- Cluster B (isolated, near-zero or negative with Cluster A): {robustness} — all inter-cluster ρ ≈ -0.19 to +0.22
- Predicted boundary: {safety, machine_ethics} vs {robustness} clear; {truthfulness, fairness, privacy} → RLHF-sensitive by association

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "hierarchical clustering Ward linkage correlation matrix experiment design"**
- Results: Low relevance (diffusion/PyTorch KB, similarity ~0.33). No directly applicable past cases for correlation-matrix Ward clustering.
- Key insight: Archon KB is a diffusion/deep learning KB — statistical clustering methods not covered.

**Query 2: "silhouette score clustering evaluation LLM benchmark dimensions"**
- Best match: hf.co/papers/2305.14314 (similarity 0.47) — partial relevance for LLM evaluation dimensions
- Other results: mmgeneration FID docs, OpenReview paper — low relevance
- Key insight: No past clustering experiment cases in KB.

**Summary:** Archon KB contains no prior cases directly relevant to Ward-linkage hierarchical clustering of correlation matrices for LLM evaluation dimensions. All experiment design grounded in Exa search results and prior H-E1/H-M1/H-M2 context.

### Archon Code Examples

**Query 1: "AgglomerativeClustering Ward correlation matrix precomputed Python"**
- Results: Incidence matrix code (Overleaf/LaTeX examples, similarity ~0.32), CUDA batched solves — completely unrelated.
- No relevant code examples in Archon KB for this task.

**Summary:** Archon code KB does not contain AgglomerativeClustering or sklearn clustering examples. Experiment design relies entirely on Exa/sklearn official docs and prior hypothesis code.

### Exa GitHub Implementations

**Query 1: sklearn AgglomerativeClustering Ward linkage silhouette_score**

**Source 1: scikit-learn official documentation** (sklearn.org/stable)
- URL: https://scikit-learn.org/stable/modules/generated/sklearn.cluster.AgglomerativeClustering.html
- Relevance: CRITICAL — defines exact API and constraints
- Key API:
  ```python
  AgglomerativeClustering(n_clusters=2, metric='euclidean', linkage='ward')
  ```
- **CRITICAL CONSTRAINT:** Ward linkage only accepts `metric='euclidean'` — NOT `metric='precomputed'`. This means cannot pass the ρ_partial distance matrix directly with Ward linkage.
- **Solution:** Convert ρ_partial matrix to Euclidean-compatible form using scipy.cluster.hierarchy with Ward method, OR use `linkage(squareform(dist_matrix), method='ward')` from scipy which accepts precomputed distances.

**Source 2: sklearn silhouette_score docs** (scikit-learn.org)
- URL: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html
- Key API:
  ```python
  silhouette_score(X, labels, metric='precomputed')
  ```
- Supports `metric='precomputed'` — silhouette_score CAN use precomputed distance matrix.

**Source 3: sklearn GitHub issue #27655** (AgglomerativeClustering + Ward + precomputed)
- URL: https://github.com/scikit-learn/scikit-learn/issues/27655
- Key finding: Ward + precomputed is a known limitation; issue opened Oct 2023, still open.
- **Resolution for H-M3:** Use `scipy.cluster.hierarchy.linkage(dist_matrix_squareform, method='ward')` instead of sklearn AgglomerativeClustering. scipy.cluster.hierarchy does NOT have this restriction.

**Source 4: AgglomerativeClustering + silhouette gist** (bitsnaps/gist)
- URL: https://gist.github.com/bitsnaps/12415200fc62539fff852a1b46168d0a
- Relevant code pattern:
  ```python
  from sklearn.cluster import AgglomerativeClustering
  from sklearn.metrics import silhouette_samples, silhouette_score
  clusterer = AgglomerativeClustering(n_clusters=n_clusters, linkage='ward')
  y_predict = clusterer.fit_predict(X)
  cluster_labels = clusterer.labels_
  silhouette_avg = silhouette_score(X, cluster_labels)
  ```
- Note: Uses Euclidean data directly (not precomputed). Must adapt for correlation matrix.

**Query 2: HowieHwong TrustLLM clustering analysis**

**Source 5: HowieHwong/TrustLLM** (GitHub, 622 stars)
- URL: https://github.com/HowieHwong/TrustLLM
- 6 dimensions: truthfulness, safety, fairness, robustness, privacy, machine_ethics
- Results stored in `results/*.json` per model per dimension
- Pre-computed ρ_partial matrix already loaded in h-e1/experiment_results_phase3.json
- No clustering analysis performed by TrustLLM authors — H-M3 is novel contribution.

**Serena Analysis Needed:** False — pure statistical analysis on a 6×6 matrix, no complex ML code to analyze.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is NOT a paper reproduction experiment. H-M3 is a novel analysis on TrustLLM published data.
Primary implementation: scipy.cluster.hierarchy (Ward linkage on precomputed distance matrix)
Fallback: sklearn AgglomerativeClustering with converted Euclidean embedding via MDS/PCA of ρ_partial

**Recommended Implementation Path:**
- Primary: scipy.cluster.hierarchy.linkage + fcluster (supports Ward + precomputed distances)
- Fallback: sklearn AgglomerativeClustering with metric='euclidean' on sqrt(1-ρ_partial) embedding
- Justification: scipy approach is standard for Ward clustering on precomputed distance matrices; sklearn Ward does not support precomputed metric (confirmed via sklearn issue #27655)

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. H-M3 is pure statistical analysis (scipy/sklearn clustering on a 6×6 matrix). No complex neural network or custom code requiring semantic analysis. All implementation patterns sourced directly from sklearn/scipy official documentation and gist examples.

---

## Experiment Specification

### Dataset

**Dataset:** TrustLLM Published Score Tables — 6×6 ρ_partial matrix (derived from H-E1)
**Type:** derived (pre-computed in h-e1/experiment_results_phase3.json) + optional HELM replication (standard)
**Source:** h-e1/experiment_results_phase3.json (rho_partial field, 6×6 matrix)

**Dataset Statistics:**
- Primary input: 6×6 ρ_partial matrix (6 TrustLLM dimensions × 6 dimensions)
- Dimension order: [truthfulness, safety, fairness, robustness, privacy, machine_ethics]
- Underlying models: 16 LLMs from TrustLLM evaluation (Sun et al., ICML 2024)
- Sample size note: The 6×6 matrix is deterministic given H-E1 output; no sampling variance
- Optional HELM replication: 30 models × 7 metrics leaderboard (https://crfm.stanford.edu/helm/latest/)

**Key pre-confirmed values from H-E1:**
| Dim Pair | ρ_partial | Status |
|----------|-----------|--------|
| truthfulness–fairness | 0.935 | Significant |
| safety–privacy | 0.971 | Significant |
| safety–machine_ethics | 0.841 | Significant |
| fairness–privacy | 0.894 | Significant |
| fairness–machine_ethics | 0.782 | Significant |
| privacy–machine_ethics | 0.859 | Significant |
| safety–robustness | -0.188 | Not significant |
| robustness–all others | -0.188 to +0.221 | Not significant |

**Loading Information** (for Phase 4 download):
- Method: JSON file read (no download needed)
- Identifier: `h-e1/experiment_results_phase3.json` field `rho_partial`
- Code:
  ```python
  import json, numpy as np
  with open("h-e1/experiment_results_phase3.json") as f:
      results = json.load(f)
  rho_partial = np.array(results["rho_partial"])
  dims = ["truthfulness", "safety", "fairness", "robustness", "privacy", "machine_ethics"]
  ```

### Models

#### Baseline Model

**Architecture:** sklearn AgglomerativeClustering (complete or average linkage) — non-Ward baseline for comparison
**Type:** statistical clustering baseline (NOT the proposed method)
**Purpose:** Compare Ward result against alternative linkage to confirm cluster structure is not linkage-specific

**Note:** The H-E1 validation already computed silhouette=0.614 with average-linkage on the same matrix. This serves as the baseline comparator.

**Loading Information** (for Phase 4 download):
- Method: scikit-learn (standard library, no download)
- Identifier: `sklearn.cluster.AgglomerativeClustering`
- Code:
  ```python
  from sklearn.cluster import AgglomerativeClustering
  # Baseline: average linkage (H-E1 result: silhouette=0.614)
  dist_matrix = 1 - rho_partial  # distance from correlation
  np.fill_diagonal(dist_matrix, 0)
  baseline = AgglomerativeClustering(n_clusters=2, metric='precomputed', linkage='average')
  baseline_labels = baseline.fit_predict(dist_matrix)
  ```

#### Proposed Model

**Architecture:** Proposed = scipy Ward-linkage hierarchical clustering on 6×6 ρ_partial distance matrix

**Core Mechanism Implementation:**

```python
# Core Mechanism: Ward-linkage 2-cluster analysis of ρ_partial correlation matrix
# Based on: scipy.cluster.hierarchy docs + sklearn silhouette_score
# Source: H-M3 hypothesis verification (h-e1/experiment_results_phase3.json)

import json, numpy as np
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from scipy.spatial.distance import squareform
from sklearn.metrics import silhouette_score

DIMS = ["truthfulness", "safety", "fairness", "robustness", "privacy", "machine_ethics"]

# PREDICTED cluster membership (pre-specified, BEFORE analysis)
PREDICTED_RLHF_SENSITIVE = {"safety", "machine_ethics"}      # positive ρ, RLHF co-optimized
PREDICTED_RLHF_INSENSITIVE = {"robustness", "privacy"}       # negative/zero ρ with safety

def run_ward_clustering(rho_partial, n_clusters=2):
    """
    Apply Ward hierarchical clustering to 6x6 ρ_partial matrix.
    Ward linkage: minimizes within-cluster variance.
    Input:  rho_partial (6,6) — symmetric partial Spearman correlation matrix
    Output: labels (6,), silhouette_score (float), membership_alignment (int/6)
    """
    # Step 1: Convert ρ to distance matrix (d = 1 - ρ, clipped to [0, 2])
    dist_matrix = np.clip(1 - rho_partial, 0, 2)
    np.fill_diagonal(dist_matrix, 0)

    # Step 2: scipy Ward linkage (accepts precomputed squareform distance)
    condensed = squareform(dist_matrix)
    Z = linkage(condensed, method='ward')

    # Step 3: Cut dendrogram at k=2 clusters
    labels = fcluster(Z, t=n_clusters, criterion='maxclust') - 1  # 0-indexed

    # Step 4: Silhouette score (precomputed distance matrix)
    sil = silhouette_score(dist_matrix, labels, metric='precomputed')

    # Step 5: Map cluster labels to dimension names
    cluster_membership = {DIMS[i]: labels[i] for i in range(len(DIMS))}

    # Step 6: Cluster membership alignment (MUST be done AFTER analysis)
    # Identify which cluster index corresponds to RLHF-sensitive group
    alignment = compute_membership_alignment(cluster_membership)

    return labels, sil, cluster_membership, alignment

def compute_membership_alignment(cluster_membership):
    """
    Count how many dimensions match predicted cluster membership.
    Try both label assignments (0=sensitive or 1=sensitive).
    """
    best = 0
    for sensitive_label in [0, 1]:
        count = 0
        for dim, label in cluster_membership.items():
            if dim in PREDICTED_RLHF_SENSITIVE and label == sensitive_label:
                count += 1
            elif dim in PREDICTED_RLHF_INSENSITIVE and label != sensitive_label:
                count += 1
        best = max(best, count)
    return best  # range: 0-4 (only 4 pre-specified dims; truthfulness/fairness unspecified)
```

### Training Protocol

**From H-E1/H-M1/H-M2 context:** All prior hypotheses use the same TrustLLM ρ_partial matrix. No training involved (pure statistical analysis). Hyperparameters:

**Clustering Configuration:**
- Algorithm: `scipy.cluster.hierarchy.linkage`, method='ward'
- Distance metric: `d = 1 - ρ_partial` (correlation to distance conversion, clipped to [0,2])
- Number of clusters: k=2 (pre-specified from hypothesis)
- Dendrogram cut criterion: `criterion='maxclust'`, t=2
- Random seed: Not applicable (Ward clustering is deterministic)

**Robustness Checks (to run after primary analysis):**
- k-sensitivity: Also compute silhouette for k=3 to confirm k=2 is optimal
- Linkage sensitivity: Run average + complete linkage for comparison
- Distance sensitivity: Try `d = sqrt(1 - ρ²)` as alternative distance metric

**HELM Optional Replication:**
- Source: HELM leaderboard (https://crfm.stanford.edu/helm/latest/)
- Metric mapping: safety→toxicity, fairness→stereotypes/bias, robustness→robustness
- Goal: Check if same sign pattern (safety-ethics positive, safety-robustness negative) appears
- Method: Same Ward clustering on HELM partial correlation matrix

**Seeds:** 1 (N/A — deterministic algorithm)

### Evaluation

**Primary Metric:** Silhouette score for k=2 Ward clustering
- Success threshold: silhouette > 0.3
- Expected from H-E1 (average-linkage): 0.614 — Ward should be similar or higher (Ward minimizes variance)

**Secondary Metric:** Cluster membership alignment score
- Pre-specified dimensions: {safety, machine_ethics} → RLHF-sensitive; {robustness, privacy} → RLHF-insensitive
- Truthfulness and fairness: NOT pre-specified (ambiguous per H-M1/H-M2 evidence)
- Success threshold: ≥4/6 dimensions correctly placed (effectively ≥4/4 pre-specified + 0/2 ambiguous counts as 4/6 minimum)
- Alignment counted over all 6 dimensions using best-of-two label assignment

**Success Criteria:**
```
PRIMARY GATE PASS: silhouette_ward > 0.3
SECONDARY GATE PASS: membership_alignment >= 4/6 dimensions
PoC Pass Condition: silhouette_ward > 0.3 AND membership_alignment >= 4/6
```

**Expected Baseline Performance (from H-E1):**
- Average-linkage silhouette = 0.614 (pre-confirmed)
- Expected Ward silhouette: likely 0.55–0.70 (Ward generally produces similar or better separation)
- Source: h-e1/experiment_results_phase3.json (silhouette field = 0.6141)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: clustering analysis (not classification/regression)
- Library: `sklearn.metrics.silhouette_score`
- Code:
  ```python
  from sklearn.metrics import silhouette_score
  sil = silhouette_score(dist_matrix, labels, metric='precomputed')
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** silhouette_ward vs 0.3 threshold; membership_alignment vs 4/6 threshold (bar chart)

#### Additional Figures (LLM Autonomous)

Based on the hypothesis (clustering structure of correlation matrix), the following additional figures are recommended:

1. **Dendrogram:** scipy dendrogram of Ward linkage on 6 TrustLLM dimensions — shows hierarchical merge order and 2-cluster cut point. Annotate predicted cluster membership with color coding.

2. **ρ_partial Heatmap with Cluster Annotations:** 6×6 heatmap of ρ_partial values, reordered by Ward cluster assignment. Highlight cluster boundaries. Color scale: diverging (red=positive, blue=negative).

3. **Silhouette Comparison Bar Chart:** Ward vs average-linkage (H-E1) vs complete-linkage silhouette scores for k=2.

4. **Cluster Membership Visualization:** 6-dimension scatter plot (2D MDS projection of ρ_partial distance matrix) with Ward cluster colors and predicted membership annotation.

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m3/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `silhouette_ward > 0.3` (proposed_metric > baseline_threshold)
3. `membership_alignment >= 4` (≥4/6 dimensions in predicted clusters)

**Pre-analysis note:** H-E1 silhouette=0.614 with average-linkage strongly suggests Ward will also exceed 0.3. The cluster membership is the more uncertain gate — depends on whether robustness is isolated (H-M2 partial support) and whether privacy clusters with RLHF-insensitive group (H-E1 suggests privacy is highly correlated with safety, ρ=0.971, which may put privacy in RLHF-sensitive cluster instead).

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Query 1: "hierarchical clustering Ward linkage correlation matrix experiment design"**
- Similarity scores: 0.31–0.34 (low relevance)
- Results: pytorch/pytorch issues, huggingface/diffusers, TensorFlow docs — unrelated to clustering
- Insight extracted: None — Archon KB is a diffusion model KB, no clustering content

**Query 2: "silhouette score clustering evaluation LLM benchmark dimensions"**
- Best match: hf.co/papers/2305.14314 (similarity 0.47) — LLM evaluation paper, partial relevance
- Insight extracted: Silhouette score is standard clustering quality metric; no domain-specific guidance for LLM dimension clustering

**Archon Code Examples:**
- Query: "AgglomerativeClustering Ward correlation matrix precomputed Python"
- Results: Incidence matrix LaTeX code (similarity 0.32), CUDA batched solver — completely unrelated
- Insight extracted: None

**Assessment:** Archon KB (diffusion/PyTorch focus) has no relevant content for this statistical analysis task. 3 queries executed, all low relevance (<0.50 similarity). All experiment design grounded in Exa search and prior hypothesis results.

### B. GitHub Implementations (Exa)

**Repository 1: scikit-learn/scikit-learn** (65k stars)
- URL: https://scikit-learn.org/stable/modules/generated/sklearn.cluster.AgglomerativeClustering.html
- Query used: "sklearn AgglomerativeClustering Ward linkage silhouette_score Python"
- Relevance: PRIMARY — defines exact API for Ward clustering
- Key code:
  ```python
  # Ward linkage: metric must be 'euclidean' (NOT 'precomputed')
  AgglomerativeClustering(n_clusters=2, linkage='ward', metric='euclidean')
  ```
- Critical constraint extracted: Ward + precomputed NOT supported in sklearn (issue #27655)
- Used for: Architecture decision → use scipy instead

**Repository 2: sklearn silhouette_score** (scikit-learn.org)
- URL: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html
- Query used: "sklearn AgglomerativeClustering Ward linkage silhouette_score Python"
- Relevance: HIGH — defines silhouette_score API with precomputed support
- Key code:
  ```python
  silhouette_score(X, labels, metric='precomputed')  # Supports precomputed distances
  ```
- Used for: Evaluation metrics implementation

**Repository 3: scikit-learn/scikit-learn issue #27655**
- URL: https://github.com/scikit-learn/scikit-learn/issues/27655
- Relevance: HIGH — confirms Ward + precomputed limitation; guides scipy approach
- Key insight: Use scipy.cluster.hierarchy.linkage(squareform, method='ward') instead
- Used for: Implementation path decision

**Repository 4: bitsnaps gist (AgglomerativeClustering + silhouette)**
- URL: https://gist.github.com/bitsnaps/12415200fc62539fff852a1b46168d0a
- Key code pattern:
  ```python
  clusterer = AgglomerativeClustering(n_clusters=n_clusters, linkage='ward')
  y_predict = clusterer.fit_predict(X)
  silhouette_avg = silhouette_score(X, cluster_labels)
  ```
- Used for: Pseudo-code pattern (adapted to precomputed distance via scipy)

**Repository 5: HowieHwong/TrustLLM** (622 stars, ICML 2024)
- URL: https://github.com/HowieHwong/TrustLLM
- 6 dimensions: truthfulness, safety, fairness, robustness, privacy, machine_ethics
- No clustering analysis by authors — H-M3 is novel
- Pre-computed ρ_partial available from H-E1
- Used for: Dataset confirmation and dimension ordering

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results was sufficiently clear for this pure statistical analysis (6×6 matrix Ward clustering). No complex custom code to analyze.

### D. Previous Hypothesis Context

**Source:** H-E1 validation (h-e1/experiment_results_phase3.json) + H-M1 (h-m1/04_validation.md) + H-M2 (h-m2/04_validation.md)

**Reused Components:**
- ρ_partial matrix (6×6): Direct input to H-M3 clustering (h-e1/experiment_results_phase3.json)
- Dimension order: [truthfulness, safety, fairness, robustness, privacy, machine_ethics]
- Baseline silhouette: 0.614 (average-linkage, H-E1) — comparator for Ward result
- RLHF co-movement evidence: H-M1 confirms safety-machine_ethics cluster (ρ=0.841)
- Robustness isolation: H-M2 confirms robustness Δ≤0 for RLHF (negative directional)

**Why Reused:** H-M3 is the culminating test — it directly uses the ρ_partial matrix computed in H-E1 to verify that the combined mechanism from H-M1+H-M2 produces the predicted 2-cluster structure. No re-computation of correlations needed.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (ρ_partial matrix) | Prior hypothesis | H-E1 (h-e1/experiment_results_phase3.json) |
| Dimension ordering | TrustLLM paper | HowieHwong/TrustLLM (B.5) |
| Ward linkage implementation | scipy docs | scipy.cluster.hierarchy (B.1, B.3) |
| Ward + precomputed workaround | sklearn GitHub issue | scikit-learn #27655 (B.3) |
| Silhouette score implementation | sklearn docs | sklearn.metrics.silhouette_score (B.2) |
| Baseline silhouette (0.614) | Prior hypothesis | H-E1 validation results (D.1) |
| Predicted cluster membership | Phase 2B hypothesis | 02b_verification_plan.md H-M3 section |
| Distance metric (1-ρ) | Standard practice | sklearn clustering docs (B.1) |
| RLHF-sensitive cluster prediction | Prior hypotheses | H-M1 (safety+ethics), H-M2 (robustness) (D.1) |
| Success threshold (silhouette>0.3) | Phase 2B gate | 02b_verification_plan.md H-M3 section |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-04

### Workflow History for This Hypothesis

- 2026-08-04T07:40:00Z: h-m3 set to IN_PROGRESS (Hypothesis Loop)
- 2026-08-04: Phase 2C experiment design IN_PROGRESS

---

*MCP Tools Used: Archon (Knowledge ×2 + Code ×1, all low relevance — diffusion KB), Exa (primary: sklearn docs, scipy clustering, scikit-learn #27655, TrustLLM GitHub), Serena (skipped — code clear)*
*All specifications grounded in researched implementations and prior hypothesis results*
*Next Phase: Phase 3 — Implementation Planning*
