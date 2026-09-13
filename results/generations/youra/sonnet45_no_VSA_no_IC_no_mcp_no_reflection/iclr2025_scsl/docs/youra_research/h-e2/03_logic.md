# Logic Design: h-e2 Gradient Variance & Forgetting Analysis

**Hypothesis:** h-e2  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-08-28  
**Author:** yoon303@ust.ac.kr  

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: API signatures verified from h-e1 actual code  
**Analyzed Path**: /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet45/TEST_scsl/docs/youra_research/h-e1/code/  
**Relevant Symbols**: AblationTrainer, get_baseline_model, get_dataloader, apply_spurious_mask, apply_core_mask  

---

## Knowledge Base Patterns Applied

**Applied**: PyTorch hook pattern for gradient tracking  
**Applied**: Rolling window variance calculation  
**Applied**: Per-sample prediction tracking pattern  

---

## External Dependencies (Base Hypothesis)

### API Signatures (From h-e1 Actual Code)

```python
# From: h-e1/code/model_v2.py (ACTUAL IMPLEMENTATION)
def get_baseline_model(dataset_name: str, pretrained: bool = True) -> nn.Module:
    """ResNet-18 for CMNIST, ResNet-50 for others. Binary classifier."""
    ...

class AblationTrainer:
    def __init__(
        self,
        model: nn.Module,
        dataset_name: str,
        lr: float,
        weight_decay: float,
        device: str = 'cuda',
        target_accuracy: float = 0.90
    ):
        """Trainer with accuracy-based convergence."""
        ...
    
    def train_variant(
        self,
        variant: Literal['spurious', 'core', 'baseline'],
        dataloader,
        max_epochs: int
    ) -> int | None:
        """Train until target_accuracy. Returns convergence epoch or None."""
        ...
    
    def compute_accuracy(self, dataloader, variant: str) -> float:
        """Compute accuracy with variant-specific masking."""
        ...

# From: h-e1/code/data.py (ACTUAL IMPLEMENTATION)
def get_dataloader(config: DatasetConfig, split: Literal['train', 'val', 'test']) -> DataLoader:
    """Load CMNIST with color bias."""
    ...

def apply_spurious_mask(images: torch.Tensor, dataset_name: str) -> torch.Tensor:
    """CMNIST: gaussian_blur(images, kernel_size=15)"""
    ...

def apply_core_mask(images: torch.Tensor, dataset_name: str) -> torch.Tensor:
    """CMNIST: rgb_to_grayscale(images, num_output_channels=3)"""
    ...
```

**Verified from**: h-e1/code/model_v2.py, h-e1/code/data.py

---

## B-1: Gradient Variance Tracker [Complexity: 8, Budget: 2]

**Applied**: Rolling window standard deviation

### API Signatures

```python
class GradientVarianceTracker:
    """Track gradient norms with rolling window variance."""
    
    def __init__(self, window_size: int = 3):
        self.window_size = window_size
        self.grad_history = []  # list of float (epoch grad norms)
    
    def log_gradient_norm(self, model: nn.Module) -> float:
        """Compute L2 norm of all gradients. Returns scalar."""
        total = sum(p.grad.norm(2).item() ** 2 for p in model.parameters() if p.grad is not None)
        norm = total ** 0.5
        self.grad_history.append(norm)
        return norm
    
    def compute_variance(self) -> float:
        """Rolling variance over last window_size epochs."""
        if len(self.grad_history) < self.window_size:
            return 0.0
        window = self.grad_history[-self.window_size:]
        return np.var(window)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Gradient norm computation | L2 norm of all model parameters |
| L-1-2 | Rolling variance | np.var over last window_size epochs |

---

## B-2: Forgetting Event Tracker [Complexity: 9, Budget: 2]

**Applied**: Per-sample prediction logging with flip detection

### API Signatures

```python
class ForgettingTracker:
    """Track per-sample predictions across epochs."""
    
    def __init__(self, num_samples: int):
        self.num_samples = num_samples
        self.predictions = {}  # {epoch: [N] tensor}
        self.labels = None  # [N] ground truth
    
    def log_predictions(self, epoch: int, preds: torch.Tensor, labels: torch.Tensor):
        """Store predictions. preds: [N], labels: [N]"""
        self.predictions[epoch] = preds.cpu()
        if self.labels is None:
            self.labels = labels.cpu()
    
    def compute_forgetting_events(self) -> float:
        """Count correct->incorrect flips. Returns: mean events per sample."""
        forgetting_count = torch.zeros(self.num_samples)
        epochs = sorted(self.predictions.keys())
        
        for i in range(len(epochs) - 1):
            curr_correct = (self.predictions[epochs[i]] == self.labels)
            next_correct = (self.predictions[epochs[i+1]] == self.labels)
            forgetting_count += (curr_correct & ~next_correct).float()
        
        return forgetting_count.mean().item()
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Prediction storage | Dict of epoch -> [N] predictions |
| L-2-2 | Flip detection | Count correct->incorrect transitions |

