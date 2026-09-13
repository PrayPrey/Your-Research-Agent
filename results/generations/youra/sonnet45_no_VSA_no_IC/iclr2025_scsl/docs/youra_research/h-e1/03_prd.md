# Product Requirements Document: H-E1 Gradient Abnormality Detection

**Hypothesis:** h-e1  
**Type:** EXISTENCE  
**Gate:** MUST_WORK  
**Date:** 2026-08-20  
**Version:** 1.0

---

## 1. Executive Summary

### 1.1 Objective
Validate that minority group samples exhibit significantly higher GAIA-Z gradient abnormality scores than majority group samples on the Waterbirds dataset, confirming that spurious correlation learning creates detectable gradient scattering patterns.

### 1.2 Success Criteria
- **Primary:** GAIA-Z(minority) - GAIA-Z(majority) ≥ 0.2, p < 0.01
- **Secondary:** Cohen's d ≥ 0.8
- **Quality:** WGA < 80%, minority_acc ≥ 60%, avg_acc > 95%

### 1.3 Timeline & Resources
- **Duration:** 4 hours (3hr training, 1hr analysis)
- **Hardware:** 1× GPU (8GB VRAM min, RTX 3070+)
- **Dependencies:** PyTorch, WILDS, pytorch-grad-cam, scipy

---

## 2. Functional Requirements

### 2.1 Data Pipeline

**FR-1.1: Dataset Loading**
- Load Waterbirds v1.0 via WILDS API
- Access train/val/test splits (4795/1199/5794 samples)
- Extract metadata (class, background, group_id)
- Verify spurious correlation: 90% training, 50% test
- **Acceptance:** Dataset loads with correct split sizes, metadata accessible

