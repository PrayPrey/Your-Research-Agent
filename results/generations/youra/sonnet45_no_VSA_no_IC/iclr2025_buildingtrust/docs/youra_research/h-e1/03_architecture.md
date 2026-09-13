# Architecture: H-E1

**Date:** 2026-08-19
**Hypothesis:** At least one model exhibits statistically significant coupling (phi ≥ 0.3, p < 0.01) for at least one dimension pair
**Type:** EXISTENCE (PoC)

Applied: Statistical PoC pattern (scipy/sklearn standard library)

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase
**Status:** existing patterns found
**Analyzed Path:** h-e1_code/
**Findings:** Working implementation exists - clustering-based approach differs from PRD spec (phi coefficient). Code uses chi2_contingency + clustering, PRD requests phi coefficient + contingency tables.

---

## File Structure

```
h-e1_code/
├── config.py                    # Single fixed config
├── src/
│   ├── data_loader.py           # MultiTrust loading + binary labels
│   ├── coupling_analyzer.py     # Phi coefficient analysis (NEW)
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
    "models": {
        "gpt-4": {"model": "gpt-4", "temperature": 0.0, "max_tokens": 512},
        "claude-3-sonnet": {"model": "claude-3-sonnet-20240229", "temperature": 0.0, "max_tokens": 512},
        "llama-3-70b": {"model": "meta-llama/Llama-3-70b", "temperature": 0.0, "max_tokens": 512}
    },
    "dataset": {"name": "thu-ml/MultiTrust", "samples": 500, "seed": 42},
    "statistical": {"phi_threshold": 0.3, "p_threshold": 0.01},
    "paths": {"data": "data/", "results": "results/", "figures": "figures/"}
}
```

---

### src/data_loader.py

**Dependencies:** pandas, datasets (HuggingFace)

```python
def load_multitrust(samples: int = 500, seed: int = 42) -> pd.DataFrame: ...

def extract_binary_labels(df: pd.DataFrame, dimensions: list[str]) -> dict[str, np.ndarray]: ...

def evaluate_model_api(model_name: str, prompts: list[str], config: dict) -> list[str]: ...
```

---

### src/coupling_analyzer.py (NEW)

**Dependencies:** scipy, sklearn, numpy

```python
class CouplingAnalyzer:
    def __init__(self, dimensions: list[str]): ...
    
    def compute_phi_coefficient(self, labels_d1: np.ndarray, labels_d2: np.ndarray) -> tuple[float, float]: ...
    
    def analyze_model(self, labels: dict[str, np.ndarray]) -> pd.DataFrame: ...
```

---

### src/visualization.py

**Dependencies:** matplotlib, seaborn

```python
def plot_coupling_heatmap(phi_matrix: np.ndarray, dimensions: list[str], output_path: str): ...

def plot_significance_scatter(results: pd.DataFrame, output_path: str): ...

def plot_gate_metrics(results: dict, output_path: str): ...
```

---

### scripts/run_experiment.py

**Dependencies:** All src modules

```python
def main():
    # Load data
    # Evaluate 3 models via API
    # Compute phi coefficients
    # Generate visualizations
    # Save results
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Pipeline | Load MultiTrust + API evaluation | 8 | 2+2+2+2 |
| A-2 | Coupling Analyzer | Implement phi coefficient computation | 6 | 2+1+2+1 |
| A-3 | Visualization | Heatmap + scatter plots + gate figure | 5 | 2+1+1+1 |
| A-4 | Integration | Run 3-model experiment + results output | 6 | 2+2+1+1 |

**Complexity Scoring:**
- A-1: Module_Size(2) + Dependencies(2) + Algorithm(2) + Integration(2) = 8
- A-2: Module_Size(2) + Dependencies(1) + Algorithm(2) + Integration(1) = 6
- A-3: Module_Size(2) + Dependencies(1) + Algorithm(1) + Integration(1) = 5
- A-4: Module_Size(2) + Dependencies(2) + Algorithm(1) + Integration(1) = 6

**Distribution:** Low(4-8): [A-1, A-2, A-3, A-4]

---

## Notes

EXISTENCE PoC - minimal implementation. Existing h-e1_code/ uses clustering approach; PRD specifies phi coefficient. New coupling_analyzer.py replaces analysis.py chi2 logic. Reuse data_loader.py structure, update for MultiTrust instead of synthetic data.
