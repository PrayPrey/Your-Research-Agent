# Implementation References: H-E1

**Hypothesis:** h-e1 (Gradient Abnormality Detection)  
**Date:** 2026-08-20  

---

## 1. Code Repositories

### 1.1 Dataset & Baseline Training

**WILDS Benchmark**
- URL: https://github.com/p-lambda/wilds
- Purpose: Waterbirds dataset loading, standard splits
- License: MIT
- Key Files:
  - `wilds/datasets/waterbirds_dataset.py` - Dataset class
  - `examples/configs/datasets.py` - Data loader configs
- Installation: `pip install wilds`
- Usage:
  ```python
  from wilds import get_dataset
  dataset = get_dataset('waterbirds', download=True)
  ```

**GroupDRO Baseline**
- URL: https://github.com/kohpangwei/group_DRO
- Purpose: Reference for Waterbirds training hyperparameters
- License: MIT
- Key Files:
  - `train.py` - Training loop with group tracking
  - `data/data.py` - Waterbirds data loading
  - `models.py` - ResNet-50 setup
- Note: We use standard ERM training (not DRO), only reference hyperparams
- Hyperparameters extracted:
  - LR: 1e-3, momentum: 0.9, weight_decay: 1e-4
  - Batch size: 128, epochs: 300

**Spurious Feature Learning**
- URL: https://github.com/izmailovpavel/spurious_feature_learning
- Purpose: Alternative training reference (Pavel Izmailov et al.)
- License: Apache 2.0
- Relevant: Contains JTT implementation for Waterbirds

### 1.2 GradCAM Implementation

**PyTorch GradCAM (jacobgil)**
- URL: https://github.com/jacobgil/pytorch-grad-cam
- PyPI: `pip install grad-cam` (v1.5.2+)
- Purpose: GradCAM extraction from ResNet-50 layer4
- License: MIT
- Key Classes:
  - `GradCAM` - Main wrapper
  - `ClassifierOutputTarget` - Target class specification
  - `ActivationsAndGradients` - Gradient extraction
- Usage:
  ```python
  from pytorch_grad_cam import GradCAM
  from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
  
  cam = GradCAM(model=model, target_layers=[model.layer4])
  targets = [ClassifierOutputTarget(class_idx)]
  grayscale_cam = cam(input_tensor=image, targets=targets)
  gradients = cam.activations_and_grads.gradients[0]
  ```
- Documentation: https://jacobgil.github.io/pytorch-gradcam-book/introduction.html

**TorchCAM (Alternative)**
- URL: https://github.com/frgfm/torch-cam
- PyPI: `pip install torchcam`
- Purpose: Backup if jacobgil/pytorch-grad-cam has issues
- License: Apache 2.0
- Note: Lighter weight, but jacobgil is preferred (more features)

### 1.3 GAIA Metrics (Conceptual Reference)

**GAIA Paper Reference**
- Paper: "Gradient-based Adversarial and Out-of-distribution Detection" (Chen et al. 2023)
- ArXiv: https://arxiv.org/abs/2301.xxxxx (search "GAIA gradient abnormality")
- Code: Not publicly available (we reimplement from paper description)
- Key Metrics:
  - GAIA-Z: Zero-deflation ratio
  - GAIA-A: Channel-wise variance abnormality
- Our Implementation: Custom (see `utils/gaia_metrics.py`)

---

## 2. Dependencies

### 2.1 Core Libraries

```
# requirements.txt
torch>=2.0.0
torchvision>=0.15.0
numpy>=1.24.0
```

### 2.2 Dataset & Evaluation

```
wilds>=2.0.0
Pillow>=9.5.0
pandas>=2.0.0
```

### 2.3 GradCAM & Metrics

```
grad-cam>=1.5.0
scipy>=1.10.0
scikit-learn>=1.3.0
```

### 2.4 Visualization

```
matplotlib>=3.7.0
seaborn>=0.12.0
```

### 2.5 Configuration & Utilities

```
pyyaml>=6.0
tqdm>=4.65.0
tensorboard>=2.13.0  # Optional, for training logs
```

### 2.6 Full Installation

```bash
# Create environment
conda create -n h_e1 python=3.10
conda activate h_e1

# Install PyTorch (CUDA 11.8 example)
pip install torch==2.0.1 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cu118

# Install remaining dependencies
pip install wilds grad-cam scipy matplotlib seaborn pandas pyyaml tqdm

# Verify installation
python -c "import torch; print(torch.__version__)"
python -c "from wilds import get_dataset; print('WILDS OK')"
python -c "from pytorch_grad_cam import GradCAM; print('GradCAM OK')"
```

---

## 3. Data Files & Paths

### 3.1 Dataset Cache

**Waterbirds (WILDS)**
- Auto-download path: `~/.wilds/waterbirds_v1.0/`
- Size: ~50 MB
- Contents:
  - `metadata.csv` - Sample metadata (class, background, group)
  - `waterbird_complete95_forest2water2/` - Image directory
  - `splits/` - Train/val/test indices

### 3.2 Model Checkpoints

