# Experiment Design: H-M1

**Date:** 2026-08-05
**Author:** Anonymous
**Hypothesis Statement:** Under GroupDRO training on Waterbirds WILDS, the worst-group loss objective upweights minority groups (land-bird on land background, water-bird on water background — background-atypical examples), creating a group-balanced effective loss signal during backbone training that differs from ERM's uniform sample weighting.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (Theory Confirmation) Template** — H-M1 is a theoretical mechanism hypothesis confirmed via literature + weight analysis, not a full training experiment.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-P0 PASS (DFR ≡ ERM backbone confirmed; cosine sim ≥ 0.9999 all 3 seeds)
**Gate Status:** MUST_WORK (not yet evaluated — pending this experiment)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM (Step 1 of causal chain: GroupDRO signal → backbone → probe accuracy)
- **Prerequisites:** H-P0 (COMPLETED, PASS)

### Gate Condition
**MUST_WORK gate:** If GroupDRO worst-group loss does NOT create a differential gradient signal vs ERM, then H-M2 (gradient propagation) is unmotivated and the entire causal chain collapses. Pipeline STOPS if gate fails.

---

## Continuation Context

**Previous hypothesis:** H-P0 (DFR Backbone Identity Sanity Check) — PASS

### Previous Hypothesis Results
- H-P0 established DFR ≡ ERM backbone (numerically identical, float32 precision)
- ERM background probe accuracy = 0.900 (confirms spurious feature encoding exists)
- Checkpoint path confirmed: `/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scsl/docs/youra_research/_archive/20260805T130336_routing_recovery/h-e1/checkpoints`
- This validates that GroupDRO vs ERM is the meaningful backbone comparison (not DFR vs ERM)

**Key reuse:** Same Waterbirds WILDS dataset (local cache verified), same ResNet-50 checkpoints (12 total: ERM×3, GroupDRO×3, SAM×3, DFR×3), same feature extraction protocol (layer4 → AdaptiveAvgPool2d → flatten → D=2048).

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: GroupDRO worst-group loss spurious correlation experiment**
- No relevant results — Archon KB contains diffusers/image-generation domain content only (similarity scores ~0.38, unrelated domain)

**Query 2: linear probe spurious feature decodability ResNet implementation**
- No relevant results — same domain mismatch

**Assessment:** Archon KB not applicable for this research domain. All implementation grounding comes from Exa GitHub searches and cited papers.

### Archon Code Examples

**Query 1: GroupDRO worst-group loss PyTorch training**
- No relevant results (diffusers/DALLE2 domain only)

**Query 2: sklearn logistic regression linear probe feature extraction**
- No relevant results (same domain mismatch)

**Assessment:** Archon code examples not applicable. Implementation grounded in Exa findings below.

### Exa GitHub Implementations

**Query 1: izmailovpavel/spurious_feature_learning official implementation**

**Repository 1:** izmailovpavel/spurious_feature_learning
- **URL:** https://github.com/izmailovpavel/spurious_feature_learning
- **Relevance:** ⭐⭐⭐ HIGHEST — This is the EXACT source of the 12 ResNet-50 checkpoints used in this experiment. Author's official implementation.
- **Key files:**
  - `group_DRO/` — GroupDRO training codebase (ported from kohpangwei/group_DRO)
  - `dfr_evaluate_spurious.py` — Feature extraction + linear probe evaluation (with `--predict_spurious` flag)
  - `train_supervised.py` — ERM training
- **Confirmed:** GroupDRO uses `--robust` flag (LossComputer with `is_robust=True`)
- **Confirmed:** `dfr_evaluate_spurious.py` uses `StandardScaler` + sklearn linear probe on `layer4` features

**Repository 2:** kohpangwei/group_DRO (Sagawa et al. 2019 official)
- **URL:** https://github.com/kohpangwei/group_DRO
- **Relevance:** ⭐⭐⭐ HIGHEST — Original GroupDRO implementation; base of izmailov repo
- **Key mechanism code (train.py):**
  ```python
  # GroupDRO LossComputer with worst-group upweighting
  train_loss_computer = LossComputer(
      criterion,
      is_robust=args.robust,   # True for GroupDRO
      dataset=dataset['train_data'],
      alpha=args.alpha,
      gamma=args.gamma,        # exponential moving avg step size
      adj=adjustments,
      step_size=args.robust_step_size,
  )
  ```
