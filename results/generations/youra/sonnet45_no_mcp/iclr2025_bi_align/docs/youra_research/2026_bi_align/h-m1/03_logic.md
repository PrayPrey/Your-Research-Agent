# Logic Design & Implementation Details
# Hypothesis: h-m1 - Annotation Consistency Study

**Version:** 1.0  
**Date:** 2026-04-19  
**Hypothesis ID:** h-m1  
**Focus:** API Signatures, Algorithms, Training Protocol Logic

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** API signatures verified from h-e1 base code  
**Analyzed Path:** `/home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_bi_align_3/docs/youra_research/20260419_bi_align/h-e1/code/`  
**Relevant Symbols:** stratified_sample, load_hh_rlhf_dataset, present_sample_for_annotation, save_annotations, load_annotations, compute_cohens_kappa, cohen_kappa_score

**Applied:** KB-Pattern-AnnotationStudy, KB-Pattern-InterRaterReliability

---

## M-1: Data Preparation with Violation-Type Stratification [Complexity: 8, Budget: 1]

**Applied:** Standard stratified sampling pattern

### API Signatures

```python
def stratified_sample_by_violation_type(
    dataset: Dataset,
    sample_size: int = 300,
    violation_taxonomy: Dict[str, List[int]],
    seed: int = 42
) -> pd.DataFrame:
    """Stratified sampling by violation type. Returns: (300, 6)"""
    ...

def create_calibration_set(
    dataset: Dataset,
    calibration_size: int = 50,
    seed: int = 42
) -> pd.DataFrame:
    """Separate calibration samples. Returns: (50, 6)"""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| dataset | (N,) | HF Dataset |
| samples | (300, 6) | [id, prompt, rejected, chosen, length, violation_type] |
| calibration | (50, 6) | Disjoint from test set |

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M1-1 | ViolationTypeMapping | Map h-e1 taxonomy to samples |

---

## M-2: Training Protocol Implementation [Complexity: 10, Budget: 2]

**Applied:** Sequential training workflow pattern

### API Signatures

```python
class TrainingProtocol:
    def __init__(self, guidelines_path: str):
        """Initialize with HH-RLHF guidelines."""
        self.guidelines: Dict[str, str] = ...
        self.calibration_threshold: float = 0.60
    
    def load_hhrlhf_guidelines(self, path: str) -> Dict[str, str]:
        """Load criteria from YAML. Returns: Dict[criterion_id, description]"""
        ...
    
    def present_training_materials(self, annotator_id: int) -> None:
        """Display guidelines (30 min presentation)."""
        ...
    
    def run_calibration_phase(
        self,
        annotator_id: int,
        calibration_samples: pd.DataFrame,
        gold_labels: pd.Series
    ) -> Tuple[float, bool]:
        """Calibration annotations. Returns: (kappa, passed_gate)"""
        ...
```

### Pseudo-code

```
1. Load guidelines from YAML (6 violation criteria)
2. For each annotator:
   a. present_training_materials() - display guidelines
   b. Collect calibration annotations (50 samples)
   c. Calculate Cohen's κ vs gold labels
   d. If κ < 0.60 → fail (require re-training)
   e. If κ ≥ 0.60 → pass (proceed to main annotation)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M2-1 | GuidelinesDocument | Create YAML with HH-RLHF criteria |
| L-M2-2 | CalibrationGate | Implement κ ≥ 0.60 gate logic |

---

## M-3: Annotation Collection with Randomization [Complexity: 9, Budget: 1]

**Applied:** Per-annotator randomization pattern

### API Signatures

```python
def collect_annotations_with_training(
    samples: pd.DataFrame,
    annotator_id: int,
    training_protocol: TrainingProtocol,
    output_file: str
) -> pd.DataFrame:
    """Full workflow: training → calibration → main annotation. Returns: (300, 3)"""
    ...

def randomize_presentation_order(
    samples: pd.DataFrame,
    annotator_id: int,
    seed: int = 42
) -> pd.DataFrame:
    """Randomize per annotator. Returns: shuffled (300, 6)"""
    ...
```

### Pseudo-code

```
1. Run training_protocol.run_calibration_phase()
2. If calibration fails → abort
3. If calibration passes:
   a. Randomize sample order (seed + annotator_id)
   b. Call collect_annotations_batch() from h-e1
   c. Save to CSV with annotator_id
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M3-1 | RandomizationLogic | Per-annotator seed-based randomization |

---

## M-4: Inter-Annotator Agreement Analysis [Complexity: 7, Budget: 1]

**Applied:** Reuse h-e1 agreement calculation

### API Signatures

```python
def compute_pairwise_kappa(
    annotations: pd.DataFrame,
    n_annotators: int = 3
) -> Tuple[float, List[float], pd.DataFrame]:
    """Calculate average pairwise Cohen's κ. Returns: (avg_kappa, [k12, k13, k23], matrix)"""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| annotations | (900, 3) | 3 annotators × 300 samples |
