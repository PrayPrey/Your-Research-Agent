# Architecture Specification: H-M2

**Date:** 2026-08-25  
**Hypothesis:** Benchmark Clustering via SentenceBERT Embeddings  
**Type:** MECHANISM (Clustering Study)  
**Archon KB Pattern Applied:** Embedding pipeline pattern (sklearn + transformers integration)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Patterns found from h-m1 implementation  
**Analyzed Path:** `experiments/h-m1/src/`  
**Findings:** Modular structure with separate config, data handling, evaluation, visualization modules. Gate evaluation pattern reusable.

---

## System Overview

Clustering pipeline for benchmarks. Load h-m1 features, embed with SentenceBERT, cluster with k-means, validate with similarity metrics.

**Core Flow:**
1. Load h-m1 extracted_features.csv
2. Convert features to natural language descriptions
3. Embed with SentenceBERT (all-MiniLM-L6-v2)
4. Cluster with k-means (k=4)
5. Calculate intra-family similarity and silhouette score
6. Generate gate metrics chart (similarity vs 0.60 threshold)

---

## Module Structure

### FeatureLoader (`src/h_m2/loader.py`)

**Dependencies:** pandas

```python
class FeatureLoader:
    def __init__(self, input_path: str): ...
    def load_features(self) -> pd.DataFrame: ...
    def to_descriptions(self, features: pd.DataFrame) -> List[str]: ...
```

### ClusteringPipeline (`src/h_m2/clustering.py`)

**Dependencies:** sentence_transformers, sklearn

```python
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans

class ClusteringPipeline:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', n_clusters: int = 4): ...
    def embed(self, descriptions: List[str]) -> np.ndarray: ...
    def cluster(self, embeddings: np.ndarray) -> np.ndarray: ...
    def run(self, descriptions: List[str]) -> dict: ...
```

### SimilarityCalculator (`src/h_m2/metrics.py`)

**Dependencies:** sklearn.metrics, numpy

```python
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import silhouette_score

class SimilarityCalculator:
    def intra_family_similarity(self, embeddings: np.ndarray, labels: np.ndarray) -> float: ...
    def silhouette(self, embeddings: np.ndarray, labels: np.ndarray) -> float: ...
    def pairwise_matrix(self, embeddings: np.ndarray) -> np.ndarray: ...
```

### ClusterAnalyzer (`src/h_m2/analyzer.py`)

**Dependencies:** pandas, numpy

```python
class ClusterAnalyzer:
    def feature_composition(self, features: pd.DataFrame, labels: np.ndarray) -> dict: ...
    def identify_outliers(self, embeddings: np.ndarray, labels: np.ndarray) -> List[int]: ...
```

### Evaluator (`src/h_m2/evaluate.py`)

**Dependencies:** SimilarityCalculator

```python
class Evaluator:
    def __init__(self, threshold: float = 0.60, silhouette_threshold: float = 0.3): ...
    def evaluate(self, embeddings: np.ndarray, labels: np.ndarray) -> dict: ...
    def check_gate(self, metrics: dict) -> str: ...  # "PASS" | "PARTIAL" | "FAIL"
```

### Visualizer (`src/h_m2/visualize.py`)

**Dependencies:** matplotlib, seaborn, sklearn (UMAP/t-SNE)

```python
class Visualizer:
    def __init__(self, output_dir: str): ...
    def plot_gate_metrics(self, similarity: float, threshold: float): ...
    def plot_embedding_space(self, embeddings: np.ndarray, labels: np.ndarray): ...
    def plot_similarity_heatmap(self, similarity_matrix: np.ndarray, labels: np.ndarray): ...
    def plot_silhouette(self, embeddings: np.ndarray, labels: np.ndarray): ...
```

### Config (`src/config/clustering_config.py`)

```python
from dataclasses import dataclass

@dataclass
class ClusteringConfig:
    hypothesis_id: str = "h-m2"
    input_path: str = "../../h-m1/data/h-m1/extracted_features.csv"
    model_name: str = "all-MiniLM-L6-v2"
    n_clusters: int = 4
    random_seed: int = 42
    similarity_threshold: float = 0.60
    silhouette_threshold: float = 0.3
    output_dir: str = "data/h-m2"
    figures_dir: str = "../../docs/youra_research/h-m2/figures"
```

---

## File Organization

```
experiments/h-m2/
├── src/
│   ├── h_m2/
│   │   ├── __init__.py
│   │   ├── loader.py          # Load h-m1 features, convert to descriptions
│   │   ├── clustering.py      # SentenceBERT + k-means pipeline
│   │   ├── metrics.py         # Similarity + silhouette calculations
│   │   ├── analyzer.py        # Cluster composition analysis
│   │   ├── evaluate.py        # Gate logic
│   │   └── visualize.py       # Required + optional figures
│   ├── config/
│   │   ├── __init__.py
│   │   └── clustering_config.py
│   └── main.py                # Orchestration script
└── data/h-m2/                 # Output directory

docs/youra_research/h-m2/
└── figures/
    ├── gate_metrics.png       # REQUIRED
    ├── embedding_space.png
    ├── similarity_heatmap.png
    └── silhouette_plot.png
```

