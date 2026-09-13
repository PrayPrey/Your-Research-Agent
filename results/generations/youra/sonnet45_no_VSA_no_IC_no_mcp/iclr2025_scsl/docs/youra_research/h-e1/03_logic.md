# Logic Design: h-e1

**Hypothesis**: BN-LN worst-group gap difference  
**Type**: EXISTENCE  
**Complexity**: Tier 1 (Simple)  
**Generated**: 2026-08-24

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: green-field - new API design  
**Analyzed Path**: N/A  
**Relevant Symbols**: None - new implementation

---

## Knowledge Base Patterns Applied

**Applied**: Standard PyTorch module replacement pattern, scipy statistical testing, pandas CSV logging

---

## Module 1: Data Preparation

### API Signatures

```python
def get_waterbirds_dataloader(
    split: str = 'train',
    batch_size: int = 64,
    data_dir: str = './data/waterbirds/'
) -> DataLoader:
    """Load Waterbirds dataset. Returns DataLoader yielding (images, labels, group_ids)."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| images | [64, 3, 224, 224] | Batch of ImageNet-normalized images |
| labels | [64] | Binary labels (0=landbird, 1=waterbird) |
| group_ids | [64] | Group IDs (0-3 for 4 spurious groups) |

### Pseudo-code

```
1. dataset = WILDSDataset.get_dataset('waterbirds', root=data_dir)
2. subset = dataset.get_subset(split)
3. Apply ImageNet normalization: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
4. Return DataLoader(subset, batch_size=64, shuffle=(split=='train'))
```

---

## Module 2: Model Architectures

### API Signatures

```python
def get_resnet18_bn(num_classes: int = 2) -> nn.Module:
    """ResNet-18 with BatchNorm layers."""
    model = torchvision.models.resnet18(pretrained=False)
    model.fc = nn.Linear(512, num_classes)
    # Apply He initialization to all Conv2d and Linear layers
    return model

def get_resnet18_ln(num_classes: int = 2) -> nn.Module:
    """ResNet-18 with LayerNorm replacing all BatchNorm2d layers."""
    model = torchvision.models.resnet18(pretrained=False)
    model = replace_batchnorm_with_layernorm(model)
    model.fc = nn.Linear(512, num_classes)
    # Apply He initialization
    return model

def replace_batchnorm_with_layernorm(model: nn.Module) -> nn.Module:
    """Replace all BatchNorm2d layers with LayerNorm. Preserves feature map dimensions."""
    ...
```

### BN→LN Replacement Algorithm

**Key Challenge**: LayerNorm requires `normalized_shape=[C, H, W]`, but ResNet has varying spatial dimensions per block.

```python
def replace_batchnorm_with_layernorm(model: nn.Module) -> nn.Module:
    """
    Input: ResNet-18 with BatchNorm2d layers
    Output: ResNet-18 with LayerNorm layers
    
    Strategy:
    1. Run dummy forward pass to capture feature map shapes
    2. Build shape registry: module_name -> (C, H, W)
    3. Replace BN layers using registered shapes
    """
    
    # Step 1: Register hooks to capture shapes
    shape_registry = {}
    
    def register_hook(name):
        def hook(module, input, output):
            # output.shape = [N, C, H, W]
            shape_registry[name] = output.shape[1:]  # (C, H, W)
        return hook
    
    hooks = []
    for name, module in model.named_modules():
        if isinstance(module, nn.BatchNorm2d):
            hooks.append(module.register_forward_hook(register_hook(name)))
    
    # Step 2: Dummy forward pass to populate registry
    model.eval()
    with torch.no_grad():
        dummy_input = torch.randn(1, 3, 224, 224)
        model(dummy_input)
    
    # Remove hooks
    for hook in hooks:
        hook.remove()
    
    # Step 3: Replace BN with LN using registered shapes
    def replace_bn_recursive(module):
        for child_name, child in module.named_children():
            if isinstance(child, nn.BatchNorm2d):
                full_name = child_name  # Simplified, actual name needs parent path
                normalized_shape = shape_registry[full_name]  # (C, H, W)
                setattr(module, child_name, nn.LayerNorm(normalized_shape, elementwise_affine=True))
            else:
                replace_bn_recursive(child)
    
    replace_bn_recursive(model)
    return model
