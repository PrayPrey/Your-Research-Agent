---
name: System Architecture
type: architecture
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
created_at: 2026-03-17
version: 1.0
patterns_applied: ["minimal PoC structure", "single-script NLP pipeline"]
---

# System Architecture: H-E1 Linguistic Marker Extraction

**Applied:** Minimal PoC structure (EXISTENCE hypothesis)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field project - no existing code to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch using standard NLP libraries (spaCy, NLTK, regex)

---

## Architecture Overview

**Type:** Statistical analysis pipeline (NOT model training)
**Infrastructure:** LIGHT (EXISTENCE PoC - minimal complexity)
**Components:** 4 modules (data, extraction, analysis, visualization)

---

## Module Definitions

### DataLoader (`code/data_loader.py`)

**Dependencies:** datasets (HuggingFace)

```python
class HHRLHFDataLoader:
    def load_dataset(self) -> dict: ...
    def preprocess_text(self, text: str) -> str: ...
    def get_all_responses(self) -> list[dict]: ...
```

### LinguisticExtractor (`code/extractor.py`)

**Dependencies:** spacy, re

```python
class LinguisticMarkerExtractor:
    def __init__(self): ...
    def extract_modal_verbs(self, text: str) -> float: ...
    def extract_hedging(self, text: str) -> float: ...
    def extract_alternatives(self, text: str) -> float: ...
    def extract_all_features(self, text: str) -> dict: ...
```

### StatisticalAnalyzer (`code/analyzer.py`)

**Dependencies:** numpy, pandas, scipy

```python
class StatisticalAnalyzer:
    def compute_statistics(self, features: np.ndarray) -> dict: ...
    def compute_cv(self, features: np.ndarray) -> float: ...
    def cross_split_validation(self, split_features: dict) -> dict: ...
    def gate_evaluation(self, cv: float, precision: float) -> bool: ...
```

### Visualizer (`code/visualizer.py`)

**Dependencies:** matplotlib, seaborn

```python
class Visualizer:
    def plot_gate_metrics(self, metrics: dict, output_path: str): ...
    def plot_distribution(self, features: np.ndarray, output_path: str): ...
    def plot_split_comparison(self, split_data: dict, output_path: str): ...
    def plot_correlation(self, modal: np.ndarray, hedging: np.ndarray, output_path: str): ...
```

### MainRunner (`code/main.py`)

**Dependencies:** DataLoader, LinguisticExtractor, StatisticalAnalyzer, Visualizer

```python
def main():
    # Load data
    # Extract features
    # Compute statistics
    # Generate visualizations
    # Evaluate gate condition
    # Save results
    ...

if __name__ == "__main__":
    main()
```

### Configuration (`code/config.py`)

**Dependencies:** None

```python
class Config:
    HEDGING_MARKERS: set[str]
    ALT_PATTERNS: list[str]
    RANDOM_SEED: int
    OUTPUT_DIR: str
    GATE_THRESHOLD_CV: float
    GATE_THRESHOLD_PRECISION: float
```

---

## File Structure

```
h-e1/
├── code/
│   ├── main.py              # Entry point
│   ├── config.py            # Configuration constants
│   ├── data_loader.py       # HH-RLHF dataset loading
│   ├── extractor.py         # Linguistic marker extraction
│   ├── analyzer.py          # Statistical analysis
│   ├── visualizer.py        # Figure generation
│   └── requirements.txt     # Dependencies
├── figures/                 # Output visualizations
│   ├── gate_metrics.png     # MANDATORY
│   ├── distribution.png
│   ├── split_comparison.png
│   └── correlation.png
├── h_e1_features.csv        # Extracted features
├── h_e1_statistics.json     # Statistics summary
└── 04_validation.md         # Results report
```

---

## Data Flow

1. `DataLoader` → Load HH-RLHF (3 splits, ~322K responses)
2. `LinguisticExtractor` → Extract 3 marker types per response
3. `StatisticalAnalyzer` → Compute CV, mean, SD across all samples
4. `Visualizer` → Generate 4 figures (gate metrics + 3 optional)
5. `MainRunner` → Evaluate gate (CV > 0.3 AND precision > 90%)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Pipeline | Load HH-RLHF, preprocess text, verify sample count | 8 | M(2)+D(1)+A(2)+I(3) |
| A-2 | Feature Extraction | Implement 3 marker extractors (modal, hedging, alt) | 11 | M(3)+D(2)+A(4)+I(2) |
| A-3 | Statistical Analysis | Compute CV, cross-split validation, gate evaluation | 9 | M(2)+D(2)+A(3)+I(2) |
| A-4 | Visualization | Generate 4 figures (gate metrics MANDATORY) | 7 | M(2)+D(1)+A(2)+I(2) |
| A-5 | Integration | Main runner, results report, validation output | 10 | M(2)+D(3)+A(2)+I(3) |

**Distribution:**
- VeryHigh(18-20): []
- High(14-17): []
- Medium(9-13): [A-2, A-3, A-5]
- Low(4-8): [A-1, A-4]

**Total Complexity:** 45 (5 tasks)

---

## Dependencies

### Python Libraries

```txt
datasets>=2.14.0      # HuggingFace HH-RLHF
spacy>=3.5.0          # POS tagging
numpy>=1.24.0         # Statistics
pandas>=2.0.0         # Data manipulation
matplotlib>=3.7.0     # Visualization
seaborn>=0.12.0       # Statistical plots
scipy>=1.10.0         # Advanced stats
```

### External Resources

- spaCy model: `en_core_web_sm` (download: `python -m spacy download en_core_web_sm`)
- HH-RLHF dataset: Auto-download via HuggingFace

---

## Success Criteria Mapping

| Epic Task | Success Criteria |
|-----------|------------------|
| A-1 | ~322K responses loaded, word count normalization |
| A-2 | 3 marker types extracted, per-100-words normalized |
| A-3 | Modal CV computed, gate evaluation (CV > 0.3) |
| A-4 | Gate metrics figure generated (MANDATORY) |
| A-5 | Results report with PASS/FAIL gate decision |

---

## Non-Functional Properties

**Performance:** CPU-only, 30-60 min runtime for full dataset
**Reproducibility:** Fixed random seed (42)
**Storage:** ~2GB dataset cache + 100MB results
**Infrastructure:** Minimal (hardcoded config, print logging, smoke test)

---

*Architecture Type: EXISTENCE PoC (minimal complexity)*
*Total Epic Tasks: 5 (within LIGHT tier limit)*
*Infrastructure Tier: LIGHT (no complex testing, simple CLI)*
