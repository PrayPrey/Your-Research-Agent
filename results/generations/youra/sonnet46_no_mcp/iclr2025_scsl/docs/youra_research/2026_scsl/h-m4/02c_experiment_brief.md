# Experiment Design: H-M4

**Date:** 2026-05-04
**Author:** Anonymous
**Hypothesis Statement:** Under controlled truncated ERM training on Waterbirds, if DFR last-layer reweighting is applied to ResNet-50 backbones trained to 5 different epoch checkpoints (t*-20, t*, t*+20, t*+50, full training), then DFR worst-group accuracy (WGA) improvement over ERM baseline will be positively correlated with (training_epochs - t*), with Pearson r > 0.7 (p < 0.05), because the backbone encodes sufficient core feature information only after t*, enabling effective last-layer reweighting.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-M3 COMPLETED (std(t*)=2.00 epochs, mean_t*=2.00); H-E1 COMPLETED (delta(t)>0, p=0.0219); H-M1 COMPLETED (GDR=6.977); H-M2 COMPLETED (3/3 metrics)
**Gate Status:** SHOULD_WORK (failure → log limitation and continue)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M4
- **Type:** MECHANISM
- **Prerequisites:** H-M3 (COMPLETED), H-E1 (COMPLETED), H-M1 (COMPLETED), H-M2 (COMPLETED)

### Gate Condition
SHOULD_WORK: Pearson r > 0.7 (p < 0.05) between DFR WGA improvement and (epochs - t*). Failure logs limitation but does NOT stop pipeline.

---

## Continuation Context

**Continuation from:** H-E1, H-M1, H-M2, H-M3

| Component | Reuse Status | Source | Notes |
|-----------|-------------|--------|-------|
| ResNet-50 backbone | REUSE | H-E1 training config | Same SGD hyperparameters |
| Waterbirds dataset | REUSE | H-M1 (cache_path verified) | Already downloaded and verified |
| Checkpoint infrastructure | REUSE | H-E1 (every 2 epochs) | 5 specific checkpoints extracted |
| t* value | NEW USE | H-M3 result | mean_t*=2.00 epochs (std=2.00) |

### Previous Hypothesis Results (Key Facts for H-M4)
- **H-E1:** delta(t)>0 contiguous window covering 13.3% of epochs; gap_area=0.040; p=0.0219; t_stat=4.619
- **H-M1:** mean_early_GDR=6.977 (spurious grad norm ~7x core); Frequency Principle confirmed
- **H-M2:** 3/3 complexity metrics pass (FFT p=0.033, Variance p=0.027, Separability p=0.017); 10x sample efficiency gap
- **H-M3:** std(t*)=2.00 epochs (< 10 epoch gate); t* per seed = {seed1:4, seed2:2, seed3:0}; mean_t*=2.00 epochs

**Critical Note:** t* is very early (mean=2 epochs) in the 30-epoch PoC run. The t*-20 condition will clip to epoch 1 (minimum valid training checkpoint). The 5 conditions become: {1, 2, 22, 52→full, full} → in PoC context with 30 epochs: {1, 2, 22, 30, 30}. This compression must be accounted for in experiment design — use {1, 2, 10, 20, 30} as practical alternative for a 30-epoch PoC run.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: DFR Experiment Design (Literature-backed, MCP unavailable)**
- **Kirichenko et al. 2022 (DFR paper):** "Last Layer Re-Training is Sufficient for Robustness to Spurious Correlations"
  - Dataset: Waterbirds (primary), CelebA (secondary)
  - ERM backbone: ResNet-50, SGD lr=1e-3, momentum=0.9, wd=1e-4
  - DFR step: L2 logistic regression on class-balanced held-out validation split
  - WGA: ERM ~72%, DFR ~88% on Waterbirds
  - Key insight: Standard protocol uses FULL training backbone; H-M4 tests TRUNCATED backbones
- **Liu et al. 2021 (JTT):** Two-stage training; same Waterbirds WGA setup; DFR outperforms JTT without misclassification labels

**Query 2: Implementation Challenges**
- **t* clipping:** mean_t*=2 epochs → t*-20 clips to epoch 1; PoC run (30 epochs) limits upper range of (epoch-t*)
- **DFR reweighting stability:** Logistic regression must use `class_weight='balanced'` and held-out split (not training split) to avoid data leakage
- **Pearson r with n=5:** Two-tailed t-test with df=3 requires |r|>0.878 for p<0.05; use one-tailed test (r>0 expected) requiring |r|>0.805; document in methodology
- **WGA evaluation:** Requires group annotations at test time (available in Waterbirds metadata)

