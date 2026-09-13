# Product Requirements Document: H-M-INTEGRATED
## Causal Mechanism Validation for Gradient Abnormality

**Hypothesis ID:** h-m-integrated  
**Type:** MECHANISM (MUST_WORK gate)  
**Prerequisites:** h-e1 (COMPLETED)  
**Version:** 1.0  
**Date:** 2026-08-20  

---

## 1. Executive Summary

**Objective:** Validate the 4-step causal mechanism linking spurious training to gradient abnormality.

**Core Mechanism:**
1. Model learns spurious shortcut (correlation rate → model bias)
2. Minority samples create conflict (lack expected spurious feature)
3. Conflict manifests as gradient scattering (GAIA-Z divergence)
4. GAIA metrics quantify scattering (divergence correlates with WGA)

**Success Criteria:** (Correlation ρ > 0.7, p < 0.05) AND (Augmentation reduction ≥ 30%) AND (Minority accuracy ≥ 60%)

**Implementation Tier:** 2 (Medium complexity)  
**Estimated Budget:** 60 hours  

---

## 2. Requirements

### 2.1 Functional Requirements

**FR-1: Correlation Rate Training Suite**
- Train 10 ResNet-50 models on Waterbirds with correlation rates: 50%, 55%, 60%, 65%, 70%, 75%, 80%, 85%, 90%, 95%
- Each model: 300 epochs, SGD (lr=1e-3), early stopping (patience 50)
- Record worst-group accuracy per model on fixed test set (4795 samples)

**FR-2: GAIA Divergence Measurement**
- Extract GAIA-Z scores for all 4795 test samples × 10 models
- Compute divergence = mean(minority GAIA-Z) - mean(majority GAIA-Z)
- Minority groups: [1, 2], Majority groups: [0, 3]

**FR-3: Correlation Analysis**
- Compute Pearson correlation: ρ(GAIA_divergence, WGA)
- Statistical test: p-value (two-tailed)
- Visualization: scatter plot with trendline

**FR-4: Background Augmentation Pipeline**
- Select 200 minority samples (100 waterbird-land, 100 landbird-water)
- Segment bird foreground using SegFormer-B5
- Swap backgrounds: waterbird-land → water, landbird-water → land
- Compute GAIA-Z reduction (original vs augmented)

**FR-5: Minority Classification Validation**
- Measure minority accuracy on 90% correlation model
- Gate threshold: ≥ 60%

### 2.2 Non-Functional Requirements

**NFR-1: Reproducibility**
- Fixed seeds per correlation rate
- Deterministic resampling logic
- Checkpoint all 10 trained models

**NFR-2: Computational Efficiency**
- Total GPU budget: ≤ 35 hours (single V100)
- Parallelizable: 10 model training runs independent

**NFR-3: Statistical Rigor**
- All tests: two-tailed, α = 0.05
- Effect sizes: Cohen's d for augmentation test
- Confidence intervals: 95% for all estimates

---

## 3. System Architecture

### 3.1 Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                  Correlation Experiment                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐   ┌──────────────┐   ┌─────────────┐ │
│  │ Resampler   │──>│ Multi-Train  │──>│ GAIA Extract│ │
│  │ (10 rates)  │   │ (10 models)  │   │ (4795×10)   │ │
│  └─────────────┘   └──────────────┘   └─────────────┘ │
│                                              │          │
│                                              v          │
│                                     ┌─────────────────┐ │
│                                     │ Correlation     │ │
│                                     │ Analyzer        │ │
│                                     └─────────────────┘ │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              Background Augmentation Experiment         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐   ┌──────────────┐   ┌─────────────┐ │
│  │ Sample      │──>│ SegFormer    │──>│ Background  │ │
│  │ Selector    │   │ Segmenter    │   │ Compositor  │ │
│  │ (200 min)   │   │ (bird mask)  │   │ (foreground)│ │
│  └─────────────┘   └──────────────┘   └─────────────┘ │
│                                              │          │
│                                              v          │
│                                     ┌─────────────────┐ │
│                                     │ GAIA-Z Compare │ │
│                                     │ (paired t-test)│ │
│                                     └─────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Data Flow

**Input:** Waterbirds dataset (WILDS)  
**Output:** 
- 10 trained models (checkpoints)
- GAIA divergence per correlation rate (CSV)
- Correlation analysis results (JSON + plot)
- Augmentation reduction statistics (JSON)
- Minority accuracy (scalar)