- **GroupDRO weight update logic (from WILDS fairlex implementation):**
  ```python
  def _update(self, results):
      # compute per-group losses
      group_losses, _, _ = self.loss.compute_group_wise(
          results['y_pred'], results['y_true'], results['g'],
          self.grouper.n_groups, return_dict=False)
      # exponentiated gradient ascent on group weights
      self.group_weights = self.group_weights * torch.exp(
          self.group_weights_step_size * group_losses.data)
      self.group_weights = self.group_weights / self.group_weights.sum()
  ```
- **Mechanism confirmed:** Minority groups (high loss = background-atypical examples) receive exponentially upweighted loss contribution each batch.

**Query 2: Sagawa GroupDRO worst-group loss upweighting minority groups PyTorch**

**Repository 3:** yangarbiter/dp-dg / coastalcph/fairlex (GroupDRO implementations)
- **URL:** https://github.com/yangarbiter/dp-dg
- **Key insight:** `objective = group_losses @ group_weights` — the weighted dot product confirms that minority groups with high loss drive the gradient update disproportionately.
- **Mechanism math (from Sagawa 2019 arXiv 1911.08731):**
  - q_g updated via: `q'_g = q_g * exp(η_q * L(θ; (x,y)))` then normalized
  - Minority groups (land-bird-land, water-bird-water) are background-atypical → high loss → exponentially higher weight
  - Majority groups (land-bird-water, water-bird-land) — spurious correlation easy to exploit → lower loss → downweighted

### 🎯 Implementation Priority Assessment

**CRITICAL: H-M1 is a theoretical mechanism verification, NOT a training experiment.**

This hypothesis verifies that the GroupDRO algorithm (as implemented in izmailovpavel/spurious_feature_learning and Sagawa et al. 2019) creates group-balanced gradient signal by construction. The verification requires:
1. Literature confirmation (Sagawa 2019 mathematical proof)
2. Code analysis (LossComputer upweighting mechanism confirmed in source)
3. Empirical proxy evidence (WGA 0.88 for GroupDRO vs 0.72 for ERM, consistent with mechanism)
4. Group distribution analysis (identify minority groups in Waterbirds WILDS)

**No model training is needed.** The checkpoints are pre-trained; we analyze the training mechanism documented in the paper and code.

**Recommended Implementation Path:**
- Primary: Theoretical confirmation via Sagawa 2019 + izmailovpavel source code analysis
- Secondary: Waterbirds group distribution analysis to identify minority groups empirically
- Fallback: Load GroupDRO checkpoint group_weight history from training logs (if available)
- Justification: H-M1 is BUILD_ON established facts (Sagawa 2019 is the definitive reference); experimental code is minimal

### Code Analysis (Serena MCP)

**Serena Analysis:** Not performed — H-M1 is a theoretical mechanism confirmation with no novel architecture. Source code from Exa (izmailovpavel repo, kohpangwei repo) is sufficiently clear for pseudo-code generation. No complex custom layers requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Dataset:** Waterbirds WILDS
**Type:** standard (real dataset, local cache verified by H-P0)
**Version:** v1.0
**Source:** WILDS benchmark (Koh et al. 2021), Sagawa et al. 2019 (original construction)

**Group structure (for H-M1 minority group identification):**
| group_array | Bird species | Background | Type | Size (approx) |
|-------------|-------------|------------|------|----------------|
| 0 | Landbird | Land | Majority (spurious-consistent) | ~3498 train |
| 1 | Landbird | Water | **Minority** (background-atypical) | ~184 train |
| 2 | Waterbird | Land | **Minority** (background-atypical) | ~56 train |
| 3 | Waterbird | Water | Majority (spurious-consistent) | ~1057 train |

**Minority groups (H-M1 focus):** group_array ∈ {1, 2} — these are the background-atypical examples that GroupDRO upweights.

**Spurious attribute:** `background_label = group_array % 2` (0=land, 1=water)

**Statistics:**
- Train: ~4795 images (imbalanced groups)
- Val: ~1199 images (balanced)
- Test: ~5794 images (full test set, used for linear probe in H-M3)

