# Logic Specification: h-m2 Formal Verification System

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New symbolic verification system (no existing codebase)  
**Analyzed Path**: N/A  
**Relevant Symbols**: None - new implementation

---

## L-1: ConstraintSatisfiabilityVerifier [Complexity: 2, Budget: 8]

**Applied**: Standard Python pattern (symbolic rule-based system)

### API Signatures

```python
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class DBMTriple:
    domain: str
    behavior: str
    measurement: str

class ConstraintSatisfiabilityVerifier:
    def __init__(self, kb_path: str):
        """Load KB from h-m1. kb_path: path to h-m1/KB.json."""
        self.kb: List[DBMTriple] = []
    
    def extract_dbm(self, hypothesis_text: str) -> Optional[DBMTriple]:
        """Extract (D,B,M) from hypothesis text via keyword matching.
        Returns: DBMTriple or None if extraction fails."""
        ...
    
    def verify(self, hypothesis_text: str) -> str:
        """Check ∃ (D,B,M) ∈ KB. Returns: 'testable' or 'not_testable'."""
        ...
    
    def _exact_match(self, extracted: DBMTriple) -> bool:
        """Check if extracted triple exists in KB (exact string match)."""
        ...
```

### Pseudo-code

```
__init__(kb_path):
    1. Load JSON from kb_path (format: [{domain, behavior, measurement}, ...])
    2. Parse into List[DBMTriple]

extract_dbm(hypothesis_text):
    1. Normalize text: lowercase, strip whitespace
    2. For each kb_triple in self.kb:
        - If kb_triple.domain in text AND kb_triple.behavior in text AND kb_triple.measurement in text:
            - Return kb_triple
    3. Return None

verify(hypothesis_text):
    1. extracted = extract_dbm(hypothesis_text)
    2. If extracted is None:
        - Return "not_testable"
    3. If _exact_match(extracted):
        - Return "testable"
    4. Else:
        - Return "not_testable"

_exact_match(extracted):
    1. For each kb_triple in self.kb:
        - If extracted == kb_triple (exact equality):
            - Return True
    2. Return False
```

### Subtasks [3/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | KB loading | Parse h-m1 KB JSON into DBMTriple list |
| L-1-2 | Keyword extraction | Match D,B,M keywords in hypothesis text |
| L-1-3 | Existence check | Verify extracted triple exists in KB |

---

## L-2: Evaluation Harness [Complexity: 1, Budget: 5]

**Applied**: Standard Python pattern

### API Signatures

```python
from typing import List, Dict

@dataclass
class LabeledSample:
    id: int
    hypothesis: str
    ground_truth: str  # "testable" or "not_testable"

def load_test_set(path: str) -> List[LabeledSample]:
    """Load 20 expert-labeled hypotheses. path: JSON file with samples."""
    ...

def compute_fpr(predictions: List[str], ground_truth: List[str]) -> float:
    """Calculate FPR = FP / (FP + TN). Returns: float [0.0, 1.0]."""
    ...

def compute_metrics(predictions: List[str], ground_truth: List[str]) -> Dict[str, float]:
    """Calculate all metrics. Returns: {fpr, precision, recall, accuracy, f1}."""
    ...
```

### Pseudo-code

```
load_test_set(path):
    1. Load JSON from path (format: [{id, hypothesis, ground_truth}, ...])
    2. Parse into List[LabeledSample]
    3. Assert len(samples) == 20
    4. Return samples

compute_fpr(predictions, ground_truth):
    1. FP = count(pred="testable" AND truth="not_testable")
    2. TN = count(pred="not_testable" AND truth="not_testable")
    3. If (FP + TN) == 0: return 0.0
    4. Return FP / (FP + TN)

compute_metrics(predictions, ground_truth):
    1. TP = count(pred="testable" AND truth="testable")
    2. FP = count(pred="testable" AND truth="not_testable")
    3. TN = count(pred="not_testable" AND truth="not_testable")
    4. FN = count(pred="not_testable" AND truth="testable")
    5. FPR = FP / (FP + TN) if (FP + TN) > 0 else 0.0
    6. Precision = TP / (TP + FP) if (TP + FP) > 0 else 0.0
    7. Recall = TP / (TP + FN) if (TP + FN) > 0 else 0.0
    8. Accuracy = (TP + TN) / (TP + FP + TN + FN)
    9. F1 = 2 * Precision * Recall / (Precision + Recall) if (Precision + Recall) > 0 else 0.0
    10. Return {fpr, precision, recall, accuracy, f1}
```

