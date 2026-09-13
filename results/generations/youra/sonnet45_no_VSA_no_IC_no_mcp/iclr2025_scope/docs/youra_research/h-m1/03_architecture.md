# Architecture Specification: H-M1

**Date:** 2026-08-25  
**Hypothesis:** Feature Extraction Protocol Inter-Rater Agreement  
**Type:** MECHANISM (Annotation Study)  
**Archon KB Pattern Applied:** DL evaluation module pattern (sklearn metrics integration)

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase  
**Status:** Patterns found - bcvf evaluation modules provide template for metric calculation and validation  
**Analyzed Path:** `src/bcvf/`  
**Findings:** Existing sklearn metrics integration (precision/recall/f1), validation module pattern, extractor pattern for text processing

---

## System Overview

Inter-rater reliability study (not ML training). Two annotators extract features from 20 benchmarks, compute Cohen's kappa.

**Core Flow:**
1. Sample benchmarks from Papers with Code API
2. Annotators extract features (task type, modality, metrics, dataset size)
3. Calculate Cohen's kappa (categorical) and ICC (continuous)
4. Generate gate metrics chart (kappa vs 0.80 threshold)

---

## Module Structure

### BenchmarkSampler (`src/h-m1/sampler.py`)

**Dependencies:** requests, pandas

```python
class BenchmarkSampler:
    def __init__(self, api_url: str): ...
    def sample_stratified(self, n_samples: int, seed: int) -> pd.DataFrame: ...
    def verify_accessibility(self, benchmarks: pd.DataFrame) -> pd.DataFrame: ...
```

### FeatureExtractor (`src/h-m1/extractor.py`)

**Dependencies:** re, json

```python
class FeatureExtractor:
    def __init__(self, taxonomy_path: str, metrics_config: str): ...
    def extract_task_type(self, abstract: str, title: str) -> str: ...
    def extract_metrics(self, full_text: str) -> List[str]: ...
    def extract_modality(self, description: str) -> str: ...
    def extract_dataset_size(self, tables: List[str]) -> int: ...
    def extract_all(self, paper: dict) -> dict: ...
```

### AgreementCalculator (`src/h-m1/agreement.py`)

**Dependencies:** sklearn.metrics, scipy.stats, numpy

```python
from sklearn.metrics import cohen_kappa_score

class AgreementCalculator:
    def calculate_kappa(self, labels1: List[str], labels2: List[str]) -> float: ...
    def calculate_icc(self, ratings: np.ndarray) -> float: ...
    def compute_confidence_interval(self, kappa: float, n: int) -> Tuple[float, float]: ...
    def analyze_disagreements(self, labels1, labels2) -> pd.DataFrame: ...
```

### AnnotationWorkflow (`src/h-m1/annotate.py`)

**Dependencies:** FeatureExtractor, pandas

```python
class AnnotationWorkflow:
    def __init__(self, protocol_version: str): ...
    def calibrate(self, practice_benchmarks: List[dict]) -> None: ...
    def annotate(self, benchmarks: List[dict], annotator_id: str) -> pd.DataFrame: ...
    def save_annotations(self, annotations: pd.DataFrame, output_path: str): ...
```

### Evaluator (`src/h-m1/evaluate.py`)

**Dependencies:** AgreementCalculator, pandas

```python
class Evaluator:
    def __init__(self, threshold: float = 0.80): ...
    def evaluate_agreement(self, annotations_a1: pd.DataFrame, annotations_a2: pd.DataFrame) -> dict: ...
    def check_gate(self, kappa_scores: dict) -> str: ...  # "PASS" | "PARTIAL" | "FAIL"
```

### Visualizer (`src/h-m1/visualize.py`)

**Dependencies:** matplotlib, seaborn, pandas

```python
class Visualizer:
    def __init__(self, output_dir: str): ...
    def plot_gate_metrics(self, kappa_scores: dict, threshold: float): ...
    def plot_confusion_matrix(self, labels1, labels2, feature_name: str): ...
    def plot_feature_distribution(self, annotations: pd.DataFrame): ...
```

### Config (`src/h-m1/config.py`)

```python
@dataclass
class Config:
    pwc_api_url: str
    n_benchmarks: int
    random_seed: int
    kappa_threshold: float
    protocol_version: str
    taxonomy_path: str
    metrics_patterns_path: str
    output_dir: str
```

---

## File Organization