**Loading Information** (for Phase 4 download):
- Method: WILDS package (already locally cached)
- Identifier: `waterbirds` (WILDS dataset name)
- Code:
  ```python
  from wilds import get_dataset
  dataset = get_dataset(dataset='waterbirds', root_dir='/home/PrayPrey/.wilds_cache')
  train_data = dataset.get_subset('train')
  test_data = dataset.get_subset('test')
  # group_array available via: dataset.metadata_array[:, dataset.metadata_fields.index('y')]
  # background: group_array % 2
  ```

### Models

#### Baseline Model

**Architecture:** ResNet-50 (ERM-trained, izmailovpavel/spurious_feature_learning)
**Configuration:**
- Feature extraction: `model.layer4 → nn.AdaptiveAvgPool2d(1,1) → flatten → D=2048`
- Source: izmailovpavel/spurious_feature_learning (3 seeds: seed1, seed2, seed3)
- Training: Standard ERM (cross-entropy, uniform sample weighting)
- WGA: 0.72 (Izmailov 2022 Table 1)
- Expected background probe accuracy: ~0.90 (confirmed by H-P0)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Hub (izmailovpavel/spurious_feature_learning)
- Identifier: `izmailovpavel/spurious_feature_learning`
- Code:
  ```python
  # Already cached from H-P0 — reuse checkpoint path
  checkpoint_dir = '/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scsl/docs/youra_research/_archive/20260805T130336_routing_recovery/h-e1/checkpoints'
  # Load ERM checkpoint for seed i
  model = torchvision.models.resnet50()
  model.load_state_dict(torch.load(f'{checkpoint_dir}/erm_seed{i}.pth'))
  model.eval()
  ```

#### Proposed Model (Comparison)

**Architecture:** ResNet-50 (GroupDRO-trained) — same architecture, different training objective

**Core Mechanism Implementation:**

```python
# GroupDRO Worst-Group Loss Upweighting Mechanism
# Based on: Sagawa et al. 2019 (arXiv:1911.08731), kohpangwei/group_DRO/train.py
# Confirmed in: izmailovpavel/spurious_feature_learning/group_DRO/

class GroupDROLossComputer:
    """
    Maintains per-group weights and computes worst-group upweighted loss.
    Minority groups (high loss) receive exponentially increasing weights.
    """
    def __init__(self, n_groups, step_size=0.01):
        # Initialize uniform group weights
        self.group_weights = torch.ones(n_groups) / n_groups  # shape: (n_groups,)
        self.step_size = step_size  # η_q in Sagawa 2019 Algorithm 1

    def compute_loss(self, per_sample_losses, group_ids):
        # Step 1: Compute per-group average loss
        group_losses = torch.zeros(self.n_groups)
        for g in range(self.n_groups):
            mask = (group_ids == g)
            group_losses[g] = per_sample_losses[mask].mean()
        # Step 2: Weighted objective (minority groups dominate if high loss)
        objective = group_losses @ self.group_weights  # dot product
        # Step 3: Exponentiated gradient ascent on group weights
        self.group_weights = self.group_weights * torch.exp(
            self.step_size * group_losses.detach())
        self.group_weights = self.group_weights / self.group_weights.sum()
        return objective
    # Result: Waterbirds minority groups (g=1: landbird-water, g=2: waterbird-land)
    # have high loss early in training → receive high weights → gradient computed
    # on backbone reflects their loss signal → backbone adapts to handle them
```

**H-M1 verification logic (pseudo-code):**
```python
# Verify mechanism: load Waterbirds group distribution, confirm minority groups
from wilds import get_dataset
import numpy as np

dataset = get_dataset('waterbirds', root_dir='/home/PrayPrey/.wilds_cache')
train_data = dataset.get_subset('train')
group_array = train_data.metadata_array[:, 0].numpy()  # group_ids

# Count minority vs majority groups
group_counts = np.bincount(group_array, minlength=4)
minority_groups = [1, 2]  # landbird-water, waterbird-land (background-atypical)
majority_groups = [0, 3]  # landbird-land, waterbird-water (spurious-consistent)

minority_fraction = group_counts[minority_groups].sum() / len(group_array)
# Expected: minority_fraction ~5% → GroupDRO upweights these heavily
print(f"Minority fraction: {minority_fraction:.3f}")  # ~0.05
print(f"Group counts: {group_counts}")  # [3498, 184, 56, 1057]
```

### Training Protocol

**NOTE:** H-M1 does NOT train a new model. The GroupDRO checkpoints are pre-trained and sourced from izmailovpavel/spurious_feature_learning. The "training protocol" here documents the original GroupDRO training configuration for mechanism verification.

