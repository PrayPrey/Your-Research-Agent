# Experiment Design Specification: h-m1 Cluster Stability Validation

**Hypothesis ID**: h-m1  
**Hypothesis Type**: MECHANISM  
**Gate**: MUST_WORK  
**Date**: 2026-08-28  
**Phase**: 2C Experiment Design  

---

## 1. Hypothesis Statement

Hierarchical clustering (Ward linkage) applied to correlation matrices identifies 2-5 distinct failure mode clusters with silhouette score > 0.5 and ≥80% bootstrap consistency (1000 iterations).

**Rationale** (from verification plan):  
Validates that observed correlations (h-e1: r > 0.99) cluster into stable failure modes representing shared root causes rather than noise.

**Prerequisites**: h-e1 (VALIDATED - correlation significance confirmed)

---

## 2. Research Context

### 2.1 Archon KB Findings

*MCP unavailable - using verification plan knowledge base*

**Key insights from verification plan (lines 136-254)**:
- Hierarchical clustering (Ward linkage) standard for correlation matrix analysis
- Bootstrap resampling (1000 iterations) validates cluster stability
- Silhouette score > 0.5 indicates good cluster separation
- Cophenetic correlation + elbow method for cluster count selection
- Stratification by model size prepares for h-m4 scale invariance test

**Related hypotheses**:
- h-e1: Validated correlation significance (all pairs r > 0.99, p < 1e-17)
- h-m2: Will validate permutation significance (downstream)
- h-m4: Will test scale invariance via Mantel test (requires stratified clustering)

### 2.2 Exa Implementation Search

*MCP unavailable - using standard ML libraries*

**Standard implementations**:
- `scipy.cluster.hierarchy.linkage` (Ward method)
- `scipy.cluster.hierarchy.dendrogram` (visualization)
- `scipy.cluster.hierarchy.fcluster` (cut dendrogram)
- `sklearn.metrics.silhouette_score` (cluster quality)
- `scipy.cluster.hierarchy.cophenet` (dendrogram quality)

**Bootstrap validation pattern** (standard approach):
```python
def bootstrap_cluster_consistency(data, n_iterations=1000):
    # Resample with replacement
    # Apply clustering to each sample
    # Track cluster assignment consistency
    # Return % of samples with stable assignments
```

### 2.3 Codebase Analysis

**Available from h-e1**:
- `h-e1/data/benchmark_scores.csv` (20 models × 3 benchmarks)
- `h-e1/results/correlation_results.json` (correlation matrix validated)
- `h-e1/code/correlation_analysis.py` (correlation computation)

**Reusable components**:
- Model stratification logic (small/medium/large)
- Benchmark score preprocessing
- Gate metric computation pattern

**h-m1 additions needed**:
- Clustering module (`clustering_analysis.py`)
- Bootstrap validation (`bootstrap.py`)
- Cluster quality metrics (`cluster_metrics.py`)
- Dendrogram visualization

---

## 3. Dataset Specification

### 3.1 Dataset Selection

**Dataset Type**: `standard` (reuse h-e1 validated data)

**Dataset Name**: LLM Multi-Benchmark Correlation Matrix

**Source**: h-e1 validated correlation results
- Input: `h-e1/data/benchmark_scores.csv` (20 models × 3 benchmarks)
- Derived: 3×3 correlation matrix from pairwise Spearman correlations

**Justification**:
- Real data (not synthetic) with validated correlation structure (h-e1 PASS)
- Sufficient sample size (20 models across 3 size strata)
- Matches verification plan requirements (Section 2.2, H-M1 protocol)

### 3.2 Data Preparation Steps

**Step 1: Load h-e1 correlation matrix**
```python
# Input: h-e1/results/correlation_results.json
# Extract 3×3 correlation matrix for clustering
# Format: symmetric matrix [TruthfulQA, AdvBench, BOLD]
```

**Step 2: Compute pairwise distance matrix**
```python
# Convert correlation to distance: d = 1 - |r|
# Distance matrix used for hierarchical clustering
```

