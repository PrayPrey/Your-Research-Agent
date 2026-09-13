# Experiment Design: H-M1

**Date:** 2026-07-13
**Author:** Anonymous
**Hypothesis Statement:** Under multi-task joint training with L_total = 0.7·L_DPO + 0.3·L_attr, if we compare hidden state representations of joint-trained vs single-objective models, then joint training will produce shared representations that encode both preference quality and attribute information (probing accuracy ≥70% for preferences AND R²≥0.6 for attributes from same hidden states), with representation divergence CKA≤0.7 from DPO-only baseline.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Validates internal workings and representation quality.

---

## Workflow Status

**Verification State:** Phase 2C Experiment Design - IN_PROGRESS
**Prerequisites Satisfied:** H-E1 PASSED (Joint training converged, baseline established)
**Gate Status:** SHOULD_WORK gate - If fails, investigate architecture or loss weighting

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM (Causal Step 1)
- **Prerequisites:** H-E1 (joint training converges)

### Gate Condition
**Type:** SHOULD_WORK  
**Pass Condition:** Probing accuracy ≥70% for preferences, R²≥0.6 for attributes, CKA≤0.7  
**Fail Action:** Investigate architectural bottlenecks or adjust loss weighting

---

## Continuation Context

This is a continuation experiment building on H-E1 (Joint Training Existence & Convergence), which validated that joint DPO + Attribute training is feasible and both objectives can converge simultaneously.

### Previous Hypothesis Results (H-E1)

**Key Results from H-E1:**
- ✓ Training convergence: Both L_DPO and L_attr decreased monotonically (DPO: -5.8%, Attr: -21.3%)
- ✓ Preference win rate: 54.07% (threshold: ≥50%)
- ✓ Attribute steering accuracy: 65.14% (threshold: ≥60%)
- ✓ Gradient angles: Mean 78.5° (threshold: <120°)
- **Model:** GPT-2 XL (1.56B parameters)
- **Dataset:** HH-RLHF (128,800 train / 32,200 test) + OpenAssistant (84,437 train / 4,401 val)
- **Loss weight:** α=0.7 (L_total = 0.7·L_DPO + 0.3·L_attr)

**Reusable Components:**
- Same datasets (proven stable)
- Same model architecture (GPT-2 XL)
- Same loss weighting (α=0.7)
- Trained joint model checkpoint available for representation extraction

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Representation Learning & Probing**
- **Source:** OpenReview forums and instruction-following research
- **Key Insights:**
  - Linear probing is standard for measuring representation quality
  - Hidden states from final transformer layer typically used
  - Probing accuracy ≥70% indicates good representation encoding
  - Multiple probing tasks (preference classification + attribute regression) test multi-dimensional encoding

**Query 2: DPO Representation Analysis**
- **Source:** NVIDIA AlignYourSteps, HuggingFace Diffusers documentation
- **Key Insights:**
  - DPO creates implicit quality representations via preference optimization
  - Representation divergence measured via similarity metrics
  - Joint training can create shared vs specialized representations

**Query 3: CKA Similarity Measurement**
- **Source:** cuBLAS documentation, PyTorch scaled_dot_product_attention
- **Key Insights:**
  - CKA (Centered Kernel Alignment) measures representation similarity
  - CKA ≤0.7 indicates sufficiently divergent representations
  - Used to compare joint-trained vs single-objective model representations

### Archon Code Examples

**Code Source 1: Hidden State Extraction**
- **Query:** Linear probing PyTorch hidden states
- **Example:** T5 encoder model hidden state extraction
  ```python
  outputs = model(input_ids=input_ids)
  last_hidden_states = outputs.last_hidden_state  # (B, seq_len, hidden_dim)
  ```
- **Used For:** Extracting hidden states for probing classifier training

**Code Source 2: Cosine Similarity for Gradients**
- **Example:** AdamW optimizer with cosine schedule
  ```python
  optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate)
  lr_scheduler = get_cosine_schedule_with_warmup(
      optimizer=optimizer,
      num_warmup_steps=config.lr_warmup_steps,
      num_training_steps=(len(train_dataloader) * config.num_epochs),
  )
  ```
