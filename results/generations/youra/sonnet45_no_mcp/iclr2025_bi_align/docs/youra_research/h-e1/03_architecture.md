# System Architecture: h-e1
# Base-Rate Validation Study

**Date:** 2026-04-19  
**Hypothesis:** h-e1 (EXISTENCE - PoC)  
**Budget Tier:** LIGHT (≤15 tasks)  
**Author:** Architecture Agent  

---

## Applied Patterns

Applied: Standard annotation study architecture (no KB search - no-MCP mode)

---

## Codebase Analysis (Serena)

**Project Type**: Green-field  
**Status**: No existing code to analyze (no-MCP mode)  
**Analyzed Path**: N/A  
**Findings**: New implementation from scratch - human annotation study for dataset validation

---

## System Overview

Human annotation study validating base-rate of genuine safety violations in HH-RLHF rejected responses. Core workflow: Data sampling → Annotation collection → Statistical analysis → Gate decision.

**Key Constraint:** This is NOT an ML training pipeline - humans replace models as evaluators.

---

## Module Structure

### DataSampler (`src/data_sampler.py`)

**Dependencies:** None

```python
class DataSampler:
    def __init__(self, dataset_name: str, subset: str, seed: int): ...
    def load_hhrlhf_dataset(self) -> Dataset: ...
    def stratified_sample(self, n: int, strata_col: str) -> pd.DataFrame: ...
    def save_samples(self, samples: pd.DataFrame, output_path: str): ...
```

---

### AnnotationInterface (`src/annotation_interface.py`)

**Dependencies:** DataSampler

```python
class AnnotationInterface:
    def __init__(self, samples_path: str, violation_criteria: List[str]): ...
    def generate_annotation_sheet(self, output_path: str): ...
    def load_annotations(self, annotation_files: List[str]) -> pd.DataFrame: ...
    def validate_annotations(self, annotations: pd.DataFrame) -> bool: ...
```

---

### StatisticalAnalyzer (`src/statistical_analyzer.py`)

**Dependencies:** AnnotationInterface

```python
class StatisticalAnalyzer:
    def __init__(self, annotations: pd.DataFrame, n_annotators: int): ...
    def compute_cohens_kappa(self) -> Tuple[float, float]: ...
    def majority_vote(self) -> pd.Series: ...
    def compute_base_rate(self, labels: pd.Series) -> float: ...
    def binomial_test(self, n_violations: int, n_total: int, p_null: float) -> dict: ...
    def length_bias_test(self, samples: pd.DataFrame, labels: pd.Series) -> dict: ...
```

---

### Visualizer (`src/visualizer.py`)

**Dependencies:** StatisticalAnalyzer

```python
class Visualizer:
    def __init__(self, results: dict, output_dir: str): ...
    def plot_gate_metrics(self, base_rate: float, threshold: float, p_value: float): ...
    def plot_agreement_matrix(self, annotations: pd.DataFrame): ...
    def plot_violation_types(self, violation_counts: pd.Series): ...
    def plot_length_bias(self, quartiles: List[str], rates: List[float]): ...
```

---

### Main Pipeline (`main.py`)

**Dependencies:** DataSampler, AnnotationInterface, StatisticalAnalyzer, Visualizer

```python
def main(args: argparse.Namespace):
    # Step 1: Sample data
    sampler = DataSampler(...)
    samples = sampler.stratified_sample(n=500, strata_col='length_quartile')
    
    # Step 2: Generate annotation interface
    interface = AnnotationInterface(...)
    interface.generate_annotation_sheet(...)
    
    # Step 3: Load annotations (after human annotation complete)
    annotations = interface.load_annotations(...)
    
    # Step 4: Statistical analysis
    analyzer = StatisticalAnalyzer(annotations, n_annotators=3)
    kappa, kappa_ci = analyzer.compute_cohens_kappa()
    labels = analyzer.majority_vote()
    base_rate = analyzer.compute_base_rate(labels)
    test_result = analyzer.binomial_test(...)
    
    # Step 5: Visualization
    viz = Visualizer(results, output_dir='figures/')
    viz.plot_gate_metrics(base_rate, threshold=0.40, p_value=test_result['p_value'])
    
    # Step 6: Gate decision
    gate_pass = (base_rate >= 0.40) and (test_result['p_value'] < 0.05)
    print(f"GATE: {'PASS' if gate_pass else 'FAIL'}")
```

---

## File Organization

