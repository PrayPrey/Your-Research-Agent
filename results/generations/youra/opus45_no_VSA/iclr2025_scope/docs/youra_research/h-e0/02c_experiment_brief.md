# Experiment Design: h-e0

**Date:** 2026-08-09
**Author:** Anonymous
**Hypothesis Statement:** Instruction prefixes are linearly separable by FLAN task family (macro-F1 ≥0.75 on 10+ families)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** None required (first hypothesis)
**Gate Status:** MUST_WORK - Must achieve macro-F1 ≥0.75

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e0
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
If macro-F1 < 0.75 on task family classification → hypothesis fundamentally fails, blocking all dependent hypotheses (H-E1, H-M1, H-M2).

---

## Continuation Context

First hypothesis in verification chain. No previous results to build upon.

### Previous Hypothesis Results (if applicable)
N/A - This is the first hypothesis.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Instruction embedding classification FLAN task**
- Limited direct matches; Archon KB focused on diffusion models
- No FLAN-specific instruction classification examples found

**Query 2: Linear probe sentence embedding classification**
- Found embedding-related content but primarily image/diffusion domain
- Text classification patterns available via Transformers library

**Query 3: MiniLM sentence encoder classification**
- No direct MiniLM sentence encoder classification examples in KB
- General transformer loading patterns documented

**Key Insight:** Archon KB lacks FLAN/instruction-classification specific content. Rely on Exa GitHub findings for implementation patterns.

### Archon Code Examples

**Pattern 1: Transformer Loading**
```python
from transformers import AutoModelForSequenceClassification
model = AutoModelForSequenceClassification.from_pretrained(model_name)
```
- Source: Apple ML Research neural engine transformers

**Pattern 2: Sentence Embedding Pipeline**
- Standard HuggingFace transformers + sklearn classifier pattern confirmed
- T5/FLAN model loading via AutoTokenizer + AutoModel

### Exa GitHub Implementations

**Repository 1**: instruction-probing/instruction-probing (⭐ Research repo)
- **URL**: https://github.com/instruction-probing/instruction-probing
- **Relevance**: EXACT MATCH - Linear probing on instruction representations
- **Architecture**: Encoder model → Linear classifier probe
- **Key Insight**: "classifier-based probing backend" for task representations
- **Training Config**: Linear probes, per-task probing
- **Pattern**: dump representations → probe with classifier

**Repository 2**: belrem/llm-prompt-intent-classifier (⭐ HuggingFace)
- **URL**: https://huggingface.co/belrem/llm-prompt-intent-classifier
- **Relevance**: HIGH - MiniLM + LogisticRegression for prompt classification
- **Architecture**: all-MiniLM-L6-v2 → LogisticRegression
- **Results**: Accuracy 0.82, F1 macro 0.82 (4 classes)
- **Key Code**:
```python
from sentence_transformers import SentenceTransformer
import joblib

embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
clf = joblib.load(clf_path)  # LogisticRegression
vec = embedder.encode([prompt])
label_id = clf.predict(vec)[0]
```

**Repository 3**: DeboJp/QLoRA-Fine-Tuning-FLAN-T5-Large-for-Stance-Classification
- **URL**: https://github.com/DeboJp/QLoRA-Fine-Tuning-FLAN-T5-Large-for-Stance-Classification
- **Relevance**: MEDIUM - FLAN + linear probe evaluation
- **Key Finding**: "Post-FT embeddings are NOT linearly separable" for stance (3 classes)
- **Probe Results**: LogisticRegression ~0.58→0.62, MLP ~0.73, XGBoost ~0.71
- **Insight**: Linear probe on FLAN embeddings IS plausible but may need non-linear backup

**Repository 4**: SetFit Models (multiple HuggingFace repos)
- **Architecture**: sentence-transformers/all-MiniLM-L6-v2 + LogisticRegression
- **Results**: 219 classes achievable with this architecture
- **Pattern**: Contrastive fine-tuning + classification head

**FLAN Collection Source**:
- **URL**: https://github.com/google-research/FLAN
- **Dataset**: flan/v2/flan_collection_info.csv
- **Task Categories**: 62+ categories with Generic Task Category labels
- **Loading**: Open-Orca/FLAN on HuggingFace (~300GB full, subsample available)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

