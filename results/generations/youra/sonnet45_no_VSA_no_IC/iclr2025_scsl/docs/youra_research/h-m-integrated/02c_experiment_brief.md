# Experiment Brief: H-M-INTEGRATED (4-Step Causal Mechanism Validation)

**Hypothesis ID:** h-m-integrated  
**Type:** MECHANISM  
**Gate:** MUST_WORK  
**Prerequisites:** h-e1 (COMPLETED)  
**Generated:** 2026-08-20  

---

## 1. Hypothesis Statement

**Core Claim:** The causal mechanism linking spurious training to gradient abnormality follows a 4-step chain:
1. Model learns spurious shortcut (correlation rate → model bias)
2. Minority samples create conflict (minority samples lack expected spurious feature)
3. Conflict manifests as gradient scattering (measured by GAIA-Z divergence)
4. GAIA metrics quantify scattering (divergence correlates with worst-group accuracy)

**Rationale:** While h-e1 proved minority groups exhibit gradient abnormality, this hypothesis validates *why* — establishing the mechanistic link between spurious reliance and observable gradient patterns.

---

## 2. Success Criteria (PoC: Direction-based)

### Primary Criteria (MUST pass both)
1. **Correlation Test:** GAIA divergence (minority-majority gap) correlates with worst-group accuracy across varying correlation rates
   - Metric: Pearson ρ > 0.7, p < 0.05
   - Why: Validates Step 1→3 (spurious reliance → gradient scattering)

2. **Augmentation Causality Test:** Background swap on minority samples reduces GAIA-Z by ≥30%
   - Metric: Mean GAIA-Z reduction ≥30% after background swap
   - Why: Validates Step 2 (conflict resolution eliminates abnormality)

### Secondary Criteria (gate fail if violated)
3. **Minority Classification Validity:** Minority samples classified correctly ≥60% of time
   - Metric: Test-set minority accuracy ≥ 0.60
   - Why: Ensures GradCAM highlights learned features (not random noise)

### Gate Logic
- **Pass:** Primary (1 AND 2) AND Secondary (3)
- **Fail:** Identify failure point (which step 1/2/3/4 breaks), pivot to detection-only

---

## 3. Experimental Design

### 3.1 Experiment 1: Correlation Rate Sweep (Step 1→3 validation)

**Objective:** Validate GAIA divergence increases with spurious reliance (correlation rate)

**Procedure:**
1. **Train Models:** Train 10 ResNet-50 models on Waterbirds with varying spurious correlation rates
   - Correlation rates: 50%, 55%, 60%, 65%, 70%, 75%, 80%, 85%, 90%, 95%
   - Model: ResNet-50 pretrained, SGD (lr=1e-3), 300 epochs
   - Dataset: Waterbirds (5794 train samples, resampled by correlation rate)
   
2. **Measure WGA:** Record worst-group accuracy for each model on standard test set (4795 samples)

3. **Compute GAIA Divergence:** For each model:
   - Extract GAIA-Z scores on all 4795 test samples (using h-e1 pipeline)
   - Compute divergence = mean(minority GAIA-Z) - mean(majority GAIA-Z)
   - Minority groups: [1, 2], Majority groups: [0, 3]

4. **Correlation Analysis:**
   - Compute Pearson correlation: ρ(GAIA_divergence, WGA)
   - Expected: ρ > 0.7 (strong negative correlation: higher divergence → lower WGA)
   - Statistical test: p < 0.05 (two-tailed)

**Dataset Details:**
- **Name:** Waterbirds
- **Type:** standard (real dataset via WILDS)
- **Size:** 
  - Train: 5794 samples (resampled per correlation rate)
  - Val: 1199 samples
  - Test: 4795 samples (fixed for all models)
- **Source:** `wilds.get_dataset('waterbirds', root_dir='./data/wilds_cache')`
- **Resampling Method:** Stratified sampling per (y, place) to achieve target correlation rate
  - Correlation = P(place=water | y=waterbird) = P(place=land | y=landbird)
  - Original: 95% correlation (4602 majority, 192 minority)
  - Target rates: adjust sampling weights to balance majority/minority ratio

**Model Details:**
- **Architecture:** ResNet-50 (torchvision.models.resnet50)
- **Pretrained:** ImageNet (pretrained=True)
- **Modification:** Replace final FC layer (in_features=2048, out_features=2)
- **Training:**
  - Optimizer: SGD (lr=1e-3, momentum=0.9, weight_decay=1e-4)
  - Scheduler: CosineAnnealingLR (T_max=300, eta_min=0)
  - Loss: CrossEntropyLoss
  - Batch size: 128
  - Epochs: 300
  - Early stopping: Patience 50 epochs on worst-group val accuracy

