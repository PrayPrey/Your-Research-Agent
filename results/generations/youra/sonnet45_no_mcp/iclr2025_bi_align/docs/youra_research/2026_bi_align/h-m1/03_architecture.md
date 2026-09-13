# System Architecture
# Hypothesis: h-m1 - Annotation Consistency Study

**Version:** 1.0  
**Date:** 2026-04-19  
**Hypothesis ID:** h-m1  
**Hypothesis Type:** MECHANISM (Step 1)  
**Architecture Type:** Human Annotation Study with Explicit Training Protocol

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Patterns found from h-e1 base code  
**Analyzed Path:** `/home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_bi_align_3/docs/youra_research/20260419_bi_align/h-e1/code/`

**Findings:** h-e1 implements annotation study infrastructure with modules for data sampling, annotation interface, agreement calculation, and statistical testing. h-m1 extends this with annotator training protocol and calibration validation.

**Applied:** KB-Pattern-AnnotationStudy, KB-Pattern-InterRaterReliability

---

## 1. System Overview

### 1.1 Architecture Pattern
**Pattern:** Annotation Study with Training Pipeline  
**Components:** Data Sampling → Training Protocol → Calibration → Annotation Collection → Statistical Analysis → Visualization

### 1.2 Design Principles
- **Reuse:** Extend h-e1 infrastructure (sampling, agreement, metrics)
- **Mechanism Focus:** Explicit criteria training with calibration gate
- **Reproducibility:** Fixed seeds, documented training protocol

---

## 2. Module Structure

### Module 1: Data Sampling (`src/data/`)

**Dependencies:** HuggingFace datasets

```python
def stratified_sample_by_violation_type(
    dataset: Dataset,
    sample_size: int = 300,
    violation_taxonomy: Dict[str, List[int]],
    seed: int = 42
) -> pd.DataFrame:
    """
    Stratified sampling by violation type (from h-e1 taxonomy).
    
    Returns:
        DataFrame with 100 samples per violation type (3 types × 100 = 300)
    """
    ...

def create_calibration_set(
    dataset: Dataset,
    calibration_size: int = 50,
    seed: int = 42
) -> pd.DataFrame:
    """
    Separate calibration samples for training phase.
    
    Returns:
        DataFrame with 50 samples (disjoint from test set)
    """
    ...
```

### Module 2: Training Protocol (`src/training/`)

**Dependencies:** None (document-based)

```python
class TrainingProtocol:
    def __init__(self, guidelines_path: str):
        self.guidelines = self.load_hhrlhf_guidelines(guidelines_path)
        self.calibration_threshold = 0.60
    
    def load_hhrlhf_guidelines(self, path: str) -> Dict[str, str]:
        """Load HH-RLHF annotation criteria from YAML."""
        ...
    
    def present_training_materials(self, annotator_id: int) -> None:
        """Display annotation guidelines (30 min presentation)."""
        ...
    
    def run_calibration_phase(
        self,
        annotator_id: int,
        calibration_samples: pd.DataFrame,
        gold_labels: pd.Series
    ) -> Tuple[float, bool]:
        """
        Collect calibration annotations and check κ ≥ 0.60.
        
        Returns:
            (calibration_kappa, passed_gate)
        """
        ...
```

### Module 3: Annotation Interface (`src/annotation/`)

**Dependencies:** storage (from h-e1)

```python
def collect_annotations_with_training(
    samples: pd.DataFrame,
    annotator_id: int,
    training_protocol: TrainingProtocol,
    output_file: str
) -> pd.DataFrame:
    """
    Full annotation workflow: training → calibration → main annotation.
    
    Returns:
        DataFrame with columns [sample_id, annotator_id, judgment]
    """
    ...

def randomize_presentation_order(
    samples: pd.DataFrame,
    annotator_id: int,
    seed: int = 42
) -> pd.DataFrame:
    """Randomize sample order per annotator (seed + annotator_id)."""
    ...
```

### Module 4: Agreement Calculation (`src/analysis/`)

**Dependencies:** numpy, pandas