**Step 3: Stratify by model size**
```python
# Split models into small/medium/large strata
# Prepare stratified correlation matrices for h-m4
```

**Step 4: Validate data quality**
```python
# Check for missing values (none expected from h-e1)
# Verify symmetric correlation matrix
# Confirm positive semi-definite property
```

**Expected Data Shape**:
- Full correlation matrix: 3×3 (3 benchmarks)
- Stratified matrices: 3×3 per stratum (small/medium/large)
- Distance matrix: 3×3 derived from correlations

**Cache Path**: `h-m1/data/correlation_distance_matrix.npy`

**Preprocessing Time Estimate**: <1 minute (simple transformation)

### 3.3 Data Quality Assurance

**Validation checks**:
1. Correlation matrix is symmetric
2. Diagonal elements = 1.0
3. All correlations in [-1, 1] range
4. Distance matrix positive semi-definite
5. Sufficient models per stratum (≥5 per stratum verified in h-e1)

**Expected statistics** (from h-e1 results):
- Mean correlation: 0.996
- Min correlation: 0.993
- All correlations significant (p < 1e-17 after Bonferroni)

---

## 4. Baseline Experiments

### 4.1 Experiment 1: Ward Linkage Clustering

**Objective**: Apply hierarchical clustering to correlation matrix and identify optimal cluster count.

**Method**: Ward linkage minimizes within-cluster variance.

**Algorithm**:
```python
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from scipy.spatial.distance import squareform

# Convert correlation to distance
distance_matrix = 1 - abs(correlation_matrix)
condensed_distance = squareform(distance_matrix)

# Apply Ward linkage
Z = linkage(condensed_distance, method='ward')

# Cut dendrogram for k=2 to k=5 clusters
for k in range(2, 6):
    cluster_labels = fcluster(Z, k, criterion='maxclust')
    # Store labels for validation
```

**Expected Output**:
- Dendrogram linkage matrix (Z)
- Cluster assignments for k=2,3,4,5
- Cophenetic correlation coefficient (target >0.7)

**Success Metric**: Dendrogram produces valid clusters for k=2-5.

---

### 4.2 Experiment 2: Silhouette Score Evaluation

**Objective**: Measure cluster separation quality for each k.

**Method**: Silhouette score ranges from -1 (poor) to 1 (excellent).

**Algorithm**:
```python
from sklearn.metrics import silhouette_score

silhouette_scores = {}
for k in range(2, 6):
    cluster_labels = fcluster(Z, k, criterion='maxclust')
    score = silhouette_score(distance_matrix, cluster_labels, metric='precomputed')
    silhouette_scores[k] = score
```

**Expected Output**:
- Silhouette scores for k=2,3,4,5
- Optimal k selection (highest silhouette score)

**Success Criterion**: At least one k in [2,5] achieves silhouette score > 0.5.

---

### 4.3 Experiment 3: Bootstrap Consistency Validation

**Objective**: Validate cluster stability via 1000 bootstrap iterations.

**Method**: Resample models with replacement, recompute correlations and clustering, track consistency.

**Algorithm**:
```python
def bootstrap_clustering(benchmark_data, n_iterations=1000, optimal_k=3):
    consistency_matrix = np.zeros((n_benchmarks, n_benchmarks))
    
    for iteration in range(n_iterations):
        # Resample models with replacement
        resampled_data = benchmark_data.sample(n=len(benchmark_data), replace=True)
        
        # Recompute correlations
        resampled_corr = compute_correlation_matrix(resampled_data)
        
        # Apply clustering
        resampled_clusters = cluster_correlation_matrix(resampled_corr, k=optimal_k)
        
        # Track cluster co-occurrence
        for i, j in combinations(range(n_benchmarks), 2):
            if resampled_clusters[i] == resampled_clusters[j]:
                consistency_matrix[i, j] += 1
    
    # Convert to percentage
    consistency_pct = consistency_matrix / n_iterations * 100
    return consistency_pct
```

**Expected Output**:
- Consistency matrix (3×3) showing % of iterations where benchmark pairs co-cluster
- Mean consistency percentage across all pairs