---

## 4. Technical Specifications

### 4.1 Dataset Resampling

**Algorithm:** Stratified sampling with replacement
- Target correlation: P(place=water | y=waterbird) = P(place=land | y=landbird)
- Original: 95% (4602 majority, 192 minority)
- Example (50% correlation): equal samples per group

**Implementation:**
```python
def resample_waterbirds(metadata_df, target_corr, seed):
    # Group by (y, place)
    # Compute target counts per group: n_group = (total_samples / 4) × (1 ± (target_corr - 0.5))
    # Majority groups: n_group = total × target_corr / 2
    # Minority groups: n_group = total × (1 - target_corr) / 2
    # Resample with replacement to match target counts
    return resampled_df
```

### 4.2 Model Training

**Architecture:** ResNet-50 (torchvision)
- Pretrained: ImageNet
- Modification: FC layer (2048 → 2)

**Hyperparameters:**
- Optimizer: SGD (lr=1e-3, momentum=0.9, weight_decay=1e-4)
- Scheduler: CosineAnnealingLR (T_max=300, eta_min=0)
- Batch size: 128
- Epochs: 300
- Early stopping: patience=50 on worst-group val accuracy

### 4.3 Background Swapping

**Segmentation Model:** SegFormer-B5 (nvidia/segformer-b5-finetuned-ade-640-640)
- Input: RGB image (224×224)
- Output: Bird segmentation mask (binary)
- Class: "bird" (ADE20K class ID)

**Compositing Logic:**
1. Extract foreground: image × mask
2. Sample random background from majority group (same class, opposite place)
3. Composite: foreground + background × (1 - mask)

### 4.4 Statistical Tests

**Test 1: Pearson Correlation**
- Variables: GAIA divergence, WGA
- N = 10 (correlation rates)
- Threshold: ρ > 0.7, p < 0.05

**Test 2: Paired t-test**
- Variables: GAIA-Z(original), GAIA-Z(augmented)
- N = 200 (minority samples)
- Threshold: mean reduction ≥ 30%, p < 0.01

---

## 5. Code Reuse from h-e1

**Directly Reusable:**
- `gaia_utils.py`: GAIA-Z computation, GradCAM extraction, statistical tests
- `waterbirds_dataset.py`: Dataset loader with group annotations
- `train_gaia.py`: Training loop skeleton

**Required Modifications:**
- Add `resample_waterbirds()` to dataset loader
- Add correlation rate parameter to training script
- Extend statistical module with `pearsonr()` wrapper

---

## 6. New Components

### 6.1 Correlation Rate Resampler
**File:** `dataset_utils.py`  
**LOC:** ~100  
**Dependencies:** pandas, numpy  
**Interface:**
```python
def resample_waterbirds(metadata_df, target_corr, seed=42) -> pd.DataFrame
```

### 6.2 Background Swapper
**File:** `augmentation_utils.py`  
**LOC:** ~200  
**Dependencies:** transformers (SegFormer), PIL, torch  
**Interface:**
```python
class BackgroundSwapper:
    def __init__(self, segmentation_model, background_pool)
    def swap_background(self, image, source_group, target_group) -> PIL.Image
```

### 6.3 Correlation Analyzer
**File:** `analysis_utils.py`  
**LOC:** ~150  
**Dependencies:** scipy, matplotlib  
**Interface:**
```python
def analyze_correlation(wga_values, gaia_divergences) -> dict[str, float]
def plot_correlation(wga_values, gaia_divergences, save_path)
```

### 6.4 Multi-Model Training Orchestrator
**File:** `train_sweep.py`  
**LOC:** ~150  
**Dependencies:** argparse, multiprocessing  
**Interface:**
```bash
python train_sweep.py --correlation_rates 50,55,60,65,70,75,80,85,90,95 --output_dir ./checkpoints
```

---

## 7. Testing Requirements

### 7.1 Unit Tests

**Test Suite 1: Resampler**
- Verify target correlation achieved (tolerance ± 2%)
- Check stratified sampling (all groups present)
- Reproducibility (same seed → same samples)

**Test Suite 2: Background Swapper**
- Segmentation quality (IoU > 0.7 on sample images)
- Compositing preserves foreground (pixel-level diff < 5%)
- Background pool sampling (random, no duplicates within experiment)

**Test Suite 3: Correlation Analyzer**
- Pearson correlation computation (vs scipy direct call)
- P-value calculation (vs scipy)
- Plot generation (no crashes, saves to disk)

