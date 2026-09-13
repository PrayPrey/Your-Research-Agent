# Architecture: h-e1 - DTS Inter-Annotator Agreement Study

**Date:** 2026-03-18
**Hypothesis Type:** EXISTENCE (PoC)
**Gate:** MUST_WORK (κ ≥ 0.60 in ≥5/6 DTS sections)
**Architecture Version:** 1.0

---

## Applied Patterns

Applied: Statistical validation study pattern (human annotation protocol with inter-rater reliability)

---

## Codebase Analysis (Serena)

**Project Type:** Green-field implementation
**Status:** New DTS annotation study - no existing code to analyze
**Analyzed Path:** N/A
**Findings:** Previous h-e1 code (MDS-12 psychometric validation) is unrelated. Current hypothesis requires new implementation for Cohen's kappa inter-annotator agreement study.

---

## System Overview

Human inter-annotator agreement study measuring Cohen's κ for DTS framework binary presence judgments across 30 datasets from 3 repositories.

**Architecture Type:** Data collection + statistical analysis pipeline (no ML training)

**Core Components:**
- Dataset collection from HuggingFace, OpenML, UCI (programmatic)
- Annotation protocol implementation (blind coding)
- Cohen's kappa computation with bootstrap CI
- Gate validation logic
- Visualization suite

---

## File Structure

```
h-e1/
├── code/
│   ├── config.py              # Configuration constants
│   ├── data_collector.py      # API collection from 3 repositories
│   ├── annotation_protocol.py # Binary coding logic
│   ├── kappa_calculator.py    # Cohen's kappa + bootstrap CI
│   ├── gate_validator.py      # MUST_WORK gate check
│   ├── visualizer.py          # 4 figures
│   └── run_experiment.py      # Main entry point
├── data/h-e1/
│   ├── datasets_metadata.csv
│   ├── documentation/         # 30 plain text files
│   └── annotations/
│       ├── coder_a_annotations.csv
│       ├── coder_b_annotations.csv
│       └── annotation_protocol.md
└── figures/
    ├── gate_metrics.png
    ├── confusion_matrices.png
    ├── agreement_heatmap.png
    └── baserate_vs_kappa.png
```

---

## Module Specifications

### Configuration (`config.py`)

**Dependencies**: None

```python
# Data collection configuration
REPOSITORIES = ["huggingface", "openml", "uci"]
SAMPLES_PER_REPO = 10

# DTS sections (6 binary presence items)
DTS_SECTIONS = [
    "Motivation",
    "Composition",
    "Collection",
    "Preprocessing",
    "Uses",
    "Maintenance"
]

# Stratification criteria
QUALITY_STRATA = {
    "high": 10,
    "medium": 10,
    "low": 10
}

# Gate thresholds
GATE_THRESHOLDS = {
    "kappa_min": 0.60,
    "sections_min": 5  # ≥5/6 sections
}

# Bootstrap configuration
BOOTSTRAP_CONFIG = {
    "n_resamples": 1000,
    "confidence_level": 0.95,
    "random_state": 42
}

# Output paths
OUTPUT_PATHS = {
    "data_dir": "data/h-e1",
    "doc_dir": "data/h-e1/documentation",
    "annotation_dir": "data/h-e1/annotations",
    "figures_dir": "h-e1/figures",
    "results_file": "h-e1/results/validation_results.json"
}
```

---

### DataCollector (`data_collector.py`)

**Dependencies**: requests, datasets (HF), openml, beautifulsoup4

```python
class DataCollector:
    def __init__(self, n_per_repo: int = 10): ...
    def collect_huggingface_datasets(self) -> List[Dict]: ...
    def collect_openml_datasets(self) -> List[Dict]: ...
    def collect_uci_datasets(self) -> List[Dict]: ...
    def stratify_by_quality(self, datasets: List[Dict]) -> List[Dict]: ...
    def extract_documentation(self, dataset: Dict) -> str: ...
    def save_metadata(self, datasets: List[Dict], path: str): ...
    def save_documentation_files(self, datasets: List[Dict], output_dir: str): ...
```

---

### AnnotationProtocol (`annotation_protocol.py`)

**Dependencies**: pandas

```python
class AnnotationProtocol:
    def __init__(self, dts_sections: List[str]): ...
    def load_documentation(self, dataset_id: str, doc_dir: str) -> str: ...
    def judge_section_presence(self, doc_text: str, section: str) -> int: ...
    def generate_annotation_template(self, datasets: List[str], output_path: str): ...
    def load_annotations(self, coder_a_path: str, coder_b_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]: ...
    def validate_annotations(self, coder_a: pd.DataFrame, coder_b: pd.DataFrame) -> bool: ...
```