**Expected Results:**
- **High correlation (90-95%):** WGA ≈ 0.60-0.70, GAIA divergence ≈ 0.25-0.30
- **Medium correlation (70-80%):** WGA ≈ 0.75-0.85, GAIA divergence ≈ 0.15-0.20
- **Low correlation (50-60%):** WGA ≈ 0.85-0.95, GAIA divergence ≈ 0.05-0.10

**Computational Cost:**
- **Training:** 10 models × 300 epochs × 45 train batches/epoch ≈ 135,000 iterations (≈30 GPU hours total on single V100)
- **Evaluation:** 10 models × 4795 test samples × GradCAM extraction ≈ 1-2 GPU hours
- **Total:** ~32 GPU hours

---

### 3.2 Experiment 2: Background Augmentation Test (Step 2 validation)

**Objective:** Validate conflict resolution (background swap) causally reduces gradient abnormality

**Procedure:**
1. **Select Test Model:** Use 90% correlation model from Experiment 1 (highest expected divergence)

2. **Sample Selection:** Select 200 minority samples from test set
   - 100 waterbird-land (group 1)
   - 100 landbird-water (group 2)
   - Criterion: Model predicts correctly (to ensure GradCAM validity)

3. **Background Swap Augmentation:**
   - For each minority sample: swap background to match majority group
     - Waterbird-land → waterbird-water (group 0 background)
     - Landbird-water → landbird-land (group 3 background)
   - Method: Copy-paste foreground onto majority background using segmentation masks
   - Segmentation: Use pretrained SegFormer (nvidia/segformer-b5-finetuned-ade-640-640) to extract bird mask
   - Background pool: Random sample from majority group (same class, opposite place)

4. **GAIA-Z Comparison:**
   - Compute GAIA-Z for original minority samples (baseline)
   - Compute GAIA-Z for augmented samples (conflict-resolved)
   - Measure reduction: reduction_pct = (baseline_mean - augmented_mean) / baseline_mean × 100%

5. **Statistical Test:**
   - Paired t-test: GAIA-Z(original) vs GAIA-Z(augmented)
   - Expected: mean reduction ≥ 30%, p < 0.01

**Dataset Details:**
- **Source:** 200 minority samples from Waterbirds test set (4795 total)
- **Background Pool:** 1000 majority samples (500 per class) for background extraction
- **Segmentation Model:** SegFormer-B5 (ADE20K-finetuned, class 'bird')

**Implementation References (from Exa search):**
- Background swap code: `kohpangwei/group_DRO/dataset_scripts/generate_waterbirds.py` (baseline implementation)
- Modern approach: "Automated Background Swapping for Robustness" (2606.32018) — uses segmentation + inpainting

**Expected Results:**
- **Original minority samples:** Mean GAIA-Z ≈ 0.40-0.45 (from h-e1 validation)
- **Augmented samples:** Mean GAIA-Z ≈ 0.25-0.30 (≈35% reduction)
- **Interpretation:** Removing spurious conflict (background mismatch) reduces gradient scattering

**Computational Cost:**
- **Segmentation:** 200 samples × SegFormer inference ≈ 5 minutes (GPU)
- **Background compositing:** 200 samples × PIL operations ≈ 2 minutes (CPU)
- **GAIA-Z extraction:** 400 samples (200 original + 200 augmented) × GradCAM ≈ 10 minutes (GPU)
- **Total:** ~20 minutes

---

### 3.3 Experiment 3: Minority Classification Validity (Step 3 validation)

**Objective:** Verify minority samples are classified correctly ≥60% to ensure GradCAM spatial masking validity

**Procedure:**
1. **Use Test Model:** Same 90% correlation model from Experiment 1

2. **Compute Minority Accuracy:**
   - Evaluate all minority test samples (groups 1, 2)
   - Metric: accuracy = correct_predictions / total_minority_samples

3. **Gate Check:**
   - If accuracy ≥ 0.60: GradCAM highlights learned features (PASS)
   - If accuracy < 0.60: GradCAM may highlight noise (FAIL → fallback to global regularization)

**Expected Results:**
- **Minority accuracy:** 0.65-0.75 (from GroupDRO baseline: ~70%)
- **Interpretation:** Model learns core features even with spurious reliance, enabling GradCAM-based spatial masking

**Computational Cost:**
- Single forward pass on 192 minority test samples ≈ 1 minute (GPU)

---

## 4. Implementation Plan

### 4.1 Code Reuse from h-e1