### 7.2 Integration Tests

**Test 1: End-to-End Correlation Experiment**
- Train 2 models (50%, 95% correlation)
- Extract GAIA divergence
- Verify divergence(95%) > divergence(50%)

**Test 2: Augmentation Pipeline**
- Swap 10 minority samples
- Compute GAIA-Z reduction
- Verify reduction > 0% (direction check)

---

## 8. Success Metrics

### 8.1 Gate Criteria (Primary)

| Metric | Threshold | Test |
|--------|-----------|------|
| Pearson ρ | > 0.7 | Experiment 1 |
| p-value | < 0.05 | Experiment 1 |
| GAIA-Z reduction | ≥ 30% | Experiment 2 |
| Minority accuracy | ≥ 0.60 | Experiment 3 |

**Gate Logic:** (ρ > 0.7 AND p < 0.05) AND (reduction ≥ 30%) AND (minority_acc ≥ 0.60)

### 8.2 Secondary Metrics (Diagnostics)

| Metric | Expected Range | Purpose |
|--------|----------------|---------|
| GAIA divergence (90% corr) | 0.25-0.30 | Baseline abnormality |
| GAIA divergence (50% corr) | 0.05-0.10 | Low spurious baseline |
| WGA (90% corr) | 0.60-0.70 | Spurious reliance |
| WGA (50% corr) | 0.85-0.95 | Balanced training |

---

## 9. Risk Mitigation

### 9.1 Training Instability
**Risk:** Hyperparameter sensitivity across correlation rates  
**Mitigation:** Fixed hyperparameters (from h-e1), early stopping  
**Detection:** Monitor validation curves per model  

### 9.2 Segmentation Failure
**Risk:** SegFormer produces low-quality bird masks  
**Mitigation:** Manual inspection of 10 random masks, fallback to bounding boxes  
**Detection:** IoU < 0.7 on validation samples  

### 9.3 Complexity Confound
**Risk:** GAIA abnormality driven by image complexity, not spurious conflict  
**Mitigation:** Augmentation test (causal validation)  
**Detection:** Correlation passes BUT augmentation fails  

---

## 10. Deliverables

### 10.1 Code
- `dataset_utils.py` (resampler)
- `augmentation_utils.py` (background swapper)
- `analysis_utils.py` (correlation analyzer)
- `train_sweep.py` (multi-model orchestrator)
- Unit tests (3 suites, 15+ tests)

### 10.2 Data Artifacts
- 10 trained model checkpoints (ResNet-50)
- GAIA divergence CSV (10 rows: correlation_rate, wga, divergence)
- Augmentation results JSON (200 samples: original_gaia, augmented_gaia)

### 10.3 Analysis Outputs
- Correlation scatter plot (GAIA divergence vs WGA)
- Statistical report (Pearson ρ, p-value, t-test results)
- Gate decision (PASS/FAIL + failure point if applicable)

### 10.4 Documentation
- 04_validation.md (Phase 4 output)
- 04_reflection.md (failure analysis if FAIL)

---

## 11. Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Implementation | 7 days | Phase 3 complete |
| Unit Testing | 2 days | Implementation complete |
| Experiment 1 (Correlation) | 3 days | Testing complete |
| Experiment 2 (Augmentation) | 1 day | Experiment 1 complete |
| Experiment 3 (Minority Acc) | 0.5 days | Experiment 1 complete |
| Analysis & Reporting | 1.5 days | All experiments complete |
| **Total** | 15 days | - |

**Budget:** 60 hours (@ 4 hours/day)  

---

## 12. Acceptance Criteria

**PRD Approved:** All sections reviewed, no ambiguities  
**Architecture Approved:** Component diagram validated, interfaces defined  
**Logic Approved:** Algorithm correctness verified (resampler, swapper, analyzer)  
**Configuration Approved:** Hyperparameters justified, matched to h-e1  

**Phase 3 Complete:** All 4 documents (PRD, Architecture, Logic, Config) signed off  
**Ready for Phase 4:** Implementation task list generated, Archon tasks created  

---

## 13. Metadata

- **Document Type:** PRD (Product Requirements Document)
- **Hypothesis:** h-m-integrated (MECHANISM, MUST_WORK)
- **Phase:** 3 (Implementation Planning)
- **Status:** DRAFT
- **Generated:** 2026-08-20T03:00:00Z
- **Next Action:** Architecture design (parallel with Logic, Config)
