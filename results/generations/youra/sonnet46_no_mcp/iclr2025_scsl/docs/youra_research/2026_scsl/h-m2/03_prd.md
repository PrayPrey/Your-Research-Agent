# Product Requirements Document: H-M2
## Feature Complexity Measurement — Spurious vs. Core Feature Analysis

**Hypothesis:** H-M2
**Type:** MECHANISM (SHOULD_WORK gate)
**Date:** 2026-05-04
**Phase:** 3 — Implementation Planning
**stepsCompleted:** [1, 2]

---

## 1. Executive Summary

H-M2 validates Assumption A1 of the SGD Temporal Feature Learning Gap hypothesis: that spurious features (background texture, hair color) are measurably simpler than core features (bird species morphology, facial structure) across three independent complexity metrics. This is a dataset characterization experiment using signal processing (FFT), feature statistics (intra-class variance), and linear separability probing — no novel neural architecture required.

**Success Condition (SHOULD_WORK):** ≥2 of 3 complexity metrics show spurious < core complexity with p < 0.05 on Waterbirds. Document any failures as limitations; H-E1 and H-M1 findings remain valid regardless.

---

## 2. Problem Statement

The SGD simplicity bias (H-E1, H-M1) predicts that spurious features are preferentially learned before core features because they are simpler. H-M2 provides direct empirical evidence of this complexity asymmetry by measuring three established complexity proxies:

1. **FFT Mean Spatial Frequency** — lower frequency = smoother = simpler (Geirhos et al. 2019)
2. **Intra-class Feature Variance** — lower variance = more uniform = simpler (Shah et al. 2020)
3. **Linear Separability Learning Curve** — fewer samples to 90% accuracy = simpler (Shah et al. 2020)

**Research Gap:** While the gradient dominance ratio (H-M1, GDR=6.977) confirms spurious features receive stronger gradient signal, no direct measurement of feature complexity has been performed for Waterbirds/CelebA in the SGD temporal gap context.

---

## 3. Functional Requirements

### FR-1: Data Preparation — Waterbirds Dataset
- **What:** Download and verify Waterbirds dataset with segmentation masks
- **How:** Clone `kohpangwei/group_DRO` repository; verify `metadata.csv` and segmentation mask files
- **Fallback:** If masks unavailable, use quadrant-based patch extraction (background=top-40%, foreground=center-60%)
- **Output:** Verified dataset at `.data_cache/datasets/waterbirds/`
- **Samples:** Full train split (4,795 images → ~9,590 patches)

### FR-2: Data Preparation — CelebA Dataset
- **What:** Download CelebA dataset via torchvision
- **How:** `torchvision.datasets.CelebA(root='./data', split='train', target_type='attr', download=True)`
- **Spurious:** hair_color (attr index 9, blond=1); **Core:** gender (attr index 20, male=1)
- **Samples:** Stratified subsample of 5,000 per group (4 groups × 5,000 = 20,000 total)
- **Patch:** hair crop = top-25% of image; facial structure = center crop 112×112

### FR-3: Patch Extraction Pipeline
- **What:** Extract spurious and core image patches from both datasets
- **Waterbirds:** Use segmentation masks — background pixels → spurious patches; bird foreground → core patches; resize all to 64×64 RGB
- **CelebA:** Hair crop (top-25%) → spurious; center face crop → core; resize to 64×64 RGB
- **Normalization:** Raw uint8 patches for FFT; ImageNet-normalized tensors for feature extraction
- **Verification:** Log n_spurious_patches, n_core_patches per dataset; minimum 100 per class

### FR-4: ResNet-50 Feature Extraction
- **What:** Extract layer-4 (2048-dim) features from pretrained ResNet-50
- **Model:** `torchvision.models.resnet50(pretrained=True)`, frozen, `model.fc = nn.Identity()`
- **Input:** Resize 256, CenterCrop 224, ImageNet normalize
- **Output:** `(N, 2048)` numpy arrays for spurious and core features
- **Batch Size:** 256 (inference only, no gradient)

### FR-5: Metric 1 — FFT Mean Spatial Frequency
- **What:** Compute mean spatial frequency of each image patch (lower = simpler)
- **Method:** 2D FFT → shift → power spectrum → weighted mean frequency
- **Formula:** `mean_freq = sum(|F(f)| ** 2 * freq_grid) / sum(|F(f)| ** 2)`
- **Statistical Test:** Two-sided t-test (`scipy.stats.ttest_ind`) spurious vs. core
- **Expected:** `spurious_mean_freq < core_mean_freq`, p < 0.05

### FR-6: Metric 2 — Intra-class Feature Variance
- **What:** Compute within-class variance of layer-4 features (lower = simpler representation)
- **Method:** `trace(Cov(features.T))` per class; t-test on per-feature variances
- **Output:** `var_spurious`, `var_core`, p-value
- **Expected:** `var_spurious < var_core`, p < 0.05

### FR-7: Metric 3 — Linear Separability Learning Curve
- **What:** Probe accuracy learning curves for spurious vs. core labels
- **Method:** `sklearn.linear_model.LogisticRegression(C=1.0, max_iter=1000)` at N ∈ {50, 100, 200, 500, 1000, 2000, full}
- **Seeds:** 3 seeds for subsampling reproducibility
- **Output:** Accuracy curves + AUC comparison + samples-to-90%-accuracy
- **Expected:** Spurious reaches 90% accuracy with ~2–5× fewer samples than core

