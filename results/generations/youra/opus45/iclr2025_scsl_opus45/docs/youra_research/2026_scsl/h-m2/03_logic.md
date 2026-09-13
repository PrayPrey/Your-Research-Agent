# Logic: H-M2 (Spurious-Specificity Mechanism Test)

Applied: Standard PyTorch GroupDRO exponentiated gradient pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual h-e1 code via direct file read (Serena project activation unavailable for this path)
**Analyzed Path**: `docs/youra_research/20260414_scsl/h-e1/code/`
**Relevant Symbols**:
- `LossTrajectoryTracker.__init__(num_samples, num_epochs=5)`
- `LossTrajectoryTracker.log_epoch_losses(sample_indices, losses, epoch_idx)`
- `LossTrajectoryTracker.get_loss_matrix() -> np.ndarray`
- `run_epoch_eval_pass(model, eval_loader, device, tracker, epoch_idx) -> None`
- `extract_trajectory_features(loss_matrix: np.ndarray) -> np.ndarray`
- `compute_auroc_cv(features, minority_labels, n_splits=5, seed=42) -> Tuple[float, float]`
- `WaterbirdsDataset.__getitem__` returns `(image, label, group_id, idx)`

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

```python
# From: h-e1/code/train.py (ACTUAL CODE)
class LossTrajectoryTracker:
    def __init__(self, num_samples: int, num_epochs: int = 5): ...
    def log_epoch_losses(
        self,
        sample_indices: np.ndarray,  # shape (B,)
        losses: np.ndarray,          # shape (B,)
        epoch_idx: int,              # 0-based
    ) -> None: ...
    def get_loss_matrix(self) -> np.ndarray: ...  # (num_samples, num_epochs)

def run_epoch_eval_pass(
    model: ResNet50Classifier,
    eval_loader: DataLoader,
    device: torch.device,
    tracker: LossTrajectoryTracker,
    epoch_idx: int,              # 0-based
) -> None: ...

# From: h-e1/code/evaluate.py (ACTUAL CODE)
def extract_trajectory_features(loss_matrix: np.ndarray) -> np.ndarray:
    # loss_matrix: (N, 5) -> features: (N, 4)

def compute_auroc_cv(
    features: np.ndarray,        # (N, 4)
    minority_labels: np.ndarray, # (N,)
    n_splits: int = 5,
    seed: int = 42,
) -> Tuple[float, float]: ...   # (mean_auroc, std_auroc)

# From: h-e1/code/data.py (ACTUAL CODE)
def get_minority_labels(dataset: WaterbirdsDataset) -> np.ndarray: ...  # (N,) binary
def get_eval_dataloader(config: Config) -> DataLoader: ...
```

**Verified from**: `h-e1/code/` (actual implementation)

---

## A-3: GroupDRO Trainer [Complexity: 14, Budget: 4 subtasks]

Applied: Standard PyTorch GroupDRO exponentiated gradient pattern

### API Signatures

```python
def train_groupdro(
    config: Config,
    model: ResNet50Classifier,
    train_loader: DataLoader,
    eval_loader: DataLoader,
    device: torch.device,
    group_counts: np.ndarray,    # (4,) count per group
) -> Tuple[ResNet50Classifier, LossTrajectoryTracker, np.ndarray]:
    """GroupDRO training with exponentiated gradient weight updates.
    Returns: (model, tracker, group_weights_history)
    group_weights_history: (epochs, 4)
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| group_counts | (4,) | count per group for weight init |
| group_weights | (4,) | current group weights, sums to 1 |
| per_sample_loss | (B,) | cross-entropy per sample |
| group_losses | (4,) | mean loss per group in batch |
| group_weights_history | (epochs, 4) | saved after each epoch |

### Pseudo-code

```
# Init
group_weights = torch.ones(4) / 4  # uniform init
optimizer = SGD(lr=0.001, momentum=0.9, weight_decay=config.weight_decay_gdro)
group_weights_history = []

