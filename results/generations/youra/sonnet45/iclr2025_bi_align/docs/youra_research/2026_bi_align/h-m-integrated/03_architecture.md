---
name: System Architecture
type: architecture
hypothesis_id: h-m-integrated
hypothesis_type: MECHANISM
created_at: 2026-03-17
version: 1.0
patterns_applied: ["statistical pipeline", "paired comparison"]
---

# System Architecture: H-M-Integrated Linguistic Mechanism Validation

**Applied:** Statistical paired comparison pipeline

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Patterns extracted from h-e1 validated implementation
**Analyzed Path:** docs/youra_research/20260317_bi_align/h-e1/code/
**Findings:** Reusing h-e1 validated extraction pipeline (LinguisticMarkerExtractor, HHRLHFDataLoader, StatisticalAnalyzer). H-e1 achieved 100% precision with CV=0.781. H-m-integrated extends this with paired statistical comparison using scipy.stats.

---

## Architecture Overview

**Type:** Statistical paired comparison analysis (NOT model training)
**Infrastructure:** STANDARD (6-12 epic tasks, moderate complexity)
**Components:** 5 modules (data pairing, h-e1 extraction reuse, paired comparison, visualization, main orchestrator)

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| LinguisticMarkerExtractor | `from h_e1_code.extractor import LinguisticMarkerExtractor` | `h-e1/code/extractor.py` |
| HHRLHFDataLoader | `from h_e1_code.data_loader import HHRLHFDataLoader` | `h-e1/code/data_loader.py` |
| StatisticalAnalyzer | `from h_e1_code.analyzer import StatisticalAnalyzer` | `h-e1/code/analyzer.py` |
| Config | `from h_e1_code.config import Config` | `h-e1/code/config.py` |

**Verified from:** h-e1/code/ (actual implementation)

**Note:** Import paths will be adjusted to match local file structure (e.g., using sys.path or relative imports from parent directory).

---

## Module Definitions

### PairedDataLoader (`code/paired_data_loader.py`)

**Dependencies:** HHRLHFDataLoader (from h-e1)

```python
class PairedDataLoader:
    def __init__(self, base_loader: HHRLHFDataLoader): ...
    def load_paired_dataset(self) -> list[tuple[str, str]]: ...
    def get_split_pairs(self, split_name: str) -> list[tuple[str, str]]: ...
    def get_pair_count(self) -> int: ...
```

### PairedComparator (`code/paired_comparator.py`)

**Dependencies:** scipy.stats, numpy, LinguisticMarkerExtractor (from h-e1)

```python
class PairedComparator:
    def __init__(self, extractor: LinguisticMarkerExtractor): ...
    def extract_paired_features(self, pairs: list[tuple[str, str]]) -> tuple[np.ndarray, np.ndarray]: ...
    def paired_ttest(self, chosen: np.ndarray, rejected: np.ndarray) -> dict: ...
    def cohens_d_paired(self, chosen: np.ndarray, rejected: np.ndarray) -> float: ...
    def check_primary_gate(self, cohens_d: float, p_value: float) -> bool: ...
```

### InternalConsistencyAnalyzer (`code/consistency_analyzer.py`)

**Dependencies:** numpy

```python
class InternalConsistencyAnalyzer:
    def cronbachs_alpha(self, item_scores: np.ndarray) -> float: ...
    def compute_correlation_matrix(self, features: np.ndarray) -> np.ndarray: ...
    def check_secondary_gate(self, alpha: float) -> bool: ...
```

### CrossSplitValidator (`code/cross_split_validator.py`)

**Dependencies:** PairedComparator

```python
class CrossSplitValidator:
    def __init__(self, comparator: PairedComparator): ...
    def validate_per_split(self, split_pairs: dict[str, list]) -> dict[str, dict]: ...
    def count_passing_splits(self, split_results: dict) -> int: ...
    def check_tertiary_gate(self, passing_count: int) -> bool: ...
```

### MechanismVisualizer (`code/visualizer.py`)

**Dependencies:** matplotlib, seaborn

```python
class MechanismVisualizer:
    def plot_gate_metrics(self, cohens_d: float, alpha: float, p_value: float, output_path: str): ...
    def plot_forest_plot(self, split_results: dict, output_path: str): ...
    def plot_density_comparison(self, chosen: np.ndarray, rejected: np.ndarray, output_path: str): ...
    def plot_paired_differences(self, differences: np.ndarray, output_path: str): ...
    def plot_correlation_heatmap(self, corr_matrix: np.ndarray, output_path: str): ...
```

### MainRunner (`code/main.py`)