**Pretrained ResNet-50 (ImageNet)**
- Auto-download path: `~/.cache/torch/hub/checkpoints/resnet50-*.pth`
- Size: ~98 MB
- Source: torchvision.models.resnet50(pretrained=True)

**Trained Model (Our Training)**
- Path: `experiments/h_e1_detection/checkpoints/trained_model.pth`
- Size: ~98 MB
- Contents: model.state_dict() + optimizer + epoch + metrics

### 3.3 Output Files

```
experiments/h_e1_detection/outputs/
├── gradients.npz              # Optional, ~500MB (5794 × 2048×7×7 float32)
├── gaia_z_scores.csv          # Required, ~200KB
├── statistical_results.json   # Required, ~1KB
└── training_log.csv           # Training metrics per epoch
```

---

## 4. Implementation Strategy

### 4.1 Code Structure

```
experiments/h_e1_detection/
├── configs/
│   └── config.yaml           # Hyperparameters from specs
├── utils/
│   ├── __init__.py
│   ├── gradcam.py           # GradCAM wrapper (jacobgil integration)
│   ├── gaia_metrics.py      # GAIA-Z computation
│   ├── data_utils.py        # WILDS data loading helpers
│   ├── training.py          # Training loop + group tracking
│   └── visualization.py     # Plotting functions
├── train_model.py           # Step 1: Train ResNet-50
├── collect_gradients.py     # Step 2: Extract GradCAM gradients
├── compute_gaia_z.py        # Step 3: Compute GAIA-Z scores
├── statistical_test.py      # Step 4: t-test + effect size
└── run_experiment.sh        # End-to-end pipeline script
```

### 4.2 Module Breakdown

**train_model.py**
- Load Waterbirds via WILDS
- Initialize ResNet-50 (pretrained ImageNet)
- Train with standard ERM (cross-entropy)
- Track per-group accuracy (WGA, minority_acc)
- Save checkpoint when WGA <80% and minority_acc ≥60%

**collect_gradients.py**
- Load trained model checkpoint
- Initialize GradCAM with layer4 target
- Iterate test set (5794 samples):
  - Forward pass → predicted class
  - Extract GradCAM gradients
  - Store: (sample_id, group_id, gradient_tensor)
- Save gradients.npz (optional, for debugging)

**compute_gaia_z.py**
- Load gradients or recompute on-the-fly
- For each sample:
  - Flatten gradient tensor
  - Compute GAIA-Z = |{g : |g|<ε}| / total
- Aggregate by group (minority vs majority)
- Save gaia_z_scores.csv

**statistical_test.py**
- Load gaia_z_scores.csv
- Separate minority vs majority scores
- Two-sample t-test (scipy.stats.ttest_ind)
- Compute Cohen's d effect size
- Generate visualizations (box plot, histogram)
- Save statistical_results.json
- Print PASS/FAIL decision

---

## 5. Key Implementation Details

### 5.1 GradCAM Gradient Extraction

**Target Layer:**
```python
# ResNet-50 architecture
model.layer4  # Final conv block before avgpool
# Output shape: [batch, 2048, 7, 7] for 224×224 input
```

**Gradient Access:**
```python
from pytorch_grad_cam import GradCAM

cam = GradCAM(model=model, target_layers=[model.layer4])

# Forward pass
output = model(image)
pred_class = output.argmax(dim=1).item()

# Get GradCAM
targets = [ClassifierOutputTarget(pred_class)]
grayscale_cam = cam(input_tensor=image, targets=targets)

# Extract raw gradients
gradients = cam.activations_and_grads.gradients[0]
# Shape: [1, 2048, 7, 7]
```

**Storage Strategy:**
- Option 1 (debugging): Save all gradients in gradients.npz (~500MB)
- Option 2 (efficient): Compute GAIA-Z on-the-fly, only save scores (~200KB)
- Recommended: Option 2 for production, Option 1 if investigation needed

### 5.2 GAIA-Z Computation

```python
import numpy as np

def compute_gaia_z(gradient_tensor, epsilon=1e-6):
    """
    GAIA-Z: Zero-deflation ratio
    
    High score → many near-zero gradients → abnormality
    Low score → few near-zero gradients → normal flow
    """
    flat_grad = gradient_tensor.cpu().numpy().flatten()
    near_zero_mask = np.abs(flat_grad) < epsilon
    near_zero_count = np.sum(near_zero_mask)
    total_elements = flat_grad.size
    
    gaia_z = near_zero_count / total_elements
    return gaia_z
```

**Vectorized (for batch processing):**
```python
def compute_gaia_z_batch(gradient_tensors, epsilon=1e-6):
    """
    gradient_tensors: [N, C, H, W] numpy array
    Returns: [N] array of GAIA-Z scores
    """
    N = gradient_tensors.shape[0]
    flat_grads = gradient_tensors.reshape(N, -1)
    near_zero_counts = np.sum(np.abs(flat_grads) < epsilon, axis=1)
    total_elements = flat_grads.shape[1]
    
    gaia_z_scores = near_zero_counts / total_elements
    return gaia_z_scores
```

