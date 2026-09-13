---
name: Logic Specification
type: logic
hypothesis_id: h-m-integrated
hypothesis_type: MECHANISM
created_at: 2026-03-17
version: 1.0
budget_subtasks: 5
---

# Logic Specification: H-M-Integrated Linguistic Mechanism Validation

**Applied:** Standard scipy.stats paired t-test pattern, NumPy statistical computations

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** API signatures verified from h-e1 actual code
**Analyzed Path:** docs/youra_research/20260317_bi_align/h-e1/code/
**Relevant Symbols:** LinguisticMarkerExtractor.extract_all_features(), HHRLHFDataLoader.get_all_responses(), StatisticalAnalyzer.compute_statistics(), Config (dataclass)

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

The following APIs are called from h-e1 hypothesis. Signatures verified from actual implementation:

```python
# From: h-e1/code/extractor.py (ACTUAL CODE)
class LinguisticMarkerExtractor:
    def __init__(
        self,
        spacy_model: str = "en_core_web_sm",
        hedging_markers: Set[str] = None,
        alternative_patterns: List[str] = None
    ):
        """Initialize extractor."""
        ...

    def extract_all_features(self, text: str) -> Dict[str, float]:
        """Extract all three marker types. Returns dict with modal_freq, hedging_freq, alt_freq, word_count."""
        ...

# From: h-e1/code/data_loader.py (ACTUAL CODE)
class HHRLHFDataLoader:
    def __init__(self, cache_dir: str = None):
        """Initialize data loader."""
        ...

    def load_dataset(self) -> Dict[str, Dataset]:
        """Load all HH-RLHF splits. Returns dict mapping split names to Dataset objects."""
        ...

    def preprocess_text(self, text: str) -> str:
        """Remove special tokens from text."""
        ...

# From: h-e1/code/analyzer.py (ACTUAL CODE)
class StatisticalAnalyzer:
    def __init__(self, random_seed: int = 42):
        """Initialize analyzer."""
        ...

    def compute_statistics(self, features: np.ndarray) -> Dict[str, float]:
        """Compute distributional statistics. Returns dict with mean, std, cv, min, max, median."""
        ...

# From: h-e1/code/config.py (ACTUAL CODE)
@dataclass
class Config:
    """Configuration dataclass."""
    dataset_name: str = "Anthropic/hh-rlhf"
    splits: List[str] = field(default_factory=lambda: ["train", "test"])
    random_seed: int = 42
    spacy_model: str = "en_core_web_sm"
    hedging_markers: Set[str] = field(default_factory=lambda: {...})
    alternative_patterns: List[str] = field(default_factory=lambda: [...])
    ...
```

**Verified from:** h-e1/code/ (actual implementation, NOT spec)

---

## M-1: Paired Data Structure [Complexity: 8, Budget: 1]

**Applied:** Standard HuggingFace datasets pattern

### API Signatures

```python
class PairedDataLoader:
    def __init__(self, base_loader: HHRLHFDataLoader):
        """Initialize paired data loader."""
        ...

    def load_paired_dataset(self) -> List[Tuple[str, str]]:
        """Load dataset as matched chosen-rejected pairs. Returns: [(chosen_1, rejected_1), ...]"""
        ...

    def get_split_pairs(self, split_name: str) -> List[Tuple[str, str]]:
        """Get pairs for specific split."""
        ...

    def get_pair_count(self) -> int:
        """Get total number of pairs."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| pairs | List[Tuple[str, str]] | List of (chosen, rejected) text pairs |

### Pseudo-code

```
1. Load base_loader.load_dataset() → dict of splits
2. For each split, iterate through examples:
   - Extract (example['chosen'], example['rejected'])
   - Preprocess both with base_loader.preprocess_text()
   - Append tuple to pairs list
3. Store split boundaries for get_split_pairs()
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Pair organization | Load dataset and create matched pairs structure |

---

## M-2: H-E1 Integration [Complexity: 7, Budget: 1]

**Applied:** Import verification pattern

### API Signatures