---

### KappaCalculator (`kappa_calculator.py`)

**Dependencies**: sklearn.metrics, scipy.stats, numpy

```python
class KappaCalculator:
    def __init__(self, n_bootstrap: int = 1000, random_state: int = 42): ...
    def compute_cohen_kappa(self, coder_a: np.ndarray, coder_b: np.ndarray) -> float: ...
    def bootstrap_confidence_interval(self, coder_a: np.ndarray, coder_b: np.ndarray) -> Tuple[float, float]: ...
    def compute_percent_agreement(self, coder_a: np.ndarray, coder_b: np.ndarray) -> float: ...
    def compute_positive_agreement(self, coder_a: np.ndarray, coder_b: np.ndarray) -> float: ...
    def compute_negative_agreement(self, coder_a: np.ndarray, coder_b: np.ndarray) -> float: ...
    def interpret_kappa(self, kappa: float) -> str: ...
    def analyze_all_sections(self, coder_a: pd.DataFrame, coder_b: pd.DataFrame, sections: List[str]) -> Dict: ...
```

---

### GateValidator (`gate_validator.py`)

**Dependencies**: None

```python
class GateValidator:
    def __init__(self, kappa_threshold: float = 0.60, min_sections: int = 5): ...
    def check_section_pass(self, kappa: float) -> bool: ...
    def evaluate_gate(self, section_results: Dict) -> Dict: ...
    def format_gate_report(self, gate_results: Dict) -> str: ...
```

---

### Visualizer (`visualizer.py`)

**Dependencies**: matplotlib, seaborn, numpy

```python
class Visualizer:
    def __init__(self, output_dir: str): ...
    def plot_gate_metrics(self, section_results: Dict, threshold: float = 0.60): ...
    def plot_confusion_matrices(self, coder_a: pd.DataFrame, coder_b: pd.DataFrame, sections: List[str]): ...
    def plot_agreement_heatmap(self, coder_a: pd.DataFrame, coder_b: pd.DataFrame, sections: List[str]): ...
    def plot_baserate_vs_kappa(self, section_results: Dict): ...
    def save_all_figures(self, coder_a: pd.DataFrame, coder_b: pd.DataFrame, section_results: Dict): ...
```

---

### Main Entry Point (`run_experiment.py`)

**Dependencies**: All modules above, json, pathlib

```python
def load_configuration() -> Dict: ...
def run_data_collection(config: Dict) -> List[Dict]: ...
def prepare_annotation_materials(datasets: List[Dict], config: Dict): ...
def compute_interrater_reliability(coder_a_path: str, coder_b_path: str, config: Dict) -> Dict: ...
def validate_gate(section_results: Dict, config: Dict) -> Dict: ...
def generate_visualizations(coder_a: pd.DataFrame, coder_b: pd.DataFrame, section_results: Dict, config: Dict): ...
def save_results(results: Dict, config: Dict): ...
def main() -> int: ...
```

---

## Data Flow

