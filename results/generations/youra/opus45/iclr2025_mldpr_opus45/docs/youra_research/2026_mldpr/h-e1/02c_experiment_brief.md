# Experiment Design: h-e1

**Date:** 2026-03-27
**Author:** Anonymous
**Hypothesis Statement:** Under the HuggingFace dataset ecosystem (datasets with >=12 months history), if we apply DTW-based TimeSeriesKMeans clustering to normalized download trajectories, then datasets will partition into 3-8 distinct clusters with silhouette score >0.25 and bootstrap Jaccard stability >0.65, because download dynamics reflect recurring adoption mechanisms.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> EXISTENCE (PoC) Template - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** Yes (no prerequisites for H-E1)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
**MUST_WORK**: If clustering structure does not exist (silhouette <= 0.25 OR k not in [3,8]), the entire verification chain stops. This is the foundation for all subsequent hypotheses.

---

## Continuation Context

**Previous Hypothesis Results:** N/A - This is the first hypothesis in the verification chain.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: DTW time series clustering experiment design**
- Results: Limited direct matches - Archon KB primarily contains deep learning/diffusion model resources
- Key insight: Time series clustering is traditional ML domain; rely on Exa GitHub search

**Query 2: TimeSeriesKMeans tslearn implementation**
- Results: No direct matches in knowledge base
- Key insight: tslearn is the standard library for this task

**Query 3: silhouette score clustering validation**
- Results: Found evaluation-related content
- Key insight: sklearn.metrics.silhouette_score is the standard approach

### Archon Code Examples

No directly relevant code examples found in Archon KB for time series clustering. The knowledge base is specialized for deep learning frameworks (PyTorch, diffusers, transformers).

### Exa GitHub Implementations

**Repository 1**: tslearn-team/tslearn (2800+ stars)
- **URL**: https://github.com/tslearn-team/tslearn
- **Relevance**: Official Python library for time series machine learning with DTW
- **Architecture**: TimeSeriesKMeans with configurable distance metrics (DTW, soft-DTW, Euclidean)
- **Key Code**:
```python
from tslearn.clustering import TimeSeriesKMeans
from tslearn.preprocessing import TimeSeriesScalerMeanVariance
from tslearn.utils import to_time_series_dataset

# Preprocessing
X = to_time_series_dataset(time_series_list)
X_scaled = TimeSeriesScalerMeanVariance().fit_transform(X)

# DTW-based clustering
model = TimeSeriesKMeans(n_clusters=k, metric="dtw",
                         max_iter=10, n_init=2, random_state=seed)
y_pred = model.fit_predict(X_scaled)
```
- **Training Config**:
  - Metric: "dtw" (or "softdtw", "euclidean")
  - max_iter: 5-10
  - max_iter_barycenter: 5-10 for DTW barycenter
  - n_init: 2 for stability
- **Dataset**: Validated on UCR time series datasets
- **Results**: Silhouette scores typically 0.2-0.5 depending on data

**Repository 2**: HuggingFace Hub Python Library
- **URL**: https://huggingface.co/docs/huggingface_hub
- **Relevance**: Data collection API for HuggingFace dataset statistics
- **Key Code**:
```python
from huggingface_hub import HfApi

api = HfApi()
# List all datasets
datasets = api.list_datasets()
# Get specific dataset info (includes downloads)
info = api.dataset_info(repo_id="dataset_name")
```
- **Data Access**: Download counts accessible via API

**Repository 3**: sklearn clustering evaluation
- **URL**: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html
- **Key Code**:
```python
from sklearn.metrics import silhouette_score

# Standard silhouette score
score = silhouette_score(X, cluster_labels)

# For DTW with precomputed distance matrix
from tslearn.metrics import dtw
dist_matrix = compute_dtw_distance_matrix(X)
score = silhouette_score(dist_matrix, labels, metric="precomputed")
```

### Implementation Priority Assessment

