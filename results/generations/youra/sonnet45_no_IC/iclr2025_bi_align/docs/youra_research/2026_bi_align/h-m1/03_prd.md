# Product Requirements Document (PRD)
## H-M1: Shared Representation Learning

---

**Document Type:** Product Requirements Document (PRD)  
**Hypothesis:** H-M1 (MECHANISM)  
**Created:** 2026-07-13  
**Author:** Anonymous  
**Status:** Draft

---

## Executive Summary

### Purpose
Validate that joint DPO + attribute training produces shared representations encoding both preference quality and attribute information. This mechanism experiment analyzes the internal workings of the joint model validated in H-E1 through representation probing and similarity analysis.

### Hypothesis Statement
Under multi-task joint training with L_total = 0.7·L_DPO + 0.3·L_attr, if we compare hidden state representations of joint-trained vs single-objective models, then joint training will produce shared representations that encode both preference quality and attribute information (probing accuracy ≥70% for preferences AND R²≥0.6 for attributes from same hidden states), with representation divergence CKA≤0.7 from DPO-only baseline.

### Success Criteria (SHOULD_WORK Gate)
1. Probing accuracy ≥70% for preference classification
2. R²≥0.6 for attribute regression from same hidden states
3. CKA similarity ≤0.7 between Joint and DPO-only representations
4. Gradient cosine similarity in range [-0.5, 0.5]

### Expected Outcome
**PASS Condition:** Representation analysis demonstrates shared encoding of both objectives with moderate divergence from baseline, validating the mechanism underlying joint training success.

**FAIL Condition:** Probing accuracy <70% OR attribute R²<0.6 OR CKA >0.7 → Investigate architectural bottlenecks or adjust loss weighting.

---

## Problem Statement

### Research Context
H-E1 validated that joint training converges (54% win rate, 65% steering accuracy). H-M1 investigates **how** this works internally by asking:
- Do hidden states encode both preferences and attributes?
- Are representations shared or specialized?
- What is the representation divergence from single-objective baselines?