**Directly Reusable:**
- `gaia_utils.py`: GAIA-Z computation, GradCAM extraction, statistical tests
- `waterbirds_dataset.py`: Dataset loader with group annotations
- `train_gaia.py`: Training loop skeleton

**Modifications Needed:**
- Add correlation rate resampling in dataset loader
- Add background swap augmentation module (new)
- Add correlation analysis module (scipy.stats.pearsonr)

### 4.2 New Components

**Component 1: Correlation Rate Resampler**
```python
# dataset_utils.py
def resample_waterbirds(df, target_correlation, seed=42):
    """
    Resample training set to achieve target correlation.
    
    Args:
        df: metadata DataFrame (y, place, split)
        target_correlation: float in [0.5, 1.0]
    
    Returns:
        resampled_df: stratified sample
    """
    # Correlation = P(place | y)
    # 90% correlation → 90% waterbird-water, 10% waterbird-land, etc.
    # Implementation: stratified sampling with adjusted weights
```

**Component 2: Background Swapper**
```python
# augmentation_utils.py
class BackgroundSwapper:
    """Swap backgrounds for minority samples."""
    
    def __init__(self, segmentation_model, background_pool):
        self.seg_model = segmentation_model  # SegFormer
        self.bg_pool = background_pool  # {group_id: [images]}
    
    def swap_background(self, image, source_group, target_group):
        """
        Extract foreground from image, composite onto target background.
        
        Returns:
            augmented_image: PIL Image
        """
        # 1. Segment foreground (bird mask)
        # 2. Sample random background from target group
        # 3. Composite foreground onto background
```

**Component 3: Correlation Analyzer**
```python
# analysis_utils.py
def analyze_correlation(wga_values, gaia_divergences):
    """
    Compute Pearson correlation + visualization.
    
    Returns:
        {rho, p_value, scatter_plot}
    """
    rho, p = scipy.stats.pearsonr(gaia_divergences, wga_values)
    # Plot scatter with trendline
```

### 4.3 Implementation Complexity Assessment

**Tier:** 2 (Medium complexity)
- **Rationale:** Builds on h-e1 infrastructure, adds 3 new modules (resampler, swapper, analyzer)
- **Estimated LOC:** ~600 lines (300 new + 300 modified from h-e1)
- **Key Challenges:**
  1. Correlation rate resampling: stratified sampling with replacement
  2. Background swapping: segmentation model integration + PIL compositing
  3. Multi-model training: hyperparameter sweep + checkpoint management

**Budget Estimate:** 60 hours (2 weeks at 30 hrs/week)
- Design/planning: 8 hours
- Implementation: 30 hours (10h resampler, 12h swapper, 8h analyzer)
- Testing: 12 hours (unit tests + integration tests)
- Validation: 10 hours (run experiments, analyze results)

---

## 5. Validation Metrics

### 5.1 Primary Metrics

| Metric | Threshold | Source | Notes |
|--------|-----------|--------|-------|
| Pearson ρ (GAIA-WGA correlation) | > 0.7 | Experiment 1 | Strong correlation validates Step 1→3 |
| p-value (correlation) | < 0.05 | Experiment 1 | Statistical significance |
| GAIA-Z reduction (augmentation) | ≥ 30% | Experiment 2 | Causal validation of Step 2 |
| Minority accuracy | ≥ 0.60 | Experiment 3 | Spatial masking validity (Step 3) |

### 5.2 Secondary Metrics (diagnostics)

| Metric | Expected Range | Purpose |
|--------|----------------|---------|
| GAIA divergence (90% corr) | 0.25-0.30 | Baseline abnormality magnitude |
| GAIA divergence (50% corr) | 0.05-0.10 | Low spurious reliance baseline |
| Augmented GAIA-Z | 0.25-0.30 | Post-conflict resolution |
| Original GAIA-Z | 0.40-0.45 | Pre-conflict resolution |

### 5.3 Gate Logic

```
PASS = (ρ > 0.7 AND p < 0.05) AND (reduction ≥ 30%) AND (minority_acc ≥ 0.60)
```

**Failure Modes:**
1. **Correlation fails (ρ < 0.7):** Step 1→3 breaks → investigate which step
   - Check: Does WGA actually vary with correlation rate? (Step 1)
   - Check: Does GAIA divergence vary with correlation rate? (Step 3)
2. **Augmentation fails (reduction < 30%):** Step 2 breaks → conflict not causal
   - Fallback: detection-only (skip h-m-mitigate)
3. **Minority accuracy fails (< 60%):** Step 3 invalid → GradCAM unreliable
   - Fallback: global regularization (no spatial masking)

---

## 6. Risk Mitigation