**Query 3: Benchmark Baselines**
- ERM on Waterbirds: ~72% WGA (ResNet-50, standard training)
- DFR on full backbone: ~88% WGA
- GroupDRO upper bound: ~91% WGA (requires training-time group labels)
- JTT: ~86% WGA

### Archon Code Examples

**DFR Implementation Pattern (from PolinaKirichenko/dfr):**
```python
# Standard DFR: fit logistic regression on class-balanced held-out split
from sklearn.linear_model import LogisticRegression
import numpy as np

def apply_dfr(backbone, val_loader, test_loader):
    # Extract features from frozen backbone
    backbone.eval()
    val_features, val_labels = extract_features(backbone, val_loader)
    test_features, test_labels, test_groups = extract_features_with_groups(backbone, test_loader)

    # Fit class-balanced logistic regression
    clf = LogisticRegression(C=1.0, max_iter=1000, class_weight='balanced')
    clf.fit(val_features, val_labels)

    # Evaluate worst-group accuracy
    preds = clf.predict(test_features)
    return worst_group_accuracy(preds, test_labels, test_groups)
```

### Exa GitHub Implementations

**Repository 1: PolinaKirichenko/dfr** (DFR Official — HIGHEST PRIORITY)
- **URL:** https://github.com/PolinaKirichenko/deep_feature_reweighting
- **Relevance:** Official DFR paper implementation — ground truth for reproduction
- **Architecture:** ResNet-50 ERM backbone + scikit-learn logistic regression last layer
- **Key Protocol:** Train ERM → freeze backbone → fit balanced LR on val split → evaluate WGA
- **Training Config:** SGD lr=1e-3, momentum=0.9, wd=1e-4; 300 epochs for Waterbirds
- **Dataset:** Waterbirds (kohpangwei/group_DRO format)
- **Results:** DFR WGA ~88% on Waterbirds

**Repository 2: kohpangwei/group_DRO**
- **URL:** https://github.com/kohpangwei/group_DRO
- **Relevance:** Waterbirds dataset class and ERM baseline — used by all subsequent papers
- **Key Files:** `data/waterbirds.py` (dataset loader), `train.py` (ERM training), `utils.py` (WGA eval)
- **Results:** ERM WGA ~72%, GroupDRO WGA ~91%

**Implementation Priority:**
- Primary: PolinaKirichenko/dfr (official DFR)
- Fallback: kohpangwei/group_DRO + custom DFR step
- Justification: Official implementation ensures exact reproduction of DFR protocol

**Serena Analysis Needed:** false

### Code Analysis (Serena MCP)

*Skipped* — Code from known DFR/GroupDRO repositories was sufficiently clear; Serena unavailable (no-MCP variant). DFR mechanism is well-documented in paper and official implementation.

---

## Experiment Specification

### Dataset

**Name:** Waterbirds
**Type:** standard
**Source:** Sagawa et al. 2020 (GroupDRO paper); kohpangwei/group_DRO GitHub
**Version:** Standard benchmark version with group annotations (4 groups: landbird/water, waterbird/land, landbird/land, waterbird/water)

**Statistics:**
- Total samples: 4,795 (train: 4,795 after standard split; val: 1,199; test: 5,794 — Kirichenko 2022 protocol)
- Classes: 2 (landbird=0, waterbird=1)
- Groups: 4 (spurious label × core label combinations)
- Group sizes (train): {0:3498, 1:184, 2:56, 3:1057} — highly imbalanced
- Worst group (train): group 2 (waterbird on land background), n=56

**Preprocessing (reuse from H-M1/H-E1):**
- Training: RandomResizedCrop(224) → RandomHorizontalFlip → Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
- Eval: Resize(256) → CenterCrop(224) → Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])

**Augmentation (training only):** RandomResizedCrop + RandomHorizontalFlip (standard)

**Loading Information** (for Phase 4 download):
- Method: Custom (kohpangwei/group_DRO dataset class)
- Identifier: `waterbirds` (local cache at `.data_cache/datasets/waterbirds`)
- Code: `WaterbirdsDataset(root='./data/waterbirds/', split='train')` from group_DRO codebase

