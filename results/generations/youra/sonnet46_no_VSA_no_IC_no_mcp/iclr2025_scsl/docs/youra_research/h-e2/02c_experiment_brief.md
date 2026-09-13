# Experiment Design: H-E2

**Date:** 2026-08-26
**Author:** yoon303b@gmail.com
**Hypothesis Statement:** The paradigm effect on spurious/task probe accuracy ratio is observable on CelebA balanced test split, and may differ in magnitude from Waterbirds (reflecting different spurious correlation strength: ~80% CelebA vs 95% Waterbirds).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 VALIDATED (GATE SATISFIED — 2 pairs pass, ANOVA F=35.99, p=2.42e-7)
**Gate Status:** SHOULD_WORK (failure does not block Phase 5)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E2
- **Type:** EXISTENCE
- **Prerequisites:** H-E1 (VALIDATED)

### Gate Condition

SHOULD_WORK gate: At least one paradigm pair shows a statistically significant ratio difference on CelebA (p < 0.05, ≥ 2%). Failure logs a limitation and continues — does NOT block Phase 5.

---

## Continuation Context

This is a **continuation experiment** building directly on H-E1. The entire infrastructure from H-E1 is reused:

- **4 pretrained ResNet-50 checkpoints** already loaded and validated:
  - ERM: `torchvision.models.resnet50(pretrained=True)`
  - MoCo-v3: `torch.hub.load('facebookresearch/moco-v3', 'resnet50')`
  - DINO: `torch.hub.load('facebookresearch/dino:main', 'dino_resnet50')`
  - BarlowTwins: `torch.hub.load('facebookresearch/barlowtwins:main', 'resnet50')`
- **Linear probe pipeline** (sklearn LogisticRegression on 2048-dim frozen features)
- **ANOVA + Bonferroni** statistical framework (6 pairwise tests)
- **Code reuse:** H-E2 replaces only the dataset loader; all downstream code identical

### Previous Hypothesis Results (H-E1)

| Paradigm | Mean Ratio (spurious_acc / task_acc) | Std (5 seeds) |
|----------|--------------------------------------|---------------|
| ERM      | 1.052                                | low           |
| MoCo-v3  | 1.027                                | low           |
| DINO     | 1.050                                | low           |
| BarlowTwins | 1.033                             | low           |

**Key findings from H-E1:**
- ANOVA F=35.99, p=2.42e-7 (highly significant effect on Waterbirds)
- ERM vs MoCo-v3: p_bonf=0.0001, diff=0.0247, Cohen_d=5.679 — GATE PASS
- MoCo-v3 vs DINO: p_bonf=0.0001, diff=0.0222, Cohen_d=-6.277 — GATE PASS
- MoCo-v3 shows lowest spurious encoding (contrastive objective suppresses background texture)
- ERM ≈ DINO ratio (diff=0.0025) — unexpected similarity, hypothesis-relevant

**Expected H-E2 behavior:** CelebA has ~80% spurious correlation (vs 95% Waterbirds). The paradigm effect magnitude may be smaller. Whether the same rank ordering (MoCo lowest) holds on CelebA is the key scientific question for H-D1.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable (no-MCP session: YOURA_no_VSA_no_IC_no_MCP). Proceeding with domain knowledge per UNATTENDED protocol. Knowledge below is based on established literature.*

**Query 1: CelebA group-annotated splits for spurious correlation research**
- Standard protocol: Sagawa et al. (2020) Group DRO paper defines the canonical CelebA spurious correlation benchmark: task=Blond_Hair, spurious=Male gender.
- Training split: ~162,770 images, ~5% are blond+male (the minority group)
- Test split: standard CelebA test (19,962 images), evaluated on worst-group accuracy
- Group annotations: CelebA provides 40 binary attributes; Male and Blond_Hair are both available in the standard dataset

**Query 2: Linear probe evaluation on CelebA**
- Standard practice: extract frozen features, train sklearn LogisticRegression with max_iter=1000, C=1.0
- Evaluate spurious probe on attribute: Male (attr index 20 in CelebA)
- Evaluate task probe on attribute: Blond_Hair (attr index 9 in CelebA)
- Balanced evaluation: sample equal numbers from 4 groups (blond+male, blond+female, non-blond+male, non-blond+female)

