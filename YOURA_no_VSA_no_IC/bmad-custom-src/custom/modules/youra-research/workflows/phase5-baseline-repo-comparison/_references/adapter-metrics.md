# Adapter: Metric Injection

> **Reference Guide for Phase 5 Step 7 - Task 4**
> Template for computing hypothesis-specific metrics on OUR model

---

## Purpose

Compute hypothesis-specific metrics (psi, lambda_max) on OUR model.

**File:** `{adaptations_folder}/metrics.py`

---

## Full Template

```python
"""Metric Injection for YouRA Baseline Comparison.

Provides functions to compute our hypothesis metrics on the adapted baseline.
These metrics are computed on OUR model's outputs, not baseline's.
"""

import torch
import torch.nn as nn
import numpy as np
from collections import defaultdict

def compute_psi(model, dataloader, simple_indices=None, complex_indices=None,
                device='cuda' if torch.cuda.is_available() else 'cpu'):
    """Compute order parameter psi for curriculum learning evaluation.

    Args:
        model: Our model (from Phase 4)
        dataloader: DataLoader with our data
        simple_indices: Indices of "simple" examples
        complex_indices: Indices of "complex" examples
        device: Device to compute on

    Returns:
        float: Computed psi value

    Note:
        This implementation should match {hypothesis_folder}/code/measurements.py
    """
    model.eval()

    # If indices not provided, use first/last half as simple/complex
    if simple_indices is None or complex_indices is None:
        total_samples = len(dataloader.dataset)
        simple_indices = list(range(total_samples // 2))
        complex_indices = list(range(total_samples // 2, total_samples))

    simple_correct = 0
    complex_correct = 0
    simple_total = len(simple_indices)
    complex_total = len(complex_indices)

    with torch.no_grad():
        for batch_idx, (data, target) in enumerate(dataloader):
            data, target = data.to(device), target.to(device)
            output = model(data)
            pred = output.argmax(dim=1)

            # Count correct for simple/complex
            batch_start = batch_idx * dataloader.batch_size
            batch_end = batch_start + len(data)

            for i, idx in enumerate(range(batch_start, batch_end)):
                is_correct = (pred[i] == target[i]).item()
                if idx in simple_indices:
                    simple_correct += is_correct
                elif idx in complex_indices:
                    complex_correct += is_correct

    # Compute psi = (simple_acc - complex_acc) / (simple_acc + complex_acc + epsilon)
    simple_acc = simple_correct / max(simple_total, 1)
    complex_acc = complex_correct / max(complex_total, 1)

    epsilon = 1e-8
    psi = (simple_acc - complex_acc) / (simple_acc + complex_acc + epsilon)

    return psi

def compute_lambda_max(model, dataloader, device='cuda' if torch.cuda.is_available() else 'cpu'):
    """Compute maximum eigenvalue of Hessian (optional metric).

    Args:
        model: Our model
        dataloader: DataLoader
        device: Device

    Returns:
        float: Estimated lambda_max
    """
    # Simplified estimation using power iteration
    # Full implementation would use torch.autograd.functional.hessian
    return 0.0 # Placeholder

class MetricTracker:
    """Track metrics during training.

    Records metrics at each epoch for later analysis and comparison.

    Attributes:
        history: List of recorded metric dictionaries
    """

    def __init__(self):
        self.history = []
        self.current_epoch_metrics = defaultdict(list)

    def record(self, epoch, lr, seed, psi, loss, dataset="primary", **extra_metrics):
        """Record metrics for a training step.

        Args:
            epoch: Current epoch number
            lr: Learning rate
            seed: Random seed
            psi: Computed psi value
            loss: Training loss
            dataset: Dataset name ("primary" or "secondary")
            **extra_metrics: Additional metrics to record
        """
        record = {
            'epoch': epoch,
            'lr': lr,
            'seed': seed,
            'dataset': dataset,
            'psi': psi,
            'loss': loss,
            **extra_metrics
        }
        self.history.append(record)

    def log_batch(self, metric_name, value):
        """Log a metric value for current epoch (will be averaged)."""
        self.current_epoch_metrics[metric_name].append(value)

    def end_epoch(self, epoch, lr, seed, dataset="primary"):
        """End epoch and compute averaged metrics."""
        avg_metrics = {}
        for name, values in self.current_epoch_metrics.items():
            avg_metrics[name] = np.mean(values)

        self.record(
            epoch=epoch,
            lr=lr,
            seed=seed,
            dataset=dataset,
            psi=avg_metrics.get('psi', 0.0),
            loss=avg_metrics.get('loss', 0.0),
            **{k: v for k, v in avg_metrics.items() if k not in ['psi', 'loss']}
        )

        self.current_epoch_metrics.clear()

    def get_history(self):
        """Get all recorded metrics as list of dicts."""
        return self.history

    def get_best(self, metric='psi', higher_is_better=True):
        """Get best result for a metric."""
        if not self.history:
            return None

        if higher_is_better:
            return max(self.history, key=lambda x: x.get(metric, float('-inf')))
        else:
            return min(self.history, key=lambda x: x.get(metric, float('inf')))

    def summary(self):
        """Get summary statistics."""
        if not self.history:
            return {}

        psi_values = [h['psi'] for h in self.history if 'psi' in h]
        loss_values = [h['loss'] for h in self.history if 'loss' in h]

        return {
            'total_records': len(self.history),
            'best_psi': max(psi_values) if psi_values else None,
            'final_psi': psi_values[-1] if psi_values else None,
            'best_loss': min(loss_values) if loss_values else None,
            'final_loss': loss_values[-1] if loss_values else None
        }
```

---

## Related Files

| File | Purpose |
|------|---------|
| `step-07-adaptation-coding.md` | Orchestration step |
| `fair-comparison-principle.md` | Why we compute metrics on OUR model |
| `adapter-results.md` | Results saver using MetricTracker |
