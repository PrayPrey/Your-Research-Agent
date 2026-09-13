# Product Requirements Document: h-e1 Temporal Convergence Validation

**Hypothesis:** Spurious features converge at least 2 epochs earlier than core features across all 4 datasets (CMNIST, Waterbirds, CelebA, NICO++)

**Type:** EXISTENCE (Proof-of-Concept)

**Gate:** MUST_WORK

**Date:** 2026-08-28

**Author:** yoon303@ust.ac.kr

---

## Executive Summary

This PRD specifies the implementation requirements for validating hypothesis h-e1, which establishes the foundational temporal ordering pattern for spurious vs. core feature convergence. The implementation must support ablation training across 4 diverse spurious correlation benchmarks and measure convergence timing via gradient norm tracking.

**Success Criteria:** Statistical evidence (p < 0.05) that spurious features converge ≥2 epochs earlier than core features across all 4 datasets.

**Failure Impact:** Blocks all dependent hypotheses (h-e2, h-e3, h-m1, h-m2) and falsifies main hypothesis H-TemporalGradient-v1.

---

## Problem Statement

Current spurious correlation research lacks precise quantification of the temporal ordering in which neural networks learn spurious vs. core features. This hypothesis validates whether a consistent 2-epoch gap exists across diverse feature types (color, texture, attribute, semantic context).

**Why This Matters:**
- Foundation for temporal-based debiasing interventions
- Validates assumption underlying all mechanism hypotheses
- Determines feasibility of gradient-based diagnostics

---

## Functional Requirements

### FR-1: Multi-Dataset Infrastructure

**Priority:** P0 (MUST_WORK gate dependency)

**Description:** Support for 4 spurious correlation benchmarks with dataset-specific preprocessing.

**Acceptance Criteria:**
- CMNIST: Torchvision MNIST + color bias injection, resize 224×224, ImageNet normalization
- Waterbirds: Wilds benchmark loading, standard splits, ImageNet preprocessing
- CelebA: Standard splits filtered for bias (Blond_Hair target), center crop + resize 224×224
- NICO++: Official repository loading, standard splits, resize 224×224
- All datasets support DataLoader with configurable batch size
- Preprocessing pipelines match benchmark standards for reproducibility

### FR-2: Ablation Training Variants

**Priority:** P0

**Description:** Three training modes per dataset to isolate spurious vs. core features.

**Acceptance Criteria:**
- **Spurious-only mode:**
  - CMNIST: Gaussian blur (kernel=15) to destroy shape, preserve color
  - Waterbirds: Foreground masking to isolate background
  - CelebA: Gender-preserving face region masking
  - NICO++: Object masking to isolate context
- **Core-only mode:**
  - CMNIST: RGB→Grayscale to remove color, preserve shape
  - Waterbirds: Background masking via segmentation
  - CelebA: Gender-invariant preprocessing
  - NICO++: Context masking to isolate object
- **Baseline mode:** Full image, standard ERM training
- Feature extraction methods validated against prior work (Nam et al. 2020, Sagawa et al. 2020)

### FR-3: Gradient-Based Convergence Tracking

**Priority:** P0

**Description:** Per-epoch gradient norm computation with 3-epoch convergence criterion.

**Acceptance Criteria:**
- Compute L2 norm of all model gradients after each training epoch
- Store gradient history in memory-efficient format
- Convergence detection: gradient norm < 10% of peak for 3 consecutive epochs
- Return convergence epoch (E_s, E_c, E_baseline) or None if no convergence by max_epochs
- Gradient norm computation handles mixed-precision training if enabled

### FR-4: Model Architecture Support

**Priority:** P0

**Description:** ResNet baseline models with ImageNet initialization.

**Acceptance Criteria:**
- ResNet-18 for CMNIST (torchvision.models.resnet18, pretrained=True)
- ResNet-50 for Waterbirds/CelebA/NICO++ (torchvision.models.resnet50, pretrained=True)
- Replace final FC layer with binary classification head
- Support freezing/unfreezing backbone layers (for optional experiments)
- Compatible with standard PyTorch optimizers (SGD momentum=0.9)

### FR-5: Training Protocol per Dataset

**Priority:** P0

**Description:** Dataset-specific hyperparameters matching benchmark standards.

**Acceptance Criteria:**
- **CMNIST:** LR=0.001, cosine annealing, batch=128, max_epochs=50, weight_decay=1e-4
- **Waterbirds:** LR=0.001, step decay (epochs 30,60), batch=64, max_epochs=100, weight_decay=1e-4
- **CelebA:** LR=0.0001, cosine annealing, batch=64, max_epochs=80, weight_decay=1e-4
- **NICO++:** LR=0.001, cosine annealing, batch=64, max_epochs=100, weight_decay=1e-4
- Loss: Binary cross-entropy with logits
- 10 random seeds per dataset (total 40 runs)

### FR-6: Statistical Validation

**Priority:** P0 (MUST_WORK gate validation)

**Description:** Paired t-test across random seeds to validate temporal gap.

**Acceptance Criteria:**
- Collect (E_s, E_c) pairs for 10 seeds per dataset
- Compute Δ = E_c - E_s for each seed
- scipy.stats.ttest_rel on (E_c, E_s) samples
- Report: t-statistic, p-value, mean(Δ), std(Δ)
- **PoC Pass:** E_s < E_c for >5/10 seeds on all 4 datasets
- **Full Pass:** p < 0.05 AND mean(Δ) ≥ 2 epochs on all 4 datasets

### FR-7: Visualization Generation

**Priority:** P1

**Description:** Automated figure generation for convergence analysis.

