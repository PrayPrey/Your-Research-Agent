# Product Requirements Document: h-e1

**Generated**: 2026-08-24  
**Hypothesis ID**: h-e1  
**Hypothesis Type**: EXISTENCE  
**Gate**: MUST_WORK  
**Archon Task ID**: c4f70e7d-cb8d-476c-9f74-91c168c072b0  
**Pipeline Project ID**: e434b9c6-e150-46c4-8cb5-1c8e857b014c

---

## User Story

**As a** deep learning researcher investigating spurious correlations,  
**I need** to train ResNet-18-BN and ResNet-18-LN on Waterbirds dataset and compare their worst-group accuracy gaps at 90% average accuracy,  
**So that** I can validate whether Batch Normalization amplifies worst-group disparities compared to Layer Normalization.

---

## Hypothesis Statement

**BN-LN Worst-Group Gap Difference Exists**: ResNet-BN shows ≥5 percentage point higher worst-group accuracy gap than ResNet-LN when both reach 90% average accuracy on Waterbirds dataset.

**Causal Mechanism**: BN amplifies early spurious learning via batch-level statistics, while LN reduces spurious amplification via instance-level normalization.

---

## Success Criteria

### Primary Success (MUST_WORK gate satisfied)
- Gap difference (BN - LN) ≥ 5.0 percentage points (mean across 10 seeds)
- Paired t-test p-value < 0.05 (two-tailed)
- Cohen's d effect size ≥ 0.8 (large effect)
- Both architectures reach ≥90% average accuracy in ≥8/10 seeds

### Falsification Criteria (MUST_WORK gate failed)
- p-value > 0.05 (no statistical significance), OR
- Gap difference < 3.0 percentage points (clinically insignificant), OR
- Cohen's d < 0.5 (small-to-medium effect)

---

## Functional Requirements

### FR-1: Dataset Preparation
- Download Waterbirds dataset via `wilds` library
- Cache to `./data/waterbirds/` directory
- Provide train/val/test splits (~4800/600/600 images)
- Return PyTorch DataLoader with:
  - Image tensors: 3×224×224, ImageNet normalized
  - Binary labels: 0=landbird, 1=waterbird
  - Group IDs: 0-3 (4 groups: landbird-land, landbird-water, waterbird-land, waterbird-water)
  - Batch size: 64
- No data augmentation (isolate architectural effects)

### FR-2: Model Architectures

#### ResNet-18-BN
- Base: `torchvision.models.resnet18(pretrained=False)`
- Final layer: `nn.Linear(512, 2)` for binary classification
- Initialization: He normal (kaiming_normal, mode='fan_out', nonlinearity='relu')
- Normalization: Default BatchNorm2d layers (8 BN layers across conv2_x to conv5_x)

#### ResNet-18-LN
- Base: `torchvision.models.resnet18(pretrained=False)`
- **All BatchNorm2d layers replaced with LayerNorm**:
  - For each `nn.BatchNorm2d(C)`, replace with `nn.LayerNorm([C, H, W], elementwise_affine=True)`
  - Feature map dimensions per block:
    - conv2_x: [64, 56, 56]
    - conv3_x: [128, 28, 28]
    - conv4_x: [256, 14, 14]
    - conv5_x: [512, 7, 7]
- Final layer: `nn.Linear(512, 2)`
- Initialization: He normal (same as BN variant)

### FR-3: Training Loop
- **Configuration**:
  - Optimizer: SGD with lr=0.01, momentum=0.9, weight_decay=1e-4
  - Loss: CrossEntropyLoss (no class weighting)
  - Epochs: 100
  - Seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
  - Device: CUDA if available, else CPU
  
- **Seed Management**:
  - Set `torch.manual_seed(seed)`, `torch.cuda.manual_seed_all(seed)`, `np.random.seed(seed)`, `random.seed(seed)`
  - Enable `torch.backends.cudnn.deterministic = True`

- **Metrics Logged Per Epoch** (save to CSV):
  - Seed ID, architecture name, epoch number
  - Training loss (average over epoch)
  - Average accuracy (test set)
  - Worst-group accuracy (min across 4 groups)
  - Per-group accuracy (4 values)
  - Worst-group gap (average_acc - worst_group_acc)

- **Output**: `results/h-e1/training_metrics.csv`

### FR-4: Evaluation and Statistical Test
- **Gap Extraction**:
  - For each (architecture, seed) pair:
    - Find first epoch where average_accuracy ≥ 90%
    - Record worst_group_gap at that epoch
    - If 90% never reached, record gap at epoch 100 and flag as incomplete

