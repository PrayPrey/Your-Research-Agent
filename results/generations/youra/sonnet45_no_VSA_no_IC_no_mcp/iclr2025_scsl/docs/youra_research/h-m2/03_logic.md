# Logic Design: h-m2

**Hypothesis**: Attention Correction Mechanism  
**Complexity**: Tier 1 (Simple)  
**Generated**: 2026-08-25

---

## Codebase Analysis (Serena)

**Project Type**: Green-field  
**Status**: New API design (no existing code to analyze)  
**Analyzed Path**: N/A  
**Relevant Symbols**: None - new implementation

---

## CBAM Attention Module

**Applied**: CBAM attention mechanism (Woo et al. 2018)

### API Signatures

```python
class ChannelAttention(nn.Module):
    def __init__(self, channels: int, reduction: int = 16):
        """Channel attention. channels: input channels, reduction: MLP bottleneck."""
        ...

    def forward(self, x: Tensor) -> Tensor:
        """Apply channel attention. x: [B,C,H,W] -> [B,C,1,1]"""
        ...


class SpatialAttention(nn.Module):
    def __init__(self, kernel_size: int = 7):
        """Spatial attention. kernel_size: conv filter size."""
        ...

    def forward(self, x: Tensor) -> Tensor:
        """Apply spatial attention. x: [B,C,H,W] -> [B,1,H,W]"""
        ...


class CBAM(nn.Module):
    def __init__(self, channels: int, reduction: int = 16, kernel_size: int = 7):
        """CBAM module. channels: feature channels."""
        ...

    def forward(self, x: Tensor) -> Tensor:
        """Apply channel+spatial attention. x: [B,C,H,W] -> [B,C,H,W]"""
        ...
```

### Pseudo-code

```
ChannelAttention:
1. avg = adaptive_avg_pool2d(x)  # [B,C,H,W] -> [B,C,1,1]
2. max = adaptive_max_pool2d(x)  # [B,C,H,W] -> [B,C,1,1]
3. mlp_avg = fc2(relu(fc1(avg)))  # fc1: [C,C//16], fc2: [C//16,C]
4. mlp_max = fc2(relu(fc1(max)))
5. return sigmoid(mlp_avg + mlp_max)  # [B,C,1,1]

SpatialAttention:
1. avg = mean(x, dim=1, keepdim=True)  # [B,C,H,W] -> [B,1,H,W]
2. max = max(x, dim=1, keepdim=True)   # [B,C,H,W] -> [B,1,H,W]
3. concat = cat([avg, max], dim=1)      # [B,2,H,W]
4. conv = conv2d(concat, kernel=7, pad=3)  # [B,2,H,W] -> [B,1,H,W]
5. return sigmoid(conv)  # [B,1,H,W]

CBAM:
1. ca = channel_attn(x)  # [B,C,1,1]
2. x_ca = x * ca         # [B,C,H,W] broadcast
3. sa = spatial_attn(x_ca)  # [B,1,H,W]
4. return x_ca * sa      # [B,C,H,W] broadcast
```

---

## ResNet-CBAM Integration

**Applied**: Insert CBAM after residual blocks

### API Signatures

```python
class ResNetCBAM(nn.Module):
    def __init__(self, num_classes: int = 2, reduction: int = 16):
        """ResNet-18 with CBAM. num_classes: output classes."""
        ...

    def forward(self, x: Tensor) -> Tensor:
        """Forward pass. x: [B,3,224,224] -> [B,num_classes]"""
        ...
```

### Pseudo-code

```
1. base_resnet = torchvision.resnet18(pretrained=False)
2. Insert CBAM after each layer2, layer3, layer4 block (4 CBAMs total)
3. Modify final fc layer: in_features=512, out_features=num_classes
4. Initialize: He normal for ResNet, Xavier normal for CBAM
```

---

## ViT-Small Integration

**Applied**: timm ViT-Small with 2-class head

### API Signatures

```python
def create_vit_small(num_classes: int = 2) -> nn.Module:
    """Create ViT-Small from timm. Returns model."""
    ...
```

### Pseudo-code

```
1. model = timm.create_model('vit_small_patch16_224', pretrained=False, num_classes=num_classes)
2. return model  # config: patch=16, dim=384, depth=12, heads=6
```

---

## Slope Computation

**Applied**: scipy.stats.linregress for linear fit

### API Signatures

```python
def compute_slope(gap_trajectory: np.ndarray, epochs: np.ndarray) -> float:
    """
    Compute slope via linear regression.
    gap_trajectory: [31,] values for epochs 20-50
    epochs: [31,] epoch indices (20,21,...,50)
    Returns: slope β₁ (pp/epoch)
    """
    ...


def compute_slopes_per_architecture(
    logs: pd.DataFrame, 
    architecture: str, 
    start_epoch: int = 20, 
    end_epoch: int = 50
) -> np.ndarray:
    """
    Compute slopes for all seeds.
    logs: DataFrame with columns [epoch, seed, arch, worst_group_gap]
    architecture: 'resnet_bn', 'resnet_cbam', or 'vit_small'
    Returns: [num_seeds,] slopes
    """
    ...
```

