# Logic Specification: h-c1 Domain Boundary Detection

**Date:** 2026-08-25
**Hypothesis:** h-c1 (CONDITION - boundary case classification)
**Phase:** Phase 3 - Logic Design
**Budget:** 8 subtasks allocated

---

## Codebase Analysis (Serena)

**Project Type**: incremental_extension
**Status**: Extending h-m4 verifier with domain boundary pre-filter
**Analyzed Path**: h-m4/src/verifier.py (ConstraintVerifier to extend)
**Relevant Symbols**: ConstraintVerifier.check_testability(), _load_kb()

**Note**: h-c1 adds DomainBoundaryDetector before h-m4 (D,B,M) check. Import h-m4 verifier class directly.

---

## Epic 1: DomainBoundaryDetector [Complexity: 8, Budget: 3/3]

**Applied**: OOD detection pattern (Archon KB)

### API Signatures

```python
from typing import Dict, List, Set, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

class DomainBoundaryDetector:
    def __init__(self, kb_domains: List[Dict], similarity_threshold: float = 0.7):
        """
        Args:
            kb_domains: List of {name: str, keywords: List[str]} from KB taxonomy
            similarity_threshold: Minimum similarity for in-scope classification
        """
        self.kb_domains = kb_domains
        self.threshold = similarity_threshold
        self.domain_embeddings = self._build_domain_embeddings()
        self.tfidf = TfidfVectorizer(max_features=100, stop_words='english')
    
    def _build_domain_embeddings(self) -> Dict[str, Set[str]]:
        """
        Build keyword sets for each KB domain.
        Returns: {domain_name: set(keywords)}
        """
        ...
    
    def forward(self, hypothesis_text: str) -> Dict:
        """
        Check if hypothesis domain is covered by KB.
        Returns: {
            'in_scope': bool,
            'domain': str or None,
            'flag': str or None
        }
        """
        ...
    
    def extract_domain_keywords(self, text: str) -> Set[str]:
        """
        Extract domain-specific keywords using TF-IDF.
        Returns: Top-5 keywords as set
        """
        ...
    
    def keyword_similarity(self, query_keywords: Set[str], domain_keywords: Set[str]) -> float:
        """
        Compute Jaccard similarity.
        Returns: similarity score [0, 1]
        """
        ...
```

### Tensor Shapes

**Not applicable** - Rule-based system (no tensors)

### Pseudo-code

```
__init__(kb_domains, similarity_threshold):
    1. self.kb_domains = kb_domains
    2. self.threshold = similarity_threshold
    3. self.domain_embeddings = _build_domain_embeddings()
    4. self.tfidf = TfidfVectorizer(max_features=100, stop_words='english')

_build_domain_embeddings():
    1. embeddings = {}
    2. For each domain in kb_domains:
        - embeddings[domain.name] = set(domain.keywords)
    3. Return embeddings

forward(hypothesis_text):
    1. query_keywords = extract_domain_keywords(hypothesis_text)
    2. similarities = []
    3. For each (domain_name, domain_keywords) in domain_embeddings:
        - sim = keyword_similarity(query_keywords, domain_keywords)
        - similarities.append((domain_name, sim))
    4. best_domain, max_sim = max(similarities, key=lambda x: x[1])
    5. IF max_sim < threshold:
        - Return {'in_scope': False, 'domain': None, 'flag': 'BOUNDARY: Domain outside KB coverage'}
    6. ELSE:
        - Return {'in_scope': True, 'domain': best_domain, 'flag': None}

extract_domain_keywords(text):
    1. Tokenize text (lowercase, remove punctuation)
    2. Fit TF-IDF on text
    3. Get top-5 tokens by TF-IDF score
    4. Filter domain-specific terms (ML vocabulary)
    5. Return set(keywords)

keyword_similarity(query_keywords, domain_keywords):
    1. intersection = query_keywords & domain_keywords
    2. union = query_keywords | domain_keywords
    3. IF len(union) == 0:
        - Return 0.0
    4. Return len(intersection) / len(union)  # Jaccard similarity
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | TF-IDF keyword extraction | Domain keyword extraction with TF-IDF |
| L-1-2 | Jaccard similarity computation | Keyword set similarity scorer |
| L-1-3 | Threshold-based classification | in_scope decision logic |

---

## Epic 2: ExtendedConstraintVerifier [Complexity: 5, Budget: 1/1]

**Applied**: Pre-filtering pattern (Archon KB)

### API Signatures

```python
from typing import Dict, Tuple