**Original GroupDRO Training (from izmailovpavel repo + Sagawa 2019 Appendix B):**

| Parameter | Value | Source |
|-----------|-------|--------|
| Optimizer | SGD (momentum=0.9) | kohpangwei/group_DRO/train.py |
| Learning Rate | 0.001 | Izmailov 2022 Appendix B |
| Weight Decay | 0.001 | Izmailov 2022 (grid search best) |
| Batch Size | 32 (Waterbirds) | Izmailov 2022 Appendix B |
| Epochs | 300 (early stopping on worst-group val acc) | Izmailov 2022 |
| Group DRO step size | 0.01 (γ) | Sagawa 2019 default |
| Generalization adjustment | 0 | Izmailov 2022 |
| Seeds | 3 (seed1, seed2, seed3) | Pre-trained checkpoints |
| Loss | GroupDRO worst-group (LossComputer, is_robust=True) | kohpangwei/group_DRO |

**H-M1 experiment protocol (what we actually run):**
- Runtime: ~2-5 minutes (group distribution analysis + mechanism documentation)
- No GPU required (analysis only)
- 1 seed sufficient (group distribution is fixed, not random)

### Evaluation

**H-M1 is a MECHANISM (theoretical) hypothesis — evaluation is confirmatory, not metric-based.**

**Primary Evaluation: Theoretical Confirmation**

| Check | Method | Expected Result | Source |
|-------|--------|----------------|--------|
| Minority group identification | Count group_array ∈ {1,2} in training set | ~240 samples (~5%) | Sagawa 2019 / Waterbirds construction |
| GroupDRO upweighting mechanism | Code review of LossComputer | group_weights increase for high-loss groups | kohpangwei/group_DRO/train.py |
| WGA proxy evidence | Report GroupDRO=0.88 vs ERM=0.72 | +0.16 WGA improvement consistent with mechanism | Izmailov 2022 Table 1 |
| Group-balanced gradient signal | Mathematical derivation of objective | `L_GroupDRO = group_losses @ q`, q upweights minority | Sagawa 2019 Algorithm 1 |