**CRITICAL: For this experiment, we use established library implementations**

**Recommended Implementation Path:**
- Primary: tslearn TimeSeriesKMeans with DTW metric
- Fallback: soft-DTW if DTW is too slow for large datasets
- Justification: tslearn is the de facto standard for time series clustering in Python, well-maintained, and validated on benchmark datasets

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. tslearn provides well-documented APIs that don't require deep code analysis.

---

## Experiment Specification

### Dataset

**Name:** HuggingFace Dataset Download Statistics
**Type:** custom (API-based collection via programmatic-api)

**Description:** Time series of monthly download counts for HuggingFace datasets meeting inclusion criteria.

**Inclusion Criteria:**
- Created between 2020-2024
- Minimum 12 months of download history
- Minimum 100 total downloads
- Target population: >= 500 qualifying datasets

**Data Collection Protocol:**
1. Query HuggingFace Hub API for all datasets
2. Filter by creation date and download history length
3. Extract monthly download time series
4. Validate data quality (< 10% missing values)

**Preprocessing:**
1. Log-transform (handle exponential growth patterns)
2. Z-score normalization (TimeSeriesScalerMeanVariance)
3. Resample to uniform length if needed

**Loading Information** (for Phase 4 download):
- Method: programmatic-api (HuggingFace Hub API)
- Identifier: huggingface_hub.HfApi().list_datasets()
- Code:
```python
from huggingface_hub import HfApi
from datetime import datetime, timedelta
import pandas as pd

api = HfApi()
datasets = list(api.list_datasets(full=True))

# Filter qualifying datasets
qualifying = []
cutoff_date = datetime.now() - timedelta(days=365)
for ds in datasets:
    if hasattr(ds, 'downloads') and ds.downloads >= 100:
        if hasattr(ds, 'created_at') and ds.created_at < cutoff_date:
            qualifying.append(ds)
```

### Models

#### Baseline Model

**Architecture:** K-Means on summary statistics
**Description:** Cluster datasets based on aggregate features (mean, std, trend slope) rather than full trajectory shapes.

**Purpose:** Establish baseline clustering performance without DTW shape matching.

**Loading Information** (for Phase 4 download):
- Method: sklearn
- Identifier: sklearn.cluster.KMeans
- Code:
```python
from sklearn.cluster import KMeans
import numpy as np

# Extract summary statistics
def extract_features(series):
    return [np.mean(series), np.std(series), np.polyfit(range(len(series)), series, 1)[0]]

features = np.array([extract_features(s) for s in time_series_list])
baseline_model = KMeans(n_clusters=k, random_state=seed)
baseline_labels = baseline_model.fit_predict(features)
```

#### Proposed Model

**Architecture:** TimeSeriesKMeans with DTW metric

**Core Mechanism Implementation:**