### 5.3 Statistical Testing

```python
from scipy.stats import ttest_ind
import numpy as np

def perform_hypothesis_test(minority_scores, majority_scores):
    # Two-sample t-test (Welch's, unequal variance)
    t_stat, p_value = ttest_ind(
        minority_scores, 
        majority_scores, 
        equal_var=False,  # Welch's test
        alternative='two-sided'
    )
    
    # Means
    mean_minority = np.mean(minority_scores)
    mean_majority = np.mean(majority_scores)
    divergence = mean_minority - mean_majority
    
    # Cohen's d
    var_minority = np.var(minority_scores, ddof=1)
    var_majority = np.var(majority_scores, ddof=1)
    pooled_std = np.sqrt((var_minority + var_majority) / 2)
    cohens_d = divergence / pooled_std
    
    # Success criteria
    primary_pass = (divergence >= 0.2) and (p_value < 0.01)
    secondary_pass = (cohens_d >= 0.8)
    gate_pass = primary_pass and secondary_pass
    
    return {
        'minority_mean': mean_minority,
        'majority_mean': mean_majority,
        'divergence': divergence,
        'p_value': p_value,
        't_statistic': t_stat,
        'cohens_d': cohens_d,
        'primary_pass': primary_pass,
        'secondary_pass': secondary_pass,
        'gate_pass': gate_pass
    }
```

---

## 6. Computational Setup

### 6.1 Hardware Requirements

**Minimum:**
- GPU: 1× NVIDIA GPU, 8GB VRAM (RTX 3060 Ti / RTX 3070)
- CPU: 8 cores (for DataLoader workers)
- RAM: 16GB
- Storage: 5GB free (dataset + checkpoints + outputs)

**Recommended:**
- GPU: 1× RTX 3080 / RTX 4070 or better
- CPU: 16 cores
- RAM: 32GB
- Storage: 10GB (for debugging artifacts)

### 6.2 Runtime Estimates

| Task | Duration | GPU Util | Notes |
|------|----------|----------|-------|
| Dataset download | 5 min | N/A | One-time, cached |
| Model training (300 epochs) | 3 hours | ~80% | Batch size 128 |
| Gradient collection (5794 samples) | 15 min | ~60% | Sequential inference |
| GAIA-Z computation | 5 min | N/A | CPU vectorized |
| Statistical analysis | <1 min | N/A | CPU |
| **Total** | **~3.5 hours** | | End-to-end |

### 6.3 Optimization Tips

**Training Speedup:**
- Use `torch.backends.cudnn.benchmark = True` (if input size fixed)
- Mixed precision: `torch.cuda.amp.autocast()` (reduces memory, faster)
- Increase batch size if GPU memory allows (128 → 256)

**Gradient Collection Speedup:**
- Batch inference: process multiple samples simultaneously
- Use `torch.no_grad()` except during GradCAM call
- Pre-load test set to GPU RAM if fits

---

## 7. Troubleshooting

### 7.1 Common Issues

**Issue: WILDS dataset download fails**
- Solution: Manual download from https://wilds.stanford.edu/downloads
- Place in `~/.wilds/waterbirds_v1.0/`

**Issue: GradCAM OOM (out of memory)**
- Solution: Process samples one-by-one instead of batched
- Reduce resolution (not recommended, changes results)

**Issue: WGA too high (≥80%)**
- Cause: Model not learning spurious correlation
- Solution: Check data augmentation (too strong?), verify dataset split, try different random seed

**Issue: Minority accuracy too low (<60%)**
- Cause: Assumption A1 violation
- Impact: GradCAM may highlight spurious features instead of core
- Response: Flag in results, consider global regularization fallback

**Issue: GAIA-Z scores all near 0.5 (uniform)**
- Cause: Gradient computation error or ε too large
- Debug: Visualize raw gradient distributions, check ε=1e-6

### 7.2 Validation Checks

```python
# After training
assert wga < 0.80, f"WGA too high: {wga:.2%}"
assert minority_acc >= 0.60, f"Minority acc too low: {minority_acc:.2%}"
assert avg_acc > 0.95, f"Avg acc too low: {avg_acc:.2%}"

# After GAIA-Z computation
assert gaia_z_df['gaia_z'].std() > 0.01, "GAIA-Z scores degenerate"
assert 0 <= gaia_z_df['gaia_z'].min() <= 1, "GAIA-Z out of range"
```

---

## 8. Next Steps After h-e1

**If h-e1 Passes:**
1. Archive outputs: `outputs/`, `checkpoints/`, `plots/`
2. Proceed to h-m-integrated experiment design
3. Reuse trained model for correlation sweep experiments

**If h-e1 Fails:**
1. Analyze failure mode in detail
2. Generate diagnostic plots (per-sample GAIA-Z vs accuracy)
3. Decision: ABANDON or investigate confounds (complexity, etc.)

---

**Document Status:** Complete  
**Next Action:** Implementation (Phase 3 after experiment design approved)  
**References Last Updated:** 2026-08-20
