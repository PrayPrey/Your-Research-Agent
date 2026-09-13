# Logic Design: h-m1

**Hypothesis:** Uncertainty Method Mechanism Analysis (MECHANISM)
**Type:** MECHANISM
**Date:** 2026-04-22
**Author:** Logic Agent

Applied: PyTorch nn.Module pattern, Multi-method comparison pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** API signatures verified from base code
**Analyzed Path:** /home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_question_3/docs/youra_research/20260421_question/h-e1/code/
**Relevant Symbols:** NQDataLoader, MistralGenerator, SemanticEntropyEstimator, EnsembleBaseline, ExperimentRunner

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

The following APIs are reused from h-e1. Signatures verified from actual implementation:

```python
# From: h-e1/code/data/loader.py (ACTUAL CODE)
class NQDataLoader:
    def __init__(self, split: str = "validation", num_samples: int = 100, seed: int = 42):
        """Initialize data loader."""
        ...
    
    def load(self) -> None:
        """Load and filter dataset for unanswerable questions."""
        ...
    
    def get_questions(self) -> List[str]:
        """Return question strings. Returns: List[str] with num_samples questions."""
        ...

# From: h-e1/code/models/generator.py (ACTUAL CODE)
class MistralGenerator:
    def __init__(
        self,
        model_name: str = "mistralai/Mistral-7B-v0.1",
        device: str = "cuda",
        dtype = torch.float16
    ):
        """Initialize Mistral-7B model."""
        ...
    
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

# From: h-e1/code/methods/uncertainty.py (ACTUAL CODE)
class SemanticEntropyEstimator:
    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        similarity_threshold: float = 0.5
    ):
        """Initialize semantic entropy estimator."""
        ...
    
    def load(self) -> None:
        """Load embedding model."""
        ...
    
    def compute_uncertainty(self, answers: List[str]) -> float:
        """Compute semantic entropy. Returns: float (higher = more uncertain)."""
        ...
```

**Verified from**: h-e1/code/ (actual implementation, NOT spec)

---

## M-1: Environment Setup [Complexity: 4, Budget: 0]

**Applied:** Module reuse pattern

### API Signatures

```python
# REUSED FROM h-e1 - No new implementation needed
# Import existing modules:
# - from h_e1.data.loader import NQDataLoader
# - from h_e1.models.generator import MistralGenerator
# - from h_e1.methods.uncertainty import SemanticEntropyEstimator

# Dependencies file
# requirements.txt includes all h-e1 dependencies
```

---

## M-2: Self-Consistency [Complexity: 6, Budget: 1]

**Applied:** Majority voting pattern

### API Signatures

```python
from typing import List
from collections import Counter

class SelfConsistencyEstimator:
    """Self-consistency via majority voting (Wang et al. 2022)."""
    
    def compute_uncertainty(self, answers: List[str]) -> float:
        """
        Compute uncertainty via disagreement rate.
        
        Args:
            answers: List[str] - K generated answers
        Returns:
            float - Disagreement rate (1 - majority_fraction)
        """
        ...
```

### Pseudo-code

```
1. vote_counts = Counter(answers)
2. max_count = max(vote_counts.values())
3. agreement = max_count / len(answers)
4. return 1.0 - agreement
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Majority Voting | Implement Counter-based voting and disagreement computation |

---

## M-3: Token Variance [Complexity: 8, Budget: 1]

**Applied:** Logit extraction pattern

### API Signatures

```python
import torch
from typing import List
import numpy as np

