"""Evaluation and metrics computation (reused from h-e1)."""
import torch
import numpy as np
import sys
sys.path.append('/workspace/TEST_scsl/docs/youra_research/h-m/code')
from config import EXPERIMENT_CONFIG


def compute_per_class_accuracy(model, test_loader, device):
    """
    Compute per-class accuracy on test set.

    Args:
        model: Trained model
        test_loader: Test data loader
        device: Device for computation

    Returns:
        dict: {per_class: [acc_0, ..., acc_9],
               symmetric_mean, asymmetric_mean, overall_acc}
    """
    model.eval()

    # Initialize counters
    class_correct = np.zeros(10)
    class_total = np.zeros(10)

    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            pred = output.argmax(dim=1)

            # Per-class statistics
            for class_idx in range(10):
                mask = target == class_idx
                class_total[class_idx] += mask.sum().item()
                class_correct[class_idx] += (pred[mask] == class_idx).sum().item()

    # Compute accuracies
    per_class = (class_correct / class_total * 100).tolist()

    # Group by symmetry
    symmetric_digits = EXPERIMENT_CONFIG["symmetric_digits"]
    asymmetric_digits = EXPERIMENT_CONFIG["asymmetric_digits"]

    symmetric_mean = np.mean([per_class[i] for i in symmetric_digits])
    asymmetric_mean = np.mean([per_class[i] for i in asymmetric_digits])
    overall_acc = np.mean(per_class)

    return {
        "per_class": per_class,
        "symmetric_mean": float(symmetric_mean),
        "asymmetric_mean": float(asymmetric_mean),
        "overall_acc": float(overall_acc)
    }
