# System Architecture: H-E1
**Hypothesis:** Structural Signal Existence in LLM Code Coverage Prediction
**Type:** EXISTENCE (PoC)
**Date:** 2026-03-18

Applied: Minimal PoC experiment pattern, scikit-learn standard pipeline

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: New implementation from scratch
**Analyzed Path**: N/A
**Findings**: No existing codebase. Clean PoC implementation using scikit-learn, radon, tree-sitter.

---

## Architecture Overview

**Design Philosophy**: Minimal EXISTENCE validation - "does structural signal exist in coverage variance?"

**Core Components**:
- Data loading (Microsoft CoverageEval)
- Feature extraction (radon + tree-sitter)
- Baseline model (task-level mean)
- Proposed model (Ridge regression with structural features)
- Statistical analysis (variance decomposition)

**File Structure** (minimal PoC):
```
code/
├── config.py              # Single fixed config
├── data_loader.py         # CoverageEval data parsing
├── feature_extractor.py   # Structural metrics extraction
├── models.py              # Baseline + Ridge regression
├── train.py               # Model fitting
├── evaluate.py            # Variance decomposition + metrics
├── visualize.py           # Figure generation
└── run_experiment.py      # Main execution script
```

---

## Module Specifications

### Config (`code/config.py`)

**Dependencies**: None

```python
class ExperimentConfig:
    def __init__(self): ...

    # Dataset
    dataset_path: str = "coverage-eval"
    num_tasks: int = 164

    # Features
    num_features: int = 12
    scaler_type: str = "StandardScaler"

    # Model
    ridge_alpha: float = 1.0
    random_seed: int = 42

    # Thresholds
    median_ratio_threshold: float = 0.5
    task_coverage_threshold: float = 0.7
    delta_r2_threshold: float = 0.1
    vif_threshold: float = 5.0
```

### DataLoader (`code/data_loader.py`)

**Dependencies**: json, pandas

```python
class CoverageEvalLoader:
    def __init__(self, dataset_path: str): ...
    def load_problems(self) -> dict: ...
    def parse_coverage_data(self, problem: dict) -> dict: ...
    def get_all_solutions(self) -> pd.DataFrame: ...
```

### FeatureExtractor (`code/feature_extractor.py`)

**Dependencies**: radon, tree_sitter, numpy

```python
class StructuralFeatureExtractor:
    def __init__(self): ...
    def extract_radon_features(self, code: str) -> dict: ...
    def extract_ast_features(self, code: str) -> dict: ...
    def extract_all_features(self, code: str) -> np.ndarray: ...
    def compute_vif(self, features: np.ndarray) -> np.ndarray: ...
```

### BaselineModel (`code/models.py`)

**Dependencies**: numpy

```python
class TaskLevelBaseline:
    def __init__(self): ...
    def fit(self, task_ids: list, coverages: list) -> None: ...
    def predict(self, task_ids: list) -> np.ndarray: ...
    def score(self, task_ids: list, coverages: list) -> float: ...
```

### ProposedModel (`code/models.py`)

**Dependencies**: sklearn, numpy

```python
class StructuralCoveragePredictor:
    def __init__(self, alpha: float = 1.0, random_state: int = 42): ...
    def fit(self, features: np.ndarray, coverages: np.ndarray,
            task_ids: np.ndarray) -> None: ...
    def predict(self, features: np.ndarray) -> np.ndarray: ...
    def get_feature_importance(self) -> np.ndarray: ...
    def score(self, features: np.ndarray, coverages: np.ndarray) -> float: ...
```

### Trainer (`code/train.py`)

**Dependencies**: models, sklearn

```python
class ExperimentTrainer:
    def __init__(self, config: ExperimentConfig): ...
    def train_baseline(self, data: pd.DataFrame) -> TaskLevelBaseline: ...
    def train_proposed(self, data: pd.DataFrame,
                      features: np.ndarray) -> StructuralCoveragePredictor: ...
    def cross_validate(self, model, data: pd.DataFrame,
                      features: np.ndarray) -> dict: ...
```

### Evaluator (`code/evaluate.py`)

**Dependencies**: sklearn, numpy, scipy

```python
class VarianceAnalyzer:
    def __init__(self, config: ExperimentConfig): ...
    def compute_residual_variance_ratio(self, task_data: pd.DataFrame,
                                       features: np.ndarray) -> float: ...
    def hierarchical_r2_decomposition(self, data: pd.DataFrame,
                                     features: np.ndarray) -> dict: ...
    def compute_gate_metrics(self, per_task_ratios: list) -> dict: ...
    def bootstrap_confidence_interval(self, ratios: list,
                                     alpha: float = 0.05) -> tuple: ...
```

### Visualizer (`code/visualize.py`)

**Dependencies**: matplotlib, seaborn

```python
class ResultVisualizer:
    def __init__(self, output_dir: str): ...
    def plot_gate_metrics(self, median_ratio: float, ci: tuple,
                         threshold: float) -> None: ...
    def plot_ratio_distribution(self, ratios: list) -> None: ...
    def plot_feature_importance(self, importance: np.ndarray,
                               feature_names: list) -> None: ...
    def plot_complexity_vs_coverage(self, complexity: np.ndarray,
                                   coverage: np.ndarray) -> None: ...
    def plot_hierarchical_r2(self, r2_values: dict) -> None: ...
```

