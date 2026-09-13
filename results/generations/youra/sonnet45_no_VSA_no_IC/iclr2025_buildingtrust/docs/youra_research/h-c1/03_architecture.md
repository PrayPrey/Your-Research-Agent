# Architecture: H-C1

**Date:** 2026-08-19
**Hypothesis:** Coupling matrices differ across models (Mantel test r < 0.7 for ≥1 model pair)
**Type:** COMPARISON

Applied: Statistical comparison pattern (scipy/sklearn + mantel library)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - no code to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch - no base hypothesis code exists

---

## File Structure

```
h-c1_code/
├── config.py                    # Model configs + thresholds
├── src/
│   ├── data_loader.py           # TrustLLM loading + stratified sampling
│   ├── coupling_matrix.py       # Phi coefficient + matrix construction
│   ├── mantel_test.py           # Cross-model matrix comparison
│   └── visualization.py         # Heatmaps + scatter plots
└── scripts/
    └── run_experiment.py        # Main execution
```

---

## Module Interfaces

### config.py

**Dependencies:** None

```python
CONFIG = {
    "models": ["GPT-4", "Claude-3", "Llama-3"],
    "dimensions": ["truthfulness", "robustness", "fairness", "safety", "privacy"],
    "dataset": {
        "name": "TrustLLM",
        "samples_per_dim": 100,
        "seed": 42
    },
    "statistical": {
        "phi_threshold": 0.3,
        "p_threshold": 0.01,
        "mantel_perms": 10000,
        "bonferroni_alpha": 0.0167
    },
    "paths": {
        "data": "data/",
        "results": "results/",
        "figures": "figures/"
    }
}
```

---

### src/data_loader.py

**Dependencies:** pandas, datasets

```python
def load_trustllm(models: list[str], samples_per_dim: int = 100, seed: int = 42) -> pd.DataFrame: ...

def stratified_sample(df: pd.DataFrame, dimension: str, n: int, seed: int) -> pd.DataFrame: ...

def binarize_labels(df: pd.DataFrame, dimension: str, threshold: float = 0.5) -> np.ndarray: ...
```

---

### src/coupling_matrix.py

**Dependencies:** scipy, sklearn, numpy

```python
class CouplingMatrix:
    def __init__(self, dimensions: list[str]): ...
    
    def compute_phi(self, labels_a: np.ndarray, labels_b: np.ndarray) -> tuple[float, float]: ...
    
    def build_matrix(self, labels_dict: dict[str, np.ndarray]) -> np.ndarray: ...
```

---

### src/mantel_test.py

**Dependencies:** mantel (jwcarr/mantel)

```python
def compare_matrices(matrix_a: np.ndarray, matrix_b: np.ndarray, perms: int = 10000) -> dict: ...

def run_all_comparisons(matrices: dict[str, np.ndarray], perms: int = 10000) -> pd.DataFrame: ...

def apply_bonferroni(results: pd.DataFrame, alpha: float = 0.05) -> pd.DataFrame: ...
```

---

### src/visualization.py

**Dependencies:** matplotlib, seaborn

```python
def plot_coupling_heatmaps(matrices: dict[str, np.ndarray], dimensions: list[str], output_path: str): ...

def plot_scatter_comparison(matrix_a: np.ndarray, matrix_b: np.ndarray, labels: tuple[str, str], output_path: str): ...

def plot_mantel_results(results: pd.DataFrame, output_path: str): ...
```

---

### scripts/run_experiment.py

**Dependencies:** All src modules

```python
def main():
    # Load TrustLLM data for 3 models
    # Build coupling matrices (3 models)
    # Run Mantel tests (3 comparisons)
    # Generate visualizations
    # Save validation report
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| C-1 | Data Pipeline | Load TrustLLM + stratified sampling | 9 | 3+2+2+2 |
| C-2 | Coupling Matrix | Phi coefficient + 5×5 matrix construction | 10 | 3+2+3+2 |
| C-3 | Mantel Test | Cross-model comparison + significance | 12 | 3+3+3+3 |
| C-4 | Visualization | Heatmaps + scatter plots + results | 8 | 2+2+2+2 |
| C-5 | Integration | Run 3-model experiment + validation report | 9 | 2+3+2+2 |
| C-6 | Gate Decision | Parse Mantel results + PASS/PARTIAL/FAIL | 6 | 2+1+2+1 |

**Complexity Scoring:**
- C-1: Module_Size(3) + Dependencies(2) + Algorithm(2) + Integration(2) = 9
- C-2: Module_Size(3) + Dependencies(2) + Algorithm(3) + Integration(2) = 10
- C-3: Module_Size(3) + Dependencies(3) + Algorithm(3) + Integration(3) = 12
- C-4: Module_Size(2) + Dependencies(2) + Algorithm(2) + Integration(2) = 8
- C-5: Module_Size(2) + Dependencies(3) + Algorithm(2) + Integration(2) = 9
- C-6: Module_Size(2) + Dependencies(1) + Algorithm(2) + Integration(1) = 6

**Distribution:** High(12): [C-3], Medium(8-10): [C-1, C-2, C-4, C-5], Low(6): [C-6]

---

## External Dependencies

### Python Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| numpy | ≥1.20 | Matrix operations |
| scipy | ≥1.7 | chi2_contingency |
| scikit-learn | ≥1.0 | matthews_corrcoef |
| mantel | ≥2.0 | Mantel test |
| pandas | ≥1.3 | Data handling |
| matplotlib | ≥3.5 | Visualization |
| seaborn | ≥0.11 | Heatmaps |
| datasets | ≥2.0 | HuggingFace TrustLLM |

---

## Data Flow

```
TrustLLM -> stratified_sample -> binarize_labels -> compute_phi -> build_matrix -> compare_matrices -> validation_report
```

---

## Notes

COMPARISON hypothesis - builds coupling matrices for 3 models then uses Mantel test to compare. No baseline model needed. Gate decision based on Mantel r < 0.7 threshold. All outcomes (PASS/PARTIAL/FAIL) proceed to Phase 5.
