# Product Requirements Document: H-M1
# SGD Gradient Structure Analysis — Spurious vs. Core Feature Gradient Dominance

**Hypothesis ID:** H-M1
**Type:** MECHANISM (INCREMENTAL — extends H-E1)
**Gate:** MUST_WORK
**Tier:** FULL (max 30 tasks)
**Date:** 2026-05-04
**Author:** Anonymous
---

## 1. Executive Summary

This PRD specifies implementation requirements for H-M1: demonstrating that SGD's gradient structure preferentially favors spurious (background texture) features over core (bird species morphology) features during early training on Waterbirds. The experiment extends H-E1's temporal probe gap finding by providing a mechanistic explanation via gradient norm analysis.

**Primary Deliverable:** A gradient instrumentation module that measures per-epoch Gradient Dominance Ratio (GDR = spurious_grad_norm / core_grad_norm) across 3 seeds, with Wilcoxon signed-rank test confirming GDR > 1.0 in early training epochs (p < 0.05).

**Success Gate:** Mean Early GDR > 1.0 across ≥2 of 3 seeds + Wilcoxon p < 0.05.

---

## 2. Problem Statement

H-E1 established that delta(t) = spurious_probe_acc(t) - core_probe_acc(t) > 0 during early training (epochs 2–8, t*=4.0). H-M1 investigates the mechanistic cause: does SGD's gradient structure itself encode this asymmetry?

**Hypothesis:** Spurious features (lower spatial frequency / simpler statistics) generate higher gradient signal in the fc layer during early SGD optimization, directly explaining the faster spurious probe accuracy observed in H-E1.

---

## 3. Background and Context

### 3.1 Foundation (H-E1 Results)
- delta(t) > 0 window: epochs 2–8 (13.3% of training, ≥10% threshold ✅)
- t*=4.0 epochs (mean across 3 seeds)
- Wilcoxon p=0.0219, t_stat=4.619
- Same ResNet-50 + SGD config reused for controlled experiment

### 3.2 Theoretical Basis
- **Frequency Principle (Xu et al. 2019):** SGD learns low-frequency components before high-frequency ones
- **Simplicity Bias (Shah et al. 2020):** Networks preferentially fit simpler statistical patterns first
- **Spurious feature complexity:** Background texture is lower-frequency/simpler than bird morphology

---

## 4. Data Specification

### 4.1 Primary Dataset: Waterbirds

| Property | Value |
|----------|-------|
| Name | Waterbirds |
| Version | Standard (Sagawa et al. 2020) |
| Source | kohpangwei/group_DRO (GitHub) |
| Download | **MANUAL** — requires download script |
| Train | 4,795 samples |
| Validation | 1,199 samples |
| Test | 4,795 samples |
| Classes | 2 (landbird=0, waterbird=1) |
| Groups | 4 ({landbird×land, landbird×water, waterbird×land, waterbird×water}) |
| Spurious feature | Background (land=0, water=1) — 95% train correlation |
| Core feature | Bird species morphology |

**Download Instructions:**
```bash
git clone https://github.com/kohpangwei/group_DRO
cd group_DRO
python download_waterbirds.py  # or manual from CUB + Places datasets
```

**Preprocessing:**
- Resize: 256×256 → CenterCrop 224×224
- Normalize: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
- No augmentation during gradient measurement (deterministic)

**Splits Used:** Train (ERM training + gradient logging), Validation (held-out evaluation)

**Key Requirement:** Dataset loader must provide both `y` (core label) and `a` (spurious label / background) per sample.

### 4.2 Data from Previous Hypothesis (H-E1)

| Artifact | Source | Usage |
|----------|--------|-------|
| Training config | H-E1 validated | SGD hyperparameters reuse |
| t* estimate | H-E1 result (4.0 epochs) | Early window definition (epochs 1–6) |
| Seed list | H-E1 (3 seeds) | Same seeds for cross-experiment alignment |

---

## 5. Functional Requirements

### FR-1: Data Loading Module