class ExtendedConstraintVerifier:
    def __init__(self, kb_path: str, boundary_detector: DomainBoundaryDetector):
        """
        Args:
            kb_path: Path to h-m1 KB YAML
            boundary_detector: Domain boundary checker
        """
        self.kb = self._load_kb(kb_path)
        self.boundary_detector = boundary_detector
        self.base_verifier = ConstraintVerifier(self.kb)  # From h-m4
    
    def check_testability(self, hypothesis: Dict) -> Dict:
        """
        Pre-filter boundaries, then run (D,B,M) check.
        Returns: {
            'testable': bool,
            'reason': str,
            'flag': str or None
        }
        """
        ...
    
    def _load_kb(self, kb_path: str) -> Dict:
        """Load KB from YAML. Returns: {metadata, triples}."""
        ...
```

### Pseudo-code

```
__init__(kb_path, boundary_detector):
    1. self.kb = _load_kb(kb_path)
    2. self.boundary_detector = boundary_detector
    3. self.base_verifier = ConstraintVerifier(self.kb)  # From h-m4

check_testability(hypothesis):
    1. boundary_check = boundary_detector.forward(hypothesis['text'])
    2. IF NOT boundary_check['in_scope']:
        - Return {
            'testable': False,
            'reason': 'domain_not_covered',
            'flag': boundary_check['flag']
          }
    3. ELSE:
        - Return base_verifier.check_dbm_existence(hypothesis, boundary_check['domain'])

_load_kb(kb_path):
    1. Load YAML file
    2. Parse metadata + triples
    3. Return {metadata, triples}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Integration wrapper | Boundary check + h-m4 verifier integration |

---

## Epic 4: BoundaryEvaluator [Complexity: 7, Budget: 2/2]

**Applied**: Classification metrics pattern (Archon KB)

### API Signatures

```python
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

class BoundaryEvaluator:
    def __init__(self, gate_threshold: float = 0.80):
        """gate_threshold: Minimum accuracy for SHOULD_WORK gate."""
        self.gate_threshold = gate_threshold
    
    def evaluate_boundary_detection(self, predictions: List[str], ground_truth: List[str]) -> Dict:
        """
        Compute accuracy, precision, recall, F1.
        Returns: {accuracy, precision, recall, f1, gate_passed}
        """
        ...
    
    def run_threshold_tuning(self, detector: DomainBoundaryDetector, validation_set: List[Dict], thresholds: List[float]) -> Tuple[float, Dict]:
        """
        Grid search for optimal similarity threshold.
        Returns: (best_threshold, sensitivity_curve_data)
        """
        ...
```

### Pseudo-code

```
__init__(gate_threshold):
    1. self.gate_threshold = gate_threshold

evaluate_boundary_detection(predictions, ground_truth):
    1. accuracy = accuracy_score(ground_truth, predictions)
    2. precision = precision_score(ground_truth, predictions, pos_label='boundary')
    3. recall = recall_score(ground_truth, predictions, pos_label='boundary')
    4. f1 = f1_score(ground_truth, predictions, pos_label='boundary')
    5. gate_passed = (accuracy >= gate_threshold)
    6. Return {accuracy, precision, recall, f1, gate_passed}

run_threshold_tuning(detector, validation_set, thresholds):
    1. results = []
    2. For each threshold in thresholds:
        - detector.threshold = threshold
        - predictions = [detector.forward(h['text'])['in_scope'] for h in validation_set]
        - ground_truth = [h['expected'] for h in validation_set]
        - metrics = evaluate_boundary_detection(predictions, ground_truth)
        - results.append({threshold, metrics})
    3. best = max(results, key=lambda x: x['f1'])
    4. Return (best.threshold, results)  # sensitivity curve data
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Metrics computation | sklearn classification metrics wrapper |
| L-4-2 | Threshold tuning | Grid search + 5-fold CV logic |

---

## Epic 5: Threshold Tuning (Optional) [Complexity: 5, Budget: 1/1]

**Applied**: Grid search pattern (Archon KB)

Implemented in `BoundaryEvaluator.run_threshold_tuning()` (see Epic 4).

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Cross-validation loop | 5-fold CV for threshold selection |

---

## Epic 7: Pipeline Orchestration [Complexity: 4, Budget: 1/1]

**Applied**: Experiment pipeline pattern (Archon KB)

### API Signatures

```python
def run_pipeline(config: Dict) -> Dict:
    """
    Execute boundary detection experiment.
    Args:
        config: {paths, thresholds, seeds, gate_threshold}
    Returns:
        {accuracy, precision, recall, gate_passed, figures_saved}
    """
    ...

def run_baseline(test_cases: List[Dict], verifier: ConstraintVerifier) -> List[str]:
    """
    Run h-m4 verifier WITHOUT boundary check.
    Returns: List of classifications
    """
    ...

def run_proposed(test_cases: List[Dict], verifier: ExtendedConstraintVerifier) -> List[str]:
    """
    Run extended verifier WITH boundary check.
    Returns: List of classifications
    """
    ...
