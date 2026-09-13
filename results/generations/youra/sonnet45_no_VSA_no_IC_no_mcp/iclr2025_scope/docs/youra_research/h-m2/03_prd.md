# Product Requirements Document (PRD)
**Hypothesis:** H-M2  
**Date:** 2026-08-25  
**Author:** Anonymous  
**Version:** 1.0

---

## Executive Summary

**Product Name:** Benchmark Clustering System for Coverage Family Detection

**Purpose:** Validate hypothesis H-M2 by implementing a SentenceBERT-based clustering pipeline that groups deep learning benchmarks into coverage families based on design features (task type, metrics, modality, dataset size), achieving ≥60% intra-family similarity.

**Hypothesis Statement:** If we embed benchmark design features using SentenceBERT and apply k-means clustering, then benchmarks will cluster into coverage families with ≥60% intra-family similarity on the feature space, because similar design constraints (task/metric/modality) create similar hypothesis coverage patterns.

**Success Criteria:**
- Intra-family similarity (cosine) ≥ 0.60
- Silhouette score > 0.3
- Code executes without errors
- Clustering separates benchmarks into 4 distinct families

---

## Problem Statement

### Background
After validating H-M1's feature extraction protocol, we need to determine whether these extracted features (task type, metrics, modality, dataset size) naturally group benchmarks into coverage families. If benchmarks cluster by design constraints, this validates that benchmark design predicts hypothesis coverage patterns.

### Current State
- H-M1 validated feature extraction with kappa >0.80
- 20 benchmarks annotated with 4 standardized features
- No clustering analysis performed yet

### Desired State
- Benchmarks clustered into 4 coverage families using SentenceBERT embeddings
- Intra-family similarity ≥60% demonstrating strong clustering
- Cluster composition analysis showing feature homogeneity
- Visualization of embedding space and cluster structure

---

## Functional Requirements

### FR-1: Feature Loading and Preprocessing
**Priority:** P0  
**Description:** Load H-M1 feature extraction output and convert to natural language descriptions.

**Acceptance Criteria:**
- Load CSV from `h-m1/outputs/extracted_features.csv`
- Convert 4 features (task_type, modality, metrics, dataset_size) to natural language template
- Template format: "{task_type} benchmark for {modality} data, measuring {metrics}, with {dataset_size} samples"
- Validate: 20 benchmark descriptions generated, no missing values

**Dependencies:** H-M1 Phase 4 completion (extracted_features.csv exists)

---

### FR-2: SentenceBERT Embedding Generation
**Priority:** P0  
**Description:** Encode benchmark descriptions using SentenceBERT to create dense semantic embeddings.

**Acceptance Criteria:**
- Load pre-trained model: `all-MiniLM-L6-v2`
- Encode 20 descriptions into 20×384 embedding matrix
- Apply L2 normalization to embeddings
- Verify embedding dimensions match model output

**Dependencies:** sentence-transformers library installed

---

### FR-3: K-Means Clustering
**Priority:** P0  
**Description:** Apply k-means clustering to embeddings with k=4 clusters.

**Acceptance Criteria:**
- Initialize k-means with n_clusters=4, random_state=42
- Max iterations: 300
- Generate cluster labels (0-3) for all 20 benchmarks
- Record cluster centroids
- No singleton clusters (all clusters have ≥2 members)

**Dependencies:** FR-2 (embeddings generated)

---

### FR-4: Intra-Family Similarity Calculation
**Priority:** P0  
**Description:** Calculate average cosine similarity within each cluster to measure family cohesion.

**Acceptance Criteria:**
- For each cluster: compute pairwise cosine similarity matrix
- Average upper triangle (exclude diagonal) for within-cluster similarity
- Aggregate across all 4 clusters (mean of cluster means)
- Final metric: scalar value in [0, 1]
- **Gate check:** intra_family_similarity ≥ 0.60

**Dependencies:** FR-3 (cluster labels assigned)

---

### FR-5: Silhouette Score Evaluation
**Priority:** P0  
**Description:** Calculate silhouette score to assess cluster quality.

**Acceptance Criteria:**
- Use sklearn.metrics.silhouette_score
- Input: embeddings + cluster labels
- Output: scalar in [-1, 1]
- **Gate check:** silhouette_score > 0.3

**Dependencies:** FR-3 (cluster labels assigned)

---

### FR-6: Cluster Feature Composition Analysis
**Priority:** P1  
**Description:** Analyze feature distribution within each cluster to assess homogeneity.

**Acceptance Criteria:**
- For each cluster: calculate dominant task_type, dominant modality, avg dataset_size
- Feature homogeneity: % of benchmarks sharing dominant task/modality
- Identify outlier benchmarks (low similarity to cluster centroid)
- Output: structured analysis dict per cluster

**Dependencies:** FR-3 (cluster labels assigned)

---

### FR-7: TF-IDF Baseline Clustering
**Priority:** P1  
**Description:** Implement TF-IDF + k-means baseline for comparison.

**Acceptance Criteria:**
- TF-IDF vectorizer with max_features=100
- K-means with n_clusters=4, same random seed
- Calculate baseline intra-family similarity
- Compare: SentenceBERT similarity - baseline similarity (delta)

**Dependencies:** FR-1 (descriptions available)

---

### FR-8: Embedding Space Visualization (t-SNE/UMAP)
**Priority:** P1  
**Description:** Generate 2D projection of embedding space colored by cluster.