- **Used For:** Measuring gradient alignment between L_DPO and L_attr

### Exa GitHub Implementations

**Status:** Exa API quota exceeded (402 error)  
**Fallback:** Used Archon knowledge base findings + H-E1 implementation patterns

**Implementation Pattern from H-E1:**
- Joint model checkpoint available with both objectives trained
- Hidden states extractable from `model.transformer` final layer
- Baseline models (DPO-only, Attr-only) also available for comparison

### 🎯 Implementation Priority Assessment

**CRITICAL: This is a continuation experiment, not paper reproduction**

**Context:** Building on H-E1's validated joint training implementation

**Recommended Implementation Path:**
- **Primary:** Reuse H-E1's trained checkpoints + add probing/CKA analysis
- **Fallback:** Standard PyTorch linear classifier + scikit-learn CKA implementation
- **Justification:** H-E1 already validated joint training; H-M1 adds representation analysis layer

**Implementation Components:**
1. Load H-E1 checkpoints (Joint, DPO-only, Attr-only)
2. Extract hidden states from 500 test examples
3. Train linear probing classifiers (preference + attribute)
4. Compute CKA similarity between representation spaces
5. Measure gradient alignment during training

### Code Analysis (Serena MCP)

*Not required* - Code structure established in H-E1, representation analysis follows standard patterns (linear probing + CKA).

---

## Experiment Specification

### Dataset

**Type:** standard (reused from H-E1)  
**Source:** HuggingFace Datasets

**Primary Dataset:** Anthropic HH-RLHF
- **Size:** 161k preference pairs (128,800 train / 32,200 test, 80/20 split)
- **Purpose:** Preference quality probing (binary classification: chosen vs rejected)
- **Preprocessing:** Tokenization with GPT-2 tokenizer, max_length=256
- **Status:** Already downloaded and cached from H-E1

**Secondary Dataset:** OpenAssistant/oasst1
- **Size:** 88k samples (84,437 train / 4,401 val)
- **Purpose:** Attribute value probing (regression: helpfulness/verbosity/creativity scores)
- **Preprocessing:** Same tokenization as HH-RLHF
- **Status:** Already downloaded and cached from H-E1

**Evaluation Split:** 500 held-out examples from HH-RLHF test set

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Datasets
- Identifier: `Anthropic/hh-rlhf`, `OpenAssistant/oasst1`
- Code: 
  ```python
  from datasets import load_dataset
  hh_rlhf = load_dataset("Anthropic/hh-rlhf")
  oasst = load_dataset("OpenAssistant/oasst1")
  ```

### Models

#### Baseline Models (from H-E1)

**Joint-trained Model:**
- **Architecture:** GPT-2 XL (1.56B parameters)
- **Training:** L_total = 0.7·L_DPO + 0.3·L_attr for 100 steps
- **Status:** Checkpoint available from H-E1 validation
- **Purpose:** Extract hidden states for joint training analysis

**DPO-only Model:**
- **Architecture:** GPT-2 XL (1.56B parameters)
- **Training:** L_DPO only for 100 steps
- **Purpose:** Baseline comparison for CKA similarity

**Attr-only Model:**
- **Architecture:** GPT-2 XL (1.56B parameters)
- **Training:** L_attr only for 100 steps
- **Purpose:** Baseline comparison for CKA similarity

**Loading Information** (for Phase 4):
- Method: Load from H-E1 checkpoint directory
- Identifier: `h-e1/checkpoints/joint_model_final.pt`, `h-e1/checkpoints/dpo_only_final.pt`, `h-e1/checkpoints/attr_only_final.pt`
- Code:
  ```python
  joint_model = torch.load("../h-e1/checkpoints/joint_model_final.pt")
  dpo_model = torch.load("../h-e1/checkpoints/dpo_only_final.pt")
  attr_model = torch.load("../h-e1/checkpoints/attr_only_final.pt")
  ```

#### Proposed Analysis Components

**Architecture:** Representation Analysis Suite

**Core Mechanism Implementation:**