### Technical Challenge
Representation analysis risks:
- Low probing accuracy (representations don't encode objectives)
- High CKA similarity (no divergence from baseline, no multi-task benefit)
- Gradient conflict (incompatible objectives)

### Stakeholders
- **Primary:** Research team validating mechanism chain (H-E1 → H-M1 → H-M2 → H-M3)
- **Secondary:** ML researchers studying multi-task representation learning

---

## Functional Requirements

### FR-1: Load Pre-trained Checkpoints
**Priority:** P0 (Critical)  
**Description:** Load trained models from H-E1 for representation extraction

**Acceptance Criteria:**
- Load Joint model checkpoint from h-e1/checkpoints/joint_model_final.pt
- Load DPO-only model checkpoint from h-e1/checkpoints/dpo_only_final.pt
- Load Attr-only model checkpoint from h-e1/checkpoints/attr_only_final.pt
- Verify all models are GPT-2 XL (1.56B parameters)
- Confirm models trained with α=0.7, 100 steps (from H-E1)

**Model Provenance:**
- Source: H-E1 Phase 4 validation
- Training: 100 steps, batch_size=4, lr=1e-5
- Datasets: HH-RLHF (128k train) + OpenAssistant (84k train)

### FR-2: Dataset Preparation for Probing
**Priority:** P0 (Critical)  
**Description:** Prepare evaluation dataset for representation analysis

**Acceptance Criteria:**
- Use 500 held-out examples from HH-RLHF test set
- Extract preference labels (chosen vs rejected: binary classification)
- Extract attribute values (helpfulness, verbosity, creativity: regression targets)
- Tokenize with GPT-2 tokenizer, max_length=256
- Verify dataset matches H-E1 preprocessing

**Data Schema:**
```python
{
    "prompt": str,
    "chosen_response": str,
    "rejected_response": str,
    "preference_label": int (0 or 1),  # 0=rejected, 1=chosen
    "attributes": {
        "helpfulness": float (1.0-5.0),
        "verbosity": float (1.0-5.0),
        "creativity": float (1.0-5.0)
    }
}
```

### FR-3: Hidden State Extraction
**Priority:** P0 (Critical)  
**Description:** Extract hidden states from final transformer layer for all models

**Acceptance Criteria:**
- Extract hidden states from last transformer layer (layer 47 in GPT-2 XL)
- Use mean pooling over sequence dimension: hidden = last_hidden.mean(dim=1)
- Shape: (N=500, hidden_size=1600) per model
- Extract from Joint, DPO-only, Attr-only models
- Freeze models (no gradient computation during extraction)

**Implementation:**
```python
with torch.no_grad():
    outputs = model(input_ids, output_hidden_states=True)
    last_hidden = outputs.hidden_states[-1]  # (B, seq_len, 1600)
    hidden_states = last_hidden.mean(dim=1)  # (B, 1600)
```

### FR-4: Linear Probing - Preference Classification
**Priority:** P0 (Critical)  
**Description:** Train linear classifier to probe preference information in representations

**Acceptance Criteria:**
- Single linear layer: hidden_size (1600) → 2 classes
- Train on frozen hidden states from Joint model
- Optimizer: Adam (lr=1e-3), 20 epochs
- Loss: CrossEntropyLoss
- Measure accuracy on test split (100 examples held-out from 500)
- Threshold: ≥70% accuracy

**Baseline:**
- Random chance: 50%
- H-E1 win rate: 54% (indicates weak preference signal)

### FR-5: Linear Probing - Attribute Regression
**Priority:** P0 (Critical)  
**Description:** Train linear regressor to probe attribute information in representations

**Acceptance Criteria:**
- Single linear layer: hidden_size (1600) → 3 outputs (one per attribute)
- Train on frozen hidden states from Joint model
- Optimizer: Adam (lr=1e-3), 20 epochs
- Loss: MSELoss
- Measure R² score per attribute (helpfulness, verbosity, creativity)
- Threshold: R²≥0.6 for ALL three attributes

**Baseline:**
- Random prediction: R²=0
- Expected: R²≥0.6 (moderate regression quality)

### FR-6: CKA Similarity Computation
**Priority:** P0 (Critical)  
**Description:** Compute Centered Kernel Alignment between representation spaces

**Acceptance Criteria:**
- Compute CKA between Joint and DPO-only representations
- Compute CKA between Joint and Attr-only representations
- Compute CKA between DPO-only and Attr-only (baseline divergence)
- Threshold: CKA(Joint, DPO) ≤0.7 (sufficient divergence)
- Expected: CKA=1.0 means identical, CKA≤0.7 means divergent

**CKA Implementation:**
```python
# Center representations
repr_joint_c = repr_joint - repr_joint.mean(dim=0)
repr_dpo_c = repr_dpo - repr_dpo.mean(dim=0)

# Gram matrices
K_joint = repr_joint_c @ repr_joint_c.T
K_dpo = repr_dpo_c @ repr_dpo_c.T

# CKA formula
hsic = (K_joint * K_dpo).sum()
cka = hsic / torch.sqrt((K_joint**2).sum() * (K_dpo**2).sum())
```

### FR-7: Gradient Alignment Measurement
**Priority:** P1 (High)  
**Description:** Measure gradient compatibility during joint training

**Acceptance Criteria:**
- Extract gradient vectors for L_DPO and L_attr from 10 random training batches
- Compute cosine similarity: cos(θ) = ⟨∇L_DPO, ∇L_attr⟩ / (||∇L_DPO|| · ||∇L_attr||)
- Expected range: [-0.5, 0.5] (moderate alignment, no severe conflict)
- Alert if cosine < -0.8 (strong negative alignment, gradient conflict)

**Interpretation:**
- cos(θ) > 0.5: Gradients aligned (synergistic objectives)
- cos(θ) ∈ [-0.5, 0.5]: Moderate alignment (multi-task compatible)
- cos(θ) < -0.5: Conflicting gradients (objectives interfere)

### FR-8: Visualization Generation
**Priority:** P1 (High)  
**Description:** Generate visualizations for representation analysis

**Required Figures:**

1. **Gate Metrics Comparison** (Mandatory)
   - Bar chart: Target vs Actual for 4 metrics
   - Metrics: Probing Acc (≥70%), Attr R² (≥0.6), CKA (≤0.7), Gradient Sim ([-0.5,0.5])
   - Color: Green if passed, Red if failed

2. **Representation Space t-SNE** (Autonomous)
   - 2D projection of hidden states (500 points)
   - Color by model type (Joint=blue, DPO=red, Attr=green)
   - Shows clustering and divergence

3. **Probing Learning Curves** (Autonomous)
   - Training/validation loss for preference probe (20 epochs)
   - Training/validation R² for attribute probe (20 epochs)
   - Shows convergence quality

4. **CKA Heatmap** (Autonomous)
   - 3×3 matrix: Joint-Joint, Joint-DPO, Joint-Attr, DPO-DPO, DPO-Attr, Attr-Attr
   - Color scale: 0 (divergent) to 1 (identical)

**Output Location:** `{hypothesis_folder}/figures/`

---

## Non-Functional Requirements

### NFR-1: Computational Efficiency
**Priority:** P1 (High)  
**Description:** Minimize redundant computation using cached models

**Acceptance Criteria:**
- Reuse H-E1 trained checkpoints (no re-training)
- Hidden state extraction: <5 minutes for 500 examples
- Probing classifier training: <10 minutes per probe
- CKA computation: <2 minutes for 500×1600 matrices
- Total runtime: <30 minutes (excluding checkpoint loading)

### NFR-2: Reproducibility
**Priority:** P0 (Critical)  
**Description:** Ensure deterministic results

**Acceptance Criteria:**
- Fixed seed: 42 (same as H-E1)
- Deterministic hidden state extraction (torch.no_grad, eval mode)
- Deterministic probing training (torch.manual_seed before each probe)
- Save all intermediate outputs (hidden states, probe weights, CKA matrices)

### NFR-3: Code Reusability
**Priority:** P2 (Medium)  
**Description:** Modular implementation for future mechanism experiments

**Acceptance Criteria:**
- Separate modules: extraction, probing, CKA, visualization
- Class-based design: RepresentationAnalyzer with reusable methods
- Config-driven: hyperparameters in YAML (probe_lr, probe_epochs, cka_threshold)

---

## Success Criteria

### Primary Metrics

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| **Preference Probing Accuracy** | ≥70% | Demonstrates shared encoding of preference quality |
| **Attribute Regression R²** | ≥0.6 (all 3) | Demonstrates shared encoding of attribute info |
| **CKA Similarity (Joint-DPO)** | ≤0.7 | Demonstrates representation divergence |
| **Gradient Alignment** | [-0.5, 0.5] | Demonstrates multi-task compatibility |

### Gate Evaluation

**SHOULD_WORK Gate PASS:**
- All 4 metrics within thresholds
- Code runs without errors
- Visualizations generated successfully

**SHOULD_WORK Gate FAIL:**
- Any metric outside threshold
- **Action:** Investigate architecture (hidden size too small?), adjust loss weighting (try α=0.5 or 0.9), or add probing capacity (2-layer probe)

---

## Dependencies

### Internal Dependencies
- **H-E1 Validation:** MUST be COMPLETED with PASS result
  - Requires: joint_model_final.pt, dpo_only_final.pt, attr_only_final.pt
  - Provides: Trained models for representation extraction

### External Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| PyTorch | ≥2.0.0 | Model loading, hidden state extraction |
| transformers | ≥4.30.0 | GPT-2 model architecture |
| scikit-learn | ≥1.3.0 | R² metric computation |
| matplotlib | ≥3.7.0 | Visualization |
| seaborn | ≥0.12.0 | Heatmap visualization |
| numpy | ≥1.24.0 | Numerical operations |

### Data Dependencies
- **HH-RLHF test set:** 500 held-out examples (already cached from H-E1)
- **OpenAssistant attribute labels:** Already mapped to HH-RLHF in H-E1

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **Low Probing Accuracy** | MEDIUM | HIGH | Add 2-layer probe, increase training epochs to 50 |
| **High CKA (no divergence)** | LOW | MEDIUM | Verify hidden layer extraction (use layer 47, not pooler) |
| **Checkpoint Compatibility** | LOW | CRITICAL | Verify H-E1 checkpoints exist before starting |
| **Gradient Conflict** | LOW | MEDIUM | Re-check H-E1 gradient monitoring logs |

---

## Acceptance Checklist

- [ ] All 3 model checkpoints loaded successfully
- [ ] 500 test examples prepared with labels and attributes
- [ ] Hidden states extracted (shape: 500×1600 per model)
- [ ] Preference probe trained and evaluated (accuracy ≥70%)
- [ ] Attribute probe trained and evaluated (R² ≥0.6 for all 3)
- [ ] CKA computed (Joint-DPO ≤0.7)
- [ ] Gradient alignment measured (cos ∈ [-0.5, 0.5])
- [ ] 4 required figures generated and saved
- [ ] Gate metrics comparison chart shows PASS/FAIL clearly

---

## Appendix

### A. Relationship to Phase 2C
This PRD implements the specification from `02c_experiment_brief.md`:
- **Section "Proposed Analysis Components"** → FR-3, FR-4, FR-5
- **Section "Evaluation Metrics"** → Success Criteria table
- **Section "Training Protocol"** → NFR-1 (reuse H-E1 checkpoints)
- **Section "Visualization Requirements"** → FR-8

### B. Relationship to H-E1
- **Datasets:** Same HH-RLHF + OpenAssistant (cached, no re-download)
- **Model:** Same GPT-2 XL architecture (1.56B params)
- **Checkpoints:** Reuse H-E1 trained models (joint, DPO-only, attr-only)
- **Hyperparameters:** Same loss weighting α=0.7

### C. Implementation Priority
1. **Phase 1 (P0):** FR-1, FR-2, FR-3 - Load models and extract hidden states
2. **Phase 2 (P0):** FR-4, FR-5 - Train probing classifiers
3. **Phase 3 (P0):** FR-6 - Compute CKA similarity
4. **Phase 4 (P1):** FR-7, FR-8 - Gradient analysis and visualization

---

**End of Document**