### Pseudo-code

```
compute_slope:
1. slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(epochs, gap_trajectory)
2. return slope

compute_slopes_per_architecture:
1. filter logs to architecture
2. for each seed:
     a. extract gap values for epochs [start_epoch, end_epoch]
     b. slope = compute_slope(gap_values, epoch_indices)
     c. append slope
3. return np.array(slopes)
```

---

## Bootstrap CI

**Applied**: Percentile bootstrap with 1000 resamples

### API Signatures

```python
def bootstrap_ci(
    slopes: np.ndarray, 
    n_bootstrap: int = 1000, 
    confidence: float = 0.95,
    seed: int = 42
) -> Tuple[float, float, float]:
    """
    Compute bootstrap CI.
    slopes: [num_seeds,] slope values
    Returns: (ci_lower, mean, ci_upper)
    """
    ...
```

### Pseudo-code

```
1. rng = np.random.default_rng(seed)
2. bootstrap_means = []
3. for i in range(n_bootstrap):
     a. resample = rng.choice(slopes, size=len(slopes), replace=True)
     b. bootstrap_means.append(resample.mean())
4. alpha = (1 - confidence) / 2
5. ci_lower = np.percentile(bootstrap_means, alpha * 100)
6. ci_upper = np.percentile(bootstrap_means, (1 - alpha) * 100)
7. return (ci_lower, slopes.mean(), ci_upper)
```

---

## Cohen's d

**Applied**: Pooled standard deviation effect size

### API Signatures

```python
def cohens_d(slopes_a: np.ndarray, slopes_b: np.ndarray) -> float:
    """
    Compute Cohen's d.
    slopes_a: [num_seeds,] slopes for architecture A
    slopes_b: [num_seeds,] slopes for architecture B (baseline)
    Returns: d (effect size)
    """
    ...
```

### Pseudo-code

```
1. mean_a = slopes_a.mean()
2. mean_b = slopes_b.mean()
3. var_a = slopes_a.var(ddof=1)
4. var_b = slopes_b.var(ddof=1)
5. pooled_std = sqrt((var_a + var_b) / 2)
6. d = (mean_a - mean_b) / pooled_std
7. return d
```

---

## ViT Stability Monitoring

**Applied**: Gradient norm tracking and adaptive clipping

### API Signatures

```python
def monitor_gradients(model: nn.Module) -> Dict[str, float]:
    """
    Compute gradient norms per layer.
    Returns: {layer_name: grad_norm}
    """
    ...


def apply_gradient_clipping(model: nn.Module, max_norm: float = 1.0) -> float:
    """
    Clip gradients if norm exceeds threshold.
    Returns: total_norm before clipping
    """
    ...


def check_loss_spike(
    current_loss: float, 
    loss_history: List[float], 
    spike_threshold: float = 2.0
) -> bool:
    """
    Detect loss spike.
    Returns: True if current_loss > spike_threshold * prev_loss
    """
    ...
```

### Pseudo-code

```
monitor_gradients:
1. grad_norms = {}
2. for name, param in model.named_parameters():
     if param.grad is not None:
         grad_norms[name] = param.grad.norm().item()
3. return grad_norms

apply_gradient_clipping:
1. total_norm = nn.utils.clip_grad_norm_(model.parameters(), max_norm)
2. return total_norm

check_loss_spike:
1. if len(loss_history) == 0: return False
2. prev_loss = loss_history[-1]
3. return current_loss > spike_threshold * prev_loss
```

---

## Training Loop with Stability Checks

**Applied**: Standard ERM with ViT-specific safeguards

### API Signatures

```python
def train_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    optimizer: Optimizer,
    criterion: nn.Module,
    device: str,
    architecture: str
) -> Tuple[float, Dict[str, float]]:
    """
    Train one epoch.
    architecture: 'resnet_bn', 'resnet_cbam', 'vit_small'
    Returns: (avg_loss, grad_stats)
    """
    ...


def evaluate_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    device: str
) -> Dict[str, float]:
    """
    Evaluate on test set.
    Returns: {
        'avg_acc': float,
        'worst_group_acc': float,
        'worst_group_gap': float,
        'group_accs': [4 floats]
    }
    """
    ...
```

### Pseudo-code

```
train_epoch:
1. model.train()
2. total_loss = 0
3. for batch in dataloader:
     a. images, labels, groups = batch
     b. logits = model(images)
     c. loss = criterion(logits, labels)
     d. loss.backward()
     e. if architecture == 'vit_small':
          - total_norm = apply_gradient_clipping(model, max_norm=1.0)
          - log total_norm
     f. optimizer.step()
     g. optimizer.zero_grad()
     h. total_loss += loss.item()
4. avg_loss = total_loss / len(dataloader)
5. grad_stats = monitor_gradients(model) if architecture == 'vit_small' else {}
6. return avg_loss, grad_stats

evaluate_epoch:
1. model.eval()
2. all_preds, all_labels, all_groups = [], [], []
3. for batch in dataloader:
     images, labels, groups = batch
     with torch.no_grad():
         logits = model(images)
         preds = logits.argmax(dim=1)
     all_preds.append(preds)
     all_labels.append(labels)
     all_groups.append(groups)
4. Concatenate predictions, labels, groups
5. avg_acc = accuracy(all_preds, all_labels)
6. For each group in [0,1,2,3]:
     group_acc = accuracy(preds[groups==g], labels[groups==g])
7. worst_group_acc = min(group_accs)
8. worst_group_gap = avg_acc - worst_group_acc
9. return metrics dict
```

