# Logic Design: h-e1

**Hypothesis:** Semantic Entropy vs Ensemble Baseline
**Type:** EXISTENCE (PoC)
**Date:** 2026-04-22
**Author:** Logic Agent

Applied: PyTorch nn.Module pattern, Semantic similarity clustering

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field - new API design
**Analyzed Path:** N/A
**Relevant Symbols:** None - new implementation

---

## E-1: Data Loading [Complexity: 6, Budget: 0]

**Applied:** HuggingFace datasets standard loading

### API Signatures

```python
from datasets import load_dataset
from typing import List

class NQDataLoader:
    def __init__(self, split: str = "validation", num_samples: int = 100, seed: int = 42):
        """Load NaturalQuestions unanswerable subset."""
        self.split = split
        self.num_samples = num_samples
        self.seed = seed
        self.questions = None
    
    def load(self) -> None:
        """Load and filter dataset."""
        ...
    
    def get_questions(self) -> List[str]:
        """Return question strings. Returns: List[str] with num_samples questions."""
        ...
```

### Pseudo-code

```
1. Load NaturalQuestions validation split
2. Filter for unanswerable questions (yes_no_answer == -1)
3. Sample num_samples questions with seed
4. Extract question text
```

---

## E-2: Model Setup [Complexity: 8, Budget: 0]

**Applied:** HuggingFace transformers AutoModel pattern

### API Signatures

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from typing import List

class MistralGenerator:
    def __init__(
        self,
        model_name: str = "mistralai/Mistral-7B-v0.1",
        device: str = "cuda",
        dtype = torch.float16
    ):
        """Initialize Mistral-7B."""
        self.model_name = model_name
        self.device = device
        self.dtype = dtype
        self.model = None
        self.tokenizer = None
    
    def load(self) -> None:
        """Load model and tokenizer."""
        ...
    
    def generate_samples(
        self,
        question: str,
        k: int = 10,
        temperature: float = 0.7,
        max_new_tokens: int = 50,
        seed: int = 42
    ) -> List[str]:
        """Generate K diverse answers. Returns: List[str] with K answers."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, L] | Tokenized question |
| outputs | [K, L'] | K generated sequences |

---

## E-3: Uncertainty Methods [Complexity: 12, Budget: 2]

**Applied:** Semantic entropy (Kuhn et al. 2023), Agglomerative clustering

### API Signatures

```python
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
import numpy as np
from typing import List

class SemanticEntropyEstimator:
    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        similarity_threshold: float = 0.5
    ):
        """Semantic entropy with clustering."""
        self.embedding_model = embedding_model
        self.threshold = similarity_threshold
        self.embedder = None
    
    def load(self) -> None:
        """Load embedding model."""
        ...
    
    def compute_uncertainty(self, answers: List[str]) -> float:
        """
        Compute semantic entropy.
        
        Args:
            answers: List[str] - K generated answers
        Returns:
            float - Semantic entropy value (higher = more uncertain)
        """
        ...

class EnsembleBaseline:
    def compute_uncertainty(self, answers: List[str]) -> float:
        """
        Compute disagreement rate.
        
        Args:
            answers: List[str] - K generated answers
        Returns:
            float - Disagreement rate (1 - majority_vote_fraction)
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| embeddings | [K, D] | Semantic embeddings (D=384 for MiniLM) |
| clusters | [K] | Cluster assignments |

### Pseudo-code

**Semantic Entropy:**
```
1. embeddings = embed_all_answers(answers)  # [K, 384]
2. clusters = agglomerative_clustering(embeddings, threshold=0.5)  # [K]
3. cluster_probs = count_clusters(clusters) / K
4. entropy = -sum(p * log(p) for p in cluster_probs)
5. return entropy
```

**Ensemble Baseline:**
```
1. vote_counts = Counter(answers)
2. max_count = max(vote_counts.values())
3. agreement = max_count / K
4. return 1 - agreement  # Disagreement as uncertainty
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Semantic Clustering | Implement embedding + agglomerative clustering |
| L-3-2 | Entropy Computation | Compute entropy over cluster distribution |

---

## E-4: Experiment Runner [Complexity: 10, Budget: 2]

**Applied:** sklearn AUROC evaluation

### API Signatures

```python
from sklearn.metrics import roc_auc_score
from typing import Dict, List

class ExperimentRunner:
    def __init__(
        self,
        data_loader: NQDataLoader,
        generator: MistralGenerator,
        semantic_estimator: SemanticEntropyEstimator,
        ensemble_estimator: EnsembleBaseline
    ):
        """Initialize experiment with all components."""
        self.data_loader = data_loader
        self.generator = generator
        self.semantic_estimator = semantic_estimator
        self.ensemble_estimator = ensemble_estimator
    
    def run_experiment(self) -> Dict[str, float]:
        """
        Run full experiment.
        
        Returns:
            Dict with keys: auroc_semantic, auroc_ensemble, difference, gate_pass
        """
        ...
    
    def evaluate_gate(self, results: Dict[str, float]) -> bool:
        """
        Check MUST_WORK gate condition.
        
        Returns:
            True if AUROC_semantic - AUROC_ensemble >= 0.07 AND AUROC_semantic >= 0.70
        """
        ...
```

### Pseudo-code

```
1. questions = data_loader.get_questions()  # 100 questions
2. For each question:
   a. answers = generator.generate_samples(question, k=10)
   b. semantic_score = semantic_estimator.compute_uncertainty(answers)
   c. ensemble_score = ensemble_estimator.compute_uncertainty(answers)
3. y_true = [1] * 100  # All unanswerable questions (knowledge gaps)
4. auroc_semantic = roc_auc_score(y_true, semantic_scores)
5. auroc_ensemble = roc_auc_score(y_true, ensemble_scores)
6. difference = auroc_semantic - auroc_ensemble
7. gate_pass = (difference >= 0.07) and (auroc_semantic >= 0.70)
8. return {auroc_semantic, auroc_ensemble, difference, gate_pass}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Score Collection | Loop through questions and collect uncertainty scores |
| L-4-2 | AUROC Computation | Compute AUROC for both methods and validate gate |

---

## E-5: Visualization [Complexity: 6, Budget: 0]

**Applied:** matplotlib bar chart and ROC curve

### API Signatures

```python
import matplotlib.pyplot as plt
from typing import Dict

class Visualizer:
    def __init__(self, output_dir: str = "./figures"):
        """Initialize visualizer."""
        self.output_dir = output_dir
    
    def plot_auroc_comparison(self, results: Dict[str, float]) -> None:
        """Bar chart: AUROC_semantic vs AUROC_ensemble with gate threshold."""
        ...
    
    def plot_roc_curves(
        self,
        y_true: List[int],
        semantic_scores: List[float],
        ensemble_scores: List[float]
    ) -> None:
        """ROC curves for both methods."""
        ...
```

### Pseudo-code

```
1. Create bar chart with AUROC values
2. Add horizontal lines: 0.70 (absolute threshold), 0.07 (difference threshold)
3. Save to figures/auroc_comparison.png
4. Create ROC curves for both methods
5. Save to figures/roc_curves.png
```

---

## Summary

**Total Subtasks:** 4 (L-3-1, L-3-2, L-4-1, L-4-2)
**Budget Compliance:** 4/4 used (within LIGHT tier allocation)
**API Completeness:** All Epic tasks have copy-paste ready signatures