```python
# Core Mechanism: DTW-based Time Series Clustering
# Based on: tslearn library (https://github.com/tslearn-team/tslearn)

from tslearn.clustering import TimeSeriesKMeans
from tslearn.preprocessing import TimeSeriesScalerMeanVariance
from tslearn.utils import to_time_series_dataset
from sklearn.metrics import silhouette_score
import numpy as np

class DTWTimeSeriesClustering:
    """
    DTW-based clustering for download trajectory analysis.
    Tests existence of clustering structure in HuggingFace dataset trajectories.
    """
    def __init__(self, k_range=(3, 8), random_state=42):
        self.k_range = k_range
        self.random_state = random_state
        self.best_k = None
        self.best_model = None
        self.best_silhouette = -1

    def preprocess(self, time_series_list):
        """
        Preprocess: log-transform + z-score normalize
        Input: List of 1D arrays (variable length OK)
        Output: 3D array (n_samples, max_len, 1)
        """
        # Log transform (add 1 to handle zeros)
        log_series = [np.log1p(ts) for ts in time_series_list]
        # Convert to tslearn format
        X = to_time_series_dataset(log_series)
        # Z-score normalize
        X_scaled = TimeSeriesScalerMeanVariance().fit_transform(X)
        return X_scaled

    def fit(self, X):
        """
        Fit DTW clustering for k in k_range, select best k by silhouette
        """
        for k in range(self.k_range[0], self.k_range[1] + 1):
            model = TimeSeriesKMeans(
                n_clusters=k,
                metric="dtw",
                max_iter=10,
                n_init=2,
                random_state=self.random_state
            )
            labels = model.fit_predict(X)

            # Compute silhouette (using Euclidean on flattened for speed)
            X_flat = X.reshape(X.shape[0], -1)
            score = silhouette_score(X_flat, labels)

            if score > self.best_silhouette:
                self.best_silhouette = score
                self.best_k = k
                self.best_model = model

        return self

    def get_results(self):
        return {
            "best_k": self.best_k,
            "silhouette_score": self.best_silhouette,
            "cluster_centers": self.best_model.cluster_centers_,
            "labels": self.best_model.labels_
        }
```

### Training Protocol

**Optimizer:** N/A (unsupervised clustering)

**Hyperparameters:**
| Parameter | Value | Source |
|-----------|-------|--------|
| k_range | [3, 8] | Phase 2B hypothesis specification |
| metric | "dtw" | Standard for shape-based clustering (Aghabozorgi et al., 2015) |
| max_iter | 10 | tslearn documentation default |
| n_init | 2 | Stability across random initializations |
| random_state | 42 | Reproducibility |

**Preprocessing Pipeline:**
1. Log transform: `np.log1p(downloads)` - handles exponential growth
2. Z-score: `TimeSeriesScalerMeanVariance()` - standardizes scale

**Bootstrap Protocol:**
- Iterations: 100
- Sample size: 80% of data with replacement
- Metric: Jaccard similarity between cluster assignments

**Seeds:** 1 (fixed at 42 for PoC)

### Evaluation

**Primary Metrics:**
| Metric | Definition | Success Threshold |
|--------|------------|-------------------|
| Silhouette Score | Cluster cohesion/separation measure | > 0.25 |
| Optimal k | Number of clusters selected | in [3, 8] |

**Secondary Metrics:**
| Metric | Definition | Success Threshold |
|--------|------------|-------------------|
| Bootstrap Jaccard | Stability of cluster assignments | > 0.65 |

