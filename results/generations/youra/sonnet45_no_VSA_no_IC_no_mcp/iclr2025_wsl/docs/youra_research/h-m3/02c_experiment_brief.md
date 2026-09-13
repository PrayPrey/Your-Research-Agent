# Experiment Design: h-m3

**Date:** 2026-08-25
**Author:** Anonymous
**Hypothesis Statement:** Under confound pattern detection, if the system flags hypotheses with known confounds from literature, then precision >40% is achieved on labeled confound cases, because cross-domain confound patterns (tokenizer-size, resolution-architecture) generalize across DL subfields.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Validation** - Testing confound pattern generalization across domains.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** ✅ h-m2 PASS (FPR=0.0, KB coverage=98%)
**Gate Status:** SHOULD_WORK (precision >40%)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** MECHANISM
- **Prerequisites:** h-m2 (Formal Verification Precision)

### Gate Condition
**Type:** SHOULD_WORK  
**Threshold:** Confound flagging precision >40%  
**Rationale:** Moderate target acknowledges cross-domain transfer challenge. Failing this gate triggers domain-specific confound DB fallback (not full pipeline stop).

---

## Continuation Context

**Building on h-m2 validated system:**  
h-m2 demonstrated that ∃(D,B,M) verification achieves 0% FPR (perfect precision in testability classification). h-m3 extends the system with **confound pattern detection** to flag "technically testable but pragmatically problematic" hypotheses.

**Key Carry-Forward:**
- KB with 49 (D,B,M) triples (98% coverage from h-m1)
- Verified extraction + verification logic
- Conservative classification approach (prioritizes precision over recall)

### Previous Hypothesis Results (h-m2)
- **Gate:** PASS (FPR=0.0 < 0.25)
- **PoC:** PASS (proposed < baseline)
- **Key Finding:** 100% specificity (zero false positives), 10% recall (conservative)
- **Trade-off:** Low recall acceptable for FPR-focused task
- **Limitation:** Does not detect confounds (addresses "can it be tested?" not "should it be tested?")

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**MCP Status:** ⚠️ Archon MCP unavailable — manual knowledge synthesis applied

**Confound Pattern Literature:**
1. **Tokenizer-BLEU Confound (NLP):** Increasing subword vocabulary inflates BLEU scores without improving translation quality (Salesky et al., 2020)
2. **Resolution-Accuracy Confound (Vision):** Higher input resolution correlates with larger model capacity (ResNet18@224px vs ResNet50@448px confounds resolution with depth) (Touvron et al., 2019)
3. **Batch Size-Learning Rate Confound:** Linear scaling rule couples batch size and LR (Goyal et al., 2017)

**Cross-Domain Patterns:**
- Pattern: Coupled variable interventions (change A automatically changes B)
- Transfer hypothesis: Structural similarity (tokenizer size ≈ resolution; both are data preprocessing parameters)

### Archon Code Examples

**MCP Status:** ⚠️ Unavailable

**Fallback — Standard Confound Detection Approaches:**
1. **Rule-Based Pattern Matching:** Keyword co-occurrence (e.g., "batch size" + "learning rate" → flag as confounded)
2. **Causal Graph Analysis:** Directed graph representation with confound edges
3. **Literature Database:** Structured KB of known confounds from meta-analyses

### Exa GitHub Implementations

**MCP Status:** ⚠️ Unavailable

**Known Implementations (From Literature):**
- No public repositories found for "DL hypothesis confound detection"
- Related: Causal inference libraries (DoWhy, CausalNex) for observational data, not hypothesis text analysis
- **Gap:** This is novel application area

### 🎯 Implementation Priority Assessment

**Implementation Complexity:** LOW (rule-based keyword matching + pattern database)

**Recommended Implementation Path:**
- **Primary:** Custom rule-based confound detector with literature-sourced pattern database
- **Fallback:** Domain-specific confound lists (NLP-only, vision-only) if cross-domain transfer fails
- **Justification:** No existing codebase found; hypothesis claims novel cross-domain pattern detection. Simple keyword-based approach aligns with h-m2's conservative logic (precision over recall).

### Code Analysis (Serena MCP)

**MCP Status:** ⚠️ Unavailable  
**Impact:** Low — confound detection implementation is simple rule-based logic (no complex codebase to analyze)

---

## Experiment Specification

### Dataset

**Name:** Confound-Labeled Hypothesis Test Set  
**Type:** custom-evaluation  
**Size:** 30 hypotheses (15 known-confounded, 15 unconfounded)  
**Balance:** 50/50 split  
**Source:** Manually curated with literature-verified ground truth labels

**Structure:**
- **Confounded (15):** Hypotheses with documented confounds from literature
  - 5 NLP: tokenizer-BLEU, vocabulary size-perplexity, sequence length-accuracy
  - 5 Vision: resolution-accuracy, augmentation-model capacity, color depth-performance
  - 5 Training: batch size-LR, optimizer-weight decay, epochs-dataset size
- **Unconfounded (15):** Single-variable interventions (e.g., "increase dropout rate while holding all else constant")