### 6.1 Assumption A3: Complexity Confound

**Risk:** GAIA abnormality caused by image complexity, not spurious conflict

**Mitigation (Built-in):**
- Waterbirds dataset: controlled backgrounds (forest vs water), similar complexity
- Augmentation test (Experiment 2): causal validation — swapping background (not complexity) reduces abnormality

**Detection:** If correlation test passes BUT augmentation test fails → complexity confound likely

### 6.2 Assumption A1: Minority Accuracy

**Risk:** Minority samples misclassified → GradCAM highlights noise

**Mitigation (Built-in):**
- Experiment 3 explicitly measures minority accuracy
- Gate threshold: ≥ 60% (from SPROD 2025: minority accuracy ~70%)

**Fallback:** If < 60% → global regularization (no spatial masking)

### 6.3 Training Instability

**Risk:** 10 model training runs with different correlation rates → hyperparameter sensitivity

**Mitigation:**
- Use same hyperparameters across all runs (from h-e1 validation)
- Early stopping on worst-group val accuracy (prevents overfitting)
- Fixed seed per correlation rate (reproducibility)

---

## 7. Expected Outcomes

### 7.1 Success Scenario (PASS gate)

**Results:**
- **Experiment 1:** ρ = 0.75-0.85, p < 0.001 (strong correlation)
- **Experiment 2:** Reduction = 35-40%, p < 0.001 (causal effect)
- **Experiment 3:** Minority accuracy = 0.70-0.75 (valid GradCAM)

**Interpretation:** 4-step causal mechanism validated → proceed to h-m-mitigate (spatial regularization)

**Next Steps:** Phase 3 implementation planning for h-m-mitigate

---

### 7.2 Failure Scenario 1: Correlation fails, Augmentation passes

**Results:**
- **Experiment 1:** ρ = 0.4-0.6, p > 0.05 (weak/no correlation)
- **Experiment 2:** Reduction = 35%, p < 0.01 (causal effect present)
- **Experiment 3:** Minority accuracy = 0.70 (valid)

**Interpretation:** Step 2 (conflict → scattering) works, but Step 1 or 4 fails
- Possible cause: WGA doesn't vary enough with correlation rate (Step 1)
- Possible cause: GAIA divergence insensitive to WGA changes (Step 4)

**Action:** 
1. Investigate Step 1: plot WGA vs correlation rate (expect monotonic decrease)
2. Investigate Step 4: plot GAIA divergence vs correlation rate (expect monotonic increase)
3. If Step 1 fails: training issue (hyperparameters, early stopping)
4. If Step 4 fails: GAIA metric limitation (pivot to detection-only)

**Gate Decision:** EXPLORE → identify failure point, reframe hypothesis

---

### 7.3 Failure Scenario 2: Augmentation fails, Correlation passes

**Results:**
- **Experiment 1:** ρ = 0.80, p < 0.01 (strong correlation)
- **Experiment 2:** Reduction = 10-15%, p > 0.05 (no causal effect)
- **Experiment 3:** Minority accuracy = 0.70 (valid)

**Interpretation:** Step 1→3 holds (correlation exists), but Step 2 fails (conflict not causal)
- Possible cause: GAIA abnormality driven by factors other than spurious conflict
- Possible cause: Background swap doesn't remove conflict (segmentation failure)

**Action:**
1. Visual inspection: check segmentation quality (bird masks)
2. Ablation: try manual background swap (ground truth masks)
3. If manual swap works: segmentation issue (fix implementation)
4. If manual swap fails: spurious conflict not causal → complexity or other factor

**Gate Decision:** PIVOT → detection-only (abandon h-m-mitigate)

---

### 7.4 Failure Scenario 3: Minority accuracy < 60%

**Results:**
- **Experiment 3:** Minority accuracy = 0.45-0.55 (below threshold)

**Interpretation:** Model relies too heavily on spurious features → core features not learned
- GradCAM spatial masking invalid (highlights spurious, not core)

**Action:**
1. Train longer (more epochs, weaker early stopping)
2. Add augmentation during training (reduce spurious reliance)
3. If still fails: fall back to global regularization (no spatial masking)

**Gate Decision:** PIVOT → global regularization variant of h-m-mitigate

---

## 8. Timeline Estimate