---

## Main Training Function

**Applied**: 3 architectures × 10 seeds

### API Signatures

```python
def run_experiment(
    architectures: List[str] = ['resnet_bn', 'resnet_cbam', 'vit_small'],
    seeds: List[int] = list(range(10)),
    num_epochs: int = 100,
    lr: float = 0.01,
    batch_size: int = 64,
    device: str = 'cuda'
) -> pd.DataFrame:
    """
    Run full experiment.
    Returns: DataFrame with all training logs
    """
    ...
```

### Pseudo-code

```
1. results = []
2. for architecture in architectures:
     for seed in seeds:
         a. set_seed(seed)
         b. model = create_model(architecture)
         c. optimizer = SGD(model.parameters(), lr=lr, momentum=0.9, weight_decay=1e-4)
         d. criterion = CrossEntropyLoss()
         e. loss_history = []
         f. for epoch in range(num_epochs):
              i. train_loss, grad_stats = train_epoch(...)
              ii. metrics = evaluate_epoch(...)
              iii. loss_history.append(train_loss)
              iv. if check_loss_spike(train_loss, loss_history) and architecture == 'vit_small':
                    - reduce lr to 0.001
                    - log warning
              v. record: {epoch, seed, arch, train_loss, **metrics}
              vi. results.append(record)
         g. save checkpoint at epoch 100
3. return pd.DataFrame(results)
```

---

## Statistical Analysis Pipeline

**Applied**: Full hypothesis test workflow

### API Signatures

```python
def analyze_slopes(
    logs: pd.DataFrame,
    start_epoch: int = 20,
    end_epoch: int = 50
) -> pd.DataFrame:
    """
    Compute slopes and CIs for all architectures.
    Returns: DataFrame with columns [arch, mean_slope, ci_lower, ci_upper, cohens_d]
    """
    ...
```

### Pseudo-code

```
1. results = []
2. baseline_slopes = compute_slopes_per_architecture(logs, 'resnet_bn', start_epoch, end_epoch)
3. for architecture in ['resnet_bn', 'resnet_cbam', 'vit_small']:
     a. slopes = compute_slopes_per_architecture(logs, architecture, start_epoch, end_epoch)
     b. ci_lower, mean, ci_upper = bootstrap_ci(slopes)
     c. d = cohens_d(slopes, baseline_slopes) if architecture != 'resnet_bn' else 0.0
     d. results.append({
          'architecture': architecture,
          'mean_slope': mean,
          'ci_lower': ci_lower,
          'ci_upper': ci_upper,
          'cohens_d': d
        })
4. return pd.DataFrame(results)
```

---

## Success Criteria Check

**Applied**: Automated hypothesis test

### API Signatures

```python
def check_hypothesis(
    slope_stats: pd.DataFrame,
    slope_threshold: float = 0.3,
    effect_size_threshold: float = 0.8
) -> Dict[str, Any]:
    """
    Test hypothesis.
    Returns: {
        'cbam_success': bool,
        'vit_success': bool,
        'interpretation': str,
        'details': dict
    }
    """
    ...
```

### Pseudo-code

```
1. Extract BN stats: bn_mean, bn_ci_lower, bn_ci_upper
2. For CBAM:
     a. cbam_mean, cbam_ci_lower, cbam_ci_upper, cbam_d = extract
     b. ci_overlap = not (cbam_ci_upper < bn_ci_lower or cbam_ci_lower > bn_ci_upper)
     c. slope_diff = bn_mean - cbam_mean  # positive if CBAM steeper negative
     d. cbam_success = (not ci_overlap) and (slope_diff >= slope_threshold) and (cbam_d >= effect_size_threshold)
3. Repeat for ViT
4. Interpretation matrix:
     - if cbam_success and vit_success: "Attention enables correction"
     - if cbam_success and not vit_success: "Channel attention sufficient"
     - if not cbam_success and vit_success: "Global architecture, not attention"
     - if not cbam_success and not vit_success: "Hypothesis falsified"
5. return {cbam_success, vit_success, interpretation, details}
```

---

## Validation Summary

**Total LoC Estimate**: ~450 lines
- CBAM module: ~60 lines
- ResNet-CBAM integration: ~40 lines
- ViT integration: ~10 lines (timm)
- Training loop: ~100 lines
- Evaluation: ~50 lines
- Slope computation: ~60 lines
- Bootstrap CI: ~30 lines
- Cohen's d: ~15 lines
- Stability monitoring: ~30 lines
- Statistical analysis: ~55 lines

**Dependencies**:
- torch, torchvision (models, ResNet)
- timm (ViT)
- scipy.stats (linregress)
- numpy (bootstrap, statistics)
- pandas (logs)

**Complexity**: Tier 1 (standard architectures, standard statistics)
