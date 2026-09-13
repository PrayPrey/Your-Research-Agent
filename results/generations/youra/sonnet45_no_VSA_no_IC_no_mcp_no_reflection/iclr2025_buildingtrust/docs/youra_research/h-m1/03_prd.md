# Product Requirements Document: h-m1 Cluster Stability Validation

**Hypothesis ID**: h-m1  
**Type**: MECHANISM  
**Gate**: MUST_WORK  
**Date**: 2026-08-28  
**Phase**: 3 Implementation Planning  
**Author**: Anonymous  

---

## Executive Summary

This PRD defines implementation requirements for validating the hypothesis that hierarchical clustering (Ward linkage) applied to correlation matrices identifies 2-5 distinct failure mode clusters with silhouette score > 0.5 and ≥80% bootstrap consistency (1000 iterations). The system will reuse h-e1 validated correlation data (20 models × 3 benchmarks) and apply Ward linkage clustering with bootstrap validation to demonstrate stable failure mode taxonomy.

**Prerequisites**: h-e1 (VALIDATED - correlation significance confirmed, r > 0.99, p < 1e-17)

**Key Deliverables**:
- Hierarchical clustering implementation with Ward linkage
- Silhouette score evaluation for k=2-5 clusters
- Bootstrap consistency validation (1000 iterations)
- Stratified clustering analysis (small/medium/large model strata)
- Dendrogram visualization
- Gate decision report (PASS/FAIL based on metrics)

**Success Criteria** (Gate: MUST_WORK):
1. Silhouette score > 0.5 for at least one k in [2,5]
2. Bootstrap consistency ≥80% across all benchmark pairs
3. 2-5 distinct clusters identified

---

## 1. Problem Statement

### 1.1 Core Challenge

H-e1 validated extremely strong correlations between benchmark failures (r > 0.99), but correlation alone doesn't prove distinct failure modes exist. Clusters could represent:
- Stable taxonomies (desired: 2-5 failure modes with shared root causes)
- Noise amplification (unstable clustering patterns)
- Degenerate structure (all benchmarks cluster together or completely separate)

Without cluster stability validation, we cannot claim failure modes form interpretable categories for downstream analysis (h-m2 permutation test, h-m4 scale invariance).

### 1.2 Current State

**Available from h-e1:**
- `benchmark_scores.csv`: 20 models × 3 benchmarks (TruthfulQA, AdvBench, BOLD)
- `correlation_results.json`: 3×3 correlation matrix (all pairs r > 0.99, p < 1e-17)
- Model stratification: small (7 models), medium (7 models), large (6 models)
- Validated correlation significance with Bonferroni correction

**Missing:**
- Cluster assignments for correlation matrix
- Silhouette score evaluation
- Bootstrap stability validation
- Cophenetic correlation for dendrogram quality
- Stratified clustering for scale invariance preparation (h-m4)

### 1.3 Desired State

**Cluster identification system** that:
1. Applies Ward linkage to correlation-based distance matrix
2. Identifies optimal cluster count (k=2-5) via silhouette score maximization
3. Validates cluster stability through 1000-iteration bootstrap resampling
4. Produces interpretable dendrogram visualization
5. Stratifies clustering by model size for h-m4 preparation
6. Reports gate metrics: silhouette score, bootstrap consistency, cluster count

**Validation outputs:**
- Cluster assignments with quality metrics (silhouette >0.5)
- Bootstrap consistency matrix (≥80% threshold)
- Dendrogram visualization showing hierarchical structure
- Gate decision report (PASS/FAIL with metrics)
- Stratified clustering results for downstream hypotheses

---

## 2. Functional Requirements

### FR-1: Data Loading and Preprocessing

**Priority**: P0 (MUST_HAVE)  
**Dependency**: h-e1 validated data  

**Requirements**:
1. Load h-e1 correlation matrix from `h-e1/results/correlation_results.json`
2. Compute distance matrix: `d = 1 - abs(r)` for hierarchical clustering
3. Validate correlation matrix properties:
   - Symmetric matrix (3×3)
   - Diagonal elements = 1.0
   - All correlations in [-1, 1]
   - Distance matrix positive semi-definite
4. Load model stratification (small/medium/large) from h-e1
5. Compute stratified correlation matrices for each size stratum