| rating_matrix | (300, 3) | Pivoted |
| pairwise_kappas | (3, 3) | Symmetric matrix |

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M4-1 | PairwiseWrapper | Wrapper for h-e1's compute_cohens_kappa |

---

## M-5: Agreement with Original Labels [Complexity: 6, Budget: 0]

**Applied:** Simple proportion calculation

### API Signatures

```python
def compute_agreement_with_original(
    annotations: pd.DataFrame,
    original_labels: pd.Series
) -> Tuple[float, List[float]]:
    """Agreement with HH-RLHF labels. Returns: (mean_agreement, [a1, a2, a3])"""
    ...
```

### Pseudo-code

```
1. For each annotator:
   a. Compare annotations to original labels
   b. agreement[i] = matches / 300
2. mean_agreement = mean(agreement)
```

### Subtasks [0/0 used]

No subtasks - straightforward implementation.

---

## M-6: Statistical Hypothesis Testing [Complexity: 8, Budget: 1]

**Applied:** One-sample t-test pattern

### API Signatures

```python
def one_sample_ttest_kappa(
    kappa_values: List[float],
    null_threshold: float = 0.60,
    alternative_threshold: float = 0.70,
    alpha: float = 0.05
) -> Dict[str, float]:
    """Test H0: κ < 0.60 vs H1: κ ≥ 0.70. Returns: {t, p, mean, ci_lower, ci_upper}"""
    ...

def gate_decision(
    avg_kappa: float,
    avg_agreement: float,
    p_value: float,
    kappa_threshold: float = 0.70,
    agreement_threshold: float = 0.75,
    alpha: float = 0.05
) -> str:
    """Determine PASS/PARTIAL/FAIL. Returns: "PASS" | "PARTIAL" | "FAIL" """
    ...
```

### Pseudo-code

```
1. One-sample t-test:
   from scipy.stats import ttest_1samp
   t_stat, p_value = ttest_1samp(kappa_values, popmean=null_threshold, alternative='greater')

2. Gate logic:
   primary_pass = (avg_kappa >= 0.70) and (p_value < 0.05)
   secondary_pass = (avg_agreement >= 0.75)
   
   if primary_pass and secondary_pass: return "PASS"
   elif primary_pass or secondary_pass: return "PARTIAL"
   else: return "FAIL"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M6-1 | GateLogic | Combined gate decision (both conditions) |

---

## M-7: Visualization Generation [Complexity: 9, Budget: 0]

**Applied:** Standard matplotlib/seaborn patterns

### API Signatures

```python
def plot_gate_metrics_comparison(
    results: Dict[str, float],
    thresholds: Dict[str, float],
    output_path: str
) -> None:
    """Bar chart: target vs actual for κ and agreement."""
    ...

def plot_inter_annotator_matrix(
    pairwise_kappas: pd.DataFrame,
    output_path: str
) -> None:
    """3×3 heatmap of pairwise κ values."""
    ...

def plot_agreement_distribution(
    per_annotator_agreement: List[float],
    threshold: float = 0.75,
    output_path: str
) -> None:
    """Bar chart: each annotator's agreement with threshold line."""
    ...

def plot_confusion_matrices(
    annotations: pd.DataFrame,
    original_labels: pd.Series,
    output_path: str
) -> None:
    """3 confusion matrices (one per annotator)."""
    ...
```

### Subtasks [0/0 used]

No subtasks - standard visualization implementations.

---

## M-8: Experiment Orchestration [Complexity: 11, Budget: 1]

**Applied:** Sequential pipeline with error handling

### API Signatures

```python
def run_h_m1_experiment(config: Dict) -> Dict:
    """
    Main experiment orchestration.
    
    Returns:
        {
            "calibration_results": Dict[int, Tuple[float, bool]],
            "avg_kappa": float,
            "avg_agreement": float,
            "p_value": float,
            "gate_decision": str
        }
    """
    ...
```

### Pseudo-code

```
1. Load and sample data
   dataset = load_hh_rlhf_dataset()
   test_samples = stratified_sample_by_violation_type(dataset, 300)
   calibration = create_calibration_set(dataset, 50)

