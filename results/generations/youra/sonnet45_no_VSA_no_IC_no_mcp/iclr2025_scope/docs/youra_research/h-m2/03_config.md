# Configuration Specification: H-M2

**Date:** 2026-08-25  
**Hypothesis:** Benchmark Clustering via SentenceBERT Embeddings  
**Type:** MECHANISM (Clustering Study)  
**Budget:** 2 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Config classes verified from h-m1 implementation  
**Config Files Found:** `experiments/h-m1/src/config/study_config.py`  
**Pattern Used:** dataclass

---

## Applied Patterns

**Applied:** Standard Python dataclass pattern (from h-m1, no ML training config needed)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: experiments/h-m1/src/config/study_config.py (ACTUAL CODE)
@dataclass
class StudyConfig:
    hypothesis_id: str = "h-m1"
    protocol_version: str = "1.0.0"
    n_benchmarks: int = 20
    random_seed: int = 42
    kappa_threshold: float = 0.80
    kappa_fail_threshold: float = 0.70
    pwc_api_url: str = "https://paperswithcode.com/api/v1/datasets/"
    api_timeout: int = 30
    taxonomy_path: str = "src/data/h-m1/taxonomy.json"
    metrics_patterns_path: str = "src/data/h-m1/metrics_patterns.json"
    output_dir: str = "data/h-m1"
    figures_dir: str = "../../docs/youra_research/h-m1/figures"
    calibration_samples: int = 3
    time_limit_minutes: int = 120
```

**Verified from:** `experiments/h-m1/src/config/study_config.py` (actual implementation)

**Reused fields:** `random_seed`, output directory structure pattern

---

## M2-CONFIG: Configuration [Complexity: 5, Budget: 2]

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ClusteringConfig:
    """H-M2 clustering pipeline configuration."""
    
    # Study Parameters
    hypothesis_id: str = "h-m2"
    random_seed: int = 42  # Inherited from h-m1
    
    # Data Paths
    input_path: str = "../../experiments/h-m1/data/h-m1/extracted_features.csv"
    output_dir: str = "data/h-m2"
    figures_dir: str = "../../docs/youra_research/h-m2/figures"
    
    # Embedding Model
    model_name: str = "all-MiniLM-L6-v2"  # SentenceBERT default
    embedding_dim: int = 384  # Model output dimension
    normalize_embeddings: bool = True  # L2 normalization for cosine similarity
    
    # Clustering Parameters
    n_clusters: int = 4
    kmeans_max_iter: int = 300
    kmeans_n_init: int = 10  # Multiple random initializations
    
    # Gate Thresholds
    similarity_threshold: float = 0.60  # MUST_WORK gate
    silhouette_threshold: float = 0.30
    partial_threshold: float = 0.50  # Try different k values
    
    # Description Template
    description_template: str = "{task_type} benchmark for {modality} data, measuring {metrics}, with {dataset_size} samples"
    
    def __post_init__(self):
        """Create output directories."""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.figures_dir).mkdir(parents=True, exist_ok=True)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-M2-1 | Config Dataclass | ClusteringConfig with embedding/clustering parameters |
| C-M2-2 | Path Resolution | Verify h-m1 input path, create output directories |

---

## Configuration Usage

### In Main Script
```python
from config.clustering_config import ClusteringConfig

config = ClusteringConfig()

# Override for experimentation
config.n_clusters = 5  # Try k=5 if PARTIAL gate
config.model_name = "all-mpnet-base-v2"  # Richer model if needed

# Module initialization
loader = FeatureLoader(input_path=config.input_path)
pipeline = ClusteringPipeline(
    model_name=config.model_name,
    n_clusters=config.n_clusters,
    random_state=config.random_seed
)
evaluator = Evaluator(
    similarity_threshold=config.similarity_threshold,
    silhouette_threshold=config.silhouette_threshold
)
```

### Gate Logic
```python
def check_gate(metrics: dict, config: ClusteringConfig) -> str:
    similarity = metrics['intra_family_similarity']
    silhouette = metrics['silhouette_score']
    
    if similarity >= config.similarity_threshold and silhouette > config.silhouette_threshold:
        return "PASS"
    elif similarity >= config.partial_threshold:
        return "PARTIAL"  # Try k=3 or k=5
    else:
        return "FAIL"  # MUST_WORK gate failed
```

---

## Self-Validation

- [x] ONE format only (dataclass)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale only for non-standard values
- [x] Subtask count within budget (2/2)
- [x] Total length < 400 lines
- [x] Codebase Analysis (Serena) section included
- [x] Inherited Configuration section with verified field names from actual h-m1 code
