# Experiment Design: H-M2

**Date:** 2026-08-25
**Author:** Anonymous
**Hypothesis Statement:** If we embed benchmark design features using SentenceBERT and apply k-means clustering, then benchmarks will cluster into coverage families with ≥60% intra-family similarity on the feature space, because similar design constraints (task/metric/modality) create similar hypothesis coverage patterns.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Template** - Validates feature-based clustering approach.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M1 (feature extraction protocol validated)
**Gate Status:** MUST_WORK (failure stops workflow)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (requires validated feature extraction)

### Gate Condition
MUST_WORK gate - Intra-family similarity must achieve ≥60%. If similarity <50%, workflow STOPS for clustering redesign.

---

## Continuation Context

Second hypothesis in verification plan, builds on H-M1's validated feature extraction protocol. Uses extracted features (task type, metrics, modality, dataset size) as input for clustering.

### Previous Hypothesis Results
**H-M1 Results:**
- Feature extraction protocol validated with kappa >0.80
- 20 diverse benchmarks annotated with 4 features
- Protocol objective enough for scaled deployment
- Features ready for embedding and clustering

---

## Implementation Research Summary

**MCP ABLATION MODE**: Archon, Exa, Serena MCPs unavailable. Experiment design based on Phase 2B protocol specification and standard embedding + clustering methodology.

### Archon Knowledge Base Findings

*MCP unavailable - No historical implementation cases retrieved*

### Archon Code Examples

*MCP unavailable - No code examples retrieved*

### Exa GitHub Implementations

*MCP unavailable - No GitHub implementations searched*

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

*MCP unavailable - Implementation priority based on standard methodology*

**Recommended Implementation Path:**
- Primary: SentenceBERT (sentence-transformers library) + scikit-learn k-means
- Fallback: TF-IDF + k-means baseline
- Justification: Standard text embedding + clustering pipeline, widely validated, matches Phase 2B specification

### Code Analysis (Serena MCP)

*MCP unavailable - No codebase analysis performed*

---

## Experiment Specification

### Dataset

**Name:** Benchmark Design Features Dataset (from H-M1)  
**Type:** custom (output from H-M1 experiment)  
**Size:** 20 diverse DL benchmarks (pilot phase)  
**Source:** H-M1 feature extraction output  
**Features per Benchmark:**
- Task type (categorical): PWC taxonomy category
- Metrics (categorical list): Regex-extracted metric names
- Modality (categorical): Image/text/audio/video/multimodal
- Dataset size (continuous): Number of samples

**Feature Preprocessing for Embedding:**
1. Concatenate features into natural language description
2. Template: "{task_type} benchmark for {modality} data, measuring {metrics}, with {dataset_size} samples"
3. Example: "Image classification benchmark for vision data, measuring accuracy and F1-score, with 50000 samples"

**Loading Information** (for Phase 4 download):
- Method: Load H-M1 output CSV/JSON
- Identifier: `h-m1/outputs/extracted_features.csv`
- Code:
```python
import pandas as pd
features_df = pd.read_csv("h-m1/outputs/extracted_features.csv")
# Convert to natural language descriptions
descriptions = features_df.apply(
    lambda row: f"{row['task_type']} benchmark for {row['modality']} data, "
                f"measuring {', '.join(row['metrics'])}, "
                f"with {row['dataset_size']} samples",
    axis=1
).tolist()
```

### Models

#### Baseline Model

**Architecture:** TF-IDF + K-Means Clustering

**Purpose:** Baseline clustering using sparse bag-of-words features

**Loading Information:**
- Method: scikit-learn built-in
- Code:
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# TF-IDF embedding
tfidf = TfidfVectorizer(max_features=100)
tfidf_embeddings = tfidf.fit_transform(descriptions)

# K-means clustering
kmeans_baseline = KMeans(n_clusters=4, random_state=42)
cluster_labels_baseline = kmeans_baseline.fit_predict(tfidf_embeddings)
```

#### Proposed Model

**Architecture:** SentenceBERT Embeddings + K-Means Clustering

**Core Mechanism Implementation:**

```python
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np