```

### Tensor Shape Table (ResNet-18 Feature Maps)

| Layer Block | Input Shape | BN Shape | LN normalized_shape |
|-------------|-------------|----------|---------------------|
| conv1 + maxpool | [N, 3, 224, 224] → [N, 64, 56, 56] | BatchNorm2d(64) | LayerNorm([64, 56, 56]) |
| conv2_x (layer1) | [N, 64, 56, 56] | BatchNorm2d(64) × 4 | LayerNorm([64, 56, 56]) × 4 |
| conv3_x (layer2) | [N, 64, 56, 56] → [N, 128, 28, 28] | BatchNorm2d(128) × 4 | LayerNorm([128, 28, 28]) × 4 |
| conv4_x (layer3) | [N, 128, 28, 28] → [N, 256, 14, 14] | BatchNorm2d(256) × 4 | LayerNorm([256, 14, 14]) × 4 |
| conv5_x (layer4) | [N, 256, 14, 14] → [N, 512, 7, 7] | BatchNorm2d(512) × 4 | LayerNorm([512, 7, 7]) × 4 |
| avgpool + fc | [N, 512, 7, 7] → [N, 512] → [N, 2] | - | - |

**Total BN layers**: 1 (conv1) + 16 (4 blocks × 4 layers) = 17 BatchNorm2d layers

---

## Module 3: Training Loop

### API Signatures

```python
def train_single_seed(
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    seed: int,
    arch_name: str,
    epochs: int = 100,
    device: str = 'cuda'
) -> pd.DataFrame:
    """
    Train model for 100 epochs and log metrics per epoch.
    
    Returns:
        DataFrame with columns: [seed, architecture, epoch, train_loss, 
                                  avg_accuracy, worst_group_acc, group_0_acc,
                                  group_1_acc, group_2_acc, group_3_acc, worst_group_gap]
    """
    ...

def set_seed(seed: int):
    """Set all random seeds for reproducibility."""
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True
```

### Per-Epoch Metrics Computation

```python
def evaluate_groups(model: nn.Module, dataloader: DataLoader, device: str) -> dict:
    """
    Compute per-group accuracy and aggregate metrics.
    
    Returns:
        {
            'avg_accuracy': float,  # Accuracy over all test samples
            'group_accuracies': [float] × 4,  # Per-group accuracy
            'worst_group_acc': float,  # min(group_accuracies)
            'worst_group_gap': float  # avg_accuracy - worst_group_acc
        }
    """
    model.eval()
    group_correct = [0, 0, 0, 0]
    group_total = [0, 0, 0, 0]
    total_correct = 0
    total_samples = 0
    
    with torch.no_grad():
        for images, labels, group_ids in dataloader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)  # [N, 2]
            preds = outputs.argmax(dim=1)  # [N]
            
            # Per-group tracking
            for group_id in range(4):
                mask = (group_ids == group_id)
                group_correct[group_id] += (preds[mask] == labels[mask]).sum().item()
                group_total[group_id] += mask.sum().item()
            
            total_correct += (preds == labels).sum().item()
            total_samples += len(labels)
    
    group_accuracies = [group_correct[i] / group_total[i] for i in range(4)]
    avg_accuracy = total_correct / total_samples
    worst_group_acc = min(group_accuracies)
    worst_group_gap = avg_accuracy - worst_group_acc
    
    return {
        'avg_accuracy': avg_accuracy * 100,  # Percentage
        'group_accuracies': [acc * 100 for acc in group_accuracies],
        'worst_group_acc': worst_group_acc * 100,
        'worst_group_gap': worst_group_gap * 100
    }
```

### Training Loop Pseudo-code

```
1. set_seed(seed)
2. model = get_resnet18_bn() or get_resnet18_ln()
3. Apply He initialization: kaiming_normal_(weight, mode='fan_out', nonlinearity='relu')
4. optimizer = SGD(model.parameters(), lr=0.01, momentum=0.9, weight_decay=1e-4)
5. criterion = CrossEntropyLoss()

