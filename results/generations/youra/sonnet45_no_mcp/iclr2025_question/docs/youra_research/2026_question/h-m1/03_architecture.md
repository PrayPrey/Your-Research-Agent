# Architecture Design: h-m1

**Hypothesis:** Uncertainty Method Mechanism Analysis (MECHANISM)
**Type:** MECHANISM
**Date:** 2026-04-22
**Author:** Architecture Agent

Applied: PyTorch experiment template, Multi-method comparison pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Patterns found from base code
**Analyzed Path:** /home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_question_3/docs/youra_research/20260421_question/h-e1/code/
**Findings:** Reusing data loader, generator, and configuration patterns from h-e1. Extending with three new uncertainty methods.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| NQDataLoader | `from h_e1.data.loader import NQDataLoader` | h-e1/code/data/loader.py |
| MistralGenerator | `from h_e1.models.generator import MistralGenerator` | h-e1/code/models/generator.py |
| SemanticEntropyEstimator | `from h_e1.methods.uncertainty import SemanticEntropyEstimator` | h-e1/code/methods/uncertainty.py |

**Verified from**: h-e1/code/ (actual implementation)

---

## 1. Module Structure

### DataModule (`data/loader.py`)

**Dependencies:** None (reused from h-e1)

```python
# REUSED FROM h-e1 - No changes needed
class NQDataLoader:
    def __init__(self, split: str = "validation", num_samples: int = 100, seed: int = 42): ...
    def load(self) -> None: ...
    def get_questions(self) -> List[str]: ...
```

### ModelModule (`models/generator.py`)

**Dependencies:** None (reused from h-e1)

```python
# REUSED FROM h-e1 - No changes needed
class MistralGenerator:
    def __init__(self, model_name: str = "mistralai/Mistral-7B-v0.1", device: str = "cuda", dtype = torch.float16): ...
    def load(self) -> None: ...
    def generate_samples(self, question: str, k: int = 10, temperature: float = 0.7, max_new_tokens: int = 50, seed: int = 42) -> List[str]: ...
```

### UncertaintyModule (`methods/uncertainty.py`)

**Dependencies:** None

```python
# REUSED: SemanticEntropyEstimator from h-e1
class SemanticEntropyEstimator:
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2", similarity_threshold: float = 0.5): ...
    def load(self) -> None: ...
    def compute_uncertainty(self, answers: List[str]) -> float: ...

# NEW: Self-consistency method
class SelfConsistencyEstimator:
    def compute_uncertainty(self, answers: List[str]) -> float: ...

# NEW: Token variance method
class TokenVarianceEstimator:
    def __init__(self, temperature: float = 0.7): ...
    def compute_uncertainty(self, answers: List[str], logits_list: List[torch.Tensor]) -> float: ...

# NEW: Verbalized confidence method
class VerbalizedConfidenceEstimator:
    def __init__(self, generator): ...
    def compute_uncertainty(self, question: str) -> float: ...
```

### AnalysisModule (`analysis/correlation.py`)

**Dependencies:** UncertaintyModule

```python
class CorrelationAnalyzer:
    def __init__(self, methods: List[str]): ...
    def compute_correlation_matrix(self, scores: dict) -> np.ndarray: ...
    def evaluate_gate(self, correlation_matrix: np.ndarray, threshold: float = 0.7) -> bool: ...
    def save_results(self, correlation_matrix: np.ndarray, output_path: str): ...
```

### VisualizationModule (`analysis/visualizer.py`)

**Dependencies:** AnalysisModule

```python
class CorrelationVisualizer:
    def __init__(self, method_names: List[str]): ...
    def plot_heatmap(self, correlation_matrix: np.ndarray, output_path: str): ...
    def plot_distributions(self, scores: dict, output_path: str): ...
    def plot_scatter_matrix(self, scores: dict, output_path: str): ...
```

### ExperimentModule (`experiment/runner.py`)

**Dependencies:** DataModule, ModelModule, UncertaintyModule, AnalysisModule, VisualizationModule

```python
class ExperimentRunner:
    def __init__(self, config: dict): ...
    def run_experiment(self) -> dict: ...
    def compute_all_methods(self, question: str, answers: List[str]) -> dict: ...
    def generate_visualizations(self, results: dict): ...
```

---

## 2. File Organization

