# Architecture: h-c1

**Date:** 2026-08-25
**Hypothesis:** Under domain boundary conditions, if a hypothesis is from a domain without established benchmark infrastructure (novel modalities, emerging applications), then the system correctly classifies it as "not testable" (or flags domain limitation), because the KB contains no matching (D,B,M) triples for that domain.
**Type:** CONDITION (boundary detection extension)
**Phase:** Phase 3 - Architecture Design

---

## Codebase Analysis (Serena)

**Project Type**: incremental_extension
**Status**: Extending h-m4 verifier with domain boundary detection module
**Analyzed Path**: h-m4/src/verifier.py (existing constraint verifier to extend)
**Findings**: Reuse h-m4 verifier architecture (keyword extraction + KB lookup). Add pre-filtering step with domain coverage check before (D,B,M) triple verification.

---

## System Overview

**Applied**: Boundary detection pattern (Archon KB - OOD classification)

**Architecture Type**: Evaluation pipeline (rule-based classifier, no training)

**Data Flow**:
```
Boundary Hypotheses → DomainBoundaryDetector → in_scope check → ConstraintVerifier (if in_scope) → Classification + Flag
```

**Components**: 4 modules (boundary detector, constraint verifier from h-m4, evaluator, visualizer)

---

## Module Specifications

### 1. DomainBoundaryDetector (`src/boundary_detector.py`)

**Dependencies**: h-m4 KB loader, sklearn (TF-IDF)

```python
class DomainBoundaryDetector:
    def __init__(self, kb_domains: list, similarity_threshold: float = 0.7):
        self.kb_domains = kb_domains  # From KB taxonomy
        self.threshold = similarity_threshold
        self.domain_embeddings = self._build_domain_embeddings()
    
    def _build_domain_embeddings(self) -> dict:
        """Extract keyword sets for each KB domain."""
        ...
    
    def forward(self, hypothesis_text: str) -> dict:
        """
        Check if hypothesis domain covered by KB.
        Returns: {'in_scope': bool, 'domain': str, 'flag': str}
        """
        ...
    
    def extract_domain_keywords(self, text: str) -> set:
        """TF-IDF-based domain keyword extraction."""
        ...
    
    def keyword_similarity(self, query_keywords: set, domain_keywords: set) -> float:
        """Jaccard similarity between keyword sets."""
        ...
```

**Interface**:
- Input: hypothesis_text (str)
- Output: {'in_scope': bool, 'domain': str or None, 'flag': str or None}
- Method: Keyword extraction → similarity scoring → threshold check

**Complexity**: Medium (text processing + similarity computation)

---

### 2. ExtendedConstraintVerifier (`src/verifier.py`)

**Dependencies**: h-m4 verifier, DomainBoundaryDetector

```python
class ExtendedConstraintVerifier:
    def __init__(self, kb_path: str, boundary_detector: DomainBoundaryDetector):
        self.kb = self._load_kb(kb_path)
        self.boundary_detector = boundary_detector
        self.base_verifier = ConstraintVerifier(self.kb)  # From h-m4
    
    def check_testability(self, hypothesis: dict) -> dict:
        """
        Pre-filter boundaries, then run (D,B,M) check.
        Returns: {'testable': bool, 'reason': str, 'flag': str}
        """
        # NEW: Boundary check first
        boundary_check = self.boundary_detector.forward(hypothesis['text'])
        
        if not boundary_check['in_scope']:
            return {
                'testable': False,
                'reason': 'domain_not_covered',
                'flag': boundary_check['flag']
            }
        
        # EXISTING: (D,B,M) verification
        return self.base_verifier.check_dbm_existence(hypothesis, boundary_check['domain'])
```

**Interface**:
- Input: hypothesis dict
- Output: classification result with flag
- Logic: Boundary check → (D,B,M) check (only if in_scope)

**Complexity**: Low (integration wrapper)

---

### 3. BoundaryEvaluator (`src/evaluator.py`)

**Dependencies**: sklearn.metrics

```python
class BoundaryEvaluator:
    def __init__(self, gate_threshold: float = 0.80):
        self.gate_threshold = gate_threshold
    
    def evaluate_boundary_detection(self, predictions: list, ground_truth: list) -> dict:
        """
        Compute accuracy, precision, recall, F1.
        Returns: {accuracy, precision, recall, f1, gate_passed}
        """
        ...
    
    def run_threshold_tuning(self, detector, validation_set, thresholds):
        """Grid search for optimal similarity threshold."""
        ...
```