```

### Pseudo-code

```
run_pipeline(config):
    1. Load data:
        - boundary_cases = load_json(config['boundary_test_path'])
        - kb_domains = load_domain_taxonomy(config['kb_path'])
    2. Initialize modules:
        - boundary_detector = DomainBoundaryDetector(kb_domains, threshold=config['threshold'])
        - verifier = ExtendedConstraintVerifier(config['kb_path'], boundary_detector)
        - evaluator = BoundaryEvaluator(gate_threshold=config['gate_threshold'])
        - visualizer = Visualizer(config['figures_dir'])
    3. Run baseline:
        - baseline_results = run_baseline(boundary_cases, verifier.base_verifier)
        - baseline_metrics = evaluator.evaluate_boundary_detection(baseline_results, ground_truth)
    4. Run proposed:
        - proposed_results = run_proposed(boundary_cases, verifier)
        - proposed_metrics = evaluator.evaluate_boundary_detection(proposed_results, ground_truth)
    5. Visualize:
        - visualizer.plot_gate_comparison(baseline_metrics, proposed_metrics, threshold)
        - visualizer.plot_confusion_matrix(ground_truth, proposed_results)
    6. Return proposed_metrics

run_baseline(test_cases, verifier):
    1. predictions = []
    2. For each case in test_cases:
        - result = verifier.check_testability(case)
        - predictions.append(result['testable'])
    3. Return predictions

run_proposed(test_cases, verifier):
    1. predictions = []
    2. For each case in test_cases:
        - result = verifier.check_testability(case)
        - predictions.append(result['testable'])
    3. Return predictions
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Pipeline orchestration | Load → baseline → proposed → evaluate → visualize |

---

## External Dependencies API (Base Hypotheses)

### API Signatures (From Actual Code)

```python
# From: h-m4/src/verifier.py (ACTUAL CODE)
class ConstraintVerifier:
    def __init__(self, kb: Dict):
        """kb: Loaded KB from _load_kb()."""
        self.kb = kb
    
    def check_dbm_existence(self, hypothesis: Dict, domain: str) -> Dict:
        """
        Check if (D,B,M) triple exists in KB.
        Returns: {
            'testable': bool,
            'reason': str
        }
        """
        ...
    
    def _load_kb(kb_path: str) -> Dict:
        """
        Load KB from YAML file.
        Returns: {metadata, triples}
        """
        ...
```

**KB Structure** (h-m1/data/pwc_cache/kb.yaml):
```yaml
metadata:
  triple_count: 49
  domains:
    - name: "vision"
      keywords: ["image", "CNN", "classification"]
    - name: "nlp"
      keywords: ["text", "BERT", "tokenizer"]
triples:
  - dataset: "CIFAR-10"
    benchmark: "image-classification"
    metric: "Accuracy"
```

**Verified from**: h-m4/src/verifier.py actual implementation

---

## Remaining Modules (Standard Python, No Subtask Allocation)

### Visualizer (src/visualizer.py)

**Applied**: Matplotlib figure generation pattern

```python
import matplotlib.pyplot as plt
import seaborn as sns

class Visualizer:
    def __init__(self, output_dir: str):
        """output_dir: h-c1/figures/"""
        self.output_dir = output_dir
    
    def plot_gate_comparison(self, baseline_metrics: Dict, proposed_metrics: Dict, threshold: float) -> str:
        """Gate metrics bar chart. Returns: saved file path."""
        ...
    
    def plot_confusion_matrix(self, y_true: List, y_pred: List) -> str:
        """Confusion matrix heatmap. Returns: saved file path."""
        ...
    
    def plot_threshold_sensitivity(self, sensitivity_data: List[Dict]) -> str:
        """Precision/Recall vs threshold curve. Returns: saved file path."""
        ...
    
    def plot_domain_coverage_heatmap(self, test_cases: List, kb_domains: List, similarity_matrix: np.ndarray) -> str:
        """Test cases × KB domains heatmap. Returns: saved file path."""
        ...
```

---

## Total Subtasks: 8/8 allocated

| Epic | Subtasks Used |
|------|---------------|
| Epic 1 (Boundary Detector) | 3 |
| Epic 2 (Verifier Integration) | 1 |
| Epic 4 (Evaluator) | 2 |
| Epic 5 (Threshold Tuning) | 1 |
| Epic 7 (Pipeline) | 1 |
| **Total** | **8** |

---

*Applied Archon KB patterns: OOD detection, classification metrics, grid search*
*Reused components: h-m4 ConstraintVerifier (check_dbm_existence, _load_kb)*
*Codebase analysis completed (h-m4/src/verifier.py verified)*
