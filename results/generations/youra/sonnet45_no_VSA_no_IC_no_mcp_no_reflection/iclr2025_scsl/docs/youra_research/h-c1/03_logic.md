# Logic Design: h-c1 Gradient-Aware Training

**Date:** 2026-08-29  
**Hypothesis:** h-c1 (CONDITION)  
**Author:** Logic Agent  
**Budget:** 8 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** API signatures verified from h-m1 code  
**Analyzed Path:** docs/youra_research/h-m1/code/  
**Relevant Symbols:** LayerNeuronAnalyzer, get_dataloader, get_spurious_labels

**Findings:** h-m1 uses flat module structure with direct imports. No existing optimizer wrappers or worst-group metrics. h-c1 must implement custom GradientAwareOptimizer and evaluation utilities.

---

## Applied Patterns

**Applied:** PyTorch optimizer wrapper pattern  
**Applied:** Hook-based activation extraction (reused from h-m1)

---

## External Dependencies API (h-m1)

h-c1 reuses ρ_j computation logic from h-m1 for parameter-level learning rate modulation.

### From h-m1/code/layer_analyzer.py

```python
class LayerNeuronAnalyzer:
    def __init__(self, model: torch.nn.Module, layer_names: List[str]):
        """Initialize analyzer with forward hooks."""
        ...
    
    def compute_layer_correlations(
        self,
        dataloader: torch.utils.data.DataLoader,
        spurious_labels: np.ndarray,
        device: str = 'cuda'
    ) -> Dict[str, np.ndarray]:
        """Compute per-neuron Pearson ρ_j. Returns {layer: [C,]} dict."""
        ...
```

**Verified from:** h-m1/code/layer_analyzer.py (actual implementation)

---

## Epic 1: Waterbirds Dataset Setup [Complexity: 7]

### API Signatures

```python
class WaterbirdDataset(Dataset):
    def __init__(self, root: str, split: str, transform: Optional[Callable] = None):
        """Load Waterbirds with group labels. split: train|val|test."""
        ...
    
    def __getitem__(self, idx: int) -> Tuple[Tensor, int, int]:
        """Returns (img, label, group). img: [3,224,224], label: {0,1}, group: {0,1,2,3}."""
        ...
    
    def __len__(self) -> int:
        ...

def get_waterbirds_loader(root: str, split: str, batch_size: int, num_workers: int = 4) -> DataLoader:
    """Create DataLoader with ImageNet transforms. Returns DataLoader."""
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    ...
```

### Subtasks [1/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Dataset loader | Implement WaterbirdDataset.__getitem__ with group labels |

---

## Epic 2: ResNet-50 Baseline Model [Complexity: 5]

### API Signatures

```python
def get_resnet50(num_classes: int = 2, pretrained: bool = True) -> torch.nn.Module:
    """
    Load ResNet-50 with modified final layer.
    Returns: ResNet-50 model
    """
    model = models.resnet50(pretrained=pretrained)
    model.fc = torch.nn.Linear(model.fc.in_features, num_classes)
    return model
```

### Subtasks [0/8 used]

Skip - trivial wrapper.

---

## Epic 3: ρ_j Loading from h-m1 [Complexity: 9]

### API Signatures

```python
def load_rho_j_from_h_m1(
    h_m1_checkpoint_path: str,
    waterbirds_loader: DataLoader,
    device: str = 'cuda'
) -> Dict[str, np.ndarray]:
    """
    Load h-m1 model, compute ρ_j on Waterbirds train set.
    
    Args:
        h_m1_checkpoint_path: Path to h-m1/checkpoints/baseline_model.pt
        waterbirds_loader: Waterbirds train loader
        device: cuda or cpu
    
    Returns:
        layer_rho_j: {layer_name: [C,]} dict
    
    Algorithm:
        1. Load ResNet-18 from h-m1 checkpoint
        2. Extract spurious labels (background) from Waterbirds
        3. Use LayerNeuronAnalyzer.compute_layer_correlations()
    """
    from layer_analyzer import LayerNeuronAnalyzer
    ...

def map_rho_j_to_resnet50(
    rho_j_resnet18: Dict[str, np.ndarray],
    resnet50_model: torch.nn.Module
) -> Dict[str, float]:
    """
    Map ResNet-18 layer ρ_j to ResNet-50 parameter groups.
    
    Args:
        rho_j_resnet18: {layer1: [64,], layer2: [128,], ...}
        resnet50_model: Target ResNet-50 model
    
    Returns:
        param_rho: {param_name: float} - mean ρ_j per layer
    
    Algorithm:
        1. Group ResNet-50 params by layer (layer1, layer2, layer3, layer4)
        2. Assign mean(rho_j_resnet18[layer]) to each param in layer
        3. Default ρ=0.0 for fc layer (task-specific)
    """
    param_rho = {}
    for name, param in resnet50_model.named_parameters():
        if 'layer1' in name:
            param_rho[name] = np.mean(rho_j_resnet18.get('layer1', [0.0]))
        elif 'layer2' in name:
            param_rho[name] = np.mean(rho_j_resnet18.get('layer2', [0.0]))
        # ... layer3, layer4
        else:
            param_rho[name] = 0.0  # fc, conv1
    return param_rho
```