```python
def compute_pairwise_kappa(
    annotations: pd.DataFrame,
    n_annotators: int = 3
) -> Tuple[float, List[float], pd.DataFrame]:
    """
    Calculate average pairwise Cohen's κ.
    
    Returns:
        (avg_kappa, kappa_list, pairwise_matrix)
    """
    ...

def compute_agreement_with_original(
    annotations: pd.DataFrame,
    original_labels: pd.Series
) -> Tuple[float, List[float]]:
    """
    Calculate agreement rate with HH-RLHF labels.
    
    Returns:
        (mean_agreement, per_annotator_agreement)
    """
    ...
```

### Module 5: Statistical Testing (`src/analysis/`)

**Dependencies:** scipy.stats

```python
def one_sample_ttest_kappa(
    kappa_values: List[float],
    null_threshold: float = 0.60,
    alternative_threshold: float = 0.70,
    alpha: float = 0.05
) -> Dict[str, float]:
    """
    Test H0: κ < 0.60 vs H1: κ ≥ 0.70.
    
    Returns:
        {t_statistic, p_value, mean_kappa, ci_lower, ci_upper}
    """
    ...

def gate_decision(
    avg_kappa: float,
    avg_agreement: float,
    p_value: float,
    kappa_threshold: float = 0.70,
    agreement_threshold: float = 0.75,
    alpha: float = 0.05
) -> str:
    """
    Determine PASS/FAIL based on both gate conditions.
    
    Returns:
        "PASS" | "PARTIAL" | "FAIL"
    """
    ...
```

### Module 6: Visualization (`src/visualization/`)

**Dependencies:** matplotlib, seaborn

```python
def plot_gate_metrics_comparison(
    results: Dict[str, float],
    thresholds: Dict[str, float],
    output_path: str
) -> None:
    """
    Bar chart: Target vs actual for κ and agreement rate.
    """
    ...

def plot_inter_annotator_matrix(
    pairwise_kappas: pd.DataFrame,
    output_path: str
) -> None:
    """
    3×3 heatmap of pairwise Cohen's κ values.
    """
    ...

def plot_agreement_distribution(
    per_annotator_agreement: List[float],
    threshold: float = 0.75,
    output_path: str
) -> None:
    """
    Bar chart: Each annotator's agreement with original labels.
    """
    ...

def plot_confusion_matrices(
    annotations: pd.DataFrame,
    original_labels: pd.Series,
    output_path: str
) -> None:
    """
    3 confusion matrices (one per annotator) vs original labels.
    """
    ...
```

### Module 7: Experiment Runner (`src/`)

**Dependencies:** All modules

```python
def run_h_m1_experiment(config: Dict) -> Dict:
    """
    Main experiment orchestration:
    1. Load and sample data (300 test + 50 calibration)
    2. For each annotator:
       a. Present training materials
       b. Run calibration (gate: κ ≥ 0.60)
       c. Collect main annotations (300 samples)
    3. Compute inter-annotator agreement
    4. Test statistical hypotheses
    5. Generate visualizations
    6. Return gate decision
    """
    ...
```

---

## 3. External Dependencies (Base Hypothesis)

### Module Paths (From h-e1 Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| cohen_kappa_score | `from src.analysis.agreement import cohen_kappa_score` | `h-e1/code/src/analysis/agreement.py` |
| stratified_sample | `from src.data.sampler import stratified_sample` | `h-e1/code/src/data/sampler.py` |
| load_dataset_hhrlhf | `from src.data.loader import load_dataset` | `h-e1/code/src/data/loader.py` |
| present_sample_for_annotation | `from src.annotation.interface import present_sample_for_annotation` | `h-e1/code/src/annotation/interface.py` |
| save_annotations | `from src.annotation.storage import save_annotations` | `h-e1/code/src/annotation/storage.py` |

**Verified from:** h-e1/code/ (actual implementation)

**Reuse Strategy:** Adapt h-e1 modules for h-m1 requirements (violation-type stratification, training workflow)

---

## 4. File Organization