**ID:** FR-1
**Title:** Waterbirds Dataset Loader with Dual Labels
**Description:** Load Waterbirds dataset providing both core label (y) and spurious label (a) per sample, using GroupDRO loader.
**Acceptance Criteria:**
- Returns (image, core_label, spurious_label, group_id) per sample
- Handles all 3 splits (train/val/test)
- Deterministic with fixed seed

### FR-2: ResNet-50 ERM Baseline

**ID:** FR-2
**Title:** Standard ERM Training (ResNet-50)
**Description:** Train ResNet-50 with CrossEntropy on core label using SGD — identical to H-E1 configuration.
**Acceptance Criteria:**
- SGD: lr=1e-3, momentum=0.9, weight_decay=1e-4
- Batch size: 64
- 30 epochs total
- Checkpoint saved every 2 epochs (15 checkpoints)
- 3 random seeds executed

### FR-3: Gradient Instrumentation Module

**ID:** FR-3
**Title:** GradientAlignmentAnalyzer — Core Mechanism
**Description:** Instrument ResNet-50 fc layer to measure gradient norms projected onto spurious-label and core-label directions via separate backward passes.
**Acceptance Criteria:**
- Register backward hook on `model.fc.weight`
- Separate forward pass for spurious_label targets → spurious_grad_norm
- Separate forward pass for core_label targets → core_grad_norm
- GDR = spurious_grad_norm / (core_grad_norm + 1e-8) computed per epoch
- Logged at every 2-epoch checkpoint (matching H-E1 intervals)
- No architectural modification to ResNet-50

**Pseudo-code:**
```python
class GradientAlignmentAnalyzer:
    def compute_label_gradient_norm(self, features, label_tensor, criterion) -> float
    def log_epoch_gradients(self, loader, spurious_labels, core_labels, criterion) -> float
    def extract_features(self, loader) -> Tensor
```

### FR-4: Primary Metric — Gradient Dominance Ratio (GDR)

**ID:** FR-4
**Title:** GDR Computation and Logging
**Description:** Compute GDR(t) = spurious_grad_norm(t) / core_grad_norm(t) at each checkpoint, log per seed.
**Acceptance Criteria:**
- GDR logged for all 15 checkpoints (epochs 2,4,...,30)
- Per-seed GDR arrays stored as numpy arrays
- Mean Early GDR = mean(GDR[epochs 1–6]) computed
- CSV/JSON export of GDR time series per seed

### FR-5: Statistical Validation — Wilcoxon Test

**ID:** FR-5
**Title:** Wilcoxon Signed-Rank Test on Early Window
**Description:** Apply one-sided Wilcoxon signed-rank test to confirm spurious_norms > core_norms in early training window.
**Acceptance Criteria:**
- Test: `wilcoxon(spurious_norms_early, core_norms_early, alternative='greater')`
- Early window: first 3 checkpoints (epochs 2, 4, 6)
- Report: stat, p-value per seed
- PASS condition: p < 0.05 in ≥2 of 3 seeds

### FR-6: Temporal Alignment Validation

**ID:** FR-6
**Title:** Pearson Correlation — GDR vs delta(t)
**Description:** Cross-validate gradient dominance with H-E1 probe gap by computing Pearson correlation between GDR(t) and delta(t) across matching checkpoints.
**Acceptance Criteria:**
- Load H-E1 delta(t) values (from h-e1 experiment output)
- Compute Pearson r(GDR, delta) over all 15 checkpoints
- Report r, p-value per seed
- Expected: positive correlation (r > 0.3)

### FR-7: Visualization

**ID:** FR-7
**Title:** Result Figures
**Description:** Generate publication-quality figures for gradient analysis results.
**Acceptance Criteria:**
- **Figure 1 (Required):** Bar chart of mean Early GDR vs. 1.0 threshold with error bars (3 seeds)
- **Figure 2:** GDR(t) line plot overlaid with delta(t) from H-E1 (15 checkpoints)
- **Figure 3:** Dual-axis plot of spurious_grad_norm(t) and core_grad_norm(t) with seed variance bands
- **Figure 4:** Violin plots of GDR distribution: early window (epochs 1–6) vs. late (epochs 25–30)
- Output location: `h-m1/figures/`

### FR-8: Experiment Runner