```
src/h-m1/
├── sampler.py           # Papers with Code API sampling
├── extractor.py         # Feature extraction protocol
├── agreement.py         # Cohen's kappa, ICC calculation
├── annotate.py          # Annotation workflow orchestration
├── evaluate.py          # Gate logic
├── visualize.py         # Required + optional figures
├── config.py            # Study parameters
└── main.py              # Orchestration script

data/h-m1/
├── taxonomy.json        # PWC task taxonomy mapping
├── metrics_patterns.json # Regex patterns for metrics
├── sampled_benchmarks.csv
├── annotations_a1.csv
└── annotations_a2.csv

docs/youra_research/h-m1/
└── figures/
    ├── gate_metrics.png       # REQUIRED
    ├── confusion_matrix.png
    └── feature_distribution.png
```

---

## Data Flow

```
PWC API → BenchmarkSampler → sampled_benchmarks.csv
sampled_benchmarks.csv → FeatureExtractor → annotations_a{1,2}.csv
annotations_a{1,2}.csv → AgreementCalculator → kappa_scores.json
kappa_scores.json → Evaluator → gate_decision.txt
kappa_scores.json → Visualizer → figures/gate_metrics.png
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M1-1 | Benchmark Sampling | PWC API integration, stratified sampling (20 benchmarks), accessibility verification | 8 | Module:2 + Deps:2 + Algo:2 + Integ:2 |
| M1-2 | Feature Extraction Protocol | Implement taxonomy mapper, regex patterns, modality decision tree, table parser | 12 | Module:3 + Deps:2 + Algo:4 + Integ:3 |
| M1-3 | Agreement Calculation | Cohen's kappa (sklearn), ICC (scipy), confidence intervals, disagreement analysis | 10 | Module:3 + Deps:2 + Algo:3 + Integ:2 |
| M1-4 | Annotation Workflow | Calibration procedure, independent annotation tracking, uncertainty flags, protocol versioning | 9 | Module:3 + Deps:1 + Algo:2 + Integ:3 |
| M1-5 | Evaluation & Gate Logic | Compute all kappa scores, check 0.80 threshold, gate decision (PASS/PARTIAL/FAIL) | 7 | Module:2 + Deps:1 + Algo:2 + Integ:2 |
| M1-6 | Visualization | Gate metrics chart (REQUIRED), confusion matrix, feature distribution histogram | 8 | Module:2 + Deps:2 + Algo:2 + Integ:2 |
| M1-7 | Configuration & Data | Taxonomy JSON, metrics patterns JSON, config dataclass, output directory setup | 6 | Module:2 + Deps:1 + Algo:1 + Integ:2 |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M1-2, M1-3, M1-4], Low(4-8): [M1-1, M1-5, M1-6, M1-7]

---

## External Dependencies

**Python Libraries:**
- `requests` - Papers with Code API
- `pandas` - Annotation data handling
- `scikit-learn` - Cohen's kappa (sklearn.metrics.cohen_kappa_score)
- `scipy` - ICC calculation (scipy.stats)
- `numpy` - Numerical computation
- `matplotlib` / `seaborn` - Visualization

**Data Sources:**
- Papers with Code API (https://paperswithcode.com/api/v1/datasets/)
- arXiv papers (manual download)

---

## Gate Validation Logic

```python
def check_gate(kappa_scores: dict) -> str:
    task_type_kappa = kappa_scores['task_type']
    modality_kappa = kappa_scores['modality']
    metrics_kappa = kappa_scores['metrics']
    dataset_size_icc = kappa_scores['dataset_size_icc']
    
    if all(k >= 0.80 for k in [task_type_kappa, modality_kappa, metrics_kappa, dataset_size_icc]):
        return "PASS"
    elif any(k < 0.70 for k in [task_type_kappa, modality_kappa, metrics_kappa, dataset_size_icc]):
        return "FAIL"  # MUST_WORK gate failed
    else:
        return "PARTIAL"  # Protocol refinement needed
```

---

## Success Criteria

**PoC Pass Conditions:**
1. All kappa scores > 0.80 (task_type, modality, metrics)
2. ICC > 0.80 (dataset_size)
3. Gate metrics chart generated
4. Disagreement patterns documented

**Gate Outcome:**
- PASS → H-M1 validated, proceed to H-M2
- PARTIAL → Protocol refinement, re-test on 10 new benchmarks
- FAIL → Workflow STOPS for protocol redesign

---

## Implementation Notes

- No model training (annotation study, not ML)
- Extractor patterns follow `src/bcvf/extractors/` structure
- Validation metrics follow `src/bcvf/evaluation/validator.py` pattern
- Use stdlib re for regex (no external NLP libraries)
- ICC implementation from scipy.stats (standard formula)
- Protocol versioning in config for reproducibility

---

**Validation Checklist:**
- [x] No ASCII diagrams
- [x] Module sections = interface only
- [x] Codebase Analysis (Serena) section included
- [x] 7 Epic tasks with complexity scores
- [x] Total length < 500 lines
- [x] Archon KB pattern applied (1 line)