```python
# Import and verify h-e1 modules
def verify_h_e1_integration() -> Tuple[LinguisticMarkerExtractor, HHRLHFDataLoader, StatisticalAnalyzer]:
    """Import and verify h-e1 modules.

    Returns:
        Tuple of (extractor, loader, analyzer) instances
    """
    ...
```

### Pseudo-code

```
1. Add h-e1/code to sys.path
2. Import LinguisticMarkerExtractor, HHRLHFDataLoader, StatisticalAnalyzer
3. Create Config from h-e1
4. Initialize extractor with Config.spacy_model, hedging_markers, alternative_patterns
5. Test extraction on sample text
6. Verify output format matches expected dict keys
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Module import | Import and verify h-e1 extraction pipeline |

---

## M-3: Paired Comparison [Complexity: 11, Budget: 1]

**Applied:** scipy.stats.ttest_rel (paired t-test), Cohen's d for paired samples

### API Signatures

```python
class PairedComparator:
    def __init__(self, extractor: LinguisticMarkerExtractor):
        """Initialize comparator."""
        ...

    def extract_paired_features(self, pairs: List[Tuple[str, str]]) -> Tuple[np.ndarray, np.ndarray]:
        """Extract features from pairs. Returns: (chosen_features [N, 3], rejected_features [N, 3])"""
        ...

    def paired_ttest(self, chosen: np.ndarray, rejected: np.ndarray) -> Dict[str, float]:
        """Conduct paired t-test. Returns: {'t_stat': float, 'p_value': float}"""
        ...

    def cohens_d_paired(self, chosen: np.ndarray, rejected: np.ndarray) -> float:
        """Compute Cohen's d for paired samples. Returns: d (negative if chosen < rejected)"""
        ...

    def check_primary_gate(self, cohens_d: float, p_value: float) -> bool:
        """Check primary gate: |d| >= 0.15 AND p < 0.05 AND d < 0"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| chosen | [N, 3] | Features for chosen responses (modal, hedge, alt) |
| rejected | [N, 3] | Features for rejected responses |
| differences | [N] | chosen[:, 0] - rejected[:, 0] for primary DV |

### Pseudo-code

```
# Extract features
1. For each (chosen_text, rejected_text) in pairs:
   - chosen_feat = extractor.extract_all_features(chosen_text)
   - rejected_feat = extractor.extract_all_features(rejected_text)
   - Append [modal_freq, hedging_freq, alt_freq] to arrays

# Paired t-test
2. t_stat, p_value = ttest_rel(chosen[:, 0], rejected[:, 0])

# Cohen's d
3. differences = chosen[:, 0] - rejected[:, 0]
4. cohens_d = np.mean(differences) / np.std(differences, ddof=1)

# Gate check
5. primary_pass = (abs(cohens_d) >= 0.15) and (p_value < 0.05) and (cohens_d < 0)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Statistical test | Implement paired t-test and Cohen's d calculation |

---

## M-4: Internal Consistency [Complexity: 9, Budget: 1]

**Applied:** Cronbach's alpha formula from psychometrics

### API Signatures

```python
class InternalConsistencyAnalyzer:
    def cronbachs_alpha(self, item_scores: np.ndarray) -> float:
        """Compute Cronbach's alpha. item_scores: [N, k] → alpha: float"""
        ...

    def compute_correlation_matrix(self, features: np.ndarray) -> np.ndarray:
        """Compute correlation matrix. features: [N, 3] → corr: [3, 3]"""
        ...

    def check_secondary_gate(self, alpha: float) -> bool:
        """Check secondary gate: alpha > 0.7"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| item_scores | [N, k] | Difference scores for k markers (k=3) |
| corr_matrix | [k, k] | Correlation matrix between markers |

### Pseudo-code

```
# Cronbach's alpha
1. k = item_scores.shape[1]  # Number of items (3)
2. item_variances = np.var(item_scores, axis=0, ddof=1)
3. total_variance = np.var(np.sum(item_scores, axis=1), ddof=1)
4. alpha = (k / (k - 1)) * (1 - np.sum(item_variances) / total_variance)

# Apply to difference scores
5. difference_matrix = chosen_features - rejected_features  # [N, 3]
6. alpha = cronbachs_alpha(difference_matrix)

# Gate check
7. secondary_pass = (alpha > 0.7)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Cronbach's alpha | Implement internal consistency calculation |

---

## M-5: Cross-Split Validation [Complexity: 10, Budget: 0]

**Applied:** Per-split replication pattern

### API Signatures

```python
class CrossSplitValidator:
    def __init__(self, comparator: PairedComparator):
        """Initialize validator."""
        ...

    def validate_per_split(self, split_pairs: Dict[str, List[Tuple[str, str]]]) -> Dict[str, Dict[str, Any]]:
        """Validate per split. Returns: {'split_name': {'d': float, 'p': float, 'pass': bool}}"""
        ...

    def count_passing_splits(self, split_results: Dict[str, Dict]) -> int:
        """Count splits that pass primary criteria."""
        ...

    def check_tertiary_gate(self, passing_count: int, total_splits: int) -> bool:
        """Check tertiary gate: passing_count >= 2 (or 2/3 if 3 splits)"""
        ...
```

### Pseudo-code

```
1. For each split_name in ['train', 'test']:
   - Extract features for this split's pairs
   - Compute paired t-test and Cohen's d
   - Check if passes primary criteria
   - Store results

2. Count passing splits
3. Tertiary gate: passing_count >= 2
```

### Subtasks [0/0 used]

---

## M-6: Statistical Visualization [Complexity: 11, Budget: 0]

**Applied:** matplotlib/seaborn statistical plotting patterns

### API Signatures

```python
class MechanismVisualizer:
    def plot_gate_metrics(self, cohens_d: float, alpha: float, p_value: float, output_path: str):
        """Plot gate metrics comparison. MANDATORY figure."""
        ...

    def plot_forest_plot(self, split_results: Dict[str, Dict], output_path: str):
        """Plot effect sizes by split with 95% CI."""
        ...

    def plot_density_comparison(self, chosen: np.ndarray, rejected: np.ndarray, output_path: str):
        """Plot overlaid distributions for chosen vs rejected."""
        ...

    def plot_paired_differences(self, differences: np.ndarray, output_path: str):
        """Plot histogram of paired differences."""
        ...

    def plot_correlation_heatmap(self, corr_matrix: np.ndarray, output_path: str):
        """Plot correlation matrix heatmap."""
        ...
```

### Subtasks [0/0 used]

---

## M-7: Gate Evaluation [Complexity: 9, Budget: 0]

**Applied:** Standard gate evaluation orchestration

### API Signatures

```python
class GateEvaluator:
    def evaluate_all_gates(
        self,
        cohens_d: float,
        p_value: float,
        alpha: float,
        split_results: Dict[str, Dict]
    ) -> Dict[str, bool]:
        """Evaluate all three gates. Returns: {'primary': bool, 'secondary': bool, 'tertiary': bool}"""
        ...

    def generate_validation_report(
        self,
        gate_results: Dict[str, bool],
        statistics: Dict[str, Any],
        output_path: str
    ):
        """Generate 04_validation.md with gate assessment."""
        ...
```

### Subtasks [0/0 used]

---

## MainRunner Orchestration

**Applied:** Standard pipeline orchestration pattern

### API Signature

```python
def main():
    """Main orchestration pipeline."""
    # 1. Setup
    config = MechanismConfig()
    extractor, base_loader, _ = verify_h_e1_integration()

    # 2. Load paired data
    paired_loader = PairedDataLoader(base_loader)
    pairs = paired_loader.load_paired_dataset()

    # 3. Extract features
    comparator = PairedComparator(extractor)
    chosen_features, rejected_features = comparator.extract_paired_features(pairs)

    # 4. Primary gate: paired t-test + Cohen's d
    t_stat, p_value = comparator.paired_ttest(chosen_features, rejected_features)
    cohens_d = comparator.cohens_d_paired(chosen_features, rejected_features)
    primary_pass = comparator.check_primary_gate(cohens_d, p_value)

    # 5. Secondary gate: Cronbach's alpha
    consistency_analyzer = InternalConsistencyAnalyzer()
    alpha = consistency_analyzer.cronbachs_alpha(chosen_features - rejected_features)
    secondary_pass = consistency_analyzer.check_secondary_gate(alpha)

    # 6. Tertiary gate: cross-split validation
    split_pairs = {
        'train': paired_loader.get_split_pairs('train'),
        'test': paired_loader.get_split_pairs('test')
    }
    validator = CrossSplitValidator(comparator)
    split_results = validator.validate_per_split(split_pairs)
    tertiary_pass = validator.check_tertiary_gate(
        validator.count_passing_splits(split_results),
        len(split_pairs)
    )

    # 7. Visualizations
    visualizer = MechanismVisualizer()
    visualizer.plot_gate_metrics(cohens_d, alpha, p_value, "figures/gate_metrics.png")
    visualizer.plot_forest_plot(split_results, "figures/forest_plot.png")
    visualizer.plot_density_comparison(chosen_features[:, 0], rejected_features[:, 0], "figures/density_plots.png")
    differences = chosen_features[:, 0] - rejected_features[:, 0]
    visualizer.plot_paired_differences(differences, "figures/paired_differences.png")
    corr_matrix = consistency_analyzer.compute_correlation_matrix(chosen_features - rejected_features)
    visualizer.plot_correlation_heatmap(corr_matrix, "figures/marker_correlations.png")

    # 8. Gate evaluation
    evaluator = GateEvaluator()
    gate_results = {
        'primary': primary_pass,
        'secondary': secondary_pass,
        'tertiary': tertiary_pass
    }
    evaluator.generate_validation_report(
        gate_results,
        {'cohens_d': cohens_d, 'p_value': p_value, 'alpha': alpha, 'split_results': split_results},
        "04_validation.md"
    )

    print(f"\nGate Results:")
    print(f"  Primary (d >= 0.15, p < 0.05, d < 0): {'PASS' if primary_pass else 'FAIL'}")
    print(f"  Secondary (α > 0.7): {'PASS' if secondary_pass else 'FAIL'}")
    print(f"  Tertiary (2/3 splits pass): {'PASS' if tertiary_pass else 'FAIL'}")

if __name__ == "__main__":
    main()
```

---

## Configuration Extension

**Applied:** Dataclass extension pattern

### API Signature

```python
@dataclass
class MechanismConfig:
    """Configuration extending h-e1 Config."""

    # Inherit h-e1 config
    base_config: Config = field(default_factory=Config)

    # Gate thresholds
    cohens_d_threshold: float = 0.15
    p_value_threshold: float = 0.05
    cronbach_alpha_threshold: float = 0.7
    min_passing_splits: int = 2

    # Output paths
    output_dir: str = "."
    figures_dir: str = "figures"
    results_file: str = "results/statistics.json"
    validation_report: str = "04_validation.md"
```

---

## File Structure

```
code/
├── main.py                      # Entry point with main() orchestration
├── config.py                    # MechanismConfig extending h-e1
├── paired_data_loader.py        # PairedDataLoader
├── paired_comparator.py         # PairedComparator
├── consistency_analyzer.py      # InternalConsistencyAnalyzer
├── cross_split_validator.py     # CrossSplitValidator
├── visualizer.py                # MechanismVisualizer
├── gate_evaluator.py            # GateEvaluator
└── requirements.txt             # Dependencies
```

---

## Budget Summary

| Task | Complexity | Budget Used | Subtasks |
|------|------------|-------------|----------|
| M-1 | 8 | 1 | L-1-1 |
| M-2 | 7 | 1 | L-2-1 |
| M-3 | 11 | 1 | L-3-1 |
| M-4 | 9 | 1 | L-4-1 |
| M-5 | 10 | 0 | - |
| M-6 | 11 | 0 | - |
| M-7 | 9 | 0 | - |
| **Total** | **65** | **4/5** | **4 subtasks** |

**Status:** Within budget (4/5 subtasks used)

---

**Generated:** 2026-03-17
**Version:** 1.0
**Status:** Ready for Phase 4 implementation