```python
# Representation Analysis for H-M1
# Based on: Standard linear probing + CKA similarity measurement

class RepresentationAnalyzer(nn.Module):
    """
    Analyzes shared representation learning in joint-trained model.
    Tests if joint training creates representations encoding both objectives.
    """
    def __init__(self, hidden_size=1600, num_classes=2, num_attributes=3):
        super().__init__()
        # Probing classifiers (single linear layer)
        self.preference_probe = nn.Linear(hidden_size, num_classes)  # Binary: chosen vs rejected
        self.attribute_probe = nn.Linear(hidden_size, num_attributes)  # Regression: 3 attributes
        
    def extract_hidden_states(self, model, input_ids):
        """
        Extract hidden states from final transformer layer.
        Args:
            model: Trained GPT-2 model (joint/DPO/attr)
            input_ids: (B, seq_len) input tokens
        Returns:
            (B, hidden_size) - mean-pooled hidden states
        """
        with torch.no_grad():
            outputs = model(input_ids, output_hidden_states=True)
            last_hidden = outputs.hidden_states[-1]  # (B, seq_len, hidden_size)
            # Mean pooling over sequence
            hidden_states = last_hidden.mean(dim=1)  # (B, hidden_size)
        return hidden_states
    
    def train_probes(self, hidden_states, preference_labels, attribute_values):
        """
        Train linear probes on frozen hidden states.
        Args:
            hidden_states: (N, hidden_size) - extracted from joint model
            preference_labels: (N,) - binary preference labels
            attribute_values: (N, 3) - attribute scores
        Returns:
            preference_acc: float - probing accuracy for preferences
            attribute_r2: float - R² for attribute regression
        """
        # Preference classification
        pref_logits = self.preference_probe(hidden_states)
        pref_loss = F.cross_entropy(pref_logits, preference_labels)
        pref_acc = (pref_logits.argmax(dim=1) == preference_labels).float().mean()
        
        # Attribute regression
        attr_preds = self.attribute_probe(hidden_states)
        attr_loss = F.mse_loss(attr_preds, attribute_values)
        attr_r2 = r2_score(attribute_values.cpu(), attr_preds.cpu())
        
        return pref_acc.item(), attr_r2
    
def compute_cka_similarity(repr_joint, repr_baseline):
    """
    Compute Centered Kernel Alignment between representation spaces.
    Args:
        repr_joint: (N, hidden_size) - joint model representations
        repr_baseline: (N, hidden_size) - baseline model representations
    Returns:
        cka_score: float - similarity in [0,1], lower is more divergent
    """
    # Centering
    repr_joint = repr_joint - repr_joint.mean(dim=0)
    repr_baseline = repr_baseline - repr_baseline.mean(dim=0)
    
    # Gram matrices
    K_joint = repr_joint @ repr_joint.T
    K_baseline = repr_baseline @ repr_baseline.T
    
    # CKA formula
    hsic = (K_joint * K_baseline).sum()
    var_joint = (K_joint * K_joint).sum()
    var_baseline = (K_baseline * K_baseline).sum()
    
    cka = hsic / torch.sqrt(var_joint * var_baseline)
    return cka.item()

def measure_gradient_alignment(grad_dpo, grad_attr):
    """
    Compute cosine similarity between DPO and Attr gradient vectors.
    Args:
        grad_dpo: Gradient tensor for L_DPO
        grad_attr: Gradient tensor for L_attr
    Returns:
        cosine_sim: float in [-1, 1]
    """
    grad_dpo_flat = torch.cat([g.flatten() for g in grad_dpo])
    grad_attr_flat = torch.cat([g.flatten() for g in grad_attr])
    
    cosine_sim = F.cosine_similarity(
        grad_dpo_flat.unsqueeze(0),
        grad_attr_flat.unsqueeze(0),
        dim=1
    )
    return cosine_sim.item()

# Integration: Load H-E1 checkpoints, extract representations, run analysis
```

### Training Protocol

