# Logic Design: H-E1 Structural Signal Existence

**Hypothesis:** Structural Signal Existence in LLM Code Coverage Prediction
**Type:** EXISTENCE (PoC)
**Date:** 2026-03-18
**Budget:** 5 subtasks allocated for Logic Agent

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: New implementation - no existing codebase to analyze
**Analyzed Path**: N/A (archived attempts exist but new implementation planned)
**Relevant Symbols**: None - fresh implementation from scratch

This is a clean PoC implementation using standard Python scientific stack (scikit-learn, radon, tree-sitter). No base hypothesis dependencies.

---

## Applied Patterns (Archon KB)

**Applied**: Standard scikit-learn regression pattern (Ridge with StandardScaler)
**Applied**: Python feature extraction pattern (radon + tree-sitter)
**Applied**: Statistical variance decomposition pattern

---

## Task Logic Specifications

### A-1: Setup & Data (Complexity: 8, Budget: 0)

**Applied**: Standard dataset loading pattern

#### API Signatures

```python
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

class CoverageEvalLoader:
    def __init__(self, dataset_path: str):
        """Initialize loader with dataset path."""
        self.dataset_path = dataset_path
        self.problems = None

    def load_problems(self) -> Dict:
        """Load CoverageEval dataset. Returns: dict with task_id keys."""
        ...

    def parse_coverage_data(self, problem: Dict) -> Dict:
        """Extract coverage metrics. Returns: {statement_cov: float, branch_cov: float}"""
        ...

    def get_all_solutions(self) -> pd.DataFrame:
        """Get all solutions. Returns: DataFrame [task_id, code, statement_coverage, branch_coverage]"""
        ...
```

### A-2: Feature Extraction (Complexity: 12, Budget: 1)

**Applied**: Radon + tree-sitter extraction pattern

#### API Signatures

```python
import numpy as np
from typing import Dict

class StructuralFeatureExtractor:
    def __init__(self):
        """Initialize feature extraction tools."""
        self.feature_names = [
            'cyclomatic_complexity', 'sloc', 'lloc', 'comment_ratio',
            'nesting_depth', 'branch_density', 'ast_entropy', 'function_count',
            'early_returns', 'exception_handlers', 'defensive_branches', 'code_to_complexity_ratio'
        ]

    def extract_radon_features(self, code: str) -> Dict[str, float]:
        """Extract radon metrics. Returns: {cyclomatic_complexity, sloc, lloc, comment_ratio}"""
        ...

    def extract_ast_features(self, code: str) -> Dict[str, float]:
        """Extract tree-sitter AST features. Returns: 8-dim dict."""
        ...

    def extract_all_features(self, code: str) -> np.ndarray:
        """Extract all 12 features. code: str -> [12,] float array"""
        ...

    def compute_vif(self, features: np.ndarray) -> np.ndarray:
        """Compute VIF for multicollinearity check. features: [N, 12] -> [12,] VIF values"""
        ...
```

#### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| code | str | Input code string |
| features | [12,] | 12-dim feature vector per solution |
| features_batch | [N, 12] | Batch of N solutions |
| vif | [12,] | VIF values per feature |

#### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Tree-sitter AST parsing | Implement nesting depth, branch density, AST entropy extraction |

### A-3: Baseline Model (Complexity: 5, Budget: 0)

**Applied**: Task-level mean baseline pattern

#### API Signatures

```python
import numpy as np
from typing import List

class TaskLevelBaseline:
    def __init__(self):
        """Initialize baseline."""
        self.task_means = {}

    def fit(self, task_ids: List[str], coverages: np.ndarray) -> None:
        """Fit task-level means. coverages: [N,]"""
        ...

    def predict(self, task_ids: List[str]) -> np.ndarray:
        """Predict using task means. Returns: [N,] predictions"""
        ...

    def score(self, task_ids: List[str], coverages: np.ndarray) -> float:
        """Compute R². Returns: float R² score"""
        ...
```

### A-4: Proposed Model (Complexity: 9, Budget: 1)

**Applied**: Ridge regression with StandardScaler pattern

#### API Signatures

