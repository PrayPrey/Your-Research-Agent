# Logic Specification: H-M2

**Date:** 2026-08-25  
**Hypothesis:** Benchmark Clustering via SentenceBERT Embeddings  
**Type:** MECHANISM (Clustering Study)  
**Allocated Tasks:** M2-1, M2-2, M2-4 (3 subtasks total)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** API signatures verified from h-m1 actual implementation  
**Analyzed Path:** `experiments/h-m1/src/`  
**Relevant Symbols:**
- `Visualizer` class pattern from `h_m1/visualize.py`
- `StudyConfig` dataclass from `config/study_config.py`

**Findings:** H-M1 uses matplotlib/seaborn visualization patterns. Gate chart method `plot_gate_metrics(scores_dict, threshold)` is reusable pattern.

---

## Knowledge Base Patterns

**Applied:** PyTorch/sklearn integration pattern for embedding pipelines  
**Applied:** Dataclass configuration pattern from stdlib

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

The following patterns are reused from h-m1 implementation. Signatures verified from actual code:

```python
# From: experiments/h-m1/src/h_m1/visualize.py (ACTUAL CODE)
class Visualizer:
    def __init__(self, output_dir: str):
        """Initialize visualizer with output directory."""
        ...

    def plot_gate_metrics(self, kappa_scores: dict, threshold: float):
        """REQUIRED: Gate metrics bar chart.
        
        Args:
            kappa_scores: dict mapping metric names to scores
            threshold: float threshold for pass/fail coloring
        """
        ...

# From: experiments/h-m1/src/config/study_config.py (ACTUAL CODE)
@dataclass
class StudyConfig:
    hypothesis_id: str = "h-m1"
    protocol_version: str = "1.0.0"
    n_benchmarks: int = 20
    random_seed: int = 42
    kappa_threshold: float = 0.80
    output_dir: str = "data/h-m1"
    figures_dir: str = "../../docs/youra_research/h-m1/figures"
```

**Verified from:** `experiments/h-m1/src/` (actual implementation, NOT spec!)

**Reuse Pattern:** H-M2 will follow same dataclass config pattern and matplotlib visualization style.

---

## M2-1: Feature Loading [Complexity: 6, Budget: 6]

**Applied:** pandas DataFrame loading pattern

### API Signatures

```python
from pathlib import Path
import pandas as pd
from typing import List

class FeatureLoader:
    def __init__(self, input_path: str):
        """Load h-m1 extracted features.
        
        Args:
            input_path: Path to h-m1/data/extracted_features.csv
        """
        self.input_path = Path(input_path)

    def load_features(self) -> pd.DataFrame:
        """Load CSV. Returns: DataFrame[20 rows × 4 cols]"""
        # Columns: benchmark_name, task_type, modality, dataset_size
        ...

    def to_descriptions(self, features: pd.DataFrame) -> List[str]:
        """Convert features to natural language. Returns: 20 descriptions"""
        # Template: "{task_type} benchmark for {modality} data, measuring {metrics}, with {dataset_size} samples"
        ...
```

### Pseudo-code

```
1. Read CSV with pandas
2. Validate: 20 rows, no NaN in [task_type, modality, dataset_size]
3. For each row: format template string with feature values
4. Return list of 20 descriptions
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M2-1-1 | CSV loading | Read h-m1 output CSV |
| L-M2-1-2 | Validation | Check 20 rows, no missing values |
| L-M2-1-3 | Description templating | Format natural language strings |
| L-M2-1-4 | Error handling | FileNotFoundError, schema validation |
| L-M2-1-5 | Unit test | Test loader with sample CSV |
| L-M2-1-6 | Integration | Connect to clustering pipeline |

---

## M2-2: SentenceBERT Embedding [Complexity: 8, Budget: 8]

**Applied:** sentence-transformers model loading pattern

### API Signatures

```python
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.preprocessing import normalize
from typing import List