### Subtasks [2/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Test set loader | Parse labeled samples from JSON |
| L-2-2 | Metrics calculation | Compute FPR and secondary metrics |

---

## L-3: Main Experiment Flow [Complexity: 1, Budget: 4]

**Applied**: Standard Python script pattern

### API Signatures

```python
def run_experiment(kb_path: str, test_set_path: str, output_dir: str) -> Dict[str, float]:
    """Run full h-m2 experiment. Returns: metrics dict."""
    ...

def save_results(metrics: Dict[str, float], predictions: List[Dict], output_dir: str):
    """Save metrics.json and predictions.json to output_dir."""
    ...

def generate_visualizations(metrics: Dict[str, float], predictions: List[Dict], output_dir: str):
    """Generate confusion matrix PNG and metrics bar chart."""
    ...
```

### Pseudo-code

```
run_experiment(kb_path, test_set_path, output_dir):
    1. verifier = ConstraintSatisfiabilityVerifier(kb_path)
    2. samples = load_test_set(test_set_path)
    3. predictions = [verifier.verify(s.hypothesis) for s in samples]
    4. ground_truth = [s.ground_truth for s in samples]
    5. metrics = compute_metrics(predictions, ground_truth)
    6. save_results(metrics, predictions, output_dir)
    7. generate_visualizations(metrics, predictions, output_dir)
    8. Return metrics

save_results(metrics, predictions, output_dir):
    1. Write metrics to {output_dir}/metrics.json
    2. Write predictions to {output_dir}/predictions.json (format: [{id, hypothesis, prediction, truth}, ...])

generate_visualizations(metrics, predictions, output_dir):
    1. Create confusion matrix (2x2) from predictions and truth
    2. Save as {output_dir}/confusion_matrix.png
    3. Create bar chart of all metrics
    4. Save as {output_dir}/metrics_chart.png
```

### Subtasks [2/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Experiment orchestration | Load KB, run verifier, compute metrics |
| L-3-2 | Results serialization | Save JSON and generate plots |

---

## Data Structures

### KB Format (h-m1 Output)

```json
[
  {"domain": "computer vision", "behavior": "object detection accuracy", "measurement": "mAP@0.5"},
  {"domain": "nlp", "behavior": "translation quality", "measurement": "BLEU score"}
]
```

### Test Set Format

```json
[
  {"id": 1, "hypothesis": "In computer vision, using ResNet improves object detection accuracy measured by mAP@0.5", "ground_truth": "testable"},
  {"id": 2, "hypothesis": "Deep learning models are generally better than traditional methods", "ground_truth": "not_testable"}
]
```

### Predictions Output

```json
[
  {"id": 1, "hypothesis": "...", "prediction": "testable", "ground_truth": "testable"},
  {"id": 2, "hypothesis": "...", "prediction": "not_testable", "ground_truth": "not_testable"}
]
```

---

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in code comments (N/A for symbolic system)
- [x] Subtask count within budget (7/17 used)
- [x] Total length < 600 lines
- [x] "Codebase Analysis (Serena)" section included
- [x] Green-field project (Serena skip acceptable)

---

**Total Complexity Used**: 7/17 subtasks  
**Key Design Choices**:
- Keyword matching over NLP parsing (EXISTENCE = minimal logic)
- Exact string match for KB lookup (deterministic, no fuzzy matching)
- Binary output only (no confidence scores)
- Standard JSON I/O (no custom serialization)