**Success Criterion**: Mean consistency ≥80% across all benchmark pairs.

---

### 4.4 Experiment 4: Stratified Clustering Analysis

**Objective**: Prepare for h-m4 scale invariance test by clustering each size stratum.

**Method**: Apply Ward linkage separately to small/medium/large model correlations.

**Algorithm**:
```python
for stratum in ['small', 'medium', 'large']:
    stratum_data = benchmark_data[benchmark_data['size_stratum'] == stratum]
    stratum_corr = compute_correlation_matrix(stratum_data)
    stratum_clusters = cluster_correlation_matrix(stratum_corr, k=optimal_k)
    # Store for h-m4 Mantel test
```

**Expected Output**:
- Cluster assignments for each stratum
- Visual comparison of cluster structures across strata

**Success Metric**: Cluster structures visually similar across strata (qualitative preparation for h-m4 Mantel test).

---

## 5. Implementation Requirements

### 5.1 Code Structure

```
h-m1/
├── code/
│   ├── config.py                  # Clustering parameters
│   ├── preprocessing.py           # Load h-e1 data, compute distance matrix
│   ├── clustering_analysis.py     # Ward linkage, cluster assignment
│   ├── cluster_metrics.py         # Silhouette score, cophenetic correlation
│   ├── bootstrap.py               # Bootstrap consistency validation
│   ├── visualizations.py          # Dendrogram, silhouette plots
│   └── main.py                    # Orchestrate all experiments
├── data/
│   ├── correlation_distance_matrix.npy
│   └── stratified_correlations/   # Small/medium/large matrices
├── results/
│   ├── clustering_results.json    # Cluster assignments, silhouette scores
│   ├── bootstrap_consistency.json # Consistency matrix, mean %
│   └── dendrogram.png             # Visualization
└── 04_validation.md               # Validation report
```

### 5.2 Dependencies

**Core libraries**:
- `scipy.cluster.hierarchy` (linkage, dendrogram, fcluster, cophenet)
- `scipy.spatial.distance` (squareform)
- `sklearn.metrics` (silhouette_score)
- `numpy`, `pandas` (data manipulation)
- `matplotlib`, `seaborn` (visualization)

**Reused from h-e1**:
- `correlation_analysis.py` (correlation computation)
- `benchmark_scores.csv` (20 models × 3 benchmarks)

### 5.3 Compute Requirements

**Expected runtime**:
- Exp 1 (Ward linkage): <1 second
- Exp 2 (Silhouette score): <1 second
- Exp 3 (Bootstrap 1000 iterations): 5-10 minutes
- Exp 4 (Stratified clustering): <5 seconds

**Total estimate**: ~10 minutes on standard CPU

**Memory**: <100 MB (small correlation matrices)

---

## 6. Validation Protocol

### 6.1 Success Criteria (from verification plan)

**Primary** (Gate: MUST_WORK):
1. Silhouette score > 0.5 for at least one k in [2,5]
2. Bootstrap consistency ≥80% across all benchmark pairs
3. 2-5 distinct clusters identified

**Secondary**:
1. Cophenetic correlation > 0.7 (dendrogram quality)
2. Cluster structures consistent across size strata (visual check)

### 6.2 Gate Decision Logic

**PASS conditions** (all must hold):
- `max(silhouette_scores.values()) > 0.5`
- `mean_bootstrap_consistency >= 80.0`
- `2 <= optimal_k <= 5`

**FAIL conditions** (any triggers PIVOT):
- `max(silhouette_scores.values()) <= 0.5` → Clusters poorly separated
- `mean_bootstrap_consistency < 80.0` → Clusters unstable
- No valid k in [2,5] produces interpretable clusters

**PIVOT action**: Revise clustering approach (try different linkage methods, check for outliers)

### 6.3 Falsification Criteria

From verification plan (lines 196-222):

**If silhouette < 0.5**:
- Correlations exist (h-e1 validated) but don't form stable clusters
- Implies no distinct failure mode taxonomy
- Reject hierarchical clustering approach

**If bootstrap consistency < 80%**:
- Cluster assignments unstable across resampling
- Implies clustering captures noise, not structure
- Reject current methodology

