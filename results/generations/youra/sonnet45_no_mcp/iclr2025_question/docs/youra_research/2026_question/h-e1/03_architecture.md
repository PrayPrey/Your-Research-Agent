# Architecture Design: h-e1

**Hypothesis:** Semantic Entropy vs Ensemble Baseline (EXISTENCE PoC)
**Type:** EXISTENCE
**Date:** 2026-04-22
**Author:** Architecture Agent

Applied: PyTorch experiment template, Minimal PoC structure

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field project - no existing code to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch

---

## 1. Module Structure

### DataModule (`data/loader.py`)

**Dependencies:** None

```python
class NQDataLoader:
    def __init__(self, split: str = "validation", num_samples: int = 100):
        """Load NaturalQuestions unanswerable subset."""
        ...
    
    def get_questions(self) -> List[str]:
        """Return list of question strings."""
        ...
```

### ModelModule (`models/generator.py`)

**Dependencies:** None

```python
class MistralGenerator:
    def __init__(self, model_name: str = "mistralai/Mistral-7B-v0.1"):
        """Initialize Mistral-7B for generation."""
        ...
    
    def generate_samples(self, question: str, k: int = 10, temperature: float = 0.7) -> List[str]:
        """Generate K diverse answers. Returns: List[str] with K answers."""
        ...
```

### UncertaintyModule (`methods/uncertainty.py`)

**Dependencies:** None

```python
class SemanticEntropyEstimator:
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2", threshold: float = 0.5):
        """Semantic entropy with clustering."""
        ...
    
    def compute_uncertainty(self, answers: List[str]) -> float:
        """Compute semantic entropy. Returns: float (higher = more uncertain)."""
        ...

class EnsembleBaseline:
    def compute_uncertainty(self, answers: List[str]) -> float:
        """Compute disagreement rate. Returns: float (higher = more uncertain)."""
        ...
```

### ExperimentModule (`experiment/runner.py`)

**Dependencies:** DataModule, ModelModule, UncertaintyModule

```python
class ExperimentRunner:
    def __init__(self, config: dict):
        """Initialize experiment with all components."""
        ...
    
    def run_experiment(self) -> dict:
        """Run full experiment. Returns: {auroc_semantic, auroc_ensemble, difference}."""
        ...
    
    def evaluate_gate(self, results: dict) -> bool:
        """Check gate condition. Returns: True if MUST_WORK gate passes."""
        ...
```

---

## 2. File Organization

```
h-e1/code/
├── data/
│   └── loader.py          # NaturalQuestions data loading
├── models/
│   └── generator.py       # Mistral-7B text generation
├── methods/
│   └── uncertainty.py     # Semantic entropy + ensemble baseline
├── experiment/
│   └── runner.py          # Experiment orchestration
├── config.py              # Single fixed config
└── main.py                # Entry point
```

---

## 3. Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Data Loading | Load NaturalQuestions unanswerable subset (100 samples) | 6 | 2+1+2+1 (Module=2, Deps=1, Algo=2, Integ=1) |
| E-2 | Model Setup | Load Mistral-7B and configure for K=10 generation | 8 | 2+2+2+2 (Module=2, Deps=2, Algo=2, Integ=2) |
| E-3 | Uncertainty Methods | Implement semantic entropy + ensemble baseline | 12 | 3+2+4+3 (Module=3, Deps=2, Algo=4, Integ=3) |
| E-4 | Experiment Runner | Run comparison and compute AUROC metrics | 10 | 3+2+3+2 (Module=3, Deps=2, Algo=3, Integ=2) |
| E-5 | Visualization | Generate AUROC comparison figures | 6 | 2+1+2+1 (Module=2, Deps=1, Algo=2, Integ=1) |

**Distribution:** VeryHigh(18-20): 0, High(14-17): 0, Medium(9-13): 2 [E-3, E-4], Low(4-8): 3 [E-1, E-2, E-5]

**Total Epic Tasks:** 5
**Total Complexity:** 42

---

## 4. Integration Points

### E-1 → E-2
Data loader provides questions to generator

### E-2 → E-3
Generator produces K=10 samples for uncertainty estimation

### E-3 → E-4
Both uncertainty methods feed into experiment runner

### E-4 → E-5
Experiment results used for visualization

---

## 5. Configuration Strategy

**Single fixed config (hardcoded dict)** - No configuration subtasks needed for EXISTENCE PoC.

All hyperparameters use defaults from research:
- K=10 samples
- Temperature=0.7
- Embedding model: all-MiniLM-L6-v2
- Clustering threshold: 0.5
- Seed: 42

---

## Summary

**Architecture Type:** Minimal PoC (EXISTENCE)
**Epic Tasks:** 5 (within LIGHT tier budget of 8 max)
**Complexity Level:** Medium (42 points)
**Implementation Approach:** Sequential pipeline (data → generation → uncertainty → evaluation)