**Acceptance Criteria:**
- t-SNE or UMAP dimensionality reduction (384D → 2D)
- Scatter plot with points colored by cluster assignment
- Cluster centroids marked
- Save figure to `h-m2/figures/embedding_space.png`

**Dependencies:** FR-3 (cluster labels assigned)

---

### FR-9: Cluster Feature Composition Plot
**Priority:** P2  
**Description:** Stacked bar chart showing feature distribution per cluster.

**Acceptance Criteria:**
- X-axis: 4 clusters
- Y-axis: benchmark count
- Stacks: task_type categories (different colors)
- Shows feature homogeneity visually
- Save figure to `h-m2/figures/cluster_composition.png`

**Dependencies:** FR-6 (composition analysis complete)

---

### FR-10: Similarity Heatmap
**Priority:** P2  
**Description:** Pairwise cosine similarity matrix (20×20) ordered by cluster.

**Acceptance Criteria:**
- Compute pairwise similarity for all benchmark pairs
- Order rows/columns by cluster assignment
- Expected pattern: block-diagonal structure (high intra-cluster sim)
- Colormap: diverging (blue=low, red=high)
- Save figure to `h-m2/figures/similarity_heatmap.png`

**Dependencies:** FR-3 (cluster labels assigned)

---

### FR-11: Silhouette Plot
**Priority:** P2  
**Description:** Per-benchmark silhouette coefficients grouped by cluster.

**Acceptance Criteria:**
- Calculate silhouette coefficient for each benchmark
- Horizontal bar chart grouped by cluster
- Identify poorly-clustered benchmarks (coef < 0)
- Save figure to `h-m2/figures/silhouette_plot.png`

**Dependencies:** FR-5 (silhouette score calculated)

---

### FR-12: Gate Metrics Comparison Chart (MANDATORY)
**Priority:** P0  
**Description:** Bar chart comparing intra-family similarity against 60% threshold.

**Acceptance Criteria:**
- Bar chart with 2 bars: achieved similarity, 0.60 threshold
- Clear visual: green if ≥0.60, red if <0.60
- Annotate with actual value
- Save figure to `h-m2/figures/gate_metrics.png`

**Dependencies:** FR-4 (similarity calculated)

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Random seed: 42 for k-means
- Deterministic SentenceBERT encoding (no dropout)
- Logged: model version, library versions, hyperparameters

### NFR-2: Performance
- Embedding generation: <10 seconds (20 descriptions)
- Clustering: <5 seconds
- Total runtime: <30 seconds

### NFR-3: Output Structure
- All figures saved to `h-m2/figures/` directory
- Metrics logged to console and saved to `h-m2/outputs/metrics.json`
- Cluster assignments saved to `h-m2/outputs/cluster_assignments.csv`

### NFR-4: Error Handling
- Validate H-M1 input file exists before loading
- Check embedding dimensions match expected (384)
- Warn if any cluster has <2 members
- Handle edge cases: empty descriptions, NaN values

---

## Dependencies

### Prerequisites
- **H-M1 Phase 4 completion:** `h-m1/outputs/extracted_features.csv` must exist
- Python 3.8+
- Libraries: sentence-transformers, scikit-learn, pandas, numpy, matplotlib, seaborn

### Data Dependencies
- Input: `h-m1/outputs/extracted_features.csv` (20 benchmarks × 4 features)
- Features: task_type, modality, metrics (list), dataset_size

### Model Dependencies
- SentenceBERT model: `all-MiniLM-L6-v2` (auto-downloaded from HuggingFace)
- No fine-tuning required

---

## Success Criteria

### PoC Pass Condition (MUST_WORK Gate)
1. ✅ Code runs without error
2. ✅ `intra_family_similarity ≥ 0.60 AND silhouette_score > 0.3`

### Gate Logic
- **PASS (intra_sim ≥ 0.60):** Proceed to H-M3
- **PARTIAL (0.50 ≤ intra_sim < 0.60):** Try k=3 or k=5, or richer embedding model
- **FAIL (intra_sim < 0.50):** MUST_WORK gate fails → STOP workflow

### Validation Checks (Phase 4 Validator)
- All 20 benchmarks assigned to clusters
- All clusters non-empty (≥2 members)
- Intra-similarity metric in valid range [0, 1]
- Silhouette score in valid range [-1, 1]
- All required figures generated (FR-8 through FR-12)
- Cluster composition analysis complete (FR-6)

---

## Out of Scope

- Fine-tuning SentenceBERT on domain-specific data
- Hierarchical clustering or other clustering algorithms
- Expanding beyond 20 benchmarks (H-M2 is pilot phase)
- Interactive cluster labeling or manual refinement
- Testing multiple values of k beyond k=4
- Cross-validation or cluster stability analysis

---

## Appendix

### Key Metrics Definitions

**Intra-Family Similarity:**
```
For each cluster c:
  sim_c = mean(pairwise_cosine_similarity(embeddings_in_c))
intra_family_similarity = mean(sim_c for all clusters)
```

**Silhouette Score:**
```
For each sample i:
  a = mean distance to samples in same cluster
  b = mean distance to samples in nearest different cluster
  silhouette_i = (b - a) / max(a, b)
silhouette_score = mean(silhouette_i for all samples)
```

### Reference Implementations
- SentenceBERT: https://www.sbert.net/
- K-Means: https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html
- Silhouette: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html

---

**Document Status:** Complete  
**Next Phase:** Phase 3 (Architecture Design)