**Acceptance Criteria**:
- Distance matrix successfully computed from h-e1 correlations
- Data quality checks pass (symmetric, valid range, no missing values)
- Stratified matrices prepared for 3 size strata
- Cache distance matrix to `h-m1/data/correlation_distance_matrix.npy`

**Test Cases**:
- Distance matrix elements in [0, 2] range (from correlations in [-1, 1])
- Symmetric property preserved after transformation
- Each stratum has ≥5 models (verified in h-e1)

---

### FR-2: Ward Linkage Clustering

**Priority**: P0 (MUST_HAVE)  
**Dependency**: FR-1 (distance matrix)  

**Requirements**:
1. Apply Ward linkage using `scipy.cluster.hierarchy.linkage`
2. Generate dendrogram linkage matrix for visualization
3. Cut dendrogram for k=2,3,4,5 cluster solutions using `fcluster`
4. Compute cophenetic correlation coefficient (target >0.7)
5. Store cluster assignments for each k value

**Acceptance Criteria**:
- Valid linkage matrix produced for dendrogram visualization
- Cluster assignments generated for k=2-5
- Cophenetic correlation >0.7 (dendrogram faithfully represents distances)
- No degenerate clusters (empty or all-inclusive)

**Test Cases**:
- Each k produces exactly k distinct clusters
- Cluster sizes balanced (no singleton clusters for k<5)
- Cophenetic correlation ≥0.7 threshold

---

### FR-3: Silhouette Score Evaluation

**Priority**: P0 (MUST_HAVE)  
**Dependency**: FR-2 (cluster assignments)  

**Requirements**:
1. Compute silhouette score for each k in [2,5] using `sklearn.metrics.silhouette_score`
2. Use precomputed distance matrix as metric
3. Identify optimal k (highest silhouette score)
4. Validate at least one k achieves silhouette >0.5
5. Store silhouette scores for all k values

**Acceptance Criteria**:
- Silhouette scores computed for k=2,3,4,5
- Optimal k identified and stored
- **Gate criterion**: `max(silhouette_scores) > 0.5`
- Silhouette values in [-1, 1] range

**Test Cases**:
- Silhouette score increases with better separation
- Score >0.5 indicates good cluster quality
- Optimal k selection automated (not hardcoded)

---

### FR-4: Bootstrap Consistency Validation

**Priority**: P0 (MUST_HAVE)  
**Dependency**: FR-2, FR-3 (optimal k selection)  

**Requirements**:
1. Implement bootstrap resampling with 1000 iterations
2. For each iteration:
   - Resample models with replacement
   - Recompute pairwise correlations
   - Apply Ward linkage with optimal k
   - Track cluster co-occurrence for benchmark pairs
3. Compute consistency matrix: % of iterations where pairs co-cluster
4. Calculate mean consistency across all pairs
5. Validate mean consistency ≥80% threshold

**Acceptance Criteria**:
- 1000 bootstrap iterations executed successfully
- Consistency matrix (3×3) produced showing co-occurrence percentages
- **Gate criterion**: `mean_consistency >= 80.0%`
- Runtime ≤10 minutes on standard CPU

**Test Cases**:
- Bootstrap samples have same size as original (n=20 models)
- Consistency percentages in [0, 100] range
- Mean consistency aggregation correct

---

### FR-5: Stratified Clustering Analysis

**Priority**: P1 (SHOULD_HAVE)  
**Dependency**: FR-2 (clustering implementation)  

**Requirements**:
1. Apply Ward linkage separately to small/medium/large model strata
2. Use optimal k from full-dataset clustering
3. Compare cluster structures across strata (visual check)
4. Store stratified cluster assignments for h-m4 Mantel test
5. Flag if cluster structures differ significantly across strata

**Acceptance Criteria**:
- Clustering applied to 3 size strata independently
- Stratified results stored for h-m4 downstream validation
- Visual comparison shows qualitative similarity (or flags differences)
- Prepares for h-m4 scale invariance test (Mantel r >0.7 target)

**Test Cases**:
- Each stratum has ≥5 models (sufficient for clustering)
- Cluster assignments valid for each stratum
- Stratified results cached for h-m4

---

### FR-6: Dendrogram Visualization

