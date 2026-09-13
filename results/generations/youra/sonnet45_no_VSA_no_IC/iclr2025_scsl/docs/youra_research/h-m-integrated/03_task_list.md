# Implementation Task List: H-M-INTEGRATED
## Causal Mechanism Validation

**Hypothesis ID:** h-m-integrated  
**Type:** MECHANISM (MUST_WORK gate)  
**Tier:** 2 (Medium complexity)  
**Total Budget:** 60 hours  
**Generated:** 2026-08-20  

---

## Task Breakdown Summary

| Category | Count | Complexity | Hours |
|----------|-------|------------|-------|
| Epic Tasks | 6 | 49 total | 40 |
| Environment Setup | 1 | - | 2 |
| Testing & Validation | 4 | - | 12 |
| Failsafe | 1 | - | 6 |
| **TOTAL** | 31 | - | 60 |

**Complexity Distribution:**
- VeryHigh (18-20): 0 epics
- High (14-17): 0 epics
- Medium (9-13): 2 epics (E-2, E-3)
- Low (4-8): 4 epics (E-1, E-4, E-5, E-6)

---

## Environment Setup

### ENV-1: Project Setup & Dependencies
**Estimated Hours:** 2  
**Description:** Initialize project structure, install dependencies, verify h-e1 code availability

**Subtasks:**
1. Create directory structure (`code/`, `utils/`, `checkpoints/`, `outputs/`, `tests/`)
2. Install dependencies (torch≥2.0, transformers≥4.30, wilds≥2.0, scipy≥1.10)
3. Verify h-e1 modules accessible (`gaia_utils.py`, `waterbirds_dataset.py`)
4. Set up config.py (copy from h-e1, modify hyperparameters)

**Acceptance Criteria:**
- All directories exist
- `import h_e1.gaia_utils` succeeds
- `python -c "import torch, transformers, wilds"` exits without error

---

## Epic Tasks

### E-1: Correlation Rate Resampler
**Complexity:** 8 (Low)  
**Estimated Hours:** 6  
**File:** `code/utils/resampler.py`

**Description:** Implement stratified sampling to achieve target spurious correlation rates (50%-95%)

**Subtasks:**

#### E-1-1: Group Count Computation
**Hours:** 1  
**Details:**
- Input: `target_corr` (float), `total_samples` (int)
- Output: Dict[group_id, target_count] where group_id ∈ {0, 1, 2, 3}
- Formula:
  - Majority groups (0, 3): `n = (total_samples × target_corr) / 2`
  - Minority groups (1, 2): `n = (total_samples × (1 - target_corr)) / 2`
- Constraint: Sum of counts = total_samples (round intelligently)

#### E-1-2: Stratified Resampling Logic
**Hours:** 2  
**Details:**
- Filter metadata to train split
- Group by (y, place) → 4 groups
- Sample with replacement per group to match target counts
- Preserve metadata columns (filename, y, place, split)
- Set seed for reproducibility

#### E-1-3: Integration with WaterbirdsDataset
**Hours:** 1  
**Details:**
- Modify `waterbirds_dataset.py` (copy from h-e1)
- Add `resample_train_set(target_corr, seed)` method
- Call `resample_waterbirds()` internally
- Update `self.metadata` to resampled DataFrame

#### E-1-4: Unit Tests
**Hours:** 2  
**Details:**
- Test target correlation achieved (tolerance ± 2%)
- Test all 4 groups present in output
- Test deterministic behavior (same seed → same samples)
- Test edge cases (50% correlation, 100% correlation)

**Dependencies:** None  
**Outputs:** `utils/resampler.py`, `tests/test_resampler.py`

---

### E-2: Background Swapper
**Complexity:** 11 (Medium)  
**Estimated Hours:** 9  
**File:** `code/utils/augmentation.py`

**Description:** SegFormer-based bird segmentation + foreground-background compositing

**Subtasks:**

#### E-2-1: SegFormer Integration
**Hours:** 2  
**Details:**
- Load `nvidia/segformer-b5-finetuned-ade-640-640` from HuggingFace
- Initialize processor and model
- Identify "bird" class ID in ADE20K vocabulary (class 9)
- Implement `segment_bird(image: PIL.Image) -> np.ndarray` (binary mask)

