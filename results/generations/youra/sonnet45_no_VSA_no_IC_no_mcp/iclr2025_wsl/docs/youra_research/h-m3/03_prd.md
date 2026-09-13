# Product Requirements Document (PRD)
## Confound Pattern Detection System (h-m3)

**Date:** 2026-08-25  
**Version:** 1.0  
**Author:** Anonymous  
**Hypothesis:** h-m3 (MECHANISM)

---

## Executive Summary

### Purpose
Implement a confound pattern detection system that flags hypotheses containing known confounds from literature, targeting precision >40% on labeled confound cases through cross-domain pattern generalization.

### Success Criteria
- **Gate (MUST):** Confound flagging precision >40%
- **PoC (MUST):** Proposed precision > baseline (random ~50%)
- **Secondary:** Recall, accuracy, F1 metrics reported

### Key Constraints
- Rule-based approach (no ML training)
- Literature-sourced pattern database
- 30-hypothesis test set (15 confounded, 15 unconfounded)

---

## Problem Statement

### Current State
h-m2 validates testability classification (FPR=0.0) but does not detect confounds. System answers "can it be tested?" but not "should it be tested?"

### Target State
System flags "technically testable but pragmatically problematic" hypotheses using cross-domain confound patterns (tokenizer-BLEU, resolution-architecture, batch-LR).

### Gap
No confound detection mechanism. Need to implement rule-based pattern matching with literature-sourced confound database.

---

## Functional Requirements

### FR-1: Confound Pattern Database
**Priority:** P0  
**Description:** Populate confound database with literature-verified patterns from 3 domains (NLP, vision, training).

**Acceptance Criteria:**
- Database contains ≥15 confound patterns
- Each pattern has: domain, keywords list, description
- Covers: tokenizer-BLEU (NLP), resolution-architecture (vision), batch-LR (training)

**Data Specification:**
```python
CONFOUND_PATTERNS = {
    "nlp": [
        {"keywords": ["tokenizer", "vocab", "BLEU"], "description": "tokenizer-BLEU confound"},
        {"keywords": ["sequence length", "accuracy"], "description": "length-metric confound"}
    ],
    "vision": [
        {"keywords": ["resolution", "architecture"], "description": "resolution-architecture confound"},
        {"keywords": ["augmentation", "model capacity"], "description": "augmentation-capacity confound"}
    ],
    "training": [
        {"keywords": ["batch size", "learning rate", "LR"], "description": "batch-LR confound"},
        {"keywords": ["optimizer", "weight decay"], "description": "optimizer-regularization confound"}
    ]
}
```

### FR-2: Confound Detection Logic
**Priority:** P0  
**Description:** Implement keyword-based confound detection function.

**Acceptance Criteria:**
- Function `detect_confound(hypothesis_text)` returns ("confounded", pattern_name) or ("unconfounded", None)
- All keywords in pattern must appear in hypothesis text (case-insensitive)
- Cross-domain transfer enabled (NLP patterns apply to vision, etc.)

**Implementation Spec:**
```python
def detect_confound(hypothesis_text):
    text_lower = hypothesis_text.lower()
    for domain, patterns in CONFOUND_PATTERNS.items():
        for pattern in patterns:
            if all(kw.lower() in text_lower for kw in pattern["keywords"]):
                return ("confounded", pattern["description"])
    return ("unconfounded", None)
```

### FR-3: Baseline Comparison (Random Flagging)
**Priority:** P0  
**Description:** Implement random baseline for PoC comparison.

**Acceptance Criteria:**
- Function `baseline_predict(hypothesis_text)` returns random label
- Expected precision ~50% (1/2 chance of correct confounded flag)

**Implementation Spec:**
```python
import random
def baseline_predict(hypothesis_text):
    return random.choice(["confounded", "unconfounded"])
```

### FR-4: Test Dataset Generation
**Priority:** P0  
**Description:** Generate 30-hypothesis test set with ground truth labels.

**Acceptance Criteria:**
- 15 confounded hypotheses (5 NLP, 5 vision, 5 training)
- 15 unconfounded hypotheses (single-variable interventions)
- Each hypothesis has `text` and `label` fields
- Literature sources cited for confounded cases

**Data Structure:**
```python
test_set = [
    {"text": "BPE tokenizer with 50k vocab vs 10k vocab on BLEU", "label": "confounded", "domain": "nlp"},
    {"text": "Increase dropout from 0.1 to 0.5 (all else constant)", "label": "unconfounded", "domain": "training"},
    # ... 28 more
]
```