```
h-m1/
├── code/
│   ├── src/
│   │   ├── data/
│   │   │   ├── __init__.py
│   │   │   ├── sampler.py              # Violation-type stratification (adapted from h-e1)
│   │   │   └── loader.py               # Dataset loading (reused from h-e1)
│   │   ├── training/
│   │   │   ├── __init__.py
│   │   │   ├── protocol.py             # Training workflow NEW
│   │   │   └── guidelines.yaml         # HH-RLHF criteria NEW
│   │   ├── annotation/
│   │   │   ├── __init__.py
│   │   │   ├── interface.py            # Extended with randomization
│   │   │   └── storage.py              # Reused from h-e1
│   │   ├── analysis/
│   │   │   ├── __init__.py
│   │   │   ├── agreement.py            # Reused from h-e1
│   │   │   ├── metrics.py              # Agreement with original NEW
│   │   │   └── hypothesis_test.py      # One-sample t-test NEW
│   │   ├── visualization/
│   │   │   ├── __init__.py
│   │   │   └── plots.py                # 4 required figures NEW
│   │   ├── main.py                     # Experiment runner
│   │   └── config.yaml                 # Configuration
│   ├── data/
│   │   ├── hh_rlhf_test_samples.csv    # 300 test samples
│   │   ├── hh_rlhf_calibration.csv     # 50 calibration samples
│   │   ├── calibration_results.csv     # Calibration annotations
│   │   └── annotations.csv             # Main annotations (3 × 300)
│   ├── outputs/
│   │   ├── figures/
│   │   │   ├── gate_metrics.png
│   │   │   ├── inter_annotator_matrix.png
│   │   │   ├── agreement_distribution.png
│   │   │   └── confusion_matrices.png
│   │   ├── results.json
│   │   └── report.md
│   ├── tests/
│   │   ├── test_training_protocol.py
│   │   ├── test_metrics.py
│   │   └── test_hypothesis_test.py
│   ├── requirements.txt
│   └── README.md
```

---

## 5. Epic Tasks with Complexity Scores

### Epic M-1: Data Preparation with Violation-Type Stratification
**ID:** M-1  
**Module:** data  
**Complexity Score:** 8/20  
**Breakdown:**
- Module Size: 2 files, ~200 LOC → 3/5
- Dependencies: HuggingFace datasets, h-e1 violation taxonomy → 2/5
- Algorithm: Stratified sampling by violation type → 2/5
- Integration: Requires h-e1 taxonomy mapping → 1/5

**Description:** Create 300-sample test set (100 per violation type) and 50-sample calibration set, stratified by h-e1 violation taxonomy.

**Acceptance Criteria:**
- Loads HH-RLHF harmless subset
- Maps samples to h-e1 violation types (harmful_content, misinformation, instruction_violation)
- Stratified sampling: 100 per type
- Separate calibration set (50 samples, disjoint from test)
- Reproducible with seed=42

---

### Epic M-2: Training Protocol Implementation
**ID:** M-2  
**Module:** training  
**Complexity Score:** 10/20  
**Breakdown:**
- Module Size: 2 files + guidelines doc, ~150 LOC → 3/5
- Dependencies: YAML configuration → 1/5
- Algorithm: Sequential training workflow with gate → 3/5
- Integration: Interfaces with annotation module → 3/5

**Description:** Implement annotator training workflow with HH-RLHF guidelines presentation, calibration phase, and κ ≥ 0.60 gate check.

**Acceptance Criteria:**
- HH-RLHF annotation guidelines in YAML format
- Training material presentation function
- Calibration annotation collection (50 samples)
- Calibration κ calculation vs gold labels
- Gate enforcement: κ < 0.60 → training fails

---

### Epic M-3: Annotation Collection with Randomization
**ID:** M-3  
**Module:** annotation  
**Complexity Score:** 9/20  
**Breakdown:**
- Module Size: Extend h-e1 interface, ~100 LOC → 2/5
- Dependencies: h-e1 annotation module, training protocol → 3/5
- Algorithm: Randomized presentation per annotator → 2/5
- Integration: Sequential workflow (training → annotation) → 2/5

**Description:** Extend h-e1 annotation interface to support per-annotator randomization and integration with training protocol.

**Acceptance Criteria:**
- Randomize sample order per annotator (seed + annotator_id)
- Independent annotation sessions (3 annotators)
- Blinded to original labels
- Progress tracking per annotator
- Saves to CSV with annotator_id column

---

### Epic M-4: Inter-Annotator Agreement Analysis
**ID:** M-4  
**Module:** analysis  
**Complexity Score:** 7/20  
**Breakdown:**
- Module Size: Reuse h-e1 agreement.py, ~50 LOC new → 2/5
- Dependencies: h-e1 agreement module → 1/5
- Algorithm: Pairwise κ (already implemented) → 2/5
- Integration: Process 3 × 300 annotation matrix → 2/5