**Interface**:
- Input: predictions (list of classifications), ground_truth (expected labels)
- Output: metrics dict + gate status
- Method: sklearn classification metrics

**Complexity**: Low (metric computation)

---

### 4. Visualizer (`src/visualizer.py`)

**Dependencies**: matplotlib, seaborn

```python
class Visualizer:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
    
    def plot_gate_comparison(self, baseline: float, proposed: float, threshold: float):
        """Gate metrics bar chart (target vs actual)."""
        ...
    
    def plot_confusion_matrix(self, y_true, y_pred):
        """Boundary vs in-scope confusion matrix."""
        ...
    
    def plot_threshold_sensitivity(self, thresholds, precision, recall):
        """Precision/Recall vs similarity threshold curve."""
        ...
    
    def plot_domain_coverage_heatmap(self, test_cases, kb_domains, similarity_matrix):
        """Test cases × KB domains similarity heatmap."""
        ...
```

**Interface**:
- Input: metrics, predictions, threshold tuning results
- Output: 4 PNG figures (gate, confusion matrix, sensitivity, heatmap)

**Complexity**: Medium (visualization generation)

---

### 5. ExperimentRunner (`src/main.py`)

**Dependencies**: All above modules

```python
def run_pipeline(config: dict) -> dict:
    """
    Execute boundary detection experiment.
    Returns: {accuracy, precision, recall, gate_passed, figures_saved}
    """
    # Load data
    boundary_cases = load_boundary_test_set(config['data_path'])
    kb_domains = load_domain_taxonomy(config['kb_path'])
    
    # Initialize modules
    boundary_detector = DomainBoundaryDetector(kb_domains, threshold=config['threshold'])
    verifier = ExtendedConstraintVerifier(config['kb_path'], boundary_detector)
    evaluator = BoundaryEvaluator(gate_threshold=config['gate_threshold'])
    visualizer = Visualizer(config['output_dir'])
    
    # Run baseline (no boundary check)
    baseline_results = run_baseline(boundary_cases, verifier.base_verifier)
    
    # Run proposed (with boundary check)
    proposed_results = run_proposed(boundary_cases, verifier)
    
    # Evaluate
    metrics = evaluator.evaluate_boundary_detection(proposed_results, ground_truth)
    
    # Visualize
    visualizer.plot_gate_comparison(baseline_metrics, metrics, threshold)
    visualizer.plot_confusion_matrix(ground_truth, proposed_results)
    
    return metrics
```

**Interface**:
- Input: config dict (paths, thresholds, seeds)
- Output: metrics dict + figures saved
- Logic: Load data → baseline → proposed → evaluate → visualize

**Complexity**: Low (orchestration)

---

## External Dependencies (Base Hypotheses)

### Module Paths (From Actual Code)

| Module | Import Strategy | File Location |
|--------|-----------------|---------------|
| ConstraintVerifier | Import class | h-m4/src/verifier.py |
| KB Loader | Copy function | h-m4/src/verifier.py (`_load_kb()`) |
| KB Data | Load YAML file | h-m1/data/pwc_cache/kb.yaml |

**Verified from**: Actual h-m4/src/ code (not specs)

**Note**: Direct import from h-m4 (relative import within docs/youra_research/)

---

## File Structure

```
h-c1/
├── src/
│   ├── boundary_detector.py  # Domain coverage checker (TF-IDF + similarity)
│   ├── verifier.py            # Extended verifier (boundary + (D,B,M) check)
│   ├── evaluator.py           # Metrics computation (accuracy, precision, recall)
│   ├── visualizer.py          # 4 required figures
│   ├── main.py                # Pipeline orchestrator
│   └── config.py              # Fixed parameters (threshold=0.7, seed=42)
├── data/
│   ├── boundary_hypotheses.json      # 10 curated test cases
│   ├── validation_set.json           # 100 hypotheses for threshold tuning
│   ├── kb_domain_taxonomy.json       # Extracted from KB (from h-m1)
│   └── predictions.json              # Baseline + proposed classifications
├── figures/
│   ├── gate_metrics_comparison.png       # Target vs actual (mandatory)
│   ├── confusion_matrix.png              # Boundary vs in-scope
│   ├── threshold_sensitivity_curve.png   # Precision/Recall vs threshold
│   └── domain_coverage_heatmap.png       # Test cases × KB domains similarity
└── config.py              # Threshold=0.7, seed=42, paths
```

