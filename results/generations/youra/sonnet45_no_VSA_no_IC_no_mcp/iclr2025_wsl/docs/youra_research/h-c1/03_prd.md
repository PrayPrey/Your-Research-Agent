# Product Requirements Document: Domain Boundary Detection

**Hypothesis:** h-c1  
**Date:** 2026-08-25  
**Version:** 1.0  
**Author:** Anonymous  

---

## Executive Summary

Build domain boundary detection module for hypothesis testability verification system. Extends validated constraint verifier (h-m1 through h-m4) with explicit out-of-scope domain detection. System must correctly flag hypotheses from novel/emerging domains (no KB coverage) as "not testable" before (D,B,M) existence check.

**Validation Gate:** SHOULD_WORK (explore alternatives on failure)  
**Success Criteria:** ≥80% accuracy on boundary test set (8/10 cases flagged correctly)

---

## Problem Statement

### Current Limitation

Validated constraint verifier (h-m4: 90% success on in-scope hypotheses) has no explicit domain coverage check. System attempts (D,B,M) verification even for out-of-scope domains, causing:
- False positives: Classifying untestable (boundary) hypotheses as testable
- No user feedback about domain limitations

### Business Impact

Research pipeline requires accurate boundary detection to:
- Route out-of-scope hypotheses for manual review
- Provide actionable feedback ("KB lacks coverage for domain X")
- Prevent wasted effort on infeasible experiments

### Target Outcome

Domain-aware testability classifier:
- Pre-filters boundary cases before (D,B,M) check
- ≥80% recall on novel/emerging domain detection
- ≥75% precision (minimize false alarms on in-scope cases)

---

## Functional Requirements

### FR-1: Domain Boundary Detector Module

**Priority:** P0 (Core hypothesis validation)

Implement `DomainBoundaryDetector` class:

```python
class DomainBoundaryDetector:
    def __init__(self, kb_domains, similarity_threshold=0.7):
        # Build domain embeddings from KB taxonomy
        
    def forward(self, hypothesis_text):
        # Extract domain keywords → compute similarity to KB domains
        # Return: {'in_scope': bool, 'domain': str, 'flag': str}
```

**Inputs:**
- `hypothesis_text` (str): Hypothesis statement
- `kb_domains` (list): Covered domain taxonomy from KB

**Outputs:**
- `in_scope` (bool): True if domain covered, False otherwise
- `domain` (str | None): Matched KB domain or None
- `flag` (str): Error message for boundary cases

**Acceptance:**
- Keyword similarity < 0.7 → flag as "BOUNDARY: Domain outside KB coverage"
- Return domain match for in-scope cases

---

### FR-2: Integrate with Constraint Verifier

**Priority:** P0 (Integration requirement)

Modify `ConstraintVerifier.check_testability()`:

```python
def check_testability(self, hypothesis):
    # NEW: Pre-filter domain boundaries
    boundary_check = self.boundary_detector.forward(hypothesis.text)
    
    if not boundary_check['in_scope']:
        return {
            'testable': False,
            'reason': 'domain_not_covered',
            'flag': boundary_check['flag']
        }
    
    # EXISTING: (D,B,M) existence check
    return self._check_dbm_existence(hypothesis, boundary_check['domain'])
```

**Acceptance:**
- Boundary cases flagged before (D,B,M) lookup
- In-scope cases proceed to normal verification

---

### FR-3: Domain Taxonomy Loader

**Priority:** P0 (Data requirement)

Load KB domain coverage from Papers With Code catalog:

```python
def load_domain_taxonomy(kb_path):
    # Parse YAML/JSON KB → extract domain list
    # Return: List[Domain(name, keywords)]
```

**Data Source:** `data/pwc_catalog_jan2026.yaml` (from h-m1)

**Acceptance:**
- Extract domain names and keywords from KB
- Support both YAML and JSON formats

---

### FR-4: Keyword Extraction

**Priority:** P0 (Core mechanism)

Implement TF-IDF-based domain keyword extractor:

```python
def extract_domain_keywords(hypothesis_text):
    # TF-IDF with domain-specific term weighting
    # Return: Set[str] - top-k domain keywords
```

**Config:**
- Max keywords: 5
- TF-IDF threshold: 0.1
- Domain term dictionary: ML research vocabulary

**Acceptance:**
- Return 3-5 domain-specific keywords per hypothesis
- Filter generic terms (e.g., "performance", "method")

---

### FR-5: Boundary Test Dataset

**Priority:** P0 (Validation requirement)

Curate 10 boundary hypothesis test cases:

```json
{
  "hypothesis_id": "boundary-001",
  "text": "Olfactory deep learning for scent classification...",
  "domain": "olfactory-ai",
  "expected": "not_testable",
  "reason": "Novel modality without benchmark infrastructure"
}
```

**Domains:**
- Novel modalities: Olfactory AI, Haptic DL, Gustatory classification
- Emerging apps: Quantum ML, Neuromorphic computing

**Save to:** `h-c1/data/boundary_hypotheses.json`

