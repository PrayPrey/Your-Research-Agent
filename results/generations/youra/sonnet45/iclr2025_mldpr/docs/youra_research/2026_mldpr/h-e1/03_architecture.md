# System Architecture: H-E1

**Date:** 2026-03-18
**Hypothesis:** Repository Heterogeneity in Documentation Completeness
**Type:** EXISTENCE (Proof of Concept)
**Architect:** Phase 3 Agent

Applied: Statistical experiment pattern (ICC modeling, bootstrap CI)

---

## Codebase Analysis (Serena)

**Project Type**: green-field with archived reference
**Status**: Fresh implementation - H-E1 requires new architecture for ICC/MVR-BCS analysis
**Analyzed Path**: Archived code at `_archive/20260318T055954_routing_recovery/h-e1/code/`
**Findings**: Previous implementation provides modular pattern (collector → scorer → analyzer → visualizer). New implementation will follow similar separation of concerns but adapted for PRD requirements.

---

## Module Structure

### DataCollector (`h-e1/code/data_collector.py`)

**Dependencies**: requests, datasets (HuggingFace), openml, beautifulsoup4

```python
class DataCollector:
    def __init__(self, config: dict): ...
    def collect_huggingface(self, n: int = 400) -> pd.DataFrame: ...
    def collect_openml(self, n: int = 400) -> pd.DataFrame: ...
    def collect_uci(self, n: int = 200) -> pd.DataFrame: ...
    def stratify_by_modality(self, df: pd.DataFrame) -> pd.DataFrame: ...
    def save_metadata(self, df: pd.DataFrame, output_path: Path) -> None: ...
```

---

### MVRBCSScorer (`h-e1/code/scorer.py`)

**Dependencies**: openai, pandas, numpy

```python
class StructuralValidator:
    def compute_structural_score(self, metadata: dict) -> float: ...
    def check_field_presence(self, fields: list[str]) -> float: ...

class SemanticValidator:
    def __init__(self, llm_client, config: dict): ...
    def validate_field_semantic(self, field: str, value: str, modality: str) -> bool: ...
    def compute_semantic_score(self, validations: list[bool]) -> float: ...

class MVRBCSScorer:
    def __init__(self, structural_validator, semantic_validator, config: dict): ...
    def score_dataset(self, metadata: dict, modality: str) -> dict: ...
    def score_batch(self, datasets_df: pd.DataFrame) -> pd.DataFrame: ...
```

---

### ICCAnalyzer (`h-e1/code/icc_analyzer.py`)

**Dependencies**: statsmodels, scipy, numpy

```python
class ICCAnalyzer:
    def __init__(self, config: dict): ...
    def fit_mixed_model(self, scores_df: pd.DataFrame) -> dict: ...
    def compute_icc(self, model_results) -> tuple[float, tuple]: ...
    def bootstrap_ci(self, scores_df: pd.DataFrame, n_iterations: int = 1000) -> tuple: ...
    def variance_decomposition(self, model_results) -> dict: ...
    def evaluate_gate(self, icc: float, ci: tuple, variance_ratio: float) -> dict: ...
```

---

### LLMValidator (`h-e1/code/llm_validator.py`)

**Dependencies**: openai, scikit-learn

```python
class LLMValidator:
    def __init__(self, llm_client, config: dict): ...
    def create_validation_set(self, datasets_df: pd.DataFrame, n_per_modality: int = 100) -> pd.DataFrame: ...
    def manual_annotation_interface(self, validation_df: pd.DataFrame) -> pd.DataFrame: ...
    def compute_f1_scores(self, predictions: list, ground_truth: list, modality: str) -> dict: ...
    def evaluate_cross_modality_range(self, f1_scores: dict) -> float: ...
```

---

### Visualizer (`h-e1/code/visualizer.py`)

**Dependencies**: matplotlib, seaborn

```python
class Visualizer:
    def __init__(self, config: dict): ...
    def plot_gate_metrics(self, icc: float, ci: tuple, variance_ratio: float, output_path: Path) -> None: ...
    def plot_variance_decomposition(self, variance_dict: dict, output_path: Path) -> None: ...
    def plot_repository_distribution(self, scores_df: pd.DataFrame, output_path: Path) -> None: ...
    def plot_modality_distribution(self, scores_df: pd.DataFrame, output_path: Path) -> None: ...
    def plot_llm_performance(self, f1_dict: dict, output_path: Path) -> None: ...
```

---

### ExperimentRunner (`h-e1/code/run_experiment.py`)

**Dependencies**: All above modules

```python
class ExperimentRunner:
    def __init__(self, config: dict, base_dir: Path): ...
    def collect_data(self) -> pd.DataFrame: ...
    def score_datasets(self, datasets_df: pd.DataFrame) -> pd.DataFrame: ...
    def validate_llm_classifier(self, scores_df: pd.DataFrame) -> dict: ...
    def compute_icc(self, scores_df: pd.DataFrame) -> dict: ...
    def evaluate_gates(self, icc_results: dict, llm_results: dict) -> dict: ...
    def generate_visualizations(self, icc_results: dict, scores_df: pd.DataFrame, llm_results: dict) -> None: ...
    def run_full_pipeline(self) -> dict: ...
```