2. For each annotator (n=3):
   protocol = TrainingProtocol("guidelines.yaml")
   kappa, passed = protocol.run_calibration_phase(annotator_id, calibration, gold_labels)
   if not passed:
       raise CalibrationFailure(f"Annotator {annotator_id} failed calibration: κ={kappa:.3f} < 0.60")
   
   annotations = collect_annotations_with_training(test_samples, annotator_id, protocol)

3. Compute inter-annotator agreement
   avg_kappa, kappa_list, matrix = compute_pairwise_kappa(annotations)

4. Test statistical hypotheses
   test_results = one_sample_ttest_kappa(kappa_list)
   
5. Agreement with original
   avg_agreement, per_annotator = compute_agreement_with_original(annotations, original_labels)

6. Gate decision
   decision = gate_decision(avg_kappa, avg_agreement, test_results['p_value'])

7. Generate visualizations
   plot_gate_metrics_comparison(...)
   plot_inter_annotator_matrix(matrix)
   plot_agreement_distribution(per_annotator)
   plot_confusion_matrices(annotations, original_labels)

8. Write report
   write_report(results, decision)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M8-1 | ErrorHandling | Calibration failure handling and retry logic |

---

## External Dependencies API (Base Hypothesis)

The following APIs are called from h-e1 base hypothesis. Signatures verified from actual implementation:

```python
# From: h-e1/code/src/data/sampler.py (ACTUAL CODE)
def stratified_sample(
    dataset: Dataset,
    sample_size: int = 500,
    strata_column: str = "length_quartile",
    seed: int = 42
) -> pd.DataFrame:
    """Stratified sampling. Returns: (sample_size, 5)"""
    ...

# From: h-e1/code/src/data/loader.py (ACTUAL CODE)
def load_hh_rlhf_dataset(
    dataset_name: str = "Anthropic/hh-rlhf",
    subset: str = None,
    split: str = "train",
    cache_dir: str = None
) -> Dataset:
    """Load HH-RLHF dataset. Returns: HF Dataset"""
    ...

# From: h-e1/code/src/annotation/interface.py (ACTUAL CODE)
def present_sample_for_annotation(
    sample: Dict[str, str],
    violation_criteria: List[str],
    annotator_id: int
) -> bool:
    """Present sample to annotator. Returns: bool (violation judgment)"""
    ...

def collect_annotations_batch(
    samples: pd.DataFrame,
    annotator_id: int,
    violation_criteria: List[str],
    output_file: str = "data/annotations.csv"
) -> pd.DataFrame:
    """Collect all annotations. Returns: (n_samples, 3)"""
    ...

# From: h-e1/code/src/annotation/storage.py (ACTUAL CODE)
def save_annotations(annotations: pd.DataFrame, output_file: str) -> None:
    """Save to CSV."""
    ...

def load_annotations(annotation_file: str) -> pd.DataFrame:
    """Load from CSV. Returns: (n, 3)"""
    ...

# From: h-e1/code/src/analysis/agreement.py (ACTUAL CODE)
def compute_cohens_kappa(
    annotations: pd.DataFrame,
    n_annotators: int = 3
) -> Tuple[float, pd.DataFrame]:
    """Calculate Cohen's κ. Returns: (overall_kappa, pairwise_matrix)"""
    ...

def cohen_kappa_score(rater1: np.ndarray, rater2: np.ndarray) -> float:
    """Cohen's κ between two raters. Returns: float"""
    ...
```

**Verified from:** h-e1/code/ (actual implementation, NOT spec!)

**Adaptation Strategy:**
- M-1: Extend stratified_sample to support violation_type stratification
- M-3: Reuse collect_annotations_batch with randomized samples
- M-4: Wrap compute_cohens_kappa to return (avg, list, matrix)

---

## Data Flow Summary

```
HH-RLHF Dataset
    ↓
[M-1] stratified_sample_by_violation_type → test_samples.csv (300)
[M-1] create_calibration_set → calibration.csv (50)
    ↓
[M-2] TrainingProtocol.present_training_materials()
    ↓
For each annotator (n=3):
    [M-2] run_calibration_phase → calibration_results.csv
    [M-2] Gate check: κ ≥ 0.60? → Pass/Fail
        ↓ (if pass)
    [M-3] randomize_presentation_order()
    [M-3] collect_annotations_with_training → annotations.csv (900 rows)
    ↓
[M-4] compute_pairwise_kappa → (avg_kappa, kappa_list, matrix)
[M-5] compute_agreement_with_original → (mean_agreement, [a1, a2, a3])
    ↓
[M-6] one_sample_ttest_kappa → {t, p, mean, ci}
[M-6] gate_decision → "PASS" | "PARTIAL" | "FAIL"
    ↓
[M-7] plot_gate_metrics_comparison → gate_metrics.png
[M-7] plot_inter_annotator_matrix → inter_annotator_matrix.png
[M-7] plot_agreement_distribution → agreement_distribution.png
[M-7] plot_confusion_matrices → confusion_matrices.png
    ↓
[M-8] write_report → report.md
```