#### E-2-2: Foreground Extraction
**Hours:** 1.5  
**Details:**
- Preprocess image with SegFormer processor
- Forward pass → logits [1, num_classes, H/4, W/4]
- Upsample to original resolution [H, W]
- Extract bird class mask: `argmax(logits, dim=1) == bird_class_id`

#### E-2-3: Mask Refinement
**Hours:** 1  
**Details:**
- Apply morphological operations (dilation + erosion) to smooth mask edges
- Kernel sizes: dilate 5×5, erode 3×3
- Convert to 3-channel mask for RGB compositing

#### E-2-4: Background Pool Builder
**Hours:** 1  
**Details:**
- Load majority samples from Waterbirds test set (groups 0, 3)
- Sample 500 images per group (1000 total)
- Store in dict: `{group_id: List[PIL.Image]}`
- Cache to disk (pickle) for reuse

#### E-2-5: Alpha Compositing
**Hours:** 1.5  
**Details:**
- Implement `swap_background(fg_img, bg_img) -> PIL.Image`
- Segment bird in foreground
- Sample random background from target group pool
- Composite: `result = fg × mask + bg × (1 - mask)`
- Return PIL Image [224, 224, 3]

#### E-2-6: Batch Processing
**Hours:** 0.5  
**Details:**
- Process 200 minority samples with progress bar (tqdm)
- Handle GPU batch processing (batch_size=16 for segmentation)
- Save augmented images to disk (optional, for debugging)

#### E-2-7: Quality Validation
**Hours:** 1  
**Details:**
- Compute IoU (Intersection over Union) on 10 random samples
- Manual inspection: segmentation mask overlays
- Threshold: Average IoU > 0.7 (pass), else raise warning

#### E-2-8: Fallback Handling
**Hours:** 0.5  
**Details:**
- If segmentation produces mask with coverage < 5% → use center crop fallback
- Center crop mask: 1.0 in center 50% of image, 0.0 elsewhere
- Log fallback usage count

**Dependencies:** E-1 (needs dataset loader)  
**Outputs:** `utils/augmentation.py`, `tests/test_augmentation.py`

---

### E-3: Multi-Model Training Orchestrator
**Complexity:** 9 (Medium)  
**Estimated Hours:** 8  
**File:** `code/train_sweep.py`

**Description:** Train 10 ResNet-50 models with varying correlation rates (50%-95%)

**Subtasks:**

#### E-3-1: CLI Interface
**Hours:** 1  
**Details:**
- argparse: `--correlation_rates` (comma-separated list)
- `--output_dir` (checkpoint directory)
- `--epochs`, `--batch_size`, `--patience`, `--device`
- Parse correlation rates: `[50, 55, 60, 65, 70, 75, 80, 85, 90, 95]`

#### E-3-2: Checkpoint Manager
**Hours:** 2  
**Details:**
- Create subdirectories: `output_dir/model_corr_{rate}/`
- Save best model: `best_model.pth` (based on worst-group val accuracy)
- Save metadata: `metadata.json` (correlation_rate, wga, val_wga, epoch)
- Save training log: `train_log.csv` (epoch, train_loss, val_loss, wga)

#### E-3-3: Training Loop Integration
**Hours:** 3  
**Details:**
- Reuse `train_gaia.py` from h-e1 (copy and modify)
- Add `correlation_rate` parameter
- Call `dataset.resample_train_set(correlation_rate)` before training
- Early stopping: monitor worst-group val accuracy (patience=50)
- Log WGA every epoch

#### E-3-4: Multi-Model Orchestration
**Hours:** 1  
**Details:**
- Loop over correlation rates sequentially (or use multiprocessing for parallel)
- Train each model independently
- Save WGA results to CSV: `wga_results.csv` (correlation_rate, final_wga, final_val_wga)

#### E-3-5: Error Recovery
**Hours:** 1  
**Details:**
- Handle training failures (NaN loss, CUDA OOM)
- Retry with reduced learning rate (lr / 10)
- Log failures in `wga_results.csv` (mark as FAILED)
- Skip failed models in downstream experiments

**Dependencies:** E-1 (resampler)  
**Outputs:** `train_sweep.py`, 10 model checkpoints, `wga_results.csv`

---

### E-4: GAIA Divergence Extraction
**Complexity:** 7 (Low)  
**Estimated Hours:** 6  
**File:** `code/extract_gaia.py`