---

## Data Flow

```
h-m1/extracted_features.csv → FeatureLoader → descriptions
descriptions → ClusteringPipeline.embed → embeddings (20×384)
embeddings → ClusteringPipeline.cluster → labels (20,)
embeddings + labels → SimilarityCalculator → metrics
metrics → Evaluator → gate_decision
metrics → Visualizer → figures/gate_metrics.png
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M2-1 | Feature Loading | Load h-m1 CSV, convert to natural language descriptions, validate completeness | 6 | Module:2 + Deps:1 + Algo:1 + Integ:2 |
| M2-2 | SentenceBERT Embedding | Download model, encode descriptions, L2 normalization, dimension validation | 8 | Module:2 + Deps:2 + Algo:2 + Integ:2 |
| M2-3 | K-Means Clustering | Initialize k-means (k=4, seed=42), fit to embeddings, verify no singletons | 7 | Module:2 + Deps:1 + Algo:2 + Integ:2 |
| M2-4 | Similarity Metrics | Intra-family cosine similarity, silhouette score, pairwise matrix | 10 | Module:3 + Deps:2 + Algo:3 + Integ:2 |
| M2-5 | Cluster Analysis | Feature composition per cluster, dominant task/modality, outlier detection | 9 | Module:3 + Deps:1 + Algo:3 + Integ:2 |
| M2-6 | Gate Evaluation | Check thresholds (similarity ≥0.60, silhouette >0.3), gate decision logic | 7 | Module:2 + Deps:1 + Algo:2 + Integ:2 |
| M2-7 | Visualization | Gate chart (REQUIRED), embedding space (UMAP/t-SNE), heatmap, silhouette plot | 10 | Module:2 + Deps:3 + Algo:2 + Integ:3 |
| M2-8 | Baseline Comparison | TF-IDF + k-means baseline, delta calculation vs SentenceBERT | 8 | Module:2 + Deps:2 + Algo:2 + Integ:2 |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M2-4, M2-5, M2-7], Low(4-8): [M2-1, M2-2, M2-3, M2-6, M2-8]

---

## External Dependencies

**Python Libraries:**
- `sentence-transformers` - SentenceBERT embeddings
- `scikit-learn` - k-means, cosine_similarity, silhouette_score
- `pandas` - Data handling
- `numpy` - Numerical computation
- `matplotlib` / `seaborn` - Visualization
- `umap-learn` (optional) - Dimensionality reduction for visualization

**Base Hypothesis (H-M1):**

| Module | Import Path | File Location |
|--------|-------------|---------------|
| StudyConfig | `from config.study_config import StudyConfig` | `experiments/h-m1/src/config/study_config.py` |
| Visualizer (pattern) | `from h_m1.visualize import Visualizer` | `experiments/h-m1/src/h_m1/visualize.py` |

**Verified from:** `experiments/h-m1/src/` (actual implementation)

---

## Gate Validation Logic

```python
def check_gate(metrics: dict) -> str:
    similarity = metrics['intra_family_similarity']
    silhouette = metrics['silhouette_score']
    
    if similarity >= 0.60 and silhouette > 0.3:
        return "PASS"
    elif similarity >= 0.50:
        return "PARTIAL"  # Try k=3 or k=5
    else:
        return "FAIL"  # MUST_WORK gate failed
```

---

## Success Criteria

**PoC Pass Conditions:**
1. Intra-family similarity ≥ 0.60
2. Silhouette score > 0.3
3. All 20 benchmarks clustered (no failures)
4. Gate metrics chart generated
5. No singleton clusters

**Gate Outcome:**
- PASS → H-M2 validated, proceed to H-M3
- PARTIAL → Try k=3/k=5 or richer embedding model
- FAIL → Workflow STOPS for clustering redesign

---

## Implementation Notes

- No model training (clustering pipeline, not ML)
- Reuse h-m1 visualization patterns (matplotlib + seaborn)
- SentenceBERT model auto-downloads from HuggingFace
- L2 normalization before clustering for better cosine similarity
- Random seed=42 for reproducibility
- t-SNE/UMAP for 2D projection (perplexity/n_neighbors tuned to n=20)

---

**Validation Checklist:**
- [x] No ASCII diagrams
- [x] Module sections = interface only
- [x] Codebase Analysis (Serena) section included
- [x] 8 Epic tasks with complexity scores
- [x] Total length < 500 lines
- [x] Archon KB pattern applied (1 line)
- [x] External Dependencies section with h-m1 import paths verified