---

## B-3: Extended Training with Tracking [Complexity: 11, Budget: 3]

**Applied**: PyTorch backward hook for gradient capture

### API Signatures

```python
def run_single_experiment_with_tracking(config: TrainConfig) -> dict:
    """
    Extend h-e1 training with variance + forgetting tracking.
    
    Returns:
        {
            'dataset': str,
            'seed': int,
            'E_spurious': int | None,
            'E_core': int | None,
            'variance_spurious': list[float],  # per checkpoint
            'variance_core': list[float],
            'forgetting_spurious': float,
            'forgetting_core': float,
            'variance_ratio': float  # mean(V_s) / mean(V_c)
        }
    """
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    dataloader = get_dataloader(DatasetConfig(config.dataset, config.batch_size), 'train')
    
    # Train spurious variant with tracking
    model_s = get_baseline_model(config.dataset, pretrained=False)
    trainer_s = AblationTrainer(model_s, config.dataset, config.lr, config.weight_decay, device)
    grad_tracker_s = GradientVarianceTracker(window_size=3)
    forget_tracker_s = ForgettingTracker(num_samples=len(dataloader.dataset))
    
    E_spurious = train_with_tracking(
        trainer_s, 'spurious', dataloader, config.max_epochs,
        grad_tracker_s, forget_tracker_s
    )
    
    # Train core variant with tracking
    model_c = get_baseline_model(config.dataset, pretrained=False)
    trainer_c = AblationTrainer(model_c, config.dataset, config.lr, config.weight_decay, device)
    grad_tracker_c = GradientVarianceTracker(window_size=3)
    forget_tracker_c = ForgettingTracker(num_samples=len(dataloader.dataset))
    
    E_core = train_with_tracking(
        trainer_c, 'core', dataloader, config.max_epochs,
        grad_tracker_c, forget_tracker_c
    )
    
    # Compute metrics
    var_s = [grad_tracker_s.compute_variance() for _ in CHECKPOINT_EPOCHS]
    var_c = [grad_tracker_c.compute_variance() for _ in CHECKPOINT_EPOCHS]
    
    return {
        'dataset': config.dataset,
        'seed': config.seed,
        'E_spurious': E_spurious,
        'E_core': E_core,
        'variance_spurious': var_s,
        'variance_core': var_c,
        'forgetting_spurious': forget_tracker_s.compute_forgetting_events(),
        'forgetting_core': forget_tracker_c.compute_forgetting_events(),
        'variance_ratio': np.mean(var_s) / np.mean(var_c) if np.mean(var_c) > 0 else float('inf')
    }


def train_with_tracking(
    trainer: AblationTrainer,
    variant: str,
    dataloader: DataLoader,
    max_epochs: int,
    grad_tracker: GradientVarianceTracker,
    forget_tracker: ForgettingTracker
) -> int | None:
    """
    Train variant with gradient and prediction tracking.
    Returns convergence epoch or None.
    """
    for epoch in range(1, max_epochs + 1):
        # Standard training epoch (reuse trainer.train_epoch)
        avg_loss = trainer.train_epoch(dataloader, variant)
        
        # Log gradient norm (after backward pass)
        grad_norm = grad_tracker.log_gradient_norm(trainer.model)
        
        # Log predictions for forgetting tracking
        preds, labels = get_predictions(trainer.model, dataloader, variant, trainer.device)
        forget_tracker.log_predictions(epoch, preds, labels)
        
        # Check convergence (reuse trainer logic)
        accuracy = trainer.compute_accuracy(dataloader, variant)
        if accuracy >= trainer.target_accuracy:
            return epoch
    
    return None


def get_predictions(model: nn.Module, dataloader: DataLoader, variant: str, device: str) -> tuple[torch.Tensor, torch.Tensor]:
    """Get all predictions and labels. Returns: ([N], [N])"""
    import torchvision.transforms.functional as TF
    
    model.eval()
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for images, labels in dataloader:
            images = images.to(device)
            
            if variant == 'spurious':
                images = TF.gaussian_blur(images, kernel_size=15)
            elif variant == 'core':
                images = TF.rgb_to_grayscale(images, num_output_channels=3)
            
            outputs = model(images)
            _, preds = torch.max(outputs, 1)
            all_preds.append(preds.cpu())
            all_labels.append(labels)
    
    return torch.cat(all_preds), torch.cat(all_labels)
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| images | [B, 3, 224, 224] | CMNIST batch |
| labels | [B] | Binary labels |
| preds | [N] | All predictions (N = dataset size) |
| grad_norm | scalar | L2 norm of gradients |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Gradient hook integration | Call grad_tracker.log_gradient_norm after backward |
| L-3-2 | Prediction collection | get_predictions helper with variant masking |
| L-3-3 | Metric aggregation | Variance ratio and forgetting rate computation |

---

## B-4: Statistical Tests [Complexity: 7, Budget: 2]

**Applied**: scipy.stats F-test and t-test

### API Signatures

```python
def variance_ratio_test(var_spurious: list[float], var_core: list[float]) -> dict:
    """
    F-test for variance ratio (H0: V_s/V_c = 1).
    
    Returns: {'f_stat': float, 'p_value': float, 'ratio': float}
    """
    from scipy import stats
    
    f_stat = np.var(var_spurious) / np.var(var_core) if np.var(var_core) > 0 else float('inf')
    p_value = stats.f.sf(f_stat, len(var_spurious)-1, len(var_core)-1)
    
    return {
        'f_stat': f_stat,
        'p_value': p_value,
        'ratio': np.mean(var_spurious) / np.mean(var_core)
    }