---

## Data Specification

### Input Data (External)

**h-m1 Knowledge Base** (kb.yaml):
```yaml
metadata:
  domains:
    - name: "vision"
      keywords: ["image", "CNN", "classification", "detection"]
    - name: "nlp"
      keywords: ["text", "BERT", "tokenizer", "NLP"]
    - name: "rl"
      keywords: ["agent", "reward", "policy", "RL"]
triples:
  - dataset: "CIFAR-10"
    benchmark: "image-classification"
    metric: "Accuracy"
```

**Boundary Test Set** (boundary_hypotheses.json):
```json
[
  {
    "id": "boundary-001",
    "text": "Olfactory neural networks using CNNs improve scent classification accuracy",
    "domain": "olfactory-ai",
    "expected": "not_testable",
    "reason": "Novel modality - no KB coverage for olfactory tasks"
  },
  {
    "id": "boundary-002",
    "text": "Quantum ML models outperform classical on entanglement detection",
    "domain": "quantum-ml",
    "expected": "not_testable",
    "reason": "Emerging application - no standard benchmarks"
  }
]
```

### Generated Data

**Predictions** (baseline vs proposed):
```json
{
  "baseline": [
    {"hypothesis_id": "boundary-001", "classification": "testable", "reason": "no_boundary_check"},
    {"hypothesis_id": "boundary-002", "classification": "testable", "reason": "no_boundary_check"}
  ],
  "proposed": [
    {"hypothesis_id": "boundary-001", "classification": "not_testable", "flag": "BOUNDARY: Domain outside KB coverage"},
    {"hypothesis_id": "boundary-002", "classification": "not_testable", "flag": "BOUNDARY: Domain outside KB coverage"}
  ]
}
```

---

## Execution Flow

**No Training Phase** - Rule-based system only:

1. **Data Preparation** (FR-5)
   - Curate 10 boundary hypothesis test cases (5 novel modality + 5 emerging app)
   - Extract KB domain taxonomy from h-m1 KB (domain names + keywords)
   - Create validation set (100 hypotheses: 50 in-scope, 50 boundary)

2. **Domain Taxonomy Loading** (FR-3)
   - Parse h-m1 KB YAML metadata → domain list
   - Extract keywords for each domain
   - Build domain embeddings (keyword sets)

3. **Baseline Evaluation** (FR-6)
   - Run h-m4 ConstraintVerifier WITHOUT boundary check
   - Record classifications for 10 test cases
   - Expected: ~50-60% accuracy (false positives on boundary cases)

4. **Proposed Evaluation** (FR-1, FR-2)
   - For each test case:
     - Extract domain keywords (TF-IDF)
     - Compute similarity to all KB domains
     - If max_similarity < threshold (0.7): flag as boundary
     - Else: proceed to (D,B,M) check
   - Record classifications

5. **Threshold Tuning** (FR-7, optional)
   - Grid search on validation set: thresholds [0.5, 0.6, 0.7, 0.8, 0.9]
   - For each threshold: compute precision, recall, F1
   - Select threshold maximizing F1
   - Generate sensitivity curve figure

6. **Metrics Computation** (FR-6)
   - Accuracy: (TP + TN) / Total
   - Precision: TP / (TP + FP)
   - Recall: TP / (TP + FN)
   - F1-Score: 2 * (P * R) / (P + R)
   - Gate check: Accuracy ≥ 0.80

7. **Visualization** (FR-8)
   - Gate metrics comparison (bar chart: baseline vs proposed)
   - Confusion matrix (2×2 heatmap)
   - Threshold sensitivity curve (line plot)
   - Domain coverage heatmap (test cases × KB domains)

---

## Proposed Tasks (Epic Level)

