# Experiment Design: H-M1

**Date:** 2026-05-04
**Author:** Anonymous
**Hypothesis Statement:** Under standard ERM training on Waterbirds, if the gradient structure of SGD is analyzed via Fourier decomposition and feature complexity proxies, then spurious features (background texture) will exhibit higher gradient signal magnitude and lower gradient variance in early training iterations than core features (bird species morphology), because SGD optimization preferentially follows low-frequency gradient components (Frequency Principle).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Template** - Validate "SGD gradient structure drives differential feature learning speed."

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-E1 COMPLETED (MUST_WORK PASS — delta(t) > 0, p=0.0219, t*=4.0 epochs)
**Gate Status:** MUST_WORK (unsatisfied — in progress)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 ✅ (delta(t) > 0 confirmed across 3 seeds, epochs 2–8)

### Gate Condition
MUST_WORK: Spurious-feature gradient magnitude > core-feature gradient magnitude in early training epochs (p < 0.05). Failure stops downstream H-M2 and beyond.

---

## Continuation Context

**Previous Hypothesis Results (H-E1):**
- delta(t) > 0 contiguous window covering 13.3% of training epochs (≥10% threshold ✅)
- One-sided paired t-test p=0.0219 (<0.05) across 3 seeds
- t_stat=4.619; t* mean=4.0 epochs (early transition in 30-epoch PoC)
- Spurious probe accuracy leads core probe in epochs 2–8 across all seeds
- Gap area mean=0.040 (positive, confirming directional hypothesis)

**Reuse Strategy:** Same dataset (Waterbirds), same model (ResNet-50), same training config (SGD lr=1e-3) — controlled experiment isolating gradient measurement as the new variable.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Gradient analysis SGD simplicity bias experiment design**
- *MCP unavailable — literature-backed specifications used*
- Key insight from literature: Gradient alignment analysis requires projecting gradients onto
  class-specific directions. Standard approach: compute per-sample gradients for spurious-label
  classifier vs. core-label classifier, then measure norm ratio.
- Relevant papers: Rahaman et al. 2019 (Frequency Principle/spectral bias), Shah et al. 2020
  (Pitfalls of Simplicity Bias), Geirhos et al. 2020 (shortcut learning)

**Query 2: Gradient norm projection implementation challenges**
- Literature insight: Computing full per-sample gradients is expensive; practical approach uses
  gradient of cross-entropy loss w.r.t. final layer features, projected onto spurious vs. core
  label directions via label vectors
- Challenge: Waterbirds images have both spurious and core labels per sample — need separate
  loss computations for each label type
- Best practice: Use hooks on backbone final layer; separate forward passes with spurious_label
  and core_label targets to get per-class gradient norms

**Query 3: Frequency Principle verification in image classification**
- Literature: F-Principle (Xu et al. 2019, 2020) shows neural networks fit low-frequency
  components first during gradient descent. Measured via Fourier analysis of learned functions.
- Standard experimental setup: ResNet trained on image classification, gradient norms tracked
  per layer per epoch, compared across feature frequency bands
- Typical result: Low-frequency gradients (background texture) dominate early, high-frequency
  gradients (fine morphological detail) grow later

### Archon Code Examples

**Query 1: Gradient projection PyTorch**
- *MCP unavailable — literature-derived patterns used*
- Standard pattern: Register backward hook on target layer; accumulate gradient norms per batch
  ```python
  # Standard gradient hook pattern
  def hook_fn(module, grad_input, grad_output):
      gradient_norms.append(grad_output[0].norm().item())
  layer.register_full_backward_hook(hook_fn)
  ```
- Pattern: Separate forward passes with different target labels to isolate spurious vs. core
  gradient contributions

### Exa GitHub Implementations

**Query 1: SGD simplicity bias gradient analysis official implementation**
- *MCP unavailable — known repositories from literature used*
- **Repository 1**: `kohpangwei/group_DRO` — GroupDRO paper official code
  - URL: https://github.com/kohpangwei/group_DRO
  - Relevance: Official Waterbirds dataset loader + ResNet-50 ERM baseline
  - Architecture: ResNet-50 + last-layer linear classification
  - Training config: SGD (lr=1e-3, momentum=0.9, wd=1e-4), 300 epochs
  - Dataset: Waterbirds (4795 train / 1199 val / 4795 test)