**FR-1.2: Data Preprocessing**
- Apply ImageNet normalization (mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
- Training augmentation: RandomResizedCrop(224), RandomHorizontalFlip, ColorJitter
- Val/Test: Resize(256), CenterCrop(224)
- **Acceptance:** Transforms produce 224×224 RGB tensors

**FR-1.3: Group Identification**
- Map metadata to group labels:
  - group_0: waterbird-water (majority)
  - group_1: waterbird-land (minority)
  - group_2: landbird-water (minority)
  - group_3: landbird-land (majority)
- **Acceptance:** Each test sample has group_id ∈ {0,1,2,3}

### 2.2 Model Training

**FR-2.1: Model Initialization**
- Load ResNet-50 pretrained on ImageNet (torchvision)
- Replace final layer: Linear(2048, 1000) → Linear(2048, 2)
- Move model to GPU
- **Acceptance:** Model outputs shape [batch, 2] for binary classification

**FR-2.2: Training Loop**
- Optimizer: SGD(lr=1e-3, momentum=0.9, weight_decay=1e-4)
- Scheduler: CosineAnnealingLR(T_max=300)
- Loss: CrossEntropyLoss
- Batch size: 128, Epochs: 300
- Early stopping: patience=50 on worst_group_accuracy
- **Acceptance:** Training completes without errors, checkpoints saved

**FR-2.3: Performance Tracking**
- Log per-epoch metrics: loss, avg_acc, group_acc (0-3), WGA
- Save best checkpoint (max WGA)
- Save final checkpoint (epoch 300 or early stop)
- **Acceptance:** training_log.csv contains all required metrics

**FR-2.4: Training Validation**
- Verify WGA < 80% (confirms spurious learning)
- Verify minority_acc ≥ 60% (A1 assumption)
- Verify avg_acc > 95% (model converged)
- **Acceptance:** All three conditions met, else raise error with diagnostic

### 2.3 Gradient Collection

**FR-3.1: GradCAM Setup**
- Initialize GradCAM with target_layers=[model.layer4]
- Use ClassifierOutputTarget for predicted class
- **Acceptance:** GradCAM initialized, no errors on test sample

**FR-3.2: Gradient Extraction**
- For each test sample:
  - Forward pass → predicted class
  - Compute GradCAM attribution
  - Extract raw gradients from cam.activations_and_grads.gradients[0]
  - Shape: [1, 2048, 7, 7]
- Store: (sample_id, group_id, gradient_tensor)
- **Acceptance:** 5794 gradient tensors collected, one per test sample

**FR-3.3: Gradient Storage (Optional)**
- Save gradients.npz: {gradients: [5794, 2048, 7, 7], group_ids: [5794], predictions: [5794]}
- Size: ~500 MB compressed
- **Acceptance:** If saved, npz loads correctly with expected shapes

### 2.4 GAIA-Z Computation

**FR-4.1: Metric Computation**
- For each gradient tensor:
  - Flatten to 1D array (size: 2048×7×7 = 100,352)
  - Count near-zero elements: |{g : |g| < 1e-6}|
  - Compute ratio: GAIA-Z = near_zero_count / total_elements
- **Acceptance:** Output in [0, 1], computed for all 5794 samples

**FR-4.2: Score Aggregation**
- Create DataFrame with columns: [sample_id, group_id, is_minority, gaia_z, prediction, ground_truth, correct]
- is_minority = True if group_id ∈ {1, 2}
- Save gaia_z_scores.csv
- **Acceptance:** CSV contains 5794 rows, valid GAIA-Z scores

**FR-4.3: Score Validation**
- Assert std(gaia_z) > 0.01 (not degenerate)
- Assert 0 ≤ min(gaia_z) ≤ max(gaia_z) ≤ 1 (valid range)
- Assert 0.1 < median(gaia_z) < 0.9 (reasonable distribution)
- **Acceptance:** All assertions pass

### 2.5 Statistical Analysis

**FR-5.1: Group Separation**
- Split scores: minority_scores (groups 1,2), majority_scores (groups 0,3)
- Compute means: mean_minority, mean_majority
- Compute divergence: mean_minority - mean_majority
- **Acceptance:** Both groups non-empty, divergence computed

**FR-5.2: Hypothesis Test**
- Two-sample t-test (Welch's): scipy.stats.ttest_ind(minority, majority, equal_var=False)
- Extract: t_statistic, p_value
- **Acceptance:** Test runs without errors, p_value returned

**FR-5.3: Effect Size**
- Compute Cohen's d: (mean_minority - mean_majority) / pooled_std
- pooled_std = sqrt((var_minority + var_majority) / 2)
- **Acceptance:** Cohen's d computed, value reasonable

**FR-5.4: Gate Evaluation**
- Primary: (divergence ≥ 0.2) AND (p_value < 0.01)
- Secondary: (cohens_d ≥ 0.8)
- Gate: primary AND secondary
- **Acceptance:** Boolean flags computed correctly

**FR-5.5: Results Output**
- Save statistical_results.json:
  ```json
  {
    "minority_mean": float,
    "majority_mean": float,
    "divergence": float,
    "p_value": float,
    "t_statistic": float,
    "cohens_d": float,
    "n_minority": int,
    "n_majority": int,
    "pass_primary": bool,
    "pass_secondary": bool,
    "gate_pass": bool
  }
  ```
- **Acceptance:** JSON valid, all fields present

### 2.6 Visualization

**FR-6.1: Box Plots**
- Plot 1: GAIA-Z by group type (minority vs majority)
  - X-axis: is_minority (False/True)
  - Y-axis: GAIA-Z score
  - File: gaia_z_boxplot_by_type.png
- Plot 2: GAIA-Z by group ID (0-3)
  - X-axis: group_id
  - Y-axis: GAIA-Z score
  - Overlays: minority_mean (red dashed), majority_mean (blue dashed)
  - File: gaia_z_boxplot_by_group.png
- **Acceptance:** Both plots saved, visually correct

**FR-6.2: Histogram**
- Separate distributions for minority (red, alpha=0.5) and majority (blue, alpha=0.5)
- X-axis: GAIA-Z score, bins=50
- File: gaia_z_histogram.png
- **Acceptance:** Histogram shows overlapping distributions, legend present

**FR-6.3: Summary Table**
- CSV with columns: [Group, N, GAIA-Z Mean, GAIA-Z Std, Accuracy]
- Rows: Group 0, 1, 2, 3, Minority Avg, Majority Avg, Divergence
- File: statistical_summary.csv
- **Acceptance:** Table formatted correctly, all values present

---

## 3. Non-Functional Requirements

### 3.1 Performance

**NFR-1.1: Training Time**
- Requirement: ≤ 4 hours on RTX 3070 or equivalent
- Batch size: 128 (adjustable based on GPU memory)
- **Acceptance:** Training completes within time budget

**NFR-1.2: Gradient Collection**
- Requirement: ≤ 20 minutes for 5794 samples
- Optimization: Batch inference where possible
- **Acceptance:** Collection finishes in reasonable time

**NFR-1.3: Memory Usage**
- GPU: ≤ 8GB during training (batch_size=128)
- RAM: ≤ 16GB during gradient collection
- **Acceptance:** No OOM errors on minimum hardware

### 3.2 Reproducibility

**NFR-2.1: Deterministic Results**
- Set seeds: torch.manual_seed(42), np.random.seed(42)
- Disable cudnn.benchmark (or use deterministic mode)
- **Acceptance:** Re-running produces identical statistical results (±1e-4)

**NFR-2.2: Checkpointing**
- Save model state_dict, optimizer, epoch, metrics
- Checkpoint format: {model, optimizer, epoch, train_log}
- **Acceptance:** Checkpoint loads correctly, training resumable

### 3.3 Robustness

**NFR-3.1: Error Handling**
- Validate dataset download completion
- Check GPU availability, fallback to CPU with warning
- Handle OOM during gradient collection (reduce batch size)
- **Acceptance:** Graceful error messages, no silent failures

**NFR-3.2: Input Validation**
- Verify dataset split sizes match expected (4795/1199/5794)
- Check gradient tensor shapes before GAIA-Z computation
- Assert statistical test inputs are non-empty
- **Acceptance:** All validation checks pass, raise clear errors if violated

### 3.4 Maintainability

**NFR-4.1: Code Organization**
- Modular structure: separate scripts for train, collect, compute, analyze
- Utils: gradcam.py, gaia_metrics.py, data_utils.py, visualization.py
- Config: config.yaml for all hyperparameters
- **Acceptance:** Each script imports from utils, no code duplication

**NFR-4.2: Documentation**
- Inline comments for non-obvious logic (GAIA-Z epsilon choice, GradCAM target layer)
- Docstrings for all functions
- README with setup and execution instructions
- **Acceptance:** Code reviewable by external developer

---

## 4. System Architecture

### 4.1 Components

```
h_e1_detection/
├── configs/
│   └── config.yaml               # Hyperparameters, paths
├── utils/
│   ├── gradcam.py               # GradCAM wrapper
│   ├── gaia_metrics.py          # GAIA-Z computation
│   ├── data_utils.py            # WILDS data loading
│   ├── training.py              # Training loop + group tracking
│   └── visualization.py         # Plotting functions
├── train_model.py               # Step 1: Train ResNet-50
├── collect_gradients.py         # Step 2: Extract gradients
├── compute_gaia_z.py            # Step 3: Compute GAIA-Z
├── statistical_test.py          # Step 4: Hypothesis test
├── run_experiment.sh            # End-to-end pipeline
└── README.md                    # Setup and usage
```

### 4.2 Data Flow

```
WILDS Dataset
    ↓
train_model.py → checkpoints/trained_model.pth
    ↓
collect_gradients.py → outputs/gradients.npz (optional)
    ↓
compute_gaia_z.py → outputs/gaia_z_scores.csv
    ↓
statistical_test.py → outputs/statistical_results.json + plots/
```

### 4.3 External Dependencies

| Component | Library | Version | Purpose |
|-----------|---------|---------|---------|
| Dataset | wilds | ≥2.0.0 | Waterbirds access |
| Model | torchvision | ≥0.15.0 | ResNet-50 pretrained |
| GradCAM | pytorch-grad-cam | ≥1.5.0 | Gradient extraction |
| Stats | scipy | ≥1.10.0 | t-test, effect size |
| Viz | matplotlib, seaborn | ≥3.7.0, ≥0.12.0 | Plots |

---

## 5. Acceptance Criteria

### 5.1 Primary Deliverables

**D-1: Trained Model**
- File: checkpoints/trained_model.pth
- Size: ~98 MB
- Contains: model.state_dict(), optimizer, epoch, metrics
- Validation: WGA < 80%, minority_acc ≥ 60%, avg_acc > 95%

**D-2: GAIA-Z Scores**
- File: outputs/gaia_z_scores.csv
- Rows: 5794 (one per test sample)
- Columns: sample_id, group_id, is_minority, gaia_z, prediction, ground_truth, correct
- Validation: All GAIA-Z ∈ [0, 1], std > 0.01

**D-3: Statistical Results**
- File: outputs/statistical_results.json
- Contains: divergence, p_value, cohens_d, gate_pass
- Validation: JSON valid, gate_pass evaluated correctly

**D-4: Visualizations**
- Files: plots/gaia_z_boxplot_by_type.png, gaia_z_boxplot_by_group.png, gaia_z_histogram.png
- Validation: Plots render correctly, show expected distributions

### 5.2 Gate Pass Conditions

**Primary:**
✓ divergence ≥ 0.2  
✓ p_value < 0.01

**Secondary:**
✓ cohens_d ≥ 0.8

**Gate Decision:**
- IF all conditions met: h-e1 PASSES → proceed to h-m-integrated
- ELSE: h-e1 FAILS → ABANDON gradient abnormality approach

---

## 6. Risk Mitigation

### 6.1 Failure Scenarios

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| WGA ≥ 80% | Low | High | Retrain with different seed/hyperparams |
| Minority acc < 60% | Low | High | Flag A1 violation, pivot to global regularization |
| Divergence < 0.2 | Medium | High | FAIL gate, analyze per-sample GAIA-Z distributions |
| p-value ≥ 0.01 | Low | Medium | Check sample size, variance; likely underpowered |
| OOM during training | Low | Medium | Reduce batch size to 64 |
| GradCAM API change | Low | Low | Pin pytorch-grad-cam version in requirements.txt |

### 6.2 Assumption Validation

**A1: Minority samples correctly classified ≥60%**
- Validate during training: monitor minority_acc
- Fallback: If violated, flag in results, consider global regularization

**A3: Gradient scattering from spurious conflict, not complexity**
- Dataset design: Waterbirds has controlled backgrounds (low variance)
- Optional test: Swap backgrounds on subset → expect GAIA-Z drop ≥30%

---

## 7. Testing Strategy

### 7.1 Unit Tests

**UT-1: GAIA-Z Computation**
- Input: Synthetic gradient tensor (known distribution)
- Expected: GAIA-Z matches hand-computed value (±1e-6)
- Edge cases: All zeros, all non-zeros, mixed

**UT-2: Group Identification**
- Input: Metadata array
- Expected: Correct mapping to minority/majority flags
- Edge cases: Verify all 4 groups covered

**UT-3: Statistical Test**
- Input: Synthetic minority/majority scores (known divergence)
- Expected: Correct p_value, Cohen's d
- Edge cases: Equal means (d=0), large divergence (d>1)

### 7.2 Integration Tests

**IT-1: End-to-End Pipeline**
- Run: train_model.py → collect_gradients.py → compute_gaia_z.py → statistical_test.py
- Verify: All outputs generated, no errors
- Duration: ~4 hours

**IT-2: Checkpoint Recovery**
- Interrupt training at epoch 100, resume from checkpoint
- Verify: Training continues correctly, final metrics consistent

### 7.3 Validation Tests

**VT-1: Training Validation**
- After training, verify WGA < 80%, minority_acc ≥ 60%, avg_acc > 95%
- If violated: Raise clear error with diagnostic info

**VT-2: GAIA-Z Validation**
- After computation, check std > 0.01, range [0, 1], median ∈ [0.1, 0.9]
- If violated: Raise error with distribution stats

---

## 8. Deployment & Execution

### 8.1 Setup

```bash
# Environment
conda create -n h_e1 python=3.10
conda activate h_e1

# Dependencies
pip install torch==2.0.1 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cu118
pip install wilds grad-cam scipy matplotlib seaborn pandas pyyaml tqdm

# Verify
python -c "import torch; print(torch.__version__)"
python -c "from wilds import get_dataset; print('WILDS OK')"
```

### 8.2 Execution

```bash
# Full pipeline
cd experiments/h_e1_detection
bash run_experiment.sh

# Individual steps
python train_model.py --config configs/config.yaml
python collect_gradients.py --checkpoint checkpoints/trained_model.pth
python compute_gaia_z.py --gradients outputs/gradients.npz
python statistical_test.py --scores outputs/gaia_z_scores.csv
```

### 8.3 Output Review

```bash
# Check training log
cat outputs/training_log.csv | tail -n 5

# View statistical results
cat outputs/statistical_results.json | jq .

# View plots
open plots/gaia_z_boxplot_by_group.png
```

---

## 9. Success Metrics Summary

| Metric | Threshold | Purpose |
|--------|-----------|---------|
| GAIA-Z Divergence | ≥ 0.2 | Primary evidence of gradient abnormality |
| p-value | < 0.01 | Statistical significance |
| Cohen's d | ≥ 0.8 | Large effect size |
| WGA | < 80% | Confirms spurious learning |
| Minority Acc | ≥ 60% | Validates assumption A1 |
| Avg Acc | > 95% | Model converged correctly |

---

## 10. Next Steps

**If h-e1 Passes:**
1. Archive all outputs (checkpoints, scores, plots)
2. Update verification_state.yaml: gate.satisfied = True
3. Proceed to h-m-integrated experiment design (Phase 2C)
4. Reuse trained_model.pth for correlation sweep experiments

**If h-e1 Fails:**
1. Analyze failure mode: divergence < 0.2, p ≥ 0.01, or d < 0.8
2. Generate diagnostic plots (per-sample GAIA-Z vs accuracy, group distributions)
3. Investigate confounds (image complexity, dataset bias)
4. Decision: ABANDON or reformulate hypothesis with refined assumptions
5. Block h-m-integrated and h-m-mitigate (both depend on h-e1 pass)

---

**Document Status:** Complete  
**Version:** 1.0  
**Archon Task ID:** 28693385-e2a4-42df-ba9a-8f8e903c76bb  
**Dependencies:** None (foundation hypothesis)  
**Blocks:** h-m-integrated, h-m-mitigate
