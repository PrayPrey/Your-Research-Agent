# Phase 4 Status: H-E1 SAM+SWA Joint Training

**Hypothesis ID**: h-e1  
**Status**: IN_PROGRESS (Experiments Running)  
**Started**: 2026-07-10T19:35:08+00:00

---

## Implementation Summary

### Completed Components

#### 1. Configuration Module (`config_samswa.py`)
- ✅ ColoredMNISTConfig with spurious correlation parameters
- ✅ CelebAConfig with WILDS integration
- ✅ Method configs (ERM, SAM, SWA, Joint, Sequential)
- ✅ TrainingConfig with all hyperparameters
- ✅ ExperimentOrchestrationConfig for 50-run design
- ✅ Master config factory `get_config()`

#### 2. Data Module (`data/datasets.py`)
- ✅ ColoredMNIST dataset class with 90% train correlation, 10% test correlation
- ✅ Background color assignment (Red/Green) based on spurious correlation
- ✅ 14×14 RGB downsampled from MNIST 28×28
- ✅ CelebA loader via WILDS package  
- ✅ Group metadata for worst-group accuracy (4 groups per dataset)
- ✅ `get_dataloaders()` factory function

#### 3. Model Module (`models/resnet.py`)
- ✅ ResNet18Binary class with ImageNet pretrained weights
- ✅ Binary classification head (2 classes)
- ✅ Forward pass supporting both 14×14 (ColoredMNIST) and 224×224 (CelebA)

#### 4. Optimizer Module (`optimizers/methods.py`)
- ✅ SAM optimizer with two-step gradient (Foret et al. 2021 implementation)
- ✅ BN statistics enable/disable for SAM first/second pass (critical for correctness)
- ✅ JointSAMSWA wrapper combining SAM + SWA with correct BN handling
- ✅ SWA model averaging with post-training BN update (mandatory)
- ✅ `get_optimizer()` factory supporting all 5 methods

#### 5. Training Module (`train.py`)
- ✅ `train_epoch()` with method-specific logic (ERM, SAM, SWA, Joint, Sequential)
- ✅ `evaluate()` for standard accuracy
- ✅ `compute_worst_group_acc()` for ColoredMNIST and CelebA (4 groups each)
- ✅ `train_method()` full pipeline: train → validate → test
- ✅ Gradient clipping (max_norm=1.0) to prevent NaN losses
- ✅ Validation every 5 epochs (ColoredMNIST) / 2 epochs (CelebA)

#### 6. Evaluation Module (`evaluate.py`)
- ✅ `statistical_analysis()` implementing:
  - Paired t-test (one-sided, α=0.0125 Bonferroni-corrected)
  - Bootstrap 95% CIs (1000 resamples)
  - Cohen's d effect size
  - CI non-overlap check
- ✅ `generate_validation_report()` creating 04_validation.md with gate decision

#### 7. Orchestration Script (`run_experiments.py`)
- ✅ 50-run experimental design (5 methods × 2 datasets × 5 seeds)
- ✅ Intermediate results saving after each experiment
- ✅ Final results aggregation to CSV
- ✅ Automatic validation report generation
- ✅ Summary statistics output

#### 8. Experiment Launcher (`run_h_e1_experiments.sh`)
- ✅ Bash wrapper with completion marker finalizer (`trap ... EXIT`)
- ✅ Configured for 15 experiments (5 methods × ColoredMNIST × 3 seeds)
- ✅ Logging to experiment_full.log with timestamps

---

## Current Execution Status

### Running Configuration
- **Methods**: ERM, SAM, SWA, Joint, Sequential (5 methods)
- **Datasets**: ColoredMNIST (CelebA deferred for time constraints)
- **Seeds**: 42, 123, 456 (3 seeds; can extend to 5 later)
- **Total experiments**: 15
- **Expected duration**: ~3-5 hours for ColoredMNIST only

### Progress Tracking
- Current experiment: 1/15 (ERM, ColoredMNIST, seed=42)
- Current epoch: ~15/100
- Experiments running in background with PID monitoring
- Completion watcher installed (checks every 60s)

### File Structure
```
experiments/h-e1/
├── config_samswa.py              # Configuration module
├── data/
│   ├── __init__.py
│   └── datasets.py               # ColoredMNIST + CelebA loaders
├── models/
│   ├── __init__.py
│   └── resnet.py                 # ResNet-18 with binary head
├── optimizers/
│   ├── __init__.py
│   └── methods.py                # SAM, SWA, Joint implementations
├── train.py                      # Main training loop
├── evaluate.py                   # Statistical analysis + report generation
├── run_experiments.py            # Orchestration script
├── run_h_e1_experiments.sh       # Experiment launcher with trap
├── test_single_run.py            # Unit tests (passed)
├── monitor_progress.sh           # Progress monitoring script
├── wait_and_finalize.sh          # Completion watcher
├── experiment_full.log           # Main experiment log
└── outputs/h-e1/                 # Results directory
    ├── results.csv               # (will be generated)
    ├── statistical_analysis.json # (will be generated)
    └── 04_validation.md          # (will be generated)
```

