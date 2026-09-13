# Architecture: H-M1

**Date:** 2026-08-19
**Hypothesis:** Observed coupling persists when controlling for instance difficulty (partial phi ≥ 0.25)
**Type:** MECHANISM

Applied: Statistical analysis pattern (pingouin partial correlation + stratified quartile validation)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** h-e1 code verified - reusable data loading + coupling analyzer
**Analyzed Path:** docs/youra_research/h-e1_code/
**Findings:** CouplingAnalyzer.compute_phi_coefficient() reusable. Need difficulty control layer on top.

---

## File Structure

```
h-m1_code/
├── config.py                          # Difficulty config + h-e1 path
├── src/
│   ├── difficulty_generator.py        # Simulated difficulty scores
│   ├── partial_correlation.py         # Pingouin wrapper
│   ├── stratified_analyzer.py         # Quartile-based analysis
│   └── visualization.py               # 4 required plots
└── scripts/
    └── run_experiment.py              # Main execution
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From h-e1 Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| CouplingAnalyzer | `from h_e1_code.src.coupling_analyzer import CouplingAnalyzer` | `docs/youra_research/h-e1_code/src/coupling_analyzer.py` |
| load_multitrust | `from h_e1_code.src.data_loader import load_multitrust` | `docs/youra_research/h-e1_code/src/data_loader.py` |

**Note:** h-e1 code generates synthetic coupling data. h-m1 adds difficulty scores to this data.

---

## Module Interfaces

### config.py

**Dependencies:** None

```python
CONFIG = {
    "h_e1_path": "docs/youra_research/h-e1_code",
    "difficulty": {
        "distribution": "normal",
        "mean": 0.5,
        "std": 0.15,
        "seed": 42,
        "independence_threshold": 0.2
    },
    "analysis": {
        "partial_phi_threshold": 0.25,
        "n_quartiles": 4,
        "min_quartile_samples": 50
    },
    "paths": {"results": "results/", "figures": "figures/"}
}
```

---

### src/difficulty_generator.py

**Dependencies:** numpy, scipy

```python
def generate_difficulty_scores(n_samples: int, seed: int = 42) -> np.ndarray: ...

def validate_independence(difficulty: np.ndarray, dimension_labels: dict[str, np.ndarray], threshold: float = 0.2) -> bool: ...
```

---

### src/partial_correlation.py

**Dependencies:** pingouin, pandas

```python
def compute_partial_correlation(df: pd.DataFrame, dim1: str, dim2: str, covar: str = 'difficulty_score') -> tuple[float, float, tuple[float, float]]: ...

def analyze_all_pairs(df: pd.DataFrame, dimension_pairs: list[tuple[str, str]]) -> pd.DataFrame: ...
```

---

### src/stratified_analyzer.py

**Dependencies:** pandas, scipy

```python
def bin_by_quartiles(df: pd.DataFrame, difficulty_col: str = 'difficulty_score', n_quartiles: int = 4) -> pd.DataFrame: ...

def compute_quartile_phi(df: pd.DataFrame, dim1: str, dim2: str, quartile_col: str = 'quartile') -> pd.DataFrame: ...

def validate_persistence(quartile_results: pd.DataFrame, threshold: float = 0.25, min_quartiles: int = 3) -> bool: ...
```

---

### src/visualization.py

**Dependencies:** matplotlib, seaborn

```python
def plot_partial_vs_raw_phi(partial_results: pd.DataFrame, raw_phi: dict, output_path: str): ...

def plot_quartile_stratified_phi(quartile_results: pd.DataFrame, output_path: str): ...

def plot_difficulty_independence(df: pd.DataFrame, dimensions: list[str], output_path: str): ...

def plot_effect_size_retention(partial_results: pd.DataFrame, raw_phi: dict, output_path: str): ...
```

---

### scripts/run_experiment.py

**Dependencies:** All src modules + h-e1 modules

```python
def main():
    # 1. Load h-e1 coupling data (reuse h-e1 data loader)
    # 2. Generate difficulty scores (independent)
    # 3. Validate difficulty independence
    # 4. Compute partial correlations (6 pairs)
    # 5. Run stratified quartile analysis
    # 6. Dual validation comparison
    # 7. Generate 4 visualizations
    # 8. Save results
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Difficulty Generation | Generate + validate independence | 7 | 2+1+2+2 |
| M-2 | Partial Correlation | Pingouin integration for 6 pairs | 9 | 3+2+2+2 |
| M-3 | Stratified Analysis | Quartile binning + within-stratum phi | 10 | 3+2+3+2 |
| M-4 | Dual Validation | Compare partial vs stratified results | 6 | 2+1+2+1 |
| M-5 | Visualization | 4 required plots + gate figure | 8 | 3+2+2+1 |
| M-6 | Integration | Load h-e1 data + run full pipeline | 8 | 2+2+2+2 |

**Complexity Scoring:**
- M-1: Module_Size(2) + Dependencies(1) + Algorithm(2) + Integration(2) = 7
- M-2: Module_Size(3) + Dependencies(2) + Algorithm(2) + Integration(2) = 9
- M-3: Module_Size(3) + Dependencies(2) + Algorithm(3) + Integration(2) = 10
- M-4: Module_Size(2) + Dependencies(1) + Algorithm(2) + Integration(1) = 6
- M-5: Module_Size(3) + Dependencies(2) + Algorithm(2) + Integration(1) = 8
- M-6: Module_Size(2) + Dependencies(2) + Algorithm(2) + Integration(2) = 8

**Distribution:** Medium(9-13): [M-2, M-3], Low(4-8): [M-1, M-4, M-5, M-6]

---

## Implementation Notes

### Data Flow

1. h-e1 data (500 instances × 5 dimensions × 3 models)
2. → Add difficulty scores (Normal(0.5, 0.15), independent)
3. → Partial correlation (pingouin) for 6 h-e1 pairs
4. → Stratified analysis (4 quartiles, phi per quartile)
5. → Dual validation (partial phi ≥ 0.25 AND quartile persistence)

### Key Dependencies

- **pingouin >= 0.5.0** - partial_corr() for difficulty control
- **scipy >= 1.7.0** - chi2_contingency for phi coefficient
- **pandas >= 1.3.0** - qcut() for quartile binning
- **numpy >= 1.21.0** - difficulty score generation

### Reuse from h-e1

- `CouplingAnalyzer.compute_phi_coefficient()` - compute raw phi for comparison
- `load_multitrust()` - generate synthetic coupling data
- Dimension list: ['truthfulness', 'robustness', 'fairness', 'safety', 'privacy']

### Critical Validations

1. Difficulty independence: |corr(difficulty, dimension)| < 0.2
2. Quartile sample size: ≥50 instances per quartile
3. Partial phi range: [-1, 1] (valid correlation)
4. Dual validation agreement: Both methods show partial phi ≥ 0.25

---

## Success Criteria

**Gate (MUST_WORK):**
- Partial phi ≥ 0.25 for ≥2 dimension pairs
- Coupling persists in ≥3 quartiles for those pairs

**Technical:**
- All 6 h-e1 pairs analyzed
- Difficulty scores independent (validated)
- No runtime errors, reproducible (seed=42)

**Outputs:**
- `results/partial_correlation.csv` - 6 rows (pairs) × 4 cols (partial_r, p_value, CI95%)
- `results/stratified_analysis.csv` - 24 rows (6 pairs × 4 quartiles)
- `figures/partial_vs_raw_phi.png`
- `figures/quartile_stratified_phi.png`
- `figures/difficulty_independence.png`
- `figures/effect_size_retention.png`