### MainExperiment (`code/run_experiment.py`)

**Dependencies**: All modules above

```python
def main():
    # Step 1: Load data
    loader = CoverageEvalLoader(config.dataset_path)
    data = loader.get_all_solutions()

    # Step 2: Extract features
    extractor = StructuralFeatureExtractor()
    features = extract_all_features_batch(data)

    # Step 3: Train models
    trainer = ExperimentTrainer(config)
    baseline = trainer.train_baseline(data)
    proposed = trainer.train_proposed(data, features)

    # Step 4: Evaluate
    analyzer = VarianceAnalyzer(config)
    metrics = analyzer.compute_gate_metrics(data, features)

    # Step 5: Visualize
    visualizer = ResultVisualizer("h-e1/figures")
    visualizer.plot_all_figures(metrics)

    # Step 6: Generate validation report
    generate_validation_report(metrics)
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Data | Setup environment, clone CoverageEval, load data | 8 | Module(2) + Deps(1) + Algo(3) + Integ(2) |
| A-2 | Feature Extraction | Implement radon + tree-sitter extraction for 12 features | 12 | Module(3) + Deps(2) + Algo(5) + Integ(2) |
| A-3 | Baseline Model | Implement task-level mean baseline | 5 | Module(1) + Deps(1) + Algo(2) + Integ(1) |
| A-4 | Proposed Model | Implement Ridge regression with StandardScaler | 9 | Module(2) + Deps(2) + Algo(3) + Integ(2) |
| A-5 | Variance Analysis | Implement hierarchical R² decomposition + VIF check | 14 | Module(3) + Deps(2) + Algo(6) + Integ(3) |
| A-6 | Visualization | Generate 5 required figures (gate metrics + diagnostics) | 10 | Module(2) + Deps(2) + Algo(4) + Integ(2) |
| A-7 | Integration | End-to-end pipeline + validation report generation | 11 | Module(3) + Deps(2) + Algo(3) + Integ(3) |

**Distribution**:
- VeryHigh (18-20): []
- High (14-17): [A-5]
- Medium (9-13): [A-2, A-4, A-6, A-7]
- Low (4-8): [A-1, A-3]

**Total Complexity**: 69 (target range: 50-80 for EXISTENCE)

---

## Data Flow

```
CoverageEval JSON files
  → DataLoader.load_problems()
    → FeatureExtractor.extract_all_features()
      → Trainer.train_baseline() + Trainer.train_proposed()
        → VarianceAnalyzer.compute_gate_metrics()
          → Visualizer.plot_all_figures()
            → validation_report.md
```

---

## External Dependencies

### Python Packages
```
radon==6.0.1
tree-sitter==0.22.3
tree-sitter-python==0.22.0
scikit-learn==1.5.0
numpy==1.26.4
pandas==2.2.0
matplotlib==3.9.0
seaborn==0.13.0
scipy==1.13.0
statsmodels==0.14.1
```

### External Repositories
- **microsoft/coverage-eval** (MIT): https://github.com/microsoft/coverage-eval
  - Clone method: `git clone https://github.com/microsoft/coverage-eval.git`
  - Usage: `sys.path.append('coverage-eval'); from utils import read_problems`

---

## Success Criteria Reference

**Gate Condition (MUST_WORK)**:
- Primary: Median residual variance ratio ≥ 0.5 with 95% CI
- Secondary: ≥70% of tasks above 0.4 threshold
- Validation: Hierarchical ΔR² ≥ 0.10
- Quality: VIF < 5 for all features

**PoC Pass Condition**:
- Code runs without error
- Proposed model R² > Baseline model R²

---

## Implementation Notes

### EXISTENCE-Specific Simplifications
1. **Single configuration**: No hyperparameter search
2. **Fixed random seed**: 42 for reproducibility
3. **No ablations**: Only baseline vs. proposed comparison
4. **CPU-only**: No GPU requirements
5. **Minimal validation**: Focus on existence proof, not optimization

### Key Technical Decisions
1. **Data source**: Microsoft CoverageEval (pre-computed coverage) vs. EvalPlus generation
   - Decision: Use CoverageEval for faster PoC
   - Rationale: Coverage data already available, reduces execution complexity

2. **Feature extraction**: Full tree-sitter parsing vs. radon-only
   - Decision: Radon for core metrics + simplified tree-sitter
   - Rationale: 12 features sufficient for EXISTENCE validation

3. **Model complexity**: Ridge vs. Neural Network
   - Decision: Ridge regression (L2 regularization)
   - Rationale: Interpretable, fast, sufficient for linear structural signal

### Critical Path
1. CoverageEval data loading (A-1)
2. Feature extraction working (A-2)
3. Both models implemented (A-3, A-4)
4. Variance decomposition correct (A-5)
5. Gate metrics computed and visualized (A-6, A-7)

---

*Architecture designed for Phase 3 → 4 handoff | Target: Minimal PoC for EXISTENCE validation*