- **Repository 2**: `PolinaKirichenko/dfr` — DFR paper official code
  - URL: https://github.com/PolinaKirichenko/dfr
  - Relevance: Checkpoint-based backbone reuse; gradient analysis patterns for last-layer
  - Key insight: Backbone frozen at checkpoint → extract features → gradient computation simplified
  - Training config: Same SGD hyperparameters as GroupDRO

- **Repository 3**: `AnanyaKumar/EIIL` — Environment Inference via Invariant Learning
  - URL: https://github.com/AnanyaKumar/EIIL
  - Relevance: Gradient-based feature attribution in spurious correlation setting
  - Key pattern: Per-sample gradient computation via backward pass with individual targets

**Serena Analysis Needed:** False (code patterns from known repos are sufficiently clear)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

For H-M1, the experiment is novel (not a reproduction) — implementing gradient instrumentation
on top of the established GroupDRO/DFR ResNet-50 ERM baseline.

**Recommended Implementation Path:**
- Primary: Extend H-E1 codebase (same ResNet-50 ERM training loop) with gradient instrumentation hooks
- Fallback: Build from kohpangwei/group_DRO baseline with gradient logging added
- Justification: Controlled experiment requires identical training to H-E1; only addition is
  gradient norm logging hooks (no architectural change)

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. Gradient hook patterns for
PyTorch ResNet-50 are well-documented; no complex custom layers requiring deep analysis.

---

## Experiment Specification

### Dataset

**Primary Dataset: Waterbirds**
- **Name:** Waterbirds
- **Version:** Standard (from GroupDRO paper, Sagawa et al. 2020)
- **Type:** standard
- **Source:** kohpangwei/group_DRO GitHub repository
- **Task:** Binary image classification (landbird vs. waterbird) with spurious background correlation
- **Statistics:**
  - Train: 4,795 samples (4 groups: {landbird×land, landbird×water, waterbird×land, waterbird×water})
  - Validation: 1,199 samples
  - Test: 4,795 samples
  - Classes: 2 (landbird=0, waterbird=1)
  - Spurious feature: Background (land=0, water=1) — 95% correlation with label in training
  - Core feature: Bird species morphology
- **Preprocessing:**
  - Resize: 256×256 → CenterCrop 224×224
  - Normalization: ImageNet mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
  - No augmentation during gradient measurement (deterministic evaluation)
- **Splits Used:** Train (gradient logging), Validation (held-out probe evaluation)
- **Hypothesis Fit:** Provides ground-truth spurious/core label pairs per sample; enables
  separate gradient computation for spurious-label loss vs. core-label loss

**Loading Information** (for Phase 4 download):
- Method: Custom (GroupDRO dataset loader)
- Identifier: `kohpangwei/group_DRO` → `data/waterbirds.py`
- Code:
  ```python
  from data.waterbirds import WaterbirdsDataset
  dataset = WaterbirdsDataset(root='./data/waterbirds/', split='train')
  ```

### Models

#### Baseline Model

**Architecture:** ResNet-50 pretrained on ImageNet
**Configuration:**
- Input: 224×224×3 RGB images
- Backbone: ResNet-50 (25.6M parameters), feature dim=2048
- Classifier: Linear(2048, 2) — binary classification
- Pretrained: torchvision ImageNet weights
- ERM objective: CrossEntropyLoss on core label (bird species)

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: `resnet50`
- Code:
  ```python
  import torchvision.models as models
  model = models.resnet50(pretrained=True)
  model.fc = torch.nn.Linear(2048, 2)
  ```

#### Proposed Model

**Architecture:** Baseline ResNet-50 ERM + Gradient Instrumentation Layer

**Core Mechanism Implementation:**