**Dependencies:** All above modules

```python
def main():
    # 1. Load paired data (chosen-rejected pairs)
    # 2. Extract features using h-e1 validated pipeline
    # 3. Compute paired t-test and Cohen's d (PRIMARY)
    # 4. Compute Cronbach's alpha (SECONDARY)
    # 5. Cross-split validation (TERTIARY)
    # 6. Generate visualizations
    # 7. Evaluate all gates and save results
    ...

if __name__ == "__main__":
    main()
```

### Configuration (`code/config.py`)

**Dependencies:** h-e1 Config (extends)

```python
class MechanismConfig:
    # Inherit h-e1 config
    BASE_CONFIG: Config

    # Gate thresholds
    COHENS_D_THRESHOLD: float = 0.15
    P_VALUE_THRESHOLD: float = 0.05
    CRONBACH_ALPHA_THRESHOLD: float = 0.7
    MIN_PASSING_SPLITS: int = 2

    # Output paths
    OUTPUT_DIR: str
    FIGURES_DIR: str
    RESULTS_FILE: str
    VALIDATION_REPORT: str
```

---

## File Structure

```
h-m-integrated/
├── code/
│   ├── main.py                      # Entry point
│   ├── config.py                    # Configuration
│   ├── paired_data_loader.py        # Pair organization
│   ├── paired_comparator.py         # Statistical comparison
│   ├── consistency_analyzer.py      # Cronbach's alpha
│   ├── cross_split_validator.py     # Cross-validation
│   ├── visualizer.py                # Figure generation
│   └── requirements.txt             # Dependencies
├── figures/                         # Output visualizations
│   ├── gate_metrics.png             # MANDATORY
│   ├── forest_plot.png
│   ├── density_plots.png
│   ├── paired_differences.png
│   └── marker_correlations.png
├── results/
│   └── statistics.json              # All statistical results
└── 04_validation.md                 # Results report
```

---

## Data Flow

1. `PairedDataLoader` → Load HH-RLHF, organize as 161K matched pairs
2. `PairedComparator` → Extract features using h-e1 pipeline, compute paired t-test + Cohen's d
3. `InternalConsistencyAnalyzer` → Compute Cronbach's alpha on difference scores
4. `CrossSplitValidator` → Repeat analysis per split (base, online, RS)
5. `MechanismVisualizer` → Generate 5 figures
6. `MainRunner` → Evaluate 3 gates (PRIMARY, SECONDARY, TERTIARY) and report PASS/FAIL

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Paired Data Structure | Load HH-RLHF and organize as matched pairs | 8 | M(2)+D(2)+A(2)+I(2) |
| M-2 | H-E1 Integration | Import and verify h-e1 extraction pipeline | 7 | M(2)+D(2)+A(1)+I(2) |
| M-3 | Paired Comparison | Implement paired t-test and Cohen's d calculation | 11 | M(3)+D(2)+A(4)+I(2) |
| M-4 | Internal Consistency | Implement Cronbach's alpha calculation | 9 | M(2)+D(1)+A(4)+I(2) |
| M-5 | Cross-Split Validation | Per-split analysis and replication check | 10 | M(2)+D(2)+A(3)+I(3) |
| M-6 | Statistical Visualization | Generate 5 required figures | 11 | M(3)+D(1)+A(3)+I(4) |
| M-7 | Gate Evaluation | Evaluate 3 gates and generate validation report | 9 | M(2)+D(2)+A(2)+I(3) |

**Distribution:**
- VeryHigh(18-20): []
- High(14-17): []
- Medium(9-13): [M-3, M-4, M-5, M-6, M-7]
- Low(4-8): [M-1, M-2]

**Total Complexity:** 65 (7 tasks)

---

## Dependencies

### Python Libraries

```txt
# Inherited from h-e1
datasets>=2.14.0          # HuggingFace HH-RLHF
spacy>=3.5.0              # POS tagging (h-e1 extraction)
numpy>=1.24.0             # Numerical operations
pandas>=2.0.0             # Data manipulation

# New for h-m-integrated
scipy>=1.10.0             # Paired t-test (ttest_rel)
matplotlib>=3.7.0         # Visualization
seaborn>=0.12.0           # Statistical plots
pingouin>=0.5.3           # Optional (Cronbach's alpha validation)
```

### External Resources

- spaCy model: `en_core_web_sm` (already downloaded for h-e1)
- HH-RLHF dataset: Auto-download via HuggingFace (cached from h-e1)
- h-e1 code: `../h-e1/code/` (validated extraction pipeline)

---

## Implementation Details

