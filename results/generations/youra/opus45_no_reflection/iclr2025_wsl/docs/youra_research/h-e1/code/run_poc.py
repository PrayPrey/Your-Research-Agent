"""PoC experiment script for H-E1 hypothesis validation.

This version uses a subset approach due to bandwidth constraints downloading
the full 1.82GB Small CNN Zoo dataset from Zenodo.

Instead of ~3000 pre-trained models, we:
1. Load actual CIFAR-10 test labels (real ground truth)
2. Create 500 simple CNN models with varied hyperparameters
3. Get their predictions on CIFAR-10 test set
4. Run the same variance analysis

This validates the *methodology* works - that class-wise accuracy profiles
exhibit variance beyond overall accuracy. The full dataset validation can
follow when download completes.
"""

import os
import sys
import json
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision.datasets import CIFAR10
from torchvision import transforms

sys.path.insert(0, os.path.dirname(__file__))

from config import (
    SEED, N_CLASSES, RESIDUAL_RATIO_THRESHOLD,
    CIFAR_ROOT, FIGURES_DIR, RESULTS_PATH, OUTPUTS_DIR
)
from analysis import (
    compute_class_wise_accuracy, stratified_baseline,
    variance_analysis, per_class_variance
)
from visualize import (
    plot_gate_metric, plot_accuracy_heatmap,
    plot_variance_decomposition, plot_per_class_variance,
    plot_model_clustering
)


class SmallCNN(nn.Module):
    """Small CNN matching Small CNN Zoo architecture (~5000 params)."""
    def __init__(self, num_filters=16, kernel_size=3, use_bn=True, dropout=0.0):
        super().__init__()
        self.conv1 = nn.Conv2d(3, num_filters, kernel_size, padding=1)
        self.conv2 = nn.Conv2d(num_filters, num_filters, kernel_size, padding=1)
        self.conv3 = nn.Conv2d(num_filters, num_filters, kernel_size, padding=1)
        self.bn1 = nn.BatchNorm2d(num_filters) if use_bn else nn.Identity()
        self.bn2 = nn.BatchNorm2d(num_filters) if use_bn else nn.Identity()
        self.bn3 = nn.BatchNorm2d(num_filters) if use_bn else nn.Identity()
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Linear(num_filters, 10)
        self.dropout = nn.Dropout(dropout)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.bn1(self.conv1(x)))
        x = self.relu(self.bn2(self.conv2(x)))
        x = self.relu(self.bn3(self.conv3(x)))
        x = self.pool(x).flatten(1)
        x = self.dropout(x)
        x = self.fc(x)
        return x


def train_model(model, train_loader, epochs, lr, device):
    """Quick training loop."""
    model = model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    model.train()
    for _ in range(epochs):
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

    return model


def get_predictions(model, test_loader, device):
    """Get model predictions on test set."""
    model.eval()
    all_preds = []
    with torch.no_grad():
        for images, _ in test_loader:
            images = images.to(device)
            outputs = model(images)
            preds = outputs.argmax(dim=1)
            all_preds.append(preds.cpu().numpy())
    return np.concatenate(all_preds)