**Priority**: P1 (SHOULD_HAVE)  
**Dependency**: FR-2 (linkage matrix)  

**Requirements**:
1. Generate dendrogram using `scipy.cluster.hierarchy.dendrogram`
2. Annotate with benchmark labels (TruthfulQA, AdvBench, BOLD)
3. Mark optimal k cluster cut on dendrogram
4. Save high-resolution figure to `h-m1/results/dendrogram.png`
5. Include cophenetic correlation in figure caption

**Acceptance Criteria**:
- Dendrogram clearly shows hierarchical structure
- Optimal k cluster cut visually marked
- Benchmark labels readable
- Figure suitable for paper inclusion

**Test Cases**:
- Dendrogram matches linkage matrix structure
- Cluster cut corresponds to optimal k
- Labels correctly map to benchmarks

---

### FR-7: Gate Decision Validation

**Priority**: P0 (MUST_HAVE)  
**Dependency**: FR-3, FR-4 (metrics computed)  

**Requirements**:
1. Evaluate gate criteria:
   - `max(silhouette_scores) > 0.5`
   - `mean_bootstrap_consistency >= 80.0`
   - `2 <= optimal_k <= 5`
2. Generate validation report with:
   - Gate decision (PASS/FAIL)
   - All metric values
   - Cluster assignments
   - Failure mode interpretation (if PASS)
3. Save report to `h-m1/04_validation.md`
4. Update verification_state.yaml with validation status

**Acceptance Criteria**:
- Gate decision automated from metrics (no manual override)
- **PASS conditions**: All 3 criteria satisfied
- **FAIL conditions**: Any criterion violated
- Validation report includes metric evidence

**Test Cases**:
- PASS triggers if silhouette=0.6, consistency=85%, k=3
- FAIL triggers if silhouette=0.4 (below threshold)
- FAIL triggers if consistency=75% (below threshold)
- FAIL triggers if optimal k=1 or k=6 (out of range)

---

## 3. Non-Functional Requirements

### NFR-1: Performance

**Requirement**: Total runtime ≤15 minutes on standard CPU (excluding bootstrap)  
**Critical Path**: Bootstrap validation (1000 iterations) ~10 minutes  
**Optimization**: Use vectorized NumPy operations for correlation computation  

**Targets**:
- Data preprocessing: <1 minute
- Ward linkage clustering: <1 second
- Silhouette score evaluation: <1 second
- Bootstrap 1000 iterations: 5-10 minutes
- Stratified clustering: <5 seconds

### NFR-2: Reproducibility

**Requirement**: Bit-exact reproducibility with fixed random seed  
**Implementation**:
- Set `np.random.seed(42)` for bootstrap resampling
- Document scipy/sklearn versions in requirements.txt
- Cache intermediate results (distance matrix, linkage matrix)

**Validation**: Re-running produces identical cluster assignments and metrics

### NFR-3: Scalability Readiness

**Current Scale**: 3 benchmarks (3×3 correlation matrix)  
**Future Scale**: Up to 10 benchmarks (10×10 matrix) for extended analysis  
**Requirement**: Code structure supports variable benchmark count without modification  

**Design**: Parameterize `n_benchmarks` in config, avoid hardcoded array sizes

### NFR-4: Code Reusability

**Requirement**: Modular design for reuse in h-m2, h-m4 downstream hypotheses  
**Key Components**:
- `clustering_analysis.py`: Reusable for different linkage methods (h-m2 may try alternatives)
- `bootstrap.py`: Generic bootstrap framework for other stability tests
- `cluster_metrics.py`: Silhouette/cophenetic functions for quality assessment

**Integration**: h-m4 Mantel test will import stratified clustering from h-m1

---

## 4. Data Requirements

### 4.1 Input Data

**Source**: h-e1 validated benchmark results  

| Data Asset | Path | Format | Size | Description |
|------------|------|--------|------|-------------|
| Benchmark scores | `h-e1/data/benchmark_scores.csv` | CSV | 20 rows × 4 cols | Model scores across 3 benchmarks + size stratum |
| Correlation matrix | `h-e1/results/correlation_results.json` | JSON | 3×3 | Pairwise Spearman correlations (r > 0.99) |
| Model stratification | Embedded in scores CSV | Column | 3 strata | small/medium/large size groups |