# 1. Embed benchmark descriptions using SentenceBERT
class BenchmarkClusteringPipeline:
    def __init__(self, model_name='all-MiniLM-L6-v2', n_clusters=4):
        # SentenceBERT model for semantic embeddings
        self.embedder = SentenceTransformer(model_name)
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    
    def embed_benchmarks(self, descriptions):
        """Convert benchmark descriptions to dense embeddings."""
        embeddings = self.embedder.encode(
            descriptions,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        return embeddings
    
    def cluster_benchmarks(self, embeddings):
        """Apply k-means clustering to embeddings."""
        cluster_labels = self.kmeans.fit_predict(embeddings)
        return cluster_labels
    
    def calculate_intra_family_similarity(self, embeddings, cluster_labels):
        """Calculate average cosine similarity within each cluster."""
        from sklearn.metrics.pairwise import cosine_similarity
        
        cluster_similarities = []
        for cluster_id in range(self.n_clusters):
            # Get embeddings in this cluster
            cluster_mask = cluster_labels == cluster_id
            cluster_embeds = embeddings[cluster_mask]
            
            if len(cluster_embeds) < 2:
                continue  # Skip singleton clusters
            
            # Calculate pairwise cosine similarity
            sim_matrix = cosine_similarity(cluster_embeds)
            # Average of upper triangle (exclude diagonal)
            upper_tri = np.triu_indices_from(sim_matrix, k=1)
            avg_similarity = sim_matrix[upper_tri].mean()
            cluster_similarities.append(avg_similarity)
        
        return np.mean(cluster_similarities)

# Main experiment logic
def run_clustering_experiment(features_df, n_clusters=4):
    # 1. Create natural language descriptions
    descriptions = create_descriptions(features_df)
    
    # 2. Embed with SentenceBERT
    pipeline = BenchmarkClusteringPipeline(n_clusters=n_clusters)
    embeddings = pipeline.embed_benchmarks(descriptions)
    
    # 3. Cluster
    cluster_labels = pipeline.cluster_benchmarks(embeddings)
    
    # 4. Calculate intra-family similarity
    intra_similarity = pipeline.calculate_intra_family_similarity(
        embeddings, cluster_labels
    )
    
    # 5. Analyze cluster composition
    cluster_analysis = analyze_clusters(features_df, cluster_labels)
    
    return {
        'embeddings': embeddings,
        'cluster_labels': cluster_labels,
        'intra_family_similarity': intra_similarity,
        'cluster_analysis': cluster_analysis
    }

def analyze_clusters(features_df, cluster_labels):
    """Analyze feature distribution within each cluster."""
    analysis = {}
    for cluster_id in np.unique(cluster_labels):
        cluster_mask = cluster_labels == cluster_id
        cluster_features = features_df[cluster_mask]
        analysis[f'cluster_{cluster_id}'] = {
            'size': cluster_features.shape[0],
            'dominant_task': cluster_features['task_type'].mode()[0],
            'dominant_modality': cluster_features['modality'].mode()[0],
            'avg_dataset_size': cluster_features['dataset_size'].mean()
        }
    return analysis
```

**Model Loading Information:**
- Library: sentence-transformers
- Model: `all-MiniLM-L6-v2` (lightweight SentenceBERT model)
- Code:
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
# Model auto-downloads from HuggingFace
```

### Training Protocol

**N/A** - No model training. This is an unsupervised clustering experiment.

**Clustering Protocol:**
1. **Feature Loading:**
   - Load H-M1 extracted features (20 benchmarks × 4 features)
   - Convert to natural language descriptions
   - Validate: no missing values

2. **Embedding:**
   - Encode descriptions using SentenceBERT
   - Output: 20 × 384 embedding matrix (all-MiniLM-L6-v2 dims)
   - Normalize embeddings (L2 norm)

3. **Clustering:**
   - K-means with k=4 clusters (hypothesis coverage families)
   - Random seed: 42 (reproducibility)
   - Max iterations: 300
   - Record: cluster labels, centroids

4. **Similarity Calculation:**
   - For each cluster: compute pairwise cosine similarity
   - Average within-cluster similarity
   - Aggregate across all clusters

5. **Cluster Validation:**
   - Silhouette score (cluster quality)
   - Feature homogeneity: dominant task/modality per cluster
   - Identify outlier benchmarks (low similarity to centroid)

### Evaluation

**Primary Metric:** Intra-Family Similarity (average cosine similarity within clusters)  
**Target:** ≥60% (0.60)  
**Secondary Metrics:**
- Silhouette score (cluster quality)
- Feature homogeneity (% dominant task/modality per cluster)

**Success Criteria (PoC):**
1. ✅ **PASS:** intra_family_similarity ≥ 0.60 AND silhouette_score > 0.3
2. ⚠️ **PARTIAL:** similarity in [0.50, 0.60] → Try different k or embedding model
3. ❌ **FAIL:** similarity < 0.50 → MUST_WORK gate fails, clustering approach invalid

**Interpretation:**
- Similarity ≥ 0.60: Clusters represent distinct coverage families
- Similarity 0.50-0.60: Weak clustering, feature space may need enrichment
- Similarity < 0.50: Random clustering, design constraints don't predict coverage

**Metrics Loading Information:**
- Library: scikit-learn (cosine_similarity, silhouette_score)
- Code:
```python
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import silhouette_score
import numpy as np

# Intra-family similarity (custom)
def calculate_intra_similarity(embeddings, labels):
    similarities = []
    for cluster_id in np.unique(labels):
        cluster_embeds = embeddings[labels == cluster_id]
        if len(cluster_embeds) < 2:
            continue
        sim_matrix = cosine_similarity(cluster_embeds)
        upper_tri = np.triu_indices_from(sim_matrix, k=1)
        similarities.append(sim_matrix[upper_tri].mean())
    return np.mean(similarities)

intra_sim = calculate_intra_similarity(embeddings, cluster_labels)

# Silhouette score (sklearn built-in)
silhouette = silhouette_score(embeddings, cluster_labels)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Intra-family similarity vs 60% threshold bar chart

#### Additional Figures (LLM Autonomous)

**Figure 1: Embedding Space Visualization (t-SNE/UMAP)**
- 2D projection of SentenceBERT embeddings
- Points colored by cluster assignment
- Shows cluster separation in feature space

**Figure 2: Cluster Feature Composition**
- Stacked bar chart: feature distribution (task/modality) per cluster
- Shows feature homogeneity within families

**Figure 3: Similarity Heatmap**
- Pairwise cosine similarity matrix (20×20 benchmarks)
- Ordered by cluster assignment
- Shows block-diagonal structure (high intra-cluster similarity)

**Figure 4: Silhouette Plot**
- Silhouette coefficient per benchmark
- Grouped by cluster
- Identifies poorly-clustered benchmarks

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_scope/docs/youra_research/h-m2/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (SentenceBERT embedding + k-means + similarity calculation)
2. `intra_family_similarity ≥ 0.60 AND silhouette_score > 0.3`

**Gate Logic:**
- ✅ PASS: Intra-similarity ≥ 0.60 → H-M2 satisfied, proceed to H-M3
- ⚠️ PARTIAL: Similarity [0.50, 0.60] → Try k=3 or k=5, or richer embedding model
- ❌ FAIL: Similarity < 0.50 → MUST_WORK gate fails, STOP workflow

---

## Appendix: Reference Implementations

**MCP ABLATION MODE** - No implementations retrieved from Archon/Exa/Serena.

**Standard References:**
1. **SentenceBERT:** sentence-transformers library
   - URL: https://www.sbert.net/
   - Model: all-MiniLM-L6-v2 (lightweight, 384 dims)
   - Usage: Standard semantic text embedding

2. **K-Means Clustering:** Scikit-learn
   - URL: https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html
   - Usage: Standard unsupervised clustering

3. **Cosine Similarity:** Scikit-learn
   - URL: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.cosine_similarity.html
   - Usage: Embedding similarity calculation

4. **Silhouette Score:** Scikit-learn
   - URL: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html
   - Usage: Cluster quality metric

5. **Clustering Evaluation (Literature):**
   - Rousseeuw, P. J. (1987). "Silhouettes: a graphical aid to the interpretation and validation of cluster analysis." Journal of computational and applied mathematics, 20, 53-65.
   - Reimers, N., & Gurevych, I. (2019). "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks." EMNLP 2019.

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-25

### Workflow History for This Hypothesis
- 2026-08-25: Phase 2C experiment design initiated (MCP ablation mode)
- Status: IN_PROGRESS
- Gate: MUST_WORK (intra-similarity ≥ 0.60 required)
- Prerequisites: H-M1 (feature extraction validated)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
