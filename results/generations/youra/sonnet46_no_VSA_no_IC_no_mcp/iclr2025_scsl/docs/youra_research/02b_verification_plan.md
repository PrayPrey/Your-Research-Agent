# Phase 2B Verification Plan
# H-SPEnc-v1: Spurious Feature Encoding Differs Across Pretraining Paradigms
# Generated: 2026-08-26

---

## Main Hypothesis

**ID:** H-SPEnc-v1
**Title:** Spurious Feature Encoding Differs Across Pretraining Paradigms Due to Objective-Determined Augmentation Invariance

**Statement:**
Under ImageNet-scale pretraining with identical ResNet-50 backbone architecture, if we compare four training paradigms (supervised ERM, SimCLR contrastive, DINO self-distillation, BarlowTwins non-contrastive SSL), then the spurious/task probe accuracy ratio on frozen representations will differ significantly across at least one paradigm pair (≥ 2%, p < 0.05) on Waterbirds and CelebA group-annotated benchmarks, because the training objective determines which visual features become instance-discriminative and thus preferentially encoded — specifically, contrastive objectives encode visually prominent spurious features (Waterbirds background) more strongly than supervised ERM because background texture is highly instance-discriminative but not invariant under standard augmentation sets.

**H0 (Null):**
No significant difference in spurious/task probe accuracy ratio across training paradigms on the same ResNet-50 backbone on either Waterbirds or CelebA balanced group-annotated test splits.

---

## Sub-Hypothesis Inventory

| ID | Type | Gate | Status | Prerequisites | Description |
|----|------|------|--------|---------------|-------------|
| H-E1 | EXISTENCE | MUST_WORK | READY | none | Paradigm difference in spurious/task ratio exists on Waterbirds |
| H-E2 | EXISTENCE | SHOULD_WORK | NOT_STARTED | H-E1 | Effect replicates or differs on CelebA |
| H-D1 | DIRECTIONAL | SHOULD_WORK | NOT_STARTED | H-E1 | SimCLR > ERM on Waterbirds but not CelebA (paradigm × dataset interaction) |
| H-M1 | MECHANISM | SHOULD_WORK | READY | none | Augmentation ablation causally reduces spurious encoding |

---

## H-E1: Existence of Paradigm Difference on Waterbirds

**Gate:** MUST_WORK (gating — failure blocks Phase 5)
**Status:** READY

**Statement:**
At least one paradigm pair shows a statistically significant difference in spurious/task probe accuracy ratio on Waterbirds balanced test split (≥ 2%, p < 0.05, across 5 seeds using frozen ResNet-50 features and logistic regression linear probes).

**Experimental Design:**
1. Load 4 pretrained ResNet-50 checkpoints:
   - ERM: `torchvision.models.resnet50(pretrained=True)`
   - Contrastive: MoCo-v3 ResNet-50 (`torch.hub.load('facebookresearch/moco-v3', 'resnet50')`) — preferred over SimCLR-v2 (TF-native checkpoint risk)
   - Self-distillation: DINO ResNet-50 (`torch.hub.load('facebookresearch/dino:main', 'dino_resnet50')`)
   - Non-contrastive SSL: BarlowTwins ResNet-50 (`torch.hub.load('facebookresearch/barlowtwins:main', 'resnet50')`)
2. Load Waterbirds via WILDS: `wilds.get_dataset('waterbirds')` with `group_balanced_sample=True` for probe train split.
3. Extract frozen 2048-dim features for all images (no gradient).
4. Train logistic regression probe for: (a) spurious attribute (background: land vs water), (b) task label (bird species).
5. Evaluate on balanced group-annotated test split (50% spurious-correlated, 50% anti-spurious).
6. Compute ratio = spurious_acc / task_acc for each paradigm × seed.
7. Run one-way ANOVA across 4 paradigms; pairwise t-tests with Bonferroni correction (6 pairs).

**Success Criterion:**
- min(p-value) < 0.05 across 6 paradigm pairs
- max(ratio_difference) ≥ 0.02

**Falsification:**
All 6 pairwise t-tests p > 0.05 OR max ratio difference < 0.02.