```
1. DataCollector
   ├─ HF API → 10 datasets
   ├─ OpenML API → 10 datasets
   └─ UCI scraping → 10 datasets

2. Stratification
   ├─ Preliminary DTS scoring
   └─ Quality strata (high/medium/low)

3. Documentation extraction
   └─ 30 plain text files in data/h-e1/documentation/

4. Annotation protocol
   ├─ Coder A: blind annotation
   ├─ Coder B: blind annotation
   └─ Save to CSV (30 rows × 6 DTS sections)

5. KappaCalculator
   ├─ Per-section Cohen's κ
   └─ Bootstrap 95% CI

6. GateValidator
   └─ Check: κ ≥ 0.60 in ≥5/6 sections

7. Visualizer
   └─ 4 figures saved to h-e1/figures/
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1-1 | Dataset Collection Pipeline | Implement multi-repository API collection with stratification | 12 | Module(3) + Deps(3) + API(4) + Integration(2) |
| E1-2 | Documentation Extraction | Extract and format 30 dataset documentation files | 8 | Module(2) + Deps(2) + Parsing(2) + Integration(2) |
| E1-3 | Annotation Protocol Implementation | Binary presence judgment logic and CSV generation | 9 | Module(2) + Deps(2) + DTS(3) + Integration(2) |
| E1-4 | Cohen's Kappa Calculator | κ computation with bootstrap confidence intervals | 11 | Module(3) + Deps(2) + Stats(4) + Integration(2) |
| E1-5 | Gate Validation Logic | MUST_WORK gate check with detailed reporting | 7 | Module(2) + Deps(1) + Logic(2) + Integration(2) |
| E1-6 | Visualization Suite | Generate 4 figures (bar chart, heatmap, confusion matrices, scatter) | 10 | Module(2) + Deps(2) + Plots(4) + Integration(2) |

**Total Complexity:** 57 points

**Distribution:**
- Very High (18-20): []
- High (14-17): []
- Medium (9-13): [E1-1, E1-4, E1-6]
- Low (4-8): [E1-2, E1-3, E1-5]

---

## Technical Constraints

### Human Annotation Requirements

**Coder Training:**
- Study Gebru et al. (2021) DTS framework (1 hour)
- Calibration on 5 datasets from Rondina et al. (2025)
- 100% agreement required on calibration set

**Annotation Protocol:**
- Blind coding (no communication between coders)
- Time limit: 5-10 minutes per dataset
- Break protocol: 10-minute breaks every hour

**Time Budget:**
- Coder A: ~5-6 hours
- Coder B: ~5-6 hours
- Total: 10-12 hours

### Computational Constraints

- CPU-only (no GPU required)
- API rate limits: 1-second delay between requests
- Bootstrap resampling: 1000 iterations (< 1 minute per section)

### Statistical Constraints

- Cohen's κ interpretation: Landis-Koch (1977) scale
- Bootstrap CI method: Percentile (95% confidence)
- Minimum sample size: 30 datasets (sufficient for κ stability)

---

## Success Criteria

### Primary Gate (MUST_WORK)
- Cohen's κ ≥ 0.60 in ≥5/6 DTS sections

### Secondary Performance Expectations
- High-base-rate sections (Uses ≈ 0.95): κ > 0.75
- Sparse sections (Collection ≈ 0.19, Maintenance): κ ≥ 0.55

### Deliverables
1. `datasets_metadata.csv` (30 rows)
2. 30 documentation files
3. 2 annotation CSVs (coder A/B)
4. `validation_results.json` with κ per section + gate result
5. 4 figures in `h-e1/figures/`

---

## Validation Protocol

### Data Quality Checks
- All 30 datasets collected successfully
- All documentation files non-empty
- All annotation CSVs complete (no missing values)
- Both coders annotated same 30 datasets

### Statistical Quality Checks
- Bootstrap CI width < 0.30 (acceptable precision)
- No negative κ values (indicates annotation errors)
- Percent agreement ≥ 70% for all sections

### Gate Validation
```python
sections_passing = sum(1 for section in results.values()
                      if section["kappa"] >= 0.60)
gate_passed = sections_passing >= 5
```

**Pass:** Display "✅ MUST_WORK gate PASSED"
**Fail:** Display "❌ MUST_WORK gate FAILED - ABANDON hypothesis"

---

## Dependencies

```
# requirements.txt
datasets>=2.10.0           # HuggingFace Hub
openml>=0.14.0            # OpenML API
beautifulsoup4>=4.11.0    # UCI scraping
requests>=2.28.0          # HTTP requests
scikit-learn>=1.2.0       # Cohen's kappa
scipy>=1.10.0             # Bootstrap CI
numpy>=1.24.0             # Numerical operations
matplotlib>=3.7.0         # Visualization
seaborn>=0.12.0           # Advanced plots
pandas>=1.5.0             # Data manipulation
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| API rate limits | 1-second delay between requests |
| UCI scraping failures | Fallback to known dataset list |
| Low inter-annotator agreement | Pre-training with calibration set + DTS study |
| Annotation fatigue | Time limits (5-10 min) + break protocol |
| Bootstrap CI instability | 1000 resamples + fixed random seed (42) |

---

## Phase 4 Implementation Notes

### Critical Path
1. Data collection (E1-1, E1-2) → Enables annotation
2. Annotation protocol (E1-3) → Enables kappa calculation
3. Kappa calculator (E1-4) → Enables gate validation
4. Gate validator (E1-5) → Required for success/failure
5. Visualization (E1-6) → Required for validation report

### Parallel Opportunities
- E1-1 and E1-2 can run together (collection + extraction)
- E1-5 and E1-6 can run in parallel (both use kappa results)

### External Data Requirements
- Rondina et al. (2025) calibration datasets (5 datasets)
- Gebru et al. (2021) DTS framework documentation

---

**Architecture Completed:** 2026-03-18
**Next Phase:** Phase 4 - Implementation
**Estimated Development Time:** 4-6 hours (code implementation) + 10-12 hours (human annotation)
