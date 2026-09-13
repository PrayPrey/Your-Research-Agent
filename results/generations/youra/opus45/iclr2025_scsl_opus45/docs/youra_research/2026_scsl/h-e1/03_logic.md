# Logic Design: H-E1

**Hypothesis**: Per-sample loss trajectory features predict minority group membership (AUROC > 0.75)
**Type**: EXISTENCE (PoC)
**Date**: 2026-04-14

Applied: Standard PyTorch per-sample loss (reduction='none') pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-4: Training Loop + Tracker [Complexity: 15, Budget: 3 subtasks]

Applied: PyTorch ERM training with per-sample loss accumulation pattern

### API Signatures

```python
# code/train.py

class LossTrajectoryTracker:
    def __init__(self, num_samples: int, num_epochs: int = 5):
        """Track per-sample losses across trajectory epochs."""
        # self.matrix: np.ndarray shape (num_samples, num_epochs)
        ...

    def log_epoch_losses(
        self,
        sample_indices: np.ndarray,  # [N_batch] int indices
        losses: np.ndarray,          # [N_batch] float32
        epoch_idx: int,              # 0-based index into trajectory
    ) -> None:
        """Store losses for a batch at given epoch slot."""
        ...

    def get_loss_matrix(self) -> np.ndarray:
        """Return filled matrix. shape: (num_samples, num_epochs) = (4795, 5)"""
        ...


def run_epoch_eval_pass(
    model: "ResNet50Classifier",
    eval_loader: DataLoader,
    device: torch.device,
    tracker: "LossTrajectoryTracker",
    epoch_idx: int,              # 0-based, range 0..4 for epochs 1..5
) -> None:
    """Run deterministic pass over full train set; fill tracker for epoch_idx."""
    ...


def train(
    config: "Config",
    model: "ResNet50Classifier",
    train_loader: DataLoader,
    eval_loader: DataLoader,
    device: torch.device,
) -> Tuple["ResNet50Classifier", "LossTrajectoryTracker"]:
    """ERM training; after epochs 1-5 calls run_epoch_eval_pass.
    Returns: (trained_model, populated_tracker)
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| tracker.matrix | (4795, 5) | row=sample_idx, col=epoch_idx |
| sample_indices | [B] | int64, from dataset __getitem__ |
| losses (batch) | [B] | float32, CrossEntropyLoss reduction='none' |
| logits | [B, 2] | ResNet-50 output |

### Pseudo-code

```
train(config, model, train_loader, eval_loader, device):
    criterion = CrossEntropyLoss(reduction='none')
    optimizer = SGD(model.parameters(), lr, momentum, weight_decay)
    tracker = LossTrajectoryTracker(num_samples=4795, num_epochs=5)

    for epoch in range(1, config.epochs + 1):          # 1..20
        model.train()
        for images, labels, _, _ in train_loader:
            logits = model(images)                     # [B, 2]
            per_sample_loss = criterion(logits, labels)  # [B]
            loss = per_sample_loss.mean()
            optimizer.zero_grad(); loss.backward(); optimizer.step()

        if epoch <= config.trajectory_epochs:           # epochs 1..5
            run_epoch_eval_pass(model, eval_loader, device, tracker, epoch-1)

    return model, tracker


run_epoch_eval_pass(model, eval_loader, device, tracker, epoch_idx):
    model.eval()
    criterion = CrossEntropyLoss(reduction='none')
    with torch.no_grad():
        for images, labels, _, sample_indices in eval_loader:
            logits = model(images)                     # [B, 2]
            losses = criterion(logits, labels)         # [B]
            tracker.log_epoch_losses(
                sample_indices.cpu().numpy(),
                losses.cpu().numpy(),
                epoch_idx
            )
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | LossTrajectoryTracker | `__init__`, `log_epoch_losses`, `get_loss_matrix` with shape (4795, 5) |
| L-4-2 | run_epoch_eval_pass | Deterministic eval pass filling tracker; no_grad, model.eval() |
| L-4-3 | train loop | ERM 20-epoch loop; conditional eval pass after epochs 1-5 |

---

## A-5: Feature Extraction + AUROC [Complexity: 14, Budget: 3 subtasks]

Applied: sklearn StratifiedKFold + LogisticRegression AUROC pattern

### API Signatures

```python
# code/evaluate.py

def extract_trajectory_features(loss_matrix: np.ndarray) -> np.ndarray:
    """Compute 4 features per sample from loss trajectories.
    loss_matrix: (N, 5) -> features: (N, 4) = [L1, slope, variance, convergence_time]
    """
    ...


def compute_auroc_cv(
    features: np.ndarray,       # (N, 4)
    minority_labels: np.ndarray,  # (N,) binary int {0,1}
    n_splits: int = 5,
    seed: int = 42,
) -> Tuple[float, float]:
    """5-fold stratified CV with LogisticRegression.
    Returns: (mean_auroc, std_auroc)
    """
    ...


def compute_per_feature_auroc(
    features: np.ndarray,        # (N, 4)
    minority_labels: np.ndarray, # (N,)
) -> Dict[str, float]:
    """Single-feature AUROC scores (no CV).
    Returns: {"L1": float, "slope": float, "variance": float, "convergence": float}
    """
    ...


def evaluate_gate(auroc: float, threshold: float = 0.75) -> bool:
    """Returns True if auroc >= threshold."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| loss_matrix | (N, 5) | N=4795, 5 trajectory epochs |
| features | (N, 4) | [L1, slope, variance, convergence_time] |
| minority_labels | (N,) | 0=majority (G1,G3), 1=minority (G2,G4) |

### Pseudo-code

```
extract_trajectory_features(loss_matrix):  # (N, 5) -> (N, 4)
    L1   = loss_matrix[:, 0]               # epoch 1 loss
    L5   = loss_matrix[:, 4]               # epoch 5 loss
    slope = (L5 - L1) / 4.0               # linear slope
    L_norm = loss_matrix / (L1[:, None] + 1e-8)  # normalize by L1
    variance = np.var(L_norm, axis=1)      # variance of normalized trajectory
    convergence_time = np.argmin(loss_matrix, axis=1).astype(float)  # epoch of min loss
    return np.stack([L1, slope, variance, convergence_time], axis=1)  # (N, 4)


compute_auroc_cv(features, minority_labels, n_splits=5, seed=42):
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    auroc_scores = []
    for train_idx, val_idx in skf.split(features, minority_labels):
        clf = LogisticRegression(max_iter=1000, random_state=seed)
        clf.fit(features[train_idx], minority_labels[train_idx])
        probs = clf.predict_proba(features[val_idx])[:, 1]
        auroc_scores.append(roc_auc_score(minority_labels[val_idx], probs))
    return np.mean(auroc_scores), np.std(auroc_scores)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | extract_trajectory_features | Compute L1, slope, variance, convergence_time from (N,5) matrix |
| L-5-2 | compute_auroc_cv | 5-fold stratified CV with LogisticRegression; return (mean, std) |
| L-5-3 | compute_per_feature_auroc + evaluate_gate | Per-feature AUROC (no CV) + threshold gate check |

---

## External Dependencies (Base Hypothesis)

None - H-E1 is the base hypothesis (green-field).

---

*Logic design for EXISTENCE hypothesis H-E1*
*Total subtasks: 6/6 budget used*