**Description:** Calculate average pairwise Cohen's κ across 3 annotators (reuse h-e1 agreement calculation).

**Acceptance Criteria:**
- Loads annotations.csv (900 rows: 3 annotators × 300 samples)
- Computes 3 pairwise κ values
- Calculates average κ
- Generates 3×3 pairwise matrix
- Reports interpretation (Landis & Koch)

---

### Epic M-5: Agreement with Original Labels
**ID:** M-5  
**Module:** analysis  
**Complexity Score:** 6/20  
**Breakdown:**
- Module Size: 1 file, ~80 LOC → 2/5
- Dependencies: pandas → 1/5
- Algorithm: Simple proportion calculation → 1/5
- Integration: Loads original HH-RLHF labels → 2/5

**Description:** Compute agreement rate between each annotator and original HH-RLHF labels.

**Acceptance Criteria:**
- Loads original labels from dataset
- Calculates per-annotator agreement (matches / 300)
- Computes mean agreement across 3 annotators
- 95% CI for mean agreement
- Target: ≥75% agreement

---

### Epic M-6: Statistical Hypothesis Testing
**ID:** M-6  
**Module:** analysis  
**Complexity Score:** 8/20  
**Breakdown:**
- Module Size: 1 file, ~100 LOC → 2/5
- Dependencies: scipy.stats → 1/5
- Algorithm: One-sample t-test → 3/5
- Integration: Uses results from M-4, M-5 → 2/5

**Description:** Perform one-sample t-test on pairwise κ values to test H0: κ < 0.60 vs H1: κ ≥ 0.70.

**Acceptance Criteria:**
- One-sample t-test on 3 pairwise κ values
- H0: κ < 0.60, H1: κ ≥ 0.70
- α = 0.05 significance level
- Effect size calculation
- Gate decision: PASS (both gates) | PARTIAL (one gate) | FAIL (neither)

---

### Epic M-7: Visualization Generation
**ID:** M-7  
**Module:** visualization  
**Complexity Score:** 9/20  
**Breakdown:**
- Module Size: 1 file, ~200 LOC → 3/5
- Dependencies: matplotlib, seaborn → 1/5
- Algorithm: 4 distinct plot types → 3/5
- Integration: Reads results from M-4, M-5, M-6 → 2/5

**Description:** Generate 4 required figures: gate metrics comparison, inter-annotator matrix, agreement distribution, confusion matrices.

**Acceptance Criteria:**
- Gate metrics bar chart (target vs actual for κ and agreement)
- 3×3 heatmap of pairwise κ values
- Bar chart: per-annotator agreement with 75% threshold line
- 3 confusion matrices (each annotator vs original)
- All figures saved to outputs/figures/

---

### Epic M-8: Experiment Orchestration
**ID:** M-8  
**Module:** main  
**Complexity Score:** 11/20  
**Breakdown:**
- Module Size: 1 file, ~150 LOC → 3/5
- Dependencies: All modules (M-1 through M-7) → 4/5
- Algorithm: Sequential pipeline with error handling → 2/5
- Integration: Coordinates all modules + training workflow → 2/5

**Description:** Main experiment runner orchestrating full pipeline from data loading through final report generation.

**Acceptance Criteria:**
- Sequential execution: sampling → training → calibration → annotation → analysis → visualization
- Config-driven execution (YAML)
- Error handling for calibration gate failures
- Generates final report.md with results
- Returns gate decision (PASS/PARTIAL/FAIL)

---

## 6. Task Budget Summary

**Hypothesis Type:** MECHANISM  
**Total Epic Tasks:** 8  
**Complexity Distribution:**
- High (10-11): 2 tasks [M-2, M-8]
- Medium (7-9): 4 tasks [M-1, M-3, M-4, M-7]
- Low (6): 2 tasks [M-5, M-6]

**Total Complexity:** 68/160 (8 tasks × 20 max)

---

## 7. Data Flow