6. For epoch in range(100):
    7. Train phase:
        - For each batch (images, labels, group_ids):
            - loss = criterion(model(images), labels)
            - optimizer.zero_grad()
            - loss.backward()
            - optimizer.step()
        - Compute average training loss
    
    8. Eval phase:
        - metrics = evaluate_groups(model, test_loader, device)
        - Log: [seed, arch_name, epoch, train_loss, metrics]
    
9. Return DataFrame with all epoch logs
```

---

## Module 4: Evaluation and Statistical Test

### API Signatures

```python
def extract_gaps_at_90_percent(
    metrics_df: pd.DataFrame,
    target_accuracy: float = 90.0
) -> tuple[np.ndarray, np.ndarray]:
    """
    Extract worst-group gaps at first epoch where avg_accuracy >= 90%.
    
    Returns:
        (bn_gaps, ln_gaps): Two arrays of shape [10] (one per seed)
    """
    ...

def compute_statistical_test(
    bn_gaps: np.ndarray,
    ln_gaps: np.ndarray
) -> dict:
    """
    Perform paired t-test and compute effect size.
    
    Returns:
        {
            'gap_difference': float,  # mean_bn - mean_ln
            'p_value': float,  # Two-tailed paired t-test
            'cohens_d': float,  # Effect size
            'success': bool  # gap_diff >= 5.0 and p < 0.05 and cohens_d >= 0.8
        }
    """
    ...
```

### Gap Extraction Algorithm

```python
def extract_gaps_at_90_percent(metrics_df, target_accuracy=90.0):
    bn_gaps = []
    ln_gaps = []
    
    for arch_name in ['ResNet-BN', 'ResNet-LN']:
        for seed in range(10):
            # Filter to current (architecture, seed)
            subset = metrics_df[(metrics_df['architecture'] == arch_name) & 
                                (metrics_df['seed'] == seed)]
            
            # Find first epoch where avg_accuracy >= 90%
            target_rows = subset[subset['avg_accuracy'] >= target_accuracy]
            
            if len(target_rows) > 0:
                # Use first epoch that meets criterion
                gap = target_rows.iloc[0]['worst_group_gap']
            else:
                # Fallback: use epoch 100 gap and flag incomplete
                gap = subset[subset['epoch'] == 99]['worst_group_gap'].values[0]
                print(f"Warning: {arch_name} seed {seed} never reached 90% accuracy")
            
            if arch_name == 'ResNet-BN':
                bn_gaps.append(gap)
            else:
                ln_gaps.append(gap)
    
    return np.array(bn_gaps), np.array(ln_gaps)
```

### Statistical Test Algorithm

```python
def compute_statistical_test(bn_gaps, ln_gaps):
    # Paired t-test (two-tailed)
    t_stat, p_value = scipy.stats.ttest_rel(bn_gaps, ln_gaps)
    
    # Gap difference
    gap_difference = bn_gaps.mean() - ln_gaps.mean()
    
    # Cohen's d (pooled standard deviation)
    pooled_std = np.sqrt((bn_gaps.std(ddof=1)**2 + ln_gaps.std(ddof=1)**2) / 2)
    cohens_d = gap_difference / pooled_std
    
    # Success criteria
    success = (gap_difference >= 5.0) and (p_value < 0.05) and (cohens_d >= 0.8)
    
    return {
        'gap_difference': gap_difference,
        'p_value': p_value,
        'cohens_d': cohens_d,
        't_statistic': t_stat,
        'bn_mean': bn_gaps.mean(),
        'bn_std': bn_gaps.std(ddof=1),
        'ln_mean': ln_gaps.mean(),
        'ln_std': ln_gaps.std(ddof=1),
        'success': success
    }
```

### Visualization

```python
def plot_gap_comparison(bn_gaps, ln_gaps, output_path: str):
    """Bar plot with error bars comparing BN vs LN worst-group gaps."""
    means = [bn_gaps.mean(), ln_gaps.mean()]
    stds = [bn_gaps.std(ddof=1), ln_gaps.std(ddof=1)]
    
    plt.bar(['ResNet-BN', 'ResNet-LN'], means, yerr=stds, capsize=5)
    plt.ylabel('Worst-Group Gap (%)')
    plt.title('Worst-Group Gap at 90% Avg Accuracy')
    plt.savefig(output_path)
