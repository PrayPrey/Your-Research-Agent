# Architecture: h-m2

**Date:** 2026-08-25
**Hypothesis:** Under formal constraint-satisfiability verification, if a hypothesis H is evaluated against the KB, then the system produces <25% false positives (marks untestable as testable), because the ∃ (D,B,M) verification logic correctly distinguishes measurable interventions from non-measurable ones.
**Type:** MECHANISM (EXISTENCE phase - rule-based verification)
**Phase:** Phase 3 - Architecture Design

---

## Codebase Analysis (Serena)

**Project Type**: Green-field
**Status**: New implementation from scratch (rule-based system, no existing codebase)
**Analyzed Path**: N/A
**Findings**: No existing code to analyze. This is a formal verification system with deterministic logic.

---

## System Overview

**Applied**: Rule-based constraint verification pattern (Archon KB)

**Architecture Type**: Evaluation-only symbolic system (no training phase)

**Data Flow**:
```
KB (h-m1) → Verifier → Predictions
Test Set → Ground Truth
Predictions + Ground Truth → Metrics → Visualization
```

**Components**: 5 modules (kb_loader, verifier, evaluator, baseline, visualizer)

---

## Module Specifications

### 1. KBLoader (`src/kb_loader.py`)

**Dependencies**: None (stdlib only)

```python
class KBLoader:
    def __init__(self, kb_path: str): ...
    def load(self) -> list[dict]: ...
    def get_triples(self) -> list[tuple[str, str, str]]: ...
```

**Interface**:
- Input: `kb_path` (str) - path to h-m1/data/pwc_cache/kb.yaml
- Output: List of {dataset, benchmark, metric} dicts

---

### 2. ConstraintVerifier (`src/verifier.py`)

**Dependencies**: KBLoader

```python
class ConstraintVerifier:
    def __init__(self, kb: list[dict]): ...
    def extract_dbm(self, hypothesis_text: str) -> tuple[str, str, str]: ...
    def verify(self, hypothesis_text: str) -> str: ...
```

**Interface**:
- Input: `hypothesis_text` (str)
- Output: "testable" | "not_testable"
- Logic: ∃ (D,B,M) ∈ KB existence check

---

### 3. Evaluator (`src/evaluator.py`)

**Dependencies**: None (stdlib only)

```python
class Evaluator:
    def compute_metrics(self, predictions: list[str], ground_truth: list[str]) -> dict: ...
    def confusion_matrix(self, predictions: list[str], ground_truth: list[str]) -> dict: ...
```

**Interface**:
- Input: predictions, ground_truth (both list[str])
- Output: {fpr, precision, accuracy, tp, fp, tn, fn}

---

### 4. RandomBaseline (`src/baseline.py`)

**Dependencies**: None (stdlib only)

```python
class RandomBaseline:
    def __init__(self, seed: int = 42): ...
    def predict(self, n_samples: int) -> list[str]: ...
```

**Interface**:
- Input: `n_samples` (int)
- Output: List of random "testable" | "not_testable" predictions

---

### 5. Visualizer (`src/visualizer.py`)

**Dependencies**: Evaluator

```python
class Visualizer:
    def __init__(self, output_dir: str): ...
    def plot_confusion_matrix(self, cm: dict, title: str) -> str: ...
    def plot_metrics_comparison(self, baseline_metrics: dict, proposed_metrics: dict) -> str: ...
```

**Interface**:
- Input: metrics dicts, confusion matrix
- Output: figure file paths (saved to output_dir)

---

### 6. TestLoader (`src/test_loader.py`)

**Dependencies**: None (stdlib only)

```python
class TestLoader:
    def __init__(self, test_path: str): ...
    def load(self) -> tuple[list[str], list[str]]: ...
```

**Interface**:
- Input: `test_path` (str) - path to test_hypotheses.json
- Output: (test_hypotheses, ground_truth_labels)

---

### 7. ExperimentRunner (`src/main.py`)

**Dependencies**: All above modules

```python
def run_experiment(kb_path: str, test_path: str, output_dir: str) -> dict:
    """
    Execute full evaluation pipeline.
    Returns: {baseline_metrics, proposed_metrics, gate_passed}
    """
    ...
```

