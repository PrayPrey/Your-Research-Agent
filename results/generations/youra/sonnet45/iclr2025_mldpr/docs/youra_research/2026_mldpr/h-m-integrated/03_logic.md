# Logic Design: h-m-integrated

**Date:** 2026-03-18
**Hypothesis:** Semantic Embeddings Encode Lifecycle Role via Distributional Signatures
**Type:** MECHANISM
**Designer:** Phase 3 Logic Agent
**Budget:** 11 subtasks allocated

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: API signatures verified from h-e1 actual code
**Analyzed Path**: `docs/youra_research/20260318_mldpr/h-e1/code/`
**Relevant Symbols**: DataCollector.collect_all(), ExperimentConfig (nested dataclass structure)

**Key Findings**:
- h-e1 uses nested dataclass config: ExperimentConfig contains DataCollectionConfig, AnnotationConfig, etc.
- DataCollector.collect_all() returns DataFrame [300, 5] with columns: field_name, field_value, repository, scaffolded, lifecycle_label
- Will reuse h-e1 dataset collection; h-m-integrated implements new clustering analysis

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

The following APIs are called from base hypothesis h-e1. Signatures verified from actual implementation:

```python
# From: h-e1/code/data/data_collector.py (ACTUAL CODE)
class DataCollector:
    """Multi-repository dataset collector with stratified sampling"""

    def __init__(self, config):
        """Initialize collector with configuration."""
        self.config = config
        self.random_seed = config.random_seed
        ...

    def collect_all(self) -> pd.DataFrame:
        """Collect metadata fields across 3 repositories. Returns: [300, 5] DataFrame
        Columns: field_name, field_value, repository, scaffolded, lifecycle_label
        """
        ...

    def classify_lifecycle_label(self, field_name: str, field_value: str) -> str:
        """Classify field into lifecycle stage. Returns: 'General Information' | 'Responsible AI'"""
        ...

# From: h-e1/code/config/config.py (ACTUAL CODE)
@dataclass
class DataCollectionConfig:
    """Data collection configuration"""
    n_huggingface: int = 150
    n_openml: int = 100
    n_uci: int = 50
    n_total_samples: int = 300
    random_seed: int = 42
    scaffold_ratio: float = 0.5

@dataclass
class ExperimentConfig:
    """Main experiment configuration (nested structure)"""
    experiment_id: str = "h-e1"
    hypothesis_type: str = "EXISTENCE"
    data_collection: DataCollectionConfig = field(default_factory=DataCollectionConfig)
    annotation: AnnotationConfig = field(default_factory=AnnotationConfig)
    statistical: StatisticalConfig = field(default_factory=StatisticalConfig)
    gate: GateConfig = field(default_factory=GateConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
```

**Verified from**: `h-e1/code/` (actual implementation, NOT spec)

**Reuse Strategy**: h-m-integrated will import h-e1 DataCollector for dataset collection. Config structure will mirror h-e1's nested dataclass pattern.

---

## M-1: Dataset Loading [Complexity: 8, Budget: 1]

**Applied**: Standard pandas DataFrame pattern

### API Signatures

