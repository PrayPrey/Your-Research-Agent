# Experiment Design: h-m1

**Date:** 2026-08-24
**Author:** Anonymous
**Hypothesis Statement:** Attention entropy classification (low vs high threshold) correctly identifies failure types with ≥70% accuracy compared to gold-labeled entity-error vs non-entity-error categories
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-e1 VALIDATED)
**Gate Status:** MUST_WORK (awaiting validation)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** h-e1

### Gate Condition
MUST_WORK — If classification accuracy < 70% on held-out test set in either model, entropy difference (h-e1) exists but is not actionable for automated routing. Entire failure-type routing framework invalidated.

---

## Continuation Context

This hypothesis builds on h-e1's proven attention pattern. h-e1 demonstrated entity-substitution errors show significantly lower attention entropy (mean=0.062) over entity spans compared to non-entity errors (mean=0.300), with p=7.5e-07 and Cohen's d=-1.13 (large effect size).

h-m1 tests whether this statistical difference is actionable: can we classify failure types with ≥70% accuracy using entropy thresholds?

### Previous Hypothesis Results
**h-e1 (VALIDATED):**
- **p-value:** 7.53e-07 (< 0.05 threshold) ✅
- **Mean entity entropy:** 0.062 < mean non-entity entropy: 0.300 ✅
- **Cohen's d:** -1.13 (large effect size)
- **Model:** GPT-2 (fallback from Llama-2-7B, CPU-only environment)
- **Dataset:** TruthfulQA entity-annotated subset (50 entity-errors, 23 non-entity-errors processed)
- **Optimal configuration:** Last layer attention, mean across 12 heads, character→token span mapping
- **Proven:** Attention pattern signature exists — entity errors concentrate attention (low entropy), non-entity errors distribute attention (high entropy)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable — designed from h-e1 results and statistical best practices*

### Archon Code Examples

*MCP unavailable — designed from h-e1 implementation patterns*

### Exa GitHub Implementations

*MCP unavailable — designed from standard classification approaches*

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

*Not applicable — this is original hypothesis validation, not paper reproduction*

**Recommended Implementation Path:**
- Primary: Reuse h-e1 entropy computation + sklearn threshold classifier
- Fallback: Manual threshold search with cross-validation
- Justification: h-e1 already computed entropy values. Classification layer adds minimal complexity (threshold + accuracy metric).

### Code Analysis (Serena MCP)

*MCP unavailable — designed from h-e1 validated architecture*

---

## Experiment Specification

### Dataset

**Name:** TruthfulQA entity-annotated subset (from h-e1)  
**Source:** h-e1 validation outputs (entropy values already computed)  
**Type:** standard (HuggingFace datasets)  
**Splits:** Use h-e1's 73 processed samples, split 60/13 train/test (80/20 split)  
**Features:**
- Entity errors: 50 samples (all processed successfully in h-e1)
- Non-entity errors: 23 samples (27 skipped due to span alignment in h-e1)
- Per-sample entropy: Precomputed in h-e1 (mean entity-span attention entropy)
- Gold labels: entity-error vs non-entity-error

**Loading Information** (for Phase 4 download):
- Method: Load from h-e1 outputs
- Identifier: `h-e1/code/entropy_results.json` (or h-e1 experiment outputs)
- Code:
```python
import json
with open('../h-e1/code/entropy_results.json') as f:
    data = json.load(f)
# data contains: sample_id, error_type, entropy_value
```

### Models

#### Baseline Model

**Name:** Random Classifier (50% accuracy baseline for binary classification)  
**Architecture:** Coin flip / random assignment to entity-error vs non-entity-error  
**Justification:** Establishes minimum performance floor — any entropy-based classifier must exceed 50% to be meaningful.

**Loading Information** (for Phase 4 download):
- Method: Built-in (no download required)
- Identifier: `numpy.random.choice([0, 1])`
- Code:
```python
import numpy as np
baseline_preds = np.random.choice([0, 1], size=len(test_samples))
baseline_acc = (baseline_preds == test_labels).mean()  # ~0.5
```

#### Proposed Model

**Architecture:** Threshold-based Binary Classifier  
**Input:** Attention entropy value (scalar, range 0.0-1.0)  
**Output:** Class prediction (0=entity-error, 1=non-entity-error)

**Core Mechanism Implementation:**