```
h-m1/code/
├── data/                  # REUSED from h-e1
│   └── loader.py         # Symlink or copy from h-e1
├── models/               # REUSED from h-e1
│   └── generator.py      # Symlink or copy from h-e1
├── methods/
│   └── uncertainty.py    # Semantic entropy (h-e1) + 3 new methods
├── analysis/
│   ├── correlation.py    # Correlation matrix computation
│   └── visualizer.py     # Visualization generation
├── experiment/
│   └── runner.py         # Experiment orchestration
├── config.py             # Configuration with 4 methods
└── main.py               # Entry point
```

---

## 3. Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Environment Setup | Reuse h-e1 data/model modules, install dependencies | 4 | 1+1+1+1 (Module=1, Deps=1, Algo=1, Integ=1) |
| M-2 | Self-Consistency | Implement majority voting method | 6 | 2+1+2+1 (Module=2, Deps=1, Algo=2, Integ=1) |
| M-3 | Token Variance | Implement token-level variance computation | 8 | 2+2+2+2 (Module=2, Deps=2, Algo=2, Integ=2) |
| M-4 | Verbalized Confidence | Implement confidence elicitation via prompting | 7 | 2+1+3+1 (Module=2, Deps=1, Algo=3, Integ=1) |
| M-5 | Correlation Analysis | Compute pairwise correlation matrix | 9 | 2+2+3+2 (Module=2, Deps=2, Algo=3, Integ=2) |
| M-6 | Visualization | Generate heatmap, distributions, scatter plots | 8 | 2+2+2+2 (Module=2, Deps=2, Algo=2, Integ=2) |
| M-7 | Experiment Runner | Orchestrate 100 questions × 4 methods | 10 | 3+2+3+2 (Module=3, Deps=2, Algo=3, Integ=2) |
| M-8 | Gate Verification | Evaluate correlation < 0.7 threshold | 5 | 1+1+2+1 (Module=1, Deps=1, Algo=2, Integ=1) |

**Distribution:** VeryHigh(18-20): 0, High(14-17): 0, Medium(9-13): 2 [M-5, M-7], Low(4-8): 6 [M-1, M-2, M-3, M-4, M-6, M-8]

**Total Epic Tasks:** 8
**Total Complexity:** 57

---

## 4. Integration Points

### M-1 → M-2, M-3, M-4
Reused modules provide foundation for new uncertainty methods

### M-2, M-3, M-4 → M-5
All four methods (semantic entropy + 3 new) feed scores into correlation analysis

### M-5 → M-6
Correlation matrix used for visualization generation

### M-7 orchestrates M-1, M-2, M-3, M-4, M-5
Experiment runner coordinates all components

### M-6, M-7 → M-8
Results and visualizations used for gate verification

---

## 5. Configuration Strategy

**Single config with multi-method support**

```python
CONFIG = {
    # Data (reused from h-e1)
    "dataset": "natural_questions",
    "split": "validation",
    "num_samples": 100,
    
    # Model (reused from h-e1)
    "model_name": "mistralai/Mistral-7B-v0.1",
    "k_samples": 10,
    "temperature": 0.7,
    
    # Methods
    "methods": [
        "semantic_entropy",
        "self_consistency",
        "token_variance",
        "verbalized_confidence"
    ],
    
    # Semantic entropy (from h-e1)
    "embedding_model": "all-MiniLM-L6-v2",
    "clustering_threshold": 0.5,
    
    # Analysis
    "correlation_threshold": 0.7,
    "seed": 42,
}
```

---

## 6. Method Implementation Details

### Semantic Entropy (Reused from h-e1)
- Generate K=10 answers
- Embed with all-MiniLM-L6-v2
- Cluster with agglomerative clustering (threshold=0.5)
- Compute entropy over clusters

### Self-Consistency (New)
- Generate K=10 answers
- Count occurrences via majority voting
- Return disagreement rate: 1 - (max_count / K)

### Token Variance (New)
- Collect logits for K=10 samples during generation
- Compute softmax probabilities
- Calculate variance across samples
- Aggregate variance (mean across vocabulary)

### Verbalized Confidence (New)
- Prompt: "{question}\n\nProvide your answer and confidence (0-100%):"
- Generate single response
- Extract percentage via regex
- Normalize to [0, 1], invert for uncertainty

---

## Summary

**Architecture Type:** Multi-method comparison (MECHANISM)
**Epic Tasks:** 8 (within standard tier budget)
**Complexity Level:** Medium-High (57 points)
**Implementation Approach:** Reuse h-e1 foundation, add 3 new methods, analyze correlations
**Key Innovation:** Systematic comparison of four orthogonal uncertainty dimensions