```python
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Optional

class DataLoader:
    """Load and preprocess metadata from h-e1 dataset"""

    def __init__(self, config):
        """Initialize with configuration."""
        self.config = config
        self.data_dir = Path(config.data_dir)

    def load_metadata(self) -> pd.DataFrame:
        """Load h-e1 metadata. Returns: [300, 5] DataFrame"""
        ...

    def prepare_text_fields(self, df: pd.DataFrame) -> list[str]:
        """Concatenate field_name + field_value. Returns: 300 strings"""
        ...

    def get_true_labels(self, df: pd.DataFrame) -> np.ndarray:
        """Extract lifecycle labels. Returns: [300] binary array (0=General, 1=RAI)"""
        ...

    def apply_length_normalization(self, texts: list[str], max_tokens: int) -> list[str]:
        """Truncate/pad to fixed length. Returns: 300 normalized strings"""
        ...

    def apply_modality_filtering(self, texts: list[str], markers: list[str]) -> list[str]:
        """Remove deontic markers. Returns: 300 filtered strings"""
        ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Text preprocessing | Concatenation, normalization, filtering logic |

---

## M-2: Embedding Model [Complexity: 10, Budget: 1]

**Applied**: sentence-transformers library pattern

### API Signatures

```python
from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingModel:
    """Sentence-transformer wrapper for semantic embeddings"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize model from HuggingFace Hub."""
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: list[str], show_progress: bool = True) -> np.ndarray:
        """Encode texts. texts: 300 strings -> [300, 384] embeddings"""
        ...

    def get_embedding_dim(self) -> int:
        """Get embedding dimension. Returns: 384"""
        ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Batch encoding | Implement encode() with progress tracking |

---

## M-3: Clustering Pipeline [Complexity: 9, Budget: 1]

**Applied**: sklearn.cluster.KMeans API

### API Signatures

```python
from sklearn.cluster import KMeans
import numpy as np

class ClusteringPipeline:
    """K-means clustering for semantic embeddings"""

    def __init__(self, config):
        """Initialize with clustering configuration."""
        self.n_clusters = config.n_clusters
        self.random_state = config.kmeans_random_state

    def cluster_semantic(self, embeddings: np.ndarray) -> np.ndarray:
        """K-means on embeddings. embeddings: [300, 384] -> [300] cluster labels"""
        ...

    def cluster_permutation(self, labels_true: np.ndarray) -> np.ndarray:
        """Random shuffle baseline. labels_true: [300] -> [300] shuffled"""
        ...

    def cluster_lda(self, texts: list[str]) -> np.ndarray:
        """LDA topic modeling. texts: 300 strings -> [300] topic labels"""
        ...

    def cluster_lexical(self, texts: list[str], keywords: list[str]) -> np.ndarray:
        """Keyword matching. texts: 300 strings -> [300] binary labels"""
        ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | K-means clustering | Implement cluster_semantic() with deterministic seed |

---

## M-4: Baseline Models [Complexity: 14, Budget: 2]

**Applied**: sklearn LDA and rule-based classification

### API Signatures

```python
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

class PermutationBaseline:
    """Random label shuffle baseline"""

    def __init__(self, random_state: int = 42):
        """Initialize with random seed."""
        self.random_state = random_state

    def predict(self, labels_true: np.ndarray) -> np.ndarray:
        """Shuffle labels. labels_true: [300] -> [300] permuted"""
        ...

class LDABaseline:
    """LDA 2-topic baseline"""

    def __init__(self, n_components: int = 2, max_iter: int = 100, random_state: int = 42):
        """Initialize LDA model."""
        self.n_components = n_components
        self.max_iter = max_iter
        self.random_state = random_state

    def fit_predict(self, texts: list[str]) -> np.ndarray:
        """LDA topic assignment. texts: 300 strings -> [300] topic labels"""
        ...

class LexicalBaseline:
    """Keyword-based rule baseline"""

    def __init__(self, keywords: list[str]):
        """Initialize with RAI keywords."""
        self.keywords = [kw.lower() for kw in keywords]

    def predict(self, texts: list[str]) -> np.ndarray:
        """Keyword matching. texts: 300 strings -> [300] binary labels"""
        ...
```

### Pseudo-code

```
LDA:
1. vectorizer = CountVectorizer()
2. doc_term_matrix = vectorizer.fit_transform(texts)  # [300, vocab_size]
3. lda = LatentDirichletAllocation(n_components=2)
4. topic_dist = lda.fit_transform(doc_term_matrix)  # [300, 2]
5. labels = topic_dist.argmax(axis=1)  # [300]