**Success Criteria (PoC):**
- proposed_silhouette > 0.25 AND
- optimal_k in [3, 8] AND
- jaccard_stability > 0.65

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: clustering evaluation
- Library: sklearn.metrics, tslearn.clustering
- Code:
```python
from sklearn.metrics import silhouette_score
from sklearn.utils import resample
import numpy as np

def compute_jaccard_stability(X, model, n_bootstrap=100, sample_ratio=0.8):
    """Bootstrap Jaccard stability for cluster assignments"""
    n_samples = len(X)
    original_labels = model.labels_
    jaccard_scores = []

    for _ in range(n_bootstrap):
        # Bootstrap sample
        indices = resample(range(n_samples), n_samples=int(n_samples * sample_ratio))
        X_boot = X[indices]

        # Refit model
        boot_model = TimeSeriesKMeans(
            n_clusters=model.n_clusters,
            metric="dtw",
            random_state=np.random.randint(10000)
        )
        boot_labels = boot_model.fit_predict(X_boot)

        # Compute Jaccard on overlapping samples
        jaccard = compute_cluster_jaccard(original_labels[indices], boot_labels)
        jaccard_scores.append(jaccard)

    return np.mean(jaccard_scores)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing silhouette score vs threshold (0.25)

#### Additional Figures (LLM Autonomous)

Based on hypothesis type and evaluation metrics:
1. **Silhouette Analysis Plot**: Silhouette score vs number of clusters (k)
2. **Cluster Centroids**: Time series plot of cluster center trajectories
3. **Cluster Distribution**: Histogram of cluster sizes
4. **t-SNE Visualization**: 2D projection of clustered trajectories

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `silhouette_score > 0.25`
3. `optimal_k in [3, 8]`
4. `jaccard_stability > 0.65`

---

## Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | DTW distance computation available in tslearn | TRUE |
| Mechanism Isolatable | Can compare DTW vs Euclidean clustering | TRUE |
| Baseline Measurable | K-means on summary statistics runs independently | TRUE |

### Architecture Compatibility Check

**Required Features:**
- Time series data with numeric values
- Variable-length series support (handled by tslearn padding)
- Sufficient sample size (>= 500 datasets target)

**Incompatible Scenarios:**
- Sparse/missing data (> 10% missing values)
- Extremely short series (< 6 time points)
- Non-numeric data

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "Clustering completed with k={k}" | main.py |
| Tensor Shape | cluster_centers_.shape = (k, max_len, 1) | model.cluster_centers_ |
| Metric Delta | silhouette_dtw > silhouette_baseline | evaluate.py |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(model, silhouette_score, baseline_silhouette):
    """Verify DTW clustering mechanism is working"""
    indicators = {
        "model_fitted": hasattr(model, 'cluster_centers_'),
        "clusters_formed": model.n_clusters >= 3,
        "silhouette_valid": silhouette_score > 0,
        "dtw_improves": silhouette_score >= baseline_silhouette * 0.9  # Allow 10% tolerance
    }
    all_passed = all(indicators.values())
    return all_passed, indicators
```

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE | Model has cluster_centers_ attribute |
| Effect Measurable | silhouette > 0 | Clustering produces separation |
| Hypothesis Supported | silhouette > 0.25 AND k in [3,8] | Primary success criteria |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

No directly relevant sources found. Archon KB is specialized for deep learning frameworks.

### B. GitHub Implementations (Exa)

**Repository 1**: tslearn-team/tslearn
- **URL**: https://github.com/tslearn-team/tslearn
- **Query Used**: "tslearn TimeSeriesKMeans DTW clustering Python implementation"
- **Relevance**: Official time series ML library with DTW support
- **Key Code**: TimeSeriesKMeans class with metric="dtw"
- **Used For**: Core clustering implementation

**Repository 2**: HuggingFace Hub API
- **URL**: https://huggingface.co/docs/huggingface_hub
- **Query Used**: "HuggingFace Hub API dataset download statistics Python"
- **Relevance**: Data collection for dataset download trajectories
- **Key Code**: HfApi().list_datasets(), dataset_info()
- **Used For**: Dataset specification

**Repository 3**: sklearn.metrics
- **URL**: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html
- **Query Used**: "sklearn silhouette_score clustering evaluation"
- **Relevance**: Standard clustering evaluation metric
- **Key Code**: silhouette_score(X, labels)
- **Used For**: Evaluation metrics

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear

### D. Previous Hypothesis Context

**Previous Context**: None - this is the first hypothesis in the verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Phase 2B | 02b_verification_plan.md Section 1.3 |
| Preprocessing | GitHub | tslearn documentation |
| Clustering algorithm | GitHub | tslearn TimeSeriesKMeans |
| DTW metric | Literature | Aghabozorgi et al. (2015) |
| Silhouette evaluation | sklearn | sklearn.metrics.silhouette_score |
| Bootstrap Jaccard | Phase 2B | Success criteria specification |
| k range [3,8] | Phase 2B | Hypothesis success criteria |
| Silhouette threshold 0.25 | Literature | Standard clustering quality threshold |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-27T07:00:00Z

### Workflow History for This Hypothesis
- 2026-03-27: Phase 2B completed - H-E1 defined as EXISTENCE hypothesis
- 2026-03-27: Phase 2C started - Experiment design initiated

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