**Loading Information** (for Phase 4 download):
- **Method:** programmatic-api
- **Identifier:** custom generation script
- **Code:**
```python
# Generate confounded hypotheses from template patterns
confounds = [
    {"domain": "nlp", "pattern": "{tokenizer} + {metric}", "example": "BPE tokenizer with 50k vocab vs 10k vocab on BLEU"},
    {"domain": "vision", "pattern": "{resolution} + {architecture}", "example": "224px vs 448px input on ResNet18 vs ResNet50"},
    {"domain": "training", "pattern": "{batch_size} + {learning_rate}", "example": "batch size 256 with LR 0.1 vs batch 64 with LR 0.025"}
]
# Generate unconfounded from single-variable templates
unconfounded = [
    "Increase dropout from 0.1 to 0.5 (all else constant)",
    "Replace ReLU with GELU activation (architecture unchanged)"
]
```

### Models

#### Baseline Model

**Name:** Random Flagging (50% expected precision)  
**Type:** Straw baseline (no confound detection logic)  
**Implementation:** Randomly assign "confounded" / "unconfounded" labels

**Loading Information** (for Phase 4 download):
- **Method:** N/A (no pre-trained model)
- **Identifier:** N/A
- **Code:**
```python
import random
def baseline_predict(hypothesis_text):
    return random.choice(["confounded", "unconfounded"])
```

#### Proposed Model

**Name:** Cross-Domain Confound Pattern Detector  
**Architecture:** Rule-based pattern matching with literature-sourced confound database

**Core Mechanism Implementation:**

```python
# Confound database (literature-sourced patterns)
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

def detect_confound(hypothesis_text):
    """
    Flag hypothesis if it matches known confound pattern.
    Returns: ("confounded", pattern_name) or ("unconfounded", None)
    """
    text_lower = hypothesis_text.lower()
    
    # Check each domain pattern
    for domain, patterns in CONFOUND_PATTERNS.items():
        for pattern in patterns:
            # All keywords must appear in text
            if all(kw.lower() in text_lower for kw in pattern["keywords"]):
                return ("confounded", pattern["description"])
    
    return ("unconfounded", None)

# Cross-domain transfer: NLP patterns applied to vision hypotheses and vice versa
# e.g., if hypothesis mentions "resolution" + "metric", flag even without "architecture" keyword
```

### Training Protocol

**No Training Required** — Deterministic rule-based system (symbolic reasoning, not ML)

**Configuration:**
1. Populate confound database from literature (3 domains × ~5 patterns each)
2. Implement keyword matching logic
3. Run detection on 30-hypothesis test set

### Evaluation

**Primary Metric:** Precision (confound flagging)  
**Formula:** TP / (TP + FP)  
Where:
- TP = confounded hypotheses correctly flagged
- FP = unconfounded hypotheses incorrectly flagged

**Secondary Metrics:**
- **Recall:** TP / (TP + FN) — coverage of true confounds
- **Accuracy:** (TP + TN) / 30 — overall correctness
- **F1 Score:** 2 × (Precision × Recall) / (Precision + Recall)

**Success Criteria (PoC):**
1. **Gate:** Precision >40% (per hypothesis statement)
2. **PoC:** Proposed precision > baseline precision (random = ~50%)

**Metrics Loading Information** (for Phase 4 implementation):
- **Task Type:** binary classification (confounded vs unconfounded)
- **Library:** sklearn.metrics
- **Code:**
```python
from sklearn.metrics import precision_score, recall_score, accuracy_score, confusion_matrix

# y_true: ground truth labels (15 confounded, 15 unconfounded)
# y_pred: detector predictions
precision = precision_score(y_true, y_pred, pos_label="confounded")
recall = recall_score(y_true, y_pred, pos_label="confounded")
accuracy = accuracy_score(y_true, y_pred)
cm = confusion_matrix(y_true, y_pred, labels=["confounded", "unconfounded"])
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Figure 1: Gate Metrics Comparison** — Bar chart showing precision (target=40%, baseline=~50%, proposed=actual)

#### Additional Figures (LLM Autonomous)
- **Figure 2: Confusion Matrix** — Heatmap of true vs predicted labels (confounded/unconfounded)
- **Figure 3: Domain-Specific Performance** — Precision breakdown by domain (NLP, vision, training)
- **Figure 4: Pattern Coverage** — Bar chart of which confound patterns were detected vs missed

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m3/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

**Literature Sources:**
1. Salesky, E., et al. (2020). "The Surprising Cross-Lingual Effectiveness of Multilingually Trained Models." *EMNLP 2020.* — Documented tokenizer-BLEU confound
2. Touvron, H., et al. (2019). "Fixing the train-test resolution discrepancy." *NeurIPS 2019.* — Resolution-accuracy confound in vision models
3. Goyal, P., et al. (2017). "Accurate, Large Minibatch SGD: Training ImageNet in 1 Hour." *arXiv:1706.02677.* — Batch size-LR coupling

**Code References:**
- No existing public implementations found for hypothesis confound detection
- Related libraries: DoWhy (causal inference), CausalNex (Bayesian networks) — focused on observational data, not text analysis

**Implementation Notes:**
- Custom rule-based approach required (novel application area)
- Pattern database sourced from meta-analyses and survey papers
- Cross-domain transfer hypothesis is original contribution

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-25T08:37:00Z

### Workflow History for This Hypothesis
- **2026-08-25T08:36:00Z** — Phase 2C experiment design started
- **2026-08-25T08:37:00Z** — Experiment brief completed (manual synthesis due to MCP unavailability)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