**If no clusters in [2,5] range**:
- Taxonomy too coarse (k=1) or too fragmented (k>5)
- Implies correlation structure doesn't match hypothesis

---

## 7. Experiment Execution Plan

### 7.1 Execution Order

**Phase 1: Data Preparation** (15 minutes)
1. Load h-e1 correlation results
2. Compute distance matrix
3. Stratify by model size
4. Validate data quality

**Phase 2: Core Clustering** (30 minutes)
1. Run Experiment 1 (Ward linkage)
2. Run Experiment 2 (Silhouette scores)
3. Select optimal k
4. Generate dendrogram visualization

**Phase 3: Stability Validation** (2 hours)
1. Run Experiment 3 (Bootstrap 1000 iterations)
2. Compute consistency matrix
3. Validate against 80% threshold

**Phase 4: Stratified Analysis** (30 minutes)
1. Run Experiment 4 (Stratified clustering)
2. Compare cluster structures across strata
3. Prepare for h-m4

**Total duration**: ~3 hours

### 7.2 Deliverables

**Code deliverables**:
1. `clustering_analysis.py` (Ward linkage implementation)
2. `bootstrap.py` (1000-iteration validation)
3. `cluster_metrics.py` (Silhouette, cophenetic correlation)
4. `main.py` (orchestration script)

**Data deliverables**:
1. `correlation_distance_matrix.npy`
2. `clustering_results.json` (cluster assignments, silhouette scores)
3. `bootstrap_consistency.json` (consistency matrix)

**Analysis deliverables**:
1. `04_validation.md` (validation report)
2. `dendrogram.png` (cluster visualization)
3. Gate decision (PASS/FAIL with metrics)

---

## 8. Next Steps

**Immediate actions**:
1. **Phase 3 Implementation Planning**: Use `/phase3-implementation-planning` to generate PRD, Architecture, PRP
2. **Archon Task Creation**: Initialize Archon project for h-m1 implementation
3. **Phase 4 Coding**: Execute Coder-Validator loop to implement experiments

**Downstream dependencies**:
- h-m2 (permutation test) depends on h-m1 cluster identification
- h-m4 (scale invariance) depends on h-m1 stratified clustering

**Expected outcome**:
- If PASS: 2-5 stable failure mode clusters identified with >0.5 silhouette and ≥80% bootstrap consistency
- If FAIL: PIVOT to alternative clustering methods or refine correlation analysis

---

## 9. Risk Mitigation

**Risk R5: Cluster Count Subjectivity** (from verification plan, line 288):
- Mitigation: Use triangulation (silhouette + cophenetic + elbow method)
- Validation: Multiple indices must agree on optimal k

**Risk R2: Confound Conflation** (from verification plan, line 266):
- Mitigation: Stratified clustering (Experiment 4) prepares for h-m4 Mantel test
- Validation: If clusters differ across strata, h-m4 will detect via Mantel r < 0.7

**Data quality risks**:
- h-e1 validation confirmed no missing values, all correlations significant
- Distance matrix validation checks positive semi-definite property

---

## 10. References

**Verification plan sections**:
- Section 2.2: H-M1 specification (lines 136-163)
- Section 3.1: Risk R5 (cluster subjectivity, lines 288-294)
- Section 4.2: Phase 2 mechanism validation (lines 373-382)

**Related experiments**:
- h-e1: Correlation significance (prerequisite, VALIDATED)
- h-m2: Permutation test (downstream)
- h-m4: Scale invariance via Mantel test (downstream)

**Standard methods**:
- Ward linkage: `scipy.cluster.hierarchy.linkage`
- Silhouette score: `sklearn.metrics.silhouette_score`
- Bootstrap resampling: Standard ML validation technique

---

**Experiment design completed**: 2026-08-28  
**Ready for Phase 3 (Implementation Planning)**: Yes  
**Estimated implementation tier**: Tier 1 (standard clustering algorithms, no custom architectures)  
**Estimated task budget**: 10-12 tasks (data prep + 4 experiments + validation + visualization)