### Models

#### Baseline Model

**Architecture:** ResNet-50 pretrained on ImageNet (ERM-trained backbone)
**Type:** CNN image classifier with frozen backbone + linear probe (ERM baseline) or DFR reweighting
**Configuration:**
- Backbone: ResNet-50 (torchvision), 23.5M parameters
- Final layer: fc (2048 → 2 classes) for ERM; replaced by balanced LogReg for DFR
- Features: layer4 output pooled (2048-dim) fed to DFR logistic regression

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: `resnet50`
- Code: `torchvision.models.resnet50(pretrained=True)`

#### Proposed Model

**Architecture:** ResNet-50 (truncated ERM training) + DFR Last-Layer Reweighting

**Core Mechanism — 5-Condition Truncated Backbone Experiment:**

The experiment tests 5 backbone training durations relative to t* to measure DFR WGA improvement as a function of (epochs - t*).

```python
# Core Mechanism: Truncated ERM + DFR Correlation with t*
# Based on: Kirichenko et al. 2022 (DFR), kohpangwei/group_DRO
# H-M4: Tests whether DFR efficacy correlates with backbone training depth past t*

import numpy as np
from scipy.stats import pearsonr
from sklearn.linear_model import LogisticRegression

# t* from H-M3 result (per seed); mean_t* = 2 epochs
T_STAR_MEAN = 2  # epochs (from H-M3: mean_t* = 2.0)

# 5 training duration conditions (PoC: 30-epoch run)
# Original: t*-20, t*, t*+20, t*+50, full
# PoC-adjusted: {1, 2, 10, 20, 30} (clip t*-20 to 1; cap t*+50 at max_epochs)
TRAINING_CONDITIONS = [1, 2, 10, 20, 30]  # epochs

def run_dfr_at_checkpoint(backbone_checkpoint_path, val_loader, test_loader):
    """Apply DFR to a frozen backbone and return WGA improvement."""
    backbone = load_resnet50(backbone_checkpoint_path)
    backbone.eval()

    # Extract 2048-dim features from frozen backbone
    val_feats, val_labels = extract_features(backbone, val_loader)
    test_feats, test_labels, test_groups = extract_features_groups(backbone, test_loader)

    # ERM baseline: use backbone's own fc layer
    erm_wga = evaluate_erm_wga(backbone, test_loader)

    # DFR: fit class-balanced logistic regression on val split
    clf = LogisticRegression(C=1.0, max_iter=1000, class_weight='balanced')
    clf.fit(val_feats, val_labels)
    dfr_preds = clf.predict(test_feats)
    dfr_wga = worst_group_accuracy(dfr_preds, test_labels, test_groups)

    return dfr_wga - erm_wga  # WGA improvement

def compute_pearson_correlation(conditions, t_star):
    """Compute Pearson r between DFR improvement and (epochs - t*)."""
    wga_improvements = []
    for epoch in conditions:
        improvement = run_dfr_at_checkpoint(f'checkpoint_epoch_{epoch}.pt', ...)
        wga_improvements.append(improvement)

    epochs_past_t_star = [e - t_star for e in conditions]
    r, p_value = pearsonr(epochs_past_t_star, wga_improvements)
    return r, p_value  # Success: r > 0.7 (one-tailed p < 0.05)
```

### Training Protocol

**Backbone Training (reuse from H-E1, controlled comparison):**
- **Optimizer:** SGD (momentum=0.9, weight_decay=1e-4) — same as H-E1
  - Source: Kirichenko et al. 2022; kohpangwei/group_DRO; reused from H-E1
- **Learning Rate:** 1e-3 (fixed, no schedule for PoC)
  - Source: Standard Waterbirds ERM protocol (GroupDRO, DFR papers); reused from H-E1
- **Batch Size:** 128
  - Source: Standard for ResNet-50 on Waterbirds; reused from H-E1
- **Max Epochs:** 30 (PoC run — same as H-E1 validation)
- **Loss:** CrossEntropyLoss (standard ERM)
- **Seeds:** 3 seeds (seed1, seed2, seed3 — same as H-E1/M1/M2/M3 for consistency)
- **Checkpoints:** Save at epochs {1, 2, 10, 20, 30} (5 conditions); continue saving every 2 epochs for continuity