**Quality Assurance** (inherited from h-e1):
- No missing values
- All correlations significant (p < 1e-17 after Bonferroni)
- Sufficient models per stratum (≥5)

### 4.2 Derived Data

**Artifacts to generate:**

| Artifact | Path | Format | Description |
|----------|------|--------|-------------|
| Distance matrix | `h-m1/data/correlation_distance_matrix.npy` | NumPy array (3×3) | `d = 1 - abs(r)` |
| Stratified correlations | `h-m1/data/stratified_correlations/` | NPY files | Per-stratum 3×3 matrices |

**Caching Strategy**: Save distance matrix to avoid recomputation in ablations

### 4.3 Output Data

**Results artifacts:**

| Output | Path | Format | Description |
|--------|------|--------|-------------|
| Clustering results | `h-m1/results/clustering_results.json` | JSON | Cluster assignments, silhouette scores, optimal k |
| Bootstrap consistency | `h-m1/results/bootstrap_consistency.json` | JSON | 3×3 consistency matrix, mean % |
| Dendrogram | `h-m1/results/dendrogram.png` | PNG | Hierarchical clustering visualization |
| Validation report | `h-m1/04_validation.md` | Markdown | Gate decision, metrics, interpretation |

---

## 5. Evaluation Metrics

### 5.1 Primary Metrics (Gate Criteria)

| Metric | Target | Measurement | Falsification |
|--------|--------|-------------|---------------|
| **Silhouette score** | >0.5 | `sklearn.metrics.silhouette_score` | ≤0.5 → Poor cluster separation |
| **Bootstrap consistency** | ≥80% | Mean % across 1000 iterations | <80% → Unstable clusters |
| **Cluster count** | [2, 5] | Optimal k from silhouette maximization | k<2 or k>5 → Invalid taxonomy |

**Gate Decision Logic**:
```python
PASS = (max(silhouette_scores) > 0.5 
        AND mean_bootstrap_consistency >= 80.0 
        AND 2 <= optimal_k <= 5)
```

### 5.2 Secondary Metrics

| Metric | Target | Purpose |
|--------|--------|---------|
| Cophenetic correlation | >0.7 | Dendrogram quality (how well it preserves distances) |
| Cluster size balance | No singletons for k<5 | Avoid degenerate clusters |
| Stratified consistency | Visual similarity | Prepare h-m4 scale invariance test |

### 5.3 Ablation Studies

**Optional investigations** (if time permits):
1. Linkage method comparison: Ward vs Average vs Complete linkage
2. Distance metric sensitivity: `1 - abs(r)` vs `1 - r` (unsigned vs signed)
3. Bootstrap sample size: 500 vs 1000 vs 2000 iterations

**Purpose**: Validate Ward linkage superiority, inform h-m2 permutation test design

---

## 6. Dependencies

### 6.1 External Dependencies

**Python libraries** (standard scientific stack):
- `scipy>=1.7.0` (cluster.hierarchy for linkage, dendrogram, fcluster, cophenet)
- `scikit-learn>=1.0.0` (metrics.silhouette_score)
- `numpy>=1.21.0` (array operations, random seeding)
- `pandas>=1.3.0` (data loading, stratification)
- `matplotlib>=3.4.0` (dendrogram visualization)
- `seaborn>=0.11.0` (enhanced plotting aesthetics)

**No custom models or pretrained weights required** (analysis-only hypothesis)

### 6.2 Internal Dependencies

**Prerequisite hypothesis:**
- **h-e1** (VALIDATED): Provides correlation matrix, benchmark scores, model stratification
- Status: PASS (all pairs r > 0.99, p < 1e-17)

**Reusable components from h-e1:**
- Correlation computation logic (if recomputing for bootstrap)
- Model stratification labels
- Gate metric computation pattern

### 6.3 Downstream Dependencies

**Hypotheses depending on h-m1:**
- **h-m2**: Permutation test (requires h-m1 cluster assignments)
- **h-m4**: Scale invariance (requires h-m1 stratified clustering)

**Deliverables for downstream:**
- `clustering_results.json` → h-m2 will permute cluster labels
- `stratified_correlations/` → h-m4 will compute Mantel correlation across strata

