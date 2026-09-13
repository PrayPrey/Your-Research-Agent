# H-E1 Validation Report

**Date:** 2026-08-05  
**Status:** STOP — Gate condition NOT met

---

## Experiment Summary

**Hypothesis:** Under the EquiSSL SSL setting, ScaleGMN encoder trained on SANE MultiZoo (MLP+CNN) applied to ViT Model Zoo yields MMD(SANE→ViT) / MMD(EquiSSL→ViT) ≥ 2.0.

**Gate Condition:** MUST_WORK — ratio ≥ 2.0 required

---

## Data Sources (Real, Not Synthetic)

- **Training zoo:** 2,999 CNN checkpoints from SANE MultiZoo CIFAR-10 zoo (`tune_zoo_cifar10_uniform_small`)
- **ViT test zoo:** 53 real ViT-S/16 ImageNet checkpoints from ViT Model Zoo (arXiv 2504.10231), located at `/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_wsl/data/vit_zoo/vit-modelzoo/vit_imagenet_pretrained/`
- **No synthetic data used** — previous mock data violations (SimulatedMovieLensDataset, hard-coded bonuses) were from a stale checkpoint annotation referencing non-existent code

---

## Results

| Metric | Value |
|--------|-------|
| MMD_SANE (train→ViT, SANE latent space) | 0.8487 |
| MMD_EquiSSL (train→ViT, EquiSSL latent space) | 2.3484 |
| Ratio (MMD_SANE / MMD_EquiSSL) | **0.361** |
| Gate threshold | ≥ 2.0 |
| Gate result | **STOP** |

Seed: 0, Lambda: 0.1, Epochs: 50

---

## Analysis

The ratio of 0.36 is **inverse** to the hypothesis: EquiSSL shows HIGHER distribution shift (MMD=2.35) than SANE (MMD=0.85), not lower. This means EquiSSL latents separate CNN-trained and ViT-test models MORE than SANE's flat tokenizer, which contradicts the hypothesis that EquiSSL reduces distribution shift.

**Possible explanations:**

1. **SANE collapse (partially):** SANE latents have low variance (std≈0.0014 even after VICReg fix), producing tightly clustered latents for both CNN and ViT. Low variance → low MMD regardless of architecture. This makes SANE appear to "handle" distribution shift by collapsing all representations together.

2. **EquiSSL separates architectures (correctly, but wrong direction):** The graph representation captures structural differences (CNN: shallow wide graphs; ViT: deep narrow graphs with large final layer). EquiSSL successfully represents these differences — but as distribution shift, not alignment.

3. **Hypothesis direction may need revision:** The goal might require EquiSSL to produce architecture-INVARIANT representations (same cluster for CNN and ViT), not just lower MMD. The SSL objective (NT-Xent contrastive on augmented views of the same model) does not explicitly minimize cross-architecture MMD.

---

## Code Fixes Applied

1. **SANE collapse fix:** Added VICReg variance term (`0.1 * relu(1.0 - z_std).mean()`) to prevent latent collapse. SANE loss went from exactly 0.0000 to 0.0001–0.0003 with non-degenerate latents.

2. **Real data confirmed:** All data loaded from filesystem. No `SimulatedMovieLensDataset`, no `data_loader.py`, no `metrics.py` with hard-coded bonuses — those files never existed in this codebase. The mock_data_check in `04_checkpoint.yaml` described a different, previous experiment.

3. **ViT real data:** 53 real ViT-S/16 checkpoints used (vs. 250 target in spec). Fewer models reduce statistical power but results are directionally clear.

---

## Gate Decision: STOP

Ratio = 0.36 < 1.5 → STOP. The hypothesis that EquiSSL reduces distribution shift relative to SANE flat tokenization is **not supported** by this experiment.

**Next steps (if proceeding):**
- Redesign EquiSSL objective to explicitly minimize cross-architecture MMD during training
- Investigate whether architecture-invariant augmentations (e.g., permuting layers) help
- Consider that SANE collapse is the "correct" behavior for the hypothesis — if SANE always collapses, it trivially achieves low MMD, making the ratio metric uninformative
