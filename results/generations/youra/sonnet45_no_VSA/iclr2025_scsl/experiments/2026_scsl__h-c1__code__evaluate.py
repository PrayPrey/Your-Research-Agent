"""Evaluation and metrics module."""
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Dict, Tuple, Any
from config import EXPERIMENT_CONFIG


def compute_per_class_accuracy(
    model: nn.Module,
    test_loader: DataLoader,
    device: torch.device
) -> Dict[int, float]:
    """Compute per-class test accuracy for all 10 digit classes.

    Args:
        model: Trained StandardCNN model
        test_loader: Test DataLoader
        device: cuda or cpu

    Returns:
        Dict mapping class_id (0-9) to accuracy (0-1)
    """
    model.eval()
    class_correct = [0] * 10
    class_total = [0] * 10

    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            pred = output.argmax(dim=1)

            for i in range(10):
                class_mask = (target == i)
                class_correct[i] += (pred[class_mask] == target[class_mask]).sum().item()
                class_total[i] += class_mask.sum().item()

    per_class_acc = {i: class_correct[i] / max(class_total[i], 1) for i in range(10)}
    return per_class_acc


def compute_differential_effect(
    per_class_acc: Dict[int, float]
) -> Tuple[float, float, float]:
    """Compute differential effect between asymmetric and symmetric digits.

    Args:
        per_class_acc: Dict mapping class_id to accuracy

    Returns:
        (symmetric_acc, asymmetric_acc, differential_effect)
        where differential_effect = asymmetric_acc - symmetric_acc
    """
    symmetric_classes = EXPERIMENT_CONFIG["symmetric_digits"]
    asymmetric_classes = EXPERIMENT_CONFIG["asymmetric_digits"]

    sym_acc = sum(per_class_acc[i] for i in symmetric_classes) / len(symmetric_classes)
    asym_acc = sum(per_class_acc[i] for i in asymmetric_classes) / len(asymmetric_classes)
    differential_effect = asym_acc - sym_acc

    return sym_acc, asym_acc, differential_effect


def check_success(
    baseline_diff: float,
    rotation_diff: float,
    threshold: float = 0.02
) -> str:
    """Check if hypothesis passes (rotation does NOT harm asymmetric digits).

    Args:
        baseline_diff: Baseline differential effect (asym - sym)
        rotation_diff: Rotation differential effect (asym - sym)
        threshold: Success threshold (2% = 0.02)

    Returns:
        "PASS" if |rotation_diff| <= |baseline_diff| OR both < threshold
        "FAIL" otherwise
    """
    if abs(rotation_diff) <= abs(baseline_diff):
        return "PASS"
    if abs(baseline_diff) < threshold and abs(rotation_diff) < threshold:
        return "PASS"
    return "FAIL"


def evaluate_all_metrics(
    baseline_model: nn.Module,
    rotation_model: nn.Module,
    test_loader: DataLoader,
    device: torch.device
) -> Dict[str, Any]:
    """Evaluate all metrics for both conditions.

    Args:
        baseline_model: Model trained without augmentation
        rotation_model: Model trained with rotation augmentation
        test_loader: Test DataLoader
        device: cuda or cpu

    Returns:
        Dict with per-condition metrics and success check
    """
    # Per-class accuracy
    baseline_per_class = compute_per_class_accuracy(baseline_model, test_loader, device)
    rotation_per_class = compute_per_class_accuracy(rotation_model, test_loader, device)

    # Differential effects
    baseline_sym, baseline_asym, baseline_diff = compute_differential_effect(baseline_per_class)
    rotation_sym, rotation_asym, rotation_diff = compute_differential_effect(rotation_per_class)

    # Success check
    success = check_success(baseline_diff, rotation_diff)

    return {
        'baseline_per_class': baseline_per_class,
        'rotation_per_class': rotation_per_class,
        'baseline_sym_acc': baseline_sym,
        'baseline_asym_acc': baseline_asym,
        'baseline_diff': baseline_diff,
        'rotation_sym_acc': rotation_sym,
        'rotation_asym_acc': rotation_asym,
        'rotation_diff': rotation_diff,
        'success_check': success
    }