Lexical:
1. For each text:
   - Check if any keyword in text.lower()
   - If yes: label=1 (RAI), else: label=0 (General)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | LDA implementation | fit_predict() with CountVectorizer |
| L-4-2 | Lexical matching | Case-insensitive keyword search |

---

## M-5: NMI Evaluator [Complexity: 12, Budget: 1]

**Applied**: sklearn.metrics.normalized_mutual_info_score

### API Signatures

```python
from sklearn.metrics import normalized_mutual_info_score
import numpy as np

class NMIEvaluator:
    """NMI computation and baseline comparison"""

    def __init__(self, config):
        """Initialize with gate thresholds."""
        self.nmi_threshold = config.nmi_threshold
        self.baseline_gap_threshold = config.baseline_gap_threshold

    def compute_nmi(self, labels_true: np.ndarray, labels_pred: np.ndarray) -> float:
        """Compute NMI. labels_true, labels_pred: [300] -> float in [0, 1]"""
        ...

    def compute_all_nmi(self, labels_true: np.ndarray, predictions: dict) -> dict:
        """Compute NMI for all methods. Returns: {method: nmi_score}"""
        ...

    def compute_baseline_gap(self, nmi_scores: dict) -> float:
        """Gap = NMI(semantic) - max(baselines). Returns: float"""
        ...

    def evaluate_controls(
        self,
        embeddings: np.ndarray,
        labels_true: np.ndarray,
        normalized_embeddings: np.ndarray,
        filtered_embeddings: np.ndarray
    ) -> dict:
        """Evaluate control experiments. Returns: {normalized_nmi, filtered_nmi}"""
        ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | NMI computation + gap | compute_nmi(), compute_baseline_gap() |

---

## M-6: Generalization Analyzer [Complexity: 13, Budget: 2]

**Applied**: sklearn.linear_model logistic probe pattern

### API Signatures

```python
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd

class GeneralizationAnalyzer:
    """Repository stratification and probe variance analysis"""

    def __init__(self, config):
        """Initialize with probe configuration."""
        self.probe_variance_threshold = config.probe_variance_threshold

    def train_repository_probes(
        self,
        embeddings: np.ndarray,
        labels: np.ndarray,
        repositories: np.ndarray
    ) -> dict:
        """Train probes per repository. Returns: {repo: accuracy}"""
        ...

    def compute_probe_variance(self, probe_results: dict) -> float:
        """Variance of probe accuracies. Returns: float"""
        ...

    def compute_repository_nmi(
        self,
        labels_true: np.ndarray,
        labels_pred: np.ndarray,
        repositories: np.ndarray
    ) -> dict:
        """NMI per repository. Returns: {repo: nmi}"""
        ...

    def analyze_scaffolding_effect(
        self,
        labels_true: np.ndarray,
        labels_pred: np.ndarray,
        scaffolding: np.ndarray
    ) -> dict:
        """Scaffolded vs unscaffolded NMI. Returns: {scaffolded_nmi, unscaffolded_nmi, gap}"""
        ...
```

### Pseudo-code

```
Repository Probes:
1. For each repo in [HF, OpenML, UCI]:
   a. Extract repo_mask = (repositories == repo)
   b. X_repo = embeddings[repo_mask]  # [n_repo, 384]
   c. y_repo = labels[repo_mask]  # [n_repo]
   d. Split: X_train, X_test, y_train, y_test (80/20)
   e. probe = LogisticRegression().fit(X_train, y_train)
   f. acc = probe.score(X_test, y_test)
2. variance = np.var([acc_hf, acc_openml, acc_uci])
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Repository probes | train_repository_probes() with stratification |
| L-6-2 | Scaffolding analysis | analyze_scaffolding_effect() |

---

## M-7: Gate Evaluator [Complexity: 10, Budget: 1]

**Applied**: Threshold-based gate logic

### API Signatures