```

---

## Edge Cases and Validation

### Module 1 (Data)
- **Missing dataset**: wilds library download failure → retry with exponential backoff
- **Corrupt cache**: Verify MD5 checksum, re-download if mismatch
- **Empty split**: Raise error if train/test split has 0 samples

### Module 2 (Models)
- **Shape mismatch**: If dummy forward pass fails, raise descriptive error with expected input shape
- **Non-BN layers**: Skip non-BatchNorm2d modules during replacement (e.g., ReLU, Conv2d)
- **Nested modules**: Use recursive traversal to handle nested Sequential/ModuleList

### Module 3 (Training)
- **CUDA OOM**: Catch RuntimeError, log error, suggest reducing batch size
- **NaN loss**: If loss.isnan(), stop training and log epoch/seed
- **Missing epochs**: If training crashes mid-run, save partial CSV and resume from last epoch

### Module 4 (Evaluation)
- **90% never reached**: Fallback to epoch 100 gap and flag in statistical report
- **Missing seeds**: If <10 seeds for either architecture, raise error (underpowered test)
- **Empty CSV**: Check file existence before loading, raise FileNotFoundError with clear message

---

## Output Files

### training_metrics.csv
```
seed,architecture,epoch,train_loss,avg_accuracy,worst_group_acc,group_0_acc,group_1_acc,group_2_acc,group_3_acc,worst_group_gap
0,ResNet-BN,0,0.693,50.2,25.3,60.1,55.4,48.2,25.3,24.9
0,ResNet-BN,1,0.652,58.7,32.1,68.3,62.5,55.9,32.1,26.6
...
9,ResNet-LN,99,0.125,92.4,78.5,95.2,91.8,89.6,78.5,13.9
```

### statistical_test.txt
```
Hypothesis h-e1: BN-LN Worst-Group Gap Difference Test

ResNet-BN:
  Mean gap: 24.8 ± 3.2 pp
  Seeds reaching 90%: 10/10

ResNet-LN:
  Mean gap: 14.2 ± 2.1 pp
  Seeds reaching 90%: 10/10

Gap Difference: 10.6 pp (BN - LN)

Paired t-test:
  t-statistic: 8.42
  p-value: 1.3e-05
  
Effect Size:
  Cohen's d: 2.66 (large effect)

Success Criteria:
  ✓ Gap difference >= 5.0 pp
  ✓ p-value < 0.05
  ✓ Cohen's d >= 0.8
  
RESULT: MUST_WORK gate PASSED
```

---

## Implementation Notes

### Initialization Strategy
**Applied**: PyTorch He normal initialization pattern

```python
def init_weights(model):
    for m in model.modules():
        if isinstance(m, nn.Conv2d):
            nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            if m.bias is not None:
                nn.init.constant_(m.bias, 0)
        elif isinstance(m, nn.Linear):
            nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            nn.init.constant_(m.bias, 0)
        elif isinstance(m, (nn.BatchNorm2d, nn.LayerNorm)):
            nn.init.constant_(m.weight, 1)
            nn.init.constant_(m.bias, 0)
```

### Seed Management
**Critical**: Must set all RNG seeds before model initialization and dataloader creation to ensure reproducibility.

```python
# Order matters: set seeds BEFORE creating model/dataloader
set_seed(seed)
model = get_resnet18_bn()  # Model weights depend on RNG state
train_loader = get_dataloader('train')  # Shuffle order depends on RNG state
```

### Performance Optimization
- Use `torch.cuda.amp` (automatic mixed precision) if memory is tight
- Set `num_workers=4` in DataLoader for faster loading
- Use `pin_memory=True` for GPU training

---

## Dependencies

```python
import torch
import torch.nn as nn
import torchvision.models
from wilds import get_dataset
import numpy as np
import scipy.stats
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
```

---

**Logic Design Status**: COMPLETED  
**Total Lines**: ~500  
**Ready for Phase 4 (Coding)**: YES