**Acceptance:**
- 10 diverse boundary cases
- Ground truth labels for evaluation

---

### FR-6: Evaluation Script

**Priority:** P0 (Validation requirement)

Compute boundary detection metrics:

```python
from sklearn.metrics import accuracy_score, precision_score, recall_score

def evaluate_boundary_detection(predictions, ground_truth):
    # Compute accuracy, precision, recall, F1
    # Save results to h-c1/04_validation.md
```

**Metrics:**
- Accuracy: (TP + TN) / Total
- Precision: TP / (TP + FP)
- Recall: TP / (TP + FN)
- F1-Score: Harmonic mean

**Acceptance:**
- Compare baseline (no boundary check) vs proposed
- Results table in validation report

---

### FR-7: Threshold Tuning

**Priority:** P1 (Optimization)

Grid search for optimal similarity threshold:

```python
thresholds = [0.5, 0.6, 0.7, 0.8, 0.9]
for t in thresholds:
    detector = DomainBoundaryDetector(kb, threshold=t)
    metrics = evaluate(detector, validation_set)
    # Select threshold maximizing F1
```

**Validation:** 5-fold CV on 50 in-scope + 50 boundary hypotheses

**Acceptance:**
- Report best threshold in 04_validation.md
- Include sensitivity curve figure

---

### FR-8: Visualization

**Priority:** P1 (Required for paper)

Generate figures:
1. **Gate Metrics Bar Chart**: Target vs actual (accuracy, precision, recall)
2. **Confusion Matrix**: Boundary vs in-scope classification
3. **Threshold Sensitivity**: Precision/Recall vs threshold
4. **Domain Coverage Heatmap**: Test cases × KB domains similarity

**Save to:** `h-c1/figures/`

**Acceptance:**
- All figures saved as PNG (300 DPI)
- Titles, axis labels, legends

---

## Non-Functional Requirements

### NFR-1: Performance

- Classification latency: <100ms per hypothesis
- KB loading: <5s

### NFR-2: Code Quality

- Type hints for all functions
- Docstrings (Google style)
- Unit tests for keyword extraction, similarity scoring

### NFR-3: Reproducibility

- Fixed random seed (42)
- Configuration in YAML file
- Dependency versions pinned

---

## Data Specifications

### Input Data

| Dataset | Type | Size | Format | Source |
|---------|------|------|--------|--------|
| Boundary Test Set | Evaluation | 10 cases | JSON | Custom curation |
| KB Domain Taxonomy | Reference | ~100 domains | YAML | PWC catalog (h-m1) |
| Validation Set | Tuning | 100 hyps | JSON | 50 in-scope + 50 boundary |

### Output Data

| Artifact | Format | Location |
|----------|--------|----------|
| Predictions | JSON | h-c1/results/predictions.json |
| Metrics | Markdown | h-c1/04_validation.md |
| Figures | PNG | h-c1/figures/*.png |

---

## Dependencies

### Core Dependencies

```
torch==2.0.0
scikit-learn==1.3.0
pyyaml==6.0
numpy==1.24.0
matplotlib==3.7.0
```

### Reused Components

- **KB Loader**: From h-m1 (`load_knowledge_base()`)
- **Constraint Verifier**: From h-m4 (`ConstraintVerifier` class)

---

## Success Criteria

### Primary Success Criteria (Gate: SHOULD_WORK)

1. **Accuracy ≥80%**: 8/10 boundary cases correctly flagged
2. **Precision ≥75%**: Low false alarm rate on in-scope cases
3. **Recall ≥80%**: Catch boundary cases consistently

### Secondary Criteria

1. Code runs without error
2. `proposed_accuracy > baseline_accuracy` (PoC pass)
3. All figures generated

### Baseline Performance

- Expected baseline (no boundary check): ~50-60% accuracy
- Target improvement: +20-30 percentage points

---

## Out of Scope

- Training neural models (rule-based approach only)
- Multi-language hypotheses (English only)
- Real-time API deployment
- Integration with production systems

---

## Traceability

| Requirement | Phase 2C Source |
|-------------|-----------------|
| FR-1, FR-2 | Mechanism design (lines 260-317) |
| FR-3 | Dataset spec (lines 195-217) |
| FR-4 | GitHub repo B.2 (TF-IDF keyword extraction) |
| FR-5 | Dataset spec (lines 183-217) |
| FR-6, FR-8 | Evaluation spec (lines 332-380) |
| FR-7 | Training protocol (lines 320-330) |

---

## Appendix: Domain Keyword Extraction Logic

**Algorithm:**
1. Tokenize hypothesis text
2. Compute TF-IDF scores for all tokens
3. Filter domain-specific terms (ML vocabulary dictionary)
4. Return top-5 tokens by TF-IDF score

**Example:**
- Input: "Olfactory neural networks for scent recognition using CNNs"
- Keywords: ["olfactory", "scent", "recognition", "CNNs"]
- Match: No KB domain contains "olfactory" → Flag as boundary
