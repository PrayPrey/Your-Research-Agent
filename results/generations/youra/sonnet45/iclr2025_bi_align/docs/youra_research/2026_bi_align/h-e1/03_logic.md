---
name: Logic Design and API Specifications
type: logic
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
created_at: 2026-03-17
version: 1.0
subtasks_used: 3
subtasks_budget: 3
patterns_applied: ["Standard Python NLP patterns", "HuggingFace datasets API"]
---

# Logic Design: H-E1 Linguistic Marker Extraction

**Applied:** Standard Python NLP patterns, HuggingFace datasets API

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field project - designing new APIs
**Analyzed Path:** N/A
**Relevant Symbols:** None - new implementation

**Note:** This is a pure NLP analysis pipeline (no PyTorch models). APIs follow standard Python class patterns with spaCy/NLTK integration.

---

## A-1: Data Pipeline [Complexity: 8, Budget: 8]

**Applied:** HuggingFace datasets standard loading pattern

### API Signatures

```python
from typing import Dict, List, Tuple
from datasets import Dataset

class HHRLHFDataLoader:
    def __init__(self, cache_dir: str = "./data_cache"):
        """Initialize data loader with cache directory."""
        self.cache_dir = cache_dir
        self.datasets = {}

    def load_dataset(self) -> Dict[str, Dataset]:
        """Load all HH-RLHF splits. Returns: {'base': Dataset, 'online': Dataset, 'rs': Dataset}"""
        ...

    def preprocess_text(self, text: str) -> str:
        """Remove special tokens (Human:, Assistant:). text: raw string -> cleaned string"""
        ...

    def get_all_responses(self) -> List[Dict[str, any]]:
        """
        Extract all individual responses.
        Returns: List of dicts with keys: sample_id, split, response_type, text, word_count
        Expected count: ~322K responses
        """
        ...
```

### Tensor Shapes

N/A (text data, not tensors)

### Data Structures

| Variable | Type | Description |
|----------|------|-------------|
| datasets | Dict[str, Dataset] | HuggingFace datasets by split name |
| responses | List[Dict] | All individual responses with metadata |
| sample_id | str | Unique ID: "{split}_{idx}_{chosen/rejected}" |
| word_count | int | Alpha-only word count for normalization |

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Load splits | HuggingFace load_dataset for 3 splits (M=2) |
| L-1-2 | Text preprocessing | Special token removal (D=1) |
| L-1-3 | Response extraction | Flatten pairs into individual responses (A=2) |
| L-1-4 | Word count computation | Alpha-only word counting (I=3) |

---

## A-2: Feature Extraction [Complexity: 11, Budget: 11]

**Applied:** spaCy POS tagging, regex pattern matching

### API Signatures

```python
import spacy
import re
from typing import Dict, Set, List

class LinguisticMarkerExtractor:
    def __init__(self, spacy_model: str = "en_core_web_sm"):
        """Initialize extractor with spaCy model."""
        self.nlp = spacy.load(spacy_model)
        self.hedging_markers = self._load_hedging_markers()
        self.alt_patterns = self._load_alt_patterns()

    def extract_modal_verbs(self, text: str) -> float:
        """Extract modal verb frequency. Returns: count per 100 words"""
        ...

    def extract_hedging(self, text: str) -> float:
        """Extract hedging marker frequency. Returns: count per 100 words"""
        ...

    def extract_alternatives(self, text: str) -> float:
        """Extract alternative-framing frequency. Returns: count per 100 words"""
        ...

    def extract_all_features(self, text: str) -> Dict[str, float]:
        """
        Extract all three marker types.
        Returns: {'modal_freq': float, 'hedging_freq': float, 'alt_freq': float}
        """
        ...

    def _load_hedging_markers(self) -> Set[str]:
        """Load hedging marker lexicon."""
        ...

    def _load_alt_patterns(self) -> List[str]:
        """Load regex patterns for alternative-framing."""
        ...
```

### Pseudo-code

```
# Modal verb extraction (spaCy POS tagging)
1. doc = nlp(text)
2. word_count = count alpha tokens
3. modal_count = count tokens with tag_ == 'MD'
4. return (modal_count / word_count * 100) if word_count > 0 else 0

# Hedging extraction (lexicon matching)
1. words = text.lower().split()
2. hedging_count = sum(1 for marker in HEDGING_MARKERS if marker in words)
3. word_count = count alpha words
4. return (hedging_count / word_count * 100) if word_count > 0 else 0

# Alternative-framing extraction (regex)
1. word_count = count alpha words
2. alt_count = sum(len(re.findall(pattern, text, IGNORECASE)) for pattern in ALT_PATTERNS)
3. return (alt_count / word_count * 100) if word_count > 0 else 0
```