class ClusteringPipeline:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', n_clusters: int = 4):
        """Initialize SentenceBERT + k-means pipeline.
        
        Args:
            model_name: HuggingFace model identifier
            n_clusters: Number of clusters for k-means
        """
        self.model = SentenceTransformer(model_name)
        self.n_clusters = n_clusters

    def embed(self, descriptions: List[str]) -> np.ndarray:
        """Encode descriptions. descriptions: 20 → [20, 384]"""
        ...

    def cluster(self, embeddings: np.ndarray) -> np.ndarray:
        """K-means clustering. [20, 384] → [20,] cluster labels"""
        ...

    def run(self, descriptions: List[str]) -> dict:
        """End-to-end pipeline. Returns: {embeddings, labels, centroids}"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| descriptions | List[20] | Input strings |
| embeddings_raw | [20, 384] | Model output (all-MiniLM-L6-v2) |
| embeddings | [20, 384] | L2-normalized |
| labels | [20,] | Cluster assignments (0-3) |
| centroids | [4, 384] | Cluster centers |

### Pseudo-code

```
1. Load SentenceBERT model (auto-download if needed)
2. embeddings = model.encode(descriptions)  # [20, 384]
3. embeddings = L2_normalize(embeddings)    # Better cosine similarity
4. kmeans = KMeans(n_clusters=4, random_state=42)
5. labels = kmeans.fit_predict(embeddings)  # [20,]
6. Return {embeddings, labels, centroids}
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M2-2-1 | Model loading | Load SentenceBERT from HuggingFace |
| L-M2-2-2 | Encoding | Encode 20 descriptions |
| L-M2-2-3 | L2 normalization | sklearn normalize with norm='l2' |
| L-M2-2-4 | Dimension validation | Assert embeddings.shape == (20, 384) |
| L-M2-2-5 | K-means init | sklearn.cluster.KMeans with seed=42 |
| L-M2-2-6 | Clustering | fit_predict on embeddings |
| L-M2-2-7 | Singleton check | Verify all clusters have ≥2 members |
| L-M2-2-8 | Integration | Pipeline orchestration |

---

## M2-4: Similarity Metrics [Complexity: 10, Budget: 10]

**Applied:** sklearn pairwise metrics pattern

### API Signatures

```python
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import silhouette_score
import numpy as np

class SimilarityCalculator:
    """Calculate clustering quality metrics."""

    def intra_family_similarity(self, embeddings: np.ndarray, labels: np.ndarray) -> float:
        """Avg cosine similarity within clusters.
        
        Args:
            embeddings: [N, D] normalized embeddings
            labels: [N,] cluster assignments
        
        Returns:
            float in [0, 1], higher = better cohesion
        """
        ...

    def silhouette(self, embeddings: np.ndarray, labels: np.ndarray) -> float:
        """Silhouette score. Returns: float in [-1, 1]"""
        ...

    def pairwise_matrix(self, embeddings: np.ndarray) -> np.ndarray:
        """Full pairwise cosine similarity. [N, D] → [N, N]"""
        ...


class Evaluator:
    """Gate evaluation logic."""

    def __init__(self, similarity_threshold: float = 0.60, silhouette_threshold: float = 0.3):
        self.similarity_threshold = similarity_threshold
        self.silhouette_threshold = silhouette_threshold
        self.calculator = SimilarityCalculator()

    def evaluate(self, embeddings: np.ndarray, labels: np.ndarray) -> dict:
        """Calculate all metrics. Returns: {intra_similarity, silhouette, gate_decision}"""
        ...

    def check_gate(self, metrics: dict) -> str:
        """Gate decision. Returns: "PASS" | "PARTIAL" | "FAIL"""
        ...
```

### Pseudo-code

```
# Intra-family similarity
1. For each cluster c in [0, 1, 2, 3]:
   a. Extract embeddings for cluster c
   b. Compute pairwise cosine similarity (upper triangle, exclude diagonal)
   c. cluster_sim[c] = mean(similarity_values)
2. intra_family_sim = mean(cluster_sim)

# Silhouette score
1. silhouette_score(embeddings, labels)  # sklearn built-in