**Reused from H-E1 (models already trained):**
- **Optimizer:** AdamW - Parameters: lr=1e-5, weight_decay=0.01
- **Batch Size:** 4 (GPU memory constraint with GPT-2 XL)
- **Training Steps:** 100 (PoC scale from H-E1)
- **Loss Weighting:** α=0.7 (L_total = 0.7·L_DPO + 0.3·L_attr)
- **Device:** CUDA (5x NVIDIA H100 NVL)
- **Seeds:** 1 (fixed: 42)

**Rationale:** H-E1 already trained the models; H-M1 analyzes their representations.

**New Analysis Protocol:**
- **Probing Classifier Training:**
  - Optimizer: Adam (lr=1e-3)
  - Epochs: 20 (small classifier, converges quickly)
  - Loss: CrossEntropy (preference), MSE (attributes)
  - Frozen representations: Hidden states from trained models
  
- **Evaluation Set:** 500 held-out examples from HH-RLHF test set

### Evaluation

**Primary Metrics:**

1. **Preference Probing Accuracy**
   - **Definition:** Binary classification accuracy on chosen vs rejected preferences
   - **Threshold:** ≥70%
   - **Computation:** `(predictions == labels).mean()`

2. **Attribute Regression R²**
   - **Definition:** R-squared score for predicting attribute values (helpfulness, verbosity, creativity)
   - **Threshold:** ≥0.6 for all three attributes
   - **Computation:** `sklearn.metrics.r2_score(y_true, y_pred)`

3. **CKA Similarity**
   - **Definition:** Centered Kernel Alignment between Joint and DPO-only representations
   - **Threshold:** ≤0.7 (indicates divergent feature learning)
   - **Computation:** Custom CKA implementation (see pseudo-code)

4. **Gradient Cosine Similarity**
   - **Definition:** Mean cosine similarity between ∇L_DPO and ∇L_attr during training
   - **Threshold:** In range [-0.5, 0.5] (moderate alignment, not conflict)
   - **Computation:** `F.cosine_similarity(grad_dpo, grad_attr)`

**Success Criteria (SHOULD_WORK Gate):**
- Probing accuracy ≥70% for preferences AND
- R²≥0.6 for all attributes AND
- CKA ≤0.7 AND
- Gradient alignment in [-0.5, 0.5]