**Description:** Extract GAIA-Z scores for 10 models × 4795 test samples, compute divergence

**Subtasks:**

#### E-4-1: Batch GAIA-Z Extraction
**Hours:** 2  
**Details:**
- Load each of 10 trained models
- Extract GAIA-Z for all 4795 test samples (reuse h-e1 `compute_gaia_z`)
- Batch size: 32 (GPU memory constraint)
- Save per-model results: `gaia_scores_corr_{rate}.npy` (array of shape [4795])

#### E-4-2: Divergence Computation
**Hours:** 1.5  
**Details:**
- Load group annotations (minority: [1, 2], majority: [0, 3])
- Compute per-model divergence: `mean(GAIA-Z[minority]) - mean(GAIA-Z[majority])`
- Store in DataFrame: columns=[correlation_rate, wga, divergence]

#### E-4-3: CSV Export
**Hours:** 0.5  
**Details:**
- Save to `outputs/gaia_divergences.csv`
- 10 rows (one per correlation rate)
- Sort by correlation_rate ascending

#### E-4-4: Validation Tests
**Hours:** 2  
**Details:**
- Test GAIA-Z extraction on 1 model (spot check)
- Verify divergence values monotonic (higher correlation → higher divergence, expected trend)
- Unit test: verify minority/majority group masks correct

**Dependencies:** E-3 (trained models)  
**Outputs:** `extract_gaia.py`, `gaia_divergences.csv`, `tests/test_extraction.py`

---

### E-5: Correlation Analyzer
**Complexity:** 6 (Low)  
**Estimated Hours:** 5  
**File:** `code/utils/analysis.py`

**Description:** Pearson correlation analysis + visualization

**Subtasks:**

#### E-5-1: Pearson Correlation Wrapper
**Hours:** 1  
**Details:**
- Implement `analyze_correlation(wga_values, gaia_divergences)`
- Call `scipy.stats.pearsonr()`
- Return dict: `{rho, p_value, pass_primary (bool)}`
- Gate check: `rho > 0.7 AND p_value < 0.05`

#### E-5-2: Scatter Plot Visualization
**Hours:** 2  
**Details:**
- Create scatter plot (x=GAIA divergence, y=WGA)
- Fit linear trendline: `np.polyfit(deg=1)`
- Annotate plot with ρ and p-value
- Save to `outputs/correlation_scatter.png`

#### E-5-3: Confidence Intervals
**Hours:** 1  
**Details:**
- Compute 95% CI for Pearson correlation (Fisher z-transform)
- Add to results dict: `{rho_ci_lower, rho_ci_upper}`
- Visualize CI as shaded region on plot

#### E-5-4: Results Export
**Hours:** 1  
**Details:**
- Save results to JSON: `outputs/exp1_correlation.json`
- Include: rho, p_value, pass_primary, rho_ci_lower, rho_ci_upper
- Save plot separately as PNG

**Dependencies:** E-4 (GAIA divergences, WGA values)  
**Outputs:** `utils/analysis.py`, `exp1_correlation.json`, `correlation_scatter.png`

---

### E-6: Augmentation Experiment
**Complexity:** 8 (Low)  
**Estimated Hours:** 6  
**File:** `code/run_augmentation_test.py`

**Description:** Background swap on 200 minority samples, measure GAIA-Z reduction

**Subtasks:**

#### E-6-1: Sample Selection
**Hours:** 1  
**Details:**
- Load 90% correlation model checkpoint
- Select 200 minority samples from test set (100 waterbird-land, 100 landbird-water)
- Filter: model predicts correctly (to ensure GradCAM validity)
- Save sample indices to `outputs/augmentation_sample_indices.json`

#### E-6-2: Background Swap Pipeline
**Hours:** 2  
**Details:**
- Initialize BackgroundSwapper (from E-2)
- Load background pool (1000 majority samples)
- Swap backgrounds: waterbird-land → water, landbird-water → land
- Save augmented images (optional, for visualization)

#### E-6-3: GAIA-Z Extraction (Original vs Augmented)
**Hours:** 1.5  
**Details:**
- Extract GAIA-Z for 200 original samples
- Extract GAIA-Z for 200 augmented samples
- Store as paired arrays: `original_gaia_z`, `augmented_gaia_z`