def forgetting_paired_test(forgetting_s: list[float], forgetting_c: list[float]) -> dict:
    """
    Paired t-test for forgetting rates (H0: F_s = F_c).
    
    Returns: {'t_stat': float, 'p_value': float, 'mean_diff': float}
    """
    from scipy import stats
    
    t_stat, p_value = stats.ttest_rel(forgetting_s, forgetting_c)
    
    return {
        't_stat': t_stat,
        'p_value': p_value,
        'mean_diff': np.mean(forgetting_s) - np.mean(forgetting_c)
    }
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | F-test wrapper | scipy.stats.f.sf for variance ratio |
| L-4-2 | Paired t-test wrapper | scipy.stats.ttest_rel for forgetting |

---

## B-5: PoC Gate Check [Complexity: 5, Budget: 1]

**Applied**: Simple threshold comparison

### API Signatures

```python
def check_poc_pass(results: dict, variance_threshold: float = 0.7) -> bool:
    """
    PoC gate: V_s/V_c < 0.7 AND F_s < F_c (directional only, no stats).
    
    results: output from run_single_experiment_with_tracking
    Returns: True if both conditions met
    """
    variance_ok = results['variance_ratio'] < variance_threshold
    forgetting_ok = results['forgetting_spurious'] < results['forgetting_core']
    
    return variance_ok and forgetting_ok
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Threshold check | Two boolean comparisons |

---

## B-6: Visualization [Complexity: 8, Budget: 2]

**Applied**: matplotlib bar and line plots

### API Signatures

```python
def plot_gate_metrics(results: dict, output_path: str):
    """
    Bar chart: variance_ratio, forgetting rates (spurious vs core).
    Saves to output_path.
    """
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    
    # Variance ratio
    axes[0].bar(['Variance Ratio'], [results['variance_ratio']])
    axes[0].axhline(0.7, color='red', linestyle='--', label='Threshold')
    axes[0].set_ylabel('V_spurious / V_core')
    axes[0].legend()
    
    # Forgetting rates
    axes[1].bar(['Spurious', 'Core'], 
                [results['forgetting_spurious'], results['forgetting_core']])
    axes[1].set_ylabel('Forgetting Events')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_rolling_variance(results: dict, output_path: str):
    """
    Line plot: V_spurious(t), V_core(t) over epochs.
    x-axis: checkpoint epochs, y-axis: variance.
    """
    import matplotlib.pyplot as plt
    
    epochs = [10, 20, 30]  # CHECKPOINT_EPOCHS from config
    
    plt.figure(figsize=(8, 4))
    plt.plot(epochs, results['variance_spurious'], marker='o', label='Spurious')
    plt.plot(epochs, results['variance_core'], marker='s', label='Core')
    plt.xlabel('Epoch')
    plt.ylabel('Gradient Variance')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Gate metrics bar chart | 2-panel subplot (variance ratio + forgetting) |
| L-6-2 | Variance time series | Line plot with markers |

---

## Configuration Constants

```python
# h-e2/code/config.py
WINDOW_SIZE = 3  # epochs for rolling variance
CHECKPOINT_EPOCHS = [10, 20, 30]  # when to compute variance
VARIANCE_THRESHOLD = 0.7  # V_s/V_c gate
P_VALUE_THRESHOLD = 0.05
NUM_SEEDS = 1  # PoC only
```

---

## Validation

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in code comments
- [x] Subtask count within budget (3+2+2+2+1+2 = 12/15 used)
- [x] Total length < 600 lines
- [x] Codebase Analysis section included
- [x] External Dependencies API verified from h-e1 actual code
- [x] EXISTENCE PoC: minimal tracking only

---

**Output for Phase 4 Coder:**
- File: /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet45/TEST_scsl/docs/youra_research/h-e2/03_logic.md
- Allocated: Tasks B-1 through B-6 (6 tasks)
- Budget: 15 subtasks, 12 used
- API signatures verified from h-e1/code/model_v2.py and h-e1/code/data.py