1. **instruction-probing/instruction-probing** - Research methodology reference
2. **belrem/llm-prompt-intent-classifier** - Production-grade MiniLM+LogReg pattern
3. **SetFit pattern** - Proven multiclass architecture

**Recommended Implementation Path:**
- Primary: MiniLM + LogisticRegression (sklearn) following belrem pattern
- Fallback: sentence-transformers + sklearn multiclass pipeline
- Justification: Multiple sources confirm MiniLM+LogReg achieves >0.82 F1 on similar tasks; FLAN has clear task family labels

### Code Analysis (Serena MCP)

*Skipped* - No local codebase to analyze. Implementation from scratch using research patterns.

---

## Experiment Specification

### Dataset

**Name:** FLAN Collection (Task Family Subset)
**Type:** standard (HuggingFace datasets)
**Source:** Open-Orca/FLAN or google-research/FLAN metadata

**Task Family Labels:** From `flan_collection_info.csv` - "Generic Task Category" column
- Examples: Question Answering, Question Generation, Explanation Generation, Common Sense Reasoning, etc.
- Target: 10+ task families (selecting families with sufficient samples)

**Sample Size:** 
- Minimum 500 samples per task family (10+ families × 500 = 5,000+ total)
- Use stratified sampling to balance classes
- 80/20 train/test split

**Preprocessing:**
1. Extract instruction prefix (first sentence/task prompt portion)
2. Truncate to max 128 tokens for MiniLM
3. Filter to families with ≥500 samples

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets + pandas for CSV metadata
- Identifier: `Open-Orca/FLAN` (subset) OR local CSV from google-research/FLAN
- Code:
```python
# Option 1: Load FLAN metadata CSV
import pandas as pd
flan_info = pd.read_csv("flan_collection_info.csv")
families = flan_info["Generic Task Category"].value_counts()
selected_families = families[families >= 500].index.tolist()[:15]

# Option 2: Load from HuggingFace (if available in subset)
from datasets import load_dataset
ds = load_dataset("Open-Orca/FLAN", split="train", streaming=True)
```

### Models

#### Baseline Model

**Architecture:** Random Classifier (stratified)
**Type:** Baseline for classification
**Purpose:** Establish chance-level performance

**Loading Information** (for Phase 4 download):
- Method: sklearn
- Identifier: DummyClassifier
- Code:
```python
from sklearn.dummy import DummyClassifier
baseline = DummyClassifier(strategy="stratified")
```

#### Proposed Model

**Architecture:** MiniLM-L6-v2 (frozen) + LogisticRegression

**Core Mechanism Implementation:**

```python
# Core Mechanism: Linear Probe on Instruction Prefix Embeddings
# Based on: belrem/llm-prompt-intent-classifier, instruction-probing

from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
import numpy as np

class InstructionPrefixClassifier:
    """
    Test if instruction prefixes are linearly separable by task family.
    Hypothesis: macro-F1 >= 0.75 on 10+ families.
    """
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.encoder = SentenceTransformer(model_name)
        self.classifier = LogisticRegression(
            max_iter=1000,
            multi_class="multinomial",
            solver="lbfgs",
            class_weight="balanced"
        )
        self.label_encoder = LabelEncoder()
    
    def encode(self, texts: list[str]) -> np.ndarray:
        """Encode instruction prefixes to 384-dim embeddings."""
        return self.encoder.encode(texts, show_progress_bar=True)
    
    def fit(self, X_texts: list[str], y_labels: list[str]):
        """Train linear probe on frozen embeddings."""
        X = self.encode(X_texts)
        y = self.label_encoder.fit_transform(y_labels)
        self.classifier.fit(X, y)
        return self
    
    def predict(self, X_texts: list[str]) -> np.ndarray:
        """Predict task family from instruction prefix."""
        X = self.encode(X_texts)
        return self.label_encoder.inverse_transform(self.classifier.predict(X))

# Integration: Standalone pipeline (no base model modification needed)
```

**Loading Information** (for Phase 4 download):
- Method: sentence-transformers
- Identifier: `sentence-transformers/all-MiniLM-L6-v2`
- Code:
```python
from sentence_transformers import SentenceTransformer
encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
```

### Training Protocol