**Implementation Risk:**
- MoCo-v3 checkpoint must be validated (ImageNet linear probe accuracy reported).
- WILDS `group_balanced_sample=True` must be verified in dataloader.
- Gate criterion: probe_accuracy > majority_class_baseline AND p < 0.05 vs chance (avoids CV > 0.05 error from prior h-e1 experience).

**Compute:** ~3 hrs (feature extraction + 40 probe runs × 5 seeds on single GPU).

---

## H-E2: Cross-Dataset Replication on CelebA

**Gate:** SHOULD_WORK (failure does not block Phase 5)
**Status:** NOT_STARTED
**Prerequisites:** H-E1 (feature extraction pipeline established; reuse code)

**Statement:**
The paradigm effect on spurious/task probe accuracy ratio is observable on CelebA balanced test split, and may differ in magnitude from Waterbirds (reflecting different spurious correlation strength: ~80% CelebA vs 95% Waterbirds).

**Experimental Design:**
1. Reuse 4 pretrained ResNet-50 checkpoints from H-E1.
2. Load CelebA via torchvision: `torchvision.datasets.CelebA`, using Group DRO splits for group annotations (Blond_Hair × Male).
3. Extract frozen features for CelebA train and test images.
4. Train logistic regression probe for: (a) spurious attribute (Male gender), (b) task label (Blond_Hair).
5. Evaluate on group-balanced test split.
6. Run same ANOVA + pairwise t-test analysis as H-E1.

**Success Criterion:**
At least one paradigm pair shows significant ratio difference on CelebA (p < 0.05, ≥ 2%).

**Compute:** ~1.5 hrs (features + 40 probe runs on single GPU; reuses H-E1 infrastructure).

---

## H-D1: Directional Paradigm × Dataset Interaction

**Gate:** SHOULD_WORK
**Status:** NOT_STARTED
**Prerequisites:** H-E1 (features and probe results from H-E1 and H-E2 needed)

**Statement:**
SimCLR/MoCo-v3 (contrastive) representations show a higher spurious/task probe accuracy ratio than ERM (supervised) on Waterbirds (p < 0.05), but no significant difference on CelebA (p > 0.1), confirming that augmentation-invariance of the spurious attribute — not label-based spurious correlation — drives differential encoding.

**Experimental Design:**
1. Use already-computed probe results from H-E1 (Waterbirds) and H-E2 (CelebA).
2. Directional test: MoCo-v3_ratio_WB > ERM_ratio_WB (t-test, p < 0.05).
3. Null test: MoCo-v3_ratio_CelebA vs ERM_ratio_CelebA (t-test, target p > 0.1).
4. Report paradigm × dataset interaction as the core mechanistic evidence.
5. Secondary: compute Pearson r between spurious/task ratio and worst-group accuracy gap across all 40 probe runs.

**Success Criterion (P2):**
- MoCo-v3 ratio > ERM ratio on Waterbirds (p < 0.05)
- MoCo-v3 vs ERM difference on CelebA not significant (p > 0.1)

**Interpretation:**
All three outcomes are scientifically informative:
- MoCo-v3 > ERM on both: label-correlation confounds augmentation-invariance argument
- MoCo-v3 > ERM on WB only: augmentation-invariance hypothesis supported
- No difference on either: ERM label-conditioning and contrastive augmentation-invariance cancel

**Compute:** < 15 min (statistical analysis on existing results — no new computation).

---

## H-M1: Augmentation Ablation Causal Mechanism Test

**Gate:** SHOULD_WORK
**Status:** READY
**Prerequisites:** none (computationally independent)

**Statement:**
SimCLR trained with background-replacement augmentation (SimCLR-NoBackground) shows a spurious/task probe accuracy ratio at least 5% lower than SimCLR trained with standard augmentations (SimCLR-Original) on Waterbirds (p < 0.05, 5 seeds), with task probe accuracy remaining within 5% — confirming augmentation invariance as the causal mechanism for spurious feature encoding in contrastive SSL.

