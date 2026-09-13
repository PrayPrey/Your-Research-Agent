# Architecture Design: h-m2

**Hypothesis:** Error Type Signature Analysis (MECHANISM)
**Type:** MECHANISM
**Date:** 2026-04-22
**Author:** Architecture Agent

Applied: Multi-dataset comparison pattern, Statistical analysis template

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Patterns found from base code
**Analyzed Path:** /home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_question_3/docs/youra_research/20260421_question/h-m1/code/
**Findings:** Reusing data loader pattern, generator, semantic entropy, and self-consistency from h-m1. Adding TruthfulQA dataset loader and statistical comparison module.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| MistralGenerator | `sys.path: h-m1/code/` then `from models.generator import MistralGenerator` | h-m1/code/models/generator.py |
| SemanticEntropyEstimator | `sys.path: h-m1/code/` then `from methods.uncertainty import SemanticEntropyEstimator` | h-m1/code/methods/uncertainty.py |
| SelfConsistencyEstimator | `sys.path: h-m1/code/` then `from methods.uncertainty import SelfConsistencyEstimator` | h-m1/code/methods/uncertainty.py |

**Verified from**: h-m1/code/ (actual implementation)

**Note:** h-m1 uses relative imports within package. For h-m2 reuse, add h-m1/code/ to sys.path.

---

## 1. Module Structure

### DataModule (`data/loader.py`)

**Dependencies:** None

```python
class NQDataLoader:
    """Load NaturalQuestions dataset (knowledge gaps)."""
    def __init__(self, split: str = "validation", num_samples: int = 100, seed: int = 42): ...
    def load(self) -> None: ...
    def get_questions(self) -> List[str]: ...

class TQADataLoader:
    """Load TruthfulQA dataset (confident misconceptions)."""
    def __init__(self, split: str = "validation", num_samples: int = 100, seed: int = 42): ...
    def load(self) -> None: ...
    def get_questions(self) -> List[str]: ...
```

### ModelModule (`models/generator.py` - REUSED from h-m1)

**Dependencies:** None

```python
# REUSED FROM h-m1 via sys.path
class MistralGenerator:
    def __init__(self, model_name: str = "mistralai/Mistral-7B-v0.1", device: str = "cuda", dtype = torch.float16): ...
    def load(self) -> None: ...
    def generate_samples(self, question: str, k: int = 5, temperature: float = 0.7, max_new_tokens: int = 50, seed: int = 42) -> List[str]: ...
```

### UncertaintyModule (`methods/uncertainty.py` - REUSED from h-m1)

**Dependencies:** None

```python
# REUSED FROM h-m1 via sys.path
class SemanticEntropyEstimator:
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2", similarity_threshold: float = 0.5): ...
    def load(self) -> None: ...
    def compute_uncertainty(self, answers: List[str]) -> float: ...

class SelfConsistencyEstimator:
    def compute_uncertainty(self, answers: List[str]) -> float: ...
```

### AnalysisModule (`analysis/signature_analyzer.py`)

**Dependencies:** UncertaintyModule

```python
class ErrorSignatureAnalyzer:
    """Analyze uncertainty signatures across error types."""
    def __init__(self, semantic_estimator, consistency_estimator, generator): ...
    def analyze_dataset(self, questions: List[str], dataset_name: str) -> Dict[str, List[float]]: ...
    def compare_signatures(self, nq_scores: dict, tqa_scores: dict) -> dict: ...
```

### StatisticalModule (`analysis/statistical_tests.py`)

**Dependencies:** None

```python
class StatisticalAnalyzer:
    """Perform statistical comparisons between error types."""
    def __init__(self): ...
    def independent_ttest(self, group1: List[float], group2: List[float]) -> dict: ...
    def evaluate_gate(self, results: dict, threshold: float = 0.05) -> bool: ...
    def save_results(self, results: dict, output_path: str): ...
```

### VisualizationModule (`analysis/visualizer.py`)

**Dependencies:** StatisticalModule

```python
class SignatureVisualizer:
    """Generate visualizations for error signature analysis."""
    def __init__(self): ...
    def plot_gate_comparison(self, results: dict, output_path: str): ...
    def plot_diversity_distributions(self, nq_scores: List[float], tqa_scores: List[float], output_path: str): ...
    def plot_agreement_distributions(self, nq_scores: List[float], tqa_scores: List[float], output_path: str): ...
    def plot_signature_space(self, nq_diversity: List[float], nq_agreement: List[float], tqa_diversity: List[float], tqa_agreement: List[float], output_path: str): ...
```

### ExperimentModule (`experiment/runner.py`)

**Dependencies:** DataModule, ModelModule, UncertaintyModule, AnalysisModule, StatisticalModule, VisualizationModule

```python
class ExperimentRunner:
    """Orchestrate error signature comparison experiment."""
    def __init__(self, config: dict): ...
    def run_experiment(self) -> dict: ...
    def setup_components(self): ...
    def generate_visualizations(self, results: dict): ...
```

---

## 2. File Organization

```
h-m2/code/
├── data/
│   └── loader.py              # NQDataLoader + TQADataLoader (new)
├── models/                    # REUSED via sys.path from h-m1
├── methods/                   # REUSED via sys.path from h-m1
├── analysis/
│   ├── signature_analyzer.py # Error signature analysis
│   ├── statistical_tests.py  # T-tests and gate evaluation
│   └── visualizer.py         # Visualization generation
├── experiment/
│   └── runner.py             # Experiment orchestration
├── config.py                 # Configuration
└── main.py                   # Entry point
```

