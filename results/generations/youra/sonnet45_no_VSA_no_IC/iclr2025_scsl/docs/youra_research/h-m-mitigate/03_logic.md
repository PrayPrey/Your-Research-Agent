# Logic Design: H-M-MITIGATE
## Spatial Gradient Regularization

**Hypothesis ID:** h-m-mitigate  
**Type:** MECHANISM (Mitigation)  
**Generated:** 2026-08-20  

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: API signatures verified from h-m-integrated code  
**Analyzed Path**: h-m-integrated/code/  
**Relevant Symbols**: create_resnet50, WaterbirdsDataset, GroupTracker, get_train_transforms, get_eval_transforms, GradCAMExtractor, compute_gaia_z  
**Note**: Green-field for mitigation trainer (new implementation), reuses base utilities

---

## M-3: Spatial Regularization Trainer [Complexity: 12, Budget: 5]

**Applied**: Standard PyTorch training loop with custom loss

### API Signatures

```python
class SpatialRegTrainer:
    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        device: torch.device,
        config: dict
    ):
        """config: {lr, lambda_init, percentile_threshold, epochs, patience}"""
        self.model = model
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = torch.optim.SGD(model.parameters(), lr=config['lr'], momentum=0.9, weight_decay=1e-4)
        self.lambda_penalty = config['lambda_init']
        self.tracker = GroupTracker()
        from pytorch_grad_cam import GradCAM
        self.gradcam = GradCAM(model=model, target_layers=[model.layer4[-1]])
    
    def compute_spurious_mask(self, imgs: Tensor, labels: Tensor, group_ids: Tensor) -> Tensor:
        """imgs: [B,3,H,W], labels: [B], group_ids: [B] -> mask: [H,W]"""
    
    def compute_regularization_loss(self, imgs: Tensor, mask: Tensor) -> Tensor:
        """imgs: [B,3,H,W], mask: [H,W] -> scalar"""
    
    def train_epoch(self) -> dict:
        """Returns: {loss, wga, avg_acc}"""
    
    def validate(self) -> dict:
        """Returns: {loss, wga, avg_acc}"""
    
    def fit(self) -> dict:
        """Returns: {best_wga, best_epoch}"""
```

### Pseudo-code

**compute_spurious_mask:**
```
1. majority_mask = (group_ids == 0) | (group_ids == 3)
   minority_mask = (group_ids == 1) | (group_ids == 2)
2. If either empty: return zeros([H,W])
3. Subsample max 16 per group:
   cam_maj = gradcam(imgs[majority_mask[:16]], labels[majority_mask[:16]])
   cam_min = gradcam(imgs[minority_mask[:16]], labels[minority_mask[:16]])
4. Average: cam_maj_mean = mean(cam_maj, dim=0), cam_min_mean = mean(cam_min, dim=0)
5. Difference: diff = abs(cam_maj_mean - cam_min_mean)
6. Threshold: mask = (diff > percentile(diff, threshold)).float()
```

**compute_regularization_loss:**
```
1. imgs.requires_grad = True
2. outputs = model(imgs)
3. grads = autograd.grad(outputs.sum(), imgs, create_graph=True)[0]  # [B,3,H,W]
4. var_spatial = grads.var(dim=1)  # [B,H,W]
5. mask_resized = F.interpolate(mask.unsqueeze(0).unsqueeze(0), size=(H,W))
6. masked_var = var_spatial * mask_resized.squeeze()
7. Return masked_var.mean()
```

**train_epoch:**
```
1. For batch_idx, (imgs, labels, metadata) in enumerate(train_loader):
   a. group_ids = metadata[:, 2]
   b. If batch_idx % 10 == 0: cached_mask = compute_spurious_mask(imgs, labels, group_ids)
   c. outputs = model(imgs)
   d. loss_ce = criterion(outputs, labels)
   e. loss_reg = compute_regularization_loss(imgs, cached_mask)
   f. loss = loss_ce + lambda_penalty * loss_reg
   g. optimizer.zero_grad(); loss.backward(); optimizer.step()
   h. tracker.update(outputs.argmax(1), labels, group_ids)
2. Return tracker.compute_metrics()
```

**validate:**
```
1. Evaluate without regularization
2. wga_gap = majority_acc - minority_acc
3. lambda_penalty *= exp(0.1 * wga_gap)
4. Clamp lambda_penalty to [0.001, 1.0]
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M3-1 | GradCAM difference map | Majority/minority CAM averaging and thresholding |
| L-M3-2 | Gradient variance penalty | autograd.grad for input gradients, variance on masked regions |
| L-M3-3 | Adaptive lambda scaling | WGA gap-based exponential adjustment |
| L-M3-4 | Training loop integration | CE loss + regularization with caching every 10 batches |
| L-M3-5 | Early stopping | Track best WGA with patience |

---

## M-8: Waterbirds Experiments [Complexity: 11, Budget: 5]

**Applied**: Grid search with multi-seed orchestration

### API Signatures

```python
def run_waterbirds_experiments(data_root: str, output_dir: str, seeds: List[int] = [0,1,2,3,4]) -> pd.DataFrame:
    """Returns: columns [method, seed, wga, avg_acc, best_epoch]"""

def hyperparameter_search(data_root: str, output_dir: str, lambda_grid=[0.001,0.01,0.1], percentile_grid=[75,85,95], seed=0) -> dict:
    """Returns: {best_config, best_wga}"""

def run_single_method(method: str, data_root: str, output_dir: str, config: dict, seed: int) -> dict:
    """method: 'erm'|'groupdro'|'spatial_reg' -> {wga, avg_acc, best_epoch}"""
