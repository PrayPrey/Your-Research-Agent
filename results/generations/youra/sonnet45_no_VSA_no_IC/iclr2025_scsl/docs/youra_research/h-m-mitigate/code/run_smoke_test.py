"""Smoke test: Verify methodology works with minimal training (PoC scope)."""

import argparse
import json
from pathlib import Path

import pandas as pd
import torch
from torch.utils.data import DataLoader, Subset

from config import MNISTConfig, WaterbirdsConfig
from data.mnist_color import MNISTColorDataset
from data.waterbirds import get_waterbirds_loaders
from models.gradcam import create_gradcam_for_resnet18, create_gradcam_for_resnet50
from trainers.erm_trainer import ERMTrainer
from trainers.spatial_reg_trainer import SpatialRegTrainer
from utils.common import (
    create_resnet18,
    create_resnet50,
    get_eval_transforms,
    get_mnist_transforms,
    get_train_transforms,
    set_seed,
)


def run_mnist_smoke_test(output_dir: Path, data_root: str, n_epochs: int = 5):
    """Run MNIST smoke test with minimal epochs.

    Args:
        output_dir: Output directory
        data_root: MNIST dataset root
        n_epochs: Number of epochs (default 5 for smoke test)
    """
    print("\n" + "=" * 60)
    print("MNIST Smoke Test")
    print("=" * 60)

    set_seed(0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Minimal config
    config = {
        "lr": 0.01,
        "batch_size": 128,
        "epochs": n_epochs,
        "lambda_init": 0.01,
        "percentile_threshold": 75,
        "momentum": 0.9,
        "weight_decay": 1e-4,
        "patience": n_epochs + 1,  # No early stopping
    }

    # Datasets (subsample for speed)
    transform = get_mnist_transforms()
    train_dataset = MNISTColorDataset(
        root=data_root, train=True, correlation=0.9, transform=transform, seed=0
    )
    val_dataset = MNISTColorDataset(
        root=data_root, train=False, correlation=0.9, transform=transform, seed=0
    )

    # Subsample 10% for smoke test
    train_subset = Subset(train_dataset, range(0, len(train_dataset), 10))
    val_subset = Subset(val_dataset, range(0, len(val_dataset), 10))

    train_loader = DataLoader(train_subset, batch_size=128, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_subset, batch_size=128, shuffle=False, num_workers=2)

    results = {}

    for method in ["erm", "spatial_reg"]:
        print(f"\nMethod: {method}")

        model = create_resnet18(num_classes=10, pretrained=False).to(device)

        if method == "erm":
            trainer = ERMTrainer(model, train_loader, val_loader, device, config)
        else:
            gradcam = create_gradcam_for_resnet18(model, device)
            trainer = SpatialRegTrainer(
                model, train_loader, val_loader, device, config, gradcam
            )

        train_results = trainer.fit()
        val_metrics = trainer.validate()

        results[method] = {
            "wga": val_metrics["wga"],
            "avg_acc": val_metrics["avg_acc"],
            "best_epoch": train_results["best_epoch"],
        }

        print(f" WGA: {val_metrics['wga']:.4f}, Avg Acc: {val_metrics['avg_acc']:.4f}")

    # Save results
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "mnist_smoke_test.json", "w") as f:
        json.dump(results, f, indent=2)

    return results


def run_waterbirds_smoke_test(output_dir: Path, data_root: str, n_epochs: int = 5):
    """Run Waterbirds smoke test with minimal epochs.

    Args:
        output_dir: Output directory
        data_root: Waterbirds dataset root
        n_epochs: Number of epochs (default 5 for smoke test)
    """
    print("\n" + "=" * 60)
    print("Waterbirds Smoke Test")
    print("=" * 60)

    set_seed(0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Minimal config
    config = {
        "lr": 0.001,
        "batch_size": 128,
        "epochs": n_epochs,
        "lambda_init": 0.01,
        "percentile_threshold": 75,
        "momentum": 0.9,
        "weight_decay": 1e-4,
        "patience": n_epochs + 1,
    }

    # Load data
    train_transform = get_train_transforms()
    eval_transform = get_eval_transforms()

    train_loader, val_loader, _ = get_waterbirds_loaders(
        data_root=data_root,
        batch_size=128,
        num_workers=2,
        train_transform=train_transform,
        eval_transform=eval_transform,
    )

    results = {}

    for method in ["erm", "spatial_reg"]:
        print(f"\nMethod: {method}")

        model = create_resnet50(num_classes=2, pretrained=True)

        if method == "erm":
            trainer = ERMTrainer(model, train_loader, val_loader, device, config)
        else:
            gradcam = create_gradcam_for_resnet50(model, device)
            trainer = SpatialRegTrainer(
                model, train_loader, val_loader, device, config, gradcam
            )

        train_results = trainer.fit()
        val_metrics = trainer.validate()

        results[method] = {
            "wga": val_metrics["wga"],
            "avg_acc": val_metrics["avg_acc"],
            "best_epoch": train_results["best_epoch"],
        }

        print(f" WGA: {val_metrics['wga']:.4f}, Avg Acc: {val_metrics['avg_acc']:.4f}")

    # Save results
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "waterbirds_smoke_test.json", "w") as f:
        json.dump(results, f, indent=2)

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./outputs/smoke_test",
        help="Output directory",
    )
    parser.add_argument(
        "--mnist_data_root",
        type=str,
        default="~/.data_cache/datasets/mnist",
        help="MNIST dataset root",
    )
    parser.add_argument(
        "--waterbirds_data_root",
        type=str,
        default="~/.data_cache/datasets/waterbirds",
        help="Waterbirds dataset root",
    )
    parser.add_argument(
        "--epochs", type=int, default=5, help="Number of epochs for smoke test"
    )
    parser.add_argument(
        "--skip_waterbirds",
        action="store_true",
        help="Skip Waterbirds (run MNIST only)",
    )

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    mnist_root = Path(args.mnist_data_root).expanduser()
    waterbirds_root = Path(args.waterbirds_data_root).expanduser()

    # Run MNIST smoke test
    mnist_results = run_mnist_smoke_test(output_dir, str(mnist_root), args.epochs)

    # Run Waterbirds smoke test (optional)
    if not args.skip_waterbirds:
        waterbirds_results = run_waterbirds_smoke_test(
            output_dir, str(waterbirds_root), args.epochs
        )
    else:
        print("\nSkipping Waterbirds smoke test (--skip_waterbirds flag)")

    print("\n" + "=" * 60)
    print("Smoke Tests Complete")
    print("=" * 60)
    print("\nMNIST Results:")
    print(json.dumps(mnist_results, indent=2))

    if not args.skip_waterbirds:
        print("\nWaterbirds Results:")
        print(json.dumps(waterbirds_results, indent=2))


if __name__ == "__main__":
    main()
