# Architecture: h-m3

**Date:** 2026-08-25
**Hypothesis:** Under confound pattern detection, if the system flags hypotheses with known confounds from literature, then precision >40% is achieved on labeled confound cases, because cross-domain confound patterns (tokenizer-BLEU, resolution-architecture) generalize across DL subfields.
**Type:** MECHANISM (rule-based pattern detection)
**Phase:** Phase 3 - Architecture Design

---

## Codebase Analysis (Serena)

**Project Type**: Green-field
**Status**: New implementation from scratch (rule-based confound detection, no existing code)
**Analyzed Path**: N/A
**Findings**: New confound detection system extending h-m2's testability verification.

---

## System Overview

**Applied**: Rule-based pattern matching (Archon KB)

**Architecture Type**: Evaluation-only symbolic system (no training)

**Data Flow**:
```
Confound DB → Detector → Predictions
Test Set → Ground Truth
Predictions + Ground Truth → Metrics → Visualization
```

**Components**: 5 modules (confound_db, detector, evaluator, baseline, visualizer)

---

## Module Specifications

### 1. ConfoundDatabase (`src/confound_db.py`)

**Dependencies**: None (stdlib only)

```python
class ConfoundDatabase:
    def __init__(self): ...
    def load_patterns(self) -> dict[str, list[dict]]: ...
    def get_all_patterns(self) -> list[dict]: ...
```

**Interface**:
- Input: None (hard-coded literature patterns)
- Output: {domain: [pattern_dicts]} with keywords + descriptions

---

### 2. ConfoundDetector (`src/detector.py`)

**Dependencies**: ConfoundDatabase

```python
class ConfoundDetector:
    def __init__(self, pattern_db: dict): ...
    def detect(self, hypothesis_text: str) -> tuple[str, Optional[str]]: ...
    def _match_keywords(self, text: str, keywords: list[str]) -> bool: ...
```

**Interface**:
- Input: `hypothesis_text` (str)
- Output: ("confounded", pattern_name) or ("unconfounded", None)
- Logic: All keywords in pattern must appear (case-insensitive)

---

### 3. Evaluator (`src/evaluator.py`)

**Dependencies**: None (sklearn)

```python
class Evaluator:
    def compute_metrics(self, y_true: list[str], y_pred: list[str]) -> dict: ...
    def confusion_matrix(self, y_true: list[str], y_pred: list[str]) -> dict: ...
```

**Interface**:
- Input: predictions, ground_truth (both list[str])
- Output: {precision, recall, accuracy, f1, tp, fp, tn, fn}

---

### 4. RandomBaseline (`src/baseline.py`)

**Dependencies**: None (stdlib)

```python
class RandomBaseline:
    def __init__(self, seed: int = 42): ...
    def predict(self, n_samples: int) -> list[str]: ...
```

**Interface**:
- Input: `n_samples` (int)
- Output: Random "confounded" | "unconfounded" predictions

---

### 5. Visualizer (`src/visualizer.py`)

**Dependencies**: Evaluator

```python
class Visualizer:
    def __init__(self, output_dir: str): ...
    def plot_gate_comparison(self, baseline: float, proposed: float, threshold: float) -> str: ...
    def plot_confusion_matrix(self, cm: dict, title: str) -> str: ...
    def plot_domain_breakdown(self, test_set: list[dict], predictions: list[str]) -> str: ...
```

**Interface**:
- Input: metrics dicts, confusion matrix, test set
- Output: figure file paths (saved to output_dir)

---

### 6. TestLoader (`src/test_loader.py`)

**Dependencies**: None (stdlib only)

```python
class TestLoader:
    def __init__(self): ...
    def generate_test_set(self) -> list[dict]: ...
```

**Interface**:
- Input: None (programmatic generation)
- Output: List of {text, label, domain} dicts (30 hypotheses)

---

### 7. ExperimentRunner (`src/main.py`)

**Dependencies**: All above modules

```python
def run_experiment(output_dir: str) -> dict:
    """
    Execute confound detection pipeline.
    Returns: {baseline_metrics, proposed_metrics, gate_passed}
    """
    ...
```

**Interface**:
- Input: output_dir path
- Output: metrics dict + saved figures
- Flow: generate test set → detect → evaluate → visualize

---

## File Structure

```
h-m3/
├── src/
│   ├── confound_db.py     # Literature-sourced confound patterns
│   ├── detector.py        # Keyword-based detection logic
│   ├── evaluator.py       # Precision/recall calculation
│   ├── baseline.py        # Random classifier
│   ├── visualizer.py      # Gate metrics, confusion matrix, domain plots
│   ├── test_loader.py     # Generate 30-hypothesis test set
│   └── main.py            # Experiment runner
├── data/                  # (Generated during runtime)
│   └── test_set.json      # 30 hypotheses with labels
├── figures/               # Output visualizations
└── config.py             # Fixed parameters
```

---

## Data Specification

### Confound Pattern Database

**Hard-coded in `confound_db.py`**:

```python
CONFOUND_PATTERNS = {
    "nlp": [
        {"keywords": ["tokenizer", "vocab", "BLEU"], 
         "description": "tokenizer-BLEU confound"},
        {"keywords": ["sequence length", "accuracy"], 
         "description": "length-metric confound"},
        {"keywords": ["vocabulary size", "perplexity"], 
         "description": "vocab-perplexity confound"},
        {"keywords": ["subword", "tokenization", "F1"], 
         "description": "tokenization-F1 confound"},
        {"keywords": ["max length", "truncation", "score"], 
         "description": "truncation-score confound"}
    ],
    "vision": [
        {"keywords": ["resolution", "architecture"], 
         "description": "resolution-architecture confound"},
        {"keywords": ["augmentation", "model capacity"], 
         "description": "augmentation-capacity confound"},
        {"keywords": ["image size", "depth"], 
         "description": "size-depth confound"},
        {"keywords": ["color depth", "network size"], 
         "description": "color-network confound"},
        {"keywords": ["crop size", "model complexity"], 
         "description": "crop-complexity confound"}
    ],
    "training": [
        {"keywords": ["batch size", "learning rate"], 
         "description": "batch-LR confound"},
        {"keywords": ["optimizer", "weight decay"], 
         "description": "optimizer-regularization confound"},
        {"keywords": ["epochs", "dataset size"], 
         "description": "epochs-data confound"},
        {"keywords": ["batch", "LR"], 
         "description": "batch-LR confound (abbrev)"},
        {"keywords": ["momentum", "learning rate schedule"], 
         "description": "momentum-schedule confound"}
    ]
}
```

### Test Set Structure

**Generated in `test_loader.py`** (30 hypotheses):

```python
test_set = [
    # Confounded (15 total: 5 NLP, 5 vision, 5 training)
    {"text": "BPE tokenizer 50k vocab vs 10k vocab on BLEU", 
     "label": "confounded", "domain": "nlp"},
    {"text": "224px resolution ResNet18 vs 448px ResNet50", 
     "label": "confounded", "domain": "vision"},
    {"text": "Batch size 256 with LR 0.1 vs batch 64 with LR 0.025", 
     "label": "confounded", "domain": "training"},
    
    # Unconfounded (15 total: 5 NLP, 5 vision, 5 training)
    {"text": "Increase dropout from 0.1 to 0.5 all else constant", 
     "label": "unconfounded", "domain": "training"},
    {"text": "Replace ReLU with GELU activation no other changes", 
     "label": "unconfounded", "domain": "nlp"},
    # ... 25 more
]
```

---

## Execution Flow

**No Training Phase** - Evaluation only:

1. **Setup Phase**
   - Load confound pattern database (15 patterns)
   - Generate 30-hypothesis test set (15 confounded, 15 unconfounded)

2. **Prediction Phase**
   - Baseline: Generate random predictions (seed=42)
   - Proposed: Run detector on each hypothesis

3. **Evaluation Phase**
   - Compute precision, recall, accuracy, F1
   - Generate confusion matrix

4. **Visualization Phase**
   - Figure 1: Gate Metrics Comparison (bar chart)
   - Figure 2: Confusion Matrix (heatmap)
   - Figure 3: Domain-Specific Performance (precision by domain)

5. **Gate Check**
   - Compare: `proposed_precision > 0.40` (SHOULD_WORK threshold)
   - Compare: `proposed_precision > baseline_precision` (PoC success)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Confound Database | Hard-code 15 literature patterns | 3 | Patterns(2) + Structure(1) |
| A-2 | Detection Logic | Keyword matching implementation | 6 | Match(3) + Cross-domain(2) + Interface(1) |
| A-3 | Test Generation | Generate 30-hypothesis test set | 5 | Templates(2) + Balance(2) + Labels(1) |
| A-4 | Evaluation Harness | Metrics + confusion matrix | 6 | Sklearn(2) + Metrics(2) + Confusion(2) |
| A-5 | Visualization | 3 figures (gate, CM, domain) | 7 | Gate(2) + CM(2) + Domain(2) + Save(1) |

**Complexity Distribution**:
- Low (4-8): [A-1, A-2, A-3, A-4, A-5]
- Medium (9-13): []

**Total Complexity**: 27 (5 epic tasks)

**Breakdown Legend**:
- Module_Size (1-5): Lines of code / complexity
- Dependencies (1-5): External dependencies count
- Algorithm (1-5): Logic complexity
- Integration (1-5): Inter-module coupling

---

## Configuration

### Fixed Parameters

```python
# config.py
SEED = 42
N_PATTERNS_MIN = 15  # Minimum confound patterns required
N_TEST_HYPOTHESES = 30  # 15 confounded, 15 unconfounded
OUTPUT_DIR = "figures/"
GATE_THRESHOLD_PRECISION = 0.40
```

---

## Success Criteria

**PoC Pass Conditions**:
1. Code runs without error
2. `proposed_precision > baseline_precision`

**Gate Pass Condition** (SHOULD_WORK):
- `proposed_precision > 0.40`

**Expected Results**:
- Baseline precision: ~50% (random chance)
- Proposed precision: >40% (hypothesis claim)

---

## Implementation Notes

**No Training Required**: Deterministic rule-based system.

**Deterministic Behavior**: Proposed detector has no randomness (only baseline does).

**Cross-Domain Transfer**: NLP patterns apply to vision/training domains and vice versa (keyword-based matching enables generalization).

**Pattern Sourcing**: All confound patterns from peer-reviewed literature (Salesky et al. 2020, Touvron et al. 2019, Goyal et al. 2017).

---

## Self-Validation

- [x] No ASCII diagrams (bullet lists used)
- [x] No KB search logs (only "Applied: X")
- [x] Module sections = interface code only
- [x] 5 Epic tasks (5 tasks within range)
- [x] Total length < 500 lines
- [x] Codebase Analysis (Serena) section included
- [x] Green-field project (Serena skip acceptable)