---

## 7. Success Criteria

### 7.1 Implementation Success (Phase 4)

**Code deliverables**:
- [ ] `clustering_analysis.py` with Ward linkage implementation
- [ ] `bootstrap.py` with 1000-iteration validation
- [ ] `cluster_metrics.py` with silhouette/cophenetic functions
- [ ] `main.py` orchestration script runs end-to-end

**Unit test coverage**: ≥80% for clustering logic, bootstrap sampling

**Integration test**: Full pipeline executes without errors

### 7.2 Validation Success (Gate: MUST_WORK)

**PASS conditions** (all required):
1. ✅ Silhouette score > 0.5 for at least one k in [2,5]
2. ✅ Bootstrap consistency ≥80% across all benchmark pairs
3. ✅ 2-5 distinct clusters identified
4. ✅ Cophenetic correlation > 0.7 (dendrogram quality)

**FAIL → PIVOT**:
- Silhouette ≤0.5 → Try alternative linkage methods (h-m2 may explore)
- Consistency <80% → Check for outliers, consider robust clustering
- No valid k → Revise correlation approach or accept single failure mode

### 7.3 Documentation Success

**Required artifacts**:
- [ ] `04_validation.md` with gate decision, metrics, cluster interpretation
- [ ] `dendrogram.png` publication-ready figure
- [ ] Updated `verification_state.yaml` with h-m1 status
- [ ] Code docstrings for all public functions

---

## 8. Timeline and Milestones

### Phase 4 Implementation (Estimated 3-4 hours)

**Milestone 1: Data Preparation** (30 min)
- Task 1.1: Load h-e1 correlation matrix
- Task 1.2: Compute distance matrix
- Task 1.3: Validate data quality
- Task 1.4: Stratify by model size

**Milestone 2: Core Clustering** (1 hour)
- Task 2.1: Implement Ward linkage clustering
- Task 2.2: Generate cluster assignments for k=2-5
- Task 2.3: Compute silhouette scores
- Task 2.4: Select optimal k

**Milestone 3: Stability Validation** (1.5 hours)
- Task 3.1: Implement bootstrap resampling loop
- Task 3.2: Run 1000 iterations (~10 min runtime)
- Task 3.3: Compute consistency matrix
- Task 3.4: Validate ≥80% threshold

**Milestone 4: Analysis & Reporting** (1 hour)
- Task 4.1: Generate dendrogram visualization
- Task 4.2: Compute cophenetic correlation
- Task 4.3: Run stratified clustering
- Task 4.4: Write validation report
- Task 4.5: Update verification state

**Total Estimate**: 4 hours implementation + testing

---

## 9. Risks and Mitigations

### Risk R1: Cluster Count Subjectivity

**Description**: Multiple indices (silhouette, cophenetic, elbow) may disagree on optimal k  
**Impact**: Medium (could invalidate cluster interpretation)  
**Mitigation**:
- Use silhouette score as primary criterion (most robust)
- Report all k values with silhouette >0.5 (may have multiple valid solutions)
- Triangulate with cophenetic correlation + dendrogram visual inspection

**Fallback**: If multiple k equally valid, select smallest k (simpler taxonomy)

### Risk R2: Bootstrap Computational Cost

**Description**: 1000 iterations may exceed 10-minute target runtime  
**Impact**: Low (acceptable delay, not a blocker)  
**Mitigation**:
- Vectorize correlation computation (NumPy broadcasting)
- Cache distance matrix per iteration (avoid recomputation)
- Parallelize bootstrap iterations if runtime >15 minutes

**Fallback**: Reduce to 500 iterations if 1000 exceeds 30 minutes

### Risk R3: Degenerate Cluster Structures

**Description**: All benchmarks cluster together (k=1) or completely separate (k=3 with singletons)  
**Impact**: High (invalidates hypothesis, requires PIVOT)  
**Likelihood**: Low (h-e1 showed r > 0.99, strong correlation suggests intermediate structure)  
**Detection**: Cluster size balance check, silhouette score validity  
**Mitigation**: If degenerate, FAIL gate and explore alternative linkage methods in h-m2

### Risk R4: Stratified Clustering Divergence