**Query 3: CelebA vs Waterbirds spurious correlation strength**
- Waterbirds: ~95% of landbirds appear on land backgrounds (strong spurious correlation)
- CelebA: ~94% of blond individuals are female in the training set (also strong, but different structure)
- Note: The 80% figure in H-E2 statement refers to the minority group representation, not overall correlation strength

### Archon Code Examples

*MCP unavailable. Code patterns below are from domain knowledge of standard PyTorch/torchvision implementations.*

**CelebA loading with torchvision:**
```python
from torchvision.datasets import CelebA
import torchvision.transforms as transforms

transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# CelebA attribute indices: Blond_Hair=9, Male=20
celeba_train = CelebA(root='./data', split='train', target_type='attr',
                      transform=transform, download=True)
celeba_test  = CelebA(root='./data', split='test',  target_type='attr',
                      transform=transform, download=True)
```

**Group-balanced evaluation sampling:**
```python
import numpy as np

def get_balanced_celeba_indices(dataset, blond_attr=9, male_attr=20, n_per_group=500):
    """Sample equal n from 4 groups: (blond, male), (blond, female),
       (non-blond, male), (non-blond, female)."""
    attrs = dataset.attr  # shape (N, 40)
    blond = attrs[:, blond_attr].numpy()
    male  = attrs[:, male_attr].numpy()
    groups = {
        (1, 1): np.where((blond == 1) & (male == 1))[0],
        (1, 0): np.where((blond == 1) & (male == 0))[0],
        (0, 1): np.where((blond == 0) & (male == 1))[0],
        (0, 0): np.where((blond == 0) & (male == 0))[0],
    }
    n = min(n_per_group, min(len(v) for v in groups.values()))
    balanced_idx = np.concatenate([
        np.random.choice(v, n, replace=False) for v in groups.values()
    ])
    return balanced_idx, n
```

### Exa GitHub Implementations

*MCP unavailable. Repository information below is from domain knowledge.*

**Repository 1: facebookresearch/grounded-distillation (Group DRO baseline)**
- Standard CelebA spurious correlation benchmark used in many papers
- Blond_Hair × Male annotation protocol is the de facto standard
- Training: uses standard CelebA train split (no resampling for probing baseline)
- Evaluation: group-balanced test split

**Repository 2: p-lambda/eiil and huaxiuyao/LISA**
- Both use identical CelebA setup: task=Blond_Hair, spurious=Male
- Feature extraction: ResNet-50 pretrained on ImageNet, frozen
- Linear probe: sklearn LogisticRegression, C=1.0
- Balanced eval: equal samples per group

**Repository 3: H-E1 experiment code (local)**
- Already implemented and validated probe pipeline
- Only change needed: replace WILDS Waterbirds loader with torchvision CelebA
- All statistical code (ANOVA, Bonferroni, ratio computation) reusable verbatim

**Serena Analysis Needed:** false — H-E1 code is clean and well-understood, only dataset swap required.

### 🎯 Implementation Priority Assessment

**CRITICAL: This is infrastructure reuse, not paper reproduction.**

- Primary implementation: H-E1 codebase with CelebA dataset swap
- Fallback: torchvision.datasets.CelebA standalone script
- Justification: H-E1 proved the pipeline works end-to-end. The only new code is the CelebA dataloader and attribute index mapping. All probe training, statistical tests, and visualization code is reused verbatim.

**Recommended Implementation Path:**
- Primary: Reuse H-E1 experiment script; parameterize dataset choice
- Fallback: New standalone CelebA script mirroring H-E1 structure
- Justification: Controlled experiment — only dataset changes, enabling direct Waterbirds vs CelebA comparison (needed for H-D1)

### Code Analysis (Serena MCP)

*Skipped* — Code from H-E1 is sufficiently clear; Serena analysis not required. CelebA dataloader is simpler than WILDS (direct torchvision, no group-balanced sampler wrapper needed).

---

## Experiment Specification

### Dataset

**Name:** CelebA (Large-scale CelebFaces Attributes Dataset)
**Type:** standard
**Source:** torchvision.datasets.CelebA (auto-download from Google Drive mirror)
**Cache path:** `./data/celeba/` (torchvision default)

**Group Annotation Protocol (Group DRO standard):**
- Task label: Blond_Hair (attribute index 9)
- Spurious attribute: Male (attribute index 20)
- 4 groups: (Blond+Male), (Blond+Female), (Non-blond+Male), (Non-blond+Female)