**ID:** FR-8
**Title:** Multi-Seed Experiment Orchestration
**Description:** Run the full gradient analysis experiment across 3 seeds, aggregate results.
**Acceptance Criteria:**
- Execute 3 seeds sequentially or in parallel
- Aggregate: mean_early_GDR, std_early_GDR across seeds
- Gate check: `assert mean_early_GDR > 1.0`
- Generate summary JSON with all metrics
- PASS/FAIL determination printed

---

## 6. Non-Functional Requirements

### NFR-1: Reproducibility
- All experiments use fixed random seeds (same 3 seeds as H-E1)
- No stochastic elements during gradient measurement (model.eval())
- Results reproducible from `03_tasks.yaml` task list

### NFR-2: Controlled Experiment
- Training config identical to H-E1 (same SGD hyperparameters, same epochs, same checkpoint interval)
- Only new variable: gradient instrumentation hooks
- No data augmentation during gradient measurement

### NFR-3: Computational Efficiency
- Gradient computation uses frozen backbone features (no full backward through ResNet-50 backbone)
- Memory-efficient: process validation set in batches
- Target: ≤2x overhead vs. plain ERM training

### NFR-4: Code Reuse from H-E1
- Extend H-E1 codebase where possible
- Same dataset loader, same training loop structure
- New module: `gradient_analyzer.py` added to existing structure

---

## 7. Technical Dependencies

### 7.1 Python Packages

```
torch>=1.12.0
torchvision>=0.13.0
numpy>=1.21.0
scipy>=1.7.0
matplotlib>=3.5.0
seaborn>=0.11.0
pandas>=1.3.0
pyyaml>=5.4.0
tqdm>=4.62.0
```

### 7.2 External Repositories

| Repository | URL | Purpose |
|------------|-----|---------|
| GroupDRO | https://github.com/kohpangwei/group_DRO | Waterbirds dataset loader, ResNet-50 ERM baseline |
| DFR | https://github.com/PolinaKirichenko/dfr | Gradient hook patterns, checkpoint analysis |

### 7.3 Internal Dependencies (H-E1)

| Artifact | Path | Usage |
|----------|------|-------|
| H-E1 codebase | h-e1/code/ | Extend training loop |
| H-E1 delta(t) results | h-e1/results/ | Temporal alignment validation (FR-6) |

---

## 8. Success Criteria

### 8.1 Primary Gate (MUST_WORK)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mean Early GDR > 1.0 | ≥2 of 3 seeds | mean(GDR[epochs 1–6]) |
| Wilcoxon p < 0.05 | ≥2 of 3 seeds | wilcoxon(spurious, core, alternative='greater') |

### 8.2 Secondary Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Temporal alignment | Pearson r > 0.0 | corr(GDR(t), delta(t)) from H-E1 |
| GDR convergence | GDR → 1.0 near t* | Visual inspection |
| Code runs without error | 100% | All 3 seeds complete |

### 8.3 Failure Response
- IF GDR ≈ 1.0 throughout → Explore alternative complexity proxies (eigenspectrum, activation variance)
- IF mechanism not confirmed → Document as LIMITATION (H-E1 finding stands independently)

---

## 9. Out of Scope

- CelebA replication (H-M1 PoC uses Waterbirds only)
- Full 300-epoch training (PoC uses 30 epochs)
- Gradient analysis on intermediate backbone layers (fc layer only)
- Fourier decomposition of gradient tensors (GDR via norm sufficient for PoC)

---

## 10. Implementation Notes

- **Gradient hook approach**: Compute gradient of CrossEntropy loss w.r.t. `model.fc.weight` using separate backward passes for spurious_label and core_label targets
- **Feature extraction**: Use `model.eval()` + `torch.no_grad()` for backbone, then enable grad only for fc layer
- **Checkpoint alignment**: Gradient measurement at same 2-epoch intervals as H-E1 linear probing for direct comparison
- **CUDA**: Use single GPU (CUDA_VISIBLE_DEVICES set per CLAUDE.md)

---

*PRD generated inline (BMAD PRD workflow.md not found — generated from Phase 2C experiment brief)*
*Hypothesis: H-M1 | Phase 3 Step 2 | Date: 2026-05-04*