### Subtasks [1/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | ρ_j mapping | Implement map_rho_j_to_resnet50() layer grouping logic |

---

## Epic 4: GradientAwareOptimizer [Complexity: 11]

### API Signatures

```python
class GradientAwareOptimizer:
    """Wrapper applying lr_j = base_lr * (1 - ρ_j) per parameter."""
    
    def __init__(
        self,
        params: Iterable,
        base_optimizer_class: Type[torch.optim.Optimizer],
        rho_j_dict: Dict[str, float],
        base_lr: float = 1e-3,
        lr_floor: float = 1e-5,
        **optimizer_kwargs
    ):
        """
        Args:
            params: Model parameters (model.named_parameters())
            base_optimizer_class: SGD or Adam
            rho_j_dict: {param_name: rho_value}
            base_lr: Base learning rate
            lr_floor: Minimum lr (stability)
            optimizer_kwargs: momentum, weight_decay, etc.
        
        Creates param_groups with modulated lr per parameter.
        """
        self.rho_j_dict = rho_j_dict
        self.base_lr = base_lr
        self.lr_floor = lr_floor
        
        # Create per-parameter groups
        param_groups = []
        for name, param in params:
            rho = rho_j_dict.get(name, 0.0)
            modulated_lr = max(base_lr * (1 - rho), lr_floor)
            param_groups.append({
                'params': [param],
                'lr': modulated_lr,
                'name': name
            })
        
        self.optimizer = base_optimizer_class(param_groups, **optimizer_kwargs)
    
    def step(self, closure=None):
        """Forward to base optimizer."""
        return self.optimizer.step(closure)
    
    def zero_grad(self):
        """Forward to base optimizer."""
        self.optimizer.zero_grad()
    
    def state_dict(self) -> dict:
        """Save optimizer state + rho_j_dict."""
        return {
            'optimizer_state': self.optimizer.state_dict(),
            'rho_j_dict': self.rho_j_dict,
            'base_lr': self.base_lr
        }
    
    def load_state_dict(self, state_dict: dict):
        """Load optimizer state."""
        self.optimizer.load_state_dict(state_dict['optimizer_state'])
        self.rho_j_dict = state_dict['rho_j_dict']
        self.base_lr = state_dict['base_lr']
```

### Subtasks [2/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Param groups | Implement per-parameter lr assignment in __init__ |
| L-4-2 | State dict | Implement state_dict/load_state_dict with rho_j persistence |

---

## Epic 5: JTT Baseline Implementation [Complexity: 12]

### API Signatures

```python
class JTTTrainer:
    """Two-stage JTT training."""
    
    def __init__(
        self,
        model: torch.nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        device: str = 'cuda',
        stage1_epochs: int = 100,
        stage2_epochs: int = 200,
        upweight_factor: float = 10.0,
        lr: float = 1e-3
    ):
        """Initialize JTT trainer."""
        ...
    
    def train_stage1(self) -> torch.nn.Module:
        """
        Stage 1: ERM training.
        Returns: Trained model (stage1)
        """
        ...
    
    def identify_misclassified(self, model: torch.nn.Module) -> np.ndarray:
        """
        Identify misclassified samples on train set.
        Returns: misclassified_mask [N,] boolean array
        """
        ...
    
    def train_stage2(self, misclassified_mask: np.ndarray) -> torch.nn.Module:
        """
        Stage 2: Reweight misclassified samples by upweight_factor.
        Returns: Final model
        """
        ...
    
    def run(self) -> torch.nn.Module:
        """Run full JTT pipeline. Returns final model."""
        model_s1 = self.train_stage1()
        misclassified = self.identify_misclassified(model_s1)
        model_final = self.train_stage2(misclassified)
        return model_final
```