### FR-5: Evaluation Metrics
**Priority:** P0  
**Description:** Compute precision, recall, accuracy, F1 using sklearn.

**Acceptance Criteria:**
- Precision = TP / (TP + FP)
- Recall = TP / (TP + FN)
- Accuracy = (TP + TN) / 30
- F1 = 2 * (Precision * Recall) / (Precision + Recall)
- Confusion matrix generated

**Implementation Spec:**
```python
from sklearn.metrics import precision_score, recall_score, accuracy_score, confusion_matrix

y_true = [h["label"] for h in test_set]
y_pred_proposed = [detect_confound(h["text"])[0] for h in test_set]
y_pred_baseline = [baseline_predict(h["text"]) for h in test_set]

precision_proposed = precision_score(y_true, y_pred_proposed, pos_label="confounded")
precision_baseline = precision_score(y_true, y_pred_baseline, pos_label="confounded")
```

### FR-6: Visualization
**Priority:** P1  
**Description:** Generate figures for gate metrics, confusion matrix, domain breakdown.

**Acceptance Criteria:**
- Figure 1: Gate Metrics Comparison (bar chart: baseline vs proposed vs threshold)
- Figure 2: Confusion Matrix (heatmap)
- Figure 3: Domain-Specific Performance (precision by NLP/vision/training)
- All figures saved to `h-m3/figures/`

---

## Non-Functional Requirements

### NFR-1: Reproducibility
**Priority:** P0  
**Description:** Fixed random seed for baseline; deterministic pattern matching for proposed.

### NFR-2: Runtime
**Priority:** P1  
**Description:** Detection runs in <1 second for 30-hypothesis test set.

### NFR-3: Code Quality
**Priority:** P1  
**Description:** Type hints, docstrings for public functions, pytest tests for detection logic.

---

## Dependencies

### Prerequisite Hypotheses
- **h-m2:** Provides validated KB structure and testability classification logic
  - Status: PASS (FPR=0.0)
  - Files: h-m2/03_prd.md, 03_architecture.md, 03_logic.md, 03_config.md

### External Libraries
- sklearn (metrics)
- matplotlib/seaborn (visualization)
- pytest (testing)

### Literature Sources
- Salesky et al. (2020) — tokenizer-BLEU confound
- Touvron et al. (2019) — resolution-architecture confound
- Goyal et al. (2017) — batch-LR confound

---

## Success Metrics

### Gate Validation (SHOULD_WORK)
- Precision >40% → PASS
- Precision ≤40% → PIVOT to domain-specific confound DBs

### PoC Validation
- proposed_precision > baseline_precision → PASS
- proposed_precision ≤ baseline_precision → FAIL

### Quality Metrics
- All 30 hypotheses processed without error
- Confusion matrix generated
- Domain breakdown reported

---

## Out of Scope

- Machine learning-based confound detection
- Confound database auto-expansion from unlabeled literature
- Integration with testability classifier (future work)
- Real-time confound detection API

---

## Appendix

### Test Set Examples

**Confounded (NLP):**
1. "BPE tokenizer 50k vocab vs 10k vocab on BLEU score"
2. "Sequence length 128 vs 512 tokens on F1 accuracy"

**Unconfounded (NLP):**
1. "Increase dropout from 0.1 to 0.5 holding architecture constant"
2. "Replace ReLU with GELU activation (no other changes)"

**Confounded (Vision):**
1. "224px resolution with ResNet18 vs 448px with ResNet50"
2. "Augmentation strength with model capacity increase"

**Unconfounded (Vision):**
1. "Test random crop vs center crop (same model)"
2. "Compare Adam vs SGD optimizer (fixed architecture)"

**Confounded (Training):**
1. "Batch size 256 with LR 0.1 vs batch 64 with LR 0.025"
2. "Optimizer change coupled with weight decay adjustment"

**Unconfounded (Training):**
1. "Increase epochs from 10 to 50 (all else fixed)"
2. "Test cosine vs step LR schedule (same optimizer)"

---

## Document Metadata

**Revision History:**
- v1.0 (2026-08-25): Initial PRD from Phase 2C experiment brief

**Stakeholders:**
- Hypothesis Validation Pipeline (gate check consumer)
- Phase 4 Coder (implementation executor)

**Related Documents:**
- h-m3/02c_experiment_brief.md (experiment design)
- h-m2/03_prd.md (prerequisite PRD)