for epoch in 1..epochs:
    model.train()
    for images, labels, group_ids, sample_idx in train_loader:
        logits = model(images)
        per_sample_loss = F.cross_entropy(logits, labels, reduction='none')  # (B,)

        # Compute per-group mean loss
        group_losses = zeros(4)
        for g in 0..3:
            mask = (group_ids == g)
            if mask.any():
                group_losses[g] = per_sample_loss[mask].mean()

        # Exponentiated gradient update (detach for weight update)
        with torch.no_grad():
            group_weights = group_weights * torch.exp(config.groupdro_gamma * group_losses.detach())
            group_weights = group_weights / group_weights.sum()

        # Weighted loss for model update
        loss = (group_losses * group_weights.detach()).sum()
        optimizer.zero_grad(); loss.backward(); optimizer.step()

    group_weights_history.append(group_weights.cpu().numpy().copy())

    if epoch <= config.trajectory_epochs:
        run_epoch_eval_pass(model, eval_loader, device, tracker, epoch - 1)

return model, tracker, np.stack(group_weights_history)  # (epochs, 4)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | GroupDRO init | Initialize group_weights (uniform), optimizer with weight_decay_gdro, tracker |
| L-3-2 | Group loss computation | Per-batch group_ids mask → per-group mean loss (4,), handle empty groups |
| L-3-3 | Exponentiated gradient update | group_weights * exp(gamma * group_losses), normalize, detach for model loss |
| L-3-4 | Weight history logging | Append to list per epoch, stack to (epochs, 4) array on return |

---

## A-4: Random Reweighting [Complexity: 13, Budget: 2 subtasks]

Applied: Standard PyTorch sample reweighting pattern

### API Signatures

```python
def compute_variance_matched_weights(
    group_counts: np.ndarray,   # (4,) count per group
    num_samples: int,            # total training samples (4795)
    groupdro_gamma: float,       # 0.1
    seed: int,                   # for reproducibility
) -> np.ndarray:
    """Sample per-sample weights matching GroupDRO gradient variance.
    Returns: weights shape (num_samples,), normalized to sum=1.
    """
    ...

def train_random_reweight(
    config: Config,
    model: ResNet50Classifier,
    train_loader: DataLoader,
    eval_loader: DataLoader,
    device: torch.device,
    random_weights: np.ndarray,  # (num_samples,) pre-computed
) -> Tuple[ResNet50Classifier, LossTrajectoryTracker]:
    """Random reweighting training with pre-computed variance-matched weights."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| random_weights (input) | (N,) | pre-computed, sum=1 |
| weights (batch) | (B,) | indexed by sample_idx |
| per_sample_loss | (B,) | cross-entropy per sample |
| loss (scalar) | () | (per_sample_loss * weights).sum() / weights.sum() |

### Pseudo-code

```
# compute_variance_matched_weights:
rng = np.random.default_rng(seed)
# Target variance: compute GroupDRO effective weight std across samples
# Group weight at convergence approx proportional to exp(gamma / group_count)
group_effective_weights = np.exp(groupdro_gamma / group_counts)
group_effective_weights /= group_effective_weights.sum()
# Assign each sample its group's effective weight + noise to match variance
per_sample_group_weight = group_effective_weights[sample_group_ids]
target_var = np.var(per_sample_group_weight)
# Draw random weights from log-normal, scale to match variance
raw_weights = rng.lognormal(mean=0.0, sigma=np.sqrt(target_var), size=num_samples)
weights = raw_weights / raw_weights.sum()
return weights

# train_random_reweight:
optimizer = SGD(lr=0.001, momentum=0.9, weight_decay=config.weight_decay_erm)
random_weights_tensor = torch.from_numpy(random_weights).float().to(device)