### Epic 1: Domain Boundary Detector Implementation
**Complexity**: 8 (Module: 3 + Dependencies: 1 + Algorithm: 3 + Integration: 1)
- Implement `DomainBoundaryDetector` class
- TF-IDF keyword extraction
- Jaccard similarity computation
- Threshold-based classification logic

**Subtasks**: Keyword extraction, Similarity scoring, Threshold logic

---

### Epic 2: Constraint Verifier Integration
**Complexity**: 5 (Module: 2 + Dependencies: 1 + Algorithm: 1 + Integration: 1)
- Extend h-m4 `ConstraintVerifier` with boundary pre-filter
- Import h-m4 verifier module
- Integrate boundary check before (D,B,M) lookup

**Subtasks**: Import h-m4 module, Add pre-filter logic, Test integration

---

### Epic 3: Data Preparation
**Complexity**: 6 (Module: 2 + Dependencies: 1 + Algorithm: 2 + Integration: 1)
- Curate 10 boundary test cases (manual)
- Extract domain taxonomy from h-m1 KB
- Generate validation set (100 hypotheses)

**Subtasks**: Curate test cases, Extract KB domains, Generate validation set

---

### Epic 4: Evaluation Pipeline
**Complexity**: 7 (Module: 2 + Dependencies: 1 + Algorithm: 3 + Integration: 1)
- Implement `BoundaryEvaluator` class
- Baseline vs proposed comparison
- sklearn metrics computation (accuracy, precision, recall, F1)

**Subtasks**: Metrics computation, Baseline run, Proposed run

---

### Epic 5: Threshold Tuning (Optional)
**Complexity**: 5 (Module: 1 + Dependencies: 1 + Algorithm: 2 + Integration: 1)
- Grid search over thresholds [0.5-0.9]
- 5-fold CV on validation set
- Select optimal threshold by F1

**Subtasks**: Grid search loop, Cross-validation, Threshold selection

---

### Epic 6: Visualization
**Complexity**: 6 (Module: 2 + Dependencies: 1 + Algorithm: 2 + Integration: 1)
- Implement `Visualizer` class
- Generate 4 required figures (gate, confusion, sensitivity, heatmap)
- Save to h-c1/figures/ (PNG, 300 DPI)

**Subtasks**: Gate comparison plot, Confusion matrix, Sensitivity curve, Heatmap

---

### Epic 7: Pipeline Orchestration
**Complexity**: 4 (Module: 1 + Dependencies: 1 + Algorithm: 1 + Integration: 1)
- Implement `main.py` orchestrator
- Load config, data, KB
- Execute baseline → proposed → evaluate → visualize
- Save results to 04_validation.md

**Subtasks**: Config loading, Pipeline execution, Results saving

---

### Epic 8: Configuration Management
**Complexity**: 3 (Module: 1 + Dependencies: 0 + Algorithm: 1 + Integration: 1)
- Create `config.py` with fixed parameters
- Threshold=0.7, seed=42, paths
- Gate threshold=0.80

**Subtasks**: Config file creation, Parameter validation

---

## Infrastructure Level: FULL

**Configuration**: YAML config file with dataclasses
**Logging**: Print statements + CSV results
**Testing**: Unit tests for keyword extraction and similarity scoring

---

## Complexity Summary

| Epic | Complexity | Type |
|------|-----------|------|
| Epic 1 | 8 | High |
| Epic 2 | 5 | Medium |
| Epic 3 | 6 | Medium |
| Epic 4 | 7 | High |
| Epic 5 | 5 | Medium |
| Epic 6 | 6 | Medium |
| Epic 7 | 4 | Medium |
| Epic 8 | 3 | Low |
| **Total** | **44** | |

**Distribution**: Very High (0), High (2), Medium (5), Low (1)

---

## Gate Verification

**SHOULD_WORK Gate**:
- Primary: Accuracy ≥ 80% on boundary test set
- Secondary: Precision ≥ 75%, Recall ≥ 80%
- PoC: proposed_accuracy > baseline_accuracy

**Expected Performance**:
- Baseline: ~50-60% (no boundary check)
- Proposed: ≥80% (with boundary detector)
- Improvement: +20-30 percentage points

---

*Applied Archon KB patterns: OOD detection, boundary classification*
*Reused components: h-m4 ConstraintVerifier, h-m1 KB*
*Codebase analysis completed (h-m4/src/ verified)*