**Success Criteria (MUST_WORK gate):**
- PRIMARY: GroupDRO worst-group loss mechanism confirmed via Sagawa 2019 derivation AND code analysis
- SECONDARY: Waterbirds minority group fraction < 10% (confirming significant imbalance that motivates upweighting)
- GATE PASS: Both checks pass → H-M2 (gradient propagation) is motivated to proceed
- GATE FAIL: If GroupDRO mechanism code cannot be confirmed (e.g., checkpoints not trained with robust loss) → STOP

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: theoretical verification (group distribution analysis + code review)
- Library: `numpy`, `wilds` (no sklearn/torch metrics needed for H-M1)
- Code:
  ```python
  from wilds import get_dataset
  import numpy as np
  dataset = get_dataset('waterbirds', root_dir='/home/PrayPrey/.wilds_cache')
  train_data = dataset.get_subset('train')
  group_array = train_data.metadata_array[:, 0].numpy()
  group_counts = np.bincount(group_array, minlength=4)
  minority_fraction = group_counts[[1,2]].sum() / len(group_array)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** GroupDRO vs ERM WGA bar chart (0.88 vs 0.72) with group-balanced upweighting annotation

#### Additional Figures (LLM Autonomous)
Based on this MECHANISM hypothesis, generate:
1. **Group distribution pie chart:** Waterbirds training group sizes (group 0,1,2,3) — showing minority group imbalance that motivates GroupDRO
2. **GroupDRO weight evolution diagram:** Schematic showing group_weight[g=1,2] increasing as minority group loss stays high (illustrative, based on Sagawa 2019 Figure 1)
3. **Causal chain diagram:** H-M1 → H-M2 → H-M3 showing mechanism flow (GroupDRO signal → gradient propagation → reduced spurious encoding)

**Output Location:** `h-m1/figures/`

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (group distribution analysis completes)
2. Minority group fraction < 10% AND GroupDRO code analysis confirms upweighting mechanism
3. WGA proxy evidence consistent (GroupDRO > ERM WGA from Izmailov 2022)

**Gate Type:** MUST_WORK → if FAIL, pipeline stops (H-M2 unmotivated)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Assessment:** No relevant results in Archon KB (diffusers/image-generation domain only). Domain mismatch — spurious correlations / robustness research not indexed.

### B. GitHub Implementations (Exa)

**Repository 1:** izmailovpavel/spurious_feature_learning (⭐ author's official repo)
- **URL:** https://github.com/izmailovpavel/spurious_feature_learning
- **Query Used:** "izmailovpavel spurious_feature_learning GroupDRO training implementation GitHub"
- **Relevance:** Source of the 12 pre-trained checkpoints used in this experiment; confirms GroupDRO training protocol
- **Key Code:** `group_DRO/` folder, `dfr_evaluate_spurious.py` (with `--predict_spurious` flag)
- **Used For:** Checkpoint loading protocol, feature extraction protocol, GroupDRO training hyperparameters

**Repository 2:** kohpangwei/group_DRO (⭐295 stars — Sagawa 2019 official implementation)
- **URL:** https://github.com/kohpangwei/group_DRO
- **Query Used:** "Sagawa GroupDRO worst group loss upweighting minority groups PyTorch implementation"
- **Relevance:** ⭐⭐⭐ HIGHEST — Official implementation of the GroupDRO algorithm (Sagawa et al. 2019)
- **Key Code:**
  ```python
  # train.py - LossComputer with is_robust=True
  # Exponentiated gradient ascent on group weights:
  self.group_weights = self.group_weights * torch.exp(
      self.group_weights_step_size * group_losses.data)
  self.group_weights = self.group_weights / self.group_weights.sum()
  ```
- **Used For:** Core mechanism pseudo-code, confirmation that minority groups receive upweighted gradient

**Repository 3:** yangarbiter/dp-dg (GroupDRO WILDS implementation)
- **URL:** https://github.com/yangarbiter/dp-dg/blob/master/examples/algorithms/groupDRO.py
- **Relevance:** Clean GroupDRO implementation confirming `objective = group_losses @ group_weights`
- **Used For:** Objective function verification

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — H-M1 is a theoretical mechanism confirmation. Code from Exa searches (kohpangwei/group_DRO, izmailovpavel) is sufficiently clear. No complex novel architecture requiring semantic analysis.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — H-P0
- **File:** `h-p0/04_validation.md`
- **Reused Components:**
  - Dataset: Waterbirds WILDS (verified, local cache at `/home/PrayPrey/.wilds_cache/waterbirds_v1.0`)
  - Checkpoints: 12 ResNet-50 checkpoints at confirmed cache path
  - Feature extraction: `layer4 → AdaptiveAvgPool2d(1,1) → flatten → D=2048` (validated protocol)
  - ERM background probe accuracy: 0.900 (baseline for H-M3 downstream)
- **Why Reused:** Enables controlled experiment; only the training objective varies (GroupDRO vs ERM), architecture and dataset identical

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|-----------------|
| Minority group identification | Phase 2B roadmap + Sagawa 2019 | 02b_verification_plan.md §2.2 H-M1 |
| GroupDRO upweighting mechanism | GitHub (official) | kohpangwei/group_DRO/train.py |
| LossComputer code | GitHub (official) | kohpangwei/group_DRO + izmailovpavel/spurious_feature_learning |
| Training hyperparameters | Paper + official repo | Izmailov 2022 Appendix B; izmailovpavel README |
| WGA proxy evidence | Paper | Izmailov 2022 Table 1 |
| Checkpoint source | GitHub + H-P0 | izmailovpavel/spurious_feature_learning; h-p0/04_validation.md |
| Dataset loading | WILDS package | H-P0 validated protocol |
| Objective function math | Paper | Sagawa 2019 Algorithm 1, arXiv:1911.08731 |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-05T00:00:00Z

### Workflow History for This Hypothesis
- H-P0 PASS: DFR ≡ ERM backbone confirmed (2026-08-05T16:39:00Z)
- H-M1 set to IN_PROGRESS (2026-08-05T16:44:14Z)
- Phase 2C experiment design started (2026-08-05)

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results, domain mismatch), Exa (GitHub — izmailovpavel official repo, kohpangwei official repo, yangarbiter GroupDRO), Serena (skipped — theoretical mechanism, no novel code)*
*All specifications grounded in Sagawa 2019 paper + izmailovpavel/spurious_feature_learning official implementation*
*Next Phase: Phase 3 - Implementation Planning*