```python
class GateEvaluator:
    """SHOULD_WORK gate validation"""

    def __init__(self, config):
        """Initialize with gate thresholds."""
        self.nmi_threshold = config.nmi_threshold
        self.baseline_gap_threshold = config.baseline_gap_threshold
        self.normalized_nmi_threshold = config.normalized_nmi_threshold
        self.probe_variance_threshold = config.probe_variance_threshold

    def evaluate_primary_criteria(self, nmi_scores: dict, baseline_gap: float) -> dict:
        """Check NMI > 0.6 AND gap >= 0.15. Returns: {passed, nmi, gap}"""
        ...

    def evaluate_secondary_criteria(self, control_results: dict, probe_variance: float) -> dict:
        """Check normalized NMI >= 0.6 AND variance < 0.1. Returns: {passed, ...}"""
        ...

    def determine_gate_status(self, primary: dict, secondary: dict) -> str:
        """Gate decision. Returns: 'PASS' | 'PARTIAL' | 'FAIL'"""
        ...

    def generate_failure_action(
        self,
        gate_status: str,
        nmi_scores: dict,
        control_results: dict
    ) -> str:
        """Failure action recommendation. Returns: action string"""
        ...
```

### Pseudo-code

```
Primary Gate:
1. pass_nmi = (nmi_scores['semantic'] > 0.6)
2. pass_gap = (baseline_gap >= 0.15)
3. primary_passed = pass_nmi AND pass_gap

Secondary Gate:
1. pass_normalized = (control_results['normalized_nmi'] >= 0.6)
2. pass_generalization = (probe_variance < 0.1)
3. secondary_passed = pass_normalized AND pass_generalization

Gate Status:
- If primary_passed AND secondary_passed: "PASS"
- If primary_passed OR (nmi >= 0.5 AND gap >= 0.10): "PARTIAL"
- Else: "FAIL"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Gate logic + actions | evaluate_primary_criteria(), determine_gate_status(), generate_failure_action() |

---

## M-8: Visualizer [Complexity: 12, Budget: 1]

**Applied**: Matplotlib/seaborn visualization pattern

### API Signatures

```python
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.manifold import TSNE
import numpy as np
from pathlib import Path

class Visualizer:
    """Generate 5 required figures"""

    def __init__(self, config):
        """Initialize with figure styling."""
        self.figures_dir = Path(config.figures_dir)
        self.dpi = 300

    def plot_gate_metrics(
        self,
        nmi_scores: dict,
        threshold: float,
        gap_threshold: float,
        output_path: Path
    ) -> None:
        """Bar chart: NMI scores with threshold lines"""
        ...

    def plot_embedding_space(
        self,
        embeddings: np.ndarray,
        labels_true: np.ndarray,
        labels_pred: np.ndarray,
        output_path: Path
    ) -> None:
        """t-SNE projection: [300, 384] -> [300, 2] visualization"""
        ...

    def plot_confusion_matrix(
        self,
        labels_true: np.ndarray,
        labels_pred: np.ndarray,
        output_path: Path
    ) -> None:
        """Confusion matrix heatmap"""
        ...

    def plot_repository_stratification(
        self,
        repository_nmi: dict,
        output_path: Path
    ) -> None:
        """Bar chart: NMI per repository"""
        ...

    def plot_scaffolding_effect(
        self,
        scaffolding_results: dict,
        output_path: Path
    ) -> None:
        """Bar chart: Scaffolded vs unscaffolded NMI"""
        ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | Figure generation | Implement 5 plot functions with consistent styling |

---

## Validation Checklist

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in code comments
- [x] Subtask count = 11 (within budget)
- [x] Total length < 600 lines
- [x] "Codebase Analysis (Serena)" section included
- [x] "External Dependencies API" section with verified h-e1 signatures
- [x] Applied patterns noted per task
- [x] Parameter names verified from h-e1 actual code (config.random_seed, config.data_dir, etc.)

---

*Generated for Phase 4 Implementation*
*Next: Configuration agent (03_config.md)*