**Reuse Strategy:**
- Add `sys.path.insert(0, "../h-m1/code")` in main.py
- Import `MistralGenerator`, `SemanticEntropyEstimator`, `SelfConsistencyEstimator` from h-m1

---

## 3. Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| S-1 | Dataset Loaders | Implement NQDataLoader and TQADataLoader | 7 | 2+1+2+2 (Module=2, Deps=1, Algo=2, Integ=2) |
| S-2 | h-m1 Integration | Setup sys.path and import h-m1 modules | 4 | 1+1+1+1 (Module=1, Deps=1, Algo=1, Integ=1) |
| S-3 | Signature Analyzer | Implement error signature analysis pipeline | 9 | 2+2+3+2 (Module=2, Deps=2, Algo=3, Integ=2) |
| S-4 | Statistical Tests | Implement t-tests and gate evaluation | 8 | 2+1+3+2 (Module=2, Deps=1, Algo=3, Integ=2) |
| S-5 | Visualizations | Generate 4 required figures | 10 | 3+2+3+2 (Module=3, Deps=2, Algo=3, Integ=2) |
| S-6 | Experiment Runner | Orchestrate full pipeline (200 questions × 2 metrics) | 11 | 3+2+4+2 (Module=3, Deps=2, Algo=4, Integ=2) |
| S-7 | Gate Verification | Evaluate SHOULD_WORK gate condition | 5 | 1+1+2+1 (Module=1, Deps=1, Algo=2, Integ=1) |

**Distribution:** VeryHigh(18-20): 0, High(14-17): 0, Medium(9-13): 3 [S-3, S-5, S-6], Low(4-8): 4 [S-1, S-2, S-4, S-7]

**Total Epic Tasks:** 7
**Total Complexity:** 54

---

## 4. Integration Points

### S-1 → S-3
Dataset loaders provide questions for signature analysis

### S-2 → S-3
h-m1 modules (semantic entropy, self-consistency) used in signature analyzer

### S-3 → S-4
Signature scores (diversity, agreement) fed into statistical tests

### S-4 → S-5
Statistical results used for visualization generation

### S-6 orchestrates S-1, S-2, S-3, S-4
Experiment runner coordinates all components

### S-5, S-6 → S-7
Results and visualizations used for gate evaluation

---

## 5. Configuration Strategy

**Single config with dual-dataset support**

```python
CONFIG = {
    # Datasets
    "datasets": {
        "natural_questions": {
            "source": "natural_questions",
            "split": "validation",
            "num_samples": 100,
            "error_type": "knowledge_gaps"
        },
        "truthful_qa": {
            "source": "truthful_qa",
            "config": "generation",
            "split": "validation",
            "num_samples": 100,
            "error_type": "confident_misconceptions"
        }
    },
    
    # Model (reused from h-m1)
    "model_name": "mistralai/Mistral-7B-v0.1",
    "k_samples": 5,  # Optimized from h-m1
    "temperature": 0.7,
    "max_new_tokens": 50,
    
    # Uncertainty methods
    "embedding_model": "all-MiniLM-L6-v2",
    "clustering_threshold": 0.5,
    
    # Analysis
    "significance_threshold": 0.05,
    "seed": 42,
    
    # Paths
    "h_m1_code_path": "../h-m1/code",
    "output_dir": "results",
    "figures_dir": "figures"
}
```

---

## 6. Error Signature Analysis Pipeline

### Stage 1: Data Loading
- Load NaturalQuestions (100 samples, seed=42)
- Load TruthfulQA (100 samples, seed=42)

### Stage 2: Answer Generation
- For each question in both datasets:
  - Generate K=5 diverse answers (temperature=0.7)
  - Store samples for metric computation

### Stage 3: Metric Computation
- For each question's K=5 samples:
  - **Semantic Diversity:** Compute semantic entropy (h-m1 code)
  - **Sampling Agreement:** Compute self-consistency (h-m1 code)

### Stage 4: Statistical Comparison
- Independent t-test on diversity scores (NQ vs TQA)
- Independent t-test on agreement scores (NQ vs TQA)
- Check gate: `(p < 0.05) AND (mean_NQ_diversity > mean_TQA_diversity)`

### Stage 5: Visualization
1. Gate metrics comparison bar chart
2. Diversity distribution box plots
3. Agreement distribution box plots
4. 2D signature space scatter plot

---

## 7. Key Design Decisions

### Reuse h-m1 Code via sys.path
- **Rationale:** Avoid code duplication, leverage validated implementations
- **Implementation:** `sys.path.insert(0, "../h-m1/code")` before imports
- **Risk:** Path dependencies (mitigated by config.h_m1_code_path)

### K=5 Sampling (Reduced from K=10)
- **Rationale:** h-m1 optimization showed K=5 sufficient for efficiency
- **Trade-off:** Faster execution vs slightly less statistical power
- **Validation:** Proven operational in h-m1

### Dual Dataset Design
- **NaturalQuestions:** Knowledge gap errors (expected high diversity)
- **TruthfulQA:** Confident misconception errors (expected low diversity)
- **Gate Success:** Statistical significance (p < 0.05) on diversity difference

---

## Summary

**Architecture Type:** Multi-dataset error signature comparison (MECHANISM)
**Epic Tasks:** 7 (within standard tier budget)
**Complexity Level:** Medium (54 points)
**Implementation Approach:** Reuse h-m1 uncertainty methods, add TruthfulQA dataset, perform statistical comparison
**Key Innovation:** Characterize different error types via uncertainty signature patterns