**Acceptance Criteria:**
- **Gate Metrics Figure (MANDATORY):** Bar chart of mean(E_s) vs mean(E_c) per dataset, error bars (±1 std), filename: `figures/convergence_comparison.png`
- **Gradient Trajectories:** 4-panel line plot (one per dataset), spurious/core/baseline curves, convergence points marked
- **Temporal Gap Distribution:** Histogram of Δ across all seeds/datasets, reference line at Δ=2
- **Statistical Summary Table:** Per-dataset mean(Δ), p-value, pass/fail indicator
- All figures saved to `h-e1/figures/` subfolder
- Matplotlib backend configured for headless rendering

### FR-8: Results Persistence

**Priority:** P0

**Description:** Structured storage of convergence data and statistical results.

**Acceptance Criteria:**
- CSV export: columns [dataset, seed, E_spurious, E_core, E_baseline, delta]
- JSON summary: {dataset: {mean_delta, p_value, t_stat, samples_count}}
- Saved to `h-e1/results/convergence_data.csv` and `h-e1/results/stats_summary.json`
- Include metadata: timestamp, git commit hash, hypothesis_id

---

## Non-Functional Requirements

### NFR-1: Reproducibility

- All random seeds logged and controllable
- Torch deterministic mode enabled
- Dataset versions documented (Torchvision version, Wilds version, etc.)
- Model checkpoint saving for each converged variant

### NFR-2: Compute Efficiency

- GPU support required (CUDA-compatible)
- Estimated runtime: ~8 hours for all 40 runs (4 datasets × 10 seeds) on single GPU
- Mixed precision training optional (not required for PoC)

### NFR-3: Error Handling

- Graceful handling of non-convergence (return None, continue next seed)
- Dataset download failures logged with retry instructions
- OOM errors caught with batch size reduction suggestion

### NFR-4: Code Quality

- Type hints for all public functions
- Docstrings for AblationTrainer class and key methods
- Config dataclass for hyperparameters
- Separation: data loading, training, evaluation, visualization modules

---

## Data Specifications

### Input Data

| Dataset | Source | Size | Splits | Format |
|---------|--------|------|--------|--------|
| CMNIST | Torchvision MNIST + coloring | ~70K images | Train/Val/Test | PNG tensors |
| Waterbirds | Wilds benchmark | ~4.8K images | Standard Wilds | JPEG |
| CelebA | Torchvision CelebA | ~200K images | Standard splits | JPEG |
| NICO++ | Official repo | ~20K images | Standard splits | JPEG |

### Output Data

- Convergence data CSV: ~40 rows (4 datasets × 10 seeds)
- Statistical summary JSON: ~1KB
- Figures: 4 PNG files, ~500KB total
- Model checkpoints (optional): ~180MB per checkpoint

---

## Success Metrics

### Phase 4 PoC Gate (MUST_WORK)

**PoC Pass Criteria:**
1. Code runs without errors across all 4 datasets
2. Direction check: E_s < E_c for majority (>5/10) seeds on ALL datasets
3. Magnitude check: mean(Δ) ≥ 2 epochs on at least 2/4 datasets

**PoC Fail → Blocks Phase 4 for dependent hypotheses**

### Full Statistical Validation

**Full Pass Criteria:**
1. All datasets: p < 0.05 (paired t-test)
2. At least 3/4 datasets: mean(Δ) ≥ 2 epochs

**Full Fail → Main hypothesis H-TemporalGradient-v1 falsified**

---

## Dependencies

### Prerequisites
- None (FOUNDATION hypothesis)

### External Dependencies
- PyTorch ≥1.12
- Torchvision ≥0.13
- Wilds library (pip install wilds)
- NICO++ dataset (manual download from official repo)
- scipy, numpy, matplotlib, pandas

### Dependent Hypotheses (Blocked if h-e1 fails)
- h-e2: Multi-metric temporal signature
- h-e3: Continuous GradCAM ratio diagnostic
- h-m1: Feature complexity mechanism
- h-m2: Architectural modulation (CNN vs ViT)

---

## Out of Scope

- Performance optimization beyond PoC validation
- Additional datasets beyond the 4 specified
- Comparison with debiasing methods (reserved for h-c1)
- Continuous monitoring during training (reserved for h-e3)
- Architecture ablations beyond ResNet (reserved for h-m2)

---

## Implementation Phases

### Phase 4a: Data Infrastructure (Epic 1-2)
- Dataset loaders for all 4 benchmarks
- Feature extraction methods (spurious-only, core-only)
- Preprocessing pipelines

### Phase 4b: Training Infrastructure (Epic 3-4)
- AblationTrainer class with gradient tracking
- Convergence detection logic
- Multi-seed experiment runner

### Phase 4c: Evaluation & Visualization (Epic 5-6)
- Statistical testing implementation
- Figure generation pipeline
- Results persistence

### Phase 4d: Validation (Epic 7-8)
- End-to-end testing on 1 seed per dataset
- Full 40-run execution
- Gate criteria verification

---

## Open Questions

1. **Convergence criterion sensitivity:** Is 10% threshold robust across datasets? (Test with 5%, 15% variants)
2. **Feature masking quality:** Do current masking methods truly isolate spurious vs. core? (Validate with attribution methods)
3. **Pretrained initialization impact:** Does ImageNet pretraining bias convergence order? (Optional ablation: random init)

---

## Approval & Sign-off

**Phase 2C Experiment Brief:** 02c_experiment_brief.md ✓
**Baseline Methods:** ERM training (standard)
**Task Budget:** LIGHT tier (≤15 tasks)
**Next Step:** Architecture design (Step 3)

---

*Generated from Phase 2C experiment brief for h-e1*
*MUST_WORK gate: Failure blocks entire hypothesis pipeline*