#### E-6-4: Paired t-test
**Hours:** 1  
**Details:**
- Implement `analyze_augmentation_effect(original, augmented)`
- Compute reduction: `mean_reduction_pct = (mean(original) - mean(augmented)) / mean(original) × 100%`
- Call `scipy.stats.ttest_rel()` (paired t-test)
- Return dict: `{mean_reduction_pct, p_value, pass_augmentation (bool)}`
- Gate check: `reduction ≥ 30% AND p_value < 0.01`

#### E-6-5: Results Export
**Hours:** 0.5  
**Details:**
- Save to JSON: `outputs/exp2_augmentation.json`
- Include: mean_reduction_pct, p_value, pass_augmentation, sample_count

**Dependencies:** E-2 (BackgroundSwapper), E-3 (90% model)  
**Outputs:** `run_augmentation_test.py`, `exp2_augmentation.json`

---

## Testing & Validation

### TEST-1: Unit Test Suite
**Estimated Hours:** 4  
**Description:** Comprehensive unit tests for all new modules

**Test Files:**
- `tests/test_resampler.py` (5 tests, E-1-4)
- `tests/test_augmentation.py` (7 tests, E-2-7)
- `tests/test_analysis.py` (3 tests, E-5-4)
- `tests/test_extraction.py` (2 tests, E-4-4)

**Coverage Target:** ≥ 80% for new code (utils/)

---

### TEST-2: Integration Test (End-to-End)
**Estimated Hours:** 3  
**Description:** Validate full pipeline on 2-model subset (50%, 95% correlation)

**Steps:**
1. Train 2 models (50%, 95%) — ~6 hours wall-clock
2. Extract GAIA divergence
3. Verify divergence(95%) > divergence(50%)
4. Run augmentation test on 10 samples (quick validation)

**Acceptance:** Divergence increases with correlation rate (monotonic)

---

### TEST-3: Minority Accuracy Validation (Experiment 3)
**Estimated Hours:** 2  
**Description:** Measure minority accuracy on 90% correlation model

**Steps:**
1. Load 90% model checkpoint
2. Evaluate on minority test samples (groups 1, 2)
3. Compute accuracy: `correct_predictions / total_minority_samples`
4. Gate check: `accuracy ≥ 0.60`

**Output:** `outputs/exp3_minority_acc.json`

---

### TEST-4: Gate Decision Logic
**Estimated Hours:** 3  
**Description:** Implement final gate decision + failure diagnostics

**File:** `code/run_gate_decision.py`

**Logic:**
```
PASS = (exp1_rho > 0.7 AND exp1_p < 0.05)  # Primary 1
       AND (exp2_reduction ≥ 30%)           # Primary 2
       AND (exp3_minority_acc ≥ 0.60)       # Secondary

FAIL → Identify failure point:
  - If exp1 fails: Step 1→3 broken (correlation/divergence link)
  - If exp2 fails: Step 2 broken (conflict not causal)
  - If exp3 fails: Step 3 invalid (GradCAM unreliable)
```

**Output:** `outputs/gate_decision.json` (gate: PASS/FAIL, failure_point: exp1/exp2/exp3/null)

---

## Failsafe

### FAILSAFE-1: Diagnostic Mode
**Estimated Hours:** 6  
**Description:** If gate FAILS, run diagnostics to identify failure step (1/2/3/4)

**Diagnostic Steps:**

#### Diagnostic 1: Verify Step 1 (Correlation rate → WGA)
- Plot WGA vs correlation rate
- Expected: monotonic decrease (higher correlation → lower WGA)
- If flat/random: training issue (hyperparameters, early stopping)

#### Diagnostic 2: Verify Step 3 (WGA → GAIA divergence)
- Plot GAIA divergence vs correlation rate
- Expected: monotonic increase (higher correlation → higher divergence)
- If flat/random: GAIA metric insensitive

#### Diagnostic 3: Verify Step 2 (Conflict causality)
- Visual inspection: segmentation quality (10 random masks)
- Fallback: manual background swap (ground truth masks)
- If manual swap works: segmentation issue (fix E-2)
- If manual swap fails: spurious conflict not causal (pivot to detection-only)

#### Diagnostic 4: Verify Step 4 (Gradient scattering)
- Visualize GradCAM heatmaps (original vs augmented)
- Expected: augmented samples show less scattering (more focused heatmaps)
- If no visual difference: GAIA-Z metric limitation