```python
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
import numpy as np

class StructuralCoveragePredictor:
    def __init__(self, alpha: float = 1.0, random_state: int = 42):
        """Initialize Ridge regression model."""
        self.alpha = alpha
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.model = Ridge(alpha=alpha, random_state=random_state)

    def fit(self, features: np.ndarray, coverages: np.ndarray,
            task_ids: np.ndarray) -> None:
        """Fit Ridge model. features: [N, 12], coverages: [N,], task_ids: [N,]"""
        ...

    def predict(self, features: np.ndarray) -> np.ndarray:
        """Predict coverage. features: [N, 12] -> [N,] predictions"""
        ...

    def get_feature_importance(self) -> np.ndarray:
        """Get Ridge coefficients. Returns: [12,] importance scores"""
        ...

    def score(self, features: np.ndarray, coverages: np.ndarray) -> float:
        """Compute R². Returns: float R² score"""
        ...
```

#### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| features | [N, 12] | Normalized structural features |
| coverages | [N,] | Target coverage values (0-100) |
| task_ids | [N,] | Task identifiers for stratification |
| predictions | [N,] | Predicted coverage values |
| coefficients | [12,] | Ridge model weights |

#### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Task-level stratification | Implement Leave-One-Group-Out CV with task-level splits |

### A-5: Variance Analysis (Complexity: 14, Budget: 2)

**Applied**: Hierarchical R² decomposition pattern

#### API Signatures

```python
import numpy as np
from typing import Dict, Tuple, List
import pandas as pd

class VarianceAnalyzer:
    def __init__(self, config):
        """Initialize analyzer with config."""
        self.config = config

    def compute_residual_variance_ratio(self, task_data: pd.DataFrame,
                                       features: np.ndarray) -> float:
        """Compute R²_marginal / R²_conditional for one task. Returns: float ratio"""
        ...

    def hierarchical_r2_decomposition(self, data: pd.DataFrame,
                                     features: np.ndarray) -> Dict[str, float]:
        """Compute hierarchical R². Returns: {r2_task_only, r2_with_features, delta_r2}"""
        ...

    def compute_gate_metrics(self, per_task_ratios: List[float]) -> Dict[str, float]:
        """Compute gate metrics. Returns: {median_ratio, task_coverage_above_04}"""
        ...

    def bootstrap_confidence_interval(self, ratios: List[float],
                                     alpha: float = 0.05) -> Tuple[float, float]:
        """Bootstrap 95% CI. ratios: [164,] -> (lower, upper) CI bounds"""
        ...
```

#### Pseudo-code

```
1. Per-task variance ratio:
   For each task t:
     - Fit Model_marginal: coverage ~ structural_features
     - Fit Model_conditional: coverage ~ structural_features + semantic_cluster
     - ratio_t = R²_marginal / R²_conditional

2. Hierarchical decomposition:
   - Model_1: coverage ~ task_difficulty
   - Model_2: coverage ~ task_difficulty + structural_features
   - delta_r2 = R²_2 - R²_1

3. Bootstrap CI:
   For 1000 iterations:
     - Resample ratios with replacement
     - Compute median
   - CI = (2.5th percentile, 97.5th percentile)
```

#### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | VIF computation | Implement variance inflation factor check for multicollinearity |
| L-5-2 | Bootstrap CI | Implement bootstrap confidence interval with 1000 iterations |

### A-6: Visualization (Complexity: 10, Budget: 0)

**Applied**: Matplotlib standard plotting pattern

#### API Signatures

```python
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List

class ResultVisualizer:
    def __init__(self, output_dir: str):
        """Initialize visualizer with output directory."""
        self.output_dir = output_dir

    def plot_gate_metrics(self, median_ratio: float, ci: Tuple[float, float],
                         threshold: float) -> None:
        """Plot gate metrics bar chart. Saves to gate_metrics.png"""
        ...

    def plot_ratio_distribution(self, ratios: List[float]) -> None:
        """Plot per-task ratio histogram. Saves to ratio_distribution.png"""
        ...

    def plot_feature_importance(self, importance: np.ndarray,
                               feature_names: List[str]) -> None:
        """Plot Ridge coefficients. importance: [12,] -> bar chart"""
        ...

    def plot_complexity_vs_coverage(self, complexity: np.ndarray,
                                   coverage: np.ndarray) -> None:
        """Scatter plot. complexity: [N,], coverage: [N,]"""
        ...

    def plot_hierarchical_r2(self, r2_values: Dict[str, float]) -> None:
        """Stacked bar chart for hierarchical R². Saves to hierarchical_r2.png"""
        ...
```