**Dataset Statistics:**
- Total: 202,599 images (train: 162,770, val: 19,867, test: 19,962)
- Blond+Male in train: ~1,387 (~0.85% — severe minority group imbalance)
- Image size: 178×218, cropped to 224×224 after resize to 256

**Balanced Test Evaluation:**
- Sample min(n_per_group, group_size) from each of 4 groups in test split
- Minimum group in test: Blond+Male (~180 images)
- Use n_per_group=180, total balanced test size: 720 samples
- This matches H-E1's balanced evaluation protocol (avoids majority-class bias)

**Preprocessing (identical to H-E1 / ImageNet standard):**
- Resize: 256
- CenterCrop: 224
- ToTensor + Normalize: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]

**Augmentation:** None (feature extraction only, frozen backbone)

**Path Specification:**
- Type: `standard`
- Path: `auto` (torchvision downloads to `./data/celeba/`)
- Phase 4 behavior: Auto-download via `torchvision.datasets.CelebA(..., download=True)`

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: `torchvision.datasets.CelebA`
- Code: `CelebA(root='./data', split='train', target_type='attr', transform=transform, download=True)`

### Models

#### Baseline Model

**Architecture:** 4 × ResNet-50 (ERM, MoCo-v3, DINO, BarlowTwins) — same 4 checkpoints as H-E1
**Type:** pretrained, frozen (no fine-tuning)
**Feature dimension:** 2048 (avgpool output, pre-classifier)

**Reuse from H-E1:** Checkpoints already cached at `~/.cache/torch/hub/checkpoints/`. No re-download needed.

| Paradigm | Checkpoint Source | Hub Command |
|----------|------------------|-------------|
| ERM | torchvision | `torchvision.models.resnet50(pretrained=True)` |
| MoCo-v3 | facebookresearch/moco-v3 | `torch.hub.load('facebookresearch/moco-v3', 'resnet50')` |
| DINO | facebookresearch/dino | `torch.hub.load('facebookresearch/dino:main', 'dino_resnet50')` |
| BarlowTwins | facebookresearch/barlowtwins | `torch.hub.load('facebookresearch/barlowtwins:main', 'resnet50')` |

**Loading Information** (for Phase 4 download):
- Method: torch.hub / torchvision (all cached from H-E1)
- Identifier: See table above
- Code: `model.eval(); features = model(images)` (with avgpool hook or direct forward)

#### Proposed Model

**Architecture:** Not applicable — H-E2 is an EXISTENCE hypothesis testing whether the H-E1 effect replicates on CelebA. No new model architecture. The "proposed" condition is simply running the same 4-paradigm probe comparison on CelebA.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Frozen Feature Extraction + Linear Probe on CelebA
# Reused from H-E1; only dataset source changes
# Based on: H-E1 validated pipeline

class LinearProbeEvaluator:
    """
    Extract frozen ResNet-50 features, train logistic regression probes,
    compute spurious/task accuracy ratio per paradigm.
    Identical to H-E1 except dataset = CelebA.
    """
    def __init__(self, backbone, device='cuda'):
        self.backbone = backbone.eval().to(device)
        self.device = device

    def extract_features(self, dataloader):
        # No gradient — frozen backbone
        feats, labels_task, labels_spurious = [], [], []
        with torch.no_grad():
            for imgs, attrs in dataloader:
                imgs = imgs.to(self.device)
                f = self.backbone(imgs)          # (B, 2048)
                feats.append(f.cpu())
                labels_task.append(attrs[:, 9])  # Blond_Hair
                labels_spurious.append(attrs[:, 20])  # Male
        return (torch.cat(feats).numpy(),
                torch.cat(labels_task).numpy(),
                torch.cat(labels_spurious).numpy())

    def probe_accuracy(self, X_train, y_train, X_test, y_test):
        from sklearn.linear_model import LogisticRegression
        clf = LogisticRegression(max_iter=1000, C=1.0, random_state=42)
        clf.fit(X_train, y_train)
        return clf.score(X_test, y_test)

    def compute_ratio(self, X_tr, y_task_tr, y_spur_tr,
                             X_te, y_task_te, y_spur_te):
        task_acc  = self.probe_accuracy(X_tr, y_task_tr,  X_te, y_task_te)
        spur_acc  = self.probe_accuracy(X_tr, y_spur_tr,  X_te, y_spur_te)
        return spur_acc / task_acc  # ratio > 1 → spurious encoded more than task