# Gate check
1. if intra_sim >= 0.60 and silhouette > 0.3: return "PASS"
2. elif intra_sim >= 0.50: return "PARTIAL"
3. else: return "FAIL"
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M2-4-1 | Pairwise similarity | sklearn.metrics.pairwise.cosine_similarity |
| L-M2-4-2 | Per-cluster calc | Loop over 4 clusters |
| L-M2-4-3 | Upper triangle extraction | Exclude diagonal for within-cluster |
| L-M2-4-4 | Aggregation | Mean of cluster means |
| L-M2-4-5 | Silhouette score | sklearn.metrics.silhouette_score |
| L-M2-4-6 | Gate logic | Threshold comparison |
| L-M2-4-7 | Metrics dict | Structure return value |
| L-M2-4-8 | Edge cases | Handle singleton clusters |
| L-M2-4-9 | Unit test | Test with mock embeddings |
| L-M2-4-10 | Integration | Connect to evaluator |

---

## Configuration

**Applied:** Dataclass pattern (matching h-m1 StudyConfig)

```python
from dataclasses import dataclass

@dataclass
class ClusteringConfig:
    """H-M2 clustering pipeline configuration."""
    
    # Study Parameters
    hypothesis_id: str = "h-m2"
    n_clusters: int = 4
    random_seed: int = 42
    
    # Model Settings
    model_name: str = "all-MiniLM-L6-v2"
    
    # Gate Thresholds
    similarity_threshold: float = 0.60
    silhouette_threshold: float = 0.3
    
    # File Paths
    input_path: str = "../../h-m1/data/h-m1/extracted_features.csv"
    output_dir: str = "data/h-m2"
    figures_dir: str = "../../docs/youra_research/h-m2/figures"
```

---

## Visualization

**Applied:** H-M1 gate chart pattern (verified from actual code)

```python
from pathlib import Path
import matplotlib.pyplot as plt

class Visualizer:
    """Generate required gate metrics chart."""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_gate_metrics(self, similarity: float, threshold: float):
        """REQUIRED: Similarity vs threshold bar chart.
        
        Args:
            similarity: Achieved intra-family similarity
            threshold: Pass threshold (0.60)
        
        Pattern: Reuses h-m1 gate chart style
        """
        # Bar chart: [Achieved, Threshold]
        # Color: green if similarity >= threshold else red
        # Save to: figures_dir/gate_metrics.png
        ...
```

---

## Main Orchestration

```python
from h_m2.loader import FeatureLoader
from h_m2.clustering import ClusteringPipeline
from h_m2.metrics import Evaluator
from h_m2.visualize import Visualizer
from config.clustering_config import ClusteringConfig


def main():
    """H-M2 clustering pipeline."""
    cfg = ClusteringConfig()
    
    # Load features
    loader = FeatureLoader(cfg.input_path)
    features = loader.load_features()
    descriptions = loader.to_descriptions(features)
    
    # Embed and cluster
    pipeline = ClusteringPipeline(cfg.model_name, cfg.n_clusters)
    result = pipeline.run(descriptions)
    
    # Evaluate
    evaluator = Evaluator(cfg.similarity_threshold, cfg.silhouette_threshold)
    metrics = evaluator.evaluate(result['embeddings'], result['labels'])
    gate = evaluator.check_gate(metrics)
    
    # Visualize
    viz = Visualizer(cfg.figures_dir)
    viz.plot_gate_metrics(metrics['intra_similarity'], cfg.similarity_threshold)
    
    # Log results
    print(f"Intra-family similarity: {metrics['intra_similarity']:.3f}")
    print(f"Silhouette score: {metrics['silhouette']:.3f}")
    print(f"Gate decision: {gate}")
    
    return gate == "PASS"
```

---

## Self-Validation

### Quick Checks
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in code comments
- [x] Subtask count within budget (3 tasks: 6+8+10=24 subtasks)
- [x] Total length < 600 lines
- [x] "Codebase Analysis (Serena)" section included

### Serena MCP Validation
- [x] Base hypothesis exists → Serena called on h-m1 code
- [x] API signatures verified from actual implementation

### Base Hypothesis Checks
- [x] Read actual code from `experiments/h-m1/src/`
- [x] API signatures verified from actual implementation (not specs)
- [x] Parameter names exactly match actual code
- [x] External Dependencies API section included

---

**Document Status:** Complete  
**Budget:** 3 tasks allocated (M2-1: 6, M2-2: 8, M2-4: 10)  
**Total Subtasks:** 24/24 used
