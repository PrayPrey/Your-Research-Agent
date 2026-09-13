# Hypothesis Context: H-E1
**Generated:** 2026-08-31 (JIT from 02b_verification_plan.md)

---

## Hypothesis Info

**ID:** H-E1
**Type:** EXISTENCE
**Gate:** MUST_WORK
**Prerequisites:** None

**Statement:**
Under standard ERM training on Waterbirds and CelebA with random mini-batch sampling, if we compute per-sample last-layer gradient cosine similarity with the batch-mean gradient at epochs {1, 5, 10, 25, 50}, then gradient alignment ROC-AUC for predicting spurious-minority group membership exceeds per-sample loss ROC-AUC at ≥1 epoch on BOTH datasets, because spurious-minority samples cannot be classified via the spurious feature and thus produce gradients conflicting with the majority batch direction.

**Rationale:**
Foundational existence test — validates the core PROVE_NEW claim (claim 5) that the alignment signal is a meaningful proxy. Without this, the intervention hypothesis (H-M3) has no mechanistic basis.

**Success Criteria (PoC):**
- Primary: Alignment ROC-AUC > loss ROC-AUC at ≥1 epoch on BOTH Waterbirds AND CelebA
- Secondary: ROC-AUC > 0.6 threshold indicates meaningful predictive power

**Failure Response:**
PIVOT — restate novelty claim; GAD may still be useful as regularization variant but mechanistic advance claim fails.

---

## Experimental Setup (from Phase 2A)

**Datasets (2):**
1. Waterbirds — standard spurious correlation benchmark; 82% majority (landbirds on land, waterbirds on water); 18% minority; group annotations available; canonical in Group DRO / JTT / LfF literature.
2. CelebA — standard spurious correlation benchmark; ~94% majority (non-blond males); ~6% minority (blond females); group annotations available.

**Primary Dataset Source:** Sagawa et al. 2020 Group DRO paper; kohpangwei/group_DRO repository standard download scripts.

**Model:** ResNet-50
- Type: Standard pretrained image classifier
- Source: torchvision.models.resnet50(pretrained=True)
- Last-layer gradient: 2048×2 = 4096 parameters; vmap-compatible

**Dataset Fit:**
- Waterbirds and CelebA are the canonical benchmarks with ground-truth group annotations, enabling annotation-free training and annotation-based evaluation of the alignment ROC-AUC signal.

**Model Fit:**
- ResNet-50 is standard backbone for these benchmarks; last-layer gradient computation feasible with torch.func.vmap at batch_size=32.

---

## Verification Protocol (from Phase 2B)

1. Train ERM ResNet-50 on Waterbirds and CelebA with kohpangwei/group_DRO standard settings.
2. At epochs {1, 5, 10, 25, 50}, compute per-sample last-layer cosine similarity with batch mean and per-sample loss for all training samples.
3. Use existing group annotations to label each sample as spurious-minority (1) or not (0).
4. Compute ROC-AUC of alignment score and loss score for each epoch on both datasets.
5. Compare ROC-AUC curves; success if alignment > loss at ≥1 epoch on both Waterbirds and CelebA.

---

## Dependencies

- Prerequisite hypotheses: None (foundation)
- Dependent hypotheses: H-M1, H-M2, H-M3, H-M4, H-C1 (all build on this)

---

## Source References

- Phase 2A PROVE_NEW claim 5; Prediction P1; sh1_existence
- Sagawa et al. 2020 (Group DRO), Liu et al. 2021 (JTT), Nam et al. 2020 (LfF)