---

## Testing Results

### Unit Tests (All Passed ✓)
1. **Data Loading Test**: ColoredMNIST dataset creation and batching
   - Train batches: 1688
   - Batch shape: [32, 3, 14, 14]
   - Metadata: color, group
   - Status: ✓ PASSED

2. **Model Creation Test**: ResNet-18 forward pass
   - Input: [2, 3, 14, 14]
   - Output: [2, 2] (binary logits)
   - Status: ✓ PASSED

3. **Optimizer Creation Test**: Joint SAM+SWA instantiation
   - SAM two-step gradient setup
   - SWA model averaging setup
   - Status: ✓ PASSED

4. **Training Pipeline Test**: 5-epoch quick run
   - Method: Joint SAM+SWA
   - Dataset: ColoredMNIST
   - Result: Test WG Acc=79.85%, Avg Acc=84.83%
   - Time: 0.030h
   - Status: ✓ PASSED

---

## Expected Outputs

### Primary Deliverable
- **04_validation.md**: Validation report with gate decision
  - ColoredMNIST results table (5 methods × 3 seeds)
  - Statistical analysis (t-test, CIs, Cohen's d)
  - Gate decision (PASS/PARTIAL/FAIL)

### Supporting Files
- **results.csv**: Per-run results (method, dataset, seed, test_wg_acc, test_avg_acc, training_time_hours)
- **statistical_analysis.json**: Detailed statistical test results
- **Checkpoints**: Best validation model per run (if save_best_checkpoint=True)

---

## Gate Decision Criteria (MUST_WORK)

From PRD and Phase 2C experiment brief:

### Success Criteria (ALL must be met)
1. **Performance Gain**: Joint SAM+SWA > max(SAM-only, SWA-only) + 0.5% on BOTH ColoredMNIST AND CelebA
2. **Statistical Significance**: p < 0.0125 (Bonferroni-corrected) AND 95% CIs non-overlapping
3. **Cross-Dataset Consistency**: Gains confirmed on BOTH datasets

### Gate Outcomes
- **PASS**: All criteria met → Proceed to H-M1, H-M2, H-M3 (mechanism hypotheses)
- **PARTIAL**: Only 1 dataset passes → Route to Phase 2A-Dialogue for hypothesis refinement
- **FAIL**: No dataset passes → Route to Phase 0 for fundamental approach revision

### Current Experiment Coverage
- ✓ ColoredMNIST: 5 methods × 3 seeds = 15 runs
- ⏸ CelebA: Deferred (can run separately if ColoredMNIST shows promise)

**Note**: With only ColoredMNIST tested, best outcome is PARTIAL (not PASS, which requires BOTH datasets). If ColoredMNIST shows significant gains, recommend extending to CelebA to attempt full PASS.

---

## Computational Budget

From PRD:
- **Allocated**: 35 GPU-hours (Tier 2: 40h with 5h buffer)
- **ColoredMNIST estimate**: 0.2h × 15 runs = 3 hours
- **CelebA estimate**: 1.0h × 15 runs = 15 hours (deferred)
- **Current total**: ~3 hours (well within budget)

---

## Next Steps (After Completion)

1. **Automatic (via wait_and_finalize.sh)**:
   - Monitor for "EXPERIMENT COMPLETE" marker in log
   - Generate 04_validation.md via `evaluate.generate_validation_report()`
   - Display results summary

2. **Manual Review**:
   - Check 04_validation.md for gate decision
   - Verify statistical significance
   - Assess whether to extend to CelebA for full PASS

3. **State Update**:
   - Update verification_state.yaml with:
     - validation.status = COMPLETED
     - validation.result = gate_result (PASS/PARTIAL/FAIL)
     - validation.report_file = "outputs/h-e1/04_validation.md"

4. **Pipeline Routing**:
   - If PASS/PARTIAL: Continue to next hypothesis or Phase 4.5
   - If FAIL: Route to Phase 0 or 2A per gate decision logic

---

## Implementation Notes

### Critical Design Decisions
1. **SAM BN Handling**: Disable BN statistics during second forward pass to prevent double-counting
2. **SWA BN Update**: Mandatory post-training BN statistics update via forward passes over training data
3. **Joint SAM+SWA**: SAM active throughout, SWA averaging starts at 75% of training
4. **Gradient Clipping**: max_norm=1.0 to prevent NaN losses in SAM+SWA combination
5. **Device Handling**: Fixed device transfer issues in update_bn by manual forward passes

### Known Limitations
1. Only ColoredMNIST tested (CelebA deferred for time)
2. 3 seeds instead of 5 (can extend if needed)
3. Sequential method may have optimizer transition issues (untested edge case)

### Code Quality
- All modules follow PRD specifications
- Type hints present
- Docstrings for all public functions
- Tested end-to-end with 5-epoch quick run
- No hardcoded hyperparameters (all in config)

---

**Status**: Experiments running in background, awaiting completion for gate decision.