**Output:** `outputs/diagnostics_report.md` (identifies failure point, recommends next action)

---

## Timeline Estimate

| Phase | Duration | Parallel | Sequential |
|-------|----------|----------|------------|
| **Setup (ENV-1)** | 2 hours | - | 2 hours |
| **Epic Implementation** | 40 hours | Yes (E-1, E-2 parallel) | 40 hours |
| - E-1 (Resampler) | 6 hours | ✓ | - |
| - E-2 (Swapper) | 9 hours | ✓ | - |
| - E-3 (Multi-Train) | 8 hours | After E-1 | - |
| - E-4 (GAIA Extract) | 6 hours | After E-3 | - |
| - E-5 (Correlation) | 5 hours | After E-4 | - |
| - E-6 (Augmentation) | 6 hours | Parallel with E-4,E-5 | - |
| **Testing** | 12 hours | Parallel with epics | 12 hours |
| **Failsafe (if needed)** | 6 hours | - | 6 hours |
| **TOTAL** | 60 hours | ~30 hours (parallelized) | 60 hours (sequential) |

**Wall-Clock (Optimized):** ~1.5 weeks (30 hours dev + 30 GPU hours training)

---

## Dependencies

**External:**
- h-e1 codebase (GAIA-Z, GradCAM, WaterbirdsDataset)
- WILDS dataset cache (~1.2 GB)
- SegFormer-B5 pretrained weights (~350 MB, auto-downloaded)

**Internal (Epic-level):**
- E-3 depends on E-1 (resampler)
- E-4 depends on E-3 (trained models)
- E-5 depends on E-4 (GAIA divergences)
- E-6 depends on E-2 (BackgroundSwapper) + E-3 (90% model)

**Parallelization Opportunities:**
- E-1 and E-2 can run in parallel (independent)
- E-5 and E-6 can run in parallel (both use E-3 outputs, different experiments)
- All testing can run alongside epic implementation

---

## Success Criteria

**Phase 3 Complete:**
- All 6 epics implemented (code compiles, tests pass)
- Unit test coverage ≥ 80%
- Integration test passes (2-model divergence check)

**Phase 4 Ready:**
- All files in `code/` directory
- `requirements.txt` complete
- README with setup instructions
- No hardcoded paths (all configurable via CLI/config)

**Gate Decision Ready:**
- Experiment 1-3 outputs present (JSON files)
- Gate decision logic implemented
- Failsafe diagnostic mode available

---

## Risk Mitigation

| Risk | Impact | Mitigation | Task |
|------|--------|------------|------|
| SegFormer segmentation failure | Augmentation test invalid | Fallback to center crop masks | E-2-8 |
| Training divergence (NaN loss) | Missing correlation data points | Retry with reduced LR, log failures | E-3-5 |
| GAIA extraction CUDA OOM | Pipeline crash | Reduce batch size (32→16→8), fallback to CPU | E-4-1 |
| Correlation weak (ρ < 0.7) | Gate fails Step 1→3 | Diagnostic mode (verify WGA vs corr, divergence vs corr) | FAILSAFE-1 |

---

## Archon Integration

**Pipeline Project ID:** ef7140fe-2bf9-4e5e-95dc-bf2484dc0083  
**Hypothesis Task ID:** 2c7459e2-2180-4032-896c-deb038ba950c  

**Archon Task Mapping:**
- Each Epic (E-1 to E-6) → Archon Epic Task
- Each Subtask (E-X-Y) → Archon Subtask
- Testing tasks (TEST-1 to TEST-4) → Archon Epic Tasks
- Failsafe → Archon Epic Task

**Total Archon Tasks:** 6 Epics + 31 Subtasks + 4 Testing Epics + 1 Failsafe = 42 tasks

---

## Document Metadata

- **Document Type:** Implementation Task List
- **Hypothesis:** h-m-integrated (MECHANISM, MUST_WORK)
- **Phase:** 3 (Implementation Planning)
- **Status:** FINAL
- **Generated:** 2026-08-20T03:10:00Z
- **Total Tasks:** 31 (6 epics + 4 testing + 1 failsafe + env setup)
- **Budget:** 60 hours
- **Next Action:** Phase 4 (Coding — execute epic tasks)