| Task | Duration | Dependencies |
|------|----------|--------------|
| **Design & Planning** | 1 day | Phase 2C approval |
| **Implementation** | 7 days | - |
| - Correlation resampler | 2 days | - |
| - Background swapper | 3 days | Segmentation model integration |
| - Correlation analyzer | 1 day | - |
| - Integration testing | 1 day | All components |
| **Experiment 1 (Correlation Sweep)** | 3 days | Implementation complete |
| - Model training (10 models) | 2 days | Parallelizable on multi-GPU |
| - GAIA extraction + analysis | 1 day | - |
| **Experiment 2 (Augmentation)** | 1 day | Experiment 1 complete |
| **Experiment 3 (Minority Acc)** | 0.5 days | Experiment 1 complete |
| **Analysis & Reporting** | 1 day | All experiments complete |
| **Total** | 13.5 days (~2 weeks) | - |

**Parallelization Opportunities:**
- Experiment 2 & 3 can run in parallel (both use 90% correlation model)
- Total wall-clock time: ~11 days with parallelization

---

## 9. Archon KB Insights

**Search Query:** "gradient correlation spurious mechanism validation"

**Key Findings:** No directly relevant prior work in Archon KB (results were diffusion model pipelines, not spurious correlation analysis)

**Conclusion:** Novel experiment design — no existing template to follow

---

## 10. Exa Implementation References

**Search 1:** "spurious correlation minority group gradient analysis waterbirds augmentation"

**Relevant Papers:**
1. **GAIA (NeurIPS 2023):** Original gradient abnormality framework (OOD detection)
   - Extends to subpopulation shift (our novelty)
2. **Bias Leaves a Gradient Trail (2605.28780):** Label-free bias identification via gradients
   - Similar concept: gradients reveal spurious reliance
3. **Nuisances via Negativa (2210.01302):** Data augmentation for spurious correlations
   - Validates augmentation approach (Experiment 2)

**Search 2:** "waterbirds background swap augmentation implementation pytorch code"

**Implementation References:**
1. **GroupDRO generate_waterbirds.py:** Original Waterbirds creation script
   - Shows background compositing logic (copy-paste method)
   - URL: `github.com/kohpangwei/group_DRO/blob/master/dataset_scripts/generate_waterbirds.py`
2. **Automated Background Swapping (2606.32018):** Modern segmentation-based approach
   - Uses SegFormer for bird segmentation + inpainting
   - More robust than manual bounding boxes

**Search 3:** "pearson correlation spurious correlation rate worst-group accuracy implementation"

**References:**
1. **Spurious Correlations Survey (2402.12715):** Comprehensive taxonomy
   - Section 4.2: Correlation rate vs WGA (empirical studies)
2. **Challenges in Worst-Group Generalization (2306.11957):** Empirical analysis
   - Figure 3: WGA vs correlation rate (validates our Experiment 1 design)

---

## 11. Codebase Analysis (Serena)

**Attempted:** Symbol search for "gradient" and "correlation" utilities

**Result:** Serena requires active project selection (error: "No active project")

**Fallback:** Manual file inspection (via `find` command)

**Key Finding:** h-e1 implementation at `/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_scsl/h-e1/`
- **gaia_utils.py:** Complete GAIA-Z, GradCAM, statistical test utilities
- **waterbirds_dataset.py:** Dataset loader with group annotations
- **train_gaia.py:** Training loop

**Reuse Strategy:** 
- Copy h-e1 infrastructure to h-m-integrated/
- Modify dataset loader for correlation resampling
- Add background swapper as new module
- Add correlation analyzer as new module

---

## 12. Summary

**Experiment Scale:** 3 experiments, 10 model training runs, ~32 GPU hours
- **NOT trivially small:** Full Waterbirds test set (4795 samples), 10 correlation rates
- **Statistically meaningful:** Standard t-tests, Pearson correlation, effect sizes

**Dataset Type:** Standard (real dataset via WILDS)
- **NOT synthetic:** Real Waterbirds images from CUB-200-2011

**Complexity Tier:** 2 (Medium)
- **Budget:** 60 hours (~2 weeks)
- **New Components:** 3 modules (~600 LOC)

**Gate Logic:** MUST_WORK (correlation AND augmentation AND minority accuracy)
- **Pass:** Proceed to h-m-mitigate (spatial regularization)
- **Fail:** Identify failure point → pivot to detection-only

**Risk Mitigation:** Built-in validity checks (augmentation causality, minority accuracy)

**Novelty:** First mechanistic validation of gradient abnormality for spurious correlation detection

---

## 13. Document Metadata

- **Generated:** 2026-08-20T02:58:00Z
- **Phase:** 2C (Experiment Design)
- **Status:** READY FOR REVIEW
- **Next Action:** Phase 3 (Implementation Planning)
- **Estimated Duration:** Phase 3 (3-4 days), Phase 4 (13.5 days)
- **Total Phase 2C→4 Duration:** ~17 days