### A-7: Integration (Complexity: 11, Budget: 1)

**Applied**: Pipeline orchestration pattern

#### API Signatures

```python
from typing import Dict
import pandas as pd

class ExperimentRunner:
    def __init__(self, config):
        """Initialize runner with config."""
        self.config = config
        self.loader = CoverageEvalLoader(config.dataset_path)
        self.extractor = StructuralFeatureExtractor()
        self.baseline = TaskLevelBaseline()
        self.proposed = StructuralCoveragePredictor(alpha=config.ridge_alpha)
        self.analyzer = VarianceAnalyzer(config)
        self.visualizer = ResultVisualizer("h-e1/figures")

    def run_full_pipeline(self) -> Dict[str, float]:
        """Execute full experiment. Returns: gate metrics dict"""
        ...

    def generate_validation_report(self, metrics: Dict) -> None:
        """Generate 04_validation.md with results."""
        ...
```

#### Pseudo-code

```
1. Load data:
   - data = loader.get_all_solutions()  # [N, 4] DataFrame

2. Extract features:
   - features = extractor.extract_all_features(data['code'])  # [N, 12]
   - vif = extractor.compute_vif(features)  # [12,]
   - assert all(vif < 5), "Multicollinearity detected"

3. Train models:
   - baseline.fit(data['task_id'], data['statement_coverage'])
   - proposed.fit(features, data['statement_coverage'], data['task_id'])

4. Evaluate:
   - per_task_ratios = []
   - For each task:
       - ratio = analyzer.compute_residual_variance_ratio(task_data, features)
       - per_task_ratios.append(ratio)
   - metrics = analyzer.compute_gate_metrics(per_task_ratios)
   - ci = analyzer.bootstrap_confidence_interval(per_task_ratios)

5. Visualize:
   - visualizer.plot_gate_metrics(metrics['median_ratio'], ci, 0.5)
   - visualizer.plot_ratio_distribution(per_task_ratios)
   - visualizer.plot_feature_importance(proposed.get_feature_importance())

6. Validate gate:
   - pass_condition = (metrics['median_ratio'] >= 0.5 and
                       metrics['task_coverage_above_04'] >= 0.7)
   - generate_validation_report(metrics)
   - return metrics
```

#### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Validation report generation | Generate 04_validation.md with gate status, figures, metrics |

---

## Data Flow Summary

```
CoverageEval JSON files
  → CoverageEvalLoader.get_all_solutions() → [N, 4] DataFrame
    → StructuralFeatureExtractor.extract_all_features() → [N, 12] features
      → StructuralCoveragePredictor.fit() + TaskLevelBaseline.fit()
        → VarianceAnalyzer.compute_residual_variance_ratio() → [164,] ratios
          → VarianceAnalyzer.compute_gate_metrics() → gate_metrics dict
            → ResultVisualizer.plot_gate_metrics() → gate_metrics.png
              → ExperimentRunner.generate_validation_report() → 04_validation.md
```

---

## Key Implementation Notes

1. **CoverageEval Integration**: Use `sys.path.append('coverage-eval')` and `from utils import read_problems`
2. **Random Seed**: Fix all random seeds to 42 for reproducibility
3. **VIF Check**: Fail fast if VIF ≥ 5 detected (multicollinearity)
4. **Leave-One-Group-Out CV**: Use task_id as group to prevent data leakage
5. **Gate Validation**: Compute both primary (median ratio ≥ 0.5) and secondary (70% coverage) metrics

---

## Subtask Summary

**Total Subtasks**: 5/5 used
- L-2-1: Tree-sitter AST parsing (A-2)
- L-4-1: Task-level stratification (A-4)
- L-5-1: VIF computation (A-5)
- L-5-2: Bootstrap CI (A-5)
- L-7-1: Validation report generation (A-7)

---

*Logic design for Phase 4 implementation | Target: Minimal PoC for EXISTENCE validation*