for epoch in 1..epochs:
    model.train()
    for images, labels, _, sample_idx in train_loader:
        logits = model(images)
        per_sample_loss = F.cross_entropy(logits, labels, reduction='none')  # (B,)
        weights = random_weights_tensor[sample_idx]  # (B,)
        loss = (per_sample_loss * weights).sum() / weights.sum()
        optimizer.zero_grad(); loss.backward(); optimizer.step()

    if epoch <= config.trajectory_epochs:
        run_epoch_eval_pass(model, eval_loader, device, tracker, epoch - 1)

return model, tracker
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Variance matching | compute_variance_matched_weights: derive target variance from GroupDRO group weights, sample log-normal weights |
| L-4-2 | Weighted training loop | train_random_reweight: index random_weights by sample_idx, weighted loss = (loss * w).sum() / w.sum() |

---

## A-5: Multi-Regime Evaluator [Complexity: 11, Budget: 2 subtasks]

Applied: Standard sklearn AUROC evaluation pattern

### API Signatures

```python
def evaluate_all_regimes(
    regime_features: Dict[str, np.ndarray],  # {'erm': (N,4), 'groupdro': (N,4), 'random': (N,4)}
    minority_labels: np.ndarray,              # (N,)
    config: Config,
) -> Dict[str, Tuple[float, float]]:
    """Compute AUROC CV for each regime. Returns {'erm': (mean, std), ...}"""
    ...

def compute_delta_auroc(
    auroc_erm: float,
    auroc_gdro: float,
    auroc_random: float,
) -> Tuple[float, float]:
    """Returns (delta_gdro, delta_random).
    delta_gdro = auroc_erm - auroc_gdro
    delta_random = auroc_erm - auroc_random
    """
    ...

def evaluate_gate(
    delta_gdro: float,
    delta_random: float,
    config: Config,
) -> Tuple[bool, str]:
    """Gate: delta_gdro > config.delta_gdro_threshold AND delta_random < config.delta_random_threshold.
    Returns: (passed, result_str)
    """
    ...

def verify_mechanism_activation(
    group_weights_history: np.ndarray,  # (epochs, 4)
    groupdro_grad_var: float,
    random_grad_var: float,
) -> Dict[str, bool]:
    """Verify GroupDRO weights diverge from uniform; variance within 20% tolerance.
    Returns: {'weights_diverged': bool, 'variance_matched': bool}
    """
    ...
```

### Pseudo-code

```
# evaluate_all_regimes:
results = {}
for regime, features in regime_features.items():
    mean_auroc, std_auroc = compute_auroc_cv(
        features, minority_labels, n_splits=config.n_folds, seed=config.base_seed
    )
    results[regime] = (mean_auroc, std_auroc)
return results

# compute_delta_auroc:
delta_gdro = auroc_erm - auroc_gdro
delta_random = auroc_erm - auroc_random
return delta_gdro, delta_random

# evaluate_gate:
cond1 = delta_gdro > config.delta_gdro_threshold   # > 0.10
cond2 = delta_random < config.delta_random_threshold  # < 0.05
passed = cond1 and cond2
result_str = f"PASS" if passed else "FAIL"
return passed, result_str

# verify_mechanism_activation:
final_weights = group_weights_history[-1]  # (4,)
uniform = np.ones(4) / 4
weights_diverged = np.max(np.abs(final_weights - uniform)) > 0.05  # >5% from uniform
variance_matched = abs(groupdro_grad_var - random_grad_var) / (groupdro_grad_var + 1e-8) < 0.20
return {'weights_diverged': weights_diverged, 'variance_matched': variance_matched}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Delta AUROC + gate | compute_delta_auroc (arithmetic), evaluate_gate (threshold comparison), verify_mechanism_activation |
| L-5-2 | Multi-regime AUROC | evaluate_all_regimes: loop over regimes, call compute_auroc_cv per regime, return dict |

---

## Budget Summary

| Task | Subtasks Used | Budget |
|------|--------------|--------|
| A-3 GroupDRO Trainer | 4 | 4 |
| A-4 Random Reweighting | 2 | 2 |
| A-5 Multi-Regime Evaluator | 2 | 2 |
| **Total** | **8** | **8** |