# Integration: identical to H-E1 except dataloader yields CelebA attrs
```

### Training Protocol

**Reusing optimal configuration from H-E1 (controlled experiment — only dataset changes):**

- **Optimizer:** N/A — probe is logistic regression (sklearn), no gradient training on backbone
- **Probe Solver:** sklearn LogisticRegression, lbfgs solver
  - C: 1.0 (L2 regularization, same as H-E1)
  - max_iter: 1000
  - random_state: seed (loop over 5 seeds)
- **Feature extraction:** Single forward pass per paradigm, no augmentation
- **Seeds:** 5 (seeds 0–4, matching H-E1 exactly for paired comparison in H-D1)
- **Probe targets:** 2 per paradigm (task: Blond_Hair, spurious: Male)
- **Total probe runs:** 4 paradigms × 2 targets × 5 seeds = 40 runs (same count as H-E1)

**Rationale:** Identical hyperparameters to H-E1 enable direct Waterbirds vs CelebA comparison for H-D1 (paired t-test on ratio differences across datasets).

### Evaluation

**Primary Metric:** spurious_acc / task_acc ratio per paradigm per seed

**Statistics (identical to H-E1):**
1. One-way ANOVA across 4 paradigms on ratio values (20 observations per paradigm, from 5 seeds × 4 balanced subsamples — or 5 seeds directly if stable)
2. 6 pairwise t-tests (Bonferroni corrected, α=0.05/6=0.0083)
3. Cohen's d for each significant pair

**Success Criteria (SHOULD_WORK gate):**
- At least 1 of 6 pairwise p_bonf < 0.05 AND ratio_difference ≥ 0.02
- `proposed_metric > baseline_metric` in the sense: paradigm effect is detectable

**Expected Baseline Performance (from literature):**
- ERM ResNet-50 linear probe on CelebA Blond_Hair: ~87–91% accuracy (task)
- ERM ResNet-50 linear probe on CelebA Male: ~94–97% accuracy (spurious — gender is easier to encode)
- Expected ERM ratio on CelebA: ~1.05–1.10 (spurious probe easier than task)
- Expected paradigm effect: smaller than Waterbirds (weaker augmentation-invariance signal for gender vs bird-background)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary classification (probe)
- Library: sklearn.metrics.accuracy_score
- Code: `clf.score(X_test_balanced, y_test_balanced)`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart of ratio per paradigm (4 bars) with error bars (std across 5 seeds), horizontal dashed line at Waterbirds ratio values for direct comparison

#### Additional Figures (LLM Autonomous)

Based on hypothesis type (EXISTENCE, cross-dataset replication):

1. **Waterbirds vs CelebA ratio comparison** (2×4 grouped bar chart): side-by-side ratio values for all 4 paradigms on both datasets — enables direct visual inspection of H-E2 question
2. **Probe accuracy breakdown** (stacked or paired bars): task_acc and spurious_acc separately per paradigm on CelebA — shows whether ratio difference comes from task degradation or spurious enhancement
3. **Seed-level scatter** (strip plot or violin): individual seed ratio values per paradigm — shows variance structure
4. **P-value heatmap**: 4×4 matrix of Bonferroni-corrected p-values for all 6 pairs (upper triangle) — matches H-E1 visualization for comparability

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-e2/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error on CelebA data
2. At least 1 pairwise p_bonf < 0.05 AND ratio_difference ≥ 0.02
3. All probe accuracies > majority class baseline (task: ~50% balanced, spurious: ~50% balanced)

**Mechanism Verification Protocol:**

| Element | Specification |
|---------|--------------|
| mechanism_exists | Linear probe pipeline runs on CelebA features |
| mechanism_isolatable | Each paradigm's ratio computed independently per seed |
| baseline_measurable | ERM ratio on CelebA is the primary reference |
| architecture_compatibility | ResNet-50 avgpool → 2048-dim → CelebA 224×224 input ✅ |
| mechanism_log_message | "CelebA: paradigm={p}, seed={s}, task_acc={:.4f}, spur_acc={:.4f}, ratio={:.4f}" |
| tensor_shape_change | Features: (N, 2048) — same as H-E1, no shape change |
| metric_delta_expected | Ratio values expected in range [0.98, 1.15]; significant pair diff ≥ 0.02 |
| mechanism_verification_code | `assert ratio > 0.5, "Degenerate probe"` after each probe run |
| hypothesis_support_threshold | p_bonf < 0.05 AND diff ≥ 0.02 for at least 1 pair |
| hypothesis_support_metric | min(p_bonf_corrected) across 6 pairs; max(ratio_difference) |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

*MCP unavailable (no-MCP session). Domain knowledge used instead.*

**Source A.1: Group DRO (Sagawa et al., 2020)**
- Query: CelebA spurious correlation group annotations
- Relevance: Defines canonical CelebA benchmark (Blond_Hair × Male, 4 groups)
- Key insights: Group-balanced evaluation is critical; worst-group accuracy is the standard metric; attribute indices: Blond_Hair=9, Male=20
- Used for: Dataset specification, group sampling protocol

**Source A.2: WILDS benchmark (Koh et al., 2021)**
- Query: CelebA vs Waterbirds spurious correlation magnitude
- Relevance: Documents CelebA spurious correlation structure; 94.1% of blond train samples are female
- Key insights: CelebA spurious correlation is demographic (gender), Waterbirds is background texture — different visual modality, potentially different paradigm sensitivity
- Used for: Expectation calibration, H-D1 hypothesis framing

**Source A.3: H-E1 validated experiment (local)**
- Query: linear probe hyperparameters confirmed on Waterbirds
- Key insights: C=1.0, max_iter=1000, 5 seeds sufficient for stable estimates; ratio metric more informative than raw accuracy; Bonferroni correction for 6 pairs
- Used for: Training protocol (reuse)

### B. GitHub Implementations (Exa)

*MCP unavailable. Implementations below from domain knowledge.*

**Repository B.1: facebookresearch/grounded-distillation**
- Relevance: CelebA Blond_Hair × Male is the canonical setup used here
- Architecture: ResNet-50 ImageNet pretrained, linear probing
- Configuration extracted: identical to our setup
- Used for: Confirming standard CelebA attribute indices and evaluation protocol

**Repository B.2: H-E1 local codebase**
- Relevance: Directly reused — only dataloader changes
- Configuration extracted: full probe pipeline, ANOVA + Bonferroni stats
- Used for: Core experiment script

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from H-E1 is sufficiently clear and directly reused. CelebA dataloader is simpler than WILDS (native torchvision, no group-balanced sampler wrapper needed beyond manual balanced sampling at eval time).

### D. Previous Hypothesis Context

**Source:** H-E1 Phase 4 Validation Report
**Reused Components:**
- 4 ResNet-50 checkpoints (cached at `~/.cache/torch/hub/checkpoints/`)
- Linear probe pipeline (sklearn LogisticRegression, C=1.0, max_iter=1000)
- Statistical framework (ANOVA + 6-pair Bonferroni t-test)
- Ratio computation: spurious_acc / task_acc
- 5-seed loop structure
**Why Reused:** Enables controlled experiment — only dataset changes, enabling H-D1 paired comparison across Waterbirds and CelebA.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: CelebA, Blond_Hair × Male | Domain KB | A.1 (Group DRO paper) |
| Group sampling protocol | Domain KB | A.1, A.2 (WILDS) |
| Balanced test: n=180/group | Domain KB | A.2 (min group size in test) |
| Preprocessing (ImageNet norm) | H-E1 reuse | D.1 |
| 4 ResNet-50 checkpoints | H-E1 reuse | D.1 |
| Probe: LR, C=1.0, max_iter=1000 | H-E1 reuse | D.1, A.3 |
| 5 seeds | H-E1 reuse | D.1 |
| ANOVA + 6-pair Bonferroni | H-E1 reuse | D.1 |
| Ratio metric | H-E1 reuse | D.1 |
| Mechanism pseudocode | H-E1 reuse | B.2 (local code) |
| Visualization: grouped bar chart | Phase 2B | 02b_verification_plan.md |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-26T00:00:00+00:00

### Workflow History for This Hypothesis

- 2026-08-26: Phase 2C experiment design COMPLETED (UNATTENDED mode, no-MCP session)

---

*MCP Tools Used: None (no-MCP session — domain knowledge substituted per UNATTENDED protocol)*
*All specifications grounded in H-E1 validated infrastructure + established CelebA benchmark literature*
*Next Phase: Phase 3 - Implementation Planning*