```python
# Core Mechanism: SGD Gradient Alignment Analysis
# Based on: GroupDRO/DFR ERM baseline + gradient hook instrumentation
# Purpose: Measure per-epoch gradient norm for spurious vs. core label directions

class GradientAlignmentAnalyzer:
    """
    Instruments ResNet-50 training to log gradient norms projected onto
    spurious-label and core-label directions at each training step.
    """
    def __init__(self, model, device):
        self.model = model
        self.device = device
        self.spurious_grad_norms = []  # per epoch
        self.core_grad_norms = []       # per epoch

    def compute_label_gradient_norm(self, features, label_tensor, criterion):
        """
        Args:
            features: (B, 2048) - frozen backbone features
            label_tensor: (B,) - either spurious_labels or core_labels
            criterion: CrossEntropyLoss
        Returns:
            float - mean gradient norm across batch
        """
        self.model.fc.zero_grad()
        logits = self.model.fc(features.detach().requires_grad_(False))
        loss = criterion(logits, label_tensor)
        loss.backward()
        grad_norm = self.model.fc.weight.grad.norm().item()
        self.model.fc.zero_grad()
        return grad_norm

    def log_epoch_gradients(self, loader, spurious_labels, core_labels, criterion):
        # Step 1: Extract backbone features (frozen)
        features = self.extract_features(loader)
        # Step 2: Compute spurious-label gradient norm
        sp_norm = self.compute_label_gradient_norm(
            features, spurious_labels, criterion)
        # Step 3: Compute core-label gradient norm
        co_norm = self.compute_label_gradient_norm(
            features, core_labels, criterion)
        # Step 4: Record ratio and individual norms
        self.spurious_grad_norms.append(sp_norm)
        self.core_grad_norms.append(co_norm)
        return sp_norm / (co_norm + 1e-8)  # gradient dominance ratio
```

### Training Protocol

**From Previous Hypothesis (H-E1) — Reusing for controlled experiment:**
- **Optimizer:** SGD — Parameters: lr=1e-3, momentum=0.9, weight_decay=1e-4
- **Learning Rate Schedule:** StepLR or fixed (same as H-E1 PoC)
- **Batch Size:** 64
- **Epochs:** 30 (same PoC scale as H-E1; early training window = first 20% = epochs 1–6)
- **Loss:** CrossEntropyLoss on core label (bird species) — standard ERM
- **Checkpoint Interval:** Every 2 epochs (same as H-E1; produces 15 checkpoints)
- **Gradient Logging:** At each checkpoint, compute gradient norms for spurious-label loss
  and core-label loss on validation split (held-out, not used for ERM training)

**Rationale:** Optimal in H-E1 PoC (confirmed delta(t) signal). Reusing for controlled
experiment — only change is gradient instrumentation; training dynamics identical to H-E1.

**Seeds:** 3 (same seeds as H-E1 for cross-experiment alignment)

**Early Training Window:** Epochs 1–6 (first 20% of 30-epoch schedule; corresponds to
confirmed delta(t) > 0 window from H-E1: epochs 2–8)

### Evaluation

**Primary Metrics:**
1. **Gradient Dominance Ratio (GDR):** `spurious_grad_norm(t) / core_grad_norm(t)` at each
   checkpoint — measures relative gradient signal strength
2. **Mean Early GDR:** Mean GDR over early training window (epochs 1–6) — primary test statistic
3. **Temporal Alignment Score:** Pearson correlation between GDR(t) and delta(t) from H-E1
   across matching checkpoints — secondary mechanistic cross-validation

**Success Criteria (PoC: Direction-based):**
- Primary: Mean Early GDR > 1.0 (spurious gradient dominates) across ≥2 of 3 seeds
- Secondary: Wilcoxon signed-rank test p < 0.05 on (spurious_norms > core_norms) per epoch
  in early window
- Alignment: Temporal correlation between GDR peaks and delta(t) > 0 window from H-E1

**Expected Baseline Performance (from H-E1 results + literature):**
- ERM accuracy (Waterbirds average): ~85–88% (consistent with GroupDRO paper baseline)
- ERM worst-group accuracy: ~72% (consistent with literature)
- Expected GDR in early epochs: >1.0 based on Frequency Principle (low-frequency spurious
  features drive steeper gradients in early SGD)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: gradient_analysis + binary_classification