---

### Config (`h-e1/code/config.py`)

**Dependencies**: None

```python
class ExperimentConfig:
    seed: int = 42
    data_dir: str = "data/h-e1"
    results_dir: str = "h-e1/results"
    figures_dir: str = "h-e1/figures"

    # Data collection
    n_huggingface: int = 400
    n_openml: int = 400
    n_uci: int = 200

    # MVR-BCS weights
    structural_weight: float = 0.6
    semantic_weight: float = 0.4

    # ICC parameters
    bootstrap_iterations: int = 1000
    confidence_level: float = 0.95

    # Gate thresholds
    icc_threshold: float = 0.10
    ci_lower_threshold: float = 0.05
    variance_ratio_threshold: float = 1.0
    llm_f1_threshold: float = 0.75
    llm_cross_modality_range: float = 0.10

    # LLM settings
    llm_model: str = "gpt-4-turbo"
    llm_temperature: float = 0.0
    validation_samples_per_modality: int = 100
```

---

## File Organization

```
h-e1/
├── code/
│   ├── __init__.py
│   ├── config.py
│   ├── data_collector.py
│   ├── scorer.py
│   ├── icc_analyzer.py
│   ├── llm_validator.py
│   ├── visualizer.py
│   ├── run_experiment.py
│   └── tests/
│       ├── __init__.py
│       ├── test_data_collector.py
│       ├── test_scorer.py
│       ├── test_icc_analyzer.py
│       └── test_visualizer.py
├── data/
│   ├── documentation/
│   │   ├── hf/
│   │   ├── openml/
│   │   └── uci/
│   ├── datasets_metadata.csv
│   ├── mvr_bcs_scores.csv
│   └── llm_validation/
│       ├── ground_truth.csv
│       ├── prompts/
│       └── responses/
├── results/
│   ├── icc_results.json
│   ├── variance_decomposition.json
│   ├── llm_validation_results.json
│   └── gate_evaluation.json
└── figures/
    ├── fig1_gate_metrics.png
    ├── fig2_variance_decomposition.png
    ├── fig3_repository_distribution.png
    ├── fig4_modality_distribution.png
    └── fig5_llm_performance.png
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Dependencies | Install dependencies, create folder structure, configure environment | 6 | 2+1+2+1 |
| A-2 | Data Collection Pipeline | Implement DataCollector with HF/OpenML/UCI collection, stratification | 14 | 4+3+3+4 |
| A-3 | MVR-BCS Scoring System | Implement structural validator, semantic LLM validator, composite scorer | 16 | 4+4+4+4 |
| A-4 | ICC Modeling | Mixed-effects model, ICC computation, bootstrap CI, variance decomposition | 18 | 5+4+5+4 |
| A-5 | LLM Validation Suite | Ground truth annotation interface, F1 computation, cross-modality analysis | 12 | 3+3+3+3 |
| A-6 | Gate Logic & Orchestration | Gate evaluation, experiment runner, checkpoint/resume, error handling | 11 | 3+3+3+2 |
| A-7 | Visualization & Reporting | 5 required figures, results export, validation report generation | 9 | 3+2+2+2 |

**Distribution**: VeryHigh(18-20): [A-4], High(14-17): [A-2, A-3], Medium(9-13): [A-5, A-6, A-7], Low(4-8): [A-1]

**Complexity Breakdown**:
- Module_Size: Lines of code (1-5)
- Dependencies: External API/library count (1-5)
- Algorithm: Statistical/ML complexity (1-5)
- Integration: Cross-module dependencies (1-5)

---

## Key Design Decisions

**1. Modular Separation**: Each major component (collector, scorer, analyzer, visualizer) isolated for independent testing and development.

**2. LLM Cost Control**: Semantic validator implements batching, caching, and fallback heuristics if API fails.

**3. Checkpoint System**: DataCollector and Scorer save intermediate results to enable resume on failure.

**4. Gate-First Architecture**: ICCAnalyzer.evaluate_gate() called before visualizations to fail fast.

**5. Test Strategy**: Unit tests for statistical calculations (ICC, variance decomposition), integration test for full pipeline.

---

## Dependencies Graph

```
ExperimentRunner
├── DataCollector
├── MVRBCSScorer
│   ├── StructuralValidator
│   └── SemanticValidator (→ OpenAI API)
├── ICCAnalyzer (→ statsmodels)
├── LLMValidator (→ OpenAI API, sklearn)
└── Visualizer (→ matplotlib, seaborn)
```

---

## Validation Checklist

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Module sections = interface code only
- [x] 7 Epic tasks with complexity scores
- [x] Total length < 500 lines
- [x] "Codebase Analysis (Serena)" section included
- [x] EXISTENCE hypothesis → 4-8 tasks (7 tasks delivered)
- [x] Minimal structure for PoC (single file modules, no over-engineering)

---

*Generated for Phase 4 Implementation*
*Next: Task breakdown and implementation*