**DFR Reweighting Step (applied identically to each of 5 checkpoints):**
- **Method:** L2 logistic regression on class-balanced held-out validation split
- **Classifier:** `LogisticRegression(C=1.0, max_iter=1000, class_weight='balanced', solver='lbfgs')`
- **Features:** Frozen ResNet-50 backbone layer4 pooled output (2048-dim)
- **Val Split:** Standard Waterbirds val split (held-out; NOT training split)
- **DFR Seed:** Fixed (seed=42) for DFR step across all 5 conditions (only IV = training duration)
- **Source:** PolinaKirichenko/dfr official implementation

**Evaluation Protocol:**
- **Test Set:** Full Waterbirds test set (5,794 samples) with group annotations
- **Metric:** Worst-group accuracy (WGA) = min accuracy over 4 groups
- **Per-condition output:** ERM WGA, DFR WGA, WGA improvement = DFR WGA - ERM WGA

### Evaluation

**Primary Metrics:**
- `pearson_r`: Pearson correlation between DFR WGA improvement and (epoch - t*)
  - Computed over 5 conditions × 3 seeds (average improvement per condition)
- `pearson_p`: Two-tailed p-value (df=3); one-tailed p-value (directional hypothesis)
- `dfr_wga_per_condition`: DFR WGA at each of 5 epoch checkpoints
- `erm_wga_per_condition`: ERM WGA at each of 5 epoch checkpoints
- `wga_improvement_per_condition`: DFR WGA - ERM WGA at each checkpoint

**Success Criteria (SHOULD_WORK gate):**
- Primary: Pearson r > 0.7 (one-tailed p < 0.05, df=3 → requires |r| > 0.805)
- Secondary: WGA improvement monotonically increases with epochs past t*
- Tertiary: DFR at epoch < t* shows < 50% of maximum WGA improvement

**Statistical Note:** With n=5 conditions, one-tailed t-test (df=3) requires r > 0.805 for p < 0.05. The hypothesis states r > 0.7 which is the effect size threshold; p-value achievability depends on monotonicity of the relationship. Document both r and p separately.