### Paired T-Test Implementation

```python
from scipy.stats import ttest_rel

# Paired t-test on modal verbs (primary marker)
t_stat, p_value = ttest_rel(chosen_features[:, 0], rejected_features[:, 0])
```

### Cohen's d for Paired Samples

```python
# Cohen's d formula for paired samples
differences = chosen_features[:, 0] - rejected_features[:, 0]
cohens_d = np.mean(differences) / np.std(differences, ddof=1)

# Gate check: d >= 0.15 AND p < 0.05 AND d < 0 (chosen < rejected)
primary_pass = (abs(cohens_d) >= 0.15) and (p_value < 0.05) and (cohens_d < 0)
```

### Cronbach's Alpha

```python
def cronbachs_alpha(item_scores: np.ndarray) -> float:
    """
    Args:
        item_scores: (N, k) array - N samples, k items (3 markers)
    Returns:
        alpha: Cronbach's alpha coefficient
    """
    k = item_scores.shape[1]  # Number of items (3)
    item_variances = np.var(item_scores, axis=0, ddof=1)
    total_variance = np.var(np.sum(item_scores, axis=1), ddof=1)

    alpha = (k / (k - 1)) * (1 - np.sum(item_variances) / total_variance)
    return alpha

# Compute on difference scores (chosen - rejected)
difference_matrix = chosen_features - rejected_features  # (N, 3)
alpha = cronbachs_alpha(difference_matrix)

# Gate check: alpha > 0.7
secondary_pass = (alpha > 0.7)
```

### Cross-Split Replication

```python
splits = ['train', 'test']  # HH-RLHF splits
results = {}

for split_name in splits:
    split_pairs = paired_loader.get_split_pairs(split_name)
    chosen_split, rejected_split = comparator.extract_paired_features(split_pairs)

    t_stat, p_value = ttest_rel(chosen_split[:, 0], rejected_split[:, 0])
    differences = chosen_split[:, 0] - rejected_split[:, 0]
    cohens_d = np.mean(differences) / np.std(differences, ddof=1)

    passed = (abs(cohens_d) >= 0.15) and (p_value < 0.05) and (cohens_d < 0)
    results[split_name] = {'d': cohens_d, 'p': p_value, 'pass': passed}

# Gate check: at least 2 of 3 splits pass (if 3 splits available)
tertiary_pass = sum([r['pass'] for r in results.values()]) >= 2
```

---

## Success Criteria Mapping

| Epic Task | Success Criteria |
|-----------|------------------|
| M-1 | 161K matched pairs loaded and verified |
| M-2 | H-e1 extraction methods imported and tested |
| M-3 | Paired t-test computed, Cohen's d >= 0.15, p < 0.05 |
| M-4 | Cronbach's alpha > 0.7 |
| M-5 | At least 2/3 splits pass primary criteria |
| M-6 | All 5 figures generated (gate_metrics.png MANDATORY) |
| M-7 | Validation report with PASS/FAIL for all 3 gates |

---

## Gate Conditions

### Primary Gate (P1) - MUST_WORK

**Criterion:** Modal verb frequency chosen < rejected, p < 0.05, Cohen's d >= 0.15

**Implementation:**
```python
primary_pass = (abs(cohens_d) >= 0.15) and (p_value < 0.05) and (cohens_d < 0)
```

**Pass Condition:** ALL three conditions met

### Secondary Gate (P2)

**Criterion:** Internal consistency Cronbach's α > 0.7

**Implementation:**
```python
alpha = cronbachs_alpha(chosen_features - rejected_features)
secondary_pass = (alpha > 0.7)
```

**Pass Condition:** α > 0.7

### Tertiary Gate (P3)

**Criterion:** Replication in at least 2 of 3 splits

**Implementation:**
```python
passing_count = sum([split_results[s]['pass'] for s in splits])
tertiary_pass = (passing_count >= 2)
```

**Pass Condition:** >= 2 splits show d >= 0.15, p < 0.05, d < 0

---

## Non-Functional Properties

**Performance:** CPU-only, 2-3 hours runtime for 161K pairs (based on h-e1: 10K in ~30 min)
**Reproducibility:** Fixed random seed (42), version pinning, dataset version tracking
**Storage:** ~2GB dataset cache (reused from h-e1) + 50MB results
**Infrastructure:** STANDARD (modular design, unit tests, comprehensive logging)

---

**Architecture Type: MECHANISM (full causal chain validation)**
**Total Epic Tasks: 7 (within 6-12 range)**
**Infrastructure Tier: STANDARD (moderate complexity, statistical rigor)**