### Subtasks [1/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Sample reweighting | Implement weighted CrossEntropyLoss in train_stage2 |

---

## Epic 6: Training Pipeline [Complexity: 10]

### API Signatures

```python
class Trainer:
    """Unified training loop for ERM, JTT, Gradient-Aware."""
    
    def __init__(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        train_loader: DataLoader,
        val_loader: DataLoader,
        device: str = 'cuda',
        checkpoint_dir: str = './checkpoints'
    ):
        """Initialize trainer."""
        self.model = model.to(device)
        self.optimizer = optimizer
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.device = device
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
    
    def train_epoch(self) -> float:
        """
        Train one epoch.
        Returns: average loss
        """
        self.model.train()
        total_loss = 0
        for x, y, _ in self.train_loader:  # (img, label, group)
            x, y = x.to(self.device), y.to(self.device)
            self.optimizer.zero_grad()
            logits = self.model(x)  # [B, 2]
            loss = F.cross_entropy(logits, y)
            loss.backward()
            self.optimizer.step()
            total_loss += loss.item()
        return total_loss / len(self.train_loader)
    
    def validate(self) -> Dict[str, float]:
        """
        Validate on val set.
        Returns: {avg_acc, worst_group_acc, per_group_acc}
        """
        from evaluator import evaluate_model
        return evaluate_model(self.model, self.val_loader, self.device)
    
    def run(self, epochs: int) -> Dict[str, List[float]]:
        """
        Run training for N epochs.
        Returns: {train_loss: [...], val_wg_acc: [...]}
        """
        history = {'train_loss': [], 'val_wg_acc': []}
        best_wg_acc = 0.0
        
        for epoch in range(epochs):
            loss = self.train_epoch()
            metrics = self.validate()
            
            history['train_loss'].append(loss)
            history['val_wg_acc'].append(metrics['worst_group_acc'])
            
            # Checkpoint best model
            if metrics['worst_group_acc'] > best_wg_acc:
                best_wg_acc = metrics['worst_group_acc']
                torch.save(self.model.state_dict(), 
                          self.checkpoint_dir / 'best_model.pt')
            
            print(f"Epoch {epoch+1}/{epochs}: "
                  f"Loss={loss:.4f}, WG-Acc={metrics['worst_group_acc']:.2f}%")
        
        return history
```

### Subtasks [1/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Checkpoint logic | Implement best model saving based on worst-group accuracy |

---

## Epic 7: Statistical Validation (Test 9) [Complexity: 8]

### API Signatures

```python
def run_statistical_test(
    gradient_aware_results: np.ndarray,
    jtt_results: np.ndarray,
    alpha: float = 0.05,
    margin: float = 0.01
) -> Dict[str, float]:
    """
    Paired t-test for non-inferiority.
    
    Args:
        gradient_aware_results: [10,] worst-group accuracy (10 seeds)
        jtt_results: [10,] worst-group accuracy (10 seeds)
        alpha: Significance level
        margin: Non-inferiority margin (1%)
    
    Returns:
        {t_stat, p_value, cohens_d, mean_diff, pass}
    
    Test:
        H0: mean(GA) < mean(JTT) - margin
        Ha: mean(GA) >= mean(JTT) - margin
    """
    from scipy.stats import ttest_rel
    
    diff = gradient_aware_results - jtt_results
    t_stat, p_value = ttest_rel(diff + margin, [0]*len(diff), alternative='greater')
    
    mean_diff = np.mean(gradient_aware_results) - np.mean(jtt_results)
    pooled_std = np.std(np.concatenate([gradient_aware_results, jtt_results]))
    cohens_d = mean_diff / pooled_std
    
    gate_pass = (p_value < alpha) and (mean_diff >= -margin)
    
    return {
        't_stat': t_stat,
        'p_value': p_value,
        'cohens_d': cohens_d,
        'mean_diff': mean_diff,
        'pass': gate_pass
    }
```

### Subtasks [1/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | T-test logic | Implement paired t-test with non-inferiority hypothesis |

---

## Epic 8: Visualization and Reporting [Complexity: 9]

### API Signatures

