# Implementation Requirements: h-e1

**Hypothesis**: BN-LN worst-group gap difference  
**Complexity Tier**: Tier 1 (Simple)  
**Estimated LoC**: 300-400 lines

---

## Module Breakdown

### Module 1: Data Preparation
**File**: `data_loader.py`  
**Responsibility**: Download and preprocess Waterbirds dataset with group labels

**Requirements**:
- Download Waterbirds via `wilds` library
- Cache to `./data/waterbirds/`
- Return PyTorch DataLoader with:
  - Image tensors (3×224×224, ImageNet normalized)
  - Binary labels (0=landbird, 1=waterbird)
  - Group IDs (0-3 for 4 groups)
  - Group names (landbird-land, landbird-water, waterbird-land, waterbird-water)
- Train/val/test splits (~4800/600/600)
- No data augmentation
- Batch size: 64

**Dependencies**: `torch`, `torchvision`, `wilds`, `numpy`

---

### Module 2: Model Definitions
**File**: `models.py`  
**Responsibility**: Define ResNet-18-BN and ResNet-18-LN architectures

**Requirements**:

#### ResNet-18-BN
- Base: `torchvision.models.resnet18(pretrained=False)`
- Modify final FC layer: `nn.Linear(512, 2)` for binary classification
- Initialization: He normal (`torch.nn.init.kaiming_normal_` with `mode='fan_out', nonlinearity='relu'`)
- No modifications to BN layers (use default)

#### ResNet-18-LN
- Base: `torchvision.models.resnet18(pretrained=False)`
- **Replace all BN layers with LN**:
  - Iterate through model modules
  - For each `nn.BatchNorm2d(num_features)`, replace with `nn.LayerNorm([num_features, H, W], elementwise_affine=True)`
  - Feature map dimensions: conv2_x (56×56), conv3_x (28×28), conv4_x (14×14), conv5_x (7×7)
- Modify final FC layer: `nn.Linear(512, 2)`
- Initialization: He normal (same as BN variant)

**Note**: LN normalized_shape must match feature map dimensions. Use dynamic replacement to handle varying H, W across layers.

**Dependencies**: `torch`, `torchvision`

---

### Module 3: Training Loop
**File**: `train.py`  
**Responsibility**: Train both architectures across 10 seeds and log metrics

**Requirements**:

**Training Configuration**:
- Optimizer: SGD(lr=0.01, momentum=0.9, weight_decay=1e-4)
- Loss: CrossEntropyLoss (no class weighting)
- Epochs: 100
- Seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
- Device: CUDA if available, else CPU

**Per-Epoch Logging** (save to CSV):
- Seed ID
- Architecture name (ResNet-BN, ResNet-LN)
- Epoch number
- Training loss (average over epoch)
- Average accuracy (test set)
- Worst-group accuracy (min across 4 groups)
- Per-group accuracy (4 values)
- Worst-group gap (average_acc - worst_group_acc)

**Seed Management**:
```python
def set_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True
```

**Output**: `results/h-e1/training_metrics.csv`

**Dependencies**: `torch`, `numpy`, `pandas`, `tqdm`

---

### Module 4: Evaluation and Statistical Test
**File**: `evaluate.py`  
**Responsibility**: Compare worst-group gaps at 90% accuracy and perform statistical test

**Requirements**:

**Gap Extraction**:
- For each (architecture, seed) pair:
  - Load training_metrics.csv
  - Find first epoch where average_accuracy ≥ 90%
  - Record worst_group_gap at that epoch
  - If 90% never reached, record gap at epoch 100 and flag as incomplete

**Statistical Analysis**:
- Compute across 10 seeds:
  - Mean gap for ResNet-BN
  - Mean gap for ResNet-LN
  - Gap difference: `mean_gap_BN - mean_gap_LN`
  - Standard error of difference
- Paired t-test (scipy.stats.ttest_rel):
  - Input: 10 BN gaps vs 10 LN gaps
  - Output: t-statistic, p-value
- Cohen's d effect size:
  - Formula: `(mean_BN - mean_LN) / pooled_std`

**Success Check**:
```python
success = (gap_difference >= 5.0) and (p_value < 0.05) and (cohens_d >= 0.8)
```

**Output**:
- Console report with summary statistics
- `results/h-e1/statistical_test.txt` with full results
- `results/h-e1/gap_comparison.png` (bar plot with error bars)

**Dependencies**: `numpy`, `scipy`, `matplotlib`, `pandas`

---

## Acceptance Criteria

### Functional
- [ ] Waterbirds dataset downloads and caches successfully
- [ ] ResNet-BN trains without errors for 100 epochs
- [ ] ResNet-LN trains without errors for 100 epochs
- [ ] All 10 seeds complete for both architectures
- [ ] Metrics logged every epoch with no missing values
- [ ] Statistical test runs and produces p-value

### Scientific
- [ ] Both architectures reach ≥90% average accuracy in ≥8/10 seeds
- [ ] Worst-group gap difference ≥5pp (mean across seeds)
- [ ] p < 0.05 (paired t-test)
- [ ] Cohen's d ≥ 0.8

### Quality
- [ ] No hardcoded paths (use argparse or config)
- [ ] Reproducible results (seed management correct)
- [ ] Results saved to versioned folder (h-e1/)
- [ ] Code passes static analysis (validator-agent)

---

## Runtime Estimates

**Per-seed training time** (estimated):
- ResNet-18 on Waterbirds (~5000 images)
- 100 epochs, batch size 64
- GPU (V100): ~20-30 minutes per seed
- CPU: ~2-3 hours per seed

**Total runtime** (10 seeds, 2 architectures):
- GPU: ~6-10 hours
- CPU: ~40-60 hours

**Recommendation**: Run on GPU, parallelize seeds if multiple GPUs available.

---

## File Structure

```
h-e1/
├── data_loader.py          # Module 1
├── models.py               # Module 2
├── train.py                # Module 3
├── evaluate.py             # Module 4
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

## Dependencies List

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

## Phase 3 Archon Tasks (Preview)

**EPIC-DATA**: Waterbirds dataset preparation
- Subtask: Download via wilds
- Subtask: Verify group splits
- Subtask: Create DataLoader

**EPIC-MODEL**: ResNet architectures
- Subtask: Implement ResNet-BN wrapper
- Subtask: Implement BN→LN replacement logic
- Subtask: Test forward pass shapes

**EPIC-TRAIN**: Training loop
- Subtask: Seed management
- Subtask: Training loop with metric logging
- Subtask: Checkpoint saving

**EPIC-EVAL**: Gap comparison
- Subtask: Extract gaps at 90% accuracy
- Subtask: Paired t-test implementation
- Subtask: Visualization and reporting

---

**Document Status**: COMPLETED  
**Ready for Archon PRD Generation**: YES