**Expected Baseline Performance** (from research):
- Random preference probing: ~50%
- Random attribute regression: R²=0
- Identical representations: CKA=1.0

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Representation Analysis (classification + regression + similarity)
- Library: PyTorch (probing), scikit-learn (R²), custom (CKA)
- Code:
  ```python
  from sklearn.metrics import r2_score
  import torch.nn.functional as F
  
  # Preference accuracy
  pref_acc = (pref_preds.argmax(dim=1) == pref_labels).float().mean()
  
  # Attribute R²
  attr_r2 = r2_score(attr_true.cpu(), attr_pred.cpu())
  
  # CKA similarity (custom)
  cka_score = compute_cka_similarity(repr_joint, repr_dpo)
  
  # Gradient alignment
  cosine_sim = F.cosine_similarity(grad_dpo_flat, grad_attr_flat, dim=1)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing target vs actual for all 4 metrics (Probing Acc, Attr R², CKA, Gradient Sim)

#### Additional Figures (LLM Autonomous)

1. **Representation Space t-SNE**
   - Visualize joint vs DPO-only vs attr-only hidden states in 2D
   - Color by preference label + attribute values
   - Shows representation clustering

2. **Probing Learning Curves**
   - Training/validation accuracy for preference probe
   - Training/validation R² for attribute probe
   - Shows convergence of linear probes

3. **Gradient Alignment Histogram**
   - Distribution of cosine similarity values across training steps
   - Shows gradient interaction dynamics

4. **CKA Heatmap**
   - CKA similarity between all model pairs (Joint-DPO, Joint-Attr, DPO-Attr)
   - Shows representation divergence structure

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 Mechanism Validation Check

**SHOULD_WORK Gate Pass Condition:**
1. Code runs without error
2. Probing accuracy ≥70% (demonstrates shared encoding of preferences)
3. Attribute R²≥0.6 (demonstrates shared encoding of attributes)
4. CKA ≤0.7 (demonstrates representation divergence from DPO-only)
5. Gradient alignment in [-0.5, 0.5] (demonstrates moderate multi-task compatibility)

**If Fails:**
- Investigate architectural bottlenecks (hidden size too small?)
- Adjust loss weighting α (try 0.5, 0.9)
- Check probing classifier capacity (add hidden layer?)
- Verify hidden state extraction is from correct layer

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1:** OpenReview - Representation Learning Papers
- **Type:** Knowledge base article
- **Query Used:** "representation learning probing accuracy shared representations"
- **Relevance:** Standard methods for measuring representation quality
- **Key Insights:**
  - Linear probing with single layer is standard
  - ≥70% accuracy indicates good encoding
  - Final transformer layer hidden states typically used
- **Used For:** Probing classifier design, success threshold selection

**Source 2:** NVIDIA AlignYourSteps + HuggingFace Diffusers
- **Type:** Knowledge base documentation
- **Query Used:** "DPO preference optimization representation analysis"
- **Relevance:** DPO creates implicit quality representations
- **Key Insights:**
  - DPO models learn preference-aware representations
  - Joint training can create shared vs specialized features
  - Representation divergence measured via similarity metrics
- **Used For:** CKA threshold selection, understanding joint training dynamics

**Source 3:** cuBLAS/PyTorch Documentation
- **Type:** Technical documentation
- **Query Used:** "CKA kernel alignment representation similarity measurement"
- **Key Insights:**
  - CKA (Centered Kernel Alignment) standard for representation comparison
  - CKA=1.0 means identical, CKA ≤0.7 indicates divergence
  - Requires centering before computing gram matrices
- **Used For:** CKA implementation, divergence threshold

### Archon Code Examples

**Code Source 1:** T5 Encoder Hidden State Extraction
- **Query Used:** "linear probing PyTorch hidden states"
- **Key Code:**
  ```python
  outputs = model(input_ids=input_ids)
  last_hidden_states = outputs.last_hidden_state
  ```
- **Used For:** Hidden state extraction pattern in pseudo-code

**Code Source 2:** AdamW with Cosine Scheduler
- **Query Used:** "representation analysis gradient cosine similarity"
- **Key Code:**
  ```python
  optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate)
  lr_scheduler = get_cosine_schedule_with_warmup(...)
  ```
- **Used For:** Optimizer configuration, gradient alignment measurement pattern

### B. GitHub Implementations (Exa)

**Status:** Exa API quota exceeded (402 error - payment required)

**Fallback:** Used H-E1 implementation patterns + Archon findings

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed - code from H-E1 and Archon examples was sufficiently clear

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report - H-E1
- **File:** `h-e1/04_validation.md`
- **Reused Components:**
  - Dataset: HH-RLHF + OpenAssistant - Proven stable, already downloaded
  - Model: GPT-2 XL - Trained checkpoints available (Joint, DPO-only, Attr-only)
  - Training config: α=0.7, lr=1e-5, batch_size=4, 100 steps
  - Device: 5x NVIDIA H100 NVL
- **Why Reused:** Enables controlled experiment - H-E1 validated training, H-M1 analyzes resulting representations

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Probing classifier design | Archon KB | OpenReview (representation learning) |
| Hidden state extraction | Archon Code | T5 encoder example |
| CKA computation | Archon KB | cuBLAS/PyTorch docs |
| Threshold selection (≥70%, ≥0.6, ≤0.7) | Archon KB | OpenReview + NVIDIA AlignYourSteps |
| Gradient alignment | Archon Code | AdamW cosine scheduler example |
| Dataset (HH-RLHF, OpenAssistant) | Previous (H-E1) | h-e1/04_validation.md |
| Model (GPT-2 XL) | Previous (H-E1) | h-e1/04_validation.md |
| Loss weighting (α=0.7) | Previous (H-E1) | h-e1/04_validation.md |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-07-13

### Workflow History for This Hypothesis

- **2026-07-13 01:01:41:** Hypothesis h-m1 set to IN_PROGRESS (External loop starting Phase 2C → 3 → 4)
- **2026-07-13 [current]:** Phase 2C experiment design in progress
- **Prerequisite:** H-E1 completed (2026-07-13 00:47:39) with PASS result

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