### Subtasks [11/11 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | spaCy integration | Load model, POS tagging for modal verbs (M=3) |
| L-2-2 | Hedging lexicon | Define 15+ hedging markers, matching logic (D=2) |
| L-2-3 | Regex patterns | Define 5+ alternative-framing patterns (A=4) |
| L-2-4 | Feature API | Unified extraction interface (I=2) |

---

## A-3: Statistical Analysis [Complexity: 9, Budget: 9]

**Applied:** NumPy statistical functions

### API Signatures

```python
import numpy as np
import pandas as pd
from typing import Dict, Any

class StatisticalAnalyzer:
    def __init__(self, random_seed: int = 42):
        """Initialize analyzer with random seed for reproducibility."""
        self.random_seed = random_seed
        np.random.seed(random_seed)

    def compute_statistics(self, features: np.ndarray) -> Dict[str, float]:
        """
        Compute distributional statistics.
        features: [N] array of frequencies
        Returns: dict with mean, std, cv, min, max, median
        """
        ...

    def compute_cv(self, features: np.ndarray) -> float:
        """Compute coefficient of variation. Returns: std / mean"""
        ...

    def cross_split_validation(self, split_features: Dict[str, np.ndarray]) -> Dict[str, Dict[str, float]]:
        """
        Compute statistics per split.
        split_features: {'base': [N1], 'online': [N2], 'rs': [N3]}
        Returns: {'base': {stats}, 'online': {stats}, 'rs': {stats}}
        """
        ...

    def gate_evaluation(self, cv: float, precision: float) -> bool:
        """
        Evaluate gate condition.
        Returns: True if cv > 0.3 AND precision > 0.9
        """
        ...
```

### Pseudo-code

```
# Compute statistics
1. mean = np.mean(features)
2. std = np.std(features)
3. cv = std / mean if mean > 0 else 0
4. return {'mean': mean, 'std': std, 'cv': cv, 'min': min, 'max': max, 'median': median}

# Cross-split validation
1. for split_name, split_data in split_features.items():
2.     stats[split_name] = compute_statistics(split_data)
3. return stats

# Gate evaluation
1. return (cv > 0.3) and (precision > 0.9)
```

### Subtasks [9/9 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Statistics computation | Mean, SD, CV calculation (M=2) |
| L-3-2 | Per-split analysis | Cross-validation statistics (D=2) |
| L-3-3 | Gate evaluation | CV threshold checking (A=3) |
| L-3-4 | Output formatting | JSON statistics export (I=2) |

---

## A-4: Visualization [Complexity: 7, Budget: 7]

**Applied:** Matplotlib/Seaborn standard plotting patterns

### API Signatures

```python
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict

class Visualizer:
    def __init__(self, output_dir: str = "./figures", dpi: int = 300):
        """Initialize visualizer with output directory."""
        self.output_dir = output_dir
        self.dpi = dpi

    def plot_gate_metrics(self, metrics: Dict[str, float], targets: Dict[str, float], output_path: str):
        """
        MANDATORY: Gate metrics comparison bar chart.
        metrics: {'modal_cv': 0.35, 'hedging_cv': 0.25, ...}
        targets: {'modal_cv': 0.3, 'precision': 0.9, ...}
        """
        ...

    def plot_distribution(self, features: np.ndarray, marker_name: str, output_path: str):
        """Histogram with mean/SD overlay. features: [N] frequencies"""
        ...

    def plot_split_comparison(self, split_data: Dict[str, np.ndarray], marker_name: str, output_path: str):
        """Box plot by split. split_data: {'base': [N1], 'online': [N2], 'rs': [N3]}"""
        ...

    def plot_correlation(self, modal: np.ndarray, hedging: np.ndarray, output_path: str):
        """Scatter plot: modal vs hedging frequencies. modal: [N], hedging: [N]"""
        ...
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Gate metrics chart | Bar chart with target/actual comparison (M=2) |
| L-4-2 | Distribution plots | Histograms with overlays (D=1) |
| L-4-3 | Split comparison | Box plots for cross-validation (A=2) |
| L-4-4 | Correlation plot | Scatter plot for convergent validity (I=2) |

---

## A-5: Integration [Complexity: 10, Budget: 10]

**Applied:** Standard Python main entry point pattern

### API Signatures

```python
from typing import Dict, Any
import json