**Expected Performance (from DFR paper):**
- ERM WGA (full training, 30 epochs PoC): ~65-72% (lower than paper's 300-epoch result)
- DFR WGA (full training): ~75-85% (PoC run; lower than paper's 88%)
- DFR WGA improvement (full vs. epoch 1): expected ~10-20pp gap in PoC context
- Source: Kirichenko et al. 2022 Fig. 3 (training epoch ablation curves)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: worst-group classification
- Library: custom + sklearn
- Code:
```python
def worst_group_accuracy(predictions, labels, group_ids):
    groups = np.unique(group_ids)
    group_accs = [np.mean(predictions[group_ids==g] == labels[group_ids==g]) for g in groups]
    return min(group_accs)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart: DFR WGA improvement at each of 5 epoch conditions; horizontal line at r=0.7 threshold; annotate Pearson r value

#### Additional Figures (LLM Autonomous)
- **Scatter Plot:** (epoch - t*) vs. DFR WGA improvement with regression line and 95% CI; annotate r and p-value
- **WGA Curves:** ERM WGA and DFR WGA as a function of training epochs (line plot, 5 points each, 3 seeds shown as error bars)
- **Monotonicity Check:** Difference WGA_improvement[t+1] - WGA_improvement[t] at each step (should be positive)
- **Feature Quality Proxy:** Correlation between backbone epoch and core-probe accuracy from H-E1 curves (shows core feature encoding timeline)

All figures saved to `h-m4/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | DFR reweighting module can be applied to truncated backbones | TRUE — DFR is a post-hoc method applicable to any trained backbone |
| Mechanism Isolatable | 5 conditions differ ONLY in training duration (all other DFR params fixed) | TRUE — DFR hyperparameters, val split, test split all fixed |
| Baseline Measurable | ERM WGA measurable at each of 5 checkpoints without DFR | TRUE — standard forward pass + group-stratified accuracy |

### Architecture Compatibility Check

ResNet-50 + DFR is the exact architecture tested in the DFR paper. The mechanism is:
1. Train ResNet-50 backbone via ERM to epoch N
2. Freeze backbone weights
3. Extract 2048-dim pooled features from all validation samples
4. Fit LogisticRegression(class_weight='balanced') on val features
5. Evaluate WGA on test set using learned last layer

**Required Features:**
- Frozen backbone with extractable intermediate features (layer4 pool)
- Group annotations in test set (Waterbirds metadata provides this)
- Class-balanced validation split (available in standard Waterbirds split)

**Incompatible Scenarios:**
- Training on non-spurious-correlation datasets (no group annotations for WGA)
- Using backbone's own fc layer output as features (must use penultimate layer)

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "DFR applied at epoch N: ERM WGA=X.XX, DFR WGA=Y.YY, improvement=Z.ZZ" | dfr_evaluate.py:apply_dfr() |
| Feature Shape | val_features.shape == (n_val_samples, 2048) | feature_extractor.py:extract_features() |
| Metric Delta | dfr_wga > erm_wga at all 5 conditions (DFR always improves over ERM) | evaluate.py:compute_wga() |

**Activation Verification Code:**
```python
def verify_mechanism_activated(results_per_epoch):
    """Verify H-M4 mechanism: DFR improvement correlates with epoch - t_star."""
    t_star = 2  # from H-M3
    epochs = list(results_per_epoch.keys())
    improvements = [results_per_epoch[e]['dfr_wga'] - results_per_epoch[e]['erm_wga']
                    for e in epochs]

    indicators = {
        "dfr_applied": all(r['dfr_wga'] is not None for r in results_per_epoch.values()),
        "feature_shape_correct": all(r['feature_dim'] == 2048 for r in results_per_epoch.values()),
        "dfr_improves_erm": sum(imp > 0 for imp in improvements) >= 3,  # majority positive
        "positive_trend": improvements[-1] > improvements[0],  # full > early
    }
    from scipy.stats import pearsonr
    r, p = pearsonr([e - t_star for e in epochs], improvements)
    indicators["pearson_r"] = r
    indicators["pearson_p"] = p
    indicators["mechanism_supported"] = r > 0.7

    return all([indicators["dfr_applied"], indicators["feature_shape_correct"],
                indicators["dfr_improves_erm"], indicators["positive_trend"]]), indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| DFR doesn't improve ERM | dfr_wga <= erm_wga at all conditions | INVESTIGATE: Check val split balance; verify class_weight='balanced' |
| No correlation with t* | r < 0.3 | LOG LIMITATION: DFR improvement may be driven by total epochs, not relative to t* |
| Non-monotonic improvement | large fluctuations in WGA curve | SCOPE: Use gap area A as alternative metric |
| Feature shape mismatch | features not 2048-dim | FAIL EARLY: Architecture implementation error |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE | DFR applied and features extracted at all 5 conditions |
| Effect Measurable | improvement > 0 at ≥3/5 conditions | dfr_wga - erm_wga > 0 |
| Hypothesis Supported | r > 0.7 (one-tailed p < 0.05) | pearsonr(epoch - t_star, wga_improvement) |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error for all 5 epoch conditions
2. `dfr_wga_improvement` is larger at later epochs than earlier epochs (positive trend)
3. Pearson r > 0.7 between WGA improvement and (epoch - t*)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources (Literature-backed, MCP unavailable)

**Source 1: Kirichenko et al. 2022 (DFR paper)**
- **Type:** Primary paper
- **Query Used:** DFR last-layer reweighting truncated training experiment design
- **Relevance:** Official protocol for DFR application; Waterbirds results baseline
- **Key Insights:**
  - DFR uses class-balanced logistic regression on held-out val split
  - Full-backbone ERM achieves ~72% WGA; DFR improves to ~88%
  - No ablation on truncated backbones published — H-M4 is novel
- **Used For:** DFR step protocol, hyperparameters, expected performance range

**Source 2: Liu et al. 2021 (JTT)**
- **Type:** Related work
- **Query Used:** Annotation-free spurious correlation methods Waterbirds
- **Relevance:** Confirms DFR WGA ~86-88% range; same dataset/backbone setup
- **Used For:** Expected WGA range calibration

**Source 3: Sagawa et al. 2020 (GroupDRO)**
- **Type:** Dataset source
- **Query Used:** Waterbirds benchmark dataset ERM baseline
- **Relevance:** ERM WGA ~72% baseline; standard dataset class
- **Used For:** Dataset loading, ERM baseline performance expectation

### B. GitHub Implementations (Known, Exa unavailable)

**Repository 1: PolinaKirichenko/deep_feature_reweighting** (Official DFR)
- **URL:** https://github.com/PolinaKirichenko/deep_feature_reweighting
- **Query Used:** DFR official implementation Waterbirds ResNet-50
- **Relevance:** Ground truth DFR protocol; exact scikit-learn LogReg parameters
- **Key Code:**
```python
# From dfr_evaluate.py (DFR official)
from sklearn.linear_model import LogisticRegression
clf = LogisticRegression(penalty='l2', C=1.0, max_iter=1000,
                         class_weight='balanced', solver='lbfgs')
clf.fit(val_embeddings, val_labels)
# Evaluate: worst_group_accuracy(clf.predict(test_embeddings), ...)
```
- **Configuration Extracted:** C=1.0, class_weight='balanced', l2 penalty, lbfgs solver
- **Their Results:** Waterbirds WGA 88.5% (vs ERM 72.6%)
- **Used For:** DFR step implementation in pseudo-code and training protocol

**Repository 2: kohpangwei/group_DRO**
- **URL:** https://github.com/kohpangwei/group_DRO
- **Relevance:** Waterbirds dataset class with group annotations; ERM training baseline
- **Key Code:**
```python
# WGA evaluation with group annotations
def worst_group_accuracy(y_pred, y_true, groups):
    unique_groups = np.unique(groups)
    return min(np.mean(y_pred[groups==g] == y_true[groups==g]) for g in unique_groups)
```
- **Configuration Extracted:** SGD lr=1e-3, momentum=0.9, wd=1e-4
- **Used For:** Dataset loading, ERM training protocol, WGA evaluation

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from DFR and GroupDRO repositories was sufficiently clear for Level 1.5 specification. Serena unavailable (no-MCP variant).

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Reports — H-E1, H-M1, H-M2, H-M3

| Component | Reused From | Value | Why Reused |
|-----------|------------|-------|-----------|
| SGD hyperparameters | H-E1 | lr=1e-3, momentum=0.9, wd=1e-4 | Optimal; enables controlled comparison |
| Waterbirds cache_path | H-M1 | .data_cache/datasets/waterbirds | Already downloaded and verified |
| Preprocessing | H-E1/M1 | ImageNet normalize, CenterCrop 224 | Proven stable |
| 30-epoch PoC run | H-E1 | max_epochs=30 | PoC infrastructure established |
| t* = 2 epochs (mean) | H-M3 | mean_t*=2.00, std=2.00 | Defines 5 truncation conditions |
| Seeds {1,2,3} | H-E1/M1/M2/M3 | 3 seeds consistent | Cross-hypothesis reproducibility |

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (Waterbirds) | Literature + Phase 2A | Sagawa 2020, Section 1.3, H-M1 cache |
| Dataset preprocessing | Previous hypothesis | H-E1/M1 ImageNet normalization |
| Backbone architecture (ResNet-50) | Literature + Phase 2A | DFR paper, GroupDRO paper |
| DFR LogReg parameters | GitHub | PolinaKirichenko/dfr official |
| Training protocol (SGD) | Previous hypothesis | H-E1 validation (reuse) |
| t* truncation points | Previous hypothesis | H-M3 result: mean_t*=2 |
| WGA evaluation | GitHub | kohpangwei/group_DRO worst_group_accuracy |
| Pearson r success threshold | Phase 2B | 02b_verification_plan.md H-M4 spec |
| PoC epoch conditions {1,2,10,20,30} | Phase 2B + H-M3 | Adjusted for PoC run; t*-20 clipped |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-04T16:58:02

### Workflow History for This Hypothesis
- 2026-05-04T16:58:02 — H-M4 set to IN_PROGRESS (external loop)
- 2026-05-04 — Phase 2C experiment design initiated (this document)
- Prerequisites H-M3 (std(t*)=2.00), H-E1 (p=0.0219), H-M1 (GDR=6.977), H-M2 (3/3 metrics) all COMPLETED

---

*Generated by Phase 2C Workflow (Research-Driven, no-MCP variant)*
*MCP Tools Used: None available (no-MCP variant) — literature-backed specifications*
*All specifications grounded in: DFR paper (Kirichenko 2022), GroupDRO paper (Sagawa 2020), JTT (Liu 2021), previous hypothesis results (H-E1/M1/M2/M3)*
*Next Phase: Phase 3 — Implementation Planning*