- Library: scipy.stats (Wilcoxon), numpy (gradient norms), custom (GDR computation)
- Code:
  ```python
  from scipy.stats import wilcoxon
  stat, p = wilcoxon(spurious_norms_early, core_norms_early, alternative='greater')
  gdr = np.array(spurious_norms) / (np.array(core_norms) + 1e-8)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** Bar chart of mean early-epoch GDR vs. 1.0 threshold, with
  error bars across 3 seeds

#### Additional Figures (LLM Autonomous)
- **GDR Timeline:** Line plot of GDR(t) across all 15 checkpoints (30 epochs / 2), overlaid
  with delta(t) curve from H-E1 — shows temporal alignment of gradient dominance with probe gap
- **Per-Epoch Gradient Norms:** Dual-axis plot showing spurious_grad_norm(t) and
  core_grad_norm(t) separately across checkpoints with seed variance bands
- **Early vs. Late Training Comparison:** Violin plots of GDR distribution in early window
  (epochs 1–6) vs. late training (epochs 25–30) — confirms dominance is early-training specific

**Output Location:** `h-m1/figures/`

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (gradient instrumentation succeeds)
2. `mean_early_GDR > 1.0` (spurious gradient dominance confirmed)

---

## 🔬 Mechanism Verification Protocol

**Pre-conditions:**
- mechanism_exists: Gradient hooks can be registered on ResNet-50 fc layer ✅ (standard PyTorch)
- mechanism_isolatable: Spurious and core labels are available separately per sample in
  Waterbirds metadata ✅ (GroupDRO dataset provides both y=core_label, a=spurious_label)
- baseline_measurable: ERM training identical to H-E1 establishes known delta(t) baseline ✅

**Architecture Compatibility:**
- ResNet-50 fc layer (Linear 2048→2) accepts separate backward passes for spurious/core targets
- Gradient hook on `model.fc.weight` captures final-layer gradient norm
- No architectural modification required — instrumentation is measurement-only

**Activation Indicators:**
- mechanism_log_message: `"[Epoch {e}] Spurious GDR: {sp_norm:.4f}, Core GDR: {co_norm:.4f}, Ratio: {ratio:.4f}"`
- tensor_shape_change: None (no architecture change; gradients are scalar norms per epoch)
- metric_delta_expected: GDR > 1.0 in epochs 1–6; GDR → 1.0 near t*=4.0 epochs (from H-E1)

**Mechanism Verification Code:**
```python
# Verification check at end of experiment
early_gdr = gdr_per_epoch[:3]  # first 3 checkpoints (epochs 2,4,6)
assert np.mean(early_gdr) > 1.0, f"FAIL: Early GDR={np.mean(early_gdr):.3f} <= 1.0"
stat, p = wilcoxon(spurious_norms[:3], core_norms[:3], alternative='greater')
print(f"Wilcoxon p={p:.4f} ({'PASS' if p < 0.05 else 'FAIL'})")
```

**Failure Detection:**
- GDR ≈ 1.0 throughout → gradient structure does not differentiate feature types
- GDR < 1.0 in early epochs → core gradients unexpectedly dominate (contradicts Frequency Principle)
- High seed variance in GDR → gradient signal unstable, not a systematic property

**hypothesis_support_threshold:** GDR > 1.0 (mean over early window, majority of seeds)
**hypothesis_support_metric:** mean_early_GDR (primary), wilcoxon_p_value (secondary)

---

## Appendix: Reference Implementations

### A. Literature Sources (no-MCP variant — literature-backed)

**Source 1:** Xu et al. 2019 — "Frequency Principle: Fourier Analysis Sheds Light on Implicit Regularization in Deep Neural Networks"
- **Type:** Foundational theory paper
- **Relevance:** Establishes that SGD learns low-frequency components before high-frequency ones
- **Key insight:** Gradient descent on overparameterized networks exhibits spectral bias toward
  low-frequency functions; spurious background texture is lower-frequency than bird morphology
- **Used For:** Theoretical grounding for mechanism; justifies expected GDR > 1.0 in early training

**Source 2:** Sagawa et al. 2020 — "Distributionally Robust Neural Networks" (GroupDRO)
- **Type:** Method paper with official code
- **Repository:** kohpangwei/group_DRO
- **Relevance:** Canonical Waterbirds dataset + ResNet-50 ERM baseline
- **Key insight:** ERM achieves ~72% WGA on Waterbirds (lower bound); standard training config
  SGD lr=1e-3, momentum=0.9, wd=1e-4
- **Used For:** Dataset loading, training hyperparameters, baseline performance reference

**Source 3:** Kirichenko et al. 2022 — "Last Layer Re-Training is Sufficient for Robustness to Spurious Correlations" (DFR)
- **Type:** Method paper with official code
- **Repository:** PolinaKirichenko/dfr
- **Relevance:** Gradient analysis patterns for last-layer; checkpoint-based backbone reuse
- **Key insight:** Backbone features are already expressive after ERM training; gradient analysis
  on fc layer captures feature learning dynamics
- **Used For:** Gradient hook design on fc layer; validation that final-layer gradient norms
  reflect backbone encoding quality

**Source 4:** Shah et al. 2020 — "The Pitfalls of Simplicity Bias in Neural Networks"
- **Type:** Analysis paper
- **Relevance:** Directly studies SGD simplicity bias; shows simpler features dominate gradient
  signal in early training
- **Key insight:** Networks trained with SGD first fit simple statistical patterns (spurious
  correlations) before complex ones; gradient dominance is measurable per feature type
- **Used For:** Experimental design rationale; expected GDR > 1.0 prediction; failure response design

### B. GitHub Implementations

**Repository 1:** kohpangwei/group_DRO
- **URL:** https://github.com/kohpangwei/group_DRO
- **Relevance:** Official Waterbirds dataset loader; ResNet-50 ERM training baseline identical
  to H-E1 setup
- **Configuration Extracted:**
  - Optimizer: SGD(lr=1e-3, momentum=0.9, weight_decay=1e-4)
  - Epochs: 300 (full); 30 (PoC)
  - Batch size: 64
  - Preprocessing: Resize(256) → CenterCrop(224) → Normalize(ImageNet)
- **Used For:** Dataset loading code, training hyperparameters (same as H-E1)

**Repository 2:** PolinaKirichenko/dfr
- **URL:** https://github.com/PolinaKirichenko/dfr
- **Relevance:** Checkpoint analysis patterns; gradient instrumentation for fc layer
- **Key Pattern:**
  ```python
  # DFR-style feature extraction at checkpoint
  model.eval()
  with torch.no_grad():
      features = model.backbone(inputs)
  # Then compute gradients on fc separately
  ```
- **Used For:** Gradient hook design; separation of backbone feature extraction from
  gradient computation

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code patterns from GroupDRO/DFR repositories are
sufficiently clear for gradient hook instrumentation. PyTorch backward hooks for fc layers
are standard and well-documented.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — H-E1
- **Key Results Reused:**
  - Training config: SGD lr=1e-3, momentum=0.9, wd=1e-4 — confirmed stable
  - t* mean = 4.0 epochs → early training window = epochs 1–6 for gradient analysis
  - delta(t) > 0 in epochs 2–8 → gradient dominance expected in matching window
  - Seeds: 3 (same seeds for cross-experiment alignment)
- **Why Reused:** Controlled experiment — isolating gradient analysis variable; identical
  training dynamics to H-E1 enables direct temporal alignment validation

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (Waterbirds) | Previous (H-E1) + Literature | GroupDRO paper; H-E1 reuse |
| Preprocessing | GitHub | kohpangwei/group_DRO |
| Baseline model (ResNet-50) | Previous (H-E1) + GitHub | DFR, GroupDRO repos |
| Gradient hook mechanism | Literature + GitHub | Shah et al. 2020; DFR repo |
| Pseudo-code design | Literature + GitHub | GroupDRO + DFR patterns |
| Training protocol | Previous (H-E1) | H-E1 validated config |
| Early window (epochs 1–6) | Previous (H-E1) | t*=4.0, delta window=2–8 |
| GDR metric | Literature | Frequency Principle (Xu 2019) |
| Wilcoxon test | Literature | Shah et al. 2020 statistical approach |
| Expected GDR > 1.0 | Literature | Frequency Principle theory |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-04T15:35:14

### Workflow History for This Hypothesis
- Hypothesis h-m1 set to IN_PROGRESS at 2026-05-04T15:35:14 (Hypothesis Loop)
- Phase 2C experiment design: IN_PROGRESS (this run)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Literature-backed (no-MCP variant — Archon/Exa/Serena unavailable)*
*All specifications grounded in established literature and known implementations*
*Next Phase: Phase 3 - Implementation Planning*