---

## Configuration Schema

```yaml
experiment:
  name: "h-m1-annotation-consistency"
  seed: 42
  test_sample_size: 300
  calibration_sample_size: 50
  n_annotators: 3

stratification:
  method: "violation_type"
  types: ["harmful_content", "misinformation", "instruction_violation"]
  samples_per_type: 100

training:
  guidelines_path: "src/training/guidelines.yaml"
  presentation_duration_min: 30
  calibration_threshold_kappa: 0.60

gates:
  primary_kappa_threshold: 0.70
  secondary_agreement_threshold: 0.75
  alpha: 0.05

baseline_comparison:
  h_e1_kappa: 0.498
  expected_improvement_min: 0.15

outputs:
  data_dir: "data/"
  figures_dir: "outputs/figures/"
  results_file: "outputs/results.json"
  report_file: "outputs/report.md"
```

---

## Error Handling & Edge Cases

### Calibration Failure
```python
class CalibrationFailureError(Exception):
    """Raised when annotator fails calibration gate."""
    pass

# In run_calibration_phase():
if kappa < self.calibration_threshold:
    raise CalibrationFailureError(
        f"Annotator {annotator_id} κ={kappa:.3f} < {self.calibration_threshold}"
    )
```

### Missing Annotations
```python
# In compute_pairwise_kappa():
assert len(annotations) == n_annotators * n_samples, \
    f"Expected {n_annotators * n_samples} annotations, got {len(annotations)}"
```

### Tie in Majority Vote (Not Needed for h-m1)
h-m1 does NOT use majority vote - each annotator's judgment is independent for inter-annotator agreement calculation.

---

## Testing Guidance

### Unit Tests

**test_training_protocol.py:**
```python
def test_calibration_gate_pass():
    # Perfect agreement → κ=1.0 → pass
    protocol = TrainingProtocol("guidelines.yaml")
    kappa, passed = protocol.run_calibration_phase(1, calibration, gold_labels)
    assert passed == True

def test_calibration_gate_fail():
    # Random annotations → κ≈0 → fail
    protocol = TrainingProtocol("guidelines.yaml")
    with pytest.raises(CalibrationFailureError):
        protocol.run_calibration_phase(1, calibration, random_labels)
```

**test_metrics.py:**
```python
def test_agreement_with_original():
    # 100% agreement case
    annotations = create_perfect_alignment_data()
    mean_agreement, per_annotator = compute_agreement_with_original(annotations, original)
    assert mean_agreement == 1.0
```

**test_hypothesis_test.py:**
```python
def test_one_sample_ttest():
    kappa_values = [0.72, 0.75, 0.73]  # All > 0.70
    result = one_sample_ttest_kappa(kappa_values)
    assert result['p_value'] < 0.05  # Significant

def test_gate_decision_pass():
    decision = gate_decision(avg_kappa=0.75, avg_agreement=0.80, p_value=0.01)
    assert decision == "PASS"

def test_gate_decision_partial():
    decision = gate_decision(avg_kappa=0.75, avg_agreement=0.65, p_value=0.01)
    assert decision == "PARTIAL"
```

---

## Subtask Budget Summary

| Epic | Complexity | Subtasks Used | Subtasks IDs |
|------|------------|---------------|--------------|
| M-1  | 8          | 1             | L-M1-1 |
| M-2  | 10         | 2             | L-M2-1, L-M2-2 |
| M-3  | 9          | 1             | L-M3-1 |
| M-4  | 7          | 1             | L-M4-1 |
| M-5  | 6          | 0             | - |
| M-6  | 8          | 1             | L-M6-1 |
| M-7  | 9          | 0             | - |
| M-8  | 11         | 1             | L-M8-1 |
| **Total** | **68** | **7** | **7/7 budget used** |

---

**Document Status:** COMPLETE  
**Next Phase:** Configuration Design (03_config.md)  
**Applied Patterns:** KB-Pattern-AnnotationStudy, KB-Pattern-InterRaterReliability  
**Base Hypothesis:** h-e1 (API signatures verified from actual code)