```
HH-RLHF Dataset
    ↓
Stratified Sampler (M-1) → test_samples.csv (300) + calibration.csv (50)
    ↓
Training Protocol (M-2) → For each annotator:
    ├→ Present guidelines (30 min)
    ├→ Calibration phase (50 samples) → calibration_results.csv
    └→ Gate check: κ ≥ 0.60?
        ↓
Annotation Collection (M-3) → annotations.csv (3 × 300)
    ↓
    ├→ Inter-Annotator Agreement (M-4) → avg_kappa, pairwise_matrix
    ├→ Agreement with Original (M-5) → mean_agreement, per_annotator_rates
    └→ Statistical Testing (M-6) → t-test results, gate decision
    ↓
Visualization (M-7) → figures/
    ↓
Experiment Runner (M-8) → report.md
```

---

## 8. Integration Points

### 8.1 Reused from h-e1
- `src.analysis.agreement.cohen_kappa_score` - Cohen's κ calculation
- `src.data.loader.load_dataset` - HuggingFace dataset loading
- `src.annotation.interface.present_sample_for_annotation` - Sample presentation logic
- `src.annotation.storage.save_annotations` - CSV persistence

### 8.2 New Components
- `src.training.protocol.TrainingProtocol` - Training workflow
- `src.analysis.metrics.compute_agreement_with_original` - Original label comparison
- `src.analysis.hypothesis_test.one_sample_ttest_kappa` - Statistical test
- `src.visualization.plots.*` - All visualization functions

### 8.3 External Dependencies
- HuggingFace `datasets` library
- h-e1 violation taxonomy (from h-e1 results)
- HH-RLHF annotation guidelines (Bai et al. 2022)

---

## 9. Mechanism Validation

### Pre-conditions
1. **Mechanism Exists:** Training with explicit criteria (established HCI/NLP practice)
2. **Baseline Measurable:** h-e1 result κ=0.498 (fair agreement without training)
3. **Improvement Target:** κ ≥ 0.70 (substantial agreement with training)

### Activation Indicators
- **Calibration Gate:** All annotators achieve κ ≥ 0.60 on 50 practice samples
- **Main Phase:** Average pairwise κ across 3 annotators
- **Expected Delta:** +0.15 to +0.25 improvement over h-e1 baseline

### Success Criteria
- **Primary Gate:** Average pairwise κ ≥ 0.70
- **Secondary Gate:** Mean agreement with original ≥ 75%
- **Statistical Significance:** One-sample t-test p < 0.05

### Failure Detection
- **Calibration Failure:** Any annotator κ < 0.60 → additional training required
- **No Improvement:** h-m1 κ ≤ 0.50 → training mechanism ineffective
- **Low Original Agreement:** <60% → guidelines misaligned with original criteria

---

## 10. Configuration Management

```yaml
experiment:
  name: "h-m1-annotation-consistency"
  seed: 42
  test_sample_size: 300
  calibration_sample_size: 50
  n_annotators: 3

stratification:
  method: "violation_type"  # from h-e1 taxonomy
  types: ["harmful_content", "misinformation", "instruction_violation"]
  samples_per_type: 100

training:
  guidelines_source: "Bai et al. 2022 (HH-RLHF paper)"
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

## 11. Testing Strategy

### 11.1 Unit Tests
- `test_training_protocol.py` - Training workflow logic
- `test_metrics.py` - Agreement with original calculation
- `test_hypothesis_test.py` - Statistical test correctness

### 11.2 Integration Tests
- Training → Calibration → Annotation pipeline
- End-to-end gate decision logic

### 11.3 Validation Tests
- Calibration gate enforcement (κ < 0.60 → fail)
- Gate decision logic (both conditions required for PASS)

---

## 12. Architecture Validation

### 12.1 Complexity Check
✓ Total Epic tasks: 8 (within 6-12 range for MECHANISM)  
✓ All tasks have complexity scores  
✓ Complexity range: 6-11/20 (appropriate for MECHANISM)

### 12.2 Dependency Check
✓ No circular dependencies  
✓ Clear sequential execution path with training gate  
✓ All h-e1 dependencies verified from actual code

### 12.3 Mechanism Check
✓ Training protocol with explicit criteria  
✓ Calibration gate (κ ≥ 0.60) enforced  
✓ Baseline comparison (h-e1 κ=0.498)  
✓ Expected improvement documented (+0.15 to +0.25)

---

**Document Status:** COMPLETE  
**Next Phase:** Logic Design (03_logic.md)  
**Applied Patterns:** KB-Pattern-AnnotationStudy, KB-Pattern-InterRaterReliability  
**Base Hypothesis:** h-e1 (code structure verified and reused)