- **Statistical Analysis**:
  - Mean gap for ResNet-BN (10 seeds)
  - Mean gap for ResNet-LN (10 seeds)
  - Gap difference: `mean_gap_BN - mean_gap_LN`
  - Standard error of difference
  - Paired t-test: `scipy.stats.ttest_rel(BN_gaps, LN_gaps)` → t-statistic, p-value
  - Cohen's d: `(mean_BN - mean_LN) / pooled_std`

- **Output**:
  - Console report with summary statistics
  - `results/h-e1/statistical_test.txt` (full results)
  - `results/h-e1/gap_comparison.png` (bar plot with error bars)

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Seed management ensures deterministic results
- No random augmentation
- Results versioned to h-e1/ folder

### NFR-2: Performance
- Runtime (GPU V100): ~6-10 hours for 10 seeds × 2 architectures
- Runtime (CPU): ~40-60 hours (not recommended)

### NFR-3: Maintainability
- No hardcoded paths (use argparse or config.yaml)
- Modular code: separate files for data, models, train, eval
- Static analysis validation via validator-agent

### NFR-4: Debuggability
- Progress bars via tqdm
- Per-epoch logging for diagnosis
- Clear error messages for dataset download failures

---

## Acceptance Criteria

### Functional Acceptance
- [ ] Waterbirds dataset downloads and caches successfully
- [ ] ResNet-BN trains for 100 epochs across 10 seeds without errors
- [ ] ResNet-LN trains for 100 epochs across 10 seeds without errors
- [ ] Metrics CSV contains 2000 rows (2 architectures × 10 seeds × 100 epochs)
- [ ] Statistical test produces valid p-value and Cohen's d

### Scientific Acceptance
- [ ] Both architectures reach ≥90% average accuracy in ≥8/10 seeds
- [ ] Gap difference ≥ 5.0 percentage points
- [ ] p < 0.05 (paired t-test)
- [ ] Cohen's d ≥ 0.8

### Code Quality Acceptance
- [ ] All modules pass static analysis (validator-agent check)
- [ ] Code follows PEP8 style
- [ ] No unused imports or dead code
- [ ] Docstrings for public functions

---

## Out of Scope

- Learning rate scheduling (constant lr=0.01 per Phase 2B)
- Data augmentation (isolates architectural effects)
- Model ensembling or test-time augmentation
- Other datasets (CelebA, COCO, etc.)
- Other architectures (VGG, EfficientNet, ViT)
- Group reweighting or fairness interventions

---

## Dependencies

```txt
torch>=2.0.0
torchvision>=0.15.0
wilds>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
pandas>=2.0.0
matplotlib>=3.7.0
tqdm>=4.65.0
```

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| 90% accuracy unreached in >2 seeds | Cannot measure gap at target | Fallback: measure gap at epoch 80 or best avg accuracy |
| High variance in gap estimates | False negative (underpowered test) | 10 seeds provide 80% power for 2pp effect; can add 5 more seeds if needed |
| LN training instability | LN fails to converge | Monitor loss curves, add gradient clipping if loss explodes |
| Dataset download failure | Blocking | Cache dataset locally, verify MD5 checksum, retry with mirror |
| Null result (hypothesis falsified) | MUST_WORK gate fails | Scientific action: route to Phase 0, test alternative datasets (CelebA) or training schedules |

---

## File Structure

```
h-e1/
├── data_loader.py          # Module 1: Dataset preparation
├── models.py               # Module 2: ResNet-BN and ResNet-LN
├── train.py                # Module 3: Training loop
├── evaluate.py             # Module 4: Statistical test
├── config.yaml             # Training configuration
├── requirements.txt        # Python dependencies
├── README.md               # Quick start guide
└── results/
    └── h-e1/
        ├── training_metrics.csv
        ├── statistical_test.txt
        └── gap_comparison.png
```

---

## Next Steps (Architecture Design)

1. **Module 1 (Data)**: Design Waterbirds DataLoader API
   - Input: batch_size, split ('train'/'val'/'test')
   - Output: DataLoader with (images, labels, group_ids)
   - Edge cases: corrupt downloads, missing files

2. **Module 2 (Models)**: Design BN→LN replacement logic
   - Input: ResNet-18 base model
   - Output: Modified model with LN layers
   - Edge cases: dynamic feature map dimensions per layer

3. **Module 3 (Train)**: Design training loop workflow
   - Input: model, dataloader, optimizer, epochs, seed
   - Output: per-epoch metrics logged to CSV
   - Edge cases: CUDA OOM, checkpoint recovery

4. **Module 4 (Eval)**: Design gap extraction algorithm
   - Input: training_metrics.csv
   - Output: statistical test results
   - Edge cases: 90% accuracy never reached, missing seeds

---

**PRD Status**: COMPLETED  
**Complexity Tier**: Tier 1 (Simple)  
**Estimated LoC**: 300-400 lines  
**Ready for Architecture Design**: YES