```python
def plot_gate_metrics(
    results: Dict[str, np.ndarray],
    target: float,
    save_path: str
) -> None:
    """
    Bar chart: Target vs actual worst-group accuracy.
    
    Args:
        results: {method_name: [10,] seed results}
        target: Target accuracy (86%)
        save_path: Output path
    
    Figure: 3 bars (ERM, JTT, Gradient-Aware) with error bars (std).
    """
    ...

def plot_lr_modulation_heatmap(
    rho_j_dict: Dict[str, float],
    base_lr: float,
    save_path: str
) -> None:
    """
    Heatmap of per-parameter learning rates.
    
    Args:
        rho_j_dict: {param_name: rho}
        base_lr: Base learning rate
        save_path: Output path
    
    Figure: Rows=layers, color=lr_j
    """
    ...

def plot_training_curves(
    histories: Dict[str, Dict[str, List[float]]],
    save_path: str
) -> None:
    """
    Training curves for 3 methods.
    
    Args:
        histories: {method: {train_loss: [...], val_wg_acc: [...]}}
        save_path: Output path
    
    Figure: 3 lines (ERM, JTT, GA) showing WG-Acc over epochs.
    """
    ...

def plot_per_group_accuracy(
    results: Dict[str, np.ndarray],
    save_path: str
) -> None:
    """
    Per-group accuracy bars (4 groups × 3 methods).
    
    Args:
        results: {method: [4,] per-group accuracy}
        save_path: Output path
    
    Figure: Grouped bar chart.
    """
    ...
```

### Subtasks [1/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | Plot functions | Implement 4 plot functions with matplotlib |

---

## Evaluation Utilities (Epic 6 Support)

### API Signatures

```python
def worst_group_accuracy(
    preds: Tensor,
    labels: Tensor,
    groups: Tensor
) -> float:
    """
    Compute min accuracy over 4 groups.
    
    Args:
        preds: [N,] predicted labels
        labels: [N,] true labels
        groups: [N,] group indices {0,1,2,3}
    
    Returns:
        worst_acc: float (0-100%)
    """
    group_accs = []
    for g in range(4):
        mask = (groups == g)
        if mask.sum() > 0:
            acc = (preds[mask] == labels[mask]).float().mean() * 100
            group_accs.append(acc)
    return min(group_accs)

def per_group_accuracy(
    preds: Tensor,
    labels: Tensor,
    groups: Tensor
) -> np.ndarray:
    """Returns [4,] array of per-group accuracy."""
    group_accs = []
    for g in range(4):
        mask = (groups == g)
        acc = (preds[mask] == labels[mask]).float().mean().item() * 100
        group_accs.append(acc)
    return np.array(group_accs)

def evaluate_model(
    model: torch.nn.Module,
    dataloader: DataLoader,
    device: str
) -> Dict[str, float]:
    """
    Full evaluation on dataloader.
    
    Returns:
        {avg_acc, worst_group_acc, per_group_acc: [4,]}
    """
    model.eval()
    all_preds, all_labels, all_groups = [], [], []
    
    with torch.no_grad():
        for x, y, g in dataloader:
            x = x.to(device)
            logits = model(x)
            preds = logits.argmax(dim=1).cpu()
            all_preds.append(preds)
            all_labels.append(y)
            all_groups.append(g)
    
    preds = torch.cat(all_preds)
    labels = torch.cat(all_labels)
    groups = torch.cat(all_groups)
    
    avg_acc = (preds == labels).float().mean().item() * 100
    wg_acc = worst_group_accuracy(preds, labels, groups)
    pg_acc = per_group_accuracy(preds, labels, groups)
    
    return {
        'avg_acc': avg_acc,
        'worst_group_acc': wg_acc,
        'per_group_acc': pg_acc
    }
```

---

## Subtask Summary

| Epic | Subtasks Used | Details |
|------|---------------|---------|
| Epic 1 | 1 | Dataset loader |
| Epic 2 | 0 | Trivial wrapper |
| Epic 3 | 1 | ρ_j mapping |
| Epic 4 | 2 | Param groups, state dict |
| Epic 5 | 1 | Sample reweighting |
| Epic 6 | 1 | Checkpoint logic |
| Epic 7 | 1 | T-test logic |
| Epic 8 | 1 | Plot functions |
| **Total** | **8/8** | ✅ Within budget |

---

**Version:** 1.0  
**Status:** Ready for Configuration Design