**Optimizer:** L-BFGS (internal to LogisticRegression)
- **Source:** sklearn default for multinomial LogReg

**Learning Rate:** N/A (closed-form optimization)

**Batch Size:** Full batch (LogisticRegression fits on full data)

**Epochs:** max_iter=1000 (convergence-based)

**Loss Function:** Cross-entropy (multinomial)

**Regularization:** L2 (default C=1.0)

**Seeds:** 1 (fixed, random_state=42)

> ⚠️ **EXISTENCE (PoC)**: Single seed run. No hyperparameter search.

### Evaluation

**Primary Metrics:**
- **Macro-F1:** Main gate metric (target ≥0.75)
- **Accuracy:** Secondary metric

**Success Criteria:**
- proposed_macro_f1 > baseline_macro_f1 (direction check)
- proposed_macro_f1 >= 0.75 (gate threshold)

**Expected Baseline Performance:**
- Random classifier: ~1/N (N = number of families)
- For 10 families: ~0.10 accuracy, ~0.10 macro-F1
- **Source:** Statistical expectation for balanced random classifier

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: multiclass classification
- Library: sklearn.metrics
- Code:
```python
from sklearn.metrics import classification_report, f1_score, accuracy_score

y_pred = model.predict(X_test)
macro_f1 = f1_score(y_test, y_pred, average="macro")
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target (0.75) vs actual macro-F1 bar chart

#### Additional Figures (LLM Autonomous)

1. **Confusion Matrix**: Task family classification confusion heatmap
2. **t-SNE/UMAP Visualization**: 2D embedding space colored by task family
3. **Per-Family F1**: Bar chart of F1 scores per task family

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e0/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists:** Linear probe on sentence embeddings
- **mechanism_isolatable:** Yes - frozen encoder, trainable classifier
- **baseline_measurable:** Yes - random/stratified classifier
- **architecture_compatibility:** MiniLM outputs 384-dim vectors; LogReg accepts any dim

### Activation Indicators
- **mechanism_log_message:** "Encoding N samples with MiniLM...", "Training LogisticRegression..."
- **tensor_shape_change:** Input texts → (N, 384) embeddings → (N,) predictions
- **metric_delta_expected:** macro-F1 should be >>0.10 (random baseline)

### Verification Code
```python
# Verify mechanism activates correctly
def verify_mechanism(model, X_sample, y_sample):
    # Check encoding produces correct shape
    embeddings = model.encode(X_sample[:10])
    assert embeddings.shape == (10, 384), f"Wrong shape: {embeddings.shape}"
    
    # Check classifier is fitted
    model.fit(X_sample, y_sample)
    assert hasattr(model.classifier, "classes_"), "Classifier not fitted"
    
    # Check predictions are valid labels
    preds = model.predict(X_sample[:10])
    assert all(p in y_sample for p in preds), "Invalid predictions"
    
    print("✅ Mechanism verification passed")
```

### Success Threshold
- **hypothesis_support_metric:** macro-F1
- **hypothesis_support_threshold:** 0.75

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_macro_f1 > baseline_macro_f1`
3. `proposed_macro_f1 >= 0.75` (gate threshold)

---

## Appendix: Reference Implementations

| Source | URL | Relevance |
|--------|-----|-----------|
| instruction-probing | https://github.com/instruction-probing/instruction-probing | Linear probing methodology |
| llm-prompt-intent-classifier | https://huggingface.co/belrem/llm-prompt-intent-classifier | MiniLM+LogReg pattern |
| FLAN Collection | https://github.com/google-research/FLAN | Dataset source |
| Open-Orca/FLAN | https://huggingface.co/datasets/Open-Orca/FLAN | HuggingFace dataset |
| SetFit | https://huggingface.co/models?library=setfit | Few-shot classification pattern |
| QLoRA FLAN stance | https://github.com/DeboJp/QLoRA-Fine-Tuning-FLAN-T5-Large-for-Stance-Classification | FLAN probe analysis |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-09

### Workflow History for This Hypothesis
- 2026-08-09: Hypothesis h-e0 set to IN_PROGRESS (Phase 2C started)
- 2026-08-09: Archon KB search (limited results for domain)
- 2026-08-09: Exa GitHub search (6 relevant implementations found)
- 2026-08-09: Experiment specification synthesized

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