class TokenVarianceEstimator:
    """Token-level variance computation."""
    
    def __init__(self, temperature: float = 0.7):
        """Initialize with temperature parameter."""
        self.temperature = temperature
    
    def compute_uncertainty(
        self,
        answers: List[str],
        logits_list: List[torch.Tensor]
    ) -> float:
        """
        Compute token-level variance across samples.
        
        Args:
            answers: List[str] - K generated answers (for compatibility)
            logits_list: List[Tensor] - K logits tensors, each [seq_len, vocab_size]
        Returns:
            float - Mean variance across tokens
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| logits | [K, seq_len, vocab_size] | Stacked logits |
| probs | [K, seq_len, vocab_size] | Softmax probabilities |
| variance | [seq_len, vocab_size] | Variance across K samples |

### Pseudo-code

```
1. Align logits to same sequence length (pad/truncate)
2. probs = softmax(logits / temperature)  # [K, seq_len, vocab_size]
3. variance = var(probs, dim=0)  # [seq_len, vocab_size]
4. return mean(variance)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Variance Computation | Implement logit collection and variance aggregation |

---

## M-4: Verbalized Confidence [Complexity: 7, Budget: 1]

**Applied:** Prompt engineering pattern

### API Signatures

```python
import re
from typing import Optional

class VerbalizedConfidenceEstimator:
    """Verbalized confidence elicitation (VCE)."""
    
    def __init__(self, generator):
        """
        Initialize with generator instance.
        
        Args:
            generator: MistralGenerator instance for prompting
        """
        self.generator = generator
    
    def compute_uncertainty(self, question: str) -> float:
        """
        Extract verbalized confidence via prompting.
        
        Args:
            question: str - Input question
        Returns:
            float - Uncertainty (1 - confidence), range [0, 1]
        """
        ...
    
    def _extract_confidence(self, response: str) -> Optional[float]:
        """Extract numeric confidence from response using regex."""
        ...
```

### Pseudo-code

```
1. prompt = f"{question}\n\nProvide your answer and confidence (0-100%):"
2. response = generator.generate_samples(prompt, k=1, temperature=0.0)[0]
3. confidence = extract_percentage_via_regex(response)
4. if confidence is None: return 0.5  # Default fallback
5. confidence_normalized = confidence / 100.0
6. return 1.0 - confidence_normalized  # Invert for uncertainty
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Confidence Extraction | Implement prompt generation and regex parsing |

---

## M-5: Correlation Analysis [Complexity: 9, Budget: 0]

**Applied:** Scipy correlation matrix pattern

### API Signatures

```python
import numpy as np
from scipy.stats import pearsonr
from typing import Dict, List

class CorrelationAnalyzer:
    """Compute pairwise correlation matrix for methods."""
    
    def __init__(self, methods: List[str]):
        """
        Initialize analyzer.
        
        Args:
            methods: List[str] - Method names for labeling
        """
        self.methods = methods
    
    def compute_correlation_matrix(self, scores: Dict[str, List[float]]) -> np.ndarray:
        """
        Compute Pearson correlation for all method pairs.
        
        Args:
            scores: Dict[str, List[float]] - method_name -> 100 scores
        Returns:
            np.ndarray - [4, 4] symmetric correlation matrix
        """
        ...
    
    def evaluate_gate(self, correlation_matrix: np.ndarray, threshold: float = 0.7) -> bool:
        """
        Check if all off-diagonal correlations < threshold.
        
        Returns:
            bool - True if gate passes (all correlations < 0.7)
        """
        ...
    
    def save_results(self, correlation_matrix: np.ndarray, output_path: str):
        """Save correlation matrix to numpy file."""
        ...
```

### Pseudo-code

```
1. n_methods = len(methods)
2. corr_matrix = np.zeros((n_methods, n_methods))
3. For i in range(n_methods):
   For j in range(n_methods):
       if i == j: corr_matrix[i, j] = 1.0
       else: corr_matrix[i, j] = pearsonr(scores[methods[i]], scores[methods[j]])[0]
4. off_diagonal = corr_matrix[~np.eye(4, dtype=bool)]
5. gate_pass = all(abs(c) < threshold for c in off_diagonal)
6. return corr_matrix, gate_pass
```

---

## M-6: Visualization [Complexity: 8, Budget: 0]

**Applied:** Seaborn heatmap pattern

### API Signatures

```python
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, List

class CorrelationVisualizer:
    """Generate correlation heatmap and analysis plots."""
    
    def __init__(self, method_names: List[str]):
        """Initialize with method names for labeling."""
        self.method_names = method_names
    
    def plot_heatmap(self, correlation_matrix: np.ndarray, output_path: str):
        """
        Generate correlation heatmap.
        
        Args:
            correlation_matrix: [4, 4] correlation matrix
            output_path: str - Path to save figure
        """
        ...
    
    def plot_distributions(self, scores: Dict[str, List[float]], output_path: str):
        """Plot score distributions for all methods (2x2 subplots)."""
        ...
    
    def plot_scatter_matrix(self, scores: Dict[str, List[float]], output_path: str):
        """Generate pairwise scatter plots (6 panels)."""
        ...
```

### Pseudo-code

```
Heatmap:
1. fig, ax = plt.subplots(figsize=(8, 8))
2. sns.heatmap(correlation_matrix, annot=True, cmap="RdBu_r", vmin=-1, vmax=1)
3. Add 0.7 threshold line annotation
4. Save to output_path

Distributions:
1. Create 2x2 subplot grid
2. For each method: plot histogram + KDE
3. Save figure

Scatter Matrix:
1. Create 3x2 subplot grid (6 pairwise combinations)
2. For each pair: scatter plot with regression line
3. Save figure
```

---

## M-7: Experiment Runner [Complexity: 10, Budget: 0]

**Applied:** Experiment orchestration pattern

### API Signatures

```python
from typing import Dict, List

class ExperimentRunner:
    """Orchestrate full experiment: 4 methods × 100 questions."""
    
    def __init__(self, config: dict):
        """
        Initialize with configuration.
        
        Args:
            config: dict - Experiment configuration (methods, hyperparams)
        """
        self.config = config
        self.data_loader = None
        self.generator = None
        self.methods = {}
    
    def run_experiment(self) -> Dict[str, any]:
        """
        Run full experiment pipeline.
        
        Returns:
            Dict with keys: scores, correlation_matrix, gate_pass, figures_saved
        """
        ...
    
    def compute_all_methods(self, question: str, answers: List[str]) -> Dict[str, float]:
        """
        Compute uncertainty scores for all methods on one question.
        
        Args:
            question: str - Input question
            answers: List[str] - K=10 generated answers
        Returns:
            Dict[str, float] - method_name -> uncertainty_score
        """
        ...
    
    def generate_visualizations(self, results: dict):
        """Generate all figures (heatmap, distributions, scatter)."""
        ...
```

### Pseudo-code

```
1. Initialize all components (data loader, generator, 4 methods)
2. questions = data_loader.get_questions()  # 100 questions
3. scores = {method: [] for method in ["semantic_entropy", "self_consistency", 
                                        "token_variance", "verbalized_confidence"]}
4. For each question:
   a. answers = generator.generate_samples(question, k=10)
   b. For each method:
      - score = method.compute_uncertainty(answers or question)
      - scores[method].append(score)
5. corr_matrix = CorrelationAnalyzer.compute_correlation_matrix(scores)
6. gate_pass = CorrelationAnalyzer.evaluate_gate(corr_matrix, threshold=0.7)
7. generate_visualizations(scores, corr_matrix)
8. save_results(scores, corr_matrix, gate_pass)
9. return results
```

---

## M-8: Gate Verification [Complexity: 5, Budget: 0]

**Applied:** Numpy array masking pattern

### API Signatures

```python
import numpy as np

def verify_gate(correlation_matrix: np.ndarray, threshold: float = 0.7) -> bool:
    """
    Verify SHOULD_WORK gate condition.
    
    Args:
        correlation_matrix: [4, 4] correlation matrix
        threshold: float - Maximum allowed correlation
    Returns:
        bool - True if all pairwise correlations < 0.7
    """
    ...

def print_gate_report(correlation_matrix: np.ndarray, gate_pass: bool):
    """Print formatted gate verification report."""
    ...
```

### Pseudo-code

```
1. Extract off-diagonal elements:
   off_diagonal = correlation_matrix[~np.eye(4, dtype=bool)]
2. Check condition:
   gate_pass = np.all(np.abs(off_diagonal) < threshold)
3. Print report:
   - List all 6 pairwise correlations
   - Show threshold
   - Display PASS/FAIL
4. Save to verification_state.yaml
```

---

## Summary

**Total Subtasks:** 3 (L-2-1, L-3-1, L-4-1)
**Budget Compliance:** 3/3 used (within allocation)
**API Completeness:** All tasks have copy-paste ready signatures
**Base Hypothesis Integration:** Verified parameter names from actual h-e1 code
**Codebase Type:** Extends base_hypothesis h-e1 with 3 new uncertainty methods
