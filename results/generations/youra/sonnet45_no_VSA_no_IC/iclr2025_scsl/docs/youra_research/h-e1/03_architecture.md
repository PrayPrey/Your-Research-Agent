# Architecture: H-E1 Gradient Abnormality Detection

**Hypothesis:** h-e1  
**Type:** EXISTENCE  
**Gate:** MUST_WORK  
**Date:** 2026-08-20

**Applied Pattern:** PyTorch standard training + GradCAM extraction + statistical pipeline

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase  
**Status:** Existing h-e1 implementation uses Integrated Gradients (Captum) - incompatible approach  
**Analyzed Path:** h-e1/code  
**Findings:** Current code implements attribution ratios via IntegratedGradients. New task requires GradCAM gradient extraction for GAIA-Z metrics. Complete rewrite needed.

---

## System Overview

**Pipeline:** Train ResNet-50 → Extract GradCAM gradients → Compute GAIA-Z → Statistical test

**Duration:** ~4 hours (3hr train, 1hr analysis)

**Components:**
1. Training module (standard ERM on Waterbirds)
2. GradCAM gradient extraction (pytorch-grad-cam)
3. GAIA-Z metric computation (zero-deflation ratio)
4. Statistical analysis (t-test, Cohen's d)
5. Visualization (box plots, histograms)

---

## Module Interfaces

### 1. DataLoader (`data/loader.py`)

**Dependencies:** WILDS library

```python
class WaterbirdsLoader:
    def __init__(self, root_dir: str, batch_size: int, num_workers: int): ...
    
    def get_train_loader(self) -> DataLoader: ...
    def get_val_loader(self) -> DataLoader: ...
    def get_test_loader(self) -> DataLoader: ...
    def get_group_mapping(self) -> dict: ...  # {group_id: (class, background, is_minority)}
```

### 2. Model (`models/resnet50.py`)

**Dependencies:** torchvision

```python
def create_resnet50_classifier(pretrained: bool = True) -> nn.Module: ...

class ResNet50Wrapper(nn.Module):
    def __init__(self, pretrained: bool): ...
    def forward(self, x: Tensor) -> Tensor: ...
    @property
    def gradcam_layer(self) -> nn.Module: ...  # Returns layer4
```

### 3. Trainer (`training/trainer.py`)

**Dependencies:** DataLoader, ResNet50Wrapper

```python
class ERM_Trainer:
    def __init__(self, model: nn.Module, train_loader: DataLoader, 
                 val_loader: DataLoader, config: dict): ...
    
    def train_epoch(self) -> dict: ...  # Returns {loss, avg_acc}
    def validate(self) -> dict: ...  # Returns {group_acc_0-3, wga, minority_acc}
    def save_checkpoint(self, path: str): ...
    def load_checkpoint(self, path: str): ...
```

### 4. GradCAM Extractor (`gradcam/extractor.py`)

**Dependencies:** pytorch-grad-cam, ResNet50Wrapper

```python
class GradCAMExtractor:
    def __init__(self, model: nn.Module, target_layer: nn.Module): ...
    
    def extract_gradients(self, image: Tensor, target_class: int) -> Tensor: ...
    # Returns shape [1, 2048, 7, 7]
    
    def extract_batch(self, images: Tensor) -> Tensor: ...
    # Returns shape [B, 2048, 7, 7]
```

### 5. GAIA Metrics (`metrics/gaia.py`)

**Dependencies:** numpy

```python
def compute_gaia_z(gradient: Tensor, epsilon: float = 1e-6) -> float: ...
# Returns zero-deflation ratio in [0, 1]

def compute_gaia_z_batch(gradients: Tensor, epsilon: float = 1e-6) -> np.ndarray: ...
# Returns [N] array

def validate_gaia_scores(scores: np.ndarray) -> dict: ...
# Returns {valid: bool, std: float, range: tuple, median: float}
```

### 6. Statistical Test (`analysis/stats.py`)

**Dependencies:** scipy, numpy

```python
def perform_ttest(minority_scores: np.ndarray, 
                  majority_scores: np.ndarray) -> dict:
    """
    Returns:
        {
            'minority_mean': float,
            'majority_mean': float,
            'divergence': float,
            'p_value': float,
            't_statistic': float,
            'cohens_d': float,
            'primary_pass': bool,
            'secondary_pass': bool,
            'gate_pass': bool
        }
    """
    ...
```

### 7. Visualization (`utils/visualize.py`)

**Dependencies:** matplotlib, seaborn

```python
def plot_boxplot_by_type(df: pd.DataFrame, save_path: str): ...
def plot_boxplot_by_group(df: pd.DataFrame, save_path: str): ...
def plot_histogram(df: pd.DataFrame, save_path: str): ...
def save_summary_table(df: pd.DataFrame, stats: dict, save_path: str): ...
```

### 8. Configuration (`config.py`)

```python
@dataclass
class TrainingConfig:
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    batch_size: int = 128
    epochs: int = 300
    early_stop_patience: int = 50

@dataclass
class ExperimentConfig:
    seed: int = 42
    data_root: str = "~/.wilds"
    checkpoint_dir: str = "checkpoints"
    output_dir: str = "outputs"
    training: TrainingConfig = field(default_factory=TrainingConfig)
```

---

## Executable Scripts

### `train.py`

**Purpose:** Train ResNet-50, validate WGA < 80%

**Dependencies:** DataLoader, ResNet50Wrapper, ERM_Trainer

**Flow:**
1. Load Waterbirds dataset
2. Initialize ResNet-50 (ImageNet pretrained)
3. Train with SGD + CosineAnnealingLR
4. Track group accuracies per epoch
5. Early stop on WGA (patience 50)
6. Validate: WGA < 80%, minority_acc ≥ 60%, avg_acc > 95%
7. Save checkpoint

**Outputs:**
- `checkpoints/trained_model.pth`
- `outputs/training_log.csv`

### `collect_gradients.py`

**Purpose:** Extract GradCAM gradients from test set

**Dependencies:** ResNet50Wrapper, GradCAMExtractor, DataLoader

**Flow:**
1. Load trained checkpoint
2. Initialize GradCAM with layer4
3. For each test sample (5794):
   - Forward pass → predicted class
   - Extract GradCAM gradients (shape [2048, 7, 7])
   - Store with group_id
4. Save gradients (optional) or compute GAIA-Z on-the-fly

**Outputs:**
- `outputs/gradients.npz` (optional, ~500MB)
- Or directly compute GAIA-Z

### `compute_gaia_z.py`

**Purpose:** Compute GAIA-Z scores

**Dependencies:** GAIA metrics, numpy

**Flow:**
1. Load gradients (or receive from collect_gradients.py)
2. For each gradient tensor:
   - Flatten to 1D (100,352 elements)
   - Count |g| < 1e-6
   - Compute ratio
3. Validate scores (std > 0.01, range [0,1])
4. Save DataFrame with metadata

**Outputs:**
- `outputs/gaia_z_scores.csv` (columns: sample_id, group_id, is_minority, gaia_z, prediction, ground_truth)

### `analyze.py`

**Purpose:** Statistical test and visualization

**Dependencies:** Statistical test, Visualization

**Flow:**
1. Load gaia_z_scores.csv
2. Separate minority (groups 1,2) vs majority (groups 0,3)
3. Two-sample t-test
4. Compute Cohen's d
5. Evaluate gate criteria
6. Generate plots
7. Save results

**Outputs:**
- `outputs/statistical_results.json`
- `plots/gaia_z_boxplot_by_type.png`
- `plots/gaia_z_boxplot_by_group.png`
- `plots/gaia_z_histogram.png`

### `run_experiment.sh`

**Purpose:** End-to-end pipeline

```bash
#!/bin/bash
python train.py --config configs/config.yaml
python collect_gradients.py --checkpoint checkpoints/trained_model.pth
python compute_gaia_z.py --gradients outputs/gradients.npz
python analyze.py --scores outputs/gaia_z_scores.csv
```

---

## Directory Structure

```
h_e1_detection/
├── configs/
│   └── config.yaml
├── data/
│   └── loader.py
├── models/
│   └── resnet50.py
├── training/
│   └── trainer.py
├── gradcam/
│   └── extractor.py
├── metrics/
│   └── gaia.py
├── analysis/
│   └── stats.py
├── utils/
│   └── visualize.py
├── train.py
├── collect_gradients.py
├── compute_gaia_z.py
├── analyze.py
├── run_experiment.sh
├── config.py
└── README.md
```

---

## Data Flow

```
Waterbirds Dataset (WILDS)
    ↓
[train.py] → checkpoints/trained_model.pth + training_log.csv
    ↓
[collect_gradients.py] → gradients [5794, 2048, 7, 7]
    ↓
[compute_gaia_z.py] → gaia_z_scores.csv
    ↓
[analyze.py] → statistical_results.json + plots/
```

**Critical Path:**
1. Training validates spurious learning (WGA < 80%)
2. GradCAM gradients extracted from layer4
3. GAIA-Z measures zero-deflation per sample
4. Statistical test compares minority vs majority

---

## Integration Points

### Training → Gradient Collection

**Interface:** Model checkpoint file

```python
# train.py saves
torch.save({
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'epoch': epoch,
    'group_accs': group_accs,
    'wga': wga
}, checkpoint_path)

# collect_gradients.py loads
checkpoint = torch.load(checkpoint_path)
model.load_state_dict(checkpoint['model_state_dict'])
```

### Gradient Collection → GAIA Computation

**Option 1:** Save gradients to disk

```python
# collect_gradients.py
np.savez_compressed('gradients.npz', 
                    gradients=all_gradients,  # [5794, 2048, 7, 7]
                    group_ids=group_ids,      # [5794]
                    predictions=predictions)  # [5794]

# compute_gaia_z.py
data = np.load('gradients.npz')
```

**Option 2:** On-the-fly computation (memory efficient)

```python
# collect_gradients.py calls compute_gaia_z.py functions directly
from metrics.gaia import compute_gaia_z_batch

for batch in test_loader:
    gradients = extractor.extract_batch(images)
    scores = compute_gaia_z_batch(gradients)
    # Append to DataFrame
```

**Recommended:** Option 2 (no intermediate storage, faster)

### GAIA Scores → Analysis

**Interface:** CSV DataFrame

```python
# compute_gaia_z.py
df = pd.DataFrame({
    'sample_id': sample_ids,
    'group_id': group_ids,
    'is_minority': is_minority,
    'gaia_z': gaia_z_scores,
    'prediction': predictions,
    'ground_truth': labels
})
df.to_csv('gaia_z_scores.csv', index=False)

# analyze.py
df = pd.read_csv('gaia_z_scores.csv')
```

---

## Error Handling & Validation

### Training Validation

```python
# After training completes
if wga >= 0.80:
    raise ValueError(f"WGA too high: {wga:.2%} (expected <80%). "
                     f"Model not learning spurious correlation.")

if minority_acc < 0.60:
    raise ValueError(f"Minority acc too low: {minority_acc:.2%} (A1 violation). "
                     f"Cannot trust GradCAM attributions.")

if avg_acc <= 0.95:
    raise ValueError(f"Avg acc too low: {avg_acc:.2%}. Model not converged.")
```

### GAIA-Z Validation

```python
# After computing GAIA-Z scores
validation = validate_gaia_scores(scores)

if not validation['valid']:
    if validation['std'] <= 0.01:
        raise ValueError("GAIA-Z scores degenerate (no variance)")
    if validation['median'] <= 0.1 or validation['median'] >= 0.9:
        raise ValueError(f"GAIA-Z median suspect: {validation['median']:.4f}")
```

### GPU Memory Handling

```python
# In collect_gradients.py
try:
    gradients = extractor.extract_batch(images)
except RuntimeError as e:
    if "out of memory" in str(e):
        torch.cuda.empty_cache()
        # Fallback to one-by-one processing
        gradients = []
        for img in images:
            gradients.append(extractor.extract_gradients(img.unsqueeze(0)))
    else:
        raise
```

### Statistical Test Validation

```python
# In analyze.py
if len(minority_scores) == 0 or len(majority_scores) == 0:
    raise ValueError("Empty group for statistical test")

if np.var(minority_scores) == 0 or np.var(majority_scores) == 0:
    raise ValueError("Zero variance in one group (degenerate distribution)")
```

---

## Performance Strategy

### Memory Optimization

**Training:**
- Batch size 128 (fits in 8GB VRAM)
- No gradient accumulation needed
- Standard DataLoader with num_workers=4

**Gradient Collection:**
- Process test set in batches of 32
- Clear cache between batches: `torch.cuda.empty_cache()`
- Use `torch.no_grad()` for forward pass (GradCAM handles gradient internally)

**GAIA-Z Computation:**
- Vectorized numpy operations
- Process in chunks of 1000 samples if memory constrained

### Compute Optimization

**Training:**
- Use `torch.backends.cudnn.benchmark = True` (fixed input size)
- Optional: Mixed precision training (`torch.cuda.amp`)
- Early stopping prevents unnecessary epochs

**Gradient Collection:**
```python
# Batch processing
model.eval()
with torch.no_grad():
    for images, labels, metadata in tqdm(test_loader):
        # GradCAM wrapper handles gradient computation
        gradients = gradcam.extract_batch(images)
        scores = compute_gaia_z_batch(gradients)
```

### Checkpoint Strategy

**During Training:**
- Save every 50 epochs (for debugging)
- Save best WGA checkpoint
- Save final checkpoint (early stop or epoch 300)

**Checkpoint Contents:**
```python
{
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'epoch': epoch,
    'train_log': {
        'loss_history': losses,
        'acc_history': accs,
        'group_acc_history': group_accs
    },
    'best_wga': best_wga
}
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1-1 | Data Pipeline | WILDS loader + group mapping + validation | 8 | 2+2+2+2 (load+map+validate+test) |
| E1-2 | Model Training | ResNet-50 + ERM training + group tracking | 12 | 3+3+3+3 (model+train+track+validate) |
| E1-3 | GradCAM Extraction | pytorch-grad-cam wrapper + batch processing | 10 | 3+3+2+2 (setup+extract+batch+test) |
| E1-4 | GAIA-Z Metrics | Zero-deflation computation + validation | 7 | 2+2+2+1 (compute+batch+validate+test) |
| E1-5 | Statistical Analysis | t-test + Cohen's d + gate evaluation | 8 | 2+2+2+2 (ttest+effect+gate+test) |
| E1-6 | Visualization | Box plots + histogram + summary table | 6 | 2+2+1+1 (boxplot+hist+table+test) |
| E1-7 | Integration | End-to-end pipeline + error handling | 9 | 3+2+2+2 (scripts+errors+validate+test) |

**Distribution:**
- VeryHigh (18-20): []
- High (14-17): []
- Medium (9-13): [E1-2, E1-3, E1-7]
- Low (4-8): [E1-1, E1-4, E1-5, E1-6]

**Total Complexity:** 60 points

---

## Critical Design Decisions

### GradCAM Target Layer

**Choice:** `model.layer4` (final convolutional block)

**Rationale:**
- Highest semantic features before classification
- Standard choice for ResNet attribution
- Output shape [2048, 7, 7] provides spatial granularity

**Alternative:** `model.layer3` (lower semantics, noisier)

### GAIA-Z Epsilon Threshold

**Choice:** `epsilon = 1e-6`

**Rationale:**
- Standard floating-point near-zero threshold
- Avoids numerical precision issues
- Validated in gradient abnormality literature

**Sensitivity:** May need tuning if gradients scale unexpectedly

### On-the-fly vs Stored Gradients

**Choice:** On-the-fly computation (no intermediate storage)

**Rationale:**
- Saves 500MB disk space
- Faster pipeline (no I/O overhead)
- Still allows debugging (can add save flag)

**Fallback:** If investigation needed, save gradients.npz with `--save-gradients` flag

### Statistical Test Type

**Choice:** Welch's t-test (unequal variance)

**Rationale:**
- No assumption of equal variance between groups
- Robust to different group sizes
- Standard for two-sample comparison

**Alternative:** Mann-Whitney U (if distributions highly non-normal, but t-test is robust)

---

## Dependencies

**Core Libraries:**
```
torch>=2.0.0
torchvision>=0.15.0
wilds>=2.0.0
grad-cam>=1.5.0
scipy>=1.10.0
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
pyyaml>=6.0
tqdm>=4.65.0
```

**Installation:**
```bash
pip install torch==2.0.1 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cu118
pip install wilds grad-cam scipy matplotlib seaborn pandas pyyaml tqdm
```

---

## Reproducibility

**Seeds:**
```python
torch.manual_seed(42)
torch.cuda.manual_seed_all(42)
np.random.seed(42)
random.seed(42)
```

**Determinism:**
```python
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
```

**Expected Variance:**
- Training metrics: ±2% across runs (due to CUDA non-determinism)
- GAIA-Z scores: ±0.01 (gradient extraction variance)
- Statistical p-value: Stable if divergence large

---

## Success Criteria Validation

**Gate Evaluation Logic:**

```python
# Primary criteria
primary_pass = (divergence >= 0.2) and (p_value < 0.01)

# Secondary criteria  
secondary_pass = (cohens_d >= 0.8)

# Overall gate
gate_pass = primary_pass and secondary_pass

if gate_pass:
    print("✓ H-E1 PASSED: Gradient abnormality exists")
    # Proceed to h-m-integrated
else:
    print("✗ H-E1 FAILED: ABANDON gradient abnormality approach")
    # Block h-m-integrated and h-m-mitigate
```

**Diagnostic Output:**

```python
if not gate_pass:
    if divergence < 0.2:
        print(f"  - Divergence insufficient: {divergence:.4f} < 0.2")
    if p_value >= 0.01:
        print(f"  - Not statistically significant: p={p_value:.4e}")
    if cohens_d < 0.8:
        print(f"  - Effect size too small: d={cohens_d:.4f} < 0.8")
```

---

## Document Status

**Status:** Complete  
**Version:** 1.0  
**Date:** 2026-08-20  
**Dependencies:** None (foundation hypothesis)  
**Blocks:** h-m-integrated, h-m-mitigate