**Interface**:
- Input: paths (kb, test set, output directory)
- Output: metrics dict + saved figures
- Flow: load → verify → evaluate → visualize

---

## File Structure

```
h-m2/
├── src/
│   ├── kb_loader.py       # Load h-m1 KB (42 triples)
│   ├── verifier.py        # ∃ (D,B,M) verification logic
│   ├── evaluator.py       # FPR calculation
│   ├── baseline.py        # Random classifier
│   ├── visualizer.py      # Confusion matrix, metrics plots
│   ├── test_loader.py     # Load expert-labeled test set
│   └── main.py            # Experiment runner
├── data/
│   └── test_hypotheses.json  # 20 expert-labeled hypotheses
├── figures/               # Output visualizations
└── config.py             # Paths configuration
```

---

## Data Dependencies

### External Data (h-m1)

| Resource | Path | Format |
|----------|------|--------|
| Knowledge Base | `docs/youra_research/h-m1/data/pwc_cache/kb.yaml` | YAML (49 triples) |

**KB Structure**:
```yaml
triples:
  - dataset: "CIFAR-10"
    benchmark: "image-classification"
    metric: "Accuracy"
  # ... 49 total
```

### Local Data (h-m2)

| Resource | Path | Format |
|----------|------|--------|
| Test Set | `h-m2/data/test_hypotheses.json` | JSON (20 hypotheses) |

**Test Set Structure**:
```json
[
  {"text": "Hypothesis statement...", "expert_label": "testable"},
  {"text": "Hypothesis statement...", "expert_label": "untestable"}
]
```

---

## Execution Flow

**No Training Phase** - Evaluation only:

1. **Load Phase**
   - Load KB from h-m1 (42 D,B,M triples)
   - Load test set (20 expert-labeled hypotheses)

2. **Prediction Phase**
   - Baseline: Generate random predictions (seed=42)
   - Proposed: Run verifier on each hypothesis

3. **Evaluation Phase**
   - Compute FPR, precision, accuracy
   - Generate confusion matrix

4. **Visualization Phase**
   - Plot confusion matrix (baseline vs proposed)
   - Plot metrics comparison bar chart

5. **Gate Check**
   - Compare: `proposed_fpr < 0.25` (MUST_WORK threshold)
   - Compare: `proposed_fpr < baseline_fpr` (PoC success)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Loading | Load KB + test set | 4 | Setup(1) + KB(1) + Test(2) |
| A-2 | Verifier Implementation | ∃ (D,B,M) logic | 8 | Extract(3) + Match(3) + Verify(2) |
| A-3 | Evaluation Harness | FPR + metrics | 6 | Metrics(2) + Confusion(2) + Baseline(2) |
| A-4 | Visualization | Plots + figures | 5 | Confusion(2) + Comparison(2) + Save(1) |

**Complexity Distribution**:
- Low (4-8): [A-1, A-3, A-4]
- Medium (9-13): [A-2]

**Total Complexity**: 23 (4 epic tasks)

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
KB_PATH = "../h-m1/data/pwc_cache/kb.yaml"
TEST_PATH = "data/test_hypotheses.json"
OUTPUT_DIR = "figures/"
GATE_THRESHOLD_FPR = 0.25
```

---

## Success Criteria

**PoC Pass Conditions**:
1. Code runs without error
2. `proposed_fpr < baseline_fpr` (verifier beats random)

**Gate Pass Condition** (MUST_WORK):
- `proposed_fpr < 0.25`

**Expected Results**:
- Baseline FPR: ~50% (random chance)
- Proposed FPR: <25% (hypothesis claim)

---

## Implementation Notes

**No Training Required**: This is a deterministic rule-based system.

**Deterministic Behavior**: Same input → same output (no randomness in verifier, only in baseline).

**Single-Pass Evaluation**: 20 hypotheses evaluated once.

**Minimal Dependencies**: Stdlib + YAML parser + matplotlib (visualization only).

---

## Self-Validation

- [x] No ASCII diagrams (bullet lists used)
- [x] No KB search logs (only "Applied: X")
- [x] Module sections = interface code only
- [x] 4 Epic tasks (EXISTENCE phase = 3-5 tasks)
- [x] Total length < 500 lines
- [x] Codebase Analysis (Serena) section included
- [x] Green-field project (Serena skip acceptable)