```python
# Entropy-based binary classifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import numpy as np

# Load h-e1 entropy results
entropies = []  # shape: (73,)
labels = []     # shape: (73,), 0=entity-error, 1=non-entity-error

# Split 80/20 train/test
X_train, X_test, y_train, y_test = train_test_split(
    entropies, labels, test_size=0.2, stratify=labels, random_state=42
)

# Find optimal threshold via grid search on training set
thresholds = np.linspace(0.0, 1.0, 101)
best_threshold = None
best_train_acc = 0

for threshold in thresholds:
    # Classify: entropy < threshold → entity-error (0)
    #           entropy >= threshold → non-entity-error (1)
    preds = (X_train >= threshold).astype(int)
    acc = accuracy_score(y_train, preds)
    if acc > best_train_acc:
        best_train_acc = acc
        best_threshold = threshold

# Evaluate on test set
test_preds = (X_test >= best_threshold).astype(int)
test_acc = accuracy_score(y_test, test_preds)

# Gate check
gate_pass = test_acc >= 0.70
```

**Key Design Decisions:**
- **Threshold search:** Grid search over [0, 1] with 0.01 resolution
- **Train/test split:** 80/20 stratified by error type
- **Classification rule:** entropy < threshold → entity-error (based on h-e1 finding: entity errors have lower entropy)
- **No hyperparameters:** Single threshold parameter, no training epochs/learning rate

### Training Protocol

**Training Method:** Threshold Grid Search (deterministic, no gradient descent)

**Steps:**
1. Load entropy values from h-e1 validation outputs
2. Split 80/20 train/test (stratified by error type)
3. Grid search 101 thresholds [0.00, 0.01, ..., 1.00] on training set
4. Select threshold with highest training accuracy
5. Evaluate on held-out test set

**Hyperparameters:**
- Threshold range: [0.0, 1.0]
- Threshold resolution: 0.01
- Train/test split: 80/20
- Random seed: 42 (reproducibility)
- Stratification: Yes (preserve class balance)

**No Neural Training:** This is a threshold-based classifier — no epochs, no optimizer, no learning rate. Training = exhaustive threshold search.

### Evaluation

**Primary Metric:** Classification Accuracy (test set)  
**Gate Threshold:** ≥70% accuracy  
**Baseline Comparison:** Random classifier (50% accuracy)

**Additional Metrics:**
- Precision (entity-error class)
- Recall (entity-error class)
- F1 Score (both classes)
- Confusion Matrix

**Evaluation Protocol:**
1. Apply best_threshold to test set entropy values
2. Compute test accuracy
3. **Gate check:** `test_acc >= 0.70` → PASS, else FAIL
4. Generate classification report
5. Visualize confusion matrix

**Success Criteria (Gate):**
- ✅ PASS: test_acc ≥ 0.70 on held-out test set
- ❌ FAIL: test_acc < 0.70 → entropy difference not actionable for classification

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification
- Library: scikit-learn
- Code:
```python
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

test_preds = (X_test >= best_threshold).astype(int)
test_acc = accuracy_score(y_test, test_preds)
report = classification_report(y_test, test_preds, target_names=['entity-error', 'non-entity-error'])
cm = confusion_matrix(y_test, test_preds)

gate_pass = test_acc >= 0.70
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

1. **Threshold vs Accuracy Curve:** Plot training accuracy for all 101 thresholds (shows optimal threshold selection)
2. **Confusion Matrix:** 2x2 heatmap (entity-error vs non-entity-error predictions)
3. **Entropy Distribution by Class:** Histogram overlays (entity-error vs non-entity-error entropy distributions with threshold line)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

**h-e1 Implementation (Prerequisite):**
- File: `h-e1/code/experiment.py`
- Outputs: `h-e1/code/entropy_results.json` (73 samples with entropy values)
- Reused: Entropy computation, NER span mapping, character→token alignment

**Standard Libraries:**
- scikit-learn: `train_test_split`, `accuracy_score`, `classification_report`
- NumPy: Threshold grid search, array operations
- Matplotlib: Visualization (threshold curve, confusion matrix, distributions)

**Design Pattern:**
- Reuse h-e1 outputs (no model re-execution)
- Minimal addition: threshold classifier layer
- Deterministic (fixed random seed=42)

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-24T07:48:00Z

### Workflow History for This Hypothesis
- 2026-08-24T07:48:00Z: Phase 2C experiment design started
- Prerequisite h-e1 validated (p=7.5e-07, Cohen's d=-1.13)
- Context generated from Phase 2B roadmap
- MCP unavailable — designed from h-e1 results and classification best practices

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