```
h-e1/
├── code/
│   ├── src/
│   │   ├── data_sampler.py          # Dataset loading + stratified sampling
│   │   ├── annotation_interface.py  # Annotation sheet generation + loading
│   │   ├── statistical_analyzer.py  # Cohen's κ, binomial test, base-rate
│   │   └── visualizer.py            # All figure generation
│   ├── main.py                      # End-to-end pipeline orchestration
│   ├── config.py                    # Hardcoded parameters (no YAML)
│   ├── requirements.txt             # Dependencies
│   └── README.md                    # Annotation protocol instructions
├── data/
│   ├── sampled_responses.csv        # 500 stratified samples
│   └── annotations/                 # Raw annotation files
│       ├── annotator_1.csv
│       ├── annotator_2.csv
│       └── annotator_3.csv
├── figures/                         # All generated plots
│   ├── gate_metrics.png
│   ├── agreement_matrix.png
│   ├── violation_types.png
│   └── length_bias.png
└── results/
    └── results.json                 # Final metrics + gate status
```

---

## Configuration

**Infrastructure Level:** LIGHT (minimal)

```python
# config.py (hardcoded parameters)

# Dataset parameters
DATASET_NAME = "Anthropic/hh-rlhf"
SUBSET = "harmless-base"
SAMPLE_SIZE = 500
RANDOM_SEED = 42

# Annotation parameters
N_ANNOTATORS = 3
VIOLATION_CRITERIA = [
    "Direct harm/violence encouragement",
    "Toxic/offensive language",
    "Privacy violations or personal information disclosure",
    "Dangerous/illegal advice",
    "Deception or misinformation",
    "Other safety policy violations"
]

# Statistical test parameters
BASE_RATE_THRESHOLD = 0.40
ALPHA = 0.05
KAPPA_TARGET = 0.75

# Output paths
DATA_DIR = "data/"
FIGURES_DIR = "figures/"
RESULTS_DIR = "results/"
```

---

## Dependencies

```
# requirements.txt
datasets>=2.0.0
pandas>=1.3.0
numpy>=1.21.0
scipy>=1.7.0
statsmodels>=0.13.0
matplotlib>=3.4.0
seaborn>=0.11.0
scikit-learn>=1.0.0
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Sampling | Load HH-RLHF + stratified sampling by length quartiles | 8 | Module(2) + Deps(1) + Algo(3) + Integ(2) |
| A-2 | Annotation Interface | Generate annotation sheet + load/validate annotations | 7 | Module(2) + Deps(1) + Algo(2) + Integ(2) |
| A-3 | Statistical Analysis | Cohen's κ, majority vote, base-rate, binomial test | 11 | Module(3) + Deps(2) + Algo(4) + Integ(2) |
| A-4 | Visualization | Gate metrics, agreement matrix, violation types, length bias | 9 | Module(2) + Deps(2) + Algo(3) + Integ(2) |
| A-5 | Pipeline Integration | Main script orchestration + config + logging | 6 | Module(1) + Deps(2) + Algo(1) + Integ(2) |

**Total Complexity:** 41  
**Task Count:** 5 (within 4-8 epic range for EXISTENCE)  
**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3], Low(4-8): [A-1, A-2, A-5], VeryLow(1-3): []

---

## Complexity Scoring Details

**A-1 (Data Sampling) = 8**
- Module Size: 2 (single class, 4 methods)
- Dependencies: 1 (HuggingFace datasets only)
- Algorithm: 3 (stratified sampling logic, length quartile computation)
- Integration: 2 (save to CSV for downstream)

**A-2 (Annotation Interface) = 7**
- Module Size: 2 (single class, 3 methods)
- Dependencies: 1 (pandas only)
- Algorithm: 2 (CSV template generation, validation logic)
- Integration: 2 (load multiple annotator files)

**A-3 (Statistical Analysis) = 11**
- Module Size: 3 (single class, 5 methods)
- Dependencies: 2 (scipy, statsmodels)
- Algorithm: 4 (Cohen's κ, majority vote, binomial test, chi-square)
- Integration: 2 (combine annotations across annotators)

**A-4 (Visualization) = 9**
- Module Size: 2 (single class, 4 plot methods)
- Dependencies: 2 (matplotlib, seaborn)
- Algorithm: 3 (4 different plot types with annotations)
- Integration: 2 (read results from analyzer)

**A-5 (Pipeline Integration) = 6**
- Module Size: 1 (main script only)
- Dependencies: 2 (all internal modules)
- Algorithm: 1 (sequential orchestration)
- Integration: 2 (config + logging + result export)

---

## Data Flow

```
HH-RLHF Dataset
    ↓
DataSampler (stratified sampling)
    ↓