**Description**: Cluster structures differ across small/medium/large strata  
**Impact**: Medium (suggests scale-dependence, affects h-m4)  
**Detection**: Visual comparison in FR-5  
**Mitigation**: Flag divergence for h-m4 Mantel test (h-m4 designed to detect this)  
**Note**: Not a h-m1 failure, but informs h-m4 interpretation

---

## 10. Out of Scope

**Explicitly excluded from this PRD**:

1. **Alternative clustering methods**: k-means, DBSCAN, spectral clustering (may be explored in h-m2 if Ward fails)
2. **Cluster interpretation**: Labeling failure modes (e.g., "truthfulness deficits" vs "adversarial brittleness") — deferred to paper writing
3. **Permutation testing**: Validating cluster significance against random baselines (h-m2 scope)
4. **Scale invariance**: Mantel test across model size strata (h-m4 scope)
5. **Extended benchmarks**: Adding more than 3 benchmarks (future work)
6. **Model-level clustering**: Clustering 20 models instead of 3 benchmarks (different analysis)

**Scope boundaries**:
- This PRD focuses on **benchmark-level clustering** only (3×3 correlation matrix)
- Bootstrap validates **cluster stability**, not statistical significance (h-m2 handles significance)
- Stratified analysis is **preparation for h-m4**, not a h-m1 gate criterion

---

## 11. Glossary

| Term | Definition |
|------|------------|
| **Ward linkage** | Hierarchical clustering method minimizing within-cluster variance |
| **Silhouette score** | Cluster quality metric [-1, 1]; >0.5 indicates good separation |
| **Bootstrap consistency** | % of bootstrap iterations where benchmark pairs co-cluster |
| **Cophenetic correlation** | Dendrogram quality metric; >0.7 indicates faithful distance representation |
| **Dendrogram** | Tree diagram showing hierarchical clustering structure |
| **Condensed distance matrix** | Upper-triangular distance matrix (scipy format) |
| **Stratification** | Grouping models by size (small/medium/large) for scale invariance analysis |
| **Gate criterion** | Pass/fail threshold for hypothesis validation (MUST_WORK) |

---

## Appendix A: Data Schema

### A.1 Correlation Matrix (Input)

```json
{
  "correlation_matrix": [
    [1.000, 0.996, 0.993],  // TruthfulQA vs [TruthfulQA, AdvBench, BOLD]
    [0.996, 1.000, 0.997],  // AdvBench vs [TruthfulQA, AdvBench, BOLD]
    [0.993, 0.997, 1.000]   // BOLD vs [TruthfulQA, AdvBench, BOLD]
  ],
  "benchmarks": ["TruthfulQA", "AdvBench", "BOLD"],
  "p_values": [[0.0, 1.2e-18, 3.4e-17], ...],  // All < 0.0033 after Bonferroni
  "sample_size": 20
}
```

### A.2 Clustering Results (Output)

```json
{
  "linkage_matrix": [...],  // (n-1) × 4 array from scipy
  "cluster_assignments": {
    "k=2": [1, 1, 2],  // Example: TruthfulQA+AdvBench vs BOLD
    "k=3": [1, 2, 3],
    "k=4": [1, 2, 3, 3],
    "k=5": [1, 2, 3, 4, 5]
  },
  "silhouette_scores": {
    "k=2": 0.65,
    "k=3": 0.58,
    "k=4": 0.42,
    "k=5": 0.31
  },
  "optimal_k": 2,
  "cophenetic_correlation": 0.87
}
```

### A.3 Bootstrap Consistency (Output)

```json
{
  "consistency_matrix": [
    [100.0, 92.3, 15.7],  // TruthfulQA co-cluster % with [TruthfulQA, AdvBench, BOLD]
    [92.3, 100.0, 18.2],  // AdvBench co-cluster %
    [15.7, 18.2, 100.0]   // BOLD co-cluster %
  ],
  "mean_consistency": 85.4,
  "gate_threshold": 80.0,
  "gate_pass": true,
  "n_iterations": 1000,
  "random_seed": 42
}
```

---

**Document Status**: DRAFT  
**Next Phase**: Phase 3 Architecture Design  
**Estimated Tier**: Tier 1 (Standard ML algorithms, no custom architectures)  
**Estimated Task Budget**: 10-12 tasks  