```

### Pseudo-code

**run_waterbirds_experiments:**
```
1. For method in ['erm', 'groupdro', 'spatial_reg']:
   a. If method == 'spatial_reg': config = hyperparameter_search(data_root, output_dir, seed=seeds[0])['best_config']
   b. Else: config = default_config[method]
   c. For seed in seeds:
      - metrics = run_single_method(method, data_root, output_dir, config, seed)
      - Append {method, seed, **metrics}
2. Return pd.DataFrame(results)
```

**hyperparameter_search:**
```
1. For lambda_init in lambda_grid:
     For percentile in percentile_grid:
       config = {lambda_init, percentile, lr=0.001, epochs=50, batch_size=128}
       trainer = SpatialRegTrainer(model, train_loader, val_loader, device, config)
       metrics = trainer.fit()
       Track best_wga and best_config
2. Return {best_config, best_wga}
```

**run_single_method:**
```
1. set_seed(seed)
2. train_loader, val_loader = get_waterbirds_loaders(data_root, batch_size)
3. model = create_resnet50(num_classes=2, pretrained=True)
4. trainer = {ERMTrainer|GroupDROTrainer|SpatialRegTrainer}(...)
5. metrics = trainer.fit()
6. Save checkpoint to output_dir / method / f"seed_{seed}/best_model.pth"
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M8-1 | Hyperparameter grid search | 3×3 grid over lambda_init and percentile_threshold |
| L-M8-2 | Multi-method orchestration | Loop over ERM, GroupDRO, SpatialReg |
| L-M8-3 | Seed management | 5 seeds per method |
| L-M8-4 | Checkpoint saving | Save best model per seed |
| L-M8-5 | Results aggregation | Collect metrics into DataFrame |

---

## M-6: Evaluation Pipeline [Complexity: 9, Budget: 5]

**Applied**: scipy bootstrap, matplotlib heatmaps

### API Signatures

```python
def compute_worst_group_accuracy(predictions: np.ndarray, labels: np.ndarray, groups: np.ndarray) -> dict:
    """Returns: {wga, avg_acc, group_accs}"""

def bootstrap_comparison(method1_wga: np.ndarray, method2_wga: np.ndarray, n_resamples=1000) -> dict:
    """method1_wga: [5], method2_wga: [5] -> {mean_diff, p_value, ci_lower, ci_upper}"""

def visualize_gradcam_shift(model_before: nn.Module, model_after: nn.Module, test_loader: DataLoader, save_path: str, n_samples=10) -> None:
    """Plot GradCAM heatmaps before/after regularization"""
```

### Pseudo-code

**compute_worst_group_accuracy:**
```
1. For group_id in [0,1,2,3]:
     acc = (predictions[groups==group_id] == labels[groups==group_id]).mean()
     group_accs.append(acc)
2. wga = min(group_accs)
3. avg_acc = (predictions == labels).mean()
```

**bootstrap_comparison:**
```
1. For i in range(n_resamples):
     idx = random.choice([0,1,2,3,4], size=5, replace=True)
     diff = method1_wga[idx].mean() - method2_wga[idx].mean()
     diff_samples.append(diff)
2. p_value = (diff_samples <= 0).sum() / n_resamples
3. ci = percentile(diff_samples, [2.5, 97.5])
```

**visualize_gradcam_shift:**
```
1. Select n_samples from test_loader (stratified by group)
2. For each: cam_before, cam_after = GradCAM(model_before)(sample), GradCAM(model_after)(sample)
3. Plot side-by-side with heatmap overlay
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M6-1 | WGA computation | Per-group accuracy with min selection |
| L-M6-2 | Bootstrap resampling | Pairwise resampling 1000 iterations |
| L-M6-3 | Statistical significance | p-value from empirical null |
| L-M6-4 | GradCAM visualization | Heatmap overlay before/after |
| L-M6-5 | Results export | Save CSV and PNG |

---

## External Dependencies (Base Hypothesis)

### API Signatures (From h-m-integrated Code)

```python
# From: h-m-integrated/code/train_single.py and h-e1/gaia_utils.py

def create_resnet50(num_classes: int = 2, pretrained: bool = True) -> nn.Module:
    """ResNet-50 with modified FC layer"""

def set_seed(seed: int) -> None:
    """Set random seeds"""

def get_train_transforms() -> transforms.Compose:
    """Training augmentation"""

def get_eval_transforms() -> transforms.Compose:
    """Evaluation preprocessing"""

class GroupTracker:
    def reset(self) -> None: ...
    def update(self, predictions: Tensor, labels: Tensor, group_ids: Tensor) -> None: ...
    def compute_metrics(self) -> dict:
        """Returns: {wga, avg_acc, group_0_acc, ...}"""

class WaterbirdsDataset(Dataset):
    def __init__(self, root_dir: str, split: str, transform: Optional[Callable] = None): ...
    def __getitem__(self, idx: int) -> Tuple[Tensor, Tensor, Tensor]:
        """Returns: (image, label, metadata) where metadata=[y, place, group]"""

class GradCAMExtractor:
    def __init__(self, model: nn.Module, target_layer: nn.Module, device: torch.device): ...
    def extract_single(self, image: Tensor, target_class: int) -> np.ndarray:
        """image: [1,3,224,224] -> [2048,7,7]"""

def compute_gaia_z(gradients: np.ndarray, epsilon: float = 1e-6) -> np.ndarray:
    """gradients: [N,C,H,W] -> [N]"""
```

**Verified from**: h-m-integrated/code/ and h-e1/ (actual implementation)

---

## Metadata

- **Document Type:** Logic Design
- **Phase:** 3 (Implementation Planning)
- **Status:** READY FOR IMPLEMENTATION
- **Total Subtasks:** 15 (within 15 budget)
- **External Dependencies:** h-m-integrated (WaterbirdsDataset, GroupTracker, transforms from h-e1)