sampled_responses.csv (500 samples)
    ↓
AnnotationInterface (generate sheets)
    ↓
[HUMAN ANNOTATION] (3 annotators)
    ↓
annotations/*.csv (raw annotations)
    ↓
StatisticalAnalyzer (Cohen's κ, majority vote, base-rate)
    ↓
results.json (base_rate, kappa, p_value, gate_status)
    ↓
Visualizer (4 figures)
    ↓
figures/*.png (gate metrics, agreement, violations, length bias)
```

---

## Validation Strategy (LIGHT Tier)

**Smoke Tests Only** (no comprehensive test suite):

1. **Data Sampling Smoke Test:**
   - Load 10 samples from HH-RLHF
   - Verify stratification produces 4 quartiles
   - Check CSV export has required columns

2. **Statistical Analysis Smoke Test:**
   - Mock 3-annotator data (50 samples)
   - Verify Cohen's κ computes without error
   - Check binomial test returns p-value

3. **Visualization Smoke Test:**
   - Generate all 4 plots with mock data
   - Verify PNG files saved to figures/

**No unit tests, no integration tests** (LIGHT tier constraint).

---

## Gate Execution Flow

```
1. Run main.py --mode sample
   → Generates sampled_responses.csv

2. Run main.py --mode generate_sheets
   → Generates annotation templates

3. [MANUAL] Human annotators fill sheets (2-3 hours each)

4. Run main.py --mode analyze
   → Computes κ, base-rate, binomial test
   → Generates figures
   → Writes results.json

5. Check gate status:
   IF base_rate >= 0.40 AND p_value < 0.05:
       GATE = PASS → Proceed to h-m1
   ELSE:
       GATE = FAIL → STOP WORKFLOW
```

---

## Logging Strategy (LIGHT Tier)

**Print statements only** (no structured logging):

```python
print(f"[DataSampler] Loaded {len(dataset)} samples from HH-RLHF")
print(f"[DataSampler] Stratified sampling: {n_per_quartile} per quartile")
print(f"[StatisticalAnalyzer] Cohen's κ: {kappa:.3f} (CI: {ci_lower:.3f}-{ci_upper:.3f})")
print(f"[StatisticalAnalyzer] Base-rate: {base_rate:.3f}")
print(f"[StatisticalAnalyzer] Binomial test p-value: {p_value:.4f}")
print(f"[GATE] Status: {'PASS' if gate_pass else 'FAIL'}")
```

**CSV export for reproducibility:**
- `data/sampled_responses.csv` (sample IDs + metadata)
- `results/results.json` (all metrics)

---

## Error Handling

**Minimal error handling** (LIGHT tier):

1. **Dataset loading failure:** Print error + exit
2. **Missing annotation files:** Print warning + skip annotator
3. **Statistical test failure:** Print error + debug info
4. **Figure generation failure:** Print warning + continue

**No retries, no graceful degradation** (PoC simplicity).

---

## Self-Validation Checklist

- [x] No ASCII diagrams (used bullet lists)
- [x] No KB search logs (noted "no-MCP mode")
- [x] Module sections = interface code only
- [x] 5 Epic tasks (within 4-8 range for EXISTENCE)
- [x] Total length < 500 lines
- [x] "Codebase Analysis (Serena)" section included
- [x] Green-field project → Serena skip acceptable
- [x] LIGHT tier infrastructure (hardcoded config, print logging, smoke tests)
- [x] Human annotation study architecture (no ML training)

---

## Implementation Notes

### Critical Decisions

1. **Annotation Interface:** CSV-based (Google Sheets compatible) instead of web UI
   - Rationale: Faster to implement, lower infrastructure overhead for PoC
   - Trade-off: Manual file distribution vs automated web interface

2. **Statistical Libraries:** scipy + statsmodels (not custom implementations)
   - Rationale: Standard, well-tested, matches PRD requirement
   - Trade-off: External dependencies vs custom code control

3. **Configuration:** Hardcoded in config.py (no YAML)
   - Rationale: LIGHT tier constraint, no parameter tuning needed
   - Trade-off: Code changes for parameter updates vs file-based config

### EXISTENCE Constraints Applied

- **Task Count:** 5 tasks (not 6-12) for PoC simplicity
- **File Structure:** Minimal (4 modules + main + config)
- **No Ablation:** Only proposed method (human annotation)
- **Baseline:** Original HH-RLHF labels serve as comparison reference

---

*Generated by Architecture Agent (Phase 3 Step 3)*  
*Next: Logic Design (Step 4)*