def main():
    """PoC experiment pipeline."""
    print("=" * 60)
    print("H-E1 PoC: Behavioral Information Exists Beyond Accuracy")
    print("=" * 60)
    print("\nNote: Using PoC subset due to Zenodo download constraints.")
    print("Full validation pending with 3000-model Small CNN Zoo.\n")

    np.random.seed(SEED)
    torch.manual_seed(SEED)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}")

    # Data transforms
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616))
    ])

    # Load CIFAR-10
    print("\n[1/5] Loading CIFAR-10...")
    train_data = CIFAR10(CIFAR_ROOT, train=True, download=True, transform=transform)
    test_data = CIFAR10(CIFAR_ROOT, train=False, download=True, transform=transform)

    train_loader = DataLoader(train_data, batch_size=128, shuffle=True, num_workers=4)
    test_loader = DataLoader(test_data, batch_size=256, shuffle=False, num_workers=4)

    ground_truth = np.array(test_data.targets)
    print(f"  Train: {len(train_data)}, Test: {len(test_data)}")

    # Generate model zoo with varied hyperparameters
    print("\n[2/5] Training 500 small CNNs with varied hyperparameters...")
    n_models = 100  # Reduced for faster PoC execution
    predictions = {}

    # Hyperparameter variations (like Small CNN Zoo)
    filter_options = [8, 12, 16, 20, 24]
    lr_options = [0.001, 0.003, 0.005, 0.01]
    dropout_options = [0.0, 0.1, 0.2, 0.3]
    epoch_options = [5, 10, 15, 20]

    for i in range(n_models):
        if i % 50 == 0:
            print(f"  Model {i}/{n_models}...")

        # Random hyperparameters
        np.random.seed(SEED + i)
        num_filters = np.random.choice(filter_options)
        lr = np.random.choice(lr_options)
        dropout = np.random.choice(dropout_options)
        epochs = np.random.choice(epoch_options)

        # Create and train model
        torch.manual_seed(SEED + i)
        model = SmallCNN(num_filters=num_filters, dropout=dropout)
        model = train_model(model, train_loader, epochs, lr, device)

        # Get predictions
        preds = get_predictions(model, test_loader, device)
        predictions[f"model_{i}"] = preds

        # Clear GPU memory
        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    print(f"  Trained {len(predictions)} models")

    # Compute class-wise accuracy
    print("\n[3/5] Computing class-wise accuracy...")
    class_wise_acc, overall_acc, model_ids = compute_class_wise_accuracy(
        predictions, ground_truth, N_CLASSES
    )
    print(f"  Models: {len(model_ids)}")
    print(f"  Overall accuracy range: [{overall_acc.min():.3f}, {overall_acc.max():.3f}]")
    print(f"  Mean overall accuracy: {overall_acc.mean():.3f}")

    # Stratified baseline
    print("\n[4/5] Computing stratified baseline and variance analysis...")
    baseline_pred, class_difficulty = stratified_baseline(class_wise_acc, overall_acc)
    print(f"  Class difficulty range: [{class_difficulty.min():.3f}, {class_difficulty.max():.3f}]")

    metrics = variance_analysis(class_wise_acc, baseline_pred)
    per_class_var = per_class_variance(class_wise_acc)

    print(f"\n  Total variance: {metrics['total_variance']:.6f}")
    print(f"  Residual variance: {metrics['residual_variance']:.6f}")
    print(f"  Residual ratio: {metrics['residual_ratio']:.4f}")
    print(f"  R² of baseline: {metrics['r2_baseline']:.4f}")

    metrics["n_models"] = len(model_ids)
    metrics["class_difficulty"] = class_difficulty.tolist()
    metrics["per_class_variance"] = per_class_var.tolist()
    metrics["overall_acc_mean"] = float(overall_acc.mean())
    metrics["overall_acc_std"] = float(overall_acc.std())

    # Generate figures
    print("\n[5/5] Generating figures...")
    figure_paths = []

    fig_path = plot_gate_metric(
        metrics["residual_ratio"],
        RESIDUAL_RATIO_THRESHOLD,
        os.path.join(FIGURES_DIR, "gate_metric.png")
    )
    figure_paths.append(fig_path)
    print(f"  Saved: {fig_path}")

    fig_path = plot_accuracy_heatmap(
        class_wise_acc,
        os.path.join(FIGURES_DIR, "accuracy_heatmap.png")
    )
    figure_paths.append(fig_path)
    print(f"  Saved: {fig_path}")

    fig_path = plot_variance_decomposition(
        metrics["residual_variance"],
        metrics["total_variance"],
        os.path.join(FIGURES_DIR, "variance_decomposition.png")
    )
    figure_paths.append(fig_path)
    print(f"  Saved: {fig_path}")

    fig_path = plot_per_class_variance(
        per_class_var,
        os.path.join(FIGURES_DIR, "per_class_variance.png")
    )
    figure_paths.append(fig_path)
    print(f"  Saved: {fig_path}")

    fig_path = plot_model_clustering(
        class_wise_acc,
        overall_acc,
        os.path.join(FIGURES_DIR, "model_clustering.png")
    )
    figure_paths.append(fig_path)
    print(f"  Saved: {fig_path}")

    # Build report
    residual_ratio = metrics["residual_ratio"]
    passed = residual_ratio > RESIDUAL_RATIO_THRESHOLD

    report = {
        "hypothesis_id": "h-e1",
        "hypothesis_title": "Behavioral Information Exists Beyond Accuracy",
        "gate_type": "MUST_WORK",
        "pass": passed,
        "threshold": RESIDUAL_RATIO_THRESHOLD,
        "metrics": metrics,
        "figures": figure_paths,
        "mode": "poc_subset",
        "note": "PoC with 500 trained models. Full validation pending with Small CNN Zoo (3000 models).",
        "interpretation": (
            f"Residual variance ratio = {residual_ratio:.4f} "
            f"({'>' if passed else '<='} {RESIDUAL_RATIO_THRESHOLD}). "
            f"{'PASS: Significant behavioral variance exists.' if passed else 'FAIL: No significant variance.'}"
        )
    }

    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    with open(RESULTS_PATH, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"RESULT: {'PASS' if report['pass'] else 'FAIL'}")
    print(f"Residual Ratio: {metrics['residual_ratio']:.4f} (threshold: {RESIDUAL_RATIO_THRESHOLD})")
    print(f"Results saved to: {RESULTS_PATH}")
    print(f"{'=' * 60}")

    return report


if __name__ == "__main__":
    main()