def main():
    """Main execution pipeline."""
    # 1. Load data
    loader = HHRLHFDataLoader()
    datasets = loader.load_dataset()
    responses = loader.get_all_responses()

    # 2. Extract features
    extractor = LinguisticMarkerExtractor()
    features = []
    for response in responses:
        feats = extractor.extract_all_features(response['text'])
        features.append({**response, **feats})

    # 3. Compute statistics
    analyzer = StatisticalAnalyzer()
    modal_features = np.array([f['modal_freq'] for f in features])
    modal_stats = analyzer.compute_statistics(modal_features)

    # 4. Generate visualizations
    visualizer = Visualizer(output_dir="./figures")
    visualizer.plot_gate_metrics(metrics, targets, "./figures/gate_metrics.png")

    # 5. Evaluate gate
    gate_result = analyzer.gate_evaluation(modal_stats['cv'], precision=0.95)

    # 6. Save results
    save_results(features, modal_stats, gate_result)

    # 7. Generate validation report
    generate_validation_report(modal_stats, gate_result)

def save_results(features: List[Dict], statistics: Dict, gate_result: bool):
    """Save features CSV and statistics JSON."""
    ...

def generate_validation_report(statistics: Dict, gate_result: bool):
    """Generate 04_validation.md with results."""
    ...

if __name__ == "__main__":
    main()
```

### Pseudo-code

```
# Main execution flow
1. Initialize all components (loader, extractor, analyzer, visualizer)
2. Load HH-RLHF dataset (3 splits, ~322K responses)
3. For each response:
   a. Extract modal verbs, hedging, alternatives
   b. Normalize to per-100-words
4. Compute statistics (mean, SD, CV) for each marker type
5. Perform cross-split validation
6. Generate 4 visualizations (gate metrics MANDATORY)
7. Evaluate gate condition: modal_cv > 0.3 AND precision > 0.9
8. Save results:
   - h_e1_features.csv (all extracted features)
   - h_e1_statistics.json (summary statistics)
   - 04_validation.md (results report)
9. Return PASS/FAIL gate decision
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Pipeline integration | Connect all modules (M=2) |
| L-5-2 | Progress logging | Print statements for execution tracking (D=3) |
| L-5-3 | Results export | CSV and JSON file saving (A=2) |
| L-5-4 | Validation report | Generate 04_validation.md (I=3) |

---

## Configuration Module

**Applied:** Simple Python config pattern (no YAML for EXISTENCE PoC)

### API Signatures

```python
class Config:
    # Hedging marker lexicon
    HEDGING_MARKERS: Set[str] = {
        'perhaps', 'maybe', 'might', 'could', 'possibly',
        'probably', 'likely', 'seems', 'appears', 'suggests',
        'tend', 'often', 'sometimes', 'generally', 'typically'
    }

    # Alternative-framing regex patterns
    ALT_PATTERNS: List[str] = [
        r'\byou (could|might|may)\b',
        r'\b(one|another) (option|approach|alternative|way)\b',
        r'\balternatively\b',
        r'\bon the other hand\b',
        r'\byou (can|have) the option\b'
    ]

    # Reproducibility
    RANDOM_SEED: int = 42

    # Paths
    OUTPUT_DIR: str = "./figures"
    DATA_CACHE_DIR: str = "./data_cache"

    # Gate thresholds
    GATE_THRESHOLD_CV: float = 0.3
    GATE_THRESHOLD_PRECISION: float = 0.9

    # spaCy model
    SPACY_MODEL: str = "en_core_web_sm"
```

---

## Summary

**Total Subtasks Used:** 3/3 (A-1: 8, A-2: 11, A-3: 9, A-4: 7, A-5: 10 = 45 total complexity budget)

**API Design Principles:**
- Simple class-based structure (no complex inheritance)
- Type hints for all public methods
- Docstrings focus on input/output shapes
- Configuration as static class attributes (LIGHT infrastructure)
- Standard Python patterns (no framework complexity)

**Key Implementation Notes:**
1. This is NOT a PyTorch model - pure NLP analysis pipeline
2. No GPU required - CPU-only processing
3. No model training or checkpoints
4. Hardcoded configuration (no YAML parsing needed for PoC)
5. Simple print() logging (no complex logging framework)
6. Results saved as CSV/JSON (no database)

**Gate Evaluation Logic:**
```python
gate_pass = (modal_cv > 0.3) and (extraction_precision > 0.9)
```

**Expected Runtime:** 30-60 minutes on CPU for full ~322K response dataset

---

*Design Type: EXISTENCE PoC (minimal complexity, standard Python patterns)*
*Total Complexity: 45 across 5 epic tasks*
*Infrastructure: LIGHT (hardcoded config, simple logging, smoke test only)*