### FR-8: Statistical Analysis & Reporting
- **Primary test:** Two-sided t-test (α=0.05) per metric
- **Bonferroni correction:** 6 tests (3 metrics × 2 datasets); secondary threshold α=0.0083
- **Gate condition:** ≥2/3 metrics significant on Waterbirds (primary); replicated directionally on CelebA
- **Report:** `results_h_m2.json` with all metric values, p-values, gate result

### FR-9: Visualization
- **Required (gate metrics):** Bar chart — spurious vs. core on all 3 metrics (Waterbirds + CelebA), with p-value annotations → `h-m2/figures/complexity_comparison.png`
- **Additional:**
  - FFT power spectrum heatmap (example patches) → `h-m2/figures/fft_spectrum.png`
  - Learning curve plot (probe accuracy vs. N) → `h-m2/figures/learning_curves.png`
  - PCA/t-SNE of layer-4 features → `h-m2/figures/feature_pca.png`
  - Complexity gap with 95% CI → `h-m2/figures/complexity_gap.png`

### FR-10: Mechanism Verification
- **What:** Run `verify_mechanism_activated(results)` to confirm analysis pipeline executed correctly
- **Checks:** patches_extracted > 100, features shape = (N, 2048), direction_correct_fft, p_value_computed
- **Log:** activation indicators to experiment log

---

## 4. Data Specification

| Dataset | Split | Size | Source | Cache Path |
|---------|-------|------|--------|------------|
| Waterbirds | train | 4,795 images → ~9,590 patches | kohpangwei/group_DRO | `.data_cache/datasets/waterbirds` |
| CelebA | train (stratified) | 5,000/group × 4 groups | torchvision | `.data_cache/datasets/celeba` |

**Waterbirds Groups (4):**
- (landbird, land), (landbird, water), (waterbird, land), (waterbird, water)
- Spurious attribute: background (land/water); Core attribute: bird species

**CelebA Groups (4):**
- (non-blond, female), (non-blond, male), (blond, female), (blond, male)
- Spurious: hair_color; Core: gender

**Patch Sizes:** All patches resized to 64×64 RGB for FFT uniformity

---

## 5. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seeds (42, 123, 456) for learning curve subsampling
- Deterministic feature extraction (model.eval(), no dropout)
- All results saved to JSON for replication

### NFR-2: Compute Efficiency
- ResNet-50 inference only (no training); completes in <30 min on single GPU
- FFT computed on CPU (numpy); no GPU required for metrics
- Batch size 256 for feature extraction

### NFR-3: Statistical Validity
- Minimum 100 patches per class required
- Full train split for Waterbirds FFT (4,795 images)
- 3 seeds for learning curve reproducibility
- Bonferroni correction applied for multiple comparisons

### NFR-4: Fallback Handling
- If Waterbirds segmentation masks unavailable → quadrant-based extraction (log degradation)
- If CelebA face landmarks unavailable → full image crop strategy
- All fallbacks logged with reason

---

## 6. Success Criteria

### Primary Gate (SHOULD_WORK):
- ≥2 of 3 metrics: `spurious_complexity < core_complexity` with p < 0.05 on Waterbirds
- `delta_complexity = complexity(core) - complexity(spurious) > 0` with 95% CI excluding zero

### Secondary:
- Directional replication on CelebA (≥2 metrics, same direction)
- Effect magnitude: variance reduction ≥20%, FFT frequency ratio ≥1.3×

### PoC Pass:
1. Code runs without error
2. ≥2/3 complexity metrics show spurious < core (direction correct, p < 0.05)

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=1.9.0
torchvision>=0.10.0
numpy>=1.21.0
scipy>=1.7.0
scikit-learn>=0.24.0
matplotlib>=3.4.0
seaborn>=0.11.0
pandas>=1.3.0
Pillow>=8.0.0
pyyaml>=5.4.0
tqdm>=4.60.0
```

### 7.2 External Repositories
- `kohpangwei/group_DRO` — Waterbirds dataset loader with segmentation masks
- `PolinaKirichenko/dfr` — Reference for ResNet-50 feature extraction pattern

### 7.3 Inherited from H-M1
- Waterbirds dataset cache: `.data_cache/datasets/waterbirds/` (verified)
- ResNet-50 pretrained weights (torchvision auto-cache)
- Layer-4 feature extraction pattern (`h-m1/code/`)

---

## 8. Constraints

- Single GPU execution (`CUDA_VISIBLE_DEVICES=<empty_gpu>`)
- No model training — inference only
- SHOULD_WORK gate: failure documents limitation but does not block H-M3/H-M4
- Budget: 30 tasks (FULL tier, MECHANISM type)

---

## 9. Out of Scope

- Novel model architecture (H-M2 uses pretrained ResNet-50 only)
- Training loop (inference only)
- Hyperparameter search (fixed complexity metrics)
- Comparison to DFR/JTT baselines (handled in H-M4)