**Experimental Design:**
1. Train SimCLR-Original: ResNet-50 backbone, standard augmentations (random crop 0.2–1.0, color jitter, gaussian blur, horizontal flip), Waterbirds train split, ≥ 20 epochs, 5 seeds.
2. Train SimCLR-NoBackground: same as SimCLR-Original but with background-replacement augmentation — randomly replace background region with a sampled Places365 image before applying standard augmentations.
3. Freeze both backbones. Extract 2048-dim features on Waterbirds.
4. Train logistic regression probe for spurious attribute and task label. Evaluate on balanced test split.
5. Compare: spurious/task ratio (primary), task probe accuracy (confound check), spurious probe accuracy (supplementary).
6. Statistical test: paired t-test across 5 seeds, NoBackground vs Original.

**Success Criterion (P3):**
- SimCLR-NoBackground ratio < SimCLR-Original ratio (p < 0.05 across 5 seeds, difference ≥ 0.05)
- Task probe accuracy difference ≤ 0.05 (representation quality not degraded)

**Confound Control:**
If task probe accuracy drops by > 5% for SimCLR-NoBackground, the mechanism test is confounded by representation quality loss. In this case, report as "inconclusive" rather than supporting the mechanism.

**Compute:** ~5 hrs (2 conditions × 5 seeds × ≥ 20 epochs SimCLR training on Waterbirds, single GPU).

---

## Dependency Graph

```
H-E1 (GATING, MUST_WORK, READY)
│
├── H-E2 (SHOULD_WORK, depends on H-E1)
│     └── feeds into H-D1
│
├── H-D1 (SHOULD_WORK, depends on H-E1 + H-E2 results)
│
└── [independent]
      H-M1 (SHOULD_WORK, READY — parallel scratch training)
```

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| SimCLR-v2 TF checkpoint incompatibility | High | High | Use MoCo-v3 PyTorch Hub as contrastive baseline |
| WILDS probe train split not balanced (95% spurious) | High | High | Explicitly use `group_balanced_sample=True` in WILDS dataloader; verify group counts |
| Ceiling effect: all paradigms ~95% spurious probe accuracy | Medium | High | Balanced test split; ratio metric normalizes; report Cohen's d alongside p-value |
| 5 seeds insufficient for small effects | Medium | Medium | Pre-register ≥ 2% threshold; report effect size |
| SimCLR-NoBackground poor representations (small dataset) | Medium | Medium | Compare task probe accuracy; ≥ 20 epochs training |
| CelebA high variance | Low | Low | Report separately; not in P1 gating criterion |

---

## Timeline

| Task | Compute | Notes |
|------|---------|-------|
| Load 4 checkpoints + extract Waterbirds features | ~1.5 hrs | All paradigms, train + test |
| H-E1: 40 probe runs (4 paradigms × 2 targets × 5 seeds) | ~1.5 hrs | Waterbirds |
| H-E2: 40 probe runs on CelebA | ~1.5 hrs | Reuses checkpoint load |
| H-D1: statistical analysis | ~0.25 hrs | No new compute |
| H-M1: SimCLR from scratch × 2 conditions × 5 seeds | ~5 hrs | Most expensive step |
| Statistics, correlation, plots | ~0.25 hrs | |
| **Total (sequential)** | **~10 hrs** | Single GPU |
| **Total (parallel H-M1)** | **~6 hrs** | 2 GPUs |

---

## Gate Decision Rules

| Hypothesis | Gate | If FAIL | If PARTIAL |
|-----------|------|---------|------------|
| H-E1 | MUST_WORK | Route to Phase 0 (paradigm effect does not exist) | 1 modification attempt; then Phase 2A-Dialogue |
| H-E2 | SHOULD_WORK | Log; continue to Phase 5 | Log; continue |
| H-D1 | SHOULD_WORK | Log; report as inconclusive; continue | Log; continue |
| H-M1 | SHOULD_WORK | Log; report mechanism as unconfirmed; continue | Log; continue |

**Phase 5 proceeds if H-E1 passes (MUST_WORK satisfied), regardless of H-E2/H-D1/H-M1 outcomes.**

---

## Execution Order

1. **READY:** H-E1 and H-M1 can start immediately.
2. After H-E1 completes: unlock H-E2, then H-D1.
3. H-D1 runs after both H-E1 and H-E2 provide probe results (statistical analysis only).
4. All four validated → proceed to Phase 5 baseline comparison.
